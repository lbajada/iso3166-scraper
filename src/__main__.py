"""Entry point for ``python -m scraper`` or ``python -m src``."""

import logging

try:
    from .output import OUTPUT_DIR, save_all_countries
    from .scraper import ISO3166Scraper
except ImportError:
    from output import OUTPUT_DIR, save_all_countries
    from scraper import ISO3166Scraper


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
