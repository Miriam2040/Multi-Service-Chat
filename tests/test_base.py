import pytest
from unittest.mock import Mock, patch
from src.services.base import ContentType, ContentGeneratorBase, GenerationError, RouterBase

@pytest.fixture
def mock_generator():
    """Create a mock generator for testing."""
    class TestGenerator(ContentGeneratorBase):
        def generate_content(self, prompt):
            return ContentType.TEXT, "test content"

        def get_price(self):
            return 0.01

    return TestGenerator()

@pytest.fixture
def mock_router():
    """Create a mock router for testing."""
    class TestRouter(RouterBase):
        def route(self, prompt):
            return mock_generator()

    return TestRouter()

# Common test data
TEST_PROMPT = "test prompt"
TEST_API_KEY = "test_key_12345"
TEST_IMAGE_URL = "https://example.com/image.jpg"
TEST_AUDIO_URL = "https://example.com/audio.mp3"