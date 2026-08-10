## ADD01_PARTICIPATION_EXPANSION -- Stage-A finding: lowering EntryLevel is net destructive

**Question (directive Master v3 sec19-24):** Has Product B been over-selective? Does lowering
the entry barrier (EntryLevel, currently 3.0 in SM14 hysteresis(3,1)) create positive
incremental participation value without destroying capital efficiency?

**Answer: No.** The additional weak-signal opportunities that a lower EntryLevel would open up
are large-sample, uniform-sign, mechanistically-explained *losers* -- not a wash, a genuine
destructive edge. Stage A is closed as clearly dead; no Stage-B integrated policy was built.

---

### 0. Correctness gate (passed before any intervention)

`u0_state_table.parquet`'s own `M`, `entry_blocked_c4`, `forced_flat_c4` columns were fed through
`health_substrate.build_pos_seq(entry_level=3.0, exit_level=1.0)` (imported logic, byte-identical
mechanics, only the session-last-bar flag rebuilt from `sess_date` grouping). Result:

- Reconstructed position sequence matches the table's own `position_B` column **bar-for-bar, 0
  mismatches out of 519,714 canon bars** (`is_health_only_bar==False`, 2022-01-03..2026-05-29).
- Reconstructed NQ net: **$301,915.92** -- exact match to the certified canonical net.
- Table's precomputed MNQ net: **$28,587.10** -- exact match to the certified canonical net.
  (MNQ leg was not independently re-derived here because this table exposes only NQ OHLC; the
  MNQ column already reflects genuine-MNQ pricing for the canonical window per
  `UNIFIED_STATE_MAP.md`. This is a disclosed scope limit, not a gate failure -- the NQ leg,
  which is exact end-to-end, is the gate.)

Gate passed. Proceeded to the intervention.

### 1. Reachable-M enumeration (mandatory, done before choosing tiers)

`M = 0.7086*Tp + 2.83*B` where `Tp` is an integer in [-13,13] and `B in {-1,0,1}`. Enumerating
the actual distinct `M` values that occur in canon bars within `[2.0, 3.0)` gives exactly **6**
values, not a continuum:

| M value | (Tp, B) | cumulative additional flat-bars if EntryLevel lowered to here (long) | (short, mirrored) |
|---|---|---|---|
| 2.1214 | (-1, 1) | 23,690 | 21,167 |
| 2.1258 | (3, 0) | 21,824 | 20,209 |
| 2.1302 | (7, -1) | 10,220 | 8,536 |
| **2.8300** | (0, 1) | 9,334 | 8,077 |
| 2.8344 | (4, 0) | 3,780 | 6,173 |
| 2.8388 | (8, -1) | 284 | 118 |

(counts = canon bars with `position_B==0` (baseline-flat), `M` in `[T,3.0)`, not
`entry_blocked_c4`, not `forced_flat_c4`.) There is a real, structural gap in the grid --
nothing exists in `(2.1302, 2.83)` or `(2.8388, 3.0)` -- so this is a genuine two-cluster
structure, not an artifact of picking arbitrary round numbers (the U1B quantization trap the
campaign has been burned by before).

**Preregistered tiers (at most 2, per protocol):**

- **T1 = 2.8344** ("mild"): strictly above 2.83. B-MOM still cannot trigger an entry
  unilaterally -- the audit's flagged structural fact (`|WBmom*B| <= 2.83 < EntryLevel`) is
  **preserved** at this tier. Chosen over the even-closer-to-baseline 2.8388 because 2.8388's
  own additional-bar population (284/118) is too thin to be a meaningful economic test; 2.8344
  is the largest reachable value that still gives a non-degenerate sample while staying in the
  same qualitative regime as baseline.
- **T2 = 2.1258** ("deep"): at/below 2.83. The 2.83 boundary is **explicitly crossed** -- B-MOM
  now CAN trigger an entry alone via the `(Tp=0, B=1)` bucket. Flagged per instruction, not
  avoided. Chosen over 2.1214 specifically to *exclude* the `(Tp=-1, B=1)` bucket, where a
  slightly-bearish Solar+HTF score (`Tp=-1`) is flipped net-positive purely by B-MOM -- that
  bucket is mechanistically closest to the previously-killed "B-dominant routing" idea (two
  prior core-decision-mechanism proposals were both killed by the frozen Gate A/B/C), so it was
  deliberately excluded from this pass to keep ADD01 a clean threshold-lowering test rather than
  an inadvertent re-test of a closed idea.

### 2. Stage-A construction

For each tier, `alt_pos_seq = build_pos_seq(M, entry_level=tier, exit_level=1.0)` (same exit
level, `entry_blocked_c4`, `forced_flat_c4` as baseline -- only `entry_level` changes). Its
contiguous nonzero runs (same block definition as `block_id_B`: a same-bar sign flip starts a
new block) were partitioned into:

- **Disjoint** blocks: baseline `position_B == 0` for *every* bar of the block -- genuinely new,
  standalone episodes the incumbent never touches.
- **Overlapping** blocks: baseline held a position somewhere inside the block -- the alt policy
  just entered *earlier* into the same excursion the incumbent was already going to trade.

The incumbent's own `position_B` sequence was never modified -- read-only throughout.

**Key correction to the directive's working assumption.** Sec22 expected overlap with incumbent
participation to be "near-zero by construction." It is not:

| Tier | total alt blocks | overlapping | disjoint | overlap % |
|---|---|---|---|---|
| T1 = 2.8344 | 2,133 | 1,978 | 155 | **92.7%** |
| T2 = 2.1258 | 2,768 | 1,978 | 790 | **71.5%** |

Every one of the incumbent's 1,978 canon-window position blocks (1,890 ENTRY + 88 REVERSAL)
necessarily sits inside *some* alt block for any threshold below 3.0 -- lowering the bar mostly
just detects the same big moves a few bars earlier, it does not manufacture new territory. Only
the disjoint minority is genuinely incremental participation, and unsurprisingly it is exactly
the population of excursions that *never* built enough conviction to reach the existing bar.

**Stage-A sleeve = alt_pos_seq restricted to disjoint blocks only**, executed standalone with
`onelot_exec` (NQ: `COMM_NQ=$2.18`, `PV_NQ=$20`, exact real prices; MNQ:
`COMM_MNQ=$0.65`, `PV_MNQ=$2`, NQ-OHLC-as-proxy for this hypothetical new path -- the same
disclosed-approximation class `UNIFIED_STATE_MAP.md` already uses for health-only bars, applied
here because genuine MNQ OHLC is not exposed for arbitrary new position paths in this table).

### 3. Stage-A economics -- decisively negative

| Metric | T1 (2.8344) | T2 (2.1258) |
|---|---|---|
| additional bars in position | 7,924 (1.52% of canon) | 33,230 (6.39% of canon) |
| disjoint episodes | 155 | 790 |
| NQ net | **-$159,025.80** | **-$534,224.40** |
| MNQ net (proxy) | -$16,036.50 | -$54,105.00 |
| win rate (episodes) | 12.9% | 21.4% |
| avg P&L / episode (NQ) | -$1,020.83 | -$670.36 |
| median P&L / episode (NQ) | -$1,167.18 | -$897.18 |
| Sharpe-like (daily) | -2.87 | -5.16 |
| Sortino-like (daily) | -2.03 | -5.50 |
| Calmar-like (daily) | -0.22 | -0.22 |
| daily-P&L corr with incumbent | 0.046 | 0.017 |
| long/short episode split | 105 short / 50 long | 413 short / 377 long |
| avg episode hold (bars, 3-min) | 51.1 (median 28) | 42.1 (median 23) |

**Chronology (year-by-year, 2022-2026 partial):**

| Year | T1 net NQ | T2 net NQ |
|---|---|---|
| 2022 | -$49,855.66 | -$128,794.70 |
| 2023 | -$30,279.38 | -$100,172.92 |
| 2024 | -$27,209.50 | -$84,701.38 |
| 2025 | -$18,069.76 | -$144,485.60 |
| 2026 (partial, through 2026-05-29) | -$32,813.60 | -$71,430.68 |

Every single year is negative for both tiers -- a uniform-sign result. No LOYO was run because
leaving out any one year cannot flip the sign of a result that is already negative in all five
years.

**2022-2025-only vs control (the campaign's wash test):** control's 2022-2025 net =
$300,156.88. Stage-A net over the same years: T1 = -$126,013.60 (**-41.98%** of control), T2 =
-$462,147.40 (**-153.97%** of control). Both are an order of magnitude past the campaign's <1%
wash threshold, in the destructive direction -- this is not "no effect," it is active value
destruction on top of the existing edge.

**Session-phase split:** every bucket (`ETH_ASIA`, `ETH_EUROPE`, `POST_RTH`, `RTH_CLOSE`,
`RTH_MID`, `RTH_OPEN`, `US_PREMARKET`) is net negative for both tiers -- not a single-session
artifact.

**Behavior on the incumbent's own worst drawdown days:** on the incumbent's worst-20
eod-drawdown days (led by the 2025-07 run culminating in a -$59,717.44 eod trough, and
2026-05-19's -$16,952.44 single day), the T1 sleeve fires **zero** episodes ($0 contribution --
neither helps nor hurts). The T2 sleeve fires on 4 of those 20 days and contributes **-$7,414.24**
-- it makes the incumbent's worst period *worse*, not better; there is no diversification
benefit hiding in this population.

**Tail distribution.** Top-20/bottom-20 episodes (both tiers) were pulled directly; a few large
winners exist (T1 best +$11,332.82 on 2025-01-27; T2 best +$13,232.82 on 2024-08-05) but they are
swamped by a long left tail. The single worst T2 episode (-$7,937.18, a 4-bar/12-minute hold on
2022-10-13 08:24-08:33 ET) was manually verified against raw OHLC: NQ dropped ~391 points in one
3-minute bar on 25,483 contracts of volume -- this is the September-2022 CPI print, a real,
famous, extreme-volatility event, not a data bug. It illustrates the real mechanism: weak/marginal
signals enter with no intrabar stop, and a hair-trigger low-threshold system occasionally eats a
full adverse tail-risk bar that the higher, more selective baseline threshold would have avoided
entirely (baseline's `M` for that same excursion never reached 3.0 before the reversal).

### 4. Right-tail audit (mandatory per shared-context item 4)

Incumbent's own top-20/bottom-20 canon-window position blocks by `run_pnl_B_dollars` at exit are
reported for reference (best: +$41,337.82, block 2870, 2025-04-09; worst: -$7,572.18, block
3431, 2025-11-25). Because Stage A's construction is read-only on `position_B` throughout (never
assigned to, only compared against), **0 of these 40 blocks can be excluded, changed, delayed, or
resequenced by the candidate** -- this is a mechanical guarantee of the sidecar design, confirmed
by the exact bar-for-bar match in the correctness gate, not merely asserted.

### 5. Gate check (reused verbatim from the prior audit's frozen Gate A/B/C, for context only)

Stage A never reached the point of needing a promotion decision, but for context: Gate B alone
(old-regime/2022-2025 non-inferiority floor of -$10k) is failed by roughly **12x-46x** its own
floor (T1 -$126k, T2 -$462k vs a -$10k floor). No plausible Stage-B construction recovers from
this Stage-A base rate.

### 6. Disposition

**CLOSED_EXACT_CONSTRUCTION.** Per the family's own stop rule (sec23): "If Stage A looks
weak/negative/degenerate, STOP and report that as the finding -- do NOT force a Stage-B
construction." Stage A is not weak or ambiguous here -- it is a large-sample (155-790 episodes),
uniform-sign (5/5 years, 7/7 session phases, both tiers), mechanistically-explained (marginal
signals disproportionately populate the market's most violent whipsaw tail, with no intrabar
stop) negative result, strongly anti-correlated in spirit with the incumbent's own risk profile
(it adds pain, not diversification, on the incumbent's worst days). Product B's EntryLevel=3.0
threshold is doing real, measurable filtering work; lowering it is not a viable direction for
this campaign. No Stage-B integrated {-1,0,1} policy was attempted -- doing so would not have
been rigorous given this evidence, per the family's own instruction not to force a construction
to manufacture a result.

### Artifacts

Working scripts (scratchpad, not persisted to the repo):
`add01_common.py`, `add01_step0_gate.py`, `add01_step0b_reconstruct_gate.py`,
`add01_step1_enum.py`, `add01_step2_stageA.py`, `add01_step3_diag.py`, `add01_step4_battery.py`
under
`C:\Users\YUKEZH~1\AppData\Local\Temp\claude\D--OneDrive---Washington-University-in-St--Louis-TradingResearch-systematic-research\bfb80633-2ca8-4554-803e-2bd6cbeeb4c1\scratchpad\`.
Source data: `runs/U0_UNIFIED_STATE/out/u0_state_table.parquet`,
`runs/SA0_SYSTEM_STRUCTURE/current_health/src/health_substrate.py`.
