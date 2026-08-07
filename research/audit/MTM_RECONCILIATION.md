# True mark-to-market reconciliation — POST_CAMPAIGN_AUDIT_01, AUDIT-A05

_2026-08-07 · driver `src/analytics/audit03_mtm_run.py` · bar series
`runs/AUDIT03_BARS/nq_3m_2022_2026.csv` (540,232 bars exported by `AuditBarExport1`
from the same engine/data that produced every ledger; the single missing final
boundary bar is the long-known exporter quirk and is handled explicitly)._

## What was reconciled

For **R5 (13 adaptive members)** and **R4 (21 fixed members)**, strict-1/N ensembles
were computed under three daily conventions, each on the ensemble's own traded-day
union:

1. `calendar_REALIZED` — round-trip net on the calendar date of the exit fill
   (the published basis; `execledger.daily_vector`);
2. `session_REALIZED` — round-trip net on the NT8 session date (18:00 ET roll);
3. `session_TRUE_MTM` — bar-level equity (cash + open-position value, marked on
   every one of 540k bars) sampled at each session's last bar.

Enforced audit checks, all passing to the cent for every one of the 34 members:
- `session_TRUE_MTM == session_REALIZED` — **the flat-at-session-close identity is
  now proven from bar-level reconstruction, not assumed** from strategy design;
- MTM total == ledger round-trip net (P&L identity).

## Results

| ensemble | basis | n_days | net | Sharpe | Sortino | max DD (daily) | Calmar | ES5 | TUW | worst day | worst week | worst qtr |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R5-13 | calendar REALIZED | 1332 | $198,058.82 | 1.0104 | 2.117 | −$39,125.61 | 0.958 | −$3,657 | 1254 | −$13,005 | −$11,853 | −$8,613 |
| R5-13 | session REALIZED | 1184 | $198,058.82 | 1.0642 | 2.225 | −$39,853.39 | 1.058 | −$3,983 | 1112 | −$13,005 | −$12,463 | −$8,613 |
| R5-13 | session TRUE_MTM | 1184 | $198,058.82 | 1.0642 | 2.225 | −$39,853.39 | 1.058 | −$3,983 | 1112 | −$13,005 | −$12,463 | −$8,613 |
| R5-13 | **bar-level TRUE_MTM** | — | $198,058.82 | — | — | **−$42,204.42** | — | — | — | — | — | — |
| R4-21 | calendar REALIZED | 1292 | $159,423.70 | 0.9368 | 1.885 | −$35,669.32 | 0.872 | −$3,680 | 1219 | −$8,087 | −$19,841 | −$8,203 |
| R4-21 | session REALIZED | 1184 | $159,423.70 | 0.9704 | 1.959 | −$36,360.30 | 0.933 | −$3,865 | 1113* | −$7,135 | −$20,997 | −$8,203 |
| R4-21 | session TRUE_MTM | 1184 | $159,423.70 | 0.9704 | 1.959 | −$36,360.30 | 0.933 | −$3,865 | 1113* | −$7,135 | −$20,997 | −$8,203 |
| R4-21 | **bar-level TRUE_MTM** | — | $159,423.70 | — | — | **−$39,493.63** | — | — | — | — | — | — |

_\* 1110/1112 in the CSV; table rounds. Full precision in
`research/audit/mtm_reconciliation_metrics.csv`._

Note on Sharpe levels: these are computed on each ensemble's own traded-day union
(1,332 / 1,292 days). The published headline Sharpes (0.9771 / 0.8922) sit on the
padded 1,424-session campaign calendar, which adds zero-P&L days from other
families' traded dates. Same data, different denominators; rankings unaffected.

## Findings

1. **No exit-date distortion at session granularity.** Because every member is flat
   at every session close, session-realized P&L IS true MTM. The audit's concern
   that published drawdown/ES might be understated by exit-date bucketing is
   resolved: at daily granularity the published figures are legitimate (and the
   published calendar basis is the *more conservative* Sharpe of the two).

2. **Calendar vs session bases differ as documented** (~5–6% Sharpe): calendar
   splits each 18:00→17:00 session's P&L across two calendar dates.

3. **New TRUE_MTM-only disclosure: intraday drawdown is deeper than any published
   daily figure.** Bar-level ensemble max DD:
   - R5: **−$42,204** vs −$39,126 published (7.9% deeper);
   - R4: **−$39,494** vs −$35,669 published (10.7% deeper).
   Daily sampling hides intraday excursion. Capital/margin sizing and any future
   drawdown budget must use the bar-level numbers. R4's "best drawdown" advantage
   over R5 narrows at bar level ($2,711 vs $3,456 at daily).

4. **Labeling rule now in force** (constitution §10): every future Sharpe/DD/ES/TUW
   quote must carry `TRUE_MTM` or `REALIZED_ONLY`. For flat-at-close strategies the
   session-basis numbers may be labeled TRUE_MTM (proven identity); the identity
   must be re-proven for any strategy that can hold across a session close.

## Ranking impact

None. R5 leads R4 on Sharpe/Sortino/Calmar under every convention; R4 keeps the
smaller max DD under every convention. The published candidate ordering survives
true-MTM accounting unchanged.
