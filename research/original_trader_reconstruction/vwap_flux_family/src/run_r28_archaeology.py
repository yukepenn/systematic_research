"""OTR_R28 (spec preregistered): 2026 evidence archaeology.

C1/C2  the panel EXTENT SERIES as a build-event signal covering the ~94% of the August
       parameter list that was never photographed.
C3/C4  the CENT LATTICE of the 2026 report cells - the technique that cracked Jan-2023 -
       applied to commission, instrument/quantity reducibility, and the -$2,600 cap.

Pixel bands are transcribed verbatim from vwap_flux_family/2026_PANEL_TOPOLOGY.md section 1,
which is a committed FACT table (grayscale run-length scans of the Settings-pane lane).
"""
from __future__ import annotations

import csv
import os
from fractions import Fraction

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "OTR_R28_2026_ARCHAEOLOGY", "out")
os.makedirs(OUT, exist_ok=True)

PITCH = 21.7          # value-box grid pitch, px (FACT, identical in every frame measured)
SIG_H = 1.0           # thumb-height uncertainty, px (topology note: +/-1 px of thumb-edge noise)
SIG_T = 1.0           # track-height uncertainty, px

# image, report_end, machine, T, h                       (from 2026_PANEL_TOPOLOGY.md section 1)
FRAMES = [
    ("OTRIMG-0113", "2026-01-30", "dev",  647, 251),
    ("OTRIMG-0115", "2026-02-06", "mimi", 645, 109),
    ("OTRIMG-0117", "2026-02-13", "hp",   642,  90),
    ("OTRIMG-0119", "2026-02-20", "hp",   641,  88),
    ("OTRIMG-0121", "2026-02-27", "hp",   642,  85),
    ("OTRIMG-0123", "2026-03-06", "hp",   642,  87),
    ("OTRIMG-0125", "2026-03-14", "dev",  648,  66),
    ("OTRIMG-0127", "2026-03-21", "hp",   642,  62),
    ("OTRIMG-0129", "2026-03-27", "dev",  648,  64),
    ("OTRIMG-0132", "2026-04-02", "dev",  648,  63),
    ("OTRIMG-0134", "2026-04-13", "hp",   633,  57),
    ("OTRIMG-0136", "2026-04-17", "hp",   681,  70),
    ("OTRIMG-0138", "2026-04-29", "dev",  633,  56),
    ("OTRIMG-0140", "2026-05-02", "dev",  629,  52),
    ("OTRIMG-0142", "2026-05-08", "dev",  634,  51),
    ("OTRIMG-0146", "2026-05-23", "dev",  631,  46),
    ("OTRIMG-0148", "2026-05-29", "hp",   628,  46),
    ("OTRIMG-0150", "2026-06-05", "dev",  631,  45),
    ("OTRIMG-0156", "2026-06-26", "hp",   631,  44),
    ("OTRIMG-0159", "2026-07-10", "hp",   631,  37),
    ("OTRIMG-0162", "2026-07-31", "hp",   642,  35),
    ("OTRIMG-0164", "2026-08-14", "hp",   648,  37),
]


def extent(T, h):
    """M1: E_rows ~ (T/pitch) * (T/h).  Returns (E, sigma_E)."""
    E = (T / PITCH) * (T / h)
    dT = 2.0 * E / T
    dh = -E / h
    sig = ((dT * SIG_T) ** 2 + (dh * SIG_H) ** 2) ** 0.5
    return E, sig


def c1_c2():
    print("=" * 78)
    print("C1 - PANEL EXTENT SERIES with propagated uncertainty")
    print("=" * 78)
    rows = []
    for img, d, mach, T, h in FRAMES:
        E, s = extent(T, h)
        rows.append(dict(image_id=img, report_end=d, machine=mach, track_T=T, thumb_h=h,
                         extent_rows=round(E, 1), sigma_rows=round(s, 1)))
    print(f"{'image':<13}{'date':<12}{'m':<5}{'T':>5}{'h':>5}{'E_rows':>9}{'sigma':>8}")
    for r in rows:
        print(f"{r['image_id']:<13}{r['report_end']:<12}{r['machine']:<5}"
              f"{r['track_T']:>5}{r['thumb_h']:>5}{r['extent_rows']:>9}{r['sigma_rows']:>8}")

    s_first = rows[2]["sigma_rows"]            # 2026-02-13, h=90
    s_late = [r for r in rows if r["report_end"] == "2026-07-31"][0]["sigma_rows"]
    ratio = s_late / s_first
    print(f"\nP1_1 sigma(2026-07-31,h=35)/sigma(2026-02-13,h=90) = {ratio:.2f}"
          f"   -> {'PASS' if ratio > 5 else 'FAIL'} (predicted > 5)")

    print("\n" + "=" * 78)
    print("C1 - WEEK-OVER-WEEK DELTAS  (build event iff |delta| > 4 sigma)")
    print("=" * 78)
    ev = []
    print(f"{'from -> to':<26}{'dE':>8}{'sigma':>8}{'n_sigma':>9}  verdict")
    for a, b in zip(rows, rows[1:]):
        dE = b["extent_rows"] - a["extent_rows"]
        sd = (a["sigma_rows"] ** 2 + b["sigma_rows"] ** 2) ** 0.5
        ns = dE / sd
        if abs(ns) > 4:
            v = "BUILD EVENT" if dE > 0 else "ROWS REMOVED"
        elif abs(ns) > 2:
            v = "marginal"
        else:
            v = "noise"
        same_pane = "" if a["track_T"] == b["track_T"] else "  [pane T changed]"
        ev.append(dict(frm=a["image_id"], to=b["image_id"], date_from=a["report_end"],
                       date_to=b["report_end"], delta_rows=round(dE, 1),
                       sigma=round(sd, 1), n_sigma=round(ns, 2), verdict=v,
                       pane_height_changed=a["track_T"] != b["track_T"]))
        print(f"{a['report_end']} -> {b['report_end']:<11}{dE:>8.1f}{sd:>8.1f}"
              f"{ns:>9.2f}  {v}{same_pane}")

    neg = [e for e in ev if e["delta_rows"] < 0]
    bad_neg = [e for e in neg if e["n_sigma"] < -2]
    print(f"\nP1_2 negative deltas: {len(neg)}; beyond -2 sigma: {len(bad_neg)}"
          f"  -> {'PASS (all noise)' if not bad_neg else 'FAIL - rows genuinely removed'}")
    for e in bad_neg:
        print(f"      {e['date_from']} -> {e['date_to']}  {e['delta_rows']:+.1f} "
              f"({e['n_sigma']:+.2f} sigma)  pane_changed={e['pane_height_changed']}")

    big = [e for e in ev if e["n_sigma"] > 4]
    print(f"\nP1_3 deltas beyond +4 sigma: {len(big)}"
          f"  -> {'PASS' if big else 'FAIL - growth not resolvable into events'}")
    for e in big:
        print(f"      BUILD EVENT  week ending {e['date_to']}: {e['delta_rows']:+.0f} rows "
              f"({e['n_sigma']:+.1f} sigma)")

    with open(os.path.join(OUT, "panel_extent_series.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with open(os.path.join(OUT, "build_events.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ev[0].keys())); w.writeheader(); w.writerows(ev)
    return rows, ev


# ----------------------------------------------------------------------------------------
# C3 / C4 - cent lattice
# ----------------------------------------------------------------------------------------
def cents(x):
    """Exact cents as an integer; avoids all float error."""
    return int(round(Fraction(str(x)) * 100))


CELLS_GROSS_LIKE = ["gross_profit_all", "gross_loss_all", "largest_win_all",
                    "largest_loss_all", "net_long", "net_short", "net_all"]


def c3_c4():
    path = os.path.join(ROOT, "research", "original_trader_reconstruction",
                        "screenshot_forensics", "derived", "targets_weekly_2026V.csv")
    recs = list(csv.DictReader(open(path, encoding="utf-8")))

    print("\n" + "=" * 78)
    print("C3 - P3_1: are the 22 zero-commission records pure $5-lattice (GROSS, qty 1 NQ)?")
    print("=" * 78)
    off = []
    for r in recs:
        if cents(r["commission_total"]) != 0:
            continue
        bad = [(k, r[k]) for k in CELLS_GROSS_LIKE if r.get(k) and cents(r[k]) % 500 != 0]
        if bad:
            off.append((r["image_id"], r["report_end"], bad))
    zero_comm = [r for r in recs if cents(r["commission_total"]) == 0]
    print(f"records with commission_total = 0: {len(zero_comm)}")
    print(f"records with an off-$5-lattice cell: {len(off)}")
    for img, d, bad in off:
        print(f"   {img} ({d}): " + ", ".join(f"{k}={v}" for k, v in bad))
    print(f"P3_1 -> {'PASS' if not off else 'FAIL'}  "
          f"(every cell of every zero-commission record lies on the $5 lattice"
          f"{' - so all 2026 SA numbers are GROSS of commission' if not off else ''})")

    print("\n" + "=" * 78)
    print("C3 - P3_2: are the cent-level Trade Performance records reducible to ONE")
    print("           (instrument, quantity, commission) triple?")
    print("=" * 78)
    tp = [r for r in recs if any(cents(r[k]) % 500 != 0 for k in CELLS_GROSS_LIKE if r.get(k))]
    print("cent-level records: " + ", ".join(f"{r['image_id']} ({r['report_end']})" for r in tp))

    sols = []
    # instrument tick value in cents: NQ = 500, MNQ = 50
    for tick_c, iname in ((500, "NQ"), (50, "MNQ")):
        for q in range(1, 11):
            lat = tick_c * q                       # gross of one trade is a multiple of this
            for c1_c in range(1, 1501):            # per-contract-per-RT commission, cents
                ok = True
                detail = []
                for r in tp:
                    n = int(r["trades_all"])
                    comm_per_rt = q * c1_c
                    # net-of-commission cells: add back n (or 1) round turns
                    tests = [("net_all", n), ("largest_loss_all", 1), ("largest_win_all", 1),
                             ("net_long", int(r["trades_long"])),
                             ("net_short", int(r["trades_short"]))]
                    for k, cnt in tests:
                        if not r.get(k):
                            continue
                        v = cents(r[k])
                        g = v + cnt * comm_per_rt if v < 0 else v + cnt * comm_per_rt
                        if g % lat != 0:
                            ok = False
                            break
                        detail.append((r["image_id"], k, g // lat))
                    if not ok:
                        break
                if ok:
                    sols.append(dict(instrument=iname, qty=q, comm_per_contract_rt=c1_c / 100,
                                     comm_per_round_turn=q * c1_c / 100, lattice_cents=lat))
    print(f"\nexhaustive search: instrument in (NQ, MNQ) x qty 1..10 x commission $0.01..$15.00")
    print(f"SOLUTIONS FOUND: {len(sols)}")
    for s in sols[:40]:
        print(f"   {s['instrument']} qty={s['qty']} "
              f"c=${s['comm_per_contract_rt']:.2f}/contract/RT "
              f"(${s['comm_per_round_turn']:.2f}/RT)")
    if len(sols) > 40:
        print(f"   ... and {len(sols)-40} more")
    print(f"\nP3_2 -> {'PASS - a single triple explains both records' if sols else 'FAIL'}")
    if not sols:
        print("       The two Trade Performance records are NOT reducible to one NQ-qty-1")
        print("       strategy under any (instrument, qty, commission) triple in the search")
        print("       space.  Per the preregistered decision rule this is positive evidence")
        print("       for the account-level multi-strategy model (directive section 30).")

    # ---- per-cell diagnostic so the failure is legible, not just a verdict ----
    print("\n   per-cell residues (value mod $5, in cents) for the cent-level records:")
    for r in tp:
        print(f"   {r['image_id']} n={r['trades_all']} nL={r['trades_long']} nS={r['trades_short']}")
        for k in CELLS_GROSS_LIKE:
            if r.get(k):
                print(f"      {k:<20} {r[k]:>12}   mod500 = {cents(r[k]) % 500:>4}")

    with open(os.path.join(OUT, "cent_lattice_solutions.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["instrument", "qty", "comm_per_contract_rt", "comm_per_round_turn"])
        for s in sols:
            w.writerow([s["instrument"], s["qty"], s["comm_per_contract_rt"],
                        s["comm_per_round_turn"]])

    print("\n" + "=" * 78)
    print("C4 - the -$2,600 cap and its overshoots")
    print("=" * 78)
    ll = sorted(((cents(r["largest_loss_all"]) / 100.0, r["image_id"], r["report_end"],
                  cents(r["commission_total"]) != 0) for r in recs))
    print(f"{'largest_loss':>13}{'points@$20':>12}  record        window end   kind")
    for v, img, d, is_tp in ll:
        print(f"{v:>13.2f}{abs(v)/20.0:>12.2f}  {img}  {d}   "
              f"{'TradePerf' if is_tp else 'SA backtest'}")
    over = [x for x in ll if x[0] < -2600.0]
    print(f"\nrecords exceeding the -$2,600 cap: {len(over)}")
    for v, img, d, is_tp in over:
        print(f"   {img} {d}: {v:.2f} = {abs(v)/20.0:.2f} pts "
              f"(overshoot {abs(v)/20.0 - 130.0:+.2f} pts) "
              f"{'LIVE' if is_tp else 'BACKTEST'}")
    bt = [abs(v)/20.0 - 130.0 for v, _, _, tp_ in over if not tp_]
    lv = [abs(v)/20.0 - 130.0 for v, _, _, tp_ in over if tp_]
    if bt and lv:
        print(f"\nP4_1 discriminator: max BACKTEST overshoot {max(bt):+.2f} pts, "
              f"max LIVE overshoot {max(lv):+.2f} pts")
        print(f"     RIVAL B predicts LIVE >= BACKTEST -> "
              f"{'CONSISTENT with RIVAL B (gap overshoot)' if max(lv) >= max(bt) else 'FAVOURS RIVAL A'}")
    at_cap = [x for x in ll if abs(x[0] + 2600.0) < 0.005]
    print(f"\nP4_2 records sitting EXACTLY at -$2,600.00: {len(at_cap)} of {len(ll)}")
    below = [x for x in ll if -2600.0 < x[0] < 0]
    print(f"     records strictly inside the cap: {len(below)}")
    print(f"     -> a cap produces a SPIKE at the cap plus a thin overshoot tail; "
          f"spike size = {len(at_cap)}/{len(ll)} = {100*len(at_cap)/len(ll):.0f}%")


if __name__ == "__main__":
    c1_c2()
    c3_c4()
