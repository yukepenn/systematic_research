# research_sdk

Reusable infrastructure for the systematic_research campaign. Not alpha code — this
package produces zero trading signal. Everything here is `ENGINEERING_ONLY` /
`ZERO_ALPHA_BUDGET` per the run-classification taxonomy below.

## prereg_guard.py

Enforces "spec commit before result commit" (post-structural-invariance master
directive sec6-7, sec170), a rule adopted after HASH01's git-forensic audit found
~44 run directories in this campaign with spec and results landed in the same
commit (`research/registry/REGISTRY_GAP_NOTE.md`) — meaning independent blindness
couldn't be verified from git history alone for that work.

**Prospective use** (call before an alpha run starts):

```
python research_sdk/prereg_guard.py check \
    --run-class BOUNDED_SELECTION \
    --spec-commit <sha-of-the-commit-that-added-only-the-spec> \
    --spec research/.../my_spec.md \
    --result research/.../out/results.json research/.../out/results.csv
```

Exit 0 = the spec is committed, unmodified on disk, HEAD descends from it, and none
of the declared result files exist yet — the run may proceed. Exit 1 = refuse.
`--run-class ENGINEERING_ONLY` or `ZERO_ALPHA_BUDGET` bypasses the gate entirely
(infrastructure work carries no selection risk).

**Audit use** (retrospective, git-forensic, no live filesystem dependency — works
on old commits regardless of current working-tree state):

```
python research_sdk/prereg_guard.py audit \
    --spec-commit <sha> --spec path/to/spec.md \
    --result out/results.json --result-commit <sha-or-HEAD>
```

Answers one question per result path: was it absent from the repo tree at
`spec_commit`? If it was already present, that's a same-commit (or spec-after-result)
violation — this is the same finding REGISTRY_GAP_NOTE.md documented by hand for one
family; audit mode makes it mechanical so the whole registry can be rescanned later
without repeating manual archaeology.

Run `python research_sdk/prereg_guard.py selftest` to see both modes exercised
against two real commits from this campaign's own history: a clean pass
(SIMPLE01 completion pass, `6ffe82d` → `e5e03bf`) and a known same-commit violation
(AUCTION04, `fcaae6c`).

## Run classes

`ENGINEERING_ONLY`, `AUDIT`, `DIAGNOSTIC`, `EXPLORATORY_DISCOVERY`,
`BOUNDED_SELECTION`, `PROTECTED_CONFIRMATION`, `LOCKED_FORWARD_MONITOR`,
`PROMOTION_CERTIFICATION` (directive sec8). Declare one per run; do not label
exploratory work as confirmation.
