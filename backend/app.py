import os
from flask import Flask, request, jsonify, send_file, send_from_directory
from services.translate_service import Translator
from services.stt_service import SpeechToText
from services.tts_service import TextToSpeech
from services.lang_detect import LanguageDetector

# Determine absolute paths for frontend folders relative to backend/app.py
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
template_dir = os.path.join(base_dir, 'frontend', 'templates')
static_dir = os.path.join(base_dir, 'frontend', 'static')

app = Flask(__name__,
            template_folder=template_dir,
            static_folder=static_dir,
            static_url_path='/static')

# Instantiate singleton service objects for caching models
translator = Translator()
stt = SpeechToText()
tts = TextToSpeech()
lang_detector = LanguageDetector()

# Language code-name mapping for UI dropdowns
LANGUAGE_MAP = {
    'en': 'English', 'es': 'Spanish', 'de': 'German', 'it': 'Italian',
    'ru': 'Russian', 'zh': 'Chinese', 'ja': 'Japanese', 'ko': 'Korean',
    'ar': 'Arabic', 'fr': 'French',
    'hi': 'Hindi', 'bn': 'Bengali', 'ta': 'Tamil', 'te': 'Telugu',
    'mr': 'Marathi', 'gu': 'Gujarati', 'pa': 'Punjabi', 'kn': 'Kannada',
    'ml': 'Malayalam', 'or': 'Odia', 'as': 'Assamese'
}

@app.route('/')
def index():
    # Serve the main frontend index.html file as a static file
    return send_from_directory(template_dir, 'index.html')

@app.route('/api/languages', methods=['GET'])
def get_languages():
    return jsonify(LANGUAGE_MAP)

@app.route('/api/translate', methods=['POST'])
def translate_text():
    data = request.json
    text = data.get('text', '')
    source_lang = data.get('source_lang', '')
    target_lang = data.get('target_lang', '')
    if not text or not target_lang:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        translated_text = translator.translate(text, source_lang, target_lang)
        return jsonify({'translated_text': translated_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stt', methods=['POST'])
def speech_to_text():
    if 'audio' not in request.files:
        return jsonify({'error': 'Missing audio file'}), 400
    audio_file = request.files['audio']
    try:
        text, detected_lang = stt.transcribe(audio_file)
        return jsonify({'text': text, 'detected_lang': detected_lang})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text', '')
    lang = data.get('lang', 'en')
    if not text:
        return jsonify({'error': 'Missing text input'}), 400
    try:
        audio_path = tts.synthesize(text, lang)
        return send_file(audio_path, mimetype='audio/wav')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/detect-lang', methods=['POST'])
def detect_language():
    data = request.json
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'Missing text input'}), 400
    try:
        lang_code = lang_detector.detect(text)
        if lang_code is None:
            lang_code = 'und'  # undetermined
        return jsonify({'lang': lang_code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5000)
