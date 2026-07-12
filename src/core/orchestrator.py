#!/usr/bin/env python3
"""
orchestrator.py

Implements a Multi-Agent Orchestration loop featuring a Researcher Agent,
a QA Reviewer Agent, and a strict Human-in-the-Loop proxy for command execution,
now migrated to a formal StateGraph using LangGraph.
"""

import json
import sys
from typing import Any, List, Optional, TypedDict

import litellm
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langchain_core.runnables.config import RunnableConfig
from langsmith import Client

from src.infrastructure.config_loader import load_config
from src.infrastructure.telemetry_logger import log_telemetry
import atexit


class AgentState(TypedDict):
    query: str
    context: str
    draft_content: str
    tool_calls: Optional[List[Any]]
    iteration: int
    qa_approved: bool
    max_iterations: int


class Agent:
    def __init__(self, name: str, system_prompt: str, model: str, tools: list = None):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.tools = tools

    def generate_response(self, user_prompt: str, context: str = ""):
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

            response = litellm.completion(**kwargs)

            # Log telemetry
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

            return response.choices[0].message
        except Exception as e:
            print(f"[{self.name}] Error generating response: {e}")
            return None


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
        if mcp_servers_config:
            from src.core.mcp_client import SyncMCPClient
            for name, config in mcp_servers_config.items():
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

        self.researcher = Agent(
            name="Researcher",
            system_prompt="You are a meticulous researcher. Your goal is to formulate comprehensive plans and answers based on user requests. Use the execute_bash_command tool if you need to execute system commands. You also have access to various MCP tools if configured.",
            model=self.default_model,
            tools=tools,
        )

        self.qa = Agent(
            name="QA_Reviewer",
            system_prompt="You are a strict QA reviewer. Evaluate the provided plan or answer. If it is high quality and safe, output exactly 'APPROVED'. If it is flawed, insecure, or hallucinates, explain why and request a revision.",
            model=self.default_model,
        )

        self.technical_writer = Agent(
            name="Technical_Writer",
            system_prompt="You are an expert technical writer and stealth AI copywriter. Your job is to rewrite documentation and reports so they pass as human-written by AI detectors. You must significantly increase 'burstiness' by heavily varying sentence length and structure, and increase 'perplexity' by avoiding standard predictable AI vocabulary (e.g. 'delve', 'moreover', 'testament'). Keep all technical facts exactly the same, just change the tone and structure to be highly human, occasionally conversational, but still professional. Return ONLY the rewritten text, nothing else.",
            model=self.default_model,
        )

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
            message = self.researcher.generate_response(
                state["query"], context=state.get("context", "")
            )
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

            qa_message = self.qa.generate_response(qa_input)
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
            message = self.technical_writer.generate_response(prompt)
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

    def run_loop(self, user_query: str):
        print("\n=== Starting Multi-Agent Orchestration ===")
        print(f"Query: {user_query}\n")

        config = {"configurable": {"thread_id": "default"}}

        # 1. Retrieve persistent memory from previous session if it exists
        past_state = self.graph.get_state(config)
        past_context = ""
        if past_state and past_state.values:
            past_context = past_state.values.get("draft_content", "")

        initial_state = {
            "query": user_query,
            "context": (
                f"Previous conversation context:\n{past_context}"
                if past_context
                else ""
            ),
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

    # Check if a single query was passed via arguments
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
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
