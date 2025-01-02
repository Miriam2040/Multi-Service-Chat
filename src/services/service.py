from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import logging
from pathlib import Path
from src.services.router.mock_router import MockRouter
from src.services.base import GenerationError
from src.services.router.openai_router import OpenAIRouter
import src.config as Config
import json
import time
from src.services.cost_tracker import CostTracker

# Initialize the cost tracker
cost_tracker = CostTracker()

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Set up logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

class ContentRequest(BaseModel):
    """Request model for content generation."""
    prompt: str

@app.post("/generate_content")
async def generate_content(request: ContentRequest):
    request_id = int(time.time() * 1000)
    logger.info(f"Request {request_id} received - Prompt: {request.prompt}")

    try:
        # Initialize router based on mode
        router = MockRouter() if Config.MODE.lower() == "dev" else OpenAIRouter()

        # Get generator and track cost
        generator = router.route(request.prompt)

        try:
            cost_tracker.track_cost(
                router.__class__.__name__,
                router.get_price(),
                request.prompt
            )

            cost_tracker.track_cost(
                generator.__class__.__name__,
                generator.get_price(),
                request.prompt
            )
        except ValueError as e:
            raise HTTPException(status_code=402, detail=str(e))

        # Generate content
        if generator.supports_streaming():

            def stream_generator():
                try:
                    chunk_count = 0
                    start_time = time.time()

                    for chunk in generator.generate_content(request.prompt):
                        logger.debug(f"chunk: {chunk}")
                        chunk_count += 1
                        if chunk_count % 100 == 0:  # Log every 100 chunks
                            logger.debug(f"Request {request_id} - Streamed {chunk_count} chunks")

                        yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"

                    duration = time.time() - start_time
                    logger.info(f"Request {request_id} - Streaming completed. Total chunks: {chunk_count}, Duration: {duration:.2f}s")

                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Request {request_id} - Streaming error: {error_msg}")
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"

            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream"
            )
        else:
            content_type, content = generator.generate_content(request.prompt)
            return JSONResponse({
                "type": content_type.value,
                "content": content
            })

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/costs/{record_id}")
async def get_cost_record(record_id: str):
    """Retrieve a specific cost record by ID."""
    try:
        return cost_tracker.get_record_by_id(record_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Cost record not found")

@app.delete("/costs/{record_id}")
async def delete_cost_record(record_id: str):
    """Delete a specific cost record."""
    success = cost_tracker.delete_record(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cost record not found or could not be deleted")
    return {"message": "Record deleted successfully"}

@app.get("/costs")
async def get_costs():
    """Get current costs status."""
    return cost_tracker.get_costs()

@app.on_event("startup")
async def startup_event():
    """Log when the FastAPI service starts."""
    logger.info("=" * 50)
    logger.info("FastAPI service starting up")
    logger.info(f"Mode: {Config.MODE}")
    logger.info(f"Log directory: {log_dir.absolute()}")
    logger.info("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    """Log when the FastAPI service shuts down."""
    logger.info("=" * 50)
    logger.info("FastAPI service shutting down")
    logger.info("=" * 50)