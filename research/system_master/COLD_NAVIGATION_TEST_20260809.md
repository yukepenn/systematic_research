# COLD_NAVIGATION_TEST — 2026-08-09

A fresh, read-only agent with zero prior context on this repo was given exactly 5 files —
`README.md`, `MAP.md`, `research/system_master/START_HERE.md`, `BASELINE_MODELS.md`,
`FINAL_OWNER_DECISION_20260809.md` — and instructed to open nothing else, then answer 10
pre-specified questions about the current state of the program.

## Result: PASS — all 10 questions answered unambiguously, with correct citations

| # | question | answered cleanly? |
|---:|---|---|
| 1 | Exact class names / file paths for the 3 baselines | yes |
| 2 | Product A's exact position-sizing formula | yes |
| 3 | BEST_ONE_NQ's entry/exit rule (exact levels) | yes |
| 4 | B-NQ vs B-MNQ parameter equality — same/different, defect? | yes |
| 5 | Product A max contracts + traded instrument | yes |
| 6 | NT8 parity certification status | yes |
| 7 | BEST_ONE_MNQ per-contract initial margin | yes |
| 8 | Live-trading authorization status | yes |
| 9 | Did the latest wave adopt any improvement? | yes |
| 10 | Single highest-priority next step | yes |

No factual contradiction was found across the 5 files on any question. Full agent transcript
(verbatim Q&A + verdict) is preserved in this session's record; the essential facts are captured
in the table above and the caveat below.

## The one real, disclosed risk the test surfaced (not a gap — a navigation hazard)

The agent's own verdict, verbatim: the 5-file set works, but **only because a reader has to
actually read and respect the redirect banners** on the two older files (`README.md` is entirely
about the different, closed Solar Wave campaign and only works because its top banner points to
`MAP.md`; `START_HERE.md` is one wave stale and only works because its top banner points to
`BASELINE_MODELS.md`). A reader who skimmed past those banners and read the older files' *body*
text in isolation could form a wrong picture (e.g. treating Solar Wave's closed-campaign
priorities as SYSTEM_MASTER's, or treating `START_HERE.md`'s "A-dominant CHALLENGER" framing as
still live when it was later rejected). This is the established repo convention (banners,
additive, never rewriting old content — see `MAP.md`'s own 2026-08-09 housekeeping note) and is
judged an acceptable, disclosed trade-off rather than a defect to fix this wave: rewriting
`START_HERE.md`'s body would itself violate the "never silently rewrite historical text" norm
this campaign has followed throughout (C7-equivalent discipline, same as every red-team
ingestion this wave). Future readers are the intended audience for this note.

## Disposition

Cleanup is judged sufficient to close the consolidation phase. No further file-level action
taken as a result of this test.
