"""Entry point for ``python -m iso3166_scraper``."""

import argparse
import logging

from .output import OUTPUT_DIR, save_country, save_all_countries_json
from .scraper import ISO3166Scraper


def main() -> None:
    """Run the scraper end-to-end and write results to disk."""
    parser = argparse.ArgumentParser(description="ISO 3166 Scraper")
    parser.add_argument(
        "--all-only",
        action="store_true",
        help="Only output the countries.json file, do not output individual country files.",
    )
    parser.add_argument(
        "--countries",
        type=str,
        help="Comma-separated list of 2-letter country codes to scrape (e.g. US,CA,GB).",
    )
    args = parser.parse_args()

    country_codes = [c.strip().upper() for c in args.countries.split(",")] if args.countries else None

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
    )

    scraped_countries = []

    with ISO3166Scraper() as scraper:
        for country in scraper.scrape_all_countries(country_codes=country_codes):
            scraped_countries.append(country)
            if not args.all_only:
                save_country(country, OUTPUT_DIR)

    save_all_countries_json(scraped_countries, OUTPUT_DIR)


if __name__ == "__main__":
    main()
