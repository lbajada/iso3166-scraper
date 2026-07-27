"""Data models for ISO 3166 country and subdivision records."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AdditionalInformation:
    """Language-specific administrative information for a country."""

    administrative_language_alpha2: str | None
    administrative_language_alpha3: str | None
    local_short_name: str | None


@dataclass
class Subdivision:
    """A single ISO 3166-2 subdivision entry."""

    category: str | None
    code3166_2: str | None
    name: str | None
    local_variant: str | None
    language_code: str | None
    romanization_system: str | None
    parent_subdivision: str | None


@dataclass
class SubdivisionCategory:
    """Summary count and locale labels for a subdivision category."""

    category_count: int
    category_locales: list[str] = field(default_factory=list)


@dataclass
class ChangeHistory:
    """A single change-history record for a country code."""

    date: str | None
    short_description_en: str | None
    short_description_fr: str | None


@dataclass
class Country:
    """Complete ISO 3166 record for a single country."""

    alpha2_code: str | None
    short_name: str | None
    short_name_lower_case: str | None
    full_name: str | None
    alpha3_code: str | None
    numeric_code: int | None
    remarks: str | None
    independent: str | None
    territory_name: str | None
    status: str | None
    subdivision_categories: list[SubdivisionCategory] = field(default_factory=list)
    subdivisions: list[Subdivision] = field(default_factory=list)
    additional_information: list[AdditionalInformation] = field(default_factory=list)
    change_history: list[ChangeHistory] = field(default_factory=list)
