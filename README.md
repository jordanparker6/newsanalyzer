# newsreader
A web-scraper, sentiment and entity analysis tool for market research

This library includes the following features:
- A base web-scraper interface for extension to additional scraping activities.
- A relational database for storing of scraped articles and NLP results.
- An NLP pipeline for analysing entities and sentiment

### Quick Start

To install `newsreader` run the following command, `pip3 install https://github.com/jordanparker6/newsreader`.

After `newsreader` has been installed, run the CLI with `python3 -m newsreader`.

Please note that the default setting will save the analyzed news articles to a sqlite database in your current directory.

### Contribute

Pull requests to add additional scrapers to the CLI are welcomed. To add a scraper, implement the `ScraperBase` interface defined at `newsreader/scrapers/base.py` within `newsreader/scrapers/all.py`. For reference, the `ScraperBase` interface is displayed below:

```python
ScraperBase(ABC)
    @abstractmethod
    def _find_documents(self, to: dt.datetime) -> Generator:
        """Collect Document records up to period 'to'."""
        raise NotImplementedError
    
    @abstractmethod
    def _scrape_document(self, href: str):
        """Collect text from the href of a collected Document record."""
        raise NotImplementedError
```

#### To do list:
- possible migration to spaCy for NLP and integration of entity linking with https://github.com/UB-Mannheim/spacyopentapioca
- add database migration utility
- add steamlit interface for summary analytics
- add better handling of errors in NLP pipeline