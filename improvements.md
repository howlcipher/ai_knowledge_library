# 🚀 Future Automation and Feature Backlog

This document tracks all conceptual improvements, architectural upgrades, and automation tasks that can be implemented to further harden, scale, and optimize the AI Knowledge Library. 

## 1. Bug Fixes & Immediate Issues
* (No open items)

## 2. Architecture & Ease of Use (Frontend, UI/UX, Accessibility)
* **Accessibility (a11y) & UX Enhancements**: Ensure the Streamlit Web UI has ARIA tags for screen readers, and add color-blind safe palettes to the Textual TUI (`color_theory`, `accessibility`).
* **Offline Local LLM Support (`system_administration`)**: Add a `docker-compose.yml` that seamlessly spins up the Library alongside a local Ollama instance for 100% offline, air-gapped usage.

## 3. Advanced Features & Tooling (Data Analytics & Automation)
* **Token & Cost Analytics Dashboard (`data_analyst`, `quantitative_finance`)**: Implement a telemetry tab in the Web UI that tracks token consumption, cost estimates across the 5 LLM providers, and query latency.
* **End-to-End (E2E) UI Testing (`quality_assurance`, `test_and_verify`)**: We currently only have unit tests. We need Playwright/Cypress integration tests to verify that the RAG Web UI and Textual TUI render correctly without crashing.
* **Multi-Agent Orchestration (Inspired by AutoGen)**: Expand the single-agent RAG into a collaborative multi-agent system (e.g., a Researcher agent communicating with a QA agent) with human-in-the-loop authorization for command execution.
* **Intelligent Failover & Rate Limit Handling (Inspired by LiteLLM)**: Enhance our LiteLLM implementation to automatically cascade/failover to a fallback provider (e.g., jump to Claude if Gemini hits a 429 error) without interrupting the user's flow.

## 4. Security & Hardening (Cyber Security, Red/Blue Team)
* **SAST Integration (`cyber_security`, `blue_team`)**: The current pre-push hook runs unit tests but misses security checks. We must integrate `bandit` (Python) and `gosec` (Go) into the `Makefile` linting suite to catch secret leaks or unsafe arbitrary code execution.
* **Adversarial Hardening (`red_team`)**: Expand the `adversarial_tester.py` to specifically test the Web UI for prompt-injection vulnerabilities that could execute malicious JavaScript in the browser.

## 5. DevOps & Infrastructure (`devops`)
* **Automated Docker Registry Publishing**: Create a new GitHub Action workflow to automatically build and push the library's Docker container to the GitHub Container Registry (GHCR) on release.
* **Prefix Caching & Memory Optimization (Inspired by LightLLM / vLLM)**: Implement KV cache prefixing so that the massive static RAG documents and system prompts are cached in memory across turns, drastically reducing latency and token costs.

## 6. Identified Skill Gaps (Missing Agent Capabilities)
* **Gap 1: Advanced RAG Engineering (Inspired by LlamaIndex)**: Create a skill to implement Hybrid Search (combining BM25 keyword search with dense vector search), Knowledge Graph extraction, and agentic OCR for ingesting PDFs/images.
* **Gap 2: Site Reliability Engineering (SRE)**: We need an SRE skill focused on auto-recovering from API rate limits (e.g., when Claude or Grok limits are hit) and handling exponential backoffs gracefully.
* **Gap 3: Prompt Engineering / AI Ops**: A dedicated skill for optimizing system prompts, managing token context windows, and refining few-shot examples for the LLM.

## ✅ Recently Completed
* **Graphical Frontend (TUI or Web UI):** Built an interactive Textual TUI (`tui.py`) and integrated Streamlit Web UI launchers natively into the Go installer.
* **Multi-LLM Integration Switch:** Implemented `litellm` routing and a configuration interface inside the TUI to dynamically swap between Claude, Gemini, GPT-4o, Grok, and Perplexity.
