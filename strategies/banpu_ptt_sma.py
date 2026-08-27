#!/usr/bin/env python3
"""Dual SMA (20/50) long-only backtest for BANPU and PTT.

Rules:
- Compute 20-day and 50-day simple moving averages of the adjusted close.
- A position for day t is opened when SMA20[t-1] > SMA50[t-1].
- Position is closed (flat) when SMA20[t-1] <= SMA50[t-1].
- Trading is done at the close of day t, so returns are the daily close-to-close
  return from t to t+1 while in the position.
- A 50/50 combined portfolio is rebalanced daily using the two symbol equity curves.

Inputs:
    tradecanvas-ui/data/banpu_history.json
    tradecanvas-ui/data/ptt_history.json

Output:
    tradecanvas-ui/data/banpu_ptt_sma.json
"""

import json
import os
from collections import OrderedDict
from statistics import mean


def load_symbol_json(name: str, project_root: str) -> list:
    path = os.path.join(project_root, "tradecanvas-ui", "data", f"{name}_history.json")
    with open(path) as f:
        data = json.load(f)
    recs = data["records"]
    for r in recs:
        r["_symbol"] = name.upper()
    return recs


def build_close_map(records: list) -> OrderedDict:
    records = sorted(records, key=lambda r: r["date"])
    return OrderedDict((r["date"], r) for r in records)


def sma(values: list, window: int) -> list:
    out = []
    s = 0.0
    for i, v in enumerate(values):
        s += v
        if i >= window:
            s -= values[i - window]
        if i + 1 >= window:
            out.append(s / window)
        else:
            out.append(None)
    return out


def run_symbol(dates: list, close_map: OrderedDict, fast: int = 20, slow: int = 50):
    # Build chronological arrays
    sorted_dates = list(close_map.keys())
    closes = [close_map[d]["close"] for d in sorted_dates]
    fast_sma = sma(closes, fast)
    slow_sma = sma(closes, slow)

    equity = [1.0]
    bh = [1.0]
    pos = [0]
    trades = []
    in_pos = False
    entry_price = None
    entry_date = None

    for i, d in enumerate(sorted_dates):
        if i == 0:
            continue

        # Today's signal is based on yesterday's SMAs
        prev_fast = fast_sma[i - 1]
        prev_slow = slow_sma[i - 1]
        long = (prev_fast is not None and prev_slow is not None and prev_fast > prev_slow)
        pos.append(1 if long else 0)

        # Daily return
        today_close = close_map[d]["close"]
        prev_close = close_map[sorted_dates[i - 1]]["close"]
        ret = today_close / prev_close - 1.0

        bh.append(bh[-1] * (1.0 + ret))
        equity.append(equity[-1] * (1.0 + (ret if long else 0.0)))

        # Trade accounting
        if long and not in_pos:
            in_pos = True
            entry_price = today_close
            entry_date = d
        elif not long and in_pos:
            exit_price = today_close
            pnl = exit_price - entry_price
            trades.append({
                "symbol": close_map[d]["_symbol"],
                "entry_date": entry_date,
                "entry_price": round(entry_price, 4),
                "exit_date": d,
                "exit_price": round(exit_price, 4),
                "pnl": round(pnl, 4),
            })
            in_pos = False
            entry_price = None
            entry_date = None

    # If still in position at end
    if in_pos:
        exit_price = close_map[sorted_dates[-1]]["close"]
        pnl = exit_price - entry_price
        trades.append({
            "symbol": close_map[sorted_dates[-1]]["_symbol"],
            "entry_date": entry_date,
            "entry_price": round(entry_price, 4),
            "exit_date": sorted_dates[-1],
            "exit_price": round(exit_price, 4),
            "pnl": round(pnl, 4),
        })

    series = []
    for i, d in enumerate(sorted_dates):
        if i == 0:
            continue
        series.append({
            "date": d,
            "close": close_map[d]["close"],
            "fast_sma": round(fast_sma[i], 4) if fast_sma[i] else None,
            "slow_sma": round(slow_sma[i], 4) if slow_sma[i] else None,
            "position": pos[i],
            "equity": round(equity[i], 6),
            "buyhold": round(bh[i], 6),
        })

    return {
        "series": series,
        "trades": trades,
        "final_equity": round(equity[-1], 4),
        "final_buyhold": round(bh[-1], 4),
    }


def combine_aligned(banpu_series: list, ptt_series: list, all_dates: list):
    """Build a chronological combined series where each symbol's equity is carried
    forward on days it has no data (e.g. BANPU suspension) and the combined
    portfolio is the simple average of the two."""
    by_banpu = {s["date"]: s for s in banpu_series}
    by_ptt = {s["date"]: s for s in ptt_series}

    last_b = 1.0
    last_p = 1.0
    combined = []
    for d in all_dates:
        b = by_banpu.get(d)
        p = by_ptt.get(d)
        if b:
            last_b = b["equity"]
        if p:
            last_p = p["equity"]
        combined.append({
            "date": d,
            "banpu_equity": round(last_b, 6),
            "ptt_equity": round(last_p, 6),
            "combined_equity": round((last_b + last_p) / 2.0, 6),
            "banpu_buyhold": round(last_b, 6) if not b else round(b["buyhold"], 6),
            "ptt_buyhold": round(last_p, 6) if not p else round(p["buyhold"], 6),
        })
    return combined


def max_drawdown(equity: list) -> float:
    peak = 1.0
    dd = 0.0
    for v in equity:
        if v > peak:
            peak = v
        if peak > 0:
            dd = max(dd, (peak - v) / peak)
    return dd


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    banpu = load_symbol_json("banpu", root)
    ptt = load_symbol_json("ptt", root)

    banpu_map = build_close_map(banpu)
    ptt_map = build_close_map(ptt)

    all_dates = sorted(set(banpu_map.keys()) | set(ptt_map.keys()))

    banpu_result = run_symbol(all_dates, banpu_map)
    ptt_result = run_symbol(all_dates, ptt_map)

    combined = combine_aligned(banpu_result["series"], ptt_result["series"], all_dates)

    # Compute combined stats on the aligned series
    c_equity = [c["combined_equity"] for c in combined]
    c_buyhold = [0.5 * c["banpu_buyhold"] + 0.5 * c["ptt_buyhold"] for c in combined]

    out = {
        "strategy": "dual_sma_20_50",
        "description": "Long-only 20/50 SMA cross on adjusted close. 50/50 combined portfolio.",
        "start_date": combined[0]["date"] if combined else None,
        "end_date": combined[-1]["date"] if combined else None,
        "fast_window": 20,
        "slow_window": 50,
        "symbols": ["BANPU", "PTT"],
        "combined_series": combined,
        "banpu_series": banpu_result["series"],
        "ptt_series": ptt_result["series"],
        "banpu_trades": banpu_result["trades"],
        "ptt_trades": ptt_result["trades"],
        "stats": {
            "banpu_total_return_pct": round((banpu_result["final_equity"] - 1.0) * 100, 2),
            "ptt_total_return_pct": round((ptt_result["final_equity"] - 1.0) * 100, 2),
            "combined_total_return_pct": round((c_equity[-1] - 1.0) * 100, 2),
            "banpu_buyhold_return_pct": round((banpu_result["final_buyhold"] - 1.0) * 100, 2),
            "ptt_buyhold_return_pct": round((ptt_result["final_buyhold"] - 1.0) * 100, 2),
            "combined_buyhold_return_pct": round((c_buyhold[-1] - 1.0) * 100, 2),
            "combined_max_drawdown_pct": round(max_drawdown(c_equity) * 100, 2),
            "combined_trade_count": len(banpu_result["trades"]) + len(ptt_result["trades"]),
        },
    }

    out_path = os.path.join(root, "tradecanvas-ui", "data", "banpu_ptt_sma.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("Wrote backtest results to", out_path)
    print(json.dumps(out["stats"], indent=2))


if __name__ == "__main__":
    main()
