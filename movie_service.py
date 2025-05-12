import requests
from typing import Dict, Optional

class MovieService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"

    def search_movie(self, query: str) -> Optional[Dict]:
        """Поиск информации о фильме через TMDB API"""
        try:
            url = f"{self.base_url}/search/movie?api_key={self.api_key}&query={query}&language=ru"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("results"):
                return None
                
            movie = data["results"][0]
            return {
                'title': movie.get('title', 'Название неизвестно'),
                'year': movie.get('release_date', '')[:4] if movie.get('release_date') else 'год неизвестен',
                'rating': movie.get('vote_average', 0),
                'overview': movie.get('overview', 'Описание отсутствует'),
                'poster': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else None
            }
        except Exception as e:
            print(f"Movie search error: {e}")
            return None