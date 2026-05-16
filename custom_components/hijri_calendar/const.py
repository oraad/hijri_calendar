"""Constants for hijri_calendar."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "hijri_calendar"

ATTR_DATE = "date"
ATTR_OFFSET = "offset"
DEFAULT_LANGUAGE = "en"

SERVICE_CALIBRATE_DATE = "calibrate_date"
SERVICE_CONVERT_TO_HIJRI = "convert_to_hijri"
SERVICE_CONVERT_TO_GREGORIAN = "convert_to_gregorian"
