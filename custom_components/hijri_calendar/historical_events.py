"""Curated Islamic historical milestones for the history calendar."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

ALL_HISTORICAL_CATEGORIES: Final[frozenset[str]] = frozenset(
    {"battle", "conquest", "treaty", "milestone"}
)


@dataclass(frozen=True)
class IslamicHistoricalEvent:
    """A recurring Hijri anniversary of a historical milestone."""

    id: str
    hijri_month: int
    hijri_day: int
    hijri_year: int
    category: str


ISLAMIC_HISTORICAL_EVENTS: Final[tuple[IslamicHistoricalEvent, ...]] = (
    IslamicHistoricalEvent("hijra", 1, 1, 1, "milestone"),
    IslamicHistoricalEvent("battle_of_badr", 9, 17, 2, "battle"),
    IslamicHistoricalEvent("battle_of_uhud", 10, 7, 3, "battle"),
    IslamicHistoricalEvent("battle_of_khandaq", 10, 5, 5, "battle"),
    IslamicHistoricalEvent("treaty_of_hudaybiyyah", 11, 1, 6, "treaty"),
    IslamicHistoricalEvent("conquest_of_khaybar", 1, 20, 7, "conquest"),
    IslamicHistoricalEvent("conquest_of_mecca", 9, 20, 8, "conquest"),
    IslamicHistoricalEvent("battle_of_hunayn", 10, 6, 8, "battle"),
    IslamicHistoricalEvent("expedition_to_tabuk", 7, 9, 9, "milestone"),
    IslamicHistoricalEvent("battle_of_yarmouk", 7, 15, 15, "battle"),
    IslamicHistoricalEvent("battle_of_qadisiyyah", 1, 16, 15, "battle"),
    IslamicHistoricalEvent("conquest_of_jerusalem", 7, 15, 17, "conquest"),
    IslamicHistoricalEvent("conquest_of_egypt", 3, 12, 21, "conquest"),
    IslamicHistoricalEvent("fall_of_constantinople", 5, 20, 857, "conquest"),
)

ALL_HISTORICAL_EVENT_IDS: Final[frozenset[str]] = frozenset(
    event.id for event in ISLAMIC_HISTORICAL_EVENTS
)


def events_by_hijri_date() -> dict[tuple[int, int], tuple[IslamicHistoricalEvent, ...]]:
    """Return historical events indexed by Hijri month and day."""
    index: dict[tuple[int, int], list[IslamicHistoricalEvent]] = {}
    for event in ISLAMIC_HISTORICAL_EVENTS:
        key = (event.hijri_month, event.hijri_day)
        index.setdefault(key, []).append(event)
    return {key: tuple(events) for key, events in index.items()}
