from cache_request import cache_request
from selectolax.parser import HTMLParser
from rich import print


def get_request(url):
    return cache_request(url)


def get_parser(url: str) -> HTMLParser:
    resp = get_request(url)
    return HTMLParser(resp.text)


parser = get_parser("https://myanimelist.net/anime/genre/info")

genre_header = parser.css(".normal_header")


GENRE = {}
for genre in genre_header:
    type = genre.text().strip().lower().replace(" ", "_")
    GENRE.setdefault(type, {})
    genres = genre.next.next.css("li")
    for genre in genres:
        strong = genre.css_first("strong")
        genre_name = strong.text()
        genre_info = strong.next.text().strip()[1:].strip()
        GENRE[type][genre_name] = genre_info


print(GENRE)
