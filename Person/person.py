import asyncio
import time
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from models import Person, get_peoplelinks, get_person_by_url, insert_person
import httpx
from itertools import count
from rich import print

COUNTER = count()
SLEEP_TIME = 60


def datestring_to_datetime(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%B %d, %Y")


class PersonParser:
    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")

    def getPersonId(self) -> int:
        return self.getPersonURL().split("/")[-2]

    def getPersonURL(self) -> str:
        return self.soup.find("meta", property="og:url")["content"].strip()

    def getPersonName(self) -> str:
        return self.soup.find("meta", property="og:title")["content"].strip()

    def getPersonImageUrl(self) -> str:
        try:
            return self.soup.find("meta", property="og:image")["content"]
        except Exception:
            return ""

    def getPersonGivenName(self) -> Optional[str]:
        try:
            return self.soup.find("span", string="Given name:").nextSibling
        except Exception:
            return ""

    def getPersonFamilyName(self):
        try:
            return self.soup.find("span", string="Family name:").nextSibling
        except Exception:
            return ""

    def getPersonAlternateNames(self) -> List[str]:
        try:
            node: list[str] = self.soup.find(
                "span", string="Alternate names:"
            ).nextSibling.split(",")
            return [name.strip() for name in node]
        except Exception:
            return []

    def getPersonWebsite(self) -> Optional[str]:
        try:
            return (
                self.soup.find("span", string="Website:")
                .find_next_sibling("a")
                .get("href")
            )
        except Exception:
            return []

    def getPersonBirthday(self) -> Optional[datetime]:
        try:
            date_str = self.soup.find("span", string="Birthday:").next_sibling.strip(
                " "
            )
            return datestring_to_datetime(date_str)
        except Exception:
            return []

    def get_person(self) -> Person:
        return Person(
            mal_id=self.getPersonId(),
            name=self.getPersonName(),
            url=self.getPersonURL(),
            given_name=self.getPersonGivenName(),
            family_name=self.getPersonFamilyName(),
            alternate_names=self.getPersonAlternateNames(),
            website=self.getPersonWebsite(),
            birthday=self.getPersonBirthday(),
            image_url=self.getPersonImageUrl(),
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
