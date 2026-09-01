"""G3_SHORTALPHA / holdtime - stage 2: MEASUREMENT ONLY.

This file may not compute the P&L of any alternative policy. It measures the hold geometry of the
two existing objects and then applies the preregistered selection rule to emit ONE number, T,
into T_FROZEN.json. Stage 3 reads that file. The separation is the point: the code that chooses
T cannot see the P&L of choosing it.
"""
from __future__ import annotations

import json
import os
import sys
import time as _time

import numpy as np
import pandas as pd

ROOT_ = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT_, "research", "weekly_edge", "src"))
from run_we_w17 import load_deep                                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cache")
OUT = os.path.join(ROOT_, "runs", "G3_SHORTALPHA_20260831", "out")

PV = 20.0
COST_FLOOR = 4.36
COST_PRIMARY = 20.65
COST_ALLIN = 25.01
SEAL = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260831)
NBOOT = 1000
TAU_GRID = list(range(5, 121, 5)) + list(range(130, 301, 10)) + [330, 360, 420, 480, 600]

LOG = []


def P(*a):
    s = " ".join(str(z) for z in a)
    print(s, flush=True); LOG.append(s)


def H(title):
    P(""); P("=" * 118); P("=== " + title); P("=" * 118)


# ---------------------------------------------------------------------------- price path helpers
def forward_prices(df, o, c):
    """px[i][tau-1] = the price obtainable by exiting after exactly tau minutes, tau = 1..dur.
    tau < dur -> next-bar open o[ei+tau] (the repo's fill convention);
    tau = dur -> the trade's actual exit price."""
    out = []
    for a, dur, xpx in zip(df["ei"].values, df["dur"].values, df["xpx"].values):
        p = o[a + 1:a + dur + 1].astype(float).copy()
        if len(p) < dur:                                # never happens inside a session, guard
            p = np.concatenate([p, np.full(dur - len(p), xpx)])
        p[dur - 1] = xpx
        out.append(p)
    return out


def capped_points(df, paths, T):
    """Signed points if every trade is closed after at most T minutes (no re-entry)."""
    d = df["d"].values.astype(float)
    epx = df["epx"].values
    dur = df["dur"].values
    k = np.minimum(dur, T)
    px = np.array([p[int(kk) - 1] for p, kk in zip(paths, k)])
    return d * (px - epx), k


# ---------------------------------------------------------------------------- dependence
def icc_oneway(y, g):
    """One-way random-effects ICC and the effective sample size it implies."""
    y = np.asarray(y, float); g = np.asarray(g)
    ok = np.isfinite(y); y, g = y[ok], g[ok]
    groups, inv = np.unique(g, return_inverse=True)
    k = len(groups); n = len(y)
    if k < 2 or n <= k:
        return 0.0, float(n), 1.0
    cnt = np.bincount(inv, minlength=k).astype(float)
    gm = np.bincount(inv, weights=y, minlength=k) / cnt
    grand = y.mean()
    msb = float((cnt * (gm - grand) ** 2).sum() / (k - 1))
    msw = float(((y - gm[inv]) ** 2).sum() / (n - k))
    m0 = (n - (cnt ** 2).sum() / n) / (k - 1)
    icc = (msb - msw) / (msb + (m0 - 1) * msw) if (msb + (m0 - 1) * msw) > 0 else 0.0
    icc = float(max(0.0, min(1.0, icc)))
    mbar = n / k
    keff = n / (1.0 + (mbar - 1.0) * icc)
    return icc, float(keff), float(mbar)


def session_bootstrap_diff(dfL, dfS, stat, nboot=NBOOT, rng=None):
    """Resample WHOLE SESSIONS with replacement from the union of session ids, recompute
    stat(short) - stat(long) on the resample. Dependence inside a session is preserved."""
    rng = rng or RNG
    sess = np.unique(np.concatenate([dfL["sess"].values, dfS["sess"].values]))
    idxL = {s: np.flatnonzero(dfL["sess"].values == s) for s in sess}
    idxS = {s: np.flatnonzero(dfS["sess"].values == s) for s in sess}
    real = stat(dfS) - stat(dfL)
    draws = np.empty(nboot)
    for b in range(nboot):
        pick = rng.choice(sess, size=len(sess), replace=True)
        iL = np.concatenate([idxL[s] for s in pick]) if len(pick) else np.array([], int)
        iS = np.concatenate([idxS[s] for s in pick]) if len(pick) else np.array([], int)
        draws[b] = stat(dfS.iloc[iS]) - stat(dfL.iloc[iL])
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return real, float(lo), float(hi), draws


# ---------------------------------------------------------------------------- main
def main():
    t0 = _time.time()
    dfL = pd.read_parquet(os.path.join(CACHE, "trades_L.parquet"))
    dfS = pd.read_parquet(os.path.join(CACHE, "trades_S.parquet"))
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    o, c, t = D["o"], D["c"], D["t"]
    assert D["n"] == 1558497, f"substrate changed: {D['n']}"

    H("SEAL + PROVENANCE")
    P(f"   substrate {D['n']:,} bars  {t[0]} -> {t[-1]}")
    assert t.max() < SEAL
    P(f"   max bar {t.max()} < {SEAL}  -> SEAL HELD (asserted)")
    P(f"   L (P1 long)          {len(dfL):>6,} trades   net ${dfL['pnl'].sum():>10,.0f}"
      f"   {dfL['pnl'].sum()/PV/1012:>6.2f} pts/session   [B1 gate passed in stage 1]")
    P(f"   S (mirrored short)   {len(dfS):>6,} trades   net ${dfS['pnl'].sum():>10,.0f}"
      f"   {dfS['pnl'].sum()/PV/1012:>6.2f} pts/session")
    P(f"   sessions {len(np.unique(np.concatenate([dfL['sess'], dfS['sess']]))):,}"
      f"   2022-07-01 -> 2026-05-29")
    P("")
    P("   ERABREAK01 STRATIFICATION: W61's object is DEFINED only on 2022-07 -> 2026-07, so this")
    P("   entire primary sample sits inside the MODERN era. There is no pre-2022 material in it")
    P("   and therefore nothing is pooled across the break. A PRE (2006-2021) replication is a")
    P("   separate stratum in stage 4 and is never merged with this one. No FULL headline exists.")

    H("COST FRAME (printed once, applied everywhere below)")
    P(f"   FLOOR    ${COST_FLOOR:>5.2f}/ctrRT  = {COST_FLOOR/PV:.3f} NQ pts   (commission only - "
      f"NEVER a headline)")
    P(f"   PRIMARY  ${COST_PRIMARY:>5.2f}/ctrRT  = {COST_PRIMARY/PV:.3f} NQ pts   (G2_EXEC01, "
      f"113 measured round turns)")
    P(f"   ALL-IN   ${COST_ALLIN:>5.2f}/ctrRT  = {COST_ALLIN/PV:.3f} NQ pts")
    for nm, df in (("L", dfL), ("S", dfS)):
        rt = df["u"].sum()
        gross = df["pnl"].sum() + COST_FLOOR * rt
        P(f"   {nm}: {int(rt):,} ctrRT   gross ${gross:,.0f}   "
          f"floor ${gross-COST_FLOOR*rt:,.0f}   PRIMARY ${gross-COST_PRIMARY*rt:,.0f}   "
          f"all-in ${gross-COST_ALLIN*rt:,.0f}")

    # ------------------------------------------------------------------ derived per-trade fields
    for df in (dfL, dfS):
        df["give"] = df["mfe"] - df["fin"]
        df["tfrac"] = df["t_mfe"] / df["dur"]
        df["mfe_s"] = df["mfe"] / df["sigma"]
        df["mae_s"] = df["mae"] / df["sigma"]
        df["fin_s"] = df["fin"] / df["sigma"]
        df["give_s"] = df["give"] / df["sigma"]
        df["dur_s"] = df["dur"].astype(float)
        df["capture"] = np.where(df["mfe"] > 1e-9, df["fin"] / df["mfe"], np.nan)
        df["year"] = pd.to_datetime(df["sdate"]).dt.year

    H("PHASE 1 - HOLD GEOMETRY. Do the short's trades COMPLETE EARLIER inside the hold?")
    cols = [("dur", "duration (min)"), ("t_mfe", "time to MFE (min)"),
            ("tfrac", "t_MFE / duration"), ("t_mae", "time to MAE (min)"),
            ("mfe", "MFE (pts)"), ("mae", "MAE (pts)"), ("fin", "realised (pts)"),
            ("give", "giveback MFE-final (pts)"),
            ("mfe_s", "MFE / sigma460"), ("give_s", "giveback / sigma460"),
            ("fin_s", "realised / sigma460"), ("capture", "capture = final/MFE")]
    P(f"{'statistic':<28}{'LONG mean':>12}{'LONG med':>10}{'SHORT mean':>12}{'SHORT med':>10}"
      f"{'d mean':>10}{'d med':>10}")
    P("-" * 92)
    for k, lab in cols:
        a, b = dfL[k].values, dfS[k].values
        a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
        P(f"{lab:<28}{a.mean():>12.3f}{np.median(a):>10.3f}{b.mean():>12.3f}{np.median(b):>10.3f}"
          f"{b.mean()-a.mean():>10.3f}{np.median(b)-np.median(a):>10.3f}")

    P("")
    P("   DECILES of time-to-MFE (minutes) and of t_MFE/duration")
    qs = [10, 25, 50, 75, 90]
    P(f"{'':<14}" + "".join(f"{'p'+str(q):>10}" for q in qs))
    for nm, df in (("LONG", dfL), ("SHORT", dfS)):
        P(f"{nm+' t_MFE':<14}" + "".join(f"{np.percentile(df['t_mfe'],q):>10.1f}" for q in qs))
    for nm, df in (("LONG", dfL), ("SHORT", dfS)):
        P(f"{nm+' tfrac':<14}" + "".join(f"{np.percentile(df['tfrac'],q):>10.3f}" for q in qs))
    for nm, df in (("LONG", dfL), ("SHORT", dfS)):
        P(f"{nm+' dur':<14}" + "".join(f"{np.percentile(df['dur'],q):>10.1f}" for q in qs))

    H("PHASE 1b - THE DURATION CONFOUND. Same comparison INSIDE duration bins.")
    P("   t_MFE/dur and capture are compared only against trades of the same length, so a")
    P("   difference in the mix of short vs long holding times cannot produce the result.")
    bins = [(1, 5), (6, 15), (16, 30), (31, 60), (61, 120), (121, 10 ** 6)]
    P(f"{'dur bin':<12}{'nL':>7}{'nS':>7}{'tfrac L':>10}{'tfrac S':>10}{'d':>8}"
      f"{'capL':>9}{'capS':>9}{'d':>8}{'giveL/s':>10}{'giveS/s':>10}{'d':>8}")
    P("-" * 116)
    for lo, hi in bins:
        mL = (dfL["dur"] >= lo) & (dfL["dur"] <= hi)
        mS = (dfS["dur"] >= lo) & (dfS["dur"] <= hi)
        if mL.sum() < 20 or mS.sum() < 20:
            continue
        tfL = float(np.median(dfL.loc[mL, "tfrac"])); tfS = float(np.median(dfS.loc[mS, "tfrac"]))
        cpL = float(np.nanmedian(dfL.loc[mL, "capture"]))
        cpS = float(np.nanmedian(dfS.loc[mS, "capture"]))
        gvL = float(np.nanmean(dfL.loc[mL, "give_s"])); gvS = float(np.nanmean(dfS.loc[mS, "give_s"]))
        lab = f"{lo}-{hi if hi < 10**6 else ''}"
        P(f"{lab:<12}{int(mL.sum()):>7}{int(mS.sum()):>7}{tfL:>10.3f}{tfS:>10.3f}{tfS-tfL:>8.3f}"
          f"{cpL:>9.3f}{cpS:>9.3f}{cpS-cpL:>8.3f}{gvL:>10.3f}{gvS:>10.3f}{gvS-gvL:>8.3f}")

    H("PHASE 2 - THE FALSIFIERS F1 and F2. Session-block bootstrap, dependence preserved.")
    icc_t, keff_t, mbar = icc_oneway(np.concatenate([dfL["tfrac"], dfS["tfrac"]]),
                                     np.concatenate([dfL["sess"], dfS["sess"]]))
    icc_g, keff_g, _ = icc_oneway(np.concatenate([dfL["give_s"], dfS["give_s"]]),
                                  np.concatenate([dfL["sess"], dfS["sess"]]))
    K = len(dfL) + len(dfS)
    P(f"   trades K = {K:,}   mean trades per session {mbar:.2f}")
    P(f"   intra-session ICC (rho_bar) on t_MFE/dur   = {icc_t:.4f}  ->  K_eff = "
      f"K/(1+(m-1)*rho_bar) = {keff_t:,.0f}  ({100*keff_t/K:.0f}% of K)")
    P(f"   intra-session ICC (rho_bar) on giveback/s  = {icc_g:.4f}  ->  K_eff = {keff_g:,.0f}"
      f"  ({100*keff_g/K:.0f}% of K)")
    P("   Every interval below resamples WHOLE SESSIONS, so it already carries this dependence.")
    P("")
    tests = [
        ("F1  median(t_MFE/dur)", lambda d: float(np.median(d["tfrac"])), "<0 supports H_LEV"),
        ("    median(t_MFE) min", lambda d: float(np.median(d["t_mfe"])), "diagnostic"),
        ("    median(dur) min", lambda d: float(np.median(d["dur"])), "diagnostic"),
        ("F2  mean(giveback/sig)", lambda d: float(np.nanmean(d["give_s"])), ">0 supports H_LEV"),
        ("    median(capture)", lambda d: float(np.nanmedian(d["capture"])), "<0 supports H_LEV"),
        ("    mean(MFE/sigma)", lambda d: float(np.nanmean(d["mfe_s"])), "diagnostic"),
        ("    mean(final/sigma)", lambda d: float(np.nanmean(d["fin_s"])), "diagnostic"),
    ]
    P(f"{'statistic':<26}{'LONG':>10}{'SHORT':>10}{'SHORT-LONG':>12}{'boot 95% CI':>26}"
      f"{'excl 0':>8}   direction")
    P("-" * 116)
    f1_ok = f2_ok = None
    for lab, fn, note in tests:
        real, lo, hi, _ = session_bootstrap_diff(dfL, dfS, fn)
        ex = (lo > 0) or (hi < 0)
        P(f"{lab:<26}{fn(dfL):>10.4f}{fn(dfS):>10.4f}{real:>12.4f}"
          f"{f'[{lo:>+.4f}, {hi:>+.4f}]':>26}{('YES' if ex else 'no'):>8}   {note}")
        if lab.startswith("F1"):
            f1_ok = bool(ex and real < 0)
        if lab.startswith("F2"):
            f2_ok = bool(ex and real > 0)
    P("")
    P(f"   F1  'shorts reach MFE at a smaller FRACTION of the hold'     -> "
      f"{'SUPPORTED' if f1_ok else 'FALSIFIED (CI contains 0, or wrong sign)'}")
    P(f"   F2  'shorts give back MORE of the move at the exit'          -> "
      f"{'SUPPORTED' if f2_ok else 'FALSIFIED (CI contains 0, or wrong sign)'}")

    H("PHASE 3 - THE CONTINUATION CURVE. What does the NEXT minute of holding pay?")
    P("   For trades still open at minute tau: E[ points still to come from tau to the exit ].")
    P("   Exit at minute tau means the fill is the OPEN of bar ei+tau - the repo's own")
    P("   next-bar-open convention, so the rule is causal by construction.")
    pathsL = forward_prices(dfL, o, c)
    pathsS = forward_prices(dfS, o, c)
    curves = {}
    for nm, df, paths in (("LONG", dfL, pathsL), ("SHORT", dfS, pathsS)):
        rows = []
        d = df["d"].values.astype(float); epx = df["epx"].values
        dur = df["dur"].values; fin = df["fin"].values
        for tau in TAU_GRID:
            alive = dur > tau
            if alive.sum() < 30:
                break
            px = np.array([p[tau - 1] for p, a in zip(paths, alive) if a])
            e2 = epx[alive]; d2 = d[alive]
            sofar = d2 * (px - e2)
            fwd = fin[alive] - sofar
            rows.append(dict(tau=tau, n_alive=int(alive.sum()),
                             pct_alive=100.0 * alive.mean(),
                             sofar=float(sofar.mean()), fwd_mean=float(fwd.mean()),
                             fwd_med=float(np.median(fwd)),
                             fwd_total_pts=float(fwd.sum()),
                             fwd_total_usd=float(fwd.sum() * PV *
                                                 df["u"].values[alive].mean())))
        curves[nm] = pd.DataFrame(rows)
    P("")
    P(f"{'tau':>5} | {'LONG n':>8}{'%alive':>8}{'E[sofar]':>10}{'E[fwd]':>10}{'tot fwd $':>12}"
      f" | {'SHORT n':>8}{'%alive':>8}{'E[sofar]':>10}{'E[fwd]':>10}{'tot fwd $':>12}")
    P("-" * 116)
    for tau in TAU_GRID:
        rl = curves["LONG"][curves["LONG"]["tau"] == tau]
        rs = curves["SHORT"][curves["SHORT"]["tau"] == tau]
        if rl.empty and rs.empty:
            continue
        def f(r, k, w, p=2):
            return f"{r.iloc[0][k]:>{w}.{p}f}" if not r.empty else " " * w
        P(f"{tau:>5} | {f(rl,'n_alive',8,0)}{f(rl,'pct_alive',8,1)}{f(rl,'sofar',10)}"
          f"{f(rl,'fwd_mean',10)}{f(rl,'fwd_total_usd',12,0)}"
          f" | {f(rs,'n_alive',8,0)}{f(rs,'pct_alive',8,1)}{f(rs,'sofar',10)}"
          f"{f(rs,'fwd_mean',10)}{f(rs,'fwd_total_usd',12,0)}")
    for nm in curves:
        curves[nm].to_csv(os.path.join(OUT, f"holdtime_curve_{nm}.csv"), index=False)

    H("PHASE 3b - APPLY THE PREREGISTERED SELECTION RULE (no P&L has been computed yet)")
    P("   RULE (spec_holdtime.yaml, written before any result): T = the smallest 5-minute-rounded")
    P("   tau at which E[forward points | still open at tau] for SHORTS is <= 0 AND STAYS <= 0")
    P("   for every remaining tau on the grid. If no such tau exists the rule returns NO")
    P("   CANDIDATE and this wave has no exit to test - which is a result, not a failure to")
    P("   report.")
    cs = curves["SHORT"]
    T = None
    for i in range(len(cs)):
        if (cs["fwd_mean"].values[i:] <= 0).all():
            T = int(cs["tau"].values[i]); break
    cl = curves["LONG"]
    TL = None
    for i in range(len(cl)):
        if (cl["fwd_mean"].values[i:] <= 0).all():
            TL = int(cl["tau"].values[i]); break
    P("")
    P(f"   SHORT: the rule selects  T = {T}" + ("  minutes" if T else "  -> NO CANDIDATE"))
    P(f"   LONG : the same rule would select T_long = {TL}"
      + ("  minutes" if TL else "  -> no candidate on the long side either"))

    # --- the same rule on the FIRST HALF only, for the out-of-sample clause of F3 ---------------
    sd = pd.to_datetime(dfS["sdate"])
    cut = sd.sort_values().iloc[len(sd) // 2]
    P(f"   split date (median short trade) = {cut.date()}")
    h1 = dfS[sd.values <= np.datetime64(cut)].copy()
    paths_h1 = [pathsS[i] for i in np.flatnonzero(sd.values <= np.datetime64(cut))]
    rows = []
    d = h1["d"].values.astype(float); epx = h1["epx"].values
    dur = h1["dur"].values; fin = h1["fin"].values
    for tau in TAU_GRID:
        alive = dur > tau
        if alive.sum() < 30:
            break
        px = np.array([p[tau - 1] for p, a in zip(paths_h1, alive) if a])
        sofar = d[alive] * (px - epx[alive])
        rows.append(dict(tau=tau, fwd_mean=float((fin[alive] - sofar).mean())))
    ch1 = pd.DataFrame(rows)
    TH = None
    for i in range(len(ch1)):
        if (ch1["fwd_mean"].values[i:] <= 0).all():
            TH = int(ch1["tau"].values[i]); break
    P(f"   FIRST HALF ONLY ({len(h1)} short trades): the rule selects T_half = {TH}"
      + ("  minutes" if TH else "  -> NO CANDIDATE on the first half"))

    frozen = dict(T_short=T, T_long_same_rule=TL, T_first_half=TH,
                  split_date=str(cut.date()),
                  rule="smallest 5-min-rounded tau with E[fwd|alive] <= 0 for all larger tau",
                  grid=TAU_GRID, n_short=int(len(dfS)), n_long=int(len(dfL)),
                  F1_supported=f1_ok, F2_supported=f2_ok)
    with open(os.path.join(HERE, "T_FROZEN.json"), "w", encoding="utf-8") as f:
        json.dump(frozen, f, indent=2)
    P("")
    P(f"   -> T_FROZEN.json written. Stage 3 may now compute P&L and may not change T.")
    P(f"   [{_time.time()-t0:.0f}s]")

    with open(os.path.join(CACHE, "stage2.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
