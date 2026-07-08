#!/usr/bin/env python3
"""
orchestrator.py

Implements a Multi-Agent Orchestration loop featuring a Researcher Agent,
a QA Reviewer Agent, and a strict Human-in-the-Loop proxy for command execution.
"""

import os
import sys
import litellm
import json

# Ensure project root is in the path for module loading
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
if repo_root not in sys.path:
    sys.path.append(repo_root)

from config.loader import load_config
from tools.telemetry_logger import log_telemetry

class Agent:
    def __init__(self, name: str, system_prompt: str, model: str):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        
    def generate_response(self, user_prompt: str, context: str = "") -> str:
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        full_prompt = user_prompt
        if context:
            full_prompt += f"\n\nContext:\n{context}"
            
        messages.append({"role": "user", "content": full_prompt})
        
        print(f"[{self.name}] Thinking...")
        try:
            response = litellm.completion(
                model=self.model,
                messages=messages
            )
            
            # Log telemetry
            usage = response.usage
            cost = litellm.completion_cost(completion_response=response) or 0.0
            log_telemetry(
                model=self.model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                cost=cost,
                latency=0.0 # Latency not tracked here yet, can be added later
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"[{self.name}] Error generating response: {e}")
            return ""

class Orchestrator:
    def __init__(self):
        self.cfg = load_config()
        self.default_model = self.cfg.get("llm_model", "gemini/gemini-1.5-pro")
        
        self.researcher = Agent(
            name="Researcher",
            system_prompt="You are a meticulous researcher. Your goal is to formulate comprehensive plans and answers based on user requests. If you propose executing any commands on the system, wrap them in a markdown code block labeled 'bash'.",
            model=self.default_model
        )
        
        self.qa = Agent(
            name="QA_Reviewer",
            system_prompt="You are a strict QA reviewer. Evaluate the provided plan or answer. If it is high quality and safe, output exactly 'APPROVED'. If it is flawed, insecure, or hallucinates, explain why and request a revision.",
            model=self.default_model
        )
        
    def human_proxy_intercept(self, content: str) -> bool:
        """Intercepts executable content and requires human approval."""
        if "```bash" in content or "```sh" in content:
            print("\n[HumanProxy] ⚠️  EXECUTABLE COMMAND DETECTED ⚠️")
            print("The agent is proposing the following action(s):")
            
            # Simple extraction for display
            lines = content.split('\n')
            in_block = False
            for line in lines:
                if line.startswith("```bash") or line.startswith("```sh"):
                    in_block = True
                    continue
                if line.startswith("```") and in_block:
                    in_block = False
                    continue
                if in_block:
                    print(f"  > {line}")
            
            while True:
                auth = input("\n[HumanProxy] Do you authorize this action? [Y/n]: ").strip().lower()
                if auth in ['', 'y', 'yes']:
                    print("[HumanProxy] Action authorized.")
                    return True
                elif auth in ['n', 'no']:
                    print("[HumanProxy] Action REJECTED.")
                    return False
        
        # No actionable commands detected, auto-approve
        return True

    def run_loop(self, user_query: str):
        print(f"\n=== Starting Multi-Agent Orchestration ===")
        print(f"Query: {user_query}\n")
        
        iteration = 1
        max_iterations = 3
        current_draft = ""
        context = ""
        
        while iteration <= max_iterations:
            print(f"\n--- Iteration {iteration} ---")
            
            # 1. Researcher drafts response
            current_draft = self.researcher.generate_response(user_query, context=context)
            print(f"\n[Researcher Draft]:\n{current_draft}\n")
            
            # 2. QA Reviewer evaluates
            qa_feedback = self.qa.generate_response(f"Review the following draft:\n\n{current_draft}")
            print(f"\n[QA Feedback]:\n{qa_feedback}\n")
            
            if "APPROVED" in qa_feedback.strip().upper():
                print("[Orchestrator] QA approved the draft.")
                break
                
            print("[Orchestrator] QA rejected the draft. Sending back for revision...")
            context = f"Previous draft failed QA. QA Feedback: {qa_feedback}"
            iteration += 1
            
        if iteration > max_iterations:
            print("[Orchestrator] Maximum iterations reached. Proceeding with latest draft.")
            
        # 3. Human-in-the-loop Execution Guard
        approved = self.human_proxy_intercept(current_draft)
        
        if approved:
            print("\n[Orchestrator] Final Output:")
            print(current_draft)
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
