"""Tests for JSON serialization and normalization."""

from iso3166_scraper.models import (
    AdditionalInformation,
    Country,
    Subdivision,
    SubdivisionCategory,
)
from iso3166_scraper.serialization import serialize


class TestNormalize:
    """Tests for the _normalize / serialize pipeline."""

    def test_empty_strings_become_none(self):
        sub = Subdivision(
            category="Land",
            code3166_2="DE-BW",
            name="Baden-Württemberg",
            local_variant="",
            language_code="de",
            romanization_system="",
            parent_subdivision="",
        )
        result = serialize(sub)
        assert result["local_variant"] is None
        assert result["romanization_system"] is None
        assert result["parent_subdivision"] is None

    def test_non_empty_strings_preserved(self):
        sub = Subdivision(
            category="Land",
            code3166_2="DE-BW",
            name="Baden-Württemberg",
            local_variant=None,
            language_code="de",
            romanization_system=None,
            parent_subdivision=None,
        )
        result = serialize(sub)
        assert result["category"] == "Land"
        assert result["name"] == "Baden-Württemberg"
        assert result["language_code"] == "de"

    def test_code3166_2_renamed(self):
        """The internal field ``code3166_2`` must appear as ``3166-2_code`` in JSON."""
        sub = Subdivision(
            category="Land",
            code3166_2="DE-BW",
            name="Baden-Württemberg",
            local_variant=None,
            language_code="de",
            romanization_system=None,
            parent_subdivision=None,
        )
        result = serialize(sub)
        assert "3166-2_code" in result
        assert "code3166_2" not in result
        assert result["3166-2_code"] == "DE-BW"

    def test_none_values_preserved(self):
        sub = Subdivision(
            category=None,
            code3166_2=None,
            name=None,
            local_variant=None,
            language_code=None,
            romanization_system=None,
            parent_subdivision=None,
        )
        result = serialize(sub)
        assert result["category"] is None
        assert result["3166-2_code"] is None

    def test_nested_serialization(self):
        """Normalization must recurse into nested lists."""
        country = Country(
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
            subdivision_categories=[
                SubdivisionCategory(category_count=68, category_locales=["local council (en)"]),
            ],
            subdivisions=[
                Subdivision(
                    category="local council",
                    code3166_2="MT-01",
                    name="Attard",
                    local_variant="",
                    language_code="mt",
                    romanization_system="",
                    parent_subdivision="",
                ),
            ],
            additional_information=[
                AdditionalInformation(
                    administrative_language_alpha2="mt",
                    administrative_language_alpha3="mlt",
                    local_short_name="Malta",
                ),
            ],
        )
        result = serialize(country)

        # Top-level fields
        assert result["alpha2_code"] == "MT"
        assert result["numeric_code"] == 470

        # Nested subdivision — key rename and empty→None
        sub = result["subdivisions"][0]
        assert "3166-2_code" in sub
        assert sub["3166-2_code"] == "MT-01"
        assert sub["local_variant"] is None
        assert sub["romanization_system"] is None

        # Nested additional information
        ai = result["additional_information"][0]
        assert ai["administrative_language_alpha2"] == "mt"

    def test_integer_values_preserved(self):
        """Numeric values must not be coerced to strings or None."""
        country = Country(
            alpha2_code="MT",
            short_name=None,
            short_name_lower_case=None,
            full_name=None,
            alpha3_code=None,
            numeric_code=470,
            remarks=None,
            independent=None,
            territory_name=None,
            status=None,
        )
        result = serialize(country)
        assert result["numeric_code"] == 470
        assert isinstance(result["numeric_code"], int)
