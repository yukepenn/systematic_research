"""Market internals: build the substrate, then GATE IT ON POWER before any model.

INFORMATION_COVERAGE recorded market internals as "no data". That was true of this REPO and false
of the CONNECTION. $TICK, $TRIN and $VIX are all served at 1-minute across the entire research
window, at zero cost.

The contrast with order flow is the whole point of running this gate:
  order flow  -> 104 of 713 sessions. Coverage is the binding constraint.
  internals   -> EVERY RTH session. Coverage is not the constraint, so the lane can actually be
                 powered where order flow structurally cannot be.

RUN CLASS: DATA ACQUISITION + GATE. No model, no feature, no hypothesis, nothing promoted.
MDE at ~80 % power, two-sided 5 %: 2.80 * sd / sqrt(n), the same yardstick as both order-flow gates.
"""
from __future__ import annotations

import glob
import hashlib
import os

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(HERE, "out", "csv", "internals_1m_bars.csv")
SUB = os.path.join(ROOT, "research", "data_internals")
OUT = os.path.join(HERE, "out")
os.makedirs(SUB, exist_ok=True)
SEAL = "2026-08-01"
MDE_K = 2.80
_fh = open(os.path.join(OUT, "gate.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def main():
    d = pd.read_csv(CSV, parse_dates=["time"])
    d["date"] = d["time"].dt.normalize()

    # HARD seal guard. Nothing at or beyond the seal may enter the substrate.
    sealed = d["date"] >= pd.Timestamp(SEAL)
    if sealed.any():
        P(f"    dropping {int(sealed.sum()):,} rows at/after the {SEAL} seal")
        d = d[~sealed]

    P("=" * 104)
    P("=== MARKET INTERNALS - acquired, then gated. INFORMATION_COVERAGE said 'no data'.")
    P("=" * 104)
    P("")
    rows = []
    for sym, g in d.groupby("symbol"):
        P(f"    {sym:<8} {len(g):>9,} bars   {g['time'].min()}  ->  {g['time'].max()}   "
          f"{g['date'].nunique():>5} sessions")
        rows.append(dict(symbol=sym, bars=len(g), sessions=int(g["date"].nunique()),
                         first=str(g["time"].min()), last=str(g["time"].max())))

    # one parquet per symbol
    man = []
    for sym, g in d.groupby("symbol"):
        safe = sym.replace("$", "").replace("^", "")
        p = os.path.join(SUB, f"{safe}_1m.parquet")
        gg = g[["time", "open", "high", "low", "close"]].reset_index(drop=True)
        gg.to_parquet(p, compression="zstd", index=False)
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        man.append(dict(symbol=sym, file=os.path.basename(p), bars=len(gg),
                        first=str(gg["time"].min()), last=str(gg["time"].max()),
                        mb=round(os.path.getsize(p) / 1e6, 2), sha256=h,
                        src="SWBarExport_v1 via RunStrategyBacktest",
                        note="index, not a traded contract - volume is 0 and must never be "
                             "treated as flow"))
    pd.DataFrame(man).to_csv(os.path.join(SUB, "MANIFEST.csv"), index=False)

    # ---------------------------------------------------------------- the gate
    L = pd.read_csv(glob.glob(os.path.join(ROOT, "runs", "RR_W001*", "out",
                                           "ledger_p1pct.csv"))[0])
    S = L[L["in_scoring_population"] == 1].copy()
    S["ts"] = pd.to_datetime(S["decision_ts"])
    S["date"] = S["ts"].dt.normalize()

    have = set(d[d["symbol"] == "$TICK"]["date"])
    # RTH minutes actually present in the internals series
    lo, hi = pd.Timestamp("09:31").time(), pd.Timestamp("15:59").time()
    in_rth = S["ts"].dt.time.between(lo, hi)
    covered = in_rth & S["date"].isin(have)

    P("")
    P("=" * 104)
    P("=== COVERAGE OF P1 DECISIONS - the question that closed the order-flow lane")
    P("=" * 104)
    n_all = len(S)
    P(f"    P1 scoring entries                       {n_all:>7,}")
    P(f"    ... inside RTH 09:31-15:59               {int(in_rth.sum()):>7,}   "
      f"({100*in_rth.mean():.1f} %)")
    P(f"    ... AND on a session internals cover     {int(covered.sum()):>7,}   "
      f"({100*covered.mean():.1f} %)")
    P("")
    P(f"    order-flow lane, for contrast                141     (6.6 %)")

    P("")
    P("=" * 104)
    P("=== POWER")
    P("=" * 104)
    for target, tname in (("delta_action_value", "session-scoped"),
                          ("delta_total_window", "FULL-HORIZON (primary)")):
        sub = S[covered]
        sd = float(sub[target].std(ddof=1))
        mean = float(sub[target].mean())
        uncond = float(S[target].mean())
        n = len(sub)
        mde = MDE_K * sd / np.sqrt(n)
        P("")
        P(f"    {tname}")
        P(f"      n covered                {n:>8,}")
        P(f"      mean on covered entries  ${mean:>9,.2f}   (unconditional ${uncond:,.2f})")
        P(f"      sd                       ${sd:>9,.2f}")
        P(f"      MDE at ~80 % power       ${mde:>9,.2f}   = {mde/abs(mean):.2f}x the "
          f"covered mean")
        v = "POWERED" if mde <= abs(mean) else "UNDERPOWERED"
        P(f"      VERDICT                  {v}")
        rows.append(dict(target=target, n=n, mean=round(mean, 2), sd=round(sd, 2),
                         mde=round(mde, 2), x_mean=round(mde / abs(mean), 3), verdict=v))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "gate.csv"), index=False)

    P("")
    P("    NOTE ON WHAT THIS DOES AND DOES NOT LICENSE. A passing power gate says a mean-scale")
    P("    effect WOULD BE DETECTABLE. It says nothing about whether one EXISTS. The information")
    P("    test is a separate, preregistered wave and is NOT run here.")
    _fh.close()


if __name__ == "__main__":
    main()
