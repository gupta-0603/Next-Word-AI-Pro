"""
Streamlit app for Next Word AI
Replaces the FastAPI frontend with a Streamlit interface
"""

import time
import streamlit as st
from pathlib import Path

from app.model_utils import load_default_model
from app.text_tools import load_text_tools

# ------------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Next Word AI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Caching - load model and tools only once
# ------------------------------------------------------------------
@st.cache_resource
def load_model():
    """Load the LSTM model (cached so it's only loaded once)"""
    return load_default_model()

@st.cache_resource
def load_tools():
    """Load text tools (cached so they're only initialized once)"""
    return load_text_tools()

# Load model and tools
try:
    model = load_model()
    text_tools = load_tools()
except Exception as e:
    st.error(f" Failed to load model or tools: {str(e)}")
    st.stop()

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
st.title(" Next Word AI")
st.markdown("""
**Predict next words**, generate text, check spelling, find synonyms, and analyze sentiment!
""")

# ------------------------------------------------------------------
# Sidebar - Navigation
# ------------------------------------------------------------------
st.sidebar.title(" Menu")
page = st.sidebar.radio(
    "Choose a feature:",
    [" Predict Next Words", " Generate Text", " Spell Check", 
     " Synonyms", " Summarize", " Sentiment Analysis"]
)

# ------------------------------------------------------------------
# Page: Predict Next Words
# ------------------------------------------------------------------
if page == " Predict Next Words":
    st.header(" Predict Next Words")
    st.write("Enter text and get top predictions for the next word.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        input_text = st.text_input(
            "Enter text:",
            value="the quick brown",
            help="Provide the context to predict the next word"
        )
    with col2:
        top_k = st.slider("Top K predictions:", 1, 10, 5)
    
    if st.button(" Predict", key="predict_btn"):
        if input_text.strip():
            with st.spinner("Predicting..."):
                start = time.time()
                try:
                    predictions = model.predict_top_k(input_text, k=top_k)
                    latency = (time.time() - start) * 1000
                    
                    st.success(f" Predictions ready ({latency:.1f}ms)")
                    
                    # Display predictions in columns
                    cols = st.columns(len(predictions))
                    for col, pred in zip(cols, predictions):
                        with col:
                            confidence = pred.get("confidence", 0)
                            st.metric(
                                label=pred["word"],
                                value=f"{confidence:.1%}"
                            )
                    
                    # Show full details
                    with st.expander(" Detailed Results"):
                        st.json(predictions)
                        
                except Exception as e:
                    st.error(f" Prediction failed: {str(e)}")
        else:
            st.warning(" Please enter some text")

# ------------------------------------------------------------------
# Page: Generate Text
# ------------------------------------------------------------------
elif page == " Generate Text":
    st.header(" Generate Text")
    st.write("Start with some text and let the model continue it.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        input_text = st.text_input(
            "Enter starting text:",
            value="the future",
            help="The model will generate text based on this"
        )
    with col2:
        num_words = st.slider("Words to generate:", 1, 20, 5)
    
    if st.button(" Generate", key="generate_btn"):
        if input_text.strip():
            with st.spinner("Generating..."):
                start = time.time()
                try:
                    generated = model.generate(input_text, num_words=num_words)
                    latency = (time.time() - start) * 1000
                    
                    st.success(f" Generated ({latency:.1f}ms)")
                    st.info(f"**Generated Text:** {generated}")
                    
                except Exception as e:
                    st.error(f" Generation failed: {str(e)}")
        else:
            st.warning(" Please enter some text")

# ------------------------------------------------------------------
# Page: Spell Check
# ------------------------------------------------------------------
elif page == " Spell Check":
    st.header(" Spell Check & Correction")
    st.write("Check and correct spelling mistakes in your text.")
    
    input_text = st.text_area(
        "Enter text to check:",
        value="i have a speling mistke",
        height=150,
        help="Type or paste text to check for spelling errors"
    )
    
    if st.button(" Check Spelling", key="spell_btn"):
        if input_text.strip():
            with st.spinner("Checking..."):
                try:
                    result = text_tools.correct_spelling(input_text)
                    
                    st.success(" Spell check complete")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Original Text")
                        st.write(input_text)
                    with col2:
                        st.subheader("Corrected Text")
                        st.write(result["corrected_text"])
                    
                    if result["corrections"]:
                        st.subheader(" Corrections Made")
                        for correction in result["corrections"]:
                            st.write(f"• **{correction['original']}** → **{correction['corrected']}**")
                    else:
                        st.info("No corrections needed!")
                        
                except Exception as e:
                    st.error(f" Spell check failed: {str(e)}")
        else:
            st.warning(" Please enter some text")

# ------------------------------------------------------------------
# Page: Synonyms
# ------------------------------------------------------------------
elif page == " Synonyms":
    st.header(" Find Synonyms")
    st.write("Find synonyms for a given word.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        word = st.text_input(
            "Enter a word:",
            value="happy",
            help="Enter a word to find synonyms"
        )
    with col2:
        limit = st.slider("Results:", 1, 10, 5)
    
    if st.button(" Find Synonyms", key="synonym_btn"):
        if word.strip():
            with st.spinner("Searching..."):
                try:
                    synonyms = text_tools.get_synonyms(word, limit=limit)
                    
                    if synonyms:
                        st.success(f" Found {len(synonyms)} synonym(s)")
                        cols = st.columns(min(5, len(synonyms)))
                        for col, syn in zip(cols, synonyms):
                            with col:
                                st.write(f"**{syn}**")
                    else:
                        st.info(f"No synonyms found for '{word}'")
                        
                except Exception as e:
                    st.error(f" Synonym search failed: {str(e)}")
        else:
            st.warning(" Please enter a word")

# ------------------------------------------------------------------
# Page: Summarization
# ------------------------------------------------------------------
elif page == " Summarize":
    st.header(" Text Summarization")
    st.write("Generate a summary of your text.")
    
    text = st.text_area(
        "Enter text to summarize:",
        value="Artificial intelligence is transforming industries. It powers recommendation systems, autonomous vehicles, and medical diagnostics. AI improves efficiency and accuracy, but raises concerns about job displacement and bias.",
        height=200,
        help="Paste your text here"
    )
    
    num_sentences = st.slider("Summary sentences:", 1, 5, 2)
    
    if st.button(" Summarize", key="summary_btn"):
        if text.strip():
            with st.spinner("Summarizing..."):
                try:
                    summary = text_tools.summarize(text, sentence_count=num_sentences)
                    
                    st.success(" Summary complete")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Original")
                        st.write(text)
                    with col2:
                        st.subheader("Summary")
                        st.write(summary)
                        
                except Exception as e:
                    st.error(f" Summarization failed: {str(e)}")
        else:
            st.warning(" Please enter some text")

# ------------------------------------------------------------------
# Page: Sentiment Analysis
# ------------------------------------------------------------------
elif page == " Sentiment Analysis":
    st.header(" Sentiment Analysis")
    st.write("Analyze the sentiment of your text.")
    
    text = st.text_area(
        "Enter text to analyze:",
        value="I absolutely love this product! It's amazing and works great.",
        height=150,
        help="Type or paste text to analyze"
    )
    
    if st.button(" Analyze Sentiment", key="sentiment_btn"):
        if text.strip():
            with st.spinner("Analyzing..."):
                try:
                    result = text_tools.analyze_sentiment(text)
                    
                    st.success(" Analysis complete")
                    
                    sentiment = result["label"]
                    
                    # Display sentiment badge
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Positive", f"{result['positive']:.1%}")
                    with col2:
                        st.metric("Neutral", f"{result['neutral']:.1%}")
                    with col3:
                        st.metric("Negative", f"{result['negative']:.1%}")
                    
                    # Overall sentiment
                    if sentiment == "positive":
                        st.success(f" **{sentiment.upper()}** (compound: {result['compound']:.2f})")
                    elif sentiment == "negative":
                        st.error(f" **{sentiment.upper()}** (compound: {result['compound']:.2f})")
                    else:
                        st.info(f" **{sentiment.upper()}** (compound: {result['compound']:.2f})")
                    
                except Exception as e:
                    st.error(f" Sentiment analysis failed: {str(e)}")
        else:
            st.warning(" Please enter some text")

# ------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown(
    """ 
    [GitHub](https://github.com) | [Docs](https://streamlit.io)
    """
)
