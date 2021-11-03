from typing import Generator
from dateutil.parser import parse
import datetime as dt
from .base import ScraperBase 

# ~~~ Scraper Implementations ~~~~~~~~~~~~~~~~~

class ITNewsScraper(ScraperBase):
    """
    A web-scraper to collect all recent ITNews articles to a specified date.
    
    """

    url = "https://www.itnews.com.au/news"

    def _find_documents(self, to: dt.datetime) -> Generator:
        i = 1
        while True:
            html = self.get_html(self.url + f"/page{i}")
            i += 1
            for el in html.select('a.article-list-container'):
                doc = {}
                doc["href"] = self.url + el["href"]
                doc["name"] = el.select_one(".article-list-title").text.strip()
                doc["date"] = parse(el.select_one(".article-list-details").text.strip())
                yield doc
            if to > doc["date"]:
                break

    def _scrape_document(self, href: str):
        html = self.get_html(href)
        text = ""
        paragraphs = html.select("#article-body > p")
        if len(paragraphs) > 0:
            for p in paragraphs:
                text += p.text + "\n\n"
        else:
            text = html.select_one("#article-body").text
        return text