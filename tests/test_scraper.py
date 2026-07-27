import pytest
from unittest.mock import MagicMock, patch

from iso3166_scraper.scraper import ISO3166Scraper
from iso3166_scraper.models import Country


class TestScraperFiltering:
    """Test the filtering and generator logic of ISO3166Scraper."""

    @patch("iso3166_scraper.scraper.ISO3166Scraper._get_country_urls")
    @patch("iso3166_scraper.scraper.ISO3166Scraper._parse_country_page")
    @patch("iso3166_scraper.scraper.ISO3166Scraper._handle_turnstile")
    def test_scrape_all_countries_no_filter(self, mock_turnstile, mock_parse, mock_urls):
        """Test scraping all countries without any filter."""
        # Mock URLs
        mock_urls.return_value = [
            "https://www.iso.org/obp/ui/#iso:code:3166:US",
            "https://www.iso.org/obp/ui/#iso:code:3166:CA",
            "https://www.iso.org/obp/ui/#iso:code:3166:GB",
        ]

        # Mock parsed countries
        mock_parse.side_effect = [
            Country(alpha2_code="US", short_name="", short_name_lower_case="", full_name="", alpha3_code="", numeric_code=1, remarks="", independent="", territory_name="", status=""),
            Country(alpha2_code="CA", short_name="", short_name_lower_case="", full_name="", alpha3_code="", numeric_code=1, remarks="", independent="", territory_name="", status=""),
            Country(alpha2_code="GB", short_name="", short_name_lower_case="", full_name="", alpha3_code="", numeric_code=1, remarks="", independent="", territory_name="", status=""),
        ]

        scraper = ISO3166Scraper()
        # Mock the sb attribute to avoid requiring an actual browser
        scraper._sb = MagicMock()

        results = list(scraper.scrape_all_countries())

        assert len(results) == 3
        assert [c.alpha2_code for c in results] == ["US", "CA", "GB"]
        assert scraper.sb.uc_open_with_reconnect.call_count == 3

    @patch("iso3166_scraper.scraper.ISO3166Scraper._get_country_urls")
    @patch("iso3166_scraper.scraper.ISO3166Scraper._parse_country_page")
    @patch("iso3166_scraper.scraper.ISO3166Scraper._handle_turnstile")
    def test_scrape_all_countries_with_filter(self, mock_turnstile, mock_parse, mock_urls):
        """Test scraping specific countries using the country_codes filter."""
        # Mock URLs
        mock_urls.return_value = [
            "https://www.iso.org/obp/ui/#iso:code:3166:US",
            "https://www.iso.org/obp/ui/#iso:code:3166:CA",
            "https://www.iso.org/obp/ui/#iso:code:3166:GB",
        ]

        # Mock parsed countries (only the filtered ones will be requested)
        mock_parse.side_effect = [
            Country(alpha2_code="US", short_name="", short_name_lower_case="", full_name="", alpha3_code="", numeric_code=1, remarks="", independent="", territory_name="", status=""),
            Country(alpha2_code="GB", short_name="", short_name_lower_case="", full_name="", alpha3_code="", numeric_code=1, remarks="", independent="", territory_name="", status=""),
        ]

        scraper = ISO3166Scraper()
        # Mock the sb attribute
        scraper._sb = MagicMock()

        # Request only US and GB (lowercase to test case-insensitivity)
        results = list(scraper.scrape_all_countries(country_codes=["us", "gB"]))

        assert len(results) == 2
        assert [c.alpha2_code for c in results] == ["US", "GB"]
        
        # Verify the browser only navigated to the 2 requested URLs
        assert scraper.sb.uc_open_with_reconnect.call_count == 2
        
        urls_visited = [
            call.args[0] for call in scraper.sb.uc_open_with_reconnect.call_args_list
        ]
        assert "https://www.iso.org/obp/ui/#iso:code:3166:US" in urls_visited
        assert "https://www.iso.org/obp/ui/#iso:code:3166:GB" in urls_visited
        assert "https://www.iso.org/obp/ui/#iso:code:3166:CA" not in urls_visited
