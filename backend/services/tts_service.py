import os
import tempfile
from TTS.api import TTS
import pyttsx3

class TextToSpeech:
    def __init__(self):
        self.tts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'tts'))
        self.coqui_tts = None
        self.pyttsx3_engine = pyttsx3.init()
        self.voice_map = {
            'en': 'tts_models/en/ljspeech/tacotron2-DDC',
            # Additional voices can be added here for other languages
        }
        self.default_lang = 'en'

    def _load_coqui_tts(self, lang_code):
        voice_name = self.voice_map.get(lang_code, self.voice_map[self.default_lang])
        if self.coqui_tts is None or self.coqui_tts.tts_model_name != voice_name:
            # Load or switch Coqui TTS model
            self.coqui_tts = TTS(voice_name, progress_bar=False, gpu=False)

    def synthesize(self, text, lang_code='en'):
        # Use Coqui TTS primarily
        try:
            self._load_coqui_tts(lang_code)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
                wav_path = wav_file.name
            self.coqui_tts.tts_to_file(text=text, file_path=wav_path)
            return wav_path
        except Exception as e:
            # On failure, fallback to pyttsx3 synthesis
            print(f"Coqui TTS synthesis failed: {e}. Falling back to pyttsx3.")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
                wav_path = wav_file.name
            self.pyttsx3_engine.save_to_file(text, wav_path)
            self.pyttsx3_engine.runAndWait()
            return wav_path

    def available_voices(self):
        # Returns available Coqui voices (initially only English configured)
        return list(self.voice_map.keys())
