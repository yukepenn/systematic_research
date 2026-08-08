# SM03 — Disaster Stop (close-basis trigger): ALL ARMS FAIL FROZEN GATES

_2026-08-08. Spec frozen before read. Results: `out/results.csv` (seq 291-296)._

## Verdict: NO PROMOTION — and a structural lesson

The frozen trigger `(entry_px − close)·side ≥ m·S_entry` is **algebraically shadowed
by the Solar reversal exit**: anchor ≥ entry (long) implies the reversal level
anchor−S ≥ entry−S, so any close beyond m≥1.0·S from entry has already fired the
Solar exit on the same close basis. FACT: m=1.25 and 1.5 arms trigger ZERO stops;
m=1.0 arms trigger only 32 (entry-fill gap cases), yielding d_maxDD +3.9%
(< 5% gate), dSharpe +0.011 (P(≤0)=0.155), retention 100/100. All arms fail the
"≥5% improvement in maxDD/ES5/worst-month" gate. Registry: seq 291-296 = FAIL.

## Lesson (labeled)

- FACT: a close-basis disaster stop cannot exist inside this architecture; the
  SM02B crossing population (MAE ≥ 1.0·S, E[remaining] −$14 CI-negative, 42% of
  gross-loss mass) is reachable only via the bar's INTRABAR extreme.
- INFERENCE: the implementable form is an OnBarClose trigger on the fill bar's
  Low/High (long: Low ≤ entry − m·S), exit next bar open — decision on completed
  bars (no resting order, so H-011's desync failure mode does not apply; the
  execution stays market-at-next-open exactly like every other exit).
- Follow-up spec SM03B frozen separately (seq 301-306). This is a corrected
  trigger-input, preregistered before any SM03B result read; SM03's close-basis
  family is dead and may not be re-tuned.
