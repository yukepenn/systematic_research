"""G2_F9_P1_SYMCERT_20260829 — TEAM P1_SYMCERT driver (ledger trial G00039).

Symmetric certification: the incumbent P1/PCT sits the same rung battery that killed
AUCTREV (META_ADVERSARY_01 indictment 1 / Q10). Executes the FROZEN spec.yaml with the
ambiguity resolutions frozen in out/spec_resolutions.txt BEFORE this file first ran
(R1..R12, referenced inline). No parameter search. The valence_precommitment band is
quoted in the gate table BEFORE the R_c observation appears (binding).

THIS IS EVIDENCE, NOT A VETO — owner doctrine keeps P1 incumbent regardless of outcome;
results are reported unvarnished.

Writes ONLY under runs/G2_F9_P1_SYMCERT_20260829/out/. Never touches git, never calls
CrossTrade, never modifies an existing file, never appends to SEARCH_LEDGER.
Seal: every dated load passes research_sdk.seal_guard.assert_presealed (R10).
"""
from __future__ import annotations

import json
import os
import sys
import time as _time

os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "G2_F9_P1_SYMCERT_20260829")
OUT = os.path.join(RUN, "out")
DET = os.path.join(OUT, "rung_details")
os.makedirs(OUT, exist_ok=True)
os.makedirs(DET, exist_ok=True)
SRC = os.path.join(ROOT, "research", "weekly_edge", "src")
sys.path.insert(0, SRC)
sys.path.insert(0, ROOT)

from research_sdk.seal_guard import assert_presealed                     # noqa: E402
from research_sdk.null_guard import (verify_null_sensitivity,            # noqa: E402
                                     run_circular_null)

import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import PV, COMM_RT                                       # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames                                    # noqa: E402
from run_we_w97 import votes, L13                                        # noqa: E402
from run_we_w98 import gfills, arm_kw                                    # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

T0 = _time.time()
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
TICKV = 5.0
BASE_WEEKLY = 1393.573663          # REPRODUCED FACT, G00000 (R6/R10 of resolutions)
EXEC01_E3_MEAN = -89.62            # recorded G00015 E3 (consistency comparator)
EXEC01_E3_SE = 99.11
BAND_LO, BAND_HI = 2.0, 40.0       # valence_precommitment band, %, endpoints inclusive
VALENCE_QUOTE = [
    "VALENCE PRECOMMITMENT (spec.yaml, quoted verbatim BEFORE any R_c number appears):",
    "  \"Mechanism-implied predictions are STATED HERE, before measurement, to prevent the",
    "   asymmetric-valence error the adversary caught:",
    "   P1's mechanism = slow trend-ratchet (holds tens of minutes, re-arms) => R_c",
    "   prediction: +1-bar-delayed entries should degrade net MODERATELY - preregistered",
    "   consistency band [2%, 40%] degradation = CONSISTENT; < 2% = TIMING-IRRELEVANT flag",
    "   (entry selection may be drift-riding; interpret jointly with R_d); > 40% =",
    "   FASTER-THAN-CLAIMED flag.\"",
]
MULTIPLICITY = ("Multiplicity: P1/PCT is the survivor of ~123 waves / 700+ prior "
                "experiments with no program-level deflator "
                "(GENESIS_PRIOR_RESEARCH_ATLAS.md:8-10); its t=4.16 is post-selection; "
                "evidence status of everything measured here remains DISCOVERY_CONSUMED; "
                "nothing in this run is forward evidence.")

PARITY_ARTIFACT = os.path.join(ROOT, "runs", "WE_P1PCT_PARITY_20260827", "out",
                               "py_trades_p1pct.csv")
ARMS_CSV = os.path.join(ROOT, "runs", "WE_W67_COMBINER", "out", "arms.csv")


def log(*a):
    print(f"[{_time.time()-T0:6.0f}s]", *a, flush=True)


# --------------------------------------------------------------------------------------
# instrumented gfills — VERBATIM logic of run_we_w98.gfills with extra RECORDED fields
# (entry/exit bar index, entry/exit price, exit kind). The EXEC01 R1 device; asserted
# equal to the original on every (d,u,et,xt,pnl) tuple in gate GA (resolutions R1).
# --------------------------------------------------------------------------------------
def gfills_instr(D, dir_arr, size_at_entry=None, halt=1300.0, target=1000.0,
                 per_ctr=False):
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
        if want != p:
            if p != 0:
                pnl = p * u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl,
                                   eti=eti, xti=i, epx=epx, xpx=o[i], xkind="open"))
                spnl += (pnl / u) if per_ctr else pnl
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


def wr(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    glines = []

    def G(*a):
        s = " ".join(str(x) for x in a)
        glines.append(s); print(s, flush=True)

    # ================================================================ Phase A: stream
    log("Phase A — substrate + P1/PCT stream regeneration (R1, verbatim repro chain)")
    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    o, c = D["o"], D["c"]
    assert_presealed(pd.DataFrame({"t": pd.to_datetime(tarr)}), "t",
                     "substrate 1-min bars")
    log(f"substrate {n:,} bars / {D['n_sess']:,} sessions — seal PASS "
        f"(max t {pd.Timestamp(tarr.max())})")

    st_, en_, _ = session_frames(D)
    NSESS = D["n_sess"]
    sdate = pd.to_datetime(D["sess_date"])
    iso = sdate.isocalendar()
    wkall = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    win = np.array([A <= tarr[st_[s]] < B for s in range(NSESS)])
    sess_in = np.flatnonzero(win)
    wk_in = wkall[sess_in]
    n_weeks = len(set(wk_in))
    log(f"in-window sessions {len(sess_in):,}, ISO weeks {n_weeks}")

    X = fast_build_context(D)
    z = np.load(os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out", "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    if mem.shape[0] != n:
        raise SystemExit("mem_ext.npz rows != substrate bars — ABORT")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    log("votes -> fills_daily -> causal_score (verbatim)")
    vl, _ = votes(D, mem, bmom, tilt, X, bmom)
    p_arr = vl.astype(np.int8)
    bb = fills_daily(D, p_arr, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, ee, window=WIN)
    sizes = np.where(sc >= 3, 2, 1).astype(np.int8)
    log("gfills (original) + gfills_instr")
    tr_ref = gfills(D, p_arr, sizes, **arm_kw("PCT", 1.183))
    tr = gfills_instr(D, p_arr, sizes, **arm_kw("PCT", 1.183))

    ga = len(tr) == len(tr_ref) and all(
        x["d"] == y["d"] and x["u"] == y["u"] and x["et"] == y["et"]
        and x["xt"] == y["xt"] and abs(x["pnl"] - y["pnl"]) <= 1e-9
        for x, y in zip(tr, tr_ref))
    n_total = len(tr)
    for x in tr:
        x["sess"] = int(sid[x["eti"]])
    n_sessfilter = sum(1 for x in tr if win[x["sess"]])
    gb = (n_total == 2401) and (n_sessfilter == 2131)
    log(f"stream: total {n_total}, session-filtered {n_sessfilter}; GA={ga} GB={gb}")

    TT = pd.DataFrame([{k: x[k] for k in
                        ("d", "u", "et", "xt", "pnl", "eti", "xti", "epx", "xpx",
                         "xkind", "sess")} for x in tr])
    TT["in_win"] = TT["sess"].map(lambda s: bool(win[s]))
    assert (sid[TT["eti"].to_numpy()] == sid[TT["xti"].to_numpy()]).all(), \
        "trade spans sessions — data-impossible"
    assert_presealed(TT.assign(et_ts=pd.to_datetime(TT["et"])), "et_ts", "P1 trade entries")
    assert_presealed(TT.assign(xt_ts=pd.to_datetime(TT["xt"])), "xt_ts", "P1 trade exits")
    TIN = TT[TT["in_win"]].reset_index(drop=True)
    TIN["year"] = TIN["sess"].map(lambda s: int(sdate[s].year))
    TIN["week"] = TIN["sess"].map(lambda s: wkall[s])

    # GC: row-by-row cross-check against the recorded frozen parity artifact (R1)
    PYA = pd.read_csv(PARITY_ARTIFACT)
    assert_presealed(PYA.assign(et_ts=pd.to_datetime(PYA["et"])), "et_ts",
                     "recorded parity artifact entries")
    gc = len(PYA) == len(TIN)
    if gc:
        gc &= bool((pd.to_datetime(TIN["et"]).to_numpy()
                    == pd.to_datetime(PYA["et"]).to_numpy()).all())
        gc &= bool((pd.to_datetime(TIN["xt"]).to_numpy()
                    == pd.to_datetime(PYA["xt"]).to_numpy()).all())
        gc &= bool((TIN["d"].to_numpy() == PYA["d"].to_numpy()).all())
        gc &= bool((TIN["u"].to_numpy() == PYA["u"].to_numpy()).all())
        gc &= bool(np.all(np.abs(TIN["pnl"].to_numpy() - PYA["pnl"].to_numpy())
                          <= 0.005 + 1e-9))
    gd = (n_weeks == 213)
    log(f"artifact cross-check GC={gc}; week count GD={gd} ({n_weeks})")
    if not (ga and gb and gc):
        G("STREAM IDENTITY FAILED (GA/GB/GC) — run aborts as DEFECT.")
        wr(os.path.join(OUT, "gate_table.txt"), glines)
        with open(os.path.join(OUT, "ledger_result_pending.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"trial_id": "G00039", "metrics": {}, "result": "DEFECT",
                       "note": "P1 stream regeneration failed identity gates"}, f)
        return

    # spread rate + canonical net weekly series — net_series VERBATIM (repro/W103) (R2)
    def net_series(tr_):
        w_ = {}
        for x in tr_:
            for ts in (x["et"], x["xt"]):
                p_ = pd.Timestamp(ts); m2 = p_.hour * 60 + p_.minute
                w_[m2] = w_.get(m2, 0.0) + x["u"]
        rate = TICKV * sum(float(prof.get(m2, 3.0)) * q for m2, q in w_.items()) / \
            max(sum(w_.values()), 1e-9)
        s_ = np.zeros(NSESS); ct = np.zeros(NSESS)
        for x in tr_:
            si = int(sid[i_of(x["et"])])
            if win[si]:
                s_[si] += x["pnl"] - rate * x["u"]; ct[si] += x["u"]
        return s_, ct, rate, len(tr_)

    ser, ctr, rate, _ntr = net_series(tr)

    def wkv(x):
        return pd.Series(x[sess_in]).groupby(wk_in).sum()

    WK_NET = wkv(ser)
    base_weekly = float(WK_NET.mean())
    base_t = base_weekly / max(WK_NET.std(ddof=1) / np.sqrt(len(WK_NET)), 1e-9)
    ge_base = abs(base_weekly - BASE_WEEKLY) <= 0.01
    log(f"canonical weekly net ${base_weekly:.6f} (t={base_t:.3f}) — "
        f"baseline identity {'OK' if ge_base else 'MISMATCH'}; rate ${rate:.2f}/ctrRT")

    # ================================================================ Phase B: R_a
    log("Phase B — R_a concentration")
    pnl = TIN["pnl"].to_numpy()
    net2 = pnl - rate * TIN["u"].to_numpy()          # secondary convention (R2)
    k_tr = int(np.ceil(0.10 * len(TIN)))             # = 214
    order = np.argsort(pnl)[::-1]
    top_share = float(pnl[order[:k_tr]].sum() / pnl.sum())
    order2 = np.argsort(net2)[::-1]
    top_share2 = float(net2[order2[:k_tr]].sum() / net2.sum())
    bot_sum = float(pnl[order[k_tr:]].sum())
    ra_pass = top_share <= 0.40

    # weeks share (non-gate): primary weekly sums of recorded pnl; canonical net series
    wk_pnl = TIN.groupby("week")["pnl"].sum()
    k_wk = int(np.ceil(0.10 * n_weeks))              # = 22
    top_wk_share_primary = float(wk_pnl.sort_values(ascending=False)
                                 .iloc[:k_wk].sum() / wk_pnl.sum())
    top_wk_share_net = float(WK_NET.sort_values(ascending=False)
                             .iloc[:k_wk].sum() / WK_NET.sum())

    # component shares (R9) — (a) B-MOM-enabled attribution, W67b rule verbatim
    idx13 = {v: k for k, v in enumerate(L13)}
    cols13 = [idx13[v] for v in L13]
    s13 = mem[:, cols13].sum(axis=1).astype(int)
    agree13 = (np.sign(s13) == tilt) & (s13 != 0) & (tilt != 0)
    eti_arr = TIN["eti"].to_numpy()
    need = np.where(agree13[eti_arr], 5, 6)
    enabled = (s13[eti_arr] < need) & (bmom[eti_arr] > 0)
    en_share = float(pnl[enabled].sum() / pnl.sum())
    en_by_year = {}
    for y in sorted(TIN["year"].unique()):
        m_ = (TIN["year"] == y).to_numpy()
        tot_y = pnl[m_].sum()
        en_by_year[int(y)] = (100 * float(pnl[m_ & enabled].sum() / tot_y)
                              if tot_y != 0 else float("nan"))
    # (b) the recorded ~51% flag from artifacts (arms.csv, counterfactual ladder)
    ARMS = pd.read_csv(ARMS_CSV).set_index("arm")
    pts0 = float(ARMS.loc["w_bmom=0.00", "pts"])
    pts283 = float(ARMS.loc["w_bmom=2.83", "pts"])
    flag51 = 100 * (1 - pts0 / pts283)

    det_a = []
    det_a.append("R_a — CONCENTRATION (primary = recorded per-trade pnl; R2/R3)")
    det_a.append(f"trades {len(TIN)}  top ceil(10%) = {k_tr}")
    det_a.append(f"total net (primary)          : ${pnl.sum():,.2f}")
    det_a.append(f"top-{k_tr} sum                 : ${pnl[order[:k_tr]].sum():,.2f}"
                 f"  -> share {100*top_share:.1f}%  (gate <= 40%)")
    det_a.append(f"remaining {len(TIN)-k_tr} trades sum   : ${bot_sum:,.2f}")
    det_a.append(f"secondary (net of ${rate:.2f}/ctrRT spread): share "
                 f"{100*top_share2:.1f}%")
    det_a.append("")
    det_a.append(f"top-decile WEEKS (non-gate): k = {k_wk} of {n_weeks}")
    det_a.append(f"  primary weekly pnl sums   : {100*top_wk_share_primary:.1f}%")
    det_a.append(f"  canonical net weekly serie: {100*top_wk_share_net:.1f}%")
    det_a.append("")
    det_a.append("component shares (non-gate, R9):")
    det_a.append(f"  (a) B-MOM-ENABLED share of primary net, frozen stream, W67b rule "
                 f"at entry bar: {100*en_share:.1f}%  ({int(enabled.sum())} of "
                 f"{len(TIN)} trades)")
    det_a.append("      by year (this run vs recorded LEGACY_DIAGNOSTIC "
                 "9.9/82.4/17.3/45.9/-16.6):")
    for y, v in en_by_year.items():
        det_a.append(f"        {y}: {v:+.1f}%")
    det_a.append(f"  (b) recorded ~51% flag re-derived from arms.csv: "
                 f"1 - {pts0:.4f}/{pts283:.4f} = {flag51:.1f}% "
                 f"(Solar-only counterfactual, LEGACY_DIAGNOSTIC, pre-W98 engine)")
    wr(os.path.join(DET, "R_a_concentration.txt"), det_a)
    top_csv = TIN.iloc[order[:k_tr]][["et", "xt", "d", "u", "pnl", "year", "week"]]
    top_csv.to_csv(os.path.join(DET, "R_a_top214_trades.csv"), index=False)
    log(f"R_a: top-{k_tr} share {100*top_share:.1f}% -> "
        f"{'PASS' if ra_pass else 'FAIL'}")

    # ================================================================ Phase C: R_b
    log("Phase C — R_b LOYO + era status")
    years = sorted(TIN["year"].unique())
    loyo_rows = []
    rb_pass = True
    min_excl = None
    for y in years:
        keep = TIN["year"] != y
        tot = float(TIN.loc[keep, "pnl"].sum())
        tot2 = float((TIN.loc[keep, "pnl"] - rate * TIN.loc[keep, "u"]).sum())
        ok = tot > 0
        rb_pass &= ok
        if min_excl is None or tot < min_excl[1]:
            min_excl = (int(y), tot)
        loyo_rows.append((int(y), int((~keep).sum()), tot, tot2, ok))
    era_status = (
        "NOT-ATTEMPTABLE — the deep substrate member/tilt/bmom caches and pipeline "
        "constants are frozen on the modern 2022-2026 load; running the member ensemble "
        "pre-2022 would be a NEW experiment, not a rung (spec R_b clause). Nearest "
        "recorded LEGACY_DIAGNOSTIC (cited, not computed here; DIFFERENT variant — "
        "pre-W98 exit engine, not the frozen PCT box): WE_W97_AUDITFIX M10 built a P1 "
        "variant on 2006-2021: net +$79,076, 44.5% positive weeks.")
    det_b = []
    det_b.append("R_b — LOYO (leave-one-year-out), primary = recorded per-trade pnl (R4)")
    det_b.append("year assignment = calendar year of the trade's SESSION date")
    det_b.append("(2022 is H2-only and 2026 ends 2026-07 — window edges, not choices)")
    det_b.append(f"{'excl year':<11}{'trades out':>11}{'remaining net $':>18}"
                 f"{'net-of-spread $':>17}{'>0?':>6}")
    for y, k, tot, tot2, ok in loyo_rows:
        det_b.append(f"{y:<11}{k:>11}{tot:>18,.2f}{tot2:>17,.2f}"
                     f"{'PASS' if ok else 'FAIL':>6}")
    det_b.append("")
    det_b.append(f"minimum exclusion: ex-{min_excl[0]} -> ${min_excl[1]:,.2f}")
    det_b.append("")
    det_b.append("ERA RUNG (pre-2022): " + era_status)
    wr(os.path.join(DET, "R_b_loyo.txt"), det_b)
    log(f"R_b: {'PASS' if rb_pass else 'FAIL'} (min exclusion ex-{min_excl[0]} "
        f"${min_excl[1]:,.0f})")

    # ================================================================ Phase D: R_c
    log("Phase D — R_c timing (+1-bar delayed fills, EXEC01 R9 code-verbatim; R6)")
    deltas = np.zeros(NSESS)
    n_shift_e = n_shift_x = n_capped = 0
    for _, x in TIN.iterrows():
        d_, u_ = int(x["d"]), int(x["u"])
        eti, xti = int(x["eti"]), int(x["xti"])
        s = int(x["sess"])
        e2 = eti + 1
        if e2 < n and sid[e2] == s:
            ep2 = o[e2]; n_shift_e += 1
        else:
            ep2 = float(x["epx"]); n_capped += 1
        if x["xkind"] == "open":
            x2 = xti + 1
            if x2 < n and sid[x2] == s:
                xp2 = o[x2]; n_shift_x += 1
            else:
                xp2 = c[xti]; n_capped += 1
        else:
            xp2 = float(x["xpx"])
        dpnl = d_ * u_ * ((xp2 - ep2) - (float(x["xpx"]) - float(x["epx"]))) * PV
        deltas[s] += dpnl
    wk_delta = pd.Series(deltas[sess_in]).groupby(wk_in).sum()
    e3_mean = float(wk_delta.mean())
    e3_se = float(wk_delta.std(ddof=1) / np.sqrt(len(wk_delta)))
    e3_total = float(wk_delta.sum())
    degr = -100.0 * e3_mean / BASE_WEEKLY
    exec01_gap = abs(e3_mean - EXEC01_E3_MEAN)
    exec01_ok = exec01_gap <= 0.5
    if BAND_LO <= degr <= BAND_HI:
        rc_verdict = "CONSISTENT"
    elif degr < BAND_LO:
        rc_verdict = "TIMING-IRRELEVANT flag (interpret jointly with R_d)"
    else:
        rc_verdict = "FASTER-THAN-CLAIMED flag"
    det_c = []
    det_c.extend(VALENCE_QUOTE)
    det_c.append("")
    det_c.append("R_c — TIMING (+1 min delayed entries AND open-exit fills on the frozen")
    det_c.append("action set; EXEC01 E3 / R9 convention, code-verbatim; costs cancel)")
    det_c.append(f"legs shifted: entries {n_shift_e}, open-exits {n_shift_x}; "
                 f"session-end-capped {n_capped}; close-exits unchanged "
                 f"{int((TIN['xkind']=='close').sum())}")
    det_c.append(f"delta net/week = ${e3_mean:+.2f} (SE ${e3_se:.2f}, {len(wk_delta)} wks; "
                 f"total ${e3_total:+,.0f})")
    det_c.append(f"degradation vs REPRODUCED baseline ${BASE_WEEKLY:,.2f}/wk : "
                 f"{degr:+.2f}%")
    det_c.append(f"consistency vs EXEC01 G00015 (-$89.62/wk, SE $99.11, -6.4%): "
                 f"gap ${exec01_gap:.2f} -> "
                 f"{'CONSISTENT' if exec01_ok else 'DISCREPANCY — reported unvarnished'}")
    det_c.append(f"band verdict: {rc_verdict}")
    wr(os.path.join(DET, "R_c_timing.txt"), det_c)
    log(f"R_c: degradation {degr:+.2f}% -> {rc_verdict}")

    # ================================================================ Phase E: R_d
    log("Phase E — R_d in-market mask circular-shift null (R7/R8)")
    # increments: inc[i] = o[i+1]-o[i] if next bar same session else c[i]-o[i]
    inc = np.empty(n)
    inc[:-1] = o[1:] - o[:-1]
    inc[-1] = c[-1] - o[-1]
    last_of_sess = np.ones(n, bool)
    last_of_sess[:-1] = sid[1:] != sid[:-1]
    inc[last_of_sess] = (c - o)[last_of_sess]
    # mask from frozen trade intervals (MAE01 R2 life-window convention)
    mask = np.zeros(n)
    for _, x in TIN.iterrows():
        hi = int(x["xti"]) - 1 if x["xkind"] == "open" else int(x["xti"])
        mask[int(x["eti"]):hi + 1] += int(x["d"]) * int(x["u"])
    gross_direct = float(sum(x["pnl"] + COMM_RT * x["u"] for _, x in TIN.iterrows()))
    gross_mask = float(PV * np.dot(mask, inc))
    gf_identity = abs(gross_mask - gross_direct) <= 1e-6
    log(f"mask identity: mask ${gross_mask:,.4f} vs trades ${gross_direct:,.4f} "
        f"-> {'OK' if gf_identity else 'FAIL'}")
    if not gf_identity:
        G("R_d MASK IDENTITY FAILED — rung aborts as DEFECT (printed unvarnished).")

    # frame: one row per in-window minute bar, session label + mask + inc
    rows_idx = np.concatenate([np.arange(st_[s], en_[s]) for s in sess_in])
    FRAME = pd.DataFrame({"session": sid[rows_idx].astype(np.int64),
                          "mask": mask[rows_idx], "inc": inc[rows_idx]})
    S = len(sess_in)

    def loader():
        return FRAME

    def decision_fn(f):
        return f            # opaque: the mask travels with the shifted session blocks

    def blocks_of(fr):
        sv = fr["session"].to_numpy()
        cut = np.flatnonzero(np.diff(sv) != 0) + 1
        return np.split(np.arange(len(sv)), cut)

    base_blocks = blocks_of(FRAME)
    base_inc = [FRAME["inc"].to_numpy()[b] for b in base_blocks]

    def statistic_fn(dec, base):
        mv = dec["mask"].to_numpy()
        sv = dec["session"].to_numpy()
        cut = np.flatnonzero(np.diff(sv) != 0) + 1
        starts = np.concatenate(([0], cut))
        ends = np.concatenate((cut, [len(sv)]))
        acc = 0.0
        for j in range(len(starts)):
            m_ = mv[starts[j]:ends[j]]
            v_ = base_inc[j]
            L = min(len(m_), len(v_))
            acc += float(np.dot(m_[:L], v_[:L]))
        return PV * acc

    log("null_guard: verify_null_sensitivity (shifts 1,2,5) ...")
    sens = verify_null_sensitivity(loader, decision_fn, statistic_fn, shifts=[1, 2, 5],
                                   unit="session")
    gg_sens = True
    log(f"sensitivity OK: real ${sens['real_stat']:,.0f}, spread ${sens['spread']:,.0f}")

    n_shifts = S - 1
    log(f"null_guard: run_circular_null over ALL {n_shifts} whole-session shifts ...")
    nul = run_circular_null(loader, decision_fn, statistic_fn, n_shifts=n_shifts,
                            unit="session", seed=20260829)
    null_arr = np.asarray(nul["null_stats"], dtype=float)
    real_stat = float(nul["real_stat"])
    align_ok = abs(real_stat - gross_mask) <= 1e-6
    p95 = float(np.percentile(null_arr, 95))
    rd_pass = real_stat > p95
    # cost constants (identical across every arm under whole-session shifts, R8)
    comm_total = float(COMM_RT * TIN["u"].sum())
    spread_total = float(rate * TIN["u"].sum())
    det_d = []
    det_d.append("R_d — IN-MARKET MASK CIRCULAR-SHIFT NULL (R7/R8)")
    det_d.append(f"in-window sessions S = {S}; minute rows {len(FRAME):,}; "
                 f"shifts used = ALL S-1 = {n_shifts} (>= 300 required: "
                 f"{'YES' if n_shifts >= 300 else 'NO'})")
    det_d.append(f"mask identity gate: mask-reconstructed gross ${gross_mask:,.2f} == "
                 f"sum(trade gross) ${gross_direct:,.2f} "
                 f"({'PASS' if gf_identity else 'FAIL'})")
    det_d.append(f"null_guard sensitivity: PASS (spread ${sens['spread']:,.0f} across "
                 f"shifts [1,2,5])")
    det_d.append(f"real statistic through the null machinery == direct dot product: "
                 f"{'PASS' if align_ok else 'FAIL'}")
    det_d.append("")
    det_d.append(f"actual gross capture             : ${real_stat:,.2f}")
    det_d.append(f"null distribution ({len(null_arr)} draws): mean ${null_arr.mean():,.0f}"
                 f"  sd ${null_arr.std(ddof=1):,.0f}  p50 ${np.percentile(null_arr,50):,.0f}"
                 f"  p95 ${p95:,.0f}  p99 ${np.percentile(null_arr,99):,.0f}"
                 f"  max ${null_arr.max():,.0f}")
    det_d.append(f"gate: actual > null p95          : ${real_stat:,.0f} vs ${p95:,.0f} "
                 f"-> {'PASS' if rd_pass else 'FAIL'}")
    det_d.append(f"percentile of actual in null     : {100*nul['percentile']:.1f}th; "
                 f"add-one p_ge = {nul['p_ge']:.4f}")
    det_d.append("")
    det_d.append("net framing (costs are constants under whole-session shifts — same "
                 "trades, same contracts, same fill minutes):")
    det_d.append(f"  commission total ${comm_total:,.0f} + modelled spread total "
                 f"${spread_total:,.0f}")
    det_d.append(f"  actual net ${real_stat-comm_total-spread_total:,.0f} vs null p95 net "
                 f"${p95-comm_total-spread_total:,.0f} — same verdict by construction")
    wr(os.path.join(DET, "R_d_mask_null.txt"), det_d)
    pd.DataFrame({"shift": nul["shifts"], "null_gross_capture": null_arr}) \
        .to_csv(os.path.join(DET, "R_d_null_distribution.csv"), index=False)
    log(f"R_d: actual ${real_stat:,.0f} vs p95 ${p95:,.0f} -> "
        f"{'PASS' if rd_pass else 'FAIL'} (pctile {100*nul['percentile']:.1f})")

    # ================================================================ gate table
    rd_pass_final = rd_pass and gf_identity and align_ok
    overall = ra_pass and rb_pass and rd_pass_final and (rc_verdict == "CONSISTENT")
    G("=" * 108)
    G("G2_F9_P1_SYMCERT_20260829 — GATE TABLE (printed by program; trial G00039)")
    G("SYMMETRIC CERTIFICATION: the incumbent P1/PCT sits the AUCTREV rung battery.")
    G("spec: runs/G2_F9_P1_SYMCERT_20260829/spec.yaml (frozen); resolutions R1-R12 frozen")
    G("pre-computation in out/spec_resolutions.txt.")
    G("THIS IS EVIDENCE, NOT A VETO — owner doctrine keeps P1 incumbent regardless.")
    G("=" * 108)
    for ln in VALENCE_QUOTE:
        G(ln)
    G("=" * 108)
    G(f"{'GATE':<7}{'SPEC':<62}{'OBSERVED':<28}{'VERDICT'}")
    G(f"{'GA':<7}{'gfills_instr == gfills on every (d,u,et,xt,pnl)':<62}"
      f"{str(ga):<28}{'PASS' if ga else 'FAIL'}")
    G(f"{'GB':<7}{'stream identity: 2401 total / 2131 session-filtered':<62}"
      f"{f'{n_total} / {n_sessfilter}':<28}{'PASS' if gb else 'FAIL'}")
    G(f"{'GC':<7}{'row-by-row == recorded py_trades_p1pct.csv (2131 rows)':<62}"
      f"{str(gc):<28}{'PASS' if gc else 'FAIL'}")
    G(f"{'GD':<7}{'weekly series has 213 ISO weeks (spec population)':<62}"
      f"{n_weeks:<28}{'PASS' if gd else 'FAIL'}")
    G(f"{'GE':<7}{'canonical weekly net == $1,393.573663 (G00000)':<62}"
      f"{f'${base_weekly:,.6f} (t {base_t:.3f})':<28}{'PASS' if ge_base else 'FAIL'}")
    G(f"{'seal':<7}{'assert_presealed on substrate + trade streams':<62}"
      f"{'no value >= 2026-08-01 read':<28}PASS")
    G("-" * 108)
    G(f"{'R_a':<7}{'top ceil(10%)=214 trades carry <= 40% of total net':<62}"
      f"{f'{100*top_share:.1f}% (secondary {100*top_share2:.1f}%)':<28}"
      f"{'PASS' if ra_pass else 'FAIL'}")
    G(f"{'R_a+':<7}{'(non-gate) top-decile WEEKS share (22 of 213)':<62}"
      f"{f'{100*top_wk_share_primary:.1f}% pnl / {100*top_wk_share_net:.1f}% net':<28}"
      f"REPORTED")
    G(f"{'R_a+':<7}{'(non-gate) B-MOM-enabled share of net (frozen stream)':<62}"
      f"{f'{100*en_share:.1f}%':<28}REPORTED")
    G(f"{'R_a+':<7}{'(non-gate) recorded ~51% flag from arms.csv':<62}"
      f"{f'{flag51:.1f}% (LEGACY_DIAGNOSTIC)':<28}REPORTED")
    G(f"{'R_b':<7}{'LOYO 2022..2026: excluding any year, total net > 0':<62}"
      f"{f'min excl ex-{min_excl[0]}: ${min_excl[1]:,.0f}':<28}"
      f"{'PASS' if rb_pass else 'FAIL'}")
    G(f"{'R_b-era':<7}{'pre-2022 era rung':<62}{'see reason below':<28}NOT-ATTEMPTABLE")
    G("  era reason: deep member/tilt/bmom caches + constants frozen on the modern load;")
    G("  a pre-2022 run is a NEW experiment, not a rung. Nearest recorded artifact")
    G("  (cited only, DIFFERENT variant, pre-W98 exit engine, LEGACY_DIAGNOSTIC):")
    G("  WE_W97_AUDITFIX M10 deep 2006-2021 P1-variant net +$79,076, 44.5% positive wks.")
    G(f"{'R_c':<7}{'PRE-STATED band (quoted above): [2%, 40%] degradation':<62}"
      f"{f'{degr:+.2f}% ({e3_mean:+.2f}/wk, SE {e3_se:.2f})':<28}{rc_verdict}")
    G(f"{'R_c+':<7}{'consistency vs EXEC01 E3 recorded -$89.62/wk (-6.4%)':<62}"
      f"{f'gap ${exec01_gap:.2f}':<28}"
      f"{'CONSISTENT' if exec01_ok else 'DISCREPANCY'}")
    G(f"{'R_d':<7}{'mask identity: reconstructed gross == trade gross':<62}"
      f"{f'${gross_mask:,.2f}':<28}{'PASS' if gf_identity else 'FAIL'}")
    sens_spread = sens["spread"]
    nul_pct = 100 * nul["percentile"]
    G(f"{'R_d':<7}{'null sensitivity (null_guard) verified before use':<62}"
      f"{f'spread ${sens_spread:,.0f}':<28}"
      f"{'PASS' if gg_sens else 'FAIL'}")
    G(f"{'R_d':<7}{f'actual gross > shifted-mask p95 ({n_shifts} shifts)':<62}"
      f"{f'${real_stat:,.0f} vs ${p95:,.0f} (pct {nul_pct:.1f})':<28}"
      f"{'PASS' if rd_pass_final else 'FAIL'}")
    G("-" * 108)
    G(f"RUNG SUMMARY: R_a {'PASS' if ra_pass else 'FAIL'} | R_b "
      f"{'PASS' if rb_pass else 'FAIL'} (era NOT-ATTEMPTABLE) | R_c {rc_verdict} | "
      f"R_d {'PASS' if rd_pass_final else 'FAIL'}")
    G(f"BATTERY VERDICT: {'ALL ATTEMPTED RUNGS PASS' if overall else 'NOT ALL RUNGS PASS'}"
      f" — no automatic demotion, no automatic celebration (spec verdict_semantics);")
    G("summary updates GENESIS_INCUMBENT_DOSSIER and the shadow's interpretive frame")
    G("(orchestrator action — this team writes nothing outside its run directory).")
    G("")
    G(MULTIPLICITY)
    G("")
    G("prohibition compliance: no parameter changed; no rescue analysis; no sealed read;")
    G("no new economics beyond the rungs; no git; no CrossTrade; no SEARCH_LEDGER append;")
    G("all writes under runs/G2_F9_P1_SYMCERT_20260829/ only. LIVE ENABLED = NO. $0.")
    wall = _time.time() - T0
    G(f"wall time: {wall:.0f} s")
    wr(os.path.join(OUT, "gate_table.txt"), glines)
    log("gate_table.txt written")

    # ================================================================ ledger result
    result = "PASS" if overall else "FAIL"
    payload = {
        "trial_id": "G00039",
        "metrics": {
            "r_a_top214_share_pct": round(100 * top_share, 2),
            "r_a_top214_share_netofspread_pct": round(100 * top_share2, 2),
            "r_a_top22_weeks_share_pnl_pct": round(100 * top_wk_share_primary, 2),
            "r_a_top22_weeks_share_net_pct": round(100 * top_wk_share_net, 2),
            "bmom_enabled_share_pct": round(100 * en_share, 2),
            "bmom_51_flag_rederived_pct": round(flag51, 2),
            "r_b_min_exclusion_year": min_excl[0],
            "r_b_min_exclusion_net": round(min_excl[1], 2),
            "r_b_era": "NOT-ATTEMPTABLE",
            "r_c_delta_net_per_week": round(e3_mean, 2),
            "r_c_se_per_week": round(e3_se, 2),
            "r_c_degradation_pct": round(degr, 2),
            "r_c_band": "[2%, 40%]",
            "r_c_exec01_gap": round(exec01_gap, 2),
            "r_d_actual_gross": round(real_stat, 2),
            "r_d_null_p95": round(p95, 2),
            "r_d_percentile": round(100 * nul["percentile"], 2),
            "r_d_p_ge": round(nul["p_ge"], 5),
            "r_d_n_shifts": n_shifts,
            "verdicts": {"R_a": "PASS" if ra_pass else "FAIL",
                         "R_b": "PASS" if rb_pass else "FAIL",
                         "R_b_era": "NOT-ATTEMPTABLE",
                         "R_c": rc_verdict,
                         "R_d": "PASS" if rd_pass_final else "FAIL"},
            "wall_s": round(wall),
        },
        "result": result,
        "note": (f"Symmetric certification of the incumbent (evidence, not veto; owner "
                 f"doctrine keeps P1 incumbent regardless). R_a top-214 share "
                 f"{100*top_share:.1f}% vs 40% bar; R_b LOYO min ex-{min_excl[0]} "
                 f"${min_excl[1]:,.0f}; era NOT-ATTEMPTABLE; R_c degradation "
                 f"{degr:+.2f}% vs preregistered band [2%,40%] -> {rc_verdict}; R_d mask "
                 f"null pct {100*nul['percentile']:.1f} vs p95 gate -> "
                 f"{'PASS' if rd_pass_final else 'FAIL'}. Valence band quoted before "
                 f"measurement. " + MULTIPLICITY),
    }
    with open(os.path.join(OUT, "ledger_result_pending.json"), "w",
              encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    log("ledger_result_pending.json written —", result)


if __name__ == "__main__":
    main()
