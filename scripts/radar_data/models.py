from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SignalResult:
    signal_a: bool
    signal_b: bool
    level: str
    label: str
    reason: str


@dataclass(frozen=True)
class DailyBar:
    date: date
    close: float
    volume: float


@dataclass(frozen=True)
class EpsPoint:
    period_end: date
    available_on: date
    value: float


@dataclass(frozen=True)
class FilingEvent:
    symbol: str
    date: date
    form: str
    title: str
    category: str
    url: str
