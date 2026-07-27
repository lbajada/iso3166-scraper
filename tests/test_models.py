"""Tests for data model construction and field defaults."""

try:
    from models import (
        AdditionalInformation,
        ChangeHistory,
        Country,
        Subdivision,
        SubdivisionCategory,
    )
except ImportError:
    from src.models import (
        AdditionalInformation,
        ChangeHistory,
        Country,
        Subdivision,
        SubdivisionCategory,
    )


class TestAdditionalInformation:
    """Tests for the AdditionalInformation dataclass."""

    def test_fields(self):
        info = AdditionalInformation(
            administrative_language_alpha2="mt",
            administrative_language_alpha3="mlt",
            local_short_name="Malta",
        )
        assert info.administrative_language_alpha2 == "mt"
        assert info.administrative_language_alpha3 == "mlt"
        assert info.local_short_name == "Malta"

    def test_nullable_fields(self):
        info = AdditionalInformation(
            administrative_language_alpha2=None,
            administrative_language_alpha3=None,
            local_short_name=None,
        )
        assert info.administrative_language_alpha2 is None
        assert info.administrative_language_alpha3 is None
        assert info.local_short_name is None


class TestSubdivision:
    """Tests for the Subdivision dataclass."""

    def test_fields(self):
        sub = Subdivision(
            category="Land",
            code3166_2="DE-BW",
            name="Baden-Württemberg",
            local_variant=None,
            language_code="de",
            romanization_system=None,
            parent_subdivision=None,
        )
        assert sub.category == "Land"
        assert sub.code3166_2 == "DE-BW"
        assert sub.name == "Baden-Württemberg"
        assert sub.language_code == "de"


class TestSubdivisionCategory:
    """Tests for the SubdivisionCategory dataclass."""

    def test_default_locales(self):
        cat = SubdivisionCategory(category_count=16)
        assert cat.category_count == 16
        assert cat.category_locales == []

    def test_with_locales(self):
        cat = SubdivisionCategory(
            category_count=16,
            category_locales=["Land (en)", "land (fr)", "Land (de)"],
        )
        assert len(cat.category_locales) == 3


class TestChangeHistory:
    """Tests for the ChangeHistory dataclass."""

    def test_fields(self):
        ch = ChangeHistory(
            date="2020-11-24",
            short_description_en="Change of spelling",
            short_description_fr="Modification de l'orthographe",
        )
        assert ch.date == "2020-11-24"
        assert ch.short_description_en == "Change of spelling"


class TestCountry:
    """Tests for the Country dataclass."""

    def test_minimal_country(self):
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
        )
        assert country.alpha2_code == "MT"
        assert country.numeric_code == 470
        assert country.subdivisions == []
        assert country.additional_information == []
        assert country.change_history == []
        assert country.subdivision_categories == []

    def test_country_with_subdivisions(self):
        sub = Subdivision(
            category="local council",
            code3166_2="MT-01",
            name="Attard",
            local_variant=None,
            language_code="mt",
            romanization_system=None,
            parent_subdivision=None,
        )
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
            subdivisions=[sub],
        )
        assert len(country.subdivisions) == 1
        assert country.subdivisions[0].code3166_2 == "MT-01"

    def test_all_none_fields(self):
        """Countries with no data should still construct cleanly."""
        country = Country(
            alpha2_code=None,
            short_name=None,
            short_name_lower_case=None,
            full_name=None,
            alpha3_code=None,
            numeric_code=None,
            remarks=None,
            independent=None,
            territory_name=None,
            status=None,
        )
        assert country.alpha2_code is None
        assert country.numeric_code is None
