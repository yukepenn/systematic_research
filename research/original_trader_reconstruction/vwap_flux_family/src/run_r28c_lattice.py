"""OTR_R28 amendment 1, part C: discipline the lattice solve with the SINGLE-TRADE cells first.

Part B searched commissions against the AGGREGATE cells and surfaced an internally contradictory
NQ answer: c = $0.06 satisfies every aggregate yet leaves all four single-trade cells with EMPTY
contract sets.  Single-trade cells (largest win, largest loss) carry exactly one trade, so their
unknown is a small integer contract count - by far the tightest constraint in the record.  They
are solved FIRST here, and only commissions surviving them are carried into the aggregates.
"""
from __future__ import annotations

import csv
import os
from fractions import Fraction

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "OTR_R28_2026_ARCHAEOLOGY", "out")
INSTRUMENTS = [("NQ", 500), ("MNQ", 50), ("ES", 1250), ("MES", 125)]
MAX_Q = 10          # contracts on a single trade
PV = {"NQ": 20.0, "MNQ": 2.0, "ES": 50.0, "MES": 5.0}   # $ per index point


def cents(x):
    return int(round(Fraction(str(x)) * 100))


def main():
    path = os.path.join(ROOT, "research", "original_trader_reconstruction",
                        "screenshot_forensics", "derived", "targets_weekly_2026V.csv")
    recs = {r["image_id"]: r for r in csv.DictReader(open(path, encoding="utf-8"))}
    TP = ["OTRIMG-0152", "OTRIMG-0154"]
    single = [(img, k, cents(recs[img][k]))
              for img in TP for k in ("largest_win_all", "largest_loss_all")]

    print("=" * 78)
    print("TEST A - the four SINGLE-TRADE cells alone.  One trade, so m = q, an integer 1..10.")
    print("=" * 78)
    for img, k, V in single:
        print(f"  {img} {k:<18} {V/100:>10.2f}   V mod 500 = {V % 500}")

    survivors = {}
    for iname, L in INSTRUMENTS:
        good = []
        for c in range(1, 1501):
            qs = []
            for _, _, V in single:
                q = [x for x in range(1, MAX_Q + 1) if (V + c * x) % L == 0]
                if not q:
                    qs = None; break
                qs.append(q)
            if qs:
                good.append((c, qs))
        survivors[iname] = good
        print(f"\n  {iname:<4} (L={L}): commissions in $0.01..$15.00 explaining ALL FOUR "
              f"single-trade cells: {len(good)}")
        for c, qs in good[:6]:
            print(f"        c=${c/100:>5.2f}/contract/RT   contract sets "
                  f"{[q[:3] for q in qs]}")
        if len(good) > 6:
            print(f"        ... and {len(good)-6} more")

    print("\n" + "=" * 78)
    print("TEST A detail - the minimal-contract reading under NQ")
    print("=" * 78)
    nq = survivors["NQ"]
    if nq:
        # the smallest commission whose minimal contract counts are all <= 2
        pick = None
        for c, qs in nq:
            if all(q[0] <= 2 for q in qs):
                pick = (c, qs); break
        if pick is None:
            pick = nq[0]
        c, qs = pick
        print(f"  commission c = ${c/100:.2f} per contract per round turn")
        print(f"  (congruence class: c = ${c/100:.2f} mod $5.00 -> also "
              f"${(c+500)/100:.2f}, ${(c+1000)/100:.2f} are indistinguishable on residues)")
        print()
        for (img, k, V), q in zip(single, qs):
            qq = q[0]
            gross = V + c * qq
            print(f"  {img} {k:<18} net {V/100:>10.2f}  contracts={qq}  "
                  f"gross {gross/100:>10.2f}  = {abs(gross)/100/(PV['NQ']*qq):>7.2f} index pts"
                  f"   ({abs(gross)/100/(5.0*qq):.0f} ticks)")
    else:
        print("  NQ admits NO commission explaining all four single-trade cells.")

    print("\n" + "=" * 78)
    print("TEST B - carry the survivors into the AGGREGATE cells")
    print("=" * 78)
    print("aggregate model: V + c*m == 0 (mod L), m = total contract-round-turns, m >= n,")
    print("with m_long+m_short == m_all and m_win+m_loss == m_all (identities verified exactly).")
    for iname, L in INSTRUMENTS:
        ok_any = []
        for c, _ in survivors[iname]:
            fits = True
            detail = []
            for img in TP:
                r = recs[img]
                n = int(r["trades_all"]); nL = int(r["trades_long"]); nS = int(r["trades_short"])
                nW = round(n * float(r["wr_all"]) / 100.0); nLo = n - nW
                cell = {"all": (cents(r["net_all"]), n),
                        "long": (cents(r["net_long"]), nL),
                        "short": (cents(r["net_short"]), nS),
                        "win": (cents(r["gross_profit_all"]), nW),
                        "loss": (cents(r["gross_loss_all"]), nLo)}
                sols = {k: [m for m in range(cnt, 10 * cnt + 1) if (V + c * m) % L == 0]
                        for k, (V, cnt) in cell.items()}
                if any(not v for v in sols.values()):
                    fits = False; break
                combos = [(a, lo, s, w, ls) for a in sols["all"]
                          for lo in sols["long"] for s in sols["short"] if lo + s == a
                          for w in sols["win"] for ls in sols["loss"] if w + ls == a]
                if not combos:
                    fits = False; break
                detail.append((img, n, nL, nS, nW, nLo, combos))
            if fits:
                ok_any.append((c, detail))
        print(f"\n  {iname:<4}: commissions surviving BOTH single-trade and aggregate cells "
              f"(m bound widened to 10n): {len(ok_any)}")
        for c, detail in ok_any[:3]:
            print(f"     c=${c/100:.2f}")
            for img, n, nL, nS, nW, nLo, combos in detail:
                ma = sorted({x[0] for x in combos})
                print(f"        {img}  n={n}  m_all in {ma[:5]}"
                      f"  -> {ma[0]/n:.2f}-{ma[-1]/n:.2f} contracts/trade")

    print("\n" + "=" * 78)
    print("VERDICT")
    print("=" * 78)
    nq_both = 0
    for iname in ("NQ",):
        for c, _ in survivors[iname]:
            pass
    print("  see REPORT.md - the discriminating question is whether a pure NQ account at a")
    print("  constant per-contract commission can explain BOTH the extreme trades and the")
    print("  aggregates of BOTH June Trade Performance records simultaneously.")


if __name__ == "__main__":
    main()
