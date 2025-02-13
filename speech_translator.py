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
def create_audio_device():
    """Create and configure audio device with error handling"""
    try:
        return sr.Microphone()
    except Exception as e:
        logging.error(f"Error creating audio device: {str(e)}")
        st.error("Could not initialize microphone. Please check your audio settings.")
        return None

def speech_to_text(language='en-US'):
    """Enhanced speech to text conversion with better error handling and feedback"""
    r = sr.Recognizer()
    audio_device = create_audio_device()
    
    if not audio_device:
        return None
        
    with audio_device as source:
        status_placeholder = st.empty()
        try:
            # Visual feedback
            status_placeholder.info(f"🎤 Listening... (Speaking in {'English' if language=='en-US' else 'Spanish'})")
            st.session_state.listening_status = True
            
            # Improve noise handling
            r.adjust_for_ambient_noise(source, duration=1.0)
            r.dynamic_energy_threshold = True
            
            # Record with timeout
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            status_placeholder.info("🔍 Processing speech...")
            
            # Multiple recognition attempts
            for attempt in range(2):
                try:
                    text = r.recognize_google(audio, language=language)
                    status_placeholder.success("✅ Speech processed successfully!")
                    time.sleep(1)
                    status_placeholder.empty()
                    st.session_state.error_count = 0  # Reset error count on success
                    return text
                except sr.UnknownValueError:
                    if attempt == 0:
                        continue
                    raise
                
        except sr.WaitTimeoutError:
            handle_error(status_placeholder, "No speech detected. Please try again.")
        except sr.UnknownValueError:
            handle_error(status_placeholder, "Could not understand audio. Please speak clearly.")
        except sr.RequestError:
            handle_error(status_placeholder, "Speech recognition service error. Please check your internet connection.")
        except Exception as e:
            handle_error(status_placeholder, f"Unexpected error: {str(e)}")
        finally:
            st.session_state.listening_status = False
            
    return None

def handle_error(placeholder, message):
    """Centralized error handling with user feedback"""
    logging.error(message)
    placeholder.error(f"⚠️ {message}")
    st.session_state.error_count += 1
    
    # Suggest solutions based on error count
    if st.session_state.error_count >= 3:
        st.warning("""
        Having trouble? Try these steps:
        1. Check your microphone connection
        2. Speak closer to the microphone
        3. Reduce background noise
        4. Ensure you have a stable internet connection
        """)
    
    time.sleep(2)
    placeholder.empty()

def play_audio(audio_file):
    """Play audio using sounddevice for better compatibility"""
    try:
        with st.spinner("🎵 Playing translation..."):
            data, samplerate = sf.read(audio_file)
            sd.play(data, samplerate)
            sd.wait()  # Wait until audio is finished playing
        os.unlink(audio_file)  # Clean up
    except Exception as e:
        logging.error(f"Audio playback error: {str(e)}")
        st.error("Could not play audio. Please check your speaker settings.")

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

def display_conversation_history():
    """Display conversation history in a structured format"""
    st.subheader("💬 Conversation History")
    
    if not st.session_state.message_history:
        st.info("No conversation history yet. Start speaking to begin!")
        return
        
    for msg in reversed(st.session_state.message_history):
        with st.container():
            st.markdown(f"""
            <div class="history-entry">
                <strong>{msg['user']} ({msg['timestamp']})</strong><br>
                🗣️ Original: <i>{msg['original']}</i><br>
                {f"🔄 Translation: <i>{msg['translated']}</i>" if msg['translated'] else ""}
            </div>
            """, unsafe_allow_html=True)

def main():
    # Initialize
    initialize_session_state()
    
    # Header
    st.title("🌎 AI Real-time Speech Translator")
    st.markdown("Enable seamless communication between English and Spanish speakers")
    
    # Sidebar with enhanced instructions
    with st.sidebar:
        st.title("ℹ️ Instructions")
        st.markdown("""
        1. Choose your language (English or Spanish)
        2. Click the 'Speak' button when ready
        3. Speak clearly into your microphone
        4. Wait for the translation
        5. Listen to the translated audio
        
        **Tips for Best Results:**
        - Use a good quality microphone
        - Speak clearly and at a normal pace
        - Minimize background noise
        - Keep sentences reasonably short
        """)
        
        st.markdown("---")
        
        # Add system status indicators
        st.subheader("🔧 System Status")
        audio_status = "✅ Ready" if create_audio_device() else "❌ Not Available"
        st.markdown(f"**Microphone:** {audio_status}")
        
        if st.button("🗑️ Clear History"):
            st.session_state.message_history = []
            st.experimental_rerun()
    
    # Speaker interfaces
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="speaker-box">
            <h2>🇺🇸 English Speaker (User 1)</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.listening_status:
            if st.button("🎤 Speak English", key="en_button"):
                audio_file = process_speech('en', 'es', 'English Speaker')
                if audio_file:
                    st.session_state.audio_queue.put(audio_file)
    
    with col2:
        st.markdown("""
        <div class="speaker-box">
            <h2>🇪🇸 Spanish Speaker (User 2)</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.listening_status:
            if st.button("🎤 Hablar Español", key="es_button"):
                audio_file = process_speech('es', 'en', 'Spanish Speaker')
                if audio_file:
                    st.session_state.audio_queue.put(audio_file)
    
    # Display conversation history
    st.markdown("---")
    display_conversation_history()
    
    # Process audio queue
    while not st.session_state.audio_queue.empty():
        audio_file = st.session_state.audio_queue.get()
        play_audio(audio_file)

if __name__ == "__main__":
    main()


