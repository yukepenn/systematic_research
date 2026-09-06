# MC-58 — breadth-washout REBOUND (long side), modern leg — trial G00055

**Run:** `G2_F14_MC58_REBOUND_20260906` · **Registered:** 2026-09-06 (spec committed before results)
**Verdict:** **CLOSED-AS-GENERIC-MR (PERMANENT)** · **survives_info_gate = False**
**Evidence status:** DISCOVERY_CONSUMED · **Promotion:** NONE · **Spend:** $0 · **Live:** NO
**Scope:** REGIME-LOCAL 2023-01-05 → 2026-05-29 internals population. **Era leg NOT in this run** (data-gated).

## G1 sentence

On the modern leg, buying 1 NQ at the open of the first 1-min bar **after** the first afternoon
takeout of the morning low, on bottom-tercile (trailing-252 causal) 11:00 cumulative adjusted-TICK
sessions, held to the 15:59 close at ALL_IN $40/RT, earns **-$60.97/event (t = -0.33, n = 154)** and
**loses to the identical trigger on non-tercile takeout sessions (+$47.73/event, n = 256; increment
-$108.71/event)** — so the banked +9.62pp G00030 washout state does **not** monetize as a rebound
long; the trade is a generic post-cross mean-reversion that the weak-breadth condition makes *worse*,
not better.

## Why this verdict (preregistered taxonomy)

The spec's anti-rescue gate makes **B2(i) — beating the same trigger on NON-bottom-tercile takeout
sessions — THE PRIMARY DISCRIMINATOR**, because the only thing separating this card from the fade
graveyard (TICK fade, sweep-reclaim, the seven 2022-era geometries, SWEEP01 generic post-cross MR,
W118 endogenous-trigger reversal) is the single banked state fact (+9.62pp, G00030).

Observed: **control ($47.73) >= candidate (-$60.97)**, increment strongly negative (-$108.71). The
preregistered taxonomy routes this directly:

> B2(i) control >= candidate OR increment ~= 0 => **CLOSED-AS-GENERIC-MR (permanent)** — collapses
> onto SWEEP01 + W118.

This is **not** a CLOSED-BY-POWER middle: that branch requires a *positive* increment under the
increment-MDE. Here the increment is negative, so the closure is the strong, permanent one and is
correctly labeled as such. It is also not merely under-powered noise being over-claimed — the point
estimate says weak breadth actively *hurts* the rebound (control wins), consistent with the earlier
BREADTHPM01 finding that the afternoon short was "worse than random shorts" and the recorded
washout-then-rebound shape: on weak-breadth tapes the flush is more persistent, so the low is more
likely taken out (the +9.62pp fact) **and** the bounce is weaker.

## Gate table (program-printed -> `out/gate_table.txt`)

| GATE | OBSERVED | PASS/FAIL |
|---|---|---|
| G0 seal / POINTS | maxTICK 2026-05-29, maxNQ 2026-05-31 (<= 2026-05-31); POINTS basis | PASS |
| G1a manifest/prov | TICK sha 72612a1e... ok, NQ sha 87aa53f0... ok | PASS |
| **G1b MDE-first barrier** | B1 mean-MDE **$515**, B2 increment-MDE **$738** printed BEFORE return table | PASS |
| B1 economics | mean = -$60.97, t = -0.33 (needs >0 & t>=2) | FAIL |
| **B2(i) PRIMARY** | increment -$108.71 (cand -$61 vs ctrl +$48) | FAIL |
| B2(ii) random | obs -$60.97 vs p95 +$432.42 (10,000 count-matched random longs) | FAIL |
| B3 circular-shift | obs -$60.97 vs p95 +$329.15 (10,000 family-shared offsets, K_eff=154) | FAIL |
| timing-teeth | base -$67 -> +30m -$171; band vacuous (base <= 0) | FAIL/NA |
| concentration | top-1 abs(event) = 2.7% of sum-abs-net (CLASSIFICATION ONLY) | INFO |

**MDE-first barrier (G1):** the power block (n=154, 45.4 events/yr; pre/post-breach decomposition of
the 263 bottom-tercile sessions into 154 breached + 109 not-breached; B1 mean-MDE $515.14/event;
B2 increment-MDE $738.24/event) was printed **before any observed mean or return table**, so the
detectable-effect scale was committed ahead of the outcome. Note both MDEs dwarf any plausible edge:
per-event net SD is ~$2,282 (candidate) / ~$3,020 (control), so this population could never have
powered a small increment — but that is moot here because the increment's *sign* is negative.

## Timing-teeth (`out/delay_curve.csv`)

| delay | mean net (common n=151) |
|---|---|
| +0m | -$66.95 |
| +5m | -$38.58 |
| +15m | -$113.94 |
| +30m | -$170.86 |

The delay band ("+30m must lose >= 40% of mean net; a FLAT curve falsifies the flush-anchored
mechanism") is **vacuous** here because the base mean net is not positive — there is no positive
flush-edge for a delay to erode, so the mechanism is simply not defended. `curve_decays_per_band =
False`. (The curve is not flat, but a non-positive base cannot license a "survives" reading regardless.)

## Concentration (classification only)

Top-1 event contributes 2.7% of sum-abs-net, top-5 12.2% — the loss is broad, not one-print. Carried
note: **"the incumbent fails this bar at 236.8%" (F9)**. Never a kill-gate; printed for classification.

## One hand-checked event (2023-01-05)

Morning low (9:31-11:00) = **13960.75**. First afternoon bar with low < morning low = **15:51**
(low 13958.75). Entry = open of the next bar, **15:52 = 13960.00**. Exit = 15:59 close = **13968.00**.
Gross = +8.00 pts -> net = 8.00 x $20 - $40 = **+$120.00**. Matches `event_table.csv` row 1 exactly
(takeout_min 951, entry_min 952, entry_open 13960.00, exit_close 13968.00, gross_pts 8.00,
net_usd_allin40 120.00). Verified against raw `nq_1m` bars.

## Prohibitions honoured / deviations

- Entry is **event-time** (bar after the takeout bar), never state-time 11:01 full-window. No drift
  to the barred full-window mirror long.
- No tercile/delay/exit search; no stops; no reclaim gating; no era pooling. State construction is
  the **G00030 verbatim** pair (same quality filters, causal trailing-252 terciles, POINTS takeout);
  counts reproduce exactly: 842 classified, 263 bottom-tercile, 154 candidates, ~258 control.
- **Data hygiene deviation (memory-only, result-neutral):** to honour the task instruction "never
  materialize >= 2026-06-01", both parquets are read with a pushdown filter `time < 2026-06-01`
  *before* the verbatim `normalize() <= 2026-05-31` filter. The G00030 reference loads full frames
  then filters; the pushdown changes only what is briefly in memory, not the computed population
  (there is no 2026-05-31->06-01 RTH data), so the state construction is byte-identical.
- Control lost 2 of 258 non-tercile takeout sessions as unenterable at/before the 15:59 exit
  (takeout too late for a post-takeout entry bar); n_ctrl = 256. All 154 candidate events were
  enterable (0 dropped). Reported in the power block.

## Decision-rule consequence

Per the spec: any closure -> a **FAILURE_MEMORY row at the exact, correctly-labeled scope**. This is
**CLOSED-AS-GENERIC-MR (permanent)** for the *rebound-long monetization* on the modern leg. The
G00030 **information** finding (+9.62pp) is untouched — information and monetization are separate
ledgers — but its long-side rebound monetization is now closed, alongside the earlier short-side
closure (BREADTHPM01 / G00033). The reclaim-anchored variant was **not** run (prohibited; gateable by
no future card without a fresh window). Era leg remains DATA-GATED and does **not** run (it runs only
after a modern B1+B2 pass — which did not occur — so the one-shot pre-2022 read is not spent here).
