import logging
from src.iso3166_scraper.scraper import ISO3166Scraper

logging.basicConfig(level=logging.INFO)

with ISO3166Scraper() as scraper:
    urls = scraper._get_country_urls()
    print("Found urls:", len(urls))
    for url in urls[:5]:
        print(url)
