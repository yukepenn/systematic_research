"""CARRY00 - CURVE DATA CAPABILITY.  Frozen by SPEC.md before it ran.

NO ALPHA P&L.  NO SIGNAL.  NO BACKTEST.  This run answers one question only:

    for each root, is a SIMULTANEOUSLY OBSERVABLE near/deferred contract pair present in the true
    unmerged store, often enough and early enough to support a causal curve signal?

TSMOM needed ONE contract per root per day. Carry needs TWO. That is strictly harder and it has
never been measured. CLOSED-BY-DATA is an allowed and respectable outcome.

FORBIDDEN HERE, and the reason is measured rather than assumed: merged / back-adjusted series.
TSMOM_DATA_CONTRACT established that four ES "contracts" report IDENTICAL volume through the merged
path - they are one front-month bar wearing four names, separated by a constant that IS the roll
basis. Differencing two of those would return the basis and call it carry.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, os.path.join(ROOT, "research", "multi_market", "src"))
import ncd_day as N                                                     # noqa: E402
import roll as R                                                        # noqa: E402

OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
Y0, Y1 = 2009, 2027
SEAL = pd.Timestamp("2026-08-01")
E1_MIN_PAIRED_DAYS = 1500
E2_MIN_FRAC_OF_TREND_DAYS = 0.60
E3_MIN_FRAC_OF_YEARS = 0.60
_fh = None


def P(*a):
    print(*a, flush=True)
    if _fh is not None:
        print(*a, file=_fh)


def month_gap(a, b):
    """Declared CONTRACT-MONTH gap. NOT a true time to expiry - the platform certifies neither."""
    (ma, ya), (mb, yb) = a, b
    return (yb - ya) * 12 + (mb - ma)


def load_root(root):
    """Every cached contract for a root, as one contract-day panel from the TRUE UNMERGED store."""
    cached = N.cached_ids()
    rows = []
    for cid, r, m, y in N.contracts_for(root, Y0, Y1):
        if cid not in cached:
            continue
        d = N.read_contract(cid)
        if d.empty:
            continue
        d = d[d["date"] < SEAL]
        if d.empty:
            continue
        d["root"], d["cmonth"], d["cyear"] = r, m, y
        d["expiry_key"] = y * 100 + m
        rows.append(d)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).sort_values(["date", "expiry_key"])


def main():
    global _fh
    _fh = open(os.path.join(OUT, "carry00.txt"), "w", encoding="utf-8")
    P("=" * 118)
    P("=== CARRY00 - CURVE DATA CAPABILITY.  NO ALPHA P&L, NO SIGNAL, NO BACKTEST.")
    P("=" * 118)
    P(f"    store: {N.DB_DAY}")
    P(f"    seal cap {SEAL.date()} (>= is never read)   years {Y0}-{Y1}")
    P("    expiry metadata: NOT CERTIFIED by the platform -> maturity is a DECLARED "
      "CONTRACT-MONTH GAP")

    universe = N.CORE + N.EXTENDED
    recs, per_root_days = [], {}
    P("")
    P("=" * 118)
    P("=== PER-ROOT CURVE OBSERVABILITY")
    P("=" * 118)
    P(f"    {'root':<5} {'sec':<13} {'contr':>6} {'first':<11} {'last':<11} "
      f"{'trendD':>7} {'pairD':>7} {'frac':>6} {'>=3':>6} {'gapMed':>7} "
      f"{'ovl p10':>8} {'p50':>6} {'p90':>6} {'neg':>5}")
    for root in universe:
        panel = load_root(root)
        if panel.empty:
            recs.append(dict(root=root, sector=N.SECTOR.get(root, "?"), n_contracts=0,
                             status="NO_DATA"))
            P(f"    {root:<5} {N.SECTOR.get(root,'?'):<13} {'0':>6}   NO CACHED CONTRACTS")
            continue

        # ---- NEAR: the existing causal active-contract engine, unchanged
        led = R.build_roll_ledger(panel[["date", "contract_id", "expiry_key", "open", "high",
                                         "low", "close", "volume"]].copy(), root)
        # KEY TYPE MATTERS. panel["date"].unique() yields numpy.datetime64 while a groupby on the
        # same column yields pandas Timestamp keys, and the two do NOT compare equal as dict keys.
        # The first version of this file silently reported ZERO paired days for all 25 roots
        # because of exactly that. Normalise once, here.
        dates = [pd.Timestamp(x) for x in np.sort(panel["date"].unique())]
        act = pd.Series(index=pd.DatetimeIndex(dates), dtype=object)
        for _, r_ in led.iterrows():
            act.loc[pd.Timestamp(r_["effective_date"])] = r_["new_contract"]
        act = act.ffill()

        meta = panel.groupby("contract_id").agg(
            first=("date", "min"), last=("date", "max"),
            cmonth=("cmonth", "first"), cyear=("cyear", "first")).sort_values("cyear")
        bydate = {pd.Timestamp(d): set(g) for d, g in panel.groupby("date")["contract_id"]}
        assert sum(1 for d in dates if bydate.get(d)) == len(dates), (
            "date-key type mismatch: live-contract lookup is silently empty")
        closes = panel.set_index(["date", "contract_id"])["close"]

        npair = nge3 = ntrend = 0
        gaps, ovl_by_pair, years_with_pair, neg = [], {}, set(), 0
        for d in dates:
            a = act.get(d)
            if not isinstance(a, str):
                continue
            ntrend += 1
            live = bydate.get(d, set())
            key = (int(meta.loc[a, "cmonth"]), int(meta.loc[a, "cyear"]))
            later = [c for c in live
                     if c != a and month_gap(key, (int(meta.loc[c, "cmonth"]),
                                                   int(meta.loc[c, "cyear"]))) > 0]
            if len(live) >= 3:
                nge3 += 1
            if not later:
                continue
            # DEFERRED = nearest later listed CONTRACT MONTH. Never future volume/liquidity.
            defer = min(later, key=lambda c: month_gap(key, (int(meta.loc[c, "cmonth"]),
                                                             int(meta.loc[c, "cyear"]))))
            g = month_gap(key, (int(meta.loc[defer, "cmonth"]), int(meta.loc[defer, "cyear"])))
            npair += 1
            gaps.append(g)
            years_with_pair.add(pd.Timestamp(d).year)
            ovl_by_pair.setdefault((a, defer), 0)
            ovl_by_pair[(a, defer)] += 1
            try:
                if closes.loc[(d, a)] <= 0 or closes.loc[(d, defer)] <= 0:
                    neg += 1
            except KeyError:
                pass

        ov = np.array(list(ovl_by_pair.values())) if ovl_by_pair else np.array([0])
        nyears = len(set(pd.DatetimeIndex(dates).year))
        frac = npair / max(ntrend, 1)
        rec = dict(root=root, sector=N.SECTOR.get(root, "?"), n_contracts=int(len(meta)),
                   first=str(pd.Timestamp(meta["first"].min()).date()),
                   last=str(pd.Timestamp(meta["last"].max()).date()),
                   trend_days=int(ntrend), paired_days=int(npair),
                   frac_paired=float(frac), frac_ge3=float(nge3 / max(ntrend, 1)),
                   gap_median=float(np.median(gaps)) if gaps else np.nan,
                   gap_min=int(min(gaps)) if gaps else -1,
                   gap_max=int(max(gaps)) if gaps else -1,
                   overlap_p10=float(np.percentile(ov, 10)),
                   overlap_p50=float(np.percentile(ov, 50)),
                   overlap_p90=float(np.percentile(ov, 90)),
                   n_years=int(nyears), years_with_pair=int(len(years_with_pair)),
                   frac_years=float(len(years_with_pair) / max(nyears, 1)),
                   nonpositive_close_days=int(neg),
                   cycle=str(N.CYCLES[root]))
        recs.append(rec)
        per_root_days[root] = npair
        P(f"    {root:<5} {rec['sector']:<13} {rec['n_contracts']:>6} {rec['first']:<11} "
          f"{rec['last']:<11} {ntrend:>7} {npair:>7} {frac:>6.3f} {rec['frac_ge3']:>6.3f} "
          f"{rec['gap_median']:>7.1f} {rec['overlap_p10']:>8.0f} {rec['overlap_p50']:>6.0f} "
          f"{rec['overlap_p90']:>6.0f} {neg:>5}")

    df = pd.DataFrame(recs)
    df.to_csv(os.path.join(OUT, "carry00_capability.csv"), index=False)

    # ================================================================ E1-E4, declared in SPEC
    P("")
    P("=" * 118)
    P("=== ELIGIBILITY - E1..E4, DATA ONLY.  Declared in SPEC before these numbers existed.")
    P("=" * 118)
    P(f"    E1  paired root-days      >= {E1_MIN_PAIRED_DAYS:,}")
    P(f"    E2  paired / trend days   >= {E2_MIN_FRAC_OF_TREND_DAYS:.2f}")
    P(f"    E3  years with a pair     >= {E3_MIN_FRAC_OF_YEARS:.2f} of the years the root spans")
    P("    E4  no non-positive closes on paired days (else FLAGGED, formula must survive them)")
    P("")
    P(f"    {'root':<5} {'sector':<13} {'E1':>10} {'E2':>10} {'E3':>10} {'E4':>10}   verdict")
    ok_roots = []
    d2 = df[df.get("status").isna()] if "status" in df.columns else df
    for _, r_ in d2.iterrows():
        e1 = r_["paired_days"] >= E1_MIN_PAIRED_DAYS
        e2 = r_["frac_paired"] >= E2_MIN_FRAC_OF_TREND_DAYS
        e3 = r_["frac_years"] >= E3_MIN_FRAC_OF_YEARS
        e4 = r_["nonpositive_close_days"] == 0
        good = bool(e1 and e2 and e3)
        if good:
            ok_roots.append((r_["root"], r_["sector"], bool(e4)))
        c1 = ("PASS " if e1 else "fail ") + format(int(r_["paired_days"]), ",")
        c2 = ("PASS " if e2 else "fail ") + f"{r_['frac_paired']:.2f}"
        c3 = ("PASS " if e3 else "fail ") + f"{r_['frac_years']:.2f}"
        c4 = ("PASS " if e4 else "FLAG ") + str(int(r_["nonpositive_close_days"]))
        tail = "  (price-sanity FLAG)" if good and not e4 else ""
        P(f"    {r_['root']:<5} {r_['sector']:<13} {c1:>11} {c2:>11} {c3:>11} {c4:>11}   "
          f"{'CARRY-CAPABLE' if good else 'DATA-BLOCKED'}{tail}")

    P("")
    P("=" * 118)
    P("=== SECTOR BREADTH - a sector needs >= 2 carry-capable roots (s40), else CASH")
    P("=" * 118)
    bysec = {}
    for r_, s, e4 in ok_roots:
        bysec.setdefault(s, []).append(r_)
    live = {s: v for s, v in bysec.items() if len(v) >= 2}
    for s in sorted(set(N.SECTOR.values())):
        v = bysec.get(s, [])
        P(f"    {s:<13} {len(v):>2} capable  {', '.join(v) if v else '-':<40} "
          f"{'PARTICIPATES' if len(v) >= 2 else 'CASH (fewer than 2)'}")
    P("")
    P(f"    carry-capable roots {len(ok_roots)} of {len(d2)}   "
      f"participating sectors {len(live)} of {len(set(N.SECTOR.values()))}")

    verdict = ("CARRY-CAPABLE" if len(live) >= 3 else
               "CLOSED-BY-DATA (breadth)" if len(live) >= 1 else "CLOSED-BY-DATA")
    P("")
    P("=" * 118)
    P(f"=== VERDICT: {verdict}")
    P("=" * 118)
    json.dump({"verdict": verdict, "capable": [r_ for r_, _, _ in ok_roots],
               "sectors": {s: v for s, v in bysec.items()},
               "participating_sectors": sorted(live),
               "E1": E1_MIN_PAIRED_DAYS, "E2": E2_MIN_FRAC_OF_TREND_DAYS,
               "E3": E3_MIN_FRAC_OF_YEARS},
              open(os.path.join(OUT, "carry00_verdict.json"), "w", encoding="utf-8"), indent=2)
    _fh.close()


if __name__ == "__main__":
    main()
