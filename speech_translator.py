import streamlit as st
from googletrans import Translator
import speech_recognition as sr
from gtts import gTTS
import os
import time
import tempfile
import sounddevice as sd
import soundfile as sf
import numpy as np
import queue
import threading
import logging
import base64
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('translator.log'),
        logging.StreamHandler()
    ]
)

# Set page configuration
st.set_page_config(
    page_title="AI Speech Translator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with improved styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        height: 3rem;
        margin: 1rem 0;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stButton>button:active {
        background-color: #3d8b40;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    .speaker-box {
        padding: 2rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 2px solid #e9ecef;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .history-entry {
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4CAF50;
        background-color: #f8f9fa;
    }
    .translation-status {
        margin-top: 1rem;
        padding: 0.5rem;
        border-radius: 4px;
    }
    .success-status {
        background-color: #d4edda;
        color: #155724;
    }
    .error-status {
        background-color: #f8d7da;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)

# Added function for text input as fallback
def get_text_input(language):
    """Get text input as fallback when speech recognition fails"""
    label = "Enter text in English:" if language == 'en-US' else "Ingrese texto en español:"
    return st.text_input(label, key=f"text_input_{language}")

def translate_text(text, src_lang, dest_lang):
    """Translate text between languages"""
    translator = Translator()
    try:
        with st.spinner("🔄 Translating..."):
            translation = translator.translate(text, src=src_lang, dest=dest_lang)
            logging.info(f"Translation successful: {text[:50]}... -> {translation.text[:50]}...")
            return translation.text
    except Exception as e:
        logging.error(f"Translation error: {str(e)}")
        st.error(f"⚠️ Translation error: {str(e)}")
        return None

def text_to_speech(text, lang):
    """Convert text to speech and save as audio file"""
    try:
        with st.spinner("🔊 Generating speech..."):
            tts = gTTS(text=text, lang=lang)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_filename = temp_file.name
            temp_file.close()
            tts.save(temp_filename)
            logging.info(f"Text-to-speech generated for: {text[:50]}...")
            return temp_filename
    except Exception as e:
        logging.error(f"Text-to-speech error: {str(e)}")
        st.error(f"⚠️ Text-to-speech error: {str(e)}")
        return None

def generate_audio_html(audio_file):
    """Generate HTML for audio playback"""
    try:
        with open(audio_file, 'rb') as f:
            audio_bytes = f.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        return f'<audio autoplay controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
    except Exception as e:
        logging.error(f"Error generating audio HTML: {str(e)}")
        return None

[Previous functions remain the same...]

def process_speech(src_lang, dest_lang, user_name):
    """Process speech with enhanced error handling and user feedback"""
    try:
        with st.spinner("Processing speech..."):
            # Try speech recognition first
            text = speech_to_text('en-US' if src_lang == 'en' else 'es-ES')
            
            # If speech recognition fails, use text input as fallback
            if not text:
                text = get_text_input('en-US' if src_lang == 'en' else 'es-ES')
            
            if text:
                # Add to history
                timestamp = time.strftime("%H:%M:%S")
                st.session_state.message_history.append({
                    'timestamp': timestamp,
                    'user': user_name,
                    'original': text,
                    'translated': None,
                    'success': False
                })
                
                # Translate
                translated_text = translate_text(text, src_lang, dest_lang)
                if translated_text:
                    # Update history
                    st.session_state.message_history[-1].update({
                        'translated': translated_text,
                        'success': True
                    })
                    
                    # Generate audio
                    audio_file = text_to_speech(translated_text, dest_lang)
                    if audio_file:
                        # Generate HTML audio element
                        audio_html = generate_audio_html(audio_file)
                        if audio_html:
                            st.markdown(audio_html, unsafe_allow_html=True)
                        
                        return audio_file
                    
    except Exception as e:
        logging.error(f"Error in speech processing: {str(e)}")
        st.error("An error occurred during speech processing")
    
    return None

[Rest of the code remains the same...]

if __name__ == "__main__":
    main()
