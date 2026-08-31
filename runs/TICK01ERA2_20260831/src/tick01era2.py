"""TICK01ERA2_20260831 - the FROZEN G2_F1_TICK01 mechanism on 2014/2016/2018/2019/2020/2021.

Spec runs/TICK01ERA2_20260831/spec.yaml committed BEFORE this file produced anything.

The mechanism is IMPORTED from runs/TICK01ERA_20260831/src/tick01era.py, which itself copied
detect_events / cluster_t / build_grid verbatim from runs/G2_F1_TICK01_20260829/src/tick01.py.
Importing rather than restating is deliberate: a restated automaton can drift between runs, an
imported one cannot. TRIG, REARM, H_TARGET, H_DIAG, MDE_K and the three gate predicates are the
same objects in memory as in TICK01ERA.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "runs", "TICK01ERA_20260831", "src"))

import tick01era as F  # the FROZEN mechanism - not re-implemented here

RUN = os.path.join(ROOT, "runs", "TICK01ERA2_20260831")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

YEARS2 = [2014, 2016, 2018, 2019, 2020, 2021]

# Re-point the frozen module's writers at THIS run, and widen its expiry-key year set so the
# NT8 display symbols of these six years resolve. Nothing about the automaton changes.
F.YEARS = YEARS2
F._log = open(os.path.join(OUT, "tick01era2_log.txt"), "w", encoding="utf-8")
F._gate = open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8")
F.OUT = OUT
P, G = F.P, F.G


def main():
    P("=" * 100)
    P("=== TICK01ERA2 - frozen G2_F1_TICK01 mechanism, unchanged, on "
      + " / ".join(str(y) for y in YEARS2))
    P(f"=== TRIG {F.TRIG} REARM {F.REARM} H_TARGET {F.H_TARGET} MDE_K {F.MDE_K} "
      f"(inherited from G2_F1_TICK01 via TICK01ERA; none chosen here)")
    P("=== population declared in spec BEFORE any count existed; disjoint from TICK01ERA's "
      "{2013, 2015, 2017}")
    P("=" * 100)

    frames, provs = {}, []
    for y in YEARS2:
        tick, nq, prov = F.load_era(y)
        provs.append(prov)
        fr, ns = F.build_grid(tick, nq)
        frames[y] = (fr, ns)
    pd.DataFrame(provs).to_csv(os.path.join(OUT, "manifest.csv"), index=False)
    P("")
    P("    frozen manifest -> out/manifest.csv")
    for pr in provs:
        P(f"      {pr['year']}  sha256 {pr['sha256'][:16]}  rows {pr['rows']:,}  "
          f"tick dates {pr['tick_dates']:,}  NQ close "
          f"{pr['nq_close_min']:,.2f}..{pr['nq_close_max']:,.2f}  {pr['contracts']}")

    F.threshold_comparability(frames)

    results = [F.evaluate(f"ERA2_{y}", frames[y][0], frames[y][1]) for y in YEARS2]
    pooled = pd.concat([frames[y][0] for y in YEARS2], ignore_index=True)
    res_pool = F.evaluate("ERA2_POOLED", pooled, int(pooled["session"].nunique()))
    results.append(res_pool)

    parts = [r["events"].assign(stratum=r["name"]) for r in results
             if "events" in r and r["name"] != "ERA2_POOLED" and len(r["events"])]
    allev = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    allev.to_csv(os.path.join(OUT, "era2_events.csv"), index=False)
    P("")
    P(f"    out/era2_events.csv: {len(allev):,} detected events preserved")

    # ------------------------------------------------------------------ GATE TABLE
    G("")
    G("=" * 118)
    G("=== GATE TABLE - TICK01ERA2_20260831 - printed by the program, never assembled by hand")
    G("=== mechanism FROZEN from G2_F1_TICK01 (trigger -1000 / re-arm -400 / NQ fwd 15 min)")
    G("=" * 118)
    G("{:<22}{:<5}{:<52}{:<32}{}".format("STRATUM", "GATE", "SPEC", "OBSERVED", "PASS-FAIL"))
    for r in results:
        if r.get("insufficient"):
            G("{:<22}{:<5}{:<52}{:<32}{}".format(
                r["name"], "--", "gate not evaluable",
                "only {} scored events".format(r["n"]), "N/A"))
            continue
        G("{:<22}{:<5}{:<52}{:<32}{}".format(
            r["name"], "T1", "mean fwd15 > 0 AND session-clustered t >= 2.0",
            "mean {:+.3f} bps, t {:+.2f} (n={:,}, G={:,})".format(r["mean"], r["t"], r["n"], r["g"]),
            "PASS" if r["T1"] else "FAIL"))
        G("{:<22}{:<5}{:<52}{:<32}{}".format(
            "", "T2", "event mean > p95 of count-matched same-session draws",
            "event {:+.3f} vs ctrl p95 {:+.3f}".format(r["mean"], r["ctrl_p95"]),
            "PASS" if r["T2"] else "FAIL"))
        G("{:<22}{:<5}{:<52}{:<32}{}".format(
            "", "T3", "real above p95 of session-block circular-shift null",
            "real {:+.3f} vs null p95 {:+.3f}".format(r["mean"], r["null_p95"]),
            "PASS" if r["T3"] else "FAIL"))
        G("{:<22}{:<5}{:<52}{:<32}{}".format(
            "", "", "MDE 2.80*sd/sqrt(n) [printed BEFORE the verdict]",
            "{:.3f} bps = {:.2f}x |mean|".format(r["mde"], r["mde"] / abs(r["mean"])),
            "UNDERPOWERED" if r["mde"] > 2.0 * abs(r["mean"]) else "powered"))
        G("")

    ok = (not res_pool.get("insufficient")) and res_pool["T1"] and res_pool["T2"] and res_pool["T3"]
    G("    VERDICT (ERA2_POOLED only, per the frozen verdict rule): "
      + ("SURVIVES -> the 2026 closure was a DATA-POWER closure"
         if ok else "FAILS -> the closure is a MECHANISM closure, confirmed on an independent, "
                    "event-bearing, out-of-sample era"))
    if not res_pool.get("insufficient"):
        under = res_pool["mde"] > 2.0 * abs(res_pool["mean"])
        G("    UNDERPOWERED_STILL clause (declared in the spec, reported ADDITIONALLY): "
          "MDE {:.3f} vs 2.0x|mean| {:.3f} -> {}".format(
              res_pool["mde"], 2.0 * abs(res_pool["mean"]),
              "the re-test is ITSELF underpowered and closes nothing on its own" if under
              else "the re-test IS powered at the declared bar"))
    G("")
    G("    DESCRIPTIVE ONLY, NO VERDICT ATTACHES (spec: combined_pre2022_reported_but_not_a_gate):")
    G("      TICK01ERA {2013,2015,2017}: 746 sessions, 7 scored events, mean +9.567 bps, t +0.85")
    if not res_pool.get("insufficient"):
        G("      TICK01ERA2 this run: {:,} sessions, {:,} scored events, mean {:+.3f} bps, t {:+.2f}"
          .format(res_pool["sessions"], res_pool["n"], res_pool["mean"], res_pool["t"]))
    G("    MODERN REFERENCE, quoted verbatim from the closed run, NEVER merged with the above:")
    G("      G2_F1_TICK01 2022-01-03..2026-07-31: n=63, mean +2.841 bps, t +0.54, "
      "ctrl p95 +4.366, null p95 +3.885, MDE 15.112 bps = 5.32x |mean| -> T1/T2/T3 all FAIL")
    G("    prohibitions honoured: no threshold search, no horizon selection, no policy, no P&L, "
      "no cost claim, no sealed read, no cross-era pooling.")

    json.dump({r["name"]: {k: (float(v) if isinstance(v, (np.floating, np.integer)) else v)
                           for k, v in r.items() if k != "events"} for r in results},
              open(os.path.join(OUT, "results.json"), "w", encoding="utf-8"),
              indent=2, default=str)
    F._log.close(); F._gate.close()


if __name__ == "__main__":
    main()
