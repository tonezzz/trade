#!/usr/bin/env python3
"""Causality / lead-lag analysis between BANPU and PTT daily returns.

Methods:
- Cross-correlation of daily returns for lags -10 to +10.
- Simple Granger-like predictive regressions:
  Does PTT_t improve when adding BANPU_{t-1} to PTT_{t-1}?
  Does BANPU_t improve when adding PTT_{t-1} to BANPU_{t-1}?

Inputs:
    tradecanvas-ui/data/banpu_history.json
    tradecanvas-ui/data/ptt_history.json

Output:
    tradecanvas-ui/data/banpu_ptt_causality.json
"""

import json
import math
import os
from collections import OrderedDict


def load_symbol_json(name: str, project_root: str) -> list:
    path = os.path.join(project_root, "tradecanvas-ui", "data", f"{name}_history.json")
    with open(path) as f:
        data = json.load(f)
    return sorted(data["records"], key=lambda r: r["date"])


def build_close_map(records: list) -> OrderedDict:
    return OrderedDict((r["date"], r) for r in records)


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def pearson(xs, ys):
    n = len(xs)
    if n == 0:
        return 0.0
    mx = mean(xs)
    my = mean(ys)
    num = 0.0
    dxx = 0.0
    dyy = 0.0
    for x, y in zip(xs, ys):
        dx = x - mx
        dy = y - my
        num += dx * dy
        dxx += dx * dx
        dyy += dy * dy
    if dxx == 0 or dyy == 0:
        return 0.0
    return num / math.sqrt(dxx * dyy)


def cross_correlation(x, y, max_lag=10):
    """Return cross-correlations for lags -max_lag..+max_lag.
    Positive lag means x leads y: corr(x[t-lag], y[t]).
    """
    n = len(x)
    out = []
    for lag in range(-max_lag, max_lag + 1):
        if lag >= 0:
            # x leads by lag: x[0:n-lag] vs y[lag:n]
            xi = x[: n - lag]
            yi = y[lag:]
        else:
            # y leads by |lag|: x[-lag:n] vs y[0:n+lag]
            xi = x[-lag:]
            yi = y[: n + lag]
        out.append({"lag": lag, "correlation": round(pearson(xi, yi), 4)})
    return out


def ols1(x, y):
    """y = b0 + b1*x. Returns coefficients and fitted values."""
    mx = mean(x)
    my = mean(y)
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    var = sum((xi - mx) ** 2 for xi in x)
    if var == 0:
        return 0.0, 0.0, [my] * len(y)
    b1 = cov / var
    b0 = my - b1 * mx
    yhat = [b0 + b1 * xi for xi in x]
    return b0, b1, yhat


def ols2(x1, x2, y):
    """y = b0 + b1*x1 + b2*x2. Returns coefficients and fitted values."""
    n = len(y)
    m1 = mean(x1)
    m2 = mean(x2)
    my = mean(y)

    c1y = sum((a - m1) * (b - my) for a, b in zip(x1, y))
    c2y = sum((a - m2) * (b - my) for a, b in zip(x2, y))
    c12 = sum((a - m1) * (b - m2) for a, b in zip(x1, x2))
    v1 = sum((a - m1) ** 2 for a in x1)
    v2 = sum((a - m2) ** 2 for a in x2)

    denom = v1 * v2 - c12 ** 2
    if denom == 0:
        b1, b2 = 0.0, 0.0
    else:
        b1 = (c1y * v2 - c2y * c12) / denom
        b2 = (v1 * c2y - c1y * c12) / denom
    b0 = my - b1 * m1 - b2 * m2

    yhat = [b0 + b1 * a + b2 * b for a, b in zip(x1, x2)]
    return b0, b1, b2, yhat


def r2(y, yhat):
    my = mean(y)
    ss_tot = sum((yi - my) ** 2 for yi in y)
    ss_res = sum((yi - yh) ** 2 for yi, yh in zip(y, yhat))
    if ss_tot == 0:
        return 0.0
    return 1.0 - ss_res / ss_tot


def granger_test(y, y_lag, x_lag, label):
    _, _, yhat_base = ols1(y_lag, y)
    r2_base = r2(y, yhat_base)
    _, _, _, yhat_full = ols2(y_lag, x_lag, y)
    r2_full = r2(y, yhat_full)
    improvement = r2_full - r2_base
    n = len(y)
    # Simple F-like improvement measure: (R2_full - R2_base) / (1 - R2_full) * (n - 3)
    # This is not the exact F-stat but gives a scaled improvement score.
    if 1 - r2_full < 1e-12:
        f_score = 0.0
    else:
        f_score = (improvement / (1 - r2_full)) * (n - 3)
    return {
        "direction": label,
        "r2_baseline": round(r2_base, 4),
        "r2_with_lag": round(r2_full, 4),
        "improvement": round(improvement, 4),
        "f_score": round(f_score, 4),
        "n": n,
    }


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    banpu = build_close_map(load_symbol_json("banpu", root))
    ptt = build_close_map(load_symbol_json("ptt", root))

    all_dates = sorted(set(banpu.keys()) & set(ptt.keys()))

    banpu_closes = [banpu[d]["close"] for d in all_dates]
    ptt_closes = [ptt[d]["close"] for d in all_dates]

    banpu_ret = [banpu_closes[i] / banpu_closes[i - 1] - 1.0 for i in range(1, len(banpu_closes))]
    ptt_ret = [ptt_closes[i] / ptt_closes[i - 1] - 1.0 for i in range(1, len(ptt_closes))]

    # Cross-correlation: positive lag = BANPU leads PTT
    cross = cross_correlation(banpu_ret, ptt_ret, max_lag=10)

    # Granger-like tests
    y_ptt = ptt_ret[1:]
    ptt_lag = ptt_ret[:-1]
    banpu_lag = banpu_ret[:-1]

    y_banpu = banpu_ret[1:]

    granger_banpu_to_ptt = granger_test(y_ptt, ptt_lag, banpu_lag, "BANPU(t-1) -> PTT(t)")
    granger_ptt_to_banpu = granger_test(y_banpu, banpu_lag, ptt_lag, "PTT(t-1) -> BANPU(t)")

    # Find strongest leading correlation
    max_lead = max(cross, key=lambda c: c["lag"] > 0, default=None)
    # Better: find max abs correlation with positive lag
    pos_corrs = [c for c in cross if c["lag"] > 0]
    neg_corrs = [c for c in cross if c["lag"] < 0]
    best_banpu_lead = max(pos_corrs, key=lambda c: abs(c["correlation"]), default=None)
    best_ptt_lead = max(neg_corrs, key=lambda c: abs(c["correlation"]), default=None)

    strongest = max(cross, key=lambda c: abs(c["correlation"]))

    out = {
        "analysis": "lead_lag_cross_correlation",
        "start_date": all_dates[1],
        "end_date": all_dates[-1],
        "n_observations": len(banpu_ret),
        "cross_correlations": cross,
        "granger_like": [granger_banpu_to_ptt, granger_ptt_to_banpu],
        "summary": {
            "strongest_overall_lag": strongest["lag"],
            "strongest_overall_correlation": strongest["correlation"],
            "best_banpu_leads_ptt": best_banpu_lead,
            "best_ptt_leads_banpu": best_ptt_lead,
            "conclusion": "BANPU appears to lead PTT" if (best_banpu_lead and best_ptt_lead and abs(best_banpu_lead["correlation"]) > abs(best_ptt_lead["correlation"])) else "PTT appears to lead BANPU" if best_ptt_lead and best_banpu_lead else "no clear lead",
        },
    }

    out_path = os.path.join(root, "tradecanvas-ui", "data", "banpu_ptt_causality.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("Wrote causality results to", out_path)
    print("Strongest overall: lag", strongest["lag"], "corr", strongest["correlation"])
    print("BANPU leads PTT best:", best_banpu_lead)
    print("PTT leads BANPU best:", best_ptt_lead)
    print("Granger:")
    print(json.dumps(out["granger_like"], indent=2))


if __name__ == "__main__":
    main()
