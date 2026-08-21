# KDJMA01 — REPORT (readout 2026-08-21; spec frozen at 0df8a1b BEFORE any statistic)

**Verdict: FAIL — SIGNIFICANTLY NEGATIVE, and negative BEFORE costs. Family CLOSED one-shot;
the OHLCV pause resumes.**

## Numbers (N=43,951 trades, 8.35/day, 20 years, C1 costs)

- Net **−$796,946** (−$18.13/trade); iid CI [−23.5, −12.8] and year-block CI [−23.8, −13.3]
  — both entirely below zero. Negative in **20 of 21 years** (2018: +$477 ≈ 0); worst year
  2025: −$148.7k (fixed 20-pt stop shrinks in % terms as NQ's price level grows → churned
  faster).
- **Gross per trade = −$3.77 BEFORE commission and slippage.** This is the decisive number:
  the signal is not "too small for costs" — it is worthless at zero friction. No cost
  engineering, no broker, no rebate can save a negative-gross signal.
- Win rate 34.2%. Exit anatomy: stops (31% of exits) −$417.5 each; ladder exits +$144;
  close exits +$328 — the 20-pt "strict stop" is the loss engine, realizing noise 13,643
  times. Both sides negative (short −$26.1, long −$11.1).
- MA127 disclosure arm (preregistered): −$18.21/trade, gross −$3.85, win 34.2% —
  parameter-indifferent (`out/kdjma01_ma127_disclosure.json`).
- G8 letter-PASS (ρ_losing 0.17) — irrelevant given own expectancy.

## The 26×/31× claim, priced

The base signal at 1 contract loses −$18/trade with ~8 trades/day (≈ −$150/day expectation).
Turning ANY strategy into 26× in a month requires extreme leverage compounded daily;
applying leverage/pyramiding to a negative-expectancy base strictly accelerates ruin. If the
posted statements are genuine, they are one surviving path of an over-leveraged scheme —
the documented shape of such evidence (Taiwan complete-market record: top 0.1% of day
traders ≈ 37.9 bps/day net ≈ 8%/month; 2,600%/month is ~300× the measured elite). Two
consecutive lucky months is exactly what survivorship posts look like: nobody screenshots
the blown accounts. The "梯形加仓" and the discipline narrative are sizing theater on top of
a signal that 20 years of data prices at **negative before costs**.

## Construction caveats (disclosed, none verdict-bearing)

KDJ params unknown in the source claim → classic (9,3,3) recursion used; MA120 primary +
MA127 both run, indistinguishable. Session-close flat imposed (house convention; the claimed
system's overnight behavior unspecified). Exit ladder = fractal-5 confirmed-swing reading of
"谷底高于一谷底". Stops evaluated at 1-minute resolution with gap-through fills at the worse
open (ONRANGE lesson applied). The verdict's margin (CI upper bound −$12.8) dwarfs any
plausible reading variance.

Family CLOSED (one shot; MA-length/KDJ-param/stop-distance/swing-definition re-skins
ineligible; a Solar-combination question would only ever have been preregistered on a PASS).
Artifacts: `out/kdjma01_{results.json,trades.csv,ma127_disclosure.json}`. No red team (FAIL).
