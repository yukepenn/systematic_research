"""DATAGATE_ORDERFLOW v2 - recompute the power gate against the EXPANDED microstructure substrate.

RUN CLASS: DATA GATE. No model, no feature, no hypothesis. This asks one question only:

    is the order-flow lane still UNDERPOWERED now that the substrate has grown?

DATAGATE_ORDERFLOW_20260827 answered it at 48 sessions: 71 of 2,131 P1 entries (3.3 %), MDE
$564/entry = 4.0x the unconditional mean, UNDERPOWERED. ORDERFLOW_EXPAND has since taken the
substrate to ~104 distinct sessions, 98 of them with full quote coverage.

Directive s18 is explicit that this comes BEFORE any model: "Do a POWER GATE before building
models. If still underpowered: keep it CLOSED-BY-DATA. Do not force a wave."

TWO LANES, KEPT SEPARATE, because they rest on different session sets:
  signed flow  -> needs Last only        -> the full union of both substrates
  BBO / quote  -> needs Last+Bid+Ask     -> only quote-complete sessions

MDE at ~80 % power, two-sided 5 %:  2.80 * sd / sqrt(n).
Verified against the v1 gate: n=71, sd=$1,697 -> $564. Reproduces exactly.
"""
from __future__ import annotations

import glob
import os
import re

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)
_fh = open(os.path.join(OUT, "gate.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


MDE_K = 2.80          # (1.96 + 0.84), two-sided 5 %, ~80 % power


def sessions_from(dirpath, pat=r"^s(\d{8})\.parquet$"):
    out = set()
    if not os.path.isdir(dirpath):
        return out
    for f in os.listdir(dirpath):
        m = re.match(pat, f)
        if m:
            g = m.group(1)
            out.add(f"{g[:4]}-{g[4:6]}-{g[6:8]}")
    return out


def main():
    # ---------------------------------------------------------------- substrates
    old = sessions_from(os.path.join(ROOT, "research", "scalping_lab",
                                     "substrate", "raw", "NQ"))
    MV2 = os.path.join(ROOT, "research", "data_microstructure_v2", "MANIFEST.csv")
    new_m = pd.read_csv(MV2)
    new = set(new_m["session_date"])

    # quote-complete classification, hour-granularity truth
    T = pd.read_csv(os.path.join(ROOT, "runs", "ORDERFLOW_EXPAND_20260827",
                                 "out", "bbo_hourly_truth.csv"))
    full_q = set(T[T["cls"] == "FULL"]["date"])

    union = old | new
    union_q = union & full_q

    # ---------------------------------------------------------------- ledger
    L = pd.read_csv(glob.glob(os.path.join(ROOT, "runs", "RR_W001*", "out",
                                           "ledger_p1pct.csv"))[0])
    S = L[L["in_scoring_population"] == 1].copy()
    S["session_date"] = S["session_date"].astype(str)

    X = pd.read_csv(glob.glob(os.path.join(ROOT, "runs", "RR_W001*", "out",
                                           "ledger_xm.csv"))[0])
    X["session_date"] = X["session_date"].astype(str)

    P("=" * 108)
    P("=== DATAGATE_ORDERFLOW v2 - has the expanded substrate changed the verdict?")
    P("=== POWER ONLY. No model, no feature, no hypothesis, nothing promoted.")
    P("=" * 108)
    P("")
    P(f"    old substrate (scalping_lab)            {len(old):>5} sessions")
    P(f"    new substrate (data_microstructure_v2)  {len(new):>5} sessions")
    P(f"    overlap                                 {len(old & new):>5}")
    P(f"    UNION                                   {len(union):>5} sessions")
    P(f"    ... of which QUOTE-COMPLETE             {len(union_q):>5} sessions")

    n_all = len(S)
    tot_sess = S["session_date"].nunique()

    # ---------------------------------------------------------------- the gate
    for target, tname in (("delta_action_value", "session-scoped"),
                          ("delta_total_window", "FULL-HORIZON (primary)")):
        sd = float(S[target].std(ddof=1))
        mean = float(S[target].mean())
        P("")
        P("=" * 108)
        P(f"=== TARGET: {target}  ({tname})")
        P("=" * 108)
        P(f"    unconditional mean  ${mean:>10,.2f}    sd ${sd:>10,.2f}    n {n_all:,}")
        P("")
        P(f"    {'lane':<34}{'sessions':>9}{'entries':>9}{'share':>9}"
          f"{'MDE/entry':>12}{'x mean':>9}  verdict")
        P("    " + "-" * 100)
        rows = []
        for lane, ss in (("v1 gate - 48-session substrate", old),
                         ("signed flow - UNION (Last)", union),
                         ("BBO / quote - quote-complete", union_q),
                         ("full window (reference)", set(S["session_date"]))):
            sub = S[S["session_date"].isin(ss)]
            n = len(sub)
            if n < 2:
                P(f"    {lane:<34}{len(ss & set(S['session_date'])):>9}{n:>9}"
                  f"{'-':>9}{'-':>12}{'-':>9}  TOO FEW")
                continue
            mde = MDE_K * sd / np.sqrt(n)
            ratio = mde / abs(mean) if mean else np.inf
            verdict = "POWERED" if ratio <= 1.0 else "UNDERPOWERED"
            P(f"    {lane:<34}{len(ss & set(S['session_date'])):>9}{n:>9}"
              f"{100*n/n_all:>8.1f}%${mde:>11,.0f}{ratio:>9.2f}  {verdict}")
            rows.append(dict(target=target, lane=lane, sessions=len(ss & set(S["session_date"])),
                             entries=n, share=round(100 * n / n_all, 2),
                             mde=round(mde, 2), x_mean=round(ratio, 3), verdict=verdict))
        pd.DataFrame(rows).to_csv(os.path.join(OUT, f"gate_{target}.csv"), index=False)

    # ---------------------------------------------------------------- XM
    P("")
    P("=" * 108)
    P("=== XM decisions")
    P("=" * 108)
    for lane, ss in (("v1 gate - 48-session", old), ("UNION", union),
                     ("quote-complete", union_q)):
        n = int(X["session_date"].isin(ss).sum())
        P(f"    {lane:<34}{n:>6} of {len(X):,} XM decisions   ({100*n/len(X):.1f} %)")

    P("")
    P("=" * 108)
    P("=== WHAT CHANGED, AND WHAT DID NOT")
    P("=" * 108)
    sd = float(S["delta_total_window"].std(ddof=1))
    n_old = len(S[S["session_date"].isin(old)])
    n_un = len(S[S["session_date"].isin(union)])
    n_q = len(S[S["session_date"].isin(union_q)])
    P(f"    entries: {n_old} -> {n_un} (signed flow), {n_q} (quote-based)")
    if n_old > 1 and n_q > 1:
        P(f"    MDE shrinks by sqrt(n) only: x{np.sqrt(n_un/n_old):.2f} (flow), "
          f"x{np.sqrt(n_q/n_old):.2f} (quote)")
    P(f"    total sessions in the modern window: {tot_sess:,}")
    P("")
    P("    A larger substrate reduces MDE as 1/sqrt(n). It does NOT change the per-entry sd,")
    P("    which is what makes this lane hard. The verdict above is the whole finding.")

    # ------------------------------------------------------------ the CEILING question
    # Not "how much more data would help?" but "is there ENOUGH DATA IN EXISTENCE?"
    P("")
    P("=" * 108)
    P("=== THE CEILING - what would FULL coverage of every session actually buy?")
    P("=== This is the question acquisition has to answer, and it is not the same as 'more data'.")
    P("=" * 108)
    per_sess = n_all / tot_sess
    P(f"    P1 scoring entries per session (mean)   {per_sess:.2f}")
    P(f"    sessions in the modern window           {tot_sess:,}")
    P(f"    entries at 100 % session coverage       {n_all:,}")
    P("")
    P(f"    {'target':<26}{'sd':>10}{'mean':>10}{'n needed':>11}{'n at 100%':>11}"
      f"{'sessions needed':>17}  reachable?")
    P("    " + "-" * 100)
    for target in ("delta_action_value", "delta_total_window"):
        sd_t = float(S[target].std(ddof=1))
        m_t = abs(float(S[target].mean()))
        need = (MDE_K * sd_t / m_t) ** 2
        sess_need = need / per_sess
        ok = "YES" if need <= n_all else "NO - NOT ENOUGH DATA EXISTS"
        P(f"    {target:<26}${sd_t:>9,.0f}${m_t:>9,.0f}{need:>11,.0f}{n_all:>11,}"
          f"{sess_need:>17,.0f}  {ok}")
    P("")
    P("    'n needed' = the sample at which MDE falls to 1.0x the unconditional mean, i.e. the")
    P("    point where an effect the SIZE OF THE MEAN becomes detectable at ~80 % power.")
    P("")
    P("    >>> For the FULL-HORIZON primary target this is NOT a coverage problem. Even complete")
    P("    >>> order-flow coverage of EVERY session in the window leaves the MDE above the mean.")
    P("    >>> Acquisition cannot rescue that. Only a LARGER effect than the mean is reachable.")
    _fh.close()


if __name__ == "__main__":
    main()
