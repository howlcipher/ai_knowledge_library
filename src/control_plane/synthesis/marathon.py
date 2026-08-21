#!/usr/bin/env python3
"""
marathon.py

Marathon dogfooding engine for repeated, evidence-driven prompt-to-product synthesis.
Runs automated synthesis benchmarks, tracks provider quotas, collects framework gaps,
and records immutable evidence entries into the control plane ledger.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Union

from src.control_plane.evidence_ledger import EvidenceEntry, EvidenceLedger
from src.control_plane.synthesis.engine import ProductSynthesizer, SynthesisResult
from src.control_plane.synthesis.provider_pool import (
    ProviderAvailabilityStatus,
    ProviderPoolManager,
)
from src.control_plane.task_spec import DataClassSerializationMixin

MARATHON_SCHEMA_VERSION = "howlplane.marathon_dogfood/v1"


# Canonical suite of prompt-to-product benchmarks
STANDARD_BENCHMARKS: Dict[str, str] = {
    "notes": (
        "Create a persistent notes application. Users should be able to create, view, "
        "edit, and delete notes. Provide a browser interface and a JSON HTTP API. "
        "Notes must survive application restart. Reject invalid note data."
    ),
    "todo": (
        "Create a persistent todo task management application with browser UI and REST API. "
        "Users can create tasks, mark them complete, and delete them. State persists across restarts."
    ),
    "status_api": (
        "Create a service status and health check API with a lightweight dashboard interface. "
        "Provide /health and /api/status endpoints with uptime and metric reporting."
    ),
    "inventory": (
        "Create a local inventory tracking application with browser UI and JSON endpoints. "
        "Track item quantities, categories, and persist changes locally."
    ),
    "json_transform": (
        "Create a JSON transformation utility with HTTP POST endpoint to normalize, "
        "validate, and store structured data records."
    ),
}


@dataclass
class DogfoodIterationResult(DataClassSerializationMixin):
    """Result of a single dogfood benchmark synthesis iteration."""

    benchmark_id: str
    prompt: str
    product_name: str
    success: bool
    status: str
    passed_checks: int
    total_checks: int
    repair_cycles: int
    duration_seconds: float
    implementing_provider: Optional[str] = None
    framework_gaps_count: int = 0
    error_message: Optional[str] = None
    bundle_path: Optional[str] = None


@dataclass
class MarathonSummaryReport(DataClassSerializationMixin):
    """Aggregated summary of a marathon dogfooding run."""

    iterations_attempted: int
    iterations_succeeded: int
    iterations_failed: int
    total_duration_seconds: float
    benchmark_results: List[DogfoodIterationResult] = field(default_factory=list)
    stopped_reason: str = "completed_all_benchmarks"
    schema: str = MARATHON_SCHEMA_VERSION

    def render_markdown(self) -> str:
        lines = [
            "# HowlPlane Marathon Dogfooding Report",
            "",
            f"- **Completed Iterations:** {self.iterations_succeeded}/{self.iterations_attempted} succeeded",
            f"- **Total Duration:** {self.total_duration_seconds}s",
            f"- **Stop Reason:** `{self.stopped_reason}`",
            "",
            "| Benchmark | Status | Acceptance | Repairs | Duration | Provider | Bundle Path |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for r in self.benchmark_results:
            mark = "✓ PASSED" if r.success else "✗ FAILED"
            acc = f"{r.passed_checks}/{r.total_checks}"
            lines.append(
                f"| {r.benchmark_id} | {mark} | {acc} | {r.repair_cycles} | "
                f"{r.duration_seconds}s | `{r.implementing_provider or 'unknown'}` | `{r.bundle_path or 'N/A'}` |"
            )
        lines.append("")
        return "\n".join(lines)


class MarathonDogfoodEngine:
    """
    Drives continuous dogfooding loops across product benchmarks.
    """

    def __init__(
        self,
        synthesizer: Optional[ProductSynthesizer] = None,
        provider_pool: Optional[ProviderPoolManager] = None,
        ledger: Optional[EvidenceLedger] = None,
        base_output_dir: Union[str, Path] = "output",
    ):
        self.provider_pool = provider_pool or ProviderPoolManager()
        self.ledger = ledger
        self.synthesizer = synthesizer or ProductSynthesizer(provider_pool=self.provider_pool, ledger=self.ledger)
        self.base_output_dir = Path(base_output_dir).resolve()

    def run_marathon(
        self,
        benchmarks: Optional[List[str]] = None,
        max_iterations: int = 5,
        until_providers_exhausted: bool = False,
        avoid_provider: Optional[str] = None,
    ) -> MarathonSummaryReport:
        """
        Executes bounded marathon dogfooding.
        """
        t0 = time.time()
        benchmark_keys = benchmarks or list(STANDARD_BENCHMARKS.keys())
        results: List[DogfoodIterationResult] = []
        stop_reason = "completed_all_benchmarks"

        self.base_output_dir.mkdir(parents=True, exist_ok=True)

        for idx, b_key in enumerate(benchmark_keys[:max_iterations]):
            prompt = STANDARD_BENCHMARKS.get(b_key, b_key)
            out_dir = self.base_output_dir / f"dogfood_{b_key}"

            # Check provider pool capacity
            available_candidates = self.provider_pool.select_candidates(
                task_category="code_heavy",
                avoid_provider=avoid_provider,
            )
            if not available_candidates:
                stop_reason = "all_providers_exhausted"
                break

            synth_res = self.synthesizer.create_from_prompt(
                prompt=prompt,
                output_dir=out_dir,
                avoid_provider=avoid_provider,
                port=8088 + idx,
            )

            acc_passed = synth_res.acceptance_report.passed_count if synth_res.acceptance_report else 0
            acc_total = synth_res.acceptance_report.total_count if synth_res.acceptance_report else 0

            iter_res = DogfoodIterationResult(
                benchmark_id=b_key,
                prompt=prompt,
                product_name=synth_res.product_name,
                success=synth_res.success,
                status=synth_res.status,
                passed_checks=acc_passed,
                total_checks=acc_total,
                repair_cycles=synth_res.repair_cycles,
                duration_seconds=synth_res.duration_seconds,
                implementing_provider=synth_res.implementing_provider,
                framework_gaps_count=len(synth_res.framework_gaps),
                error_message=synth_res.error_message,
                bundle_path=str(out_dir) if synth_res.success else None,
            )
            results.append(iter_res)

        total_elapsed = round(time.time() - t0, 3)
        succeeded = sum(1 for r in results if r.success)
        failed = len(results) - succeeded

        return MarathonSummaryReport(
            iterations_attempted=len(results),
            iterations_succeeded=succeeded,
            iterations_failed=failed,
            total_duration_seconds=total_elapsed,
            benchmark_results=results,
            stopped_reason=stop_reason,
        )
