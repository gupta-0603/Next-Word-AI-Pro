"""
Enhanced Streamlit app for Next Word AI
With new features and improved UI
"""

import time
import streamlit as st
import pandas as pd
from pathlib import Path
from io import StringIO
import json

from app.model_utils import load_default_model
from app.text_tools import load_text_tools

# ------------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Next Word AI Pro",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
def get_theme_css(theme):
    """Generate CSS based on selected theme"""
    if theme == "Dark":
        return """
        <style>
            .main {
                padding-top: 2rem;
            }
            [data-testid="metric-container"] {
                background-color: #1e3a8a !important;
                padding: 1.5rem !important;
                border-radius: 0.75rem !important;
                border: 2px solid #3b82f6 !important;
            }
            [data-testid="metric-container"] label {
                color: #60a5fa !important;
                font-size: 14px !important;
                font-weight: 600 !important;
            }
            [data-testid="metric-container"] > div:last-child {
                color: #10b981 !important;
                font-size: 24px !important;
                font-weight: bold !important;
            }
            .stMetric {
                background-color: #1e3a8a;
                padding: 1.5rem;
                border-radius: 0.75rem;
                border: 2px solid #3b82f6;
            }
            .feature-box {
                background-color: #1e40af;
                padding: 1.5rem;
                border-radius: 0.75rem;
                border-left: 4px solid #60a5fa;
                margin-bottom: 1rem;
                color: #e0e7ff;
            }
            .success-box {
                background-color: #064e3b;
                padding: 1rem;
                border-radius: 0.5rem;
                color: #d1fae5;
            }
            .stButton > button {
                background-color: #3b82f6 !important;
                color: white !important;
            }
        </style>
        """
    else:  # Light theme
        return """
        <style>
            .main {
                padding-top: 2rem;
            }
            [data-testid="metric-container"] {
                background-color: #dbeafe !important;
                padding: 1.5rem !important;
                border-radius: 0.75rem !important;
                border: 2px solid #0284c7 !important;
            }
            [data-testid="metric-container"] label {
                color: #0c4a6e !important;
                font-size: 14px !important;
                font-weight: 600 !important;
            }
            [data-testid="metric-container"] > div:last-child {
                color: #059669 !important;
                font-size: 24px !important;
                font-weight: bold !important;
            }
            .stMetric {
                background-color: #e0f2fe;
                padding: 1.5rem;
                border-radius: 0.75rem;
                border: 2px solid #0284c7;
            }
            .feature-box {
                background-color: #e0e7ff;
                padding: 1.5rem;
                border-radius: 0.75rem;
                border-left: 4px solid #3b82f6;
                margin-bottom: 1rem;
                color: #1e1b4b;
            }
            .success-box {
                background-color: #d1fae5;
                padding: 1rem;
                border-radius: 0.5rem;
                color: #065f46;
            }
            .stButton > button {
                background-color: #0284c7 !important;
                color: white !important;
            }
        </style>
        """

# ------------------------------------------------------------------
# Session State Initialization (MUST BE FIRST!)
# ------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

# NOW apply the CSS after session state is ready
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

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
# Helper Functions
# ------------------------------------------------------------------
def add_to_history(feature, input_text, result):
    """Add result to history"""
    st.session_state.history.append({
        "feature": feature,
        "input": input_text[:100],
        "result": str(result)[:100],
        "timestamp": time.strftime("%H:%M:%S")
    })
    if len(st.session_state.history) > 10:
        st.session_state.history.pop(0)

def export_to_csv(data):
    """Convert data to CSV"""
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8')

def export_to_json(data):
    """Convert data to JSON"""
    return json.dumps(data, indent=2).encode('utf-8')

# ------------------------------------------------------------------
# Sidebar Navigation & Settings
# ------------------------------------------------------------------
with st.sidebar:
    st.title(" Next Word AI Pro")
    
    st.markdown("---")
    
    # Settings Section
    with st.expander(" Settings", expanded=False):
        new_theme = st.radio(" Theme:", ["Light", "Dark"])
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()
        show_stats = st.checkbox(" Show Statistics", value=True)
        auto_correct = st.checkbox(" Auto Correct Spelling", value=True)
    
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        " Select Feature:",
        [
            " Home",
            " Predict Next Words",
            " Generate Text",
            " Spell Check",
            " Synonyms",
            " Summarize",
            " Sentiment Analysis",
            " Smart Analysis",
            " Batch Processing",
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # History Section
    if st.session_state.history:
        with st.expander(" Recent History"):
            for i, item in enumerate(reversed(st.session_state.history[-5:])):
                st.caption(f"**{item['feature']}** - {item['timestamp']}")
                st.text(item['input'])
    
    st.markdown("---")
    st.caption("")

# ------------------------------------------------------------------
# HOME PAGE
# ------------------------------------------------------------------
if page == " Home":
    st.title(" Welcome to Next Word AI Pro")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ###  Features
        
        **Text Analysis:**
        -  Predict next words with confidence scores
        -  Generate full text from seed phrases
        -  Spell check & correction
        -  Find synonyms instantly
        
        **NLP Tools:**
        -  Extractive summarization
        -  Sentiment analysis (positive/neutral/negative)
        -  Smart analysis combining multiple tools
        -  Batch processing for files
        """)
    
    with col2:
        st.markdown("""
        ###  Quick Stats
        
        **Your Activity:**
        - Recent actions: {0}
        - Favorite feature: Analysis
        - Processing speed: Fast 
        
        ###  Tips
        - Start with the Home page to understand features
        - Use Smart Analysis for combined insights
        - Batch process multiple texts at once
        - Export results as CSV or JSON
        """.format(len(st.session_state.history)))
    
    st.markdown("---")
    
    # Feature Overview
    st.subheader(" Feature Overview")
    
    features = {
        " Predict Next Words": "Get top predictions for the next word based on context",
        " Generate Text": "Extend your text with AI-generated continuations",
        " Spell Check": "Detect and correct spelling errors automatically",
        " Synonyms": "Find alternative words with similar meanings",
        " Summarize": "Get concise summaries of longer texts",
        " Sentiment": "Analyze emotional tone (positive/negative/neutral)",
        " Smart Analysis": "Combine multiple analysis tools for deep insights",
        " Batch Processing": "Process multiple texts or upload files",
    }
    
    cols = st.columns(2)
    for idx, (feature, desc) in enumerate(features.items()):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class='feature-box'>
                <b>{feature}</b><br>
                {desc}
            </div>
            """, unsafe_allow_html=True)

# ------------------------------------------------------------------
# PREDICT NEXT WORDS
# ------------------------------------------------------------------
elif page == " Predict Next Words":
    st.header(" Predict Next Words")
    st.write("Enter text and get top predictions for the next word.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        input_text = st.text_input(
            "Enter text:",
            value="the quick brown",
            placeholder="Type your text here..."
        )
    with col2:
        top_k = st.slider("Top K:", 1, 10, 5)
    
    if st.button(" Predict", key="predict_btn", use_container_width=True):
        if input_text.strip():
            with st.spinner(" Analyzing context..."):
                start = time.time()
                try:
                    predictions = model.predict_top_k(input_text, k=top_k)
                    latency = (time.time() - start) * 1000
                    
                    add_to_history("Predict", input_text, predictions)
                    
                    st.success(f" Predictions ready ({latency:.1f}ms)")
                    
                    # Display predictions in columns
                    cols = st.columns(len(predictions))
                    for col, pred in zip(cols, predictions):
                        with col:
                            confidence = pred.get("confidence", 0)
                            st.metric(
                                label=f"#{pred['word'].upper()}",
                                value=f"{confidence:.1%}",
                                delta=f"{confidence*100:.0f}%"
                            )
                    
                    # Show full details
                    with st.expander(" Detailed Results"):
                        df = pd.DataFrame(predictions)
                        st.dataframe(df, use_container_width=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                "📥 Download CSV",
                                export_to_csv(predictions),
                                "predictions.csv",
                                "text/csv"
                            )
                        with col2:
                            st.download_button(
                                "📥 Download JSON",
                                export_to_json(predictions),
                                "predictions.json",
                                "application/json"
                            )
                        
                except Exception as e:
                    st.error(f" Prediction failed: {str(e)}")
        else:
            st.warning(" Please enter some text")

# ------------------------------------------------------------------
# GENERATE TEXT
# ------------------------------------------------------------------
elif page == " Generate Text":
    st.header(" Generate Text")
    st.write("Start with some text and let the model continue it.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        input_text = st.text_input(
            "Enter starting text:",
            value="the future",
            placeholder="Type your seed text..."
        )
    with col2:
        num_words = st.slider("Words:", 1, 20, 5)
    
    if st.button(" Generate", key="generate_btn", use_container_width=True):
        if input_text.strip():
            with st.spinner(" Generating text..."):
                start = time.time()
                try:
                    generated = model.generate_text(input_text, num_words=num_words)
                    latency = (time.time() - start) * 1000
                    
                    add_to_history("Generate", input_text, generated)
                    
                    st.success(f" Generated ({latency:.1f}ms)")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Original Text:**")
                        st.info(input_text)
                    with col2:
                        st.markdown("**Generated Text:**")
                        st.success(generated)
                    
                    # Copy button
                    st.text_area("Full text (copy below):", value=generated, height=100, disabled=True)
                    
                except Exception as e:
                    st.error(f" Generation failed: {str(e)}")
        else:
            st.warning(" Please enter some text")

# ------------------------------------------------------------------
# SPELL CHECK
# ------------------------------------------------------------------
elif page == " Spell Check":
    st.header(" Spell Check & Correction")
    st.write("Detect and correct spelling mistakes automatically.")
    
    input_text = st.text_area(
        "Enter text to check:",
        value="i have a speling mistke",
        height=150,
        placeholder="Paste your text here..."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(" Check & Fix", key="spell_btn", use_container_width=True):
            if input_text.strip():
                with st.spinner(" Checking..."):
                    try:
                        result = text_tools.correct_spelling(input_text)
                        add_to_history("Spell Check", input_text, result)
                        
                        st.success(" Check complete")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("Original")
                            st.info(input_text)
                        with col2:
                            st.subheader("Corrected")
                            st.success(result["corrected_text"])
                        
                        if result["corrections"]:
                            st.subheader(f" {len(result['corrections'])} Corrections")
                            df = pd.DataFrame(result["corrections"])
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.info("✓ No corrections needed!")
                            
                    except Exception as e:
                        st.error(f" Failed: {str(e)}")
            else:
                st.warning(" Please enter text")

# ------------------------------------------------------------------
# SYNONYMS
# ------------------------------------------------------------------
elif page == " Synonyms":
    st.header(" Find Synonyms")
    st.write("Discover alternative words with similar meanings.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        word = st.text_input(
            "Enter a word:",
            value="happy",
            placeholder="Type a word..."
        )
    with col2:
        limit = st.slider("Results:", 1, 10, 5)
    
    if st.button(" Find Synonyms", key="synonym_btn", use_container_width=True):
        if word.strip():
            with st.spinner(" Searching..."):
                try:
                    synonyms = text_tools.get_synonyms(word, limit=limit)
                    add_to_history("Synonyms", word, synonyms)
                    
                    if synonyms:
                        st.success(f" Found {len(synonyms)} synonym(s)")
                        
                        cols = st.columns(min(5, len(synonyms)))
                        for col, syn in zip(cols, synonyms):
                            with col:
                                st.metric(label="Word", value=syn)
                        
                        st.dataframe(pd.DataFrame({"Synonyms": synonyms}), use_container_width=True)
                    else:
                        st.info(f"No synonyms found for '{word}'")
                        
                except Exception as e:
                    st.error(f" Search failed: {str(e)}")
        else:
            st.warning(" Please enter a word")

# ------------------------------------------------------------------
# SUMMARIZATION
# ------------------------------------------------------------------
elif page == " Summarize":
    st.header(" Text Summarization")
    st.write("Extract key points and create concise summaries.")
    
    text = st.text_area(
        "Enter text to summarize:",
        value="Artificial intelligence is transforming industries. It powers recommendation systems, autonomous vehicles, and medical diagnostics. AI improves efficiency and accuracy, but raises concerns about job displacement and bias.",
        height=200,
        placeholder="Paste your text here..."
    )
    
    num_sentences = st.slider("Summary sentences:", 1, 5, 2)
    
    if st.button(" Summarize", key="summary_btn", use_container_width=True):
        if text.strip():
            with st.spinner(" Summarizing..."):
                try:
                    summary = text_tools.summarize(text, sentence_count=num_sentences)
                    add_to_history("Summarize", text, summary)
                    
                    st.success(" Summary complete")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Original")
                        st.info(text)
                        st.caption(f"Words: {len(text.split())}")
                    with col2:
                        st.subheader("Summary")
                        st.success(summary)
                        st.caption(f"Words: {len(summary.split())}")
                    
                    compression = (1 - len(summary.split()) / len(text.split())) * 100
                    st.metric("Compression Ratio", f"{compression:.1f}%")
                        
                except Exception as e:
                    st.error(f" Failed: {str(e)}")
        else:
            st.warning(" Please enter text")

# ------------------------------------------------------------------
# SENTIMENT ANALYSIS
# ------------------------------------------------------------------
elif page == " Sentiment Analysis":
    st.header(" Sentiment Analysis")
    st.write("Analyze emotional tone and opinions in text.")
    
    text = st.text_area(
        "Enter text to analyze:",
        value="I absolutely love this product! It's amazing and works great.",
        height=150,
        placeholder="Type your text here..."
    )
    
    if st.button(" Analyze", key="sentiment_btn", use_container_width=True):
        if text.strip():
            with st.spinner("🔍 Analyzing..."):
                try:
                    result = text_tools.analyze_sentiment(text)
                    add_to_history("Sentiment", text, result)
                    
                    st.success(" Analysis complete")
                    
                    sentiment = result["label"]
                    
                    # Display scores
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(" Positive", f"{result['positive']:.1%}")
                    with col2:
                        st.metric(" Neutral", f"{result['neutral']:.1%}")
                    with col3:
                        st.metric(" Negative", f"{result['negative']:.1%}")
                    
                    # Overall sentiment
                    st.markdown("---")
                    if sentiment == "positive":
                        st.success(f" **POSITIVE** Sentiment (Compound: {result['compound']:.2f})")
                    elif sentiment == "negative":
                        st.error(f" **NEGATIVE** Sentiment (Compound: {result['compound']:.2f})")
                    else:
                        st.info(f" **NEUTRAL** Sentiment (Compound: {result['compound']:.2f})")
                    
                except Exception as e:
                    st.error(f" Analysis failed: {str(e)}")
        else:
            st.warning(" Please enter text")

# ------------------------------------------------------------------
# SMART ANALYSIS (NEW FEATURE)
# ------------------------------------------------------------------
elif page == " Smart Analysis":
    st.header(" Smart Analysis")
    st.write("Run multiple analysis tools at once for deep insights.")
    
    text = st.text_area(
        "Enter text for analysis:",
        value="AI is revolutionizing everything! I'm so excited about the future.",
        height=150,
        placeholder="Paste your text here..."
    )
    
    # Select tools
    col1, col2, col3 = st.columns(3)
    with col1:
        check_sentiment = st.checkbox("Sentiment Analysis", value=True)
    with col2:
        check_summary = st.checkbox("Summarization", value=False)
    with col3:
        check_spell = st.checkbox("Spell Check", value=False)
    
    if st.button(" Analyze All", key="smart_btn", use_container_width=True):
        if text.strip():
            with st.spinner(" Running analysis..."):
                start = time.time()
                results = {}
                
                try:
                    if check_sentiment:
                        results["Sentiment"] = text_tools.analyze_sentiment(text)
                        st.markdown("###  Sentiment Analysis")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Positive", f"{results['Sentiment']['positive']:.1%}")
                        with col2:
                            st.metric("Neutral", f"{results['Sentiment']['neutral']:.1%}")
                        with col3:
                            st.metric("Negative", f"{results['Sentiment']['negative']:.1%}")
                        st.write(f"Label: **{results['Sentiment']['label'].upper()}**")
                        st.markdown("---")
                    
                    if check_summary:
                        results["Summary"] = text_tools.summarize(text, sentence_count=2)
                        st.markdown("###  Summary")
                        st.info(results["Summary"])
                        st.markdown("---")
                    
                    if check_spell:
                        results["Spelling"] = text_tools.correct_spelling(text)
                        st.markdown("###  Spelling")
                        if results["Spelling"]["corrections"]:
                            st.write(f"Found {len(results['Spelling']['corrections'])} errors")
                            st.dataframe(pd.DataFrame(results["Spelling"]["corrections"]))
                        else:
                            st.success("✓ No spelling errors!")
                        st.markdown("---")
                    
                    latency = (time.time() - start) * 1000
                    st.success(f" Analysis complete ({latency:.1f}ms)")
                    
                    add_to_history("Smart Analysis", text, results)
                    
                except Exception as e:
                    st.error(f" Analysis failed: {str(e)}")
        else:
            st.warning(" Please enter text")

# ------------------------------------------------------------------
# BATCH PROCESSING (NEW FEATURE)
# ------------------------------------------------------------------
elif page == " Batch Processing":
    st.header(" Batch Processing")
    st.write("Process multiple texts or upload a file at once.")
    
    tab1, tab2 = st.tabs([" Multiple Texts", " Upload File"])
    
    with tab1:
        st.subheader("Process Multiple Texts")
        
        analysis_type = st.selectbox(
            "Choose analysis:",
            ["Sentiment Analysis", "Spell Check", "Summarization"]
        )
        
        num_texts = st.number_input("Number of texts:", min_value=1, max_value=10, value=2)
        
        texts = []
        for i in range(num_texts):
            text = st.text_area(f"Text {i+1}:", height=80, key=f"batch_{i}")
            if text:
                texts.append(text)
        
        if st.button(" Process All", use_container_width=True):
            if texts:
                with st.spinner("Processing..."):
                    results = []
                    
                    try:
                        for idx, text in enumerate(texts):
                            if analysis_type == "Sentiment Analysis":
                                result = text_tools.analyze_sentiment(text)
                                results.append({
                                    "Text": text[:50],
                                    "Sentiment": result["label"],
                                    "Score": f"{result['positive']:.2f}"
                                })
                            elif analysis_type == "Spell Check":
                                result = text_tools.correct_spelling(text)
                                results.append({
                                    "Text": text[:50],
                                    "Errors": len(result["corrections"]),
                                    "Corrected": result["corrected_text"][:50]
                                })
                            elif analysis_type == "Summarization":
                                result = text_tools.summarize(text, sentence_count=1)
                                results.append({
                                    "Original": text[:40],
                                    "Summary": result[:40]
                                })
                        
                        df = pd.DataFrame(results)
                        st.dataframe(df, use_container_width=True)
                        
                        # Export buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                " Download CSV",
                                export_to_csv(results),
                                "batch_results.csv",
                                "text/csv",
                                use_container_width=True
                            )
                        with col2:
                            st.download_button(
                                " Download JSON",
                                export_to_json(results),
                                "batch_results.json",
                                "application/json",
                                use_container_width=True
                            )
                        
                    except Exception as e:
                        st.error(f" Processing failed: {str(e)}")
            else:
                st.warning(" Please enter at least one text")
    
    with tab2:
        st.subheader("Upload & Process File")
        
        uploaded_file = st.file_uploader("Choose a .txt file", type="txt")
        
        file_analysis = st.selectbox(
            "Analysis type:",
            ["Sentiment Analysis", "Spell Check"],
            key="file_analysis"
        )
        
        if uploaded_file and st.button("📤 Process File", use_container_width=True):
            with st.spinner("Processing file..."):
                try:
                    content = uploaded_file.read().decode("utf-8")
                    lines = [line.strip() for line in content.split("\n") if line.strip()]
                    
                    results = []
                    for line in lines[:20]:  # Limit to first 20 lines
                        if file_analysis == "Sentiment Analysis":
                            result = text_tools.analyze_sentiment(line)
                            results.append({
                                "Text": line[:50],
                                "Sentiment": result["label"],
                                "Confidence": f"{max(result['positive'], result['negative']):.2f}"
                            })
                        else:
                            result = text_tools.correct_spelling(line)
                            results.append({
                                "Text": line[:50],
                                "Errors": len(result["corrections"])
                            })
                    
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
                    
                    st.download_button(
                        " Download Results",
                        export_to_csv(results),
                        "file_results.csv",
                        "text/csv",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f" File processing failed: {str(e)}")

# ------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    
   Tip: Use the Settings menu to customize your experience
</div>
""", unsafe_allow_html=True)
