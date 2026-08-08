# RT-1 — ATTACK THE KILLS (independent red team, W6)

Charter: `specs/W6_fss10_redteam.md` §RT, lens RT-1. Date: 2026-08-08 (run 2026-08-07 wall).
Reviewer: independent adversarial pass; no access to RT-2 output. Scope: the 14 family
kills + the C5 predictability ceiling. Method: every load-bearing number was either
re-derived from the committed CSVs/parquets or re-simulated read-only from
`substrate/sechilo/NQ` + `substrate/grid1s/NQ`. No run dirs touched, no sealed dates
(≥2026-06-01) read, no confirmation-pool sessions read, no commits.

Reconciliation of the audit itself: my independent re-implementation of the W3-1
sequential simulator reproduces the committed pooled numbers exactly (e.g. k=10 long
24/8: n=12,630, P(tgt)=0.2544, net C1 −2.728 vs report −2.73; k=30 long 32/10:
−2.306 vs −2.31), and my independent 30s-clock excursion scan reproduces the census
unconditional surface to 4 dp (0.2525/0.2488/0.2361/0.2328). The audit and the audited
object agree before any attack is mounted.

---

## 1. Cross-cutting attacks (charter items a–g) — measured, not asserted

### 1.1 (d) The conservative same-second→adverse tie rule: bias BOUNDED, negligible

Re-simulated all 8 W3-1 primary configs (D=12, delay=0, 37 sessions) under BOTH tie
rules, counting ties (episodes whose resolving second crossed both barriers):

| config | ties/episodes | net C1 adverse-rule | net C1 target-first | Δ |
|---|---|---|---|---|
| k10 long 24/8 | 23/12,630 (0.18%) | −2.728 | −2.670 | +0.058 |
| k10 long 32/10 | 7/11,528 (0.06%) | −2.732 | −2.706 | +0.026 |
| k10 short 24/8 | 21/12,744 (0.16%) | −2.867 | −2.814 | +0.053 |
| k10 short 32/10 | 7/11,643 (0.06%) | −2.716 | −2.691 | +0.025 |
| k30 long 24/8 | 18/11,566 (0.16%) | −2.486 | −2.436 | +0.050 |
| k30 long 32/10 | 8/10,586 (0.08%) | −2.306 | −2.274 | +0.032 |
| k30 short 24/8 | 16/11,809 (0.14%) | −2.600 | −2.557 | +0.043 |
| k30 short 32/10 | 2/10,816 (0.02%) | −2.260 | −2.252 | +0.008 |

A tie requires a single second whose mid range spans A+B (32–42t); this is rare even on
this high-vol tape. **Worst-case bias of the frozen tie rule: ≤ +0.06t/trade and
≤ +0.2pp of P(tgt) — three orders of magnitude below the 2.3–2.9t deficits. Cannot flip
any kill.** The same convention is used in the census surface, in every W4/W5 family sim
and in the C5 labels, so lift comparisons are internally consistent as well.

### 1.2 (e) 1s-grid vs tick truth: intra-second flicker bias bounded by an extreme

The real 1s-grid worry is not ties, it is that `mid_high`/`mid_low` are quote-mid
extremes within the second: a fleeting BBO flicker can hit the NEAR stop (B=8–10t) that
trade prices never hit, while the FAR target (24–32t) is much less exposed —
an asymmetric anti-strategy bias. Bound: I re-ran the 8 W3-1 primaries evaluating
barriers on `mid_last` ONLY (i.e., pretending EVERY intra-second extreme is phantom —
an indefensibly optimistic extreme, since I-2 showed mid is clean of Roll bounce and the
sechilo extremes are mostly real):

| config | net C1 frozen | net C1 close-only extreme | Δ |
|---|---|---|---|
| k10 long 24/8 | −2.728 | −1.286 | +1.44 |
| k10 long 32/10 | −2.732 | −1.099 | +1.63 |
| k10 short 24/8 | −2.867 | −1.314 | +1.55 |
| k10 short 32/10 | −2.716 | −1.347 | +1.37 |
| k30 long 24/8 | −2.486 | −1.163 | +1.32 |
| k30 long 32/10 | −2.306 | −0.889 | +1.42 |
| k30 short 24/8 | −2.600 | −1.074 | +1.53 |
| k30 short 32/10 | −2.260 | −0.893 | +1.37 |

**Even under the unphysical extreme, every config stays negative (−0.89 to −1.35t).**
The total barrier-evaluation convention bias is bounded at ~+1.3–1.6t/trade at these
brackets; the realistic value is a fraction of that, and it is partly offset by two
optimistic conventions running the other way (entry at mid on the trigger second;
stops booked at exactly −B with no through-print slippage). Every FSS kill's deficit
(2.2–4.6t at the primaries) exceeds the full bound.

**Convention sensitivity of the "needed lift" constants**: the same close-only extreme
raises the unconditional surface p_tgt by +2.8 to +3.5pp (24/8 long 0.2525→0.2876,
short 0.2488→0.2821; 32/10 long 0.2361→0.2669, short 0.2328→0.2605). Two consequences:
(i) conditional and unconditional shift together, so **lift-based kill logic
(+1–2pp measured vs 7–10pp needed) is convention-invariant to first order** — verified:
W3-1 close-only lift is +1.7–2.3pp vs frozen +1.5–1.9pp; (ii) the absolute gap
"7.0–9.1pp" would shrink to ~4.0–5.8pp under the extreme. All measured conditional
lifts (max +2.42pp anywhere in the campaign) still fall short of even the reduced
gap, but closure language should say the gap constant carries ~±3pp of barrier-
convention uncertainty (see §3 on C5).

### 1.3 (c) Costs: no double-counting found; errors run in the PRO-family direction

- C1 = $4.36 + 2×1t = 2.872t: verified against EXECUTION_MODEL.md; the MNQ double-count
  was already caught and corrected (DR-E) and touches no kill.
- W4-A passive C1p = 1.872t (commission + 1t market exit only) is correct for
  limit-entry/market-exit; the 1t passive stress is applied via price, not double-charged.
- Entry at mid + 1t/side slip vs measured in-state spread 2.42t (census): C1 is mildly
  OPTIMISTIC in-state (~0.2–0.4t light), i.e., the true kills are slightly deeper than
  reported. No kill rests on overstated friction.
- Kills where gross is already ≤ 0 pre-cost (FSS-1 market −0.93t, FSS-3 ~−0.3t, W3-1
  direct, Z1 direct) are cost-model-independent.

### 1.4 (a) Non-binding gates inventory (verified from committed artifacts)

| family | distinguishing condition | binds? | evidence |
|---|---|---|---|
| W5-C1 | 2t recovery off trailing-30s low | **NO — inert** | `w5c1_pooled.csv`: entry_rate 0.9999–1.0000, n_exp = 0 across all 24 configs, mean lag 2.3–2.4s |
| W5-C3 | context 12–24t/120s before probe | **near-inert** | `w5c3_pooled.csv`: probes/context = 97.3% pooled — context adds ~nothing; the >2t-undercut cancel (54.9%) and ≥50% recovery do bind |
| W3-1 | 10–30s counter-move ≥ D | semi-inert (near-permanent state) | 300–400 epi/day, documented in w31_report |
| W5-C4 FSS-7 | ret20 ≥ 12t & retrace ≤ 0.25 | binds (16% of seconds) but zero information | lift −0.79..+0.53pp on 18,962 episodes |
| W4-C pierce=4 corner | reclaim window W | **W inert at pierce=4** | `w4c_pooled.csv`: ONL reclaim long 24/8 has IDENTICAL n=159, p_tgt=0.3082, net −1.010 for W=30/60/120 |
| W4-A | eff≥0.5, depth∈[3t,0.5I], rebreak | binds | funnel 2,465 imp → 1,704 pb → 778 epi (45.7% fill) |
| W5-C2 | acceptance closes + AH+1t cross | binds | funnel n_trig 2,598 → 816 episodes; no-cross cancels ~25–35% |
| W4-D | ret≤0.25 cell | binds (15% of episodes) but label-leaked (see §2.8) | `w4d_cells.csv` |

Only W5-C1's DISTINGUISHING mechanism is fully inert; that is exactly the case the
report itself disclosed. Consequence assessed in §2.9.

### 1.5 (f) Regime dependence — the honest scope of every Zone-F kill

All 1s-substrate kills live on 37 sessions, 2025-08-14 → 2026-05-20 (verified from
sechilo filenames), i.e., a single ~9-month high-vol macro regime — this is forced by
the vendor's rolling ~1yr Bid/Ask window, not chosen. The stratification (40 sessions,
seed 20260807) is stratified WITHIN that window. Therefore: every FSS kill is evidence
about "fast NQ states in a high-vol regime". Three kills are specifically
regime-exposed: FSS-6 (§2.11 — the setup does not OCCUR in this regime), the census
gap constants themselves (bracket sizes are vol-relative), and W3-1/W5-C1 (fade
economics in high vol). The §34 declaration form "not found in the tested universe"
already scopes this correctly — the closure text must keep it explicit.

### 1.6 (g) Sequential-sim logic: no errors found

- W3-1: independently re-implemented; exact reproduction (see header). Cooldown 30s
  matches its spec; W4-C/W4-D use 60s per their specs — no spec/code mismatch found.
- W4-B: report's own 10/10 independent trade recompute (`w4b_verify_stdout.txt`);
  0 overlap/cooldown/window violations.
- W5-C4: independent verify pass 8/8 cells exact (`w5c4_verify.txt`).
- W2-0: detector byte-identical to the audited code; OBS reproduces the W1-1 table;
  DIRECT P&L on the martingale null ≈ 0 — the optional-stopping sanity check the
  harness must pass, and does.
- C5: fold/leakage assertions re-verified by me from the committed OOF parquet (§3).
- Shorts are simulated in sign-flipped space in W4-A/W5-C1 etc.; W3-1 short barrier
  algebra checked line-by-line — correct.

---

## 2. Verdicts per kill

Summary: **10 SOUND, 4 FLAWED** (FSS-6-as-kill, B1-as-kill, S2a-as-"definitive",
W5-C1-as-intended-hypothesis). None of the four flaws restores a TESTED fast-scalp
edge at C1; three leave genuinely untested/unresolved territory that closure language
must not describe as falsified.

### 2.1 H-A1 / H-D5 (last-30-min momentum) — **SOUND**
Slope t=1.04 (reproduced exactly from `ha1_last30.csv`: +0.0113, t=1.04), sign 49.3%,
era-split negative since 2023, tercile gradient all-negative. 2022–2026 spans several
regimes. No construction could turn this into a masked edge; 3-min closes and C1 are
immaterial at t≈1. Flip at C1: **no**.

### 2.2 H-D3 @3min (cash-close leak) — **SOUND as scoped, with a dangling retest**
Kill is explicitly "closed at the 3-min construction" and the report is honest that
gross is POSITIVE (+2.61t/day ≈ 0.9× C1) with mechanism-consistent sign (slope
+0.0293, t=0.61 — reproduced). Flaw-adjacent fact: the ONE preregistered 1-min
reconstruction (predictor 15:50→15:55) was reserved in the readout and has never been
run, although the pipeline it was waiting for now exists. This family is the clearest
case in the 14 of "unresolved positive-gross, not refuted". It is ADJACENT_INTRADAY
(does not gate Zone-F §9), but the campaign-level "14/14 killed" tally overstates it.
Flip at (finer-resolution) C1: **plausible** — that is exactly what the reserved retest
would decide. Re-test: run the already-permitted 1-min spec.

### 2.3 Z1-standalone incl. W2-0 null audit — **SOUND (exemplary)**
The audit's own reconciliation reproduces the audited numbers; NULL-3 (empirical |dmid|
with iid random signs) is a correctly matched jump null; the algebra-vs-direct
demonstration (the published "+0.7–0.9t gross" also appears on a martingale) is
decisive; direct-on-null ≈ 0 passes optional stopping. Direct net C1 −2.9 to −9.5t with
day-clustered CIs < 0 through θ=80. I found no way to reconstruct a real edge under any
alternative convention. Flip at C1: **no**.

### 2.4 FSS-4 snapback (W3-1) — **SOUND**
The strongest possible attack was mounted on this family (it is the reference case for
§§1.1–1.2): tie bias ≤ +0.06t; close-only extreme leaves all 8 primaries negative;
lift is convention-invariant (+1.5–2.3pp vs needed 7–10pp under either convention);
delay=1 changes nothing; the trigger is near-permanent so the CIs are high-powered;
C1 optimistic in-state. Coherent negative plateau across 24 configs. Flip at C1: **no**
(the bound in §1.2 is the proof, not an opinion).

### 2.5 FSS-1 impulse-pullback-rebreak market+passive (W4-A) — **SOUND**
0/48; every CI_hi < 0 (max −1.29); gross negative pre-cost at the primary (−0.93t
market), so no cost regime rescues it. Passive fill logic is conservative-correct
(next-second arming, strict trade-through, fill-second barriers) and the
passive-worse-gross finding (−1.50 vs −0.93: adverse selection > spread saving) is a
valuable positive fact, consistent with the external prior. Gates bind (§1.4). Flip at
C1: **no**.

### 2.6 S2a-v01 at owner params (W4-B) — **FLAWED: power; "definitive kill" overstates**
The frozen-rule fail is procedurally valid (fix3 net C1 −1.675 < 0) and the LONG side
is genuinely dead (CI_hi < 0 in 5/7 variants). But the primary readout has n=109,
per-trade sd = 64.1t (recomputed from `w4b_trades.csv`), SE ≈ 6.1t: the pass bar
(net>0 AND CI_lo>−0.5) implicitly required a **≈ +11.5t/trade** true edge — 4× the
entire cost stack — and P(observing net ≤ −1.675 | true edge = +5t) ≈ 14%. The kill is
therefore weak evidence against a moderate edge at the frozen params; what actually
carries the family kill is the secondary bracket readout (n=120, (24,8) −3.989
CI [−6.05,−1.81]; (32,10) −4.239 CI [−6.94,−1.44]) showing the ENTRIES have no
excursion-scale directional edge, plus the decisively dead long side. The short-side
+13.5t (n=43) observation remains an unresolved tail-driven point estimate.
Exact flaw: sample too small for the primary metric at ~3 trades/day × 37 sessions;
"definitive" label unearned for the fixed-time exits. Re-test: nothing at Tier-0 —
a Tier-1 read on the internal confirmation pool (~168 sessions) would shrink SE ~2.4×
and actually resolve ±2–3t. Flip at C1: **statistically possible (CI_hi +11.0),
point estimate says no**; the REJECTED_IDEAS retry clause (new spec, e.g.
side-specific) is the correct standing disposition, and closure language should say
"not positive, underpowered at owner params", not "definitively killed".

### 2.7 FSS-5 sweep→reclaim/continuation (W4-C) — **SOUND (family), one corner noted**
0/144 with primaries at −2.1 to −4.6 and every primary CI < 0; the 5–7% reclaim rate is
a real structural finding. Two honest weaknesses, neither verdict-changing: (i) the
best neighbor corner (ONL reclaim, pierce=4: net −1.010, CI [−2.45,+0.61], n=159 on 18
days; W-window inert there per §1.4) sits INSIDE the §1.2 barrier-convention band — the
only cell in the campaign where a tick-truth re-evaluation could plausibly move the
point estimate to ~breakeven; it would still fail the pass rule (CI_lo −2.4) and it is
a 1-of-144 neighbor under a decisively negative plateau. (ii) trades concentrate on
14–26 unique days per config, so effective day-cluster counts are small; CIs are
day-clustered, correctly, but fragile. PDH/PDL untested (data-blocked, disclosed) —
that is RT-2 territory, not a kill flaw. Flip at C1: **no for the family; marginal-not-
credible for the pierce=4 corner**.

### 2.8 H-B5 spike classification + rule (W4-D) — **SOUND**
Pooled classification is clean (P(CONT) 0.390 < P(REV) 0.407, n=10,061). The only
qualifying cell (ret≤0.25, P(CONT)=0.870) is mechanically label-leaked — the
conditioning window [0,+10s] lies INSIDE the label window measured from spike end —
and the report correctly identifies this and correctly re-anchors the trade readout at
+10s, which kills decisively (−3.461, CI_hi −2.80, both directions). The kill is of the
frozen rule, and the report says so. A shorter conditioning window with earlier entry
is a NEW spec; the measured fast-trigger ladder (max +1–2pp) prices its prior low.
Flip at C1: **no at the frozen construction**.

### 2.9 W5-C1 clean/deep entry — kill **SOUND**; family label **FLAWED (inert mechanism)**
The tested rule is uniformly dead: 0/24, net −2.24 to −2.95, all CI_hi ≤ −1.77, max
lift +1.64pp vs 7.03pp needed, identical under both frozen-text readings. Verified from
`w5c1_pooled.csv`: entry_rate 0.9999–1.0000, n_exp = 0 — the recovery confirmation
NEVER binds, so what was killed is "W3-1 + eff/flow filter + 1–2s delay", not the
intended "deep fade WITH binding recovery confirmation". The report discloses this
precisely and the retry clause requires a demonstrably binding confirmation. For the §9
checklist this means: the W5-1 family AS SPECIFIED is killed; the INTENDED mechanism
(confirmation-gated deep entry) is strictly speaking untested. Given W3-1, C1's
filters, and C5 all measure ≤ 2pp of lift in this state space, the prior that a binding
confirmation finds 7pp is low — but "killed" ≠ "tested" here. Exact flaw: gate
constant (2t vs trailing-30s close-low) below the noise floor of the state it gates.
Re-test: a confirmation that binds (e.g., threshold scaled to trailing rv, or
completed-bar reclaim). Flip at C1: **no for the tested rule; unknown for the intended
mechanism** — should be carried on RT-2's untested-list side of the ledger, not as a
second independent kill.

### 2.10 Fast FSS-2 15s/30s (W5-C2) — **SOUND**
0/16, all CI_hi < 0 (best −0.762), gross barely ≥ 0 in the single best cell so no cost
engineering rescues; funnel binds (§1.4); the internal gradient (more confirmation →
loses less) points at "trade never", the signature of genuine absence rather than a
mis-tuned edge. Together with S2a (1-min) and FSS-1, breakout-continuation is now dead
at four clocks with consistent failure geometry. Flip at C1: **no**.

### 2.11 FSS-6 compression→expansion (W5-C4) — **FLAWED as a "kill": it is a
non-occurrence result in a sample where the setup cannot occur**
The measurement is correct (336/818,965 compression seconds = 0.041%; 5 triggers, all
on the Labor-Day session; independent verify 0/37 mismatches). But a family whose
precondition occurs 5 times in 37 high-vol sessions has not been TESTED for edge — it
has been shown ABSENT from this regime. In a mid/low-vol regime an 8t/120s range is
routine; the kill cannot speak to that regime, and backward L2 data is vendor-blocked.
Exact flaw: regime-specificity of the support, presented in the 14/14 kill count.
Re-test: same definition on future low-vol tape (or archived ES-era analogue) once
available. Flip at C1: **unknowable from this sample — untested, not falsified.**
Closure language must class FSS-6 as "not occurring in the tested regime".
FSS-7 velocity/low-retracement, by contrast, is a **SOUND** robust kill (18,962
episodes, lift −0.79..+0.53pp, all CI_hi ≤ −2.12).

### 2.12 B1 overnight 16:44→09:30 — **FLAWED as a "kill": the frozen bar is
unsatisfiable at its own effect size, and the extension gate is a catch-22**
The measurement is honest and well-audited (roll-gap detector, contamination handling,
correlation ρ=0.015). The flaw is the decision design, recomputed from
`w5b1_nightly.csv` (sd = 577.6t, n = 1,092, SE = 17.5t):
- To pass "CI_lo > 0" at the frozen economic bar (+4t/night) requires ≈ 80,000 nights
  ≈ **318 years**. The rule could never certify the effect it defines as promising.
- Even at the OBSERVED +17.2t/night, certification needs ≈ 4,300 nights ≈ 17 years.
- The 2005+ extension (~5,300 nights) would give SE ≈ 7.9t — t ≈ 2.2 at +17.2t — i.e.,
  the extension is precisely what could resolve the question, and the frozen rule
  blocked the extension BECAUSE the small sample was unresolved.
The point estimate exceeded the +4t bar more than 4×, the one frozen conditional
(prior-RTH-down +28.4 vs +7.8) moved the mechanism-consistent way, and ρ vs Solar is
~0. Counting this as one of "14 killed" misstates the evidence. Exact flaw: power/
gate design (significance demanded of a 0.03-Sharpe/night effect on 4.4 years).
Re-test: 2005+ as a MEASUREMENT study (the report itself names this), new frozen spec.
Flip: **plausibly a real family** — cannot flip Zone-F economics (it is Program B, not
a C1 bracket trade), but the closure narrative must carry it as unresolved.

### 2.13 W5-C3 failed-opposite-probe — **SOUND**
0/36 with NEGATIVE lift in every cell — conditioning selects seconds slightly worse
than unconditional; the setup is near-vacuous (97.3% context→probe, verified pooled
from `w5c3_pooled.csv`) and the ≥50%-recovery entry is structurally late, both
disclosed. The near-vacuity means the family as specced mostly re-tested the
unconditional surface at a locally rich entry price — which is itself the informative
result: the grammar contains nothing. A non-vacuous probe definition is a new spec
(retry clause already says so). Flip at C1: **no**.

### 2.14 The census + measured-lift ladder (supporting constants) — SOUND with one flag
The gap constants (7.0–9.1pp) and the signal ladder (+0.2–0.6pp micro, +1–2pp fast
trigger) were re-verified where they enter kills; the barrier-convention sensitivity of
the ABSOLUTE gap (±3pp, §1.2) does not change any family verdict because measured
lifts are 3–8pp short of even the most optimistic gap, but the "order of magnitude
short" phrasing in some reports should be read as "3–8× short".

---

## 3. C5 predictability ceiling — audit

**Verdict: SOUND as an average-case ceiling; two scope caveats for §9 wording.**

Verified from committed artifacts (`w5c5_oof_predictions.parquet`, 177,368 rows):
- **Fold construction**: 4 validation folds, sessions disjoint (checked pairwise),
  strictly chronological (fold-i max session < fold-i+1 min session: s20251128 <
  s20251209 < … < s20260417), expanding train. Matches spec. The two leakage
  assertions (±1000t label perturbation; train<val ordering) are printed in stdout and
  are the right tests.
- **Headline lifts reproduce exactly** from the OOF parquet: short 24/8 hgb +2.42pp,
  long 24/8 hgb +1.69pp (my recomputation, per-fold 90th-percentile thresholds).
- **Threshold selection**: top decile cut within each VALIDATION fold from validation
  predictions. This is a small anti-conservative bias (a deployable rule must set the
  threshold from training data), i.e., it can only OVERSTATE the ceiling — the negative
  finding is a fortiori. Correctly disclosed.
- **Clock**: identical to the census surface (base rates match to 4dp — reproduced
  independently in §1.2), so the gap comparison is apples-to-apples.
- **Feature completeness vs the census**: the 27 features = the census library's 26
  discriminator features + tod, verified by set-diff against `census_features.csv`.
  Nothing the census measured is missing. Excluded by design: book size/depth (L3
  semantics coarse), ES (deferred to FSS-10/T2 — correctly, since W6-T2 reruns this
  exact protocol with ES features), calendar-event anchoring, level-distance features
  beyond session hi/lo (no ON/OR distances — those families were tested directly in
  W4-C instead). pyGAM absent (2 of 3 model families run) — a real but minor gap; a
  GAM sits between logit and depth-3 HGB in capacity and would be unlikely to find what
  neither neighbor finds.
- **Caveat 1 — rare-state power**: top-decile lift on an unconditional 30s panel
  (~22k validation rows per label) DILUTES any state occupying ≪10% of seconds. A true
  state firing ~2–5×/day with +10pp lift would contribute < 0.5pp to top-decile lift —
  invisible to C5. The direct FSS family tests partially cover this hole, but only for
  the grammars actually specced. C5 therefore proves "no broad conditioning of ≥5pp
  exists in this library", NOT "no rare state exists". The §9 wording should keep the
  ceiling claim tied to the information set AND the unconditional-clock design.
- **Caveat 2 — gap yardstick convention**: per §1.2 the 7.0–9.1pp gap is measured under
  the conservative barrier rule; the convention-consistent comparison (lift vs gap,
  both conservative) is valid, but the absolute "cost wall is 3–4× higher" statement
  ranges from ~1.7× to ~4× across barrier conventions. Under EVERY convention the
  best lift (+2.42pp) is below the wall.
- Brier skills negative and calibration flat across all 8 pairs: the models learn vol,
  not direction — consistent with the census pre-state finding. No contradiction found.

---

## 4. Bottom line for the §9 decision

1. **No construction flaw was found that could flip any tested FAST_STRUCTURAL family
   kill at C1.** The two generic conventions attacked hardest (same-second→adverse,
   1s-grid extremes) are bounded at +0.06t and +1.3–1.6t (unphysical extreme)
   respectively, against deficits of 2.2–4.6t; costs contain no double-count and lean
   optimistic; sequential-sim logic reproduces independently everywhere it was
   re-implemented.
2. **Four verdicts carry real defects — of scope, power, or labeling, not of masked
   edges**: FSS-6 (non-occurrence ≠ kill; regime-blocked), B1 (unsatisfiable
   significance bar + extension catch-22; plausibly a real family), S2a ("definitive"
   unearned on n=109; short side unresolved), W5-C1 (intended mechanism untested —
   its distinguishing gate is provably inert). H-D3 additionally has a preregistered
   1-min retest that was reserved and never run despite the pipeline now existing.
3. **C5 is sound but is an average-case ceiling** with no power against rare states and
   a convention-dependent absolute yardstick; W6-T2's ES rerun inherits both caveats.
4. **Therefore**: RT-1 does NOT block the §34 declaration in its mandated form
   ("no qualified fast NQ scalping edge found in the tested research universe"),
   PROVIDED the declaration text: (i) scopes the universe to the 2025-08→2026-05
   high-vol regime on 36 effective sessions; (ii) lists FSS-6 as not-occurring-in-
   regime rather than falsified; (iii) carries B1, S2a-short-side, H-D3@1min, and
   binding-recovery deep-entry as UNRESOLVED (Program-B / future-spec items), not as
   kills; and (iv) states the C5 ceiling as library-and-clock-relative with the
   rare-state limitation. Items (ii) and (iii) do not reopen Zone F at C1 — none of
   them is a fast-scalp edge claim that survived testing — but writing them as kills
   would misstate what the campaign actually knows.

Artifacts of this audit: this file. Re-simulation code was run from the session
scratchpad (read-only on substrate); the tie-bias and close-only tables above are the
complete outputs. Every number cited appears in the named committed files or in the
tables printed here.
