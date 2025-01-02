from typing import Tuple
import requests
import ssl
from requests.adapters import HTTPAdapter
from src.services.base import ContentType, ContentGeneratorBase, GenerationError
import src.config  as Config
from flux.api import ImageRequest

class CustomSSLAdapter(HTTPAdapter):
    """
    Custom HTTPS adapter that skips SSL verification.
    Warning: This should only be used in development/testing environments.
    """
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

class FluxImageGenerator(ContentGeneratorBase):
    """
    Image generator using the Flux API service.
    Inherits from ContentGeneratorBase to implement image generation functionality.
    """
    def __init__(self):
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Creates and configures a requests session with SSL settings.

        Returns:
            requests.Session: Configured session object
        """
        session = requests.Session()
        session.mount('https://', CustomSSLAdapter())
        return session

    def _patch_requests(self):
        """
        Monkey patches the requests module with our custom session.
        Warning: This affects all requests globally - use with caution.
        """
        requests.get = self.session.get
        requests.post = self.session.post
        requests.put = self.session.put
        requests.delete = self.session.delete

    def generate_content(self, prompt: str) -> Tuple[ContentType, str]:
        """
        Generates an image based on the provided prompt using Flux API.

        Args:
            prompt (str): The description of the image to generate

        Returns:
            Tuple[ContentType, str]: Content type and URL of the generated image

        Raises:
            GenerationError: If image generation fails
        """
        try:
            # Apply request patches
            self._patch_requests()

            # Create image request
            result = ImageRequest(
                prompt=prompt,
                name=Config.IMAGE_GENERATION_MODEL,
                api_key=Config.IMAGE_API_KEY,
                width=Config.IMAGE_WIDTH,
                height=Config.IMAGE_HEIGHT
            )

            if not result.url:
                raise GenerationError("No image URL returned from API")

            return ContentType.IMAGE, result.url

        except Exception as e:
            raise GenerationError(f"Failed to generate image: {str(e)}")

    def get_price(self) -> float:
        """
        Returns the cost of generating one image.

        Returns:
            float: Cost in currency units
        """
        return Config.IMAGE_COST