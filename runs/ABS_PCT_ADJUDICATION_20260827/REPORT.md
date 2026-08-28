# ABS vs PCT — PCT reproduces coherently and stays incumbent. Historical work CLOSED.

| | |
|---|---|
| **verdict** | **OUTPUT A — the published PCT advantage reproduces coherently. KEEP PCT.** ABS frozen as prospective challenger/control |
| date | 2026-08-27 |
| reproduction | **BYTE-EQUIVALENT** — `dashboard.csv` re-run, max numeric diff **0.0e+00** across all 281 rows |
| scope | **CLOSED.** No W124–W140 box campaign follows this |

---

## 1. Source-provenance gate, in order

| step | |
|---|---|
| producing artifact | `runs/WE_W98_BOXDENOM/out/dashboard.csv` |
| producing code | `research/weekly_edge/src/run_we_w98.py` |
| **exact semantics** | **ABS**: `spnl += pnl` — the session box is a **dollar limit on TOTAL position P&L**. **PCT**: `spnl += pnl/u` — the box is **per contract**. `u` = contracts at entry, so **at size 1 the two objects are identical by construction**; every difference is a multi-contract session. P1 runs size 2 on **18.3 %** of trades |
| week key | **ISO week on session date** — already the same convention as W103 |
| cost | each arm's **own** candidate-specific spread rate from its own fill minutes (ABS $14.5175, PCT $14.4053 /ctrRT) + commission |
| reproduction | re-ran the producing script; **0.0e+00** difference. Published ABS `$885.19 / $26,388 / 53.05 % / t 3.581` all reproduce |

**Nothing was rebuilt from scratch.** ABS and PCT already come from *one run, one code path, one cost model, one week convention* — which is a stronger comparison than a fresh reconstruction, and the gate is satisfied by reproducing it.

## 2. Fixed windows — all burned

| arm | 13w | 26w | 52w | 104w | FULL |
|---|---:|---:|---:|---:|---:|
| **ABS** fixed-DD $/wk | −1,180 | −302 | 595 | 1,283 | **885** |
| **PCT** fixed-DD $/wk | **−522** | **882** | **1,988** | **1,713** | **1,231** |
| ABS positive weeks | 23.1 % | 42.3 % | 50.0 % | 54.8 % | 53.1 % |
| PCT positive weeks | 30.8 % | 53.8 % | 55.8 % | 56.7 % | 56.3 % |
| ABS maxDD | 21,674 | 26,388 | 26,388 | 26,388 | 26,388 |
| PCT maxDD | 12,874 | 12,874 | 12,874 | 22,928 | 22,928 |

**PCT is ahead in every window, including the recent ones.** There is no §3C situation — ABS does not look better lately.

## 3. The paired test, and why it needs two statistics

| window | mean PCT−ABS | t | p | **PCT wins** |
|---|---:|---:|---:|---:|
| 13w | +$931.23 | 0.752 | 0.467 | 84.6 % |
| 26w | +$954.04 | 1.253 | 0.222 | 84.6 % |
| 52w | +$489.24 | 1.240 | 0.221 | 84.6 % |
| 104w | +$268.27 | 1.150 | 0.253 | 80.8 % |
| **FULL** | **+$240.18** | **1.904** | **0.058** | **82.6 %** |

The FULL row reproduces W98's own `paired.csv` (240.178 / 126.125 / 1.904 / 0.0569).
**PCT's advantage does not clear 5 % on the paired magnitude test, even on the full sample.**

### Why an 82.6 % win rate only reaches p = 0.058

| | |
|---|---:|
| weeks PCT wins | **176 / 213** |
| **sign test** | **p = 7.09 × 10⁻²³** |
| mean gain on PCT-win weeks | **+$528.52** (n 176) |
| mean loss on ABS-win weeks | **−$1,196.03** (n 35) |
| ratio | **2.26×** |

> ### **PCT wins small and often; ABS wins rarely and big.**
> The **direction** of the effect is overwhelming; the **magnitude** is not. Both are true and both
> belong in the verdict: the per-contract denominator reliably improves the typical week while
> giving back **2.26× per occurrence** in the 16 % of weeks where the absolute box was the better
> constraint. A single p-value hides that; two statistics show it.

## 4. The control W98 built for exactly this question

`ABS_LOOSE` raises ABS's dollar budget by the **same factor** PCT's denominator does, isolating
*"is PCT better, or is a looser box better?"*

| comparison | mean $/wk | t | p |
|---|---:|---:|---:|
| PCT − ABS | 240.18 | 1.904 | 0.057 |
| PCT − ABS_LOOSE | 234.37 | 1.769 | 0.077 |
| **ABS_LOOSE − ABS** | **5.81** | **0.075** | **0.940** |
| PCT_MATCH − ABS | 153.53 | 1.482 | 0.138 |
| NOBOX − ABS | 450.53 | 1.624 | 0.105 |

> **Loosening the box is worth $5.81 (p 0.94). The gain is specific to the per-contract
> denominator, not to having more room.** That part of the original claim survives cleanly, and it
> is the part that matters mechanically.

## 5. Concentration

Top-1 differing week carries **11.5 %** of the total absolute PCT−ABS difference; top-5 **34.8 %**;
top-10 **50.6 %**; top-20 **70.1 %**. Consistent with the already-recorded *90.8 % of the gross
difference in 53 of 1,058 sessions*. **The effect is real, mechanically explained, and concentrated.**

## 6. Verdict

| | |
|---|---|
| **decision** | **OUTPUT A — KEEP PCT as research incumbent.** ABS is frozen as a **prospective challenger/control** |
| **what passed** | byte-equivalent reproduction; PCT ahead in every fixed window; the mechanism isolated by `ABS_LOOSE`; direction overwhelming on the sign test |
| **what did NOT pass** | the paired **magnitude** test — p 0.058 full-sample, and 0.22–0.47 on every shorter window |
| **honest statement** | **PCT is the better policy on direction and on every window, with a clean isolated mechanism, but its dollar advantage is not statistically established at 5 % and is concentrated in a minority of sessions** |
| **evidence class** | DISCOVERY-CONSUMED / BURNED. A burned advantage is not confirmation |
| **scope** | **`P1/ABS` historical research is CLOSED.** ABS earns its next evidence prospectively, beside PCT, from a common future timestamp |
