import scrapers
import cli
from database import Database
from nlp import analyse

__author__ = "@jordanparker6"

def main():
    cli.log("Newsreader CLI", color="blue", figlet=True)
    cli.log("Welcome to Newsreader CLI", "green")
    database = cli.askDatabaseInfo()
    db = Database(database["uri"])
    methods = cli.askMethodInfo()["methods"]
    cfg = cli.askQuestions(methods)
    if "scrapers" in methods:
        config = scrapers.ScraperConfig(**cfg["scrapers"], headless=True)
        for Scraper in scrapers.ScraperBase.__subclasses__():
            scraper = Scraper(db, config)
            scraper.start()
    if "nlp" in methods:
        analyse(db, cfg["nlp"]["ner"], cfg["nlp"]["sent"])

    if "dashboard" in methods:
        cli.log("serving dashboard...", color="green")
    

if __name__ == "__main__":
    main()
