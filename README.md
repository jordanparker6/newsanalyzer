# newsreader
A web-scraper, sentiment and entity analysis tool for market research

This library includes the following features:
- A base web-scraper interface for extension to additional scraping activities.
- A relational database for storing of scraped articles and NLP results.
- An NLP pipeline for analysing entities and sentiment

To do list:
- possible migration to spaCy for NLP and integration of entity linking with https://github.com/UB-Mannheim/spacyopentapioca
- add database migration utility
- add steamlit interface for summary analytics
- add better handling of errors in NLP pipeline