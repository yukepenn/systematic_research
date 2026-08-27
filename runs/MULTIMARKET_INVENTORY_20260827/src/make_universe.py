"""Build the probe list for the multi-market INVENTORY (directive s11).

This is an INVENTORY, not the substrate. It answers "which markets are actually usable, and how
deep does each go?" by sampling a few contracts per root across the years, rather than downloading
every contract. Building the full continuous substrate is the NEXT step and it should not start
until this says which markets are worth the effort.

Measured per market, per directive s11: available history, contract continuity, liquidity (volume),
missing intervals. Roll handling and session calendars come with the substrate build, not here.

Contract cycles are the standard listed ones, not guesses:
    equity index / rates / FX  -> H M U Z            (Mar Jun Sep Dec)
    CL, NG                     -> all twelve
    GC                         -> G J M Q V Z        (Feb Apr Jun Aug Oct Dec)
    SI, HG, ZC, ZW             -> H K N U Z          (Mar May Jul Sep Dec)
    ZS                         -> F H K N Q U X
"""
from __future__ import annotations

import json
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)

QUARTERLY = [3, 6, 9, 12]
ALL12 = list(range(1, 13))
GC_C = [2, 4, 6, 8, 10, 12]
METAL = [3, 5, 7, 9, 12]
SOY = [1, 3, 5, 7, 8, 9, 11]

UNIVERSE = [
    # (root, sector, cycle, note)
    ("ES", "equity_index", QUARTERLY, "S&P 500"),
    ("NQ", "equity_index", QUARTERLY, "Nasdaq 100 - the incumbent's market"),
    ("RTY", "equity_index", QUARTERLY, "Russell 2000"),
    ("YM", "equity_index", QUARTERLY, "Dow"),
    ("ZT", "rates", QUARTERLY, "2y note"),
    ("ZF", "rates", QUARTERLY, "5y note"),
    ("ZN", "rates", QUARTERLY, "10y note"),
    ("ZB", "rates", QUARTERLY, "30y bond"),
    ("6E", "fx", QUARTERLY, "EUR"),
    ("6J", "fx", QUARTERLY, "JPY"),
    ("6B", "fx", QUARTERLY, "GBP"),
    ("6A", "fx", QUARTERLY, "AUD"),
    ("6C", "fx", QUARTERLY, "CAD"),
    ("6S", "fx", QUARTERLY, "CHF"),
    ("CL", "energy", ALL12, "WTI crude"),
    ("NG", "energy", ALL12, "natural gas"),
    ("RB", "energy", ALL12, "RBOB gasoline"),
    ("HO", "energy", ALL12, "heating oil"),
    ("GC", "metals", GC_C, "gold"),
    ("SI", "metals", METAL, "silver"),
    ("HG", "metals", METAL, "copper"),
    ("ZC", "ags", METAL, "corn"),
    ("ZW", "ags", METAL, "wheat"),
    ("ZS", "ags", SOY, "soybeans"),
    ("ZM", "ags", SOY, "soybean meal"),
    ("ZL", "ags", SOY, "soybean oil"),
]

# Depth samples: one contract per probe year, so a root's history depth is measured, not assumed.
PROBE_YEARS = [2016, 2019, 2022, 2025]


def front_for(cycle, year, target_month=9):
    """Pick the listed contract nearest a mid-year reference month."""
    best = min(cycle, key=lambda m: (abs(m - target_month), m))
    return best, year


def main():
    probes, rows = [], []
    for root, sector, cycle, note in UNIVERSE:
        for y in PROBE_YEARS:
            m, yy = front_for(cycle, y)
            name = f"{root} {m:02d}-{yy % 100:02d}"
            probes.append(name)
            rows.append(dict(root=root, sector=sector, note=note, probe_year=y,
                             instrument=name,
                             # a mid-contract window that is liquid and pre-expiry
                             frm=f"{yy}-0{max(1, m-2)}-01" if m - 2 < 10 else f"{yy}-{m-2:02d}-01",
                             to=f"{yy}-{m:02d}-01"))

    import pandas as pd
    P = pd.DataFrame(rows)
    P.to_csv(os.path.join(OUT, "probe_plan.csv"), index=False)

    # group into runs of at most 20 secondary series, all sharing one probe year so the
    # backtest date range is common to every symbol in the run
    runs = []
    for y, g in P.groupby("probe_year"):
        syms = list(g["instrument"])
        for i in range(0, len(syms), 20):
            chunk = syms[i:i + 20]
            runs.append(dict(probe_year=int(y), primary=chunk[0],
                             symbols=",".join(chunk[1:]),
                             frm=f"{y}-01-01", to=f"{y}-12-01",
                             n=len(chunk)))
    with open(os.path.join(OUT, "run_plan.json"), "w") as f:
        json.dump(runs, f, indent=2)

    print(f"  universe            {len(UNIVERSE)} roots, {P['sector'].nunique()} sectors")
    print(f"  probe contracts     {len(probes)}")
    print(f"  runs to fire        {len(runs)}")
    for r in runs:
        print(f"    {r['probe_year']}  primary={r['primary']:<12} +{r['n']-1:>2} symbols  "
              f"{r['frm']} -> {r['to']}")


if __name__ == "__main__":
    main()
