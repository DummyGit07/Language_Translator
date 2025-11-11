import os
import fasttext

class LanguageDetector:
    def __init__(self, threshold=0.7):
        self.lid_model_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'lid', 'lid.176.bin')
        )
        self.model = fasttext.load_model(self.lid_model_path)
        self.confidence_threshold = threshold

    def detect(self, text):
        """
        Detect language code for input text.
        Returns ISO 639-1 language code string or None if confidence below threshold.
        """
        if not text or text.strip() == '':
            return None

        predictions = self.model.predict(text.replace('\n', ' '), k=1)  # top 1 prediction
        label, confidence = predictions[0][0], predictions[1][0]  # label = '__label__en'

        # Extract code from label string
        lang_code = label.replace('__label__', '')

        if confidence < self.confidence_threshold:
            return None
        return lang_code
