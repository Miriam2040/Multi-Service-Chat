from typing import Dict, Type
from pydantic import BaseModel
from openai import OpenAI
from src.services.base import RouterBase, ContentGeneratorBase, ContentType, GenerationError, ContentType
from src.services.research.openai_research_generator import OpenAIResearchGenerator
from src.services.image.flux_image_generator import FluxImageGenerator
from src.services.song.suno_song_generator import SunoSongGenerator
import src.config  as Config


class ContentGenerationType(BaseModel):
    type: ContentType

class OpenAIRouter(RouterBase):
    """
    Router that uses OpenAI to determine the appropriate content generator.
    """

    def __init__(self):
        """Initialize the OpenAI client and generator mappings."""
        try:
            self.client = OpenAI(api_key=Config.ROUTER_API_KEY)
            # Map ContentType enum to generator classes
            self.generators: Dict[ContentType, Type[ContentGeneratorBase]] = {
                ContentType.TEXT: OpenAIResearchGenerator,
                ContentType.SONG: SunoSongGenerator,
                ContentType.IMAGE: FluxImageGenerator
            }
        except Exception as e:
            raise GenerationError(f"Failed to initialize OpenAI router: {str(e)}")

    def _get_content_type(self, prompt: str) -> ContentType:
        """
        Use OpenAI to determine the content type from the prompt.

        Args:
            prompt (str): User's input prompt

        Returns:
            ContentType: Determined content type enum

        Raises:
            GenerationError: If content type determination fails
        """
        try:
            completion = self.client.beta.chat.completions.parse(
                model=Config.ROUTER_MODEL_NAME,
                messages=[
                    {"role": "system", "content": Config.ROUTER_SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format= ContentGenerationType
            )

            if not completion.choices or not completion.choices[0].message.content:
                raise GenerationError("No response received from OpenAI")

            return completion.choices[0].message.parsed.type

        except Exception as e:
            raise GenerationError(f"Failed to determine content type: {str(e)}")

    def route(self, prompt: str) -> ContentGeneratorBase:
        """
        Route the prompt to appropriate content generator.

        Args:
            prompt (str): User's input prompt

        Returns:
            ContentGeneratorBase: Appropriate content generator instance

        Raises:
            GenerationError: If routing fails
        """
        try:
            # Get content type from OpenAI
            content_type = self._get_content_type(prompt)

            # Get appropriate generator class
            generator_class = self.generators.get(content_type)

            if not generator_class:
                raise GenerationError(f"Unsupported content type: {content_type}")

            # Return new instance of the generator
            return generator_class()

        except GenerationError:
            raise
        except Exception as e:
            raise GenerationError(f"Failed to route prompt: {str(e)}")

    def get_price(self) -> float:
        """
        Get the price for routing.

        Returns:
            float: Cost in currency units
        """
        return Config.ROUTER_COST