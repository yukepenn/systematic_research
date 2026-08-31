"""T2_ORBSHORT_20260831 — PART B: independent SHORT alpha, preregistered.

Spec: runs/T2_ORBSHORT_20260831/spec.yaml part_b (committed 7b519ac BEFORE any short P&L).
Two arms, both frozen there: S1 SHORT_VWAP_RECLAIM_FAILURE, S2 SHORT_WEAK_OPEN_CONTINUATION.
Gates B1..B7 applied identically to both. Activation (B1) is printed BEFORE any economics.

DISCLOSED SPEC DEFECT + MINIMAL REPAIR (found by reading the frozen text, before any result):
  S2's `no_reclaim` was written "max(high) over bars stamped 09:31..10:00 <= open of the
  09:31-stamped bar". The 09:31 bar's own high is >= its own open by construction, so the
  clause is satisfiable only when the first RTH minute never ticks above its open — it is
  very nearly a null set and does not express the stated mechanism ("never reclaimed the
  open"). The minimal faithful repair, adding NO new parameter, evaluates the clause on bar
  CLOSES (the repo's standing causal convention): max(close) over 09:31..10:00 <= open of the
  09:31 bar. Both counts are printed. The defective clause's own count is reported so the
  repair can be audited.
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

PT, RT = 20.0, 18.80
RNG = np.random.default_rng(31082026)
L = []


def ap(s=""):
    L.append(s)
    print(s, flush=True)


def session_id(ts):
    d = ts.dt.normalize()
    return (d + pd.to_timedelta((ts.dt.hour >= 18).astype(int), unit="D")).dt.date


def iso_week(dates):
    iso = pd.to_datetime(pd.Series(list(dates))).dt.isocalendar()
    return pd.Series((iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values,
                     index=list(dates))


def wk_metrics(w):
    n = len(w); mu = float(w.mean()); sd = float(w.std(ddof=1))
    t = mu / sd * math.sqrt(n) if sd > 0 else float("nan")
    eq = w.cumsum(); dd = float((eq.cummax() - eq).max())
    return dict(n_weeks=n, mean=mu, sd=sd, t=t, maxdd=dd, total=float(w.sum()),
                pct_pos=float((w > 0).mean() * 100), worst=float(w.min()))


def main():
    df = pd.read_parquet(PARQUET).sort_values("time").reset_index(drop=True)
    assert df["time"].max() < pd.Timestamp("2026-08-01")
    df["sid"] = session_id(df["time"])
    df["hm"] = df["time"].dt.hour * 100 + df["time"].dt.minute
    sessions = pd.Index(sorted(df["sid"].unique()))
    week_of = iso_week(sessions)
    week_grid = pd.Index(pd.unique(week_of.values))

    def to_weekly(s):
        s = pd.Series(s, index=sessions).fillna(0.0)
        return s.groupby(week_of.values).sum().reindex(week_grid, fill_value=0.0)

    rth = df[(df["hm"] >= 931) & (df["hm"] <= 1559)].copy()
    ovn = df[(df["hm"] >= 1801) | (df["hm"] <= 930)].copy()

    # per-session RTH matrices (ragged -> dict of frames)
    rth_g = dict(tuple(rth.groupby("sid")))
    ovn_g = dict(tuple(ovn.groupby("sid")))
    b1559 = df[df["hm"] == 1559].set_index("sid")["close"]
    b931 = df[df["hm"] == 931].set_index("sid")
    b1001 = df[df["hm"] == 1001].set_index("sid")

    eligible = [s for s in sessions
                if s in rth_g and s in b1559.index and s in b931.index and s in b1001.index
                and len(rth_g[s]) >= 120]
    ap(f"eligible sessions (full RTH block present): {len(eligible)} of {len(sessions)}")

    # ---------------- S1: VWAP reclaim failure ----------------
    s1_rows, s1_delay_rows = [], []
    s1_state_sessions = []
    for s in eligible:
        g = rth_g[s]
        h = g["high"].values; l = g["low"].values; c = g["close"].values
        o = g["open"].values; v = g["volume"].values.astype(float); hm = g["hm"].values
        tp = (h + l + c) / 3.0
        cum_pv = np.cumsum(tp * v); cum_v = np.cumsum(v)
        vwap = np.where(cum_v > 0, cum_pv / np.maximum(cum_v, 1e-9), c)
        below = (c < vwap).astype(int)
        # rolling count of "closed below" over the last 30 bars ending at t (inclusive)
        cs = np.concatenate([[0], np.cumsum(below)])
        n = len(c)
        roll = np.full(n, 0)
        for i in range(n):
            j = max(0, i - 29)
            roll[i] = cs[i + 1] - cs[j]
        below_state = roll >= 20
        touch = h >= vwap
        reject = c < vwap
        window = (hm >= 1001) & (hm <= 1529)
        trig = below_state & touch & reject & window
        if not trig.any():
            continue
        i = int(np.argmax(trig))
        s1_state_sessions.append(s)
        if i + 1 >= n:
            continue
        entry = float(o[i + 1])
        exitp = float(b1559.loc[s])
        gross = (entry - exitp) * PT
        s1_rows.append(dict(sid=s, trig_hm=int(hm[i]), entry_hm=int(hm[i + 1]),
                            entry_px=entry, exit_px=exitp, gross=gross, net=gross - RT))
        # B5 timing teeth: same trigger, entry delayed 30 minutes
        k = i + 31
        if k < n:
            e2 = float(o[k])
            s1_delay_rows.append(dict(sid=s, net=(e2 - exitp) * PT - RT))
    S1 = pd.DataFrame(s1_rows)
    S1D = pd.DataFrame(s1_delay_rows)

    # ---------------- S2: weak-open continuation ----------------
    s2_rows, s2_delay_rows = [], []
    n_defect_clause = 0
    prev_close = {}
    prev = None
    for s in sessions:
        if s in b1559.index:
            prev_close[s] = prev
            prev = float(b1559.loc[s])
        else:
            prev_close[s] = prev
    for s in eligible:
        pc = prev_close.get(s)
        if pc is None or s not in ovn_g:
            continue
        g = rth_g[s]
        hm = g["hm"].values
        om = (hm >= 931) & (hm <= 1000)
        if om.sum() < 25:
            continue
        open0930 = float(b931.loc[s, "open"])
        og = ovn_g[s]
        ovn_hi, ovn_lo = float(og["high"].max()), float(og["low"].min())
        ovn_mid = (ovn_hi + ovn_lo) / 2.0
        gap_down = open0930 < pc
        below_mid = open0930 < ovn_mid
        no_reclaim_close = float(g["close"].values[om].max()) <= open0930     # REPAIRED clause
        no_reclaim_high = float(g["high"].values[om].max()) <= open0930      # defective clause
        new_low = float(g["low"].values[om].min()) < ovn_lo
        if gap_down and below_mid and no_reclaim_high and new_low:
            n_defect_clause += 1
        if not (gap_down and below_mid and no_reclaim_close and new_low):
            continue
        entry = float(b1001.loc[s, "open"])
        exitp = float(b1559.loc[s])
        gross = (entry - exitp) * PT
        s2_rows.append(dict(sid=s, entry_hm=1001, entry_px=entry, exit_px=exitp,
                            gross=gross, net=gross - RT))
        gg = rth_g[s]
        m31 = gg["hm"].values == 1031
        if m31.any():
            e2 = float(gg["open"].values[m31][0])
            s2_delay_rows.append(dict(sid=s, net=(e2 - exitp) * PT - RT))
    S2 = pd.DataFrame(s2_rows)
    S2D = pd.DataFrame(s2_delay_rows)

    # ================= B1 ACTIVATION, PRINTED BEFORE ANY ECONOMICS =================
    ap("\n" + "=" * 104)
    ap("PART B — GATE B1 (ACTIVATION), printed BEFORE any P&L, exactly as the spec requires")
    ap("=" * 104)
    ap(f"{'ARM':<34}{'fires':>8}{'spec 40..500':>14}  VERDICT")
    b1_s1 = 40 <= len(S1) <= 500
    b1_s2 = 40 <= len(S2) <= 500
    ap(f"{'S1 SHORT_VWAP_RECLAIM_FAILURE':<34}{len(S1):>8}{'40..500':>14}  {'PASS' if b1_s1 else 'FAIL'}")
    ap(f"{'S2 SHORT_WEAK_OPEN_CONTINUATION':<34}{len(S2):>8}{'40..500':>14}  {'PASS' if b1_s2 else 'FAIL'}")
    ap(f"  (S2 defective-clause count, disclosed: {n_defect_clause} sessions — the repair is "
       f"load-bearing and is declared in this file's docstring)")
    ap(f"  (S1 sessions that ever reached the below-VWAP state in-window: {len(s1_state_sessions)})")

    # ================= economics + gates =================
    results = {}
    for nm, T, TD, in [("S1", S1, S1D), ("S2", S2, S2D)]:
        if len(T) == 0:
            continue
        ap("\n" + "=" * 104)
        ap(f"ARM {nm}  —  {'SHORT_VWAP_RECLAIM_FAILURE' if nm=='S1' else 'SHORT_WEAK_OPEN_CONTINUATION'}")
        ap("=" * 104)
        w = to_weekly(T.set_index("sid")["net"])
        mm = wk_metrics(w)
        pt_ = float(T["net"].mean())
        ap(f"  B2 ECONOMICS: n={len(T)}  net ${T['net'].sum():,.0f}  $/trade ${pt_:,.0f}  "
           f"win {(T['net']>0).mean()*100:.1f}%  wk ${mm['mean']:,.0f}  t {mm['t']:.2f}  "
           f"maxDD ${mm['maxdd']:,.0f}")
        b2 = T["net"].sum() > 0
        ap(f"     -> B2 {'PASS' if b2 else 'FAIL'} (spec: net > 0 after $18.80/ctrRT)")

        # B3 rate-matched random-short placebo
        slots = T["entry_hm"].values
        elig = [s for s in eligible]
        draws = np.empty(1000)
        pool_open = {}
        for s in elig:
            g = rth_g[s]
            pool_open[s] = dict(zip(g["hm"].values.tolist(), g["open"].values.tolist()))
        for r in range(1000):
            pick = RNG.choice(len(elig), size=len(T), replace=False)
            sl = RNG.choice(slots, size=len(T), replace=True)
            acc = []
            for pi, hh in zip(pick, sl):
                s = elig[pi]
                po = pool_open[s]
                if hh not in po:
                    continue
                acc.append((po[hh] - float(b1559.loc[s])) * PT - RT)
            draws[r] = np.mean(acc) if acc else 0.0
        p95 = float(np.percentile(draws, 95))
        pct = float((draws < pt_).mean() * 100)
        b3 = pt_ > p95
        ap(f"  B3 RATE-MATCHED RANDOM-SHORT PLACEBO (1,000 draws, same n, same entry-slot "
           f"distribution):")
        ap(f"     null mean ${draws.mean():,.0f}  p95 ${p95:,.0f}  REAL ${pt_:,.0f}  "
           f"percentile {pct:.1f}   -> B3 {'PASS' if b3 else 'FAIL'}")

        # B4 state validity
        rets = {}
        for s in eligible:
            rets[s] = (float(b1559.loc[s]) - float(b931.loc[s, "open"])) * PT
        uncond = np.mean([rets[s] for s in eligible])
        instate = np.mean([rets[s] for s in T["sid"]])
        b4 = instate < uncond
        ap(f"  B4 STATE VALIDITY: mean RTH open->close $ move, in-state ${instate:,.0f} vs "
           f"matched unconditional ${uncond:,.0f}  -> B4 {'PASS' if b4 else 'FAIL'}")

        # B5 timing teeth
        if len(TD):
            merged = T.set_index("sid")["net"].reindex(TD["sid"]).values
            dnet = TD["net"].sum()
            deg = (T["net"].sum() - dnet) / abs(T["net"].sum()) if T["net"].sum() != 0 else 0
            b5 = deg >= 0.25
            ap(f"  B5 TIMING TEETH (+30 min entry delay): net ${dnet:,.0f} vs ${T['net'].sum():,.0f}"
               f"  degradation {deg*100:.1f}%  -> B5 {'PASS' if b5 else 'FAIL'} (spec >= 25%)")
        else:
            b5 = False
            ap("  B5 TIMING TEETH: not computable -> FAIL")

        # B6/B7 tail
        s = np.sort(T["net"].values)[::-1]; tot = s.sum()
        k10 = max(1, int(round(0.10 * len(s))))
        k5 = max(1, int(round(0.05 * len(s))))
        k1 = max(1, int(round(0.01 * len(s))))
        ap(f"  B6 CONCENTRATION (classification, never a kill gate): top-10% = {k10} trades = "
           f"{s[:k10].sum()/tot*100:.1f}% of net   [incumbent P1 fails this bar at 236.8%]")
        ap(f"  B7 TAIL AUDIT: top1% {s[:k1].sum()/tot*100:.1f}%  top5% {s[:k5].sum()/tot*100:.1f}%  "
           f"ex-top-1 ${tot-s[0]:,.0f}  ex-top-5 ${tot-s[:5].sum():,.0f}  median ${np.median(T['net']):,.0f}")
        T["year"] = pd.to_datetime(pd.Series(list(T["sid"]))).dt.year.values
        ap("     per-year: " + "  ".join(f"{y}: n={len(g)} ${g['net'].sum():,.0f}"
                                          for y, g in T.groupby("year")))
        ap("     LOYO net: " + "  ".join(f"excl{y}: ${T[T['year']!=y]['net'].sum():,.0f}"
                                          for y in sorted(T['year'].unique())))
        verdict = "CHALLENGER (B1..B5 all PASS)" if (b1_s1 if nm == "S1" else b1_s2) and b2 and b3 and b4 and b5 else "FAILED"
        ap(f"  VERDICT {nm}: {verdict}")
        results[nm] = dict(n=len(T), net=float(T["net"].sum()), per_trade=pt_,
                           b1=bool(b1_s1 if nm == "S1" else b1_s2), b2=bool(b2), b3=bool(b3),
                           b4=bool(b4), b5=bool(b5), null_p95=p95, percentile=pct,
                           metrics=mm, verdict=verdict)
        T.to_csv(os.path.join(OUT, f"short_trades_{nm}.csv"), index=False)

    # correlation of any surviving arm with the incumbent
    p1 = pd.read_csv(P1_CSV, parse_dates=["et"]); p1["sid"] = session_id(p1["et"])
    xm = pd.read_csv(XM_CSV, parse_dates=["et"]); xm["sid"] = session_id(xm["et"])
    p1w = to_weekly(p1[p1["sid"].isin(set(sessions))].groupby("sid")["pnl"].sum())
    xmw = to_weekly(xm[xm["sid"].isin(set(sessions))].groupby("sid")["pnl"].sum())
    ap("\nWEEKLY CORRELATION WITH THE INCUMBENT")
    cols = {"P1": p1w, "XM": xmw, "M11": p1w + xmw}
    for nm, T in [("S1", S1), ("S2", S2)]:
        if len(T) == 0:
            continue
        w = to_weekly(T.set_index("sid")["net"])
        ap(f"  {nm}: " + "  ".join(f"{k} {w.corr(v):+.3f}" for k, v in cols.items()))

    open(os.path.join(OUT, "part_b_gates.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    json.dump(results, open(os.path.join(OUT, "part_b_results.json"), "w"), indent=2, default=float)


if __name__ == "__main__":
    sys.exit(main())
