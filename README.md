# Offline Multilingual Translator

## Overview
This project is an offline multilingual translation application with features including speech-to-text, text-to-speech, language detection, and text translation, primarily targeting Indic and popular international languages. It operates fully offline with locally cached NLP models to ensure fast, privacy-preserving translations without internet dependence.

---

## File Structure

backend/
app.py # Flask backend server with API routes
services/
translate_service.py # Translation logic using MarianMT models
stt_service.py # Speech-to-text service with Whisper/Vosk
tts_service.py # Text-to-speech service with Coqui/pyttsx3
lang_detect.py # Language detection using fastText

models/
translation/ # Downloaded MarianMT translation models
stt/ # Whisper/Vosk speech-to-text models
tts/ # Coqui TTS voices
lid/ # fastText language ID model

frontend/
templates/
index.html # Main frontend HTML page
static/
css/
styles.css # Frontend styles
js/
main.js # Frontend JavaScript for UI interactions

scripts/
download_models.py # Script to download models offline

requirements.txt # Python dependencies file
README.md # Project overview and setup instructions
.env.example # Sample environment variables

---

## Setup and Running Instructions

1. **Create a Python virtual environment and activate it**

python -m venv venv

Windows PowerShell
.\venv\Scripts\Activate.ps1

macOS/Linux
source venv/bin/activate

2. **Install required Python packages**

pip install -r requirements.txt


3. **Download all required ML models**

From the project root, run:

python scripts/download_models.py


This will download and cache MarianMT, Whisper, Vosk, Coqui, and fastText models into the `models/` folder.

4. **Start the Flask backend server**

python backend/app.py


This starts the server on [http://localhost:5000](http://localhost:5000).

5. **Access the frontend**

Open your web browser and visit:

http://localhost:5000


You can input texts, select languages, perform translations, and use speech features.

---

## Notes

- Make sure models download completes successfully for all your target languages.
- Frontend language selectors exclude languages whose models are unavailable.
- The backend uses English as a pivot language for unsupported direct translations.
- Model files can be large, so sufficient disk space is needed.

---

## Tech Stack

- Python, Flask
- Hugging Face Transformers (MarianMT models)
- OpenAI Whisper, Vosk (Speech-to-text)
- Coqui TTS, pyttsx3 (Text-to-speech)
- fastText Language Detection
- HTML, CSS, JavaScript (Frontend)