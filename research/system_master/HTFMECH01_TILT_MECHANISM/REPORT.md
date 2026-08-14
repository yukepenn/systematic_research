# HTFMECH01 — HTF marginal-contribution mechanism decomposition: REAL, LONG/SHORT-CONCENTRATED FINDING

**Diagnostic only, per SPEC.md (committed `594bbc4` before this ran). Zero construction, zero
promotion, no incumbent file touched.** Both gates passed: gate #1 (grid_core's own certified
dev-window self-check) and gate #2 (this script's own canonical-window net cross-check against
`grid_core.product_a_exec`/`product_b_exec`, to $0.01). Whole-window totals reproduce PLACEBO01's
own reported figures exactly: real marginal net $5,966.50 (A) / $9,148.16 (B), matching PLACEBO01's
disclosed $5,967 / $9,148 to the dollar — same computation, same inputs, independently re-derived.

## Headline: not uniform. Concentrated by direction, not by year.

**Year decomposition** — HTF's marginal contribution is mixed, not uniformly weak:

| Year | Sessions | Marginal net A | Marginal net B |
|---|---:|---:|---:|
| 2023 | 258 | +$4,864.70 | **−$5,429.64** |
| 2024 | 259 | +$3,847.00 | **+$13,769.60** |
| 2025 (22-session stub) | 22 | −$2,745.20 | +$808.20 |

No single bad year explains the whole-window shortfall — 2024 was strongly positive for Product B.
This decomposition alone would not have flagged HTF as concerning.

**Side decomposition** (by `sign(T_bar)`, the Solar consensus direction at each bar) — this is
where the real story is:

| Side | Bars | Marginal net A | Marginal net B |
|---|---:|---:|---:|
| Long | 99,556 | **+$11,914.30** | **+$15,100.74** |
| Short | 98,431 | **−$22,019.55** | **−$2,822.32** |
| Flat (position carried from an earlier regime) | 47,956 | +$16,071.75 | −$3,130.26 |

**HTF's up-weight mechanism is strongly value-additive on the long side and value-destructive on
the short side — most starkly for Product A, where the short-side cost (−$22,019.55) is over 3.5×
the whole-window net positive contribution ($5,966.50).** The long-side and carried-position gains
are large enough to keep the aggregate positive, which is exactly why the whole-window number alone
(what PLACEBO01 reported, correctly, as its own scope) didn't surface this.

## Why this matters, and what it does and doesn't imply

This is genuinely corroborated by independent evidence already in this campaign, not a new isolated
claim: `SA0_SYSTEM_STRUCTURE/REPORT.md` found shorts structurally weaker than longs (Sharpe 0.18 vs
1.54, 9.7× higher tail concentration) and `PA0_PRODUCT_A_STRUCTURE` found the same asymmetry
(shorts Sharpe 0.40 vs 1.38). **HTF's blanket, direction-agnostic up-weighting mechanism appears to
be amplifying an already-known structural weakness on the short side**, not introducing a new one —
three independently-designed diagnostics (SA0, PA0/PA1, and now this one) now agree shorts are the
weaker leg, and this is the first to show HTF's specific mechanism concentrates its own weakness
there too.

**What this does NOT do**: does not prove a side-conditioned HTF variant would work (no
significance test was run per slice — only descriptive dollar decomposition, per SPEC.md's own
disclosed scope boundary; no out-of-sample or chronology-robustness check on this specific split;
no cost/turnover impact of a hypothetical change was measured). Does not authorize building,
testing, or promoting a long-only-HTF construction here — that would need its own preregistration,
full battery (chronology, tail-risk, right-tail-safety, NT8-executable proof), exactly like every
other candidate this campaign has ever required, and is explicitly out of scope for this task (see
SPEC.md). Does not touch `B1`, ACTIONMAP01, U6B, or any DOM/Replay data.

## What this adds to STRUCTURAL_INVARIANCE_MINIMUM_SYSTEM_SYNTHESIS.md's own framing

That synthesis called HTF "the natural target for any future, better-powered structural test."
This sharpens the target: **not "is HTF weak" (already answered) but "HTF's specific failure mode
is direction-conditional, and lines up with this system's already-documented short-side weakness."**
The natural next-next step — NOT undertaken here — would be a separately preregistered construction
test of a direction-conditioned HTF multiplier (e.g., up-weight only on agreement-with-long, neutral
or reduced on agreement-with-short), run through the same full gate battery every other candidate in
this campaign has had to clear. Recorded here as a sharpened, well-evidenced lead for that future
task, not acted on.

## Artifacts

`src/01_htf_mechanism_decomposition.py` → `out/htfmech01_year_decomposition.csv`,
`out/htfmech01_side_decomposition.csv`, `out/htfmech01_results.json`. Reuses
`research/system_master/PLACEBO01_COMPONENT_CAUSALITY/src/02_htf_placebo.py`'s `solve_A`/`solve_B`
verbatim (copied, not modified) and `GRID01_SOLAR_RESOLUTION_CONVERGENCE/src/grid_core.py`'s
certified substrate unmodified.
