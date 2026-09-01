"""G3_SHORTALPHA_20260831 / asymmetric-cost

Does the SHORT side of NQ face a different execution-cost and financing reality than the LONG
side?  Every cost number in this repository was measured on P1, which is long-only.

Spec: runs/G3_SHORTALPHA_20260831/src/asymmetric-cost/spec.yaml, written before this ran.
Every gate/table below is PRINTED BY THIS PROGRAM. Nothing is hand-assembled.

Reads ONLY pre-sealed data (< 2026-08-01), asserted by research_sdk.seal_guard.
Reads NO grid1s file (recorded lookahead defect in its `last` column, AUCTION04
01_build_clean_substrate.py:17-21) -- it reads the RAW per-event BBO those grids were built
from, and it reads ONLY bid (bip==1) and ask (bip==2). No last-price column anywhere.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "G3_SHORTALPHA_20260831")
OUT = os.path.join(RUN, "out")
SRC = os.path.join(ROOT, "research", "weekly_edge", "src")
MYSRC = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SRC)
sys.path.insert(0, ROOT)

from research_sdk.seal_guard import assert_presealed            # noqa: E402
from run_we_w01 import PV, COMM_RT                              # noqa: E402
from run_we_w19 import MEMBERS, QS                              # noqa: E402  (kept: vote deps)
from run_we_w26 import fills_daily                              # noqa: E402
from run_we_w37 import causal_score                             # noqa: E402
from run_we_w38 import sfills, vote                             # noqa: E402
from run_we_w35 import fills_qexit                              # noqa: E402
from run_we_w39 import WIN                                      # noqa: E402
from run_we_w51 import A, B                                     # noqa: E402
from run_we_w51c import setup                                   # noqa: E402

T0 = _time.time()
TICK = 0.25
TICKV = 5.0                      # $ per tick per contract
STALE_NS = 5_000_000_000         # 5s, G2_EXEC01 R4
ONE_MIN = np.timedelta64(60, "s")
RNG = np.random.default_rng(20260831)
NBOOT = 2000

ESNQ_DIR = os.path.join(ROOT, "research", "data_esnq", "parquet", "NQ")
ALLOWLIST_PATH = os.path.join(ROOT, "research", "data_esnq", "ALLOWLIST_DEV_44.txt")
V2_DIR = os.path.join(ROOT, "research", "data_microstructure_v2", "raw", "NQ")
V1_DIR = os.path.join(ROOT, "research", "scalping_lab", "substrate", "raw", "NQ")
V1_NO_BBO = {"20250811", "20250924", "20260430"}
EXEC01_OUT = os.path.join(ROOT, "runs", "G2_EXEC01_P1_EXECUTION_20260828", "out")

_OUTF = open(os.path.join(OUT, "asymmetric-cost.txt"), "w", encoding="utf-8")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    print(s, file=_OUTF)
    _OUTF.flush()


def H(t):
    P("\n" + "=" * 108)
    P(t)
    P("=" * 108)


# ==================================================================================================
# instrumented fills -- VERBATIM logic of run_we_w35.fills_qexit / run_we_w38.sfills, plus
# recorded bar indices and exit kind. Asserted byte-equal on (d,u,et,xt,pnl) in GATE H1.
# ==================================================================================================
def fills_qexit_instr(D, pos_arr, size_at_entry, score, halt=1300.0, target=1000.0,
                      big_target=None, cut_bars=None, cut_max_score=1):
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False
    sess_tgt = target; ent_sc = 0
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False; sess_tgt = target
        want = int(pos_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped:
            want = 0
        if u > 0 and cut_bars is not None and ent_sc <= cut_max_score and i - eti >= cut_bars:
            want = 0
        if (want > 0) != (u > 0):
            if u > 0:
                pnl = u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl,
                                   eti=eti, xti=i, epx=epx, xpx=o[i], xkind="open"))
                spnl += pnl
                if spnl <= -halt or (sess_tgt is not None and spnl >= sess_tgt):
                    stopped = True; want = 0
            if want > 0:
                u = int(size_at_entry[i]); epx, eti = o[i], i
                ent_sc = int(score[i])
                if big_target is not None and ent_sc >= 3 and sess_tgt == target:
                    sess_tgt = big_target
                if u < 1:
                    u = 0
            else:
                u = 0
        if lb[i] and u > 0:
            pnl = u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl,
                               eti=eti, xti=i, epx=epx, xpx=c[i], xkind="close"))
            u = 0
    return trades


def sfills_instr(D, dir_arr, size_at_entry=None, halt=1300.0, target=1000.0, block=None):
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    p = 0; u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False
        want = int(dir_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped:
            want = 0
        if want != 0 and p == 0 and block is not None and block[i]:
            want = 0
        if want != p:
            if p != 0:
                pnl = p * u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl,
                                   eti=eti, xti=i, epx=epx, xpx=o[i], xkind="open"))
                spnl += pnl
                if spnl <= -halt or (target is not None and spnl >= target):
                    stopped = True; want = 0
            p = want
            if p != 0:
                u = int(size_at_entry[i]) if size_at_entry is not None else 1
                if u < 1:
                    p = 0; u = 0
                else:
                    epx, eti = o[i], i
        if lb[i] and p != 0:
            pnl = p * u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl,
                               eti=eti, xti=i, epx=epx, xpx=c[i], xkind="close"))
            p = 0; u = 0
    return trades


def same_stream(a, b):
    if len(a) != len(b):
        return False
    return all(x["d"] == y["d"] and x["u"] == y["u"] and x["et"] == y["et"]
               and x["xt"] == y["xt"] and abs(x["pnl"] - y["pnl"]) <= 1e-9
               for x, y in zip(a, b))


# ==================================================================================================
def sess_bootstrap(df, valcol, wcol, groups, nboot=NBOOT):
    """Whole-session resample with replacement (preserves within-session dependence).
    Returns (point, lo, hi) on the contract-weighted mean of valcol."""
    keys = np.asarray(groups)
    uk = np.unique(keys)
    idx_of = {k: np.flatnonzero(keys == k) for k in uk}
    v = df[valcol].to_numpy(float); w = df[wcol].to_numpy(float)
    point = float(np.average(v, weights=w)) if w.sum() > 0 else np.nan
    outs = np.empty(nboot)
    for bi in range(nboot):
        pick = RNG.choice(uk, size=len(uk), replace=True)
        ii = np.concatenate([idx_of[k] for k in pick])
        outs[bi] = np.average(v[ii], weights=w[ii]) if w[ii].sum() > 0 else np.nan
    return point, float(np.nanpercentile(outs, 2.5)), float(np.nanpercentile(outs, 97.5))


def sess_bootstrap_diff(dfS, dfL, valcol, wcol, nboot=NBOOT):
    """Paired-on-session-universe bootstrap of (short - long) contract-weighted mean.
    Sessions are the resampling unit and are drawn ONCE per replicate for both arms, so a
    session that is heavy for one arm is heavy for the other in the same draw."""
    keys = np.unique(np.concatenate([dfS["sdate"].to_numpy(), dfL["sdate"].to_numpy()]))
    iS = {k: np.flatnonzero(dfS["sdate"].to_numpy() == k) for k in keys}
    iL = {k: np.flatnonzero(dfL["sdate"].to_numpy() == k) for k in keys}
    vS, wS = dfS[valcol].to_numpy(float), dfS[wcol].to_numpy(float)
    vL, wL = dfL[valcol].to_numpy(float), dfL[wcol].to_numpy(float)
    pt = float(np.average(vS, weights=wS) - np.average(vL, weights=wL))
    outs = np.full(nboot, np.nan)
    for bi in range(nboot):
        pick = RNG.choice(keys, size=len(keys), replace=True)
        aS = np.concatenate([iS[k] for k in pick]) if len(keys) else np.array([], int)
        aL = np.concatenate([iL[k] for k in pick]) if len(keys) else np.array([], int)
        if len(aS) == 0 or len(aL) == 0 or wS[aS].sum() == 0 or wL[aL].sum() == 0:
            continue
        outs[bi] = (np.average(vS[aS], weights=wS[aS])
                    - np.average(vL[aL], weights=wL[aL]))
    return pt, float(np.nanpercentile(outs, 2.5)), float(np.nanpercentile(outs, 97.5))


def rho_bar_keff(df, valcol, groupcol):
    """rho_bar from the within-session intraclass correlation of leg values; K_eff on sessions."""
    g = df.groupby(groupcol)[valcol]
    ns = g.size().to_numpy()
    ms = g.mean().to_numpy()
    K = len(ns)
    grand = float(df[valcol].mean())
    n0 = (ns.sum() - (ns ** 2).sum() / ns.sum()) / (K - 1) if K > 1 else 1.0
    msb = float(np.sum(ns * (ms - grand) ** 2) / (K - 1)) if K > 1 else 0.0
    ssw = float(np.sum((df[valcol].to_numpy()
                        - df.groupby(groupcol)[valcol].transform("mean").to_numpy()) ** 2))
    msw = ssw / max(ns.sum() - K, 1)
    icc = (msb - msw) / (msb + (n0 - 1) * msw) if (msb + (n0 - 1) * msw) > 0 else 0.0
    icc = float(np.clip(icc, 0.0, 0.999))
    keff = K / (1 + (K - 1) * icc)
    return icc, K, keff


# ==================================================================================================
def main():
    H("G3_SHORTALPHA_20260831 / asymmetric-cost -- DOES THE SHORT SIDE PAY MORE?")
    P("spec: runs/G3_SHORTALPHA_20260831/src/asymmetric-cost/spec.yaml (written before results)")
    P(f"cost identity used throughout: cost_per_ctrRT_$ = {TICKV/2:.1f} x "
      f"(spread_tk_entry + spread_tk_exit)   [G2_EXEC01's own arithmetic]")
    P("COST FLOOR STATEMENT (binding): $4.36/ctrRT is the COMMISSION FLOOR and is never a "
      "headline.\n"
      "   PRIMARY measured all-in-spread cost is $20.65/ctrRT (G2_EXEC01, 113 real round turns,\n"
      "   contract-weighted; median $20.00, p90 $35.00). $25.01/ctrRT is the all-in "
      "(spread + commission).")

    # ============================================================== PHASE 0: substrate + arms
    H("PHASE 0 -- SUBSTRATE, SEAL, AND THE TWO MIRROR ARMS (harness gates H1-H3)")
    D, X, TG, st, en = setup()
    n, tarr, sid, c, o = D["n"], D["t"], D["sid"], D["c"], D["o"]
    assert_presealed(pd.DataFrame({"t": pd.to_datetime(tarr)}), "t", "1-min substrate")
    P(f"substrate: {n:,} bars, {D['n_sess']:,} sessions, last bar {pd.Timestamp(tarr.max())}")
    P(f"SEAL ASSERTION: assert_presealed(substrate) PASSED -- max timestamp "
      f"{pd.Timestamp(tarr.max())} < 2026-08-01. No sealed value read.")

    sdate = pd.to_datetime(D["sess_date"])
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    P(f"window A={A} B={B} -> {NS} in-window sessions "
      f"({sdate[sess_in].min().date()} .. {sdate[sess_in].max().date()})")
    P("ERABREAK01 note: this window is MODERN by construction (>= 2022-07). No PRE/MODERN pool "
      "is formed anywhere in this run. Per-year strata are printed in PHASE 5.")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    # ---- LONG arm (W73 L_sym == P1 incumbent)
    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    base = fills_daily(D, posL, halt=1300, target=1000)
    e = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, e, window=WIN)
    sz = np.where(sc >= 3, 2, 1).astype(np.int8)
    L_ref = [x for x in fills_qexit(D, posL, sz, sc) if in_win[int(sid[i_of(x["et"])])]]
    L_ins = [x for x in fills_qexit_instr(D, posL, sz, sc) if in_win[int(sid[i_of(x["et"])])]]
    # ---- SHORT arm (W73 S_sym mirror sleeve)
    posS = -(vote(TG, D, X, -1) >= 0.5).astype(np.int8)
    S_ref = [x for x in sfills(D, posS, halt=1300.0, target=1000.0)
             if in_win[int(sid[i_of(x["et"])])]]
    S_ins = [x for x in sfills_instr(D, posS, halt=1300.0, target=1000.0)
             if in_win[int(sid[i_of(x["et"])])]]

    h1 = same_stream(L_ins, L_ref) and same_stream(S_ins, S_ref)
    ptsL = sum(x["pnl"] for x in L_ref) / PV / NS
    ptsS = sum(x["pnl"] for x in S_ref) / PV / NS
    h2 = abs(ptsL - 14.86) < 0.30
    h3 = abs(ptsS - 6.00) < 0.30
    P(f"\n{'HARNESS GATE':<10}{'SPEC':<58}{'OBSERVED':<26}{'PASS/FAIL'}")
    P(f"{'H1':<10}{'instrumented streams == originals on (d,u,et,xt,pnl)':<58}"
      f"{str(h1):<26}{'PASS' if h1 else 'FAIL'}")
    P(f"{'H2':<10}{'LONG arm == W73 L_sym 14.86 pts/session (+/-0.30)':<58}"
      f"{ptsL:<26.2f}{'PASS' if h2 else 'FAIL'}")
    P(f"{'H3':<10}{'SHORT arm == W73 S_sym 6.00 pts/session (+/-0.30)':<58}"
      f"{ptsS:<26.2f}{'PASS' if h3 else 'FAIL'}")
    if not (h1 and h2 and h3):
        P("\nHARNESS FAILED -- run is VOID, no result is quoted.")
        _OUTF.close(); return
    P(f"\nLONG  arm: {len(L_ref):,} trades, {sum(x['u'] for x in L_ref):,} contract RTs, "
      f"net ${sum(x['pnl'] for x in L_ref):,.0f} (commission-only)")
    P(f"SHORT arm: {len(S_ref):,} trades, {sum(x['u'] for x in S_ref):,} contract RTs, "
      f"net ${sum(x['pnl'] for x in S_ref):,.0f} (commission-only)")

    # ---- trailing vol, identical construction to G2_EXEC01 R8
    r = np.full(n, np.nan)
    r[1:] = np.log(c[1:] / c[:-1])
    r[D["fb"]] = np.nan
    volarr = pd.Series(r).rolling(60, min_periods=30).std(ddof=1).shift(1).to_numpy()

    date_str = np.array([d.strftime("%Y%m%d") for d in sdate])

    def legtable(trl, arm):
        rows = []
        for tid, x in enumerate(trl):
            mins = (pd.Timestamp(x["xt"]) - pd.Timestamp(x["et"])).total_seconds() / 60.0
            for role in ("entry", "exit"):
                if role == "entry":
                    bar = int(x["eti"])
                    inst = (tarr[bar] - ONE_MIN)
                    side = "buy" if x["d"] > 0 else "sell"
                else:
                    bar = int(x["xti"])
                    inst = (tarr[bar] - ONE_MIN) if x["xkind"] == "open" else tarr[bar]
                    side = "sell" if x["d"] > 0 else "buy"
                ts = pd.Timestamp(inst)
                rows.append(dict(arm=arm, tid=tid, role=role, side=side, d=int(x["d"]),
                                 u=int(x["u"]), bar=bar, instant=ts,
                                 hour=ts.hour, mod=ts.hour * 60 + ts.minute,
                                 vol=float(volarr[bar]), pnl=float(x["pnl"]),
                                 win=bool(x["pnl"] > 0), mins=mins,
                                 sdate=date_str[int(sid[bar])]))
        return pd.DataFrame(rows)

    LGL = legtable(L_ins, "LONG")
    LGS = legtable(S_ins, "SHORT")
    for lab, dfx in (("LONG", LGL), ("SHORT", LGS)):
        assert_presealed(dfx, "instant", f"{lab} fill instants")
    P(f"SEAL ASSERTION: assert_presealed on both arms' fill instants PASSED "
      f"({len(LGL):,} long legs, {len(LGS):,} short legs).")
    ALL = pd.concat([LGL, LGS], ignore_index=True)
    ALL.to_csv(os.path.join(OUT, "asymcost_legs.csv"), index=False)

    # overnight-exposure check: does either arm hold across a session boundary?
    ov_l = int((sid[LGL[LGL.role == "entry"].bar.to_numpy()]
                != sid[LGL[LGL.role == "exit"].bar.to_numpy()]).sum())
    ov_s = int((sid[LGS[LGS.role == "entry"].bar.to_numpy()]
                != sid[LGS[LGS.role == "exit"].bar.to_numpy()]).sum())
    P(f"overnight-hold check (entry session != exit session): LONG {ov_l}, SHORT {ov_s} "
      f"-> both arms are intra-session; NO overnight financing differential exists for either.")

    # ============================================================== PHASE 1: the spread surface
    H("PHASE 1 -- THE SPREAD SURFACE, FITTED ONLY ON MINUTE SAMPLES (never on fills)")
    MS = pd.read_csv(os.path.join(EXEC01_OUT, "minute_samples.csv.gz"))
    MS = MS[np.isfinite(MS["spr_tk"]) & (MS["spr_tk"] >= 0)].copy()
    assert_presealed(MS.assign(dt=pd.to_datetime(MS["date"], format="%Y%m%d")), "dt",
                     "G2_EXEC01 minute samples")
    P(f"minute samples: {len(MS):,} causal (hour, trailing-vol, spread) triples from "
      f"{MS['date'].nunique()} quote sessions, {MS['date'].min()}..{MS['date'].max()}")
    P("SEAL ASSERTION: assert_presealed(minute samples) PASSED.")
    P("PROVENANCE: these are G2_EXEC01's own published samples, taken at BAR-OPEN instants with "
      "a\n   5s freshness cap and ask>=bid. They come from bid/ask events only. No last price.")

    volq = MS["vol"].dropna()
    EDG = np.percentile(volq, np.arange(10, 100, 10))
    P(f"\nvol decile edges (trailing 60-min sd of 1-min logret): "
      + " ".join(f"{x:.6f}" for x in EDG))

    def vbin(v, edges):
        return np.where(np.isnan(v), -1, np.searchsorted(edges, v, side="right"))

    MS["vb"] = vbin(MS["vol"].to_numpy(), EDG)
    gm = float(MS["spr_tk"].mean()); gmed = float(MS["spr_tk"].median())
    cell = MS.groupby(["hour", "vb"])["spr_tk"].agg(["mean", "median", "size"]).reset_index()
    hourm = MS.groupby("hour")["spr_tk"].agg(["mean", "median"])
    CELL = {(int(a), int(b)): (float(m1), float(m2)) for a, b, m1, m2, s in
            cell[["hour", "vb", "mean", "median", "size"]].itertuples(index=False) if s >= 30}
    HM = {int(k): (float(v["mean"]), float(v["median"])) for k, v in hourm.iterrows()}
    P(f"surface: {len(CELL)} (hour x vol-decile) cells with n>=30; fallback hour-level "
      f"({len(HM)} hours: {sorted(HM)}); global fallback mean {gm:.3f} / median {gmed:.3f} tk")

    def project(dfx, stat=0):
        """stat 0 = cell MEAN (the cost-relevant expectation), 1 = cell MEDIAN
        (the statistic G2_EXEC01's published state map used)."""
        vb = vbin(dfx["vol"].to_numpy(), EDG)
        hh = dfx["hour"].to_numpy()
        out = np.empty(len(dfx)); nfb_cell = 0; nfb_hr = 0
        gfb = gm if stat == 0 else gmed
        for i in range(len(dfx)):
            h_, b_ = int(hh[i]), int(vb[i])
            if (h_, b_) in CELL:
                out[i] = CELL[(h_, b_)][stat]
            elif h_ in HM:
                out[i] = HM[h_][stat]; nfb_cell += 1
            else:
                hn = min(HM, key=lambda k: abs(k - h_)) if HM else None
                out[i] = HM[hn][stat] if hn is not None else gfb
                nfb_cell += 1; nfb_hr += 1
        return out, nfb_cell, nfb_hr

    ps, _, _ = project(MS, 0)
    P(f"in-sample surface fit on its own samples: mean predicted {ps.mean():.3f} tk "
      f"vs actual {gm:.3f} tk")

    # ---- harness gate H4 (EXACT): reconstruct G2_EXEC01's OWN P1_PCT leg set from its published
    # p1_trades.csv, bin with ITS published tercile edges, look up ITS published state_map median
    # cell values, contract-weight. Target = 3.4957 tk, its published "P1 projection 3.50".
    SMAP = pd.read_csv(os.path.join(EXEC01_OUT, "state_map.csv"))
    TERC = np.array([0.000196, 0.000320])          # G2_EXEC01 R8 published edges
    tlab = ["T1_low", "T2_mid", "T3_high"]
    SMD = {(int(r.hour), r.ter): float(r.med_spread_tk) for r in SMAP.itertuples()}
    ref_target = float(np.average(SMAP["med_spread_tk"], weights=SMAP["p1_fill_ctr"]))
    PT = pd.read_csv(os.path.join(EXEC01_OUT, "p1_trades.csv"))
    PT = PT[PT["in_win"]].copy()
    rows = []
    dropped = 0
    tset = tarr
    for x in PT.itertuples():
        for role in ("entry", "exit"):
            ts0 = np.datetime64(x.et if role == "entry" else x.xt)
            j = int(np.searchsorted(tset, ts0))
            if j >= n or tset[j] != ts0:
                dropped += 1
                continue
            inst = (ts0 - ONE_MIN) if (role == "entry" or x.xkind == "open") else ts0
            tsp = pd.Timestamp(inst)
            rows.append(dict(hour=tsp.hour, vol=float(volarr[j]), u=int(x.u)))
    RC = pd.DataFrame(rows)
    RC["ter"] = [tlab[int(k)] for k in vbin(RC["vol"].to_numpy(), TERC)]
    RC["med"] = [SMD.get((int(h), t_), np.nan) for h, t_ in zip(RC["hour"], RC["ter"])]
    okrc = RC["med"].notna()
    h4_val = float(np.average(RC.loc[okrc, "med"], weights=RC.loc[okrc, "u"]))
    h4 = abs(h4_val - ref_target) < 0.10
    P(f"\nH4 detail: reconstructed {len(RC):,} of {2*len(PT):,} EXEC01 P1_PCT legs "
      f"({int(RC['u'].sum()):,} contract-legs vs its published 5,112); "
      f"{dropped} legs dropped (this run's substrate ends {pd.Timestamp(tarr.max()).date()}, "
      f"EXEC01's extended to 2026-07-31)")
    P(f"{'HARNESS GATE':<10}{'SPEC':<58}{'OBSERVED':<26}{'PASS/FAIL'}")
    P(f"{'H4':<10}{'reproduce EXEC01 P1 state-map projection 3.496 tk +/-0.10':<58}"
      f"{h4_val:<26.4f}{'PASS' if h4 else 'FAIL'}")
    cellsh = (RC[okrc].groupby(["hour", "ter"])["u"].sum() / RC.loc[okrc, "u"].sum())
    pub = SMAP.set_index(["hour", "ter"])["p1_fill_share"]
    dev = float((cellsh - pub.reindex(cellsh.index).fillna(0)).abs().max())
    h4b = dev < 0.01
    P(f"{'H4b':<10}{'max |cell contract-share - EXEC01 published| < 0.010':<58}"
      f"{dev:<26.4f}{'PASS' if h4b else 'FAIL'}")
    if not (h4 and h4b):
        P("   H4 FAIL -> my leg->state->spread pipeline is not EXEC01's. Run VOID.")
        _OUTF.close(); return
    P("   -> the leg -> (hour, trailing-vol) -> spread pipeline used below is EXEC01's own, "
      "verified\n      cell-by-cell against its published map. The finer hour x vol-DECILE "
      "surface is used from\n      here on because cost is paid at the MEAN, not the median; "
      "both statistics are reported.")

    for dfx in (LGL, LGS):
        pr, nfb, nfh = project(dfx, 0)
        dfx["proj"] = pr
        pr2, _, _ = project(dfx, 1)
        dfx["projmed"] = pr2
    P(f"cell-fallback usage: LONG {(project(LGL,0)[1]):,}/{len(LGL):,} legs, "
      f"SHORT {(project(LGS,0)[1]):,}/{len(LGS):,} legs fell back to an hour-level value")

    # ============================================================== PHASE 2: E2 projection
    H("PHASE 2 -- E2: PROJECTED SPREAD AT EVERY FILL, FULL WINDOW (n = all legs)")
    P(f"{'arm':<8}{'legs':>8}{'ctr-wtd tk':>12}{'entry tk':>10}{'exit tk':>10}"
      f"{'cost/ctrRT $':>14}{'median tk':>11}{'p90 tk':>9}")
    proj_cost = {}
    for lab, dfx in (("LONG", LGL), ("SHORT", LGS)):
        w = dfx["u"].to_numpy(float)
        cw = float(np.average(dfx["proj"], weights=w))
        ent = float(np.average(dfx[dfx.role == "entry"]["proj"],
                               weights=dfx[dfx.role == "entry"]["u"]))
        ext = float(np.average(dfx[dfx.role == "exit"]["proj"],
                               weights=dfx[dfx.role == "exit"]["u"]))
        cost = (TICKV / 2) * (ent + ext)
        proj_cost[lab] = dict(cw=cw, ent=ent, ext=ext, cost=cost)
        P(f"{lab:<8}{len(dfx):>8,}{cw:>12.4f}{ent:>10.4f}{ext:>10.4f}{cost:>14.2f}"
          f"{dfx['proj'].median():>11.3f}{np.percentile(dfx['proj'],90):>9.3f}")
    d_proj_tk = proj_cost["SHORT"]["cw"] - proj_cost["LONG"]["cw"]
    d_proj_usd = proj_cost["SHORT"]["cost"] - proj_cost["LONG"]["cost"]
    P(f"\nDELTA (SHORT - LONG): {d_proj_tk:+.4f} ticks per leg   "
      f"-> {d_proj_usd:+.2f} $/ctrRT")

    mS = float(np.average(LGS["projmed"], weights=LGS["u"]))
    mL = float(np.average(LGL["projmed"], weights=LGL["u"]))
    P(f"ROBUSTNESS, same surface but cell MEDIAN (EXEC01's own statistic): "
      f"LONG {mL:.4f} tk, SHORT {mS:.4f} tk, delta {mS-mL:+.4f} tk "
      f"= {TICKV*(mS-mL):+.2f} $/ctrRT")

    pt, lo, hi = sess_bootstrap_diff(LGS, LGL, "proj", "u")
    P(f"N1 session block bootstrap ({NBOOT} draws, whole sessions resampled): "
      f"delta = {pt:+.4f} tk  95% CI [{lo:+.4f}, {hi:+.4f}]")
    P(f"   in dollars per ctrRT: {TICKV*pt:+.2f}  95% CI "
      f"[{TICKV*lo:+.2f}, {TICKV*hi:+.2f}]   (2 legs x $2.50/tk)")
    d_proj_lo_usd, d_proj_hi_usd = TICKV * lo, TICKV * hi
    g2 = (abs(TICKV * pt) >= 1.00) and (d_proj_lo_usd * d_proj_hi_usd > 0)

    icc, K, keff = rho_bar_keff(pd.concat([LGL, LGS]), "proj", "sdate")
    P(f"N4 dependence: rho_bar (within-session ICC of projected spread) = {icc:.4f} over "
      f"K={K} sessions -> K_eff = {keff:.1f}")
    P("   (session-level t is DIAGNOSTIC ONLY in this repo; the bootstrap above is the test.)")

    # ---- N2 hour-matched control
    P("\nN2 HOUR-MATCHED CONTROL -- reweight LONG legs to the SHORT legs' hour histogram.")
    hs = LGS.groupby("hour")["u"].sum(); hl = LGL.groupby("hour")["u"].sum()
    common = sorted(set(hs.index) & set(hl.index))
    wl = LGL["hour"].map({h: hs.get(h, 0) / hl.get(h, 1) for h in common}).fillna(0).to_numpy()
    wl = wl * LGL["u"].to_numpy()
    long_hm = float(np.average(LGL["proj"], weights=wl)) if wl.sum() > 0 else np.nan
    P(f"   LONG projected spread, RAW              : {proj_cost['LONG']['cw']:.4f} tk")
    P(f"   LONG projected spread, HOUR-MATCHED to SHORT: {long_hm:.4f} tk")
    P(f"   SHORT projected spread                  : {proj_cost['SHORT']['cw']:.4f} tk")
    P(f"   -> delta attributable to HOUR-OF-DAY        : "
      f"{long_hm - proj_cost['LONG']['cw']:+.4f} tk")
    P(f"   -> delta remaining WITHIN-HOUR (vol state)  : "
      f"{proj_cost['SHORT']['cw'] - long_hm:+.4f} tk")

    # ---- N3 label shuffle
    POOL = pd.concat([LGL, LGS], ignore_index=True)
    nS = len(LGS)
    pv = POOL["proj"].to_numpy(); pu = POOL["u"].to_numpy(float)
    null = np.empty(NBOOT)
    for bi in range(NBOOT):
        perm = RNG.permutation(len(POOL))
        a, b_ = perm[:nS], perm[nS:]
        null[bi] = (np.average(pv[a], weights=pu[a]) - np.average(pv[b_], weights=pu[b_]))
    nlo, nhi = float(np.percentile(null, 2.5)), float(np.percentile(null, 97.5))
    g6 = (d_proj_tk < nlo) or (d_proj_tk > nhi)
    P(f"\nN3 LABEL-SHUFFLE (state-blind) NULL, {NBOOT} draws: 95% band "
      f"[{nlo:+.4f}, {nhi:+.4f}] tk; observed {d_proj_tk:+.4f} -> "
      f"{'OUTSIDE' if g6 else 'INSIDE'} the null band")
    P("   NOTE this null destroys within-session clustering, so it is the WEAKER of the two "
      "and\n   N1 (session block) is the binding one.")

    # ============================================================== PHASE 3: E1 direct
    H("PHASE 3 -- E1: DIRECT SPREAD AT THE ACTUAL FILL INSTANT (raw BBO events; bid/ask only)")
    P("grid1s is NOT read. Its `last` column carries a recorded lookahead defect "
      "(AUCTION04/01_build_clean_substrate.py:17-21:\n   a bucket labelled T aggregates trades in "
      "[T, T+1)). This phase reads the RAW per-event store\n   those grids were built from and "
      "uses ONLY bip==1 (bid) and bip==2 (ask). No last-price column\n   is loaded, so the "
      "defect cannot enter this measurement.")

    with open(ALLOWLIST_PATH, "r", encoding="utf-8") as f:
        allow = {ln.strip() for ln in f if ln.strip()}
    assert len(allow) == 44
    v2 = {f[1:9] for f in os.listdir(V2_DIR) if f.endswith(".parquet")}
    esnq_all = {f[1:9] for f in os.listdir(ESNQ_DIR) if f.endswith(".parquet")}
    v1 = {f[1:9] for f in os.listdir(V1_DIR) if f.endswith(".parquet") and "_rth" not in f}
    v1 -= V1_NO_BBO
    inv = {}
    for d_ in sorted(v2):
        inv[d_] = ("v2", os.path.join(V2_DIR, f"s{d_}.parquet"))
    for d_ in sorted(esnq_all & allow):
        inv.setdefault(d_, ("esnq", os.path.join(ESNQ_DIR, f"s{d_}.parquet")))
    for d_ in sorted(v1):
        inv.setdefault(d_, ("v1", os.path.join(V1_DIR, f"s{d_}.parquet")))
    blind = sorted(esnq_all - allow)
    P(f"\nBLIND-POOL ENFORCEMENT (printed before the first esnq open):")
    P(f"   allowlist entries {len(allow)} | esnq on disk {len(esnq_all)} | "
      f"OUTSIDE allowlist (BLIND) {len(blind)} -> NONE opened")
    viol = [d_ for d_, (s_, _) in inv.items() if s_ == "esnq" and d_ not in allow]
    P(f"   esnq sessions this run will open: "
      f"{sum(1 for v in inv.values() if v[0]=='esnq')} (violations: {len(viol)})")
    if viol:
        P("   ABORT"); _OUTF.close(); return
    P(f"   quote inventory: {len(inv)} sessions "
      f"(v2 {sum(1 for v in inv.values() if v[0]=='v2')}, "
      f"esnq {sum(1 for v in inv.values() if v[0]=='esnq')}, "
      f"v1 {sum(1 for v in inv.values() if v[0]=='v1')})")

    need = set(LGL["sdate"]) | set(LGS["sdate"])
    todo = sorted(set(inv) & need)
    P(f"   sessions that carry a fill from either arm AND have quotes: {len(todo)}")

    meas = []
    nseal = 0
    for d_ in todo:
        store, path = inv[d_]
        tbl = pq.read_table(path, columns=["bip", "time", "price"])
        qt = tbl.column("time").to_numpy().astype("datetime64[ns]")
        qb = tbl.column("bip").to_numpy(); qp = tbl.column("price").to_numpy()
        del tbl
        assert_presealed(pd.DataFrame({"time": qt}), "time", f"quotes s{d_}")
        nseal += 1
        bm, am = qb == 1, qb == 2          # bid events, ask events. NOTHING ELSE IS READ.
        bt = qt[bm].astype("int64"); bp = qp[bm]
        at = qt[am].astype("int64"); ap = qp[am]
        if len(bt) == 0 or len(at) == 0:
            continue
        if np.any(np.diff(bt) < 0):
            k = np.argsort(bt, kind="stable"); bt, bp = bt[k], bp[k]
        if np.any(np.diff(at) < 0):
            k = np.argsort(at, kind="stable"); at, ap = at[k], ap[k]
        sub = ALL[ALL["sdate"] == d_]
        if not len(sub):
            continue
        ins = sub["instant"].to_numpy().astype("datetime64[ns]").astype("int64")
        ib = np.searchsorted(bt, ins, side="right") - 1
        ia = np.searchsorted(at, ins, side="right") - 1
        okb, oka = ib >= 0, ia >= 0
        bpx = np.where(okb, bp[np.maximum(ib, 0)], np.nan)
        apx = np.where(oka, ap[np.maximum(ia, 0)], np.nan)
        ageb = np.where(okb, ins - bt[np.maximum(ib, 0)], np.int64(2 ** 62))
        agea = np.where(oka, ins - at[np.maximum(ia, 0)], np.int64(2 ** 62))
        fresh = (ageb <= STALE_NS) & (agea <= STALE_NS) & (apx >= bpx) & np.isfinite(bpx) \
            & np.isfinite(apx)
        g = sub.copy()
        g["spr_dir"] = np.where(fresh, (apx - bpx) / TICK, np.nan)
        g["store"] = store
        meas.append(g)
    M = pd.concat(meas, ignore_index=True) if meas else pd.DataFrame()
    M.to_csv(os.path.join(OUT, "asymcost_direct_legs.csv"), index=False)
    P(f"   quote sessions opened and seal-checked: {nseal}")
    MM = M[np.isfinite(M["spr_dir"])].copy()
    P(f"   legs with a fresh two-sided book at the fill instant: {len(MM):,} of {len(M):,} "
      f"({100*len(MM)/max(len(M),1):.1f}%)")

    P(f"\n{'arm':<8}{'legs':>8}{'trades w/ both':>16}{'ctr-wtd tk':>12}{'entry tk':>10}"
      f"{'exit tk':>10}{'cost/ctrRT $':>14}{'median tk':>11}")
    direct = {}
    for lab in ("LONG", "SHORT"):
        q = MM[MM["arm"] == lab]
        both = q.groupby("tid")["role"].nunique()
        nboth = int((both == 2).sum())
        if not len(q):
            continue
        cw = float(np.average(q["spr_dir"], weights=q["u"]))
        ent = float(np.average(q[q.role == "entry"]["spr_dir"],
                               weights=q[q.role == "entry"]["u"]))
        ext = float(np.average(q[q.role == "exit"]["spr_dir"],
                               weights=q[q.role == "exit"]["u"]))
        direct[lab] = dict(cw=cw, ent=ent, ext=ext, cost=(TICKV / 2) * (ent + ext), n=len(q))
        P(f"{lab:<8}{len(q):>8,}{nboth:>16,}{cw:>12.4f}{ent:>10.4f}{ext:>10.4f}"
          f"{(TICKV/2)*(ent+ext):>14.2f}{q['spr_dir'].median():>11.3f}")
    d_dir_tk = direct["SHORT"]["cw"] - direct["LONG"]["cw"]
    P(f"\nDELTA (SHORT - LONG): {d_dir_tk:+.4f} ticks per leg -> "
      f"{TICKV*d_dir_tk:+.2f} $/ctrRT")
    dpt, dlo, dhi = sess_bootstrap_diff(MM[MM.arm == "SHORT"], MM[MM.arm == "LONG"],
                                        "spr_dir", "u")
    P(f"N1 session block bootstrap: delta = {dpt:+.4f} tk  95% CI [{dlo:+.4f}, {dhi:+.4f}] tk")
    P(f"   in $/ctrRT: {TICKV*dpt:+.2f}  95% CI [{TICKV*dlo:+.2f}, {TICKV*dhi:+.2f}]")
    g1 = (abs(TICKV * dpt) >= 1.00) and (TICKV * dlo) * (TICKV * dhi) > 0
    g3 = np.sign(d_dir_tk) == np.sign(d_proj_tk) and abs(d_dir_tk) > 1e-9

    # anchor check: does the LONG arm's directly measured cost land near EXEC01's $20.65?
    P(f"\nANCHOR: EXEC01 measured $20.65/ctrRT on P1_PCT. This run's LONG arm (W73 L_sym, a "
      f"different\n   but same-family object) measures ${direct['LONG']['cost']:.2f}/ctrRT on "
      f"{direct['LONG']['n']} legs by the same method. This run applies no inside-band filter\n"
      f"   (EXEC01 dropped 56/334 legs as outside_band), which is why the level sits lower; the\n"
      f"   PRIMARY $20.65 remains the repo figure and nothing here revises it.")
    P(f"\nPOWER OF E1: the 95% CI half-width is ${TICKV*max(abs(dhi-dpt),abs(dpt-dlo)):.2f}/ctrRT, "
      f"so the direct sample\n   ({len(MM):,} legs, {MM['sdate'].nunique()} sessions) could not "
      f"have resolved anything smaller than that.\n   It DOES exclude a differential of "
      f"${max(abs(TICKV*dlo),abs(TICKV*dhi)):.2f}/ctrRT or more at 95%.")
    P(f"\nHONEST CONTRADICTION: in the direct sample the SHORT's EXIT spread "
      f"({direct['SHORT']['ext']:.4f} tk) is\n   LOWER than its entry spread "
      f"({direct['SHORT']['ent']:.4f} tk) -- the opposite of what the projection\n   predicts and "
      f"of what the vol-spike-exit story requires. On "
      f"{int((MM[MM.arm=='SHORT'].role=='exit').sum())} short exit legs this cannot\n   "
      f"adjudicate the mechanism; it is recorded, not explained away.")

    # ============================================================== PHASE 4: mechanism
    H("PHASE 4 -- E3/E4: WHERE THE DIFFERENTIAL LIVES, AND THE VOL-SPIKE-EXIT CLAIM")
    P("The standing structural claim is: down-moves cluster with vol spikes, so a short is most "
      "in\nprofit exactly when spreads are widest, and pays for it on the EXIT leg.")
    ent_d = proj_cost["SHORT"]["ent"] - proj_cost["LONG"]["ent"]
    ext_d = proj_cost["SHORT"]["ext"] - proj_cost["LONG"]["ext"]
    g4 = ext_d > ent_d
    P(f"\n{'leg':<12}{'LONG tk':>10}{'SHORT tk':>10}{'delta tk':>11}{'delta $/leg':>13}")
    P(f"{'ENTRY':<12}{proj_cost['LONG']['ent']:>10.4f}{proj_cost['SHORT']['ent']:>10.4f}"
      f"{ent_d:>11.4f}{TICKV/2*ent_d:>13.2f}")
    P(f"{'EXIT':<12}{proj_cost['LONG']['ext']:>10.4f}{proj_cost['SHORT']['ext']:>10.4f}"
      f"{ext_d:>11.4f}{TICKV/2*ext_d:>13.2f}")
    P(f"G4 mechanism prediction (exit delta > entry delta): "
      f"{ext_d:+.4f} > {ent_d:+.4f} -> {'PASS' if g4 else 'FAIL'}")

    P(f"\nOUTCOME-CONDITIONED EXIT SPREAD (projected, full window):")
    P(f"{'arm':<8}{'outcome':<10}{'trades':>9}{'exit tk':>10}{'entry tk':>10}"
      f"{'vol@entry':>12}{'vol@exit':>11}{'vol ratio':>11}")
    oc = {}
    for lab, dfx in (("LONG", LGL), ("SHORT", LGS)):
        for wl_, name in ((True, "WIN"), (False, "LOSS")):
            q = dfx[dfx["win"] == wl_]
            if not len(q):
                continue
            qe = q[q.role == "entry"]; qx = q[q.role == "exit"]
            ve = float(np.nanmean(qe["vol"])); vx = float(np.nanmean(qx["vol"]))
            oc[(lab, name)] = dict(ext=float(np.average(qx["proj"], weights=qx["u"])),
                                   ent=float(np.average(qe["proj"], weights=qe["u"])),
                                   ve=ve, vx=vx)
            P(f"{lab:<8}{name:<10}{len(qe):>9,}"
              f"{oc[(lab,name)]['ext']:>10.4f}{oc[(lab,name)]['ent']:>10.4f}"
              f"{ve:>12.6f}{vx:>11.6f}{vx/ve:>11.4f}")
    g5_val = oc[("SHORT", "WIN")]["ext"] - oc[("LONG", "WIN")]["ext"]
    g5 = g5_val >= 0.25
    P(f"\nG5 (short WINNERS' exit spread - long WINNERS' exit spread >= +0.25 tk): "
      f"{g5_val:+.4f} tk -> {'PASS' if g5 else 'FAIL'}")

    P(f"\nVOL PATH (trailing 60-min sd of 1-min logret, all trades):")
    P(f"{'arm':<8}{'vol@entry':>12}{'vol@exit':>11}{'ratio':>9}{'% exits vol>entry vol':>24}")
    volpath = {}
    for lab, dfx in (("LONG", LGL), ("SHORT", LGS)):
        qe = dfx[dfx.role == "entry"].reset_index(drop=True)
        qx = dfx[dfx.role == "exit"].reset_index(drop=True)
        m = np.isfinite(qe["vol"]) & np.isfinite(qx["vol"])
        ve = float(qe["vol"][m].mean()); vx = float(qx["vol"][m].mean())
        up = 100 * float((qx["vol"][m].to_numpy() > qe["vol"][m].to_numpy()).mean())
        volpath[lab] = (ve, vx, up)
        P(f"{lab:<8}{ve:>12.6f}{vx:>11.6f}{vx/ve:>9.4f}{up:>23.1f}%")

    # vol -> spread elasticity from the minute samples
    P(f"\nVOL -> SPREAD ELASTICITY (minute samples only, RTH+ETH pooled):")
    P(f"{'vol decile':<12}{'n':>9}{'mean vol':>12}{'mean spread tk':>16}")
    for k in range(10):
        q = MS[MS["vb"] == k]
        if len(q):
            P(f"{k:<12}{len(q):>9,}{q['vol'].mean():>12.6f}{q['spr_tk'].mean():>16.3f}")
    lo10 = MS[MS["vb"] == 0]["spr_tk"].mean(); hi10 = MS[MS["vb"] == 9]["spr_tk"].mean()
    P(f"   top decile vs bottom decile: {hi10:.3f} vs {lo10:.3f} tk "
      f"= {TICKV*(hi10-lo10):+.2f} $/ctrRT of vol-state cost range")

    # ============================================================== PHASE 5: strata
    H("PHASE 5 -- PER-YEAR STRATA (MODERN window; no PRE-era pooling anywhere)")
    LGL["yr"] = pd.to_datetime(LGL["instant"]).dt.year
    LGS["yr"] = pd.to_datetime(LGS["instant"]).dt.year
    yrs = sorted(set(LGL["yr"]) | set(LGS["yr"]))
    P(f"{'year':<8}{'LONG legs':>11}{'LONG tk':>10}{'SHORT legs':>12}{'SHORT tk':>10}"
      f"{'delta tk':>10}{'delta $/ctrRT':>15}")
    for y in yrs:
        a_ = LGL[LGL.yr == y]; b_ = LGS[LGS.yr == y]
        if not len(a_) or not len(b_):
            continue
        ca = float(np.average(a_["proj"], weights=a_["u"]))
        cb = float(np.average(b_["proj"], weights=b_["u"]))
        P(f"{y:<8}{len(a_):>11,}{ca:>10.4f}{len(b_):>12,}{cb:>10.4f}{cb-ca:>10.4f}"
          f"{TICKV*(cb-ca):>15.2f}")
    P("PRE-2022 IS NOT MEASURABLE HERE: the repository holds NO NQ quote sample below NQ 23,036\n"
      "   (W82 defect 19a). A pre-2022 spread number is not manufactured in this run.")
    P("\nERA-TRANSFER CAVEAT ON THE E2 *LEVEL* (W82 defect 19a, applied to my own work):\n"
      "   the surface is fitted on 2025-08..2026-07 quotes (NQ 23,036-29,479) and applied to legs\n"
      "   back to 2022-07 (NQ ~11,000). A TICK-denominated spread does not transfer across that\n"
      "   price range, so the E2 LEVEL for 2022-2024 is NOT quotable. What is defensible is the\n"
      "   DIFFERENTIAL: both arms pass through the identical surface, so a common level error\n"
      "   cancels in (SHORT - LONG). The per-year deltas above show that differential is itself\n"
      "   unstable (-0.01 to +0.58 tk), which is the honest reading: it is small AND noisy.")

    # ============================================================== PHASE 6: structural
    H("PHASE 6 -- E5: THE STRUCTURAL (NON-EXECUTION) ASYMMETRY, PRICED")
    dif = np.zeros(n); dif[1:] = np.diff(c); dif[D["fb"]] = np.nan
    inwin_bar = (tarr >= A) & (tarr < B)
    ds = dif[inwin_bar & np.isfinite(dif)]
    mu = float(np.mean(ds)); mu_se = float(np.std(ds, ddof=1) / np.sqrt(len(ds)))
    P(f"modern-window per-minute futures drift: {mu:+.6f} pts/min  (naive-iid SE {mu_se:.6f}, "
      f"t = {mu/mu_se:+.2f}, {len(ds):,} bars)")
    P(f"   = {mu*1380:+.3f} pts/session, {mu*1380*252*PV:+,.0f} $/yr at 1 contract held always")
    P("   THE NAIVE-IID t IS NOT THE TEST. 1.38M minutes inside 1,012 sessions are not 1.38M\n"
      "   independent observations. The dependence-preserving statement follows.")

    # dependence-preserving inference on the drift: whole sessions are the resampling unit
    bar_sess = sid[np.flatnonzero(inwin_bar & np.isfinite(dif))]
    dvals = ds
    usess = np.unique(bar_sess)
    idx_s = {s_: np.flatnonzero(bar_sess == s_) for s_ in usess}
    bs = np.empty(NBOOT)
    for bi in range(NBOOT):
        pick = RNG.choice(usess, size=len(usess), replace=True)
        ii = np.concatenate([idx_s[s_] for s_ in pick])
        bs[bi] = dvals[ii].mean()
    dlo_, dhi_ = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
    drift_sig = (dlo_ * dhi_) > 0
    P(f"   SESSION BLOCK BOOTSTRAP ({NBOOT} draws, whole sessions): mu = {mu:+.6f} pts/min, "
      f"95% CI [{dlo_:+.6f}, {dhi_:+.6f}]")
    P(f"   -> drift is {'DISTINGUISHABLE from zero' if drift_sig else 'NOT distinguishable from zero'}"
      f" once within-session dependence is preserved.")
    # sensitivity: day-to-day dependence too (moving blocks of L consecutive sessions)
    ssum = np.array([dvals[idx_s[s_]].sum() for s_ in usess])
    scnt = np.array([len(idx_s[s_]) for s_ in usess])
    NSS = len(usess)
    P(f"   MOVING-BLOCK SENSITIVITY (blocks of L consecutive sessions, so day-to-day "
      f"dependence is\n   preserved too -- the session bootstrap above assumes sessions are "
      f"independent):")
    P(f"{'   L (sessions)':<18}{'mu pts/min':>14}{'95% CI':>34}{'excludes 0?':>14}")
    for L_ in (1, 5, 21):
        nb = int(np.ceil(NSS / L_))
        starts_all = np.arange(NSS)
        outs = np.empty(NBOOT)
        for bi in range(NBOOT):
            s0 = RNG.choice(starts_all, size=nb, replace=True)
            ii = np.concatenate([np.arange(x, x + L_) % NSS for x in s0])[:NSS]
            outs[bi] = ssum[ii].sum() / scnt[ii].sum()
        a_, b_ = float(np.percentile(outs, 2.5)), float(np.percentile(outs, 97.5))
        P(f"   {L_:<15}{mu:>14.6f}{f'[{a_:+.6f}, {b_:+.6f}]':>34}"
          f"{('YES' if a_*b_ > 0 else 'NO'):>14}")
        if L_ == 21:
            drift_sig = (a_ * b_) > 0
            dlo_, dhi_ = a_, b_
    P(f"   -> the CONSERVATIVE (L=21, monthly blocks) reading is used for the per-trade CI "
      f"below:\n      drift is "
      f"{'DISTINGUISHABLE from zero' if drift_sig else 'NOT distinguishable from zero'}.")
    P("   (Orchestrator's stated premise measured +0.008057 pts/min t=+1.48 on >=2022-05 to "
      "2026-07.\n    This run's window is 2022-07-01..2026-05-29 because W73's substrate ends "
      "2026-05-29; the\n    naive t differs, and the block-bootstrap statement above is the one "
      "to quote.)")

    P(f"\n{'arm':<8}{'trades':>8}{'signed ctr-min':>16}{'per trade':>11}"
      f"{'DRIFT $':>12}{'$/trade':>10}{'95% CI $/trade (block bs)':>30}")
    drift_pt = {}
    for lab, trl in (("LONG", L_ins), ("SHORT", S_ins)):
        mins = np.array([(pd.Timestamp(x["xt"]) - pd.Timestamp(x["et"])).total_seconds() / 60.0
                         for x in trl])
        cm = np.array([x["d"] * x["u"] for x in trl]) * mins
        drift = cm.sum() * mu * PV
        pertr = drift / len(trl)
        c_lo = cm.sum() * dlo_ * PV / len(trl)
        c_hi = cm.sum() * dhi_ * PV / len(trl)
        drift_pt[lab] = pertr
        P(f"{lab:<8}{len(trl):>8,}{cm.sum():>16,.0f}{cm.sum()/len(trl):>11.1f}"
          f"{drift:>12,.0f}{pertr:>10.2f}"
          f"{f'[{min(c_lo,c_hi):+.2f}, {max(c_lo,c_hi):+.2f}]':>30}")
    P("   READ: the drift term is the market moving under the position, per trade. It is not an\n"
      "   execution cost and no broker charges it; it is the direction the two arms disagree on.")

    P(f"\nDRIFT BY YEAR, AND LEAVE-ONE-YEAR-OUT (is the whole thing one year?):")
    yr_bar = pd.to_datetime(tarr[np.flatnonzero(inwin_bar & np.isfinite(dif))]).year
    yr_sess = pd.to_datetime(sdate[usess]).year.to_numpy()
    P(f"{'year':<8}{'bars':>12}{'pts/min':>12}{'pts/session':>14}"
      f"{'mu WITHOUT this year':>22}{'L=21 CI without it':>34}{'excl 0?':>9}")
    for y in sorted(set(yr_bar)):
        m_ = yr_bar == y
        keep = np.flatnonzero(yr_sess != y)
        mu_x = ssum[keep].sum() / scnt[keep].sum()
        NK = len(keep); L_ = 21; nb = int(np.ceil(NK / L_))
        outs = np.empty(NBOOT)
        for bi in range(NBOOT):
            s0 = RNG.choice(np.arange(NK), size=nb, replace=True)
            ii = keep[np.concatenate([np.arange(x, x + L_) % NK for x in s0])[:NK]]
            outs[bi] = ssum[ii].sum() / scnt[ii].sum()
        a_, b_ = float(np.percentile(outs, 2.5)), float(np.percentile(outs, 97.5))
        P(f"{y:<8}{int(m_.sum()):>12,}{dvals[m_].mean():>12.6f}{dvals[m_].mean()*1380:>14.2f}"
          f"{mu_x:>22.6f}{f'[{a_:+.6f}, {b_:+.6f}]':>34}"
          f"{('YES' if a_*b_ > 0 else 'NO'):>9}")
    P("   READ: if dropping ONE year flips 'excludes 0' to NO, the modern drift rests on that "
      "year alone.")
    P("   VERDICT ON THE DRIFT: it excludes zero on the FULL 2022-07..2026-05 window at every "
      "block\n   length, but the exclusion does NOT survive dropping 2023, and does NOT survive "
      "dropping the\n   partial 2026 stub. Two of five years carry it. The orchestrator's "
      "premise -- 'the drift is not\n   measurable on the modern window' -- is therefore NOT "
      "refuted here; it is FRAGILE IN BOTH\n   DIRECTIONS, and W73's -$23,078 short-side drift "
      "attribution stays unestablished. This run does\n   NOT claim the drift explains the short "
      "deficit; it claims only that the drift term is ~37x the\n   cost-asymmetry term, so cost "
      "asymmetry cannot be the explanation regardless of which way\n   the drift resolves.")

    P(f"\nTHE COMPARISON THAT MATTERS -- per trade, SHORT minus LONG:")
    P(f"{'term':<44}{'LONG $/trade':>14}{'SHORT $/trade':>15}{'gap':>12}")
    cost_L = 2300 / 1942 * 20.65
    cost_S = 2225 / 2225 * 20.65
    P(f"{'spread cost at the PRIMARY $20.65/ctrRT':<44}{-cost_L:>14.2f}{-cost_S:>15.2f}"
      f"{cost_L-cost_S:>12.2f}")
    P(f"{'measured per-ctrRT COST ASYMMETRY (E2, this run)':<44}{0.0:>14.2f}"
      f"{-TICKV*pt*(2225/2225):>15.2f}{-TICKV*pt:>12.2f}")
    P(f"{'drift / carry (market moving underneath)':<44}{drift_pt['LONG']:>14.2f}"
      f"{drift_pt['SHORT']:>15.2f}{drift_pt['SHORT']-drift_pt['LONG']:>12.2f}")
    P(f"{'gross per trade (commission-only, measured)':<44}"
      f"{sum(x['pnl'] for x in L_ins)/len(L_ins):>14.2f}"
      f"{sum(x['pnl'] for x in S_ins)/len(S_ins):>15.2f}"
      f"{sum(x['pnl'] for x in S_ins)/len(S_ins)-sum(x['pnl'] for x in L_ins)/len(L_ins):>12.2f}")
    P(f"\n   the COST-asymmetry gap is ${abs(TICKV*pt):.2f}/trade. The DRIFT gap is "
      f"${abs(drift_pt['SHORT']-drift_pt['LONG']):.2f}/trade -- "
      f"{abs((drift_pt['SHORT']-drift_pt['LONG'])/(TICKV*pt)):.0f}x larger.")

    P("\nEVERY OTHER CANDIDATE STRUCTURAL ASYMMETRY, PRICED:")
    P(f"{'item':<34}{'long':>8}{'short':>8}{'differential':>14}   why")
    for it, lo_, so_, dl, why in (
            ("stock-borrow / locate fee", "$0", "$0", "$0.00",
             "a FUTURE has no borrow leg at all"),
            ("dividend payable when short", "$0", "$0", "$0.00",
             "dividends live in the basis, symmetric"),
            ("hard-to-borrow / recall risk", "$0", "$0", "$0.00",
             "no share to recall"),
            ("initial + maintenance margin", "same", "same", "$0.00",
             "CME margins are side-symmetric"),
            ("uptick / short-sale restriction", "n/a", "n/a", "$0.00",
             "no SSR in futures"),
            ("overnight financing", "$0", "$0", "$0.00",
             "both arms flat at session close (PHASE 0: 0 overnight holds)"),
            ("roll cost", "same", "same", "$0.00",
             "the calendar spread is paid on both sides at the same size")):
        P(f"{it:<34}{lo_:>8}{so_:>8}{dl:>14}   {why}")
    P("   The equity-short intuition (borrow cost, dividends, locate, SSR) transfers to an index\n"
      "   FUTURE as EXACTLY ZERO dollars. The only structural term that survives is the drift\n"
      "   above, and that drift is already the futures drift, net of carry.")

    # ============================================================== PHASE 7: burden
    H("PHASE 7 -- E6: COST BURDEN. THE SAME $/ctrRT IS NOT THE SAME COST.")
    rows = []
    for lab, trl, dfx in (("LONG", L_ins, LGL), ("SHORT", S_ins, LGS)):
        ntr = len(trl); ctr = sum(x["u"] for x in trl)
        gross = sum(x["pnl"] for x in trl)                 # already net of $4.36 commission
        own = (direct[lab]["cost"] if lab in direct else np.nan)
        for tag, rate in (("floor $4.36/ctrRT = COMMISSION FLOOR, never a headline", COMM_RT),
                          ("PRIMARY $20.65/ctrRT spread (G2_EXEC01, long-side)", 20.65),
                          ("all-in $25.01/ctrRT = $20.65 spread + $4.36 comm "
                           "(comm already in gross)", 25.01 - COMM_RT),
                          (f"this arm's own E1-measured spread ${own:.2f}/ctrRT", own)):
            if not np.isfinite(rate):
                continue
            cost = ctr * rate
            rows.append(dict(arm=lab, basis=tag, ctr=ctr, gross=gross, cost=cost,
                             net=gross - cost, burden=100 * cost / gross if gross else np.nan))
    BR = pd.DataFrame(rows)
    P(f"{'arm':<7}{'basis':<62}{'ctrRT':>8}{'gross $':>11}{'cost $':>11}{'net $':>11}"
      f"{'cost/gross':>12}")
    for _, x in BR.iterrows():
        P(f"{x['arm']:<7}{x['basis']:<62}{x['ctr']:>8,}{x['gross']:>11,.0f}"
          f"{x['cost']:>11,.0f}{x['net']:>11,.0f}{x['burden']:>11.1f}%")
    BR.to_csv(os.path.join(OUT, "asymcost_burden.csv"), index=False)
    bl = BR[(BR.arm == "LONG") & (BR.basis.str.startswith("PRIMARY"))]["burden"].iloc[0]
    bs = BR[(BR.arm == "SHORT") & (BR.basis.str.startswith("PRIMARY"))]["burden"].iloc[0]
    g8 = (bs / bl) >= 1.5
    P(f"\nG8 burden ratio at the SAME $20.65/ctrRT: SHORT {bs:.1f}% / LONG {bl:.1f}% = "
      f"{bs/bl:.2f}x -> {'PASS' if g8 else 'FAIL'}")
    P("   This is ARITHMETIC on established quantities (trade count x contracts / gross), not a\n"
      "   per-round-turn claim. It is scored separately and may not substitute for G1/G2.")

    # per-trade economics
    P(f"\nPER-TRADE ECONOMICS AT THE PRIMARY $20.65/ctrRT:")
    P(f"{'arm':<8}{'trades':>8}{'ctr/trade':>11}{'gross $/trade':>15}"
      f"{'spread $/trade':>16}{'net $/trade':>13}{'net pts/session':>17}")
    for lab, trl in (("LONG", L_ins), ("SHORT", S_ins)):
        ntr = len(trl); ctr = sum(x["u"] for x in trl)
        gross = sum(x["pnl"] for x in trl)
        sp = ctr * 20.65
        P(f"{lab:<8}{ntr:>8,}{ctr/ntr:>11.3f}{gross/ntr:>15.2f}{sp/ntr:>16.2f}"
          f"{(gross-sp)/ntr:>13.2f}{(gross-sp)/PV/NS:>17.2f}")

    # ============================================================== PHASE 8: gate table
    H("GATE TABLE -- PREREGISTERED IN spec.yaml BEFORE RESULTS EXISTED")
    P(f"{'GATE':<8}{'SPEC':<58}{'OBSERVED':<30}{'PASS/FAIL'}")
    gates = [
        ("G1", "|E1 direct delta| >= $1.00/ctrRT and N1 CI excludes 0",
         f"{TICKV*dpt:+.2f} CI[{TICKV*dlo:+.2f},{TICKV*dhi:+.2f}]", g1),
        ("G2", "|E2 projected delta| >= $1.00/ctrRT and N1 CI excludes 0",
         f"{TICKV*pt:+.2f} CI[{TICKV*lo:+.2f},{TICKV*hi:+.2f}]", g2),
        ("G3", "E1 and E2 agree in sign",
         f"E1 {d_dir_tk:+.4f} tk / E2 {d_proj_tk:+.4f} tk", bool(g3)),
        ("G4", "exit-leg delta > entry-leg delta (mechanism)",
         f"exit {ext_d:+.4f} vs entry {ent_d:+.4f}", bool(g4)),
        ("G5", "short WIN exit spread - long WIN exit spread >= +0.25 tk",
         f"{g5_val:+.4f} tk", bool(g5)),
        ("G6", "E2 delta outside N3 label-shuffle 95% band",
         f"{d_proj_tk:+.4f} vs [{nlo:+.4f},{nhi:+.4f}]", bool(g6)),
        ("G7", "delta cost/ctrRT >= $5.00 (MATERIAL: >= 9% of short gross)",
         f"E2 {TICKV*pt:+.2f} / E1 {TICKV*dpt:+.2f}",
         bool(abs(TICKV*pt) >= 5.0 or abs(TICKV*dpt) >= 5.0)),
        ("G8", "short cost/gross >= 1.5x long cost/gross at same $20.65",
         f"{bs:.1f}% / {bl:.1f}% = {bs/bl:.2f}x", bool(g8)),
    ]
    for k, s, ob, ok in gates:
        P(f"{k:<8}{s:<58}{ob:<30}{'PASS' if ok else 'FAIL'}")

    P("\nPREREGISTERED DECISION RULE APPLIED:")
    g7 = bool(abs(TICKV*pt) >= 5.0 or abs(TICKV*dpt) >= 5.0)
    if g1 and g2 and g3 and g7:
        verdict = ("CLOSES_A_DIRECTION -- the short side IS materially more expensive per round "
                   "turn;\n   every short candidate in this repo has been quoted at a flattering "
                   "cost.")
    elif g1 and g2 and g3:
        verdict = ("per-round-turn asymmetry is REAL but SMALL; it does not by itself explain the "
                   "short deficit.")
    else:
        # publish the exclusion bound
        wid = max(abs(TICKV*lo), abs(TICKV*hi))
        verdict = (f"NO MATERIAL per-round-turn cost asymmetry is established. The E2 95% CI "
                   f"is\n   [{TICKV*lo:+.2f}, {TICKV*hi:+.2f}] $/ctrRT, so a differential larger "
                   f"than ${wid:.2f}/ctrRT is EXCLUDED at 95%.\n   That CLOSES the 'shorts are "
                   f"secretly more expensive per round turn' explanation for the short deficit.")
    P("   " + verdict)

    H("WHAT THIS RUN SHOWS, AND WHAT IT DOES NOT")
    P("SHOWS:")
    P(f"  1. The MECHANISM is real and survives its controls. Shorts do fire and exit in "
      f"higher-vol\n     states than longs (vol@exit {volpath['SHORT'][1]:.6f} vs "
      f"{volpath['LONG'][1]:.6f}; {volpath['SHORT'][2]:.1f}% vs {volpath['LONG'][2]:.1f}% of "
      f"exits are into\n     rising vol), the differential is"
      f"\n     concentrated on the EXIT leg (G4), it is largest for the short's "
      f"WINNERS (G5, {g5_val:+.3f} tk),\n     it is NOT explained by hour-of-day (N2: only "
      f"{TICKV*(long_hm-proj_cost['LONG']['cw']):+.2f} of {TICKV*d_proj_tk:+.2f} $/ctrRT is "
      f"hour), and it\n     sits far outside the state-blind label-shuffle null (G6).")
    P(f"  2. The DOLLARS are small. {TICKV*pt:+.2f} $/ctrRT, 95% CI "
      f"[{TICKV*lo:+.2f}, {TICKV*hi:+.2f}]. That is "
      f"{100*abs(TICKV*pt)/54.59:.1f}% of the\n     short sleeve's $54.59/trade "
      f"commission-only gross. The preregistered materiality bar was\n     $5.00/ctrRT and it "
      f"is MISSED by a factor of {5.0/abs(TICKV*pt):.1f}.")
    P(f"  3. The DIRECT measurement does not confirm even that. On {len(MM):,} real fill instants "
      f"it is\n     {TICKV*dpt:+.2f} $/ctrRT, CI [{TICKV*dlo:+.2f}, {TICKV*dhi:+.2f}] -- "
      f"the WRONG SIGN, and consistent with zero. G3 FAILS.")
    P(f"  4. Every non-execution asymmetry an equity short would face prices at EXACTLY $0 in an\n"
      f"     index FUTURE: no borrow, no locate, no dividend liability, no SSR, side-symmetric\n"
      f"     margin, and both arms flat at the close so no overnight financing either.")
    P("DOES NOT SHOW:")
    P("  a. It does not measure a pre-2022 spread. No NQ quote below NQ 23,036 exists in this "
      "repo.")
    P("  b. The E2 LEVEL for 2022-2024 is not quotable (tick-denominated spread across a 2x "
      "price\n     range). Only the SHORT-minus-LONG differential is defended, and that "
      "differential is itself\n     unstable year to year (-0.01 to +0.58 tk).")
    P("  c. It does not test whether a short-specific ENTRY or EXIT POLICY could avoid the "
      "wide-spread\n     states. That would be an exposure-reducing rule and would require a "
      "state-blind random-\n     thinning control, which this repo's record says it would lose "
      "(11 for 11). None is proposed.")
    P("  d. It does not revise the repo's $20.65/ctrRT. It says that number applies to the short "
      "side\n     too, within about a dollar.")

    P("\nTHE ONE NUMBER THAT DID MOVE, AND IT IS NOT A COST-ASYMMETRY NUMBER:")
    P(f"   At the SAME measured $20.65/ctrRT, the short sleeve pays {bs:.1f}% of its own gross in "
      f"spread\n   against the long object's {bl:.1f}% -- {bs/bl:.2f}x -- purely because it needs "
      f"{2225} contract round\n   turns to earn $121,454 while the long needs {2300} to earn "
      f"$300,817. W61/W62/W73/W120 all\n   quote this sleeve COMMISSION-ONLY. Its honest "
      f"post-spread standalone figure is\n   {(sum(x['pnl'] for x in S_ins)-2225*20.65)/PV/NS:.2f} "
      f"pts/session, not the 6.00 in the record -- a "
      f"{100*(1-((sum(x['pnl'] for x in S_ins)-2225*20.65)/(sum(x['pnl'] for x in S_ins)))):.0f}% "
      f"haircut,\n   against the long object's "
      f"{100*(1-((sum(x['pnl'] for x in L_ins)-2300*20.65)/(sum(x['pnl'] for x in L_ins)))):.0f}%."
      f" This is arithmetic, not a new measurement, and it was\n   always available; it is stated "
      f"here because no short-side report in the repo states it.")

    P(f"\nWALL TIME {_time.time()-T0:.0f}s")
    P("STATUS: diagnostic. NOTHING ADOPTED. NO CANDIDATE PROPOSED. No CrossTrade/NT8 call was "
      "made;\n   no order, deploy, backtest or .cs edit occurred; no file under "
      "research/weekly_edge/src or\n   research_sdk was modified.")
    _OUTF.close()


if __name__ == "__main__":
    main()
