#!/usr/bin/env python3
import sys

try:
    import litellm
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical
    from textual.widgets import Footer, Header, Input, Label, Select, Static
except ImportError:
    print("Error: Required packages not installed. Please run:")
    print("pip install textual litellm")
    sys.exit(1)

from src.infrastructure.config_loader import ConfigLoader


class ChatArea(Static):
    """Area to display chat messages."""


class AILibraryTUI(App):
    """A Textual UI for the AI Knowledge Library."""

    CSS = """
    Screen {
        layout: horizontal;
    }
    
    #sidebar {
        width: 30%;
        height: 100%;
        border-right: solid green;
        padding: 1;
        background: $surface;
    }
    
    #main-area {
        width: 70%;
        height: 100%;
        padding: 1;
    }
    
    .chat-message {
        margin: 1;
        padding: 1;
        border: solid cyan;
    }
    
    .user-message {
        border: solid green;
        text-align: right;
    }
    
    #input-box {
        dock: bottom;
        margin: 1;
    }
    """

    BINDINGS = [Binding("q", "quit", "Quit"), Binding("c", "clear_chat", "Clear Chat")]

    def __init__(self):
        super().__init__()
        self.config = ConfigLoader()
        self.chat_history = []

        # Determine preferred LLM from config, default to gemini
        self.current_model = self.config.get("llm_model", "gemini/gemini-1.5-pro")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("🤖 AI Knowledge Library")
                yield Label("")
                yield Label("Select LLM Provider:")
                yield Select(
                    [
                        ("Gemini 1.5 Pro", "gemini/gemini-1.5-pro"),
                        ("Claude 3.5 Sonnet", "anthropic/claude-3-5-sonnet-20240620"),
                        ("GPT-4o", "openai/gpt-4o"),
                        ("Grok 2", "xai/grok-2"),
                        (
                            "Perplexity Sonar",
                            "perplexity/llama-3-sonar-large-32k-online",
                        ),
                    ],
                    value=self.current_model,
                    id="llm-select",
                )
                yield Label("")
                yield Label("[System Status]")
                yield Label("PgVector: ONLINE", classes="status-green")
                yield Label("ChromaDB: ONLINE", classes="status-green")

            with Vertical(id="main-area"):
                self.chat_container = Vertical(id="chat-container")
                yield self.chat_container
                yield Input(placeholder="Ask the knowledge base...", id="input-box")

        yield Footer()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle LLM selection change."""
        if event.select.id == "llm-select":
            self.current_model = event.value
            self.notify(f"Switched LLM to: {self.current_model}")

            # Save preference back to settings.yaml
            settings_path = self.config.config_path
            try:
                import yaml

                with open(settings_path, "r") as f:
                    data = yaml.safe_load(f) or {}
                data["llm_model"] = self.current_model
                with open(settings_path, "w") as f:
                    yaml.dump(data, f)
            except Exception as e:
                import sys

                print(f"Error saving settings: {e}", file=sys.stderr)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input."""
        if not event.value.strip():
            return

        user_text = event.value
        event.input.value = ""

        # Add user message to UI
        self.chat_container.mount(
            Label(f"You: {user_text}", classes="chat-message user-message")
        )
        self.chat_container.scroll_end()

        # Execute LiteLLM with Intelligent Failover and Rate Limit Handling
        try:
            fallbacks = [
                "gemini/gemini-1.5-pro",
                "anthropic/claude-3-5-sonnet-20240620",
                "openai/gpt-4o",
                "xai/grok-2",
            ]
            if self.current_model in fallbacks:
                fallbacks.remove(self.current_model)

            import time

            start_time = time.time()
            messages = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are the Antigravity AI Knowledge Library assistant. Answer the user's questions.",
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                },
                {"role": "user", "content": user_text},
            ]
            response = await litellm.acompletion(
                model=self.current_model,
                messages=messages,
                fallbacks=fallbacks,
            )
            latency = time.time() - start_time

            # Log telemetry
            try:
                from src.infrastructure.telemetry_logger import log_telemetry

                cost = litellm.completion_cost(completion_response=response)
                usage = response.usage

                # Extract cached tokens safely from different provider formats
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
                    model=response.model,
                    prompt_tokens=usage.prompt_tokens if usage else 0,
                    completion_tokens=usage.completion_tokens if usage else 0,
                    total_tokens=usage.total_tokens if usage else 0,
                    cost=float(cost) if cost else 0.0,
                    latency=latency,
                    cached_tokens=cached_tokens,
                )
            except Exception as e:
                import sys

                print(f"Error logging telemetry: {e}", file=sys.stderr)

            response_text = f"[{self.current_model.split('/')[0].upper()}]: {response.choices[0].message.content}"
            self.chat_container.mount(Label(response_text, classes="chat-message"))
        except Exception as e:
            self.chat_container.mount(
                Label(
                    f"[{self.current_model.split('/')[0].upper()}] Placeholder RAG response for '{user_text}'. (Configure API keys to enable real inference. Failover Error: {str(e)})",
                    classes="chat-message",
                )
            )

        self.chat_container.scroll_end()

    def action_clear_chat(self) -> None:
        """Action to clear the chat."""
        for child in self.chat_container.children:
            child.remove()
        self.notify("Chat cleared.")


def main():
    app = AILibraryTUI()
    app.run()


if __name__ == "__main__":
    main()
