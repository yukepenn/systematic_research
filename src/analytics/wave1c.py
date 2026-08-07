"""wave1c.py — build the Wave-1c Tier-2 table from exported execution ledgers.

Usage:  python src/analytics/wave1c.py <ledger_dir> [<out_csv>]

Ranking rule (preregistered, DISCOVERY_WAVE1_spec + campaign §19): never rank by
single-point net profit. Every cell carries its neighbourhood median over the
dense StopMultiplier grid, and plateau membership is reported alongside the point
estimate.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from execledger import read_exec_ledger, metrics, daily_vector  # noqa: E402

NAME_RE = re.compile(
    r"^(?P<tag>[^_]+)__tf(?P<tf>\d+)_sm(?P<sm>\d+)_tm(?P<tm>\d+)_ss(?P<ss>\d+)"
    r"_wws(?P<wws>\d+)_est(?P<est>\d+)_(?P<exit>[a-z0-9]+)_slip(?P<slip>\d+)"
    r"_L(?P<long>\d)S(?P<short>\d)\.csv$")


def parse_name(path: Path):
    m = NAME_RE.match(path.name)
    if not m:
        return None
    d = m.groupdict()
    for k in ("tf", "sm", "tm", "ss", "wws", "est", "slip", "long", "short"):
        d[k] = int(d[k])
    return d


def build(ledger_dir, out_csv=None):
    ledger_dir = Path(ledger_dir)
    rows, dailies = [], {}
    for p in sorted(ledger_dir.glob("*.csv")):
        meta = parse_name(p)
        if meta is None:
            continue
        trades, header = read_exec_ledger(p)
        if trades.empty:
            continue
        label = f"tf{meta['tf']}_sm{meta['sm']}_{meta['exit']}_slip{meta['slip']}"
        m = metrics(trades, label=label)
        m.update({k: meta[k] for k in ("tf", "sm", "tm", "ss", "wws", "est", "slip")})
        m["exit"] = meta["exit"]
        m["file"] = p.name
        rows.append(m)
        dailies[label] = daily_vector(trades)

    if not rows:
        raise SystemExit(f"no parsable ledgers in {ledger_dir}")
    df = pd.DataFrame(rows)

    # neighbourhood median of net over the dense SM grid, within (tf, exit, slip)
    df = df.sort_values(["tf", "exit", "slip", "sm"]).reset_index(drop=True)
    df["nbhd_net"] = np.nan
    df["nbhd_sharpe"] = np.nan
    df["plateau_width"] = np.nan
    for _, g in df.groupby(["tf", "exit", "slip"]):
        idx = g.index.to_numpy()
        nets = g.net.to_numpy()
        shp = g.sharpe_daily.to_numpy()
        for j, i in enumerate(idx):
            lo, hi = max(0, j - 1), min(len(idx), j + 2)
            df.loc[i, "nbhd_net"] = float(np.median(nets[lo:hi]))
            df.loc[i, "nbhd_sharpe"] = float(np.median(shp[lo:hi]))
        # connected run of positive-net cells containing each point
        pos = nets > 0
        for j, i in enumerate(idx):
            if not pos[j]:
                df.loc[i, "plateau_width"] = 0
                continue
            a = j
            while a > 0 and pos[a - 1]:
                a -= 1
            b = j
            while b < len(pos) - 1 and pos[b + 1]:
                b += 1
            df.loc[i, "plateau_width"] = b - a + 1

    if out_csv:
        df.to_csv(out_csv, index=False)
        dd = pd.DataFrame(dailies)
        dd.to_csv(str(out_csv).replace(".csv", "_daily.csv"))
    return df, dailies


if __name__ == "__main__":
    d, _ = build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    cols = ["label", "trades", "net", "nbhd_net", "avg_trade", "pf", "sharpe_daily",
            "calmar", "max_dd", "worst_year", "pos_years", "plateau_width"]
    with pd.option_context("display.width", 250, "display.max_rows", 300):
        print(d[cols].round(3).to_string(index=False))
