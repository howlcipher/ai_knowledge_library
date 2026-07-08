#!/usr/bin/env python3
"""
orchestrator.py

Implements a Multi-Agent Orchestration loop featuring a Researcher Agent,
a QA Reviewer Agent, and a strict Human-in-the-Loop proxy for command execution,
now migrated to a formal StateGraph using LangGraph.
"""

import os
import sys
import litellm
import json
from typing import TypedDict, Any, List, Optional
from langgraph.graph import StateGraph, END

from src.infrastructure.config_loader import load_config
from src.infrastructure.telemetry_logger import log_telemetry

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
                        "cache_control": {"type": "ephemeral"}
                    }
                ]
            }
        ]
        
        full_prompt = user_prompt
        if context:
            full_prompt += f"\n\nContext:\n{context}"
            
        messages.append({"role": "user", "content": full_prompt})
        
        print(f"[{self.name}] Thinking...")
        try:
            kwargs = {
                "model": self.model,
                "messages": messages
            }
            if self.tools:
                kwargs["tools"] = self.tools

            response = litellm.completion(**kwargs)
            
            # Log telemetry
            usage = response.usage
            cost = litellm.completion_cost(completion_response=response) or 0.0
            
            cached_tokens = 0
            if usage:
                cached_tokens = getattr(usage, 'cache_read_input_tokens', 0)
                if not cached_tokens and hasattr(usage, 'prompt_tokens_details'):
                    prompt_details = getattr(usage, 'prompt_tokens_details', {})
                    if isinstance(prompt_details, dict):
                        cached_tokens = prompt_details.get('cached_tokens', 0)
                    elif hasattr(prompt_details, 'cached_tokens'):
                        cached_tokens = prompt_details.cached_tokens
                        
            log_telemetry(
                model=self.model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                cost=cost,
                latency=0.0,
                cached_tokens=cached_tokens
            )
            
            return response.choices[0].message
        except Exception as e:
            print(f"[{self.name}] Error generating response: {e}")
            return None

class Orchestrator:
    def __init__(self):
        self.cfg = load_config()
        self.default_model = self.cfg.get("llm_model", "gemini/gemini-1.5-pro")
        
        tools = [{
            "type": "function",
            "function": {
                "name": "execute_bash_command",
                "description": "Execute a bash command on the host system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The exact bash command to run."
                        }
                    },
                    "required": ["command"]
                }
            }
        }]

        self.researcher = Agent(
            name="Researcher",
            system_prompt="You are a meticulous researcher. Your goal is to formulate comprehensive plans and answers based on user requests. Use the execute_bash_command tool if you need to execute system commands.",
            model=self.default_model,
            tools=tools
        )
        
        self.qa = Agent(
            name="QA_Reviewer",
            system_prompt="You are a strict QA reviewer. Evaluate the provided plan or answer. If it is high quality and safe, output exactly 'APPROVED'. If it is flawed, insecure, or hallucinates, explain why and request a revision.",
            model=self.default_model
        )
        self.graph = self._build_graph()
        
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        def researcher_node(state: AgentState):
            iteration = state.get("iteration", 1)
            print(f"\n--- Iteration {iteration} ---")
            message = self.researcher.generate_response(state["query"], context=state.get("context", ""))
            if not message:
                print("[Orchestrator] Failed to get response from Researcher.")
                return {"draft_content": "", "tool_calls": None}
            
            draft_content = message.content or ""
            tool_calls = getattr(message, 'tool_calls', None)
            
            print(f"\n[Researcher Draft]:\n{draft_content}")
            if tool_calls:
                print("[Researcher requested tool executions]")
            print()
            return {"draft_content": draft_content, "tool_calls": tool_calls}

        def qa_node(state: AgentState):
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
            
            if "APPROVED" in qa_feedback.strip().upper():
                print("[Orchestrator] QA approved the draft.")
                return {"qa_approved": True}
                
            print("[Orchestrator] QA rejected the draft. Sending back for revision...")
            new_context = f"Previous Draft:\n{draft_content}\n\nQA Feedback:\n{qa_feedback}\n\nPlease revise your draft to address the QA Feedback."
            return {"qa_approved": False, "context": new_context, "iteration": state.get("iteration", 1) + 1}
            
        def should_continue(state: AgentState):
            if state.get("qa_approved", False):
                return END
            if state.get("iteration", 1) > state.get("max_iterations", 3):
                print("[Orchestrator] Maximum iterations reached. Proceeding with latest draft.")
                return END
            return "researcher"

        workflow.add_node("researcher", researcher_node)
        workflow.add_node("qa", qa_node)
        
        workflow.set_entry_point("researcher")
        workflow.add_edge("researcher", "qa")
        workflow.add_conditional_edges("qa", should_continue, {"researcher": "researcher", END: END})
        
        return workflow.compile()
        
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
        
        while True:
            auth = input("\n[HumanProxy] Do you authorize this action? [Y/n]: ").strip().lower()
            if auth in ['', 'y', 'yes']:
                print("[HumanProxy] Action authorized.")
                return True
            elif auth in ['n', 'no']:
                print("[HumanProxy] Action REJECTED.")
                return False

    def run_loop(self, user_query: str):
        print(f"\n=== Starting Multi-Agent Orchestration ===")
        print(f"Query: {user_query}\n")
        
        initial_state = {
            "query": user_query,
            "context": "",
            "draft_content": "",
            "tool_calls": None,
            "iteration": 1,
            "qa_approved": False,
            "max_iterations": 3
        }
        
        final_state = self.graph.invoke(initial_state)
        
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
                            cmd = args.get('command')
                            print(f"\n$ {cmd}")
                            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)  # nosec B602
                            if result.stdout:
                                print(result.stdout)
                            if result.stderr:
                                print(result.stderr, file=sys.stderr)
                        except Exception as e:
                            print(f"Error executing command: {e}", file=sys.stderr)
        else:
            print("\n[Orchestrator] Task aborted due to human rejection.")

def main():
    if len(sys.argv) < 2:
        print("Usage: orchestrator.py <query>")
        sys.exit(1)
        
    query = " ".join(sys.argv[1:])
    orchestrator = Orchestrator()
    orchestrator.run_loop(query)

if __name__ == "__main__":
    main()
