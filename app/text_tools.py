"""
text_tools.py
-------------
Four NLP utilities, independent of the LSTM model:
  - Spell correction   (pyspellchecker — pure Python, no downloads)
  - Synonym lookup     (nltk WordNet — needs a one-time corpus download)
  - Text summarization (sumy TextRank — needs nltk 'punkt' tokenizer)
  - Sentiment analysis (VADER — lexicon-based, no downloads, good for
                         short/informal text)

Kept in one module, separate from model_utils.py, because these don't touch
the Keras model at all — they're classical NLP, not the LSTM's job.
"""

import logging

from spellchecker import SpellChecker
from nltk.corpus import wordnet
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer as SumyTokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger("next_word_ai")


class TextTools:
    """Bundles the four tools so they're initialized once at app startup,
    not re-created on every request (SpellChecker in particular loads a
    frequency dictionary into memory)."""

    def __init__(self):
        self.spell = SpellChecker()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.summarizer = TextRankSummarizer()

    # ------------------------------------------------------------------
    # Spell correction
    # ------------------------------------------------------------------
    def correct_spelling(self, text: str) -> dict:
        """Returns the corrected text plus a list of individual corrections made."""
        words = text.split()
        corrections = []
        corrected_words = []

        for word in words:
            # Strip trailing punctuation so "hten." checks as "hten"
            stripped = word.strip(".,!?;:\"'")
            trailing = word[len(stripped):]

            if not stripped or not stripped.isalpha():
                corrected_words.append(word)
                continue

            if stripped.lower() in self.spell:
                corrected_words.append(word)
                continue

            correction = self.spell.correction(stripped)
            if correction and correction.lower() != stripped.lower():
                corrections.append({"original": stripped, "corrected": correction})
                corrected_words.append(correction + trailing)
            else:
                corrected_words.append(word)

        return {
            "corrected_text": " ".join(corrected_words),
            "corrections": corrections,
        }

    # ------------------------------------------------------------------
    # Synonyms
    # ------------------------------------------------------------------
    def get_synonyms(self, word: str, limit: int = 8) -> list[str]:
        """Looks up synonyms via WordNet. Returns an empty list if the
        word isn't found (e.g. typos, proper nouns) rather than raising."""
        synonyms = set()

        for synset in wordnet.synsets(word):
            for lemma in synset.lemmas():
                candidate = lemma.name().replace("_", " ")
                if candidate.lower() != word.lower():
                    synonyms.add(candidate)
            if len(synonyms) >= limit:
                break

        return sorted(synonyms)[:limit]

    # ------------------------------------------------------------------
    # Summarization
    # ------------------------------------------------------------------
    def summarize(self, text: str, sentence_count: int = 3) -> str:
        """Extractive summary via TextRank — picks the most central existing
        sentences rather than generating new ones (safer, no hallucination,
        and doesn't need a second heavy model)."""
        parser = PlaintextParser.from_string(text, SumyTokenizer("english"))
        sentences = self.summarizer(parser.document, sentence_count)
        summary = " ".join(str(s) for s in sentences)
        return summary if summary else text

    # ------------------------------------------------------------------
    # Sentiment
    # ------------------------------------------------------------------
    def analyze_sentiment(self, text: str) -> dict:
        scores = self.sentiment_analyzer.polarity_scores(text)
        compound = scores["compound"]

        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {
            "label": label,
            "compound": compound,
            "positive": scores["pos"],
            "neutral": scores["neu"],
            "negative": scores["neg"],
        }


def load_text_tools() -> TextTools:
    return TextTools()
