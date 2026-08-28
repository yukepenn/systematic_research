"""TSMOM-TAIL-H1 - does the FROZEN 252d TSMOM object earn its place as a PORTFOLIO TAIL
DIVERSIFIER on the one-sided-blind 2023-01-01 -> 2026-05-30 window?

THIS IS NOT V2.1. The trading object is EXACTLY the frozen V2: 21 CORE roots, sign(R252), same
roll machinery, eligibility, vol scaling, rebalance, long/short symmetry, costs, commission,
PRIMARY/STRESS assumptions and fractional research sizing. NO strategy parameter changes.

ONLY THE SCIENTIFIC CLAIM CHANGES.
    V2  claim: "a sufficiently stable standalone slow-trend premium."      FAILED (G3, 2 of 4 yrs)
    H1  claim: "valuable portfolio diversification / tail behaviour DESPITE uneven yearly returns."

*** EVIDENCE PROVENANCE, permanent, attached to every number below ***
    HYPOTHESIS MOTIVATED BY THE FAILED 2019-2022 VALIDATION
    2019-2022 IS DISCOVERY FOR THIS NEW CLAIM, NOT EVIDENCE
    NOT A CLEAN EX-ANTE HYPOTHESIS

*** AND THE HOLDOUT IS ONE-SIDED ***
    The TSMOM leg is genuinely blind on 2023-2026: its outcomes have never been read.
    The INCUMBENT leg is NOT - P1/XM were discovered using modern data covering much of this
    window. So this is a ONE-SIDED BLIND TSMOM HISTORICAL HOLDOUT. It is NOT prospective, NOT a
    fully pristine portfolio out-of-sample, and NOT forward evidence. That asymmetry travels with
    every result here.
"""
from __future__ import annotations

import hashlib
import os
import sys

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
MM = os.path.join(ROOT, "research", "multi_market")
sys.path.insert(0, os.path.join(MM, "src"))
import ncd_day as N                                                        # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)

# ---- INHERITED FROM FROZEN V2, UNCHANGED
VOL_LOOKBACK, TARGET_RISK_USD, COMMISSION_RT, HORIZON = 63, 1000.0, 4.36, 252
# ---- H1 WINDOW
HOLD_START, HOLD_END = "2023-01-01", "2026-05-30"
SEAL = "2026-08-01"
# ---- ALLOCATOR, declared in SPEC.md before this ran
WARMUP_WK = 26            # same constant already declared in PORTFOLIO_B_RECONCILIATION
TARGET_DD = 20245.0
BOOT_B, BOOT_SEED = 20000, 20260828
_fh = open(os.path.join(OUT, "tail_h1.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def maxdd(x):
    c = np.cumsum(np.asarray(x, float))
    return float(np.max(np.maximum.accumulate(c) - c))


def fixdd(x):
    m = maxdd(x)
    return float(np.mean(x) * TARGET_DD / m) if m > 0 else np.nan


def es5(x):
    x = np.sort(np.asarray(x, float))
    return float(x[:max(1, len(x) // 20)].mean())


def tsmom_weekly():
    """Frozen V2 object, run continuously; aggregated to ISO week on session date."""
    r = pd.read_parquet(os.path.join(MM, "out", "economic_returns.parquet"))
    r = r.sort_values(["root", "date"]).reset_index(drop=True)
    assert pd.Timestamp(r["date"].max()) < pd.Timestamp(SEAL), "SEAL VIOLATION"
    tv = {}
    for root in r["root"].unique():
        x = N.read_contract(N.contract_id(root, N.CYCLES[root][0], 2012))
        tv[root] = float(x["tick_size"].iloc[0]) * N.PV[root] if len(x) else np.nan
    r["tick_usd"] = r["root"].map(tv)
    out = []
    for root, g in r.groupby("root", sort=False):
        g = g.sort_values("date").copy()
        cum = g["ret_usd"].cumsum()
        g["score"] = np.sign(cum - cum.shift(HORIZON))
        g.loc[g.index[:HORIZON], "score"] = np.nan
        g["score"] = g["score"].shift(1)
        g["vol"] = g["ret_usd"].rolling(VOL_LOOKBACK).std().shift(1)
        out.append(g)
    d = pd.concat(out, ignore_index=True)
    res = {}
    for lab, tk in (("PRIMARY", 1.0), ("STRESS", 2.0)):
        x = d[d["eligible"] & d["score"].notna() & d["vol"].notna() & (d["vol"] > 0)].copy()
        x["inv_vol"] = 1.0 / x["vol"]
        nsec = x.groupby("date")["sector"].transform("nunique")
        nroot = x.groupby(["date", "sector"])["root"].transform("nunique")
        x["q"] = x["score"] * (TARGET_RISK_USD / nsec / nroot) * x["inv_vol"]
        x = x.sort_values(["root", "date"])
        x["q_prev"] = x.groupby("root")["q"].shift(1).fillna(0.0)
        side = tk * x["tick_usd"] + COMMISSION_RT / 2.0
        x["cost"] = (x["q"] - x["q_prev"]).abs() * side + \
                    x["rolled"] * 2.0 * x["q_prev"].abs() * side
        x["net"] = x["q_prev"] * x["ret_usd"] - x["cost"]
        daily = x.groupby("date")["net"].sum()
        iso = pd.DatetimeIndex(daily.index).isocalendar()
        wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
        res[lab] = pd.Series(daily.values, index=wk).groupby(level=0).sum()
        if lab == "PRIMARY":
            res["_detail"] = x
    return res


def causal_ivol(streams, warmup=WARMUP_WK):
    """ONE frozen allocator: expanding inverse-vol from weeks STRICTLY BEFORE the allocation week,
    one-week lag, warmup declared before results. No optimizer, no weight search, no future vol."""
    M = np.column_stack(streams)
    n, k = M.shape
    out = np.full(n, np.nan)
    W = np.full((n, k), np.nan)
    for t in range(warmup, n):
        sd = M[:t].std(axis=0, ddof=1)
        if not np.all(sd > 0):
            continue
        w = (1 / sd) / np.sum(1 / sd)
        W[t] = w
        out[t] = float(np.dot(w, M[t]))
    return out, W


def block_boot_lb(x, B=BOOT_B, seed=BOOT_SEED, q=5.0):
    """Dependence-aware circular block bootstrap; one-sided lower bound on the mean.
    Block length = round(n^(1/3)), the same rule FWD_BOOTSTRAP_V2 uses. Frozen before the read."""
    x = np.asarray(x, float)
    n = len(x)
    L = max(2, int(round(n ** (1 / 3))))
    rng = np.random.default_rng(seed)
    xt = np.concatenate([x, x])
    nb = int(np.ceil(n / L))
    st = rng.integers(0, n, size=(B, nb))
    idx = (st[:, :, None] + np.arange(L)[None, None, :]).reshape(B, -1)[:, :n]
    means = xt[idx].mean(axis=1)
    return float(np.percentile(means, q)), L


def main():
    P("=" * 104)
    P("=== TSMOM-TAIL-H1  -  portfolio tail role of the FROZEN 252d object")
    P(f"=== ONE-SIDED BLIND holdout {HOLD_START} -> {HOLD_END}")
    P("=" * 104)
    P("    PROVENANCE: hypothesis MOTIVATED BY the failed 2019-2022 validation. 2019-2022 is")
    P("    DISCOVERY for this claim. The TSMOM leg is blind here; the INCUMBENT leg is not.")
    P(f"    THIS FILE sha256 {hashlib.sha256(open(os.path.abspath(__file__),'rb').read()).hexdigest()}")

    T = tsmom_weekly()
    inc = pd.read_csv(os.path.join(ROOT, "runs/WE_W110_XMDIVERSE/out/weekly.csv"))
    inc = inc.set_index("week")

    common = [w for w in inc.index if w in T["PRIMARY"].index]
    P(f"\n    incumbent weeks {len(inc)}   TSMOM weeks {len(T['PRIMARY'])}   common {len(common)}")
    p1 = inc.loc[common, "p1"].values.astype(float)
    xm = inc.loc[common, "xm"].values.astype(float)
    ts = T["PRIMARY"].loc[common].values.astype(float)
    tsS = T["STRESS"].loc[common].values.astype(float)
    wks = np.array(common)

    # holdout mask on ISO week -> use the Monday of each ISO week
    yr = np.array([int(w[:4]) for w in wks])
    wn = np.array([int(w[-2:]) for w in wks])
    dts = pd.to_datetime([f"{a}-W{b:02d}-1" for a, b in zip(yr, wn)], format="%G-W%V-%u")
    hold = (dts >= pd.Timestamp(HOLD_START)) & (dts <= pd.Timestamp(HOLD_END))
    assert dts[hold].max() <= pd.Timestamp(HOLD_END), "HOLDOUT BOUND VIOLATION"
    P(f"    holdout weeks {int(hold.sum())}   {wks[hold][0]} -> {wks[hold][-1]}")

    # ---- allocator uses ALL prior weeks (including pre-holdout) but never future weeks
    incum, Wi = causal_ivol([p1, xm])
    comb, Wc = causal_ivol([p1, xm, ts])
    combS, _ = causal_ivol([p1, xm, tsS])
    p1ts, _ = causal_ivol([p1, ts])
    ok = hold & ~np.isnan(incum) & ~np.isnan(comb)
    P(f"    evaluated holdout weeks (allocator warm) {int(ok.sum())}")

    A, Bc, BS, PT = incum[ok], comb[ok], combS[ok], p1ts[ok]
    TS, TSs = ts[ok], tsS[ok]

    P("")
    P("=" * 104)
    P("=== STANDALONE AND PORTFOLIO ECONOMICS ON THE HOLDOUT")
    P("=" * 104)
    P(f"    {'object':<26}{'$/wk':>10}{'fixDD $/wk':>13}{'maxDD':>11}{'ES5%':>10}"
      f"{'pos wk':>9}{'t':>7}")
    P("    " + "-" * 86)
    for nm, v in (("TSMOM standalone", TS), ("INCUMBENT P1+XM", A),
                  ("INCUMBENT + TSMOM", Bc), ("P1 + TSMOM (secondary)", PT)):
        sd = v.std(ddof=1)
        P(f"    {nm:<26}{v.mean():>10,.0f}{fixdd(v):>13,.0f}{maxdd(v):>11,.0f}{es5(v):>10,.0f}"
          f"{100*np.mean(v>0):>8.1f}%{v.mean()/(sd/np.sqrt(len(v))):>7.2f}")

    d_fix = fixdd(Bc) - fixdd(A)
    d_fixS = fixdd(BS) - fixdd(A)
    P("")
    P(f"    PRIMARY  delta fixed-DD $/week = {d_fix:+,.2f}")
    P(f"    STRESS   delta fixed-DD $/week = {d_fixS:+,.2f}")

    # ---- paired weekly inference on the fixed-DD-normalised difference
    kA = TARGET_DD / maxdd(A)
    kB = TARGET_DD / maxdd(Bc)
    paired = Bc * kB - A * kA
    lb, L = block_boot_lb(paired)
    P("")
    P("=== H1-G2 dependence-aware paired weekly inference (frozen form)")
    P(f"    paired weekly (combined - incumbent) at each object's OWN fixed-DD normalisation")
    P(f"    mean ${paired.mean():+,.2f}/wk   circular block bootstrap L={L}, B={BOOT_B:,}")
    P(f"    one-sided lower 95 % bound  ${lb:+,.2f}")

    # ---- tail behaviour
    dec = np.percentile(A, 10)
    worst = A <= dec
    P("")
    P("=" * 104)
    P("=== TAIL BEHAVIOUR - the actual H1 claim")
    P("=" * 104)
    P(f"    incumbent worst-decile weeks: {int(worst.sum())} of {len(A)}  (threshold ${dec:,.0f})")
    P(f"    mean TSMOM in those weeks              ${TS[worst].mean():>10,.2f}   <- H1-G4 PRIMARY")
    P(f"    mean TSMOM when incumbent < 0          ${TS[A<0].mean():>10,.2f}")
    P(f"    rho(incumbent, TSMOM) all weeks        {np.corrcoef(A,TS)[0,1]:>10.3f}")
    if (A < 0).sum() > 2:
        P(f"    rho | incumbent < 0                    "
          f"{np.corrcoef(A[A<0],TS[A<0])[0,1]:>10.3f}")
    P(f"    incumbent ES5%                         ${es5(A*kA):>10,.2f}  (fixed-DD normalised)")
    P(f"    combined  ES5%                         ${es5(Bc*kB):>10,.2f}  (fixed-DD normalised)")
    P(f"    ES improvement                         ${es5(Bc*kB)-es5(A*kA):>+10,.2f}   <- diagnostic")
    ov = np.mean(TS[worst] < 0)
    P(f"    worst-decile overlap (TSMOM also <0)   {100*ov:>10.1f} %")
    P(f"    combined maxDD (fixed-DD normalised)   ${maxdd(Bc*kB):>10,.0f}  vs incumbent "
      f"${maxdd(A*kA):,.0f}")

    P("")
    P("=== yearly (holdout)")
    hy = pd.Series(TS, index=dts[ok]).groupby(pd.DatetimeIndex(dts[ok]).year).agg(["sum", "size"])
    P("    TSMOM standalone by year")
    P("    " + hy.to_string().replace("\n", "\n    "))

    # ---- GATES
    P("")
    P("=" * 104)
    P("=== PREREGISTERED H1 GATES (SPEC.md, frozen before this ran)")
    P("=" * 104)
    g = [("H1-G1 delta fixed-DD $/wk > 0", d_fix > 0, f"{d_fix:+,.2f}"),
         ("H1-G2 paired boot lower 95 % > 0", lb > 0, f"{lb:+,.2f}"),
         ("H1-G3 delta fixed-DD > 0 at STRESS", d_fixS > 0, f"{d_fixS:+,.2f}"),
         ("H1-G4 mean TSMOM in worst decile > 0", TS[worst].mean() > 0,
          f"{TS[worst].mean():+,.2f}"),
         ("H1-G5 combined ES5% not worse", es5(Bc * kB) >= es5(A * kA),
          f"{es5(Bc*kB)-es5(A*kA):+,.2f}")]
    P(f"    {'gate':<40}{'observed':>16}   verdict")
    P("    " + "-" * 70)
    for nm, okg, obs in g:
        P(f"    {nm:<40}{obs:>16}   {'PASS' if okg else '*** FAIL ***'}")
    allp = all(x[1] for x in g)
    P("")
    if allp:
        P("    ALL GATES PASS ->")
        P("    'Frozen 252d TSMOM is SUPPORTED as a HISTORICAL TAIL-DIVERSIFIER CANDIDATE under a")
        P("     ONE-SIDED-BLIND holdout; clean portfolio confirmation still requires prospective")
        P("     time.'  It is NOT 'validated alpha'. Freeze it and enter prospective shadow.")
    else:
        P("    *** H1 FAILS ***")
        P("    TSMOM is CLOSED for this campaign: the steady-premium role failed (V2-G3) and the")
        P("    tail-diversifier role failed here. Do not invent H2. Do not spend more history on")
        P("    another TSMOM formulation. Move on.")
    pd.DataFrame(dict(week=wks[ok], incumbent=A, combined=Bc, tsmom=TS,
                      p1_tsmom=PT)).to_csv(os.path.join(OUT, "h1_weekly.csv"), index=False)
    _fh.close()


if __name__ == "__main__":
    main()
