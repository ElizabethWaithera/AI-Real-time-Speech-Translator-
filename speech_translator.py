import streamlit as st
from googletrans import Translator
from gtts import gTTS
import time
import tempfile
import os

# Page configuration
st.set_page_config(
    page_title="AI Language Translator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
    <style>
    /* Main Container Styling */
    .main {
        padding: 2rem;
        background-color: #f8f9fa;
    }
    
    /* Header Styling */
    .stApp header {
        background-color: #ffffff;
        border-bottom: 1px solid #eee;
    }
    
    /* Title and Headers */
    h1 {
        color: #1e88e5;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(120deg, #1e88e5 0%, #4a90e2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    h3 {
        color: #2c3e50;
        font-weight: 600 !important;
        margin-top: 1rem !important;
    }
    
    /* Language Selection Box */
    .language-selector {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    
    /* Translation Box */
    .translation-box {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .translation-box:hover {
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* Button Styling */
    .stButton>button {
        width: 100%;
        padding: 0.75rem 1.5rem !important;
        background: linear-gradient(120deg, #1e88e5 0%, #4a90e2 100%);
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
    }
    
    .stButton>button:active {
        transform: translateY(0px);
    }
    
    /* Text Area Styling */
    .stTextArea>div>div {
        border-radius: 8px !important;
        border-color: #e0e0e0 !important;
    }
    
    .stTextArea>div>div:focus {
        border-color: #1e88e5 !important;
        box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.2) !important;
    }
    
    /* History Entry Styling */
    .history-entry {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1e88e5;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .history-entry:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transform: translateX(4px);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Stats Card */
    .stats-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Loading Animation */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .loading {
        animation: pulse 1.5s infinite;
    }
    
    /* Audio Player Styling */
    audio {
        width: 100%;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Selectbox Styling */
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 8px !important;
    }
    
    /* Info Messages */
    .stInfo {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1e88e5;
    }
    </style>
""", unsafe_allow_html=True)

# Language options with flags
LANGUAGES = {
    'en': '🇺🇸 English',
    'es': '🇪🇸 Spanish',
    'fr': '🇫🇷 French',
    'de': '🇩🇪 German',
    'it': '🇮🇹 Italian',
    'pt': '🇵🇹 Portuguese',
    'ru': '🇷🇺 Russian',
    'ja': '🇯🇵 Japanese',
    'ko': '🇰🇷 Korean',
    'zh-cn': '🇨🇳 Chinese (Simplified)',
    'ar': '🇸🇦 Arabic',
    'hi': '🇮🇳 Hindi'
}

def initialize_session_state():
    """Initialize session state variables"""
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'translation_count' not in st.session_state:
        st.session_state.translation_count = 0
    if 'favorite_translations' not in st.session_state:
        st.session_state.favorite_translations = set()

def text_to_speech(text, lang):
    """Convert text to speech and return audio file path"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts = gTTS(text=text, lang=lang.split('-')[0])  # Handle compound language codes
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
        with st.spinner("🔄 Magic translation in progress..."):
            translation = translator.translate(text, src=src_lang.split('-')[0], dest=dest_lang.split('-')[0])
            time.sleep(0.5)  # Add slight delay for better UX
            return translation.text
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return None

def display_stats():
    """Display translation statistics"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="stats-card">
            <h4>Total Translations</h4>
            <h2 style="color: #1e88e5;">{}</h2>
        </div>
        """.format(st.session_state.translation_count), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-card">
            <h4>Favorite Translations</h4>
            <h2 style="color: #1e88e5;">{}</h2>
        </div>
        """.format(len(st.session_state.favorite_translations)), unsafe_allow_html=True)

def main():
    initialize_session_state()
    
    # Title and description
    st.markdown("""
        <h1>🤖 AI Language Translator</h1>
        <p style="text-align: center; font-size: 1.2em; color: #666; margin-bottom: 2rem;">
            Breaking language barriers with artificial intelligence
        </p>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Dashboard")
        display_stats()
        
        st.markdown("---")
        st.markdown("### 🎯 Quick Tips")
        st.info("""
        - Use clear, simple sentences
        - Check the audio output for pronunciation
        - Save important translations as favorites
        - Clear history periodically for better performance
        """)
        
        if st.button("🗑️ Clear History", key="clear_history"):
            st.session_state.history = []
            st.session_state.translation_count = 0
            st.experimental_rerun()
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="language-selector">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="language-selector">', unsafe_allow_html=True)
        st.markdown("### Target Language")
        dest_lang = st.selectbox(
            "Select output language",
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            key='dest_lang'
        )
        
        if st.button("🔮 Translate", key="translate_button"):
            if source_text:
                translated_text = translate_text(source_text, src_lang, dest_lang)
                
                if translated_text:
                    st.markdown("### Translation Result")
                    st.markdown(f"""
                    <div class="translation-box">
                        <div style="font-size: 1.2em; line-height: 1.5;">
                            {translated_text}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Audio output
                    audio_file = text_to_speech(translated_text, dest_lang)
                    if audio_file:
                        st.audio(audio_file)
                        os.unlink(audio_file)
                    
                    # Add to history
                    timestamp = time.strftime("%H:%M:%S")
                    st.session_state.history.append({
                        'timestamp': timestamp,
                        'source_text': source_text,
                        'translated_text': translated_text,
                        'src_lang': LANGUAGES[src_lang],
                        'dest_lang': LANGUAGES[dest_lang],
                        'id': len(st.session_state.history)
                    })
                    st.session_state.translation_count += 1
            else:
                st.warning("Please enter some text to translate! 📝")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Translation History
    if st.session_state.history:
        st.markdown("---")
        st.markdown("### 📜 Translation History")
        
        for item in reversed(st.session_state.history):
            is_favorite = item['id'] in st.session_state.favorite_translations
            
            col_hist, col_fav = st.columns([6, 1])
            
            with col_hist:
                st.markdown(f"""
                <div class="history-entry">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <small style="color: #666;">⏰ {item['timestamp']}</small>
                        <small style="color: #666;">{item['src_lang']} → {item['dest_lang']}</small>
                    </div>
                    <div style="margin: 0.5rem 0;">
                        <strong style="color: #1e88e5;">Original:</strong> 
                        <div style="margin: 0.3rem 0;">{item['source_text']}</div>
                        <strong style="color: #1e88e5;">Translation:</strong> 
                        <div style="margin: 0.3rem 0;">{item['translated_text']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_fav:
                if st.button(
                    "⭐" if is_favorite else "☆",
                    key=f"fav_{item['id']}",
                    help="Add to favorites"
                ):
                    if is_favorite:
                        st.session_state.favorite_translations.remove(item['id'])
                    else:
                        st.session_state.favorite_translations.add(item['id'])
                    
    else:
        st.info("👋 Welcome! Start translating to see your history here.")

if __name__ == "__main__":
    main()

