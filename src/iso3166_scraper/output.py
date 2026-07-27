"""File I/O for writing scraped ISO 3166 data to JSON."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from .models import Country
from .serialization import serialize

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("./countries")


def save_country(country: Country, output_dir: Path = OUTPUT_DIR) -> None:
    """Write an individual country to a JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    data = serialize(country)
    filepath = output_dir / f"{data['alpha2_code']}.json"
    filepath.write_text(
        json.dumps(data, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )

def save_all_countries_json(countries: list[Country], output_dir: Path = OUTPUT_DIR) -> None:
    """Write all countries to a combined ``countries.json``."""
    output_dir.mkdir(parents=True, exist_ok=True)
    serialized = [serialize(c) for c in countries]
    all_path = output_dir / "countries.json"
    all_path.write_text(
        json.dumps({"countries": serialized}, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )
    logger.info("Saved %s (%d countries)", all_path, len(countries))

def save_all_countries(countries: list[Country], output_dir: Path = OUTPUT_DIR) -> None:
    """Write individual country files and a combined ``countries.json``."""
    for country in countries:
        save_country(country, output_dir)
    save_all_countries_json(countries, output_dir)
