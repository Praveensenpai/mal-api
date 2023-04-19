import asyncio
import httpx
from rich import print
from genre import AnimeGenreParser
from models import fetch_basic_genre_all, genre_insert, basic_genre_insert
from genres import ANIME_GENRES_URL, AnimeGenreListParser

BASE_URL = "https://myanimelist.net"


async def fill_basic_genres():
    async with httpx.AsyncClient() as client:
        resp = await client.get(ANIME_GENRES_URL)
    parser = AnimeGenreListParser(resp.text)
    genres = parser.get_genres()
    for genre in genres:
        basic_genre_insert(genre)

    explicit_genres = parser.get_explicit_genres()
    for explicit_genre in explicit_genres:
        basic_genre_insert(explicit_genre)

    themes = parser.get_themes()
    for theme in themes:
        basic_genre_insert(theme)

    demographics = parser.get_demographics()
    for demographic in demographics:
        basic_genre_insert(demographic)

    print("Inserted basic genres")


async def fill_genres():
    genres: list = fetch_basic_genre_all()
    async with httpx.AsyncClient() as client:
        tasks = []
        for genre in genres:
            url = f"{BASE_URL}{genre.url}"
            tasks.append(asyncio.create_task(fetch_genre(client, url, genre.type)))
        await asyncio.gather(*tasks)


async def fetch_genre(client: httpx.AsyncClient, url, genre_type):
    resp = await client.get(url)
    anime_genre_parser = AnimeGenreParser(resp.text, genre_type)
    anime_genre = anime_genre_parser.get_genre()
    genre_insert(anime_genre)


async def main():
    await fill_basic_genres()
    await fill_genres()


if __name__ == "__main__":
    asyncio.run(main())
