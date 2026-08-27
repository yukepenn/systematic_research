"""Multi-market INVENTORY (directive s11) - which markets are actually usable, and how deep?

This is deliberately NOT the substrate. It samples one contract per root per probe year (2016,
2019, 2022, 2025) and measures what directive s11 asks for: available history, contract continuity,
liquidity, and missing intervals. Roll handling and continuous-return construction belong to the
substrate build, which should not start until this says which markets are worth it.

Liquidity is reported as median DAILY DOLLAR VOLUME using each contract's real point value, because
raw contract counts are not comparable across markets - 1 ZC contract is not 1 ES contract.
"""
from __future__ import annotations

import glob
import os

import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(HERE, "out", "csv")
OUT = os.path.join(HERE, "out")

# CME point values (USD per 1.00 of quoted price), for dollar-volume comparability.
PV = {
    "ES": 50, "NQ": 20, "RTY": 50, "YM": 5,
    "ZT": 2000, "ZF": 1000, "ZN": 1000, "ZB": 1000,
    "6E": 125000, "6J": 12500000, "6B": 62500, "6A": 100000, "6C": 100000, "6S": 125000,
    "CL": 1000, "NG": 10000, "RB": 42000, "HO": 42000,
    "GC": 100, "SI": 5000, "HG": 25000,
    "ZC": 50, "ZW": 50, "ZS": 50, "ZM": 100, "ZL": 600,
}
SECTOR = {
    "ES": "equity_index", "NQ": "equity_index", "RTY": "equity_index", "YM": "equity_index",
    "ZT": "rates", "ZF": "rates", "ZN": "rates", "ZB": "rates",
    "6E": "fx", "6J": "fx", "6B": "fx", "6A": "fx", "6C": "fx", "6S": "fx",
    "CL": "energy", "NG": "energy", "RB": "energy", "HO": "energy",
    "GC": "metals", "SI": "metals", "HG": "metals",
    "ZC": "ags", "ZW": "ags", "ZS": "ags", "ZM": "ags", "ZL": "ags",
}
# NT8 returns resolved codes like ESU2 / GCQ5. Map back to root by longest-prefix match.
ROOTS = sorted(PV, key=len, reverse=True)


def root_of(sym: str) -> str:
    for r in ROOTS:
        if sym.startswith(r):
            return r
    return sym


def main():
    frames = []
    for f in sorted(glob.glob(os.path.join(CSV, "y*_bars.csv"))):
        tag = os.path.basename(f).split("_")[0]
        d = pd.read_csv(f, parse_dates=["time"])
        d["probe_year"] = int(tag[1:5])
        frames.append(d)
    D = pd.concat(frames, ignore_index=True)
    D["root"] = D["symbol"].map(root_of)
    D["sector"] = D["root"].map(SECTOR)
    D["pv"] = D["root"].map(PV)
    D["dollar_vol"] = D["close"] * D["volume"] * D["pv"]

    # failures, from the v2 sidecars
    fails = []
    for f in glob.glob(os.path.join(CSV, "*_symbols.csv")):
        s = pd.read_csv(f)
        for _, r in s[s["status"] == "FAILED"].iterrows():
            fails.append(dict(tag=os.path.basename(f).split("_")[0], symbol=r["symbol"]))
    F = pd.DataFrame(fails)

    rows = []
    for (root, y), g in D.groupby(["root", "probe_year"]):
        rows.append(dict(root=root, sector=SECTOR.get(root, "?"), probe_year=y,
                         bars=len(g), first=str(g["time"].min().date()),
                         last=str(g["time"].max().date()),
                         med_contracts=int(g["volume"].median()),
                         med_dollar_vol_musd=round(g["dollar_vol"].median() / 1e6, 1),
                         zero_vol_days=int((g["volume"] == 0).sum())))
    R = pd.DataFrame(rows).sort_values(["sector", "root", "probe_year"])
    R.to_csv(os.path.join(OUT, "inventory.csv"), index=False)

    P = print
    P("=" * 104)
    P("=== MULTI-MARKET INVENTORY - what the existing connection actually serves, at $0")
    P("=" * 104)
    P("")
    P(f"    roots probed        {D['root'].nunique()}")
    P(f"    sectors             {D['sector'].nunique()}")
    P(f"    probe years         {sorted(D['probe_year'].unique())}")
    P(f"    contract-years      {len(R)}")
    P(f"    daily bars pulled   {len(D):,}")
    P("")

    piv = R.pivot_table(index=["sector", "root"], columns="probe_year",
                        values="bars", aggfunc="sum").fillna(0).astype(int)
    P("    DEPTH - daily bars returned per probe year (0 = contract did not resolve)")
    P("")
    P(piv.to_string())

    P("")
    P("    LIQUIDITY - median daily dollar volume, $M, at the 2025 probe")
    P("")
    L = (R[R["probe_year"] == 2025].sort_values("med_dollar_vol_musd", ascending=False)
         [["sector", "root", "med_dollar_vol_musd", "med_contracts"]])
    P(L.to_string(index=False))

    if len(F):
        P("")
        P("    UNRESOLVED CONTRACTS - a result, not an error")
        P("")
        for _, r in F.sort_values("symbol").iterrows():
            P(f"      {r['symbol']:<12} ({r['tag']})")

    P("")
    P("=" * 104)
    P("=== VERDICT")
    P("=" * 104)
    full = piv[(piv > 100).all(axis=1)]
    P(f"    roots with >100 daily bars in EVERY probe year (2016-2025): {len(full)}")
    P(f"      {sorted(set(i[1] for i in full.index))}")
    P("")
    P("    That is the tradable universe for a preregistered TSMOM/carry book, at zero data cost.")
    P("    NOT yet built: continuous returns, roll process, carry from the curve, session")
    P("    calendars. Those are the substrate, and the substrate is the next step, not this one.")
    print(f"\n    wrote {OUT}\\inventory.csv")


if __name__ == "__main__":
    main()
