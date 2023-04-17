from itertools import count
import time
import xmltodict
from character import insert_character, CharacterParser, exist_character
import httpx
from rich import print

counter = count(1)
exist_counter = count(1)
REQUEST_LIMIT = 10
TIMEOUT = 60

HEADERS = {
    "authority": "myanimelist.net",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en",
    "cache-control": "max-age=0",
    "dnt": "1",
    "referer": "https://myanimelist.net/",
    "sec-ch-ua": "^^Chromium^^;v=^^112^^, ^^Google",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "^^Windows^^",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}


async def get_request(url: str, *args, **kwargs):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, *args, **kwargs)
            print(next(counter), url)
            response.raise_for_status()
            return response
        except (httpx.RequestError, httpx.HTTPStatusError):
            print(f"Temporary banned! timeout {TIMEOUT} seconds")
            time.sleep(TIMEOUT)  # block the async
            raise Exception("4xx Error")


async def get_characters_pages():
    character_url1 = "https://myanimelist.net/sitemap/character-000.xml"
    resp = await get_request(character_url1, headers=HEADERS)
    doc = xmltodict.parse(resp.text)
    urls = list({key["loc"] for key in doc["urlset"]["url"]})
    print(f"TOTAL URLS: {len(urls)}")
    for i in range(0, len(urls), REQUEST_LIMIT):
        yield urls[i : i + REQUEST_LIMIT]


async def process_character(url: str):
    try:
        if exist_character(url):
            print("Exist Count:", next(exist_counter), url)
            return
        resp = await get_request(url, headers=HEADERS)
        character_parser = CharacterParser(resp.text)
        character = character_parser.get_character()
        insert_character(character)
    except Exception as e:
        print("Failed", url)
        print(e)
