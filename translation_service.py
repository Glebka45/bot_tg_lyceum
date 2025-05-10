import logging
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        pass

    def translate_text(self, text: str, target_lang: str = 'en') -> str:
        """Перевод текста с помощью Google Translate"""
        try:
            if target_lang == 'en':
                # Определяем, нужно ли переводить с русского на английский
                translator = GoogleTranslator(source='auto', target='en')
                return translator.translate(text)
            else:
                # Переводим с английского на русский
                translator = GoogleTranslator(source='auto', target='ru')
                return translator.translate(text)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return "Ошибка перевода"