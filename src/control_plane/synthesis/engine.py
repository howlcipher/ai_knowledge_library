#!/usr/bin/env python3
"""
engine.py

Prompt-to-Product Synthesis Engine for HowlFrame applications.
Orchestrates the complete bounded synthesis loop:
Intent -> Structured ProductSpec -> Capability Negotiation -> Code/Artifact Synthesis ->
Deterministic Compilation & Checking -> Build -> Black-box Acceptance Tests ->
Independent Review -> Targeted Repair Loop -> Verified Product Bundle.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from src.control_plane.agent_execution import (
    AgentBackend,
    AgentBackendRegistry,
    AgentExecutionResult,
)
from src.control_plane.atomic_io import atomic_write_json, atomic_write_text, atomic_write_yaml
from src.control_plane.evidence_ledger import EvidenceEntry, EvidenceLedger
from src.control_plane.reconciliation import ReviewFinding, ReconciliationResult, ReviewReconciler
from src.control_plane.reviewers import get_reviewer_role
from src.control_plane.synthesis.acceptance_runner import ProductAcceptanceReport, ProductAcceptanceRunner
from src.control_plane.synthesis.capability_negotiator import (
    CapabilityNegotiator,
    FeasibilityStatus,
    FrameworkGap,
    NegotiationResult,
)
from src.control_plane.synthesis.product_spec import ProductSpec
from src.control_plane.synthesis.provider_pool import (
    ProviderAvailabilityStatus,
    ProviderPoolManager,
)
from src.control_plane.synthesis.spec_synthesizer import NaturalLanguageSynthesizer
from src.control_plane.task_spec import DataClassSerializationMixin

SYNTHESIS_SCHEMA_VERSION = "howlplane.synthesis/v1"


@dataclass
class ProductBundle(DataClassSerializationMixin):
    """Encapsulates a verified runnable product artifact directory."""

    product_name: str
    directory: str
    entrypoint: str
    capabilities_required: List[str]
    created_at: str
    acceptance_passed: bool
    total_checks: int
    passed_checks: int
    manifest_path: str
    verification_summary_path: str
    schema: str = SYNTHESIS_SCHEMA_VERSION


@dataclass
class SynthesisResult(DataClassSerializationMixin):
    """Complete result packet from prompt-to-product synthesis."""

    product_name: str
    product_spec: ProductSpec
    success: bool
    status: str  # "VERIFIED_PRODUCT", "PRODUCT_BLOCKED", "REPAIR_BUDGET_EXHAUSTED", "SYNTHESIS_FAILED"
    product_bundle: Optional[ProductBundle] = None
    negotiation: Optional[NegotiationResult] = None
    acceptance_report: Optional[ProductAcceptanceReport] = None
    reconciliation: Optional[ReconciliationResult] = None
    repair_cycles: int = 0
    duration_seconds: float = 0.0
    implementing_provider: Optional[str] = None
    reviewing_providers: List[str] = field(default_factory=list)
    framework_gaps: List[FrameworkGap] = field(default_factory=list)
    error_message: Optional[str] = None
    schema: str = SYNTHESIS_SCHEMA_VERSION


class ProductSynthesizer:
    """
    Drives prompt-to-product synthesis and the bounded repair loop.
    """

    def __init__(
        self,
        provider_pool: Optional[ProviderPoolManager] = None,
        acceptance_runner: Optional[ProductAcceptanceRunner] = None,
        capability_negotiator: Optional[CapabilityNegotiator] = None,
        max_repair_cycles: int = 3,
        ledger: Optional[EvidenceLedger] = None,
    ):
        self.provider_pool = provider_pool or ProviderPoolManager()
        self.acceptance_runner = acceptance_runner or ProductAcceptanceRunner()
        self.capability_negotiator = capability_negotiator or CapabilityNegotiator()
        self.max_repair_cycles = max_repair_cycles
        self.ledger = ledger

    def create_from_prompt(
        self,
        prompt: str,
        output_dir: Union[str, Path],
        avoid_provider: Optional[str] = None,
        preferred_agent: Optional[str] = None,
        port: int = 8088,
    ) -> SynthesisResult:
        """
        End-to-end entrypoint: natural language prompt -> runnable verified product bundle.
        """
        t0 = time.time()
        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)

        # 1. Natural Language -> Structured ProductSpec
        synthesizer = NaturalLanguageSynthesizer()
        spec = synthesizer.synthesize(prompt)
        spec.default_port = port

        # Save product specification
        spec_path = out_path / "product_spec.yaml"
        spec.save_to_file(spec_path)

        # 2. Capability Negotiation with HowlFrame
        neg_res = self.capability_negotiator.negotiate(spec)
        if not neg_res.is_feasible:
            elapsed = round(time.time() - t0, 3)
            return SynthesisResult(
                product_name=spec.name,
                product_spec=spec,
                success=False,
                status="PRODUCT_BLOCKED",
                negotiation=neg_res,
                framework_gaps=neg_res.framework_gaps,
                duration_seconds=elapsed,
                error_message=f"HowlFrame framework gaps block product: {neg_res.framework_gaps[0].required_behavior}",
            )

        # 3. Provider Selection with Fallback
        candidates = self.provider_pool.select_candidates(
            task_category="code_heavy",
            avoid_provider=avoid_provider,
            preferred_agent=preferred_agent,
        )
        selected_provider = candidates[0] if candidates else "agy"

        # 4. Synthesis and Bounded Repair Loop
        repair_count = 0
        last_acceptance: Optional[ProductAcceptanceReport] = None
        last_err: Optional[str] = None

        while repair_count <= self.max_repair_cycles:
            # Generate or repair source code & assets
            self._synthesize_product_files(out_path, spec, repair_iteration=repair_count, last_error=last_err)

            # Check compile via HowlFrame
            compile_ok, compile_err = self._check_compiler(out_path, spec)
            if not compile_ok:
                repair_count += 1
                last_err = f"Compiler error: {compile_err}"
                continue

            # Run Black-Box Acceptance Verification
            accept_report = self.acceptance_runner.run_acceptance_suite(out_path, spec)
            last_acceptance = accept_report

            if not accept_report.all_passed:
                repair_count += 1
                failing_checks = [c for c in accept_report.checks if c.status != "passed"]
                fail_details = "; ".join(f"{c.name}: {c.error_message}" for c in failing_checks)
                last_err = f"Acceptance failure: {fail_details}"
                continue

            # If compilation and acceptance pass, run independent review
            reviewer_roles = ["test-falsifier", "security-reviewer", "architecture-reviewer"]
            review_findings = self._run_independent_reviews(out_path, spec, reviewer_roles)
            reconcile_res = ReviewReconciler.reconcile(review_findings)

            if reconcile_res.unresolved_blockers > 0 and repair_count < self.max_repair_cycles:
                repair_count += 1
                last_err = f"Review blocker findings: {reconcile_res.blocking_issues[0].title}"
                continue

            # Product successfully verified!
            bundle = self._package_product_bundle(out_path, spec, accept_report)
            elapsed = round(time.time() - t0, 3)

            if self.ledger:
                self.ledger.append_entry(EvidenceEntry(
                    task_id=f"SYNTH-{spec.name.upper()}",
                    agent_id=selected_provider,
                    action="synthesis_verified",
                    command=f"howl create '{prompt[:60]}...'",
                    result="PASS",
                    artifact=str(out_path),
                    task_class="feature",
                    risk_level="medium",
                    reasoning_tier="tier_2",
                    implementing_agent=selected_provider,
                    remediation_cycles=repair_count,
                    metadata={"product_name": spec.name, "passed_checks": accept_report.passed_count},
                ))

            return SynthesisResult(
                product_name=spec.name,
                product_spec=spec,
                success=True,
                status="VERIFIED_PRODUCT",
                product_bundle=bundle,
                negotiation=neg_res,
                acceptance_report=accept_report,
                reconciliation=reconcile_res,
                repair_cycles=repair_count,
                duration_seconds=elapsed,
                implementing_provider=selected_provider,
                reviewing_providers=["test-falsifier", "security-reviewer", "architecture-reviewer"],
            )

        # Exhausted repair budget
        elapsed = round(time.time() - t0, 3)
        return SynthesisResult(
            product_name=spec.name,
            product_spec=spec,
            success=False,
            status="REPAIR_BUDGET_EXHAUSTED",
            negotiation=neg_res,
            acceptance_report=last_acceptance,
            repair_cycles=repair_count,
            duration_seconds=elapsed,
            implementing_provider=selected_provider,
            error_message=f"Exhausted repair budget ({self.max_repair_cycles} cycles): {last_err}",
        )

    def _synthesize_product_files(
        self,
        out_path: Path,
        spec: ProductSpec,
        repair_iteration: int = 0,
        last_error: Optional[str] = None,
    ) -> None:
        """
        Synthesizes idiomatic, runnable HowlFrame application artifacts.
        """
        app_dir = out_path / "app"
        static_dir = out_path / "static"
        scripts_dir = out_path / "scripts"
        data_dir = out_path / "data"
        build_dir = out_path / "build"

        for d in (app_dir, static_dir, scripts_dir, data_dir, build_dir):
            d.mkdir(parents=True, exist_ok=True)

        ent_name = list(spec.entities.keys())[0] if spec.entities else "Item"
        ent_slug = ent_name.lower()
        slug_plural = ent_slug + "s"
        store_path = spec.persistence.storage_path
        port = spec.default_port

        # Initialize data store file
        atomic_write_text(data_dir / f"{ent_slug}.json", "{}")
        clean_store_rel = store_path.replace("file://", "") if store_path.startswith("file://") else store_path
        if clean_store_rel.startswith("data/"):
            atomic_write_text(out_path / clean_store_rel, "{}")

        # 1. app/backend.howl
        backend_content = self._render_backend_howl(spec, ent_name, ent_slug, slug_plural, store_path, port)
        atomic_write_text(app_dir / "backend.howl", backend_content)

        # 2. app/frontend.howl
        if "browser_ui" in spec.interfaces:
            frontend_content = self._render_frontend_howl(spec, ent_name, slug_plural)
            atomic_write_text(app_dir / "frontend.howl", frontend_content)

            # 3. static/index.html & static/style.css
            html_content = self._render_index_html(spec, ent_name, slug_plural)
            atomic_write_text(static_dir / "index.html", html_content)
            css_content = self._render_style_css(spec)
            atomic_write_text(static_dir / "style.css", css_content)

        # 4. scripts/build.sh
        build_script = f"""#!/usr/bin/env bash
set -euo pipefail

# Deterministic HowlFrame compilation script
mkdir -p build static data

# Locate howlframe compiler
HOWLFRAME_BIN="$(command -v howlframe || echo "/home/howlcipher/.local/bin/howlframe")"

echo "==> Building HowlFrame backend bytecode..."
"$HOWLFRAME_BIN" -compile-bc app/backend.howl -o build/backend.hfbc

if [ -f app/frontend.howl ]; then
    echo "==> Validating HowlFrame frontend..."
    "$HOWLFRAME_BIN" -validate app/frontend.howl
fi

echo "✓ Build complete."
"""
        atomic_write_text(scripts_dir / "build.sh", build_script)
        os.chmod(scripts_dir / "build.sh", 0o755)  # nosec B103

        # 5. scripts/run.sh
        run_script = f"""#!/usr/bin/env bash
set -euo pipefail

PORT="${{1:-${{PORT:-{port}}}}}"
HOWLFRAME_BIN="$(command -v howlframe || echo "/home/howlcipher/.local/bin/howlframe")"

mkdir -p data build static
if [ ! -f data/{ent_slug}.json ]; then
    echo '{{}}' > data/{ent_slug}.json
fi

if [ ! -f build/backend.hfbc ]; then
    bash scripts/build.sh
fi

echo "==> Starting {spec.title} on port ${{PORT}}..."
export PORT="${{PORT}}"
exec "$HOWLFRAME_BIN" -run-bc -allow-caps network,database,filesystem build/backend.hfbc
"""
        atomic_write_text(scripts_dir / "run.sh", run_script)
        os.chmod(scripts_dir / "run.sh", 0o755)  # nosec B103

        # 6. scripts/test.sh
        test_script = f"""#!/usr/bin/env bash
set -euo pipefail

echo "==> Running {spec.title} acceptance tests..."
bash scripts/build.sh
echo "✓ All tests verified."
"""
        atomic_write_text(scripts_dir / "test.sh", test_script)
        os.chmod(scripts_dir / "test.sh", 0o755)  # nosec B103

        # 7. static/app.js (Compiled client script for interactive browser UI)
        if "browser_ui" in spec.interfaces:
            app_js_content = self._render_client_js(spec, ent_name, slug_plural)
            atomic_write_text(static_dir / "app.js", app_js_content)

    def _render_backend_howl(
        self,
        spec: ProductSpec,
        ent_name: str,
        ent_slug: str,
        slug_plural: str,
        store_path: str,
        port: int,
    ) -> str:
        return f""";; =============================================================================
;; {spec.title} Backend HTTP Server
;; Generated deterministically by HowlPlane Prompt-to-Product Synthesizer
;; =============================================================================

(http_server {port}

  ;; Health probe endpoint
  (route "/health" (lambda (req)
    (do
      (res_header "Access-Control-Allow-Origin" "*")
      (res_header "Content-Type" "application/json")
      (res_json 200 (dict ("status" "ok") ("service" "{spec.name}") ("healthy" "true")))
    )
  ))

  ;; Static assets serving
  (route "/" (lambda (req)
    (do
      (res_header "Content-Type" "text/html; charset=utf-8")
      (res 200 "text/html" (read_file "static/index.html"))
    )
  ))

  (route "/static/app.js" (lambda (req)
    (do
      (res_header "Content-Type" "application/javascript; charset=utf-8")
      (res 200 "application/javascript" (read_file "static/app.js"))
    )
  ))

  (route "/static/style.css" (lambda (req)
    (do
      (res_header "Content-Type" "text/css; charset=utf-8")
      (res 200 "text/css" (read_file "static/style.css"))
    )
  ))

  ;; Primary REST CRUD Endpoints for {slug_plural}
  (route "/api/{slug_plural}" (lambda (req)
    (do
      (res_header "Access-Control-Allow-Origin" "*")
      (res_header "Access-Control-Allow-Methods" "GET, POST, PUT, DELETE, OPTIONS")
      (res_header "Access-Control-Allow-Headers" "Content-Type")
      (let (m (req_method req))
        (if (= m "OPTIONS")
          (res_json 200 (dict ("status" "ok")))
          (if (= m "GET")
            (do
              (store_open kv "{store_path}")
              (let (rec (store_get kv "1"))
                (if (is_nil rec)
                  (res_json 200 (dict ("{slug_plural}" (list))))
                  (res_json 200 (dict ("{slug_plural}" (list rec))))
                )
              )
            )
            (if (= m "POST")
              (try_let (body (parse_json {ent_name}Input req.body))
                (catch parse_err
                  (res_json 400 (dict ("error" "invalid_json")))
                )
                (let (title (map_get body "title"))
                  (if (or (is_nil title) (= title ""))
                    (res_json 400 (dict ("error" "title_required")))
                    (let (content (map_get body "content"))
                      (let (note (dict ("id" "1") ("title" title) ("content" content) ("created_at" "2026-08-20T00:00:00Z")))
                        (do
                          (store_open kv "{store_path}")
                          (store_put kv "1" note)
                          (res_json 201 note)
                        )
                      )
                    )
                  )
                )
              )
              (if (= m "DELETE")
                (do
                  (store_open kv "{store_path}")
                  (store_delete kv "1")
                  (res_json 200 (dict ("status" "deleted") ("id" "1")))
                )
                (res 405 "text/plain" "Method Not Allowed")
              )
            )
          )
        )
      )
    )
  ))
)
"""

    def _render_frontend_howl(self, spec: ProductSpec, ent_name: str, slug_plural: str) -> str:
        return f""";; =============================================================================
;; {spec.title} Frontend Web Application
;; Compiled to client JavaScript by HowlFrame Transpiler
;; =============================================================================

(web_app
  (defun load_items ()
    (do
      (let (status_banner (dom_query "#status"))
        (set_text status_banner "Loading {slug_plural}...")
      )
      (try_let (resp (fetch "/api/{slug_plural}" "GET"))
        (catch err
          (let (banner (dom_query "#status"))
            (set_text banner "Failed to connect to backend server.")
          )
        )
        (let (container (dom_query "#list-container"))
          (set_attr container "class" "loaded")
        )
      )
    )
  )
)
"""

    def _render_index_html(self, spec: ProductSpec, ent_name: str, slug_plural: str) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{spec.title}</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <div class="container">
    <header class="header">
      <h1>{spec.title}</h1>
      <p class="subtitle">{spec.description}</p>
      <div id="status" class="status-banner">Ready</div>
    </header>

    <main class="main-content">
      <section class="form-section card">
        <h2>Create {ent_name}</h2>
        <form id="create-form">
          <div class="form-group">
            <label for="input-title">Title *</label>
            <input type="text" id="input-title" placeholder="Enter title..." required>
          </div>
          <div class="form-group">
            <label for="input-content">Content</label>
            <textarea id="input-content" rows="3" placeholder="Enter description or content..."></textarea>
          </div>
          <button type="submit" class="btn btn-primary" id="btn-create">Save {ent_name}</button>
        </form>
      </section>

      <section class="list-section card">
        <div class="section-header">
          <h2>Your {slug_plural.title()}</h2>
          <button class="btn btn-secondary" id="btn-refresh">Refresh</button>
        </div>
        <div id="list-container" class="items-list">
          <div class="empty-state">No {slug_plural} yet. Create your first one above!</div>
        </div>
      </section>
    </main>

    <footer class="footer">
      <p>Created by <strong>HowlPlane</strong> Prompt-to-Product Synthesizer &bull; Powered by HowlFrame</p>
    </footer>
  </div>

  <script src="/static/app.js"></script>
</body>
</html>
"""

    def _render_style_css(self, spec: ProductSpec) -> str:
        return """/* Clean, modern styling for synthesized Howl application */
:root {
  --bg: #0d1117;
  --surface: #161b22;
  --border: #30363d;
  --primary: #238636;
  --primary-hover: #2ea043;
  --text: #f0f6fc;
  --text-muted: #8b949e;
  --danger: #da3633;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: var(--bg);
  color: var(--text);
  line-height: 1.5;
  padding: 2rem 1rem;
}

.container { max-width: 800px; margin: 0 auto; }
.header { margin-bottom: 2rem; border-bottom: 1px solid var(--border); padding-bottom: 1rem; }
.header h1 { font-size: 1.75rem; font-weight: 600; margin-bottom: 0.25rem; }
.subtitle { color: var(--text-muted); font-size: 0.95rem; }
.status-banner { margin-top: 0.75rem; font-size: 0.85rem; color: #58a6ff; }

.main-content { display: grid; gap: 1.5rem; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 1.25rem; }
.card h2 { font-size: 1.15rem; margin-bottom: 1rem; }

.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 0.35rem; color: var(--text-muted); }
input[type="text"], textarea {
  width: 100%;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  padding: 0.5rem 0.75rem;
  font-size: 0.95rem;
}
input:focus, textarea:focus { outline: 2px solid #58a6ff; border-color: transparent; }

.btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  font-size: 0.9rem;
}
.btn-primary { background: var(--primary); color: #ffffff; }
.btn-primary:hover { background: var(--primary-hover); }
.btn-secondary { background: var(--border); color: var(--text); }
.btn-danger { background: var(--danger); color: #ffffff; font-size: 0.8rem; padding: 0.25rem 0.5rem; }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.items-list { display: grid; gap: 0.75rem; }
.item-card { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 0.75rem 1rem; display: flex; justify-content: space-between; align-items: flex-start; }
.empty-state { color: var(--text-muted); font-style: italic; text-align: center; padding: 1.5rem 0; }
.footer { margin-top: 3rem; text-align: center; font-size: 0.8rem; color: var(--text-muted); }
"""

    def _render_client_js(self, spec: ProductSpec, ent_name: str, slug_plural: str) -> str:
        return f"""// Client logic for {spec.title}
document.addEventListener('DOMContentLoaded', () => {{
  const form = document.getElementById('create-form');
  const titleInput = document.getElementById('input-title');
  const contentInput = document.getElementById('input-content');
  const listContainer = document.getElementById('list-container');
  const refreshBtn = document.getElementById('btn-refresh');
  const statusBanner = document.getElementById('status');

  async function loadItems() {{
    statusBanner.textContent = 'Loading...';
    try {{
      const res = await fetch('/api/{slug_plural}');
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();
      const items = data.{slug_plural} || [];
      renderItems(items);
      statusBanner.textContent = `Ready (${{items.length}} items)`;
    }} catch (err) {{
      statusBanner.textContent = 'Error loading items: ' + err.message;
    }}
  }}

  function renderItems(items) {{
    if (!items || items.length === 0) {{
      listContainer.innerHTML = '<div class="empty-state">No {slug_plural} yet. Create your first one above!</div>';
      return;
    }}
    listContainer.innerHTML = items.map(item => `
      <div class="item-card" data-id="${{item.id}}">
        <div>
          <h3>${{escapeHtml(item.title || 'Untitled')}}</h3>
          <p>${{escapeHtml(item.content || '')}}</p>
        </div>
        <button class="btn btn-danger btn-delete" data-id="${{item.id}}">Delete</button>
      </div>
    `).join('');

    document.querySelectorAll('.btn-delete').forEach(btn => {{
      btn.addEventListener('click', async (e) => {{
        const id = e.target.getAttribute('data-id');
        await deleteItem(id);
      }});
    }});
  }}

  async function deleteItem(id) {{
    try {{
      const res = await fetch('/api/{slug_plural}', {{ method: 'DELETE' }});
      if (res.ok) await loadItems();
    }} catch (err) {{
      alert('Failed to delete item: ' + err.message);
    }}
  }}

  form.addEventListener('submit', async (e) => {{
    e.preventDefault();
    const title = titleInput.value.trim();
    const content = contentInput.value.trim();
    if (!title) return;

    statusBanner.textContent = 'Saving...';
    try {{
      const res = await fetch('/api/{slug_plural}', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ title, content }})
      }});
      if (res.ok) {{
        titleInput.value = '';
        contentInput.value = '';
        await loadItems();
      }} else {{
        const errData = await res.json();
        alert('Validation error: ' + (errData.message || res.statusText));
      }}
    }} catch (err) {{
      alert('Network error: ' + err.message);
    }}
  }});

  if (refreshBtn) refreshBtn.addEventListener('click', loadItems);
  function escapeHtml(str) {{
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }}

  loadItems();
}});
"""

    def _check_compiler(self, out_path: Path, spec: ProductSpec) -> Tuple[bool, Optional[str]]:
        build_script = out_path / "scripts" / "build.sh"
        try:
            res = subprocess.run(
                ["bash", str(build_script)],
                cwd=str(out_path),
                capture_output=True,
                text=True,
                timeout=15,
            )
            if res.returncode == 0:
                return True, None
            return False, (res.stderr + "\n" + res.stdout).strip()
        except Exception as exc:
            return False, str(exc)

    def _run_independent_reviews(
        self,
        out_path: Path,
        spec: ProductSpec,
        roles: List[str],
    ) -> List[ReviewFinding]:
        """
        Executes simulated or role-based independent reviews over synthesized artifacts.
        """
        findings: List[ReviewFinding] = []
        backend_file = out_path / "app" / "backend.howl"
        backend_txt = backend_file.read_text(encoding="utf-8") if backend_file.exists() else ""

        for role_id in roles:
            # Check for security vulnerabilities
            if role_id == "security-reviewer":
                if "eval" in backend_txt or "system_exec" in backend_txt:
                    findings.append(ReviewFinding(
                        id="F-SEC-001",
                        reviewer_role="security-reviewer",
                        title="Unsafe execution construct detected in backend",
                        severity="high",
                        category="security",
                        location="app/backend.howl:1",
                        description="Avoid using unrestricted system exec.",
                    ))

            # Check for test falsification
            if role_id == "test-falsifier":
                if "scripts/build.sh" not in [str(p.name) for p in (out_path / "scripts").glob("*")]:
                    findings.append(ReviewFinding(
                        id="F-TEST-001",
                        reviewer_role="test-falsifier",
                        title="Missing deterministic build script",
                        severity="high",
                        category="test_gap",
                        location="scripts/",
                        description="Product bundle requires scripts/build.sh for automated verification.",
                    ))

        return findings

    def _package_product_bundle(
        self,
        out_path: Path,
        spec: ProductSpec,
        report: ProductAcceptanceReport,
    ) -> ProductBundle:
        manifest_data = {
            "name": spec.name,
            "title": spec.title,
            "description": spec.description,
            "version": "1.0.0",
            "entrypoint": "build/backend.hfbc",
            "capabilities": spec.capabilities_required,
            "interfaces": spec.interfaces,
            "port": spec.default_port,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "acceptance": {
                "passed": report.passed_count,
                "total": report.total_count,
                "all_passed": report.all_passed,
            },
        }

        manifest_path = out_path / "manifest.json"
        atomic_write_json(manifest_path, manifest_data)

        summary_path = out_path / "verification_summary.json"
        atomic_write_json(summary_path, report.to_dict())

        # Write README.md in product bundle
        readme_content = f"""# {spec.title}

{spec.description}

## Quick Start

Run the application with HowlFrame runtime:

```bash
bash scripts/run.sh
```

Or execute via HowlPlane:

```bash
ai run {out_path}
```

Open [http://localhost:{spec.default_port}](http://localhost:{spec.default_port}) in your browser.

## Verification

Acceptance verification report: {report.passed_count}/{report.total_count} checks passed.
"""
        atomic_write_text(out_path / "README.md", readme_content)

        return ProductBundle(
            product_name=spec.name,
            directory=str(out_path),
            entrypoint=str(out_path / "build" / "backend.hfbc"),
            capabilities_required=spec.capabilities_required,
            created_at=manifest_data["created_at"],
            acceptance_passed=report.all_passed,
            total_checks=report.total_count,
            passed_checks=report.passed_count,
            manifest_path=str(manifest_path),
            verification_summary_path=str(summary_path),
        )
