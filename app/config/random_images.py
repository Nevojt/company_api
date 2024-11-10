import requests
from _log_config.log_config import get_logger

image_logger = get_logger('image_fetch', 'image_fetch.log')

async def fetch_image_url():
    try:
        url = "https://random.imagecdn.app/v1/image?width=200&height=300&category=photos&format=json"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            image_url = data['url']
            return image_url
        else:
            return "Error fetching image"
    except Exception as e:

        image_logger.error(f"Error fetching image: {e}")
        return "Error fetching image"
