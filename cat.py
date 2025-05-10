import requests

def get_random_cat():
    """Получает случайное фото кота с cataas.com и возвращает его в виде bytes"""
    url = 'https://cataas.com/cat'
    response = requests.get(url, allow_redirects=True)
    return response.content