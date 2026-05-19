"""Constants for hijri_calendar."""

from logging import Logger, getLogger
from typing import Final, Literal

LOGGER: Logger = getLogger(__package__)

DOMAIN: Final = "hijri_calendar"
ATTRIBUTION: Final = "Umm al-Qura calendar via hijridate"
DEFAULT_NAME: Final = "Hijri Calendar"

ATTR_DATE = "date"
ATTR_OFFSET = "offset"

CONF_DAY_BOUNDARY = "day_boundary"
CONF_OFFSET_DAYS = "offset_days"

DEFAULT_LANGUAGE = "en"
DEFAULT_DAY_BOUNDARY = "midnight"
DEFAULT_OFFSET_DAYS = 0

DAY_BOUNDARY_MIDNIGHT = "midnight"
DAY_BOUNDARY_SUNSET = "sunset"

SUPPORTED_LANGUAGES: Final[tuple[str, ...]] = ("en", "ar", "tr")

HijriLanguage = Literal["en", "ar", "tr"]

SERVICE_CALIBRATE_DATE = "calibrate_date"
SERVICE_CONVERT_TO_HIJRI = "convert_to_hijri"
SERVICE_CONVERT_TO_GREGORIAN = "convert_to_gregorian"
SERVICE_SET_DAY_OFFSET = "set_day_offset"
