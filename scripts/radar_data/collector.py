from __future__ import annotations

import json
import os
from datetime import date, datetime
from pathlib import Path
from collections.abc import Callable
from typing import Any, Sequence

from .metrics import (
    classify_signal,
    compute_pe,
    percentile_rank,
    relative_volume,
    simple_moving_average,
)
from .models import DailyBar, EpsPoint, FilingEvent


def _ttm_eps_as_of(points: Sequence[EpsPoint], market_date: date) -> float | None:
    available = [point for point in points if point.available_on <= market_date]
    if len(available) < 4:
        return None
    latest_by_period: dict[date, EpsPoint] = {}
    for point in available:
        existing = latest_by_period.get(point.period_end)
        if existing is None or point.available_on < existing.available_on:
            latest_by_period[point.period_end] = point
    ordered = sorted(latest_by_period.values(), key=lambda point: point.period_end)
    if len(ordered) < 4:
        return None
    return sum(point.value for point in ordered[-4:])


def build_pe_history(
    bars: Sequence[DailyBar], eps_points: Sequence[EpsPoint]
) -> list[tuple[date, float]]:
    history: list[tuple[date, float]] = []
    for bar in bars:
        ttm_eps = _ttm_eps_as_of(eps_points, bar.date)
        pe = compute_pe(bar.close, ttm_eps, "stock")
        if pe is not None:
            history.append((bar.date, pe))
    return history


def build_instrument_snapshot(
    *,
    symbol: str,
    name: str,
    security_type: str,
    bars: Sequence[DailyBar],
    eps_points: Sequence[EpsPoint],
    events: Sequence[FilingEvent],
    generated_at: datetime,
) -> dict[str, Any]:
    if not bars:
        raise ValueError(f"{symbol} has no complete market bars")
    closes = [bar.close for bar in bars[-504:]]
    latest = bars[-1]
    sma200 = simple_moving_average(closes, 200)
    price_percentile = percentile_rank(closes, latest.close, min_samples=200)
    rel_volume = relative_volume(
        latest.volume,
        [bar.volume for bar in bars[:-1]],
        window=20,
    )
    pe_history = (
        build_pe_history(bars[-504:], eps_points)
        if security_type.lower() == "stock"
        else []
    )
    ttm_eps = _ttm_eps_as_of(eps_points, latest.date)
    ttm_pe = compute_pe(latest.close, ttm_eps, security_type)
    pe_percentile = percentile_rank(
        [value for _, value in pe_history],
        ttm_pe,
        min_samples=60,
    )
    signal = classify_signal(
        price=latest.close,
        sma200=sma200,
        price_percentile=price_percentile,
        pe_percentile=pe_percentile,
    )
    return {
        "symbol": symbol,
        "name": name,
        "securityType": security_type,
        "price": round(latest.close, 4),
        "priceDate": latest.date.isoformat(),
        "sma200": round(sma200, 4) if sma200 is not None else None,
        "distanceToSma200": (
            round(latest.close / sma200 - 1, 6) if sma200 else None
        ),
        "pricePercentile2y": (
            round(price_percentile, 2) if price_percentile is not None else None
        ),
        "ttmEps": round(ttm_eps, 4) if ttm_eps is not None else None,
        "ttmPe": round(ttm_pe, 2) if ttm_pe is not None else None,
        "pePercentile2y": (
            round(pe_percentile, 2) if pe_percentile is not None else None
        ),
        "relativeVolume20d": round(rel_volume, 2) if rel_volume is not None else None,
        "signal": {
            "a": signal.signal_a,
            "b": signal.signal_b,
            "level": signal.level,
            "label": signal.label,
            "reason": signal.reason,
        },
        "events": [
            {
                "date": event.date.isoformat(),
                "form": event.form,
                "title": event.title,
                "category": event.category,
                "url": event.url,
            }
            for event in events[:5]
        ],
        "series": {
            "dates": [bar.date.isoformat() for bar in bars[-504:]],
            "prices": [round(bar.close, 4) for bar in bars[-504:]],
            "volumes": [round(bar.volume, 2) for bar in bars[-504:]],
            "pe": [
                {"date": point_date.isoformat(), "value": round(value, 2)}
                for point_date, value in pe_history
            ],
        },
        "generatedAt": generated_at.isoformat(),
    }


def replace_snapshot_atomically(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def collect_public_snapshot(
    *,
    universe: Sequence[dict[str, Any]],
    market_provider: Callable[[str], list[DailyBar]],
    eps_provider: Callable[[str], list[EpsPoint]],
    event_provider: Callable[[str, str], list[FilingEvent]],
    generated_at: datetime,
) -> dict[str, Any]:
    instruments: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for item in universe:
        symbol = str(item["symbol"])
        try:
            bars = market_provider(symbol)
            cik = item.get("cik")
            eps_points = eps_provider(str(cik)) if cik else []
            events = event_provider(str(cik), symbol) if cik else []
            instruments.append(
                build_instrument_snapshot(
                    symbol=symbol,
                    name=str(item["name"]),
                    security_type=str(item["securityType"]),
                    bars=bars,
                    eps_points=eps_points,
                    events=events,
                    generated_at=generated_at,
                )
            )
        except Exception as error:  # provider boundaries are intentionally isolated
            errors.append(
                {
                    "symbol": symbol,
                    "source": "public market / SEC",
                    "message": f"{type(error).__name__}: {error}",
                }
            )

    all_events = sorted(
        (
            {"symbol": item["symbol"], **event}
            for item in instruments
            for event in item["events"]
        ),
        key=lambda event: event["date"],
        reverse=True,
    )
    status = "ok" if not errors else ("partial" if instruments else "failed")
    return {
        "schemaVersion": 1,
        "mode": "public_safe",
        "generatedAt": generated_at.isoformat(),
        "instruments": instruments,
        "events": all_events[:30],
        "dataHealth": {
            "status": status,
            "sources": [
                {
                    "name": "Yahoo Chart",
                    "role": "价格与成交量",
                    "asOf": generated_at.isoformat(),
                },
                {
                    "name": "SEC EDGAR",
                    "role": "财务与监管事件",
                    "asOf": generated_at.isoformat(),
                },
            ],
            "errors": errors,
        },
    }
