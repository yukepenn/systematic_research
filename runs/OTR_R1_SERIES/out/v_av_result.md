# TASK V1 — Adversarial verification of the D-gate (tag: v_av)

Scripts: `v_av_1_reimpl.py` (independent re-implementation + label/master check),
`v_av_2_break.py` (+ `v_av_2_break.json`, alternative-rule battery),
`v_av_3_oos.py` / `v_av_4_oos_forensics.py` (Feb-2025 OOS).
Engine written independently from the rule DESCRIPTION (hunt_D_result.md box + task
brief); no calls into `eng.run_wrapper` or `run_r1g.run_integrated`.

## Claim 1 — 42/42 hard-label fit and master numbers: **CONFIRMED**

* Label config (ledger EARLY signals, no B1, guard m<3, X=1600/K=3/C=1000, eve 360'):
  **HARD 42/42, SOFT 1/7, EPS 77/78** — identical to hunt_D's reported scorecard,
  including the identity of every SOFT/EPS failure (01-04 FOMC cluster, 01-12 13:39,
  01-12 20:36). Aggregate **5008 trades / net 244,266.56 / dd −29,077.40 / hold 92.81
  (105.21/80.65)** = hunt_D's table row exactly.
* Integrated config (LATE signals, B1, no guard): **n=5011 L2483/S2528 net=244,589.02
  wr=39.83 pf=1.1269 dd=−29,077.40 hold=93.02 (105.61/80.65)** — matches the claimed
  INT_T1only master to the cent.
* Nuance: under the integrated config the HARD SKIP label 01-08T18:02 is satisfied
  *vacuously* — B1 removes the candidate entirely (my scorer flags MISSING; the trade is
  correctly absent). The open-guard (m<3) and B1 are label-equivalent on Jan but are
  different mechanisms; only 18:01–18:02 fills ever separate them.

## Claim 2 — the gate is uniquely identified: **PARTIAL**

**Structure: confirmed necessary.** Deleting any component breaks HARD labels:
no evening rule → 5 HARD fails; no arming (X=0) → 2; no cum<0 → 3; no per-side consec →
3. Alternative *mechanisms* rejected by HARD labels alone: drawdown-from-high (any D,
armed or pure — always fails the 01-03 16:04 TAKE), arming by loss count / win count,
consecutive-losses-any-side, per-side-total K∈{3,5}, evening band rule. The armed/evening
interlock claim replicates.

**Constants: weakly identified — published intervals are overstated for HARD evidence.**
(full-sim verified at the boundaries)
* X: HARD-only feasible **[1425, 1925]** (bounds: 01-10 high 1419.92 must not arm;
  01-05 high 1937.46 must arm). The claimed lower bound 1536.56 exists only with EPS
  labels (X≤1525 costs 2 EPS).
* noon: **11:00–12:15 ET** all pass — "noon" is not pinned.
* K ∈ {2,3,4}: confirmed.
* C: HARD-feasible **[50, ~2475]** — far wider than the claimed (300.16, 1328.52].
  Reason: the claim's upper bound uses the trader's *actual* 01-04 net (≈−1149), but the
  self-consistent simulated prior is **−5174.42** because the sim wrongly takes the 01-04
  FOMC cluster (the SOFT failures). Until that cluster is reproduced, C is effectively
  unidentified above ~300 (lower end costs EPS only: C=50 → 5 EPS fails).

**Indistinguishable reformulations (pass 42/42 with same SOFT/EPS):**
* `cum <= 0` vs `cum < 0`: **zero** decision differences over the entire 2023-2025 run.
* Gross / points-based accounting (arm at 80 pts, red = gross<0, i.e. commission-free):
  **one** differing trade in two years (2025-01-07, Δnet −874.18). The dollars-vs-points
  and net-vs-gross questions are empirically unanswerable from this data.

**Competitive rival found:** `ALT_loss_side_K4` — block a side after **4 total (not 3
consecutive) same-side session losses**. Passes HARD 42/42 with an *identical* SOFT
(1/7) and EPS (77/78) profile; diverges from the registered rule on 117 trades across 51
sessions; master net **252,218.50** — *closer* to the target 292,172.82 than the
registered rule's 244,245. The Jan labels cannot separate these two. Also surviving:
`ALT_eve_anyred` (evening block after any red day; −6 EPS) and `ALT_arm_bigwin≥2000`
(worse master by −50.7k, +1 EPS fail — soft-rejected).

**Discriminating future evidence:**
1. Per-day trade tables for **2023-02-02 / 02-07 / 07-20 / 08-25** (first
   consec-vs-total disagreement days) — one day's take/skip pattern kills one rival.
2. Any session with prior-day net in (−1000, −50): separates C values and eve_anyred.
3. Any session whose equity high lands in (1425, 1925) before noon: pins X.
4. An after-noon armed day whose equity dips to exactly 0: pins < vs ≤ (until then moot).
5. Reproducing the 01-04 FOMC cluster (signal-stream fix): restores the C upper bound.

## Claim 3 — OOS Feb-2025 (per-window fresh state, late signals, B1): **PARTIAL**

**W0204** (2/3 18:00→2/5 17:00, 2760 bars, 2 sessions; tgt 30 tr 15L/15S net −3805.40):
* NOGATE: 33 tr L17/S16 net −4612.94 hold 68.94, LW/LL exact. The stream contains a
  **cent-exact 30-trade 15L/15S subset netting −3805.40** — two distinct exact
  solutions: rm {08:23L, 12:45L, **20:59S**} (kept hold 60.97) or rm {11:30L, 03:41S,
  14:08L} (kept hold 66.77 — closer to tgt 69.5). Strong support for the late-mode T1
  leg stream itself.
* GATE: blocks exactly the two 02-04-evening trades 19:37L(−859.18)/20:59S(+645.82) via
  the **evening rule** (simulated prior −3228.60). Under exact-solution 1 the trader
  *took* 19:37 (gate wrong 1 of 2); under solution 2 he took *both* (wrong 2 of 2).
  Arithmetically the gate helps: dn +1 vs +3, dnet −594 vs −808; but hold moves away
  (58.2 vs 68.9; tgt 69.5). **Helps on aggregate distance, yet blocks ≥1 trade the
  trader demonstrably took — OOS evidence against the evening rule as formulated.**
  (Echoes the in-sample 01-12-evening EPS failure: trades after big red days do occur.)
* W0209** (2/8 18:00→2/11 17:00; tgt 10 tr 4L/6S net −891.80): NOGATE = GATE = 13 tr
  L6/S7 net +190.66 — **the gate fires nothing** (no evening candidates inside 360';
  02-11 session arms at 2098>1600 after noon but cum>0 and no post-noon losses). Best
  subset (err $10, only solution within $25): trader lacked {13:03L −679, **09:32L
  +1800.82**, 15:39S −29}. Skipping a +1800 winner after two small losses cannot be
  produced by any loss-triggered equity gate → residual gap is signal-stream-level, not
  gating. Gate neither helps nor hurts.
* **The armed-noon rule — the heart of family D — never fires in either window: these
  OOS windows provide zero evidence for or against it.** All 42/42-surviving rule
  variants (X 1450/1600, noon 11:00/12:00, gross/net, eve_anyred) produce byte-identical
  OOS trades here; Feb 2/4-5 and 2/9-11 cannot discriminate them.

## Verdicts

| Claim | Verdict |
|---|---|
| 42/42 HARD fit (label config) | **CONFIRMED** (exact, incl. failure identities) |
| Master numbers INT_T1only | **CONFIRMED** (to the cent) |
| Gate structure (4 components necessary; dd/loss-count/any-side rejected) | **CONFIRMED** |
| Gate constants + exact form identified | **REFUTED as stated** — X/C/noon intervals overstated; cum≤0 and points-basis indistinguishable; `loss_side_K4` rival passes identically and fits master better |
| OOS: gate helps | **PARTIAL** — W0204 aggregate distance improves but ≥1 blocked trade was actually taken (evening rule wounded); W0209 no effect; armed-noon rule untested OOS |
