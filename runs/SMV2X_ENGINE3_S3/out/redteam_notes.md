# Red team notes — SMV2X_ENGINE3_S3 (seq 396-398, R1 Family Test, Engine-3 slate 3)

Verdict: **CONFIRMED** (letter-exact spec execution; independent recomputation matches all
gate-bearing numbers; four honest KILLs; one immaterial numeric slip in a supplementary
disclosure, corrected below).

## 1. Spec letter-exactness

- Gates implemented exactly as frozen in `spec.yaml`, no softening, no extra cells, no post-hoc
  selection:
  - e396: N>=40, t_nw>=2, WF same-sign, plateau {1,2,3} same-sign — 4/4 gates checked,
    center=hold 2 exactly as spec says ("center = 2"). `gates.csv` shows N=12 (FAIL),
    t_nw=-2.2215 (FAIL, and wrong-signed vs the tested continuation hypothesis), WF same-sign
    (PASS, both negative), plateau same-sign (PASS, all three holds negative).
  - e397: two cells (FOMC, CPI), N>=25 / t_nw>=2 / WF-same-sign each, reported separately per
    spec ("report separately, not pooled") — no pooling occurred, no extra plateau gate
    invented (spec does not specify one for e397 and none was added).
  - e398: N>=40, t_nw>=2, WF same-sign, plateau {T+1-only, T+1..T+3} same-sign — center =
    T+1-only (reasonable, disclosed default; both cells share the same N=28 so the choice is
    immaterial to the N gate).
  - No gate thresholds were adjusted after seeing results. All four cells (e396, e397-FOMC,
    e397-CPI, e398) fail on t_nw>=2, the binding gate in every case; `verdicts.json` = all FAIL,
    matches `gates.csv` mechanically (`sub["pass"].all()` per engine).
- NW t-stat (session-clustered, Bartlett/Newey-West lag 5) and bootstrap (block=5, B=10000,
  seed=20260808) match the disclosed "house convention," and match the literal implementation
  used in the prior engine-3 slates (`runs/SMV2K_ENGINE3_S1/smv2k.py`,
  `runs/SMV2P_ENGINE3_S2/smv2p.py`: same `NW_LAG=5`, same `boot_ci_mean` signature/seed).
- Commission $4.36/RT (NQ Lifetime) and 1-tick adverse slippage via the shared `_fill` helper
  match CLAUDE.md's frozen truth and the substrate's `TICK=0.25`.
- "No fade variant" instruction for e397 respected: both `sim_fomc`/`sim_cpi` trade
  `d = sign(move)` — continuation of the initial post-release move, never a fade.
- e398 FLAT-during-T-3..T constraint is asserted in code (not just claimed in prose) and the
  assertion holds trivially by construction (entries always start at T+1, strictly after the
  window) — re-run confirms both `pnl_during_flat_windows_t1only` and `..._t3` are exactly 0.0.
- Citations to the owner directive check out: V4 §51 "Automatic next-wave logic" (line 2756)
  does say, in sequence, "IF first Engine #3 slate fails: run three new mechanism-expansion
  passes," consistent with slate-1(SMV2K)->3-passes->slate-2(SMV2P)->3-passes->slate-3(SMV2X)
  lineage recorded in `research/system_master/COMPLEMENTARY_ENGINE_FRONTIER.md`. §25 "Engine #3
  promotion standard" (line 1453) is the actual source of the "losing-day/losing-week
  correlation" complementarity criterion cited in `spec.yaml`. The "9 candidates total" claim
  (3+3+3 across SMV2K/SMV2P/SMV2X) and the "defer to ES/RTY/YM cross-market export before a 4th
  slate" claim both match `COMPLEMENTARY_ENGINE_FRONTIER.md` and
  `research/system_master/NEXT_HANDOFF.md` verbatim — not fabricated.
- Champion curve used for complementarity (`runs/SMV2H_ONECONTRACT/out/rerank_curves.csv`,
  column `60_40`) is confirmed as DAYONLY_DUAL6040 per
  `research/system_master/SYSTEM_FRONTIER.yaml` (line 125, "champion: DAYONLY_DUAL6040 (60/40
  retained)") and `CURRENT_TRUTH.md` line 97.
- No data >= 2026-08-01 used: script asserts
  `bars["sd"].max() < pd.Timestamp("2026-08-01")` and additionally clips to `DEV_END =
  2026-05-31`; re-run confirms `range 2022-01-03 .. 2026-05-29`.

## 2. Independent recomputation (from `out/` artifacts and raw substrate, not from the script's
own printed numbers)

Full script re-run (`python runs/SMV2X_ENGINE3_S3/smv2x.py`) reproduces every `out/*.csv` file
byte-identical to what's on disk (`diff -rq` clean) — deterministic, no manual editing of
outputs.

Independently reimplemented (fresh code, not copy-pasted from `smv2x.py`) NW t-stat and WF-split
computation, run directly against `out/e396_events.csv`, `out/e397_events.csv`,
`out/e398_events.csv`:
- e396 hold=2: n=12, mean=-2429.36, **t_nw=-2.2215** (matches `e396_summary.csv` exactly), WF
  22-24=-1906.03 / 25-26=-2952.69 (matches).
- e397 FOMC: n=35, mean=-255.93, t_nw=-0.3060 (matches). e397 CPI: n=52, mean=159.39,
  t_nw=0.5899 (matches). WF splits for both match exactly.
- e398 T+1-only: n=28, mean=325.64, t_nw=0.6836 (matches). T+1..T+3: n=28, mean=905.46,
  t_nw=1.2548, WF 22-24=1564.06 (t=2.73) / 25-26=-484.92 (t=-0.39) (matches, including the
  flagged in-sample-only WF flip).
- Recomputed from raw substrate (`sm01_solarsim.load_bars_3m`, independent of the run script):
  burn-in-eligible sessions = 881 (matches); 3-sigma shock count WITH 12mo burn-in = 12
  (matches, this is the gated N); WITHOUT burn-in = 14 (matches the "14 total" side-claim, which
  is not itself persisted as code in `smv2x.py` but is reproducible); at a looser 2-sigma
  threshold WITHOUT burn-in = 64 (matches the "64" side-claim). These two supplementary checks
  were evidently run ad hoc and not saved to the committed script — they are reproducible and
  correct, but not independently re-derivable from the repo alone without rewriting them (minor
  provenance gap, does not affect the verdict since they are disclosed as supplementary, not
  gate-bearing).
- `jointloss_complementarity.csv` correlations and joint-loss-week means all match
  `key_numbers` in the exec report exactly (corr_daily/weekly for all 4 cells, champ
  mean/week-all, champ mean/week-jointloss, per-engine mean/week-jointloss).
- Calendar counts verified against `calendars.py` directly: `FOMC_DATES` has 37 entries (35
  fall <=2026-05-31, matches N used, confirms "zero dropped for missing bar data" for FOMC);
  `CPI_DATES` has 52 entries, all <=2026-05-31, all used (matches "zero dropped").
- e398: 53 candidate 3rd-Fridays generated (`e398_expiry_calendar.csv` has 53 rows), exactly 2
  flagged `in_session_calendar=False` (2022-04-15, 2025-04-18, both Good Friday) -> 51 valid,
  independently re-derived scan of the T+1 breakout logic against the raw substrate finds the
  same 28 breakout events and confirms **zero** ambiguous same-bar dual-breach cases occurred
  (supports the "never observed" claim rather than merely asserting it).

**One discrepancy found and corrected**: the exec report's caveat states "even excluding it
[the 2024-07-31 event, -$20,599.36] the remaining 11 events average -984/event." Recomputing
directly from `e396_events.csv` (`net_h2` column, sum=-29152.32 total, minus -20599.36 =
-8552.96 over 11 events) gives **-$777.54/event**, not -$984. This is a genuine arithmetic
error in the supplementary disclosure — not a fabricated number (some real intermediate
miscalculation), and it does not touch any gate, verdict, or the four persisted `out/`
artifacts (all of which check out exactly). Directionally the claim is still correct (excluding
the outlier, the remaining events still average a loss, so the "not driven entirely by one
event, but that one event moved the point estimate a lot" framing survives) — only the specific
dollar figure is wrong. Correct value for the record: **-$777.54/event** (n=11).

## 3. Lookahead / leakage scan

- e396 shock definition: `sigma60 = logret.shift(1).rolling(60, min_periods=2).std()` — causal
  (uses only sessions strictly before the shock day), 12-month burn-in enforced via
  `S["sd"].ge(BURNIN_CUTOFF)` where `BURNIN_CUTOFF = FIRST_SD + 365 calendar days`
  (2023-01-03) — no expanding-window peek past the burn-in boundary.
- Entry occurs the session AFTER the shock (`sd_entry = ALL_SD[i+1]`, entered at that session's
  0936-stamped bar open) — the shock itself (measured off session-close-to-close) is fully
  known before the entry fill. No same-bar or intra-shock-day entry.
- e397 FOMC/CPI: entries are at the second measurement bar's open (1433 / 1003), i.e. after the
  move used to determine direction has already printed — no lookahead into the move itself.
  Exit for FOMC is same-session close (known only after the session ends, correctly realized at
  `at_close` fill); CPI exit is the first bar closing >=11:00, again strictly forward-only.
- e398: T-3..T range uses only completed sessions' RTH high/low; breakout scan starts at T+1's
  first RTH bar and walks forward bar-by-bar with `np.searchsorted`/sequential scan — no
  peeking into bars after the triggering one for entry price (entry fill uses only the
  triggering bar's own O/H/L).
- Calendar dates (FOMC/CPI/opex) are exogenous public dates, not derived from or fitted to the
  price series; opex dates are a mechanical WOM-3FRI rule cross-checked against the session
  calendar (2 correctly excluded as Good Friday, not silently substituted).
- `assert bars["sd"].max() < pd.Timestamp("2026-08-01")` present and passes; dev window capped
  at 2026-05-31, comfortably inside the campaign-wide sealed-forward boundary (>=2026-08-01).
  No holdout/locked-forward data used for tuning.

## 4. Language / honesty audit

- All four verdicts are correctly labeled KILL and match the mechanical gate table — no
  gate was softened because a result "looked good" (none did; nothing came close to passing
  cleanly. FOMC and e396 fail 2-3 gates each, not just the marginal one).
- The e396 "WRONG SIGN" characterization is accurate and appropriately emphasized: the center
  cell is significantly *negative* (t=-2.22) against a hypothesis that explicitly required a
  positive-sign continuation read — this is a stronger, more informative kill than a flat/noise
  result, and the report does not undersell it.
- e398's T+1..T+3 in-sample WF significance (t=+2.73 on 2022-24, flipping to -0.39 on 2025-26)
  is flagged rather than spun as supportive evidence; correctly framed as "exactly the kind of
  in-sample-only result the campaign's WF discipline exists to catch."
- The CPI-only scope decision for e397's "CPI/NFP/PCE" cell is disclosed prominently (not a
  silent drop): rationale (N mismatch 3x spec estimate, NFP/PCE lack a clean schedule) is
  documented in `out/calendar_sources.md`, and the deferral is named as a scope limitation, not
  presented as if the full pooled cell had been tested.
- The BLOCKED disclosure on `REPORT.md` (spec's `outputs:` line names it, but the subagent could
  not write it per its own tooling restriction) is a genuine, correctly-labeled BLOCKED, with the
  narrative content preserved in the structured output instead — not silently dropped. All other
  named `outputs:` artifacts exist on disk and were verified present.
- Confidence caveats on the CPI 2022-2024 date list (HTTP 403 on the two canonical BLS schedule
  pages, spot-verified on 4 months instead) are disclosed rather than presented as
  fully-independently-sourced.

## 5. Decision mechanics

`verdicts.json` is produced purely from `gates.csv` via `sub["pass"].all()` per engine/cell —
no manual override path exists in the code. Re-running the script reproduces the identical
verdict dict. The run-level roll-up ("ALL THREE ENGINES FAIL... next step is a cross-market
data export before a 4th NQ-only slate") is the literal V4 §51 next-wave logic applied
mechanically to a 0/3-pass outcome, not an editorial call.

## Overall

Letter-exact spec execution; every gate-bearing number recomputes exactly from
`out/e396_events.csv`, `out/e397_events.csv`, `out/e398_events.csv`,
`out/jointloss_complementarity.csv`, and the raw substrate; script is fully deterministic/
reproducible; no lookahead found; calendar dates are genuinely deterministic/public (FOMC
fetched live, opex mechanically ruled, CPI disclosed as reconstructed+spot-verified for
2022-2024); language is honest throughout, kills are correctly and mechanically applied. One
immaterial arithmetic slip in a supplementary (non-gate-bearing) disclosure was found and is
corrected above (-$777.54/event, not -$984/event, for the "excluding the worst e396 event"
side-note) — this does not change any verdict, gate, or persisted artifact, so the run stands
as **CONFIRMED**.
