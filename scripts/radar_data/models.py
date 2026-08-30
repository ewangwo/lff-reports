from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SignalResult:
    signal_a: bool
    signal_b: bool
    level: str
    label: str
    reason: str

