#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from radar_data.collector import collect_public_snapshot, replace_snapshot_atomically
from radar_data.providers import fetch_sec_eps, fetch_sec_events, fetch_yahoo_bars
from radar_data.universe import PUBLIC_UNIVERSE


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh the public-safe radar snapshot")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/ibkr-radar/public-snapshot.json"),
    )
    parser.add_argument(
        "--symbols",
        help="Comma-separated public-universe subset for bounded smoke runs",
    )
    args = parser.parse_args()
    selected = PUBLIC_UNIVERSE
    if args.symbols:
        wanted = {symbol.strip().upper() for symbol in args.symbols.split(",")}
        selected = [item for item in PUBLIC_UNIVERSE if item["symbol"] in wanted]

    snapshot = collect_public_snapshot(
        universe=selected,
        market_provider=fetch_yahoo_bars,
        eps_provider=fetch_sec_eps,
        event_provider=fetch_sec_events,
        generated_at=datetime.now(timezone.utc),
    )
    if not snapshot["instruments"]:
        print("No complete instruments were collected; existing snapshot retained")
        for error in snapshot["dataHealth"]["errors"]:
            print(f"- {error['symbol']}: {error['message']}")
        return 1
    replace_snapshot_atomically(args.output, snapshot)
    print(
        f"Wrote {len(snapshot['instruments'])} instruments to {args.output}; "
        f"status={snapshot['dataHealth']['status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
