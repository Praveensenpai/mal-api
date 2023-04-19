import re
from cache_request import cache_request
from selectolax.parser import HTMLParser
from models import Studio
from utility.utility import exception_handler


def get_request(url):
    return cache_request(url)


class StudioParser:
    def __init__(self, html):
        self.parser: HTMLParser = HTMLParser(html)
        self.text: str = self.parser.text()

    def get_url(self):
        return self.parser.css_first('meta[property="og:url"]').attributes["content"]

    def get_title(self):
        return self.get_url().split("/")[-1].replace("_", " ")

    def get_malid(self):
        return int(self.get_url().split("/")[-2])

    @exception_handler([])
    def get_alternate_titles(self):
        english_titles = [
            h1.text().strip()
            for h1 in self.parser.css("#contentWrapper > div:first-child > h1")
        ]
        japanese_titles = (
            re.search(r"Japanese:.*", self.text)[0].replace("Japanese: ", "").strip()
        )
        return [*english_titles, japanese_titles]

    @exception_handler
    def get_established(self):
        return (
            re.search(r"Established:.*", self.text)[0]
            .replace("Established:", "")
            .strip()
        )

    @exception_handler
    def get_favorites(self):
        return (
            re.search(r"Member Favorites: .*", self.text)[0]
            .replace("Member Favorites: ", "")
            .strip()
        ).replace(",", "")

    @exception_handler
    def get_animecount(self):
        li_text = self.parser.css_first("#content ul.btn-type li").text()
        return re.search(r"\d+", li_text)[0]

    @exception_handler([])
    def get_external_links(self):
        return [
            a.attributes["href"]
            for a in self.parser.css(
                "#content > div:nth-of-type(1) > div.user-profile-sns > span a"
            )
        ]

    @exception_handler
    def get_image(self):
        return self.parser.css_first('meta[property="og:image"]').attributes["content"]

    @exception_handler
    def get_about(self):
        return self.parser.css_first(
            "#content > div:nth-of-type(1) div.spaceit_pad > span:not(.dark_text)"
        ).text()

    @exception_handler
    def get_studio(self) -> Studio:
        return Studio(
            malid=self.get_malid(),
            url=self.get_url(),
            title=self.get_title(),
            titles=self.get_alternate_titles(),
            established=self.get_established(),
            favorites=int(self.get_favorites()),
            anime_count=int(self.get_animecount()),
            external_links=self.get_external_links(),
            images=self.get_image(),
            about=self.get_about(),
        )
