"""Entry point for ``python -m iso3166_scraper``."""

import logging

from .output import OUTPUT_DIR
from .scraper import ISO3166Scraper
from .output import save_all_countries


def main() -> None:
    """Run the scraper end-to-end and write results to disk."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
    )

    with ISO3166Scraper() as scraper:
        countries = scraper.scrape_all_countries()

    save_all_countries(countries, OUTPUT_DIR)


if __name__ == "__main__":
    main()
