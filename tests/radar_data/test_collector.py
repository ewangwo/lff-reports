from __future__ import annotations

from datetime import date, datetime, timezone

from scripts.radar_data.collector import (
    build_instrument_snapshot,
    build_pe_history,
    collect_public_snapshot,
    replace_snapshot_atomically,
)
from scripts.radar_data.models import DailyBar, EpsPoint
from scripts.radar_data.providers import (
    extract_quarterly_eps,
    parse_sec_submissions,
    parse_yahoo_chart,
)


def test_parse_yahoo_chart_uses_adjusted_close_and_skips_empty_rows():
    payload = {
        "chart": {
            "result": [
                {
                    "meta": {"currency": "USD", "exchangeTimezoneName": "America/New_York"},
                    "timestamp": [1_700_000_000, 1_700_086_400, 1_700_172_800],
                    "indicators": {
                        "quote": [
                            {
                                "close": [100.0, None, 103.0],
                                "volume": [1_000, None, 1_300],
                            }
                        ],
                        "adjclose": [{"adjclose": [99.0, None, 102.0]}],
                    },
                }
            ],
            "error": None,
        }
    }

    bars = parse_yahoo_chart(payload)

    assert [bar.close for bar in bars] == [99.0, 102.0]
    assert [bar.volume for bar in bars] == [1_000.0, 1_300.0]


def test_extract_quarterly_eps_derives_q4_from_annual_without_future_dates():
    payload = {
        "facts": {
            "us-gaap": {
                "EarningsPerShareDiluted": {
                    "units": {
                        "USD/shares": [
                            _eps_fact("2025-03-31", 1.0, "CY2025Q1", "2025-05-01", "10-Q"),
                            _eps_fact("2025-06-30", 1.2, "CY2025Q2", "2025-08-01", "10-Q"),
                            _eps_fact("2025-09-30", 1.4, "CY2025Q3", "2025-11-01", "10-Q"),
                            _eps_fact("2025-12-31", 5.2, "CY2025", "2026-02-01", "10-K"),
                        ]
                    }
                }
            }
        }
    }

    points = extract_quarterly_eps(payload)

    assert [point.value for point in points] == [1.0, 1.2, 1.4, 1.6]
    assert points[-1].available_on == date(2026, 2, 1)


def test_pe_history_only_uses_eps_available_on_each_market_date():
    bars = [
        DailyBar(date=date(2026, 1, 31), close=100.0, volume=1_000),
        DailyBar(date=date(2026, 2, 2), close=110.0, volume=1_100),
    ]
    points = [
        EpsPoint(date(2025, 3, 31), date(2025, 5, 1), 1.0),
        EpsPoint(date(2025, 6, 30), date(2025, 8, 1), 1.0),
        EpsPoint(date(2025, 9, 30), date(2025, 11, 1), 1.0),
        EpsPoint(date(2025, 12, 31), date(2026, 2, 1), 2.0),
    ]

    history = build_pe_history(bars, points)

    assert history == [(date(2026, 2, 2), 22.0)]


def test_sec_submission_parser_keeps_material_forms_and_links():
    payload = {
        "cik": "0000000123",
        "filings": {
            "recent": {
                "accessionNumber": ["0000000123-26-000001", "0000000123-26-000002"],
                "filingDate": ["2026-08-29", "2026-08-28"],
                "reportDate": ["2026-08-28", "2026-08-27"],
                "form": ["8-K", "S-8"],
                "primaryDocument": ["event.htm", "plan.htm"],
                "primaryDocDescription": ["Current report", "Employee plan"],
            }
        },
    }

    events = parse_sec_submissions(payload, "TEST")

    assert len(events) == 1
    assert events[0].form == "8-K"
    assert events[0].url.endswith("/event.htm")


def test_snapshot_classifies_etf_without_pe_signal():
    bars = [
        DailyBar(date=date(2025, 1, 1), close=float(index), volume=100.0)
        for index in range(1, 221)
    ]

    snapshot = build_instrument_snapshot(
        symbol="QQQ",
        name="Invesco QQQ",
        security_type="etf",
        bars=bars,
        eps_points=[],
        events=[],
        generated_at=datetime(2026, 8, 30, tzinfo=timezone.utc),
    )

    assert snapshot["ttmPe"] is None
    assert snapshot["pePercentile2y"] is None
    assert snapshot["signal"]["level"] == "unknown"


def test_atomic_snapshot_replace_does_not_leave_partial_file(tmp_path):
    target = tmp_path / "snapshot.json"

    replace_snapshot_atomically(target, {"schemaVersion": 1, "ok": True})

    assert target.read_text(encoding="utf-8").endswith("\n")
    assert not list(tmp_path.glob("*.tmp"))


def test_collection_records_partial_provider_failures_without_private_data():
    bars = [
        DailyBar(date=date(2025, 1, 1), close=float(index), volume=100.0)
        for index in range(1, 221)
    ]

    def market_provider(symbol: str):
        if symbol == "FAIL":
            raise RuntimeError("upstream unavailable")
        return bars

    snapshot = collect_public_snapshot(
        universe=[
            {"symbol": "OK", "name": "Okay Corp", "securityType": "stock", "cik": None},
            {"symbol": "FAIL", "name": "Failed Corp", "securityType": "stock", "cik": None},
        ],
        market_provider=market_provider,
        eps_provider=lambda _cik: [],
        event_provider=lambda _cik, _symbol: [],
        generated_at=datetime(2026, 8, 30, tzinfo=timezone.utc),
    )

    assert [item["symbol"] for item in snapshot["instruments"]] == ["OK"]
    assert snapshot["dataHealth"]["status"] == "partial"
    assert snapshot["dataHealth"]["errors"][0]["symbol"] == "FAIL"
    serialized = str(snapshot)
    assert "account" not in serialized.lower()
    assert "position" not in serialized.lower()


def _eps_fact(end: str, value: float, frame: str, filed: str, form: str) -> dict:
    return {
        "start": end[:4] + "-01-01",
        "end": end,
        "val": value,
        "frame": frame,
        "filed": filed,
        "form": form,
    }
