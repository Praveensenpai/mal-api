import asyncio
import time
from selectolax.parser import HTMLParser
import httpx
from rich import print
from models import insert_people_links


BASE_URL = "https://myanimelist.net/people.php?limit="
MAX_PAGES = 25_000
PER_PAGE = 50
REQUEST_PER = 10
SLEEP_TIME = 60


async def get_people_links(limit, semaphore):
    async with semaphore:
        try:
            async with httpx.AsyncClient() as client:
                print(f"LIMIT = {limit}")
                resp = await client.get(f"{BASE_URL}{limit}")
                if resp.status_code != 200:
                    print(
                        f"Temporarily banned!\n sleeping for {SLEEP_TIME} seconds...\n STATUS CODE: {resp.status_code}"
                    )
                    time.sleep(SLEEP_TIME)
                parser = HTMLParser(resp.text)
                return [a.attributes["href"] for a in parser.css(".people > a")]
        except Exception as e:
            print(e)
            return []


async def push_people_links() -> None:
    semaphore = asyncio.Semaphore(REQUEST_PER)
    tasks = [
        get_people_links(limit, semaphore) for limit in range(0, MAX_PAGES, PER_PAGE)
    ]
    people_links = []
    for people_list in await asyncio.gather(*tasks):
        people_links.extend(people_list)
    people_links = list(set(people_links))
    insert_people_links(people_links)
