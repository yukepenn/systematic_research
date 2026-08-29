"""G2_F7 finalizer — consolidated gate_table.txt, S3 ABORTED record, ledger list.

S3 (trial G00036) is NOT executed because S2 (G00035) failed gates R_a and R_c;
the sequential protocol stops at the first failed stage. Printed by program.
"""
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from engine import OUT  # noqa: E402

MULT_SENT = ("Multiplicity: AUCTREV is 1 of 13 formal GENESIS II objects (~750 prior "
             "experiments); evidence status remains DISCOVERY_CONSUMED.")


def main():
    s1 = json.load(open(os.path.join(OUT, "state_s1.json"), encoding="utf-8"))
    s2 = json.load(open(os.path.join(OUT, "state_s2.json"), encoding="utf-8"))
    assert s1["s1_pass"] and not s2["s2_pass"]

    # ---- S3_portfolio.txt: ABORTED record --------------------------------------------
    s3_lines = [
        "=" * 100,
        "G2_F7_AUCTREV_CERT_20260829 — S3 PORTFOLIO MARGINAL (trial G00036)",
        "printed by srcV/finalize.py",
        "=" * 100,
        "",
        "STAGE NOT EXECUTED — ABORTED: prior stage failed.",
        "S2 (trial G00035) failed gates R_a (top-decile concentration 203.2% vs <= 40%) and",
        "R_c (late-entry degradation 15.4% vs >= 50%). The F7 spec runs stages sequentially",
        "and stops at the first failure; no portfolio economics were computed, and none are",
        "quotable from this run.",
        "",
        "For the record (V12, resolved before any compute): had S3 run, the incumbent book",
        "weekly stream would have been built from runs/WE_W119_BOOKLOSS/out/book_loss_ledger.csv",
        "(recorded per-session book_pnl at the recorded inverse-vol weights 0.473*P1/PCT +",
        "0.527*XM, 2022-07-04..2026-07-31, ISO weeks), validated against the",
        "WE_W103_CONSOLIDATE combinations.csv 'INV-VOL: P1 + XM' aggregates (213 weeks,",
        "$1,141.68/wk raw, maxDD $11,489.40, $2,011.70/wk at the $20,245 normalization).",
        "No gate P_a/P_b/P_c/P_d value exists.",
        "",
        MULT_SENT,
    ]
    with open(os.path.join(OUT, "S3_portfolio.txt"), "wb") as f:
        f.write(("\n".join(s3_lines) + "\n").encode("utf-8"))

    # ---- consolidated gate table ------------------------------------------------------
    g = []
    A = g.append
    A("=" * 100)
    A("G2_F7_AUCTREV_CERT_20260829 — CONSOLIDATED GATE TABLE (certification of AUCTREV, G00032)")
    A("printed by srcV/finalize.py from state_s1.json / state_s2.json — never hand-assembled")
    A("stages sequential: S1 G00034 -> S2 G00035 -> S3 G00036; stop at first failure")
    A("=" * 100)
    A("")
    A("STAGE  GATE      SPEC                                          OBSERVED                    VERDICT")
    A("-" * 100)
    A(f"S1     audit     srcI references no forbidden path             {s1['audit_hits']} grep matches"
      f"{'':15s}PASS")
    A(f"S1     S1-a      event-set agreement >= 99%                    {s1['jaccard']*100:.3f}% (534/535)"
      f"{'':10s}PASS")
    A(f"S1     S1-b      per-event net corr >= 0.99                    {s1['corr']:.6f} on 534 events    PASS")
    A(f"S1     S1-c      total net within 1%                           dev {s1['tot_dev']*100:.3f}% "
      f"({s1['tot_primary_pts']:+.0f} vs {s1['tot_indep_pts']:+.1f} pts)  PASS")
    A(f"S1     class     every disagreement classified                 {s1['n_census_diff']} census + "
      f"{s1['n_event_diff']} event, 1 root cause   DONE")
    A(f"S2     R_a       largest 10% of events carry <= 40% of net     {s2['conc']*100:.1f}%"
      f"{'':21s}FAIL")
    A(f"S2     R_b       LOYO-modern net > 0, all years 2016..2026     min exclusion +3026.25 pts   PASS")
    A(f"S2     R_c       late entry degrades mean net >= 50%           {s2['degradation']*100:.1f}% "
      f"({s2['mean_ontime_pts']:+.2f} -> {s2['mean_late_pts']:+.2f} pts)   FAIL")
    A(f"S2     R_d(rep)  decile-2 weaker than decile-1                 d1 {s2['mean_ontime_pts']:+.2f} / "
      f"d2 {s2['mean_dec2_pts']:+.2f} pts (N={s2['n_dec2']})   REPORTED")
    A(f"S2     R_e(rep)  $45/ctrRT stress                              {s2['mean_net45_pts']:+.4f} pts/event"
      f"{'':8s}REPORTED")
    A("S3     P_a-P_d   (not executed)                                ABORTED: prior stage failed  ABORTED")
    A("-" * 100)
    A("")
    A("VERDICT: S1 PASS, S2 FAIL (R_a, R_c), S3 ABORTED.")
    A("Per spec verdict_ladder: the object stops at its LAST PASSED RUNG — AUCTREV remains")
    A("SURVIVED-DISCOVERY (G00032) and is now additionally INDEPENDENT-IMPLEMENTATION-VERIFIED")
    A("(S1). It is NOT ROBUSTNESS-SUPPORTED and NOT PORTFOLIO-ADDITIVE. The S2 failure modes:")
    A("  R_a: the P&L is tail-carried — the top 54 events hold 203% of total net (the remaining")
    A("       480 events sum NEGATIVE, -5,605 pts). Not a broad edge; a rare-event payoff.")
    A("  R_c: entering one full session late keeps 85% of the economics (+10.17 -> +8.60 pts).")
    A("       The claimed fast overnight auction-reversion mechanism is NOT what pays; the")
    A("       timing test had teeth and it bit — mechanism claim falsified at this geometry.")
    A("Both failures are mechanism-classification findings, not arithmetic disputes: S1 showed")
    A("the two implementations agree to 0.000 pts on every common event.")
    A("")
    A(MULT_SENT)
    A("live_enabled NO. spend $0. No sealed row (>= 2026-08-01) touched; seal_guard passed on")
    A("every load. POINTS-based throughout; substrate sha256 verified == recorded provenance.")
    with open(os.path.join(OUT, "gate_table.txt"), "wb") as f:
        f.write(("\n".join(g) + "\n").encode("utf-8"))

    # ---- ledger list ------------------------------------------------------------------
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    base = dict(hash=None, prev_hash=None, seq=None, kind="RESULT", selected=False,
                pending="orchestrator must chain hash/prev_hash/seq on append", ts_utc=ts)
    entries = [
        dict(base, trial_id="G00034", result="PASS", metrics=dict(
            audit_grep_matches=s1["audit_hits"], event_set_agreement=s1["jaccard"],
            per_event_net_corr=s1["corr"], total_net_primary_pts=s1["tot_primary_pts"],
            total_net_indep_pts=s1["tot_indep_pts"], total_net_dev=s1["tot_dev"],
            n_reconciled=s1["n_reconciled"], n_census_diff=s1["n_census_diff"],
            n_event_diff=s1["n_event_diff"], n_value_mismatch=s1["n_value_mismatch"],
            engine_reproduced_primary=s1["engine_repro_primary"],
            engine_reproduced_indep=s1["engine_repro_indep"]),
            note=("S1 parity: clean-room audit clean (0 forbidden refs); 99.813% event-set "
                  "agreement, corr 1.000000, total net dev 0.341%. All 4 disagreements (3 "
                  "census + 1 event) classified to ONE root cause: F6 R3(c) seed-bar "
                  "ambiguity (time-of-day-on-date vs chronological). Parity CERTIFIED.")),
        dict(base, trial_id="G00035", result="FAIL", metrics=dict(
            gate_Ra=False, gate_Rb=True, gate_Rc=False,
            concentration_top_decile=s2["conc"], k_top=s2["k"],
            mean_ontime_pts=s2["mean_ontime_pts"], mean_late_pts=s2["mean_late_pts"],
            late_degradation=s2["degradation"], n_late=s2["n_late"],
            mean_dec2_pts=s2["mean_dec2_pts"], n_dec2=s2["n_dec2"],
            mean_net45_pts=s2["mean_net45_pts"], n_reconciled=s2["n_reconciled"]),
            note=("S2 robustness FAIL: R_a top-decile concentration 203.2% (<=40% gate) — "
                  "tail-carried P&L, other 480 events sum negative; R_c late-entry control "
                  "degrades only 15.4% (>=50% gate) — fast-reversion mechanism claim "
                  "falsified, payoff persists a full session. R_b LOYO-modern passed (min "
                  "exclusion +3026.25 pts). Object stops at SURVIVED-DISCOVERY + S1 parity.")),
        dict(base, trial_id="G00036", result="ABORTED", metrics={},
            note="prior stage failed"),
    ]
    with open(os.path.join(OUT, "ledger_result_pending.json"), "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=1)
    print("\n".join(g))
    print("\nwrote gate_table.txt, S3_portfolio.txt, ledger_result_pending.json (3 entries)")


if __name__ == "__main__":
    main()
