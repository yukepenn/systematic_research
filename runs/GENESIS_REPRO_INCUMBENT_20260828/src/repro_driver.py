"""GENESIS_REPRO_INCUMBENT_20260828 — TEAM R1 driver (trial G00000).

Re-executes the recorded incumbent generating chain (load_deep -> votes -> fills_daily ->
causal_score -> gfills -> W103 economics assembly) in a fresh process, from the raw parquets
+ the W82 spread profile + the recorded mem_ext.npz cache, and compares against the recorded
runs/WE_W103_CONSOLIDATE/out/components.csv.

The economics code below is a VERBATIM transcription of run_we_w103.main()'s component
construction (those helpers are defined inside main() and cannot be imported), plus the
sequential XM sigma loop transcribed verbatim from export_xm_reference.main(). No parameter,
constant, or ordering was changed. All outputs go ONLY to this run's out/ directory.

Writes: out/repro_components.csv, out/population_reconciliation.txt, out/gate_table.txt,
out/ledger_result_pending.json, out/run_provenance.txt. Never touches runs/WE_*.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
import time as _time

os.environ.setdefault("MPLBACKEND", "Agg")   # headless if anything imports matplotlib

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "GENESIS_REPRO_INCUMBENT_20260828")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
SRC = os.path.join(ROOT, "research", "weekly_edge", "src")
sys.path.insert(0, SRC)

T0 = _time.time()


def log(*a):
    print(f"[{_time.time()-T0:7.0f}s]", *a, flush=True)


log("importing recorded chain modules (side effects: os.makedirs(exist_ok=True) only)")
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import PV, COMM_RT                                       # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames                                    # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w97 import votes                                             # noqa: E402
from run_we_w98 import gfills, arm_kw                                    # noqa: E402
from we_channels import build_channels                                   # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
SEAL = np.datetime64("2026-08-01")
DDT = 20245.0
TICKV = 5.0
ANCH, DEC, ENTM, EXITM, EXITNB = 571, 585, 586, 945, 946   # W102c / export_xm_reference
SIG_LB, SIG_MIN = 60, 20
XM = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
      "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
      "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}
COMPS = ("P1_PCT", "X9a_PCT", "BMOM", "PAIR23", "XM_CONFLICT")

INPUT_FILES = [
    os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                 "nq1m_2005_202605.parquet"),
    os.path.join(ROOT, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet"),
    os.path.join(ROOT, XM["ES"]),
    os.path.join(ROOT, XM["RTY"]),
    os.path.join(ROOT, XM["YM"]),
    os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out", "mem_ext.npz"),
    os.path.join(ROOT, "runs", "WE_W82_FILLAUDIT", "out", "spread_by_minute.csv"),
]
RECORDED_COMPONENTS = os.path.join(ROOT, "runs", "WE_W103_CONSOLIDATE", "out",
                                   "components.csv")
NT8_TRADES = os.path.join(ROOT, "runs", "WE_P1PCT_PARITY_20260827", "out",
                          "nt8_trades_p1pct.csv")
PY_TRADES_ARTIFACT = os.path.join(ROOT, "runs", "WE_P1PCT_PARITY_20260827", "out",
                                  "py_trades_p1pct.csv")


def sha256_stream(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main():
    # ------------------------------------------------------------------ provenance
    prov = []
    prov.append("GENESIS_REPRO_INCUMBENT_20260828 — input provenance (printed by program)")
    prov.append(f"python {sys.version.split()[0]}  numpy {np.__version__}  "
                f"pandas {pd.__version__}")
    for p in INPUT_FILES + [RECORDED_COMPONENTS, NT8_TRADES, PY_TRADES_ARTIFACT]:
        st = os.stat(p)
        prov.append(f"  {sha256_stream(p)}  {st.st_size:>12,} B  "
                    f"mtime {pd.Timestamp(st.st_mtime, unit='s').strftime('%Y-%m-%d %H:%M:%S')}  "
                    f"{os.path.relpath(p, ROOT)}")
        log("hashed", os.path.basename(p))
    prov.append("  NOTE: mem_ext.npz is USED AS THE RECORDED CACHE (concordance mode: "
                "code+cache -> artifact), exactly as run_we_w103 uses it.")

    # ------------------------------------------------------------------ substrate
    log("load_deep 2022-01-01 -> 2026-07-31 17:00 extend=True")
    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    o, c, h, l, v = D["o"], D["c"], D["h"], D["l"], D["v"]
    if not (tarr.max() < SEAL):
        raise SystemExit("SEAL VIOLATION: substrate contains bars >= 2026-08-01 — ABORT")
    log(f"substrate bars {n:,}  sessions {D['n_sess']:,}  seal check max(t) < 2026-08-01: OK")

    st_, en_, _ = session_frames(D)
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    NSESS = D["n_sess"]
    sdate = pd.to_datetime(D["sess_date"])
    iso = sdate.isocalendar()
    wkall = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    win = np.array([A <= tarr[st_[s]] < B for s in range(NSESS)])
    sess_in = np.flatnonzero(win)
    wk = wkall[sess_in]
    log(f"in-window sessions {len(sess_in):,}  weeks {len(set(wk)):,}")

    log("fast_build_context")
    X = fast_build_context(D)
    z = np.load(os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out", "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    if mem.shape[0] != n:
        raise SystemExit(f"mem_ext.npz rows {mem.shape[0]:,} != substrate bars {n:,} — ABORT")
    log(f"mem_ext.npz cache loaded: mem {mem.shape}, bmom/tilt len {len(bmom):,}")
    CH = build_channels(D, which=["X9a_disp_sessanchor"])
    flatm = tarr >= D["sess_end"][sid] - np.timedelta64(21 * 60, "s")

    # ---------------- helpers transcribed VERBATIM from run_we_w103.main() ----------------
    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def net_series(tr):
        w_ = {}
        for x in tr:
            for ts in (x["et"], x["xt"]):
                p_ = pd.Timestamp(ts); m2 = p_.hour * 60 + p_.minute
                w_[m2] = w_.get(m2, 0.0) + x["u"]
        rate = TICKV * sum(float(prof.get(m2, 3.0)) * q for m2, q in w_.items()) / \
            max(sum(w_.values()), 1e-9)
        s_ = np.zeros(NSESS); ct = np.zeros(NSESS)
        for x in tr:
            si = int(sid[i_of(x["et"])])
            if win[si]:
                s_[si] += x["pnl"] - rate * x["u"]; ct[si] += x["u"]
        return s_, ct, rate, len(tr)

    def obj(chan):
        vl, _ = votes(D, mem, bmom, tilt, X, chan)
        p = vl.astype(np.int8)
        bb = fills_daily(D, p, halt=1300, target=1000)
        ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
        sc, _ = causal_score(X, ee, window=WIN)
        tr = gfills(D, p, np.where(sc >= 3, 2, 1).astype(np.int8), **arm_kw("PCT", 1.183))
        return net_series(tr), tr

    SER, CTR, RATE, NTR = {}, {}, {}, {}
    log("building P1_PCT (votes -> fills_daily -> causal_score -> gfills)")
    (SER["P1_PCT"], CTR["P1_PCT"], RATE["P1_PCT"], NTR["P1_PCT"]), trP = obj(bmom)
    log(f"P1_PCT built: {NTR['P1_PCT']:,} total trades")
    log("building X9a_PCT")
    (SER["X9a_PCT"], CTR["X9a_PCT"], RATE["X9a_PCT"], NTR["X9a_PCT"]), _trX = \
        obj(CH["X9a_disp_sessanchor"])
    log(f"X9a_PCT built: {NTR['X9a_PCT']:,} total trades")
    log("building BMOM")
    trB = gfills(D, np.where(flatm, 0, bmom).astype(np.int8), None, **arm_kw("PCT", 1.0))
    SER["BMOM"], CTR["BMOM"], RATE["BMOM"], NTR["BMOM"] = net_series(trB)
    log(f"BMOM built: {NTR['BMOM']:,} total trades")
    SER["PAIR23"] = (2 * SER["BMOM"] + 3 * SER["X9a_PCT"]) / 5.0
    CTR["PAIR23"] = (2 * CTR["BMOM"] + 3 * CTR["X9a_PCT"]) / 5.0
    RATE["PAIR23"] = np.nan; NTR["PAIR23"] = 2 * NTR["BMOM"] + 3 * NTR["X9a_PCT"]

    # ---------------- XM_CONFLICT, vectorised — VERBATIM from run_we_w103.main() ----------
    log("XM_CONFLICT vectorised block")
    nq = pd.DataFrame({"time": pd.to_datetime(tarr), "nq": c}).set_index("time")
    XD = {}
    for k, path in XM.items():
        d_ = pd.read_parquet(os.path.join(ROOT, path), columns=["time", "close"])
        d_["time"] = pd.to_datetime(d_["time"])
        XD[k] = nq.join(d_.set_index("time")["close"].rename(k), how="left")[k].to_numpy()

    def at(mv, arr, uo=False):
        r = np.full(NSESS, np.nan)
        m_ = mod == mv
        r[sid[m_]] = (o[m_] if uo else arr[m_])
        return r
    pa, pdc, pe, px = at(ANCH, o, True), at(DEC, c), at(ENTM, o, True), at(EXITM, c)
    drive = np.sign(pdc - pa)
    acc = np.zeros(NSESS); cnt = np.zeros(NSESS)
    for k in XM:
        a_, b_ = at(ANCH, XD[k]), at(DEC, XD[k])
        r_ = np.log(b_ / a_)
        s_ = pd.Series(r_).rolling(60, min_periods=20).std().shift(1).to_numpy()
        zz = r_ / np.maximum(s_, 1e-12)
        g = np.isfinite(zz); acc[g] += zz[g]; cnt[g] += 1
    xs = np.sign(np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan))
    okm = (win & np.isfinite(pa) & np.isfinite(pdc) & np.isfinite(pe) & np.isfinite(px) &
           np.isfinite(xs) & (drive != 0) & (xs != 0))
    cf = okm & (xs != drive)
    cstx = COMM_RT + TICKV * (float(prof.loc[ENTM]) + float(prof.loc[EXITM])) / 2.0
    sxm = np.zeros(NSESS); ctx = np.zeros(NSESS)
    sxm[cf] = drive[cf] * (px[cf] - pe[cf]) * PV - cstx
    ctx[cf] = 1.0
    SER["XM_CONFLICT"], CTR["XM_CONFLICT"] = sxm, ctx
    RATE["XM_CONFLICT"] = cstx - COMM_RT; NTR["XM_CONFLICT"] = int(cf.sum())
    log(f"XM_CONFLICT vectorised: {int(cf.sum()):,} trades")

    # ---------------- weekly aggregation + pan — VERBATIM from run_we_w103.main() ---------
    def wkv(x):
        return pd.Series(x[sess_in]).groupby(wk).sum().to_numpy()
    WKS = {k: wkv(SER[k]) for k in COMPS}

    def pan(w):
        dp = dd_profile(w)
        stk = max((len(list(g)) for k_, g in itertools.groupby(w < 0) if k_), default=0)
        cq = max(1, int(round(0.05 * len(w))))
        return dict(weekly=float(w.mean()), fixdd=float(w.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    poswk=100 * float((w > 0).mean()), maxdd=dp["maxdd"],
                    top5=dp["dd_mean_top5"], worst=float(w.min()),
                    cvar5=float(np.sort(w)[:cq].mean()), streak=int(stk),
                    t=float(w.mean()) / max(w.std(ddof=1) / np.sqrt(len(w)), 1e-9))

    srows = []
    for k in COMPS:
        a_ = pan(WKS[k])
        srows.append(dict(component=k, trades=NTR[k], rate=RATE[k], **a_))
    REPRO = pd.DataFrame(srows)
    REPRO.to_csv(os.path.join(OUT, "repro_components.csv"), index=False)
    log("repro_components.csv written")

    # ---------------- XM sequential sigma loop — VERBATIM from export_xm_reference.main() -
    log("XM_CONFLICT sequential (frozen executable rule) block")
    XTS = {k: ~np.isnan(XD[k]) for k in XM}

    def at2(mv, arr, uo=False):
        r = np.full(NSESS, np.nan); ix = np.full(NSESS, -1, np.int64)
        m_ = mod == mv
        r[sid[m_]] = (o[m_] if uo else arr[m_]); ix[sid[m_]] = np.flatnonzero(m_)
        return r, ix
    pa2, ia = at2(ANCH, o, True)
    pdc2, idc = at2(DEC, c)
    pe2, ie = at2(ENTM, o, True)
    px_close, ix_c = at2(EXITM, c)
    px_nbo, ix_n = at2(EXITNB, o, True)
    HIST = {k: [] for k in XM}
    drive2 = np.zeros(NSESS); comp2 = np.full(NSESS, np.nan)
    conflict2 = np.zeros(NSESS, np.int8); desired2 = np.zeros(NSESS, np.int8)
    disq = np.zeros(NSESS, bool)
    for s in range(NSESS):
        if not np.isfinite(pa2[s]) or not np.isfinite(pdc2[s]):
            continue
        ok = True
        for k in XM:
            if ia[s] < 0 or idc[s] < 0 or not XTS[k][ia[s]] or not XTS[k][idc[s]]:
                ok = False
        if not ok:
            disq[s] = True
            continue
        if not win[s]:
            for k in XM:
                HIST[k].append(np.log(XD[k][idc[s]] / XD[k][ia[s]]))
            continue
        drive2[s] = np.sign(pdc2[s] - pa2[s])
        acc2, cnt2 = 0.0, 0
        for k in XM:
            r_ = np.log(XD[k][idc[s]] / XD[k][ia[s]])
            hh = HIST[k]
            if len(hh) >= SIG_MIN:
                w = hh[-SIG_LB:]
                sg = float(np.std(w, ddof=1))
                if sg > 1e-12:
                    acc2 += r_ / sg; cnt2 += 1
            hh.append(r_)
        if cnt2:
            comp2[s] = acc2 / cnt2
            xs2 = np.sign(comp2[s])
            if xs2 != 0 and drive2[s] != 0 and xs2 != drive2[s]:
                conflict2[s] = 1; desired2[s] = int(drive2[s])
    take = (desired2 != 0) & np.isfinite(pe2) & np.isfinite(px_close) & np.isfinite(px_nbo)
    desired2 = np.where(take, desired2, 0).astype(np.int8)
    n_seq = int((desired2 != 0).sum())
    n_seq_long = int((desired2 > 0).sum()); n_seq_short = int((desired2 < 0).sum())
    vec_set = set(np.flatnonzero(cf).tolist())
    seq_set = set(np.flatnonzero(desired2 != 0).tolist())
    only_vec = sorted(vec_set - seq_set); only_seq = sorted(seq_set - vec_set)
    log(f"sequential: {n_seq} trades ({n_seq_long}L/{n_seq_short}S); "
        f"vec-only {len(only_vec)}, seq-only {len(only_seq)}")

    # ---------------- population reconciliation (printed by program) ----------------------
    ets = np.array([np.datetime64(x["et"]) for x in trP])
    n_total = len(trP)
    n_tsfilter = int(((ets >= A) & (ets < B)).sum())
    n_sessfilter = int(sum(1 for x in trP if win[int(sid[i_of(x["et"])])]))
    NT = pd.read_csv(NT8_TRADES)
    nt_ets = NT["et"].to_numpy()
    n_nt8_raw = len(NT)
    # NAMED definition of the circulating 2,137 (run_p1pct_parity.py:107): ENTRY-TIMESTAMP
    # filter on the NT8 serialized list — NOT the session-start filter the Python side used.
    nt_ts = pd.to_datetime(NT["et"])
    n_nt8_win = int(((nt_ts >= pd.Timestamp("2022-07-01"))
                     & (nt_ts < pd.Timestamp("2026-08-01"))).sum())
    # session-start variant, for the asymmetry note (parity headline compared 2,131
    # session-filtered Python vs 2,137 ts-filtered NT8):
    n_nt8_sessfilter = int(sum(1 for t_ in nt_ets if win[int(sid[i_of(t_)])]))
    PYA = pd.read_csv(PY_TRADES_ARTIFACT)
    n_py_artifact = len(PYA)

    rec_lines = []

    def R(*a):
        s = " ".join(str(x) for x in a)
        rec_lines.append(s); print(s, flush=True)

    R("=" * 100)
    R("POPULATION RECONCILIATION — the four circulating P1/PCT trade counts, each computed")
    R("from code in this process against its NAMED definition (GENESIS G2).")
    R("=" * 100)
    R(f"substrate: {n:,} bars, {NSESS:,} sessions loaded 2022-01-01 -> 2026-07-31 17:00;")
    R(f"in-window [2022-07-01, 2026-08-01) by SESSION-START filter: {len(sess_in):,} sessions, "
      f"{len(set(wk)):,} ISO weeks (session-date convention)")
    R("")
    R(f"{'count':>7}  {'named definition':<74} {'observed':>9}  verdict")
    rows = [
        (2401, "ALL gfills trades over the full 2022-01 load INCLUDING Jan-Jun 2022 warm-up "
               "(components.csv 'trades')", n_total),
        (2139, "ENTRY-TIMESTAMP filter: trades with 2022-07-01 <= entry_ts < 2026-08-01 "
               "(RR_W001 ts-filter)", n_tsfilter),
        (2131, "SESSION-START filter: trades whose session's first bar is in-window "
               "(parity run / CURRENT_BASELINE)", n_sessfilter),
        (2137, "NT8 Strategy Analyzer trades under the ENTRY-TIMESTAMP filter (recorded "
               "parity artifact; run_p1pct_parity.py:107)", n_nt8_win),
    ]
    all_pop_ok = True
    for want, desc, got in rows:
        ok = (got == want)
        all_pop_ok &= ok
        R(f"{want:>7,}  {desc:<74} {got:>9,}  {'MATCH' if ok else 'MISMATCH'}")
    R("")
    R(f"cross-checks: NT8 raw serialized list (2022-01-03 load, incl. warm-up) = "
      f"{n_nt8_raw:,} rows; recorded Python parity artifact py_trades_p1pct.csv = "
      f"{n_py_artifact:,} rows (expected 2,131)")
    R(f"gap arithmetic: 2401-2139 = {n_total - n_tsfilter} warm-up-by-timestamp trades; "
      f"2139-2131 = {n_tsfilter - n_sessfilter} trades with entry_ts >= 2022-07-01 inside a "
      f"session that STARTED before 2022-07-01 (session-start filter excludes them).")
    R("")
    R("FILTER-ASYMMETRY FINDING (programmatic): the recorded parity headline compared the")
    R("Python list under the SESSION-START filter (2,131) against the NT8 list under the")
    R(f"ENTRY-TIMESTAMP filter (2,137). The NT8 list under the SAME session-start filter is "
      f"{n_nt8_sessfilter:,},")
    R(f"so {n_nt8_win - n_nt8_sessfilter} of the +6 headline gap is window-filter asymmetry "
      f"(boundary-session trades, e.g. the 2022-07-01")
    R("day session that started 2022-06-30 18:00), not engine disagreement. "
      "Apples-to-apples counts:")
    R(f"  session-start filter: Python {n_sessfilter:,} vs NT8 {n_nt8_sessfilter:,} "
      f"({100*abs(n_nt8_sessfilter-n_sessfilter)/n_sessfilter:.2f} %)")
    R(f"  entry-ts filter:      Python {n_tsfilter:,} vs NT8 {n_nt8_win:,} "
      f"({100*abs(n_nt8_win-n_tsfilter)/n_tsfilter:.2f} %)")
    R("")
    R("XM_CONFLICT population reconciliation (GENESIS G3):")
    R(f"  vectorised (pandas rolling(60,20).shift(1) sigma; W102c/W103 headline) : "
      f"{int(cf.sum()):>4} trades")
    R(f"  sequential (causal loop, appended-after-use; reference + certified C#) : "
      f"{n_seq:>4} trades ({n_seq_long}L/{n_seq_short}S)")
    R(f"  sessions where the two disagree: vec-only "
      f"{[sdate[s].strftime('%Y-%m-%d') for s in only_vec]}, seq-only "
      f"{[sdate[s].strftime('%Y-%m-%d') for s in only_seq]}")
    R("  mechanism: pandas rolling std tolerates an interior NaN in the 60-window; the")
    R("  sequential loop disqualifies that session's sigma history entry instead.")
    R(f"  sessions disqualified by a missing/stale secondary bar: {int(disq.sum())}")
    with open(os.path.join(OUT, "population_reconciliation.txt"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(rec_lines) + "\n")
    log("population_reconciliation.txt written")

    # ---------------- gate table (printed by program, never hand-assembled) ---------------
    REC = pd.read_csv(RECORDED_COMPONENTS).set_index("component")
    RP = REPRO.set_index("component")
    glines = []

    def G(*a):
        s = " ".join(str(x) for x in a)
        glines.append(s); print(s, flush=True)

    G("=" * 108)
    G("GENESIS_REPRO_INCUMBENT_20260828 — GATE TABLE (printed by program)")
    G("recorded reference: runs/WE_W103_CONSOLIDATE/out/components.csv")
    G("=" * 108)
    G(f"{'GATE':<6}{'SPEC':<58}{'OBSERVED':<32}{'PASS/FAIL'}")
    verdicts = {}

    def num_gate(gid, comp, field, tol=0.01):
        rec = float(REC.loc[comp, field]); obs = float(RP.loc[comp, field])
        d = abs(obs - rec)
        ok = d <= tol
        G(f"{gid:<6}{comp + ' ' + field + f' == {rec:.6f} ±{tol}':<58}"
          f"{f'{obs:.6f} (Δ {d:.2e})':<32}{'PASS' if ok else 'FAIL'}")
        return ok

    # G1 — P1_PCT row
    g1 = True
    for fld in ("weekly", "fixdd", "maxdd", "t"):
        g1 &= num_gate("G1", "P1_PCT", fld)
    ok_tr = int(RP.loc["P1_PCT", "trades"]) == int(REC.loc["P1_PCT", "trades"])
    g1 &= ok_tr
    G(f"{'G1':<6}{'P1_PCT trades == ' + str(int(REC.loc['P1_PCT','trades'])):<58}"
      f"{int(RP.loc['P1_PCT','trades']):<32}{'PASS' if ok_tr else 'FAIL'}")
    ok_rate = abs(float(RP.loc["P1_PCT", "rate"]) - float(REC.loc["P1_PCT", "rate"])) <= 0.01
    G(f"{'G1':<6}{'P1_PCT $/ctrRT spread rate ±0.01 (informational)':<58}"
      f"{float(RP.loc['P1_PCT','rate']):<32.6f}{'PASS' if ok_rate else 'FAIL'}")
    verdicts["G1"] = g1

    # G2 — populations
    G(f"{'G2':<6}{'four populations reconcile to named definitions':<58}"
      f"{f'{n_total}/{n_tsfilter}/{n_sessfilter}/NT8 {n_nt8_win}':<32}"
      f"{'PASS' if all_pop_ok else 'FAIL'}")
    verdicts["G2"] = all_pop_ok

    # G3 — XM_CONFLICT row + 348/346 reconciliation
    g3 = True
    for fld in ("weekly", "fixdd", "maxdd", "t"):
        g3 &= num_gate("G3", "XM_CONFLICT", fld)
    ok_348 = int(cf.sum()) == 348 and int(RP.loc["XM_CONFLICT", "trades"]) == 348
    G(f"{'G3':<6}{'XM vectorised trades == 348':<58}{int(cf.sum()):<32}"
      f"{'PASS' if ok_348 else 'FAIL'}")
    ok_346 = (n_seq == 346)
    G(f"{'G3':<6}{'XM sequential trades == 346 (reconciliation printed)':<58}"
      f"{f'{n_seq} ({n_seq_long}L/{n_seq_short}S)':<32}{'PASS' if ok_346 else 'FAIL'}")
    g3 &= ok_348 & ok_346
    verdicts["G3"] = g3

    G("-" * 108)
    for k in ("G1", "G2", "G3"):
        G(f"{k}: {'PASS' if verdicts[k] else 'FAIL'}")
    overall = all(verdicts.values())
    G(f"OVERALL: {'PASS — RECORDED CLAIM upgraded to REPRODUCED FACT (backtest artifact)' if overall else 'FAIL — STOP: do not interpret economics further'}")
    G("")
    G("informational deltas, all five components (repro − recorded), $ columns:")
    for comp in COMPS:
        ds = {f: float(RP.loc[comp, f]) - float(REC.loc[comp, f])
              for f in ("weekly", "fixdd", "maxdd", "t")}
        G(f"  {comp:<12} " + "  ".join(f"{f} {ds[f]:+.6f}" for f in ds))

    try:
        import psutil
        peak = psutil.Process().memory_info().peak_wset / 1e9
        G(f"peak working set: {peak:.2f} GB")
    except Exception:
        peak = None
    wall = _time.time() - T0
    G(f"wall time: {wall:.0f} s")
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(glines) + "\n")
    log("gate_table.txt written")

    with open(os.path.join(OUT, "run_provenance.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(prov) + f"\nwall_s {wall:.0f}\npeak_gb "
                f"{peak if peak is not None else 'n/a'}\n")

    # ---------------- ledger result (pending; orchestrator appends centrally) -------------
    result = {
        "trial_id": "G00000",
        "metrics": {
            "p1_weekly": float(RP.loc["P1_PCT", "weekly"]),
            "p1_fixdd": float(RP.loc["P1_PCT", "fixdd"]),
            "p1_maxdd": float(RP.loc["P1_PCT", "maxdd"]),
            "p1_t": float(RP.loc["P1_PCT", "t"]),
            "p1_trades_total": n_total,
            "p1_trades_ts_filter": n_tsfilter,
            "p1_trades_sess_filter": n_sessfilter,
            "nt8_trades_ts_filter_recorded_artifact": n_nt8_win,
            "nt8_trades_sess_filter_recorded_artifact": n_nt8_sessfilter,
            "xm_weekly": float(RP.loc["XM_CONFLICT", "weekly"]),
            "xm_fixdd": float(RP.loc["XM_CONFLICT", "fixdd"]),
            "xm_maxdd": float(RP.loc["XM_CONFLICT", "maxdd"]),
            "xm_t": float(RP.loc["XM_CONFLICT", "t"]),
            "xm_vectorised_trades": int(cf.sum()),
            "xm_sequential_trades": n_seq,
            "g1": bool(verdicts["G1"]), "g2": bool(verdicts["G2"]),
            "g3": bool(verdicts["G3"]),
            "wall_s": round(wall),
        },
        "result": "PASS" if overall else "FAIL",
        "note": ("Incumbent pipeline re-run from raw parquets + recorded mem_ext.npz cache "
                 "(concordance mode); W103 economics transcribed verbatim; all gates "
                 + ("passed — headline upgraded RECORDED CLAIM -> REPRODUCED FACT "
                    "(backtest; DISCOVERY_CONSUMED unchanged, no forward claim)."
                    if overall else
                    "NOT all passed — discrepancy documented in gate_table.txt; economics "
                    "not interpreted further per spec on_fail.")),
    }
    with open(os.path.join(OUT, "ledger_result_pending.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    log("ledger_result_pending.json written —", result["result"])


if __name__ == "__main__":
    main()
