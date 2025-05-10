import logging
import re
import io
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from weather_service import WeatherService
from translation_service import TranslationService
from fun_service import FunService
from cat import get_random_cat

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MultiToolBot:
    def __init__(self):
        self.weather_service = WeatherService("8013b162-6b42-4997-9691-77b7074026e0")
        self.translation_service = TranslationService()
        self.fun_service = FunService()
        self.user_modes = {}  # Словарь для хранения режимов работы пользователей

    # Основные команды (ваш существующий функционал)
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_text = """
🌟 *Добро пожаловать в MultiToolBot!* 🌟

Я многофункциональный бот с новыми возможностями:

🌤 Погода: /map [город]
🌍 Перевод: /pereen [текст], /pereru [текст]
😄 Развлечения: /fact, /cat
🧮 *Новый калькулятор*: /calc или "калькулятор"

Для полного списка команд введите /help
"""
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
🤖 *Доступные команды*:

🧮 *Калькулятор*:
/calc - Открыть калькулятор
(или просто введите математическое выражение)

🌤 *Погода*:
/map [место] - Узнать погоду

🌍 *Переводчик*:
/pereen [текст] - На английский
/pereru [текст] - На русский

😄 *Развлечения*:
/fact - Случайный факт
/cat - Фото котика

🆘 *Помощь*:
/help - Список команд
/start - Перезапустить бота
"""
        await update.message.reply_text(help_text, parse_mode="Markdown")

    # Ваши существующие обработчики (map, pereen, pereru, fact, cat)
    # ... (оставьте их без изменений, как в вашем исходном коде)
    
    # Новый функционал калькулятора
    async def calc_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Активирует режим калькулятора"""
        self.user_modes[update.effective_user.id] = 'calculator'
        await update.message.reply_text(
            "🧮 Режим калькулятора. Введите математическое выражение (например: 2+2*3)\n"
            "Используйте /exit для выхода из режима",
            reply_markup=self._get_calc_keyboard()
        )

    async def handle_calculation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает математические выражения"""
        user_id = update.effective_user.id
        
        # Проверяем, находится ли пользователь в режиме калькулятора
        # или просто ввел математическое выражение
        if (user_id not in self.user_modes or 
            self.user_modes[user_id] != 'calculator') and not self._is_math_expression(update.message.text):
            return
        
        text = update.message.text.strip().lower()
        
        if text in ('exit', '/exit', 'выход'):
            self.user_modes.pop(user_id, None)
            await update.message.reply_text("Выход из режима калькулятора", reply_markup=None)
            return
        
        try:
            # Безопасная проверка выражения
            if not self._is_safe_expression(text):
                await update.message.reply_text("⚠️ Используйте только цифры и операторы (+-*/).")
                return
                
            result = eval(text)  # Важно: в продакшне замените на безопасный парсер!
            await update.message.reply_text(f"✅ Результат: {result}")
        except ZeroDivisionError:
            await update.message.reply_text("❌ Ошибка: деление на ноль!")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")

    # Вспомогательные методы для калькулятора
    def _get_calc_keyboard(self):
        """Создает клавиатуру для калькулятора"""
        buttons = [
            "7", "8", "9", "/",
            "4", "5", "6", "*",
            "1", "2", "3", "-",
            "0", ".", "=", "+",
            "C", "(", ")", "exit"
        ]
        keyboard = []
        for i in range(0, len(buttons), 4):
            keyboard.append(buttons[i:i+4])
        return {'keyboard': keyboard, 'resize_keyboard': True}

    def _is_math_expression(self, text):
        """Проверяет, является ли текст математическим выражением"""
        return bool(re.match(r'^[\d+\-*/().\s=]+$', text.strip()))

    def _is_safe_expression(self, text):
        """Проверка безопасности выражения"""
        return bool(re.fullmatch(r'^[\d+\-*/().\s=]+$', text.strip()))

    def run(self):
        """Запуск бота со всеми обработчиками"""
        application = Application.builder().token("8169674662:AAGKP5lBoeYudEHYW_nWKHW6jlue3xW4xT0").build()

        # Ваши существующие обработчики команд
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("map", self.map_command))
        application.add_handler(CommandHandler("pereen", self.pereen_command))
        application.add_handler(CommandHandler("pereru", self.pereru_command))
        application.add_handler(CommandHandler("fact", self.fact_command))
        application.add_handler(CommandHandler("cat", self.cat_command))
        
        # Новые обработчики для калькулятора
        application.add_handler(CommandHandler("calc", self.calc_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_calculation))

        application.run_polling()

if __name__ == "__main__":
    bot = MultiToolBot()
    bot.run()