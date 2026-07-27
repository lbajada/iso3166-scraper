"""File I/O for writing scraped ISO 3166 data to JSON."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from .models import Country
from .serialization import serialize

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("./countries")


def save_all_countries(countries: list[Country], output_dir: Path = OUTPUT_DIR) -> None:
    """Write individual country files and a combined ``all_countries.json``."""
    output_dir.mkdir(parents=True, exist_ok=True)

    serialized = [serialize(c) for c in countries]

    for data in serialized:
        filepath = output_dir / f"{data['alpha2_code']}.json"
        filepath.write_text(
            json.dumps(data, ensure_ascii=False, indent=4),
            encoding="utf-8",
        )

    all_path = output_dir / "all_countries.json"
    all_path.write_text(
        json.dumps({"countries": serialized}, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )
    logger.info("Saved %s (%d countries)", all_path, len(countries))
