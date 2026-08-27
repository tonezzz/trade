#!/usr/bin/env python3
"""Causality / lead-lag between BANPU/PTT and gold (XAU), USD/THB, THB gold.

Tests both directions:
- Does XAU/USD, USD/THB, or XAU/THB lead BANPU or PTT?
- Does BANPU or PTT lead XAU/USD, USD/THB, or XAU/THB?

Inputs:
    /home/tony/CascadeProjects/chaba/experiments/gold-thb-usd-causality/data/aligned_usd.csv
    tradecanvas-ui/data/banpu_history.json
    tradecanvas-ui/data/ptt_history.json

Output:
    tradecanvas-ui/data/banpu_ptt_gold_causality.json
"""

import csv
import json
import os
import sys

# Reuse the stats helpers from the BANPU/PTT causality script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import banpu_ptt_causality as bc


def load_csv_series(path: str):
    """Read aligned_usd.csv and return dicts: date -> value."""
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = sorted(reader, key=lambda r: r["date"])
    xau = {}
    thb = {}
    usd = {}
    for r in rows:
        d = r["date"]
        xau[d] = float(r["xau"])
        thb[d] = float(r["thb"])
        usd[d] = float(r["usd"])
    return xau, thb, usd


def load_json_series(name: str, project_root: str):
    path = os.path.join(project_root, "tradecanvas-ui", "data", f"{name}_history.json")
    with open(path) as f:
        data = json.load(f)
    recs = sorted(data["records"], key=lambda r: r["date"])
    return {r["date"]: float(r["close"]) for r in recs}


def returns_from_aligned(values: list):
    return [values[i] / values[i - 1] - 1.0 for i in range(1, len(values))]


def align_series(a: dict, b: dict):
    common = sorted(set(a.keys()) & set(b.keys()))
    return returns_from_aligned([a[d] for d in common]), returns_from_aligned([b[d] for d in common]), common


def pair_test(a_name: str, a: dict, b_name: str, b: dict, max_lag: int = 10):
    ra, rb, dates = align_series(a, b)
    n = len(ra)
    if n < 2:
        return None

    cross = bc.cross_correlation(ra, rb, max_lag=max_lag)
    # positive lag = a leads b; negative lag = b leads a
    pos = [c for c in cross if c["lag"] > 0]
    neg = [c for c in cross if c["lag"] < 0]
    best_a_leads_b = max(pos, key=lambda c: abs(c["correlation"])) if pos else None
    best_b_leads_a = max(neg, key=lambda c: abs(c["correlation"])) if neg else None
    strongest = max(cross, key=lambda c: abs(c["correlation"]))

    # Granger-like: a -> b
    g_a_b = bc.granger_test(rb[1:], rb[:-1], ra[:-1], f"{a_name}(t-1) -> {b_name}(t)")
    # b -> a
    g_b_a = bc.granger_test(ra[1:], ra[:-1], rb[:-1], f"{b_name}(t-1) -> {a_name}(t)")

    return {
        "pair": f"{a_name} vs {b_name}",
        "n_observations": n,
        "cross_correlations": cross,
        "best_a_leads_b": best_a_leads_b,
        "best_b_leads_a": best_b_leads_a,
        "strongest_overall": strongest,
        "granger_a_to_b": g_a_b,
        "granger_b_to_a": g_b_a,
    }


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chaba_data = "/home/tony/CascadeProjects/chaba/experiments/gold-thb-usd-causality/data/aligned_usd.csv"

    xau, thb, usd = load_csv_series(chaba_data)
    banpu = load_json_series("banpu", root)
    ptt = load_json_series("ptt", root)

    factors = {"XAU/USD": xau, "XAU/THB": thb, "USD/THB": usd}
    stocks = {"BANPU": banpu, "PTT": ptt}

    results = []
    for f_name, f in factors.items():
        for s_name, s in stocks.items():
            # f -> s
            r = pair_test(f_name, f, s_name, s)
            if r:
                results.append(r)

    # Also test XAU/USD vs USD/THB themselves for context
    results.append(pair_test("XAU/USD", xau, "USD/THB", usd))
    results.append(pair_test("XAU/THB", thb, "USD/THB", usd))

    # Build a concise summary table
    summary = []
    for r in results:
        if r is None:
            continue
        a, b = r["pair"].split(" vs ")
        summary.append({
            "from": a,
            "to": b,
            "n": r["n_observations"],
            "best_lag": r["best_a_leads_b"]["lag"] if r["best_a_leads_b"] else None,
            "best_corr": r["best_a_leads_b"]["correlation"] if r["best_a_leads_b"] else None,
            "granger_improvement": r["granger_a_to_b"]["improvement"],
            "granger_f": r["granger_a_to_b"]["f_score"],
        })
        summary.append({
            "from": b,
            "to": a,
            "n": r["n_observations"],
            "best_lag": r["best_b_leads_a"]["lag"] if r["best_b_leads_a"] else None,
            "best_corr": r["best_b_leads_a"]["correlation"] if r["best_b_leads_a"] else None,
            "granger_improvement": r["granger_b_to_a"]["improvement"],
            "granger_f": r["granger_b_to_a"]["f_score"],
        })

    out = {
        "analysis": "cross_asset_causality",
        "factors": ["XAU/USD", "XAU/THB", "USD/THB"],
        "stocks": ["BANPU", "PTT"],
        "summary": summary,
        "results": results,
    }

    out_path = os.path.join(root, "tradecanvas-ui", "data", "banpu_ptt_gold_causality.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("Wrote cross-asset causality results to", out_path)
    for s in summary:
        print(f"{s['from']:12} -> {s['to']:8}  lag={str(s['best_lag']):>4}  corr={s['best_corr']:>7}  granger={s['granger_improvement']:.4f}")


if __name__ == "__main__":
    main()
