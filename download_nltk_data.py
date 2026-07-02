"""
download_nltk_data.py
----------------------
Run this once after `pip install -r requirements.txt`, before starting the
server, to fetch the NLTK corpora that /api/synonyms and /api/summarize
need. Without this, the app still starts (see main.py's lifespan handler)
but those two endpoints return a clear 503 instead of the words you want.

Usage:
    python download_nltk_data.py
"""

import nltk

REQUIRED_CORPORA = [
    "wordnet",    # synonym lookups (get_synonyms)
    "omw-1.4",    # multilingual wordnet data wordnet.py needs internally
    "punkt",      # sentence tokenizer used by sumy for summarization
    "punkt_tab",  # newer nltk versions split punkt into this as well
]

if __name__ == "__main__":
    for corpus in REQUIRED_CORPORA:
        print(f"Downloading '{corpus}'...")
        nltk.download(corpus)
    print("Done. You can now start the server.")
