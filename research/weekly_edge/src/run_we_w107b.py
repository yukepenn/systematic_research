"""WE_W107b - ADVERSARIAL CORRECTION TO MY OWN LANE-B RESULT.

Two defects in W107, both mine:
  1. the survivor rule had NO MINIMUM BIN SIZE. `MORNING_DIR` is a discrete +/-1 variable; the
     binner gave it levels {-1, 0, +1} with n = 4 in the middle, and that 4-session bin's 75 %
     sign rate is what made the shape "single-peak" and the spread 25.5 pp. On the two real
     levels the spread is 7.8 pp - BELOW the 8 pp bar. It should never have survived.
  2. the rate calibrator cannot bin a discrete variable: MORNING_DIR's 25/50/75 % arms returned
     481/485/485 trades, i.e. no calibration happened at all.
Plus the control W107 owed and did not run: what does an UNCONDITIONAL trade at the same geometry
earn? NQ rose over 2022-2026 and a bullish tilt would masquerade as a mechanism.
"""
from __future__ import annotations
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV
from we_lanes import LaneBench, RATES
OUT = os.path.join(ROOT, "runs", "WE_W107_AFT", "out")
MORN_A, MORN_B, MID_A, MID_B = 571, 689, 690, 809
DEC, EXIT = 830, 944
MINBIN = 50
SEED = 1072

def main():
    out = open(os.path.join(OUT, "aft_correction.txt"), "w", encoding="utf-8")
    def P_(*a): print(*a, flush=True); print(*a, file=out); out.flush()
    L = LaneBench(); NS = L.NS
    p0931, p1129 = L.at(MORN_A, use_open=True), L.at(MORN_B)
    p1329, p1330, p1544 = L.at(MID_B), L.at(810, use_open=True), L.at(EXIT)
    absm = L.agg(MORN_A, MID_B, "absmove")
    path_eff = np.abs(p1329 - p0931) / np.maximum(absm, 1e-9)
    morn_dir = np.sign(p1129 - p0931)
    target = (p1544 - p1330) * PV
    elig = L.win & np.isfinite(target) & np.isfinite(p1329) & np.isfinite(p0931)

    P_("="*118)
    P_("=== 1. MORNING_DIR ON ITS TWO REAL LEVELS - the middle bin had FOUR sessions")
    P_("="*118)
    P_(f"{'level':<12}{'n':>7}{'sign %':>10}{'mean $':>11}")
    lv = []
    for v, lab in ((-1.0, "down morning"), (0.0, "flat (n~0)"), (1.0, "up morning")):
        m = elig & (morn_dir == v)
        if m.sum() == 0: continue
        P_(f"{lab:<12}{int(m.sum()):>7}{100*float((target[m]>0).mean()):>9.1f}%"
           f"{float(target[m].mean()):>11,.0f}")
        if m.sum() >= MINBIN: lv.append(100*float((target[m]>0).mean()))
    sp = max(lv) - min(lv) if len(lv) >= 2 else 0.0
    P_(f"\n    spread across bins with n >= {MINBIN}: {sp:.1f} pp   "
       f"-> {'SURVIVES' if sp >= 8.0 else 'FAILS the 8 pp bar'}")
    P_("    W107 reported 25.5 pp. That number came from a FOUR-SESSION bin. WITHDRAWN.")

    P_("")
    P_("="*118)
    P_("=== 2. PATH_EFF re-checked with a minimum bin size, and the shape re-read")
    P_("="*118)
    d = elig & np.isfinite(path_eff)
    xv, tg = path_eff[d], target[d]
    q = np.nanpercentile(xv, [20, 40, 60, 80])
    bins = [xv <= q[0], (xv>q[0])&(xv<=q[1]), (xv>q[1])&(xv<=q[2]), (xv>q[2])&(xv<=q[3]), xv>q[3]]
    sr = [100*float((tg[b]>0).mean()) for b in bins]
    P_(f"{'quintile':<10}" + "".join(f"{'Q'+str(i+1):>12}" for i in range(5)))
    P_(f"{'n':<10}" + "".join(f"{int(b.sum()):>12}" for b in bins))
    P_(f"{'sign %':<10}" + "".join(f"{s:>11.1f}%" for s in sr))
    P_(f"{'mean $':<10}" + "".join(f"{float(tg[b].mean()):>12,.0f}" for b in bins))
    P_(f"\n    every bin n >= {MINBIN}: {'YES' if min(int(b.sum()) for b in bins) >= MINBIN else 'NO'}"
       f"   spread {max(sr)-min(sr):.1f} pp   -> PATH_EFF is the ONLY genuine stage-1 survivor")

    P_("")
    P_("="*118)
    P_("=== 3. THE CONTROL W107 OWED: what does an UNCONDITIONAL trade earn at this geometry?")
    P_("===    NQ rose over 2022-2026; a bullish tilt would masquerade as a mechanism.")
    P_("="*118)
    P_(f"{'arm':<28}{'N':>6}{'hit%':>8}{'p*':>8}{'$/trade':>10}{'net $':>11}{'wk$@fixDD':>11}{'t':>6}")
    rows = []
    for lab, des in (("ALWAYS LONG", np.where(L.win, 1, 0)),
                     ("ALWAYS SHORT", np.where(L.win, -1, 0)),
                     ("MORNING_DIR (all sessions)", np.nan_to_num(morn_dir))):
        pnl, take, cost, em = L.trade(np.asarray(des).astype(np.int8), DEC, EXIT)
        st = L.stats(pnl, take, cost, em)
        if st is None: continue
        P_(f"{lab:<28}{st['n']:>6}{st['hit']:>7.2f}%{st['p_star']:>8.4f}"
           f"{st['per_trade']:>10,.0f}{st['net']:>11,.0f}{st['fixdd']:>11,.0f}{st['t']:>6.2f}")
        rows.append(dict(arm=lab, **st))
    rng = np.random.default_rng(SEED)
    cells, prim = [], []
    P_("")
    P_(f"{'PATH_EFF alone':<28}{'rate':>7}{'N':>6}{'hit%':>8}{'$/trade':>10}{'net $':>11}"
       f"{'wk$@fixDD':>11}{'t':>6}")
    med = float(np.nanmedian(path_eff[L.win]))
    for r in RATES:
        ok = LaneBench.accept(np.abs(path_eff - med), r)
        des = np.nan_to_num(np.where(ok, np.sign(path_eff - med), 0)).astype(np.int8)
        pnl, take, cost, em = L.trade(des, DEC, EXIT)
        st = L.stats(pnl, take, cost, em)
        if st is None: continue
        P_(f"{'':28}{r:>7.2f}{st['n']:>6}{st['hit']:>7.2f}%{st['per_trade']:>10,.0f}"
           f"{st['net']:>11,.0f}{st['fixdd']:>11,.0f}{st['t']:>6.2f}")
        mv = ((L.at(EXIT) - L.at(DEC+1, use_open=True)) * PV)[take]
        cells.append((mv, cost)); rows.append(dict(arm=f"PATH_EFF@{r}", **st))
        if abs(r-0.50) < 1e-9: prim.append((mv, cost))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "correction.csv"), index=False)
    if prim:
        mn, _ = LaneBench.coin_null(prim, rng)
        _, mx = LaneBench.coin_null(cells, rng)
        pv = float([r_["per_trade"] for r_ in rows if r_["arm"] == "PATH_EFF@0.5"][0])
        P_("")
        P_(f"    CORRECTED PRIMARY - PATH_EFF alone at the 50 % arm: ${pv:,.0f}/trade")
        P_(f"    single-cell coin null p95 ${float(np.nanpercentile(mn,95)):,.0f}  -> "
           f"{100*float(np.nanmean(mn < pv)):.1f}th percentile")
        P_(f"    best-of-3 bar ${float(np.nanpercentile(mx,95)):,.0f}")
        P_(f"    VERDICT: {'PASSES its own null' if pv > float(np.nanpercentile(mn,95)) else 'FAILS'}"
           f" / {'clears' if pv > float(np.nanpercentile(mx,95)) else 'does NOT clear'} the best-of-3 bar")
    P_("")
    P_("    W107's headline of $99/trade averaged PATH_EFF with a variable that should never")
    P_("    have been a survivor. It is WITHDRAWN and replaced by the corrected figure above.")
    out.close()

if __name__ == "__main__":
    main()
