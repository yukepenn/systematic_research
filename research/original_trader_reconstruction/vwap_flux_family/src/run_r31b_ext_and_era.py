"""OTR_R31 amendment 2: extend the volatility law to 22 windows, and the 2023 era discriminator.

Reuses existing artifacts rather than rebuilding anything:
  - the UNIQUE 89-trade Jan-2023 path from runs/OTR_R11_INVERSE/out/r22_global_path_11days.json
    (already carries per-trade mae/mfe in dollars, entry/exit bar indices and prices)
  - the June/July 2026 1-minute exports already in research/original_trader_reconstruction/data/
"""
from __future__ import annotations

import csv
import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "OTR_R31_JOINT_MECHANISM", "out")
os.makedirs(OUT, exist_ok=True)
DATA = os.path.join(ROOT, "research", "original_trader_reconstruction", "data")
PV = 20.0

# window -> which bar source (fixed in advance by amendment 2)
JUN = os.path.join(DATA, "nq0626_jun2026_1m.csv")
JUL = os.path.join(DATA, "nq0926_junjul2026_1m.csv")
SRC = {"5/31/2026": JUN, "6/7/2026": JUN, "6/14/2026": JUL,
       "6/21/2026": JUL, "6/28/2026": JUL, "7/12/2026": JUL}


def powerfit(x, y):
    lx, ly = np.log(np.asarray(x, float)), np.log(np.asarray(y, float))
    b, a = np.polyfit(lx, ly, 1)
    ss = np.sum((ly - (a + b * lx)) ** 2); tt = np.sum((ly - ly.mean()) ** 2)
    return float(b), float(1 - ss / tt if tt > 0 else np.nan)


def load(path):
    d = pd.read_csv(path)
    d["time"] = pd.to_datetime(d["time"])
    return d


def window_stats(d, a, b):
    m = (d["time"].values.astype("datetime64[s]") >= a) & \
        (d["time"].values.astype("datetime64[s]") <= b)
    if m.sum() < 100:
        return None
    hi = d["high"].values[m]; lo = d["low"].values[m]; c = d["close"].values[m]
    t = d["time"].values[m].astype("datetime64[s]")
    tr = np.maximum(hi - lo, np.maximum(np.abs(hi - np.roll(c, 1)), np.abs(lo - np.roll(c, 1))))
    tr[0] = hi[0] - lo[0]
    atr = pd.Series(tr).rolling(14, min_periods=1).mean().values
    fb = np.zeros(m.sum(), bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    sid = np.cumsum(fb) - 1
    runs = []
    for k in np.unique(sid):
        ch = c[sid == k]
        if len(ch) < 5:
            continue
        dd = np.diff(ch); best = cur = 0.0; sgn = 0
        for x in dd:
            s2 = 1 if x > 0 else (-1 if x < 0 else sgn)
            cur = cur + x if s2 == sgn else x
            sgn = s2; best = max(best, abs(cur))
        runs.append(best)
    return float(atr.mean()), float(np.mean(runs))


def part_a_ext():
    print("=" * 92)
    print("PART A-EXT - extend the volatility law from 17 to 22 windows (August stays SEALED)")
    print("=" * 92)
    tgt = list(csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2026V.csv"), encoding="utf-8")))
    prev = {r["image_id"]: r for r in csv.DictReader(open(os.path.join(
        ROOT, "runs", "OTR_R30_ENTRY_EXIT_DECOMP", "out",
        "opportunity_by_window.csv"), encoding="utf-8"))}
    cache = {}
    rows = []
    for r in tgt:
        if pd.Timestamp(r["report_end"]) >= pd.Timestamp("2026-08-01"):
            print(f"   {r['report_start']}->{r['report_end']:<11} SEALED by LOCKED_FORWARD - excluded")
            continue
        if r["image_id"] in prev:
            p = prev[r["image_id"]]
            rows.append(dict(image_id=r["image_id"], window=f"{r['report_start']}->{r['report_end']}",
                             atr=float(p["atr14"]), max_run=float(p["max_run"]),
                             hold=float(r["avg_time_min_all"]),
                             avg_win=float(r["avg_win_all"]), avg_loss=abs(float(r["avg_loss_all"])),
                             src="parquet"))
            continue
        src = SRC.get(r["report_start"])
        if src is None:
            continue
        if src not in cache:
            cache[src] = load(src)
        a = np.datetime64(pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        b = np.datetime64(pd.Timestamp(r["report_end"])) + np.timedelta64(17, "h")
        st = window_stats(cache[src], a, b)
        if st is None:
            print(f"   {r['report_start']}->{r['report_end']:<11} insufficient bars - skipped")
            continue
        rows.append(dict(image_id=r["image_id"], window=f"{r['report_start']}->{r['report_end']}",
                         atr=st[0], max_run=st[1], hold=float(r["avg_time_min_all"]),
                         avg_win=float(r["avg_win_all"]), avg_loss=abs(float(r["avg_loss_all"])),
                         src=os.path.basename(src)))

    print(f"\n{'window':<24}{'src':<26}{'atr':>7}{'maxRun':>8}{'hold':>8}{'avgWin':>9}{'avgLoss':>9}")
    for d in rows:
        new = "  <== NEW" if d["src"] != "parquet" else ""
        print(f"{d['window']:<24}{d['src']:<26}{d['atr']:>7.2f}{d['max_run']:>8.0f}"
              f"{d['hold']:>8.1f}{d['avg_win']:>9.0f}{d['avg_loss']:>9.0f}{new}")

    A = np.array([d["atr"] for d in rows]); Hh = np.array([d["hold"] for d in rows])
    AW = np.array([d["avg_win"] for d in rows]); AL = np.array([d["avg_loss"] for d in rows])
    R = np.array([d["max_run"] for d in rows])
    b17, r17 = -1.636, 0.923
    b22, r22 = powerfit(A, Hh)
    print("\n" + "-" * 92)
    print(f"I1  17-window fit : b = {b17:+.3f}   R^2 = {r17:.3f}")
    print(f"I1  {len(rows)}-window fit : b = {b22:+.3f}   R^2 = {r22:.3f}")
    ok = (-2.0 <= b22 <= -1.2) and r22 > 0.75
    print(f"I1  preregistered band b in [-2.0,-1.2] and R^2 > 0.75 -> "
          f"{'PASS - identification survives out of sample' if ok else 'FAIL - IDENTIFICATION WITHDRAWN'}")
    new = [d for d in rows if d["src"] != "parquet"]
    print(f"\nI2  the five NEW windows:")
    for d in new:
        pred = np.exp(np.polyfit(np.log(A), np.log(Hh), 1)[1]) * d["atr"] ** b22
        print(f"    {d['window']:<24} atr {d['atr']:>6.2f}  hold {d['hold']:>6.1f}  "
              f"law predicts {pred:>6.1f}  resid {d['hold']-pred:>+7.1f}")
    rt = [d for d in new if d["window"].startswith(("6/21", "7/12"))]
    print(f"    right-tail weeks are {'LOW' if all(d['atr'] < np.median(A) for d in rt) else 'NOT low'}-ATR "
          f"-> I2 {'PASS' if all(d['atr'] < np.median(A) for d in rt) else 'FAIL'}")
    print(f"\nI3  dollar co-scaling over {len(rows)} windows:")
    print(f"    corr(ATR, avg_win)  = {np.corrcoef(A, AW)[0,1]:+.3f}   (17-window: -0.469)")
    print(f"    corr(ATR, avg_loss) = {np.corrcoef(A, AL)[0,1]:+.3f}   (17-window: -0.509)")
    print(f"    corr(ATR, payoff)   = {np.corrcoef(A, AW/AL)[0,1]:+.3f}   (17-window: -0.062)")
    print(f"    corr(max_run,payoff)= {np.corrcoef(R, AW/AL)[0,1]:+.3f}   (17-window: -0.452)")
    with open(os.path.join(OUT, "volatility_law_22windows.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    return b22, r22


def part_e():
    print("\n" + "=" * 92)
    print("PART E - the 2023 ERA DISCRIMINATOR, on the already-recovered 89-trade path")
    print("=" * 92)
    path = json.load(open(os.path.join(ROOT, "runs", "OTR_R11_INVERSE", "out",
                                       "r22_global_path_11days.json")))
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2023-01-02 18:00") &
             (df["time"] <= "2023-01-18 17:00")].reset_index(drop=True)
    t = seg["time"].values.astype("datetime64[s]")
    o, hi, lo, c = (seg[k].values.astype(float) for k in ("open", "high", "low", "close"))
    # ---- alignment self-check: entry prices in the path must equal bar opens at ei ----
    bad = sum(1 for x in path if abs(o[x["ei"] + 1] - x["epx"]) > 1e-6)
    bad0 = sum(1 for x in path if abs(o[x["ei"]] - x["epx"]) > 1e-6)
    off = 1 if bad < bad0 else 0
    print(f"   alignment self-check: entry price == open[ei+{off}] for "
          f"{len(path)-min(bad,bad0)}/{len(path)} trades")
    if min(bad, bad0) > 3:
        print("   ALIGNMENT FAILED - aborting Part E rather than reporting a wrong law")
        return
    tr = np.maximum(hi - lo, np.maximum(np.abs(hi - np.roll(c, 1)), np.abs(lo - np.roll(c, 1))))
    tr[0] = hi[0] - lo[0]
    atr = pd.Series(tr).rolling(14, min_periods=1).mean().values

    mae_pts = np.array([x["mae"] / PV for x in path])
    mfe_pts = np.array([x["mfe"] / PV for x in path])
    print(f"\nE1  his 2023 per-trade MAE (index points), n={len(path)}:")
    for q in (10, 25, 50, 75, 90, 95, 100):
        print(f"       p{q:<3} {np.percentile(mae_pts, q):>7.2f}")
    print(f"       mean {mae_pts.mean():.2f}   share exceeding 25 pts: "
          f"{100*(mae_pts>25).mean():.1f}%   exceeding 30 pts: {100*(mae_pts>30).mean():.1f}%")
    print(f"    CONTROL reading: the 2023 mechanism is a known stop-and-reverse on Solar flips")
    print(f"    with NO trailing stop, so a broad MAE distribution is EXPECTED here.")
    print(f"    A 25-pt trailing stop would have killed {100*(mae_pts>25).mean():.0f}% of his")
    print(f"    2023 trades before they developed.")

    # ---- E2: per-day hold vs ATR in 2023 ----
    days = {}
    for x in path:
        h = float((t[x["xi"]] - t[x["ei"] + off]).astype("timedelta64[s]").astype(np.int64)) / 60.0
        days.setdefault(x["day"], []).append((h, float(atr[x["ei"] + off])))
    dd = sorted(days)
    Hh = np.array([np.mean([v[0] for v in days[k]]) for k in dd])
    A = np.array([np.mean([v[1] for v in days[k]]) for k in dd])
    b, r2 = powerfit(A, Hh)
    print(f"\nE2  2023 per-day fit over {len(dd)} days: hold ~ ATR^{b:+.3f}   R^2 = {r2:.3f}")
    print(f"    2026 (22 windows)                     : hold ~ ATR^-1.6xx  R^2 ~0.9")
    print(f"    2023 exit is KNOWN state-based (Solar flip); prediction was |b| < 0.6, low R^2")
    flat = abs(b) < 0.6
    print(f"    E2 -> {'PASS - eras differ as predicted; the law IS diagnostic of exit class' if flat else 'FAIL - both eras steep; law is NOT diagnostic, identification WITHDRAWN'}")
    print(f"\n    {'day':<12}{'nTrades':>9}{'meanHold':>10}{'meanATR':>9}")
    for k in dd:
        print(f"    {k:<12}{len(days[k]):>9}{np.mean([v[0] for v in days[k]]):>10.1f}"
              f"{np.mean([v[1] for v in days[k]]):>9.2f}")
    with open(os.path.join(OUT, "era2023_hold_atr.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["day", "n_trades", "mean_hold_min", "mean_atr"])
        for k in dd:
            w.writerow([k, len(days[k]), round(float(np.mean([v[0] for v in days[k]])), 2),
                        round(float(np.mean([v[1] for v in days[k]])), 3)])


if __name__ == "__main__":
    part_a_ext()
    part_e()
