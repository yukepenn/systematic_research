"""T2_P1SIZE01 - P1 SIZING lane. Executes runs/T2_P1SIZE01_20260831/spec.yaml.

Deliverables:
  D1  concentration reproduction on the EXECUTABLE object (2,439 NT8 trades)
  D2  tail-decay stress surface (frequency and size axes)
  A0/A1/A2 three frozen sizing arms + preregistered gate table

NOTHING is fitted. No order, no deploy, no CrossTrade, no read >= 2026-09-01.
"""
from __future__ import annotations

import os
import sys
import json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
SRC = os.path.join(ROOT, "research", "weekly_edge", "src")
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "vwap_flux_family", "src"))

RUN = os.path.join(ROOT, "runs", "T2_P1SIZE01_20260831")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

PV = 20.0
COMM_RT = 4.36
WIN, MINHIST = 250, 100
# PHASE: index offset from the NT8 FILL bar at which the causal features are read.
#   PHASE=0 -> information through fill_bar-1  = the PYTHON RESEARCH object's phase
#   PHASE=1 -> information through fill_bar-2  = the CERTIFIED NinjaScript's phase
# The spec's object under test is the EXECUTABLE object, so PHASE=1 is the correct
# reconstruction; PHASE=0 is retained and reported as a named diagnostic. See
# src/diag_phase.py, whose output selected PHASE by the preregistered G0b criterion alone.
PHASE = 1
FIXED_DD = 20245.0
NT8_TRADES = os.path.join(ROOT, "runs", "G2_AUG_INCUMBENT_READ_20260830", "out",
                          "p1_trades_full.csv")
LEDGER = os.path.join(ROOT, "runs", "RR_W001_ACTION_VALUE_LEDGER", "out", "ledger_p1pct.csv")
PARQ = os.path.join(ROOT, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet")

_fh = None


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    if _fh:
        _fh.write(s + "\n")
        _fh.flush()


# --------------------------------------------------------------------------- weekly metrics
def weekly(df, pnl_col="p"):
    return df.groupby("wk")[pnl_col].sum().sort_index()


def maxdd(w):
    eq = np.cumsum(np.asarray(w, float))
    return float(np.max(np.maximum.accumulate(np.concatenate([[0.0], eq])) -
                        np.concatenate([[0.0], eq])))


def fixed_dd_weekly(w):
    """Weekly $ after rescaling the whole stream so its own maxDD == FIXED_DD.

    Scale-invariant algebra: it is a pure change of unit, so it cannot be inflated by leverage.
    """
    w = np.asarray(w, float)
    dd = maxdd(w)
    if dd <= 0:
        return float("nan"), float("nan")
    k = FIXED_DD / dd
    return float(np.mean(w) * k), k


def share(v, frac):
    v = np.sort(np.asarray(v, float))[::-1]
    k = int(np.ceil(len(v) * frac))
    return k, float(v[:k].sum())


# --------------------------------------------------------------------------- substrate
def load_substrate():
    df = pd.read_parquet(PARQ)
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    t = df["time"].values.astype("datetime64[s]")
    o, h, l, c = (df[k].values.astype(float) for k in ("open", "high", "low", "close"))
    v = df["volume"].values.astype(float)
    n = len(df)
    fb = np.zeros(n, bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    lb = np.zeros(n, bool); lb[:-1] = fb[1:]; lb[-1] = True
    sid = np.cumsum(fb) - 1
    return dict(t=t, o=o, h=h, l=l, c=c, v=v, n=n, fb=fb, lb=lb, sid=sid,
                n_sess=int(sid[-1] + 1))


def causal_score_and_z(X, ent_i, atr_d, window=WIN, minhist=MINHIST):
    """Reproduce the certified causal 5-bit score AND the A1 rank composite AND A2's key.

    Every statistic at entry j uses ONLY entries [j-window, j).
    """
    feats = [("dist_open", +1, 2 / 3), ("prev_ret", -1, 1 / 3), ("runlen", +1, 0.9),
             ("dist_vwap", +1, 2 / 3), ("delta_mag", +1, 2 / 3)]
    vals = {k: np.asarray(X[k])[ent_i].astype(float) for k, _, _ in feats}
    av = np.asarray(atr_d)[ent_i].astype(float)
    N = len(ent_i)
    sc = np.full(N, np.nan)
    z = np.full(N, np.nan)
    relvol = np.full(N, np.nan)
    for j in range(N):
        if j < minhist:
            continue
        lo = max(0, j - window)
        s = 0
        pr = []
        for k, sgn, q in feats:
            hist = vals[k][lo:j]
            thr = np.nanquantile(hist, q)
            x = vals[k][j]
            s += (x >= thr) if sgn > 0 else (x <= thr)
            # percentile rank of the DIRECTIONALLY SIGNED feature among the same history
            hs = hist if sgn > 0 else -hist
            xs = x if sgn > 0 else -x
            pr.append(float(np.mean(hs <= xs)))
        sc[j] = s
        z[j] = float(np.mean(pr))
        m = np.nanmedian(av[lo:j])
        relvol[j] = av[j] / m if m > 0 else 1.0
    return sc, z, relvol, av


def causal_threshold_arm(key, sc, window=WIN, minhist=MINHIST):
    """Size 2 when `key` >= the causal (1 - r) quantile of key over the previous `window`
    entries, where r is the INCUMBENT's own realised size-2 rate over those same entries.

    Zero free parameters: window, minhist and the rate are all inherited from the incumbent.
    """
    N = len(key)
    size = np.ones(N, np.int64)
    inc2 = (sc >= 3).astype(float)
    for j in range(N):
        if j < minhist or not np.isfinite(key[j]):
            continue
        lo = max(0, j - window)
        r = float(np.nanmean(inc2[lo:j]))
        if not np.isfinite(r) or r <= 0:
            continue
        hist = key[lo:j]
        hist = hist[np.isfinite(hist)]
        if len(hist) < 20:
            continue
        thr = np.nanquantile(hist, 1.0 - r)
        if key[j] >= thr:
            size[j] = 2
    return size


# =============================================================================== MAIN
def main():
    global _fh
    _fh = open(os.path.join(OUT, "console.txt"), "w", encoding="utf-8")
    P("=" * 110)
    P("T2_P1SIZE01 - P1 SIZING LANE.  spec.yaml written before any arm P&L existed.")
    P("LIVE ENABLED = NO.  $0.  No order / deploy / CrossTrade / sealed read.")
    P("=" * 110)

    # ---------------------------------------------------------------- the executable object
    nt = pd.read_csv(NT8_TRADES, parse_dates=["et", "xt"])
    nt["p"] = nt["pnl"].astype(float)
    nt["per_ctr"] = nt["p"] / nt["qty"]
    nt["yr"] = nt["et"].dt.year
    P(f"\nEXECUTABLE OBJECT: {len(nt)} NT8 closed trades, "
      f"net ${nt.p.sum():,.2f}, ctrRT {int(nt.qty.sum())}, "
      f"qty2 {int((nt.qty == 2).sum())} ({(nt.qty == 2).mean() * 100:.1f}%)")

    # G0c - size-invariance necessary condition
    g0c1 = float(np.max(np.abs(nt["p"] - nt["qty"] * nt["per_ctr"])))
    g0c2 = float(np.max(np.abs(nt["comm"] - COMM_RT * nt["qty"])))
    P(f"G0c size-invariance identity: max|pnl - qty*per_ctr| = {g0c1:.2e} ; "
      f"max|comm - 4.36*qty| = {g0c2:.2e}")

    # ================================================================ D1 CONCENTRATION
    P("\n" + "=" * 110)
    P("D1  CONCENTRATION ON THE EXECUTABLE OBJECT (2022-01-03 .. 2026-08-30, NT8 cost basis)")
    P("=" * 110)
    v = nt["p"].to_numpy()
    net = v.sum()
    rows = []
    for f in (0.01, 0.05, 0.10, 0.20):
        k, s = share(v, f)
        rows.append((f"top {f*100:.0f}%", k, s, 100 * s / net))
    P(f"{'bucket':<10}{'n':>7}{'sum $':>16}{'% of net':>12}")
    for a, b, c_, d in rows:
        P(f"{a:<10}{b:>7}{c_:>16,.2f}{d:>11.1f}%")
    k10, s10 = share(v, 0.10)
    rest = net - s10
    P(f"\nnet                 = ${net:,.2f}")
    P(f"top 10% ({k10} trades) = ${s10:,.2f}  = {100*s10/net:.1f}% of net")
    P(f"the other {len(v)-k10} trades sum ${rest:,.2f}")
    P(f"median trade        = ${np.median(v):,.2f}")
    P(f"mean trade          = ${np.mean(v):,.2f}")
    P(f"win rate            = {100*np.mean(v > 0):.1f}%")
    sv = np.sort(v)[::-1]
    P(f"ex-top-1 net        = ${net - sv[0]:,.2f}   (largest single ${sv[0]:,.2f})")
    P(f"ex-top-5 net        = ${net - sv[:5].sum():,.2f}")
    P(f"ex-top-10 net       = ${net - sv[:10].sum():,.2f}")
    P(f"ex-top-25 net       = ${net - sv[:25].sum():,.2f}")
    P("\nleave-one-calendar-year-out (drop the year, sum the rest):")
    for y in sorted(nt.yr.unique()):
        sub = nt[nt.yr != y]
        P(f"  ex-{y}: n={len(sub):5d}  net ${sub.p.sum():>12,.2f}")
    P("\nby year:")
    for y in sorted(nt.yr.unique()):
        sub = nt[nt.yr == y]
        kk, ss = share(sub.p.to_numpy(), 0.10)
        P(f"  {y}: n={len(sub):5d}  net ${sub.p.sum():>12,.2f}  qty2 "
          f"{100*(sub.qty==2).mean():5.1f}%  top10% share "
          f"{100*ss/sub.p.sum() if sub.p.sum()!=0 else float('nan'):7.1f}%")

    # weekly concentration
    wk = weekly(nt)
    wsv = np.sort(wk.to_numpy())[::-1]
    n22 = 22
    P(f"\nweeks: {len(wk)}   positive {100*np.mean(wk > 0):.1f}%   "
      f"top-{n22} weeks = {100*wsv[:n22].sum()/wk.sum():.1f}% of net")
    P(f"maxDD (weekly, ISO week on session date) = ${maxdd(wk):,.2f}")
    fd, kk = fixed_dd_weekly(wk)
    P(f"weekly $ raw = ${wk.mean():,.2f} ; at fixed ${FIXED_DD:,.0f} DD = ${fd:,.2f} "
      f"(scale {kk:.4f})")

    # ================================================================ D2 TAIL DECAY SURFACE
    P("\n" + "=" * 110)
    P("D2  TAIL-DECAY STRESS SURFACE   (TAIL := top decile of trades by realised P&L, n=%d)" % k10)
    P("=" * 110)
    thr = sv[k10 - 1]
    tail_mask = v >= thr
    P(f"tail threshold = ${thr:,.2f} ; tail n = {tail_mask.sum()} ; "
      f"non-tail n = {(~tail_mask).sum()}")
    base_wk = wk.copy()
    base_ev, _ = float(base_wk.mean()), None
    base_dd = maxdd(base_wk)
    P(f"\nBASELINE: weekly EV ${base_wk.mean():,.2f}  maxDD ${base_dd:,.2f}  "
      f"net ${net:,.2f}")

    # --- SIZE decay: deterministic
    P("\nAXIS 1 - TAIL SIZE DECAY (every tail trade's P&L x (1-f); frequency unchanged)")
    P(f"{'f':>6}{'net $':>16}{'weekly EV $':>14}{'maxDD $':>14}{'EV vs base':>12}"
      f"{'DD vs base':>12}")
    size_rows = []
    for f in (0.0, 0.25, 0.50, 0.75, 1.0):
        vv = v.copy()
        vv[tail_mask] = vv[tail_mask] * (1 - f)
        d2 = nt.assign(p2=vv)
        w2 = d2.groupby("wk")["p2"].sum().sort_index()
        size_rows.append((f, vv.sum(), w2.mean(), maxdd(w2)))
        P(f"{f:>6.2f}{vv.sum():>16,.0f}{w2.mean():>14,.0f}{maxdd(w2):>14,.0f}"
          f"{100*(w2.mean()/base_wk.mean()-1):>11.1f}%"
          f"{100*(maxdd(w2)/base_dd-1):>11.1f}%")
    # breakeven f on the size axis (linear in f)
    tail_sum = v[tail_mask].sum()
    f_be_size = net / tail_sum if tail_sum > 0 else float("nan")
    P(f"breakeven f (weekly EV = 0) on the SIZE axis = {f_be_size:.3f}  "
      f"(net {net:,.0f} / tail {tail_sum:,.0f})")

    # --- FREQUENCY decay: Monte Carlo, tail event replaced by a non-tail draw
    P("\nAXIS 2 - TAIL FREQUENCY DECAY (each tail trade independently fails with prob f;")
    P("         on failure its P&L is replaced by a draw from the NON-TAIL distribution)")
    rng = np.random.default_rng(20260831)
    nontail = v[~tail_mask]
    wkkey = nt["wk"].to_numpy()
    uk = pd.Index(sorted(pd.unique(wkkey)))
    wix = uk.get_indexer(wkkey)
    NMC = 2000
    P(f"{'f':>6}{'weekly EV $':>14}{'[p5':>12}{'p95]':>12}{'maxDD $':>14}"
      f"{'[p5':>12}{'p95]':>12}{'P(net<=0)':>11}")
    freq_rows = []
    for f in (0.0, 0.25, 0.50, 0.75, 1.0):
        evs = np.empty(NMC); dds = np.empty(NMC); nets = np.empty(NMC)
        ti = np.flatnonzero(tail_mask)
        for b in range(NMC):
            vv = v.copy()
            fail = rng.random(len(ti)) < f
            nf = int(fail.sum())
            if nf:
                vv[ti[fail]] = rng.choice(nontail, size=nf, replace=False)
            wsum = np.bincount(wix, weights=vv, minlength=len(uk))
            evs[b] = wsum.mean(); dds[b] = maxdd(wsum); nets[b] = vv.sum()
        freq_rows.append((f, evs.mean(), dds.mean()))
        P(f"{f:>6.2f}{evs.mean():>14,.0f}{np.percentile(evs,5):>12,.0f}"
          f"{np.percentile(evs,95):>12,.0f}{dds.mean():>14,.0f}"
          f"{np.percentile(dds,5):>12,.0f}{np.percentile(dds,95):>12,.0f}"
          f"{np.mean(nets <= 0):>10.1%}")
    # breakeven f on the frequency axis (expected value is linear in f)
    mean_nontail = nontail.mean()
    slope = (v[tail_mask] - mean_nontail).sum()
    f_be_freq = net / slope if slope > 0 else float("nan")
    P(f"breakeven f (expected weekly EV = 0) on the FREQUENCY axis = {f_be_freq:.3f}")
    P(f"  (mean non-tail trade ${mean_nontail:,.2f}; mean tail trade ${v[tail_mask].mean():,.2f})")

    # ================================================================ ARMS
    P("\n" + "=" * 110)
    P("SIZING ARMS - window 2022-01-02 .. 2026-07-31 (the substrate physically ends there)")
    P("=" * 110)
    D = load_substrate()
    P(f"substrate {D['n']:,} bars / {D['n_sess']:,} sessions, "
      f"{D['t'][0]} .. {D['t'][-1]}")
    from we_fastctx import fast_build_context, fast_intraday_features
    ifeat = fast_intraday_features(D)
    X = fast_build_context(D, ifeat=ifeat)
    atr_l = ifeat[2]                      # ATR14 already lagged one bar, in POINTS
    atr_d = atr_l * PV                    # dollars per contract

    sub = nt[nt["et"] <= pd.Timestamp("2026-07-31 17:00")].reset_index(drop=True)
    tt = sub["et"].values.astype("datetime64[s]")
    ent_i = np.searchsorted(D["t"], tt)
    ok = (ent_i < D["n"]) & (D["t"][np.minimum(ent_i, D["n"] - 1)] == tt)
    P(f"\nNT8 trades with et <= 2026-07-31: {len(sub)} ; exact bar match {int(ok.sum())}")
    sub = sub[ok].reset_index(drop=True)
    ent_i = ent_i[ok]
    qty_nt8 = sub["qty"].to_numpy()
    per_all = (sub["pnl"] / sub["qty"]).to_numpy()

    # ---- PHASE determination: which bar does each engine read the score at?
    P("\n" + "-" * 110)
    P("PHASE DIAGNOSTIC - at which bar is the causal quality score evaluated?")
    P("  Python gfills:   want = dir[i-1], fill at o[i], size read at index i   -> info thru i-1")
    P("  NinjaScript:     decide at bar b from the lagged cache, fill at open of b+1")
    P("-" * 110)
    P(f"{'features read at':<24}{'size == NT8 qty':>18}{'reconstructed net $':>22}")
    phase_scores = {}
    for lag in (0, 1, 2):
        sc_l, _, _, _ = causal_score_and_z(X, np.maximum(ent_i - lag, 0), atr_d)
        sc_l = np.where(np.isnan(sc_l), 0.0, sc_l)
        sz_l = 1 + (sc_l >= 3).astype(np.int64)
        phase_scores[lag] = (sc_l, sz_l)
        P(f"{'fill_bar - ' + str(lag):<24}"
          f"{100*np.mean(sz_l == qty_nt8):>17.2f}%{np.sum(per_all * sz_l):>22,.0f}")
    P(f"{'NT8 ACTUAL':<24}{'100.00%':>18}{sub['pnl'].sum():>22,.0f}")
    P(f"\n>>> PHASE = {PHASE} adopted (spec object = the EXECUTABLE object; selection is by the "
      f"preregistered G0b criterion alone, not by P&L).")

    sc, z, relvol, av = causal_score_and_z(X, np.maximum(ent_i - PHASE, 0), atr_d)
    sc0 = np.where(np.isnan(sc), 0.0, sc)      # the .cs leaves lastScore = 0 during warm-up
    sA0 = 1 + (sc0 >= 3).astype(np.int64)
    sc_research = phase_scores[0][0]
    sA0_research = phase_scores[0][1]

    # ---- G0a / G0b verification
    agree = float(np.mean(sA0 == sub["qty"].to_numpy()))
    P(f"\nG0b  recomputed size vs NT8 qty: agreement {100*agree:.2f}% "
      f"({int((sA0 == sub['qty'].to_numpy()).sum())}/{len(sub)})"
      f"   spec >=99% -> {'PASS' if agree >= 0.99 else 'FAIL'}")
    lg = pd.read_csv(LEDGER, parse_dates=["decision_ts"])
    lgm = lg.set_index("decision_ts")["causal_quality_score"]
    j = sub["et"].map(lgm)
    have = j.notna().to_numpy()
    a0 = float(np.mean(sc0[have] == j.to_numpy()[have]))
    P(f"G0a  recomputed score vs RR_W001 ledger causal_quality_score on the "
      f"{int(have.sum())} scored joined rows: agreement {100*a0:.2f}%")

    P("\nscore histogram (recomputed, on the arm window):")
    for s_ in range(6):
        P(f"  score {s_}: n={int((sc0 == s_).sum()):5d} "
          f"({100*np.mean(sc0 == s_):5.1f}%)  mean per-contract P&L "
          f"${sub['per_ctr'].to_numpy()[sc0 == s_].mean():>10,.2f}  "
          f"win {100*np.mean(sub['per_ctr'].to_numpy()[sc0 == s_] > 0):4.1f}%")

    # ---- arms
    sA1 = causal_threshold_arm(z, sc0)
    keyA2 = np.where(np.isfinite(relvol) & (relvol > 0), sc0 / np.maximum(relvol, 1e-9), np.nan)
    sA2 = causal_threshold_arm(keyA2, sc0)
    keyRAW = np.where(np.isfinite(av) & (av > 0), sc0 / np.maximum(av, 1e-9), np.nan)
    sRAW = causal_threshold_arm(keyRAW, sc0)

    per = sub["per_ctr"].to_numpy()
    wkk = sub["wk"].to_numpy()
    yr = sub["et"].dt.year.to_numpy()
    arms = {"A0_INCUMBENT": sA0, "A1_SMOOTH": sA1, "A2_VOLN": sA2,
            "A2raw_DIAGNOSTIC": sRAW, "A0phase0_DIAGNOSTIC": sA0_research,
            "FLAT1_DIAGNOSTIC": np.ones(len(sA0), np.int64),
            "NT8_ACTUAL_QTY": qty_nt8}

    def arm_frame(s):
        return pd.DataFrame(dict(wk=wkk, p=per * s, s=s, yr=yr, per=per))

    P("\n" + "-" * 110)
    P("ARM SUMMARY (NT8 cost basis $4.36/ctrRT already inside per-contract P&L)")
    P("-" * 110)
    P(f"{'arm':<20}{'net $':>14}{'ctrRT':>8}{'mean sz':>9}{'sz2 %':>8}"
      f"{'wk raw $':>10}{'maxDD $':>11}{'fixDD wk $':>12}{'wk+%':>7}{'skew':>7}")
    res = {}
    for name, s in arms.items():
        fr = arm_frame(s)
        w = weekly(fr)
        fd_, _ = fixed_dd_weekly(w)
        res[name] = dict(frame=fr, w=w, net=float(fr.p.sum()), ctr=int(s.sum()),
                         mean_sz=float(s.mean()), sz2=float(np.mean(s == 2)),
                         wk_raw=float(w.mean()), dd=maxdd(w), fixdd=fd_,
                         wkpos=float(np.mean(w > 0)), skew=float(pd.Series(w).skew()))
        r = res[name]
        P(f"{name:<20}{r['net']:>14,.0f}{r['ctr']:>8}{r['mean_sz']:>9.4f}"
          f"{100*r['sz2']:>7.1f}%{r['wk_raw']:>10,.0f}{r['dd']:>11,.0f}"
          f"{r['fixdd']:>12,.0f}{100*r['wkpos']:>6.1f}%{r['skew']:>7.2f}")

    # size-2 overlap with the incumbent
    P("\noverlap of the second contract with the incumbent's:")
    for name in ("A1_SMOOTH", "A2_VOLN", "A2raw_DIAGNOSTIC", "A0phase0_DIAGNOSTIC"):
        s = arms[name]
        both = int(np.sum((s == 2) & (sA0 == 2)))
        P(f"  {name:<20} size-2 n={int((s==2).sum()):4d}  shared with A0 {both:4d}  "
          f"Jaccard {both/max(1,int(np.sum((s==2)|(sA0==2)))):.3f}")

    P("\nsize-2 rate BY YEAR (era-tilt check):")
    P(f"{'arm':<20}" + "".join(f"{y:>9}" for y in sorted(set(yr))))
    for name, s in arms.items():
        P(f"{name:<20}" + "".join(
            f"{100*np.mean(s[yr == y] == 2):>8.1f}%" for y in sorted(set(yr))))

    # ---- cost lines
    P("\ncost-line sensitivity (extra modelled spread per ctrRT, on top of the NT8 basis):")
    P(f"{'arm':<20}{'+$0.00':>14}{'+$14.44':>14}{'+$20.65':>14}")
    for name, s in arms.items():
        line = []
        for extra in (0.0, 14.44, 20.65):
            fr = pd.DataFrame(dict(wk=wkk, p=per * s - extra * s))
            w = weekly(fr)
            fd_, _ = fixed_dd_weekly(w)
            line.append(fd_)
        P(f"{name:<20}" + "".join(f"{x:>14,.0f}" for x in line))

    # ---- tail preservation
    P("\ntail preservation (top decile of each arm's OWN trade P&L):")
    P(f"{'arm':<20}{'top10% share':>14}{'top1% share':>13}{'median trade':>14}"
      f"{'top-22wk share':>16}")
    for name, s in arms.items():
        pv_ = per * s
        _, s10_ = share(pv_, 0.10)
        _, s1_ = share(pv_, 0.01)
        w = res[name]["w"].to_numpy()
        ws = np.sort(w)[::-1]
        P(f"{name:<20}{100*s10_/pv_.sum():>13.1f}%{100*s1_/pv_.sum():>12.1f}%"
          f"{np.median(pv_):>14,.2f}{100*ws[:22].sum()/w.sum():>15.1f}%")

    # ---- mandatory tail audit for EVERY headline number
    P("\n" + "-" * 110)
    P("TAIL AUDIT (mandatory for every headline). fixDD = weekly $ after rescaling to a "
      f"${FIXED_DD:,.0f} maxDD.")
    P("-" * 110)
    P(f"{'arm':<21}{'fixDD':>9}{'ex-t1trade':>11}{'ex-t5trade':>11}{'ex-t1wk':>9}"
      f"{'ex-t5wk':>9}" + "".join(f"{'ex' + str(y)[2:]:>8}" for y in sorted(set(yr))))
    for name, s in arms.items():
        pv_ = per * s
        o_ = np.argsort(pv_)[::-1]
        row = [res[name]["fixdd"]]
        for kdrop in (1, 5):
            m = np.ones(len(pv_), bool); m[o_[:kdrop]] = False
            w_ = pd.DataFrame(dict(wk=wkk[m], p=pv_[m])).groupby("wk")["p"].sum().sort_index()
            row.append(fixed_dd_weekly(w_)[0])
        w = res[name]["w"]
        ow = np.argsort(w.to_numpy())[::-1]
        for kdrop in (1, 5):
            ww = w.drop(w.index[ow[:kdrop]])
            row.append(fixed_dd_weekly(ww)[0])
        for y in sorted(set(yr)):
            m = yr != y
            w_ = pd.DataFrame(dict(wk=wkk[m], p=pv_[m])).groupby("wk")["p"].sum().sort_index()
            row.append(fixed_dd_weekly(w_)[0])
        P(f"{name:<21}" + f"{row[0]:>9,.0f}{row[1]:>11,.0f}{row[2]:>11,.0f}"
          f"{row[3]:>9,.0f}{row[4]:>9,.0f}" + "".join(f"{x:>8,.0f}" for x in row[5:]))
    P("\nper-year fixDD weekly $ (each year rescaled to its own maxDD - shape, not level):")
    P(f"{'arm':<21}" + "".join(f"{y:>9}" for y in sorted(set(yr))))
    for name, s in arms.items():
        pv_ = per * s
        cells = []
        for y in sorted(set(yr)):
            m = yr == y
            w_ = pd.DataFrame(dict(wk=wkk[m], p=pv_[m])).groupby("wk")["p"].sum().sort_index()
            cells.append(fixed_dd_weekly(w_)[0])
        P(f"{name:<21}" + "".join(f"{x:>9,.0f}" for x in cells))

    # ---- the layer's value ON THE EXECUTABLE OBJECT (A0 vs FLAT1), with a null
    P("\n--- THE QUALITY-SIZING LAYER'S VALUE ON THE EXECUTABLE OBJECT (A0 vs FLAT size 1) ---")
    f1 = res["FLAT1_DIAGNOSTIC"]
    P(f"A0 fixDD ${res['A0_INCUMBENT']['fixdd']:,.2f}  vs  "
      f"FLAT1 ${f1['fixdd']:,.2f}   = "
      f"{res['A0_INCUMBENT']['fixdd']/f1['fixdd']:.3f}x "
      f"({100*(res['A0_INCUMBENT']['fixdd']/f1['fixdd']-1):+.1f}%)")
    P(f"positive weeks {100*res['A0_INCUMBENT']['wkpos']:.1f}% vs {100*f1['wkpos']:.1f}%  "
      f"| maxDD ${res['A0_INCUMBENT']['dd']:,.0f} vs ${f1['dd']:,.0f}  "
      f"| skew {res['A0_INCUMBENT']['skew']:.2f} vs {f1['skew']:.2f}")
    P("NOTE: on THIS object the box is PER CONTRACT (W98), so the trade schedule is")
    P("      bit-identical across sizing arms. W83 measured the layer on the ABS-box object")
    P("      (run_we_w35.fills_qexit, spnl += pnl, TOTAL) where changing size ALSO moves the")
    P("      halt, so W83's +19.3% / -2.3pp is not a pure sizing measurement.")

    # ================================================================ GATES
    P("\n" + "=" * 110)
    P("PREREGISTERED GATE TABLE")
    P("=" * 110)
    a0 = res["A0_INCUMBENT"]
    gates = []
    rngn = np.random.default_rng(11)

    for name in ("A1_SMOOTH", "A2_VOLN"):
        r = res[name]
        s = arms[name]
        P(f"\n--- {name} ---")
        # G1
        g1a = abs(r["mean_sz"] / a0["mean_sz"] - 1)
        g1b = abs(r["ctr"] / a0["ctr"] - 1)
        g1 = (g1a <= 0.02) and (g1b <= 0.02)
        # G2
        ratio = r["fixdd"] / a0["fixdd"]
        g2 = ratio >= 1.05
        # G3
        pv_ = per * s
        _, s10a = share(per * sA0, 0.10)
        _, s10b = share(pv_, 0.10)
        sha = s10a / (per * sA0).sum()
        shb = s10b / pv_.sum()
        g3 = (shb >= 0.80 * sha) and (len(pv_) == len(per))
        # G4 size-label permutation null
        nullv = np.empty(1000)
        for b in range(1000):
            sp = rngn.permutation(s)
            w = pd.DataFrame(dict(wk=wkk, p=per * sp)).groupby("wk")["p"].sum().sort_index()
            nullv[b], _ = fixed_dd_weekly(w)
        p95 = float(np.nanpercentile(nullv, 95))
        pct = float(np.mean(nullv < r["fixdd"]))
        g4 = r["fixdd"] > p95
        # G5 rolling 24-month windows + LOYO
        dts = sub["et"].to_numpy()
        starts = pd.date_range("2022-01-01", "2024-08-01", periods=25)
        wins_beat = 0
        nwin = 0
        for st in starts:
            en = st + pd.DateOffset(months=24)
            m = (sub["et"] >= st) & (sub["et"] < en)
            if m.sum() < 100:
                continue
            nwin += 1
            wa, _ = fixed_dd_weekly(pd.DataFrame(dict(wk=wkk[m], p=(per * sA0)[m]))
                                    .groupby("wk")["p"].sum().sort_index())
            wb, _ = fixed_dd_weekly(pd.DataFrame(dict(wk=wkk[m], p=(per * s)[m]))
                                    .groupby("wk")["p"].sum().sort_index())
            wins_beat += int(wb > wa)
        loyo = 0
        for y in sorted(set(yr)):
            m = yr != y
            wa, _ = fixed_dd_weekly(pd.DataFrame(dict(wk=wkk[m], p=(per * sA0)[m]))
                                    .groupby("wk")["p"].sum().sort_index())
            wb, _ = fixed_dd_weekly(pd.DataFrame(dict(wk=wkk[m], p=(per * s)[m]))
                                    .groupby("wk")["p"].sum().sort_index())
            loyo += int(wb > wa)
        g5 = (nwin > 0 and wins_beat / nwin >= 0.60) and (loyo >= 4)
        # G6 stationary bootstrap on the weekly DIFFERENCE at each arm's own fixed-DD scale
        wa_s = a0["w"] * (FIXED_DD / a0["dd"])
        wb_s = r["w"] * (FIXED_DD / r["dd"])
        idx = wa_s.index.union(wb_s.index)
        dvec = (wb_s.reindex(idx).fillna(0) - wa_s.reindex(idx).fillna(0)).to_numpy()
        NB, mb = 10000, 4
        L = len(dvec)
        bs = np.empty(NB)
        rb = np.random.default_rng(7)
        for b in range(NB):
            out = np.empty(L)
            i = 0
            while i < L:
                st = rb.integers(0, L)
                bl = 1 + rb.geometric(1.0 / mb)
                take = min(bl, L - i)
                sl = (np.arange(st, st + take) % L)
                out[i:i + take] = dvec[sl]
                i += take
            bs[b] = out.mean()
        lo90, hi90 = np.percentile(bs, [5, 95])
        g6 = (lo90 > 0) or (hi90 < 0)
        tstat = dvec.mean() / (dvec.std(ddof=1) / np.sqrt(L))
        P(f"G1 budget      mean size {r['mean_sz']:.4f} vs {a0['mean_sz']:.4f} "
          f"(d {100*g1a:.2f}%)  ctrRT {r['ctr']} vs {a0['ctr']} (d {100*g1b:.2f}%)"
          f"   spec |d|<=2.00%   -> {'PASS' if g1 else 'FAIL'}")
        P(f"G2 money       fixDD wk ${r['fixdd']:,.2f} vs ${a0['fixdd']:,.2f} "
          f"= {ratio:.4f}x            spec >=1.05x       -> {'PASS' if g2 else 'FAIL'}")
        P(f"G3 tail        top-10% share {100*shb:.1f}% vs A0 {100*sha:.1f}% "
          f"(ratio {shb/sha:.3f}); trades {len(pv_)} vs {len(per)}   spec >=0.80 "
          f"-> {'PASS' if g3 else 'FAIL'}")
        P(f"G4 null        fixDD ${r['fixdd']:,.2f} vs own-size-permutation p95 "
          f"${p95:,.2f} (pctile {100*pct:.1f})   spec >p95  -> {'PASS' if g4 else 'FAIL'}")
        P(f"G5 stability   rolling24m beats A0 {wins_beat}/{nwin} "
          f"({100*wins_beat/max(1,nwin):.0f}%); LOYO {loyo}/5   spec >=60% and >=4/5 "
          f"-> {'PASS' if g5 else 'FAIL'}")
        P(f"G6 bootstrap   weekly diff mean ${dvec.mean():,.2f}; stationary-bootstrap 90% CI "
          f"[{lo90:,.2f}, {hi90:,.2f}]; (t {tstat:.2f} diagnostic only) -> "
          f"{'PASS' if g6 else 'FAIL'}")
        verdict = "CANDIDATE" if all([g1, g2, g3, g4, g5, g6]) else "FAIL"
        P(f"VERDICT {name}: {verdict}  "
          f"(G1 {int(g1)} G2 {int(g2)} G3 {int(g3)} G4 {int(g4)} G5 {int(g5)} G6 {int(g6)})")
        gates.append(dict(arm=name, G1=bool(g1), G2=bool(g2), G3=bool(g3), G4=bool(g4),
                          G5=bool(g5), G6=bool(g6), verdict=verdict,
                          fixdd=r["fixdd"], a0_fixdd=a0["fixdd"], ratio=ratio,
                          null_p95=p95, null_pct=pct, roll=f"{wins_beat}/{nwin}",
                          loyo=loyo, ci=[float(lo90), float(hi90)],
                          diff_mean=float(dvec.mean())))

    # ---- extra: is the incumbent itself above its own permutation null on this window?
    P("\n--- A0 against its own size-label permutation null (context for G4) ---")
    nullv = np.empty(1000)
    rr = np.random.default_rng(99)
    for b in range(1000):
        sp = rr.permutation(sA0)
        w = pd.DataFrame(dict(wk=wkk, p=per * sp)).groupby("wk")["p"].sum().sort_index()
        nullv[b], _ = fixed_dd_weekly(w)
    P(f"A0 fixDD ${a0['fixdd']:,.2f}  null mean ${np.nanmean(nullv):,.2f}  "
      f"p95 ${np.nanpercentile(nullv,95):,.2f}  pctile {100*np.mean(nullv < a0['fixdd']):.1f}")

    # ---- August out-of-arm note
    aug = nt[nt["et"] > pd.Timestamp("2026-07-31 17:00")]
    P(f"\nAugust 2026 (OUT OF THE ARM WINDOW - the substrate cannot see it): "
      f"{len(aug)} trades, net ${aug.p.sum():,.2f}")

    # ---- artifacts
    pd.DataFrame(dict(et=sub["et"], xt=sub["xt"], per_ctr=per, wk=wkk, yr=yr,
                      qty_nt8=qty_nt8, score=sc0, score_research=sc_research,
                      z=z, relvol=relvol, atr_d=av,
                      sA0=sA0, sA1=sA1, sA2=sA2, sRAW=sRAW,
                      sA0_research=sA0_research)).to_csv(
        os.path.join(OUT, "arm_ledger.csv"), index=False)
    pd.DataFrame(gates).to_json(os.path.join(OUT, "gates.json"), orient="records", indent=1)
    P("\nartifacts: out/console.txt out/arm_ledger.csv out/gates.json")
    P("LIVE ENABLED = NO.  $0 spent.  Nothing promoted.")
    _fh.close()


if __name__ == "__main__":
    main()
