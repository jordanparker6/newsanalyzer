import config
from scrapers.base import ScraperBase
from database import Database
from nlp import analyse

def main():
    database = Database(config.DB_URI)
    for Scraper in ScraperBase.__subclasses__():
        scraper = Scraper(database)
        scraper.run(to_period="2020-07-01")

if __name__ == "__main__":
    main()
