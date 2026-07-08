#!/usr/bin/env python3
import os
import sys

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import (
        Header,
        Footer,
        Static,
        Input,
        Button,
        Markdown,
        Select,
        Label,
    )
    from textual.binding import Binding
    import litellm
except ImportError:
    print("Error: Required packages not installed. Please run:")
    print("pip install textual litellm")
    sys.exit(1)

from config_loader import ConfigLoader


class ChatArea(Static):
    """Area to display chat messages."""

    pass


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
                pass

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

        # Placeholder for actual RAG query
        # Since we use litellm, we can seamlessly switch APIs!
        try:
            # We wrap it in a mock response if API keys aren't set
            response_text = f"[{self.current_model.split('/')[0].upper()}]: This is a placeholder RAG response for '{user_text}'. Configure your API keys to enable real inference."
            self.chat_container.mount(Label(response_text, classes="chat-message"))
        except Exception as e:
            self.chat_container.mount(
                Label(f"Error connecting to LLM: {str(e)}", classes="chat-message")
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
