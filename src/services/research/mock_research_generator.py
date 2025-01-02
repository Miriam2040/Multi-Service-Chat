import random
import time
from typing import Tuple, List
from src.services.base import ContentType, ContentGeneratorBase

class MockResearchGenerator(ContentGeneratorBase):
    """
    Mock research generator that simulates streaming responses.
    Used for testing and development.
    """
    def supports_streaming(self) -> bool:
        """Indicate that this generator supports streaming."""
        return True

    def generate_content(self, prompt: str) ->  Tuple[ContentType, str]:
        """
        Generate mock research content with simulated delays.

        Args:
            prompt (str): Research topic/question

        Yields:
            str: Chunks of mock research text
        """
        # Initial response
        time.sleep(1)  # Initial delay
        yield f"Researching about {prompt}...\n\n"

        # Introduction
        time.sleep(0.5)
        yield "Introduction:\n"
        yield f"This research paper explores {prompt} in detail.\n\n"

        # Main content sections
        sections = ["Background", "Methodology", "Results", "Discussion"]
        for section in sections:
            time.sleep(random.uniform(0.5, 1.5))
            yield f"{section}:\n"
            yield f"This section contains mock content about {prompt}.\n\n"

        # Conclusion
        time.sleep(0.5)
        yield "Conclusion:\n"
        yield f"These findings about {prompt} suggest significant implications.\n"

    def get_price(self) -> float:
        """Get mock price for research generation."""
        return 0.001