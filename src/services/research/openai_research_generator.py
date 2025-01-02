import random
import time
from typing import Tuple
from src.services.base import ContentType, ContentGeneratorBase, GenerationError
import src.config  as Config
from openai import OpenAI
from openai.types.chat import ChatCompletion

class OpenAIResearchGenerator(ContentGeneratorBase):
    """
    Research content generator using OpenAI's streaming API.
    """
    def __init__(self):
        try:
            self.client = OpenAI(api_key=Config.RESEARCH_API_KEY)
        except Exception as e:
            raise GenerationError(f"Failed to initialize OpenAI client: {str(e)}")

    def supports_streaming(self) -> bool:
        """Indicate that this generator supports streaming."""
        return True

    def generate_content(self, prompt: str) ->  Tuple[ContentType, str]:
        """
        Generate research content using OpenAI's streaming API.

        Args:
            prompt (str): Research topic/question

        Yields:
            str: Chunks of generated text

        Raises:
            GenerationError: If content generation fails
        """
        try:
            completion = self.client.chat.completions.create(
                model=Config.RESEARCH_MODEL_NAME,
                messages=[
                    {"role": "system", "content": Config.RESEARCH_SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise GenerationError(f"Failed to generate research: {str(e)}")

    def get_price(self) -> float:
        """Get the price for research generation."""
        return Config.RESEARCH_COST