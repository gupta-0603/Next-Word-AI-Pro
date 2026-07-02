# Next Word AI

An LSTM-powered writing assistant with next-word prediction, live autocomplete,
and creative sentence/paragraph generation — served through a FastAPI backend
with a clean, dependency-free frontend.

Built on top of a Keras `Tokenizer` + LSTM model. Started as a next-word
prediction script; this version wraps it in a real API, adds confidence
scoring, temperature-controlled generation, and a polished UI.

## Features

- **Top-5 predictions with confidence** — see the model's next-word guesses
  ranked, each shown as a filled "keycap" proportional to its confidence.
- **Live autocomplete** — predictions update automatically as you type (debounced).
- **Sentence & paragraph completion** — generate N more words from your text,
  with a temperature slider (0 = greedy/deterministic, 2 = high-variance/creative).
- **Copy & download** — grab your text as plain `.txt` or straight to clipboard.
- **Session history** — recent predictions/generations are kept client-side
  (`localStorage`), no login required.
- **Spell correction** — flags misspelled words and suggests fixes, with a
  one-click "apply" to update your text.
- **Synonym suggestions** — WordNet-backed lookup for any single word.
- **Text summarization** — extractive (TextRank) summary, adjustable length.
- **Sentiment analysis** — positive/neutral/negative breakdown with a
  compound score, via VADER.
- **Dark / light mode**, responsive layout, toast notifications, loading states.

## Project structure

```
next-word-ai/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app, routes, middleware, error handling
│   ├── model_utils.py    # Model loading + prediction/generation logic
│   └── schemas.py        # Pydantic request/response models
├── models/
│   └── README.md         # Where to put lstm_model.h5 / tokenizer.pkl / max_len.pkl
├── static/
│   ├── style.css
│   └── script.js
├── templates/
│   └── index.html
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

## Why FastAPI over Flask

Kept your existing model logic unchanged — only the serving layer moved.
FastAPI gives request validation for free (bad input gets a clean `422`
instead of crashing the model), auto-generated interactive docs at `/docs`,
and async-friendly routing, at no extra code cost over Flask for this size
of app.

## Installation

```bash
git clone <your-repo-url>
cd next-word-ai

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

# One-time: fetch NLTK corpora needed for synonyms + summarization
python download_nltk_data.py
```

Then drop your trained model files into `models/` (see `models/README.md`
for exact filenames expected).

## Running locally

```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000`. Interactive API docs are auto-generated at
`http://localhost:8000/docs`.

If the model files aren't found, the app still starts — the API returns a
clear `503` error explaining what's missing instead of crashing on boot.

## API documentation

### `GET /api/health`
Returns whether the model loaded successfully and the vocab size.

### `POST /api/predict`
```json
// Request
{ "text": "the weather is", "top_k": 5 }

// Response
{
  "input_text": "the weather is",
  "predictions": [
    { "word": "nice", "confidence": 42.1 },
    { "word": "cold", "confidence": 18.7 }
  ],
  "latency_ms": 12.4
}
```

### `POST /api/generate`
```json
// Request
{ "text": "once upon a time", "num_words": 15, "temperature": 1.0 }

// Response
{
  "input_text": "once upon a time",
  "generated_text": "once upon a time there was a ...",
  "latency_ms": 210.5
}
```

### `POST /api/spellcheck`
```json
// Request
{ "text": "this is a smple sentance" }

// Response
{
  "corrected_text": "this is a simple sentence",
  "corrections": [
    { "original": "smple", "corrected": "simple" },
    { "original": "sentance", "corrected": "sentence" }
  ],
  "latency_ms": 3.2
}
```

### `POST /api/synonyms`
```json
// Request
{ "word": "happy" }

// Response
{ "word": "happy", "synonyms": ["felicitous", "glad", "well-chosen", "..."], "latency_ms": 1.8 }
```

### `POST /api/summarize`
```json
// Request
{ "text": "<long text>", "sentence_count": 3 }

// Response
{ "summary": "<the 3 most central sentences>", "latency_ms": 45.6 }
```

### `POST /api/sentiment`
```json
// Request
{ "text": "I absolutely love this!" }

// Response
{
  "label": "positive",
  "compound": 0.75,
  "positive": 0.65,
  "neutral": 0.35,
  "negative": 0.0,
  "latency_ms": 0.9
}
```

Rate limits: 20/min on `/api/predict` and `/api/spellcheck`, 10/min on
`/api/generate`, 15/min on `/api/summarize`, 30/min on `/api/synonyms` and
`/api/sentiment` (via `slowapi`), to protect against runaway loops.

## Deployment

### Docker
```bash
docker build -t next-word-ai .
docker run -p 8000:8000 -v $(pwd)/models:/app/models next-word-ai
```
The volume mount keeps large model files out of the image itself.

### Bare-metal / VM
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Put this behind Nginx/Caddy for TLS in production, and tighten
`allow_origins` in `app/main.py` from `"*"` to your actual domain.

### Model hosting note
`lstm_model.h5` is excluded from version control (see `.gitignore`) because
large binaries don't belong in Git history. For deployment, either:
- use [Git LFS](https://git-lfs.com/), or
- host the file on Hugging Face Hub / S3 / a release asset and download it
  in a startup script before `uvicorn` boots.

## Testing

No formal test suite is included yet — a reasonable next step. In the
meantime, manually verify:

1. `GET /api/health` → `model_loaded: true`
2. `POST /api/predict` with a short phrase → 5 ranked predictions
3. `POST /api/generate` with `temperature: 0` → deterministic output
   (same input always produces the same output)
4. `POST /api/generate` with `temperature: 1.5` twice on the same input →
   different output each time (sampling is working)
5. Submit empty text → `422` validation error, not a crash

## Future improvements

- User accounts + persistent (server-side) history
- Analytics dashboard (usage over time, most-predicted words, latency trends)
- Compare LSTM vs. GRU vs. Transformer side-by-side
- Fine-tuning on a user-uploaded dataset
- PWA support for offline use
- Automated test suite (pytest + httpx)

## Resume bullet points

- Built and deployed a full-stack AI writing assistant (FastAPI + Keras LSTM)
  with real-time next-word prediction, confidence scoring, and
  temperature-controlled text generation.
- Designed a REST API with Pydantic-validated schemas, rate limiting, and
  structured error handling; auto-documented via OpenAPI/Swagger.
- Implemented a responsive, dependency-free frontend with live autocomplete,
  session-based history, and dark/light theming.
- Containerized the application with Docker for reproducible deployment.
