import os

def get_api_key(name: str) -> str:
    """Get API key from environment variables or raise error if missing."""
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Missing API key in environment variables: {name}")
    return value

# System
MODE = 'PRODUCTION'
BUDGET = 20

# Image
IMAGE_API_KEY = get_api_key("BFL_API_KEY")
IMAGE_GENERATION_MODEL = "flux.1.1-pro"
IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512
IMAGE_COST = 0.04
IMAGE_TEMPERATURE = 0.8

# Song
SONG_GENERATION_TOKEN = get_api_key("UDIO_API_KEY")
SONG_GENERATION_URL = "https://udioapi.pro/api/generate"
SONG_GENERATION_MODEL = "chirp-v3.0"
SONG_COST = 0.05
SONG_FEED_URL = "https://udioapi.pro/api/feed?workId="
SONG_TEMPERATURE = 0.9

# Research
RESEARCH_API_KEY = get_api_key("OPENAI_API_KEY")
RESEARCH_MODEL_NAME = "gpt-4o-mini"
RESEARCH_COST = 0.01
RESEARCH_MAX_TOKENS = 4000
RESEARCH_SYSTEM_MESSAGE = "You are an expert researcher. Produce a research paper on the following topic: "

# Router
ROUTER_MODEL_NAME = "gpt-4o-mini"
ROUTER_API_KEY = RESEARCH_API_KEY  # Reusing OpenAI key
ROUTER_COST = 0.01
ROUTER_SYSTEM_MESSAGE = "You are an expert at user message intent classification. Classify the following user message into one of these categories: image, song, research. Example user messages include: 'make me a image of a sunset', 'I want a song about the rain', 'write me research paper about the moon'."