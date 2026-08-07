# SW02a — Timed-Exit Falsification: **PASS (no fill artifact); bonus finding: 16:30 exit dominates**

2026-08-06. Spec: DISCOVERY_WAVE1_spec.md §1 (preregistered, commit `1b14f9c`). Implementation: frozen replica's own time filter (cross-midnight window `StartTime=180000`), exits are ordinary market orders (L/S-TimeExit) filling at next-bar open — real prints, no new code.

| Exit basis | slip-0 Net | % of baseline | PF | Max DD |
|---|---|---|---|---|
| Session-close print (baseline) | $146,440.60 | 100.0% | 1.1322 | −$22,066.60 |
| ~16:59 fill (EndTime 16:58) | $146,434.96 | **100.0%** | 1.1329 | −$21,951.60 |
| ~16:56 fill | $143,984.32 | 98.3% | 1.1306 | −$22,151.60 |
| ~16:46 fill | $144,502.40 | 98.7% | 1.1311 | −$22,253.52 |
| **~16:31 fill** | **$149,989.72** | **102.4%** | **1.1367** | **−$21,538.52** |

Slip-1 confirmation at 16:58: $118,584.96 = 99.9% of the slip-1 baseline ($118,645.60).

**Verdict (preregistered rule: ≥70% at 16:58 → no material artifact): PASS at 100.0%.** The close-bucket profit is fully achievable one minute early at tradable next-bar-open prices; the external review's last-print-artifact concern is refuted empirically. The 266 TimeExit trades net +$187,370 ≈ the baseline's close bucket (+$189.6k).

**Bonus finding:** the final 30 minutes of holding contribute *negatively* — exiting at ~16:31 yields +$3.5k more net AND a smaller drawdown than holding to the close. The "close-bucket edge" is accumulated during the day by surviving trades, not in the final minutes. A ~16:30 timed exit is a strictly-dominant exit variant candidate (better net, better DD, exits into deep RTH liquidity) — to be treated as an exit-architecture option in Wave-2 candidate assembly, subject to per-year stability checks.

Runs: SW02a_1658_s0/s1, SW02a_1655_s0, SW02a_1645_s0, SW02a_1630_s0 (full payloads under runs/).
