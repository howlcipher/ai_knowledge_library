# Task Journal: Preflight the provider before a run

Copy this file to `YYYY-MM-DD_<slug>.md` before starting a task (see the Working Protocol in `improvements.md`). Update and commit it at every milestone. A fresh session resumes by reading Status, the last Progress entry, and Next Step. When the task completes, move anything durable (findings, decisions, verification evidence) into the backlog Done note, the changelog, or a proper doc, then delete the journal in the task's final commit — only in-flight tasks have a journal here.

## Summary

- **Task:** Backlog item 5 — Preflight the provider before a run
- **Status:** In progress
- **Started:** 2026-07-18
- **Agent and model:** Claude Code / Fable 5

## Pre-Flight Re-Evaluation

- **Model choice:** Session is already running on Fable 5 (Claude Pro). Table suggests Sonnet 5; switching models or delegating to a subagent would cost a cold-start context reload for a small, well-scoped change, so staying inline on the current session model. Available: Claude Pro (this session), Gemini Pro (not launched), local Ollama (`qwen3:30b-instruct`, `qwen2.5vl:7b`, `nomic-embed-text` — live-checked via /api/tags).
- **Skills routed:** `software_development`, `defensive_debugging`, `test_and_verify`, `commit_and_changelog`.
- **Free tools:** `curl` for live Ollama checks; `pytest` (installed) for verification. Nothing new to install.

## Plan

- [ ] Read detail section + `documentation/multi_agent_payload_protocol.md` + routed SKILL.md files
- [ ] Add a provider preflight module: for each distinct model used by the run (tier models + default), verify the provider is reachable, the model tag exists (Ollama `/api/tags`), and a 1-token generation succeeds; fail fast with an actionable error
- [ ] Wire it into `run_payload_loop` before pass 1
- [ ] Unit tests for the preflight logic (mocked provider)
- [ ] Live verification against local Ollama: healthy model passes; bogus tag and dead server produce actionable errors without burning validation attempts
- [ ] Update backlog (Done note + status), changelog, commit, delete journal, push

## Progress Log

- 2026-07-18 — Journal opened. Ollama live check done (3 tags). Key code read: `orchestrator.py` (`run_payload_loop`), `config_loader.py` (llm_model default `gemini/gemini-1.5-pro`, tier_models fallback).

## Next Step

Read `documentation/multi_agent_payload_protocol.md` and the routed SKILL.md files, then implement the preflight module.
