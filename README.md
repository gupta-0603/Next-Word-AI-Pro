# Next Word AI Pro

**Live Demo:** [next-word-ai-pro-03.streamlit.app](https://next-word-ai-pro-03.streamlit.app/)

An NLP toolkit built around an LSTM-based next-word prediction model, wrapped in an interactive Streamlit web app with a companion FastAPI backend. Combines deep learning text prediction with classic NLP utilities (spell check, summarization, sentiment analysis, synonym lookup) into a single, deployable application.

---

## Features

| Feature | Description |
|---|---|
| **Next Word Prediction** | Predicts the top-k most likely next words for a given input, with confidence scores, using a trained LSTM model |
| **Text Generation** | Extends a seed phrase into full text using temperature-controlled sampling (greedy → creative) |
| **Spell Check** | Detects and auto-corrects spelling errors |
| **Synonym Finder** | Returns semantically similar words for a given term |
| **Summarization** | Extractive summarization for condensing longer passages |
| **Sentiment Analysis** | Classifies text as positive / neutral / negative with confidence breakdown |
| **Smart Analysis** | Runs multiple NLP tools on the same input in one pass |
| **Batch Processing** | Processes multiple texts or uploaded `.txt` files at once, with CSV/JSON export |

## Tech Stack

- **Model:** LSTM (TensorFlow / Keras) trained for next-word prediction
- **Frontend:** Streamlit
- **Backend API:** FastAPI (with rate limiting via SlowAPI) — exposes the same functionality as REST endpoints for programmatic access
- **NLP Tooling:** NLTK, Sumy (summarization), VADER (sentiment), pyspellchecker
- **Deployment:** Streamlit Community Cloud

## Project Structure

```
Next-Word-AI-Pro/
├── app/
│   ├── main.py            # FastAPI application & REST endpoints
│   ├── model_utils.py     # LSTM model loading & prediction logic
│   ├── text_tools.py      # Spellcheck / synonyms / summarizer / sentiment
│   └── schemas.py         # Pydantic request/response models
├── models/                # Trained model artifacts (lstm_model.h5, tokenizer.pkl, max_len.pkl)
├── static/                 # Frontend assets for the FastAPI-served UI
├── templates/               # HTML templates for the FastAPI-served UI
├── streamlit_app_enhanced.py  # Main Streamlit application (deployed entrypoint)
├── run.py                  # Local launcher for the Streamlit app
├── requirements.txt
└── runtime.txt              # Pinned Python version for deployment
```

## Running Locally

```bash
git clone https://github.com/gupta-0603/Next-Word-AI-Pro.git
cd Next-Word-AI-Pro
pip install -r requirements.txt
python download_nltk_data.py   # one-time NLTK corpus download
python run.py
```

The app will be available at `http://localhost:8501`.

## API Access

The FastAPI backend (`app/main.py`) exposes the same core functionality as REST endpoints (`/api/predict`, `/api/generate`, `/api/spellcheck`, `/api/synonyms`, `/api/summarize`, `/api/sentiment`) for integration into other applications. Run it separately with:

```bash
uvicorn app.main:app --reload
```

## Model

The next-word prediction model is a Keras LSTM trained on [describe your dataset here, e.g. "a corpus of English text"]. It takes a padded sequence of tokenized words as input and outputs a probability distribution over the vocabulary for the next word.

## Author

**Aditya Kumar**
[GitHub](https://github.com/gupta-0603)
