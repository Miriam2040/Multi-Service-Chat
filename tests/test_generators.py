import pytest
from unittest.mock import Mock, patch
from src.services.image.mock_image_generator import MockImageGenerator
from src.services.song.mock_song_generator import MockSongGenerator
from src.services.research.mock_research_generator import MockResearchGenerator
from src.services.image.flux_image_generator import FluxImageGenerator
from src.services.song.suno_song_generator import SunoSongGenerator
from src.services.research.openai_research_generator import OpenAIResearchGenerator
from src.services.base import ContentType, GenerationError

class TestMockGenerators:
    def test_mock_image_generator(self):
        """Test mock image generator functionality."""
        generator = MockImageGenerator(min_delay=0, max_delay=1)
        content_type, url = generator.generate_content("test prompt")

        assert content_type == ContentType.IMAGE
        assert isinstance(url, str)
        assert url.startswith("http")
        assert generator.get_price() > 0

    def test_mock_song_generator(self):
        """Test mock song generator functionality."""
        generator = MockSongGenerator(min_delay=0, max_delay=1)
        content_type, url = generator.generate_content("test prompt")

        assert content_type == ContentType.SONG
        assert isinstance(url, str)
        assert url.startswith("http")
        assert generator.get_price() > 0

    def test_mock_research_generator(self):
        """Test mock research generator functionality."""
        generator = MockResearchGenerator()
        assert generator.supports_streaming() is True

        # Test streaming generation
        content = list(generator.generate_content("test prompt"))
        assert len(content) > 0
        assert all(isinstance(chunk, str) for chunk in content)
        assert generator.get_price() > 0

class TestFluxImageGenerator:
    @patch('requests.Session')
    def test_image_generation_failure(self, mock_session):
        """Test image generation failure handling."""
        mock_session.return_value.post.side_effect = Exception("API Error")

        generator = FluxImageGenerator()
        with pytest.raises(GenerationError):
            generator.generate_content("test prompt")

class TestSunoSongGenerator:
    @patch('requests.post')
    @patch('requests.get')
    def test_song_generation_success(self, mock_get, mock_post):
        """Test successful song generation with Suno API."""
        # Fix mock response structure
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"workId": "test_id"}

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "type": "complete",
            "response_data": [{
                "audio_url": "https://example.com/song.mp3"
            }]
        }

        generator = SunoSongGenerator()
        content_type, url = generator.generate_content("test prompt")

        assert content_type == ContentType.SONG
        assert url == "https://example.com/song.mp3"

    @patch('requests.post')
    def test_song_generation_failure(self, mock_post):
        """Test song generation failure handling."""
        mock_post.side_effect = Exception("API Error")

        generator = SunoSongGenerator()
        with pytest.raises(GenerationError):
            generator.generate_content("test prompt")

class TestOpenAIResearchGenerator:
    @patch('openai.OpenAI')
    def test_research_generation_success(self, mock_openai):
        """Test successful research generation with OpenAI API."""
        # Mock streaming response
        mock_chunks = [
            Mock(choices=[Mock(delta=Mock(content="chunk1"))]),
            Mock(choices=[Mock(delta=Mock(content="chunk2"))])
        ]
        mock_openai.return_value.chat.completions.create.return_value = mock_chunks

        generator = OpenAIResearchGenerator()
        content = list(generator.generate_content("test prompt"))

        assert len(content) > 0
        assert generator.supports_streaming() is True