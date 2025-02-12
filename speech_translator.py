import streamlit as st
from googletrans import Translator
import speech_recognition as sr
from gtts import gTTS
import os
import time
import tempfile
from logger_setup import (
    setup_logger,
    log_speech_event,
    log_error,
    log_translation_event,
    log_api_usage,
    get_log_summary
)
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import queue

# Set page configuration
st.set_page_config(
    page_title="AI Speech Translator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        height: 3rem;
        margin: 1rem 0;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .speaker-box {
        padding: 2rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 2px solid #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'message_history' not in st.session_state:
        st.session_state.message_history = []
    if 'audio_queue' not in st.session_state:
        st.session_state.audio_queue = queue.Queue()
    if 'listening_status' not in st.session_state:
        st.session_state.listening_status = False

def speech_to_text(language='en-US'):
    """Convert speech to text using speech recognition"""
    start_time = time.time()
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # Visual feedback for listening state
        status_placeholder = st.empty()
        status_placeholder.info(f"🎤 Listening... (Speaking in {'English' if language=='en-US' else 'Spanish'})")
        st.session_state.listening_status = True
        
        # Adjust for ambient noise
        r.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            status_placeholder.info("🔍 Processing speech...")
            
            text = r.recognize_google(audio, language=language)
            status_placeholder.success("✅ Speech processed successfully!")
            time.sleep(1)
            status_placeholder.empty()
            duration = (time.time() - start_time) * 1000
            log_api_usage("speech_recognition", True, duration)
            return text
            
        except sr.WaitTimeoutError:
            status_placeholder.error("⚠️ No speech detected. Please try again.")
            time.sleep(2)
            status_placeholder.empty()
            return None
        except sr.UnknownValueError:
            status_placeholder.error("⚠️ Could not understand audio. Please speak clearly and try again.")
            time.sleep(2)
            status_placeholder.empty()
            return None
        except sr.RequestError:
            status_placeholder.error("⚠️ Could not connect to speech recognition service. Please check your internet connection.")
            time.sleep(2)
            status_placeholder.empty()
            return None
        finally:
            st.session_state.listening_status = False

def translate_text(text, src_lang, dest_lang):
    """Translate text between languages"""
    start_time = time.time()
    translator = Translator()
    try:
        with st.spinner("🔄 Translating..."):
            translation = translator.translate(text, src=src_lang, dest=dest_lang)
        duration = (time.time() - start_time) * 1000
        log_translation_event(src_lang, dest_lang, True, duration)
        return translation.text
    except Exception as e:
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
        return temp_filename
    except Exception as e:
        st.error(f"⚠️ Text-to-speech error: {str(e)}")
        return None

def play_audio(audio_file):
    """Play audio file using playsound"""
    try:
        with st.spinner("🎵 Playing translation..."):
            playsound(audio_file)
        os.unlink(audio_file)  # Clean up temporary file
    except Exception as e:
        st.error(f"⚠️ Audio playback error: {str(e)}")

def process_speech(src_lang, dest_lang, user_name):
    """Process speech: convert to text, translate, and convert back to speech"""
    # Speech to text
    text = speech_to_text('en-US' if src_lang == 'en' else 'es-ES')
    if text:
        # Add original text to history with timestamp
        timestamp = time.strftime("%H:%M:%S")
        st.session_state.message_history.append({
            'timestamp': timestamp,
            'user': user_name,
            'original': text,
            'translated': None
        })
        
        # Translate
        translated_text = translate_text(text, src_lang, dest_lang)
        if translated_text:
            # Update history with translation
            st.session_state.message_history[-1]['translated'] = translated_text
            
            # Text to speech
            audio_file = text_to_speech(translated_text, dest_lang)
            return audio_file
    return None

def display_conversation_history():
    """Display conversation history in a structured format"""
    st.subheader("💬 Conversation History")
    
    if not st.session_state.message_history:
        st.info("No conversation history yet. Start speaking to begin!")
        return
        
    for msg in st.session_state.message_history:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **{msg['user']} ({msg['timestamp']}):**  
            🗣️ Original: _{msg['original']}_
            """)
            
        with col2:
            if msg['translated']:
                st.markdown(f"""
                **Translation:**  
                🔄 _{msg['translated']}_
                """)

def main():
    # Initialize logger
    setup_logger()
    log_speech_event("app_start", {"version": "1.0.0"})
    
    # Sidebar with instructions
    with st.sidebar:
        st.title("ℹ️ Instructions")
        st.markdown("""
        1. Choose your language (English or Spanish)
        2. Click the 'Speak' button
        3. Speak clearly into your microphone
        4. Wait for the translation
        5. Listen to the translated audio
        
        **Note:** Make sure your microphone is properly connected and you have a stable internet connection.
        """)
        
        st.markdown("---")
        st.subheader("🛠️ Technical Requirements")
        st.markdown("""
        - Working microphone
        - Stable internet connection
        - Speakers or headphones
        """)
        
        st.markdown("---")
        st.subheader("📊 Usage Statistics")
        if st.button("View Today's Statistics"):
            summary = get_log_summary()
            st.write(f"Total Translations: {summary['total_translations']}")
            st.write(f"Success Rate: {(summary['successful_translations']/summary['total_translations']*100 if summary['total_translations'] > 0 else 0):.1f}%")
            st.write(f"Average Translation Time: {summary['average_translation_time']:.1f}ms")
            st.write("Most Used Language Pairs:")
            for pair, count in sorted(summary['language_pairs'].items(), key=lambda x: x[1], reverse=True)[:3]:
                st.write(f"- {pair}: {count} translations")
        
        st.markdown("---")
        if st.button("🗑️ Clear History"):
            st.session_state.message_history = []
            st.experimental_rerun()
    
    # Main content
    st.title("🌎 AI Real-time Speech Translator")
    st.markdown("Enable seamless communication between English and Spanish speakers")
    
    initialize_session_state()
    
    # Speaker interfaces
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="speaker-box">
            <h2>🇺🇸 English Speaker (User 1)</h2>
        """, unsafe_allow_html=True)
        
        if not st.session_state.listening_status:
            if st.button("🎤 Speak English", key="en_button"):
                audio_file = process_speech('en', 'es', 'English Speaker')
                if audio_file:
                    st.session_state.audio_queue.put(audio_file)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="speaker-box">
            <h2>🇪🇸 Spanish Speaker (User 2)</h2>
        """, unsafe_allow_html=True)
        
        if not st.session_state.listening_status:
            if st.button("🎤 Hablar Español", key="es_button"):
                audio_file = process_speech('es', 'en', 'Spanish Speaker')
                if audio_file:
                    st.session_state.audio_queue.put(audio_file)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display conversation history
    st.markdown("---")
    display_conversation_history()
    
    # Process audio queue
    while not st.session_state.audio_queue.empty():
        audio_file = st.session_state.audio_queue.get()
        play_audio(audio_file)

if __name__ == "__main__":
    main()
