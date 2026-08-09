# MAP — repo orientation (start here for anything not already in `CLAUDE.md`)

_Written 2026-08-09. Describes structure, not results — results live in the docs this file
points to, and those change; this file's own job is to stay a stable pointer, not to duplicate
content that will drift out of sync with it. If anything below and `CURRENT_TRUTH.md` disagree,
believe `CURRENT_TRUTH.md`._

## This repo holds four research campaigns, run one after another

| # | Campaign | Status | Entry point |
|---|---|---|---|
| 1 | **Solar Wave** — recover the vendor indicator, find the raw edge | CLOSED 2026-08-07 | `README.md` (root) |
| 2 | **Post-campaign audit** — independent re-verification of #1 | CLOSED 2026-08-07 | `research/audit/AUDIT_EXECUTIVE.md` |
| 3 | **SYSTEM_MASTER** — portfolio construction + one-contract product | **ACTIVE** | `research/system_master/CURRENT_TRUTH.md` |
| 4 | **Scalping Lab** — short-horizon scalp-alpha search, parallel to #3 | phase complete, dormant | `research/scalping_lab/CAMPAIGN_STATE.md` |

**If you only read one file: `research/system_master/CURRENT_TRUTH.md`.** It is the single
running log of the active campaign, updated after every wave, and the only doc in the repo
guaranteed not to lag behind the actual state of the research. Everything else — including this
file — can go stale; that one is append-only and current by construction.

Two filename collisions to know about, both intentional (different campaigns, not a mistake):
`NEXT_HANDOFF.md` exists at repo root (campaign #1/#2, closed) **and** inside
`research/system_master/` (campaign #3, live) — open the one under `system_master/` for a
resume point. `frontier.yaml`/`FRONTIER.yaml`/`SYSTEM_FRONTIER.yaml` exist under `research/`,
`research/scalping_lab/`, and `research/system_master/` respectively — one machine-readable
frontier per campaign, not three copies of the same thing.

## Top-level layout

```
CLAUDE.md          Agent rulebook — hard safety boundary, frozen baseline, conventions. Read first, always.
MAP.md             This file.
README.md          Campaign #1's own entry point (closed; banner added pointing here)
NEXT_HANDOFF.md     Campaign #1/#2's resume state (closed; banner added)
research/           All research content — see below
runs/                Immutable experiment directories: spec.yaml (frozen before results) + out/
src/analytics/       Python simulators/analytics — canonical, reused across campaigns
src/ninjascript/      The actual NT8 strategy source (.cs files) — what's really deployed/backtested
reports/              Campaign #1's final deliverable package only (not campaign #3's)
```

## `research/` subdirectories

**Campaign #1 (Solar Wave, closed) — numbered phases, raw evidence, never touch:**
`00_truth/`, `01_diagnostics/`, `02_solar_refinements/`, `03_reverse_engineering/`
(the indicator-recovery math — still genuinely useful reference, see
`SOLARWAVE_MATH.md`/`TYPE2_RECOVERY_REPORT.md`), `04_execution/`, `05_open_axes/`,
`06_red_team/`, `07_h014_price/`, `08_es_portability/`, `09_sleeves/`,
`10_v3v4_equivalence/`, `deep_research/` (top-level), `solar_wave_parity/`,
`crosstrade_smoke_test/`. Plus `Research_Thesis.txt` (the constitution, still governing
all campaigns) and `Research_Thesis_Empirical_Update.md`/`CAMPAIGN_STATE.md` (closed).

**Campaign #2 (audit, closed):** `04_complementary_family/`, `audit/`.

**Cross-campaign, still live:**
`registry/` (the trial ledger — `tested_configs.csv` is append-only and current, now well
past seq 442), `operational/` (live-ops rules: margin flatten, monitor protocol, locked-forward
data seal — still binding).

**Campaign #3 (SYSTEM_MASTER, active):** `system_master/`. This is where nearly all current
work lives. **As of 2026-08-09 (FINAL OPTIMIZATION DIRECTIVE close-out), the 3 shipped
objects' identity/architecture/formula/parameters/performance/capital-map/invalidation-criteria
live in one place: `BASELINE_MODELS.md`.** For "what are the final objects and exactly how do
they work", start there, not in the per-wave frontier docs below. For "what is the campaign
doing right now / what changed most recently", `FINAL_OWNER_DECISION_20260809.md` is the
closing status report — read it before `CURRENT_TRUTH.md` if you only have time for one file.
Its own reading order (per its `START_HERE.md`):
`START_HERE.md → CURRENT_TRUTH.md → SYSTEM_SCORECARD.md → NEXT_HANDOFF.md`, plus
`CLAIM_LEDGER.md` / `SUPERSEDED_CONCLUSIONS.md` / `KNOWN_ERRORS_AND_CORRECTIONS.md` for
what-changed-and-why, and `CONVENTIONS.md` for the binding statistical/evaluation rules used
in every wave. **Caution**: this directory also contains an early "V1" documentation layer
(`CURRENT_STATE.md`, `FINAL_NQ_SYSTEM*.md`, `NINJATRADER_MASTER_SPEC.md`, and several
`*_FRONTIER.md`/`*_ATLAS.md` docs from the campaign's first day) that is superseded in framing
but not deleted — `SUPERSEDED_CONCLUSIONS.md` tracks specific claim-level supersessions, though
note it too was last edited mid-campaign and its newest row (SM14 vs A-dominant) is now itself
outdated by later waves (A-dominant was subsequently killed at confirmation; SM14 is uncontested
FINAL again) — this is a live example of why `CURRENT_TRUTH.md` is the only doc trusted as
tie-breaker, not any index or ledger *about* CURRENT_TRUTH.

**Campaign #4 (Scalping Lab, dormant):** `scalping_lab/`. Entry: `CAMPAIGN_STATE.md`
(not `reports/LATEST.md`, which is a stale template — banner added). Its evidence (B-MOM, B1,
B-FADE) is a direct input into campaign #3, cited throughout as "B-MOM".

## `runs/` — every experiment, immutable

112+ directories, one per experiment, named by campaign generation: `SW*`/`RE01*`/`FH_*` =
campaign #1; `AUDIT*`/`B01*`/`DM01*`/`PORT01*` = campaign #2; `SM*` (non-V2) = campaign #3
early; `SMV2*` = campaign #3 current series (A through AK+, this is where all recent work is);
`EXPORT01`/`DATAPROBE01` = campaign #4. Each should have a `spec.yaml` (frozen before any
result was read) and, from `SMV2AA` onward, a `REPORT.md`. **Never overwrite a run dir, never
delete outputs** — this is raw evidence, not scratch, even for killed/rejected experiments.

## What actually governs everything (never edit after the fact)

- `CLAUDE.md` — hard safety boundary, frozen baseline numbers, workflow rules.
- `research/system_master/CONVENTIONS.md` — binding statistical/evaluation protocol for
  campaign #3 (bootstrap method, cost model, promotion gates).
- `research/registry/tested_configs.csv` + `TRIAL_ACCOUNTING_RULE.md` — the trial-counting
  ledger multiple-testing corrections are computed against.
- `research/operational/LOCKED_FORWARD.md` — the virgin-data seal (data ≥2026-08-01 is
  off-limits for tuning).

## Housekeeping done 2026-08-09 (this pass)

Removed (zero content, zero evidence lost): 7 empty placeholder directories
(`research/03_timeframes_parameters/`, `05_portfolio/`, `06_locked_forward/`, `src/ninja/`,
`src/research/`, and two empty run-output subfolders) and all stray `__pycache__`/`.pyc` build
artifacts (already gitignored, regenerable, never tracked). Added orientation banners (additive
only, zero content removed) to `README.md`, `NEXT_HANDOFF.md` (root), `RESEARCH_INDEX.md`, and
`scalping_lab/reports/LATEST.md` where they were silently stale. Did **not** move, rename, or
delete any run directory, spec, report, registry row, or raw data file — the "never delete raw
research evidence" rule in `CLAUDE.md` is absolute and was treated as such throughout.
