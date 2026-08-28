"""PORTFOLIO B - arithmetic truth vs CAUSAL portfolio truth, and the incumbent adjudication.

BOUNDED DIAGNOSTIC (owner s10). Not the product.

THE QUESTION IS NO LONGER "is $2,012 a cost error?" It is not - that was retracted. The question is
HOW MUCH OF $2,012 DEPENDS ON (a) IN-SAMPLE WEIGHTING and (b) BEST-OF-SIX SELECTION.

STEP 1  reproduce legacy B EXACTLY, or stop.
STEP 2  ONE predeclared causal counterpart. No weight-rule search.
            expanding inverse-vol, volatility from weeks STRICTLY BEFORE the allocation week,
            one-week lag, warmup 26 weeks DECLARED HERE before any result.
STEP 3  quantify WEIGHTING OPTIMISM and SELECTION OPTIMISM separately.
STEP 4  the already-preregistered fixed-window incumbent adjudication.

Frozen B is NOT rewritten. The output is an uncertainty adjustment and an evidence
classification, not a new optimised portfolio.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)
TARGET_DD = 20245.0
WARMUP = 26                 # weeks. DECLARED BEFORE RESULTS.
WINDOWS = [13, 26, 52, 104]
_fh = open(os.path.join(OUT, "reconcile_b.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def maxdd(x):
    c = np.cumsum(x)
    return float(np.max(np.maximum.accumulate(c) - c))


def summarize(x):
    x = np.asarray(x, float)
    dd = maxdd(x)
    k = TARGET_DD / dd if dd > 0 else np.nan
    sd = x.std(ddof=1)
    return dict(n=len(x), weekly=float(x.mean()), maxdd=dd, k=k,
                fixdd=float(x.mean() * k) if dd > 0 else np.nan,
                poswk=100 * float((x > 0).mean()),
                t=float(x.mean() / (sd / np.sqrt(len(x)))) if sd > 0 else np.nan,
                cvar5=float(np.mean(np.sort(x)[:max(1, len(x) // 20)])))


def main():
    d = pd.read_csv(os.path.join(ROOT, "runs/WE_W110_XMDIVERSE/out/weekly.csv"))
    p1, xm = d["p1"].values.astype(float), d["xm"].values.astype(float)
    n = len(p1)

    P("=" * 104)
    P("=== PORTFOLIO B - arithmetic truth vs causal portfolio truth")
    P("=" * 104)
    P(f"    canonical ISO-week series, {n} weeks, {d['week'].iloc[0]} -> {d['week'].iloc[-1]}")

    # ---------------------------------------------------- STEP 1: reproduce legacy B EXACTLY
    s1, s2 = p1.std(ddof=1), xm.std(ddof=1)                 # FULL-SAMPLE, IN-SAMPLE
    w1 = (1 / s1) / (1 / s1 + 1 / s2)
    w2 = 1 - w1
    legacy = w1 * p1 + w2 * xm
    L = summarize(legacy)
    P("")
    P("=== STEP 1  REPRODUCE LEGACY B (full-sample inverse-vol, applied in-sample)")
    P(f"    weights  P1 {w1:.6f}   XM {w2:.6f}      (published 0.473097 / 0.526903)")
    P(f"    {'':<22}{'reproduced':>16}{'published':>16}{'diff':>12}")
    for lab, got, pub in (("weekly mean", L["weekly"], 1141.678278),
                          ("maxDD", L["maxdd"], 11489.404203),
                          ("fixed-DD weekly", L["fixdd"], 2011.703681),
                          ("t", L["t"], 4.903442),
                          ("positive weeks %", L["poswk"], 59.154930)):
        P(f"    {lab:<22}{got:>16,.6f}{pub:>16,.6f}{got-pub:>12.6f}")
    ok = (abs(L["weekly"] - 1141.678278) < 1e-4 and abs(L["maxdd"] - 11489.404203) < 1e-3
          and abs(L["fixdd"] - 2011.703681) < 1e-3)
    P(f"    >>> {'EXACT REPRODUCTION' if ok else '*** DOES NOT REPRODUCE - STOP ***'}")
    assert ok, "legacy Portfolio B did not reproduce; do not proceed to the causal counterpart"

    # ---------------------------------------------------- STEP 2: ONE causal counterpart
    P("")
    P("=== STEP 2  CAUSAL COUNTERPART - expanding inverse-vol, prior weeks only, 1-week lag")
    P(f"    warmup {WARMUP} weeks, declared before results. NO weight-rule search.")
    causal = np.full(n, np.nan)
    wser = np.full(n, np.nan)
    for t in range(n):
        if t < WARMUP:
            continue
        a, b = p1[:t], xm[:t]                    # STRICTLY BEFORE week t
        sa, sb = a.std(ddof=1), b.std(ddof=1)
        if not (sa > 0 and sb > 0):
            continue
        u = (1 / sa) / (1 / sa + 1 / sb)
        wser[t] = u
        causal[t] = u * p1[t] + (1 - u) * xm[t]
    m = ~np.isnan(causal)
    C = summarize(causal[m])
    # legacy restricted to the SAME weeks, so the comparison is like-for-like
    Lm = summarize(legacy[m])
    P(f"    causal weeks used {m.sum()} of {n}   P1 weight: mean {np.nanmean(wser):.4f}  "
      f"range [{np.nanmin(wser):.4f}, {np.nanmax(wser):.4f}]")
    P("")
    P(f"    {'':<24}{'LEGACY (in-sample)':>22}{'CAUSAL (lagged)':>20}{'difference':>14}")
    P("    " + "-" * 80)
    for lab, key in (("weekly mean $", "weekly"), ("maxDD $", "maxdd"),
                     ("FIXED-DD $/week", "fixdd"), ("t", "t"),
                     ("positive weeks %", "poswk"), ("CVaR5 $", "cvar5")):
        P(f"    {lab:<24}{Lm[key]:>22,.2f}{C[key]:>20,.2f}{C[key]-Lm[key]:>14,.2f}")
    weight_optimism = Lm["fixdd"] - C["fixdd"]
    P("")
    P(f"    >>> WEIGHTING OPTIMISM = ${weight_optimism:,.2f}/week "
      f"({100*weight_optimism/max(Lm['fixdd'],1e-9):.1f} % of the legacy figure)")
    P("    >>> on the SAME weeks, so this isolates the weighting rule and nothing else.")

    # ---------------------------------------------------- STEP 3: selection optimism
    P("")
    P("=== STEP 3  SELECTION OPTIMISM - best-of-six, from W103's own table")
    cmb = pd.read_csv(os.path.join(ROOT, "runs/WE_W103_CONSOLIDATE/out/combinations.csv"))
    inv = cmb[cmb["name"].str.startswith("INV-VOL")].copy()
    inv = inv.sort_values("fixdd", ascending=False)
    P(f"    {'combination':<38}{'fixed-DD $/wk':>16}")
    P("    " + "-" * 56)
    for _, r in inv.iterrows():
        star = "  <- PREREGISTERED PRIMARY" if "PRIMARY" in r["name"] else ""
        star += "  <- SELECTED" if r["fixdd"] == inv["fixdd"].max() else ""
        P(f"    {r['name'].replace('  *PRIMARY*',''):<38}{r['fixdd']:>16,.2f}{star}")
    sel = float(inv["fixdd"].max())
    prim = float(inv[inv["name"].str.contains("PRIMARY")]["fixdd"].iloc[0])
    P("")
    P(f"    selected (P1+XM)                ${sel:,.2f}")
    P(f"    preregistered primary           ${prim:,.2f}")
    P(f"    >>> SELECTION OPTIMISM (visible) = ${sel-prim:,.2f}/week "
      f"({100*(sel-prim)/prim:.1f} % above the object the spec named)")
    P(f"    >>> spread across the six inverse-vol combinations: "
      f"${inv['fixdd'].min():,.2f} .. ${inv['fixdd'].max():,.2f}")
    P("    >>> This is the OBSERVABLE part only. The true selection premium is at least this,")
    P("    >>> because the six were themselves chosen from a larger space of possible baskets.")

    # ---------------------------------------------------- STEP 4: incumbent adjudication
    P("")
    P("=" * 104)
    P("=== STEP 4  INCUMBENT ADJUDICATION - fixed windows, declared in spec_v2.yaml")
    P("=== BURNED evidence. Real, but not confirmation. A 13-week result may not decide anything.")
    P("=" * 104)
    kP1 = TARGET_DD / maxdd(p1)
    objs = {"PCT (P1)": p1, "XM": xm, "PCT+XM legacy": legacy, "PCT+XM causal": causal}
    P(f"    {'object':<16}{'window':>9}{'n':>5}{'$/wk raw':>11}{'fixDD $/wk':>12}"
      f"{'maxDD $':>11}{'pos %':>8}{'t':>7}")
    P("    " + "-" * 79)
    rows = []
    for nm, v in objs.items():
        for w in WINDOWS + [n]:
            x = v[-w:]
            x = x[~np.isnan(x)]
            if len(x) < 5:
                continue
            s = summarize(x)
            lab = "FULL" if w >= n else f"last {w}w"
            P(f"    {nm:<16}{lab:>9}{s['n']:>5}{s['weekly']:>11,.0f}{s['fixdd']:>12,.0f}"
              f"{s['maxdd']:>11,.0f}{s['poswk']:>7.1f}%{s['t']:>7.2f}")
            rows.append(dict(object=nm, window=lab, **s))
        P("    " + "-" * 79)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "adjudication.csv"), index=False)

    # marginal value of XM, on ONE risk denominator
    P("")
    P("=== MARGINAL VALUE OF XM  (causal weighting, fixed-DD, same weeks)")
    P(f"    {'window':>9}{'P1 alone':>12}{'P1+XM causal':>15}{'marginal':>12}"
      f"{'rho':>8}{'XM | P1<0':>12}")
    P("    " + "-" * 68)
    for w in WINDOWS + [n]:
        sl = slice(n - w, n) if w < n else slice(0, n)
        a, b, c = p1[sl], xm[sl], causal[sl]
        good = ~np.isnan(c)
        if good.sum() < 5:
            continue
        sa = summarize(a[good])
        sc = summarize(c[good])
        rho = float(np.corrcoef(a[good], b[good])[0, 1])
        lose = a[good] < 0
        cond = float(np.mean(b[good][lose]) * kP1) if lose.sum() > 1 else np.nan
        lab = "FULL" if w >= n else f"last {w}w"
        P(f"    {lab:>9}{sa['fixdd']:>12,.0f}{sc['fixdd']:>15,.0f}"
          f"{sc['fixdd']-sa['fixdd']:>12,.0f}{rho:>8.3f}{cond:>12,.0f}")
    P("")
    P("    NOTE: 'XM | P1<0' is XM's mean in P1's losing weeks, scaled by P1's own k so the")
    P("    figures are comparable across rows. It is a CONDITIONAL MEAN, not a portfolio result.")
    _fh.close()


if __name__ == "__main__":
    main()
