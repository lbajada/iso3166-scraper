"""Smoke test: verify that SeleniumBase UC mode bypasses Cloudflare Turnstile.

Run inside Docker to confirm the container can reach the ISO OBP country list:

    docker compose run --rm iso3166-scraper python3 tests/test_turnstile.py
"""

import logging
import sys

from seleniumbase import SB

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

URL = "https://www.iso.org/obp/ui/#iso:pub:PUB500001:en"
SUCCESS_SELECTOR = ".grs-grid"
TURNSTILE_IFRAME = 'iframe[src*="challenges.cloudflare.com"]'


def main() -> int:
    """Return 0 on success, 1 on failure."""
    logger.info("Starting Turnstile bypass smoke test …")

    with SB(uc=True, xvfb=True, headless=False, incognito=True) as sb:
        sb.uc_open_with_reconnect(URL, reconnect_time=12)

        # If a Turnstile challenge iframe is visible, click it
        if sb.is_element_visible(TURNSTILE_IFRAME):
            logger.info("Turnstile challenge detected — clicking …")
            sb.uc_gui_click_captcha()
            sb.sleep(5)

        # Check if we got through
        try:
            sb.wait_for_element(SUCCESS_SELECTOR, timeout=30)
            logger.info("SUCCESS — Cloudflare bypassed, country list loaded!")
            logger.info("Page title: %s", sb.get_title())
            return 0
        except Exception:
            logger.error("FAILED — could not load country list.")
            logger.error("Page title: %s", sb.get_title())
            logger.error("Current URL: %s", sb.get_current_url())
            logger.error(
                "Page source (first 2000 chars):\n%s",
                sb.get_page_source()[:2000],
            )
            return 1


if __name__ == "__main__":
    sys.exit(main())
