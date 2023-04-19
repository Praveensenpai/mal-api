import asyncio
import time
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from models import Person, get_peoplelinks, get_person_by_url, insert_person
import httpx
from itertools import count
from rich import print
from utility.utility import exception_handler


COUNTER = count()
SLEEP_TIME = 60


def datestring_to_datetime(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%B %d, %Y")


class PersonParser:
    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")

    def get_person_id(self) -> int:
        return self.get_person_url().split("/")[-2]

    def get_person_url(self) -> str:
        return self.soup.find("meta", property="og:url")["content"].strip()

    def get_person_name(self) -> str:
        return self.soup.find("meta", property="og:title")["content"].strip()

    @exception_handler
    def get_person_image(self) -> str:
        return self.soup.find("meta", property="og:image")["content"]

    @exception_handler
    def get_person_given_name(self) -> Optional[str]:
        return self.soup.find("span", string="Given name:").nextSibling

    @exception_handler
    def get_person_family_name(self):
        return self.soup.find("span", string="Family name:").nextSibling

    @exception_handler([])
    def get_person_alterate_names(self) -> List[str]:
        node: list[str] = self.soup.find(
            "span", string="Alternate names:"
        ).nextSibling.split(",")
        return [name.strip() for name in node]

    @exception_handler([])
    def get_person_website(self) -> Optional[str]:
        return (
            self.soup.find("span", string="Website:").find_next_sibling("a").get("href")
        )

    @exception_handler([])
    def get_dob(self) -> Optional[datetime]:
        date_str = self.soup.find("span", string="Birthday:").next_sibling.strip(" ")
        return datestring_to_datetime(date_str)

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
