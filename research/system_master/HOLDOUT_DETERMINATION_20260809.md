# HOLDOUT DETERMINATION — 2026-06-01 → 2026-07-31, for the SYSTEM_MASTER campaign

_Written 2026-08-09 under MEGA PROMPT V7 §E-1. Append-only; nothing in this file may be
rewritten later, only appended to with a dated correction (C7)._

## VERDICT: **CONSUMED.** Confidence: near-certain, from direct evidence.

**The directive's premise is false, and I am saying so plainly because §18 requires it.**
V7 §E states that "whether SYSTEM_MASTER's own discovery ever touched Jun-Jul 2026 is a
different question and has never been answered." It was answered on **2026-08-08**, the day
before this directive was written, by a run that exists in this repo and whose entire purpose
was to answer it: `runs/SM11_HOLDOUT_READ/`.

There is therefore **nothing to seal**, and the sealed-holdout declaration V7 §E-2 asks for
cannot honestly be made. Declaring it a holdout now would be a false statement about the
record.

---

## The decisive artifact

`runs/SM11_HOLDOUT_READ/out/report.md:1` —

> `# SM11 — THE Joint Holdout Read (2026-06-01 → 2026-07-31): CONSUMED`

> `_2026-08-08. Protocol: FINAL_PACKAGE_SPEC.md (frozen+committed before this read).`
> `One read, 45 sessions. Daily vectors committed per finalist._`

Six finalists were scored **on that window** and the numbers published:

| finalist | net | mean/day | sd | maxDD (window) | worst day |
|---|---:|---:|---:|---:|---:|
| F1 SOLAR | +$60,150 | 1,337 | 4,826 | −13,344 | −12,724 |
| F2 TILT50 | +$60,394 | 1,342 | 4,654 | −13,528 | −11,096 |
| F3 BMOM (1 NQ) | +$400 | 9 | 5,931 | −39,161 | −16,742 |
| B1 leg (1 NQ) | +$12,535 | 279 | 6,852 | −38,810 | −18,800 |
| F4 PORT_532 | +$46,117 | 1,025 | 4,640 | −13,014 | −9,952 |
| F5 PORT_TILT_532 | +$45,833 | 1,019 | 4,498 | −13,853 | **−8,703** |

Six per-finalist daily P&L vectors are committed alongside it
(`holdout_daily_F1_SOLAR.csv` … `holdout_daily_B1_leg.csv`, `holdout_results.json`).

**The read was properly pre-registered.** I verified the ordering myself rather than
accepting the report's own claim:

```
git log --diff-filter=A -- research/system_master/FINAL_PACKAGE_SPEC.md
  8ff512d  2026-08-08 03:58:02 -0400  ... FINAL_PACKAGE_SPEC FROZEN before the single joint holdout read ...
git log --diff-filter=A -- runs/SM11_HOLDOUT_READ/out/report.md
  0b9825e  2026-08-08 04:00:03 -0400  SM11 THE HOLDOUT READ executed and CONSUMED (45 sessions 2026-06/07) ...
```

Spec committed at 03:58:02, results at 04:00:03. Two minutes apart, correct order. This was
disciplined work, not an accident — and the owner authorised it in advance
(`OWNER_DIRECTIVE_20260808.txt:159-163`: *"If the sealed June/July 2026 block remains
untouched, preserve it until a JOINT FINALIST PACKAGE is frozen; then ONE JOINT READ … Mark
consumed afterward."*). SM11 is the execution of that instruction, and the marking was done.

## The campaign says so in ten more places

`FINAL_PACKAGE_SPEC.md:46-48` ("**HOLDOUT CONSUMED 2026-08-08** … may not inform any future
selection"); `SYSTEM_FRONTIER.yaml:102-103` (`status: consumed`); `NEXT_HANDOFF.md:111`
("June/July 2026 CONSUMED. Dev ≤2026-05-31"); `START_HERE.md:32`; `CLAIM_LEDGER.md:21` ("No
pristine global OOS exists through 2026-07-31" — ledgered as a **fact**);
`KNOWN_ERRORS_AND_CORRECTIONS.md:11-13` (a formal correction entry recording that V1 docs
wrongly called it a holdout); `CURRENT_TRUTH.md:572`; registry **seq 315**; and the scalping
campaign's own `CONTAMINATION_LEDGER.md:61-65` recording that SM11 spent the window for
*all* campaigns.

## Uses beyond SM11

| where | what entered a report | selection-bearing? |
|---|---|---|
| `SM14_ONELOT_DAYMARGIN/out/report.md:22-23` | "+$4.2k MNQ / +$59.5k NQ" for the adopted one-lot product | no — spec pre-declares "characterization only" |
| `SMV2Q_DIAGNOSTICS/REPORT.md:177-188` | June +$20,617, July +$14,380, 53.3% positive days, r120 Sharpe at 2026-07-31 = 1.03 | no — "No tuning, no gate, no selection follows from this read" |
| `SYSTEM_SCORECARD.md:46`, `CURRENT_TRUTH.md:528` | June 2026 +$20.6k promoted into the permanent scorecard | no |
| W17 red team (`red_team/INDEX.md:44-51`) | 45 post-dev sessions, +$34,997.10, $777.71/session | no — a disclosure correcting a silence |
| registry **seq 458** (mine, 2026-08-09) | 2026-01-01→2026-07-31 backtest; Jun-Jul alone +$59,515.04 | no — methodological diagnostic |

I found **no artifact anywhere in which a June/July 2026 number changed a ranking or a
promotion.** That is a real and well-documented distinction, and it means the window is
degraded rather than worthless. But it is a claim about *intent*, and files cannot falsify it:
a reader who has seen +$60,150 cannot un-see it. Which is exactly why the campaign marked the
window spent rather than arguing it was still clean.

---

## A scope correction on `LOCKED_FORWARD.md`, because the repo has been citing it loosely

`research/operational/LOCKED_FORWARD.md:8` says, verbatim:

> `- DATA BOUNDARY: everything through 2026-07-31 is research-consumed (in-sample era). Data from`
> `  2026-08-01 onward is VIRGIN …`

That sentence is true and it does cover June and July 2026. **But `LOCKED_FORWARD.md` is a
campaign-#1/#2 artifact** (declared 2026-08-07, the day campaign #1 closed; it names the R5-E10
champion and campaign-#1 definition files). On its own it establishes only that the window was
**already contaminated before SYSTEM_MASTER started** — not that SYSTEM_MASTER consumed it.
`CONVENTIONS.md:23-28` makes exactly that distinction and makes it correctly: the window was
"clean for B-MOM, B-FADE, B1, and every NEW engine developed on ≤2026-05-31 data".

**SM11 is what converted "already dirty from campaign #1" into "consumed by SYSTEM_MASTER
too", including for B-MOM and B1** — SM11 read F3 BMOM and the B1 leg directly. So the verdict
rests on SM11, not on LOCKED_FORWARD.md, and any future citation of LOCKED_FORWARD.md as
authority for SYSTEM_MASTER's own consumption is a category error.

**A related misattribution, logged not fixed:**
`runs/W17_C4_COMPLIANCE/src/v1f_eventdays.py:49` reads
`DEV_END = pd.Timestamp("2026-05-29")   # dev window per LOCKED_FORWARD.md`.
`LOCKED_FORWARD.md` contains no dev-window definition and never mentions 2026-05-29. The
authority is `CONVENTIONS.md:12`. The *value* is harmless (2026-05-29 is the last session
≤ the stated 2026-05-31 boundary); the *provenance claim* is false.

---

## Two record defects found while answering this, reported rather than tidied

**1. The dev boundary is written two ways across the record.** `CONVENTIONS.md:12` says
**2026-05-31**; `src/analytics/primary_objective.py:64` and `v1f_eventdays.py:49` say
**2026-05-29**; most SM/SMV2 analysis code says 2026-05-31. In practice these are the same
window because 2026-05-29 (Friday) is the last session ≤ 2026-05-31 — but there is no single
canonical constant and the record is not self-consistent. Filed as a standing caution.

**2. A figure in `CURRENT_TRUTH.md` §8b has no provenance in this repo, and it may indicate a
locked-forward read.** §8b (written by me yesterday, Wave 17) states:

> *"the $2,575 gap between the owner's $78,024.60 and a from-scratch reproduction of
> $75,449.60 on the nominally identical 2026-01-01→2026-08-07 window."*

A repo-wide search for `75,449` / `75449` / `78,024` / `78024` returns **no committed
artifact** — no run directory, no spec, no registry row has a `to` date of 2026-08-07. The
$78,024.60 is the owner's own Strategy Analyzer number, supplied conversationally, and is not a
repo read. The **$75,449.60 has no traceable source**. Two possibilities, and I cannot
discriminate them from the record:

- (a) a backtest was run to 2026-08-07 and never committed — which would be a **read into the
  locked-forward window** (`LOCKED_FORWARD.md:8-11` permits reads of ≥2026-08-01 only via
  MONITOR-01 or a pre-registered annual frozen-champion evaluation, and this was neither); or
- (b) the figure was recorded in error.

**Actions taken, in the only order C7 allows:** the figure is NOT deleted. It is flagged here
and in a dated correction appended to `CURRENT_TRUTH.md`. The "$2,575 gap" is downgraded from
UNEXPLAINED to **UNVERIFIED — DO NOT CITE**, and it is removed from the open-questions list as
a research item, because chasing a number with no provenance is not research. A precautionary
entry is written to the access ledger below. Note that registry seq 458 itself stops at
2026-07-31 and explicitly labels the Aug 1-7 residual as "LOCKED-FORWARD virgin, not used for
anything here" — so the *registry* row is clean; the defect is confined to the CURRENT_TRUTH
prose.

---

## What this means for the program

1. **V7 §E-2 is inapplicable.** There is no unconsumed quasi-holdout to protect. Nothing is
   sealed here, because there is nothing left to seal.
2. **V6 §4's ranking of evidence substitutes is confirmed, not weakened.** With no clean
   historical OOS available anywhere, cross-instrument replication within the same era really
   is the strongest substitute this program has — which is what `runs/W18R2_M5_XINST` exercises
   in this same wave.
3. **The only genuinely clean data is ≥2026-08-01, and it is nine days old.** Per
   `LOCKED_FORWARD.md:9-14` it may be consumed only by (a) quarterly MONITOR-01 readings —
   reading #2 due on/after **2026-11-01** — or (b) a pre-registered annual frozen-champion
   evaluation due on/after **2027-08-01**. It accrues at one quarter per quarter and no amount
   of research effort speeds that up.
4. **C1 is not violated by any of this.** Nothing above proposes a plan that depends on data
   that does not yet exist. It is a statement about what already exists and what its status is.

---

## LOCKED-FORWARD ACCESS LEDGER (opened 2026-08-09)

Every read of data ≥2026-08-01 is recorded here with date, reason and who authorised it.
This ledger exists because V7 §E-2 asked for one for a window that turns out not to need it;
the ledger is redirected to the window that **does** — the only virgin data this program has.

| date | window read | reason | authority | status |
|---|---|---|---|---|
| 2026-08-09 | 2026-01-01 → 2026-08-07 (**suspected**, see record defect 2 above) | unknown; possibly a from-scratch reproduction during Wave 17 | **none identified** | ⚠ UNRESOLVED — logged precautionarily; the figure it produced is marked DO-NOT-CITE and has been used for nothing |

No other access to ≥2026-08-01 is known. Wave 18 read nothing at or after 2026-08-01 on any
instrument: `runs/W18_XINST_BARS` exports stop at 2026-05-29 by spec, and both Track-R runs
slice to `sess_date <= 2026-05-29`.
