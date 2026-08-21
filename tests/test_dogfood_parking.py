#!/usr/bin/env python3
"""
tests/test_dogfood_parking.py

Phase 24 parking acceptance (#59): Task A requires human authority (its gap
fix implies a force-push, a never-delegatable boundary) and parks; Task B is
an independent, low-risk, evidence-backed fix that completes through the
full real git/GitHub integration lifecycle. The campaign must not globally
hang on Task A -- final status clearly shows Task A awaiting operator
decision while Task B lands.
"""

from pathlib import Path
import subprocess

from src.control_plane.evidence_ledger import EvidenceLedger
from src.control_plane.git_baseline import RepositoryDelta
from src.control_plane.git_integration import GitIntegrationExecutor
from src.control_plane.orchestrator import OrchestrationResult
from src.control_plane.synthesis.campaign_state import GitIntegrationRecord
from src.control_plane.synthesis.capability_negotiator import FrameworkGap
from src.control_plane.synthesis.engine import ProductSynthesizer, SynthesisResult
from src.control_plane.synthesis.marathon import MarathonDogfoodEngine
from src.control_plane.synthesis.product_spec import ProductSpec
from src.control_plane.synthesis.provider_pool import ProviderAvailabilityStatus, ProviderPoolManager

REPO_SLUG = "howlcipher/howlplane"


class _ScriptedRunner:
    def __init__(self):
        self.responses = {}
        self.calls = []

    def on(self, args, returncode=0, stdout="", stderr=""):
        self.responses.setdefault(tuple(args), []).append(
            subprocess.CompletedProcess(args=list(args), returncode=returncode, stdout=stdout, stderr=stderr)
        )
        return self

    def __call__(self, repo_root, args, timeout=60):
        key = tuple(args)
        self.calls.append(key)
        q = self.responses.get(key)
        if q:
            return q[0] if len(q) == 1 else q.pop(0)
        return subprocess.CompletedProcess(args=list(args), returncode=0, stdout="", stderr="")


class _FakeOrchestrator:
    def __init__(self, run_dir, modified_file):
        self.run_dir = run_dir
        self.modified_file = modified_file

    def run(self, task_spec, planned_actions=None):
        return OrchestrationResult(
            task_id=task_spec.task_id, task_spec=task_spec, final_state="complete", exit_code=0,
            final_delta=RepositoryDelta(
                files_modified=[self.modified_file], diff_content="x", insertions=1, is_empty=False,
            ),
            run_dir=str(self.run_dir),
        )


class _TwoGapSynthesizer(ProductSynthesizer):
    """
    "notes" always fails with a gap whose description implies a force push
    (never-delegatable -> parks). "todo" fails once with an ordinary gap,
    then succeeds on retry once the (fully real, fake-boundary) fix lands.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.todo_attempts = 0

    def create_from_prompt(self, prompt: str, output_dir, **kwargs) -> SynthesisResult:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        is_notes = "notes" in str(output_dir)
        mock_spec = ProductSpec(name="p", title="P", description="P")

        if is_notes:
            gap = FrameworkGap(
                code="HF_GAP_NOTES", required_behavior="requires a force push to land safely",
                current_support="none", suggested_enhancement="n/a",
            )
            return SynthesisResult(
                product_name="p", product_spec=mock_spec, success=False, status="PRODUCT_BLOCKED",
                framework_gaps=[gap], error_message="blocked: requires a force push to land safely",
            )

        self.todo_attempts += 1
        if self.todo_attempts == 1:
            gap = FrameworkGap(
                code="HF_GAP_TODO", required_behavior="ordinary missing helper",
                current_support="none", suggested_enhancement="add helper",
            )
            return SynthesisResult(
                product_name="p", product_spec=mock_spec, success=False, status="PRODUCT_BLOCKED",
                framework_gaps=[gap], error_message="blocked: ordinary missing helper",
            )
        report = self.acceptance_runner.run_acceptance_suite(out_path, mock_spec)
        bundle = self._package_product_bundle(out_path, mock_spec, report)
        return SynthesisResult(
            product_name="p", product_spec=mock_spec, success=True, status="VERIFIED_PRODUCT",
            product_bundle=bundle, acceptance_report=report, implementing_provider="codex",
        )


def test_task_a_parks_task_b_completes_campaign_does_not_hang(tmp_path):
    pool = ProviderPoolManager()
    pool.set_status("codex", ProviderAvailabilityStatus.AVAILABLE)
    ledger = EvidenceLedger(tmp_path / "ledger.jsonl")
    synth = _TwoGapSynthesizer(provider_pool=pool, ledger=ledger, synthesis_mode="deterministic_baseline")

    todo_task_id = "ENG-TODO-02"
    branch = f"fix/{todo_task_id}"
    run_dir = tmp_path / "fake_run" / todo_task_id

    git = _ScriptedRunner()
    git.on(["fetch", "origin", "main"], returncode=0)
    git.on(["switch", "-c", branch, "origin/main"], returncode=0)
    git.on(["rev-parse", "--verify", branch], returncode=0, stdout="bsha\n")
    git.on(["add", "--", "src/x.py"], returncode=0)
    git.on(["commit", "-m", "fix(todo): resolve HF_GAP_TODO found during marathon dogfooding"], returncode=0)
    git.on(["rev-parse", "HEAD"], returncode=0, stdout="csha\n")
    git.on(["push", "-u", "origin", branch], returncode=0)
    git.on(["rev-parse", branch], returncode=0, stdout="csha\n")
    git.on(["ls-remote", "origin", branch], returncode=0, stdout=f"csha\trefs/heads/{branch}\n")
    git.on(["merge-base", "--is-ancestor", "msha", "origin/main"], returncode=0)
    git.on(["switch", "main"], returncode=0)
    git.on(["merge", "--ff-only", "origin/main"], returncode=0)
    git.on(["status", "--porcelain"], returncode=0, stdout="")
    git.on(["rev-parse", "origin/main"], returncode=0, stdout="finalsha\n")

    gh = _ScriptedRunner()
    gh.on(
        ["pr", "create", "--repo", REPO_SLUG, "--base", "main", "--head", branch,
         "--title", "fix(todo): HF_GAP_TODO", "--body",
         "Automated marathon dogfooding fix.\n\nGap: HF_GAP_TODO\nordinary missing helper"],
        returncode=0,
    )
    gh.on(["pr", "list", "--repo", REPO_SLUG, "--head", branch, "--json", "number,url"],
          returncode=0, stdout='[{"number": 55, "url": "https://x/pull/55"}]')
    gh.on(["pr", "view", "55", "--json", "number"], returncode=0, stdout='{"number": 55}')
    gh.on(["api", f"repos/{REPO_SLUG}/branches/main/protection"],
          returncode=0, stdout='{"required_status_checks": {"contexts": ["test-python"]}}')
    gh.on(["pr", "checks", "55", "--json", "name,state,bucket,link"], returncode=0,
          stdout='[{"name": "test-python", "state": "SUCCESS", "bucket": "pass"}]')
    gh.on(["pr", "view", "55", "--json", "headRefName"], returncode=0, stdout=f'{{"headRefName": "{branch}"}}')
    gh.on(["pr", "merge", "55", "--repo", REPO_SLUG, "--squash", "--delete-branch"], returncode=0)
    gh.on(
        ["pr", "view", "55", "--repo", REPO_SLUG, "--json", "state,merged,mergeCommit"],
        returncode=0, stdout='{"state": "MERGED", "merged": true, "mergeCommit": {"oid": "msha"}}',
    )

    engine = MarathonDogfoodEngine(
        synthesizer=synth, provider_pool=pool, ledger=ledger,
        base_output_dir=tmp_path / "out", campaign_dir=tmp_path / "campaigns",
        target_repo=tmp_path, repo_slug=REPO_SLUG,
        orchestrator_factory=lambda config: _FakeOrchestrator(run_dir, "src/x.py"),
        git_executor_factory=lambda env, merges: GitIntegrationExecutor(
            tmp_path, REPO_SLUG, env, git_runner=git, gh_runner=gh, merges_so_far=merges,
        ),
    )

    report = engine.run_marathon(
        benchmarks=["notes", "todo"], max_iterations=2, authority_profile_id="overnight-safe",
    )

    # Campaign must not have hung/globally frozen on Task A.
    assert report.stopped_reason != "AWAITING_HUMAN"

    # Task A ("notes" gap): parked, never fabricated as integrated.
    notes_records = [g for g in report.git_records if g.get("task_id", "").startswith("ENG-NOTES")]
    assert notes_records == []  # parked before any git integration was attempted

    # Task B ("todo" gap): fully, really integrated.
    todo_rec = next(g for g in report.git_records if g.get("task_id") == todo_task_id)
    assert GitIntegrationRecord.from_dict(todo_rec).is_fully_integrated() is True

    # "todo" benchmark itself succeeded after the real fix landed and was retried.
    todo_result = next(r for r in report.benchmark_results if r.benchmark_id == "todo")
    assert todo_result.success is True
    assert todo_result.retried_after_fix is True

    # "notes" benchmark remains failed (its gap is parked, unresolved).
    notes_result = next(r for r in report.benchmark_results if r.benchmark_id == "notes")
    assert notes_result.success is False

    # Morning decision queue clearly shows Task A awaiting operator decision.
    from src.control_plane.synthesis.campaign_state import DurableCampaignState
    state = DurableCampaignState.load(Path(report.state_dir))
    assert len(state.pending_human_decisions) == 1
    assert state.pending_human_decisions[0]["boundary_type"] == "force_push"
    assert "force_push" in state.pending_human_decisions[0]["why_delegated_authority_did_not_apply"]

    markdown = state.render_markdown()
    assert "Pending Human Decisions" in markdown
