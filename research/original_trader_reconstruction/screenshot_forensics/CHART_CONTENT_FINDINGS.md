# CHART_CONTENT_FINDINGS — IMG-16 chart-content sweep (90 frames)

Date: 2026-08-24
Source: 5 sweep agents (S1–S5), staging JSONL at `staging/chart_content_S1..S5.jsonl` (18 rows each, 90 total).
Consolidated ledger: `CHART_CONTENT_LEDGER.csv` (90 rows, one per frame, columns = JSONL fields).
Frame coverage: OTRIMG-0001 → OTRIMG-0163 (the sweep's assigned subset; mostly rednote text cover cards and comment-thread screenshots).

Headline: **89 of 90 frames contain no price chart at all.** The single chart frame (OTRIMG-0130) is a COMMENTER's TradingView MNQ chart, not the author's platform. This corpus segment contributes essentially zero chart-morphology evidence; its value is text/metadata (see F6).

---

## F1 — Signal-arrow / trade-marker timestamps

**Answer: NO frame in this 90-frame sweep yields any signal-arrow or trade-marker timestamp, even approximate.** (pixel-certain, in the sense that no candidate exists)

Complete candidate list:

| Frame | What is actually readable | Verdict |
|---|---|---|
| OTRIMG-0130 | Commenter 三十而立's TradingView-style dark MNQ chart. No entry/exit triangles, no PnL tags. One blurry order/position-line-like tag on a pink horizontal line reading `@ 23,206.25?` (digits partly uncertain; could be 23,208.25?), glyph before `@` unreadable. **No time-axis labels visible** — bottom edge covered by TradingView drawing toolbar; no date anywhere on the chart. Price axis 23060.00–23440.00 in 20.00 steps is legible, instrument tag `/MNQ 23398.75` (LOW-MED confidence on `/`). | Not the author's system; no timestamp readable. Zero value for OTR-VF-CAND1 separation or S-family gate questions. |

No other frame has any chart pixels, so no other candidate exists. This sweep therefore provides **no** timestamp evidence to separate OTR-VF-CAND1 members or feed S-family gate questions.

## F2 — FairValue line position in HIS 2026 VF-cloud frames (edge-hugging/percentile vs midspan/min-max)

**Answer: NOT TESTABLE in this sweep — zero VF-cloud frames present.** (pixel-certain that none are present in these 90 frames)

No frame shows the author's 2026 platform chart, so no FairValue-line geometry could be observed. EV-040 (vendor charts → percentile family confirmed) remains the only evidence on this question; this sweep neither corroborates nor contradicts it.

## F3 — Cloud width scale vs morphology stats (VF-ANCHOR ~47 NQ pts vs VF-BLOCK ~106)

**Answer: NOT TESTABLE — no cloud rendered in any frame.** (pixel-certain)

All `cloud_width_est_pts` fields are null across 90 rows. No width comparison possible.

## F4 — 18:00 session-open cloud behavior (pool reset vs carry-over)

**Answer: NOT TESTABLE — no cloud, no chart spanning a session open.** (pixel-certain that no such frame exists here)

Related but non-chart text evidence (probable, text-legible): OTRIMG-0143 comment thread — author states positions auto-flatten ~30 seconds before 5pm ET (16:59:30 ET) unless stopped out; this is session-CLOSE behavior of the strategy, not cloud pool behavior, and was already captured in the per-image audit record.

## F5 — S-era wave line + entries vs recovered TrailingStop geometry

**Answer: NOT TESTABLE — zero S-era chart frames in this sweep.** (pixel-certain that none are present)

No stepped-line/flip geometry could be checked. The recovered-TrailingStop plot-geometry question remains open for whatever corpus segments actually contain S-era charts.

## F6 — Other label-grade content

Nothing chart-derived. Text-derived items below; most are explicitly noted in the JSONL as matching existing per-image audit records, so they are confirmations, not new ledger entries:

1. **Commission-methodology admission (OTRIMG-0098; probable — small phone-screenshot text but sweep agent transcribed it as legible).** Author reply 12/20/2025: he runs several strategies concurrently, analyzes single-strategy performance via Strategy Analyzer, manually selects a commission rate of "大约是$2一个来回", plus slippage — "所以实际上的盈利是贴出来的 0.9左右，亏损是1.1左右" (actual profits ≈ 0.9× posted, losses ≈ 1.1× posted). Follow-up 12/21/2025: "你是第一个发现这个问题的…偷懒了一下，所以就一直懒下去了。" This is a global scaling correction applicable to EVERY weekly result card in the corpus. JSONL says it matches audit record OTRIMG-0098.md — verify it is propagated as a corpus-wide adjustment flag, not just a per-image note.
2. **Session-exit rule (OTRIMG-0143; probable):** auto-flatten ~16:59:30 ET (30 s before 5pm ET) unless stopped out — hard mechanical constraint for reconstruction. Already in per-image record.
3. **Platform + sizing confirmations (probable):** OTRIMG-0084 "ninjatrader" (+ "比ib要好用且更加稳定", 11/2025); OTRIMG-0157 "一个NQ合同，本金保持在10万美金左右" and a "$22000" single-trade claim (late-June 2026); OTRIMG-0032 Analyzer table strip (18.83 trades/day; avg bars in trade 44.69 = 44.69 min avg time in market on 1-min bars) plus author reply "纯价格，没有成交量".
4. **Regime remark (OTRIMG-0130 thread; probable):** author 3/27–3/28/2026: "日内" and "没办法，市场条件不太适合做趋势，经常是一根大红柱子和大绿柱子。" — contemporaneous with the −$42,235 week (OTRIMG-0128, week of 3/22–3/27).
5. **Recoverable-evidence lead (OTRIMG-0160; pixel-certain that the area is blank):** rednote post dated 7/11, 2-image carousel at page 2/2, but the entire post-image area rendered BLACK in this capture — the post's two images (plausibly performance/chart screenshots) exist but are unreadable here. If any other corpus frame captures the same post with images loaded, prefer it; otherwise this is a candidate for re-capture at source.
6. **Background statement (OTRIMG-0054; probable):** author self-describes "业余的量化交易" and prior losses "前面已经折腾股票和期权已经亏了二十多万了" (>$200k? currency/unit not stated — 二十多万 verbatim) before the current system.

No overclaiming note: every "not testable" verdict above is a statement about THIS 90-frame sweep only, not about the full 164-image corpus. Frames OTRIMG-0002/0003/0005/etc. (even-numbered and other IDs outside this sweep's coverage) are not addressed here.
