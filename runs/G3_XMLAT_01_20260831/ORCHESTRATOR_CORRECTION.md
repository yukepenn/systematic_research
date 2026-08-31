# ORCHESTRATOR CORRECTION TO `G3_XMLAT_01`

The run's nine gates, its X5 decomposition and its `retain_rule` verdict all stand. I independently
reproduced the two load-bearing scale checks and they hold (see §3). **One finding is corrected, and
it is corrected because it is a claim about LIVE SAFETY.**

---

## 1. 🔴 CORRECTED: "the `MaxStaleMinutes=3` session-level rule is the largest unclosed risk here"

**The structural insight behind it is right. The risk conclusion drawn from it is wrong about the
object we actually run.**

### What is right, and it is a genuinely good finding

The cross-market composite is `mean_k( r_k / σ_k )`. A ±0.5·σ_k shock to market *k* therefore moves
the composite by exactly ±0.5/count **regardless of which k**. That is why X1-POS returned flip
rates of *identically* 17.40% for ES, RTY and YM — structural, not a bug. **Every cross-market leg
has exactly equal marginal influence, so a stale YM feed is exactly as dangerous as a stale ES
feed.** That was worth finding and it is retained.

### What is wrong

The claim that the staleness rule is **session-level** and therefore "does not protect against
intraday staleness" describes the **Python reference**, not the **executable**.

`export_xm_reference.py:86-93` disqualifies a session when the anchor or decision *index* is missing
— a session-level construct, because the reference works from a daily-indexed frame.

`WeeklyEdgeXMConflict_v4.cs` does something materially stronger, at **minute** resolution:

```csharp
:982   private bool SeriesFresh(int i, DateTime nqTs)
:984       if (CurrentBars[i] < 1) return false;
:985       double age = (nqTs - Times[i][0]).TotalMinutes;
:986       return age >= -0.5 && age <= MaxStaleMinutes;

:1044  ANCHOR   (09:31)  for (i=1..3) if (!SeriesFresh(i, ts)) fresh = false;
                         if (!fresh) sessionDisqualified = true;   // no stale forward-fill, ever
:1059  DECISION (09:45)  for (i=1..3) if (!SeriesFresh(i, ts)) fresh = false;
                         if (!fresh) sessionDisqualified = true;
```

The guard runs **at both clock instants that matter**, **per series**, comparing each secondary's
latest *minute bar* timestamp against the primary's. If any of ES/RTY/YM is stale, **the session is
disqualified and no trade is taken.** NinjaScript's silent forward-fill — which is the actual hazard
the finding was reaching for — is exactly what this closes, and the source comment at `:73-76` says
so in those words.

### The residual risk, stated at its true size

A **3-minute tolerance is still a tolerance.** A secondary series up to 3 minutes stale passes the
guard, so at 09:45 the composite could legitimately be built from an ES/RTY/YM close as old as
09:42. That is real contamination, but it is **bounded, documented, and deliberate** — not an
unguarded hole, and not "the largest unclosed risk here."

**Corrected ranking of XM's unclosed risks:**

| rank | risk | size |
|---|---|---|
| 1 | **XM does not carry its own risk** — `G3_INCUMBENT_BASELINE_00`: −$182/wk at matched ES95, −$640/wk at matched maxDD | the book-level question |
| 2 | XM's weekly mean is itself uncertain to **±$550** (95% CI $199–$1,305) | dwarfs everything below |
| 3 | far-side vs print fill, **$6.21/wk unbooked** (the run's own finding #4) | real, small, and NOT latency |
| 4 | up-to-3-minute secondary staleness inside a guard that does fire | bounded |

## 2. ⚠️ THE GUARD HAS NEVER ONCE RUN LIVE — and that is a schedulable check

`HdXmAgeRow` is `State.Realtime`-gated (`if (State != State.Realtime) return;`) and writes to
`DiagDir`. **`C:\NT8_ForwardLogs\diag` is empty**, and the reason is mundane rather than alarming:

| deployment | when (ET) | vs the 09:31 anchor |
|---|---|---|
| `dep_55403f7de5f5` | 2026-08-30 09:51 | Sunday — no RTH |
| `dep_51bf1a7382cb` | 2026-08-31 10:27 | **after** today's anchor |
| `dep_27ff47e7e3b7` (live) | 2026-08-31 12:32 | **after** today's anchor |

Every XM deployment so far began *after* 09:31 ET, so the anchor and decision blocks have never
executed in `Realtime`. **The first live observation of the actual staleness margins will be
2026-09-01 at 09:31 ET.** Until then the guard is verified by source reading only.

⇒ **Monitoring item for the next session: read `C:\NT8_ForwardLogs\diag` after 09:46 ET on
2026-09-01 for the `ANCHOR` and `DECISION` rows and record the observed `ESAgeMin` / `RTYAgeMin` /
`YMAgeMin`.** If any routinely exceeds ~1.0, the 3-minute tolerance is closer to binding than the
source suggests. This costs nothing and needs no new instrumentation.

## 3. WHAT I REPRODUCED INDEPENDENTLY, AND IT HELD

- **XM's weekly noise dwarfs every latency effect.** From my own baseline (weekly SD $4,398,
  n = 243): SE $282, 95% CI **[$199, $1,305]**, width **$1,106**. The run reports [$224, $1,239] on
  its own window. **The entire latency effect of $17–74/wk is 2–7% of the uncertainty about whether
  XM works at all.**
- **The population correction is real.** The −$74.18/wk figure belongs to 346 trades / **213 ISO
  weeks** (2022-07-01 → 2026-08-01). My first cross-check said 349 trades / 180 weeks and the
  difference is my own convention error: 180 counts weeks *containing* an XM trade, whereas the
  denominator of a $/wk figure must be **all** weeks in the window (~213). The run's population is
  correct and mine was not.
- **The `SeriesFresh` correction above** was found by reading the source the run cited, which is the
  only reason it surfaced.

## 4. WHAT REMAINS UNCHANGED

`retain_rule` fires. E = **$918.35/wk** against a $468.16 downgrade threshold (**1.96×**); a 250 ms
fill retains **98.1%**; the most pessimistic break-even latency (16 s) is **63×** a 250 ms fill.

> **XM's edge is not latency-fragile. XM is not an execution strategy, and the −$74.18/wk figure is
> a red herring for deployment.** Its problem lies elsewhere — see risk #1 above.
