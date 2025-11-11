import os
from transformers import MarianMTModel, MarianTokenizer


class Translator:
    def __init__(self):
        self.model_cache = {}
        self.tokenizer_cache = {}
        self.translation_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'translation'))

        # Supported language pairs for direct translation
        self.lang_pairs = [
            ('en', 'es'), ('es', 'en'),       # Spanish
            ('en', 'de'), ('de', 'en'),       # German
            ('en', 'it'), ('it', 'en'),       # Italian
            ('en', 'nl'), ('nl', 'en'),       # Dutch
            ('en', 'ru'), ('ru', 'en'),       # Russian
            ('en', 'zh'), ('zh', 'en'),       # Chinese
            ('en', 'ja'), ('ja', 'en'),       # Japanese
            ('en', 'ko'), ('ko', 'en'),       # Korean
            ('en', 'ar'), ('ar', 'en'),       # Arabic
            ('en', 'fr'), ('fr', 'en'),       # French
            ('en', 'hi'), ('hi', 'en'),       # Hindi
            ('en', 'ben'), ('ben', 'en'),     # Bengali
            ('en', 'tam'), ('tam', 'en'),     # Tamil
            ('en', 'tl'), ('tl', 'en'),       # Telugu
            ('en', 'mr'), ('mr', 'en'),       # Marathi
            ('en', 'guj'), ('guj', 'en'),     # Gujarati
            ('en', 'pnb'), ('pnb', 'en'),     # Punjabi (Punjabi Shahmukhi)
            ('en', 'ml'), ('ml', 'en'),       # Malayalam
            ('en', 'ori'), ('ori', 'en'),     # Odia
            ('en', 'asm'), ('asm', 'en'),     # Assamese
        ]

        self.pivot_lang = 'en'  # English as pivot language

    def _load_model_tokenizer(self, src, tgt):
        pair_key = f"{src}-{tgt}"
        if pair_key in self.model_cache and pair_key in self.tokenizer_cache:
            return self.model_cache[pair_key], self.tokenizer_cache[pair_key]

        model_name = f"Helsinki-NLP/opus-mt-{src}-{tgt}"
        cache_dir = self.translation_dir

        try:
            tokenizer = MarianTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
            model = MarianMTModel.from_pretrained(model_name, cache_dir=cache_dir)
        except Exception as e:
            raise RuntimeError(f"Model loading failed for {model_name}: {str(e)}")

        self.model_cache[pair_key] = model
        self.tokenizer_cache[pair_key] = tokenizer
        return model, tokenizer

    def _translate_text(self, model, tokenizer, text):
        # Tokenize input text
        batch = tokenizer([text], return_tensors="pt", padding=True)
        # Perform translation
        generated = model.generate(**batch)
        # Decode translated tokens
        translated_text = tokenizer.decode(generated[0], skip_special_tokens=True)
        return translated_text

    def translate(self, text, src_lang, tgt_lang):
        src_lang = src_lang.lower()
        tgt_lang = tgt_lang.lower()

        if not text:
            raise ValueError("Input text is empty.")

        if src_lang == tgt_lang:
            # Same language, no translation needed
            return text

        # Try direct translation
        if (src_lang, tgt_lang) in self.lang_pairs:
            try:
                model, tokenizer = self._load_model_tokenizer(src_lang, tgt_lang)
                return self._translate_text(model, tokenizer, text)
            except Exception as e:
                raise RuntimeError(f"Direct translation failed for {src_lang} to {tgt_lang}: {str(e)}")

        # Try pivot translation via English
        if src_lang != self.pivot_lang and tgt_lang != self.pivot_lang:
            if (src_lang, self.pivot_lang) in self.lang_pairs and (self.pivot_lang, tgt_lang) in self.lang_pairs:
                try:
                    # Source --> English
                    model1, tokenizer1 = self._load_model_tokenizer(src_lang, self.pivot_lang)
                    intermediate = self._translate_text(model1, tokenizer1, text)

                    # English --> Target
                    model2, tokenizer2 = self._load_model_tokenizer(self.pivot_lang, tgt_lang)
                    return self._translate_text(model2, tokenizer2, intermediate)
                except Exception as e:
                    raise RuntimeError(f"Pivot translation failed for {src_lang} to {tgt_lang} via English: {str(e)}")

        raise ValueError(f"No suitable translation model found for {src_lang} to {tgt_lang}")
