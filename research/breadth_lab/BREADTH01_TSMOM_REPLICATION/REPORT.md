# BREADTH01 — REPORT (readout 2026-08-19; spec frozen at f0bd917 BEFORE any data download)

**Verdict: FAIL per the frozen decision rule — CLOSED one-shot.** ARM_FULL fails G3-SPLIT's
"≥1 era CI_lo>0" prong (pre-2020 mean +2.11%/yr, CI [−0.33, +4.48]; post-2020 +2.75%/yr,
CI [−0.68, +6.15]) and consequently G7's G3-at-stress arm. Spec §6 letter: "G2/G3/G4/G7 fail
→ the replication itself fails on our data → record and close." The rule, not the narrative,
decides — same standard that closed ATRPOOL01 by 0.009 earlier today. **Closure scope: this
construction — 12-1 monthly sign TSMOM on the 15-ETF universe, both preregistered arms.**

## Full disclosure (the parts that passed, and by how much)

| gate | result | verdict |
|---|---|---|
| G1 (≥10 assets ≥15y; book ≥18y) | 15 assets; 23.3y (2003-02..2026-05, rf-clipped to 2002+) | PASS |
| G2 (full-period year-block CI) | net Sharpe **0.463**, ann +2.29% at 4.9% vol; CI **[+0.84%, +3.75%]** | PASS |
| **G3-SPLIT (≥1 era CI_lo>0)** | both era means positive; pre t≈1.76, post t≈1.2 — neither CI_lo>0 | **FAIL** |
| G4 (halves same sign) | Sharpe 0.42 / 0.52 | PASS |
| G5 (complementarity) | ρ_full **−0.037**, ρ_losing **+0.040**, +3.34%/yr on Solar losing days | PASS* |
| G6 (50/50 risk blend) | Sharpe 0.280→**0.544**; CDaR5 (vol-units) 48.1→**15.8** (−67%); maxDD 50.3→19.2 | PASS* |
| G7 (3× cost stress) | Sharpe 0.408, G2 holds; G3 fails as above | FAIL |

\* G5/G6 are **not red-team-verified** (FAIL verdicts don't trigger the confirm step);
treat as strong-but-unaudited. Known audit point: the Solar comparator concatenates
`e10_daily_hist.csv` (2006-2021) with `e10_daily_py.csv` (2022-2026) — scale consistency
between the two files must be verified before these numbers are used for any decision.

Replication fidelity: 13 of 15 stream Sharpes positive (median ≈0.28 vs the literature's
0.34); per-year book returns positive in **2008 (+5.1%), 2020 (+5.4%), 2022 (+6.9%)** — the
crisis-alpha signature the drawdown atlas asked complementary engines to have. Turnover
~23%/month of gross notional; disclosed rf substitution (official 13-week bill CSV, Yahoo
^IRX history unavailable).

## The spec-design error (mine), recorded as a campaign convention

G3-SPLIT's era-significance prong was designed for per-event NQ edges (hundreds-to-thousands
of events, large per-event t). Frozen onto a diversified low-Sharpe book it demands era-level
Sharpe ≥ ~0.49 (17y era) / ~0.79 (6.4y era) — while this spec's own §7 prior said "expected
0.4-0.8". Under my own prior the gate had roughly coin-flip power against a TRUE effect.
That is the ATRPOOL01 instrument pathology, self-inflicted at spec time. The rule stands and
the family closes (consistency is worth more than any single candidate), but the lesson is
now **binding prospective convention** (`../CONVENTIONS.md`): for diversified-book objects
with prior Sharpe ≤0.8, the era gate is means>0 both eras + halves same-sign + full-period
year-block CI_lo>0 + neither era CI_hi<0 — era-level significance is NOT required, because
requiring it selects against exactly the low-Sharpe/high-breadth objects this campaign
exists to test. This convention is set BEFORE any future breadth spec is written.

## What is and is not closed

- CLOSED (one-shot, permanent): 12-1 monthly sign TSMOM on this 15-ETF universe (both arms).
  No universe/horizon/parameter re-skin may be preregistered — a 1/3/12-month ensemble or a
  futures-universe re-run of the same sign rule would be a re-skin, not a new mechanism.
- NOT closed: the breadth CAMPAIGN (this was its first construction), genuinely different
  mechanisms (carry, defensive, cross-sectional), and the OWNER's mandate decision (whether
  to fund breadth properly — real futures data, real universe — which OUTSIDE_VIEW2 priced).
- Artifacts: `out/breadth01_results.json`, `out/book_daily_{full,exuseq}.csv`,
  `data/MANIFEST.json` (sha256 per file). Analysis mask ≤2026-05-31 held; data past the mask
  stored unread.
