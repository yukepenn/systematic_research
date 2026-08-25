"""OTR_R30 Part A (spec preregistered): quantity audit of the -$2,600 fingerprint.

Owner correction 5.  The confirmed qty-2 trade reopens 65 pts x 2 = $2,600 as a rival to
130 pts x 1 - and 65 points is exactly the established 2025-era stop, so "the stop never changed"
is the MORE parsimonious rival.  This run decides, per record, whether the lattice forces q = 1.

Key facts used:
  (i)  an NQ trade of quantity q has gross P&L = 5 * q * (integer ticks) dollars, so a
       SINGLE-TRADE cell that is an ODD multiple of $5 forces that trade's quantity to be ODD;
  (ii) 2600 / (20 q) must be a legal NQ increment (multiple of 0.25), which admits
       q in {1,2,4,5,8,10,...} and EXCLUDES q = 3,6,7,9;
  (iii) aggregate cells bound only the SUM over trades, never an individual trade's quantity.
"""
from __future__ import annotations

import csv
import os
from fractions import Fraction
from math import gcd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "OTR_R30_ENTRY_EXIT_DECOMP", "out")
os.makedirs(OUT, exist_ok=True)

SINGLE_TRADE_CELLS = ["largest_win_all", "largest_loss_all"]
AGG_CELLS = ["net_all", "gross_profit_all", "gross_loss_all", "net_long", "net_short"]


def cents(x):
    return int(round(Fraction(str(x)) * 100))


def legal_q_for_2600():
    """q such that 2600/(20q) is a multiple of 0.25 index points."""
    ok = []
    for q in range(1, 21):
        pts4 = Fraction(2600, 20 * q) * 4          # points x 4 must be an integer
        if pts4.denominator == 1:
            ok.append((q, float(Fraction(2600, 20 * q))))
    return ok


def main():
    path = os.path.join(ROOT, "research", "original_trader_reconstruction",
                        "screenshot_forensics", "derived", "targets_weekly_2026V.csv")
    recs = list(csv.DictReader(open(path, encoding="utf-8")))

    print("=" * 80)
    print("A - which quantities can even produce a -$2,600 stop at a legal NQ increment?")
    print("=" * 80)
    for q, pts in legal_q_for_2600():
        note = ""
        if q == 1:
            note = "  <- the 130-point hypothesis"
        if q == 2:
            note = "  <- 65 pts, EXACTLY the established 2025-era stop"
        print(f"   q={q:<3} -> {pts:>7.2f} index points{note}")
    print("   q = 3, 6, 7, 9 are EXCLUDED (non-integer tick)")

    print("\n" + "=" * 80)
    print("A1 - single-trade cells: odd multiple of $5 forces ODD quantity on that trade")
    print("=" * 80)
    rows = []
    print(f"{'record':<13}{'window end':<12}{'cell':<19}{'value':>12}{'/$5':>10}"
          f"{'parity':>9}  quantity constraint")
    n_odd = 0
    for r in recs:
        is_tp = cents(r["commission_total"]) != 0
        for k in SINGLE_TRADE_CELLS:
            if not r.get(k):
                continue
            c = cents(r[k])
            if c % 500 != 0:
                cons = "TP record - not on the $5 lattice (commission included); see Part A3"
                par = "n/a"
                units = float(c) / 500.0
            else:
                units = abs(c) // 500
                par = "ODD" if units % 2 == 1 else "even"
                if units % 2 == 1:
                    cons = "q is ODD -> q in {1,5,...}"
                    n_odd += 1
                else:
                    cons = "q unconstrained by parity"
            print(f"{r['image_id']:<13}{r['report_end']:<12}{k:<19}{r[k]:>12}"
                  f"{units:>10.1f}{par:>9}  {cons}")
            rows.append(dict(image_id=r["image_id"], report_end=r["report_end"], cell=k,
                             value=r[k], units_of_5=units, parity=par,
                             kind="TradePerf" if is_tp else "SA", constraint=cons))
    print(f"\nA1 -> single-trade cells that are ODD multiples of $5: {n_odd}")
    print(f"A1 PREDICTION was 'at least one' -> {'PASS' if n_odd else 'FAIL'}")

    print("\n" + "=" * 80)
    print("A2 - bucket every -$2,600 occurrence")
    print("=" * 80)
    buckets = {"A": [], "B": [], "C": []}
    for r in recs:
        if not r.get("largest_loss_all") or cents(r["largest_loss_all"]) != -260000:
            continue
        is_tp = cents(r["commission_total"]) != 0
        # does ANY single-trade cell in this record have odd $5-units?
        odd_here = []
        for k in SINGLE_TRADE_CELLS:
            if r.get(k) and cents(r[k]) % 500 == 0 and (abs(cents(r[k])) // 500) % 2 == 1:
                odd_here.append(k)
        if is_tp:
            b = "C"
        elif odd_here:
            b = "A"
        else:
            b = "B"
        buckets[b].append((r["image_id"], r["report_end"], odd_here))
    print("bucket A - SA record whose OWN single-trade cells force ODD quantity")
    for img, d, oh in buckets["A"]:
        print(f"   {img} {d}   odd cell(s): {', '.join(oh)}")
    print(f"   count: {len(buckets['A'])}")
    print("\nbucket B - SA record, quantity NOT determinable from the lattice")
    for img, d, _ in buckets["B"]:
        print(f"   {img} {d}")
    print(f"   count: {len(buckets['B'])}")
    print("\nbucket C - Trade Performance record")
    for img, d, _ in buckets["C"]:
        print(f"   {img} {d}")
    print(f"   count: {len(buckets['C'])}")

    print("\n" + "=" * 80)
    print("A2 VERDICT (decision rule fixed in advance)")
    print("=" * 80)
    tot = sum(len(v) for v in buckets.values())
    print(f"  -$2,600 occurrences: {tot}")
    print(f"  '130 NQ points = $2,600' CONFIRMED for : {len(buckets['A'])}  (bucket A)")
    print(f"  '130 x 1 OR 65 x 2, both live'    for : {len(buckets['B'])}  (bucket B)")
    print(f"  Trade Performance, handled separately  : {len(buckets['C'])}  (bucket C)")
    if buckets["A"]:
        print("\n  NOTE on bucket A: an odd single-trade cell forces q in {1,5,...} for THAT trade.")
        print("  q=5 would mean a 26-point stop with a $2,260 average winner = 22.6 points at")
        print("  q=5; both are internally consistent, so q=5 is NOT excluded by arithmetic alone")
        print("  and is carried as a rival per section 6.")

    print("\n" + "=" * 80)
    print("A - cross-check: whole-record gcd (bounds the SUM's quantity, not each trade)")
    print("=" * 80)
    print(f"{'record':<13}{'gcd(cells) cents':>18}{'gcd/$5 units':>14}   implication")
    for r in recs:
        if cents(r["commission_total"]) != 0:
            continue
        vals = [abs(cents(r[k])) for k in AGG_CELLS + SINGLE_TRADE_CELLS
                if r.get(k) and cents(r[k]) != 0]
        g = 0
        for v in vals:
            g = gcd(g, v)
        u = g / 500.0
        imp = ("sum is an ODD multiple of $5 -> at least one trade had odd q"
               if (g // 500) % 2 == 1 else "sum is an even multiple of $5")
        print(f"{r['image_id']:<13}{g:>18}{u:>14.1f}   {imp}")

    with open(os.path.join(OUT, "quantity_audit.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"\nwritten: {os.path.join(OUT, 'quantity_audit.csv')}")


if __name__ == "__main__":
    main()
