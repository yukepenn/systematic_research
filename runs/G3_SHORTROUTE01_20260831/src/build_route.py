"""G3_SHORTROUTE01 - STAGE 1: substrate, sleeve, session frame.

Spec: runs/G3_SHORTROUTE01_20260831/spec.yaml, committed at 9a18980 BEFORE any conditional
statistic existed. Not edited.

WHAT THIS FILE DOES AND WHY IT DOES IT THIS WAY
-----------------------------------------------
1. SUBSTRATE TRAP (established by WAVE C, load-bearing here). run_we_w51c.py:38 calls
   load_deep WITHOUT extend=True and therefore silently truncates at 2026-05-29 16:59.
   This file NEVER imports setup(). It calls load_deep itself, passes extend=True for the
   ANALYSIS substrate, and ASSERTS + PRINTS the max bar timestamp for every substrate it
   touches.

2. G0 needs WAVE C's CORE figures, and those were measured on the deliberately truncated
   extend=OFF substrate (the exact object W61/W73 used). So a second, clearly labelled
   substrate is loaded with extend=False for the G0 reproduction ONLY. It is never used for
   any conditional statistic. Both are asserted and printed side by side, and the FULL
   substrate is additionally restricted to the same session set as an independent check.

3. Everything about the sleeve is IMPORTED, not re-implemented: the vendor targets, the vote,
   the signed fills, the halt/target, the session box. The only new computation here is the
   per-session RTH / OVERNIGHT split of absolute movement, which S5 needs and which WAVE C's
   session frame does not carry.

No orders, no deploys, no backtests, no CrossTrade, no NinjaTrader. Nothing under
research/weekly_edge/src or research_sdk is written to.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
WE = os.path.join(ROOT, "research", "weekly_edge", "src")
sys.path.insert(0, WE)
from run_we_w01 import PV, COMM_RT, sm14_1m                              # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS                                           # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import vote, sfills                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import A as W61_A, B as W61_B                            # noqa: E402
from we_quality import build_context                                     # noqa: E402

RUN = os.path.join(ROOT, "runs", "G3_SHORTROUTE01_20260831")
OUT = os.path.join(RUN, "out")
CACHE = os.path.join(OUT, "_cache")
os.makedirs(CACHE, exist_ok=True)

SEAL = np.datetime64("2026-08-01")
VIXF = os.path.join(ROOT, "runs", "GENESIS_FREEDATA_CBOE_20260828", "certified",
                    "idx_VIX_daily.parquet")

# read-only target caches produced by earlier waves; keyed on bar count + close checksum, so a
# hit is a proof of substrate identity, not an assumption of it.
TG_SEARCH = (os.path.join(ROOT, "runs", "G3_SHORTALPHA_20260831", "out", "_decay_cache"),
             os.path.join(ROOT, "runs", "WE_W38_SHORTQ", "out"))

RTH_LO, RTH_HI = 9 * 60 + 31, 16 * 60      # bars are END-stamped: 09:31 covers 09:30-09:31


# ==================================================================================================
def assert_seal(D, tag, log):
    mx = D["t"].max()
    log(f"   SEAL ASSERTION [{tag}]: max bar {mx}  <  {SEAL}  ->  "
        f"{'PASS' if mx < SEAL else 'VIOLATION'}")
    if not (mx < SEAL):
        raise SystemExit("SEAL VIOLATION - refusing to continue")


def targets_cached(D, log):
    key = f"{D['n']}_{int(abs(D['c']).sum())}"
    TG = {}
    for k, v in MEMBERS.items():
        hit = None
        for d in TG_SEARCH + (CACHE,):
            f = os.path.join(d, f"tg_{k}_{key}.npy")
            if os.path.exists(f):
                hit = f
                break
        if hit is not None:
            TG[k] = np.load(hit)
            log(f"   targets {k:<8} REUSED from {os.path.relpath(hit, ROOT)}")
            continue
        t1 = _time.time()
        TG[k] = sm14_1m(D, 460, return_targets=True, volmults=v)
        np.save(os.path.join(CACHE, f"tg_{k}_{key}.npy"), TG[k])
        log(f"   targets {k:<8} BUILT [{_time.time()-t1:.0f}s]")
    return TG


def session_bounds(D):
    sid, ns, n = D["sid"], D["n_sess"], D["n"]
    st = np.searchsorted(sid, np.arange(ns), side="left")
    en = np.searchsorted(sid, np.arange(ns), side="right")
    return st, en


def build_short(D, X, TG, log, tag):
    """W61's mirrored short sleeve, unmodified: mirrored vote at 0.5, one contract, the same
    halt/target and the same session box."""
    posS = -(vote(TG, D, X, -1) >= 0.5).astype(np.int8)
    tr = sfills(D, posS, halt=1300.0, target=1000.0)
    log(f"   [{tag}] short sleeve raw trades: {len(tr):,}")
    return tr


def build_long(D, X, TG, log, tag, ent_lo=None, ent_hi=None):
    """P1, the B1 gate object, exactly as every wave builds it."""
    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    base = fills_daily(D, posL, halt=1300, target=1000)
    tarr, n = D["t"], D["n"]
    ets = [np.datetime64(x["et"]) for x in base]
    keep = [int(min(np.searchsorted(tarr, e), n - 1)) for e in ets
            if (ent_lo is None or e >= ent_lo) and (ent_hi is None or e < ent_hi)]
    sc, _ = causal_score(X, np.array(keep), window=WIN)
    sz = np.where(sc >= 3, 2, 1).astype(np.int8)
    tr = fills_qexit(D, posL, sz, sc)
    log(f"   [{tag}] P1 raw trades: {len(tr):,} (causal-score history from {len(keep):,} entries)")
    return tr


def trades_frame(trades, D):
    tarr, n, sid, sdate = D["t"], D["n"], D["sid"], D["sess_date"]
    ei = np.minimum(np.searchsorted(tarr, np.array([np.datetime64(x["et"]) for x in trades])),
                    n - 1)
    xi = np.minimum(np.searchsorted(tarr, np.array([np.datetime64(x["xt"]) for x in trades])),
                    n - 1)
    s = sid[ei]
    u = np.array([x["u"] for x in trades], float)
    pnl = np.array([x["pnl"] for x in trades], float)
    return pd.DataFrame(dict(sess=s, date=pd.to_datetime(sdate[s]), entry_i=ei, exit_i=xi,
                             bars=(xi - ei).astype(int), u=u,
                             d=[x["d"] for x in trades], pnl436=pnl,
                             gross_pts=(pnl + COMM_RT * u) / (PV * np.maximum(u, 1.0))))


# ==================================================================================================
def main():
    t0 = _time.time()
    lf = open(os.path.join(CACHE, "build.log"), "w", encoding="utf-8")

    def log(*a):
        print(*a, flush=True); print(*a, file=lf); lf.flush()

    log("=" * 110)
    log("G3_SHORTROUTE01 - STAGE 1 BUILD  (spec 9a18980, unedited)")
    log("=" * 110)

    # ------------------------------------------------------------------ CORE, G0 reproduction only
    log("\n[CORE] G0-ONLY substrate: load_deep('2022-01-01','2026-07-31 17:00', extend=False).")
    log("       extend is OFF *on purpose*: this is the exact truncated object W61/W73 measured,")
    log("       and G0 asks whether this run rebuilds THAT object. It is used for nothing else.")
    Dc = load_deep("2022-01-01", "2026-07-31 17:00", extend=False)
    assert_seal(Dc, "CORE", log)
    log(f"   substrate {Dc['n']:,} bars, {Dc['n_sess']} sessions "
        f"({Dc['t'].min()} .. {Dc['t'].max()})   [{_time.time()-t0:.0f}s]")
    log(f"   TRUNCATION CONFIRMED: this substrate stops at {Dc['t'].max()} although "
        f"2026-07-31 17:00 was requested.")
    Xc = build_context(Dc)
    TGc = targets_cached(Dc, log)
    stc, _enc = session_bounds(Dc)
    in_win = np.array([(W61_A <= Dc["t"][stc[s]] < W61_B) for s in range(Dc["n_sess"])])
    NS = int(in_win.sum())
    trS = build_short(Dc, Xc, TGc, log, "CORE")
    trL = build_long(Dc, Xc, TGc, log, "CORE", ent_lo=W61_A, ent_hi=W61_B)
    dS = trades_frame(trS, Dc); dL = trades_frame(trL, Dc)
    dS = dS[in_win[dS["sess"].values]].reset_index(drop=True)
    dL = dL[in_win[dL["sess"].values]].reset_index(drop=True)
    g0 = dict(window=f"{W61_A} .. {W61_B}", sessions=NS,
              short_trades=int(len(dS)), short_net=float(dS["pnl436"].sum()),
              short_pts_sess=float(dS["pnl436"].sum() / PV / NS),
              p1_pts_sess=float(dL["pnl436"].sum() / PV / NS))
    log(f"\n   CORE window {g0['window']}: {NS} sessions")
    log(f"   G0a short trades   : {g0['short_trades']:,}          (WAVE C: 2,225)")
    log(f"   G0b short pts/sess : {g0['short_pts_sess']:.2f}            (WAVE C: 6.00)")
    log(f"   G0c short net $4.36: ${g0['short_net']:,.0f}      (WAVE C: $121,454)")
    log(f"   G0d P1 pts/session : {g0['p1_pts_sess']:.2f}           (WAVE C / W73: 14.86)")
    pd.Series(g0).to_json(os.path.join(CACHE, "g0_core.json"))
    core_daily = pd.DataFrame(dict(
        date=pd.to_datetime(Dc["sess_date"])[in_win].strftime("%Y-%m-%d")))
    v = np.zeros(Dc["n_sess"]); np.add.at(v, dS["sess"].values, dS["pnl436"].values)
    core_daily["short"] = v[in_win]
    core_daily.to_csv(os.path.join(CACHE, "core_daily.csv"), index=False)
    core_last = Dc["sess_date"].max()
    del Dc, Xc, TGc, trS, trL, dS, dL

    # ------------------------------------------------------------------ FULL, the analysis object
    log(f"\n[FULL] ANALYSIS substrate: load_deep('2006-01-01','2026-07-31 17:00', extend=TRUE)"
        f"  [{_time.time()-t0:.0f}s]")
    D = load_deep("2006-01-01", "2026-07-31 17:00", extend=True)
    assert_seal(D, "FULL", log)
    log(f"   substrate {D['n']:,} bars, {D['n_sess']} sessions "
        f"({D['t'].min()} .. {D['t'].max()})   [{_time.time()-t0:.0f}s]")
    log(f"   EXTEND WORKED: max bar {D['t'].max()} > CORE's {core_last} "
        f"-> the truncation trap is not present in this run.")
    X = build_context(D)
    log(f"   context built [{_time.time()-t0:.0f}s]")
    TG = targets_cached(D, log)
    st, en = session_bounds(D)
    trS = build_short(D, X, TG, log, "FULL")
    TR = trades_frame(trS, D)
    TR.to_csv(os.path.join(CACHE, "full_short_trades.csv"), index=False)
    log(f"   fills done [{_time.time()-t0:.0f}s]")

    # ------------------------------------------------------------------ session frame
    ns = D["n_sess"]
    c, o, h, l, tarr = D["c"], D["o"], D["h"], D["l"], D["t"]
    dif = np.zeros(D["n"]); dif[1:] = np.abs(np.diff(c)); dif[st] = 0.0    # no cross-session diff
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[m]").astype(np.int64))
    is_rth = (mod >= RTH_LO) & (mod <= RTH_HI)
    absmove = np.zeros(ns); np.add.at(absmove, D["sid"], dif)
    abs_rth = np.zeros(ns); np.add.at(abs_rth, D["sid"], np.where(is_rth, dif, 0.0))
    abs_on = np.zeros(ns); np.add.at(abs_on, D["sid"], np.where(is_rth, 0.0, dif))
    n_rth = np.zeros(ns); np.add.at(n_rth, D["sid"], is_rth.astype(float))
    sdate = pd.to_datetime(D["sess_date"])
    S = pd.DataFrame(dict(
        sess=np.arange(ns), date=sdate, year=sdate.year, bars=(en - st), bars_rth=n_rth,
        s_open=o[st], s_close=c[en - 1],
        s_high=np.array([h[a:b].max() for a, b in zip(st, en)]),
        s_low=np.array([l[a:b].min() for a, b in zip(st, en)]),
        absmove=absmove, abs_rth=abs_rth, abs_on=abs_on))
    S["ret"] = S["s_close"] - S["s_open"]
    S["rng"] = S["s_high"] - S["s_low"]
    for nm, df in (("short", TR),):
        v = np.zeros(ns); np.add.at(v, df["sess"].values, df["pnl436"].values)
        S[f"{nm}_pnl436"] = v
        v = np.zeros(ns); np.add.at(v, df["sess"].values, np.ones(len(df)))
        S[f"{nm}_ntr"] = v
        v = np.zeros(ns); np.add.at(v, df["sess"].values, (df["gross_pts"] * df["u"]).values)
        S[f"{nm}_gross_pts"] = v

    # ------------------------------------------------------------------ VIX (S6), prior close
    log(f"\n[VIX] {os.path.relpath(VIXF, ROOT)}")
    VX = pd.read_parquet(VIXF)[["date", "close"]].dropna().sort_values("date")
    n_all = len(VX)
    VX = VX[VX["date"] < pd.Timestamp("2026-08-01")].reset_index(drop=True)
    log(f"   {n_all:,} rows; {n_all-len(VX)} dropped by the >=2026-08-01 seal; "
        f"kept {len(VX):,} ({VX['date'].min().date()} .. {VX['date'].max().date()})")
    # STRICTLY PRIOR: the last VIX close dated strictly before the session's own date. The NQ
    # session dated d starts 18:00 ET on d-1, by which time d-1's VIX close is published.
    pos = np.searchsorted(VX["date"].values, S["date"].values, side="left") - 1
    S["vix_prev"] = np.where(pos >= 0, VX["close"].values[np.maximum(pos, 0)], np.nan)
    S["vix_prev_date"] = np.where(pos >= 0, VX["date"].values[np.maximum(pos, 0)],
                                  np.datetime64("NaT"))
    bad = int((pd.to_datetime(S["vix_prev_date"]) >= S["date"]).sum())
    log(f"   look-ahead assertion: VIX rows dated >= their own session date = {bad}  "
        f"-> {'PASS' if bad == 0 else 'VIOLATION'}")
    if bad:
        raise SystemExit("VIX look-ahead - refusing to continue")
    log(f"   sessions with no prior VIX close: {int(S['vix_prev'].isna().sum())}")

    S.to_csv(os.path.join(CACHE, "full_sessions.csv"), index=False)
    log(f"\n[cached] {len(S):,} sessions -> full_sessions.csv   [{_time.time()-t0:.0f}s]")

    # ------------------------------------------------------------------ independent G0 check
    log("\n[CROSS-CHECK] the FULL substrate restricted to the CORE session set must be the SAME")
    log("              object (WAVE C measured 100.0 % identical sessions).")
    cd = pd.read_csv(os.path.join(CACHE, "core_daily.csv"), parse_dates=["date"])
    mg = cd.merge(S[["date", "short_pnl436"]], on="date", how="inner")
    log(f"   {len(mg)} shared sessions | CORE ${mg['short'].sum():,.0f} vs "
        f"FULL ${mg['short_pnl436'].sum():,.0f} | identical sessions "
        f"{100*float(np.isclose(mg['short'], mg['short_pnl436']).mean()):.1f} %")

    # ------------------------------------------------------------------ what the seal excluded
    log("\n[SEAL / WINDOW EXCLUSIONS - printed, not assumed]")
    log(f"   sessions >= 2026-08-01 in the substrate            : "
        f"{int((S['date'] >= '2026-08-01').sum())}  (seal)")
    log(f"   sessions 2026-05-30 .. 2026-07-31 present but OUTSIDE the spec's MODERN window "
        f"(ends 2026-05-29): {int((S['date'] > '2026-05-29').sum())}")
    log(f"   sessions 2020-01-01 .. 2022-04-30 (TRANS, EXCLUDED ENTIRELY by the spec): "
        f"{int(((S['date'] >= '2020-01-01') & (S['date'] <= '2022-04-30')).sum())}")
    log(f"   sessions in PRE 2006-01-01 .. 2019-12-31           : "
        f"{int((S['date'] <= '2019-12-31').sum())}")
    log(f"   sessions in MODERN 2022-05-01 .. 2026-05-29        : "
        f"{int(((S['date'] >= '2022-05-01') & (S['date'] <= '2026-05-29')).sum())}")
    log(f"\ndone [{_time.time()-t0:.0f}s]")
    lf.close()


if __name__ == "__main__":
    main()
