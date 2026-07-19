"""Constants for hijri_calendar."""

from logging import Logger, getLogger
from typing import Final

LOGGER: Logger = getLogger(__package__)

DOMAIN: Final = "hijri_calendar"
ATTRIBUTION: Final = "Umm al-Qura calendar via hijridate"
DEFAULT_NAME: Final = "Hijri Calendar"

ATTR_DATE = "date"
ATTR_HIJRI = "hijri"
ATTR_OFFSET = "offset"

OFFSET_DAYS_MIN = -2
OFFSET_DAYS_MAX = 2

CONF_DAY_BOUNDARY = "day_boundary"
CONF_OFFSET_DAYS = "offset_days"
CONF_OBSERVANCES_CALENDAR_LANGUAGE = "observances_calendar_language"
CONF_ISLAMIC_HISTORY_CALENDAR_LANGUAGE = "islamic_history_calendar_language"
CONF_HIJRI_MONTH_STARTS_CALENDAR_LANGUAGE = "hijri_month_starts_calendar_language"

CALENDAR_LANGUAGE_DEFAULT = "default"
CALENDAR_LANGUAGE_ARABIC = "ar"
DEFAULT_CALENDAR_LANGUAGE = CALENDAR_LANGUAGE_DEFAULT

DEFAULT_LANGUAGE = "en"
DEFAULT_DAY_BOUNDARY = "midnight"
DEFAULT_OFFSET_DAYS = 0

DAY_BOUNDARY_MIDNIGHT = "midnight"
DAY_BOUNDARY_SUNSET = "sunset"

SUPPORTED_LANGUAGES: Final[tuple[str, ...]] = (
    "en",
    "ar",
    "bn",
    "de",
    "es",
    "fa",
    "fr",
    "he",
    "id",
    "it",
    "ja",
    "ko",
    "nl",
    "pl",
    "pt",
    "pt-BR",
    "ru",
    "tr",
    "uk",
    "zh-Hans",
)

# Selector option values must match hassfest's translation key rules
# ([a-z0-9-_]+), so mixed-case language codes are lowercased in the UI options.
CALENDAR_LANGUAGE_OPTIONS: Final[tuple[str, ...]] = (
    CALENDAR_LANGUAGE_DEFAULT,
    *(language.lower() for language in SUPPORTED_LANGUAGES),
)

_LANGUAGE_BY_OPTION: Final[dict[str, str]] = {
    language.lower(): language for language in SUPPORTED_LANGUAGES
}

HIJRI_DATE_NATIVE_LANGUAGES: Final[tuple[str, ...]] = ("en", "ar", "bn", "tr")

HijriLanguage = str


def is_supported_language(language: str) -> bool:
    """Return True when language is a supported integration language code."""
    return language in SUPPORTED_LANGUAGES


def canonical_language(language: str) -> str | None:
    """Return the canonical language code for a value or selector option key."""
    if language in SUPPORTED_LANGUAGES:
        return language
    return _LANGUAGE_BY_OPTION.get(language.lower())


SERVICE_CALIBRATE_DATE = "calibrate_date"
SERVICE_CONVERT_TO_HIJRI = "convert_to_hijri"
SERVICE_CONVERT_TO_GREGORIAN = "convert_to_gregorian"
SERVICE_SET_DAY_OFFSET = "set_day_offset"
