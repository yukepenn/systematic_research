"""OTR_R28 amendment 1: per-cell contract-round-turn solver on the cent lattice.

The uniform-quantity model (spec c3.P3_2) returned 0 solutions.  Its own residues show why:
a single NQ round turn at commission c makes a net cell congruent to -c (mod 500), and the two
records give residues 382, 382, 264 on single-trade cells - i.e. the SAME c with a different
number of contract-round-turns.  This solver lets the contract count vary per cell and imposes
the two accounting identities that were verified to hold exactly.
"""
from __future__ import annotations

import csv
import os
from fractions import Fraction

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "OTR_R28_2026_ARCHAEOLOGY", "out")

INSTRUMENTS = [("NQ", 500), ("MNQ", 50), ("ES", 1250), ("MES", 125)]


def cents(x):
    return int(round(Fraction(str(x)) * 100))


def solve_m(V, c, L, lo, hi):
    """All integers m in [lo, hi] with V + c*m == 0 (mod L)."""
    return [m for m in range(lo, hi + 1) if (V + c * m) % L == 0]


def main():
    path = os.path.join(ROOT, "research", "original_trader_reconstruction",
                        "screenshot_forensics", "derived", "targets_weekly_2026V.csv")
    recs = {r["image_id"]: r for r in csv.DictReader(open(path, encoding="utf-8"))}
    TP = ["OTRIMG-0152", "OTRIMG-0154"]

    print("=" * 78)
    print("verify the two accounting identities (they are imposed as constraints)")
    print("=" * 78)
    for img in TP:
        r = recs[img]
        gp, gl, na = cents(r["gross_profit_all"]), cents(r["gross_loss_all"]), cents(r["net_all"])
        nl, ns = cents(r["net_long"]), cents(r["net_short"])
        print(f"  {img}: gross_profit+gross_loss-net_all = {gp+gl-na:>4} cents   "
              f"net_long+net_short-net_all = {nl+ns-na:>4} cents")

    print("\n" + "=" * 78)
    print("P5_1 / P5_2 - joint solve for (instrument, commission, per-cell contract counts)")
    print("=" * 78)
    feasible = []
    for iname, L in INSTRUMENTS:
        for c in range(1, 1501):
            allrec = []
            ok = True
            for img in TP:
                r = recs[img]
                n = int(r["trades_all"]); nL = int(r["trades_long"]); nS = int(r["trades_short"])
                nW = round(n * float(r["wr_all"]) / 100.0); nLo = n - nW
                cell = {
                    "all":   (cents(r["net_all"]),      n),
                    "long":  (cents(r["net_long"]),     nL),
                    "short": (cents(r["net_short"]),    nS),
                    "win":   (cents(r["gross_profit_all"]), nW),
                    "loss":  (cents(r["gross_loss_all"]),   nLo),
                }
                sols = {k: solve_m(V, c, L, cnt, 4 * cnt) for k, (V, cnt) in cell.items()}
                if any(not v for v in sols.values()):
                    ok = False; break
                # impose m_long + m_short == m_all  and  m_win + m_loss == m_all
                combos = [(a, lo, s, w, ls)
                          for a in sols["all"]
                          for lo in sols["long"] for s in sols["short"] if lo + s == a
                          for w in sols["win"] for ls in sols["loss"] if w + ls == a]
                if not combos:
                    ok = False; break
                allrec.append((img, n, nL, nS, nW, nLo, combos))
            if ok:
                feasible.append((iname, c, allrec))

    print(f"feasible (instrument, commission) pairs: {len(feasible)}")
    if not feasible:
        print("NONE - the generalised model also fails.  Reported as a negative result.")
        return

    by_inst = {}
    for iname, c, _ in feasible:
        by_inst.setdefault(iname, []).append(c)
    print("\ncommission congruence classes that survive, per instrument:")
    for iname, cs in by_inst.items():
        L = dict(INSTRUMENTS)[iname]
        classes = sorted({x % L for x in cs})
        print(f"  {iname:<4} L={L:<5} c mod {L} in {[f'${x/100:.2f}' for x in classes]}   "
              f"({len(cs)} raw values in $0.01..$15.00)")
        print(f"       -> absolute c candidates: "
              f"{[f'${x/100:.2f}' for x in sorted(cs)][:12]}"
              f"{' ...' if len(cs) > 12 else ''}")

    print("\n" + "=" * 78)
    print("P5_2 DISCRIMINATOR - implied contract-round-turns vs reported trade counts")
    print("=" * 78)
    # Take the smallest surviving commission per instrument as the representative for display;
    # the congruence structure (and hence every m) is identical across the class.
    for iname in by_inst:
        c = min(by_inst[iname])
        rec = [f for f in feasible if f[0] == iname and f[1] == c][0][2]
        L = dict(INSTRUMENTS)[iname]
        print(f"\n--- {iname} (L={L}), representative c = ${c/100:.2f}/contract/RT ---")
        for img, n, nL, nS, nW, nLo, combos in rec:
            m_all = sorted({x[0] for x in combos})
            m_lo = sorted({x[1] for x in combos}); m_sh = sorted({x[2] for x in combos})
            m_w = sorted({x[3] for x in combos}); m_ls = sorted({x[4] for x in combos})
            print(f"  {img}  reported n={n} (L{nL}/S{nS}, W{nW}/Lo{nLo})")
            print(f"     m_all   in {m_all[:6]}{'...' if len(m_all)>6 else ''}"
                  f"   -> contracts/trade {m_all[0]/n:.3f}"
                  f"{'' if len(m_all)==1 else f' .. {m_all[-1]/n:.3f}'}")
            print(f"     m_long  in {m_lo[:6]}{'...' if len(m_lo)>6 else ''}  (nL={nL})")
            print(f"     m_short in {m_sh[:6]}{'...' if len(m_sh)>6 else ''}  (nS={nS})")
            print(f"     m_win   in {m_w[:6]}{'...' if len(m_w)>6 else ''}  (nW={nW})")
            print(f"     m_loss  in {m_ls[:6]}{'...' if len(m_ls)>6 else ''}  (nLo={nLo})")
            exact = (m_all == [n])
            print(f"     m == n exactly? {'YES - all qty 1' if exact else 'NO'}")

    print("\n" + "=" * 78)
    print("single-trade cells: how many contracts did the largest win / largest loss carry?")
    print("=" * 78)
    for iname, L in INSTRUMENTS:
        cs = by_inst.get(iname)
        if not cs:
            continue
        c = min(cs)
        print(f"\n--- {iname}, c = ${c/100:.2f}/contract/RT ---")
        for img in TP:
            r = recs[img]
            for k in ("largest_win_all", "largest_loss_all"):
                V = cents(r[k])
                q = solve_m(V, c, L, 1, 20)
                gross = [(V + c * qq) / 100.0 for qq in q[:4]]
                pts = [f"{abs(g)/(20.0*qq):.2f}" for g, qq in zip(gross, q[:4])] \
                    if iname == "NQ" else ["-"] * len(gross)
                print(f"  {img} {k:<18} {r[k]:>11}  contracts in {q[:6]}"
                      f"   gross {[f'{g:.2f}' for g in gross]}  pts/contract {pts}")

    with open(os.path.join(OUT, "cent_lattice_solutions.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["instrument", "tick_cents", "commission_c_cents", "commission_c_dollars"])
        for iname, c, _ in feasible:
            w.writerow([iname, dict(INSTRUMENTS)[iname], c, c / 100.0])


if __name__ == "__main__":
    main()
