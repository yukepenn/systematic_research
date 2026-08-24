# OTRIMG-0143

## A FILE IDENTITY
- id: OTRIMG-0143
- filename: 20260824_172738000_iOS.png
- resolution: 1290x2796 (iPhone screenshot)

## B DATE EVIDENCE
- screen_capture_date: none visible
- screen_capture_time: 1:27 (iPhone status bar; location-services arrow glyph next to time)
- taskbar_date: none visible
- social_post_date: none visible at this scroll position
- comment_dates: all visible comments 5/10 (year not shown; context implies 2026, INFERRED)
- report_start_date: none visible
- report_end_date: none visible
- contract_date_clue: commenter refers to "这一手nq" (this one NQ contract position)

## C SOURCE TYPE
SOCIAL_THREAD — rednote comment section of a "mac studio" post; single deep Q&A thread about position holding rules and session hours.

## D STRATEGY IDENTITY
- None visible. Author handle "mac studio".

## E DATA SERIES
- Instrument referenced in discussion: NQ ("这一手nq"), one contract. Session behavior per author: flat over the daily 17:00–18:00 ET futures break (see J/K). No bar type visible.

## F PARAMETERS
- n/a (social UI). Controls: header (back, avatar, mac studio, Following, share), a partially cut "Drop a comment..." input at very top, Reply/Translate links, hearts, emoji icons, "Hide", footer "Say something...", like 2, Save, comment 10.

## G ENGINE SETTINGS
- n/a (but author describes automatic flatten rule — see J/K)

## H PERFORMANCE
- n/a

## I GRAPH MORPHOLOGY
- n/a

## J SOCIAL CONTENT (verbatim)
1. COMMENTER 足球搭子 (avatar: white rabbit/figure with red glasses): "请问老哥你持有这一手nq过周末吗？还是周五平掉下周再开？" — 5/10
   1.1 AUTHOR (mac studio) [Author badge]: "每天东部时间5pm前30秒，如果前面没有止损的话，都自动平仓了" — 5/10
   1.2 COMMENTER 足球搭子: "Reply mac studio: 懂了，就是绝对不持仓过周末对吧？而且持仓过周末还有额外收费？" — 5/10
   1.3 COMMENTER 足球搭子: "Reply mac studio: 对了，老哥你这策略可以卖给我吗？或者租用也行，我就自己用" — 5/10
   1.4 AUTHOR (mac studio) [Author badge]: "Reply 足球搭子: 每天下午五点到六点，指数期货市场有一小时休息，这段时间是空仓的，如果持仓，没有额外费用，但是保证金是日内的40倍左右" — 5/10
   1.5 COMMENTER 足球搭子: "Reply mac studio: 应该16：00-17：00休息一小时吧，如果是芝加哥交易所时间，可能和你那里有一个小时时差[emoji: small pink/peach-like glyph, LOW confidence]" — 5/10
   — Hide —

Footer: likes 2, Save, comments 10. (No reply from the author to the buy/rent request is visible in this frame.)

## K FORENSIC INTERPRETATION
Direct facts (author statements, 5/10):
- EXIT RULE: "每天东部时间5pm前30秒，如果前面没有止损的话，都自动平仓了" — every day, 30 seconds before 5:00 pm Eastern Time, the position is automatically flattened unless a stop-loss already fired earlier. This is the single most precise session-exit specification in the corpus: flatten at ≈16:59:30 ET.
  - Confirms: (a) strategy carries positions intraday until the session close unless stopped; (b) there IS a stop-loss in the system; (c) flat over the 17:00–18:00 ET maintenance hour, hence never holds over the weekend.
- Author knows/states: index futures have a one-hour daily break "下午五点到六点" (5–6 pm, his local/ET frame), system is flat during it; holding overnight has no extra fees but requires margin ≈40x the intraday margin (保证金是日内的40倍左右).
  - 40x ratio matches intraday micro-margin (~$50-style promos) vs full overnight margin, or NT's $1k-ish intraday vs ~$24k+ overnight NQ margin (~consistent with "40倍左右" if intraday margin very low). HYPOTHESIS: NinjaTrader-style deep intraday discount margin.
- Commenter attempted to BUY or RENT the strategy ("卖给我吗？或者租用也行"); no visible author reply in frame.
- Commenter's correction "应该16：00-17：00…芝加哥交易所时间…一个小时时差" shows the 17:00 ET == 16:00 CT equivalence discussion; author's "5pm" is Eastern — matches CME index futures 17:00 ET close.
Implication for reconstruction:
- The 30-seconds-before-close flatten aligns with NT8 "Exit on session close" with ExitOnSessionCloseSeconds = 30 — a direct parameter-level fingerprint.
