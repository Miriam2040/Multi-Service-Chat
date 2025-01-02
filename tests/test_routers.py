import pytest
from unittest.mock import Mock, patch
from src.services.router.mock_router import MockRouter
from src.services.router.openai_router import OpenAIRouter
from src.services.base import ContentType, GenerationError

class TestMockRouter:
    def test_route_research(self):
        """Test routing of research requests."""
        router = MockRouter()
        generator = router.route("research about AI")
        assert generator.supports_streaming() is True
        assert isinstance(generator.get_price(), float)

    def test_route_song(self):
        """Test routing of song requests."""
        router = MockRouter()
        generator = router.route("create a song about love")
        assert not generator.supports_streaming()
        assert isinstance(generator.get_price(), float)

    def test_route_default(self):
        """Test default routing behavior."""
        router = MockRouter()
        generator = router.route("something random")
        assert not generator.supports_streaming()
        assert isinstance(generator.get_price(), float)

class TestOpenAIRouter:
    @patch('openai.OpenAI')
    def test_route_success(self, mock_openai):
        """Test successful routing with OpenAI."""
        # Mock OpenAI response for content type determination
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content='{"type": "text"}'))
        ]
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        router = OpenAIRouter()
        generator = router.route("test prompt")
        assert isinstance(generator.get_price(), float)