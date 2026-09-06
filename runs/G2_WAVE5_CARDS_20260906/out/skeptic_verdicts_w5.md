# SKEPTIC VERDICTS — GENESIS II Wave 5 (MC-57, MC-58)

Role: adversarial audit of `runs/G2_WAVE5_CARDS_20260906/{MC-57_zb.md, MC-58_rebound.md}`
against `research/genesis2/FAILURE_MEMORY.md`, the W2 pristine-window register
(`runs/G2_WORLDSCAN_W2_20260829/out/skeptic_verdicts_w2.md` §0), the EXEC01 cost truth, and the
substrate manifests. Written 2026-09-06. No git action taken. No data ≥ 2026-08-01 read.

Facts verified against artifacts this session (not taken from the cards):
- `runs/SM1M_ZB_SUBSTRATE/MANIFEST.md`: parquet sha256 `ae04d0a7…`, 923 sessions
  2022-12-27→**2026-07-31** — the store **contains the BURNED Jun–Jul 2026 window**; series is a
  **merge back-adjusted chain with cumulative additive roll offsets** (median −41/32nds in
  late-2025 segments); ZB prints **no bar in zero-trade minutes**.
- `runs/G2_F6_BREADTHPM01_20260829/REPORT.md` (G00033): the dead short is the **full-window
  11:01→15:59** entry at **$25.01/RT** (−$367/event, $143 worse than random shorts, p_one 0.82);
  the post-takeout leg is genuinely unmeasured; the closure itself says a rebound card "enters the
  queue only through a fresh card with that history addressed."
- `runs/TICK01ERA_20260831/spec.yaml`: the pre-2022 $TICK reads run as PROTECTED_CONFIRMATION,
  and the locally acquired pre-2022 store is **non-contiguous: 2013 / 2015 / 2017 only**
  (CAPPROBE01), not "2013-2021".
- `runs/G2_F11_MC54LEG2_VOLFORECAST_20260906/REPORT.md` (G00052): today's NOT-IDENTIFIED verdict
  — a nested vol-forecast "pass" is meaningless when candidate and baseline are collinear;
  identification (VIF) gates are now mandatory equipment for any RV-increment claim.
- FAILURE_MEMORY: no ZB/Treasury/bond row exists (card's grep claim confirmed); "vol-state as
  RISK SPECIFICATION" sits on the NOT-closed list; W118 = event-driven reversal at endogenous
  triggers dead, continuation +$374 at the same bars.

---

## MC-57 — Rates-complex intraday state for NQ · VERDICT: **TRIAGE-HIGH** (with three mandatory spec amendments)

**Attack 1 — RESERVE VIOLATION AS WRITTEN (P-1).** Leg (a)'s baseline "HAR(NQ-RV)+VXN" on a
window that is entirely 2022-12+ is discovery on the **2022+ implied-vol-daily → NQ-outcome
join** — the exact reserve for which W2 stripped MC-38's VXN add-on and held MC-52/56. Putting
the reserve join in the *control arm* does not launder it: the run still learns VXN's 2022+
incremental value and conditions the ZB verdict on it. **Amendment: VXN excluded from BOTH
arms.** Controls = univariate NQ-only HAR (plain HAR-RV — G2_F3 already killed the RS−/ON
refinement) + $0 macro-calendar flags. This is also the MC-53-imported rule the card itself
declares binding, so the fix costs the card nothing it claimed to need.

**Attack 2 — DELEV01 SUBSTRATE TRAP + two load-time traps.** The ZB parquet is an additively
back-adjusted chain with cumulative roll offsets; **percent returns/RV computed on adjusted ZB
levels are era-distorted by construction** (the earlier the segment, the bigger the offset).
Every ZB observable must be **POINTS (32nds) basis**: point returns for corr, diurnal-adjusted
point ranges for RV/expansion thresholds. Second: the parquet runs to 2026-07-31 — the spec must
**hard-drop sessions > 2026-05-31 at load and print the retained boundary** (burned window
inside an owned file is still burned). Third: ZB's sparse minutes force a **pinned alignment
rule** for corr/RV windows (inner-join on common minutes, minimum-coverage per rolling window,
coverage printed) or the corr state is silently RTH-biased and overnight flips are artifacts of
missingness.

**Attack 3 — MECHANICAL CONFOUND + ONE-ERA CAP.** ZB range expansions and corr-flips co-occur
with elevated NQ vol near-mechanically (joint macro shocks); a same-timestamp control alone is
the PDH/PDL geometry trap in cross-asset costume. Legs (b)/(c) controls must ALSO be
**NQ-trailing-60-min-RV-decile matched**, on top of the calendar-flag control. And the entire
window sits in the post-2022-flip corr regime: the "bonds still hedging" cell may be close to
empty — **cell occupancy and per-era event counts print BEFORE any gate; thin cells go
CLOSED-BY-POWER unread.** F11's lesson imported: a **VIF/identification gate** between ZB RV
terms and the NQ RV baseline is mandatory — a collinear "pass" is NOT-IDENTIFIED, not PASS.

**Not a rescue.** No bond/rates row in FAILURE_MEMORY; nearest closures (ESNQ sub-minute
−$503/session, ms-arbitraged 1-min lead-lag, SWING park, H1 daily VX terciles) differ on asset
class, moment, and horizon simultaneously and are honored as in-card bans, not evaded. The lane
occupied (second-moment RISK SPECIFICATION) is explicitly on the NOT-closed register. Modal
outcome is full collapse into the NQ-only controls — and that collapse retires the last
"genuinely new raw surface" flag from external mining, which is bankable.

**FROZEN PRIMARY (leg a, amended):** Population: ZB∩NQ sessions 2022-12-27→2026-05-31
(program-printed n≈860; sessions >2026-05-31 hard-dropped at load; boundary printed). Statistic:
OOS QLIKE improvement (Diebold-Mariano, HAC) for rest-of-session-from-11:00 NQ RV (primary
target; next-session secondary, pre-declared) of HAR(NQ-RV)+macro-calendar-flags AUGMENTED with
pre-declared ZB terms {session/30-min diurnal-adjusted ZB RV in POINTS; 60-min NQ-ZB point-return
corr level/sign (inner-join minutes, min-coverage rule); ZB expansion count} vs the identical
model WITHOUT ZB terms. **VXN in neither arm (P-1).** Frozen split: train 2022-12-27→2024-12-31,
test 2025-01-02→2026-05-31, one fit, no refit. Null: ONE shared per-session circular-shift draw
across legs (a)/(b)/(c) — one family, effective-K corrected. Identification gate: VIF between
each ZB term and the NQ baseline printed; collinear increment ⇒ NOT-IDENTIFIED, not PASS.
MDE-before-looking: DM-detectable QLIKE delta at test-n, per-era session counts, and legs
(b)/(c) event counts (95th-pct expansions; corr-flips ≤−0.3→≥+0.3) printed before any gate.
Legs (b)/(c) controls: same-timestamp AND NQ-RV-decile-matched AND macro-calendar-flag — ZB must
add beyond all three or the leg is recorded a redundancy closure. Cost floor: none (conditioner;
no trades). Classification locked: RISK SPECIFICATION / REGIME ROUTING; any tie = redundancy
closure banked.

**Reserve ruling:** As written the card **consumes P-1** via its VXN baseline → gated amendment
above removes the consumption; with VXN out, no frozen reserve is touched. P-2 (2019+
multi-market **daily** panel) is not consumed as registered — new intraday substrate, second-
moment role — but with a rider: **MC-57 results may not be cited for or against MC-53's daily
stock-bond-corr leg** (no informal pre-read of the P-2 confirmation). Seals: pre-burn only after
the mandatory >2026-05-31 load drop; BURNED and VIRGIN untouched.

---

## MC-58 — Breadth-washout rebound · VERDICT: **TRIAGE-MED** (modern leg; era leg DATA-GATED + sequential)

**Attack 1 — POWER-VS-CLAIM MISMATCH (the sharpest).** The only measured prior for the breadth
INCREMENT is +$143/event over the unconditional long, failing its matched control (p_one ≈ 0.18)
at n=263 on the full window. The card's own MDE expectation at n≈154 is $400–550/event — roughly
**3× the only prior estimate of the quantity B2 must detect**. So the likeliest result is not the
card's advertised clean collapse but an inconclusive middle: candidate above control, under MDE.
The promised "permanent closure of the rebound side" is licensed ONLY in the control-wins /
point≈0 cell. **Mandate a pre-registered outcome taxonomy: (i) B2 control ≥ candidate or
increment ≈ 0 ⇒ CLOSED-AS-GENERIC-MR (collapses onto G2_F2_SWEEP01 + W118, permanent); (ii)
positive but under the printed increment-MDE ⇒ CLOSED-BY-POWER at exact scope — a different,
weaker closure that must be labeled as such.** The B2-increment MDE (not just B1's mean-MDE)
prints before any return table.

**Attack 2 — GRAVEYARD GEOMETRY.** W118 closed event-driven reversal at endogenous triggers
with continuation +$374 at the same bars; this card IS a long reversal at an endogenous intraday
trigger. The single discriminator versus the entire fade graveyard is one banked state fact
(+9.62 pp, p 0.0019, G00030 — verified real and control-beating). Therefore **B2(i) is THE
primary gate, not a robustness rung** — and the timing-teeth valence band must be NUMERIC in the
spec (e.g. "+30-min delay loses ≥40% of mean net"), per the AUCTREV lesson that adjectives
don't kill. A flat delay curve falsifies the flush-anchored mechanism even if economics pass.

**Attack 3 — ERA LEG IS BROKEN AS WRITTEN.** The card claims "$TICK 2013-2021 is PRE-FROZEN";
what is actually local is **non-contiguous 2013 / 2015 / 2017** (CAPPROBE01, used by TICK01ERA).
The frozen G00030 construction needs **trailing-252 causal terciles — unimplementable on
isolated single years without redefinition**, and redefinition of the tercile construction is a
new spec, not this card. Era leg ⇒ **DATA-GATED**: runs only (a) after the modern primary passes
B1+B2, (b) after contiguous multi-year extraction with a per-era trailing-252 burn-in year,
(c) as PROTECTED_CONFIRMATION class (TICK01ERA precedent), sign-only, ERABREAK pooling ban.
Never spend a one-shot pre-frozen read decorating a dead card.

**Cost check:** $40/RT stressed floor is correct and required (buying a fresh afternoon low on a
weak-breadth tape is the p90-spread regime); $25.01/$33 print non-gate. **DELEV01 check:** not
implicated on the modern leg — the takeout is a within-session POINTS comparison, additive
offsets cancel. **Not a rescue:** the G00033 closure itself invited this card with the graveyard
addressed; direction, entry anchor (event-time takeout vs state-time 11:01), and population
(~154 takeout sessions vs 263) are materially different; the full-window mirror long stays
BARRED (already measured failing its control); any drift back toward 11:01 full-window in
execution voids the run.

**FROZEN PRIMARY (modern leg):** Population: bottom-tercile (trailing-252 causal) 11:00
cumulative adjusted-TICK sessions whose afternoon 1-min low takes out the morning 1-min low
(POINTS), G00030 construction verbatim on the manifest-checked pair (TICK_1m sha256 72612a1e…,
nq_1m sha256 87aa53f0…), 2023-01→2026-05-31, expected n≈154 — program prints n, events/yr,
pre/post-breach decomposition, B1 mean-MDE AND B2 increment-MDE BEFORE any return table.
Statistic: mean net $/event of LONG 1 NQ at the open of the first 1-min bar after the FIRST
afternoon takeout bar, exit 15:59-stamped close, no stop, at **$40/RT ALL_IN** ($25.01/$33
non-gate). Gates: B1 event-clustered t ≥ 2.0 on mean net > 0; **B2(i) primary discriminator:**
beats the identical trigger on non-bottom-tercile takeout sessions (n≈258, time-of-day matched);
B2(ii) beats p95 of ≥10,000 count-matched random-session longs at resampled takeout times; B3
circular-shift null on the state series, ONE draw shared across the MC-23/41/58 family,
effective-K per CLAUDE.md §4. Timing-teeth: +5/+15/+30-min delayed entries with the numeric
valence band pre-stated in the spec; flat curve = mechanism falsified regardless of economics.
Concentration printed as CLASSIFICATION only, carrying "the incumbent fails this bar at 236.8%"
(F9). Outcome taxonomy pre-registered as in Attack 1; prohibitions locked (no tercile/delay/exit
search, no stops, no reclaim gating, no era pooling); reclaim-anchored variant printed
shape-only, labeled DIAGNOSTIC_CONSUMED, gateable by no future card without a fresh window.
Headline carries DISCOVERY_CONSUMED whatever happens; a pass licenses only robustness + the
gated era leg + scheduled virgin reads — never promotion.

**Reserve ruling:** Modern leg touches no frozen reserve — it runs on the already-consumed
discovery pair, and the DISCOVERY_CONSUMED tag is permanent. The era leg **would consume the
one-shot pre-frozen pre-2022 $TICK replication read for this family** and is gated: sequential
on a modern B1+B2 pass, contingent on contiguous-era extraction (currently impossible — local
store is 2013/2015/2017 only), PROTECTED_CONFIRMATION class, sign-only, never pooled. BURNED
Jun–Jul 2026 and VIRGIN ≥2026-08 untouched; no P-1/P-2 contact.

---

## Verdict counts

| Verdict | Cards |
|---|---|
| TRIAGE-HIGH | MC-57 (3 mandatory amendments: VXN out of both arms; POINTS-basis ZB observables + >2026-05-31 load drop + alignment rule; NQ-RV-matched controls + VIF gate) |
| TRIAGE-MED | MC-58 (outcome-taxonomy + increment-MDE mandated; era leg DATA-GATED + sequential) |

## Disagreements with the card authors' implied triage

| Card | Author's stance | Skeptic | Why |
|---|---|---|---|
| MC-57 | run as specced | TRIAGE-HIGH **only after amendment** | The HAR+VXN baseline silently spends P-1 — the same join W2 stripped from MC-38; "control arm" is not an exemption. Substrate is additively back-adjusted → percent-basis ZB RV is a DELEV01 violation the card never rules out; parquet physically contains the burned window. |
| MC-58 | "B2(i) failure = permanent closure of the rebound side" | Only the control-wins cell closes it | The one measured prior for the increment ($143/event, p_one 0.18) is ~3× under the card's own MDE band — the modal result is an underpowered middle, and calling that "closed for good" would be a mislabeled statistic (the CAP01 lesson in miniature). CLOSED-BY-POWER and CLOSED-AS-GENERIC are different rows. |
| MC-58 era leg | "PRE-FROZEN 2013-2021 $TICK, era-stratified use" | DATA-GATED | The local pre-2022 store is 2013/2015/2017 non-contiguous; trailing-252 terciles cannot be built on isolated years. As written the leg is unimplementable, and running a redefined version would be a silent spec change. |
