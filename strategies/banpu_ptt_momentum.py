#!/usr/bin/env python3
"""Dual momentum / relative-strength strategy for BANPU and PTT.

Rules:
- Compute the 20-day return (momentum) for each symbol at the close of day t-1.
- For day t, hold the symbol with the highest momentum, but only if that
  momentum is positive. If both momentums are negative, go to cash.
- Use close-to-close returns; position selection uses t-1 information only.
- If the selected symbol has no trade on a given day (e.g. BANPU suspension),
  that day's return is zero for the strategy.

Inputs:
    tradecanvas-ui/data/banpu_history.json
    tradecanvas-ui/data/ptt_history.json

Output:
    tradecanvas-ui/data/banpu_ptt_momentum.json
"""

import json
import os
from collections import OrderedDict


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


def max_drawdown(equity: list) -> float:
    peak = 1.0
    dd = 0.0
    for v in equity:
        if v > peak:
            peak = v
        if peak > 0:
            dd = max(dd, (peak - v) / peak)
    return dd


def momentum(rec_map: OrderedDict, window: int, current_date: str):
    sorted_dates = list(rec_map.keys())
    if current_date not in rec_map:
        return None
    idx = sorted_dates.index(current_date)
    if idx < window:
        return None
    prev_date = sorted_dates[idx - window]
    return rec_map[current_date]["close"] / rec_map[prev_date]["close"] - 1.0


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    banpu = load_symbol_json("banpu", root)
    ptt = load_symbol_json("ptt", root)

    banpu_map = build_close_map(banpu)
    ptt_map = build_close_map(ptt)
    all_dates = sorted(set(banpu_map.keys()) | set(ptt_map.keys()))

    momentum_window = 20

    equity = 1.0
    bh_banpu = 1.0
    bh_ptt = 1.0
    prev_b = None
    prev_p = None
    selected = None
    previous_selected = None
    switches = 0
    days_banpu = 0
    days_ptt = 0
    days_cash = 0
    series = []

    for i, d in enumerate(all_dates):
        b_rec = banpu_map.get(d)
        p_rec = ptt_map.get(d)

        # Day return for the symbol we selected at the previous close
        if i == 0:
            day_ret = 0.0
        else:
            if selected == "BANPU" and b_rec and prev_b is not None:
                day_ret = b_rec["close"] / prev_b - 1.0
            elif selected == "PTT" and p_rec and prev_p is not None:
                day_ret = p_rec["close"] / prev_p - 1.0
            else:
                day_ret = 0.0

        equity *= (1.0 + day_ret)

        # Track days in each state
        if i > 0:
            if selected == "BANPU":
                days_banpu += 1
            elif selected == "PTT":
                days_ptt += 1
            else:
                days_cash += 1

            if selected != previous_selected:
                switches += 1
            previous_selected = selected

        # Update buy/hold curves and previous closes
        if b_rec and prev_b is not None:
            bh_banpu *= (1.0 + (b_rec["close"] / prev_b - 1.0))
        if p_rec and prev_p is not None:
            bh_ptt *= (1.0 + (p_rec["close"] / prev_p - 1.0))

        if b_rec:
            prev_b = b_rec["close"]
        if p_rec:
            prev_p = p_rec["close"]

        buyhold = (bh_banpu + bh_ptt) / 2.0

        if i > 0:
            series.append({
                "date": d,
                "selected": selected,
                "equity": round(equity, 6),
                "buyhold": round(buyhold, 6),
            })

        # Select the holding for the next day based on today's momentum
        mom_b = momentum(banpu_map, momentum_window, d) if b_rec else None
        mom_p = momentum(ptt_map, momentum_window, d) if p_rec else None

        candidates = []
        if mom_b is not None:
            candidates.append(("BANPU", mom_b))
        if mom_p is not None:
            candidates.append(("PTT", mom_p))

        if candidates:
            best_symbol, best_mom = max(candidates, key=lambda x: x[1])
            selected = best_symbol if best_mom > 0 else "CASH"
        else:
            selected = "CASH"

    out = {
        "strategy": "dual_momentum_20",
        "description": "Hold the symbol with the highest 20-day momentum if it is positive; otherwise cash. Switches daily.",
        "start_date": all_dates[0],
        "end_date": all_dates[-1],
        "momentum_window": momentum_window,
        "symbols": ["BANPU", "PTT"],
        "combined_series": series,
        "stats": {
            "total_return_pct": round((equity - 1.0) * 100, 2),
            "buyhold_return_pct": round((buyhold - 1.0) * 100, 2),
            "max_drawdown_pct": round(max_drawdown([s["equity"] for s in series]) * 100, 2),
            "switches": switches,
            "days_in_banpu": days_banpu,
            "days_in_ptt": days_ptt,
            "days_in_cash": days_cash,
        },
    }

    out_path = os.path.join(root, "tradecanvas-ui", "data", "banpu_ptt_momentum.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("Wrote momentum results to", out_path)
    print(json.dumps(out["stats"], indent=2))


if __name__ == "__main__":
    main()
