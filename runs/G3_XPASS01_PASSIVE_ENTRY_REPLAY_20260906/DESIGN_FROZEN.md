# SPEC — G3_XPASS01: P1 passive-entry policy replay (join-bid limit + T-second timeout)

run_id: G3_XPASS01_PASSIVE_ENTRY_REPLAY_20260906
class: X — EXECUTION (cost/fill measurement on an existing engine; NOT alpha research)
stage: DISCOVERY-grade by construction (all quote sessions outcome-consumed; no valid blind BBO pool exists — split.txt truth). Output can never be alpha evidence; it prices an execution policy.
spec_committed_before_results: true (this file commits before any quote row is opened)

## 1. Question
At each historical P1/PCT entry decision, replace the marketable buy (pay the ask) with a JOIN-BID limit at the prevailing best bid, timeout T seconds, T ∈ {5, 30, 120} (three preregistered variants, one family). Measure fill-weighted spread savings minus alpha foregone on unfilled entries, against already-extracted, governance-clean NQ tick/BBO data.

## 2. Object (exact)
- **Entry population**: the bench-regenerated P1/PCT entry events (long-only, buy entries only; exits untouched) whose session lies in the 104-session clean tick union. The bench MUST first re-pass G0 parity (reproduce weekly/maxDD/t/trades/rate to rounding vs committed; RAISE on failure — a bench that cannot reproduce P1 generates no timestamps).
- **Anchor instant** per entry: the bench entry action instant (its committed next-bar convention, minute END-stamped, ET) + latency δ = 250 ms (preregistered; sensitivity {100 ms, 1 s}).
- **Baseline leg**: fill at the first valid (uncrossed) ask at/after the anchor. Both legs share the anchor → decision-series identical; the policy changes ONLY the entry fill.
- **Policy leg**: buy limit at best bid B at anchor, resting T seconds.
  - **Fill rules (both computed; conservative is primary)**: STRICT-THROUGH (primary): filled at B only when a trade prints strictly below B, or ask ≤ B, within (anchor, anchor+T]. AT-TOUCH (upper bound, diagnostic): a trade at ≤ B or bid-side print at B. The pair brackets the truth (no queue/depth data — stated limitation).
  - **+1-TICK STRESS (schema-required)**: strict-through shifted one tick — fill requires a print ≤ B − 1 tick. Any T-variant positive only without this stress is recorded FILL-FRAGILE, not a candidate.
  - Size-2 entries (19.9%): both contracts assumed filled together at L1 granularity (no depth) — stated assumption; contract-weighted throughout.
- **Two foregone accountings, both preregistered**:
  - **A. CHASE (deployable, powered — primary)**: if unfilled at anchor+T, buy at the first valid ask after anchor+T. Per-contract delta_A = (ask_anchor − effective_fill) × PV. Alpha foregone appears as the adverse drift paid at timeout. Tick-scale variance → powerable at n≈187.
  - **B. CANCEL (the task's literal object — secondary)**: if unfilled, skip the trade. delta_B = filled: (ask_anchor − B) × PV; unfilled: −(incumbent all-in trade net P&L: bench pnl incl. commission, minus the $14.44/ctrRT MODELLED spread addend, per the WE_W103 convention — basis approximation stated in G6). Trade-P&L variance (~$1.5–2k SD) → expected UNPOWERED at n≈187; the MDE gate adjudicates BEFORE outcomes are read; if MDE > ceiling, accounting B is declared UNPOWERED-BY-DESIGN and reported as components only, never as a headline.
- **Data hygiene**: substrate precedence v2 > ESNQ > v1 per session; NEVER merge v1/v2 within a session; all timestamp offset arithmetic asserted int64 ns (the MS-BBO int32 overflow is the recorded failure mode); crossed-BBO instants dropped and counted; v1 truncation mask (15 files @ 12,000,000 rows) — entries whose window [anchor, anchor+120s+exit-check] exceeds file coverage are UNMEASURABLE, excluded symmetrically from all variants, and censused.

## 3. Ceiling (OPPORTUNITY_LANGUAGE — level named)
EXECUTION level, entry side only. Absolute ceiling = fill_rate × quoted entry spread: at median RTH 3 ticks ($15/ctr) / all-hours 4 ticks ($20/ctr, MEASURED, burned-window) × ~10.1 ctr-trades/wk ⇒ **≤ ~$150–200/wk at fill_rate = 1 (unreachable); realistic band well below**. P1 net ≈ $1,394/wk ⇒ this is a ≤10% execution overlay, never an alpha claim. Savings BASIS: SPREAD_ONLY, EVIDENCE: MEASURED; weekly conversion uses the incumbent's MODELLED trade rate.

## 4. Gates (program-printed GATE / SPEC / OBSERVED / PASS-FAIL; failed gates recorded failed)
- **G0 seal**: every replay session < 2026-08-01, asserted at load, boundary printed.
- **G0b pool intersection (mechanical, from the four registers)**: replay set ∩ (W5 confirmation_pool_168_dates.txt ∪ MICRO_BLIND_CONFIRMATION_POOL.csv ∪ BBO_BLIND_POOL_MANIFEST.csv ∪ ESNQ manifests) = ∅; explicit assert 2026-05-05 ∉ set; RAISE if nonempty.
- **G0c bench parity**: P1/PCT reproduced to rounding (all 5 metrics) before any entry timestamp is emitted; RAISE on failure.
- **G1 MDE-FIRST (barrier)**: for each accounting × T, MDE at 80% power printed BEFORE any observed policy outcome, from n_measurable entries and preregistered variance proxies (spread distribution for A; bench per-trade P&L SD for B — already-known discovery content). If MDE_B > ceiling, accounting B is UNPOWERED (recorded in advance, components-only reporting).
- **G2 primary**: accounting-A strict-through per-ctr-entry net delta, per T, with session-level block-bootstrap 95% CI (dependence-preserving; one shared resample across the T-family). Family = 3; Bonferroni α = 0.05/3.
- **G3 +1-tick stress**: G2 repeated under the stress rule; positive-only-without-stress ⇒ FILL-FRAGILE.
- **G4 semantic double-computation (the CAP01 rule)**: one printed sentence per T stating exactly what population/event the headline is over ("over N measurable bench entry events in the M-session union, per-contract mean of …"), AND the identity fill_rate × mean(savings|fill) − (1−fill_rate) × mean(cost|unfilled) recomputed independently and asserted equal to the direct mean to rounding.
- **G5 censoring & selection control**: census of unmeasurable entries (truncation / RTH-only / coverage) + comparison of measurable vs unmeasurable entries' incumbent P&L (biased-subset check); adverse-selection diagnostic printed (incumbent P&L of unfilled vs filled entries — the mechanism prior says unfilled skew toward winners).
- **G6 evidence tags**: per-session tag table (PRE_BURN/DISCOVERY-CONSUMED vs BURNED-WINDOW); every dollar figure carries BASIS + EVIDENCE; the run's own class printed: Class-X EXECUTION, DISCOVERY-grade, never alpha.

## 5. Decision rule (mechanical) + KILL rule
- **CANDIDATE** (per T): G2 PASS (Bonferroni, accounting-A net > 0) AND G3 PASS AND strict-through fill_rate ≥ 20% ⇒ queue as an execution-policy candidate for owner-gated NT8 implementation study + forward shadow. NO live change, NO sizing change, NO promotion from this run.
- **KILL-1 (powered kill)**: if for ALL T the strict-through accounting-A upper 95% CI < $2.50/ctr-entry (≈ $25/wk ≈ 1.8% of P1 net — materiality floor declared here), record **PASSIVE-ENTRY-AT-L1 CLOSED** in FAILURE_MEMORY; do not revisit without depth/queue data.
- **KILL-2 (mechanism kill)**: strict-through fill_rate(T=120) < 20% ⇒ CLOSED-BY-MECHANISM (the policy cannot engage the book at P1's entry instants).
- Accounting B is reported per its G1 power status; if UNPOWERED it can neither adopt nor kill — recorded as measured components.
- Ledger: ONE trial, family EXEC_PASSIVE_ENTRY (3 T-variants = one preregistered family), registered before outcomes.

## 6. Outputs
out/gate_table.txt (program-printed) · out/per_entry.csv · out/fill_curves.csv (f(T), time-to-fill) · out/censoring_census.csv · REPORT.md. No pool file opened; no session ≥ 2026-08-01 read.