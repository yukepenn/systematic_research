# CORRECTION NOTE — `MSBBO_V1`, 2026-08-28

Two defects were found in this run **after** its result was committed. Both are recorded here rather
than edited away, because the point of a prereg→result chronology is that it cannot be tidied.

| | |
|---|---|
| **1D — feature count "18" vs 20** | **CLERICAL COUNTING DEFECT. The freeze is VALID.** |
| **1E — L2 "sub-minute half-life"** | **OVERCLAIM. Retracted and replaced with the supported statement.** |
| **neither** | changes any number, any gate, any model, or the candidate's evidence class |

---

## 1D. The 18-vs-20 discrepancy is a prose typo, and the proof is a hash, not an argument

`SPEC.md` §4 is headed **"Feature budget — 18, fixed"**, while its own enumeration in the same
section sums to **20**, and both the runner and `MS_BBO_CANDIDATE_1_FROZEN.json` carry **20**.

The directive's test is the right one and it is decisive: *were all 20 exact features already present
in the **pre-result committed runner**?*

```
git diff 8467526 1a188e0 -- runs/MSBBO_V1_20260828/src/bbo_v1.py
    -> EMPTY.  The alpha-defining runner did not change between prereg and result.

sha256  src/bbo_v1.py    36dee22cdb001f0a36f6f7de112e97d3590f0be8eb9b6338d8d33383bb65dc6d
sha256  SPEC.md          3034c61a7dcb645316d406558829165884486c3655f77103316bedffc9e83438
    -> IDENTICAL at the prereg commit 8467526, at the result commit 1a188e0, and in the worktree.
```

The only files added between the two commits are `REPORT.md`, the frozen manifest, the two
`leak_audit*.py` probes and their outputs. **No alpha-defining file was touched after results were
visible.**

**The exact 20, mechanically enumerated from the source at the prereg commit:**

| # | | # | | # | | # | |
|---:|---|---:|---|---:|---|---:|---|
| 1 | `spread_tk` | 6 | `rvol_30s` | 11 | `spread_pctile` | 16 | `ask_up_30s` |
| 2 | `midret_1s` | 7 | `range_30s` | 12 | `bid_upd_30s` | 17 | `trade_buckets_30s` |
| 3 | `midret_5s` | 8 | `dist_hi_30s` | 13 | `ask_upd_30s` | 18 | `trade_vol_30s` |
| 4 | `midret_15s` | 9 | `dist_lo_30s` | 14 | `bid_up_30s` | 19 | `signed_flow_30s` |
| 5 | `midret_30s` | 10 | `spread_chg_30s` | 15 | — | 20 | `tod` |

Against `SPEC.md` §4's own prose enumeration: **F1 = 8** (4 mid returns · rvol · range · 2 distances)
· **F2 = 4** (spread · change · min-fraction · percentile) · **F3 = 4** (2 update counts · 2 up-move
counts) · **F4 = 3** (buckets · volume · signed flow) · **TOD = 1**. **8+4+4+3+1 = 20.**

> ### Verdict: the header integer is wrong; the **enumeration** and the **committed runner** agree
> ### exactly and are authoritative. This is a clerical count, not a post-hoc feature addition.
> `SPEC.md` is **not** rewritten — a spec's value is that it is the artifact that existed before the
> result, and silently correcting its arithmetic would destroy exactly the property being relied on.

**One honest caveat on how this was nearly missed.** My first mechanical enumeration returned **19**,
because the regex matched `F["name"] = ...` assignments and missed `F = {"spread_tk": ...}`, the
dict-literal initialisation. A count derived from a pattern is only as good as the pattern. The
figure above is reconciled three ways — source, SPEC prose, frozen manifest — and all three give 20.

## 1D-b. A separate, smaller defect found while checking this: `out/bbo_v1.txt` is 0 bytes

`bbo_v1.py` opens its log handle at module scope and `main()` never closes it, so the primary run's
console log was **never flushed to disk**. The numbers in `REPORT.md` came from stdout, and
`out/bbo_v1_sessions.csv` (the per-session P&L) *did* persist, as did both leak-audit logs — those
scripts close their handles.

**This is an evidence-completeness gap, not an evidence-integrity failure**, and it is recorded
rather than repaired in place: fixing `bbo_v1.py` would change the sha256 that the frozen candidate
manifest commits to. The deployment-freeze run reproduces the discovery figure from the unmodified
module and logs it properly, which closes the gap without touching the frozen object.

## 1E. Retracting "sub-minute half-life"

`REPORT.md` §4 asserted **"The signal has a sub-minute half-life (L2)"**. That is not supported by
L2. What L2 measured is a single fact: moving every feature back one 60-second step takes the result
from **+$5,125/session to −$1,490/session**.

| claimed | supported |
|---|---|
| ~~"fast-decaying real alpha"~~ | the candidate is **highly local in time** |
| ~~"signal half-life < 60 seconds"~~ | the **specific stale-BBO reconstruction hypothesis was tested and REJECTED** (quote ages median 24 ms, \|bid age − ask age\| median 0 ms, edge survives freshness filtering at $5,175.60/session) |
| ~~a decay curve was estimated~~ | **simple price momentum does not explain the result** (L3: dropping every mid-return feature costs $5,125 → $4,873) |
| | ⚠️ **the lag-sign-reversal mechanism remains UNKNOWN** |

A half-life is a **parameter of a decay model**. No decay model was fitted; one lag was tried, and it
did not merely decay to zero — it **inverted sign**, which a simple exponential decay does not
predict. "Consistent with" was written up as "established," which is the exact move this project
forbids elsewhere.

**Consequence, and it is deliberately restrictive:** no further historical mechanism mining around
L2. Per the standing rule, mechanism research on the 48 consumed sessions is **deferred until
prospective support exists** — otherwise the explanation would be fitted to the same data that
produced the thing being explained.
