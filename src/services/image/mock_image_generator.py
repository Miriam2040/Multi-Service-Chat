import random
import time
from typing import Tuple, List
from src.services.base import ContentType, ContentGeneratorBase

class MockImageGenerator(ContentGeneratorBase):
    """
    Mock image generator for testing purposes.
    Simulates API behavior with random delays and sample images.
    """

    # Sample image URLs for testing different scenarios
    SAMPLE_IMAGES = [
        "https://raw.githubusercontent.com/CompVis/stable-diffusion/main/assets/stable-samples/img2img/sketch-mountains-input.jpg"
    ]

    def __init__(self, min_delay: int = 3, max_delay: int = 20):
        """
        Initialize mock generator with configurable delays.

        Args:
            min_delay (int): Minimum processing delay in seconds
            max_delay (int): Maximum processing delay in seconds
        """
        self.min_delay = min_delay
        self.max_delay = max_delay

    def _simulate_processing_time(self):
        """Simulate API processing time with random delay."""
        time.sleep(random.randint(self.min_delay, self.max_delay))

    def generate_content(self, prompt: str) -> Tuple[ContentType, str]:
        """
        Mock image generation with simulated delay.

        Args:
            prompt (str): Image description (unused in mock)

        Returns:
            Tuple[ContentType, str]: Content type and random sample image URL
        """
        # Simulate processing time
        self._simulate_processing_time()

        # Return random sample image
        return ContentType.IMAGE, random.choice(self.SAMPLE_IMAGES)

    def get_price(self) -> float:
        """
        Get mock price for image generation.

        Returns:
            float: Fixed mock price
        """
        return 0.02