# Ship Check and Human Authority Gate

Evaluate evidence, verification status, and human authority boundaries before marking a task complete or merging changes.

## 1. Principles

- **Human Authority Boundary:** High-risk actions (production changes, infrastructure apply, destructive migrations, paid services, external messaging, credentials) require explicit human sign-off.
- **Fail-Closed:** Absence of human response is treated as DENIED.
- **Complete Decision Packet:** When human authorization is needed, present objective, change summary, evidence, risks, findings, and verification status in a concise packet.

## 2. Procedure

1. Evaluate policy boundaries:
   ```bash
   python -m src.control_plane check-boundary --task-file <task_spec.yaml> --actions <planned_actions>
   ```
2. If boundaries are triggered (exit code 2), transition task state to `awaiting_human` and present the decision packet to the human operator.
3. If clean and authorized:
   - Ensure evidence ledger has recorded all milestones.
   - Run final project verification.
   - Transition task state to `complete`.
   - Close out task journal and push verified commits.
