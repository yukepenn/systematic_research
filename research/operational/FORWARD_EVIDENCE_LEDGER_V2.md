# FORWARD_EVIDENCE_LEDGER_V2 — the home for real-money evidence

**Built 2026-09-01.** Code: **[`research_sdk/forward_ledger_v2.py`](../../research_sdk/forward_ledger_v2.py)**
— `python -m research_sdk.forward_ledger_v2` → **21/21 adversarial tests PASS**.
Data: `research/operational/forward_v2/{decisions,outcomes,gaps}.csv`.

**V2 does not replace v1 and does not touch it.** `SHADOW_START` and the v1 hash chain are
frozen by `PROSPECTIVE_SHADOW.md` and remain frozen. V2 runs alongside.

---

## §1 THE GAP IT CLOSES

Since 2026-09-01 the campaign trades real money on `2047681`. The v1 chain **cannot record it**:

- `shadow_runner.py:35` — `TARGET_ACCOUNTS = {"DEMO8383477", "Sim101"}` excludes it **by design**.
- `shadow_runner.py:34` — `SHADOW_START = 2026-09-01T18:00:00-04:00` **post-dates** the live
  book's first realtime bar (00:42 ET), so even the account filter is not the only barrier.

> The highest-quality evidence this campaign has ever produced — its **first non-simulated
> fills** — had nowhere to go.

## §2 THE THREE CLOCKS — and why they may never be merged

| clock | instant (ET) | book | how it was pinned |
|---|---|---|---|
| `OWNER_FORWARD_START` | 2026-08-30 18:00 | PAPER_NQ | first realtime bar of both certified NQ legs |
| `LEGACY_FORMAL_SHADOW_START` | 2026-09-01 18:00 | PAPER_NQ | `shadow_runner.py:34`. **Frozen. Never moved.** |
| 🔴 **`LIVE_FORWARD_START`** | **2026-09-01 00:42** | **LIVE_MNQ** | **mechanically, from the NT8 log** — see below |

### How `LIVE_FORWARD_START` was pinned, and what it is not

From `log.20260901.00000.txt`: P1 `399562885` enabled **00:31:01.219** (`WARMUP GO`,
`DaysToLoad 365`); XM `399562886` enabled **00:41:32.494** (`WARMUP GO`, `DaysToLoad 365`).
Both legs are simultaneously Realtime and GO from **00:41:32**; the first full minute bar after
that is **00:42:00**, and that row exists in the live XM ledger.

- **Deliberately the LATER of the two legs.** A book clock never claims evidence before both
  legs had it.
- 🔴 **It is not, and cannot be, the first profitable anything.** At pin time the account had
  taken **zero trades** — `ListOrders`, `ListExecutions` and `ordersCount` all empty. The clock
  is fixed by an engine event *before any outcome existed*, which is the whole requirement.
- It is a **decision** clock, not an execution clock. The first `FORWARD_EXECUTION_REAL` row
  will come later and separately.

### Paper fills and live fills never pool

Paper fills are `SIMULATED_FILL_NON_EVIDENTIAL` — a Tradovate server-side demo engine with
unlimited liquidity at one price. **That is a ZERO-information class, not a low-power one**: no
`N` makes it informative, so it is immune to the "just collect more" argument. Live fills are
`FORWARD_EXECUTION_REAL`.

**The schema refuses to mix them.** `append_outcome` reads the referenced decision's `book` and
raises if a `PAPER_NQ` decision is given a real-fill class, or a `LIVE_MNQ` decision a simulated
one. `health()` reports **per class** and never pools.

## §3 WHAT V2 FIXES THAT V1 GOT WRONG

| # | v1 | v2 |
|---|---|---|
| 1 | 🔴 **`quality_status` is hard-coded `"OK"`** (`shadow_runner.py:145`) — it can never emit `BLOCKED`/`GAP`. An outage is indistinguishable from a quiet market. | **`append_gap()`.** An outage is a first-class row. **The 2026-09-01 P1 writer death is recorded as evidence, not as absence.** |
| 2 | Fields repurposed away from their names: `config_hash` holds an `OrderId`, `source_hash` holds the literal `"NT8_SIM_STREAM_v1"`. | 31 named decision fields, validated. `source_sha256` is a sha256. |
| 3 | **Strict global monotonicity** — two legs deciding in the same minute cannot both be recorded; the second spills forever. | Uniqueness keyed on **`(ts, strategy_id)`**. Both legs coexist; a genuine duplicate is still refused. |
| 4 | 🔴 **CSV append is not atomic.** A mid-write crash leaves a truncated final line, and `_read` then raises on every later call — **one bad write bricks the ledger**. | Write-to-temp + `os.replace`, with `fsync`. A crash leaves the **last good state**. |
| 5 | 🔴 **`COSTS_MODELLED` was not in `QUALITY`** — see §4. | In the enum, and the **seam** is tested. |

## §4 🔴 THE LATENT BUG THAT WOULD HAVE FIRED TONIGHT

`shadow_runner.exec_costs()` (`:88`) returns `data_quality="COSTS_MODELLED"` whenever the broker
reports **$0.00 commission — which is every execution this broker produces** — and passes it
straight to `append_outcome(data_quality=...)` at `:176`. But
`shadow_ledger.QUALITY` did **not** contain `COSTS_MODELLED`, so `append_outcome` raised
`LedgerError` and the row **spilled**.

> **Both sides were tested and both passed.** The runner's selftest (10/10) asserts `exec_costs`
> returns exactly that tuple. The ledger's selftest (11/11) asserts the enum rejects unknown
> values. **Nobody tested the join** — and the join is where the forward chain lives.

The failure mode is the worst kind: spillover is *by design* "recorded, never lost", so the
ledger would have quietly accumulated **decisions with no outcomes, forever**, while every
component reported healthy. The chain has zero rows, so it never fired. **It fires on the first
outcome after `SHADOW_START` = 2026-09-01 18:00 ET — tonight.**

Fixed by adding the value the emitter already intends to emit. `SHADOW_START`, `_canon` and
`_hash` are **untouched**; the chain is unchanged and still empty. Locked in by
`research_sdk/test_forward_seam.py` (**4/4**), which AST-extracts every quality literal
`exec_costs` can return and asserts the ledger accepts each one.

## §5 THE 21 ADVERSARIAL TESTS

Every attack the clean-set directive names, each of which **must fail loudly**:

| attack | result |
|---|---|
| backfill before the clock | REFUSED |
| naive / offset-less timestamp | REFUSED — instants, never strings (the DST defect) |
| paper decision filed on the live clock | REFUSED |
| wrong account for the clock | REFUSED |
| a FILL class on a DECISION row | REFUSED |
| `BLOCKED` with no reason | REFUSED — *why it did not trade is the evidence* |
| exact duplicate re-ingestion | REFUSED — idempotent |
| out-of-order decision | REFUSED |
| **two legs sharing one instant** | **ACCEPTED** — the v1 limitation, fixed |
| outcome for a nonexistent decision | REFUSED |
| **simulated fill on a live decision** | **REFUSED** |
| **real fill on a paper decision** | **REFUSED** |
| outcome preceding its decision | REFUSED |
| second outcome for one decision | REFUSED |
| editing any written row | **TAMPER DETECTED** by chain recomputation |
| `health()` returning performance | asserted impossible against a forbidden-field list |

## §6 STATE RIGHT NOW

`gaps.csv` — **1 row**, chain `71dc1c96…`, verified. Its content is the live P1 writer outage.

`decisions.csv` / `outcomes.csv` — **empty, deliberately.**

> Decision ingestion does not start while a leg's writer is dead. Ingesting now would bake the
> outage into the data as missing rows instead of recording it as a **named, bounded gap** — and
> silently-missing rows are exactly what this ledger exists to make impossible.
> **Ingestion begins once the owner restarts P1** (`OWNER_ACTION_20260901_P1_LEDGER_DEAD.md`).

## §7 STANDING RULES

1. **Never move a clock backward.** Never merge two clocks.
2. **A blocked decision, a disconnect, a rejected order, a restart, a rollover and a dead writer
   are all DATA.** Record them. Silence is not evidence of absence.
3. **Never relabel a simulated fill as real, or a real fill as simulated.** The schema enforces it.
4. **Never edit a decision row to carry its outcome.** That edit is the act that destroys the
   evidence class.
5. **Test the seams, not only the parts.** Two green selftests either side of an untested join is
   how §4 happened.
