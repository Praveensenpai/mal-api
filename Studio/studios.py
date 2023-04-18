from selectolax.parser import HTMLParser
import httpx


def get_request(url) -> httpx.Response:
    return httpx.get(url)


def get_parser(url: str) -> HTMLParser:
    resp = get_request(url)
    return HTMLParser(resp.text)


def get_studio_pages():
    parser = get_parser("https://myanimelist.net/anime/producer")
    return (
        f'https://myanimelist.net{a.attributes["href"]}'
        for a in parser.css("a.genre-name-link")
        if "/producer/" in a.attributes["href"]
    )
