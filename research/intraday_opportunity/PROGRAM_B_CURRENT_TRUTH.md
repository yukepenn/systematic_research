# PROGRAM B — NQ INTRADAY OPPORTUNITY FACTORY · current truth + forensic plan

**COMMIT A.** Verified against the repository, not against the directive. **No new strategy result
exists at this commit.**

| | |
|---|---|
| HEAD · branch · tree | `10e379e` · `main` · clean · `== origin/main` (verified via `git ls-remote`) |
| **LIVE ENABLED** | **NO** |
| this campaign | **PROGRAM B** — opportunity density inside one NQ session |
| **not** this campaign | **PROGRAM A** — which independent alpha families belong in a portfolio |

---

## 1. ⚠️ THE DIRECTIVE'S `$1,166` EXPECTATION IS FALSE PER REPOSITORY TRUTH

The directive lists as a possible current fact:

> *"the historically quoted P1 fixed-DD number may have been corrected from roughly $1,230/week
> toward roughly $1,166/week because of a cost/DD denominator inconsistency"*

**That correction was itself RETRACTED on the same day it was issued, before any seal read.**
`runs/FWD_DD_RECONCILIATION/REPORT.md` now opens with its own retraction. §1 of the directive binds:
*repository truth governs*, and it governs in this direction too — **a retracted correction must not
be silently re-adopted because a later directive repeats it.**

**Verified independently, from a single row of a single file** —
`runs/WE_W103_CONSOLIDATE/out/components.csv`:

```
P1_PCT , trades 2401 , $/ctrRT 14.4365 , wk$ 1393.5737 , wk$@fixDD 1230.3567 ,
         wk+% 56.338 , maxDD 22930.6659 , top5 17835.39 , worst wk -9221.12 , t 4.1636
```

> ### **The numerator (`$1,393.57`) and the denominator (`$22,930.67`) are the SAME ROW of the SAME
> ### SERIES.** There is no cost-model mixing to correct. `k = 20,245 / 22,930.67 = 0.882879`
> ### reproduces **`$1,230.36/wk`**.

**What the retracted report got wrong:** it assumed `RR_W003`'s weekly file was canonical. That file
buckets by a **Sunday-ending label**, giving maxDD `$24,212.92`; the canonical stream buckets by
**ISO week on session date**. Failing to match, it searched cost-model and population variants and
reported the nearest as a mechanism — **an argmax from an under-constrained search, i.e. exactly the
multiplicity error this campaign polices elsewhere.**

**What survives and binds this campaign:** max drawdown is **week-boundary sensitive by $1,282
(5.6 %)** on this very series. **Every drawdown figure must state its week convention.**

## 2. Canonical incumbent economics — what Program B must be measured against

| | object | weekly $ @ fixed $20,245 DD | positive wk | maxDD | t |
|---|---|---:|---:|---:|---:|
| **A** `RESEARCH_SINGLE` | `P1/PCT` | **$1,230.36** ($1,393.57 raw) | 56.34 % | $22,930.67 | 4.164 |
| **B** `RESEARCH_PORTFOLIO` | `{P1/PCT + XM}` inv-vol | **$2,012** | 59.2 % | $11,489 | 4.90 |
| **C** `EXECUTABLE_SINGLE` | `WeeklyEdgeP1PCT_v1` | ✅ parity-certified | | | |
| **D** `EXECUTABLE_COMPONENT_SET` | + `WeeklyEdgeXMConflict_v2` | ✅ both legs certified | | | |

⚠️ **`B`'s $2,012 carries two independent cautions that travel with every quotation**: its inverse-vol
weights are a **single full-sample sd applied in-sample to the weeks that produced them**, and
`P1+XM` was a **best-of-six** pick whose preregistered primary `P1+PAIR+XM` scored **$1,765.99**.
Observable selection optimism **$245.71/wk (13.9 %)**. A selection-adjusted, causally-weighted B sits
nearer **$1,750–1,800/wk**. ⚠️ **`D` is a certified component set, NOT an executable `B`** — the
integer-contract mapping is an unmade owner decision.

**Evidence class of A and B: `DISCOVERY_CONSUMED`** (2022-07 → 2026-08, 123 waves).

## 3. ⭐ The incumbent's opportunity density — the number this campaign exists to move

Populations reconciled in-repo (`src/run_rr_w001.py:236`): **2,401 total / 2,131 session-filter /
2,139 ts-filter**. They are three filters of one stream, not a contradiction.

| | value | basis |
|---|---:|---|
| window | **1,058 sessions · 213 weeks** | 2022-07-01 → 2026-08-01, frozen |
| `P1/PCT` trades | **2,401** | the stream behind the canonical headline |
| **trades per CALENDAR session** | **≈ 2.27** | 2,401 / 1,058 |
| sessions `P1` is **completely flat** | **282 (26.7 %)** | `WE_W119` / `RR_W000` |
| **trades per ACTIVE session** | **≈ 3.09** | 2,401 / 776 |
| on **losing** sessions | **3.04** entries | `RR_W000` corrected comparator |
| on **winning** sessions | **2.42** entries | ⚠️ the corrected figure — W119's quoted 1.377 was *winning + flat* and is wrong |
| `XM_CONFLICT` trades | **348** (346 sequential) | ≈ **0.33/session**, active ~33 % of sessions |

> ### **The incumbent takes roughly 2–3 trades per session and is entirely absent from more than a
> ### quarter of them.** That is the sparsity the owner is pointing at, stated in measured numbers
> ### rather than impression.

⚠️ **The reference figure quoted in the directive (~8.26 trades/day) is NOT yet verified from any
artifact.** It is being recovered forensically (§5) and is treated as **UNVERIFIED** until an
artifact supports it.

## 4. Other current-truth items the directive asked to verify

| item | verified state |
|---|---|
| ≥ 2026-08-01 seal | **VIRGIN / UNTOUCHED** |
| `ESNQ_BLIND_EFFECTIVE_14` | **unread, unspent** |
| NQ BBO blind | **19** outcome-unconsumed · 18 pristine · 1 metadata-exposed |
| remaining unread ES BBO | **20** sessions, outside any blind manifest |
| 141-session Last-only pool | **untouched** |
| **shadow logging** | ⚠️ **ENGINEERED, NOT STARTED.** `research_sdk/shadow_ledger.py` exists (9/9 self-test incl. tamper detection); **no ledger file exists anywhere in the repo.** `SHADOW_START = 2026-09-01 18:00 ET` has not arrived |
| recent alpha campaigns | `MS-BBO` **VOID** (future-reading, int32) · corrected causal version **no edge** · `CARRY_V1` **CLOSED** (concentration) · `ESNQ_V1` **CLOSED** · `VOLUME_LIQUIDITY_V1` **CLOSED** · `TSMOM` **CLOSED** |

## 5. Forensic plan — what is being recovered before any signal is designed

**The reference object is campaign #6 `original_trader_reconstruction` (OTR)**, closed 2026-08-25,
plus the Solar Wave reverse-engineering line. ⚠️ **It is NOT assumed that today's `P1/PCT` is the
reference trader** — the genealogy is an output of this work, not an input.

Ten disjoint slices are being read in parallel, each returning claims tagged
**`FACT` / `INFERENCE` / `UNKNOWN` / `FALSIFIED`** with an artifact path and a verbatim quote, and
every `FACT`/`INFERENCE` is then handed to an **adversarial verifier** told to refute it:

| slice | question |
|---|---|
| OTR top-level state | what the campaign concluded the object IS |
| **original screenshots + forensics** | the primary source: his own reported results, and whether a **trade-level ledger** exists at all |
| vendor forensics / author statements | product genealogy · **testimony vs measurement** |
| **`OTR_S5_REENTRY_QUALITY` · `S5B_CHURN` · `S6_T2`** | ⭐ **repeated same-day trading — the campaign's core question** |
| `OTR_S4_EXITS` · `S3_SELTIME` · `SD1_LOSSLIMIT` · `R2_STOPGROUP` | hold time · exits · the "130-point stop" and its evidentiary status |
| `OTR_R30/R31/R32/R34` | does the edge live in **entry or exit**; the methodology equalizer |
| VWAP Flux family | **signal density per session** |
| **adversarial audit + falsified hypotheses** | what must **not** be resurrected |
| Solar Wave math + parity | is `P1/PCT` **descended** from the reference, or merely sharing an indicator? |
| incumbent density | P1/XM trades-per-session and the canonical fixed-DD figure |

**Two priors that shape how the output will be read**, both from repo history:
the OTR 8-skeptic audit returned **0 of 8 claims confirmed as stated**, and the owner's R33 decision
was to treat VWAP Flux as **an instrument, not proof**. **A number the author reported is not a
number we measured**, and the fingerprint will keep those in separate tables.

## 6. What this commit does NOT contain

No archetype. No signal. No event definition. No backtest. No P&L. No opportunity measurement.
`OPPORTUNITY00` is not specified yet, and it will be specified **before** any event is counted.

**LIVE ENABLED = NO.**
