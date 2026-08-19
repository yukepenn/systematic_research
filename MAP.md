# MAP — repo orientation (start here for anything not already in `CLAUDE.md`)

_Written 2026-08-09, updated same day (repo consolidation, parity campaign close-out). Describes
structure, not results — results live in the docs this file points to, and those change; this
file's own job is to stay a stable pointer, not to duplicate content that will drift out of sync
with it. If anything below and `/BASELINE_MODELS.md` (repo root) disagree, believe
`/BASELINE_MODELS.md` for the 3 current objects and `CURRENT_TRUTH.md` for everything else._

## Start here

`README.md` (repo root) is now the current project landing page — read it first. It points to
`/BASELINE_MODELS.md` (the 3 canonical objects), `research/system_master/CURRENT_TRUTH.md`
(current state snapshot), `research/system_master/FINAL_OWNER_DECISION_20260809.md` (closing
status report), and `RESEARCH_HANDOFF.md` (repo root — what a new research wave should read
before starting). The rest of this file is deeper structural orientation, not a substitute.

## This repo holds four research campaigns, run one after another

| # | Campaign | Status | Entry point |
|---|---|---|---|
| 1 | **Solar Wave** — recover the vendor indicator, find the raw edge | CLOSED 2026-08-07 | `research/SOLAR_WAVE_CAMPAIGN_README.md` (moved from root 2026-08-09, content unchanged — root `README.md` is now the whole-repo landing page, not campaign #1's) |
| 2 | **Post-campaign audit** — independent re-verification of #1 | CLOSED 2026-08-07 | `research/audit/AUDIT_EXECUTIVE.md` |
| 3 | **SYSTEM_MASTER** — portfolio construction + one-contract product | **ACTIVE (engineering/parity CLOSED, back in research mode)** | `/BASELINE_MODELS.md` (repo root), then `research/system_master/CURRENT_TRUTH.md` |
| 4 | **Scalping Lab** — short-horizon scalp-alpha search, parallel to #3 | phase complete, dormant | `research/scalping_lab/CAMPAIGN_STATE.md` |

**If you only read one file for the 3 current objects: `/BASELINE_MODELS.md` (repo root).** For
"what's true right now" beyond the 3 objects themselves: `research/system_master/CURRENT_TRUTH.md`
— the single running log of the active campaign, updated after every wave, and the only doc in
the repo guaranteed not to lag behind the actual state of the research. Everything else —
including this file — can go stale; that one is append-only and current by construction.

One filename collision to know about (fixed 2026-08-11 — was previously two files both named
`NEXT_HANDOFF.md`, root and `research/system_master/`, "easy to open the wrong one"): the
root-level one is now named `NEXT_HANDOFF_CAMPAIGN1_CLOSED.md` to make the distinction
unambiguous. For a live resume point, use `research/system_master/NEXT_HANDOFF.md` — that one is
also now archived (superseded by `FINAL_OWNER_DECISION_20260809.md`/`CURRENT_TRUTH.md`, see
`research/system_master/_archive/README.md`), so in practice neither `NEXT_HANDOFF*` file is the
current resume point anymore; use `CURRENT_TRUTH.md` and `ACTIVE_RESEARCH_QUEUE.md` instead.
`frontier.yaml`/`FRONTIER.yaml`/`SYSTEM_FRONTIER.yaml` exist under `research/`,
`research/scalping_lab/`, and `research/system_master/` respectively — one machine-readable
frontier per campaign, not three copies of the same thing (this one remains intentional).

## Top-level layout

```
CLAUDE.md          Agent rulebook — hard safety boundary, frozen baseline, conventions. Read first, always.
README.md          Whole-repo landing page (rewritten 2026-08-09 — current systems, not campaign #1)
BASELINE_MODELS.md  THE canonical record of the 3 current objects (moved to root 2026-08-09)
RESEARCH_HANDOFF.md What a new research wave should read before starting (added 2026-08-09)
MAP.md             This file.
NEXT_HANDOFF_CAMPAIGN1_CLOSED.md  Campaign #1/#2's resume state (closed; renamed 2026-08-11, was NEXT_HANDOFF.md)
research/           All research content — see below (includes SOLAR_WAVE_CAMPAIGN_README.md,
                     campaign #1's own entry point, moved from root 2026-08-09)
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
work lives. **As of 2026-08-09, the 3 shipped objects' identity/architecture/formula/parameters/
performance/capital-map/invalidation-criteria live in one place at repo root:
[`/BASELINE_MODELS.md`](../BASELINE_MODELS.md).** (Moved there this same day — the copy still at
`research/system_master/BASELINE_MODELS.md` is now a one-line redirect stub, not the canonical
copy.) For "what are the final objects and exactly how do they work", start there, not in the
per-wave frontier docs below. For "what is the campaign doing right now / what changed most
recently", `FINAL_OWNER_DECISION_20260809.md` is the closing status report — read it before
`CURRENT_TRUTH.md` if you only have time for one file.
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

## Addendum 2026-08-18 (consolidation pass — three corrections to this file's own claims)

- The "one machine-readable frontier per campaign" note above is wrong about campaign #3:
  **`SYSTEM_FRONTIER.yaml` and `SYSTEM_SCORECARD.md` do not exist anywhere in the repo** (verified
  by full-tree search; the reading order quoting them is from an archived layer). Campaign #3's
  machine-ish state lives in `CURRENT_TRUTH.md` + `ACTIVE_RESEARCH_QUEUE.md` +
  `TESTING_LEDGER.csv`. The `research/frontier.yaml` (campaign #1) and
  `research/scalping_lab/FRONTIER.yaml` (campaign #4) files do exist.
- `runs/` is now **191 directories** (the "112+" above is a 2026-08-09 count). A machine-readable
  classification now exists: `research/registry/RUNS_INDEX.csv`.
- A repo-wide consolidated state map now exists and is the recommended first read after
  `README.md`: **`/STATE_OF_RESEARCH_20260818.md`** (all campaigns, merged open frontier, unified
  data boundaries, monitoring calendar).

## Housekeeping done 2026-08-09 (this pass)

Removed (zero content, zero evidence lost): 7 empty placeholder directories
(`research/03_timeframes_parameters/`, `05_portfolio/`, `06_locked_forward/`, `src/ninja/`,
`src/research/`, and two empty run-output subfolders) and all stray `__pycache__`/`.pyc` build
artifacts (already gitignored, regenerable, never tracked). Added orientation banners (additive
only, zero content removed) to `README.md`, `NEXT_HANDOFF.md` (root, since renamed — see below),
`RESEARCH_INDEX.md`, and `scalping_lab/reports/LATEST.md` where they were silently stale. Did
**not** move, rename, or delete any run directory, spec, report, registry row, or raw data file —
the "never delete raw research evidence" rule in `CLAUDE.md` is absolute and was treated as such
throughout.

## Housekeeping done 2026-08-11 (this pass)

A 6-zone read-only audit Workflow (system_master top-level docs, system_master run
subdirectories, `runs/`, `scalping_lab/`, other closed-campaign `research/` trees, `src/`+
`reports/`+root docs — ~2,800+ files reviewed) found **zero delete-worthy junk** anywhere — the
evidence layer (`runs/`, every campaign's experiment subdirectories) was already clean and stayed
untouched. All findings were top-level meta-documentation sprawl: 23 superseded docs moved from
`research/system_master/` into `research/system_master/_archive/` (index + reasoning per file in
that folder's own `README.md`), plus `reports/OWNER_STATUS.html` (a stale campaign-#3 dashboard
that had ended up inside campaign-#1's otherwise internally consistent closed package) moved to
`reports/_archive/`. Every move is a plain `git mv` — zero content edits, full git history
preserved. Also fixed the filename collision flagged above: root `NEXT_HANDOFF.md` renamed to
`NEXT_HANDOFF_CAMPAIGN1_CLOSED.md` (its own research/system_master sibling was itself one of the
23 archived — neither `NEXT_HANDOFF*` file is a live resume point anymore; use `CURRENT_TRUTH.md`
and `ACTIVE_RESEARCH_QUEUE.md`). Purged 27 gitignored, untracked `__pycache__` directories from
disk (948K, zero git footprint). No run directory, spec, report, registry row, or raw data file
was moved, renamed, or deleted.
