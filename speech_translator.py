import streamlit as st
from googletrans import Translator
from gtts import gTTS
import time
import tempfile
import os

# Page configuration
st.set_page_config(
    page_title="Multilingual Translator",
    page_icon="🌍",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stAudio {
        width: 100%;
    }
    .main {
        padding: 2rem;
    }
    .language-selector {
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .translation-box {
        padding: 1rem;
        background-color: white;
        border-radius: 0.5rem;
        border: 2px solid #e9ecef;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

# Language options
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh-cn': 'Chinese (Simplified)',
    'ar': 'Arabic',
    'hi': 'Hindi'
}

def initialize_session_state():
    """Initialize session state variables"""
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'translation_count' not in st.session_state:
        st.session_state.translation_count = 0

def text_to_speech(text, lang):
    """Convert text to speech and return audio file path"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts = gTTS(text=text, lang=lang)
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None

def translate_text(text, src_lang, dest_lang):
    """Translate text between languages"""
    if not text:
        return None
        
    translator = Translator()
    try:
        translation = translator.translate(text, src=src_lang, dest=dest_lang)
        return translation.text
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return None

def add_to_history(source_text, translated_text, src_lang, dest_lang):
    """Add translation to history"""
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.history.append({
        'timestamp': timestamp,
        'source_text': source_text,
        'translated_text': translated_text,
        'src_lang': LANGUAGES[src_lang],
        'dest_lang': LANGUAGES[dest_lang]
    })
    st.session_state.translation_count += 1

def main():
    initialize_session_state()
    
    # Title and description
    st.title("🌍 Multilingual Translator")
    st.markdown("Translate text between multiple languages instantly!")
    
    # Sidebar for instructions and stats
    with st.sidebar:
        st.header("📊 Statistics")
        st.metric("Translations Made", st.session_state.translation_count)
        
        st.markdown("---")
        st.header("ℹ️ Instructions")
        st.markdown("""
        1. Select your source and target languages
        2. Enter your text
        3. Click translate
        4. Listen to the translation
        
        **Supported Features:**
        - Text translation
        - Audio output
        - Translation history
        - Multiple languages
        """)
    
    # Create two columns for source and target languages
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Source Language")
        src_lang = st.selectbox(
            "Select input language",
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            key='src_lang'
        )
        
        source_text = st.text_area(
            "Enter text to translate",
            height=150,
            key='source_text',
            placeholder="Type or paste your text here..."
        )
    
    with col2:
        st.markdown("### Target Language")
        dest_lang = st.selectbox(
            "Select output language",
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            key='dest_lang'
        )
        
        # Translate button
        if st.button("🔄 Translate", type="primary"):
            if source_text:
                with st.spinner("Translating..."):
                    translated_text = translate_text(source_text, src_lang, dest_lang)
                    
                    if translated_text:
                        st.markdown("### Translation")
                        st.markdown(f"""
                        <div class='translation-box'>
                            <div style='font-size: 1.1em;'>{translated_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Generate audio for translation
                        with st.spinner("Generating audio..."):
                            audio_file = text_to_speech(translated_text, dest_lang)
                            if audio_file:
                                st.audio(audio_file)
                                os.unlink(audio_file)  # Clean up
                            
                        # Add to history
                        add_to_history(source_text, translated_text, src_lang, dest_lang)
            else:
                st.warning("Please enter some text to translate.")
    
    # Translation History
    st.markdown("---")
    col_history, col_clear = st.columns([5,1])
    
    with col_history:
        st.markdown("### 📜 Translation History")
    
    with col_clear:
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.session_state.translation_count = 0
            st.experimental_rerun()
    
    if not st.session_state.history:
        st.info("No translations yet. Start translating to build history!")
    else:
        for item in reversed(st.session_state.history):
            st.markdown(f"""
            <div style='padding: 1rem; margin: 0.5rem 0; border-left: 4px solid #3498db; 
                        background-color: #f8f9fa; border-radius: 4px;'>
                <small>{item['timestamp']}</small><br>
                <strong>{item['src_lang']} → {item['dest_lang']}</strong><br>
                <div style='margin: 0.5rem 0;'>
                    <strong>Original:</strong> {item['source_text']}<br>
                    <strong>Translation:</strong> {item['translated_text']}
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

