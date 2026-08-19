# Reconcile Multi-Agent Reviews

Synthesize findings from multiple independent review passes into a classified reconciliation report without silently erasing disagreements.

## 1. Principles

- **Preserve disagreement:** Do not allow one agent to silently dismiss another reviewer's finding.
- **Mandatory dismissal rationale:** Any dismissed `blocker` or `high` finding requires an explicit, documented `resolution_reason`.
- **Classification categories:**
  - `confirmed`: Multiple reviewers agree or finding is verified.
  - `likely`: High-confidence finding from a domain reviewer.
  - `disputed`: Disagreement between reviewers or with implementation rationale.
  - `requires_human_judgment`: Security-sensitive or architectural disputes requiring human authority.
  - `false_positive`: Proved incorrect with explicit reasoning.
  - `out_of_scope`: Legitimate point outside task scope, filed as a backlog item.

## 2. Procedure

1. Run the reconciliation engine:
   ```bash
   python -m src.control_plane reconcile --findings-file <findings.yaml> --output <report.md>
   ```
2. Remediate all confirmed and likely findings.
3. For disputed or high-risk findings, escalate to human review before proceeding to verification.
