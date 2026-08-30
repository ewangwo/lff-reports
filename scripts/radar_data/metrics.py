from __future__ import annotations

from collections.abc import Iterable, Sequence
from math import isfinite

from .models import SignalResult


def _valid_numbers(values: Iterable[float | None]) -> list[float]:
    return [float(value) for value in values if value is not None and isfinite(value)]


def simple_moving_average(
    values: Sequence[float | None], window: int
) -> float | None:
    if window <= 0:
        raise ValueError("window must be positive")
    valid = _valid_numbers(values)
    if len(valid) < window:
        return None
    return sum(valid[-window:]) / window


def percentile_rank(
    values: Sequence[float | None], current: float | None, *, min_samples: int
) -> float | None:
    if current is None or not isfinite(current):
        return None
    valid = _valid_numbers(values)
    if len(valid) < min_samples:
        return None
    return 100.0 * sum(value <= current for value in valid) / len(valid)


def relative_volume(
    current_volume: float | None,
    prior_volumes: Sequence[float | None],
    window: int = 20,
) -> float | None:
    if current_volume is None or current_volume < 0:
        return None
    baseline = simple_moving_average(prior_volumes, window)
    if baseline is None or baseline <= 0:
        return None
    return current_volume / baseline


def compute_pe(
    price: float | None, ttm_eps: float | None, security_type: str
) -> float | None:
    if security_type.lower() != "stock":
        return None
    if price is None or ttm_eps is None or price <= 0 or ttm_eps <= 0:
        return None
    return price / ttm_eps


def classify_signal(
    *,
    price: float | None,
    sma200: float | None,
    price_percentile: float | None,
    pe_percentile: float | None,
    stale: bool = False,
    threshold: float = 10.0,
) -> SignalResult:
    required = (price, sma200, price_percentile, pe_percentile)
    if stale or any(value is None or not isfinite(value) for value in required):
        return SignalResult(
            signal_a=False,
            signal_b=False,
            level="unknown",
            label="数据不足",
            reason="数据缺失或已过期，不能形成组合判断",
        )

    signal_a = bool(price < sma200)
    signal_b = bool(
        price_percentile <= threshold and pe_percentile <= threshold
    )
    if signal_a and signal_b:
        return SignalResult(
            signal_a=True,
            signal_b=True,
            level="review",
            label="人工复核",
            reason="低于200日均线，且价格与TTM PE均位于两年低10%区域",
        )
    if signal_a or signal_b:
        return SignalResult(
            signal_a=signal_a,
            signal_b=signal_b,
            level="watch",
            label="观察",
            reason="仅有部分条件成立",
        )
    return SignalResult(
        signal_a=False,
        signal_b=False,
        level="normal",
        label="正常",
        reason="核心人工复核条件未触发",
    )
