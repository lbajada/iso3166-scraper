"""ISO 3166 Scraper — extract country and subdivision data from the ISO OBP.

Example usage::

    from scraper import ISO3166Scraper, save_all_countries

    with ISO3166Scraper() as scraper:
        countries = scraper.scrape_all_countries()

    save_all_countries(countries)
"""

try:
    from .models import (
        AdditionalInformation,
        ChangeHistory,
        Country,
        Subdivision,
        SubdivisionCategory,
    )
    from .output import save_all_countries
    from .scraper import ISO3166Scraper
except ImportError:
    from models import (
        AdditionalInformation,
        ChangeHistory,
        Country,
        Subdivision,
        SubdivisionCategory,
    )
    from output import save_all_countries
    from scraper import ISO3166Scraper

__all__ = [
    "ISO3166Scraper",
    "Country",
    "Subdivision",
    "SubdivisionCategory",
    "AdditionalInformation",
    "ChangeHistory",
    "save_all_countries",
]
