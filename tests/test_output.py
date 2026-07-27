"""Tests for JSON file output."""

import json
from pathlib import Path

from iso3166_scraper.models import Country, Subdivision
from iso3166_scraper.output import save_all_countries


class TestSaveAllCountries:
    """Tests for the save_all_countries function."""

    def test_creates_individual_files(self, tmp_path: Path):
        countries = [
            Country(
                alpha2_code="MT",
                short_name="MALTA",
                short_name_lower_case="Malta",
                full_name="the Republic of Malta",
                alpha3_code="MLT",
                numeric_code=470,
                remarks=None,
                independent="Yes",
                territory_name=None,
                status="Officially assigned",
            ),
            Country(
                alpha2_code="DE",
                short_name="GERMANY",
                short_name_lower_case="Germany",
                full_name="the Federal Republic of Germany",
                alpha3_code="DEU",
                numeric_code=276,
                remarks=None,
                independent="Yes",
                territory_name=None,
                status="Officially assigned",
            ),
        ]

        save_all_countries(countries, tmp_path)

        assert (tmp_path / "MT.json").exists()
        assert (tmp_path / "DE.json").exists()
        assert (tmp_path / "all_countries.json").exists()

    def test_individual_file_content(self, tmp_path: Path):
        countries = [
            Country(
                alpha2_code="MT",
                short_name="MALTA",
                short_name_lower_case="Malta",
                full_name="the Republic of Malta",
                alpha3_code="MLT",
                numeric_code=470,
                remarks=None,
                independent="Yes",
                territory_name=None,
                status="Officially assigned",
            ),
        ]

        save_all_countries(countries, tmp_path)

        data = json.loads((tmp_path / "MT.json").read_text(encoding="utf-8"))
        assert data["alpha2_code"] == "MT"
        assert data["short_name"] == "MALTA"
        assert data["numeric_code"] == 470
        assert data["remarks"] is None
        assert data["subdivisions"] == []

    def test_combined_file_structure(self, tmp_path: Path):
        countries = [
            Country(
                alpha2_code="MT",
                short_name="MALTA",
                short_name_lower_case="Malta",
                full_name=None,
                alpha3_code="MLT",
                numeric_code=470,
                remarks=None,
                independent=None,
                territory_name=None,
                status=None,
            ),
            Country(
                alpha2_code="DE",
                short_name="GERMANY",
                short_name_lower_case="Germany",
                full_name=None,
                alpha3_code="DEU",
                numeric_code=276,
                remarks=None,
                independent=None,
                territory_name=None,
                status=None,
            ),
        ]

        save_all_countries(countries, tmp_path)

        data = json.loads((tmp_path / "all_countries.json").read_text(encoding="utf-8"))
        assert "countries" in data
        assert len(data["countries"]) == 2
        codes = {c["alpha2_code"] for c in data["countries"]}
        assert codes == {"MT", "DE"}

    def test_unicode_preserved(self, tmp_path: Path):
        """Non-ASCII characters must be written without escaping."""
        countries = [
            Country(
                alpha2_code="DE",
                short_name="GERMANY",
                short_name_lower_case="Germany",
                full_name="the Federal Republic of Germany",
                alpha3_code="DEU",
                numeric_code=276,
                remarks=None,
                independent="Yes",
                territory_name=None,
                status="Officially assigned",
                subdivisions=[
                    Subdivision(
                        category="Land",
                        code3166_2="DE-BW",
                        name="Baden-Württemberg",
                        local_variant=None,
                        language_code="de",
                        romanization_system=None,
                        parent_subdivision=None,
                    ),
                ],
            ),
        ]

        save_all_countries(countries, tmp_path)

        raw = (tmp_path / "DE.json").read_text(encoding="utf-8")
        assert "Baden-Württemberg" in raw
        assert "\\u" not in raw  # ensure_ascii=False

    def test_key_rename_in_output(self, tmp_path: Path):
        """The internal ``code3166_2`` must appear as ``3166-2_code`` in the JSON files."""
        countries = [
            Country(
                alpha2_code="MT",
                short_name="MALTA",
                short_name_lower_case="Malta",
                full_name=None,
                alpha3_code="MLT",
                numeric_code=470,
                remarks=None,
                independent=None,
                territory_name=None,
                status=None,
                subdivisions=[
                    Subdivision(
                        category="local council",
                        code3166_2="MT-01",
                        name="Attard",
                        local_variant=None,
                        language_code="mt",
                        romanization_system=None,
                        parent_subdivision=None,
                    ),
                ],
            ),
        ]

        save_all_countries(countries, tmp_path)

        data = json.loads((tmp_path / "MT.json").read_text(encoding="utf-8"))
        sub = data["subdivisions"][0]
        assert "3166-2_code" in sub
        assert "code3166_2" not in sub

    def test_creates_output_dir(self, tmp_path: Path):
        """The output directory should be created if it doesn't exist."""
        nested = tmp_path / "deep" / "nested" / "dir"

        countries = [
            Country(
                alpha2_code="MT",
                short_name="MALTA",
                short_name_lower_case="Malta",
                full_name=None,
                alpha3_code=None,
                numeric_code=None,
                remarks=None,
                independent=None,
                territory_name=None,
                status=None,
            ),
        ]

        save_all_countries(countries, nested)

        assert nested.exists()
        assert (nested / "MT.json").exists()
