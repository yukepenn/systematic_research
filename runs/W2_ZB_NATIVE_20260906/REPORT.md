# W2_ZB_NATIVE_20260906 — Stage-5 falsifier on ZB (the most orthogonal market, ρ≈0.06)

**Run:** `W2_ZB_NATIVE_20260906` — spec committed before results (trial **G00062**, family
`CROSS_ASSET_NATIVE`). **Instrument:** ZB (CBOT 30-yr Treasury bond future), 1-min,
**POINTS (32nds) basis** (DELEV01): $/pt = PV = $1,000, 1 tick = 1/32 pt = **$31.25**, 1 pt = 32 ticks.
**Window:** 2023-07-01 → 2026-07-31 (6-mo warmup from the 2022-12-26 data start, mirroring NQ/XINST).
**Evidence status: DISCOVERY_CONSUMED, in-sample.** No ledger promotion, no sizing, no deploy. Live
book `2047681` untouched. $0.

Two native engines were falsified to the P1 bar. **Neither survives.** Program-printed gates in
`out/gate_table.txt`; full transcript `out/run_log.txt`.

---

## Result in one line

**Leg A (intraday mean-reversion / range-fade) is COST-FRAGILE** — the per-fade gross reversion is
real and positive (t≈4–6, bootstrap CI excludes 0) but tops out at **0.19 ticks ($5.87)**, ~6× below
the **1-tick ALL_IN of $35.61** it must clear; weekly-vol-matched to P1 it is **−$14,991/wk, negative
even at a 0-tick spread**. **Leg B (08:30/14:00 scheduled-release vol/path) is VOL-ONLY-NO-DIRECTION** —
release-window RV expansion is large and highly powered (**08:30 ×2.90, FOMC ×2.51**, MDE printed
first, event-shift null p=0.0002), but the post-release *path* is not tradeable: continuation and
reversion of the first move are **both negative net of 2-tick** with non-significant nulls. The
diversification prize is real and useless: **daily ρ(ZB engine, P1) = +0.015** (weekly +0.008),
orthogonal exactly as the autopsy foretold (+0.064) — but there is no positive edge to diversify with.

**SURVIVES = FALSE.**

---

## G0 — seal + points basis (PASS)

- 1,086,151 bars / 925 sessions; **0 dropped ≥ 2026-08-01** (export pre-capped at the §5 boundary).
- `ASSERT max retained session 2026-07-31 < 2026-08-01` → **PASS**.
- `ASSERT all closes on the 1/32 grid` → **PASS** (max off-grid 0.00e+00). All range/box/RV math in
  POINTS/32nds; back-adjusted levels never used as thresholds.
- 370,512 RTH bars in the analysis window ([08:00,16:00) ET, the autopsy's volume-derived US
  cash-Treasury day session; end-stamped bars → RTH = end-stamp minute-of-day ∈ [481,960]).

## P1 reproduction (for orthogonality)

The validated bench (`XINST01…/src/xinst_bench.py`) reproduces the committed P1/PCT figures **exactly**
inside this run: weekly **$1,393.573663**, maxDD **$22,930.665853**, t **4.163612** (byte-for-byte the
`WE_W103` headline). P1's daily/weekly series are taken from that reproduction.

---

## LEG A — intraday mean-reversion / range-fade — **COST-FIRST → COST-FRAGILE**

**Rule (spec-literal):** fade the displacement from an intraday **anchor** ∈ {session VWAP, opening-
range midpoint} at a tradeable horizon **H ∈ {5,15,30} min**; enter when **|price−anchor| > k·σ**,
k ∈ {1,1.5,2}, where σ is the **trailing rolling std of the deviation** (60-bar/30-min-min-periods,
causal — a standard VWAP-band scale); short if price>anchor, long if below; **exit at anchor-touch or
H** (time stop). Cost band **ALL_IN = $4.36 comm + {0.5,1,2}-tick spread = $19.98 / $35.61 / $66.86**
per ctrRT. Realistic-tick gate = **1 tick → gross must exceed 0.03561 pt = 1.140 ticks**.

**Neighborhood (18 cells; gross reversion per NON-overlapping fade, then net of ALL_IN):**

| anchor | H | k | trades | gross (tk) | gross $ | t | CI-lo $ | **net@1tk** | uncond $ | circ-p |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| VWAP | 5 | 1.0 | 49,747 | 0.059 | 1.85 | 6.19 | +1.27 | **−33.76** | 1.69 | 1.000 |
| VWAP | 5 | 2.0 | 37,125 | 0.077 | 2.42 | 7.25 | +1.75 | **−33.19** | 1.69 | 0.985 |
| VWAP | 15 | 1.5\* | 18,049 | 0.113 | 3.54 | 4.52 | +2.00 | **−32.07** | 2.65 | 0.997 |
| VWAP | 30 | 1.0 | 12,213 | 0.173 | 5.42 | 4.30 | +3.12 | **−30.19** | 3.14 | 0.972 |
| VWAP | 30 | 2.0 | 8,956 | **0.188** | **5.87** | 3.89 | +2.94 | **−29.74** ← best | 3.14 | 0.685 |
| ORMID | 30 | 1.5 | 10,542 | 0.095 | 2.98 | 2.14 | +0.27 | −32.63 | 4.33 | 1.000 |

(\* = preregistered primary cell; full 18-row table in `out/legA_neighborhood.csv`.)

**Findings.**
1. **The reversion is real but tiny.** Every cell's per-fade gross reversion is positive with a
   bootstrap CI that excludes 0 (t 2–7). This is the VR(60)=0.65 / efficiency-0.043 microstructure the
   autopsy measured — it is genuinely there.
2. **It dies on cost, by ~6×.** The best cell captures **0.188 ticks** gross; the realistic 1-tick
   ALL_IN is **1.140 ticks**. **0 of 18 cells** clear a 1-tick spread with CI>0. Best net@1tk =
   **−$29.74**. This is the autopsy's explicit warning realized: median RTH range ~0.9 pt (29 ticks),
   so the per-fade edge is a handful of hundredths of a tick and cannot survive one tick of spread.
3. **The displacement gate ANTI-selects reversion.** The circular-shift null (roll the fade-signed
   forward-reversion series relative to the gate mask, 5,000 draws) returns **circ-p ≈ 0.7–1.0**: bars
   with *large* |price−anchor| have *lower* forward reversion than randomly-placed bars (a big
   displacement is a trend that keeps going). The unconditional fade (`uncond $`, fade any
   displacement) is comparable to or *larger* than the gated fade — **the "signal" adds nothing**; the
   mild reversion is a pervasive property, not a selectable event. This is the matched-unconditional
   control (WE_W111b rule) failing to be beaten.
4. **Judged to the P1 bar (weekly-vol lead).** The primary cell risk-matched to P1's weekly volatility
   is **−$14,991/wk**; the spread band is monotone-negative (**0tk −$416, 0.5tk −$8,078, 1tk −$14,991,
   2tk −$26,195**) → **negative even at 0-tick spread**. fixed-DD shown only beside its side-blind
   random-thinning placebo (lift +$0.00; eval_battery would raise otherwise) — no fixed-DD artifact,
   and no edge on weekly-vol.

**Leg A verdict: COST-FRAGILE.** Gross reversion does not clear a realistic (1-tick) ALL_IN with CI>0
vs the null → **STOP leg A** (per spec `cost_first`). Distinct from the NQ fade graveyard (WE_W108/W118,
G2_F2_SWEEP01), where continuation won; here reversion is real but sub-cost and the gate anti-selects.

---

## LEG B — 08:30/14:00 scheduled-release vol/path — **MDE FIRST → VOL-ONLY-NO-DIRECTION**

**Calendar:** `research/04_complementary_family/c01_announcement_calendar.csv` (bls.gov /
federalreserve.gov). In-window: **08:30 NFP+CPI n=72** (36 CPI + 36 NFP, ~23/yr), **14:00 FOMC n=25**;
797 sessions, 96 release, 701 non-release. Release window = [release, +30 min); base price = close of
the bar ending at the release instant (bars END-stamped: 08:30 release opens the 08:31-stamped bar).

### (i) RV excess — POWERED (a FACT, pre-stated)

| window | n_rel | **MDE (printed first)** | RV release | RV non-rel | excess | ratio | event-shift p | powered? |
|---|--:|--:|--:|--:|--:|--:|--:|:--:|
| 08:30 NFP+CPI | 72 | **$42 (0.042 pt)** | 0.660 pt ($660) | 0.228 pt ($228) | **+$433** | **2.90×** | 0.0002 | **YES** |
| 14:00 FOMC | 24 | **$29 (0.029 pt)** | 0.370 pt ($370) | 0.147 pt ($147) | **+$223** | **2.51×** | 0.0002 | **YES** |

Release windows expand realized vol ~2.5–2.9×, far above the pre-printed MDE, p=0.0002 against an
event-time-shift null. **This is a FACT, not an engine** — the same phenotype as G2_F12 (NQ FOMC vol
×5.66) and CL-EIA. It is banked as descriptive structure; it does not license a trade.

### (ii) post-release path — NOT tradeable

First move = signed 5-min return after the release; continuation leg = 5→30 min. **Continuation** =
trade in the sign of the first move; **reversion** = fade it. Net of **2-tick ($66.86)**, tested vs an
event-time-shift null (same path stat on non-release days):

| window | first-move mean | continuation net | cont p | reversion net | rev p | tradeable? |
|---|--:|--:|--:|--:|--:|:--:|
| 08:30 | −$48 | **−$85.96** | 0.88 | **−$47.76** | 0.12 | **NO** |
| 14:00 FOMC | −$4 | **−$89.00** | 0.88 | **−$44.72** | 0.15 | **NO** |

Both directions are negative net of cost; neither null is significant. **A linear ZB future cannot
capture the vol expansion without taking a direction, and there is no directional edge in the
post-release path.** (A "range capture" is an options structure, not available in the single linear
instrument — see deviations.)

**Leg B verdict: VOL-ONLY-NO-DIRECTION** — exactly the pre-stated null hypothesis (like NQ FOMC and CL
EIA). Recorded as a **FACT**, not a PASS (spec G2B). Distinct from GENESIS_H2 (calendar-mean null),
G2_F10 (overnight NFP/CPI carry on NQ), and G2_F12 (NQ FOMC, different instrument/clock).

---

## G4 — orthogonality (the diversification prize): real and useless

The ZB engine daily series (Leg A primary cell, net@1tk — the dense daily engine, used **only** for
the diversification read; its profitability verdict is COST-FRAGILE above) vs reproduced P1:

- **daily ρ(ZB, P1) = +0.0151**, **weekly ρ = +0.0076**, 797 shared days. Genuinely orthogonal,
  consistent with the autopsy's daily point-return ρ(ZB,NQ)=+0.064.
- `out/daily_pnl.csv` written (797 rows) for any portfolio step.

**ZB is the most orthogonal market in the complex, and porting the incumbent to it (XINST01) already
found ZB anti-transfers with a large negative edge. This run confirms the orthogonality is real from
the ZB-native side too — but neither a native MR fade nor a native release-path engine yields a
positive, cost-robust edge to diversify with.** Orthogonality without a positive edge is worth nothing.

---

## Program-printed GATE / SPEC / OBSERVED / PASS-FAIL

```
G0    points basis + seal asserted                grid&seal, maxsess 2026-07-31          PASS
G1    MDE / cost-to-edge printed BEFORE observed   legA cost=$35.61; legB MDE first       PASS
G2A   legA gross clears 1tk ALL_IN, CI excl 0      0/18 cells; best net@1tk $-30          FAIL
G2B   legB RV powered(MDE) AND tradeable path      powered=True; tradeable_path=False     FACT
G3    any edge on weekly-vol (not fixed-DD-only)   legA weekly-vol $-14,991/wk            FAIL
G4    rho-to-P1 daily PnL printed                  daily rho +0.0151 (797 shared d)       PASS
------------------------------------------------------------------------------------------------
SURVIVES (legA cost-robust CI>0  OR  legB tradeable net of cost) : False
VERDICT : COST-FRAGILE (leg A) + VOL-ONLY-NO-DIRECTION (leg B)
```

`FACT` = leg B powered-vol / zero-directional-edge is recorded as a fact, not a pass.

---

## FAILURE_MEMORY

**ZB's textbook intraday mean-reversion (VR(60)=0.65, efficiency 0.04, tortuosity 23×) is REAL but
sub-cost: the per-fade gross reversion is ~0.06–0.19 ticks, ~6× below one tick of spread, and the
displacement gate anti-selects it (big deviation = trend, not reversion). ZB's scheduled-release vol
expansion (08:30 ×2.90, 14:00 ×2.51) is large and highly powered, but the post-release path carries
zero tradeable directional edge net of 2-tick.** The most orthogonal market in the complex (daily ρ to
P1 ≈ +0.015) yields no positive cost-robust engine from either its defining MR microstructure or its
defining release-vol structure. Combined with XINST01 (P1/PCT anti-transfers to ZB, −$4,179/wk
weekly-vol), the cross-asset conclusion stands: **ZB's orthogonality is genuine and its edge, on every
mechanism tried, is not.** No XM replacement emerges. DISCOVERY_CONSUMED; no forward-queue entry, no
promotion, no deploy.

---

## Deviations / interpretations from the literal spec (transparent)

1. **10:00 ISM/JOLTS releases DEFERRED, not silently dropped.** The spec names an 08:30 + 10:00 + 14:00
   release set; the repo has a provenanced 08:30 (NFP/CPI) + 14:00 (FOMC) calendar
   (`c01_announcement_calendar.csv`) but **no provenanced 10:00 ISM/JOLTS calendar**. Fabricating those
   dates would violate the no-unverified-data discipline (cf. the SMV2X NFP/PCE deferral). The 08:30
   cluster is the autopsy's most-ZB-native, best-powered surface (n=72), so the leg-B conclusion is not
   materially weakened; 10:00 is flagged for a follow-up wave if a calendar is acquired.
2. **Trailing intraday σ = 60-bar rolling std of the anchor-deviation** (causal, min-periods 30) — the
   standard VWAP-band displacement scale. A return-scale σ (~0.03 pt) would mis-scale the band by ~30×;
   the deviation-scale σ is the only reading of "band = k·σ" that yields sensible k∈{1,1.5,2}. The
   verdict is robust to this: gross is 6× below cost regardless of the exact σ window.
3. **Entry at bar close** (act on the deviation observed at close_t). The spread cost, not this ~1-bar
   timing, dominates: the gross-to-cost gap is a factor of ~6, unbridgeable by execution nuance.
4. **"Range capture" (spec leg-B (ii)) is an options structure**, not realizable in a single linear ZB
   future without taking a direction. The linear-tradeable question therefore reduces to
   continuation-vs-reversion of the post-release move, both tested and both failing net of cost.
5. **Circular-shift null for leg A** operates on the overlapping gate-conditional forward-reversion
   series (rolls the fade-signed forward-reversion relative to the gate mask); the per-fade CI uses a
   moving-block bootstrap (L=4) on the non-overlapping trades. Both are dependence-preserving; they
   agree that there is a small real reversion that the gate does not concentrate and that cost erases.
6. **Primary cell preregistered** as (VWAP, H=15, k=1.5) — the middle of the grid, chosen before P&L;
   the full 18-cell neighborhood is reported so no cell is cherry-picked. The `best`-cell figure is
   reported for transparency but is not treated as a pass (it still fails cost by $30).
7. **Single overall verdict = COST-FRAGILE** (leg A, the tradeable directional engine, on the
   cost axis the spec flags as decisive for ZB); leg B's VOL-ONLY-NO-DIRECTION is carried explicitly.
   Both drive SURVIVES=False.

## Deliverables

- `out/gate_table.txt` — program-printed GATE/SPEC/OBSERVED/PASS-FAIL.
- `out/legA_neighborhood.csv` — 18-cell fade neighborhood (gross/net/CI/control/circular-null).
- `out/legB_release.csv` — RV excess (MDE-first) + post-release path (continuation/reversion) per window.
- `out/daily_pnl.csv` — ZB engine daily PnL (797 rows) for the orthogonality / portfolio step.
- `out/summary.json`, `out/run_log.txt` — machine-readable summary and full transcript.
- `src/run_w2_zb.py` — the single program (load+seal → leg A → leg B → P1 reproduction → gates).
