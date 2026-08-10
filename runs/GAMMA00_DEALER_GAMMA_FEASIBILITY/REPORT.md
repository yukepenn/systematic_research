# GAMMA00 — dealer-gamma literature + data feasibility: DATA_BLOCKED, one new hypothesis spun off

**Disposition: CLOSED for now, DATA_LIMITED.** Literature review complete (primary sources only,
per directive sec44/79 prohibition on vendor/retail evidence). Local data feasibility check
complete: zero SPX/NDX options data exists in this repo, and building the genuine strike-level
dealer-gamma mechanism GAMMA00 was scoped for requires external data acquisition. Not purchased —
this is the owner's call. One valuable, genuinely new, no-data-needed hypothesis fell out of the
literature pass and has been spun off as its own family: **MOM01**.

## Literature: the mechanism is real, but the rigorous (dealer-data) evidence says "not large," and none of it is NQ-specific

Read primary sources directly (not vendor summaries), across five angles per directive sec44:

1. **Dao/Nguyen/Deremble/Lempérière/Bouchaud/Potters** (arXiv:1607.02410) — does NOT model dealer
   hedging at all. It's a trend-convexity result (trend P&L ≈ long-term minus short-term realized
   variance, replicating the SG CTA Index >80% correlation). Relevant to this campaign's trend/
   convexity framing generally, not to the gamma-hedging question specifically.
2. **Dim, Eraker, Vilkov** ("0DTEs: Trading, Gamma Risk and Volatility Propagation," R&R at
   *Review of Financial Studies*) — abstract states open-interest gamma "does not propagate past
   volatility"; the 2012-2019 vs 2020-2023 volatility-response difference is "economically
   negligible" (0.15 std devs). Their gamma variable is Level C/D (not dealer-signed) — a
   limitation the authors themselves flag. SPX/SPY/ES only, no NDX.
3. **Baltussen, Da, Lammers, Martens** (*JFE* 2021) — establishes a broad "hedging-demand-driven
   intraday momentum" effect across 60+ futures. **NQ is directly, robustly included and shows
   one of the strongest effects of any of the 17 equity index futures tested** (β_ROD=6.36,
   t=7.97, R²_OOS=3.76%). But their *specific* options-dealer-gamma test (not the broader
   momentum effect) was built and tested only for SPX, on a self-acknowledged naive Level-D proxy
   ("we assume option market makers are short all puts and long all calls" — footnote 8), and is
   conditional (significant only on negative-gamma days, insignificant on positive-gamma days).
4. **Amaya, Garcia-Ares, Pearson, Vasquez** (Cboe-hosted, Jan 2025) and **Cboe's own Mandy Xu
   analysis** (Sept 2023) — both genuine Level-A studies (real trade-capacity-tagged dealer
   inventory reconstruction, 442.6M SPX/SPXW trades). Both conclude the effect, while
   statistically real, is **"not large"**: max gamma-induced daily realized-vol increase is 3.3
   percentage points, against a natural day-to-day RV std dev of 4.5pp (changes ≥3pp happen
   ~weekly anyway); typical/median impact is actually a *reduction* in volatility (dealers are
   usually net long gamma). Hedging flow is 0.04%-1.9% of daily SPX futures liquidity.
5. **No primary source anywhere performs a rigorous, dealer-data-based (Level A/B) test of this
   mechanism for NDX/QQQ/NQ specifically.** Only unverified retail GEX-vendor blog claims exist
   for NQ — explicitly excluded from the evidence base per directive sec47/79.

**Synthesis:** the literature supports treating "index intraday momentum consistent with
dynamic-hedging demand" as real and NQ-specific (Baltussen et al., strong direct evidence) — but
does **not** support assuming "0DTE options-dealer gamma specifically is a major, tradeable
driver of NQ price action" (no NQ-specific rigorous evidence, and the closest analogue, SPX, is
explicitly characterized by its own most careful investigators as *not large*).

## Data feasibility: fully blocked locally

Repo-wide search (Glob/Grep for `*SPX*`, `*NDX*`, `*option*`, `*OI*`, `*greeks*`, `*gamma*`,
`*0DTE*`, `*dealer*`) confirms **zero** SPX/NDX options-chain data exists anywhere in this repo —
no strikes, Greeks, open interest, NBBO quotes, or trade prints, at any granularity. No top-level
`data/` directory exists to hold it. The only options-adjacent asset
(`research/04_complementary_family/c01_t08_vrp_proxy_report.md`) uses free, EOD, index-level
proxies (Cboe PUT index, SVXY, VIX-minus-RV) — no strike-level detail, cannot support a genuine
dealer-gamma-by-strike computation. `research/deep_research/DR-02.md`'s hypothesis H-DR-D5
already flagged and deferred this exact gap.

See `DATA_PURCHASE_OPTION.md` (same directory) for the concrete cost/coverage picture, per
directive sec48. **No purchase or subscription action was taken.**

## Verdict

**CLOSED — DATA_LIMITED, not CLOSED_INFORMATION_CLASS** (per the addendum's own vocabulary,
Task #115). The mechanism is theoretically sound and even empirically confirmed for SPX with
genuine dealer data; it is specifically the *NQ-relevant, strike-level* evidence that's missing,
and that's a data-acquisition blocker, not a falsified hypothesis. Deferred pending an owner
authorize/defer decision on the options-data purchase.

**Spun off:** `MOM01` — Baltussen et al.'s direct, robust, NQ-specific intraday-momentum finding
needs no new data and is a genuinely distinct external mechanism (not another internal OHLCV
transform). Opened as its own family; see `runs/MOM01_INTRADAY_MOMENTUM/`.
