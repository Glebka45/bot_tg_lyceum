from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes
from weather_service import WeatherService
from translation_service import TranslationService
from fun_service import FunService
from cat import get_random_cat
import io
import logging

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ключи API
YANDEX_GEOCODER_API_KEY = "8013b162-6b42-4997-9691-77b7074026e0"
TELEGRAM_BOT_TOKEN = "8169674662:AAGKP5lBoeYudEHYW_nWKHW6jlue3xW4xT0"


class WeatherBot:
    def __init__(self):
        self.weather_service = WeatherService(YANDEX_GEOCODER_API_KEY)
        self.translation_service = TranslationService()
        self.fun_service = FunService()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start - приветствие пользователя"""
        welcome_text = """
🌟 *Добро пожаловать в WeatherBot!* 🌟

Я многофункциональный бот, который может:
🌤 Показывать погоду в любом месте
🌍 Переводить текст между русским и английским
😄 Развлекать интересными фактами
🐈 Присылать милых котиков

Для начала работы используйте команды:
/map [город] - узнать погоду
/pereen [текст] - перевести на английский
/pereru [текст] - перевести на русский
/fact - случайный факт
/cat - фото котика

📌 Для полного списка команд введите /help
"""
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help - показывает список всех команд"""
        help_text = """
🤖 *Доступные команды бота*:

🌤 *Погода*:
/map [место] - Узнать погоду в указанном месте (например: /map Москва)

🌍 *Переводчик*:
/pereen [текст] - Перевести текст на английский
/pereru [текст] - Перевести текст на русский

😄 *Развлечения*:
/fact - Получить случайный интересный факт
/cat - Получить случайное фото котика

🆘 *Помощь*:
/help - Показать это сообщение с описанием команд
/start - Начать работу с ботом
"""
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def map_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /map с параметром"""
        if not context.args:
            await update.message.reply_text("Пожалуйста, укажите место после команды, например: /map Москва")
            return

        location = ' '.join(context.args)
        await self.process_location(update, location)

    async def pereen_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /pereen для перевода текста на английский"""
        if not context.args:
            await update.message.reply_text(
                "Пожалуйста, укажите текст для перевода после команды, например: /pereen привет")
            return

        text = ' '.join(context.args)
        translated = self.translation_service.translate_text(text, target_lang='en')
        await update.message.reply_text(f"Перевод: {translated}")

    async def pereru_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /pereru для перевода текста на русский"""
        if not context.args:
            await update.message.reply_text(
                "Пожалуйста, укажите текст для перевода после команды, например: /pereru hello")
            return

        text = ' '.join(context.args)
        translated = self.translation_service.translate_text(text, target_lang='ru')
        await update.message.reply_text(f"Перевод: {translated}")

    async def fact_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /fact для получения случайного факта"""
        fact = self.fun_service.get_random_fact()
        await update.message.reply_text(f"Интересный факт: {fact}")

    async def cat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /cat для отправки случайного котика"""
        try:
            cat_image = get_random_cat()
            photo_stream = io.BytesIO(cat_image)
            photo_stream.name = 'cat.jpg'
            await update.message.reply_photo(photo=InputFile(photo_stream))
        except Exception as e:
            logger.error(f"Error sending cat: {e}")
            await update.message.reply_text("Не удалось загрузить котика 😿 Попробуйте позже")

    async def process_location(self, update: Update, location: str):
        """Основная логика обработки локации"""
        try:
            latitude, longitude = await self.weather_service.get_coordinates(location)
            if not latitude or not longitude:
                await update.message.reply_text("Не удалось определить координаты для указанного места.")
                return

            weather_data = await self.weather_service.get_weather(latitude, longitude)
            message = self.weather_service.format_weather_message(weather_data)
            await update.message.reply_text(message)

        except Exception as e:
            logger.error(f"Error processing location: {e}")
            await update.message.reply_text("Произошла ошибка при обработке запроса. Попробуйте другой адрес.")

    def run(self):
        """Запуск бота"""
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        # Регистрируем все обработчики команд
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("map", self.map_command))
        application.add_handler(CommandHandler("pereen", self.pereen_command))  # Изменено с pere_en
        application.add_handler(CommandHandler("pereru", self.pereru_command))  # Изменено с pere_ru
        application.add_handler(CommandHandler("fact", self.fact_command))
        application.add_handler(CommandHandler("cat", self.cat_command))

        application.run_polling()


if __name__ == "__main__":
    bot = WeatherBot()
    bot.run()