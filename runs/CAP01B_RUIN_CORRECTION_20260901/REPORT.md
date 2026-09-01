# CAP01B — the corrected ruin table. **CAP01's headline was wrong.**

**2026-09-01.** Spec committed before results (`2c89374`). All four gates PASS.
`EVIDENCE STATUS: DISCOVERY_CONSUMED` — in-sample, post-selection, **LOWER BOUND on risk.**
**CAP01 is not overwritten.** It stands with a superseded banner, per `CLAUDE.md` §4.

---

## §0 THE CORRECTION

> **CAP01 published `P(max drawdown from peak > starting equity) = 66.2 %` and labelled it
> "P(lose the account)". That is not what it means.**
>
> | | at CAP01's own horizon and scale |
> |---|---:|
> | `P(maxDD from peak > equity)` — what CAP01 published | **0.666** |
> | **`P(equity actually reaches zero)`** — what the phrase means | **0.058** |
>
> **A 11.5× gap**, because the modelled path carries the in-sample drift. A path that makes
> +$40,000 and gives back $11,000 has `maxDD > equity` and has lost nothing.

**And the bound in CAP01 §6 was inverted.** Because `maxdd` prepends a zero peak,
`maxDD ≥ −min(cum)` holds on **every** path — verified true on all 20,000 draws (gate G2).
So `P(maxDD > E)` is an **UPPER** bound on no-liquidation ruin. CAP01 said *"the reported 0.662 is
a **lower** bound on ruin."* Backwards, in a real-money capital document.

**The qualitative conclusion survives, and that is stated before the numbers so it cannot look
like a rescue:** this account is **badly under-funded at 3 MNQ and adequately funded at 1.**

## §1 GATES

| gate | spec | observed | verdict |
|---|---|---|---|
| CAP01B-G1 | reproduce CAP01's `0.662` at **its** horizon — proving the difference is the correction, not a new bug | **0.666** | **PASS** |
| CAP01B-G2 | `maxdd ≥ worst_equity` on **every** draw (the identity that inverts the bound) | **True** | **PASS** |
| CAP01B-G3 | full-pool trade-level max DD == $51,891 | **51,891** | **PASS** |
| CAP01B-G4 | traded sessions/year == 188.1 | **188.1** | **PASS** |

## §2 THE THREE OTHER DEFECTS

**D2 — the horizons were 34 % long.** `sess_series` is a `groupby`-sum, so **only sessions on
which a trade closed exist in the series.** 873 such sessions span 4.641 calendar years =
**188.1 traded sessions/year**. CAP01's *"1y = 252"* is really **1.34 yr**; *"2y = 504"* is
**2.68 yr**. CAP01's own §4 contradicted this by correctly calling the sample "4.6-year".
**True horizons: 188 and 376.**

**D3 — CAP01 priced the NQ book × 0.30, not the MNQ book.** Gross P&L scaling is exact
(3 MNQ = $6/pt vs 1 NQ = $20/pt = 0.30 exactly). **Commission is not.** The CSV nets NQ
commission at $4.36/ctrRT; 0.30 × that is $1.31 where the live book pays 3 × $1.30 = **$3.90**.
$2.59 per full-size ctrRT × 13.65 ctrRT/wk = **$35.4/wk** — *exactly* `cost_model.weekly_penalty
(13.65, 3, 0.0)`, **committed one commit before CAP01 and not used.** Now charged.

**D4 — "the five worst sessions are all joint-loss days" is false.**

| session | P1 | XM | |
|---|---:|---:|---|
| 2026-07-29 | −2,388 | −8,864 | joint |
| **2022-04-21** | **0** | −10,749 | 🔴 **XM only — P1 did not trade** |
| 2026-07-17 | −1,722 | −7,524 | joint |
| 2026-07-20 | −2,764 | −6,229 | joint |
| 2026-06-04 | −1,764 | −6,444 | joint |

**4 of 5.** CAP01 printed the *combined* series under a label saying `JOINT`, and 2022-04-21 is
excluded by CAP01's own `aligned` filter. The claim was load-bearing for the
"diversification is worth less than it looks" argument.

**D5 — the correlation switched populations silently.** ρ = **0.242** on n = 231 (both legs
traded — CAP01's choice) · ρ = **0.205** on n = 378 (all days XM traded — **the repo's canonical
population**, and the one the +0.408/−0.204 mixture was computed on) · ρ = **0.105** on all 873.
CAP01 put its 0.242 beside the mixture figures and called it "consistent". Two populations,
presented as one.

**D6 — "sum of the legs $60,511" adds non-contemporaneous troughs.** P1's max-DD trough is
**2022-03-15**; XM's is **2022-07-19**. Adding peak-to-trough depths four months apart is not an
attainable no-diversification benchmark, so "the pair saves 14 %" is measured against a straw man.
(`GENESIS_III_VERDICT.md` separately states the sum of the legs as ~$39,500 against CAP01's
$60,511; **that discrepancy is unresolved.**)

## §3 🔴 THE CORRECTED TABLE

MEASURED basis · **MNQ commission charged** · **TRUE 2-year horizon (376 traded sessions)** ·
stationary bootstrap, sessions as whole units, 20,000 draws · account **$10,206.86**.

| pool | `MnqPerNq` | p50 DD | p90 DD | `P(DD > account)` | **`P(RUIN)`** | `P(margin call)` |
|---|---|---:|---:|---:|---:|---:|
| full | **1** | 36 % | 58 % | 0.004 | **0.001** | 0.001 |
| full | **2** | 71 % | 115 % | 0.195 | **0.019** | 0.024 |
| full | 🔴 **3 — LIVE** | **108 %** | **175 %** | 0.576 | 🔴 **0.065** | **0.082** |
| warm | 1 | 28 % | 42 % | 0.000 | 0.000 | 0.000 |
| warm | 2 | 57 % | 84 % | 0.035 | 0.002 | 0.003 |
| warm | 🔴 **3 — LIVE** | **85 %** | **126 %** | 0.356 | **0.017** | 0.026 |

**`P(RUIN)` = equity reaches zero. `P(margin call)` = equity falls below the day margin the peak
position needs (9 MNQ × $100 at size 3), at which point the book cannot post margin and is
liquidated — locking the loss in.** Margin call is the operative one and it is *higher* than ruin.

⚠️ **Both pools are shown and neither is quoted alone.** The `warm` pool drops the 37-session
un-warmed cold start, which the repo retired as an artifact and which the live book — running
`DaysToLoad = 365` — is configured not to reproduce. **But the warm cut is defined exactly at the
trough of the drawdown it removes**, so it is not innocent either. The truth is between them.

## §4 🔴 THE SENSITIVITY CAP01 NEVER RAN — and the answer is dominated by it

CAP01's series carries **$1,933/wk full-size**, which is **above the top of the campaign's own
honest band of $900–1,900/wk**, and CAP01 never varied it. Re-centring the series (variance
untouched), `MnqPerNq = 3`, true 2-year:

| assumed edge, $/wk full size | **`P(RUIN)`** | `P(margin call)` |
|---|---:|---:|
| in-sample $1,933 — as CAP01 built it | 0.059 | 0.075 |
| honest HIGH $1,900 | 0.054 | 0.067 |
| **honest CENTRAL $1,450** | **0.097** | 0.115 |
| **honest LOW $900** | **0.216** | 0.245 |
| **ZERO EDGE** | 🔴 **0.604** | 0.635 |

> **At `MnqPerNq = 3` the defensible two-year probability of losing the account is roughly
> 6 %–22 %, and 60 % if the edge is zero.** The campaign's own estimate is a **70 % chance that
> two years of live data cannot distinguish this book from zero** — which is not the same as
> P(edge = 0), but it is why the last row is not hypothetical.
>
> **CAP01's 66.2 % happened to land near the zero-edge figure. That was a coincidence, not a
> derivation.**

## §5 WHAT DID NOT CHANGE

- **1 MNQ remains safe** on every basis, pool and drift assumption: `P(RUIN) ≤ 0.001` full pool.
- **The under-funding conclusion stands.** The repo's corrected capital plan is $75,000–90,000 at
  full size → **$22,500–27,000 at 0.30 scale against $10,206.86 — 38–45 % funded.** Unchanged.
- **The machinery was not the problem.** An independent re-implementation confirmed the
  Politis–Romano bootstrap correct (E[sum] matches to 0.02 %, index usage uniform to 1.9 %), the
  zero-prepend **correct** (and it is what makes the error provable), the 18:00 ET session
  boundary correct and DST-safe, the spread charge matching `we_lab.py`'s convention exactly,
  session-unit resampling safe (1 of 2,817 trades crosses a boundary), and 20,000 draws stable
  across five seeds. **The arithmetic was right; the label on the output was wrong.**

## §6 THE LESSON, AND IT IS THE REPO'S OWN

`CLAUDE.md` §4: *"Decide the falsifier in advance, code every clause of it, and print a
GATE / SPEC / OBSERVED / PASS-FAIL table from the program — never assembled by hand."*
CAP01 did that, and **all four of its gates passed**, because every gate tested the
*reconstruction* ($51,891 / $36,943 / $537,353) and none tested **what the output quantity
meant**. A gate that checks arithmetic cannot catch a mislabelled statistic.

> **Add to the method: when a run's headline is a probability, one gate must state in words what
> event the probability is over, and a second must compute that event a different way.**
> G1 and G2 here are that pair, and they are cheap.
