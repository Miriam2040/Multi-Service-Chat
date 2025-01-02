from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
from enum import Enum

class ContentType(Enum):
    """
    Enum defining the types of content that can be generated.
    Using an enum ensures type safety and prevents typos.
    """
    TEXT = "text"
    IMAGE = "image"
    SONG = "song"

class GenerationError(Exception):
    """Custom exception for content generation errors."""
    pass

class ContentGeneratorBase(ABC):
    """
    Abstract base class for all content generators.
    Any class that inherits from this must implement generate_content and get_price.
    """

    def supports_streaming(self) -> bool:
        """Whether this generator supports streaming. Default is False."""
        return False

    @abstractmethod
    def generate_content(self, prompt: str) -> Tuple[ContentType, str]:
        """
        Generate content based on the given prompt.

        Args:
            prompt (str): The user's input prompt

        Returns:
            Tuple[ContentType, str]: Content type and the generated content

        Raises:
            GenerationError: If content generation fails
        """
        pass

    @abstractmethod
    def get_price(self) -> float:
        """
        Get the price for generating content.

        Returns:
            float: Price in currency units
        """
        pass

class RouterBase(ABC):
    """
    Abstract base class for routing user prompts to appropriate content generators.
    Any class that inherits from this must implement the route method.
    """
    @abstractmethod
    def route(self, prompt: str) -> ContentGeneratorBase:
        """
        Route the prompt to appropriate content generator.

        Args:
            prompt (str): The user's input prompt

        Returns:
            ContentGeneratorBase: The appropriate content generator

        Raises:
            ValueError: If prompt cannot be routed
        """
        pass