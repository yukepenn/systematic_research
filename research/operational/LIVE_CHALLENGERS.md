# LIVE CHALLENGERS — the promotion pipeline, and how to invoke it

The champion is **`M_11` = `P1/PCT` ×1 + `XM_CONFLICT` ×1, as TWO INDEPENDENT LEGS.**
Not `WeeklyEdgeBookM11_v1` (that class NETS the legs — a measurement convenience). Not the research
inverse-vol Portfolio B. **Three different objects; keep them separate forever.**

**M_11 stays the incumbent until beaten.** It is not defended because it was expensive to build, and
it is not replaced because something looks exciting.

## THE TEN STAGES

| # | stage | where it runs |
|---|---|---|
| 0 | mechanism — one sentence of economic reason | research wave |
| 1 | data — can the inputs be obtained CAUSALLY now? | research wave |
| 2 | spec — **committed before any P&L** | research wave |
| 3 | causality — negative AND positive probes | research wave |
| 4 | implementation — primary | research wave |
| 5 | development economics — after cost | research wave |
| 6 | adversarial — nulls, chronology, concentration, era, cost | research wave |
| 7 | portfolio — incremental value vs M_11 at COMMON RISK | research wave |
| **8** | **independent re-implementation + NinjaScript** | **`build_wave.js`** |
| **9** | **parity — research ↔ NT8, trade-for-trade** | **`build_wave.js`** |
| **10** | **live readiness — warm-up, rollover, logging, account, fills** | **`build_wave.js`** |

Stages 0–7 are the Tier-1/Tier-2 research waves. **Stages 8–10 are pre-built and ready** — they were
the gap, and they are now closed.

## HOW TO INVOKE THE BUILD WAVE

```
Workflow({ scriptPath: "<repo>/research_sdk/workflows/build_wave.js",
           args: { candidate: "SHORT_ORB_V1",
                   spec_path: "runs/T2_ORBSHORT_20260831/spec.md",
                   mechanism: "<the FROZEN one-sentence mechanism>",
                   python_ref: "research/weekly_edge/src/<ref>.py",
                   instrument: "NQ 09-26",
                   session_template: "CME US Index Futures ETH",
                   expected_direction: "SHORT" } })
```

⛔ **It refuses to run without a `candidate`.** It is not a research tool — it only promotes an
object that has ALREADY survived standalone economics and the adversarial kill. The mechanism is
**frozen**: it may not change a threshold, horizon, sign, feature or session window. If the object
does not survive implementation the correct output is a **FAILED BUILD REPORT**, not a modified
object.

It ends with two adversaries — an **NT8 deployment adversary** and a **statistical adversary** — and
assigns exactly one label:

- **`RESEARCH_ONLY`** — interesting, not executable / not evidence-ready
- **`PAPER_READY`** — fully causal, executable, parity-certified; evidence not yet sufficient for real money
- **`LIVE_READY`** — engineering complete AND evidence compelling enough to *consider* real money

⚠️ **`LIVE_READY` does not auto-enable orders. The owner retains real-money authorization.**

## THE ACCEPTANCE SET IS CODE, NOT A CHECKLIST

`research_sdk/live_readiness_check.py` — `--selftest` (10/10, every guard proven to fire) and
`--tags p1pct,xm2`.

> 🔴 **THE DEFAULT INVOCATION CHECKS THE PAPER BOOK ONLY.** `DEFAULT_WARMUP` / `DEFAULT_EXPORT`
> (`live_readiness_check.py:46-47`) are `C:\NT8_ForwardLogs\warmup` / `\export` — `DEMO8383477`'s
> directories. **The LIVE book writes to `C:\NT8_ForwardLogs\mnq\`.** To check the real-money book
> you MUST pass them explicitly:
>
> ```
> python research_sdk/live_readiness_check.py --tags p1pct,xm2 ^
>   --warmup C:\NT8_ForwardLogs\mnq\warmup --export C:\NT8_ForwardLogs\mnq\export
> ```
>
> **Run it for BOTH books.** A PASS on the defaults says nothing about `2047681`.

Each assertion was bought with a specific failure:

| | check | why it exists |
|---|---|---|
| **R1** | **`ROLL-PLAN blockNewEntriesFrom` is in the FUTURE** | 🔴 **The only check that catches a permanently-latched book.** The guard resolves ONCE and is monotone, and `GetNextRolloverDate` is root-level so it cannot tell you already rolled. A latched book reads Enabled · Realtime · bars advancing · warm-up GO · flat and **passes every other check on this list.** |
| R2 | warm-up `GO`, `qual_entries ≥ 250`, `DaysToLoad ≥ 330` | a cold deploy loads ~4 sessions ⇒ size-1 only for ~3 months; the qty-2 bucket is ~43.5 % of delivered net |
| R3 | no `ROLL-BLOCK` / `ENTRY-BLOCKED` lines | |
| R4 | `WARMUP-CARRY-FLAT` — ledger reconciled at transition | |
| R5 | instrument guard ARMED | `ExpectInstrument` defaults to `""` = **disabled**, and shipped that way through the whole first forward window |
| R6 | decision ledger writing — **verified BY READING** | ⚠️ a directory size of 0 on an open handle is a **metadata artifact**; a 46,313,472-byte file reported 0 B for over an hour and I wrongly called it data loss |
| R7 | all series on the SAME contract month | a partial roll trades Dec NQ against Sept secondaries |
| R8 | `DaysToLoad ≥ 330` | convergence measured at ~9 months (decision state) / ~10.5 months (position SIZE, which binds) |

## TWO SOURCES THAT LIE — never build a monitor on them

1. **The deployment registry.** `DisableStrategy` does not clear it; it has reported **3 deployments
   when 2 strategies existed.** Count with `ListAllStrategies`.
2. **`live.performance.net_profit_currency`.** That is `DaysToLoad` warm-up **simulation** presented
   inside a block labelled *"live"*. And on a 4-series strategy the scalar `current_bar` /
   `instrumentName` report a **secondary series** — read `currentBars[0]` and `instruments[]`.

## CURRENT CHALLENGER BOARD

| challenger | status |
|---|---|
| `WeeklyEdgeP1PCT_v3` / `XMConflict_v4` | **DEPLOYED** — parity 0/2,439 and 0/378, durable-ledger fix only |
| ORB control | reproduced exactly, **t 2.1944** (591 L / 542 S) — a control, not yet a candidate |
| two preregistered SHORT mechanisms | ❌ **FAILED** |
| `P1_BOX_INVARIANCE_00` | Gate A PASS, **Gate B FAIL** — nothing frozen, **no economics run** |
| `TICK01ERA` | 7 events on 2013/2015/2017 — **not a decidable test**; widened as `TICK01ERA2` |
| XM direction economics · XM cost audit · FLOWSUB Stage 0 · P1 sizing | in flight |

**`INCUMBENT CHANGE: NONE`** — nothing has beaten M_11 yet, which is the expected first-day result.