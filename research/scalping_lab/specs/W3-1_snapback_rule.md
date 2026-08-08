# W3-1 — SNAPBACK rule family, first forward test (Zone F, FSS-4 flavored)

Status: FROZEN before any readout. Date: 2026-08-08. Family: FAST_STRUCTURAL / FSS-4.
Source hypothesis: W2-1 census (committed e3319a2): the only strong directional
precursor of ≥20t/60s moves is a CONTRARIAN 5–30s counter-move (ret5/ret10 up-vs-down
effect ~0.5); viability gap at 24–32t brackets is ~7–10pp. This spec converts that
retrospective observation into a preregistered forward rule. The census conditional is
P(precursor | move); this test measures P(move | precursor) — inversion may fail.

## Rule (frozen)

1s decision clock, RTH (09:30–16:00 ET), quote-alive (upd in trailing 60s > 0),
37 L2 discovery sessions, sechilo mid_last/mid_high/mid_low (ticks).

- Trigger: ret_k(t) = mid_last(t) − mid_last(t−k).
  LONG if ret_k(t) ≤ −D (fade the fast drop); SHORT if ret_k(t) ≥ +D.
- PRIMARY grid (8 configs, DoF charge 8): k ∈ {10, 30}s × D = 12t ×
  bracket (A,B) ∈ {(24,8), (32,10)} × {LONG, SHORT}.
- ROBUSTNESS neighbors (reported always, never selected on): D ∈ {8, 16}.
- Sequential episode simulation (no overlapping fake sample): enter at mid_last(t)
  when triggered and flat and cooldown elapsed; position resolves at first barrier hit
  on per-second hi/lo (same-second both-crossed → adverse, conservative) or at cap
  300s → exit at mid_last(t_cap). Cooldown after resolution: 30s.
- Latency stress: entry at mid_last(t+1) (1s delay), same barriers off the same entry
  reference; reported for every config.

## Economics (frozen)

Per trade net ticks: target +A − c; adverse −B − c; cap-exit (mid − entry)·dir − c.
c = 2.872 (C1, promotion truth) and 4.872 (C2, mandatory stress). Entry at mid is
optimistic by construction — census showed in-state spread ≈ 2.4t; C2 column is the
honest stress. Metrics per config: episodes, epi/day, unique days, P(target first),
P(adverse first), P(cap), net t/trade C1 and C2 with day-clustered 95% CI (session
bootstrap, seed 20260808), win rate vs frozen break-even, long/short and
time-block diagnostics. Diagnostic split (NO selection): spread_t(t) ≤ 2 vs > 2.

## Verdict rules (frozen)

- A config passes Tier-0 iff net C1/trade > 0 AND day-clustered CI lower bound > −0.5t.
- FAMILY verdict is joint over the 8 primary configs (plateau logic, Amendment 4 §29):
  isolated single-config positives with negative neighbors = FRAGILE, not a pass.
- If all primary configs fail at C1: this parameterization of snapback is REJECTED at
  Tier-0; entry goes to REJECTED_IDEAS with the P(move|precursor) inversion documented;
  remaining FSS families proceed unaffected.
- Survivors (if any) go to tick-stream re-evaluation + BBO_EXEC diagnostic before any
  Tier-1 confirmation claim. No re-tuning of D/k/brackets on this sample beyond the
  frozen neighbors.

Artifacts: `artifacts/w31_snapback/w31_results.csv`, `w31_report.md`.
Code: `src/python/w31_snapback.py`. Registry: S8 (+robustness rows not separately
numbered; census-derived, DoF 8 charged).
