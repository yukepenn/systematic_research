"""G2_F7 S2 — robustness battery on the reconciled event set, trial G00035.

R_a concentration (gate), R_b LOYO-modern (gate), R_c late-entry positive control
re-simulated from the substrate (gate), R_d monotonicity (reported), R_e $45 stress
(reported). Printed by program; V7-V11 of out/spec_resolutions_verifier.txt.
"""
import json
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from engine import OUT, COST35, COST45, load_bars, session_table, build_events  # noqa: E402

L = []


def P(s=""):
    print(s)
    L.append(s)


def main():
    st1 = json.load(open(os.path.join(OUT, "state_s1.json"), encoding="utf-8"))
    assert st1["s1_pass"], "S1 did not pass; S2 must not run"
    rec = pd.read_csv(os.path.join(OUT, "reconciled_events.csv"))
    rec["net35"] = rec["net35_pts"]
    N = len(rec)
    assert N == st1["n_reconciled"]

    P("=" * 100)
    P("G2_F7_AUCTREV_CERT_20260829 — S2 ROBUSTNESS on the reconciled event set (trial G00035)")
    P("printed by srcV/s2_robustness.py — POINTS-based, $35/ctrRT = 1.75 pts unless stated")
    P(f"reconciled events N = {N} (S1 intersection, primary recorded values)")
    P("=" * 100)

    mean_ontime = float(rec["net35"].mean())
    total = float(rec["net35"].sum())

    # ---- R_a concentration (V7) -------------------------------------------------------
    k = math.ceil(0.10 * N)
    topk = rec["net35"].nlargest(k)
    conc = float(topk.sum()) / total
    P()
    P(f"R_a  top-decile concentration: k = ceil(0.10*{N}) = {k}")
    P(f"     sum of {k} largest net35 = {topk.sum():+.2f} pts; total net = {total:+.2f} pts")
    P(f"     concentration = {conc*100:.1f}%  (gate <= 40%)")
    ra = conc <= 0.40

    # ---- R_b LOYO-modern (V8) ---------------------------------------------------------
    P()
    P("R_b  LOYO-modern: era-2 (2016..2026/05) net with each single year excluded")
    modern = rec[rec["session_id"] >= "2016-01-01"]  # era-2 by signal session (R5)
    yrs = modern["session_id"].str.slice(0, 4).astype(int)
    P(f"     modern events N = {len(modern)}; total modern net = {modern['net35'].sum():+.2f} pts")
    rb = True
    for y in range(2016, 2027):
        ex = float(modern.loc[yrs != y, "net35"].sum())
        ny = int((yrs == y).sum())
        ok = ex > 0
        rb &= ok
        P(f"       excl {y} (drops {ny:3d} events): net {ex:+9.2f} pts  {'PASS' if ok else 'FAIL'}")

    # ---- R_c late-entry positive control (V9) — re-simulated from substrate ----------
    P()
    P("R_c  late-entry positive control: enter at qualifying session i+1's (16:00,17:00] first-bar")
    P("     OPEN, exit at session i+2's 09:30 seed close; same $35 cost; primary-rule session table")
    bars = load_bars()
    qP = session_table(bars, "morning")
    late, cnt = build_events(qP, bars, "bottom", entry_offset=1)
    late = late[late["session_id"].isin(set(rec["session_id"]))]
    mean_late = float(late["net35"].mean())
    degr = 1.0 - mean_late / mean_ontime
    rc = mean_late <= 0.5 * mean_ontime
    P(f"     late trades on reconciled signals: N = {len(late)} "
      f"(signals {cnt['signals']}, dropped no-next {cnt['drop_next']}, no-entry {cnt['drop_entry']})")
    P(f"     on-time mean net/event = {mean_ontime:+.4f} pts; one-session-late mean = {mean_late:+.4f} pts")
    P(f"     degradation = {degr*100:.1f}%  (gate: late <= 50% of on-time, i.e. degradation >= 50%)")

    # ---- R_d monotonicity (V10, reported) ---------------------------------------------
    d2, cnt2 = build_events(qP, bars, "dec2")
    mean_d2 = float(d2["net35"].mean())
    P()
    P(f"R_d  monotonicity (REPORTED, non-gate): decile-2 sessions (Q10 <= D < Q20), same policy")
    P(f"     decile-1 (reconciled) mean {mean_ontime:+.4f} pts (N={N}); "
      f"decile-2 mean {mean_d2:+.4f} pts (N={len(d2)})")
    P(f"     decile-2 weaker than decile-1: {mean_d2 < mean_ontime}")

    # ---- R_e $45 stress (V11, reported) -----------------------------------------------
    mean45 = float((rec["gross_pts"] - COST45).mean())
    t45 = mean45 / (float((rec["gross_pts"] - COST45).std(ddof=1)) / np.sqrt(N))
    P()
    P(f"R_e  $45/ctrRT stress (REPORTED, non-gate): mean net/event {mean45:+.4f} pts "
      f"= {mean45*20:+.2f} USD (t={t45:.2f})")

    # ---- gate table -------------------------------------------------------------------
    P()
    P("   GATE   SPEC                                              OBSERVED                VERDICT")
    P("   " + "-" * 92)
    P(f"   R_a    largest 10% of events carry <= 40% of total net   {conc*100:6.1f}%"
      f"{'':17s}{'PASS' if ra else 'FAIL'}")
    P(f"   R_b    modern net > 0 excluding any single year 16-26    min holds: {rb}"
      f"{'':12s}{'PASS' if rb else 'FAIL'}")
    P(f"   R_c    late entry degrades mean net/event >= 50%         {degr*100:6.1f}%"
      f"{'':17s}{'PASS' if rc else 'FAIL'}")
    P(f"   R_d    (reported) decile-2 weaker than decile-1          d1 {mean_ontime:+.2f} d2 {mean_d2:+.2f}     REPORTED")
    P(f"   R_e    (reported) $45/RT stress                          {mean45:+.4f} pts          REPORTED")
    s2_pass = bool(ra and rb and rc)
    P()
    P(f"S2 VERDICT: {'PASS — robustness battery survived' if s2_pass else 'FAIL — object stops at SURVIVED-DISCOVERY + S1 parity'}")
    P("Multiplicity: AUCTREV is 1 of 13 formal GENESIS II objects (~750 prior experiments); "
      "evidence status remains DISCOVERY_CONSUMED.")

    state = dict(s2_pass=s2_pass, conc=conc, k=k, ra=bool(ra), rb=bool(rb), rc=bool(rc),
                 mean_ontime_pts=mean_ontime, mean_late_pts=mean_late, degradation=degr,
                 n_late=int(len(late)), mean_dec2_pts=mean_d2, n_dec2=int(len(d2)),
                 mean_net45_pts=mean45, n_reconciled=N)
    with open(os.path.join(OUT, "state_s2.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=1)
    text = "\n".join(L) + "\n"
    with open(os.path.join(OUT, "S2_robustness.txt"), "wb") as f:
        f.write(text.encode("utf-8"))
    assert os.path.getsize(os.path.join(OUT, "S2_robustness.txt")) > 0


if __name__ == "__main__":
    main()
