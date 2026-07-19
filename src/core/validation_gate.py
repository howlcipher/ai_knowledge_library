#!/usr/bin/env python3
"""
validation_gate.py

Code level validation gate for the tiered 3 pass agent pipeline, implementing
the contract in documentation/multi_agent_payload_protocol.md:

1. Parse raw model output as pure JSON (no fences, no prose).
2. Validate against config/schemas/agent_task_payload.schema.json.
3. Recompute and verify content.sha256.
4. Diff immutable fields against the input payload per the mutation matrix.
5. On failure feed the exact validator errors back to the agent and retry;
   after max_attempts emit a failed payload with a structured error object.
"""

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, List, Optional
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker

from src.infrastructure.config_loader import default_loader

SCHEMA_VERSION = "1.0.0"

# Fields no agent may change once the dispatcher has set them.
IMMUTABLE_ALWAYS = ["schema_version", "task_id", "created_at", "task", "routing"]

# Additional read only fields per pass, from the field mutation matrix.
IMMUTABLE_BY_PASS = {
    2: [["content"]],
    3: [["critique", "adversarial_tests"]],
}


def utc_now() -> str:
    """RFC 3339 UTC timestamp with second precision."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_of(body: str) -> str:
    return hashlib.sha256(body.encode("utf8")).hexdigest()


def build_initial_payload(objective: str, domain: str, skills: List[dict]) -> dict:
    """
    Dispatcher helper: constructs the schema valid task envelope handed to the
    Tier 3 agent at pass 1. Content starts empty; the agent writes the draft.
    """
    now = utc_now()
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": str(uuid4()),
        "created_at": now,
        "updated_at": now,
        "pipeline": {
            "pass_number": 1,
            "pass_name": "draft_self_correct",
            "tier": 3,
            "agent_id": "dispatcher",
            "status": "in_progress",
            "attempt": 1,
        },
        "routing": {"skills": skills},
        "task": {
            "objective": objective,
            "domain": domain,
            "constraints": [],
            "acceptance_criteria": [],
        },
        "content": {"format": "markdown", "body": "", "sha256": sha256_of("")},
        "lineage": {"revision": 0, "history": []},
    }


@dataclass
class GateResult:
    ok: bool
    payload: Optional[dict]
    errors: List[str] = field(default_factory=list)
    stage: str = ""
    attempts: int = 1


class ValidationGate:
    """
    Zero trust boundary between pipeline passes. All checks run in code;
    no LLM is trusted to validate its own output.
    """

    def __init__(self, schema_path: Optional[str] = None, max_attempts: int = 3):
        if schema_path is None:
            schema_path = os.path.join(
                default_loader.get_repo_root(),
                "config",
                "schemas",
                "agent_task_payload.schema.json",
            )
        with open(schema_path, "r", encoding="utf8") as f:
            self.schema = json.load(f)
        Draft202012Validator.check_schema(self.schema)
        self.validator = Draft202012Validator(
            self.schema, format_checker=FormatChecker()
        )
        self.max_attempts = max_attempts

    @staticmethod
    def parse(raw) -> "tuple[Optional[dict], Optional[str]]":
        """Strict parse: the response must be exactly one bare JSON object."""
        if not isinstance(raw, str) or not raw.strip():
            return None, "Empty response; expected one bare JSON object."
        stripped = raw.strip()
        if not stripped.startswith("{"):
            return None, (
                "Response does not start with '{'. No code fences, prose, or "
                "markdown are allowed; the JSON object is the entire response."
            )
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError as e:
            return None, f"JSON parse error: {e}"
        if not isinstance(obj, dict):
            return None, "Top level JSON value must be an object."
        return obj, None

    def schema_errors(self, payload: dict) -> List[str]:
        return [
            f"{'/'.join(str(p) for p in e.absolute_path) or '(root)'}: {e.message}"
            for e in self.validator.iter_errors(payload)
        ]

    @staticmethod
    def hash_error(payload: dict) -> Optional[str]:
        content = payload.get("content", {})
        expected = sha256_of(content.get("body", ""))
        if content.get("sha256") != expected:
            return (
                f"content.sha256 is {content.get('sha256')} but the SHA-256 of "
                f"content.body is {expected}. Recompute the hash of the exact body."
            )
        return None

    @staticmethod
    def _get_path(payload: dict, path: List[str]):
        node = payload
        for key in path:
            if not isinstance(node, dict) or key not in node:
                return None
            node = node[key]
        return node

    def mutation_errors(self, prev: dict, curr: dict, pass_number: int) -> List[str]:
        """Enforces the field mutation matrix against the previous payload."""
        errors = []

        paths = [[f] for f in IMMUTABLE_ALWAYS]
        paths += IMMUTABLE_BY_PASS.get(pass_number, [])
        for path in paths:
            before = self._get_path(prev, path)
            after = self._get_path(curr, path)
            if before is not None and before != after:
                errors.append(
                    f"{'.'.join(path)} is read only at pass {pass_number}; "
                    "copy it byte for byte from the input payload."
                )

        prev_history = (prev.get("lineage") or {}).get("history", [])
        curr_history = (curr.get("lineage") or {}).get("history", [])
        if curr_history[: len(prev_history)] != prev_history:
            errors.append(
                "lineage.history is append only; existing entries were modified."
            )
        elif len(curr_history) != len(prev_history) + 1:
            errors.append(
                "lineage.history must grow by exactly one entry for your pass."
            )

        if pass_number == 2:
            prev_findings = (prev.get("critique") or {}).get("findings", [])
            curr_findings = (curr.get("critique") or {}).get("findings", [])
            if curr_findings[: len(prev_findings)] != prev_findings:
                errors.append(
                    "critique.findings is append only at pass 2; existing "
                    "findings were modified."
                )
        return errors

    def check(
        self, raw, prev: Optional[dict] = None, expected_pass: Optional[int] = None
    ) -> GateResult:
        """Runs the full gate sequence on one raw model response."""
        payload, parse_err = self.parse(raw)
        if parse_err:
            return GateResult(False, None, [parse_err], "parse")

        errors = self.schema_errors(payload)
        if errors:
            return GateResult(False, payload, errors, "schema")

        actual_pass = payload["pipeline"]["pass_number"]
        if expected_pass is not None and actual_pass != expected_pass:
            return GateResult(
                False,
                payload,
                [
                    f"pipeline.pass_number is {actual_pass}; this boundary "
                    f"expects pass {expected_pass}."
                ],
                "pass_check",
            )

        hash_err = self.hash_error(payload)
        if hash_err:
            return GateResult(False, payload, [hash_err], "hash")

        if prev is not None:
            errors = self.mutation_errors(prev, payload, actual_pass)
            if errors:
                return GateResult(False, payload, errors, "mutation")

        return GateResult(True, payload, [], "ok")

    def run(
        self,
        call_fn: Callable[[Optional[str]], str],
        prev: Optional[dict],
        expected_pass: int,
    ) -> GateResult:
        """
        Bounded retry loop. call_fn receives None on the first attempt and a
        "VALIDATION ERROR:" feedback string on retries, and returns the raw
        model response. On exhaustion, returns a failed payload built from prev.
        """
        feedback = None
        last = GateResult(False, None, ["no attempts executed"], "none")
        for attempt in range(1, self.max_attempts + 1):
            raw = call_fn(feedback)
            last = self.check(raw, prev=prev, expected_pass=expected_pass)
            last.attempts = attempt
            if last.ok:
                last.payload["pipeline"]["attempt"] = attempt
                return last
            feedback = "VALIDATION ERROR:\n" + "\n".join(last.errors)
            print(
                f"[ValidationGate] Pass {expected_pass} attempt {attempt} failed "
                f"at stage '{last.stage}': {last.errors[0]}"
            )

        failed = self.build_failed_payload(prev, last.errors, last.stage)
        return GateResult(False, failed, last.errors, last.stage, self.max_attempts)

    def build_failed_payload(
        self,
        prev: Optional[dict],
        errors: List[str],
        stage: str,
        code: str = "SCHEMA_VALIDATION_FAILED",
        failure_vector: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> Optional[dict]:
        """Marks the previous payload failed with a structured error object.

        The defaults describe gate exhaustion; callers reporting other failure
        classes (e.g. UPSTREAM_UNAVAILABLE from the transport layer) override
        code, failure_vector, and context so the real cause is not masked.
        """
        if prev is None:
            return None
        failed = json.loads(json.dumps(prev))
        failed["pipeline"]["status"] = "failed"
        failed["pipeline"]["attempt"] = self.max_attempts
        failed["updated_at"] = utc_now()
        failed["error"] = {
            "code": code,
            "message": "; ".join(errors)[:2000] or "unknown validation failure",
            "failure_vector": failure_vector or f"validation_gate.{stage}",
            "context": context
            if context is not None
            else {"max_attempts": self.max_attempts},
            "occurred_at": utc_now(),
        }
        return failed
