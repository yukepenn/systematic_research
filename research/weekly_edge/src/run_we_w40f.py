"""WE_W40 amendment 5 (declared in amendment_3.yaml before this run).

Amendment 4 met the preregistered promotion condition, but on H2 rather than H1:
  the HIGH-volatility band is stress-net positive in BOTH modern halves
    2022-2024  +$13.4/trade, stress-net +$12,015
    2025-2026  +$96.9/trade, stress-net +$75,665
  while the LOW band is stress-net negative in both. Deep history says B's viability is an
  EPOCH: dead 2006-2019 (three 5-year blocks all stress-negative), alive 2019-2026.

So the object to test is not B, it is B GATED ON THE VOLATILITY REGIME. The gate must not
introduce a fitted constant: instead of amendment 4's 0.943 (the modern-window median), the
gate here compares the regime variable to its OWN TRAILING MEDIAN over the previous 250
sessions - causal, and derived rather than chosen, in the same spirit as W37's k = "a majority
of five" and the 23-bar cut.

Everything is measured on the FULL window (2022-07 -> 2026-08) and per year, per the standing
policy amendment 2 created.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, STRESS_RT                               # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import weekly                                            # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote, sfills                             # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w40 import OUT, A, B, axis_volexp                            # noqa: E402
from run_we_w40e import regime_rel                                       # noqa: E402
from we_quality import build_context                                     # noqa: E402

RNG = np.random.default_rng(2026405)


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    X = build_context(D)
    TG = targets(D)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def wk_of(ts):
        return wkmap[int(D["sid"][i_of(ts)])]
    out = open(os.path.join(OUT, "second_f.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    # ---- the long object -------------------------------------------------------------
    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    bl = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    scQ0, _ = causal_score(X, entL, window=WIN)
    LONG = fills_qexit(D, posL, np.where(scQ0 >= 3, 2, 1).astype(np.int8), scQ0)
    pts = np.array([x["pnl"] for x in LONG
                    if A <= np.datetime64(x["et"]) < B]).sum() / PV / len(
        np.unique(D["sid"][(tarr >= A) & (tarr < B)]))
    P_(f"=== B1: {pts:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(pts-14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(pts - 14.72) >= 0.6:
        out.close(); return

    # ---- the causal, constant-free regime gate ---------------------------------------
    rel = regime_rel(D)
    ns_ = D["n_sess"]
    rs = np.array([rel[D["sid"] == s][0] for s in range(ns_)])
    med = pd.Series(rs).rolling(250, min_periods=60).median().shift(1).values
    gate_s = np.nan_to_num(rs, nan=1.0) >= np.nan_to_num(med, nan=1e9)
    gate = gate_s[D["sid"]]
    P_(f"   regime gate open on {gate.mean()*100:.1f} % of bars "
       f"({gate_s.mean()*100:.1f} % of sessions); threshold is the TRAILING 250-session "
       f"median of the same variable, so no constant is fitted")

    posB = axis_volexp(D, X, 1.6, 1.0, 15)
    posBG = (posB * gate.astype(np.int8)).astype(np.int8)
    BT = sfills(D, posB, halt=1300.0, target=1000.0)
    BG = sfills(D, posBG, halt=1300.0, target=1000.0)

    keys = sorted(weekly(LONG, wk_of, A, B))

    def wvec(trl, k=1.0, a=A, b=B, kk=None):
        d = weekly(trl, wk_of, a, b)
        ks = kk if kk is not None else keys
        return np.array([d.get(x, 0.0) for x in ks]) * k

    def ntr(trl, k=1.0, a=A, b=B):
        return k * len([x for x in trl if a <= np.datetime64(x["et"]) < b])

    def expo(trl, a=A, b=B):
        return float(sum(x.get("u", 1)
                         * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                            / np.timedelta64(1, "m"))
                         for x in trl if a <= np.datetime64(x["et"]) < b))

    rows = []

    def show(nm, v, nt):
        if len(v) < 8:
            return None
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        cve = float(v.mean() / abs(cv)) if cv < 0 else 9.9
        st = float(v.mean() - STRESS_RT * nt / len(v))
        P_(f"{nm:<32}{v.mean():>9,.0f}{(v>0).mean()*100:>7.1f}{v.min():>10,.0f}"
           f"{cv:>10,.0f}{s:>8.3f}{eff:>8.3f}{cve:>8.3f}{st:>9,.0f}")
        r = dict(arm=nm, wk=round(float(v.mean())),
                 wkpos=round(float((v > 0).mean() * 100), 1), worst=round(float(v.min())),
                 cvar5=round(cv), sharpe=round(s, 3), eff=round(eff, 3),
                 cveff=round(cve, 3), stress=round(st))
        rows.append(r); return r
    hdr = (f"{'arm':<32}{'wk$':>9}{'wk+%':>7}{'worst':>10}{'CVaR5':>10}{'shrp':>8}"
           f"{'eff':>8}{'cvEff':>8}{'stress':>9}")

    P_(f"\n=== STANDALONE, FULL WINDOW 2022-07 -> 2026-08 [{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    rL = show("LONG x1", wvec(LONG), ntr(LONG))
    show("B ungated", wvec(BT), ntr(BT))
    rBG = show("B REGIME-GATED", wvec(BG), ntr(BG))
    vL, vG = wvec(LONG), wvec(BG)
    dd = np.argsort(vL)[:max(3, len(vL) // 10)]
    P_(f"   B-gated vs long: corr {np.corrcoef(vG, vL)[0,1]:+.3f} | "
       f"corr inside the long object's worst-decile weeks "
       f"{np.corrcoef(vG[dd], vL[dd])[0,1]:+.3f} | "
       f"bar overlap {100*(posBG[posL != 0] != 0).mean():.1f} %")

    P_(f"\n=== PER YEAR, B-gated alone (the test amendment 2 applied to the ungated version) ===")
    P_(hdr)
    for y in (2022, 2023, 2024, 2025, 2026):
        a = max(A, np.datetime64(f"{y}-01-01")); b = min(B, np.datetime64(f"{y+1}-01-01"))
        if a >= b:
            continue
        kk = sorted(weekly(BG, wk_of, a, b))
        if len(kk) < 8:
            continue
        show(f"{y} B-gated", wvec(BG, 1.0, a, b, kk), ntr(BG, 1.0, a, b))

    # ---- weight scan on the FULL window ----------------------------------------------
    eL, eB = expo(LONG), expo(BG)
    P_(f"\n=== WEIGHT SCAN at constant total exposure, FULL WINDOW "
       f"(long {eL:,.0f} contract-min, B-gated {eB:,.0f}) [{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    ref = None
    for w in (0.0, 0.05, 0.10, 0.15, 0.20, 0.30):
        kL = 1 - w
        kB = (w * eL / eB) if eB > 0 else 0.0
        r = show(f"w={w:.2f} (long x{kL:.2f} + B x{kB:.2f})",
                 wvec(LONG, kL) + wvec(BG, kB), ntr(LONG, kL) + ntr(BG, kB))
        if r:
            r["w"] = w
            if w == 0.0:
                ref = r
    imp = [r for r in rows if r.get("w", 0) > 0
           and (r["eff"] > ref["eff"] or r["cveff"] > ref["cveff"])]
    P_(f"\n   weights improving eff OR CVaR-eff over w=0 ON THE FULL WINDOW: "
       f"{[r['w'] for r in imp] if imp else 'NONE -> B stays parked'}")
    P_("\n   tradeable integer ratios vs exposure-matched long alone:")
    P_(hdr)
    for a_, b_ in ((8, 1), (6, 1), (4, 1)):
        show(f"{a_} long : {b_} B-gated", wvec(LONG, a_) + wvec(BG, b_),
             ntr(LONG, a_) + ntr(BG, b_))
        k = (a_ * eL + b_ * eB) / eL
        show(f"long alone x{k:.2f} (match {a_}:{b_})", wvec(LONG, k), ntr(LONG, k))

    # ---- nulls on the gated mask ------------------------------------------------------
    if imp:
        P_(f"\n=== NULLS on the B-gated entry mask, full window [{_time.time()-t0:.0f}s] ===")
        base_eff = rBG["eff"]
        ent_b = np.where((posBG != 0) & (np.concatenate([[0], posBG[:-1]]) == 0))[0]
        for tag in ("N1 circular shift", "N2 count-matched random entries"):
            nl = []
            for j in range(100):
                if tag.startswith("N1"):
                    pn = np.roll(posBG, int(RNG.integers(20_000, n - 20_000)))
                else:
                    pn = np.zeros(n, np.int8)
                    pick = RNG.choice(n - 40, size=len(ent_b), replace=False)
                    for k_, s_ in zip(pick, RNG.choice([-1, 1], size=len(pick))):
                        pn[k_:k_ + 30] = s_
                v = wvec(sfills(D, pn, halt=1300.0, target=1000.0))
                nl.append(v.mean() / abs(v.min()) if v.min() < 0 else 9.9)
                if (j + 1) % 50 == 0:
                    print(f"   {tag} {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
            nu = np.array(nl)
            pct = 100.0 * (nu < base_eff).mean()
            P_(f"   {tag:<32} real {base_eff:.3f} | null mean {nu.mean():.3f} | "
               f"p95 {np.percentile(nu,95):.3f} | pctile {pct:.1f} | "
               f"p {(nu>=base_eff).mean():.3f} -> "
               f"{'EVIDENCE' if pct>=95 else ('weak' if pct>=80 else 'NOT EVIDENCE')}")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary_f.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
