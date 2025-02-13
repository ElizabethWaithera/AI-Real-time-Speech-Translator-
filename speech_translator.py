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

def main():
    initialize_session_state()
    
    # Title and description
    st.title("🌍 Multilingual Voice Translator")
    st.markdown("Translate text and speech between multiple languages instantly!")
    
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
        
        # Input methods
        input_method = st.radio(
            "Choose input method",
            ["Text Input", "Voice Input (Microphone)"]
        )
        
        if input_method == "Text Input":
            source_text = st.text_area("Enter text to translate", key='source_text')
        else:
            # Use Streamlit's built-in audio recorder
            audio_bytes = st.audio_recorder(
                text="Click to record",
                recording_color="#e74c3c",
                neutral_color="#3498db"
            )
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                st.info("Voice input received! (Note: Speech-to-text processing would go here)")
                source_text = st.text_input("Or type your text here", key='voice_text')
    
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
            if 'source_text' in locals() and source_text:
                with st.spinner("Translating..."):
                    translated_text = translate_text(source_text, src_lang, dest_lang)
                    
                    if translated_text:
                        st.markdown("### Translation")
                        st.markdown(f"<div class='translation-box'>{translated_text}</div>", 
                                  unsafe_allow_html=True)
                        
                        # Generate audio for translation
                        audio_file = text_to_speech(translated_text, dest_lang)
                        if audio_file:
                            st.audio(audio_file)
                            os.unlink(audio_file)  # Clean up
                            
                        # Add to history
                        add_to_history(source_text, translated_text, src_lang, dest_lang)
    
    # Translation History
    st.markdown("---")
    st.markdown("### 📜 Translation History")
    
    if not st.session_state.history:
        st.info("No translations yet. Start translating to build history!")
    else:
        for item in reversed(st.session_state.history):
            st.markdown(f"""
            <div style='padding: 1rem; margin: 0.5rem 0; border-left: 4px solid #3498db; background-color: #f8f9fa;'>
                <small>{item['timestamp']}</small><br>
                <strong>{item['src_lang']} → {item['dest_lang']}</strong><br>
                Original: {item['source_text']}<br>
                Translation: {item['translated_text']}
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("Clear History"):
            st.session_state.history = []
            st.experimental_rerun()

if __name__ == "__main__":
    main()

