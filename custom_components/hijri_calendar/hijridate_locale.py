"""Map integration language codes to hijridate-supported locales."""

from __future__ import annotations

from typing import Final, Literal

HijridateLanguage = Literal["en", "ar", "bn", "tr"]

_HIJRI_DATE_MAP: Final[dict[str, HijridateLanguage]] = {
    "ar": "ar",
    "bn": "bn",
    "tr": "tr",
}


def hijridate_language(language: str) -> HijridateLanguage:
    """Return the hijridate locale for month/day names and notation."""
    tag = language.lower().split("-", 1)[0]
    return _HIJRI_DATE_MAP.get(tag, "en")
