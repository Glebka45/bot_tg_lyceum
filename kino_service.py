import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class KinoService:
    async def search_movie(message: types.Message):
        movie_title = message.text
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie_title}"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if data.get("Response") == "True":
                # Формируем информацию о фильме
                info = (
                    f"🎥 <b>{data.get('Title', 'Нет данных')}</b> ({data.get('Year', 'Нет данных')})\n"
                    f"⭐ <b>IMDb:</b> {data.get('imdbRating', 'Нет данных')}\n"
                    f"🎭 <b>Жанр:</b> {data.get('Genre', 'Нет данных')}\n"
                    f"📅 <b>Дата выхода:</b> {data.get('Released', 'Нет данных')}\n"
                    f"📝 <b>Описание:</b> {data.get('Plot', 'Нет данных')}"
                )
                
                # Отправляем постер (если есть)
                if data.get("Poster") and data["Poster"] != "N/A":
                    await message.answer_photo(
                        photo=data["Poster"],
                        caption=info,
                        parse_mode="HTML"
                    )
                else:
                    await message.answer(info, parse_mode="HTML")
            else:
                await message.answer("Фильм не найден. Попробуйте другое название.")
                
        except Exception as e:
            await message.answer("⚠️ Произошла ошибка при поиске. Попробуйте позже.")
            print(f"Ошибка: {e}")

