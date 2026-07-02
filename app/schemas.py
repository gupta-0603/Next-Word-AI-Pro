"""
schemas.py
----------
Pydantic models define the exact shape of requests/responses. FastAPI uses
these to auto-validate incoming data (so bad input gets rejected with a
clear 422 error instead of crashing the model) and to auto-generate the
interactive API docs at /docs.
"""

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Input text to predict from")
    top_k: int = Field(5, ge=1, le=10, description="How many predictions to return")


class Prediction(BaseModel):
    word: str
    confidence: float


class PredictResponse(BaseModel):
    input_text: str
    predictions: list[Prediction]
    latency_ms: float


class GenerateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    num_words: int = Field(15, ge=1, le=100, description="Number of words to generate")
    temperature: float = Field(1.0, ge=0.0, le=2.0, description="0 = greedy, higher = more creative")


class GenerateResponse(BaseModel):
    input_text: str
    generated_text: str
    latency_ms: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    vocab_size: int | None = None


# ----------------------------------------------------------------------
# Text tools: spell correction, synonyms, summarization, sentiment
# ----------------------------------------------------------------------
class SpellCheckRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class SpellCorrection(BaseModel):
    original: str
    corrected: str


class SpellCheckResponse(BaseModel):
    corrected_text: str
    corrections: list[SpellCorrection]
    latency_ms: float


class SynonymRequest(BaseModel):
    word: str = Field(..., min_length=1, max_length=50)


class SynonymResponse(BaseModel):
    word: str
    synonyms: list[str]
    latency_ms: float


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    sentence_count: int = Field(3, ge=1, le=10)


class SummarizeResponse(BaseModel):
    summary: str
    latency_ms: float


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class SentimentResponse(BaseModel):
    label: str
    compound: float
    positive: float
    neutral: float
    negative: float
    latency_ms: float
