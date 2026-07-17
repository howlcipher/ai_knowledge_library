---
name: "automation"
description: "Triggers during scripting, task scheduling, and repetitive workflow optimization"
---

# Automation Guidelines and Standards

This skill establishes best practices for writing scripts, scheduling tasks, and optimizing repetitive workflows to ensure reliability and observability.

## Scripting and Execution Standards

### 1. Fault Tolerance and Resilience
- Write automation scripts that handle unexpected failures gracefully (e.g., using try-catch blocks, retry mechanisms, and fallback logic).
- Implement exponential backoff for external API calls and network-dependent tasks.

### 2. Observability and Monitoring
- Output structured logs (e.g., JSON or key-value pairs) from all background and scheduled jobs.
- Ensure log payloads contain execution status, timestamps, target systems, and any error trace details.

### 3. Workflow Consolidation
- Consolidate repetitive manual tasks into single, well-documented command-line tools or unified automation scripts.
- Avoid fragmented scripts that require manual intervention or coordination.

### 4. Integration Integrity and Input Validation
- Always validate inputs, outputs, and status codes when integrating disparate systems via APIs or CLI tools.
- Implement strict schema validation (e.g., JSON Schema) for data exchange interfaces.
