from typing import Tuple
import random
import time
from src.services.base import ContentType, ContentGeneratorBase

class MockSongGenerator(ContentGeneratorBase):
    """
    Mock song generator for testing purposes.
    Simulates API behavior with random delays.
    """

    def __init__(self, min_delay: int = 3, max_delay: int = 20):
        """
        Initialize mock generator with configurable delays.

        Args:
            min_delay (int): Minimum processing delay in seconds
            max_delay (int): Maximum processing delay in seconds
        """
        self.min_delay = min_delay
        self.max_delay = max_delay

    def generate_content(self, prompt: str) -> Tuple[ContentType, str]:
        """
        Mock song generation with simulated delay.

        Args:
            prompt (str): Song description

        Returns:
            Tuple[ContentType, str]: Content type and URL of mock song
        """
        time.sleep(random.randint(self.min_delay, self.max_delay))
        return ContentType.SONG, "https://cdn1.suno.ai/db9539de-b621-42f5-9188-f83302a511b8.mp3"

    def get_price(self) -> float:
        """
        Get mock price for song generation.

        Returns:
            float: Fixed mock price
        """
        return 0.01