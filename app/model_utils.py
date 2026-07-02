"""
model_utils.py
----------------
Everything related to the LSTM model lives here: loading, prediction,
and text-generation logic. Keeping this separate from main.py means
the API layer doesn't need to know anything about TensorFlow internals,
and you can unit-test predictions without spinning up a server.
"""

import pickle
import logging
from pathlib import Path

import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

logger = logging.getLogger("next_word_ai")

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


class NextWordModel:
    """Wraps the trained LSTM model + tokenizer and exposes clean prediction methods."""

    def __init__(self, model_path: Path, tokenizer_path: Path, max_len_path: Path):
        logger.info("Loading model from %s", model_path)
        self.model = load_model(model_path)

        with open(tokenizer_path, "rb") as f:
            self.tokenizer = pickle.load(f)

        with open(max_len_path, "rb") as f:
            self.max_len = pickle.load(f)

        # Reverse lookup: index -> word (built once, not on every request)
        self.index_to_word = {idx: word for word, idx in self.tokenizer.word_index.items()}

        logger.info("Model loaded. Vocab size: %d, max_len: %d",
                    len(self.tokenizer.word_index), self.max_len)

    def _prepare_input(self, text: str) -> np.ndarray:
        sequence = self.tokenizer.texts_to_sequences([text])[0]
        return pad_sequences([sequence], maxlen=self.max_len - 1, padding="pre")

    def predict_top_k(self, text: str, k: int = 5) -> list[dict]:
        """
        Returns the top-k next-word predictions with confidence scores.
        Example: [{"word": "world", "confidence": 0.42}, ...]
        """
        if not text.strip():
            return []

        padded = self._prepare_input(text)
        preds = self.model.predict(padded, verbose=0)[0]  # shape: (vocab_size,)

        top_indices = np.argsort(preds)[-k:][::-1]

        results = []
        for idx in top_indices:
            word = self.index_to_word.get(idx)
            if word:
                results.append({
                    "word": word,
                    "confidence": round(float(preds[idx]) * 100, 2)
                })
        return results

    def generate_text(self, text: str, num_words: int = 15, temperature: float = 1.0) -> str:
        """
        Extends the input text word-by-word using temperature sampling.
        temperature < 1.0 -> more conservative / predictable
        temperature > 1.0 -> more creative / random
        temperature == 0  -> greedy (always pick the highest-probability word)
        """
        result_text = text.strip()

        for _ in range(num_words):
            padded = self._prepare_input(result_text)
            preds = self.model.predict(padded, verbose=0)[0]

            if temperature <= 0:
                next_index = int(np.argmax(preds))
            else:
                next_index = self._sample_with_temperature(preds, temperature)

            next_word = self.index_to_word.get(next_index)
            if not next_word:
                break

            result_text += " " + next_word

        return result_text

    @staticmethod
    def _sample_with_temperature(preds: np.ndarray, temperature: float) -> int:
        """Standard temperature-scaled sampling used in char/word-RNN generation."""
        preds = np.asarray(preds).astype("float64")
        # avoid log(0)
        preds = np.clip(preds, 1e-10, 1.0)
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return int(np.argmax(probas))


def load_default_model() -> NextWordModel:
    """
    Loads model files from the /models directory. Drop your own
    lstm_model.h5, tokenizer.pkl, and max_len.pkl in there — filenames
    must match exactly, or update the paths below.
    """
    return NextWordModel(
        model_path=MODELS_DIR / "lstm_model.h5",
        tokenizer_path=MODELS_DIR / "tokenizer.pkl",
        max_len_path=MODELS_DIR / "max_len.pkl",
    )
