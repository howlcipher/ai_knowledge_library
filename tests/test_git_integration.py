#!/usr/bin/env python3
"""
tests/test_git_integration.py

Phase 20 layered lifecycle tests for real git/GitHub integration (#59).
Fakes are injected ONLY at the subprocess boundary (a ScriptedRunner
standing in for `git`/`gh`) -- the production GitIntegrationExecutor logic
under test is the real code that will run against a genuine `git`/`gh` in
production. Each negative test proves a specific failure mode fails closed:
no fabricated success record is ever produced when a real-world step did not
actually happen.
"""

import pytest

from src.control_plane.authority_envelope import create_envelope
from src.control_plane.authority_profile import get_profile
from src.control_plane.git_integration import (
    GitIntegrationError,
    GitIntegrationExecutor,
    GitHubCIObserver,
)
from src.control_plane.proposed_action import ProposedAction
from src.control_plane.synthesis.campaign_state import GitIntegrationRecord
from tests._dogfood_test_helpers import ScriptedRunner, build_full_merge_flow


REPO_SLUG = "howlcipher/howlplane"


def make_envelope(profile_id="overnight-safe", campaign_id="DOGFOOD-TEST-GIT"):
    profile = get_profile(profile_id)
    return create_envelope(profile, campaign_id, operator_origin="cli:test@host")


_UNSET = object()


def make_executor(git_runner=None, gh_runner=None, envelope=_UNSET):
    return GitIntegrationExecutor(
        repo_root="/fake/repo",
        repo_slug=REPO_SLUG,
        envelope=make_envelope() if envelope is _UNSET else envelope,
        git_runner=git_runner or ScriptedRunner(),
        gh_runner=gh_runner or ScriptedRunner(),
    )


# ---------------------------------------------------------------------------
# Negative tests: each proves a specific failure fails closed.
# ---------------------------------------------------------------------------


def test_missing_commit_fails_closed():
    """If HEAD does not move after `git commit`, stage_and_commit must raise
    rather than report a fabricated commit SHA."""
    git = ScriptedRunner()
    git.on(["add", "--", "foo.py"], returncode=0)
    git.on(["commit", "-m", "fix: nothing"], returncode=0)
    # HEAD did not move: same SHA reported before and after (baseline == post-commit)
    git.on(["rev-parse", "HEAD"], returncode=0, stdout="deadbeef1234\n")

    executor = make_executor(git_runner=git)
    with pytest.raises(GitIntegrationError, match="did not actually happen"):
        executor.stage_and_commit(["foo.py"], "fix: nothing", baseline_sha="deadbeef1234")


def test_empty_path_list_fails_closed():
    """Never allowed to stage nothing and call it a commit."""
    executor = make_executor()
    with pytest.raises(GitIntegrationError, match="empty path list"):
        executor.stage_and_commit([], "fix: nothing")


def test_push_failure_blocks_downstream():
    """A failed `git push` must raise, never silently proceed to PR/merge."""
    git = ScriptedRunner()
    git.on(["push", "-u", "origin", "fix/T1"], returncode=1, stderr="remote rejected")
    executor = make_executor(git_runner=git)
    with pytest.raises(GitIntegrationError, match="git push"):
        executor.push_branch("fix/T1")


def test_push_reports_success_but_remote_sha_mismatch_fails_closed():
    """Push exits 0 but the remote SHA doesn't match local -- must fail closed,
    not just trust the exit code (#59 Phase 4)."""
    git = ScriptedRunner()
    git.on(["push", "-u", "origin", "fix/T1"], returncode=0)
    git.on(["rev-parse", "fix/T1"], returncode=0, stdout="aaaa1111\n")
    git.on(["ls-remote", "origin", "fix/T1"], returncode=0, stdout="bbbb2222\trefs/heads/fix/T1\n")
    executor = make_executor(git_runner=git)
    with pytest.raises(GitIntegrationError, match="does not match local SHA"):
        executor.push_branch("fix/T1")


def test_pr_creation_failure_blocks_merge():
    """`gh pr create` failing must raise, never proceed to a fabricated PR number."""
    gh = ScriptedRunner()
    gh.on(
        ["pr", "create", "--repo", REPO_SLUG, "--base", "main", "--head", "fix/T1", "--title", "t", "--body", "b"],
        returncode=1, stderr="validation failed",
    )
    executor = make_executor(gh_runner=gh)
    with pytest.raises(GitIntegrationError, match="gh pr create failed"):
        executor.open_pull_request("fix/T1", "t", "b")


def test_pr_create_reports_success_but_not_listed_fails_closed():
    """gh pr create exits 0 but a follow-up `gh pr list` finds nothing --
    must not trust the initial exit code alone."""
    gh = ScriptedRunner()
    gh.on(
        ["pr", "create", "--repo", REPO_SLUG, "--base", "main", "--head", "fix/T1", "--title", "t", "--body", "b"],
        returncode=0,
    )
    gh.on(["pr", "list", "--repo", REPO_SLUG, "--head", "fix/T1", "--json", "number,url"], returncode=0, stdout="[]")
    executor = make_executor(gh_runner=gh)
    with pytest.raises(GitIntegrationError, match="no PR found"):
        executor.open_pull_request("fix/T1", "t", "b")


def test_ci_pending_blocks_merge():
    """CI checks not yet observed as terminal must report all_required_green=False."""
    gh = ScriptedRunner()
    gh.on(["api", f"repos/{REPO_SLUG}/branches/main/protection"], returncode=404, stderr="Branch not protected")
    gh.on(
        ["pr", "checks", "5", "--json", "name,state,bucket,link"],
        returncode=0,
        stdout='[{"name": "test-python", "state": "PENDING", "bucket": "pending"}]',
    )
    observer = GitHubCIObserver(gh_runner=gh, git_runner=ScriptedRunner())
    obs = observer.observe_once("/fake/repo", 5, REPO_SLUG)
    assert obs.all_required_green is False


def test_ci_failed_check_reported_not_green():
    gh = ScriptedRunner()
    gh.on(["api", f"repos/{REPO_SLUG}/branches/main/protection"], returncode=404)
    gh.on(
        ["pr", "checks", "5", "--json", "name,state,bucket,link"],
        returncode=0,
        stdout=(
            '[{"name": "test-python", "state": "SUCCESS", "bucket": "pass"}, '
            '{"name": "test-go", "state": "FAILURE", "bucket": "fail"}, '
            '{"name": "lint", "state": "SUCCESS", "bucket": "pass"}]'
        ),
    )
    observer = GitHubCIObserver(gh_runner=gh, git_runner=ScriptedRunner())
    obs = observer.observe_once("/fake/repo", 5, REPO_SLUG)
    assert obs.all_required_green is False
    assert any(f["name"] == "test-go" for f in obs.failed_jobs)


def test_ci_all_green_reports_true():
    gh = ScriptedRunner()
    gh.on(
        ["api", f"repos/{REPO_SLUG}/branches/main/protection"],
        returncode=0,
        stdout='{"required_status_checks": {"contexts": ["test-python", "test-go", "lint"]}}',
    )
    gh.on(
        ["pr", "checks", "5", "--json", "name,state,bucket,link"],
        returncode=0,
        stdout=(
            '[{"name": "test-python", "state": "SUCCESS", "bucket": "pass"}, '
            '{"name": "test-go", "state": "SUCCESS", "bucket": "pass"}, '
            '{"name": "lint", "state": "SUCCESS", "bucket": "pass"}]'
        ),
    )
    observer = GitHubCIObserver(gh_runner=gh, git_runner=ScriptedRunner())
    obs = observer.observe_once("/fake/repo", 5, REPO_SLUG)
    assert obs.all_required_green is True
    assert obs.all_required_observed is True


def test_simulated_ci_evidence_rejected_in_overnight_mode():
    """A GitIntegrationRecord in simulated/legacy mode must never satisfy
    is_fully_integrated(), regardless of what ci_status string it carries --
    simulated_green (or any simulated value) can never authorize a merge."""
    rec = GitIntegrationRecord(
        task_id="T1", target_repo="howlplane", integration_mode="simulated",
        ci_status="passed", merged=True,  # even if some legacy code tried to force these
    )
    # merged/ci_status alone are not authoritative -- is_fully_integrated()
    # requires every *_observed flag, none of which a simulated record sets.
    assert rec.is_fully_integrated() is False


def test_merge_reported_success_but_remote_main_missing_sha_not_integrated():
    """gh pr merge exits 0 and reports merged=true, but the merge SHA is not
    yet reachable from origin/main -- must not be treated as integrated."""
    git = ScriptedRunner()
    git.on(["fetch", "origin", "main"], returncode=0)
    git.on(["merge-base", "--is-ancestor", "mergesha123", "origin/main"], returncode=1)
    executor = make_executor(git_runner=git)
    assert executor.verify_remote_main_contains("mergesha123") is False


def test_merge_pull_request_rejects_non_task_branch():
    gh = ScriptedRunner()
    gh.on(["pr", "view", "5", "--json", "headRefName"], returncode=0, stdout='{"headRefName": "main"}')
    executor = make_executor(gh_runner=gh)
    with pytest.raises(GitIntegrationError, match="not a recognized campaign task branch"):
        executor.merge_pull_request(5)


def test_merge_pull_request_gh_merge_failure_raises():
    gh = ScriptedRunner()
    gh.on(["pr", "view", "5", "--json", "headRefName"], returncode=0, stdout='{"headRefName": "fix/T1"}')
    gh.on(
        ["pr", "merge", "5", "--repo", REPO_SLUG, "--squash", "--delete-branch"],
        returncode=1, stderr="required checks have not passed",
    )
    executor = make_executor(gh_runner=gh)
    with pytest.raises(GitIntegrationError, match="gh pr merge --squash"):
        executor.merge_pull_request(5)


def test_merge_pull_request_success_path_returns_merge_sha():
    gh = ScriptedRunner()
    gh.on(["pr", "view", "5", "--json", "headRefName"], returncode=0, stdout='{"headRefName": "fix/T1"}')
    gh.on(["pr", "merge", "5", "--repo", REPO_SLUG, "--squash", "--delete-branch"], returncode=0)
    gh.on(
        ["pr", "view", "5", "--repo", REPO_SLUG, "--json", "state,merged,mergeCommit"],
        returncode=0,
        stdout='{"state": "MERGED", "merged": true, "mergeCommit": {"oid": "sha_merge_1"}}',
    )
    executor = make_executor(gh_runner=gh)
    assert executor.merge_pull_request(5) == "sha_merge_1"


# ---------------------------------------------------------------------------
# Positive lifecycle test: real call ordering through the whole sequence.
# ---------------------------------------------------------------------------


def test_real_lifecycle_calls_occur_in_order():
    git = ScriptedRunner()
    gh = ScriptedRunner()
    build_full_merge_flow(
        git, gh, task_id="T1", repo_slug=REPO_SLUG, pr_number=42,
        commit_message="fix: T1", pr_title="t", pr_body="b",
        modified_path="src/foo.py", commit_sha="commitsha1", merge_sha="mergesha1",
    )

    executor = make_executor(git_runner=git, gh_runner=gh)

    branch = executor.create_task_branch("T1")
    assert branch == "fix/T1"

    commit_sha = executor.stage_and_commit(["src/foo.py"], "fix: T1")
    assert commit_sha == "commitsha1"

    assert executor.push_branch(branch) is True

    pr_number, pr_url = executor.open_pull_request(branch, "t", "b")
    assert pr_number == 42

    merge_sha = executor.merge_pull_request(pr_number)
    assert merge_sha == "mergesha1"

    assert executor.verify_remote_main_contains(merge_sha) is True

    # Verify call ordering: branch -> add/commit -> push -> PR create/list/view -> merge -> verify
    branch_idx = git.calls.index(("switch", "-c", "fix/T1", "origin/main"))
    commit_idx = git.calls.index(("commit", "-m", "fix: T1"))
    push_idx = git.calls.index(("push", "-u", "origin", "fix/T1"))
    assert branch_idx < commit_idx < push_idx


def test_evaluate_allows_within_envelope_scope():
    executor = make_executor()
    action = ProposedAction(action_type="merge_pull_request", target_repo=REPO_SLUG)
    verdict, decision_id, reason = executor.evaluate(action, "/fake/repo", "/fake/run")
    assert verdict == "ALLOW"
    assert decision_id is not None


def test_evaluate_denies_force_push_regardless_of_envelope():
    executor = make_executor()
    action = ProposedAction(action_type="force_push", target_repo=REPO_SLUG)
    verdict, decision_id, reason = executor.evaluate(action, "/fake/repo", "/fake/run")
    assert verdict == "DENY"


def test_evaluate_requires_approval_with_no_envelope():
    executor = make_executor(envelope=None)
    action = ProposedAction(action_type="merge_pull_request", target_repo=REPO_SLUG)
    verdict, decision_id, reason = executor.evaluate(action, "/fake/repo", "/fake/run")
    assert verdict == "REQUIRE_APPROVAL"
