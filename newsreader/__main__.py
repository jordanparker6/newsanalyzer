from . import scrapers
from . import cli
from .database import Database
from .nlp.transformers import analyse

__author__ = "@jordanparker6"

def main():
    cli.log("Newsreader CLI", style="#00b3ff", figlet=True)
    cli.log("Welcome to Newsreader CLI", style="#07b05b bold")
    database = cli.askDatabaseInfo()
    db = Database(database["uri"])
    methods = cli.askMethodInfo()["methods"]
    cfg = cli.askQuestions(methods)

    # 1) Run Scrapers
    if "scrapers" in methods:
        selected_scrapers = cfg["scrapers"]["classes"]
        del cfg["scrapers"]["classes"]
        config = scrapers.ScraperConfig(**cfg["scrapers"], headless=True)
        for Scraper in scrapers.ScraperBase.__subclasses__():
            if Scraper.__name__ in selected_scrapers:
                scraper = Scraper(db, config)
                scraper.start()

    # 2) Run NLP Pipeline
    if "nlp" in methods:
        analyse(db, cfg["nlp"]["ner"], cfg["nlp"]["sent"])

    # 3) Serve Dashboard
    if "dashboard" in methods:
        cli.log("serving dashboard...", color="green")
    

if __name__ == "__main__":
    main()
