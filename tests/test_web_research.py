import pytest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure the project root is in the path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
if repo_root not in sys.path:
    sys.path.append(repo_root)

from tools.web_research import (
    ContentVerifier,
    WebScraper,
    VectorStoreManager,
    TextChunker,
    main
)

class TestContentVerifier:
    def test_init_with_api_key(self):
        verifier = ContentVerifier(api_key="test_key")
        assert verifier.api_key == "test_key"

    @patch.dict(os.environ, {"GEMINI_API_KEY": "env_test_key"})
    def test_init_with_env_var(self):
        verifier = ContentVerifier()
        assert verifier.api_key == "env_test_key"

    def test_heuristic_check_too_short(self):
        verifier = ContentVerifier(api_key=None)
        is_verified, score, reason = verifier._heuristic_check("short")
        assert not is_verified
        assert score == 0
        assert "too short" in reason

    def test_heuristic_check_pass(self):
        verifier = ContentVerifier(api_key=None)
        long_text = "a" * 150
        is_verified, score, reason = verifier._heuristic_check(long_text)
        assert is_verified
        assert score == 70
        assert "passed" in reason

    @patch("tools.web_research.ContentVerifier._heuristic_check")
    def test_verify_no_api_key(self, mock_heuristic):
        mock_heuristic.return_value = (True, 70, "mocked")
        verifier = ContentVerifier(api_key=None)
        res = verifier.verify("text", "url")
        assert res == (True, 70, "mocked")
        mock_heuristic.assert_called_once_with("text")

    @patch("tools.web_research.ContentVerifier._llm_check")
    def test_verify_with_api_key(self, mock_llm):
        mock_llm.return_value = (True, 95, "llm pass")
        verifier = ContentVerifier(api_key="fake_key")
        res = verifier.verify("text", "url")
        assert res == (True, 95, "llm pass")
        mock_llm.assert_called_once_with("text", "url")

    @patch("tools.web_research.ContentVerifier._llm_check")
    def test_verify_llm_exception(self, mock_llm):
        mock_llm.side_effect = Exception("LLM Error")
        verifier = ContentVerifier(api_key="fake_key")
        is_verified, score, reason = verifier.verify("text", "url")
        assert not is_verified
        assert score == 0
        assert "LLM Error" in reason

    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_llm_check(self, mock_configure, mock_model_class):
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        mock_response = MagicMock()
        mock_response.text = '```json\n{"verified": true, "confidence": 85, "reason": "good"}\n```'
        mock_model.generate_content.return_value = mock_response

        verifier = ContentVerifier(api_key="key")
        is_verified, score, reason = verifier._llm_check("text", "url")
        
        assert is_verified
        assert score == 85
        assert reason == "good"
        mock_configure.assert_called_once_with(api_key="key")

    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_llm_check_no_json_format(self, mock_configure, mock_model_class):
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        mock_response = MagicMock()
        mock_response.text = '{"verified": false, "confidence": 10, "reason": "spam"}'
        mock_model.generate_content.return_value = mock_response

        verifier = ContentVerifier(api_key="key")
        is_verified, score, reason = verifier._llm_check("text", "url")
        
        assert not is_verified
        assert score == 10
        assert reason == "spam"


class TestWebScraper:
    @patch("requests.get")
    def test_fetch_text_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.text = "<html><body><main>Test content</main><script>ignore</script></body></html>"
        mock_get.return_value = mock_resp
        
        scraper = WebScraper()
        text = scraper.fetch_text("http://example.com")
        
        assert text == "Test content"
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_fetch_text_exception(self, mock_get):
        mock_get.side_effect = Exception("Network Error")
        
        scraper = WebScraper()
        text = scraper.fetch_text("http://example.com")
        
        assert text is None


class TestVectorStoreManager:
    @patch("tools.pgvector_backend.PgVectorStore")
    def test_insert_pgvector(self, mock_store_class):
        mock_store = MagicMock()
        mock_store_class.return_value = mock_store
        
        manager = VectorStoreManager(db_mode="pgvector")
        manager.insert(["doc1"], [{"meta": 1}], ["id1"])
        
        mock_store.upsert.assert_called_once_with(docs=["doc1"], metadatas=[{"meta": 1}])

    @patch("chromadb.PersistentClient")
    @patch("tools.web_research.get_chroma_db_path")
    def test_insert_chroma(self, mock_get_path, mock_client_class):
        mock_get_path.return_value = "/tmp/db"  # nosec B108
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        
        manager = VectorStoreManager(db_mode="chroma")
        manager.insert(["doc1", "doc2"], [{"meta": 1}, {"meta": 2}], ["id1", "id2"])
        
        mock_collection.upsert.assert_called_once()


class TestTextChunker:
    def test_chunk(self):
        text = "word " * 50 # 50 words
        chunks = TextChunker.chunk(text, max_len=20)
        assert len(chunks) > 1
        assert "word word word" in chunks[0]

    def test_chunk_empty(self):
        assert TextChunker.chunk("") == []


class TestMain:
    @patch("argparse.ArgumentParser.parse_args")
    @patch("tools.web_research.WebScraper")
    @patch("tools.web_research.ContentVerifier")
    @patch("tools.web_research.VectorStoreManager")
    @patch("tools.web_research.load_config")
    def test_main_success(self, mock_config, mock_vsm_class, mock_verifier_class, mock_scraper_class, mock_parse_args):
        mock_parse_args.return_value = MagicMock(url="http://example.com")
        
        mock_scraper = MagicMock()
        mock_scraper.fetch_text.return_value = "Long valid text content"
        mock_scraper_class.return_value = mock_scraper
        
        mock_verifier = MagicMock()
        mock_verifier.verify.return_value = (True, 90, "Good")
        mock_verifier_class.return_value = mock_verifier
        
        mock_config.return_value = {"database": {"mode": "sqlite"}}
        
        mock_vsm = MagicMock()
        mock_vsm_class.return_value = mock_vsm
        
        main()
        
        mock_scraper.fetch_text.assert_called_once_with("http://example.com")
        mock_verifier.verify.assert_called_once_with("Long valid text content", "http://example.com")
        mock_vsm.insert.assert_called_once()

    @patch("argparse.ArgumentParser.parse_args")
    @patch("tools.web_research.WebScraper")
    def test_main_no_text(self, mock_scraper_class, mock_parse_args):
        mock_parse_args.return_value = MagicMock(url="http://example.com")
        mock_scraper = MagicMock()
        mock_scraper.fetch_text.return_value = None
        mock_scraper_class.return_value = mock_scraper
        
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1

    @patch("argparse.ArgumentParser.parse_args")
    @patch("tools.web_research.WebScraper")
    @patch("tools.web_research.ContentVerifier")
    def test_main_verification_failed(self, mock_verifier_class, mock_scraper_class, mock_parse_args):
        mock_parse_args.return_value = MagicMock(url="http://example.com")
        mock_scraper = MagicMock()
        mock_scraper.fetch_text.return_value = "Bad text"
        mock_scraper_class.return_value = mock_scraper
        
        mock_verifier = MagicMock()
        mock_verifier.verify.return_value = (False, 10, "Spam")
        mock_verifier_class.return_value = mock_verifier
        
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1
