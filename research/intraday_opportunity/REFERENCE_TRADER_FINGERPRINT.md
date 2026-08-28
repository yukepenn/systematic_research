# REFERENCE TRADER FINGERPRINT

**COMMIT B.** Recovered from campaign #6 `original_trader_reconstruction` (closed 2026-08-25) by
10 disjoint forensic readers with adversarial verification of every claimed fact.
**No strategy, no signal, no P&L is designed in this document.**

> ## ⚠️ **THE ENTIRE REFERENCE-SIDE EVIDENCE BASE IS 164 SCREENSHOTS.**
> There is **no source code, no account statement, no broker record, no trade ledger, no chart
> image, and no per-trade timestamp anywhere** — proven by exhaustive sweep, not assumed.
> Every number below is a **pixel read of a report the trader published himself.**

*(The individual's identity, handle and account id are recorded in
`research/original_trader_reconstruction/`. They are not repeated here — they carry no analytical
content for Program B.)*

---

## 1. What the object is — genealogy

**It is a person, not a product, and not one strategy.** A self-described amateur with a day job,
writing his own NinjaScript, running fully automated on NT8 across four hosts. His own verbatim
statement (2025-12-20): **he ran several strategies concurrently**, and used Strategy Analyzer
precisely because it isolates one at a time.

> ### **CONSEQUENCE THAT GOVERNS EVERYTHING: every posted number is a SLEEVE, never an account
> ### result.** His account-level trade rate is `≥ the largest single-sleeve figure` and is
> ### **UNQUANTIFIED**. Binding frame: `ACCOUNT(t) = time-varying combination of families; no clean
> ### regime switch is established.`

| era | span | fingerprint |
|---|---|---|
| **S** | 2023-01 → 2025-02 | `SolarWindRKSelTime`, Qty 1, NQ 1-min Last. **8.26 trades/day, 94.15 min holds, WR 40.29 %, PF 1.18, maxDD $32.7k, longs carry 73.6 % of net, NO hard stop** (largest loss −$4,449.18) |
| **SD** | 2025-02 → late 2025 | commission reporting switched **OFF** 2025-02-28; a 90-trade day on 2025-02-27; exact **−$1,300.00** largest-loss signature recurring 2025-07 → 2026-01 |
| **V** | 2026-02 → 2026-08-14 | **name unrecoverable — proven, not merely failed** (NT8 drew the combo box as a bare chevron). 13-field VWAP-Flux-shaped block. Risk cap **−$2,600**, first seen **one week BEFORE** the first VF panel. Frequency 2–3×, holds collapse to 20–50 min |

### ⭐ Is today's `P1/PCT` descended from the reference trader? — **NO.**

**`P1/PCT` shares an *indicator ancestor* with his 2023–25 build. It is not descended from his
strategy, and no test in either campaign has ever had him as an endpoint.** A repo-wide grep of the
OTR campaign for `P1` / `PCT` / `WEEKLY_EDGE` / `XM_CONFLICT` returns only unrelated hits.

> **`ORIGINAL_PARITY` — agreement between us and the original trader — has NEVER been tested
> anywhere in this campaign.** The much-quoted "BIT-EXACT / PARITY: PASS" is implementation parity
> between **three of our own artifacts**.

The link to Solar Wave RK is a **parameter coincidence plus a name** (his `90/179/5/10/10` equals
the vendor panel quintuple; the manual independently says the trailing offset "should roughly
double" the trend offset, and 179 ≈ 2 × 90). Recorded as **INFERENCE**; whether his engine computes
the same mathematics is **UNKNOWN**.

**Structural divergences that make descent implausible even as a story:**

| | reference (S-era) | `P1/PCT` |
|---|---|---|
| direction | **two-sided**, 2,166 L / 2,185 S | **LONG-ONLY** — `p == −1` on 0.00 % of bars, by design |
| overnight | **holds overnight** (a measured long 21:39 → 06:44, +$2,270.82) | **flat at every session close** |
| session | full **18:00 → 17:00 ET** | RTH |
| sizing | Qty 1 | size 1–2, quality sizing (19.9 % at size 2) |
| session risk | **none** in S-era | box **−$1,300 / +$1,000 per contract** |

> ### 🚨 **THE $1,300 COLLISION IS A COINCIDENCE AND MUST NOT BE PROMOTED.**
> `P1/PCT`'s session box is **−$1,300**; his 2025 largest-loss signature is **exactly −$1,300.00**.
> Same instrument, same number, **unrelated**: `P1/PCT`'s box was selected from a grid by
> walk-forward refit — `(1300, 1000)` chosen in **15 of 17 refits** — years before the OTR corpus
> existed. **A component may not be identified from numeric coincidence.** Second instance: his mean
> hold **94.15 min** vs `P1/PCT`'s **86.92 min**. Also not evidence of anything.

## 2. SECTION A — FACTS (pixel-read; **all BACKTEST unless marked EXECUTED**)

### A1 · Master Strategy Analyzer backtest, 2023-01-01 → 2025-02-02

Survived verification on five axes twice, arithmetically self-consistent on 15 identities.

| | | | |
|---|---:|---|---:|
| net profit | **$292,172.82** | trades | **4,351** (2,166 L / 2,185 S) |
| long / short net | $214,911.12 / $77,261.70 → **73.6 % long** | percent profitable | **40.29 %** |
| profit factor | **1.1764** | max drawdown | **$32,677.42** |
| avg trade | **$67.15** | avg win / avg loss | $1,111.73 / −$637.68 → payoff **1.74** |
| **avg time in market** | **94.15 min** | max consec W / L | 8 / **15** |
| largest win / loss | $7,705.82 / **−$4,449.18** ← no hard stop | NT8 "trades per day" | **8.26** (implied denom **526.8**) |
| commission | $18,187.18 = **$4.18/RT** | **slippage** | **0** |
| Sharpe / Sortino | 0.63 / 2.00 | avg bars in trade | 94.13 → **proves 1-min primary series** |

**Config, label-photographed:** Qty **1** · NQ front month · Minute/1/Last · Tick Replay unchecked ·
**Entries per direction 1** (Feb-2025 only) · **TradingHours = "Use instrument settings" = full
18:00→17:00 ET** · slippage 0. **"Include commission" UNCHECKED from ~2025-02-28** — 46 of 71 posted
windows carry **$0.00 commission**.

### A2 · The ONLY per-day granularity in all 164 images

| frame | rows | content |
|---|---|---|
| `OTRIMG-0003` | **11** daily rows, 2023-01-03 → 01-17 | **12, 14, 6, 10, 3, 9, 4, 16, 6, 3, 6** (89 trades) — the **top-of-scroll prefix, 2.05 %** of the run |
| `OTRIMG-0026` | **2** daily rows | 2025-02-26 (15 trades) · **2025-02-27 = 90 trades**, +$11,083.80 |

**13 daily rows exist in total. Nothing in the corpus is finer than a period summary.**

### A3 · EXECUTED-trade evidence — **3 frames, 249 trades, in an 18-month posting history**

| frame | window | trades | net | WR | avg hold |
|---|---|---:|---:|---:|---:|
| `OTRIMG-0005` | 2025-02-03, **one session** | **35** | **−$616.30** | 28.57 % | 38.71 min |
| `OTRIMG-0152` | 2026-06-07..12 | **136** (27.2/session) | +$11,860.30 | 50.00 % | **20.49 min** |
| `OTRIMG-0154` | 2026-06-14..18 | **78** (15.6/session) | +$8,503.24 | 42.31 % | 34.10 min |

⚠️ **LIVE vs SIM is UNKNOWN** — no account tag in any frame. `OTRIMG-0152`'s **$1.04/fill**
commission basis is unexplained and **matters**: an MNQ sleeve would invalidate every dollar-based
stop inference.

### A4 · Posted extremes

worst week **−$42,235** (2026-03-22..27, 92 trades, WR 28.26 %) · best week **+$42,765**
(2026-06-21..26, 71 trades) · worst 2025 week −$15,365.

## 3. TESTIMONY — *"he said this"*, never *"it is true"*

**Not one has ever been cross-checked against a ledger, because no ledger exists.**

| statement | date | note |
|---|---|---|
| **"runs several strategies simultaneously"** | 2025-12-20 | the load-bearing account-layer statement |
| **"generally traded one contract"** | 2025-12-27 | ⚠️ **"generally" ≠ "always"** — a frame charges $12.54/trade (≈3×) and a Qty-3 experiment is logged. Contradiction **C-7 OPEN** |
| $60k capital, day margin ~$3k, historical max DD ~$30k+ | 2025-12-27 | **agrees with the master backtest's $32,677 to ~9 % — he sized off the very backtest in this corpus** |
| **2025 ≈ "~$150k+"**, self-labelled approximate | 2025-12-27 | **35 % BELOW the sum of his own posted slices** |
| "~$500–600/day normally" | 2025-11-08 | said while **deflating** a good week |
| real ≈ posted **×0.9 on wins, ×1.1 on losses** | 2025-12-20 | consistency check only; forbidden as execution physics |
| auto-flatten 30 s before 17:00 ET | 2026-05-10 | ⚠️ **NOT** "no overnight positions" — see §5 |

## 4. INFERENCES — labelled, none is a fact

- the **−$2,600** cap is a **wrapper/account-level risk layer**, not a vendor property (it appears
  one week *before* the first VF panel; a full vendor sweep found **no 130-pt/$2,600 stop anywhere**);
- a `SelTime` window exists and is **hard-coded** (no time box exists in any S-family panel);
- his 2026 re-entry throttle was **dramatically looser than any published preset** —
  `Signal Quantity Per Trend 3 / Split 5 bars / Close Threshold 10 %` vs vendor defaults 4 / 30 / 80.
  **He *permitted* dense re-entry. This says nothing about whether it earned.**

## 5. FALSIFIED / RETRACTED — do not resurrect

| claim | status |
|---|---|
| **"−$2,600 = 130 points × 1 contract"** | ⚠️ **arithmetic REFUTED** — all 18 occurrences are parity-unconstrained; **"130 pt is author testimony, not arithmetic; 65 × 2 is not excluded."** Four in-repo files still say "130-pt stop" and predate the retraction |
| "the −$2,600 cap is universal in 2026" | **FALSIFIED** — a week shows −$1,890 and another a −$2,820 gap-through |
| **"intraday-only / no overnight positions"** | ⚠️ **REFUTED as stated.** It is testimony about the futures **SESSION** (18:00→17:00), not the calendar day. Contradicted by his own data |
| "04:00–16:00 ET SelTime window" | **FALSIFIED** — *"the target contains overnight trades the window forbids"* |
| "42/42 cent-exact ground-truth trade labels" | **RETIRED** to `CONDITIONAL_LATENT_LABELS` — six candidate universes each admit a solution |
| "the 11-day 2023 path is UNIQUE" | **WITHDRAWN** — 2 global paths; and *"16 of its 105 decisions are declines produced by choice, not by a rule"* |
| "June–July 2026 is a TRUE OOS test" | **FALSIFIED** → `HELD_OUT_RECONSTRUCTION_WINDOW` |
| "his long/short profits are ~50/50" (his own testimony) | **FALSIFIED for PROFIT** by his own grid: **74/26**. True for *count* |
| session-equity gate constants X=1600, K=3, cap=20, cooldown=3 | **FALSE — they are OURS.** Never quote as his |

## 6. 🚨 SECTION C — UNKNOWN, and the central void

> ### **WHETHER THE REFERENCE TRADER'S LATER SAME-DAY TRADES WERE PROFITABLE IS UNKNOWN — AND IS
> ### UNKNOWABLE FROM THE FIXED 164-IMAGE CORPUS.**
>
> There is **no evidence of any kind** bearing on the profitability of his 2nd, 5th or 12th trade of
> a session. **Not weak evidence. None.** Five independently fatal blockers: no per-trade record
> exists corpus-wide · the finest granularity is the **day**, and only **13 such rows exist**, and a
> daily row **carries no intra-day ordering** · zero chart imagery · `Longest flat period` spans the
> overnight break and is not a re-entry gap · the one trade-level object in the repo is **ours**, is
> a **constraint-solver output rather than a program**, and has been formally retired.
>
> **It cannot be closed by more reading, more inference, or more modelling of our replicas.** It
> needs an artifact that does not exist, and the owner has confirmed the corpus is complete.

⚠️ **The slice commissioned to answer this returned nothing about him:** `OTR_S5_REENTRY_QUALITY` /
`S5B_CHURN` / `S6_T2` are **parameter sweeps over OUR OWN Python re-implementation**, on our
substrate, at **commission $0 / slippage 0**, scored against eight rounded numbers from one
screenshot. **Every "re-entry quality" result there is a property of our wrapper, not an observation
of him.**

**Also UNKNOWN:** hold-time *distribution* (only means exist) · equity path / drawdown duration ·
monthly P&L · re-entry spacing · long/short split outside the master · any account-level figure ·
**anything at all after 2026-08-14** — *"not weak evidence, none."*

> ### **COROLLARY THE CAMPAIGN MUST ACCEPT:**
> ### **The reference trader can MOTIVATE the opportunity-density hypothesis. He cannot VALIDATE
> ### it. Any density result must be earned on our own substrate.**

## 7. Contradictions surfaced, not smoothed

**8.26 vs 8.09** — 8.26 is the whole-population NT8 cell; 8.09 is a **2 % top-of-scroll prefix** and
is **not** a corroboration. On our own 539-session substrate the same trades give **8.07**.
**NT8's "trades per day" denominator was never reverse-engineered** and runs ~1.2× high on weekly
windows (32.83 against 136 ÷ 5 = 27.2). **Use trades ÷ Mon–Fri sessions for any gate.**
**Per-session ≠ per-day**: the Jan-2023 rows are grouped by calendar exit date, and he demonstrably
held across 18:00 ET. **Three "weekly" frames are 2–3-week windows** — comparing them under a
frequency header is a 2–3× error. And the corpus's 2025 slice total was overstated by **$39,787**
from **7 dropped minus signs** still uncorrected on disk.

## 8. The campaign's verdict on itself — quoted, not softened

Written after an eight-skeptic audit returning **0 CONFIRMED / 2 REFUTED / 6 WEAKER_THAN_STATED**:

> *"One era is reconstructed at trade level over 11 days; the other two are not reconstructed at all."*

Per-era reconstruction scores /100 (2023 / 2025 / 2026): signal **70 / 20 / 18** · entry
**55 / 15 / 16** · exit **72 / 18 / 12** · long-short asymmetry **25 / 12 / 10**.

The audit's own diagnosis of its global failure mode — **the rule this document exists to enforce**:

> *"a correct measurement, described with a stronger word than the measurement supports… The
> quantifiers were wrong nearly everywhere."*

**LIVE ENABLED: NO.**
