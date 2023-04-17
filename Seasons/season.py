import itertools
from cache_request import cache_request
from selectolax.parser import HTMLParser
import models


def get_request(url):
    return cache_request(url)


def get_parser(url: str) -> HTMLParser:
    resp = get_request(url)
    return HTMLParser(resp.text)


class SeasonParser:
    def __init__(self, html: str):
        self.parser = HTMLParser(html)

    def get_a_s(self):
        return self.parser.css(".anime-seasonal-byseason > tbody:nth-child(1) > tr a")

    def get_seasons(self) -> list[models.Season]:
        season_names = []
        season_years = []
        for a in self.get_a_s():
            link = a.attributes["href"]
            if "/season/" in link:
                splitted_a = link.split("/")
                season_years.append(splitted_a[-2])
                season_names.append(splitted_a[-1])
        season_names = list(set(season_names))
        season_years = list(set(season_years))

        seasons = []
        for season_name, season_year in itertools.product(season_names, season_years):
            season = models.Season(
                name=season_name,
                year=season_year,
                url=f"https://myanimelist.net/anime/season/{season_year}/{season_name}",
            )
            seasons.append(season)
        return seasons


def push_seasons() -> str:
    html = get_request("https://myanimelist.net/anime/season/archive").text
    seasons = SeasonParser(html).get_seasons()
    models.insert_seasons(seasons)


def get_season_urls():
    for season in models.get_seasons():
        yield season.url


# if __name__ == "__main__":
#     print(get_season_urls())
