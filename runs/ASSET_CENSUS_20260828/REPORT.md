# PHASE 2 — asset census. **ES BBO is 64 sessions and ZERO of it has ever been read.**

| | |
|---|---|
| **method** | bounded option-value census. **No price read, no hypothesis proposed, no model fitted** |
| **headline** | **ES BBO price-side: 64 RTH-complete pre-seal sessions, outcome-consumed = 0** |
| second finding | **no genuinely new multi-market root with usable depth exists.** "Add more roots" is `CLOSED-BY-DATA` |
| third finding | **15 sessions have BOTH ES and NQ sides unread** — enough for a one-shot blind falsification |

---

## 1. The registry

| asset | usable pre-seal | outcome-consumed | **genuinely unread** | blind pool possible? |
|---|---:|---:|---:|---|
| NQ **Last-only** blind pool | 141 | 0 | **141** | **is one** — but **no quotes**, so no bid/ask crossing can be priced |
| **ES BBO price-side** | 64 | **0** | **64** | ✅ **yes — the whole asset** |
| NQ BBO price-side | 116 | 97 | **19** | ✅ yes — frozen, `84a8575a…0931` |
| **ES ∩ NQ overlap** | 59 | 44 | **15** | ✅ **partial — 15 with both sides unread** |
| Multi-market daily | 2,315 dirs | 2,315 | **0** | ❌ every window read by trend or curve |
| NT8 minute store | 261 dirs | 261 | **0** | ❌ 123 weekly_edge waves + XM + W122 |

## 2. ES BBO — the finding, and how far it can be trusted

**64 RTH-complete pre-seal sessions**, 2025-08-13 → 2026-07-15, across `ES 09-25 / 12-25 / 03-26 /
06-26 / 09-26`. **Zero post-seal.**

> ### **The only code that has ever touched ES tick data is `esnq00_census.py`, written this
> ### session, which reads file names and hour labels and no prices at all.**

A repo-wide search for any run referencing ES tick contracts returns exactly that one file. There is
no ES microstructure substrate on disk. **ES BBO is the largest fully-unread quote-bearing asset the
project owns**, and unlike the NQ lane it could support **development and blind confirmation from a
single pristine asset** — a structure the NQ lane never had and can never retrofit.

⚠️ **The prior it must be judged against, stated honestly.** The causally-corrected NQ-only object
earned **−$1,785.88/session at OOF corr 0.0072**. That is one feature set, one model, one horizon —
not a proof — but it *is* direct evidence that **single-instrument price-side quote features carry
little at 60 s in this market structure.** ES is the same structure. **An ES-only repeat of that
hypothesis class has a low prior and would mostly re-spend a pristine asset to re-learn a null.**

## 3. Multi-market — "add more roots" is closed, not merely unattempted

`db/day` holds **2,315 instrument dirs across 38 roots** against a declared universe of 25. The 13
extras decompose completely:

| extra roots | verdict |
|---|---|
| `MGC MNQ MES MYM M6B MHG MCL MET MBT QM` | **MICROS of roots already in the universe** — same underlying, same curve, **zero new information** |
| `10YR` (8) · `2YR` (7) · `ZS` (5) | too few contracts for any protected chronology |

> **No non-micro root has ≥ 10 contracts.** So the natural rescue for `CARRY_V1`'s `n_sector = 2`
> degeneracy — "fetch more roots so sectors have ≥ 3" — is **`CLOSED-BY-DATA`.** That is worth
> knowing precisely because it was the most tempting follow-up, and it is now foreclosed by
> measurement rather than by discipline alone.

**What the multi-market substrate does still hold, at the right strength:** contract **volume** is in
every `.ncd` record and has been used **only as the roll criterion**, never as a signal input. That
is a genuinely different information surface — but it sits on **outcome-consumed dates** (2009–2018
TSMOM+CARRY development, 2019–2022 TSMOM validation, 2023–2026 TAIL-H1), so **no blind window can
ever exist for it** and it inherits family-selection debt. **Permanently discovery-grade.**

## 4. The distinction this census is built on

```
"these market dates were used somewhere else"
    does NOT consume every possible feature family on them

"this same OUTCOME was inspected while choosing THIS hypothesis"
    DOES create selection debt
```

Every asset therefore carries **two** fields — `outcome_consumed` (were forward returns computed on
these rows at all?) and `family_consumed` (which hypothesis families were chosen while looking at
them?). Multi-market daily is **outcome-consumed and family-consumed by trend and curve**; a volume
family is genuinely different but cannot claim an unread window. Conflating the two would either
sterilise usable data or manufacture a clean holdout that does not exist.

## 5. The NQ Last-only pool's real limitation, stated once

141 sessions, unspent, frozen at `fd7b05f`. **But its quote classes are `NONE` 101 / `PARTIAL` 40 —
it has no usable quote surface.** A strategy validated there cannot have its **bid/ask crossing**
priced, which is the execution contract every microstructure object in this campaign uses. It
remains an asset for a **Last-only** mechanism genuinely different from `MS-LAST-V1`, and **no such
mechanism is currently on the table.** It is not spent, and it is not spendable by anything now
proposed.

## 6. Cost and feasibility, measured

| | |
|---|---|
| exported NQ substrate | 2.3 GB / 58 sessions = **40.6 MB/session** |
| ES-only, 64 sessions | ≈ **1.5 GB** |
| ES + NQ, 59 overlapping sessions | ≈ **3.7 GB** |
| **free space** | **D: 170 GB free** (repo volume). **C: 24 GB — untouched, per the standing constraint** |

Export is **feasible and bounded**. It is not free: it needs a NinjaScript tick export per
instrument per session.

| | |
|---|---|
| pools consumed by this census | **none** — directory listings, file names, hour labels, sizes |
| seal | **7 post-seal NQ dates counted in an inventory; 0 for ES. Not read** |
