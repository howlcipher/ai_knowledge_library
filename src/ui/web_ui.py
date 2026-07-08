#!/usr/bin/env python3
"""
AI Knowledge Library Chat Interface

This script provides a Streamlit-based web interface to search
and chat with the repository context.
"""

import sys

try:
    import streamlit as st
except ImportError:
    print(
        "Error: streamlit or chromadb not installed. Run 'pip install streamlit chromadb sentence-transformers'"
    )
    sys.exit(1)


class KnowledgeUI:
    """Manages the Streamlit UI for the knowledge library."""

    def __init__(self, collection_name: str = "ai_library_knowledge"):
        """Initialize the UI with a specific collection name."""
        from src.infrastructure.vector_store_factory import VectorStoreFactory

        self.store = VectorStoreFactory.get_store()

    def render(self):
        """Render the Streamlit interface."""
        st.set_page_config(page_title="AI Knowledge Library", layout="wide")

        st.title("🤖 AI Knowledge Library")

        tab1, tab2 = st.tabs(["💬 RAG Chat", "📊 Telemetry Dashboard"])

        with tab1:
            st.markdown(
                "Search and chat with the repository context directly from your browser!"
            )
            query = st.text_input("Enter your query to search the knowledge base:")

            if st.button("Search") and query:
                self._handle_search(query)

        with tab2:
            self._render_telemetry()

    def _render_telemetry(self):
        """Render the telemetry dashboard."""
        st.header("Token & Cost Analytics Dashboard")
        st.markdown(
            "Tracks token consumption, cost estimates across LLM providers, and query latency."
        )

        try:
            from src.infrastructure.telemetry_logger import get_telemetry_data

            df = get_telemetry_data()
            if len(df) == 0:
                st.info(
                    "No telemetry data recorded yet. Try asking some questions in the chat!"
                )
                return

            # High level metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total API Calls", len(df))
            col2.metric("Total Tokens", df["total_tokens"].sum())
            col3.metric("Cached Tokens", df["cached_tokens"].sum())
            col4.metric("Total Cost", f"${df['cost'].sum():.6f}")
            col5.metric("Avg Latency", f"{df['latency_seconds'].mean():.2f}s")

            # Charts
            st.subheader("Cost Over Time")
            st.line_chart(df.set_index("timestamp")["cost"])

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("API Calls by Model")
                model_counts = df["model"].value_counts()
                st.bar_chart(model_counts)

            with col2:
                st.subheader("Latency by Model")
                latency_avg = df.groupby("model")["latency_seconds"].mean()
                st.bar_chart(latency_avg)

            st.subheader("Raw Telemetry Logs")
            st.dataframe(df)

        except Exception as e:
            st.error(f"Failed to load telemetry data: {e}")

    def _handle_search(self, query: str):
        """Execute a search query and display results."""
        with st.spinner("Searching..."):
            results = self.store.query(query, n_results=5)

            if not results:
                st.warning("No relevant results found.")
                return

            st.success("Found relevant context!")
            self._display_results(results)

    def _display_results(self, results: list):
        """Format and display search results."""
        for i, row in enumerate(results):
            content, source, dist = row
            with st.expander(
                f"Result {i+1} | Source: {source} (Confidence: {1 - dist:.2f})"
            ):
                st.write(content)


def main():
    """Main execution point for the Streamlit app."""
    ui = KnowledgeUI()
    ui.render()


if __name__ == "__main__":
    main()
