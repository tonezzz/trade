#!/usr/bin/env python3
"""RSI-14 mean reversion backtest for BANPU and PTT.

Rules:
- Compute 14-day RSI on the adjusted close.
- Go long when RSI drops below 30 (oversold).
- Hold until RSI rises above 70 (overbought), then close the position and go flat.
- The position for day t is decided at close of day t-1 to avoid lookahead bias.
- A 50/50 combined portfolio is rebalanced daily.

Inputs:
    tradecanvas-ui/data/banpu_history.json
    tradecanvas-ui/data/ptt_history.json

Output:
    tradecanvas-ui/data/banpu_ptt_rsi.json
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


def rsi(values: list, period: int = 14) -> list:
    out = []
    for i in range(len(values)):
        if i < period:
            out.append(None)
            continue
        gains = []
        losses = []
        for j in range(i - period + 1, i + 1):
            change = values[j] - values[j - 1]
            if change > 0:
                gains.append(change)
                losses.append(0.0)
            else:
                gains.append(0.0)
                losses.append(-change)
        avg_gain = mean(gains) if gains else 0.0
        avg_loss = mean(losses) if losses else 0.0
        if avg_loss == 0:
            out.append(100.0)
        else:
            rs = avg_gain / avg_loss
            out.append(100.0 - 100.0 / (1.0 + rs))
    return out


def run_symbol(dates: list, close_map: OrderedDict, period: int = 14, oversold: float = 30.0, overbought: float = 70.0):
    sorted_dates = list(close_map.keys())
    closes = [close_map[d]["close"] for d in sorted_dates]
    rsi_vals = rsi(closes, period)

    equity = [1.0]
    bh = [1.0]
    pos = [0]
    trades = []
    in_pos = False
    entry_price = None
    entry_date = None
    target_pos = 0

    for i, d in enumerate(sorted_dates):
        if i == 0:
            continue

        prev_rsi = rsi_vals[i - 1]
        if prev_rsi is not None:
            if prev_rsi < oversold:
                target_pos = 1
            elif prev_rsi > overbought:
                target_pos = 0
            # If RSI is between oversold and overbought, keep the previous target

        long = target_pos == 1
        pos.append(1 if long else 0)

        today_close = close_map[d]["close"]
        prev_close = close_map[sorted_dates[i - 1]]["close"]
        ret = today_close / prev_close - 1.0

        bh.append(bh[-1] * (1.0 + ret))
        equity.append(equity[-1] * (1.0 + (ret if long else 0.0)))

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
            "rsi": round(rsi_vals[i], 4) if rsi_vals[i] is not None else None,
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

    c_equity = [c["combined_equity"] for c in combined]
    c_buyhold = [0.5 * c["banpu_buyhold"] + 0.5 * c["ptt_buyhold"] for c in combined]

    out = {
        "strategy": "rsi_14_mean_reversion",
        "description": "Long-only RSI-14 mean reversion (oversold 30 / overbought 70). 50/50 combined portfolio.",
        "start_date": combined[0]["date"] if combined else None,
        "end_date": combined[-1]["date"] if combined else None,
        "rsi_period": 14,
        "oversold": 30,
        "overbought": 70,
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

    out_path = os.path.join(root, "tradecanvas-ui", "data", "banpu_ptt_rsi.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("Wrote backtest results to", out_path)
    print(json.dumps(out["stats"], indent=2))


if __name__ == "__main__":
    main()
