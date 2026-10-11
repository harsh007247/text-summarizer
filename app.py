"""
================================================================================
Text Summarization Web Application Backend (FastAPI)
================================================================================
This file contains the complete FastAPI implementation for the Text Summarizer.
It handles:
1. Static file mounting and frontend template serving (HTML, CSS, JS).
2. Health check endpoint to monitor model availability.
3. Summarization endpoint with request validation, PEGASUS inference,
   and statistical metrics computation (word counts, tokens, reduction %).
================================================================================
"""

import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

# Import the existing prediction pipeline from the textsummarizer package
from textsummarizer.pipeline.prediction import PredictionPipeline
from textsummarizer.logging import logger

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Initialize FastAPI application
app = FastAPI(
    title="PEGASUS Text Summarizer",
    description="Professional Text Summarization API powered by fine-tuned PEGASUS",
    version="1.0.0"
)

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for CSS and JS assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Global pipeline instance (loaded once at startup)
pipeline: Optional[PredictionPipeline] = None


# ------------------------------------------------------------------------------
# Request Schema
# ------------------------------------------------------------------------------
class SummarizeRequest(BaseModel):
    """Simple inline schema for summarization requests with defaults and constraints."""
    text: str = Field(..., description="Input dialogue or text passage to summarize")
    max_length: Optional[int] = Field(default=128, ge=20, le=512, description="Max token length")
    min_length: Optional[int] = Field(default=20, ge=5, le=256, description="Min token length")
    num_beams: Optional[int] = Field(default=8, ge=1, le=16, description="Beam search width")
    length_penalty: Optional[float] = Field(default=0.8, ge=0.1, le=2.0, description="Length penalty")


# ------------------------------------------------------------------------------
# Lifecycle Events
# ------------------------------------------------------------------------------
@app.on_event("startup")
def load_model():
    """
    Load the PEGASUS model and tokenizer once when the application starts.
    Reuses the preloaded weights for all subsequent inference requests.
    """
    global pipeline
    try:
        logger.info("Initializing PEGASUS model on application startup...")
        pipeline = PredictionPipeline()
        logger.info("PEGASUS model successfully loaded and ready for predictions.")
    except Exception as e:
        logger.exception(f"Error loading PEGASUS model on startup: {str(e)}")


# ------------------------------------------------------------------------------
# API Routes
# ------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the single-page HTML frontend."""
    index_path = TEMPLATES_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frontend template index.html not found."
        )
    return FileResponse(str(index_path))


@app.get("/api/health")
async def health_check():
    """Health check endpoint to inspect model readiness and device."""
    is_ready = pipeline is not None and getattr(pipeline, "model", None) is not None
    device_name = getattr(pipeline, "device", "unknown") if is_ready else "unknown"
    return {
        "status": "healthy" if is_ready else "initializing",
        "model_loaded": is_ready,
        "device": device_name
    }


@app.post("/api/summarize")
async def summarize_text(req: SummarizeRequest):
    """
    Summarize input text using the trained PEGASUS model.
    Validates input and generation length parameters, performs inference,
    and returns the summary along with word and token count statistics.
    """
    # 1. Check if model is initialized
    if pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The summarization model is currently initializing. Please try again in a few seconds."
        )

    # 2. Input text validation
    clean_text = req.text.strip() if req.text else ""
    if not clean_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Input text cannot be empty or solely whitespace."
        )

    # 3. Parameter validation
    max_len = req.max_length or 128
    min_len = req.min_length or 20
    if min_len > max_len:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Minimum length ({min_len}) cannot be greater than maximum length ({max_len})."
        )

    num_beams = req.num_beams or 8
    length_penalty = req.length_penalty or 0.8

    try:
        start_time = time.perf_counter()

        # Count input words and tokens
        input_words = len(clean_text.split())
        input_token_ids = pipeline.tokenizer.encode(
            clean_text,
            truncation=True,
            max_length=1024
        )
        input_tokens = len(input_token_ids)

        # Run inference in a background threadpool so the FastAPI event loop is not blocked
        summary = await run_in_threadpool(
            pipeline.predict,
            text=clean_text,
            max_length=max_len,
            min_length=min_len,
            num_beams=num_beams,
            length_penalty=length_penalty
        )

        elapsed_time = round(time.perf_counter() - start_time, 2)

        # Count summary words and tokens
        summary_words = len(summary.strip().split()) if summary else 0
        summary_tokens = len(pipeline.tokenizer.encode(summary)) if summary else 0

        # Calculate word reduction percentage
        if input_words > 0:
            reduction_pct = round(max(0.0, (1.0 - (summary_words / input_words)) * 100.0), 1)
        else:
            reduction_pct = 0.0

        return {
            "summary": summary,
            "input_words": input_words,
            "summary_words": summary_words,
            "input_tokens": input_tokens,
            "summary_tokens": summary_tokens,
            "reduction_percentage": reduction_pct,
            "inference_time_seconds": elapsed_time
        }

    except Exception as e:
        logger.exception(f"Summarization inference failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    # Start the server directly via: python app.py
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=False)

