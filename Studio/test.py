import asyncio
import httpx
from studios import get_studio_pages
from studio import StudioParser
from models import get_studio, insert_studio
from rich import print


async def get_request(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text


async def push_studio(url: str):
    print(url)
    if get_studio(url):
        print(f"Studio already exists, URL={url}")
        return
    html = await get_request(url)
    studio_parser = StudioParser(html)
    studio = studio_parser.get_studio()
    insert_studio(studio)


async def push_studios():
    tasks = [asyncio.create_task(push_studio(page)) for page in get_studio_pages()]
    await asyncio.gather(*tasks)


asyncio.run(push_studios())
# print(get_studio(1185))
