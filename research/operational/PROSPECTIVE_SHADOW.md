# PROSPECTIVE SHADOW — the only evidence class this project does not yet own

| | |
|---|---|
| **status** | **ARCHITECTURE READY. ACCUMULATION STARTS AT A FUTURE TIMESTAMP.** |
| created | 2026-08-28 |
| **LIVE ENABLED** | **NO.** Shadow is evidence accumulation, never authorization to trade |

> ### **Every result this campaign owns is discovery-consumed, validation-consumed, one-sided
> ### blind, or parity-only. The project has ZERO prospective evidence.** That is now its single
> ### largest structural gap, and no amount of further historical work closes it.

---

## 1. The one rule that makes this worth doing

> ### **NO BACKFILL. EVER.**
>
> A shadow ledger's entire value is that its rows were written **before** the outcome was known.
> One backfilled row destroys that property for the whole file, and it cannot be repaired by
> labelling. Accumulation begins at a **future full-session boundary**, strictly after the source
> and config hashes below were frozen.
>
> **Historical Playback is not prospective.** Re-running a strategy over stored bars produces
> exactly the evidence class we already have. If a row's outcome existed before the row did, it is
> not shadow evidence.

**`SHADOW_START = 2026-09-01 18:00 ET`** — the evening open of the first session strictly after
every hash in §3 was committed. No row before that timestamp may enter the ledger.

## 2. What shadow evidence is, and what it is not

| it IS | it is NOT |
|---|---|
| forward, un-consumed, one row per decision | permission to trade |
| the only path to confirming a discovery-grade candidate | a substitute for a preregistered forward checkpoint |
| accumulation that costs nothing but calendar time | a reason to re-tune a frozen object |

**Distinction that matters and is easy to blur:** *logging* shadow rows is not *reading* the sealed
pool for research. `WEEKLY_EDGE_FORWARD_PROTOCOL` still governs when `P1/PCT`'s post-seal
performance may be **adjudicated**, at its own preregistered checkpoints. Shadow rows accumulate
continuously; **reading them for a verdict requires its own preregistration.**

## 3. The shadow roster — what may accumulate, and why

| object | status | why it is in the shadow |
|---|---|---|
| **`P1/PCT`** | incumbent, parity-certified | the benchmark. Parity proves implementation fidelity, **not** forward alpha validity |
| **`XM_CONFLICT_v2`** | incumbent sleeve, parity-certified | its **hedge mechanism has inverted** (ρ 0.086 → 0.369, payoff when P1 loses +$598 → −$1,243). Forward data is the only way to learn whether it still earns its place |
| **`P1/ABS`** | **challenger/control** | PCT beats ABS on direction overwhelmingly (176/213 weeks, sign test p 7.1e-23) but **not** on paired magnitude (p 0.058). Burned data cannot settle it; running both from a common future timestamp can |
| **`MS-BBO-CANDIDATE-1`** | **discovery-grade, frozen** | **no clean BBO historical holdout exists or can be built.** Prospective evidence is not the next-best test for this object — it is the **only** test it will ever have |
| ~~TSMOM V2 / TAIL-H1~~ | **CLOSED** | both roles failed on two protected windows. Does **not** join the shadow |

**A new candidate joins only after its definition is frozen**, never before.

## 4. Ledger schema — one row per decision, written before the outcome

```
ts_decision          ISO-8601 with timezone, the instant the decision was made
strategy_id          e.g. MS-BBO-CANDIDATE-1
source_hash          sha256 of the frozen source
config_hash          sha256 of the frozen config/spec
signal               raw model output
side                 LONG | SHORT | FLAT
intended_qty         research units (fractional permitted; flagged as research sizing)
theoretical_fill     the crossing price the frozen execution contract specifies
executable_fill      simulated fill where a sim account provides one, else null
bid, ask, spread     quote state at the decision instant
slippage             executable_fill - theoretical_fill, null if unavailable
latency_ms           decision -> fill
ts_exit, exit_fill   exit leg, same contract
gross_pnl, costs, net_pnl
session_id           NT8 session identity
data_quality         OK | GAP | STALE_QUOTE | FILL_TIMEOUT
```

**`data_quality` is mandatory.** A shadow ledger that silently drops bad rows becomes a filtered
sample, which is the failure mode it exists to avoid.

## 5. Account-safety preconditions — blocking

Before any simulated order is emitted, the runner must **programmatically assert** that the target
account is a simulation/backtest/playback account. **If account identity is not positively
verified, no order is sent.** There is no fallback path to a real account, and none may be added.
`LIVE ENABLED = NO` remains binding and is not a per-strategy setting.

## 6. What would make this worth reading

Declared now so it cannot be invented later:

- **`MS-BBO-CANDIDATE-1`** trades ~200×/session, so it accrues sample fastest. Its first read should
  be preregistered on a **session count**, not a date, and not before **60 shadow sessions**.
- **`P1/PCT` vs `P1/ABS`** accrues at ~1.6 decisions/week; a paired forward read needs **far** more
  calendar than the BBO candidate. Do not read it early because it is available.
- **No object's shadow may be read to decide whether to keep accumulating.** That is peeking.
