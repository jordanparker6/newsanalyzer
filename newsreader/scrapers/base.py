from abc import abstractmethod
from dataclasses import dataclass
from typing import Generator
import hashlib
import requests
import threading
from bs4 import BeautifulSoup
import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sqlmodel import select, or_
from newsreader.database import Database, Document
# ~~~ Base Scraping Class ~~~~~~~~~~~~~~~~~~~~~~

@dataclass
class ScraperConfig:
    period_to: str
    headless: bool = True
    batch: int = 10

class ScraperBase(threading.Thread):
    """
    A base class for building scrapers. 
    
    Please ensure that abstract methods are implemented
    to handle the bespoke scraping requirements of the
    webpage at hand.
    """
    url: str = ""

    def __init__(self, 
            database: Database, 
            config: ScraperConfig
        ) -> None:
        super().__init__()
        print("Creating scraper for: ", self.url)
        self.name = type(self).__name__
        self.db = database
        self.config = config
        options = Options()
        if config.headless:
            options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=options)
    
    def run(self):
        self.collect_documents(self.config.period_to, self.config.batch)
        self.scrape_documents()

    def collect_documents(self, to: str, batch: int):
        """
        Collects the URLs of documents between a certain period

        """
        now = dt.datetime.now()
        to = dt.datetime.fromisoformat(to)
        i = 0
        cache = []
        print("Collecting Documents:")
        for doc in self._find_documents(to=to):
            document = Document(
                id=hashlib.md5(doc["href"].encode("utf-8")).hexdigest(), 
                date_collected=dt.datetime.now(),
                collected_by=self.name,
                **doc
            )
            cache.append(document)
            i += 1
            if i % batch:
                self.db.create_all(cache)
                cache = []
            print("Total Documents", i, "|", doc["date"], "------->", to, end='\r', flush=True)
        self.db.create_all(cache)
        print("Total Documents", i, "|", now, "------->", doc["date"])

    def scrape_documents(self, batch=10):
        """
        Scrapes the document text from any collected documents missing text
        
        """
        cache = []
        statement = select(
                        Document
                    ).where(
                        or_(Document.text == None, Document.text == "")
                    ).where(
                        Document.collected_by == self.name
                    )
        docs = self.db.exec(statement)
        print("Scraping Document Text:")
        for i, doc in enumerate(docs):
            text = self._scrape_document(doc.href).strip()
            doc.text = text
            cache.append(doc)
            if i % batch:
                self.db.create_all(cache)
                cache = []
            print("Total Documents", i, "//", len(docs), end='\r', flush=True)
        print("Total Documents", i, "//", len(docs))
    
    # ~~~ Utility Methods ~~~~~~~~~~~~~~~~~~~~~~~

    def get_html(self, href: str):
        page = requests.get(href)
        return BeautifulSoup(page.content, features="lxml")

    # ~~~ Abstract Methods ~~~~~~~~~~~~~~~~~~~~~~

    @abstractmethod
    def _find_documents(self, to: dt.datetime) -> Generator:
        raise NotImplementedError
    
    @abstractmethod
    def _scrape_document(self, href: str) -> str:
        raise NotImplementedError

    def __del__(self):
        self.browser.close()