from telegram import Update, InputFile
import pytz
from telegram.ext import Defaults
from telegram.ext import Application, CommandHandler, ContextTypes
from weather_service import WeatherService
from translation_service import TranslationService
from fun_service import FunService
from calculator_service import CalculatorService
from movie_service import MovieService
from cat import get_random_cat
import io
import logging
import requests

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ключи API
YANDEX_GEOCODER_API_KEY = "8013b162-6b42-4997-9691-77b7074026e0"
TELEGRAM_BOT_TOKEN = "7920203153:AAHyEVeHPWU-vwoYviguKUk7IWJdsNdQSik"
TMDB_API_KEY = 'dd60521'
OMDB_API_KEY = "dd60521"


class WeatherBot:
    def __init__(self):
        self.weather_service = WeatherService(YANDEX_GEOCODER_API_KEY)
        self.translation_service = TranslationService()
        self.fun_service = FunService()
        self.calculator = CalculatorService()
        self.movie_service = MovieService(TMDB_API_KEY)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start - приветствие пользователя"""
        welcome_text = """
🌟 *Добро пожаловать в WeatherBot!* 🌟

Я многофункциональный бот, который может:
🌤 Показывать погоду в любом месте
🌍 Переводить текст между русским и английским
🎬 Искать информацию о фильмах
🧮 Выполнять математические расчеты
😄 Развлекать интересными фактами
🐈 Присылать милых котиков

Для начала работы используйте команды:
/map [город] - узнать погоду
/pereen [текст] - перевести на английский
/pereru [текст] - перевести на русский
/movie [название] - найти информацию о фильме
/calc [выражение] - вычислить выражение
/fact - случайный факт
/cat - фото котика

📌 Для полного списка команд введите /help
"""
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help - показывает список всех команд"""
        help_text = """
🤖 *Доступные команды бота*:

🧮 *Калькулятор*:
/calc [выражение] - Вычислить математическое выражение

🎬 *Фильмы*:
/movie [название] - Найти информацию о фильме (например: /movie The Matrix)

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

    async def calc_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /calc"""
        if not context.args:
            await update.message.reply_text("Введите выражение для расчета, например: /calc 2+2*3")
            return

        expression = ' '.join(context.args)
        result = self.calculator.calculate(expression)
        await update.message.reply_text(result)

    async def movie_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /movie - поиск информации о фильме (как в первом боте)"""
        if not context.args:
            await update.message.reply_text("Укажите название фильма, например: /movie Матрица")
            return

        movie_title = ' '.join(context.args)
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie_title}"

        try:
            response = requests.get(url)
            data = response.json()

            if data.get("Response") == "True":
                # Формируем информацию о фильме
                info = (
                    f"🎥 *{data.get('Title', 'Нет данных')}* ({data.get('Year', 'Нет данных')})\n"
                    f"⭐ *IMDb:* {data.get('imdbRating', 'Нет данных')}\n"
                    f"🎭 *Жанр:* {data.get('Genre', 'Нет данных')}\n"
                    f"📅 *Дата выхода:* {data.get('Released', 'Нет данных')}\n"
                    f"📝 *Описание:* {data.get('Plot', 'Нет данных')}"
                )

                # Отправляем постер
                if data.get("Poster") and data["Poster"] != "N/A":
                    await update.message.reply_photo(
                        photo=data["Poster"],
                        caption=info,
                        parse_mode="Markdown"
                    )
                else:
                    await update.message.reply_text(info, parse_mode="Markdown")
            else:
                await update.message.reply_text("Фильм не найден. Попробуйте другое название.")

        except Exception as e:
            await update.message.reply_text("⚠️ Произошла ошибка при поиске. Попробуйте позже.")
            logger.error(f"Ошибка при поиске фильма: {e}")

    def run(self):
        """Запуск бота"""
        # Указываем часовой пояс явно
        defaults = Defaults(tzinfo=pytz.timezone('Europe/Moscow'))

        application = (
            Application.builder()
            .token(TELEGRAM_BOT_TOKEN)
            .defaults(defaults)
            .build()
        )

        # Регистрируем обработчики команд
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("map", self.map_command))
        application.add_handler(CommandHandler("pereen", self.pereen_command))
        application.add_handler(CommandHandler("pereru", self.pereru_command))
        application.add_handler(CommandHandler("fact", self.fact_command))
        application.add_handler(CommandHandler("cat", self.cat_command))
        application.add_handler(CommandHandler("calc", self.calc_command))
        application.add_handler(CommandHandler("movie", self.movie_command))

        application.run_polling()


if __name__ == "__main__":
    bot = WeatherBot()
    bot.run()