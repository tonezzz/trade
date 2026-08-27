#!/usr/bin/env python3
"""RSI mean-reversion backtest for BANPU and PTT with transaction costs and stop-loss.

Parameters (taken from the parameter sweep top result):
- RSI period 14, oversold 25, overbought 65
- One-way transaction cost 0.15% (commission + slippage)
- Stop-loss at 5% below the entry close

Rules:
- Long when RSI < 25, hold until RSI > 65 or a 5% stop is hit.
- Entry is at the previous close; exit at the close or stop price.
- One-way cost is charged on both entry and exit day.

Inputs:
    tradecanvas-ui/data/banpu_history.json
    tradecanvas-ui/data/ptt_history.json

Output:
    tradecanvas-ui/data/banpu_ptt_rsi_costs.json
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


def run_symbol(close_map: OrderedDict, period: int, oversold: float, overbought: float, one_way: float, stop_pct: float):
    sorted_dates = list(close_map.keys())
    closes = [close_map[d]["close"] for d in sorted_dates]
    lows = [close_map[d]["low"] for d in sorted_dates]
    rsi_vals = rsi(closes, period)

    equity = 1.0
    bh = 1.0
    pos = 0
    trades = []
    in_pos = False
    entry_price = None
    stop_price = None
    entry_date = None
    target = 0
    equity_curve = []
    buyhold_curve = []

    for i, d in enumerate(sorted_dates):
        if i == 0:
            equity_curve.append(equity)
            buyhold_curve.append(bh)
            continue

        prev_rsi = rsi_vals[i - 1]
        if prev_rsi is not None:
            if prev_rsi < oversold:
                target = 1
            elif prev_rsi > overbought:
                target = 0

        # Check stop-loss if in position
        stopped = False
        if in_pos and lows[i] <= stop_price:
            target = 0
            stopped = True

        long = target == 1

        prev_close = closes[i - 1]
        today_close = closes[i]
        today_low = lows[i]

        # Determine the raw price move for the day
        if stopped:
            # Filled at stop; assume exit at stop price
            exit_raw = stop_price
            ret = exit_raw / prev_close - 1.0
            cost_day = one_way  # exit cost
        else:
            ret = today_close / prev_close - 1.0
            if long and not in_pos:
                cost_day = one_way  # entry cost
            elif not long and in_pos:
                cost_day = one_way  # exit cost
            else:
                cost_day = 0.0

        bh *= (1.0 + ret)

        if long:
            if not in_pos:
                # Enter at prev close
                in_pos = True
                entry_price = prev_close
                stop_price = entry_price * (1.0 - stop_pct)
                entry_date = d
            equity *= (1.0 + ret) * (1.0 - cost_day)
        else:
            if in_pos:
                # Exit
                exit_price = stop_price if stopped else today_close
                pnl = exit_price - entry_price
                trades.append({
                    "symbol": close_map[d]["_symbol"],
                    "entry_date": entry_date,
                    "entry_price": round(entry_price, 4),
                    "exit_date": d,
                    "exit_price": round(exit_price, 4),
                    "pnl": round(pnl, 4),
                    "stopped": stopped,
                })
                in_pos = False
                entry_price = None
                stop_price = None
                entry_date = None
            equity *= (1.0 + (ret if long else 0.0)) * (1.0 - cost_day)

        pos = 1 if long else 0
        equity_curve.append(equity)
        buyhold_curve.append(bh)

    # If still in position at end
    if in_pos:
        exit_price = closes[-1]
        pnl = exit_price - entry_price
        trades.append({
            "symbol": close_map[sorted_dates[-1]]["_symbol"],
            "entry_date": entry_date,
            "entry_price": round(entry_price, 4),
            "exit_date": sorted_dates[-1],
            "exit_price": round(exit_price, 4),
            "pnl": round(pnl, 4),
            "stopped": False,
        })

    series = []
    for i, d in enumerate(sorted_dates):
        if i == 0:
            continue
        series.append({
            "date": d,
            "close": close_map[d]["close"],
            "rsi": round(rsi_vals[i], 4) if rsi_vals[i] is not None else None,
            "position": pos,
            "equity": round(equity_curve[i], 6),
            "buyhold": round(buyhold_curve[i], 6),
        })

    return {
        "series": series,
        "trades": trades,
        "final_equity": round(equity_curve[-1], 4),
        "final_buyhold": round(buyhold_curve[-1], 4),
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

    period = 14
    oversold = 25
    overbought = 65
    one_way = 0.0015  # 0.15% per side (commission + slippage)
    stop_pct = 0.05   # 5% stop loss

    banpu_result = run_symbol(banpu_map, period, oversold, overbought, one_way, stop_pct)
    ptt_result = run_symbol(ptt_map, period, oversold, overbought, one_way, stop_pct)

    combined = combine_aligned(banpu_result["series"], ptt_result["series"], all_dates)

    c_equity = [c["combined_equity"] for c in combined]
    c_buyhold = [0.5 * c["banpu_buyhold"] + 0.5 * c["ptt_buyhold"] for c in combined]

    out = {
        "strategy": "rsi_14_25_65_with_costs",
        "description": f"RSI-14 mean reversion (oversold {oversold}, overbought {overbought}) with {one_way*100:.2f}% one-way cost and {stop_pct*100:.0f}% stop-loss.",
        "start_date": combined[0]["date"] if combined else None,
        "end_date": combined[-1]["date"] if combined else None,
        "rsi_period": period,
        "oversold": oversold,
        "overbought": overbought,
        "one_way_cost_pct": one_way * 100,
        "stop_loss_pct": stop_pct * 100,
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
            "stops_hit": sum(1 for t in banpu_result["trades"] + ptt_result["trades"] if t["stopped"]),
        },
    }

    out_path = os.path.join(root, "tradecanvas-ui", "data", "banpu_ptt_rsi_costs.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("Wrote cost/stop results to", out_path)
    print(json.dumps(out["stats"], indent=2))


if __name__ == "__main__":
    main()
