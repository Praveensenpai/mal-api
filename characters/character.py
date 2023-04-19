import re
from selectolax.parser import HTMLParser
from typing import List
from sqlmodel import JSON, Column, SQLModel, Session, Field, create_engine, select
from rich import print
from utility.utility import exception_handler

sqlite_url = "sqlite:///characters.db"
engine = create_engine(sqlite_url, echo=False)


class Character(SQLModel, table=True):
    url: str
    mal_id: int = Field(primary_key=True)
    title: str
    kanji_title: str = Field(nullable=True)
    about: str = Field(nullable=True)
    nicknames: List[str] = Field(sa_column=Column("nicknames", JSON), nullable=True)
    favorite: int = Field(nullable=True)
    image: str = Field(nullable=True)
    animeography: List[str] = Field(
        sa_column=Column("animeography", JSON), nullable=True
    )
    mangaography: List[str] = Field(
        sa_column=Column("mangaography", JSON), nullable=True
    )
    voice_actors: List[dict] = Field(
        sa_column=Column("voice_actors", JSON), nullable=False
    )


Character.metadata.create_all(engine)


class CharacterParser:
    def __init__(self, html: str):
        self.html = html
        self.parser = self.get_parser()

    def get_parser(self):
        return HTMLParser(self.html)

    @staticmethod
    def parse_malid(url: str):
        return int(url.split("/")[-2])

    def get_malid(self):
        return self.parse_malid(
            self.parser.css_first("meta[property='og:url']").attributes["content"]
        )

    def get_character_url(self):
        return self.parser.css_first("meta[property='og:url']").attributes["content"]

    def get_title(self):
        return self.parser.css_first("meta[property='og:title']").attributes["content"]

    @exception_handler
    def get_kanji_title(self):
        return self.parser.css_first("h2.normal_header span small").text().strip("()")

    @exception_handler
    def get_about(self):
        td = self.parser.css_first("#content table tbody tr > td:nth-of-type(2)")
        tags = ["div", "br", "table", "h2"]
        td.strip_tags(tags)
        sentences = td.text().split("\n")
        return "\n\n".join(sentences).strip()
        # return "\n\n".join(s for s in sentences if len(s) >= 50).strip()

    @exception_handler([])
    def get_nicknames(self):
        aliases = self.parser.css_first("h1").text().strip()
        aliases = aliases[aliases.find('"') + 1 : aliases.rfind('"')].strip()
        return aliases.split(", ")

    @exception_handler
    def get_member_favorites_count(self):
        pattern = r"Member Favorites: (\d+,?\d+)"
        match = re.search(pattern, self.html)
        return re.search(r"\d+,?\d+", match[0])[0].replace(",", "")

    @exception_handler
    def get_image(self):
        return self.parser.css_first("meta[property='og:image']").attributes["content"]

    @exception_handler([])
    def get_animeography(self):
        anime_links = {
            link
            for link in self.parser.css("td.borderClass tr a")
            if "/anime/" in link.attributes.get("href", "")
        }

        return list({self.parse_malid(link.attributes["href"]) for link in anime_links})

    @exception_handler([])
    def get_mangagraphy(self):
        manga_links = [
            link
            for link in self.parser.css("td.borderClass tr a")
            if "/manga/" in link.attributes.get("href", "")
        ]
        return list({self.parse_malid(link.attributes["href"]) for link in manga_links})

    @exception_handler([])
    def get_voice_actors(self) -> List[dict]:
        return [
            {
                "language": td.css_first("small").text(),
                "mal_id": self.parse_malid(td.css_first("a").attributes["href"]),
            }
            for td in self.parser.css("table > tbody > tr > td:nth-child(2)")
            if "/people/" in td.css_first("a").attributes["href"]
        ]

    @exception_handler
    def get_character(self):
        return Character(
            url=self.get_character_url(),
            about=self.get_about(),
            title=self.get_title(),
            mal_id=self.get_malid(),
            kanji_title=self.get_kanji_title(),
            nicknames=self.get_nicknames(),
            favorite=self.get_member_favorites_count(),
            image=self.get_image(),
            animeography=self.get_animeography(),
            mangaography=self.get_mangagraphy(),
            voice_actors=self.get_voice_actors(),
        )


def insert_character(character: Character):
    with Session(engine) as session:
        session.add(character)
        session.commit()
        print("Added character: ", character.title)


def exist_character(url: str):
    with Session(engine) as session:
        statement = select(Character).where(Character.url == url)
        return bool(session.exec(statement).first())
