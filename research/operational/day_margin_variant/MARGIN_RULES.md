# NinjaTrader Day-Margin Rules — Verified Facts (DRAFT)

Status: DRAFT — research evidence for a prospective DAY_MARGIN_FLAT strategy variant.
Not committed. Do not treat as an operational go-signal.
All facts verified 2026-08-07 unless noted. All times are wall-clock exchange times
(CT = America/Chicago, ET = America/New_York); the CME session runs 17:00 CT → 16:00 CT
(18:00 ET → 17:00 ET), matching the repo session convention.

---

## 1. Verified facts (with citations)

| # | Fact | Value | Source (accessed 2026-08-07) | Quoted language |
|---|------|-------|------------------------------|-----------------|
| F1 | Intraday (day) margin cutoff | **15:45 CT / 4:45 PM ET** — 15 min before session close for CME equity index futures | https://ninjatrader.com/pricing/margins-position-management/ | "Intraday margin rates are effective from the product open until 15 minutes prior to the session close" (page lists 15:45 CT for E-mini S&P 500 / Micro E-mini group; session close 16:00 CT) |
| F2 | Same cutoff, stated in ET | 4:45 PM ET | https://ninjatrader.com/futures/blogs/futures-margin-day-trading-vs-overnight-trading/ | "intraday positions must be closed 15 minutes prior to session close. This is 4:45 pm ET for the majority of popular CME Group contracts, which is 15 minutes before the official session close at 5:00 pm ET." |
| F3 | Initial-margin window | 15:45 CT → session close 16:00 CT (and any position carried past close) requires exchange initial margin | https://ninjatrader.com/pricing/margins-position-management/ + F2 blog | "To carry this position past the close, the initial margin requirement set by the applicable exchange must be met." |
| F4 | Intraday-margin re-open | Intraday rates resume at **product open = 17:00 CT / 6:00 PM ET** (derived: F1 "effective from the product open" + verified 6:00 PM ET Globex open, F10) | F1 page + https://ninjatrader.com/futures/blogs/futures-trading-hours/ | "Intraday margin rates are effective from the product open …" / "from Sunday 6:00 p.m. ET to Friday 5:00 p.m. ET" |
| F5 | NQ day margin (NinjaTrader) | **$1,000.00** | https://ninjatrader.com/pricing/margins/ | Table row: E-Mini NASDAQ-100 (NQ), Day: $1,000.00 |
| F6 | MNQ day margin (NinjaTrader) | **$100.00** | https://ninjatrader.com/pricing/margins/ | Table row: Micro E-mini NASDAQ-100 (MNQ), Day: $100.00 |
| F7 | NQ initial margin (as listed by NinjaTrader) | **$43,433.67** | https://ninjatrader.com/pricing/margins/ | Table row: NQ, Initial: $43,433.67 (columns shown: Symbol, Market, Exchange, Group, Day, Initial — no Maintenance column) |
| F8 | MNQ initial margin (as listed by NinjaTrader) | **$4,343.38** | https://ninjatrader.com/pricing/margins/ | Table row: MNQ, Initial: $4,343.38 (exactly 1/10 of NQ, internally consistent) |
| F9 | Violation fees for being caught past cutoff under-margined | **$25 first violation, $50 subsequent** execution fee; position "subject to liquidation" | https://ninjatrader.com/pricing/margins-position-management/ | "1st Violation: $25 execution fee" / "Subsequent Violations: $50 execution fee"; "Accounts that do not meet margin requirements are subject to liquidation and applicable fees"; "If you fail to maintain the required margin, you may receive a margin call … or potentially have your positions liquidated by the Trade Desk." |
| F10 | Weekly Globex schedule (per NinjaTrader) | Sunday 6:00 PM ET open → Friday 5:00 PM ET close, with a 60-minute daily break | https://ninjatrader.com/futures/blogs/futures-trading-hours/ | "U.S. futures markets trade nearly 24 hours a day—from Sunday 6:00 p.m. ET to Friday 5:00 p.m. ET, with a 60-minute daily break for mark-to-market settlement." |
| F11 | Daily maintenance break window (equity index) | **16:00–17:00 CT (5:00–6:00 PM ET)**, Mon–Thu; session close 16:00 CT is stated by NinjaTrader (F1 page); the full 60-min window is corroborated by secondary sources only (see §2) | F1 page (close 16:00 CT) + F10 (60-min daily break) + secondary corroboration | F1 page: session close "16:00 CT" for the E-mini group; F10: "60-minute daily break" |
| F12 | News-event margin multiplier | Intraday margins may be set to **4X** standard ≥15 min before key economic releases | https://ninjatrader.com/pricing/margins-position-management/ | "Intraday margins may be set to 4X our standard rates at least 15 minutes prior to the release of key economic news announcements" |
| F13 | Discretionary volatility adjustments | Margins can change in real time without prior notification | https://ninjatrader.com/pricing/margins/ (same language on F1 page) | "The NinjaTrader risk team evaluates market conditions in real-time and reserves the right to adjust intraday margins in accordance with market volatility. If required, temporary changes to the amount of margin required for trading may be made without prior notification." |
| F14 | 3:15–3:30 PM CT equity-index halt | **Removed** on regular days, effective 2021-06-28 (broker notice quoting CME) | https://blog.ampglobal.com/cme-equity-index-products-trading-halt-between-315-and-330-p.m-removed | "CME Group has removed the trading halt between 3:15 and 3:30 p.m. CST on CME Globex for Equity Index products." ("Starting today, June 28, 2021") |

Answers to the five campaign questions, mapped to the table:
1. **Cutoff**: yes — 4:45 PM ET (15:45 CT) is the current NinjaTrader day-margin cutoff (F1, F2). Re-open of intraday rates: product open, 6:00 PM ET / 17:00 CT (F4).
2. **Numbers**: NQ day $1,000 / MNQ day $100; NQ initial $43,433.67 / MNQ initial $4,343.38 as listed by NinjaTrader (F5–F8). Maintenance not displayed (see §2).
3. **Auto-flatten**: NOT guaranteed-automatic in the official language. Positions held past cutoff without initial margin are "subject to liquidation" by the Trade Desk plus $25/$50 execution fees and possible margin call (F9). Treat liquidation as probable but discretionary in timing — do not rely on it as a free stop.
4. **Exceptions/volatility**: 4X pre-news intraday margins (F12) and unannounced real-time margin increases (F13). No NQ/MNQ-specific carve-out found.
5. **CME break**: session close 16:00 CT; daily break 16:00–17:00 CT (5:00–6:00 PM ET) Mon–Thu; Sunday reopen 17:00 CT / 6:00 PM ET (F10, F11). The old 3:15–3:30 PM CT equity-index halt is removed on regular days (F14).

---

## 2. Not verified from official/primary sources (explicit)

- **CME exchange margins directly from CME**: cmegroup.com actively blocks this research IP ("This IP address is blocked due to suspected web scraping activity…"), so the exchange's own initial/maintenance figures for NQ/MNQ could not be pulled from cmegroup.com. No circumvention was attempted. The $43,433.67 / $4,343.38 figures are NinjaTrader's posted "Initial" values, which the F3 policy language says track "the initial margin requirement set by the applicable exchange." If CME uses the usual initial = 110% x maintenance speculator ratio, the implied CME maintenance is ~$39,485 (NQ) / ~$3,948.50 (MNQ) — **inference, not verified**.
- **Maintenance margin as a separate number**: NinjaTrader's margins table shows only "Day" and "Initial" columns; no maintenance column is published there.
- **Guaranteed auto-flatten at exactly 16:45 ET**: official language is "subject to liquidation" / "may be liquidated by the Trade Desk" — a right, not a commitment to a precise timestamp. Anecdotal reports of automated risk-system flattens shortly after 15:45 CT exist but were not verifiable from official pages (the relevant NinjaTrader support-forum threads now 404 after the forum's migration to discourse.ninjatrader.com).
- **Explicit stated re-open time for intraday margins**: 6:00 PM ET is derived from "effective from the product open" plus the published Globex open; no single sentence on an official page states "intraday margins resume at 6:00 PM ET."
- **The 16:00–17:00 CT maintenance window as CME's own text**: NinjaTrader states the 16:00 CT close and a 60-minute daily break; the exact 16:00–17:00 CT framing is corroborated only by secondary sources (quantvps.com, proptradingvibes.com, damnpropfirms.com) because cmegroup.com is unreachable from here.
- **Month-end 3:15–3:30 PM CT halt exception**: search results indicate a fair-value settlement halt still occurs on the **last business day of each month** for equity index futures (referenced to CME's fair-value FAQ), but the CME page could not be fetched and the AMP notice text retrieved did not contain the exception. Treat as plausible-unverified; it matters for month-end flatten scheduling (see §3).

---

## 3. Implications for a DAY_MARGIN_FLAT strategy variant

Context: the frozen baseline (SolarWaveRKReplicaV0, exit-on-session-close) goes flat at the
**17:00 ET session close** — i.e., 15 minutes AFTER the 16:45 ET day-margin cutoff. Under
day-margin account sizing, every baseline position held between 16:45 and 17:00 ET would
require full initial margin (~$43.4k/contract NQ). Exit-on-session-close alone does NOT
satisfy the day-margin regime.

Design constraints for the variant:

1. **Flatten deadline with buffer**: hard external deadline 16:45:00 ET. Recommended internal
   deadline **16:40:00 ET** (submit flatten no later than ~16:38 ET) — a 5–7 minute buffer for
   order routing, partial fills, and clock skew. On a 1-min series the last entry-eligible bar
   should close well before that (e.g., no new entries after ~16:30 ET).
2. **Liquidity window**: post-cash-close (16:00–17:00 ET) NQ liquidity thins materially.
   Flattening at ~16:40 ET pays wider spreads than flattening near 16:00 ET. A variant grid
   should test flatten times {16:00, 16:10, 16:30, 16:40 ET} — the margin benefit is identical
   for all of them; only PnL/slippage differs.
3. **Month-end defense**: if the reported last-business-day 16:15–16:30 ET (3:15–3:30 CT)
   fair-value halt is real, a 16:20 ET flatten order would sit unfilled inside the halt. Until
   verified, schedule month-end flattens to complete **before 16:10 ET**.
4. **No action possible 17:00–18:00 ET**: daily maintenance break — cannot flatten, cannot
   re-enter. Any position carried into 17:00 ET is committed to initial margin through the break.
5. **Re-entry at 18:00 ET**: intraday rates resume at product open (F4). A DAY_MARGIN_FLAT
   variant may re-open positions any time from 18:00 ET at $1,000/NQ day margin. Note the
   baseline signal engine treats 18:00 ET as session start already, so re-entry logic composes
   naturally with the existing session template.
6. **Sizing headroom is not constant**: 4X pre-news intraday margins (F12) and unannounced
   volatility adjustments (F13) mean an account sized to N contracts at $1,000/contract can
   become under-margined intraday. Conservative sizing rule: size to **4X day margin**
   ($4,000/NQ, $400/MNQ) as the working floor; anything tighter is an operational bet on the
   risk desk's discretion.
7. **Not comparable to the frozen baseline**: moving the exit from 17:00 ET to ≤16:40 ET changes
   the trade population (the baseline's session-close exits reprice). Any variant must be run as
   a new experiment with its own sequence number, spec.yaml, and run dir — never presented as a
   like-for-like of the canonical $146,440.60 result.

---

## 4. Requires periodic re-verification

Margins are volatility-linked and change **without prior notification** (F13). The dollar
figures in F5–F8 are a snapshot of 2026-08-07 and WILL drift; the 4:45 PM ET cutoff and fee
schedule are policy-stable but not contractual. Before any live/sim deployment of a
DAY_MARGIN_FLAT variant — and at least monthly while it is under consideration — re-verify:

- https://ninjatrader.com/pricing/margins/ (Day + Initial for NQ/MNQ)
- https://ninjatrader.com/pricing/margins-position-management/ (cutoff times, violation fees, 4X news rule)
- CME NQ margins page (https://www.cmegroup.com/markets/equities/nasdaq/e-mini-nasdaq-100.margins.html) from a non-blocked network, to close the exchange-margin verification gap in §2.

Last verified: 2026-08-07 (this document).
