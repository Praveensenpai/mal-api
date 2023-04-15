import re
from selectolax.parser import HTMLParser
from models import Genre, GenreType


class AnimeGenreParser:
    def __init__(self, html: str, genre_type: GenreType):
        self.parser = HTMLParser(html)
        self.type = genre_type

    def get_mal_id(self) -> int:
        try:
            url = self.get_url()
            return int(url.split("/")[-2])
        except (ValueError, IndexError):
            return None

    def get_url(self) -> str:
        try:
            return self.parser.css_first('meta[property="og:url"]').attributes[
                "content"
            ]
        except ValueError:
            return None

    def get_name(self) -> str:
        try:
            return self.get_url().split("/")[-1].replace("_", " ")
        except (AttributeError, IndexError):
            return None

    def get_description(self) -> str:
        try:
            return self.parser.css_first("div.mt8:nth-child(4)").text().strip()
        except AttributeError:
            return None

    def get_count(self) -> int:
        try:
            text = self.parser.css_first("span.di-ib.mt4 > span").text()
            return int("".join(re.findall(r"\d+", text)))
        except (AttributeError, TypeError, IndexError):
            return None

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


# resp = cache_request("https://myanimelist.net/anime/genre/1/Action")
# parser = AnimeGenreParser(resp.text)
