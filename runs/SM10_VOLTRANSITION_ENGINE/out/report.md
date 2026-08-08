# SM10 — Day-Scale Volatility-Transition Engine: FAIL (all arms)

_2026-08-08. Spec frozen before read (seq 312-314). Results: `out/results.csv`._

- FACT: K=1 dev: 125 trades, +26.7t/trade C1, day-clustered CI [−93.4, +147.0] —
  CI_lo ≪ 0, FAIL; 3/5 years positive; pre-2022: −4.7t/trade (−$9.0k/16yr).
- FACT: K=2: dev −76.7t/trade (36 trades); K=3: −222.8t (15 trades). Both FAIL.
- FACT: losing-day correlation vs Solar ≈ 0 (0.00-0.02) — the diversification would
  have been real had the edge existed; it does not.
- Verdict: daily-scale compression→expansion continuation has no qualified edge on NQ
  under C1 friction. Registry seq 312-314 FAIL. (Seconds-scale FSS-6 remains
  absent-not-falsified; this closes the DAY-scale variant.)
