# WE_W29 — FINAL WALK-FORWARD · REPORT

**VERDICT: STRONG.** The quoted object survives an honest out-of-sample refit of every free
parameter it has.

| object | weeks | net | weekly | % weeks + | worst | **Sharpe** | trades |
|---|---|---|---|---|---|---|---|
| **WF_FINAL (walk-forward)** | 199 | $205,679 | $1,034 | **60.3 %** | −$8,189 | **0.290** | 2,123 |
| FIXED_FINAL (1300/1000/0.5/0.8) | 203 | $211,484 | $1,042 | 59.6 % | −$7,797 | 0.300 | 1,967 |
| NAIVE (no box) | 203 | $226,157 | $1,114 | 60.1 % | −$17,365 | 0.214 | 2,636 |
| BESTFIXED (hindsight) | 197 | $205,811 | $1,045 | 63.5 % | −$7,257 | 0.304 | 1,736 |

**Walk-forward reaches 97 % of the fixed-calibration Sharpe** (0.290 vs 0.300) and clears
naive by a wide margin. The preregistered bar was 80 %.

## The contrast that tells the campaign's story

| | old family (W19) | current object (W29) |
|---|---|---|
| what is refit | which single config to trade | box levels, vote threshold, throttle q |
| **WF / FIXED** | **0.171 / 0.249 = 69 %** | **0.290 / 0.300 = 97 %** |
| choice churn | **88 %** of boundaries | **38 %** |
| verdict | WEAK | **STRONG** |

Replacing "select one configuration each quarter" with "aggregate the whole family and box the
session" converted a fitted result into a stable one. The quarterly picks cluster tightly —
`(1300, 1000, ·, ·)` appears in 15 of 17 refits — which is what parameter stability looks like
when you measure it instead of asserting it.

## Walk-forward per-year (all positive)
2022 **0.353** · 2023 0.062 · 2024 **0.410** · 2025 0.248 · 2026 **0.490**

## What this licenses, and what it does not
**Licensed:** quoting ~$1,040/week per contract at ~0.29–0.30 Sharpe with a −$8k worst week as
the object's honest out-of-sample expectation within this regime.
**Not licensed:** any claim beyond the modern regime (W17/W21: 2006–2021 is +0.056 pooled),
any claim of daily consistency (W26), and any relaxation of the model-risk statement (W25:
every sleeve is the same Solar ratchet).
