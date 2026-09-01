# TRUNCATION BLAST RADIUS — the silent-truncation defect, complete

**2026-09-01.** First complete caller-exposure audit. Partial statements existed in five
scattered places; **no repo-wide inventory did.**

---

## §1 THE MECHANISM — and the two things the repo got wrong about it

`research/weekly_edge/src/run_we_w17.py`, `load_deep(a, b)`:

```python
:35  df = pd.read_parquet(".../scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet")
:51  df = df[(df["time"] >= a) & (df["time"] <= b)]...
```

Line 35 hardcodes a file whose last row is **2026-05-29 16:59**. Line 51 is a **boolean mask,
not a range assertion**: `time <= "2026-07-31 17:00"` selects every row of a file that stops in
May, and raises nothing. There was no `assert max >= b`, no row-count check, no warning.

> **The defect was never `extend`. `extend` is the FIX** (added 2026-08-26, commit `33aa197`).
> **The defect is the SILENCE**, and adding `extend` did not remove it — it only gave callers a
> way to opt out, which every pre-existing caller physically could not do because the parameter
> did not exist when they were written.

**Truncates ⟺ `b > 2026-05-29 16:59` AND `extend is not True`.** Requests ending on or before
2026-05-29 are unaffected — they never needed the missing rows.

**Magnitude: 61,547 bars ≈ 44 trading sessions** (2026-05-29 17:00 → 2026-07-31 16:59).
For 2026 specifically: **106 sessions reported where 152 exist — a 42 % undercount.**
⚠️ The repo states this as "44" (W76 spec, `holdtime.txt`) and "46" (W76 REPORT). **UNKNOWN which
is right**; resolved only by counting sessions in the extension file. It does not change any verdict.

## §2 🔴 THE VECTOR NOBODY FIXED — and it kept catching people

`research/weekly_edge/src/run_we_w51c.py:38` — the campaign's shared substrate entry point:

```python
def setup():
    D = load_deep("2022-01-01", "2026-07-31 17:00")     # no extend. 22 files import this.
```

**It was never modified when `extend` landed.** Independently counted at `ce6627e`:

| | count |
|---|---:|
| direct `load_deep` calls asking through `2026-07-31` with no `extend` | **52** |
| files doing `from run_we_w51c import setup` | **22** |
| files in `weekly_edge/src` reading the truncated base parquet directly, bypassing `load_deep` | **5** |
| calls that correctly pass `extend=True` | 81 |

> **Three files committed 2026-08-31 — five days AFTER the fix — still routed through `setup()`
> and silently inherited the defect**: `G3_SHORTALPHA_20260831/src/{decay/build.py,
> holdtime/build_trades.py, asymmetric-cost/run_asymcost.py}`. One of them
> (`decay/analyze.py:870`) even *prints an explanation of the defect* while its sibling consumes it.
> A fix that leaves the trap armed is not a fix.

⚠️ **The 5 direct-parquet bypasses are invisible to every `extend=` grep anyone has run** —
including `run_we_w57.py:31-32` and `run_we_w62.py:32`. Searching for `extend` cannot find them.

## §3 THE FIX — loud, not silent, and it does not rewrite history

`load_deep` now raises `SubstrateTruncationError` when the request overshoots the data's own end
by more than a day. One day of slack is deliberate: callers legitimately ask for `17:00` when the
last bar is `16:59`. **The real defect was 63 days wide**, so the margin costs nothing.

```
load_deep asked through 2026-07-31 17:00 but the substrate ends 2026-05-29 16:59 -- short by 63 days.
  Choose ONE, explicitly:
    extend=True            -> load through 2026-07-31 (the CORRECT choice for new work)
    allow_truncation=True  -> reproduce a pre-W76 wave bit-exactly, on purpose
```

**`allow_truncation=True` preserves exact bit-reproducibility** of the pre-W76 waves — the reason
`extend` defaulted off in the first place. Nothing historical is rewritten; a *deliberate*
reproduction now has to say it is deliberate.

Locked in by `research/weekly_edge/src/test_load_deep_coverage.py` — **5/5 PASS**, including
`test_setup_wrapper_no_longer_defaults_to_lying`.

## §4 WHAT IS ALREADY MEASURED — the corrections that exist

These are **already computed and published in other runs' outputs**, and are not in doubt:

| wave | published | corrected under full data | source |
|---|---|---|---|
| **W61** | 2026 short sleeve **−10.62 pts/session** | **−3.64** over 152 sessions. The unseen window ran **+12.46 pts/session across 46 sessions.** Decay gate G4 → **10.9th pct, FAIL** | `G3_SHORTALPHA/out/decay.txt:594-597` |
| **W76 (P1, 2026)** | $33,467 · 15.79 pts/sess · DD $12,607 | **$12,781 · 4.20 pts/sess · DD $24,225** — *"P1 is not shippable as it stands"* | `WE_W76_FORWARD2026/REPORT.md:99-133` |
| **W75** | `K_admissible = 2` | **1** — the 2 was an artifact of the truncated substrate | `WE_W79_CLIQUE/REPORT.md:29-45` |
| **W67** | Solar **7.26** pts/session | **6.64** | `WE_W91_FUSEVSPORT/REPORT.md:27-29` |
| AXISB | $66,581 | $43,766 | `WE_W79_CLIQUE/REPORT.md:29-45` |

🔴 **W61, W62 and W73's own `REPORT.md` files were never amended.** Zero hits for
`truncat|extend|W76|SUPERSEDED|CORRECTION`. Their corrections live only in *other runs' output
files*. **Anyone reading those reports directly still gets the withdrawn conclusion.** That is
editorial debt, and it is the cheapest item on this page.

## §5 CLASSIFICATION

| category | waves |
|---|---|
| **CANONICAL OBJECT CHANGE** | none. `CURRENT_BASELINE.md` cites the entire W17–W75 range **exactly once** (W72), so the baseline is largely insulated. The doctrine documents are not. |
| **GATE CHANGE** | **W61** (decay G4 now FAILS at the 10.9th pct) |
| **MATERIAL INTERPRETATION CHANGE** | **W76-P1-2026** (2.6× smaller, DD 1.9× larger); **W75** (`K_admissible` 2→1) |
| **NUMERIC CHANGE, VERDICT SAME** | **W67** (7.26→6.64); AXISB |
| **EXPOSED, UNMEASURED** | the rest of §2's 52 + 22 + 5 — see the ranked list below |
| **NO EFFECT** | the 81 `extend=True` calls; every request ending ≤ 2026-05-29; W01–W16 (they load the *extended* file) |
| **EXPOSED BUT DELIBERATE — do not "fix"** | `G3_SHORTALPHA/src/native/run_native.py:390`, `holdtime/measure.py:117` (asserts `n == 1558497`), `holdtime/evaluate.py:112`. They pin the truncated substrate **on purpose**, so the B1 gate reproduces W61/W73 exactly. These now need `allow_truncation=True`. |

## §6 RANKED RE-RUN CANDIDATES

Ranked by *published conclusion still load-bearing* × *exposure*. Citation counts are from
`PRINCIPLES.md` / `STATE_OF_THE_SYSTEM.md`, where the exposed waves actually survive.

**Tier 0 — already done.** `run_we_w51c.py:38`. Not a re-run; a code fix. Done at this commit.

1. **W57 `BMOMREGIME`** — exposed via **direct base-parquet read**, so invisible to every
   `extend=` grep. **Most-cited exposed wave in the doctrine** (7× PRINCIPLES, 8× STATE). Never
   named in any correction. **Highest value.**
2. **W59 `REOPTIM`** — a *re-optimisation* whose parameters were selected on a substrate missing
   its most recent 44 sessions. Its output feeds W60, W71, W74: fixing one fixes four.
3. **W74 `WEEKMATH`** — most-cited derived wave (8× STATE), triple-inherits (W59 + W61 + W72).
4. **W51/51b/51c/51d/53/54/55/55b** — the "don't-trade" E4 family. W51d is described in source as
   *"the binding test"* — a binding null evaluated on truncated data.
5. **W41 / W42** — clock and exit families, 5× each. W41's adoption was already withdrawn once for
   an unrelated full-sample-quantile defect; this is a second, independent one.
6. **W38 / W39 / W40** — vote/features/second-engine core. `WE_W76/REPORT.md:133` explicitly says
   W38's withdrawal of short-sleeve "insurance" *"deserves re-examination."*
7. **W67** — known-wrong; one number was corrected, the wave was not re-run.
8. **W61 / W62 / W73** — quantitatively reversed already (§4). Ranked here **only because the
   correction is measured**; the remaining work is **editorial and urgent** — the three REPORTs
   still publish withdrawn conclusions with no notice. W62 and W73 have no re-measured replacement.
9. **W18 / W19 / W20 / W29** — W29 is the origin of the campaign's **80 % out-of-sample retention
   bar**, which W76 then applied. The bar itself was calibrated on truncated data.
10. **W44 / W44b** — NT8 parity, window `2025-11-01 → 2026-07-31`, so the truncation removed
    **~2 of 9 months — the largest proportional loss of any exposed run.** Parity verdicts are
    load-bearing for the live book.

## §7 🔴 THE CONSTRAINT THAT LIMITS ALL OF IT

`STATE_OF_THE_SYSTEM.md:303-311` retracts W76's "virgin window" claim, and `CLAUDE.md` §5 confirms:
**2026-05-31 → 2026-07-31 is BURNED.**

> Re-running an exposed wave with `extend=True` recovers **correctness**, not a clean out-of-sample
> read. Every re-run must be tagged **`DISCOVERY_CONSUMED` / `DIRECTLY_BURNED`**, never `FORWARD`.
> The missing 44 sessions are not new evidence. They are the sessions the campaign already spent.

Which is why **no re-run is scheduled by this audit.** The code is fixed, the exposure is
inventoried, and re-running is now a preregisterable decision with a known, non-zero evidence cost.
