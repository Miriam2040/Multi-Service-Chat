import json
import requests
import time
from typing import Tuple, Dict
from src.services.base import ContentType, ContentGeneratorBase, GenerationError
import src.config  as Config

class SunoSongGenerator(ContentGeneratorBase):
    """
    Song generator using the Suno API service.
    Handles song generation requests and polling for completion.
    """

    def _generate_song_request(self, prompt: str) -> str:
        """
        Initiate a song generation request.

        Args:
            prompt (str): Description of the song to generate

        Returns:
            str: Work ID for tracking the generation progress

        Raises:
            GenerationError: If the request fails
        """
        try:
            payload: Dict = {
                "prompt": prompt,
                "model": Config.SONG_GENERATION_MODEL,
                "token": Config.SONG_GENERATION_TOKEN
            }

            headers = {"Content-Type": "application/json"}

            response = requests.post(
                Config.SONG_GENERATION_URL,
                headers=headers,
                data=json.dumps(payload),
                verify=False,
                timeout=30  # Add timeout to prevent hanging
            )

            response.raise_for_status()  # Raise exception for bad status codes

            work_id = response.json().get("workId")
            if not work_id:
                raise GenerationError("No work ID received from API")

            return work_id

        except requests.RequestException as e:
            raise GenerationError(f"Failed to initiate song generation: {str(e)}")
        except json.JSONDecodeError as e:
            raise GenerationError(f"Invalid API response format: {str(e)}")

    def _feed_song_generation(self, work_id: str, max_attempts: int = 60) -> str:
        """
        Poll for song generation completion.

        Args:
            work_id (str): Work ID to track
            max_attempts (int): Maximum number of polling attempts

        Returns:
            str: URL of the generated audio

        Raises:
            GenerationError: If polling fails or times out
        """
        try:
            url = Config.SONG_FEED_URL + work_id
            attempts = 0

            while attempts < max_attempts:
                response = requests.get(url, verify=False, timeout=10)
                response.raise_for_status()

                data = response.json()
                status = data.get("type")

                if status == "complete":
                    audio_url = data.get("response_data")[0]['audio_url']
                    if not audio_url:
                        raise GenerationError("No audio URL in complete response")
                    return audio_url
                elif status == "failed":
                    raise GenerationError(f"Song generation failed: {data.get('error', 'Unknown error')}")

                attempts += 1
                time.sleep(1)

            raise GenerationError(f"Song generation timed out after {max_attempts} seconds")

        except requests.RequestException as e:
            raise GenerationError(f"Error while polling for song completion: {str(e)}")
        except json.JSONDecodeError as e:
            raise GenerationError(f"Invalid polling response format: {str(e)}")

    def generate_content(self, prompt: str) -> Tuple[ContentType, str]:
        """
        Generate a song based on the provided prompt.

        Args:
            prompt (str): Description of the song to generate

        Returns:
            Tuple[ContentType, str]: Content type and URL of the generated song

        Raises:
            GenerationError: If song generation fails
        """
        try:
            work_id = self._generate_song_request(prompt)
            audio_url = self._feed_song_generation(work_id)
            return ContentType.SONG, audio_url

        except GenerationError:
            raise
        except Exception as e:
            raise GenerationError(f"Unexpected error during song generation: {str(e)}")

    def get_price(self) -> float:
        """
        Get the price for song generation.

        Returns:
            float: Cost in currency units
        """
        return Config.SONG_COST