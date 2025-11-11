import os
from transformers import MarianMTModel, MarianTokenizer
import whisper
import fasttext
import requests
import subprocess

# Configuration: model paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TRANSLATION_DIR = os.path.join(BASE_DIR, 'models', 'translation')
STT_DIR = os.path.join(BASE_DIR, 'models', 'stt')
TTS_DIR = os.path.join(BASE_DIR, 'models', 'tts')
LID_DIR = os.path.join(BASE_DIR, 'models', 'lid')

os.makedirs(TRANSLATION_DIR, exist_ok=True)
os.makedirs(STT_DIR, exist_ok=True)
os.makedirs(TTS_DIR, exist_ok=True)
os.makedirs(LID_DIR, exist_ok=True)

# MarianMT language pairs for demo (add more ISO codes as needed)
LANG_PAIRS = [
    ('en', 'es'), ('es', 'en'), # Spanish
    ('en', 'de'), ('de', 'en'), # German
    ('en', 'it'), ('it', 'en'), # Italian
    ('en', 'nl'), ('nl', 'en'), # Dutch
    ('en', 'ru'), ('ru', 'en'), # Russian
    ('en', 'zh'), ('zh', 'en'), # Chinese
    ('en', 'ja'), ('ja', 'en'), # Japanese
    ('en', 'ko'), ('ko', 'en'), # Korean
    ('en', 'ar'), ('ar', 'en'), # Arabic
    ('en', 'fr'), ('fr', 'en'), # French
    ('en', 'hi'), ('hi', 'en'),   # Hindi
    ('en', 'ben'), ('ben', 'en'),   # Bengali
    ('en', 'tam'), ('tam', 'en'),   # Tamil
    ('en', 'tl'), ('tl', 'en'),   # Telugu
    ('en', 'mr'), ('mr', 'en'),   # Marathi
    ('en', 'guj'), ('guj', 'en'),   # Gujarati
    ('en', 'pnb'), ('pnb', 'en'),   # Punjabi
    ('en', 'ml'), ('ml', 'en'),   # Malayalam
    ('en', 'ori'), ('ori', 'en'),   # Odia
    ('en', 'asm'), ('asm', 'en'),   # Assamese
]


def download_marianmt_models():
    print("Downloading MarianMT models...")
    for src, tgt in LANG_PAIRS:
        model_name = f'Helsinki-NLP/opus-mt-{src}-{tgt}'
        print(f"Downloading {model_name}")
        try:
            tokenizer = MarianTokenizer.from_pretrained(model_name, cache_dir=TRANSLATION_DIR)
            model = MarianMTModel.from_pretrained(model_name, cache_dir=TRANSLATION_DIR)
        except Exception as e:
            print(f"Warning: Could not download {model_name}. Error: {e}")
            continue


def download_whisper_model():
    print("Downloading Whisper model (small)...")
    model = whisper.load_model("small", download_root=STT_DIR)

def download_vosk_model():
    # Example: Using English small model, add instructions to download more separately as needed
    vosk_model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    dest_path = os.path.join(STT_DIR, "vosk-model-small-en-us-0.15.zip")
    if not os.path.exists(dest_path):
        print("Downloading Vosk model (English small)...")
        r = requests.get(vosk_model_url, stream=True)
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Extract Vosk model manually to:", STT_DIR)
    else:
        print("Vosk model already downloaded.")

def download_coqui_tts_voice():
    # Coqui TTS uses prebuilt voices downloaded on first use.
    # For demo, we can download one from their github repo or use from cache.
    print("Coqui TTS voices will download on first synthesis call.")

def download_fasttext_model():
    lid_path = os.path.join(LID_DIR, 'lid.176.bin')
    if not os.path.exists(lid_path):
        print("Downloading fastText language identification model...")
        url = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
        response = requests.get(url, stream=True)
        with open(lid_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        print("fastText lid.176.bin model already exists.")

if __name__ == "__main__":
    download_marianmt_models()
    download_whisper_model()
    download_vosk_model()
    download_coqui_tts_voice()
    download_fasttext_model()
    print("All models downloaded and cached.")
