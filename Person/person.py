import asyncio
import time
from typing import List, Optional
from datetime import datetime
from models import Person, get_peoplelinks, get_person_by_url, insert_person
import httpx
from itertools import count
from rich import print
from selectolax.parser import HTMLParser
from utility.utility import exception_handler


COUNTER = count()
SLEEP_TIME = 60


class PersonParser:
    def __init__(self, html: str):
        self.parser = HTMLParser(html)
        self.text = self.parser.text()

    def get_person_id(self) -> int:
        return self.get_person_url().split("/")[-2]

    def get_person_url(self) -> str:
        return (
            self.parser.css_first('meta[property="og:url"]')
            .attributes["content"]
            .strip()
        )

    def get_person_name(self) -> str:
        return (
            self.parser.css_first('meta[property="og:title"]')
            .attributes["content"]
            .strip()
        )

    @exception_handler()
    def get_person_image(self) -> str:
        return (
            self.parser.css_first('meta[property="og:image"]')
            .attributes["content"]
            .strip()
        )

    @exception_handler()
    def get_person_given_name(self) -> Optional[str]:
        return (
            self.parser.select("span")
            .text_contains("Given name:")
            .matches[0]
            .next.text()
        )

    @exception_handler()
    def get_person_family_name(self):
        return (
            self.parser.select("span")
            .text_contains("Family name:")
            .matches[0]
            .next.text()
        )

    @exception_handler([])
    def get_person_alterate_names(self) -> List[str]:
        node = (
            self.parser.select("span")
            .text_contains("Alternate names:")
            .matches[0]
            .next.text()
        ).split(",")

        return [name.strip() for name in node]

    @exception_handler([])
    def get_person_website(self) -> Optional[str]:
        return (
            self.parser.select("span")
            .text_contains("Website:")
            .matches[0]
            .next.next.attributes["href"]
        )

    @exception_handler([])
    def get_dob(self) -> Optional[datetime]:
        return (
            self.parser.select("span").text_contains("Birthday:").matches[0].next.text()
        )

    def get_person(self) -> Person:
        return Person(
            mal_id=self.get_person_id(),
            name=self.get_person_name(),
            url=self.get_person_url(),
            given_name=self.get_person_given_name(),
            family_name=self.get_person_family_name(),
            alternate_names=self.get_person_alterate_names(),
            website=self.get_person_website(),
            birthday=self.get_dob(),
            image_url=self.get_person_image(),
        )


def get_people_pages() -> List[str]:
    for people_link in get_peoplelinks():
        yield people_link.url


async def get_request(url: str) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.get(url)


async def process_person(url: str, sem: asyncio.Semaphore) -> None:
    async with sem:
        try:
            print(f"Count = {next(COUNTER)}")
            if get_person_by_url(url):
                print(f"Already processed {url}")
                return
            resp = await get_request(url)
            if resp.status_code != 200:
                print(
                    f"Temporarily banned!\n sleeping for {SLEEP_TIME} seconds...\n\
                     STATUS CODE: {resp.status_code}"
                )
                time.sleep(SLEEP_TIME)
            person_parser = PersonParser(resp.text)
            person = person_parser.get_person()
            insert_person(person)
        except Exception:
            print(f"Error processing person {url}")
