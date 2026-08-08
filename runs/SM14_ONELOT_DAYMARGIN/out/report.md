# SM14 — One-Lot Day-Margin Variant: PASS (plateau 318/319)

_2026-08-08. Spec frozen before read (seq 316-319). Rule: sign-with-hysteresis on the
winner's frozen consolidated MNQ target M = 0.7086·T′ + 2.83·B; flat decided 16:39,
filled ~16:42 (< 16:45 cutoff); no entries 16:30→18:00; B1 leg excluded by construction._

## Dev results (2022-01→2026-05)

| arm | a/b | 1 MNQ net | Sharpe | maxDD | worst mo | pos years | H1/H2 | 1 NQ net | 1 NQ maxDD |
|---|---|---|---|---|---|---|---|---|---|
| 316 | 2/0 | $21,155 | 0.713 | −$9,101 | −$3,024 | 4/5 | +/+ | — | — |
| 317 | 3/0 | $21,270 | 0.765 | −$6,524 | −$2,085 | 4/5 | +/+ | — | — |
| **318** | **3/1** | **$27,287** | **1.004** | **−$6,374** | −$2,105 | 4/5 | +/+ | $298,040 | −$58,887 |
| **319** | **4/1** | $25,915 | **1.016** | **−$5,160** | −$2,061 | **5/5** | +/+ | $265,244 | −$49,775 |
| anchor sign(M) | 0/0 | $23,837 | 0.730 | −$9,171 | −$4,076 | — | — | — | — |

Gates: all arms net>0 ✓; ≥3/5 years ✓; H1/H2 same sign ✓; max month share 21-25% ✓;
plateau = arms 318+319 (adjacent, Sharpe ~1.0, maxDD −$5.2-6.4k) ✓; both beat the
unconditional anchor on maxDD (−30/−44%) and worst-month (~half) ✓. **PASS.**

**Adopted: (a=3, b=1) primary, (a=4, b=1) co-equal plateau member.** ~2.8-3.5
executions/day. 2026-06/07 (CONSUMED window, characterization only): +$4.2k MNQ /
+$59.5k NQ (a=3,b=1). NQ commission is cheaper per notional ($4.36/RT vs $13.00/RT
for 10 MNQ), hence the higher NQ Sharpe; MNQ has 10× smaller unit risk and $100 day
margin — **recommendation: 1 MNQ** for margin ease, 1 NQ when capital ≥ ~$60k bar-level
DD budget. Day margin applies (flat before 16:45, re-entry after 18:00 at intraday rates).

Caveats: no clean OOS exists for this variant (holdout consumed); it inherits the
winner's regime dependence and monitors; 1-lot quantization forfeits the ensemble's
graded sizing (Sharpe 1.0-1.1 vs portfolio 1.22 at scale) — it is the EASY-TO-TRADE
variant, not the optimum. Registry: seq 316-319, 318/319 PASS_ADOPTED.
