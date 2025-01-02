import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from src.services.service import app  # Updated import path
from src.services.base import ContentType, GenerationError

client = TestClient(app)

class TestFastAPIService:
    def test_startup_event(self):
        """Test service startup event."""
        with client:
            response = client.get("/")
            assert response.status_code in [404, 200]  # Depends on if you have a root endpoint

    @patch('src.services.router.mock_router.MockRouter')
    def test_generate_content_streaming(self, mock_router_class):
        """Test streaming content generation."""
        mock_generator = Mock()
        mock_generator.supports_streaming.return_value = True
        mock_generator.generate_content.return_value = ["chunk1", "chunk2"]

        mock_router_instance = Mock()
        mock_router_instance.route.return_value = mock_generator
        mock_router_class.return_value = mock_router_instance

        response = client.post(
            "/generate_content",
            json={"prompt": "test prompt"}
        )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

    def test_invalid_request(self):
        """Test handling of invalid requests."""
        response = client.post(
            "/generate_content",
            json={}  # Missing required prompt
        )
        assert response.status_code == 422