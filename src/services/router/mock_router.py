from typing import Dict, Type
from src.services.base import RouterBase, ContentGeneratorBase, ContentType
from src.services.research.mock_research_generator import MockResearchGenerator
from src.services.image.mock_image_generator import MockImageGenerator
from src.services.song.mock_song_generator import MockSongGenerator

class MockRouter(RouterBase):
    """
    Mock router for testing purposes.
    Routes prompts to appropriate mock generators based on simple keyword matching.
    """

    def __init__(self):
        """Initialize router with generator mappings."""
        # Store generator classes
        self.generators = {
            ContentType.TEXT: MockResearchGenerator,
            ContentType.SONG: MockSongGenerator,
            ContentType.IMAGE: MockImageGenerator
        }
        self.default_type = ContentType.IMAGE

    def route(self, prompt: str) -> ContentGeneratorBase:
        """
        Route the prompt to appropriate mock generator.

        Args:
            prompt (str): User's input prompt

        Returns:
            ContentGeneratorBase: Appropriate mock generator instance
        """
        prompt = prompt.lower()

        # Return new instance of appropriate generator
        if "research" in prompt:
            return self.generators[ContentType.TEXT]()
        elif "song" in prompt:
            return self.generators[ContentType.SONG]()

        # Default to image generator
        return self.generators[self.default_type]()