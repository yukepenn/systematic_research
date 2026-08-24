# OTRIMG-0154

## A FILE IDENTITY
- id: OTRIMG-0154
- filename: 20260824_173119076_iOS.jpg

## B DATE EVIDENCE
- screen_capture_date: mobile status bar shows time "2:19" only (no date); 5G, battery 49%
- taskbar_date: 2:19 PM / 6/18/2026 (remote Windows taskbar, bottom right of RD viewport)
- social_post_date: none visible (but Xiaohongshu watermark present — image was distributed via rednote/小红书)
- report_start_date: 6/14/2026 (Start date row; left date picker "06/14/2026")
- report_end_date: 6/18/2026 (End date row; right date picker "06/18/2026")
- contract_date_clue: none visible

## C SOURCE TYPE
NT_TRADE_PERFORMANCE — NinjaTrader 8 "Trade Performance" window viewed through a MOBILE (Android-style) remote-desktop client (dark status bar with 2:19/5G/49%, RD toolbar icons: fullscreen, keyboard, touch, pin-off, kebab menu; Android dock at bottom). NOT the macOS Jump Desktop frame of the other JD images.

## D STRATEGY IDENTITY
- No strategy/account name visible; no machine title bar visible in this client.

## E DATA SERIES
- Not visible (execution report).

## F PARAMETERS
- No settings pane. Toolbar: Display [dropdown]="Summary ($)"; filter icon (cursor hovering); date picker [06/14/2026]; date picker [06/18/2026]; button "Generate".

## G ENGINE SETTINGS
- Commission NON-ZERO: $96.76 all / $49.56 long / $47.20 short → real recorded executions; cent-level values throughout.

## H PERFORMANCE (All / Long / Short)
| Row | All trades | Long trades | Short trades |
|---|---|---|---|
| Total net profit | $8,503.24 | $13,735.44 | ($5,232.20) |
| Gross profit | $40,206.34 | $28,624.04 | $11,582.30 |
| Gross loss | ($31,703.10) | ($14,888.60) | ($16,814.50) |
| Commission | $96.76 | $49.56 | $47.20 |
| Profit factor | 1.27 | 1.92 | 0.69 |
| Max. drawdown | ($9,668.16) | ($6,570.96) | ($7,530.62) |
| Sharpe ratio | 1.85 | 1.90 | -1.79 |
| Sortino ratio | 1.00 | 1.00 | -5.93 |
| Ulcer index | 0.01 | 0.01 | 0.01 |
| Probability | 19.40% | 4.88% | 82.91% |
| Start date | 6/14/2026 | | |
| End date | 6/18/2026 | | |
| Total # of trades | 78 | 39 | 39 |
| Percent profitable | 42.31% | 48.72% | 35.90% |
| # of winning trades | 33 | 19 | 14 |
| # of losing trades | 45 | 20 | 25 |
| # of even trades | 0 | 0 | 0 |
| Avg. trade | $109.02 | $352.19 | ($134.16) |
| Avg. winning trade | $1,218.37 | $1,506.53 | $827.31 |
| Avg. losing trade | ($704.51) | ($744.43) | ($672.58) |
| Ratio avg. win / avg. loss | 1.73 | 2.02 | 1.23 |
| Max. consec. winners | 3 | 4 | 3 |
| Max. consec. losers | 6 | 6 | 9 |
| Largest winning trade | $5,277.64 | $5,277.64 | $3,397.64 |
| Largest losing trade | ($1,426.18) | ($1,321.18) | ($1,426.18) |
| Avg. # of trades per day | 22.60 | 11.30 | 11.30 |
| Avg. time in market | 34.10 min | 50.20 min | 18.01 min |
| Profit per month | $51,869.76 | $83,786.18 | ($31,916.42) |
| Max. time to recover | 2.94 days | 2.27 days | 1.94 days |
| Longest flat period | 1349.61 min | 1373.18 min | 1350.60 min |
| Avg. MAE (row cut at bottom) | $921.73? | $1,115.51? | $727.95? |

## I GRAPH MORPHOLOGY
n/a (summary table only)

## J SOCIAL CONTENT
n/a (no post text; but the frame carries Xiaohongshu distribution markers — see K)

## K FORENSIC INTERPRETATION
- Direct facts: WATERMARK FULLY LEGIBLE here: "rednote ID: 1384856832" (bottom right, with a 小红书 logo pill above it). This pins the Xiaohongshu (rednote) account ID for the whole watermark series and confirms these screenshots circulated on Xiaohongshu.
- Execution report week 6/14–6/18/2026: net +$8,503.24 on 136→78 trades... (78 trades), 42.31% win, commission $96.76 (≈$1.24/trade — same low per-trade commission pattern as OTRIMG-0152).
- Long side +$13,735.44 vs short side −$5,232.20 → live results reproduce the long-dominant asymmetry seen in backtests.
- Device context: the trader ALSO monitors the remote Windows box from a phone/tablet (Android-style RD client) — dock apps visible: phone, Chrome, 知乎 (Zhihu), 小红书 (Xiaohongshu), an "sd" app, QQ音乐 (green music note), an "Aa" dictionary-style app, screenshot/gallery, WeChat (微信), eBay. Chinese app ecosystem (Zhihu/Xiaohongshu/WeChat) → Chinese-speaking user.
- Remote Windows taskbar (light theme, differs from dev/hp dark taskbars): Search with weather icon, folder, NinjaTrader, Chrome, notes app; clock 2:19 PM 6/18/2026 — matches mobile status bar 2:19 → phone clock and remote clock in same timezone at capture (or coincidental alignment; hypothesis).
- 6/18/2026 is a Thursday; report generated intra-week (not the usual Friday review).
- Open questions: which machine this RD session targets (hp/dev/third); which account produced the executions.
