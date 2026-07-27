"""ISO 3166 scraper using SeleniumBase UC mode with a virtual display.

Navigates the ISO Online Browsing Platform (OBP) to extract country codes,
subdivision data, additional language information, and change history for every
ISO 3166 entry.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from seleniumbase import SB

from .models import (
    AdditionalInformation,
    ChangeHistory,
    Country,
    Subdivision,
    SubdivisionCategory,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ISO_COUNTRY_LIST_URL = "https://www.iso.org/obp/ui/#iso:pub:PUB500001:en"
PAGE_LOAD_WAIT_SECONDS = 30

# Cloudflare Turnstile challenge iframe selector
TURNSTILE_IFRAME = 'iframe[src*="challenges.cloudflare.com"]'

# ---------------------------------------------------------------------------
# Column mappings — map HTML table headers to internal field names
# ---------------------------------------------------------------------------

_ADDITIONAL_INFO_COLUMNS: dict[str, str] = {
    "Administrative language(s) alpha-2": "al_alpha2",
    "Administrative language(s) alpha-3": "al_alpha3",
    "Local short name": "local_short_name",
}

_CHANGE_HISTORY_COLUMNS: dict[str, str] = {
    "Effective date of change": "date",
    "Short description of change (en)": "short_description_en",
    "Short description of change (fr)": "short_description_fr",
}

_SUBDIVISION_COLUMNS: dict[str, str] = {
    "Subdivision category": "category",
    "3166-2 code": "code",
    "Subdivision name": "name",
    "Local variant": "local_variant",
    "Language code": "language_code",
    "Romanization system": "romanization_system",
    "Parent subdivision": "parent_subdivision",
}

_CORE_VIEW_FIELDS: dict[str, str] = {
    "Alpha-2 code": "alpha2_code",
    "Short name": "short_name",
    "Short name lower case": "short_name_lower_case",
    "Full name": "full_name",
    "Alpha-3 code": "alpha3_code",
    "Numeric code": "numeric_code",
    "Remarks": "remarks",
    "Independent": "independent",
    "Territory name": "territory_name",
    "Status": "status",
}


# ---------------------------------------------------------------------------
# Table-parsing helpers
# ---------------------------------------------------------------------------

def _discover_columns(
    headers: list[WebElement],
    column_map: dict[str, str],
) -> dict[str, int]:
    """Map logical column names to their positional indices in a table header.

    Returns a dict of ``{internal_name: column_index}`` for every header text
    that appears in *column_map*.
    """
    positions: dict[str, int] = {}
    for index, header in enumerate(headers):
        internal_name = column_map.get(header.text)
        if internal_name is not None:
            positions[internal_name] = index
    return positions


def _parse_table(
    table_element: WebElement,
    column_map: dict[str, str],
    row_factory: Callable[[dict[str, int], list[WebElement]], Any],
) -> list[Any]:
    """Generic helper to parse an HTML table into a list of dataclass instances.

    Args:
        table_element: The ``<table>`` (or container with ``<thead>``/``<tbody>``)
            WebElement to parse.
        column_map: Mapping of header text → internal field name.
        row_factory: Callable that receives ``(column_positions, cells)`` and
            returns a single dataclass instance.
    """
    headers = table_element.find_element(
        By.CSS_SELECTOR, "thead"
    ).find_elements(By.CSS_SELECTOR, "th")
    positions = _discover_columns(headers, column_map)

    rows = table_element.find_element(
        By.CSS_SELECTOR, "tbody"
    ).find_elements(By.CSS_SELECTOR, "tr")

    return [
        row_factory(positions, cells)
        for row in rows
        for cells in [row.find_elements(By.CSS_SELECTOR, "td")]
    ]


# ---------------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------------

class ISO3166Scraper:
    """Scrape ISO 3166 data using SeleniumBase UC mode with a virtual display.

    SeleniumBase's Undetected-Chromedriver (UC) mode evades Cloudflare
    Turnstile by running Chrome in normal headed mode inside an Xvfb
    virtual framebuffer, patching the driver binary, and strategically
    disconnecting the WebDriver during page loads.

    Use as a context manager to ensure proper cleanup::

        with ISO3166Scraper() as scraper:
            countries = scraper.scrape_all_countries()
    """

    def __init__(self) -> None:
        self._sb_manager: Any = None
        self._sb: Any = None

    # -- Context manager protocol -------------------------------------------

    def __enter__(self) -> ISO3166Scraper:
        self._sb_manager = SB(
            uc=True,
            xvfb=True,
            headless=False,
            incognito=True,
        )
        self._sb = self._sb_manager.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._sb_manager is not None:
            self._sb_manager.__exit__(exc_type, exc_val, exc_tb)
            self._sb_manager = None
            self._sb = None

    @property
    def sb(self) -> Any:
        """Return the active SeleniumBase instance."""
        if self._sb is None:
            raise RuntimeError("Scraper is not open; use it as a context manager.")
        return self._sb

    @property
    def driver(self) -> Any:
        """Return the underlying Selenium WebDriver for element queries."""
        return self.sb.driver

    # -- Cloudflare handling ------------------------------------------------

    def _handle_turnstile(self) -> None:
        """Detect and click through a Cloudflare Turnstile challenge."""
        try:
            if self.sb.is_element_visible(TURNSTILE_IFRAME):
                logger.info("Turnstile challenge detected — clicking …")
                self.sb.uc_gui_click_captcha()
                self.sb.sleep(3)
        except Exception:  # pylint: disable=broad-exception-caught
            # If we can't detect or click the captcha, continue anyway —
            # the page may have already passed the challenge.
            pass

    # -- URL discovery ------------------------------------------------------

    def _get_country_urls(self) -> list[str]:
        """Fetch the master country list and extract all country-page URLs."""
        self.sb.uc_open_with_reconnect(ISO_COUNTRY_LIST_URL, reconnect_time=12)
        self._handle_turnstile()

        logger.info("Page title: %s", self.sb.get_title())
        logger.info("Current URL: %s", self.sb.get_current_url())

        try:
            self.sb.wait_for_element(".grs-grid", timeout=PAGE_LOAD_WAIT_SECONDS)
        except Exception:
            logger.error("Timed out waiting for country list.")
            logger.error("Final page title: %s", self.sb.get_title())
            logger.error("Final URL: %s", self.sb.get_current_url())
            logger.error(
                "Page source:\n%s", self.sb.get_page_source()[:5000]
            )
            raise

        return [
            link.get_attribute("href")
            for link in self.driver.find_element(
                By.CLASS_NAME, "grs-grid"
            ).find_elements(By.CSS_SELECTOR, "a")
        ]

    # -- Section parsers ----------------------------------------------------

    def _get_additional_information(self) -> list[AdditionalInformation]:
        """Parse the 'Additional information' table on the current page."""
        table = self.driver.find_element(By.ID, "country-additional-info")

        def _build_row(pos: dict[str, int], cells: list[WebElement]) -> AdditionalInformation:
            return AdditionalInformation(
                administrative_language_alpha2=cells[pos["al_alpha2"]].text,
                administrative_language_alpha3=cells[pos["al_alpha3"]].text,
                local_short_name=cells[pos["local_short_name"]].text,
            )

        return _parse_table(table, _ADDITIONAL_INFO_COLUMNS, _build_row)

    def _get_subdivision_categories(self) -> list[SubdivisionCategory]:
        """Parse subdivision category summaries from ``<p>`` elements."""
        categories: list[SubdivisionCategory] = []

        for paragraph in self.driver.find_elements(By.CSS_SELECTOR, "p"):
            count_elements = paragraph.find_elements(By.CLASS_NAME, "category-count")
            if not count_elements:
                continue

            category_count = int(count_elements[0].text)
            category_locales = [
                el.text
                for el in paragraph.find_elements(By.CLASS_NAME, "category-locales")
            ]
            categories.append(
                SubdivisionCategory(
                    category_count=category_count,
                    category_locales=category_locales,
                )
            )

        return categories

    def _get_change_history(self) -> list[ChangeHistory]:
        """Parse the 'Change history of country code' table, if present."""
        change_history_div = None

        for div in self.driver.find_element(
            By.CLASS_NAME, "code-view-container"
        ).find_elements(By.CSS_SELECTOR, "div"):
            h3_elements = div.find_elements(By.CSS_SELECTOR, "h3")
            if h3_elements and h3_elements[0].text == "Change history of country code":
                change_history_div = div
                break

        if change_history_div is None:
            return []

        def _build_row(pos: dict[str, int], cells: list[WebElement]) -> ChangeHistory:
            return ChangeHistory(
                date=cells[pos["date"]].text,
                short_description_en=cells[pos["short_description_en"]].text,
                short_description_fr=cells[pos["short_description_fr"]].text,
            )

        return _parse_table(change_history_div, _CHANGE_HISTORY_COLUMNS, _build_row)

    def _get_subdivisions(self) -> list[Subdivision]:
        """Parse the full subdivisions table."""
        table = self.driver.find_element(By.ID, "subdivision")

        def _build_row(pos: dict[str, int], cells: list[WebElement]) -> Subdivision:
            return Subdivision(
                category=cells[pos["category"]].text,
                code3166_2=cells[pos["code"]].text.replace("*", ""),
                name=cells[pos["name"]].text,
                local_variant=cells[pos["local_variant"]].text,
                language_code=cells[pos["language_code"]].text,
                romanization_system=cells[pos["romanization_system"]].text,
                parent_subdivision=cells[pos["parent_subdivision"]].text,
            )

        return _parse_table(table, _SUBDIVISION_COLUMNS, _build_row)

    # -- Country page parser ------------------------------------------------

    def _parse_country_page(self) -> Country:
        """Extract all data from the currently loaded country page."""
        core_view_lines = self.driver.find_element(
            By.CLASS_NAME, "core-view-summary"
        ).find_elements(By.CLASS_NAME, "core-view-line")

        fields: dict[str, Any] = {}

        for core_view in core_view_lines:
            field_name = core_view.find_element(
                By.CLASS_NAME, "core-view-field-name"
            ).text

            internal_name = _CORE_VIEW_FIELDS.get(field_name)
            if internal_name is None:
                continue

            value_elements = core_view.find_elements(
                By.CLASS_NAME, "core-view-field-value"
            )
            if not value_elements:
                continue

            field_value = value_elements[0].text
            if not field_value:
                continue

            field_value = field_value.replace("*", "")

            if internal_name == "numeric_code":
                fields[internal_name] = int(field_value)
            else:
                fields[internal_name] = field_value

        return Country(
            alpha2_code=fields.get("alpha2_code"),
            short_name=fields.get("short_name"),
            short_name_lower_case=fields.get("short_name_lower_case"),
            full_name=fields.get("full_name"),
            alpha3_code=fields.get("alpha3_code"),
            numeric_code=fields.get("numeric_code"),
            remarks=fields.get("remarks"),
            independent=fields.get("independent"),
            territory_name=fields.get("territory_name"),
            status=fields.get("status"),
            subdivision_categories=self._get_subdivision_categories(),
            subdivisions=self._get_subdivisions(),
            additional_information=self._get_additional_information(),
            change_history=self._get_change_history(),
        )

    # -- High-level orchestration -------------------------------------------

    def scrape_all_countries(self) -> list[Country]:
        """Scrape every country from the ISO OBP and return the full list."""
        country_urls = self._get_country_urls()
        logger.info("Found %d country URLs to scrape.", len(country_urls))

        countries: list[Country] = []

        for index, url in enumerate(country_urls, start=1):
            self.sb.uc_open_with_reconnect(url, reconnect_time=8)
            self._handle_turnstile()

            self.sb.wait_for_element("#subdivision", timeout=PAGE_LOAD_WAIT_SECONDS)

            country = self._parse_country_page()
            countries.append(country)

            logger.info(
                "[%d/%d] Scraped %s (%s)",
                index,
                len(country_urls),
                country.alpha2_code,
                country.short_name,
            )

            # Small delay between requests to be respectful
            time.sleep(1)

        return countries
