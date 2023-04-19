from typing import List
from selectolax.parser import HTMLParser

from models import BasicGenre, GenreType


ANIME_GENRES_URL = "https://myanimelist.net/anime.php"


class AnimeGenreListParser:
    def __init__(self, html: str):
        self.parser = HTMLParser(html, "html.parser")

    def get_genres(self) -> List[BasicGenre]:
        return self.parse_genre_links(
            GenreType.GENRE,
            self.parser.css(".genre-link:nth-of-type(2) .genre-name-link"),
        )

    def get_explicit_genres(self) -> List[BasicGenre]:
        return self.parse_genre_links(
            GenreType.EXPLICIT,
            self.parser.css(".genre-link:nth-of-type(4) .genre-name-link"),
        )

    def get_themes(self) -> List[BasicGenre]:
        return self.parse_genre_links(
            GenreType.THEME,
            self.parser.css(".genre-link:nth-of-type(6) .genre-name-link"),
        )

    def get_demographics(self) -> List[BasicGenre]:
        return self.parse_genre_links(
            GenreType.DEMOGRAPHIC,
            self.parser.css(".genre-link:nth-of-type(8) .genre-name-link"),
        )

    def parse_genre_links(
        self, genre_type: GenreType, genre_links: List[HTMLParser]
    ) -> List[BasicGenre]:
        base_genres = []
        for link in genre_links:
            url = link.attributes["href"]
            url_parts = url.split("/")
            base_genres.append(
                BasicGenre(
                    name=url_parts[-1].replace("_", " "),
                    mal_id=int(url_parts[-2]),
                    url=url,
                    type=genre_type,
                )
            )
        return base_genres


# resp = cache_request(ANIME_GENRES_URL)
# parser = AnimeGenreListParser(resp.text)

# genres = parser.get_genres()
# explicit_genres = parser.get_explicit_genres()
# themes = parser.get_themes()
# demographics = parser.get_demographics()

# print("Genres:", genres)
# print("Explicit genres:", explicit_genres)
# print("Themes:", themes)
# print("Demographics:", demographics)
