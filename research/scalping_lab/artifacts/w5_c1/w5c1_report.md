# W5-C1 — CLEAN/deep entry readout (FAIL, 0/24 configs pass)

Spec: `research/scalping_lab/specs/W5_programs_wave.md` §C1 (Amendment 6, frozen before
readout). Code: `research/scalping_lab/src/python/w5_c1_cleanentry.py`. Seed 20260808,
1000-rep session (day-clustered) bootstrap. 37 L2 discovery sessions (s20250814 →
s20260520); s20250902 produced zero triggers, so 36 unique episode days.

Mechanical distinction from killed W3-1 (raw immediate fade), per frozen spec:
(a) interaction trigger depth x efficiency x flow — ret30 ≤ −D AND eff60 ≥ 0.12 AND
sflow10 ≤ 0 (LONG; SHORT symmetric); (b) recovery-confirmation entry — wait for
mid_last ≥ trailing-30s low + 2t within 60s of trigger, else cancel; enter at the
recovery-tick second's mid_last. Brackets (20,6), (24,8), (32,10); cap 300s; cooldown
30s; sequential; costs C1=2.872t / C2=4.872t RT.

## Interpretation notes (frozen-text ambiguities, resolved and documented)

1. **"trailing-30s low" series is unnamed in the spec.** Both readings were run, no
   thresholds changed:
   - `lowsrc=close` (PRIMARY): rolling 30s min of `mid_last` (incl. current second).
   - `lowsrc=wick` (sensitivity): rolling 30s min of `mid_low`.
   The wick reading makes the recovery gate a strict no-op (~100% entry rate, mean lag
   1.3s) because intra-second wicks sit below closes during fast drops; the close
   reading was designated primary because it is the only reading under which the
   confirmation can bind. **Verdict is identical under both.**
2. House conventions (as in w31_snapback / w4a_fss1): grid1s LEFT JOIN sechilo on time,
   ffill `mid_last`, fill hi/lo with `mid_last`, drop leading NaN; decision seconds =
   RTH [09:30, 16:00) ET AND trailing-60s (bid_upd+ask_upd) > 0; trigger and entry both
   require decision seconds — a recovery crossing on a dead second kills the setup
   (W4-A convention; 0–2 kills per config); market entry, barrier evaluation starts the
   second AFTER entry; same-second both-barriers-crossed → adverse; cap exit at
   mid_last(entry+300); shorts in sign-flipped space.
3. eff60 = |mid(t) − mid(t−60)| / trailing-60s sum |1s dmid|; sflow10 = trailing-10s
   sum of grid1s `sflow`; recovery window scan starts at trigger+1 ("entry NOT at
   trigger"); recovery-tick low is the rolling value at the check second.

## Headline: lift vs the unconditional excursion surface

Required lift to break even at C1 (census `gap_c1` = BE_C1 − unconditional p_target):
**10.7–10.9 pp for (20,6), 8.7–9.1 pp for (24,8), 7.0–7.4 pp for (32,10).**

Delivered lift across all 24 configs (both readings): **−0.36 pp to +1.64 pp.**
Best cell (close, D=16, long, 32/10): P(tgt)=0.2525 vs census 0.2361 → +1.64 pp, i.e.
~22% of the required 7.03 pp gap. The interaction gate plus recovery confirmation
selects almost nothing beyond the unconditional base rates.

## Pooled results — lowsrc=close (PRIMARY)

| D | dir | A/B | trig | epi | epi/day | days | lag(s) | P(tgt) | census | lift(pp) | BE_C1 | net C1 (t) | 95% CI | net C2 (t) | PASS |
|---|-----|-----|------|-----|---------|------|--------|--------|--------|----------|-------|-----------|--------|-----------|------|
| 12 | long | 20/6 | 7609 | 7608 | 211.33 | 36 | 2.4 | 0.2366 | 0.2345 | +0.21 | 0.3412 | −2.716 | [−2.996, −2.423] | −4.716 | fail * |
| 12 | long | 24/8 | 7288 | 7287 | 202.42 | 36 | 2.3 | 0.2602 | 0.2525 | +0.77 | 0.3397 | −2.538 | [−2.872, −2.197] | −4.538 | fail * |
| 12 | long | 32/10 | 6857 | 6857 | 190.47 | 36 | 2.3 | 0.2520 | 0.2361 | +1.59 | 0.3065 | −2.258 | [−2.679, −1.840] | −4.258 | fail * |
| 12 | short | 20/6 | 7791 | 7790 | 216.39 | 36 | 2.4 | 0.2329 | 0.2323 | +0.06 | 0.3412 | −2.814 | [−3.062, −2.553] | −4.814 | fail * |
| 12 | short | 24/8 | 7436 | 7434 | 206.50 | 36 | 2.4 | 0.2593 | 0.2488 | +1.05 | 0.3397 | −2.564 | [−2.925, −2.185] | −4.564 | fail * |
| 12 | short | 32/10 | 6983 | 6982 | 193.94 | 36 | 2.4 | 0.2428 | 0.2328 | +1.00 | 0.3065 | −2.636 | [−3.169, −2.140] | −4.636 | fail * |
| 16 | long | 20/6 | 6803 | 6802 | 188.94 | 36 | 2.3 | 0.2388 | 0.2345 | +0.43 | 0.3412 | −2.663 | [−2.959, −2.363] | −4.663 | fail |
| 16 | long | 24/8 | 6560 | 6558 | 182.17 | 36 | 2.3 | 0.2627 | 0.2525 | +1.02 | 0.3397 | −2.463 | [−2.800, −2.117] | −4.463 | fail |
| 16 | long | 32/10 | 6209 | 6209 | 172.47 | 36 | 2.3 | 0.2525 | 0.2361 | +1.64 | 0.3065 | −2.241 | [−2.690, −1.768] | −4.241 | fail |
| 16 | short | 20/6 | 6933 | 6932 | 192.56 | 36 | 2.4 | 0.2287 | 0.2323 | −0.36 | 0.3412 | −2.925 | [−3.191, −2.660] | −4.925 | fail |
| 16 | short | 24/8 | 6654 | 6653 | 184.81 | 36 | 2.4 | 0.2558 | 0.2488 | +0.70 | 0.3397 | −2.680 | [−3.027, −2.347] | −4.680 | fail |
| 16 | short | 32/10 | 6294 | 6293 | 174.81 | 36 | 2.4 | 0.2367 | 0.2328 | +0.39 | 0.3065 | −2.884 | [−3.425, −2.407] | −4.884 | fail |

(* = primary D=12; D=16 neighbor reported, never selected on. P(tgt) = n_tgt/(n_tgt+n_adv);
cap-outs 0.0–0.5% of episodes. Full tables incl. wick reading, long+short combined, and
per-session rows: `w5c1_pooled.csv`, `w5c1_by_session.csv`, `w5c1_stdout.txt`.)

lowsrc=wick sensitivity: net C1 −2.37 to −2.95t, lift −0.32 to +1.31 pp — same verdict.
Long+short combined (diagnostic): net C1 −2.45 to −2.80t, all CI_hi < −1.7t.

## Findings

1. **FAIL, 0/24.** Every config has net C1 < 0 (−2.24 to −2.95t/trade) with CI_hi ≤
   −1.77t — not near the pass boundary (net C1 > 0 AND CI_lo > −0.5t). Net C2 is ~2t
   worse. Gross per trade is +0.06 to +0.61t on the primary reading — the conditioning
   is not even cost-free-positive by ~2.3t.
2. **The recovery confirmation as frozen does not bind.** Entry rate ≈ 100% of triggers,
   zero 60s-window expirations in 173k+ trigger evaluations, mean trigger→entry lag
   1.3s (wick) / 2.3–2.4s (close). A 2t bounce off the trailing-30s low is smaller than
   routine NQ per-second noise after a ≥12t/30s move, so C1-as-frozen degenerates to
   W3-1 with an eff/flow gate and a 1–2s entry delay.
3. **The interaction gate carries almost no selectivity.** Depth x efficiency x flow
   moves P(target-first) by at most +1.64 pp vs the unconditional surface, against a
   required 7.0–10.9 pp. Consistent with the W3-1 kill and with the census finding that
   post-drop continuation/mean-reversion asymmetry at these horizons is thin.
4. Episode counts are large (172–216 epi/day; the machine is triggered nearly
   continuously during fast tape), so the CIs are tight and the kill is high-powered.

## Verdict (frozen rules)

Pass rule: net C1 > 0 AND CI_lo > −0.5t → **0 / 12 primary-reading configs pass; 0 / 12
sensitivity-reading configs pass.** Family verdict = plateau: the (D x dir x bracket)
plateau is uniformly and deeply negative under both ambiguity readings — no cell, no
neighborhood, no direction is close. **W5-C1 is KILLED.** Per Amendment 6 §7C no
retuning of this loser; any future deep-fade idea must state a mechanical distinction
from BOTH W3-1 and W5-C1 (in particular, a recovery confirmation that actually binds —
the 2t/30s-low construction demonstrably does not on this substrate).

## Artifacts

- `w5c1_by_session.csv` — 888 rows (37 sessions x 2 lowsrc x 2 D x 2 dir x 3 brackets)
- `w5c1_pooled.csv` — 24 pooled config rows with CIs, census comparison, pass flags
- `w5c1_stdout.txt` — full run stdout + consistency checks (row identity
  n = trig − dead − exp holds on all 888 rows)
