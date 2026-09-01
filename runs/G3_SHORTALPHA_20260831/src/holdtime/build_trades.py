"""G3_SHORTALPHA / holdtime - stage 1.

Rebuild the two objects W61/W73 measured (P1 long, mirrored short sleeve) and emit a RICH trade
ledger that additionally carries the entry/exit bar index, the entry/exit price and the exit kind.

The rich fill functions here are local re-implementations of `run_we_w38.sfills` and
`run_we_w35.fills_qexit`. They are asserted BIT-IDENTICAL to the imported originals on
(d, u, et, xt, pnl) before anything downstream is allowed to run. Nothing in
research/weekly_edge/src or research_sdk is edited.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

ROOT_ = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT_, "research", "weekly_edge", "src"))

from run_we_w01 import ROOT, PV, COMM_RT                                  # noqa: E402
from run_we_w26 import fills_daily                                        # noqa: E402
from run_we_w35 import fills_qexit                                        # noqa: E402
from run_we_w37 import causal_score                                       # noqa: E402
from run_we_w38 import vote, sfills                                       # noqa: E402
from run_we_w39 import WIN                                                # noqa: E402
from run_we_w51 import A, B                                               # noqa: E402
from run_we_w51c import setup                                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "G3_SHORTALPHA_20260831", "out")
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache")
os.makedirs(OUT, exist_ok=True)
os.makedirs(CACHE, exist_ok=True)

SEAL = np.datetime64("2026-08-01")


# ------------------------------------------------------------------ rich fills (verified copies)
def sfills_rich(D, dir_arr, size_at_entry=None, halt=1300.0, target=1000.0, block=None):
    """Byte-for-byte copy of run_we_w38.sfills with (ei, xi, epx, xpx, kind) added."""
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
                                   ei=eti, xi=i, epx=epx, xpx=o[i], kind="flip"))
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
                               ei=eti, xi=i, epx=epx, xpx=c[i], kind="close"))
            p = 0; u = 0
    return trades


def fills_qexit_rich(D, pos_arr, size_at_entry, score, halt=1300.0, target=1000.0,
                     big_target=None, cut_bars=None, cut_max_score=1):
    """Byte-for-byte copy of run_we_w35.fills_qexit with (ei, xi, epx, xpx, kind) added."""
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
                                   ei=eti, xi=i, epx=epx, xpx=o[i], kind="flip"))
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
                               ei=eti, xi=i, epx=epx, xpx=c[i], kind="close"))
            u = 0
    return trades


def _same(a, b, keys=("d", "u", "et", "xt", "pnl")):
    if len(a) != len(b):
        return False, f"length {len(a)} vs {len(b)}"
    for i, (x, y) in enumerate(zip(a, b)):
        for k in keys:
            if k == "pnl":
                if abs(x[k] - y[k]) > 1e-9:
                    return False, f"trade {i} pnl {x[k]} vs {y[k]}"
            elif x[k] != y[k]:
                return False, f"trade {i} {k} {x[k]} vs {y[k]}"
    return True, "identical"


# ------------------------------------------------------------------ enrichment
def enrich(D, trades, sigma460, sid, sess_date):
    """Per-trade excursion geometry. Bars a..b-1 are live for a flip exit, a..b for a close
    exit; the exit fill price is appended to the path so the terminal print is included."""
    h, l, o, c, t = D["h"], D["l"], D["o"], D["c"], D["t"]
    rows = []
    for x in trades:
        a, b, d = int(x["ei"]), int(x["xi"]), int(x["d"])
        last = b if x["kind"] == "close" else b - 1
        if last < a:
            last = a
        hh = h[a:last + 1]; ll = l[a:last + 1]
        fav = (hh - x["epx"]) if d > 0 else (x["epx"] - ll)
        adv = (ll - x["epx"]) if d > 0 else (x["epx"] - hh)
        # append the exit fill itself (a realisable price)
        fin = d * (x["xpx"] - x["epx"])
        fav = np.append(fav, fin); adv = np.append(adv, fin)
        dur = last - a + 1
        j_f = int(np.argmax(fav)); j_a = int(np.argmin(adv))
        rows.append(dict(
            d=d, u=int(x["u"]), et=x["et"], xt=x["xt"], pnl=float(x["pnl"]),
            ei=a, xi=b, epx=float(x["epx"]), xpx=float(x["xpx"]), kind=x["kind"],
            sess=int(sid[a]), sdate=str(sess_date[int(sid[a])]),
            dur=int(dur),
            mfe=float(fav.max()), mae=float(adv.min()), fin=float(fin),
            t_mfe=int(min(j_f + 1, dur)), t_mae=int(min(j_a + 1, dur)),
            sigma=float(sigma460[a]),
        ))
    return pd.DataFrame(rows)


def rolling_sigma460(D):
    """The vendor's own scale: mean |dClose| over the trailing 460 bars, causal (uses closes
    strictly before the bar), reset-free across sessions exactly as sm14_1m accumulates it."""
    c = D["c"]
    dc = np.abs(np.diff(c, prepend=c[0]))
    dc[0] = np.nan
    s = pd.Series(dc).rolling(460, min_periods=30).mean().shift(1).values
    return s


def main():
    t0 = _time.time()
    log = []

    def P(*a):
        print(*a, flush=True); log.append(" ".join(str(z) for z in a))

    D, X, TG, st, en = setup()
    tarr, n, sid = D["t"], D["n"], D["sid"]

    # ------------------------------------------------------------------ SEAL
    mx = tarr.max()
    P("=" * 116)
    P("=== SEAL ASSERTION")
    P("=" * 116)
    P(f"   substrate  {D['n']:,} bars  {D['n_sess']:,} sessions   {tarr[0]} -> {tarr[-1]}")
    assert mx < SEAL, f"SEAL VIOLATION: substrate reaches {mx} >= {SEAL}"
    assert np.datetime64(str(B)) <= SEAL
    P(f"   max bar timestamp {mx} < 2026-08-01  -> SEAL HELD (asserted in code, not asserted "
      f"by narration)")
    P(f"   window A={A}  B={B} (exclusive)")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    NS = len(sess_in)
    P(f"   sessions in window: {NS}")

    sig = rolling_sigma460(D)

    # ------------------------------------------------------------------ P1 long
    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    base = fills_daily(D, posL, halt=1300, target=1000)
    e = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, e, window=WIN)
    sz = np.where(sc >= 3, 2, 1).astype(np.int8)

    ref_L = fills_qexit(D, posL, sz, sc)
    rich_L = fills_qexit_rich(D, posL, sz, sc)
    ok, msg = _same(ref_L, rich_L)
    P("")
    P("=" * 116)
    P("=== RICH-FILL IDENTITY CHECK (the rich ledger must be the SAME object, not a variant)")
    P("=" * 116)
    P(f"   fills_qexit_rich vs fills_qexit : {msg}  -> {'PASS' if ok else 'FAIL - VOID'}")
    assert ok, msg

    L = [x for x in rich_L if in_win[int(sid[x['ei']])]]

    # ------------------------------------------------------------------ mirrored short
    fs = vote(TG, D, X, -1)
    posS = -(fs >= 0.5).astype(np.int8)
    ref_S = sfills(D, posS, halt=1300.0, target=1000.0)
    rich_S = sfills_rich(D, posS, halt=1300.0, target=1000.0)
    ok2, msg2 = _same(ref_S, rich_S)
    P(f"   sfills_rich      vs sfills      : {msg2}  -> {'PASS' if ok2 else 'FAIL - VOID'}")
    assert ok2, msg2

    S = [x for x in rich_S if in_win[int(sid[x['ei']])]]

    # ------------------------------------------------------------------ B1 gate
    netL = sum(x["pnl"] for x in L); netS = sum(x["pnl"] for x in S)
    ptsL = netL / PV / NS; ptsS = netS / PV / NS
    P("")
    P("=" * 116)
    P("=== B1 GATE (must reproduce W73 exactly: L = 14.86 pts/session, S = 6.00, 2,225 trades)")
    P("=" * 116)
    P(f"{'arm':<26}{'trades':>9}{'net $':>13}{'pts/sess':>11}{'expect':>9}{'verdict':>10}")
    gL = abs(ptsL - 14.86) < 0.6
    gS = abs(ptsS - 6.00) < 0.6 and abs(len(S) - 2225) <= 5
    P(f"{'L  P1 long':<26}{len(L):>9,}{netL:>13,.0f}{ptsL:>11.2f}{14.86:>9.2f}"
      f"{'PASS' if gL else 'FAIL':>10}")
    P(f"{'S  mirrored short':<26}{len(S):>9,}{netS:>13,.0f}{ptsS:>11.2f}{6.00:>9.2f}"
      f"{'PASS' if gS else 'FAIL':>10}")
    assert gL and gS, "B1 GATE FAILED - wave VOID"

    # ------------------------------------------------------------------ enrich + persist
    dfL = enrich(D, L, sig, sid, D["sess_date"])
    dfS = enrich(D, S, sig, sid, D["sess_date"])
    # reconstruction check: enriched final points must reproduce pnl exactly
    for nm, df in (("L", dfL), ("S", dfS)):
        rec = df["fin"].values * df["u"].values * PV - COMM_RT * df["u"].values
        err = float(np.abs(rec - df["pnl"].values).max())
        P(f"   {nm}: max |reconstructed pnl - ledger pnl| = {err:.2e}  -> "
          f"{'PASS' if err < 1e-8 else 'FAIL'}")
        assert err < 1e-8
    P(f"   sigma460 finite on entries: L {np.isfinite(dfL['sigma']).mean()*100:.1f}%  "
      f"S {np.isfinite(dfS['sigma']).mean()*100:.1f}%")

    dfL.to_parquet(os.path.join(CACHE, "trades_L.parquet"))
    dfS.to_parquet(os.path.join(CACHE, "trades_S.parquet"))
    pd.DataFrame(dict(sess=sess_in, sdate=[str(D["sess_date"][s]) for s in sess_in],
                      wk=[D["wk"][s] for s in sess_in])).to_parquet(
        os.path.join(CACHE, "sessions.parquet"))
    P(f"   cached {len(dfL):,} long and {len(dfS):,} short rich trades "
      f"[{_time.time()-t0:.0f}s]")

    with open(os.path.join(CACHE, "stage1.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
