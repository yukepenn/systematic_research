# WE_W43 — MULTI-INSTRUMENT RE-DERIVATION · REPORT

Spec + amendment 1 (read 1 VOID on its own identity gate; see below).
**B1 IDENTITY PASS**: the NQ "re-derived" arm reproduces the incumbent **exactly**
($1,470/week, eff 0.198), which is the point of expressing NQ's own constants as multiples of
NQ's own σ and mapping them back. Net $4.36/RT, stress $14.36/RT, 2022-07 → 2026-08.

**Verdict: the preregistered falsifier fires. "The edge is NQ-specific" is now a SUPPORTED
claim instead of an artifact of a bad transplant — which is exactly the outcome the spec said
would be worth having.**

---

## 1. Why W11 did not settle this

W11 transplanted NQ's constants, and two of them are not dimensionless:

| | tick | clamp [40, 1200] ticks | median σ | clamp in σ units |
|---|---|---|---|---|
| NQ | 0.25 | [10, 300] pts | 3.253 | **[3.07, 92.22] σ** — never binds (VolMults are 6–16 σ) |
| ES | 0.25 | [10, 300] pts | 0.721 | **[13.9, 416] σ** — the lower bound collapses VolMult 6, 8 and 10 onto one threshold |
| RTY | 0.10 | [4, 120] pts | 0.451 | **[8.9, 266] σ** — same collapse |
| YM | 1.00 | [40, 1200] pts | 5.143 | **[7.8, 233] σ** — same collapse |

**W11 was not running the 6-member engine on the other instruments; it was running a
3-to-4-member engine.** The session box compounded it: −$1,300 in dollars against point values
of 20 / 50 / 50 / 5.

Re-derived, each instrument gets the clamp as **the same multiple of its own σ** and the box as
**the same fraction of its own median session dollar range** — nothing dimensionless is touched.

## 2. It does not rescue them (`SUPPORTED`)

| instrument | box | trades | $/trade | weekly | worst week | Sharpe | eff | **stress-net** |
|---|---|---|---|---|---|---|---|---|
| **NQ (identity check)** | −$1,300/+$1,000 | 1,950 | $153.0 | **$1,470** | −$7,418 | 0.311 | 0.198 | **+$1,374** |
| ES re-derived | −$715/+$550 | 2,008 | $19.7 | $188 | −$5,243 | 0.083 | 0.036 | **+$92** |
| RTY re-derived | −$433/+$333 | 2,326 | $2.2 | $24 | −$3,301 | 0.017 | 0.007 | **−$87** |
| YM re-derived | −$510/+$392 | 2,331 | $9.2 | $101 | −$3,338 | 0.062 | 0.030 | **−$9** |
| ES W11 transplant | −$1,300 | 2,370 | $21.7 | $243 | −$13,139 | 0.080 | 0.019 | +$131 |
| RTY W11 transplant | −$1,300 | 2,081 | $10.3 | $101 | −$3,997 | 0.055 | 0.025 | +$2 |
| YM W11 transplant | −$1,300 | 3,070 | $6.2 | $90 | −$4,641 | 0.045 | 0.019 | −$55 |

The re-derivation does what it was supposed to — ES's worst week improves from −$13,139 to
−$5,243 and its eff nearly doubles (0.019 → 0.036) — **and it still does not produce a
tradeable sleeve.** RTY and YM are stress-net *negative*; ES clears the stress line by $92 a
week on 2,008 trades, which is noise. Per year, ES is stress-negative in 2023, RTY in three of
five years, YM in three of five.

**The honest statement is now the strong one**: with the constants re-derived correctly in each
instrument's own units, the Solar ratchet still does not earn on ES, RTY or YM. It is NQ-specific.

## 3. The genuinely valuable measurement — and its cruelty

| weekly P&L correlation | NQ | ES | RTY | YM |
|---|---|---|---|---|
| NQ | 1.00 | 0.61 | **0.10** | **0.10** |
| **inside NQ's worst-decile weeks** | 1.00 | 0.40 | **0.04** | **0.03** |

**RTY and YM are almost perfectly decoupled from NQ, including inside our drawdowns** — 0.04
and 0.03, the best decoupling any sleeve in this campaign has shown, better than axis B's −0.25
and far better than the clock sleeves' 0.12–0.33.

**And they do not earn.** The equal-risk basket, at the same total weekly σ as NQ alone:

| | Sharpe | eff | CVaR-eff |
|---|---|---|---|
| equal-risk NQ+ES+RTY+YM | 0.176 | **0.095** | 0.118 |
| **NQ alone at the same σ** | **0.303** | **0.188** | **0.258** |

Adding three near-zero-expectancy sleeves halves the efficiency. **Decoupling is necessary and
not sufficient** — the same lesson W40's axis B taught, now with the cleanest possible example:
correlation 0.03 inside our worst weeks is worthless when the sleeve's own expectancy is zero.

## 4. Read 1 was VOID on its own identity gate (amendment 1)
The NQ arm produced $1,529/week against the incumbent's $1,470. The re-derivation arithmetic
was right; the fill layer was not — it conflated direction and size into one array, so a bar
where the vote had just turned off suppressed an entry the incumbent would have taken. Fixed to
the incumbent's exact semantics, and the identity is now a **hard gate that aborts the run**
rather than a number to inspect afterwards. **The built-in identity check is what caught it** —
without it the wave would have quoted a different object's numbers.

## 5. Where this leaves the campaign
The last cheap route to diversification is closed. What remains open: the W41 clock basket
(adopted, scale-limited), the exposure gap found in W44, and paid information (VWAP Flux).
The model-concentration prior is unchanged and now has a sharper statement: **not only is every
profitable sleeve the same Solar ratchet, the ratchet itself does not travel to the other three
index futures even when its constants are re-derived in their own units.**
