#!/usr/bin/env python3
"""Fetch and merge historical 1D candle data from Settrade SDK.

This script reads credentials from ~/.config/devin/credentials/settrade-v2.json,
fetches 1D candles for one or two symbols (pre-event and post-event), applies an
optional swap/par adjustment, and writes a JSON file that settrade-research.html
or other UI pages can load.

Examples:
    BANPU (pre=BANPUU, post=BANPU, swap=0.38242):
        /home/tony/.venvs/settrade/bin/python scripts/settrade_v2_extract.py \
            --symbol BANPU \
            --pre BANPUU \
            --post BANPU \
            --swap 0.38242 \
            --event-date 2026-08-04

    PTT (no split):
        /home/tony/.venvs/settrade/bin/python scripts/settrade_v2_extract.py \
            --symbol PTT

    SCB (no split):
        /home/tony/.venvs/settrade/bin/python scripts/settrade_v2_extract.py \
            --symbol SCB
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta


def load_credentials(path: str = None) -> dict:
    if path is None:
        path = os.path.expanduser("~/.config/devin/credentials/settrade-v2.json")
    with open(path) as f:
        return json.load(f)


def connect(creds: dict):
    import settrade_v2
    return settrade_v2.Investor(
        app_id=creds["app_id"],
        app_secret=creds["app_secret"],
        app_code=creds["app_code"],
        broker_id=creds["broker_id"],
        is_auto_queue=False,
    )


def parse_candles(raw: dict, symbol: str, swap: float, is_pre: bool):
    """Convert SDK candlestick response into normalized records."""
    tz = timezone(timedelta(hours=7))
    n = len(raw["time"])
    factor = 1.0 / swap if is_pre and swap else 1.0
    records = []
    for i in range(n):
        date = datetime.fromtimestamp(raw["time"][i], tz=tz).date().isoformat()
        o = float(raw["open"][i])
        h = float(raw["high"][i])
        l = float(raw["low"][i])
        cl = float(raw["close"][i])
        vol = float(raw["volume"][i])
        val = float(raw["value"][i])

        pct = None
        if i > 0:
            prev = float(raw["close"][i - 1])
            if prev != 0:
                pct = round(((cl - prev) / prev) * 100, 2)

        record = {
            "date": date,
            "rawOpen": round(o, 4),
            "rawHigh": round(h, 4),
            "rawLow": round(l, 4),
            "rawClose": round(cl, 4),
            "open": round(o * factor, 4),
            "high": round(h * factor, 4),
            "low": round(l * factor, 4),
            "close": round(cl * factor, 4),
            "rawVolume": round(vol, 0),
            "volume": round(vol * swap, 0) if is_pre and swap != 1.0 else round(vol, 0),
            "value": round(val, 2),
            "percentChange": pct,
            "source": f"settrade-v2 {symbol}",
        }
        records.append(record)
    return records


def fetch_candles(market, symbol: str, limit: int = 1000):
    raw = market.get_candlestick(symbol, "1d", limit=limit)
    if not raw or not raw.get("time"):
        raise RuntimeError(f"No data returned for {symbol}")
    return raw


def main():
    parser = argparse.ArgumentParser(description="Fetch Settrade SDK 1D history")
    parser.add_argument("--symbol", required=True, help="Output / display symbol")
    parser.add_argument("--pre", help="Pre-event symbol (defaults to --symbol)")
    parser.add_argument("--post", help="Post-event symbol (defaults to --symbol)")
    parser.add_argument(
        "--swap",
        type=float,
        default=1.0,
        help="Swap ratio: number of new shares received per 1 old share",
    )
    parser.add_argument("--event-date", help="Effective date of the event (YYYY-MM-DD)")
    parser.add_argument("--event-label", help="Short label for the chart marker")
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Max candles per SDK call (max 1000)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output JSON path (default: tradecanvas-ui/data/{symbol}_history.json)",
    )
    parser.add_argument(
        "--creds",
        default=None,
        help="Path to settrade-v2 credentials JSON",
    )
    args = parser.parse_args()

    pre = args.pre or args.symbol
    post = args.post or args.symbol
    factor = 1.0 / args.swap if args.swap != 0 else 1.0

    creds = load_credentials(args.creds)
    inv = connect(creds)
    md = inv.MarketData()

    records = []
    tz = timezone(timedelta(hours=7))

    # Fetch pre
    pre_raw = fetch_candles(md, pre, args.limit)
    pre_first = datetime.fromtimestamp(pre_raw["time"][0], tz=tz).date().isoformat()
    pre_last = datetime.fromtimestamp(pre_raw["time"][-1], tz=tz).date().isoformat()
    records += parse_candles(pre_raw, pre, args.swap, is_pre=True)

    # Fetch post if different symbol
    if post != pre:
        try:
            post_raw = fetch_candles(md, post, args.limit)
            post_first = datetime.fromtimestamp(post_raw["time"][0], tz=tz).date().isoformat()
            post_last = datetime.fromtimestamp(post_raw["time"][-1], tz=tz).date().isoformat()
            records += parse_candles(post_raw, post, 1.0, is_pre=False)
            post_range = f"{post_first} to {post_last}"
        except Exception as e:
            print(f"Warning: could not fetch post data for {post}: {e}", file=sys.stderr)
            post_range = "not available"
    else:
        post_range = f"{pre_first} to {pre_last}"

    records.sort(key=lambda r: r["date"])

    # Build note
    if pre == post and args.swap == 1.0:
        note = (
            f"{args.symbol} daily OHLC from settrade-v2 {pre} 1D candles "
            f"({len(records)} sessions from {pre_first} to {pre_last}). "
            "No split/par adjustment applied."
        )
    else:
        note = (
            f"{args.symbol} history: pre-event data from settrade-v2 {pre} 1D candles "
            f"({len(parse_candles(pre_raw, pre, args.swap, is_pre=True))} sessions from {pre_first} to {pre_last}); "
            f"post-event data from settrade-v2 {post} 1D candles ({post_range}). "
            f"Pre-event prices are back-adjusted by 1/{args.swap} = {factor:.4f}; "
            f"pre-event volumes are scaled by {args.swap}. "
            f"Restructuring effective date {args.event_date}."
        )

    out = {
        "symbol": args.symbol,
        "note": note,
        "swapRatio": args.swap,
        "priceFactor": round(factor, 6),
        "volumeFactor": args.swap,
        "count": len(records),
        "records": records,
    }

    if args.event_date:
        out["eventDate"] = args.event_date
        out["eventLabel"] = args.event_label or f"{args.symbol} restructuring"

    if args.out is None:
        args.out = f"/home/tony/CascadeProjects/trade/tradecanvas-ui/data/{args.symbol.lower()}_history.json"

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(records)} records to {args.out}")
    print(f"  first: {records[0]['date']} open={records[0]['open']} close={records[0]['close']}")
    print(f"  last:  {records[-1]['date']} open={records[-1]['open']} close={records[-1]['close']}")


if __name__ == "__main__":
    main()
