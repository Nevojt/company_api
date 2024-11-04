import requests


async def fetch_image_url():
    url = "https://random.imagecdn.app/v1/image?width=200&height=300&category=photos&format=json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        image_url = data['url']
        return image_url
    else:
        return "Error fetching image"
