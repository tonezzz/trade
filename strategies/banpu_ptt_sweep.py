#!/usr/bin/env python3
"""Parameter sweep for BANPU + PTT long-only strategies.

Sweeps:
- SMA cross: fast window 5..30, slow window fast+10..100
- RSI mean reversion: period 7,14,21, oversold 20,25,30, overbought 65,70,75

Evaluates each config on the adjusted close of BANPU and PTT (50/50) and
reports the best by total return and best by risk-adjusted return
(return / max drawdown).

Output: tradecanvas-ui/data/banpu_ptt_sweep.json
"""

import json
import os
from collections import OrderedDict
from itertools import product
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


def rsi(values: list, period: int) -> list:
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


def max_drawdown(equity: list) -> float:
    peak = 1.0
    dd = 0.0
    for v in equity:
        if v > peak:
            peak = v
        if peak > 0:
            dd = max(dd, (peak - v) / peak)
    return dd


def run_sma(close_map: OrderedDict, fast: int, slow: int):
    sorted_dates = list(close_map.keys())
    closes = [close_map[d]["close"] for d in sorted_dates]
    fast_sma = sma(closes, fast)
    slow_sma = sma(closes, slow)

    equity = [1.0]
    pos = [0]
    for i, d in enumerate(sorted_dates):
        if i == 0:
            continue
        prev_fast = fast_sma[i - 1]
        prev_slow = slow_sma[i - 1]
        long = prev_fast is not None and prev_slow is not None and prev_fast > prev_slow
        pos.append(1 if long else 0)

        today = close_map[d]["close"]
        prev = close_map[sorted_dates[i - 1]]["close"]
        ret = today / prev - 1.0
        equity.append(equity[-1] * (1.0 + (ret if long else 0.0)))

    return equity[-1], max_drawdown(equity)


def run_rsi(close_map: OrderedDict, period: int, oversold: float, overbought: float):
    sorted_dates = list(close_map.keys())
    closes = [close_map[d]["close"] for d in sorted_dates]
    rsi_vals = rsi(closes, period)

    equity = [1.0]
    pos = [0]
    target = 0
    for i, d in enumerate(sorted_dates):
        if i == 0:
            continue
        prev_rsi = rsi_vals[i - 1]
        if prev_rsi is not None:
            if prev_rsi < oversold:
                target = 1
            elif prev_rsi > overbought:
                target = 0

        long = target == 1
        pos.append(1 if long else 0)

        today = close_map[d]["close"]
        prev = close_map[sorted_dates[i - 1]]["close"]
        ret = today / prev - 1.0
        equity.append(equity[-1] * (1.0 + (ret if long else 0.0)))

    return equity[-1], max_drawdown(equity)


def combine_symbol_results(banpu_equity, ptt_equity, all_dates, banpu_map, ptt_map):
    by_banpu = {d: banpu_equity[d] for d in banpu_map}
    by_ptt = {d: ptt_equity[d] for d in ptt_map}

    last_b = 1.0
    last_p = 1.0
    combined = []
    for d in all_dates:
        if d in by_banpu:
            last_b = by_banpu[d]
        if d in by_ptt:
            last_p = by_ptt[d]
        combined.append((last_b + last_p) / 2.0)
    return combined


def run_combined_sma(banpu_map, ptt_map, all_dates, fast, slow):
    banpu_eq = []
    ptt_eq = []
    sorted_banpu = list(banpu_map.keys())
    sorted_ptt = list(ptt_map.keys())
    banpu_final, _ = run_sma(banpu_map, fast, slow)
    ptt_final, _ = run_sma(ptt_map, fast, slow)

    # Not enough info for proper date alignment here; use the simple approach
    # where each symbol is run independently and the combined equity is the
    # average of the two final values (approximate).
    return (banpu_final + ptt_final) / 2.0, 0.0


def run_strategy(banpu_map: OrderedDict, ptt_map: OrderedDict, all_dates: list, kind: str, params: dict):
    if kind == "sma":
        banpu_final, banpu_dd = run_sma(banpu_map, params["fast"], params["slow"])
        ptt_final, ptt_dd = run_sma(ptt_map, params["fast"], params["slow"])
    else:
        banpu_final, banpu_dd = run_rsi(banpu_map, params["period"], params["oversold"], params["overbought"])
        ptt_final, ptt_dd = run_rsi(ptt_map, params["period"], params["oversold"], params["overbought"])

    combined_final = (banpu_final + ptt_final) / 2.0
    combined_dd = (banpu_dd + ptt_dd) / 2.0
    total_return = (combined_final - 1.0) * 100
    risk_adj = total_return / (combined_dd * 100) if combined_dd > 0 else float('inf') if total_return > 0 else float('-inf')
    return {
        "kind": kind,
        "params": params,
        "banpu_final": round(banpu_final, 4),
        "ptt_final": round(ptt_final, 4),
        "combined_final": round(combined_final, 4),
        "banpu_max_dd_pct": round(banpu_dd * 100, 2),
        "ptt_max_dd_pct": round(ptt_dd * 100, 2),
        "combined_max_dd_pct": round(combined_dd * 100, 2),
        "total_return_pct": round(total_return, 2),
        "risk_adjusted": round(risk_adj, 4) if risk_adj != float('inf') and risk_adj != float('-inf') else None,
    }


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    banpu = load_symbol_json("banpu", root)
    ptt = load_symbol_json("ptt", root)
    banpu_map = build_close_map(banpu)
    ptt_map = build_close_map(ptt)
    all_dates = sorted(set(banpu_map.keys()) | set(ptt_map.keys()))

    results = []

    # SMA sweep
    for fast, slow in product(range(5, 31, 5), range(20, 101, 10)):
        if fast >= slow:
            continue
        r = run_strategy(banpu_map, ptt_map, all_dates, "sma", {"fast": fast, "slow": slow})
        results.append(r)

    # RSI sweep
    for period, oversold, overbought in product([7, 14, 21], [20, 25, 30], [65, 70, 75]):
        r = run_strategy(banpu_map, ptt_map, all_dates, "rsi", {"period": period, "oversold": oversold, "overbought": overbought})
        results.append(r)

    # Sort by return and by risk-adjusted
    by_return = sorted(results, key=lambda x: x["total_return_pct"], reverse=True)[:10]
    by_risk = [r for r in sorted(results, key=lambda x: (x["risk_adjusted"] if x["risk_adjusted"] is not None else -1e9), reverse=True)[:10] if r["risk_adjusted"] is not None]

    out = {
        "total_runs": len(results),
        "start_date": all_dates[0],
        "end_date": all_dates[-1],
        "symbols": ["BANPU", "PTT"],
        "top_by_return": by_return,
        "top_by_risk_adjusted": by_risk,
        "all_results": results,
    }

    out_path = os.path.join(root, "tradecanvas-ui", "data", "banpu_ptt_sweep.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("Wrote sweep results to", out_path)
    print("Runs:", len(results))
    print("Top by return:")
    print(json.dumps(by_return[:3], indent=2))


if __name__ == "__main__":
    main()
