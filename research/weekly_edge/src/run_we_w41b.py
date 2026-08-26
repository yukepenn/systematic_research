"""WE_W41 amendment 1 (declared in amendment_1.yaml before this run).

Read 1 overturned W32 on the true engine and produced the campaign's most promising
diversification result: four alternative clocks whose weekly P&L correlates only 0.32-0.48
with the long quality object and 0.02-0.33 INSIDE its worst-decile weeks, all four clearing
BOTH nulls at the 100th percentile, and each giving a four-way improvement at w = 0.05.

W40's axis B cleared five preregistered conditions and was then withdrawn on the per-year
read. That is now standing policy, so this run applies it BEFORE anything is adopted, and
additionally asks the question read 1 did not: does a BASKET of clocks beat any single one?
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
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w41 import OUT, A, B, clock_vote                             # noqa: E402
from we_quality import build_context                                     # noqa: E402
from we_clocks import clock_time, clock_volume, clock_range, size_for_rate  # noqa: E402

RNG = np.random.default_rng(2026411)


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
    out = open(os.path.join(OUT, "clock2_b.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    bl = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    scQ0, _ = causal_score(X, entL, window=WIN)
    LONG = fills_qexit(D, posL, np.where(scQ0 >= 3, 2, 1).astype(np.int8), scQ0)
    NS = len(np.unique(D["sid"][(tarr >= A) & (tarr < B)]))
    pts = np.array([x["pnl"] for x in LONG
                    if A <= np.datetime64(x["et"]) < B]).sum() / PV / NS
    P_(f"=== B1: {pts:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(pts-14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(pts - 14.72) >= 0.6:
        out.close(); return

    V3, R3 = size_for_rate(D, 460)
    specs = [("3-min", lambda: clock_time(D, 3), max(20, 460 // 3)),
             ("5-min", lambda: clock_time(D, 5), max(20, 460 // 5)),
             ("volume", lambda: clock_volume(D, V3), max(20, 460 // 3)),
             ("range", lambda: clock_range(D, R3), max(20, 460 // 3))]
    SL = {}
    for nm, fn, sb in specs:
        f = os.path.join(OUT, f"pos_{nm}.npy")
        if os.path.exists(f):
            pos = np.load(f)
        else:
            Dc, ec = fn()
            pos = (clock_vote(D, Dc, ec, X, sb) >= 0.5).astype(np.int8)
            np.save(f, pos)
        SL[nm] = (pos, fills_daily(D, pos, halt=1300, target=1000))
        print(f"   {nm} ready [{_time.time()-t0:.0f}s]", flush=True)

    keys = sorted(weekly(LONG, wk_of, A, B))

    def wv(trl, k=1.0, a=A, b=B, kk=None):
        d = weekly(trl, wk_of, a, b)
        return np.array([d.get(x, 0.0) for x in (kk if kk is not None else keys)]) * k

    def ntr(trl, k=1.0, a=A, b=B):
        return k * len([x for x in trl if a <= np.datetime64(x["et"]) < b])
    rows = []
    hdr = (f"{'arm':<34}{'wks':>5}{'wk$':>9}{'wk+%':>7}{'worst':>10}{'CVaR5':>10}"
           f"{'shrp':>8}{'eff':>8}{'cvEff':>8}{'stress':>9}")

    def show(nm, v, nt):
        if len(v) < 8:
            return None
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        cve = float(v.mean() / abs(cv)) if cv < 0 else 9.9
        st = float(v.mean() - STRESS_RT * nt / len(v))
        P_(f"{nm:<34}{len(v):>5}{v.mean():>9,.0f}{(v>0).mean()*100:>7.1f}{v.min():>10,.0f}"
           f"{cv:>10,.0f}{s:>8.3f}{eff:>8.3f}{cve:>8.3f}{st:>9,.0f}")
        r = dict(arm=nm, weeks=len(v), wk=round(float(v.mean())),
                 wkpos=round(float((v > 0).mean() * 100), 1), worst=round(float(v.min())),
                 cvar5=round(cv), sharpe=round(s, 3), eff=round(eff, 3),
                 cveff=round(cve, 3), stress=round(st))
        rows.append(r); return r

    # ---------------- correlation matrix ------------------------------------------------
    P_(f"\n=== WEEKLY P&L CORRELATION MATRIX (the clocks are the SAME RULE on different "
       f"samplings, so this is SAMPLING diversification, not model diversification) ===")
    names = ["LONG"] + [s[0] for s in specs]
    mats = [wv(LONG)] + [wv(SL[s[0]][1]) for s in specs]
    P_("        " + "".join(f"{x:>9}" for x in names))
    for i, a_ in enumerate(names):
        P_(f"{a_:<8}" + "".join(f"{np.corrcoef(mats[i], mats[j])[0,1]:>9.2f}"
                                for j in range(len(names))))
    vL = mats[0]
    dd = np.argsort(vL)[:max(3, len(vL) // 10)]
    P_("   inside the LONG object's worst-decile weeks:")
    P_(f"{'':<8}" + "".join(f"{x:>9}" for x in names))
    P_(f"{'LONG':<8}" + "".join(f"{np.corrcoef(mats[0][dd], mats[j][dd])[0,1]:>9.2f}"
                                for j in range(len(names))))

    # ---------------- per-year, the test that withdrew W40's axis B ---------------------
    P_(f"\n=== PER YEAR, each clock sleeve alone (standing policy since W40 am.2) "
       f"[{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    for nm, _, _ in specs:
        for y in (2022, 2023, 2024, 2025, 2026):
            a = max(A, np.datetime64(f"{y}-01-01")); b = min(B, np.datetime64(f"{y+1}-01-01"))
            if a >= b:
                continue
            kk = sorted(weekly(SL[nm][1], wk_of, a, b))
            show(f"{nm} {y}", wv(SL[nm][1], 1.0, a, b, kk), ntr(SL[nm][1], 1.0, a, b))
        P_("")

    # ---------------- baskets ------------------------------------------------------------
    def expo(trl, k=1.0, a=A, b=B):
        return k * float(sum(x.get("u", 1)
                             * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                                / np.timedelta64(1, "m"))
                             for x in trl if a <= np.datetime64(x["et"]) < b))
    eL = expo(LONG)
    P_(f"\n=== BASKETS at constant total exposure, FULL WINDOW [{_time.time()-t0:.0f}s] ===")
    P_(hdr)
    ref = show("w=0 long quality alone", wv(LONG), ntr(LONG))
    combos = [("3-min", ), ("range", ), ("volume", ),
              ("3-min", "range"), ("3-min", "volume", "range"),
              ("3-min", "5-min", "volume", "range")]
    best = None
    for w in (0.03, 0.05, 0.08):
        for cb in combos:
            kL = 1 - w * len(cb)
            if kL <= 0:
                continue
            v = wv(LONG, kL); nt = ntr(LONG, kL)
            for c in cb:
                kB = w * eL / max(expo(SL[c][1]), 1e-9)
                v = v + wv(SL[c][1], kB); nt += ntr(SL[c][1], kB)
            r = show(f"w={w:.2f} each: long + {'+'.join(cb)}", v, nt)
            if r and r["eff"] > ref["eff"] and r["cveff"] > ref["cveff"]:
                r["combo"] = cb; r["w"] = w
                if best is None or r["eff"] > best["eff"]:
                    best = r
    P_(f"\n   best basket improving BOTH eff and CVaR-eff: "
       f"{best['arm'] if best else 'NONE'}")

    # ---------------- per-year for the best basket ---------------------------------------
    if best:
        P_(f"\n=== PER YEAR: best basket vs long alone at the same exposure ===")
        P_(hdr)
        w, cb = best["w"], best["combo"]
        kL = 1 - w * len(cb)
        ks = {c: w * eL / max(expo(SL[c][1]), 1e-9) for c in cb}
        tot = kL + sum(ks.values()) * 0 + 1e-12
        scale_alone = 1.0
        for y in (2022, 2023, 2024, 2025, 2026):
            a = max(A, np.datetime64(f"{y}-01-01")); b = min(B, np.datetime64(f"{y+1}-01-01"))
            if a >= b:
                continue
            kk = sorted(weekly(LONG, wk_of, a, b))
            v = wv(LONG, kL, a, b, kk); nt = ntr(LONG, kL, a, b)
            for c in cb:
                v = v + wv(SL[c][1], ks[c], a, b, kk); nt += ntr(SL[c][1], ks[c], a, b)
            show(f"{y} basket", v, nt)
            show(f"{y} long alone", wv(LONG, scale_alone, a, b, kk),
                 ntr(LONG, scale_alone, a, b))
            P_("")
        # binding null: replace each clock sleeve with a count-matched random sleeve
        P_(f"=== BINDING NULL on the basket [{_time.time()-t0:.0f}s] ===")
        nl = []
        for j in range(100):
            v = wv(LONG, kL); nt = ntr(LONG, kL)
            for c in cb:
                pos = SL[c][0]
                ent = np.where((pos != 0) & (np.concatenate([[0], pos[:-1]]) == 0))[0]
                pn = np.zeros(n, np.int8)
                pick = RNG.choice(n - 60, size=len(ent), replace=False)
                hold = int(np.median(np.diff(np.append(ent, n))[:len(ent)])) if len(ent) else 30
                hold = int(np.clip(hold, 5, 120))
                for k_ in pick:
                    pn[k_:k_ + hold] = 1
                tn = fills_daily(D, pn, halt=1300, target=1000)
                kB = ks[c]
                v = v + wv(tn, kB); nt += ntr(tn, kB)
            nl.append(v.mean() / abs(v.min()) if v.min() < 0 else 9.9)
            if (j + 1) % 25 == 0:
                print(f"   null {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
        nu = np.array(nl)
        pct = 100.0 * (nu < best["eff"]).mean()
        P_(f"   count-matched random sleeves: real {best['eff']:.3f} | null mean "
           f"{nu.mean():.3f} | p95 {np.percentile(nu,95):.3f} | pctile {pct:.1f} | "
           f"p {(nu>=best['eff']).mean():.3f} -> "
           f"{'EVIDENCE' if pct>=95 else ('weak' if pct>=80 else 'NOT EVIDENCE')}")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary_b.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
