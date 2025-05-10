import logging
import aiohttp

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self, yandex_geocoder_api_key: str):
        self.yandex_geocoder_api_key = yandex_geocoder_api_key

    async def get_weather(self, latitude: str, longitude: str) -> dict:
        """Получение данных о погоде через Open-Meteo API"""
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return None

    async def get_coordinates(self, location: str) -> tuple:
        """Получение координат через Yandex Geocoder API"""
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": self.yandex_geocoder_api_key,
            "geocode": location,
            "format": "json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

                    toponym = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                    longitude, latitude = toponym["Point"]["pos"].split()
                    return latitude, longitude
        except Exception as e:
            logger.error(f"Geocoder API error: {e}")
            return None, None

    def format_weather_message(self, weather_data: dict) -> str:
        """Форматирование сообщения о погоде"""
        if not weather_data:
            return "Не удалось получить данные о погоде."

        current = weather_data.get("current_weather", {})
        temperature = current.get("temperature", "N/A")
        windspeed = current.get("windspeed", "N/A")
        weathercode = current.get("weathercode", "N/A")

        return (
            "🌤 Текущая погода:\n"
            f"🌡 Температура: {temperature}°C\n"
            f"🌬 Скорость ветра: {windspeed} км/ч\n"
            f"☀ Код погоды (WMO): {weathercode}"
        )