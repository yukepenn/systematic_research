# WE_W75 — THE STREAM CENSUS · REPORT

Spec preregistered, including the owner's binding recency gate, before anything was computed.
Twenty streams on one 1,012-session grid. **Nothing adopted.**

> ## THE NUMBER: **K_admissible = 2.** W74 says we need **6**.

---

## 1. What was asked and what was counted

W74 established by bootstrap — from P1's own 204 empirical weeks, with a Gaussian copula and no
distributional assumption — that **76 % positive weeks needs 6 genuinely independent streams at
our current quality**, 10 at ρ = 0.1, and is **unreachable at ρ ≥ 0.2 for any K**. It also showed
the positive-week rate is scale-invariant, so contracts cannot contribute to it at all. That made
the stream count the only open lever, and this repo had never counted them.

The owner's gate, applied before any clique was quoted: **a stream is admissible only if it is
positive over the full window AND positive in 2025 AND positive in 2026.** Deep history is
informative; it does not admit anything.

## 2. The answer (`FACT`)

**Only three of the twenty streams are |ρ| < 0.20 against P1 on daily P&L:**

| stream | ρ vs P1 | full window | 2025 | **2026** | verdict |
|---|---|---|---|---|---|
| SHORT (mirrored short sleeve) | **−0.003** | $121,454 | $31,341 | **−$22,519** | **fails 2026** |
| **AXISB** (volatility-expansion) | **+0.031** | $66,581 | $63,231 | **+$19,340** | **ADMISSIBLE** |
| S_sig (signed-σ short, W73) | −0.014 | $96,936 | $34,853 | **−$33,992** | **fails 2026** |

Everything else in the repo is 0.30–0.89 correlated with P1. The four clock sleeves are
0.42–0.56. The twelve W72 channel-substituted objects are 0.45–0.89. B-MOM standalone is 0.32.
The signed-σ long object is 0.86.

> **Largest admissible clique containing P1 = 2: {P1, AXISB}** — and it is 2 at ρ < 0.15,
> ρ < 0.20 **and** ρ < 0.25, so the answer is not sensitive to where the cut is drawn.

**We have two streams. We need six. The shortfall is four.**

That is a far more specific brief than *"find a second model"*, which is what W40, W56, W57, W61
and W65 were each given.

## 3. The clique that does NOT contain P1 — and it is the best object measured here

The largest admissible clique anywhere is **3: {AXISB, BMOM, w72:X9a}**, realised pairwise
|ρ| mean 0.069, max 0.167. Equal-weighted and inverse-vol-weighted at constant exposure, no
optimisation of any kind:

| | net | pts/session | week + % | wk streak | median week | **weekly $ at a fixed $20,245 DD** | **max DD** | worst week |
|---|---|---|---|---|---|---|---|---|
| **equal weight** | $184,623 | 9.12 | **58.8 %** | **6** | **$820** | **$2,346** | **$7,810** | **−$5,976** |
| inverse vol | $173,041 | 8.55 | **61.8 %** | **4** | $758 | $1,831 | $9,380 | **−$4,974** |
| **P1 alone** | $300,817 | 14.86 | 58.3 % | 8 | $455 | $1,475 | $20,245 | −$7,418 |

Read at a **matched drawdown**, which is the campaign's standard unit: the three-stream portfolio
has a **2.6× smaller maximum drawdown**, and at the incumbent's drawdown it makes **+59 % more
money** with a **+80 % larger median week** and a weekly losing streak of **6 instead of 8**. The
inverse-vol version reaches **61.8 % positive weeks with a streak of 4**.

`OBSERVATION, NOT A PROMOTION.` It has no null of its own, its members have never individually
faced one (AXISB's own W40 record is mixed and B-MOM is the component W67–W69 disclosed as
regime-local), and its 2025 and 2026 raw dollars are **below** P1's ($68,086 vs $120,040 and
$24,081 vs $33,467) — they only overtake after the drawdown-matched rescaling. It is queued for
its own preregistered wave rather than quoted as a result.

## 4. `CORRECTION` — two streams in this census are contaminated and may not be quoted

The census included CLKRANGE and CLKVOL, and they produced the two best 2026 figures on the page
— **$46,007 and $60,833 against P1's $33,467**. Both are void:

- `we_clocks.size_for_rate()` sets the **range** clock's bar size from a **full-sample quantile**
  over the whole measurement array. This is the exact defect that withdrew W41's adoption — the
  campaign's fourth full-sample-quantile casualty.
- The same function sets the **volume** clock's bar size as `D["v"].sum() / target` — a
  **full-sample mean** over the same array. Under the campaign's categorical rule (*any threshold
  or cut on the measurement sample must be re-derived causally*), a full-sample mean used as a bar
  size is the same class of defect.

I was one step from quoting CLKVOL's 2026 as the headline answer to the owner's question about
this year. **Only CLK3 and CLK5 carry no full-sample parameter** — their bar sizes are a fixed 3
and 5 minutes — and their 2026 figures ($30,144 and $31,474) sit slightly *below* P1's.

## 5. The 2026 ledger, which is what the owner actually asked about

2026 = 106 sessions / 22 weeks on this grid (**and see W76 — the substrate was silently truncated
and 2026 is really ~150 sessions**). At **one contract**:

| | 2026 net | pts/session | per week | **week + %** | worst week |
|---|---|---|---|---|---|
| **P1** | **$33,467** | **15.79** | **$1,521** | **68.2 %** | −$6,344 |
| w72:X9b | $40,010 | 18.87 | $1,819 | 59.1 % | −$8,541 |
| w72:X3 | $36,318 | 17.13 | $1,651 | 59.1 % | −$6,698 |
| L_sig | $33,022 | 15.58 | $1,501 | 59.1 % | −$7,414 |
| CLK5 | $31,474 | 14.85 | $1,431 | 50.0 % | −$8,018 |
| BMOM | $20,150 | 9.50 | $916 | 50.0 % | −$12,217 |
| AXISB | $19,340 | 9.12 | $879 | 59.1 % | −$8,337 |
| SHORT | **−$22,519** | −10.62 | −$1,024 | 36.4 % | −$6,244 |

**2026 is not a weak year for P1 — it is the best year the object has ever had on the metric the
owner ranks first.** 68.2 % positive weeks against a full-window 58.3 %, and 15.79 pts/session
against 14.86. It looks small only because it is quoted at one contract over a partial year.

Annualising 2026's realised rate:

| contracts | annualised | 2026 max DD | 2026 worst week |
|---|---|---|---|
| 1 | $79,564 | $12,607 | −$6,344 |
| **2** | **$159,127** | $25,214 | −$12,688 |
| **3** | **$238,691** | $37,821 | −$19,032 |
| 4 | $318,255 | $50,428 | −$25,377 |
| 7 | $556,945 | $88,249 | −$44,410 |

## 6. What this census closes and what it opens

- **Closed**: the idea that sampling diversification contributes to consistency. Every clock, every
  member-set variant and every channel arm is 0.30–0.89 against P1 — far above the ρ ≥ 0.2 wall
  W74 identified. A quantitative restatement of the campaign's own model-risk law.
- **Closed**: the search framing. Decorrelation is a **threshold**, not a quality to maximise.
  Past the threshold, only the count matters (W74 §5).
- **Open, and now the whole brief**: find **four** more streams that are ρ < 0.2 against P1 *and*
  against each other *and* work in 2025–2026. The only two candidates ever found (SHORT, AXISB)
  came from completely different mechanisms — a mirrored ratchet and a volatility-expansion event
  engine — which is consistent with the finding that mechanism distance, not tuning distance, is
  what produces low ρ.
- **Queued**: a preregistered wave for the three-stream portfolio of §3, with its own nulls.

## 7. Files
`out/census.txt` · `out/panel.csv` `out/corr_daily.csv` `out/corr_weekly.csv`
`out/streams_daily.csv` · code `research/weekly_edge/src/run_we_w75.py`
