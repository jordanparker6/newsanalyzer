import sys
from . import scrapers
from . import cli
from .database import Database
from .nlp.spacy import analyse
from .utils import install_spacy_required_packages, run_streamlit_dashboard

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
        model = cfg["nlp"]["model"]
        install_spacy_required_packages(model)
        analyse(db, model)

    # 3) Serve Dashboard
    if "dashboard" in methods:
        cli.log("Serving your dashboard...", style="#07b05b bold")
        run_streamlit_dashboard(database["uri"])
    

if __name__ == "__main__":
    main()
