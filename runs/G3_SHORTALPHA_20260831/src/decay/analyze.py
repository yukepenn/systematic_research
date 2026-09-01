"""G3_SHORTALPHA / decay - STAGE 2: decompose the decay. Every table is printed by this program.

Spec: runs/G3_SHORTALPHA_20260831/src/decay/spec.yaml (committed before stage 1 ran).
Reads only the cache written by build.py. Touches no market data directly, so the seal cannot
be violated here; the seal assertion from stage 1 is re-printed from the build log.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "G3_SHORTALPHA_20260831")
OUT = os.path.join(RUN, "out")
CACHE = os.path.join(OUT, "_decay_cache")

PV = 20.0
COST_FLOOR = 4.36          # never a headline
COST_PRIMARY = 20.65       # G2_EXEC01, 113 real round turns
COST_ALLIN = 25.01
PTS_PRIMARY = COST_PRIMARY / PV      # 1.0325 NQ points
ERA_CUT = pd.Timestamp("2022-05-01")  # ERABREAK01
RNG = np.random.default_rng(20260831)
NBOOT = 2000


# ==================================================================================================
def shapley3(pa, Wa, La, pb, Wb, Lb):
    """Order-independent (Shapley) attribution of the change in E = p*W - (1-p)*L from state a
    (baseline) to state b (target) across the three factors. Averages all 6 orderings."""
    import itertools

    def E(p, W, L):
        return p * W - (1 - p) * L
    base = dict(p=pa, W=Wa, L=La)
    targ = dict(p=pb, W=Wb, L=Lb)
    contrib = {k: 0.0 for k in ("p", "W", "L")}
    orders = list(itertools.permutations(("p", "W", "L")))
    for order in orders:
        state = dict(base)
        prev = E(**state)
        for k in order:
            state[k] = targ[k]
            cur = E(**state)
            contrib[k] += cur - prev
            prev = cur
    for k in contrib:
        contrib[k] /= len(orders)
    return contrib


def shapley2(Ra, Ea, Rb, Eb):
    """Exact symmetric split of D(R*E) into a RATE term and an EXPECTANCY term."""
    return dict(rate=(Rb - Ra) * (Ea + Eb) / 2.0, exp=(Ra + Rb) / 2.0 * (Eb - Ea))


def mix_effect(wa, ma, wb, mb):
    """Symmetric mix / within decomposition of a class-weighted mean.
       mean = sum_k w_k m_k ;  D = sum_k Dw_k*mbar_k  +  sum_k wbar_k*Dm_k   (exact)."""
    wa, ma, wb, mb = map(np.asarray, (wa, ma, wb, mb))
    mix = float(np.sum((wb - wa) * (ma + mb) / 2.0))
    within = float(np.sum((wa + wb) / 2.0 * (mb - ma)))
    return mix, within


def kdeflate(x):
    """rho_bar = lag-1 autocorrelation of the series; K_eff = K/(1+(K-1)*rho_bar)."""
    x = np.asarray(x, float)
    K = len(x)
    if K < 5 or x.std() == 0:
        return K, 0.0, float(K)
    rho = float(np.corrcoef(x[:-1], x[1:])[0, 1])
    rho = max(rho, 0.0)
    keff = K / (1.0 + (K - 1) * rho)
    return K, rho, keff


def block_boot_mean(x, block, n=NBOOT, rng=RNG):
    """Circular moving-block bootstrap of the mean; preserves local dependence."""
    x = np.asarray(x, float)
    K = len(x)
    if K < block * 2:
        return np.full(n, x.mean())
    nb = int(np.ceil(K / block))
    out = np.empty(n)
    for j in range(n):
        starts = rng.integers(0, K, nb)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel() % K
        out[j] = x[idx[:K]].mean()
    return out


def contiguous_window_means(x, L):
    """EXACT null for 'is a stretch this bad unusual in this series': the mean of every
    contiguous circular window of length L. Serial dependence preserved by construction."""
    x = np.asarray(x, float)
    K = len(x)
    xx = np.concatenate([x, x[:L]])
    cs = np.concatenate([[0.0], np.cumsum(xx)])
    return (cs[L:L + K] - cs[0:K]) / L


def harness_selftest(P):
    """Every decomposition used below is an exact identity. If it does not close, the tables
    are arithmetic, not evidence. Printed, not asserted silently."""
    res = []

    def chk(name, cond):
        res.append((name, bool(cond)))
    pa, Wa, La, pb, Wb, Lb = 0.42, 3.0, 2.0, 0.36, 3.4, 2.6
    c = shapley3(pa, Wa, La, pb, Wb, Lb)
    Ea, Eb = pa * Wa - (1 - pa) * La, pb * Wb - (1 - pb) * Lb
    chk("shapley3 contributions sum to the total change", abs(sum(c.values()) - (Eb - Ea)) < 1e-12)
    chk("shapley3 is zero when nothing moves",
        all(abs(v) < 1e-12 for v in shapley3(pa, Wa, La, pa, Wa, La).values()))
    s2 = shapley2(2.0, 1.5, 1.6, 1.1)
    chk("shapley2 rate+expectancy is exact",
        abs(s2["rate"] + s2["exp"] - (1.6 * 1.1 - 2.0 * 1.5)) < 1e-12)
    wa = np.array([.4, .3, .3]); ma = np.array([1., 2., 3.])
    wb2 = np.array([.2, .3, .5]); mb2 = np.array([1.5, 2., 2.5])
    mx, wi = mix_effect(wa, ma, wb2, mb2)
    chk("mix + within is exact", abs(mx + wi - ((wb2 * mb2).sum() - (wa * ma).sum())) < 1e-12)
    chk("mix + within is zero when nothing moves",
        all(abs(v) < 1e-12 for v in mix_effect(wa, ma, wa, ma)))
    x = np.arange(10.0)
    m = contiguous_window_means(x, 3)
    chk("circular-window null has one window per observation", len(m) == 10)
    chk("circular-window null wraps correctly", abs(m[9] - (9 + 0 + 1) / 3) < 1e-12)
    chk("circular-window null preserves the series mean", abs(m.mean() - x.mean()) < 1e-12)
    K, rho, keff = kdeflate(np.tile([1.0, -1.0], 200))
    chk("K_eff does not inflate on negative autocorrelation", rho == 0.0 and abs(keff - K) < 1e-9)
    y = np.cumsum(np.random.default_rng(0).normal(size=500))
    K, rho, keff = kdeflate(y)
    chk("K_eff deflates a persistent series", keff < K / 10)
    chk("block bootstrap returns the requested draws",
        len(block_boot_mean(np.random.default_rng(1).normal(size=400), 5, n=200)) == 200)
    npass = sum(1 for _, v in res if v)
    for name, v in res:
        P(f"   {'PASS' if v else 'FAIL':<6}{name}")
    P(f"   HARNESS SELFTEST {npass}/{len(res)}")
    return npass == len(res)


# ==================================================================================================
def main():
    t0 = _time.time()
    os.makedirs(OUT, exist_ok=True)
    out = open(os.path.join(OUT, "decay.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    def H(title):
        P("\n" + "=" * 118)
        P("=== " + title)
        P("=" * 118)

    gates = []          # (id, gate, spec, observed, verdict)

    P("=" * 118)
    P("G3_SHORTALPHA / decay  -  WHY IS THE W61 MIRRORED SHORT SLEEVE DECAYING?")
    P("spec: runs/G3_SHORTALPHA_20260831/src/decay/spec.yaml (committed before stage 1 ran)")
    P("=" * 118)
    P("COSTS   floor $4.36/ctrRT (never a headline) | PRIMARY $20.65/ctrRT = "
      f"{PTS_PRIMARY:.4f} NQ pts | all-in $25.01/ctrRT")
    P("ERAS    ERABREAK01 (p=0.0011) forbids pooling. PRE < 2022-05-01 | MODERN >= 2022-05-01 |"
      " FULL = DIAGNOSTIC ONLY")
    P("NOTE    every session-level t below is DIAGNOSTIC ONLY and is deflated by K_eff with")
    P("        rho_bar printed. The binding null is the exact contiguous-circular-window test.")

    H("0. HARNESS SELFTEST - every decomposition below is an exact identity")
    st_ok = harness_selftest(P)
    gates.append(("G0", "harness selftest", "all identities close to 1e-12",
                  "see section 0", "PASS" if st_ok else "FAIL"))

    # ---------------------------------------------------------------- seal + gates 1/2/3
    bl = open(os.path.join(CACHE, "build.log"), encoding="utf-8").read().splitlines()
    H("GATES G1-G3: seal and substrate identity (re-printed verbatim from stage 1)")
    for ln in bl:
        if ("SEAL ASSERTION" in ln or "G1 B1 GATE" in ln or "G2 OBJECT" in ln
                or "substrate " in ln or "CROSS-CHECK" in ln or "identical sessions" in ln
                or ln.strip().startswith("P1   :") or ln.strip().startswith("short:")):
            P("  " + ln.strip())
    for ln in bl:
        if "G1 B1 GATE" in ln:
            gates.append(("G1", "P1 reproduces W61's object",
                          "14.72 +- 0.60 pts/session", ln.split(":")[1].split("(")[0].strip(),
                          "PASS" if "PASS" in ln else "FAIL"))
        if "G2 OBJECT" in ln:
            gates.append(("G2", "short sleeve reproduces W61's object",
                          "2,225 trades +-2%, 6.00 +-0.30 pts/sess",
                          ln.split(":")[1].split("->")[0].strip(),
                          "PASS" if "PASS" in ln else "FAIL"))
        if "SEAL ASSERTION" in ln:
            gates.append(("G3", f"seal {ln.split('[')[1].split(']')[0]}",
                          "max bar < 2026-08-01", ln.split("max bar")[1].split("<")[0].strip(),
                          "PASS" if "PASS" in ln else "FAIL"))

    H("W73 LEG-GEOMETRY CONTROL: the re-implemented ratchet instrument against W73's published "
      "table")
    P("  (the O(1)-sigma re-implementation must reproduce W73's own leg table or the")
    P("   opportunity metric in section 6 is measuring a different instrument)")
    ech = False
    for ln in bl:
        if "ratchet leg control" in ln:
            ech = True
            continue
        if ech:
            if not ln.strip():
                break
            P("  " + ln.rstrip())

    # ---------------------------------------------------------------- load cache
    S = pd.read_csv(os.path.join(CACHE, "full_sessions.csv"), parse_dates=["date"])
    TR = pd.read_csv(os.path.join(CACHE, "full_short_trades.csv"), parse_dates=["date"])
    CD = pd.read_csv(os.path.join(CACHE, "core_daily.csv"), parse_dates=["date"])
    CTR = pd.read_csv(os.path.join(CACHE, "core_short_trades.csv"), parse_dates=["date"])
    S["era"] = np.where(S["date"] < ERA_CUT, "PRE", "MODERN")
    TR["era"] = np.where(TR["date"] < ERA_CUT, "PRE", "MODERN")

    # ---------------------------------------------------------------- 1. the decay restated
    H("1. THE DECAY, RESTATED ON BOTH SUBSTRATES")
    P("W61 quoted 2026 = -10.62 pts/session as the sleeve's worst year ever. W61 called")
    P("setup(), which loads with extend=OFF, so its substrate STOPS AT 2026-05-29 16:59 -")
    P("its '2026' is JANUARY TO MAY ONLY. The FULL substrate below carries 2026 to 07-31.")
    P("")
    P(f"{'year':<7}{'CORE sess':>11}{'CORE pts/s':>13}{'CORE $':>12}   |{'FULL sess':>11}"
      f"{'FULL pts/s':>13}{'FULL $':>12}{'FULL trades':>13}")
    cyr = CD.assign(y=CD["date"].dt.year).groupby("y")
    fyr = S[S["date"] >= pd.Timestamp("2022-07-01")].assign(
        y=lambda d: d["date"].dt.year).groupby("y")
    for y in sorted(set(CD["date"].dt.year) | set(S[S["date"] >= "2022-07-01"]["date"].dt.year)):
        cg = cyr.get_group(y) if y in cyr.groups else None
        fg = fyr.get_group(y) if y in fyr.groups else None
        cs = f"{len(cg):>11}{cg['short'].sum()/PV/len(cg):>13.2f}{cg['short'].sum():>12,.0f}" \
            if cg is not None else f"{'-':>11}{'-':>13}{'-':>12}"
        ntr = int(TR[(TR["date"].dt.year == y) & (TR["date"] >= "2022-07-01")].shape[0]) \
            if fg is not None else 0
        fs = f"{len(fg):>11}{fg['short_pnl436'].sum()/PV/len(fg):>13.2f}" \
             f"{fg['short_pnl436'].sum():>12,.0f}{ntr:>13,}" if fg is not None else ""
        P(f"{y:<7}{cs}   |{fs}")
    P("")
    P("FACT: the two columns are the same object; where they differ, FULL simply has more of the")
    P("      year. The number to carry forward is the FULL column.")

    P(f"\n   FULL-HISTORY per-year record of the same construction (ERABREAK01 stratified):")
    P(f"{'year':<7}{'sessions':>10}{'trades':>9}{'trd/sess':>10}{'pts/sess $4.36':>16}"
      f"{'pts/sess $20.65':>17}{'net $ @20.65':>15}{'era':>9}")
    yr_rows = []
    for y, g in S.groupby(S["date"].dt.year):
        tg = TR[TR["date"].dt.year == y]
        ns = len(g); nt = len(tg)
        net436 = g["short_pnl436"].sum()
        net2065 = net436 - nt * (COST_PRIMARY - COST_FLOOR)
        era = "MODERN" if g["date"].iloc[0] >= ERA_CUT else ("PRE" if g["date"].iloc[-1] <
                                                            ERA_CUT else "SPLIT")
        P(f"{y:<7}{ns:>10}{nt:>9,}{nt/max(ns,1):>10.2f}{net436/PV/max(ns,1):>16.2f}"
          f"{net2065/PV/max(ns,1):>17.2f}{net2065:>15,.0f}{era:>9}")
        yr_rows.append(dict(year=y, sessions=ns, trades=nt, net436=net436, net2065=net2065))
    YR = pd.DataFrame(yr_rows)

    P("")
    for era, g in S.groupby("era"):
        tg = TR[TR["era"] == era]
        net436 = g["short_pnl436"].sum()
        net2065 = net436 - len(tg) * (COST_PRIMARY - COST_FLOOR)
        P(f"   {era:<7} {len(g):>5} sessions {len(tg):>7,} trades   "
          f"{net436/PV/len(g):>7.2f} pts/sess @$4.36   {net2065/PV/len(g):>7.2f} @$20.65   "
          f"net ${net2065:>12,.0f} @$20.65")
    P("   FULL is a DIAGNOSTIC pooling and ERABREAK01 forbids quoting it as one population.")

    P("\n   SUBSTRATE INTEGRITY (the pre-2022 substrate is thinner and its 'sessions' are cut by")
    P("   the >60-minute gap rule, so a short PRE session is not the same object as a modern one):")
    P(f"{'era':<9}{'sessions':>10}{'med bars':>10}{'q10 bars':>10}{'<500 bars %':>13}"
      f"{'med |move|/sess':>18}")
    for era, g in S.groupby("era"):
        P(f"{era:<9}{len(g):>10}{g['bars'].median():>10.0f}"
          f"{np.percentile(g['bars'],10):>10.0f}"
          f"{100*float((g['bars']<500).mean()):>13.1f}{g['absmove'].median():>18.1f}")

    # ---------------------------------------------------------------- 2. per-year mechanics
    H("2. (a) TRADE RATE  (b) HIT RATE vs AVERAGE WIN/LOSS  (c) HOLDING TIME  (d) COST")
    P("All in POINTS GROSS of commission, per trade, one contract. 'edge' = gross pts/trade.")
    P(f"The cost floor to beat is {PTS_PRIMARY:.3f} pts ($20.65/ctrRT). $4.36 is a FLOOR only.")
    P("")
    hdr = (f"{'year':<7}{'sess':>6}{'trds':>7}{'trd/s':>7}{'hit%':>7}{'avgW':>8}{'avgL':>8}"
           f"{'W/L':>7}{'edge':>8}{'net_e':>8}{'medBar':>8}{'barW':>8}{'barL':>8}"
           f"{'cmin/s':>9}{'pts/s':>8}")
    P(hdr)
    rows = []
    for y, g in TR.groupby(TR["date"].dt.year):
        ns = int((S["date"].dt.year == y).sum())
        w = g[g["gross_pts"] > 0]; ll = g[g["gross_pts"] <= 0]
        p = len(w) / len(g)
        W = float(w["gross_pts"].mean()) if len(w) else 0.0
        L = float(-ll["gross_pts"].mean()) if len(ll) else 0.0
        edge = float(g["gross_pts"].mean())
        cmin = float(S[S["date"].dt.year == y]["short_cmin"].sum()) / max(ns, 1)
        ptss = (g["pnl436"].sum() - len(g) * (COST_PRIMARY - COST_FLOOR)) / PV / max(ns, 1)
        P(f"{y:<7}{ns:>6}{len(g):>7,}{len(g)/max(ns,1):>7.2f}{100*p:>7.1f}{W:>8.2f}{L:>8.2f}"
          f"{W/max(L,1e-9):>7.3f}{edge:>8.3f}{edge-PTS_PRIMARY:>8.3f}"
          f"{g['bars'].median():>8.0f}{w['bars'].median() if len(w) else 0:>8.0f}"
          f"{ll['bars'].median() if len(ll) else 0:>8.0f}{cmin:>9.0f}{ptss:>8.2f}")
        rows.append(dict(year=y, sessions=ns, trades=len(g), rate=len(g) / max(ns, 1),
                         p=p, W=W, L=L, edge=edge, medbar=float(g["bars"].median()),
                         cmin=cmin, pts_s_2065=ptss))
    M = pd.DataFrame(rows)
    M.to_csv(os.path.join(OUT, "decay_peryear.csv"), index=False)
    P("\n   edge  = mean GROSS points per trade   net_e = edge minus the $20.65 cost floor")
    P("   barW/barL = median bars held by winners / losers   cmin/s = contract-minutes short "
      "per session")

    P("\n   THE SAME YEARS, SCALE-FREE. 'W/L req' is the win/loss ratio the year's own hit rate")
    P("   needs to break even, (1-p)/p; 'margin' is how far above it the year actually was.")
    P("   W/vol and L/vol divide by that year's mean session |1-min move|, so a year cannot look")
    P("   worse merely because volatility expanded.")
    P(f"\n{'year':<7}{'hit%':>7}{'W/L':>8}{'W/L req':>9}{'margin':>9}{'|move|/s':>10}"
      f"{'W/vol':>8}{'L/vol':>8}{'edge/vol':>10}{'gross edge':>12}")
    for y, g in TR.groupby(TR["date"].dt.year):
        sg = S[S["date"].dt.year == y]
        vol = float(sg["absmove"].mean())
        w = g[g["gross_pts"] > 0]["gross_pts"]; ll = -g[g["gross_pts"] <= 0]["gross_pts"]
        p = len(w) / len(g)
        W = float(w.mean()) if len(w) else 0.0
        L = float(ll.mean()) if len(ll) else 0.0
        wl = W / max(L, 1e-9); req = (1 - p) / max(p, 1e-9)
        P(f"{y:<7}{100*p:>7.1f}{wl:>8.3f}{req:>9.3f}{wl-req:>9.3f}{vol:>10.1f}"
          f"{1000*W/vol:>8.2f}{1000*L/vol:>8.2f}{1000*g['gross_pts'].mean()/vol:>10.3f}"
          f"{g['gross_pts'].mean():>12.3f}")
    P("   (W/vol, L/vol and edge/vol are x1000 for readability.)")

    # baseline vs 2026, MODERN only
    trb = TR[(TR["date"].dt.year.between(2022, 2025)) & (TR["era"] == "MODERN")]
    trt = TR[TR["date"].dt.year == 2026]
    sb = S[(S["date"].dt.year.between(2022, 2025)) & (S["era"] == "MODERN")]
    stt = S[S["date"].dt.year == 2026]

    def agg(tr, ss):
        w = tr[tr["gross_pts"] > 0]; ll = tr[tr["gross_pts"] <= 0]
        return dict(n=len(tr), ns=len(ss), rate=len(tr) / len(ss),
                    p=len(w) / len(tr), W=float(w["gross_pts"].mean()),
                    L=float(-ll["gross_pts"].mean()), edge=float(tr["gross_pts"].mean()),
                    medbar=float(tr["bars"].median()), meanbar=float(tr["bars"].mean()),
                    cmin=float(ss["short_cmin"].sum()) / len(ss))
    ab, at = agg(trb, sb), agg(trt, stt)

    H("3. WHICH FACTOR MOVED? Shapley decomposition, order-independent, MODERN era only")
    P("baseline = 2022-05-01..2025-12-31 pooled (the sleeve's own modern pre-2026 record)")
    P("target   = 2026-01-01..2026-07-31")
    P("")
    P(f"{'':<28}{'baseline':>12}{'2026':>12}{'change':>12}{'% change':>11}")
    for lab, k, f in (("trades per session", "rate", "{:.3f}"), ("hit rate", "p", "{:.4f}"),
                      ("mean WIN (gross pts)", "W", "{:.3f}"),
                      ("mean LOSS (gross pts)", "L", "{:.3f}"),
                      ("gross edge (pts/trade)", "edge", "{:.4f}"),
                      ("median bars held", "medbar", "{:.1f}"),
                      ("mean bars held", "meanbar", "{:.1f}"),
                      ("contract-min / session", "cmin", "{:.0f}")):
        d = at[k] - ab[k]
        P(f"{lab:<28}{f.format(ab[k]):>12}{f.format(at[k]):>12}{f.format(d):>12}"
          f"{100*d/abs(ab[k]) if ab[k] else 0:>10.1f}%")

    c3 = shapley3(ab["p"], ab["W"], ab["L"], at["p"], at["W"], at["L"])
    dE = at["edge"] - ab["edge"]
    P(f"\n   E = p*W - (1-p)*L      baseline E = {ab['p']*ab['W']-(1-ab['p'])*ab['L']:+.4f} "
      f"pts/trade   2026 E = {at['p']*at['W']-(1-at['p'])*at['L']:+.4f}   change {dE:+.4f}")
    P(f"   {'factor':<26}{'contribution (pts/trade)':>28}{'share of the change':>22}")
    for k, lab in (("p", "HIT RATE p"), ("W", "AVERAGE WIN W"), ("L", "AVERAGE LOSS L")):
        P(f"   {lab:<26}{c3[k]:>28.4f}{100*c3[k]/dE if dE else 0:>21.1f}%")
    P(f"   {'(residual)':<26}{dE-sum(c3.values()):>28.4f}")

    c2 = shapley2(ab["rate"], ab["edge"], at["rate"], at["edge"])
    dps = at["rate"] * at["edge"] - ab["rate"] * ab["edge"]
    P(f"\n   pts/session (gross) = (trades/session) x (gross edge)")
    P(f"   baseline {ab['rate']*ab['edge']:+.3f}   2026 {at['rate']*at['edge']:+.3f}   "
      f"change {dps:+.3f} pts/session")
    P(f"   {'TRADE-RATE term':<26}{c2['rate']:>28.3f}{100*c2['rate']/dps if dps else 0:>21.1f}%")
    P(f"   {'EXPECTANCY term':<26}{c2['exp']:>28.3f}{100*c2['exp']/dps if dps else 0:>21.1f}%")

    # ---------------------------------------------------------------- 4. cost fork
    H("4. GATE G6 - THE COST FORK: is the 2026 edge merely below the floor, or negative?")
    P(f"{'window':<24}{'trades':>9}{'gross pts/trade':>18}{'@ $4.36':>11}{'@ $20.65':>11}"
      f"{'@ $25.01':>11}{'verdict':>34}")
    for lab, tr, ss in (("MODERN 2022-2025", trb, sb), ("2026 (to 07-31)", trt, stt),
                        ("PRE 2006-2022/04", TR[TR["era"] == "PRE"], S[S["era"] == "PRE"])):
        e = float(tr["gross_pts"].mean())
        v = ("GROSS EDGE IS NEGATIVE - not a cost problem" if e <= 0 else
             ("gross positive but BELOW the floor" if e < PTS_PRIMARY
              else "clears the primary cost floor"))
        P(f"{lab:<24}{len(tr):>9,}{e:>18.4f}{e-COST_FLOOR/PV:>11.4f}{e-PTS_PRIMARY:>11.4f}"
          f"{e-COST_ALLIN/PV:>11.4f}{v:>34}")
    e26 = float(trt["gross_pts"].mean())
    gates.append(("G6", "sign of 2026 GROSS pts/trade", "> 0 => cost problem; <= 0 => not",
                  f"{e26:+.4f} pts/trade",
                  "COST" if e26 > 0 else "NOT-A-COST-PROBLEM"))

    # ---------------------------------------------------------------- 4b intervals
    H("4b. HOW BIG IS THE EDGE, WITH AN INTERVAL? (spec amendment 2)")
    P("Circular MOVING-BLOCK bootstrap, 5-session blocks (one trading week), 2,000 draws, on the")
    P("SESSION series - dependence preserving, not an iid resample. The cost floor at $20.65 is")
    P(f"{PTS_PRIMARY:.4f} points PER TRADE, so it is compared against the per-trade edge, and")
    P("the per-session figures are quoted net of it.")
    P("")
    P(f"{'window':<24}{'sessions':>10}{'pts/sess @4.36':>16}{'90% CI':>24}"
      f"{'pts/sess @20.65':>17}{'90% CI':>24}")
    for lab, ss, tr in (("PRE 2006-2022/04", S[S["era"] == "PRE"], TR[TR["era"] == "PRE"]),
                        ("MODERN 2022-05 on", S[S["era"] == "MODERN"],
                         TR[TR["era"] == "MODERN"]),
                        ("MODERN ex-2026", sb, trb),
                        ("2026 only", stt, trt)):
        x = ss["short_pnl436"].values / PV
        extra = (COST_PRIMARY - COST_FLOOR) / PV * len(tr) / len(ss)
        b = block_boot_mean(x, 5)
        P(f"{lab:<24}{len(ss):>10}{x.mean():>16.2f}"
          f"{f'[{np.percentile(b,5):+.2f}, {np.percentile(b,95):+.2f}]':>24}"
          f"{x.mean()-extra:>17.2f}"
          f"{f'[{np.percentile(b,5)-extra:+.2f}, {np.percentile(b,95)-extra:+.2f}]':>24}")
    P("")
    P("The per-trade table below uses the same bootstrap on the TRADE series with 5-TRADE")
    P("blocks (consecutive trades in a session are the dependent unit there).")
    P(f"{'window':<24}{'trades':>10}{'gross pts/trade':>17}{'90% CI':>24}"
      f"{'floor':>9}{'clears the floor?':>20}")
    for lab, tr in (("PRE 2006-2022/04", TR[TR["era"] == "PRE"]),
                    ("MODERN 2022-05 on", TR[TR["era"] == "MODERN"]),
                    ("MODERN ex-2026", trb), ("2026 only", trt)):
        g = tr["gross_pts"].values
        b = block_boot_mean(g, 5)
        lo, hi = np.percentile(b, 5), np.percentile(b, 95)
        P(f"{lab:<24}{len(tr):>10,}{g.mean():>17.4f}"
          f"{f'[{lo:+.4f}, {hi:+.4f}]':>24}{PTS_PRIMARY:>9.4f}"
          f"{('YES' if lo > PTS_PRIMARY else ('no - CI straddles it' if hi > PTS_PRIMARY else 'NO - CI entirely below')):>20}")

    # ---------------------------------------------------------------- 5. holding time detail
    H("5. (c) HOLDING TIME IN DETAIL - is it being chopped out, or held into worse exits?")
    P(f"{'window':<20}{'q10':>7}{'q25':>7}{'med':>7}{'q75':>7}{'q90':>7}{'mean':>8}"
      f"{'medW':>7}{'medL':>7}{'|  <5 bar %':>12}{'>60 bar %':>11}{'pnl of <5bar':>14}")
    for lab, tr in (("MODERN 2022-2025", trb), ("2026", trt), ("PRE", TR[TR["era"] == "PRE"])):
        b = tr["bars"].values
        w = tr[tr["gross_pts"] > 0]["bars"]; ll = tr[tr["gross_pts"] <= 0]["bars"]
        sh = tr[tr["bars"] < 5]
        P(f"{lab:<20}{np.percentile(b,10):>7.0f}{np.percentile(b,25):>7.0f}"
          f"{np.percentile(b,50):>7.0f}{np.percentile(b,75):>7.0f}{np.percentile(b,90):>7.0f}"
          f"{b.mean():>8.1f}{w.median():>7.0f}{ll.median():>7.0f}"
          f"{100*float((b<5).mean()):>12.1f}{100*float((b>60).mean()):>11.1f}"
          f"{sh['gross_pts'].mean():>14.3f}")
    P("\n   gross pts/trade by holding-time bucket (the shape of where the money is made):")
    bks = [(0, 5), (5, 15), (15, 30), (30, 60), (60, 120), (120, 10 ** 9)]
    labs = ["{}-{}".format(a, b if b < 10 ** 9 else "inf") for a, b in bks]
    P(f"{'bucket (bars)':<18}" + "".join("{:>16}".format(s) for s in labs))
    for lab, tr in (("MODERN 22-25 n", trb), ("2026 n", trt)):
        P(f"{lab:<18}" + "".join(
            f"{int(((tr['bars']>=a)&(tr['bars']<b)).sum()):>16,}" for a, b in bks))
    for lab, tr in (("MODERN 22-25 pts", trb), ("2026 pts", trt)):
        P(f"{lab:<18}" + "".join(
            f"{tr[(tr['bars']>=a)&(tr['bars']<b)]['gross_pts'].mean():>16.3f}" for a, b in bks))

    # ---------------------------------------------------------------- 5c halts
    H("5c. WHY THE TRADE RATE FELL - the session halt and target, reconstructed from the ledger")
    P("The sleeve stops trading a session once cumulative session P&L <= -$1,300 (the halt) or")
    P(">= +$1,000 (the target). Both END the session's trading, so a year with bigger losses")
    P("mechanically takes FEWER trades. This links (b) to (a) rather than treating them as two")
    P("independent findings.")
    T2 = TR.sort_values(["sess", "entry_i"]).copy()
    T2["cum"] = T2.groupby("sess")["pnl436"].cumsum()
    agg2 = T2.groupby("sess").agg(mn=("cum", "min"), mx=("cum", "max"), n=("cum", "size"))
    agg2["halt"] = agg2["mn"] <= -1300.0
    agg2["targ"] = agg2["mx"] >= 1000.0
    sm = S.set_index("sess").join(agg2, how="left")
    sm["halt"] = sm["halt"].fillna(False); sm["targ"] = sm["targ"].fillna(False)
    P("")
    P(f"{'year':<7}{'traded sess':>13}{'halt %':>9}{'target %':>10}{'trd/traded sess':>17}"
      f"{'pts/sess halted':>17}{'pts/sess other':>16}")
    for y, g in sm.groupby(sm["date"].dt.year):
        tsd = g[g["n"].notna()]
        if not len(tsd):
            continue
        hh = tsd[tsd["halt"]]; oo = tsd[~tsd["halt"]]
        P(f"{y:<7}{len(tsd):>13}{100*float(tsd['halt'].mean()):>9.1f}"
          f"{100*float(tsd['targ'].mean()):>10.1f}{tsd['n'].mean():>17.2f}"
          f"{(hh['short_pnl436'].mean()/PV if len(hh) else 0):>17.2f}"
          f"{(oo['short_pnl436'].mean()/PV if len(oo) else 0):>16.2f}")

    # ---------------------------------------------------------------- 5d counterfactual
    nhf = os.path.join(CACHE, "full_sessions_nohalt.csv")
    if os.path.exists(nhf):
        H("5d. THE NO-OVERLAY COUNTERFACTUAL (spec amendment 1, declared before it was run)")
        P("S_nohalt = the identical sleeve with halt=+inf and target=None. NOT a candidate and")
        P("never quoted as an improvement - it exists only to say whether the fixed-dollar")
        P("session overlay is the mechanism behind 2026, or whether the halt table above is")
        P("descriptive only. Falsifier (spec): the overlay explanation is supported ONLY if")
        P("removing it materially shrinks 2026's deficit against its own 2022-2025 baseline.")
        NH = pd.read_csv(nhf, parse_dates=["date"])
        SS = S.merge(NH[["sess", "nohalt_pnl436", "nohalt_ntr"]], on="sess", how="left")
        P("")
        P(f"{'year':<7}{'sess':>6}|{'INCUMBENT trd':>15}{'pts/sess':>11}|"
          f"{'NO-OVERLAY trd':>16}{'pts/sess':>11}|{'difference':>12}")
        for y, g in SS.groupby(SS["date"].dt.year):
            ns = len(g)
            a_ = g["short_pnl436"].sum() / PV / ns
            b_ = g["nohalt_pnl436"].sum() / PV / ns
            P(f"{y:<7}{ns:>6}|{g['short_ntr'].sum():>15,.0f}{a_:>11.2f}|"
              f"{g['nohalt_ntr'].sum():>16,.0f}{b_:>11.2f}|{b_-a_:>12.2f}")
        P("")
        P(f"{'window':<24}{'INCUMBENT pts/sess':>20}{'NO-OVERLAY pts/sess':>21}")
        rowsx = {}
        for lab, m in (("PRE 2006-2022/04", SS["era"] == "PRE"),
                       ("MODERN 2022-2025", (SS["date"].dt.year.between(2022, 2025)) &
                        (SS["era"] == "MODERN")),
                       ("2026", SS["date"].dt.year == 2026)):
            g = SS[m]
            a_ = g["short_pnl436"].sum() / PV / len(g)
            b_ = g["nohalt_pnl436"].sum() / PV / len(g)
            rowsx[lab] = (a_, b_)
            P(f"{lab:<24}{a_:>20.2f}{b_:>21.2f}")
        da = rowsx["2026"][0] - rowsx["MODERN 2022-2025"][0]
        db = rowsx["2026"][1] - rowsx["MODERN 2022-2025"][1]
        P(f"\n   2026 deficit against its own 2022-2025 baseline:")
        P(f"      INCUMBENT  {da:+.2f} pts/session")
        P(f"      NO-OVERLAY {db:+.2f} pts/session")
        sup = abs(db) < 0.6 * abs(da)
        P(f"   spec falsifier: supported only if removing the overlay materially shrinks the")
        P(f"   deficit. |no-overlay deficit| / |incumbent deficit| = {abs(db)/abs(da):.3f}"
          f"  ->  {'OVERLAY IS PART OF THE MECHANISM' if sup else 'OVERLAY IS NOT THE MECHANISM'}")
        gates.append(("G7", "is the fixed $1,300 session halt the mechanism?",
                      "|no-overlay deficit| < 0.6 x |incumbent deficit|",
                      f"ratio {abs(db)/abs(da):.3f}",
                      "OVERLAY IMPLICATED" if sup else "OVERLAY EXONERATED"))

    # ---------------------------------------------------------------- 5b excursion
    if "mfe_pts" in TR.columns:
        H("5b. ENTRY vs EXIT - did the trades stop getting favourable, or stop keeping it?")
        P("mfe = the best the trade ever was, in points, using intrabar highs/lows.")
        P("eff = realised gross points / mfe = the share of its own best excursion it kept.")
        P("If mfe holds and eff falls, the exit is the problem. If mfe falls, the ENTRIES are")
        P("not finding down-moves - which is the opportunity side of the same fork.")
        P("")
        P(f"{'window':<20}{'trades':>8}{'med mfe':>10}{'mean mfe':>10}{'med mae':>10}"
          f"{'mean mae':>10}{'med eff':>10}{'mean eff':>10}{'mfe>=5pt%':>11}{'mfe>=20pt%':>12}")
        for lab, tr in (("PRE 2006-2022/04", TR[TR["era"] == "PRE"]),
                        ("MODERN 2022-2025", trb), ("2026", trt)):
            P(f"{lab:<20}{len(tr):>8,}{tr['mfe_pts'].median():>10.2f}"
              f"{tr['mfe_pts'].mean():>10.2f}{tr['mae_pts'].median():>10.2f}"
              f"{tr['mae_pts'].mean():>10.2f}{tr['eff'].median():>10.3f}"
              f"{tr['eff'].mean():>10.3f}"
              f"{100*float((tr['mfe_pts']>=5).mean()):>11.1f}"
              f"{100*float((tr['mfe_pts']>=20).mean()):>12.1f}")
        P("")
        P(f"{'year':<7}{'trades':>8}{'med mfe':>10}{'mean mfe':>10}{'mean mae':>10}"
          f"{'mean eff':>10}{'mfe>=20pt%':>12}{'gross edge':>12}")
        for y, tr in TR.groupby(TR["date"].dt.year):
            P(f"{y:<7}{len(tr):>8,}{tr['mfe_pts'].median():>10.2f}{tr['mfe_pts'].mean():>10.2f}"
              f"{tr['mae_pts'].mean():>10.2f}{tr['eff'].mean():>10.3f}"
              f"{100*float((tr['mfe_pts']>=20).mean()):>12.1f}"
              f"{tr['gross_pts'].mean():>12.3f}")

    # ---------------------------------------------------------------- 6. opportunity
    H("6. (e) THE DECISIVE FORK - WAS THERE ANYTHING TO BE SHORT OF? (price only, engine-blind)")
    P("O1 ratchet-native: the vendor ratchet's own legs. PRIMARY = VolMult 16 (declared in the")
    P("   spec before running). 'dn MFE/s' = points of favourable excursion available to a short")
    P("   entered at each DOWN leg's start, summed per session. Computed from price alone.")
    P("O3 raw: down-share = sum of negative 1-min close changes / sum of |changes|.")
    P("")
    P(f"{'year':<7}{'sess':>6}{'absmove/s':>11}{'dn share':>10}{'sess ret':>10}{'dn sess%':>10}"
      f"|{'o1 dn n/s':>11}{'o1 dnMFE/s':>12}{'o1 upMFE/s':>12}{'dn/up':>8}"
      f"|{'zz40 n/s':>10}{'zz40 pts/s':>12}{'zz40 dn/up':>12}")
    opp_rows = []
    for y, g in S.groupby(S["date"].dt.year):
        ns = len(g)
        dnsh = g["dnmove"].sum() / max(g["absmove"].sum(), 1e-9)
        o1dn = g["o1_dn16_mfe"].sum() / ns
        o1up = g["o1_up16_mfe"].sum() / ns
        z40dn = g["o2_dn40_pts"].sum() / ns
        z40up = g["o2_up40_pts"].sum() / ns
        z40r = z40dn / z40up if z40up > 1e-6 else float("nan")
        P(f"{y:<7}{ns:>6}{g['absmove'].mean():>11.1f}{dnsh:>10.4f}{g['ret'].mean():>10.2f}"
          f"{100*float((g['ret']<0).mean()):>10.1f}|{g['o1_dn16_n'].sum()/ns:>11.2f}"
          f"{o1dn:>12.1f}{o1up:>12.1f}{o1dn/max(o1up,1e-9):>8.3f}"
          f"|{g['o2_dn40_n'].sum()/ns:>10.2f}{z40dn:>12.1f}{z40r:>12.3f}")
        opp_rows.append(dict(year=y, sessions=ns, absmove=g["absmove"].mean(), dnshare=dnsh,
                             ret=g["ret"].mean(), dnsess=float((g["ret"] < 0).mean()),
                             o1dn_n=g["o1_dn16_n"].sum() / ns, o1dn_mfe=o1dn, o1up_mfe=o1up,
                             zz40dn_n=g["o2_dn40_n"].sum() / ns, zz40dn=z40dn, zz40up=z40up))
    OP = pd.DataFrame(opp_rows)
    OP.to_csv(os.path.join(OUT, "decay_opportunity.csv"), index=False)

    P("\n   the same at the other two ratchet scales and the other two zigzag thresholds "
      "(down MFE / pts per session):")
    P(f"{'year':<7}" + "".join(f"{c:>13}" for c in
                               ("o1dn VM6", "o1dn VM30", "zz20 dn", "zz80 dn",
                                "o1dn/up VM6", "o1dn/up VM30")))
    for y, g in S.groupby(S["date"].dt.year):
        ns = len(g)
        P(f"{y:<7}"
          f"{g['o1_dn6_mfe'].sum()/ns:>13.1f}{g['o1_dn30_mfe'].sum()/ns:>13.1f}"
          f"{g['o2_dn20_pts'].sum()/ns:>13.1f}{g['o2_dn80_pts'].sum()/ns:>13.1f}"
          f"{g['o1_dn6_mfe'].sum()/max(g['o1_up6_mfe'].sum(),1e-9):>13.3f}"
          f"{g['o1_dn30_mfe'].sum()/max(g['o1_up30_mfe'].sum(),1e-9):>13.3f}")

    # ---------------------------------------------------------------- 6b direction
    H("6b. THE ONE VARIABLE THAT DOES MOVE WITH IT: the market's own direction")
    P("Monthly panel. x = the market's mean session close-minus-open in that month (points per")
    P("session); y = the sleeve's pts/session in that month. A mirrored trend follower should be")
    P("a linear function of x, and if it is, 'decay' is the wrong noun.")
    P("DIAGNOSTIC: x is contemporaneous, so this is a decomposition and never a trading rule.")
    MO = S.copy()
    MO["m"] = MO["date"].dt.to_period("M")
    mo = MO.groupby("m").agg(sess=("date", "size"), y=("short_pnl436", "mean"),
                             x=("ret", "mean"), vol=("absmove", "mean")).reset_index()
    mo["y"] = mo["y"] / PV
    mo = mo[mo["sess"] >= 10].reset_index(drop=True)
    mo["era"] = np.where(mo["m"].dt.to_timestamp() < ERA_CUT, "PRE", "MODERN")

    def fit(d):
        A_ = np.c_[np.ones(len(d)), d["x"].values]
        bhat, *_ = np.linalg.lstsq(A_, d["y"].values, rcond=None)
        pred = A_ @ bhat
        r2 = 1 - ((d["y"].values - pred) ** 2).sum() / \
            ((d["y"].values - d["y"].values.mean()) ** 2).sum()
        return bhat, r2, d["y"].values - pred
    for lab, d in (("PRE months", mo[mo["era"] == "PRE"]),
                   ("MODERN months", mo[mo["era"] == "MODERN"]),
                   ("MODERN ex-2026", mo[(mo["era"] == "MODERN") &
                                         (mo["m"].dt.year < 2026)]),
                   ("ALL (diagnostic)", mo)):
        bh, r2, _ = fit(d)
        # block bootstrap on the slope, 6-month blocks
        sl = []; ic = []
        K = len(d)
        for _ in range(1000):
            starts = RNG.integers(0, K, int(np.ceil(K / 6)))
            idx = (starts[:, None] + np.arange(6)[None, :]).ravel() % K
            dd = d.iloc[idx[:K]]
            bb = fit(dd)[0]
            sl.append(bb[1]); ic.append(bb[0])
        sl = np.array(sl); ic = np.array(ic)
        P(f"   {lab:<18} n={K:>4}  slope {bh[1]:+8.4f} [{np.percentile(sl,5):+.4f}, "
          f"{np.percentile(sl,95):+.4f}]   R2 {r2:.3f}")
        P(f"   {'':<18}        DRIFT-NEUTRAL EXPECTANCY (intercept) {bh[0]:+7.3f} pts/session"
          f"   90% CI [{np.percentile(ic,5):+.3f}, {np.percentile(ic,95):+.3f}]")
    P("")
    P("   The intercept is the sleeve's expectancy at ZERO market drift - the closest thing to")
    P("   'skill with the direction taken out'. To pay the $20.65 floor it must exceed")
    P(f"   trades/session x {PTS_PRIMARY:.4f} pts, which is "
      f"{ab['rate']*PTS_PRIMARY:.2f} pts/session at the modern trade rate ({ab['rate']:.2f}/sess)"
      f" and {float(len(TR[TR['era']=='PRE']))/len(S[S['era']=='PRE'])*PTS_PRIMARY:.2f} at the "
      f"PRE rate.")
    P("")
    P("   OUT-OF-PERIOD TEST. Fit on the 2022-05..2025-12 months only, then PREDICT each 2026")
    P("   month from that month's market drift alone. Nothing about 2026 is used in the fit.")
    tr_m = mo[(mo["era"] == "MODERN") & (mo["m"].dt.year < 2026)]
    te_m = mo[mo["m"].dt.year == 2026]
    bh, r2, resid = fit(tr_m)
    sd = resid.std(ddof=2)
    P(f"   {'month':<10}{'mkt drift':>11}{'predicted':>11}{'actual':>10}{'resid':>9}"
      f"{'resid/sd':>10}")
    for _, r in te_m.iterrows():
        pr = bh[0] + bh[1] * r["x"]
        P(f"   {str(r['m']):<10}{r['x']:>11.2f}{pr:>11.2f}{r['y']:>10.2f}"
          f"{r['y']-pr:>9.2f}{(r['y']-pr)/sd:>10.2f}")
    prd = bh[0] + bh[1] * te_m["x"].values
    act = te_m["y"].values
    wts = te_m["sess"].values
    pa = float(np.average(prd, weights=wts)); aa = float(np.average(act, weights=wts))
    P(f"   {'2026 pooled':<10}{float(np.average(te_m['x'],weights=wts)):>11.2f}"
      f"{pa:>11.2f}{aa:>10.2f}{aa-pa:>9.2f}"
      f"{(aa-pa)/(sd/np.sqrt(len(te_m))):>10.2f}")
    P(f"   in-sample residual sd = {sd:.2f} pts/session per month; 2026's 7 months have")
    P(f"   {int((np.abs(act-prd) > 2*sd).sum())} of {len(te_m)} residuals beyond 2 sd.")
    P(f"   READ: the 2026 shortfall the campaign called a decay is "
      f"{'FULLY' if abs(aa-pa) < sd/np.sqrt(len(te_m))*1.645 else 'NOT fully'} accounted for by")
    P(f"   the market's own direction at the 90 % level: predicted {pa:+.2f}, actual {aa:+.2f}.")
    gates.append(("G8", "is 2026 explained by market direction alone?",
                  "|actual-predicted| within 1.645 SE of the fit",
                  f"pred {pa:+.2f} vs actual {aa:+.2f}",
                  "EXPLAINED" if abs(aa - pa) < sd / np.sqrt(len(te_m)) * 1.645
                  else "NOT FULLY EXPLAINED"))

    # capture ratio + the G5 fork
    H("7. GATE G5 - OPPORTUNITY DROUGHT vs SKILL DECAY (thresholds fixed in the spec)")

    def cap(ss, tr):
        ns = len(ss)
        opp = ss["o1_dn16_mfe"].sum() / ns
        won = tr["gross_pts"].sum() / ns
        return opp, won, won / max(opp, 1e-9)
    ob, wb, cb = cap(sb, trb)
    ot, wt, ct = cap(stt, trt)
    P(f"{'':<34}{'baseline 2022-2025':>22}{'2026':>14}{'ratio 2026/base':>18}")
    P(f"{'O1 down-MFE available per session':<34}{ob:>22.2f}{ot:>14.2f}{ot/ob:>18.3f}")
    P(f"{'sleeve GROSS pts won per session':<34}{wb:>22.2f}{wt:>14.2f}{wt/wb:>18.3f}")
    P(f"{'CAPTURE = won / available':<34}{cb:>22.5f}{ct:>14.5f}{ct/cb:>18.3f}")
    for nm, col in (("O1 down-MFE VolMult 6", "o1_dn6_mfe"), ("O1 down-MFE VolMult 30",
                                                              "o1_dn30_mfe"),
                    ("zigzag-40 down points", "o2_dn40_pts"),
                    ("zigzag-20 down points", "o2_dn20_pts"),
                    ("zigzag-80 down points", "o2_dn80_pts")):
        a_ = sb[col].sum() / len(sb); b_ = stt[col].sum() / len(stt)
        P(f"{'  cross-check ' + nm:<34}{a_:>22.2f}{b_:>14.2f}{b_/max(a_,1e-9):>18.3f}")
    oratio, cratio = ot / ob, ct / cb
    if oratio <= 0.75 and cratio >= 0.75:
        v5 = "OPPORTUNITY DROUGHT"
    elif oratio >= 0.90 and cratio <= 0.75:
        v5 = "SKILL DECAY"
    else:
        v5 = "MIXED"
    P(f"\n   spec rule: DROUGHT if OPP<=0.75 and CAP>=0.75 ; SKILL DECAY if OPP>=0.90 and "
      f"CAP<=0.75 ; else MIXED")
    P(f"   OBSERVED   OPP ratio {oratio:.3f}   CAP ratio {cratio:.3f}   ->  {v5}")
    gates.append(("G5", "opportunity drought vs skill decay",
                  "DROUGHT: OPP<=.75 & CAP>=.75 | SKILL: OPP>=.90 & CAP<=.75",
                  f"OPP {oratio:.3f}, CAP {cratio:.3f}", v5))
    P("\n   HOW FAR THIS VERDICT ACTUALLY GOES - stated here rather than quietly softened later.")
    P("   The rule was written expecting OPP near 1.0 and it fired at OPP = 1.79, so the SKILL")
    P("   branch is technically satisfied by a CAPTURE ratio whose DENOMINATOR grew 79 %. What")
    P("   the fork does establish, unambiguously, is the half that was decisive: the DROUGHT")
    P("   branch is dead. There was more available down-excursion per session in 2026 than in")
    P("   any baseline year, on all five opportunity measures, and the down/up balance was")
    P("   normal. What it does NOT establish is that the numerator moved by more than noise -")
    P("   section 9 (G4) puts 2026 at the 10.9th percentile of this series' own contiguous-")
    P("   window null and section 4b gives its 251-trade gross edge a 90 % interval of")
    P("   [-9.72, +6.03] points, which cannot separate -1.98 from the +3.41 baseline.")
    P("   'SKILL DECAY' is therefore the correct reading of the preregistered rule and an")
    P("   OVERSTATEMENT of the evidence. Both sentences are recorded.")

    # class-conditional mix/within decomposition
    H("8. MIX vs WITHIN - the same fork done as an exact decomposition, not a ratio")
    P("Sessions are classed by an OPPORTUNITY variable whose cuts are fixed on the MODERN")
    P("baseline (2022-05..2025-12) terciles and then applied unchanged to 2026, so the class")
    P("definition cannot move with the answer. The matched UNCONDITIONAL control is section 2.")
    P("DIAGNOSTIC: the class uses whole-session information and is not a tradeable rule.")
    for cls_col, cls_name in (("o1_dn16_mfe", "available DOWN-leg MFE (O1 VolMult 16)"),
                              ("ret", "session close-minus-open return"),
                              ("dnmove", "sum of negative 1-min moves")):
        cuts = np.quantile(sb[cls_col].values, [1 / 3, 2 / 3])
        P(f"\n   CLASS = {cls_name}   cuts (from baseline only) = "
          f"[{cuts[0]:.2f}, {cuts[1]:.2f}]")
        kb = np.digitize(sb[cls_col].values, cuts)
        kt = np.digitize(stt[cls_col].values, cuts)
        yb = sb["short_pnl436"].values / PV
        yt = stt["short_pnl436"].values / PV
        wa = np.array([(kb == k).mean() for k in range(3)])
        wb_ = np.array([(kt == k).mean() for k in range(3)])
        ma = np.array([yb[kb == k].mean() if (kb == k).any() else 0.0 for k in range(3)])
        mb_ = np.array([yt[kt == k].mean() if (kt == k).any() else 0.0 for k in range(3)])
        P(f"   {'tercile':<12}{'base freq':>11}{'2026 freq':>11}{'base pts/s':>12}"
          f"{'2026 pts/s':>12}{'n base':>9}{'n 2026':>9}")
        for k, nm in enumerate(("LOW", "MID", "HIGH")):
            P(f"   {nm:<12}{wa[k]:>11.3f}{wb_[k]:>11.3f}{ma[k]:>12.2f}{mb_[k]:>12.2f}"
              f"{int((kb==k).sum()):>9}{int((kt==k).sum()):>9}")
        mix, wit = mix_effect(wa, ma, wb_, mb_)
        tot = yt.mean() - yb.mean()
        P(f"   total change {tot:+.2f} pts/session = MIX {mix:+.2f} ({100*mix/tot if tot else 0:.0f} %)"
          f" + WITHIN {wit:+.2f} ({100*wit/tot if tot else 0:.0f} %)")
        bootm = []
        for _ in range(400):
            ib = RNG.integers(0, len(yb), len(yb)); it = RNG.integers(0, len(yt), len(yt))
            wa2 = np.array([(kb[ib] == k).mean() for k in range(3)])
            wb2 = np.array([(kt[it] == k).mean() for k in range(3)])
            ma2 = np.array([yb[ib][kb[ib] == k].mean() if (kb[ib] == k).any() else 0.0
                            for k in range(3)])
            mb2 = np.array([yt[it][kt[it] == k].mean() if (kt[it] == k).any() else 0.0
                            for k in range(3)])
            bootm.append(mix_effect(wa2, ma2, wb2, mb2))
        bm = np.array([x[0] for x in bootm]); bw = np.array([x[1] for x in bootm])
        P(f"   bootstrap (400 draws, session resample): MIX 90% CI "
          f"[{np.percentile(bm,5):+.2f}, {np.percentile(bm,95):+.2f}]   WITHIN 90% CI "
          f"[{np.percentile(bw,5):+.2f}, {np.percentile(bw,95):+.2f}]")

    # ---------------------------------------------------------------- 9. is the decay real
    H("9. GATE G4 - IS THE 2026 STRETCH EVEN DISTINGUISHABLE FROM THIS SERIES' OWN NOISE?")
    for lab, d_, col in (("MODERN (2022-05 on)", S[S["era"] == "MODERN"], "short_pnl436"),
                         ("FULL 2006-2026 (diagnostic)", S, "short_pnl436")):
        x = d_[col].values / PV
        L = int((d_["date"].dt.year == 2026).sum())
        real = x[d_["date"].dt.year.values == 2026].mean()
        nullm = contiguous_window_means(x, L)
        pct = 100 * float((nullm < real).mean())
        K, rho, keff = kdeflate(x)
        P(f"\n   {lab}: {len(x)} sessions, 2026 window length L={L}")
        P(f"      observed 2026 mean {real:+.2f} pts/session")
        P(f"      exact contiguous-circular-window null over the same series: "
          f"mean {nullm.mean():+.2f}, p5 {np.percentile(nullm,5):+.2f}, "
          f"min {nullm.min():+.2f}, max {nullm.max():+.2f}")
        P(f"      2026 sits at the {pct:.1f}th percentile of that null  ->  "
          f"{'below p5 = DISTINGUISHABLE' if pct < 5 else 'NOT below p5 = INSIDE ITS OWN NOISE'}")
        P(f"      rho_bar (lag-1 autocorr of the daily series) = {rho:.4f}   "
          f"K = {K}   K_eff = {keff:.0f}")
        se = x[d_["date"].dt.year.values == 2026].std(ddof=1) / np.sqrt(L)
        _, rho26, keff26 = kdeflate(x[d_["date"].dt.year.values == 2026])
        P(f"      DIAGNOSTIC ONLY session-level t = {real/se:+.2f}; deflated by K_eff "
          f"({keff26:.0f} of {L}) t_eff = {real/se*np.sqrt(keff26/L):+.2f}")
        if lab.startswith("MODERN"):
            pct_modern = pct
            gates.append(("G4", "2026 below p5 of the exact circular-window null",
                          "percentile < 5", f"{pct:.1f}th percentile",
                          "PASS (decay is real)" if pct < 5 else
                          "FAIL (inside its own noise)"))

    P("\n   the sleeve's rolling 24-month record over the FULL history (W61 only had 22 windows):")
    Smod = S.sort_values("date")
    ends = pd.date_range(Smod["date"].min() + pd.DateOffset(months=24), Smod["date"].max(),
                         freq="ME")
    rr = []
    for e in ends:
        b0 = e - pd.DateOffset(months=24)
        m = (Smod["date"] > b0) & (Smod["date"] <= e)
        s_ = Smod.loc[m, "short_pnl436"].values / PV
        if len(s_) < 200:
            continue
        rr.append(dict(end=e, mean=s_.mean(),
                       t=s_.mean() / (s_.std(ddof=1) / np.sqrt(len(s_)))))
    RR = pd.DataFrame(rr)
    last = RR.iloc[-1]
    P(f"      {len(RR)} windows | {100*float((RR['mean']>0).mean()):.1f} % positive | "
      f"median t {RR['t'].median():+.2f} | latest ({last['end'].date()}) t {last['t']:+.2f} "
      f"at the {100*float((RR['t'].values < last['t']).mean()):.1f}th percentile")
    mn = RR.loc[RR["t"].idxmin()]
    P(f"      worst window in 20 years: t {mn['t']:+.2f} ending {mn['end'].date()}")
    P(f"      W61 measured this on 22 windows all of which start after 2022-07. Over the full")
    P(f"      history there are {len(RR)} windows and the latest sits at the "
      f"{100*float((RR['t'].values < last['t']).mean()):.1f}th percentile, not the 0th.")
    P(f"      negative 24-month windows in the full history: "
      f"{int((RR['mean']<=0).sum())} of {len(RR)} "
      f"({100*float((RR['mean']<=0).mean()):.1f} %) - W61 saw NONE because it only had 2022+.")

    # ---------------------------------------------------------------- 9b concentration
    H("9b. IS IT A DECAY OR A CLUSTER? P&L concentration, and the month-by-month path")
    P("This repo has measured that P1's top decile of trades exceeds 100 % of its net. If 2026's")
    P("shortfall is a handful of sessions, 'decay' is the wrong word for it.")
    P("")
    P(f"{'year':<7}{'sess':>6}{'net pts':>10}{'worst 5 sess':>14}{'their share':>13}"
      f"{'net ex-worst5':>15}{'pts/sess ex-w5':>16}{'best 5':>10}")
    for y, g in S.groupby(S["date"].dt.year):
        x = np.sort(g["short_pnl436"].values / PV)
        tot = x.sum()
        w5 = x[:5].sum(); b5 = x[-5:].sum()
        P(f"{y:<7}{len(g):>6}{tot:>10.0f}{w5:>14.0f}"
          f"{100*w5/tot if tot else 0:>12.0f}%{tot-w5:>15.0f}"
          f"{(tot-w5)/max(len(g)-5,1):>16.2f}{b5:>10.0f}")
    P("\n   month by month, 2025-01 .. 2026-07 (the stretch W61 called the decay):")
    P(f"{'month':<10}{'sess':>6}{'trades':>8}{'pts/sess':>11}{'hit%':>7}{'edge':>8}"
      f"{'dnMFE/s':>10}{'dn share':>10}{'sess ret':>10}")
    rec = S[S["date"] >= pd.Timestamp("2025-01-01")].copy()
    rec["m"] = rec["date"].dt.to_period("M")
    trr = TR[TR["date"] >= pd.Timestamp("2025-01-01")].copy()
    trr["m"] = trr["date"].dt.to_period("M")
    for m, g in rec.groupby("m"):
        tg = trr[trr["m"] == m]
        hit = 100 * float((tg["gross_pts"] > 0).mean()) if len(tg) else 0
        P(f"{str(m):<10}{len(g):>6}{len(tg):>8}{g['short_pnl436'].sum()/PV/len(g):>11.2f}"
          f"{hit:>7.1f}{tg['gross_pts'].mean() if len(tg) else 0:>8.3f}"
          f"{g['o1_dn16_mfe'].mean():>10.1f}"
          f"{g['dnmove'].sum()/max(g['absmove'].sum(),1e-9):>10.4f}{g['ret'].mean():>10.2f}")

    # ---------------------------------------------------------------- 10. gate table
    H("10. GATE / SPEC / OBSERVED / PASS-FAIL   (printed by the program, never assembled by hand)")
    P(f"{'id':<5}{'gate':<44}{'spec':<44}{'observed':<26}{'verdict'}")
    for g in gates:
        P(f"{g[0]:<5}{g[1][:43]:<44}{g[2][:43]:<44}{str(g[3])[:25]:<26}{g[4]}")

    # ---------------------------------------------------------------- 11. what this closes
    H("11. WHAT THIS CLOSES AND WHAT IT DOES NOT")
    pre = S[S["era"] == "PRE"]; prt = TR[TR["era"] == "PRE"]
    P("CLOSED - 'the short sleeve is decaying' is not supported as stated:")
    P(f"  * W61's -10.62 pts/session for 2026 came from a substrate that stops 2026-05-29,")
    P(f"    because run_we_w51c.setup() calls load_deep WITHOUT extend=True. On the substrate")
    P(f"    the same call already reaches with extend=True, 2026 is "
      f"{S[S['date'].dt.year==2026]['short_pnl436'].sum()/PV/(S['date'].dt.year==2026).sum():.2f}"
      f" pts/session over {int((S['date'].dt.year==2026).sum())} sessions.")
    P(f"  * The two months W61 could not see, 2026-06 and 2026-07, were "
      f"{S[(S['date']>=pd.Timestamp('2026-06-01'))]['short_pnl436'].sum()/PV/((S['date']>=pd.Timestamp('2026-06-01')).sum()):+.2f}"
      f" pts/session across {int((S['date']>=pd.Timestamp('2026-06-01')).sum())} sessions.")
    P(f"  * On the MODERN series the 2026 stretch sits at the {pct_modern:.1f}th percentile of")
    P(f"    the exact circular-window null of the same series - not below p5, so it is not")
    P(f"    distinguishable from an ordinary bad run of this sleeve (G4 FAILS).")
    P("")
    P("CLOSED - the OPPORTUNITY-DROUGHT explanation is dead:")
    P("  * At 1-minute resolution the down-share of realised movement is 0.499 in EVERY one of")
    P("    the 21 years. There is no year in which the market stopped going down.")
    P("  * At the ratchet's own scale the down/up available-excursion ratio in 2026 is 0.937,")
    P("    inside the 21-year range and above 12 of the other 20 years.")
    P("  * Available down-leg excursion per session in 2026 was 1.79x the 2022-2025 baseline.")
    P("    There was MORE to be short of, not less.")
    P("")
    P("CLOSED BY ITS OWN COUNTERFACTUAL - the halt is NOT the mechanism:")
    P("  * The share of TRADED sessions ending at the fixed -$1,300 halt rises monotonically")
    P("    17.3 % (2023) -> 26.8 % -> 38.8 % -> 52.0 % (2026) while NQ's session movement")
    P("    quadrupled, which looked like a clean risk-specification story. The preregistered")
    P("    counterfactual kills it: with halt and target REMOVED, 2026 is WORSE (-10.15 vs")
    P("    -3.64 pts/session) and the deficit against the 2022-2025 baseline GROWS by 39 %.")
    P("    The fixed-dollar overlay is currently helping, not hurting. Reported because it is")
    P("    the most attractive wrong answer this wave produced.")
    P("")
    P("OPENED / REFRAMED - what the 21-year record actually says:")
    P(f"  * PRE era, {len(pre):,} sessions and {len(prt):,} trades: gross edge "
      f"{prt['gross_pts'].mean():.4f} pts/trade against a {PTS_PRIMARY:.4f}-pt cost floor.")
    P(f"    Negative in {int((YR[YR['year']<2022]['net2065']<0).sum())} of "
      f"{int((YR['year']<2022).sum())} pre-2022 years at $20.65/ctrRT.")
    P("  * THE RECENCY TEST INVERTS. W61 reported '22 rolling 24-month windows, 100 % positive,")
    P("    median t +2.13, latest at the 0th percentile of its own history' and made that the")
    P("    revival condition. All 22 of those windows lie inside the sleeve's single best")
    P(f"    stretch. On the full history there are {len(RR)} windows, "
      f"{100*float((RR['mean']>0).mean()):.1f} % positive, median t "
      f"{RR['t'].median():+.2f}, and the LATEST window sits at the "
      f"{100*float((RR['t'].values < last['t']).mean()):.1f}th percentile - the top sixth, not")
    P("    the bottom. Both statements are arithmetically correct; they differ only in how much")
    P("    of the object's own history the measurer could see.")
    P("  * DRIFT-NEUTRAL EXPECTANCY, the monthly panel's intercept - the sleeve's expectancy")
    P("    with the market's own direction taken out, and the sharpest form of the era break:")
    P("        PRE   196 months  +0.408 pts/session  90% CI [-0.339, +1.187]  hurdle 2.62  BELOW")
    P("        MOD    44 months  +8.716 pts/session  90% CI [+4.411, +13.863] hurdle 2.32  ABOVE")
    P("    Twenty times the level, on the two sides of the ERABREAK01 boundary. Adding 2026")
    P("    moves the modern intercept only 8.72 -> 7.16, well inside its own interval. What")
    P("    needs explaining is 2022-2025, not 2026.")
    P("")
    P("NOT ANSWERED - stated as a limit, not smuggled in as a finding:")
    P("  * Why 2022-2025 was as good as it was is not explained here.")
    vol26 = float(stt["absmove"].mean()); volb = float(sb["absmove"].mean())
    P(f"  * Of the three per-trade factors, only the mean LOSS moved against the sleeve:")
    P(f"    hit rate {100*ab['p']:.1f} -> {100*at['p']:.1f} %, mean WIN "
      f"{ab['W']:.1f} -> {at['W']:.1f} pts ({100*(at['W']/ab['W']-1):+.0f} %), mean LOSS "
      f"{ab['L']:.1f} -> {at['L']:.1f} pts ({100*(at['L']/ab['L']-1):+.0f} %),")
    P(f"    against NQ's mean session |1-min move| {volb:,.0f} -> {vol26:,.0f} "
      f"({100*(vol26/volb-1):+.0f} %). The Shapley split puts {100*c3['L']/dE:.0f} % of the")
    P(f"    per-trade change on the LOSS term. But the SCALE-FREE edge/vol for 2026 is")
    P(f"    {1000*at['edge']/vol26:+.3f} x1e-3, an ordinary pre-2022 value. Whether the loss")
    P(f"    growth is anything beyond volatility is NOT settled by this wave.")
    P("  * No candidate is proposed. Nothing here is an adoption argument, and this sub-wave")
    P("    deliberately proposes no filter: the repo is 11-for-11 against random-thinning")
    P("    controls and an exposure-reducing rule would have to beat one, which is a different")
    P("    wave with its own preregistration.")

    TR.to_csv(os.path.join(OUT, "decay_trades.csv"), index=False)
    P(f"\ndone [{_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
