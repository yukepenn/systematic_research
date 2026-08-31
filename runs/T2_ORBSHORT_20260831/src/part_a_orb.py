"""T2_ORBSHORT_20260831 — PART A: recover the GENESIS ORB momentum-side CONTROL (B3).

Frozen spec: runs/T2_ORBSHORT_20260831/spec.yaml (committed 7b519ac, before any result).
Rule R1..R9 are transcribed from runs/GENESIS_BASELINES_20260828/src/run_baselines.py
block "B3"; this file is an INDEPENDENT re-implementation so that G_A1..G_A3 is a real
reproduction check, not a re-run of the same object.

NO opening-range length search occurs anywhere in this file (barred by FAILURE_MEMORY).
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(REPO, "runs", "T2_ORBSHORT_20260831")
OUT = os.path.join(RUN, "out")
PARQUET = os.path.join(REPO, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet")
P1_CSV = os.path.join(REPO, "runs", "G2_AUG_INCUMBENT_READ_20260830", "out", "p1_trades_full.csv")
XM_CSV = os.path.join(REPO, "runs", "G2_AUG_INCUMBENT_READ_20260830", "out", "xm_trades_full.csv")

PT = 20.0
RT = 4.36 + 14.44          # 18.80, the GENESIS baseline cost model
SEAL = pd.Timestamp("2026-08-01")
RNG = np.random.default_rng(20260831)

# reported B3 numbers we must reproduce (spec G_A1..G_A3)
TGT_NETWK, TGT_T, TGT_LONG, TGT_SHORT = 1042.7180, 2.1944, 591, 542


def log(m):
    print(m, flush=True)


def session_id(ts: pd.Series) -> pd.Series:
    d = ts.dt.normalize()
    return (d + pd.to_timedelta((ts.dt.hour >= 18).astype(int), unit="D")).dt.date


def iso_week(dates) -> pd.Series:
    iso = pd.to_datetime(pd.Series(list(dates))).dt.isocalendar()
    return pd.Series((iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values,
                     index=list(dates))


def wk_metrics(net_w: pd.Series) -> dict:
    n = len(net_w)
    mu = float(net_w.mean())
    sd = float(net_w.std(ddof=1))
    t = mu / sd * math.sqrt(n) if sd > 0 else float("nan")
    eq = net_w.cumsum()
    dd = float((eq.cummax() - eq).max())
    return dict(n_weeks=n, mean=mu, sd=sd, t=t, maxdd=dd,
                pct_pos=float((net_w > 0).mean() * 100), worst=float(net_w.min()),
                total=float(net_w.sum()))


def stationary_bootstrap(x: np.ndarray, nrep: int, mean_block: float, rng) -> np.ndarray:
    """Politis-Romano stationary bootstrap; returns nrep resampled means."""
    n = len(x)
    p = 1.0 / mean_block
    out = np.empty(nrep)
    for r in range(nrep):
        idx = np.empty(n, dtype=np.int64)
        i = rng.integers(n)
        for j in range(n):
            idx[j] = i
            if rng.random() < p:
                i = rng.integers(n)
            else:
                i = (i + 1) % n
        out[r] = x[idx].mean()
    return out


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    lines = []
    ap = lines.append

    df = pd.read_parquet(PARQUET).sort_values("time").reset_index(drop=True)
    assert df["time"].max() < SEAL, "SEAL VIOLATION"
    df["sid"] = session_id(df["time"])
    sessions = pd.Index(sorted(df["sid"].unique()))
    week_of = iso_week(sessions)
    week_grid = pd.Index(pd.unique(week_of.values))
    log(f"sessions {len(sessions)}  weeks {len(week_grid)}  bars {len(df)}")

    hm = df["time"].dt.hour * 100 + df["time"].dt.minute
    df["hm"] = hm

    # ---------------- B3 exact ----------------
    or_bars = df[(hm >= 931) & (hm <= 1000)]
    or_high = or_bars.groupby("sid")["high"].max()
    or_low = or_bars.groupby("sid")["low"].min()
    scan = df[(hm >= 1001) & (hm <= 1559)]
    b1559 = df[hm == 1559].set_index("sid")
    b931 = df[hm == 931].set_index("sid")
    exit_close = b1559["close"]

    scan_g = dict(tuple(scan.groupby("sid")))
    rows = []
    n_skip = n_ambig = n_nobreak = 0
    for sid in sessions:
        if sid not in or_high.index or sid not in exit_close.index or sid not in scan_g:
            n_skip += 1
            continue
        oh, ol = or_high.loc[sid], or_low.loc[sid]
        sb = scan_g[sid]
        up = sb["high"].values > oh
        dn = sb["low"].values < ol
        hit = up | dn
        if not hit.any():
            n_nobreak += 1
            continue
        i = int(np.argmax(hit))
        if up[i] and dn[i]:
            n_ambig += 1
            continue
        o = float(sb["open"].values[i])
        xc = float(exit_close.loc[sid])
        if up[i]:
            entry, d = max(oh, o), 1
        else:
            entry, d = min(ol, o), -1
        gross = (xc - entry) * d * PT
        rows.append(dict(sid=sid, dir=d, entry_ts=pd.Timestamp(sb["time"].values[i]),
                         entry_hm=int(sb["hm"].values[i]), entry_px=entry, exit_px=xc,
                         gross=gross, net=gross - RT, or_high=oh, or_low=ol,
                         or_range_pts=oh - ol))
    orb = pd.DataFrame(rows)
    orb["week"] = orb["sid"].map(week_of)
    orb["year"] = pd.to_datetime(pd.Series(list(orb["sid"]))).dt.year.values

    def to_weekly(s_by_sid: pd.Series) -> pd.Series:
        s = pd.Series(s_by_sid, index=sessions).fillna(0.0)
        return s.groupby(week_of.values).sum().reindex(week_grid, fill_value=0.0)

    net_by_sid = orb.set_index("sid")["net"]
    orb_w = to_weekly(net_by_sid)
    m = wk_metrics(orb_w)
    nL = int((orb["dir"] == 1).sum())
    nS = int((orb["dir"] == -1).sum())

    ap("T2_ORBSHORT_20260831 — PART A GATE TABLE (printed by src/part_a_orb.py)")
    ap("=" * 112)
    ap(f"{'GATE':<14} {'SPEC':<44} {'OBSERVED':<34} VERDICT")
    ap("-" * 112)
    ap(f"{'SEAL':<14} {'max bar ts < 2026-08-01':<44} {str(df['time'].max()):<34} PASS")
    gA1 = abs(m["mean"] - TGT_NETWK) <= 0.01
    gA2 = abs(m["t"] - TGT_T) <= 0.001
    gA3 = (nL == TGT_LONG) and (nS == TGT_SHORT)
    obs1 = f"{m['mean']:.4f}"
    obs2 = f"{m['t']:.4f}"
    ap(f"{'G_A1 net/wk':<14} {'== 1042.7180 (+-0.01)':<44} {obs1:<34} {'PASS' if gA1 else 'FAIL'}")
    ap(f"{'G_A2 weekly t':<14} {'== 2.1944 (+-0.001)':<44} {obs2:<34} {'PASS' if gA2 else 'FAIL'}")
    ap(f"{'G_A3 counts':<14} {'591 long / 542 short':<44} {f'{nL} long / {nS} short':<34} {'PASS' if gA3 else 'FAIL'}")
    ap("-" * 112)
    log("\n".join(lines))
    json.dump(dict(gA1=bool(gA1), gA2=bool(gA2), gA3=bool(gA3), metrics=m, nL=nL, nS=nS,
                   n_skip=n_skip, n_ambig=n_ambig, n_nobreak=n_nobreak),
              open(os.path.join(OUT, "part_a_repro.json"), "w"), indent=2, default=float)
    orb.to_csv(os.path.join(OUT, "orb_trades.csv"), index=False)
    orb_w.to_csv(os.path.join(OUT, "orb_weekly.csv"))
    log(f"n_skip={n_skip} n_ambig={n_ambig} n_nobreak={n_nobreak}")
    log(json.dumps(m, indent=2, default=float))


if __name__ == "__main__":
    sys.exit(main())
