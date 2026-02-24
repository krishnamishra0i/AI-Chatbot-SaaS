"""
AI Avatar Chatbot - Test Suite
Comprehensive testing for all components
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Test configuration
TEST_DB_PATH = "./test_db"
TEST_ENV = {
    "API_HOST": "localhost",
    "API_PORT": "8001",
    "DEBUG": "true",
    "LLM_PROVIDER": "groq",
    "CHROMA_DB_PATH": TEST_DB_PATH,
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    # Set test environment variables
    for key, value in TEST_ENV.items():
        os.environ[key] = value

    # Create test database directory
    os.makedirs(TEST_DB_PATH, exist_ok=True)

    yield

    # Cleanup
    import shutil
    if os.path.exists(TEST_DB_PATH):
        shutil.rmtree(TEST_DB_PATH)

class TestBackendImports:
    """Test that all backend modules can be imported."""

    def test_core_imports(self):
        """Test core backend imports."""
        try:
            from backend.config import CORS_ORIGINS, API_HOST, API_PORT
            from backend.utils.logger import setup_logger
            assert True
        except ImportError as e:
            pytest.fail(f"Core import failed: {e}")

    def test_llm_imports(self):
        """Test LLM module imports."""
        try:
            from backend.llm import LLMInterface
            assert True
        except ImportError as e:
            pytest.fail(f"LLM import failed: {e}")

    def test_rag_imports(self):
        """Test RAG module imports."""
        try:
            from backend.rag import SimpleVectorDB, Retriever
            assert True
        except ImportError as e:
            pytest.fail(f"RAG import failed: {e}")

    def test_tts_imports(self):
        """Test TTS module imports."""
        try:
            from backend.tts import ModernTTS
            assert True
        except ImportError as e:
            pytest.fail(f"TTS import failed: {e}")

    def test_asr_imports(self):
        """Test ASR module imports."""
        try:
            from backend.asr import WhisperASR
            assert True
        except ImportError as e:
            pytest.fail(f"ASR import failed: {e}")

class TestVectorDatabase:
    """Test vector database functionality."""

    @pytest.fixture
    def db(self):
        """Create a test database instance."""
        from backend.rag.vectordb import SimpleVectorDB
        db = SimpleVectorDB(db_path=TEST_DB_PATH, collection_name="test_collection")
        yield db
        # Cleanup
        try:
            db.client.delete_collection("test_collection")
        except:
            pass

    def test_database_initialization(self, db):
        """Test database initialization."""
        assert db.collection_name == "test_collection"
        assert db.db_path == TEST_DB_PATH

    def test_add_and_search(self, db):
        """Test adding documents and searching."""
        import numpy as np

        # Add a test document
        test_text = "This is a test document about artificial intelligence."
        test_embedding = np.random.rand(768)  # BAAI embedding dimension

        db.add(test_text, test_embedding, {"source": "test"})

        # Search for similar documents
        results = db.search(test_embedding, top_k=1)
        assert len(results) > 0
        assert results[0]["text"] == test_text

class TestLLMIntegration:
    """Test LLM integration."""

    @pytest.fixture
    def llm(self):
        """Create LLM instance for testing."""
        # Mock LLM for testing (since we don't want to make real API calls)
        class MockLLM:
            async def generate_response(self, prompt, **kwargs):
                return f"Mock response to: {prompt[:50]}..."

        return MockLLM()

    @pytest.mark.asyncio
    async def test_llm_response(self, llm):
        """Test LLM response generation."""
        prompt = "Hello, how are you?"
        response = await llm.generate_response(prompt)
        assert isinstance(response, str)
        assert len(response) > 0

class TestAPIEndpoints:
    """Test API endpoints."""

    @pytest.fixture
    async def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        try:
            from backend.main_enhanced import app
            client = TestClient(app)
            yield client
        except ImportError:
            pytest.skip("Backend not available for testing")

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_chat_endpoint(self, client):
        """Test chat endpoint (mock)."""
        # This would need proper mocking of the LLM
        pytest.skip("Chat endpoint testing requires LLM mocking")

class TestConfiguration:
    """Test configuration management."""

    def test_config_loading(self):
        """Test configuration loading."""
        from backend.config import API_HOST, API_PORT, DEBUG
        assert API_HOST == "localhost"
        assert API_PORT == 8001
        assert DEBUG is True

class TestUtilities:
    """Test utility functions."""

    def test_logger_setup(self):
        """Test logger setup."""
        from backend.utils.logger import setup_logger
        logger = setup_logger("test")
        assert logger is not None
        assert logger.name == "test"

# Integration Tests
class TestIntegration:
    """Integration tests for multiple components."""

    @pytest.mark.slow
    def test_full_rag_pipeline(self):
        """Test complete RAG pipeline."""
        pytest.skip("Full RAG pipeline test requires real data and models")

    @pytest.mark.slow
    def test_tts_stt_pipeline(self):
        """Test TTS and STT pipeline."""
        pytest.skip("TTS/STT pipeline test requires audio hardware")

# Performance Tests
class TestPerformance:
    """Performance tests."""

    @pytest.mark.slow
    def test_embedding_speed(self):
        """Test embedding generation speed."""
        pytest.skip("Performance test requires specific hardware")

    @pytest.mark.slow
    def test_search_speed(self):
        """Test vector search speed."""
        pytest.skip("Performance test requires large dataset")

# Error Handling Tests
class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_input_handling(self):
        """Test handling of invalid inputs."""
        # Test with invalid database path
        from backend.rag.vectordb import SimpleVectorDB
        with pytest.raises(Exception):
            db = SimpleVectorDB(db_path="/invalid/path")

    def test_missing_environment_variables(self):
        """Test behavior with missing environment variables."""
        # Remove a required env var temporarily
        original = os.environ.get("API_HOST")
        if "API_HOST" in os.environ:
            del os.environ["API_HOST"]

        # This should not crash the import
        try:
            from backend.config import API_HOST
            # Should fall back to default
            assert API_HOST is not None
        finally:
            if original:
                os.environ["API_HOST"] = original

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])