# AI Real-time Speech Translator 🌎

A real-time speech translation application built with Streamlit that enables seamless verbal communication between English and Spanish speakers. The application uses state-of-the-art speech recognition, translation, and text-to-speech technologies to facilitate natural conversations across language barriers.

## 🌟 Features

- **Real-time Speech Recognition**: Captures speech input from both English and Spanish speakers
- **Instant Translation**: Translates between English and Spanish in real-time
- **Text-to-Speech Output**: Converts translated text to natural-sounding speech
- **Conversation History**: Maintains a log of all conversations with timestamps
- **User-friendly Interface**: Clean and intuitive design with clear visual feedback
- **Bilingual Support**: Full support for both English and Spanish languages
- **Error Handling**: Robust error handling with clear user feedback
- **Ambient Noise Adjustment**: Automatically adjusts for background noise levels

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Working microphone
- Speakers or headphones
- Stable internet connection

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-speech-translator.git
cd ai-speech-translator
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the Streamlit app:
```bash
streamlit run speech_translator.py
```

2. Open your web browser and navigate to the provided local URL (typically http://localhost:8501)

## 💡 How to Use

1. Select your language (English or Spanish)
2. Click the appropriate "Speak" button for your language
3. Speak clearly into your microphone
4. Wait for the translation process to complete
5. Listen to the translated audio output
6. View the conversation history below the speaker interfaces

## 🛠️ Technical Architecture

The application combines several technologies:
- **Streamlit**: Web application framework
- **Google Speech Recognition**: Speech-to-text conversion
- **Google Translate**: Text translation
- **gTTS (Google Text-to-Speech)**: Text-to-speech conversion
- **PyAudio**: Audio input/output handling
- **Playsound**: Audio playback

## 📋 System Requirements

- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 500MB free space
- **Internet**: Broadband connection (minimum 1Mbps)
- **Audio**: Working microphone and speakers/headphones

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Speech Recognition API
- Google Translate API
- Streamlit Framework
- All contributors and supporters

## 📞 Support

If you encounter any issues or have questions, please:
1. Check the existing issues or create a new one
2. Ensure your microphone and speakers are properly configured
3. Verify your internet connection is stable
4. Check that all dependencies are correctly installed

## 🔮 Future Enhancements

- Support for additional languages
- Offline mode capability
- Custom voice selection
- Speech accent adaptation
- Real-time subtitle display
- Mobile application version
- Audio recording and export features
- Group conversation support

---

Made with ❤️ by Elizabeth Waithera


