#!/usr/bin/env python3
"""
orchestrator.py

Implements a Multi-Agent Orchestration loop featuring a Researcher Agent,
a QA Reviewer Agent, and a strict Human-in-the-Loop proxy for command execution,
now migrated to a formal StateGraph using LangGraph.
"""

import json
import os
import sys
from typing import Any, List, Optional, TypedDict

import litellm
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langchain_core.runnables.config import RunnableConfig
from langsmith import Client

from src.core.claude_code_backend import CLAUDE_CODE_MODEL, ClaudeCodeAgent
from src.infrastructure.config_loader import default_loader, load_config
from src.infrastructure.telemetry_logger import log_gate_failure, log_telemetry
import atexit


class AgentState(TypedDict):
    query: str
    context: str
    draft_content: str
    tool_calls: Optional[List[Any]]
    iteration: int
    qa_approved: bool
    max_iterations: int


def tier_setting(overrides: dict, tier: int, default):
    """Resolves a per tier override (key ``tier_<n>``), falling back to the
    default when the override is missing, empty, or zero."""
    return (overrides or {}).get(f"tier_{tier}") or default


def build_tier_agent(
    name: str,
    prompt: str,
    model: str,
    timeout: Optional[float] = None,
    response_format: Optional[dict] = None,
):
    """Constructs the agent for one payload-pipeline tier: a ClaudeCodeAgent
    when the resolved model is the CLAUDE_CODE_MODEL sentinel (shells out to
    headless Claude Code instead of LiteLLM), otherwise the usual
    LiteLLM-backed Agent."""
    if model == CLAUDE_CODE_MODEL:
        return ClaudeCodeAgent(
            name, prompt, model, timeout=timeout, response_format=response_format
        )
    return Agent(name, prompt, model, timeout=timeout, response_format=response_format)


class Agent:
    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: str,
        tools: list = None,
        timeout: Optional[float] = None,
        response_format: Optional[dict] = None,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.tools = tools
        self.timeout = timeout
        self.response_format = response_format

    def generate_response(
        self, user_prompt: str, context: str = "", raise_errors: bool = False
    ):
        # Anthropic explicit caching injection on system message
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": self.system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
            }
        ]

        full_prompt = user_prompt
        if context:
            full_prompt += f"\n\nContext:\n{context}"

        messages.append({"role": "user", "content": full_prompt})

        print(f"[{self.name}] Thinking...")
        try:
            kwargs = {"model": self.model, "messages": messages}
            if self.tools:
                kwargs["tools"] = self.tools
            if self.timeout:
                kwargs["timeout"] = self.timeout
            if self.response_format:
                kwargs["response_format"] = self.response_format

            response = litellm.completion(**kwargs)
        except Exception as e:
            print(f"[{self.name}] Error generating response: {e}")
            if raise_errors:
                raise
            return None

        try:
            usage = response.usage
            cost = litellm.completion_cost(completion_response=response) or 0.0

            cached_tokens = 0
            if usage:
                cached_tokens = getattr(usage, "cache_read_input_tokens", 0)
                if not cached_tokens and hasattr(usage, "prompt_tokens_details"):
                    prompt_details = getattr(usage, "prompt_tokens_details", {})
                    if isinstance(prompt_details, dict):
                        cached_tokens = prompt_details.get("cached_tokens", 0)
                    elif hasattr(prompt_details, "cached_tokens"):
                        cached_tokens = prompt_details.cached_tokens

            log_telemetry(
                model=self.model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                cost=cost,
                latency=0.0,
                cached_tokens=cached_tokens,
            )
        except Exception as e:
            # A telemetry failure must never discard a successful completion.
            print(f"[{self.name}] Telemetry logging failed: {e}")

        return response.choices[0].message


class Orchestrator:
    def __init__(self):
        self.cfg = load_config()
        self.default_model = self.cfg.get("llm_model", "gemini/gemini-1.5-pro")

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "execute_bash_command",
                    "description": "Execute a bash command on the host system.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "The exact bash command to run.",
                            }
                        },
                        "required": ["command"],
                    },
                },
            }
        ]

        # Try to load configured MCP servers
        self.mcp_clients = {}
        mcp_servers_config = self.cfg.get("mcp_servers", {})
        active_mcps = self.cfg.get("active_mcps", [])

        if mcp_servers_config:
            from src.core.mcp_client import SyncMCPClient
            for name, config in mcp_servers_config.items():
                if active_mcps and name not in active_mcps:
                    continue
                print(f"[Orchestrator] Connecting to MCP Server: {name}...")
                try:
                    client = SyncMCPClient(
                        name=name,
                        command=config.get("command"),
                        args=config.get("args", []),
                        env=config.get("env")
                    )
                    client.connect()
                    self.mcp_clients[name] = client
                    
                    # Fetch tools and append to litellm tools
                    mcp_tools = client.get_tools()
                    for t in mcp_tools:
                        tools.append({
                            "type": "function",
                            "function": {
                                "name": f"mcp_{name}_{t.name}",
                                "description": f"(MCP Tool from {name}) {t.description}",
                                "parameters": t.inputSchema
                            }
                        })
                    print(f"[Orchestrator] Loaded {len(mcp_tools)} tools from {name}.")
                except Exception as e:
                    print(f"[Orchestrator] Failed to load MCP Server {name}: {e}")

        global_timeout = self.cfg.get("llm_timeout", 600.0)

        self.researcher = Agent(
            name="Researcher",
            system_prompt="You are a meticulous researcher. Your goal is to formulate comprehensive plans and answers based on user requests. Use the execute_bash_command tool if you need to execute system commands. You also have access to various MCP tools if configured.",
            model=self.default_model,
            tools=tools,
            timeout=global_timeout,
        )

        self.qa = Agent(
            name="QA_Reviewer",
            system_prompt="You are a strict QA reviewer. Evaluate the provided plan or answer. If it is high quality and safe, output exactly 'APPROVED'. If it is flawed, insecure, or hallucinates, explain why and request a revision.",
            model=self.default_model,
            timeout=global_timeout,
        )

        self.technical_writer = Agent(
            name="Technical_Writer",
            system_prompt="You are an expert technical writer and stealth AI copywriter. Your job is to rewrite documentation and reports so they pass as human-written by AI detectors. You must significantly increase 'burstiness' by heavily varying sentence length and structure, and increase 'perplexity' by avoiding standard predictable AI vocabulary (e.g. 'delve', 'moreover', 'testament'). Keep all technical facts exactly the same, just change the tone and structure to be highly human, occasionally conversational, but still professional. Return ONLY the rewritten text, nothing else.",
            model=self.default_model,
            timeout=global_timeout,
        )

        try:
            from src.core.skill_router import SkillRouter

            self.skill_router = SkillRouter(cfg=self.cfg)
        except Exception as e:
            print(f"[Orchestrator] Skill router unavailable: {e}")
            self.skill_router = None

        self.payload_cfg = self.cfg.get("payload_pipeline", {}) or {}

        self.graph = self._build_graph()
        atexit.register(self.shutdown)

    def shutdown(self):
        for name, client in self.mcp_clients.items():
            print(f"[Orchestrator] Shutting down MCP Server: {name}...")
            try:
                client.close()
            except Exception:
                pass

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        def researcher_node(state: AgentState):
            iteration = state.get("iteration", 1)
            print(f"\n--- Iteration {iteration} ---")
            
            from src.core.transport_retry import call_with_transport_retry, ProviderTransportError
            try:
                message = call_with_transport_retry(
                    lambda: self.researcher.generate_response(
                        state["query"], context=state.get("context", ""), raise_errors=True
                    ),
                    retries=self.payload_cfg.get("transport_retries", 2),
                    backoff=self.payload_cfg.get("transport_backoff", 2.0),
                    model=self.researcher.model,
                )
            except ProviderTransportError as e:
                print(f"[Orchestrator] Researcher transport error: {e}")
                message = None

            if not message:
                print("[Orchestrator] Failed to get response from Researcher.")
                return {"draft_content": "", "tool_calls": None}

            draft_content = message.content or ""
            tool_calls = getattr(message, "tool_calls", None)

            print(f"\n[Researcher Draft]:\n{draft_content}")
            if tool_calls:
                print("[Researcher requested tool executions]")
            print()
            return {"draft_content": draft_content, "tool_calls": tool_calls}

        def qa_node(state: AgentState, config: RunnableConfig):
            draft_content = state["draft_content"]
            tool_calls = state["tool_calls"]

            qa_input = f"Review the following draft:\n\n{draft_content}"
            if tool_calls:
                qa_input += f"\n\nTool calls proposed:\n{tool_calls}"

            from src.core.transport_retry import call_with_transport_retry, ProviderTransportError
            try:
                qa_message = call_with_transport_retry(
                    lambda: self.qa.generate_response(qa_input, raise_errors=True),
                    retries=self.payload_cfg.get("transport_retries", 2),
                    backoff=self.payload_cfg.get("transport_backoff", 2.0),
                    model=self.qa.model,
                )
            except ProviderTransportError as e:
                print(f"[Orchestrator] QA transport error: {e}")
                qa_message = None

            if not qa_message:
                print("[Orchestrator] Failed to get response from QA.")
                return {"qa_approved": False, "context": ""}

            qa_feedback = qa_message.content or ""
            print(f"\n[QA Feedback]:\n{qa_feedback}\n")

            run_id = config.get("configurable", {}).get("run_id") or config.get(
                "run_id"
            )
            ls_client = None
            try:
                ls_client = Client()
            except Exception:
                pass  # Ignore if LangSmith is not configured

            if "APPROVED" in qa_feedback.strip().upper():
                print("[Orchestrator] QA approved the draft.")
                if ls_client and run_id:
                    ls_client.create_feedback(run_id, key="qa_approval", score=1.0)
                return {"qa_approved": True}

            print("[Orchestrator] QA rejected the draft. Sending back for revision...")
            if ls_client and run_id:
                ls_client.create_feedback(
                    run_id, key="qa_approval", score=0.0, comment=qa_feedback
                )

            new_context = f"Previous Draft:\n{draft_content}\n\nQA Feedback:\n{qa_feedback}\n\nPlease revise your draft to address the QA Feedback."
            return {
                "qa_approved": False,
                "context": new_context,
                "iteration": state.get("iteration", 1) + 1,
            }

        def humanize_node(state: AgentState):
            print("\n--- Humanizing Output (Stealth Mode) ---")
            draft_content = state["draft_content"]
            prompt = f"Please humanize the following technical report/documentation. Maintain all facts but drastically increase burstiness and perplexity to bypass AI detectors:\n\n{draft_content}"
            
            from src.core.transport_retry import call_with_transport_retry, ProviderTransportError
            try:
                message = call_with_transport_retry(
                    lambda: self.technical_writer.generate_response(prompt, raise_errors=True),
                    retries=self.payload_cfg.get("transport_retries", 2),
                    backoff=self.payload_cfg.get("transport_backoff", 2.0),
                    model=self.technical_writer.model,
                )
            except ProviderTransportError as e:
                print(f"[Orchestrator] Technical_Writer transport error: {e}")
                message = None

            if message and message.content:
                print("\n[Technical_Writer] Successfully humanized the draft.")
                return {"draft_content": message.content}
            return {"draft_content": draft_content}

        def should_continue(state: AgentState):
            if state.get("qa_approved", False):
                return "humanize"
            if state.get("iteration", 1) > state.get("max_iterations", 3):
                print(
                    "[Orchestrator] Maximum iterations reached. Proceeding with latest draft."
                )
                return "humanize"
            return "researcher"

        workflow.add_node("researcher", researcher_node)
        workflow.add_node("qa", qa_node)
        workflow.add_node("humanize", humanize_node)

        workflow.set_entry_point("researcher")
        workflow.add_edge("researcher", "qa")
        workflow.add_edge("humanize", END)
        workflow.add_conditional_edges(
            "qa", should_continue, {"researcher": "researcher", "humanize": "humanize"}
        )

        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)

    def human_proxy_intercept(self, tool_calls) -> bool:
        """Intercepts executable tool calls and requires human approval."""
        if not tool_calls:
            return True

        print("\n[HumanProxy] ⚠️  EXECUTABLE COMMAND DETECTED ⚠️")
        print("The agent is proposing the following action(s):")

        for call in tool_calls:
            if call.function.name == "execute_bash_command":
                try:
                    args = json.loads(call.function.arguments)
                    print(f"  > {args.get('command')}")
                except Exception:
                    print(f"  > [Failed to parse arguments: {call.function.arguments}]")
            elif call.function.name.startswith("mcp_"):
                try:
                    args = json.loads(call.function.arguments)
                    print(f"  > [MCP Plugin: {call.function.name}] args: {args}")
                except Exception:
                    print(f"  > [MCP Plugin: {call.function.name}] Failed to parse args")

        while True:
            auth = (
                input("\n[HumanProxy] Do you authorize this action? [Y/n]: ")
                .strip()
                .lower()
            )
            if auth in ["", "y", "yes"]:
                print("[HumanProxy] Action authorized.")
                return True
            elif auth in ["n", "no"]:
                print("[HumanProxy] Action REJECTED.")
                return False

    def _persist_payload(self, payload: dict):
        """Writes one JSON file per pass under the task id for replay and audit."""
        try:
            artifact_dir = os.path.join(
                default_loader.get_repo_root(),
                self.payload_cfg.get("artifact_dir", "logs/payloads"),
                payload["task_id"],
            )
            os.makedirs(artifact_dir, exist_ok=True)
            pass_number = payload["pipeline"]["pass_number"]
            path = os.path.join(artifact_dir, f"pass_{pass_number}.json")
            with open(path, "w", encoding="utf8") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            print(f"[Orchestrator] Failed to persist payload: {e}")

    def run_payload_loop(self, user_query: str):
        """
        Tiered 3 pass pipeline with a code level validation gate at every
        boundary, per documentation/multi_agent_payload_protocol.md. Agents
        exchange AgentTaskPayload JSON; tool calls are disabled because they
        conflict with the JSON only output contract.
        """
        from src.core.tier_prompts import TIER1_PROMPT, TIER2_PROMPT, TIER3_PROMPT
        from src.core.transport_retry import (
            ProviderTransportError,
            call_with_transport_retry,
        )
        from src.core.validation_gate import ValidationGate, build_initial_payload

        print("\n=== Starting 3 Pass Payload Pipeline ===")
        print(f"Query: {user_query}\n")

        gate = ValidationGate(max_attempts=self.payload_cfg.get("max_attempts", 3))

        # Dispatch: route skills once; they ride in routing.skills for all passes.
        # Per-pass skill directive context (respecting each skill's optional
        # pipeline_pass) is built fresh inside the pass loop below.
        skills = []
        if self.skill_router:
            try:
                for skill, score, reason in self.skill_router.route(user_query):
                    entry = {"name": skill.name}
                    if reason.startswith("trigger"):
                        entry["matched_by"] = "trigger"
                        if "'" in reason:
                            entry["trigger"] = reason.split("'")[1]
                    else:
                        entry["matched_by"] = "semantic"
                        entry["score"] = round(score, 4)
                    skills.append(entry)
            except Exception as e:
                print(f"[Orchestrator] Skill routing failed: {e}")

        domain = skills[0]["name"] if skills else "general"
        initial = build_initial_payload(user_query, domain, skills)

        tier_models = self.payload_cfg.get("tier_models", {}) or {}
        tier_timeouts = self.payload_cfg.get("tier_timeouts", {}) or {}
        default_timeout = self.payload_cfg.get("timeout", 600.0)

        def model_for(tier: int) -> str:
            return tier_setting(tier_models, tier, self.default_model)

        def timeout_for(tier: int) -> float:
            return tier_setting(tier_timeouts, tier, default_timeout)

        if self.payload_cfg.get("preflight", True):
            from src.core.provider_preflight import preflight_models

            print("[Preflight] Checking providers before pass 1...")
            preflight = preflight_models(
                [model_for(3), model_for(2), model_for(1)],
                timeout=self.payload_cfg.get("preflight_timeout", 120.0),
            )
            if not preflight.ok:
                for error in preflight.errors:
                    print(f"[Preflight] {error}")
                print(
                    "[Orchestrator] Aborting run: provider preflight failed "
                    "before any validation attempt was spent."
                )
                return None
            print(f"[Preflight] OK ({', '.join(preflight.checked_models)})")

        # Provider enforced structured outputs: hand the payload schema to the
        # provider so shape compliance is mechanical. The gate stays
        # authoritative; the prompt contract stays as defense in depth.
        response_format = None
        if self.payload_cfg.get("structured_outputs", True):
            from src.core.structured_output import payload_response_format

            try:
                response_format = payload_response_format()
            except Exception as e:
                print(
                    "[Orchestrator] Structured outputs disabled for this run "
                    f"(failed to build response_format): {e}"
                )

        def tier_agent(name, prompt, tier):
            return build_tier_agent(
                name,
                prompt,
                model_for(tier),
                timeout=timeout_for(tier),
                response_format=response_format,
            )

        tiers = [
            (1, tier_agent("Tier3_Executor", TIER3_PROMPT, 3)),
            (2, tier_agent("Tier2_Specialist", TIER2_PROMPT, 2)),
            (3, tier_agent("Tier1_Orchestrator", TIER1_PROMPT, 1)),
        ]

        transport_retries = self.payload_cfg.get("transport_retries", 2)
        transport_backoff = self.payload_cfg.get("transport_backoff", 2.0)

        payload = initial
        for pass_number, agent in tiers:
            print(f"\n--- Pass {pass_number}: {agent.name} ---")

            # Build skill context specific to this pipeline pass
            skill_context = ""
            if self.skill_router:
                try:
                    skill_context = self.skill_router.build_context(user_query, pipeline_pass=pass_number)
                except Exception as e:
                    print(f"[Orchestrator] Skill context build failed for pass {pass_number}: {e}")

            def call_fn(feedback, agent=agent, payload=payload):
                user_msg = json.dumps(payload)
                if skill_context:
                    user_msg += f"\n\nSKILL DIRECTIVES (binding):\n{skill_context}"
                if feedback:
                    user_msg += f"\n\n{feedback}"
                # Provider exceptions are retried here with backoff so they
                # never reach the gate as fake parse failures; on exhaustion
                # ProviderTransportError aborts the pass without spending a
                # validation attempt.
                message = call_with_transport_retry(
                    lambda: agent.generate_response(user_msg, raise_errors=True),
                    retries=transport_retries,
                    backoff=transport_backoff,
                    model=agent.model,
                )
                return message.content if message and message.content else ""

            def on_attempt_failure(attempt, stage, errors, agent=agent, pass_number=pass_number):
                try:
                    log_gate_failure(
                        agent.model, pass_number, attempt, stage, "; ".join(errors)[:2000]
                    )
                except Exception as e:
                    print(f"[Orchestrator] Failed to log gate failure telemetry: {e}")

            try:
                result = gate.run(
                    call_fn,
                    prev=payload,
                    expected_pass=pass_number,
                    on_attempt_failure=on_attempt_failure,
                )
            except ProviderTransportError as e:
                print(
                    f"[Orchestrator] Pass {pass_number} aborted: provider for "
                    f"{e.model} unavailable after "
                    f"{len(e.attempt_errors)} transport attempts: {e}"
                )
                failed = gate.build_failed_payload(
                    payload,
                    [str(e)],
                    stage="transport",
                    attempt=0,
                    code="UPSTREAM_UNAVAILABLE",
                    failure_vector="llm_transport.completion",
                    context={
                        "model": e.model,
                        "transport_attempts": len(e.attempt_errors),
                        "attempt_errors": e.attempt_errors,
                    },
                )
                if failed:
                    self._persist_payload(failed)
                return failed
            if result.payload:
                self._persist_payload(result.payload)
            if not result.ok:
                print(
                    f"[Orchestrator] Pass {pass_number} failed validation after "
                    f"{result.attempts} attempts: {result.errors[0]}"
                )
                return result.payload
            payload = result.payload
            verdict = (payload.get("critique") or {}).get("verdict", "n/a")
            print(
                f"[Gate] Pass {pass_number} valid on attempt {result.attempts} "
                f"(verdict: {verdict})"
            )

        print(f"\n[Orchestrator] Final status: {payload['pipeline']['status']}")
        print("\n[Orchestrator] Final Output:")
        print(payload["content"]["body"])
        return payload

    def run_loop(self, user_query: str):
        if self.payload_cfg.get("enabled", False):
            return self.run_payload_loop(user_query)

        if self.cfg.get("preflight", True):
            from src.core.provider_preflight import preflight_models

            print("[Preflight] Checking providers before multi-agent loop...")
            preflight = preflight_models(
                [self.default_model],
                timeout=self.payload_cfg.get("preflight_timeout", 120.0),
            )
            if not preflight.ok:
                for error in preflight.errors:
                    print(f"[Preflight] {error}")
                print(
                    "[Orchestrator] Aborting run: provider preflight failed."
                )
                return None
            print(f"[Preflight] OK ({', '.join(preflight.checked_models)})")

        print("\n=== Starting Multi-Agent Orchestration ===")
        print(f"Query: {user_query}\n")

        config = {"configurable": {"thread_id": "default"}}

        # 1. Retrieve persistent memory from previous session if it exists
        past_state = self.graph.get_state(config)
        past_context = ""
        if past_state and past_state.values:
            past_context = past_state.values.get("draft_content", "")

        # 2. Route library skills relevant to this query into the context
        skill_context = ""
        if self.skill_router:
            try:
                skill_context = self.skill_router.build_context(user_query)
            except Exception as e:
                print(f"[Orchestrator] Skill routing failed: {e}")

        context_parts = []
        if skill_context:
            context_parts.append(skill_context)
        if past_context:
            context_parts.append(f"Previous conversation context:\n{past_context}")

        initial_state = {
            "query": user_query,
            "context": "\n\n".join(context_parts),
            "draft_content": "",
            "tool_calls": None,
            "iteration": 1,
            "qa_approved": False,
            "max_iterations": 3,
        }

        final_state = self.graph.invoke(initial_state, config=config)

        current_draft_content = final_state.get("draft_content", "")
        current_tool_calls = final_state.get("tool_calls", None)

        # 3. Human-in-the-loop Execution Guard
        approved = self.human_proxy_intercept(current_tool_calls)

        if approved:
            print("\n[Orchestrator] Final Output:")
            print(current_draft_content)
            if current_tool_calls:
                import subprocess

                print(f"\n[Executing {len(current_tool_calls)} tool calls...]")
                for call in current_tool_calls:
                    if call.function.name == "execute_bash_command":
                        try:
                            args = json.loads(call.function.arguments)
                            cmd = args.get("command")
                            print(f"\n$ {cmd}")
                            result = subprocess.run(
                                cmd, shell=True, capture_output=True, text=True
                            )  # nosec B602
                            if result.stdout:
                                print(result.stdout)
                            if result.stderr:
                                print(result.stderr, file=sys.stderr)
                        except Exception as e:
                            print(f"Error executing command: {e}", file=sys.stderr)
                    elif call.function.name.startswith("mcp_"):
                        try:
                            # format: mcp_{server_name}_{tool_name}
                            parts = call.function.name.split("_", 2)
                            if len(parts) == 3:
                                _, server_name, tool_name = parts
                                if server_name in self.mcp_clients:
                                    args = json.loads(call.function.arguments)
                                    print(f"\n$ Calling MCP tool '{tool_name}' on '{server_name}'...")
                                    result = self.mcp_clients[server_name].call_tool(tool_name, args)
                                    
                                    # Output the result content
                                    if hasattr(result, 'content'):
                                        for content_block in result.content:
                                            if hasattr(content_block, 'text'):
                                                print(content_block.text)
                                            else:
                                                print(content_block)
                                    else:
                                        print(result)
                                else:
                                    print(f"Error: Unknown MCP server {server_name}")
                        except Exception as e:
                            print(f"Error executing MCP tool: {e}", file=sys.stderr)
        else:
            print("\n[Orchestrator] Task aborted due to human rejection.")


def main():
    print("Welcome to the AI Knowledge Library Orchestrator.")
    print("Type 'exit' or 'quit' to stop.")

    orchestrator = Orchestrator()

    args = sys.argv[1:]
    if "--payload" in args:
        args.remove("--payload")
        orchestrator.payload_cfg = dict(orchestrator.payload_cfg, enabled=True)

    # Check if a single query was passed via arguments
    if args:
        query = " ".join(args)
        orchestrator.run_loop(query)
        return

    # Otherwise enter interactive mode
    while True:
        try:
            query = input("\nUser> ")
            if query.lower() in ["exit", "quit"]:
                break
            if not query.strip():
                continue
            orchestrator.run_loop(query)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()
