"""
main.py
-------
The FastAPI application. Responsibilities:
  - Load the model once at startup (not per-request — that would be slow)
  - Expose /predict and /generate endpoints
  - Serve the frontend (static HTML/CSS/JS)
  - Handle errors gracefully so a bad model call never 500s with a stack trace
  - Basic rate limiting so one client can't hammer the model endpoint
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.model_utils import load_default_model
from app.text_tools import load_text_tools
from app.schemas import (
    PredictRequest, PredictResponse,
    GenerateRequest, GenerateResponse,
    HealthResponse,
    SpellCheckRequest, SpellCheckResponse,
    SynonymRequest, SynonymResponse,
    SummarizeRequest, SummarizeResponse,
    SentimentRequest, SentimentResponse,
)

# ------------------------------------------------------------------
# Logging setup — writes to console; redirect to a file in production
# (e.g. `uvicorn app.main:app >> app.log 2>&1`)
# ------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("next_word_ai")

# ------------------------------------------------------------------
# Rate limiting — protects the model endpoint from abuse/accidental
# infinite loops on the frontend. 20 requests/minute is generous for
# a demo but stops runaway scripts.
# ------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)

model_holder = {"model": None, "text_tools": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load LSTM model once
    try:
        model_holder["model"] = load_default_model()
        logger.info("Startup complete — model ready.")
    except Exception as e:
        # We don't crash the whole app if the model is missing — this lets
        # the frontend load and show a clear "model not found" message
        # instead of the server failing to start at all.
        logger.error("Failed to load model at startup: %s", e)
        model_holder["model"] = None

    # Startup: load text tools (spellcheck / synonyms / summarizer / sentiment)
    try:
        model_holder["text_tools"] = load_text_tools()
        logger.info("Text tools ready (spellcheck, synonyms, summarizer, sentiment).")
    except Exception as e:
        logger.error(
            "Failed to load text tools — did you run the nltk download step? "
            "See README. Error: %s", e
        )
        model_holder["text_tools"] = None

    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Next Word AI",
    description="LSTM-powered next-word prediction and text generation API",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — open for local dev; tighten allow_origins to your actual domain in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


def get_model():
    model = model_holder["model"]
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Place lstm_model.h5, tokenizer.pkl, "
                   "and max_len.pkl in the /models directory and restart the server.",
        )
    return model


def get_text_tools():
    tools = model_holder["text_tools"]
    if tools is None:
        raise HTTPException(
            status_code=503,
            detail="Text tools failed to load. Run the nltk download step "
                   "from the README (wordnet, omw-1.4, punkt) and restart the server.",
        )
    return tools


@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse("templates/index.html")


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def health_check():
    model = model_holder["model"]
    return HealthResponse(
        status="ok" if model else "model_not_loaded",
        model_loaded=model is not None,
        vocab_size=len(model.tokenizer.word_index) if model else None,
    )


@app.post("/api/predict", response_model=PredictResponse, tags=["Prediction"])
@limiter.limit("20/minute")
def predict_next_word(request: Request, body: PredictRequest):
    model = get_model()
    start = time.perf_counter()

    try:
        predictions = model.predict_top_k(body.text, k=body.top_k)
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    latency_ms = round((time.perf_counter() - start) * 1000, 2)

    return PredictResponse(
        input_text=body.text,
        predictions=predictions,
        latency_ms=latency_ms,
    )


@app.post("/api/generate", response_model=GenerateResponse, tags=["Prediction"])
@limiter.limit("10/minute")
def generate_text(request: Request, body: GenerateRequest):
    model = get_model()
    start = time.perf_counter()

    try:
        generated = model.generate_text(
            body.text, num_words=body.num_words, temperature=body.temperature
        )
    except Exception as e:
        logger.exception("Generation failed")
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

    latency_ms = round((time.perf_counter() - start) * 1000, 2)

    return GenerateResponse(
        input_text=body.text,
        generated_text=generated,
        latency_ms=latency_ms,
    )


@app.post("/api/spellcheck", response_model=SpellCheckResponse, tags=["Text Tools"])
@limiter.limit("20/minute")
def spellcheck(request: Request, body: SpellCheckRequest):
    tools = get_text_tools()
    start = time.perf_counter()

    try:
        result = tools.correct_spelling(body.text)
    except Exception as e:
        logger.exception("Spell check failed")
        raise HTTPException(status_code=500, detail=f"Spell check failed: {e}")

    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    return SpellCheckResponse(
        corrected_text=result["corrected_text"],
        corrections=result["corrections"],
        latency_ms=latency_ms,
    )


@app.post("/api/synonyms", response_model=SynonymResponse, tags=["Text Tools"])
@limiter.limit("30/minute")
def synonyms(request: Request, body: SynonymRequest):
    tools = get_text_tools()
    start = time.perf_counter()

    try:
        result = tools.get_synonyms(body.word)
    except Exception as e:
        logger.exception("Synonym lookup failed")
        raise HTTPException(status_code=500, detail=f"Synonym lookup failed: {e}")

    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    return SynonymResponse(word=body.word, synonyms=result, latency_ms=latency_ms)


@app.post("/api/summarize", response_model=SummarizeResponse, tags=["Text Tools"])
@limiter.limit("15/minute")
def summarize(request: Request, body: SummarizeRequest):
    tools = get_text_tools()
    start = time.perf_counter()

    try:
        summary = tools.summarize(body.text, sentence_count=body.sentence_count)
    except Exception as e:
        logger.exception("Summarization failed")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {e}")

    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    return SummarizeResponse(summary=summary, latency_ms=latency_ms)


@app.post("/api/sentiment", response_model=SentimentResponse, tags=["Text Tools"])
@limiter.limit("30/minute")
def sentiment(request: Request, body: SentimentRequest):
    tools = get_text_tools()
    start = time.perf_counter()

    try:
        result = tools.analyze_sentiment(body.text)
    except Exception as e:
        logger.exception("Sentiment analysis failed")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {e}")

    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    return SentimentResponse(
        label=result["label"],
        compound=result["compound"],
        positive=result["positive"],
        neutral=result["neutral"],
        negative=result["negative"],
        latency_ms=latency_ms,
    )
