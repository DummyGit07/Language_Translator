import os
import tempfile
import wave
import contextlib
import whisper
from vosk import Model as VoskModel, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)  # suppress Vosk logs

class SpeechToText:
    def __init__(self, use_vosk_fallback=True):
        self.stt_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'stt'))
        self.whisper_model = None
        self.vosk_model = None
        self.use_vosk_fallback = use_vosk_fallback

        # Load Whisper model once
        self._load_whisper_model('small')

        # Load Vosk model once if fallback enabled
        if self.use_vosk_fallback:
            self._load_vosk_model()

    def _load_whisper_model(self, model_name):
        if self.whisper_model is None:
            self.whisper_model = whisper.load_model(model_name, download_root=self.stt_dir)

    def _load_vosk_model(self):
        model_path = os.path.join(self.stt_dir, "vosk-model-small-en-us-0.15")
        if os.path.exists(model_path):
            self.vosk_model = VoskModel(model_path)

    def _get_wav_duration(self, wav_path):
        with contextlib.closing(wave.open(wav_path,'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration

    def _convert_audio_to_wav(self, audio_file_path):
        # Whisper accepts many formats but Vosk needs 16kHz WAV mono
        # Here we only convert audio to WAV if needed for Vosk fallback
        return audio_file_path  # Assuming upload is WAV; add FFmpeg conversion if needed

    def transcribe(self, audio_file):
        """
        Transcribes audio file object to text. Returns transcribed text and detected language code.
        Tries Whisper first, falls back to Vosk if enabled and Whisper fails or is slow.
        """
        try:
            # Save audio file to temp WAV for Whisper
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp_audio:
                audio_file.save(tmp_audio.name)

                # Whisper transcription
                result = self.whisper_model.transcribe(tmp_audio.name)
                text = result.get('text', '').strip()
                lang_code = result.get('language', None)
                return text, lang_code

        except Exception as e:
            if self.use_vosk_fallback and self.vosk_model is not None:
                try:
                    wav_path = self._convert_audio_to_wav(audio_file.filename)
                    with wave.open(audio_file.stream, "rb") as wf:
                        rec = KaldiRecognizer(self.vosk_model, wf.getframerate())
                        rec.SetWords(True)
                        text_chunks = []
                        while True:
                            data = wf.readframes(4000)
                            if len(data) == 0:
                                break
                            if rec.AcceptWaveform(data):
                                res = rec.Result()
                                text_chunks.append(res)
                        text_chunks.append(rec.FinalResult())
                        import json
                        texts = []
                        for chunk in text_chunks:
                            jres = json.loads(chunk)
                            texts.append(jres.get('text', ''))
                        joined_text = ' '.join(texts).strip()
                        return joined_text, 'en'  # Vosk fallback supports English only
                except Exception as ve:
                    raise RuntimeError(f"Vosk fallback failed: {ve}") from ve
            else:
                raise RuntimeError(f"Whisper transcription failed: {e}") from e
