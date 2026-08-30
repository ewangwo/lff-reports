from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen

from .models import DailyBar, EpsPoint, FilingEvent


MATERIAL_FORMS = {
    "10-K": "财报",
    "10-Q": "财报",
    "20-F": "财报",
    "6-K": "财报/事件",
    "8-K": "重大事件",
    "4": "内部人交易",
    "13D": "股权变化",
    "13D/A": "股权变化",
    "13G": "股权变化",
    "13G/A": "股权变化",
}

USER_AGENT = "LFF Portfolio Radar research contact ewangwo020@gmail.com"


def fetch_json(url: str, *, timeout: float = 20.0) -> dict[str, Any]:
    request = Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def fetch_yahoo_bars(symbol: str) -> list[DailyBar]:
    encoded = quote(symbol, safe="")
    payload = fetch_json(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}"
        "?range=2y&interval=1d&events=div%2Csplits"
    )
    return parse_yahoo_chart(payload)


def fetch_sec_eps(cik: str) -> list[EpsPoint]:
    payload = fetch_json(
        f"https://data.sec.gov/api/xbrl/companyfacts/CIK{str(cik).zfill(10)}.json"
    )
    return extract_quarterly_eps(payload)


def fetch_sec_events(cik: str, symbol: str) -> list[FilingEvent]:
    payload = fetch_json(
        f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
    )
    return parse_sec_submissions(payload, symbol)


def parse_yahoo_chart(payload: dict[str, Any]) -> list[DailyBar]:
    chart = payload.get("chart", {})
    if chart.get("error"):
        raise ValueError(f"Yahoo chart error: {chart['error']}")
    results = chart.get("result") or []
    if not results:
        raise ValueError("Yahoo chart returned no result")
    result = results[0]
    timestamps = result.get("timestamp") or []
    indicators = result.get("indicators") or {}
    quotes = (indicators.get("quote") or [{}])[0]
    raw_closes = quotes.get("close") or []
    volumes = quotes.get("volume") or []
    adjusted_sets = indicators.get("adjclose") or []
    closes = adjusted_sets[0].get("adjclose", raw_closes) if adjusted_sets else raw_closes

    bars: list[DailyBar] = []
    for timestamp, close, volume in zip(timestamps, closes, volumes, strict=False):
        if close is None or volume is None:
            continue
        market_date = datetime.fromtimestamp(timestamp, tz=timezone.utc).date()
        bars.append(DailyBar(market_date, float(close), float(volume)))
    if not bars:
        raise ValueError("Yahoo chart returned no complete bars")
    return bars


def extract_quarterly_eps(payload: dict[str, Any]) -> list[EpsPoint]:
    facts = payload.get("facts", {})
    concept = facts.get("us-gaap", {}).get("EarningsPerShareDiluted", {})
    units = concept.get("units", {})
    entries = units.get("USD/shares") or units.get("USD / shares") or []

    quarter_map: dict[str, EpsPoint] = {}
    annual_map: dict[str, EpsPoint] = {}
    for item in entries:
        form = item.get("form")
        frame = item.get("frame")
        if form not in {"10-Q", "10-K"} or not frame or not item.get("filed"):
            continue
        try:
            point = EpsPoint(
                period_end=datetime.strptime(item["end"], "%Y-%m-%d").date(),
                available_on=datetime.strptime(item["filed"], "%Y-%m-%d").date(),
                value=float(item["val"]),
            )
        except (KeyError, TypeError, ValueError):
            continue
        if frame.startswith("CY") and frame[-2:-1] == "Q" and frame[-1:] in "123":
            existing = quarter_map.get(frame)
            if existing is None or point.available_on < existing.available_on:
                quarter_map[frame] = point
        elif frame.startswith("CY") and frame[2:].isdigit():
            existing = annual_map.get(frame)
            if existing is None or point.available_on < existing.available_on:
                annual_map[frame] = point

    derived: list[EpsPoint] = list(quarter_map.values())
    for annual_frame, annual in annual_map.items():
        year = annual_frame[2:]
        quarters = [quarter_map.get(f"CY{year}Q{number}") for number in (1, 2, 3)]
        if not all(quarters):
            continue
        q4_value = round(
            annual.value - sum(point.value for point in quarters if point), 10
        )
        derived.append(EpsPoint(annual.period_end, annual.available_on, q4_value))

    by_period: dict[tuple[datetime.date, datetime.date], EpsPoint] = {}
    for point in derived:
        by_period[(point.period_end, point.available_on)] = point
    return sorted(by_period.values(), key=lambda point: point.period_end)


def parse_sec_submissions(payload: dict[str, Any], symbol: str) -> list[FilingEvent]:
    cik = str(payload.get("cik", "")).zfill(10)
    recent = payload.get("filings", {}).get("recent", {})
    columns = zip(
        recent.get("accessionNumber", []),
        recent.get("filingDate", []),
        recent.get("form", []),
        recent.get("primaryDocument", []),
        recent.get("primaryDocDescription", []),
        strict=False,
    )
    events: list[FilingEvent] = []
    for accession, filed, form, document, description in columns:
        category = MATERIAL_FORMS.get(form)
        if not category:
            continue
        compact_accession = accession.replace("-", "")
        url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{compact_accession}/{document}"
        events.append(
            FilingEvent(
                symbol=symbol,
                date=datetime.strptime(filed, "%Y-%m-%d").date(),
                form=form,
                title=description or form,
                category=category,
                url=url,
            )
        )
    return sorted(events, key=lambda event: event.date, reverse=True)
