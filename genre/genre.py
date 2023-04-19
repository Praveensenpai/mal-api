import re
from selectolax.parser import HTMLParser
from models import Genre, GenreType
from utility.utility import exception_handler


class AnimeGenreParser:
    def __init__(self, html: str, genre_type: GenreType):
        self.parser = HTMLParser(html)
        self.type = genre_type

    def get_mal_id(self) -> int:
        url = self.get_url()
        return int(url.split("/")[-2])

    def get_url(self) -> str:
        return self.parser.css_first('meta[property="og:url"]').attributes["content"]

    def get_name(self) -> str:
        return self.get_url().split("/")[-1].replace("_", " ")

    @exception_handler()
    def get_description(self) -> str:
        return self.parser.css_first("div.mt8:nth-child(4)").text().strip()

    @exception_handler()
    def get_count(self) -> int:
        text = self.parser.css_first("span.di-ib.mt4 > span").text()
        return int("".join(re.findall(r"\d+", text)))

    @exception_handler()
    def get_genre(self) -> list[Genre]:
        mal_id = self.get_mal_id()
        if mal_id is None:
            return []

        return Genre(
            mal_id=mal_id,
            url=self.get_url() or "",
            name=self.get_name() or "",
            description=self.get_description() or "",
            count=self.get_count() or 0,
            type=self.type,
        )
