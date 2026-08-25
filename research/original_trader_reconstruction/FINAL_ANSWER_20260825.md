# FINAL ANSWER — 2026-08-25

Three questions: how good is the reconstruction, which ninZa components did he plausibly combine,
and what (if anything) should be bought. Written **after** an eight-skeptic adversarial audit that
returned **0 CONFIRMED / 2 REFUTED / 6 WEAKER_THAN_STATED**, and against the audited claims.

---

## 1. HOW GOOD IS THE RECONSTRUCTION

Scored on the campaign's own standard — **trade-level reproduction, not summary-statistic
similarity** — by three independent agents, one per era. No blended percentage; the campaign
forbids that, and the blend would hide the shape.

| axis | 2023 | 2025 | 2026 |
|---|---|---|---|
| component identity | 60 | 38 | 32 |
| parameter identity | 58 | 45 | 33 |
| **signal generation** | **70** | 20 | **18** |
| **entry rule** | 55 | **15** | **16** |
| **exit rule** | 72 | 18 | **12** |
| risk / stop | 30 | 55 | 55 |
| time / session | 70 | 42 | 24 |
| **long-short asymmetry** | 25 | **12** | **10** |
| position sizing | 85 | 75 | 45 |
| version chronology | 40 | 72 | 46 |

**The honest one-line summary: one era is reconstructed at trade level over 11 days; the other two
are not reconstructed at all.**

### 2023 — the real result, and its real size
A path reproducing **all 88 constrained cells** of the eleven-day table, cent- and tick-exact,
survived independent adversarial re-execution. The constraint system also *rejects* wrong models:
INCLUSIVE exit, session-date grouping, and any stop ≤ 110 pts all return **zero** paths. That is
genuine trade-level reproduction.

Four things bound it:
- **It is two paths, not one.** `r22_log.txt`: *"global 11-day paths = 2"*. Only one was
  serialized. "Unique" was my error and is withdrawn.
- **It covers 89 trades over 11 days — about 2 % of the 4,351-trade window he reports.**
- **There is nothing to run.** The path is a constraint-solver output, not a program: 16 of its
  105 decisions are declines produced *by choice*, not by a rule.
- The executable object we do own (CAND2 + D-gate) over his master window gives **4,598 trades
  against his 4,351 (+5.7 %)** and **$264,955 against his $292,172.82 (−9.3 %)**.

### 2025 — well observed, well dated, not reconstructed
The 2023 mechanism is **falsified at cent level** for an ordinary 15-trade day. The entry universe
is proven wrong and no replacement is proven right. The seductive part: every *shape* statistic
passes — win rate within −1.2 pp, hold within −1.3 min, long/short share within 2 pp, long-side
largest loss capping at exactly −$1,300 as his does — **and the money is a different security.**

### 2026 — well documented, poorly reconstructed
Every axis above 40 rests on direct observation or an arithmetic invariant (the exactly-repeating
−$2,600 with correctly-ordered gap overshoot; the $5 tick lattice; scrollbar geometry with
propagated σ; a scale-free 2× commission ratio). Every axis below 20 rests on fitting a Python
clean-room to ~16 weekly aggregate cells. **There is no trade-level test available for this era at
all** — no `Signal_Trade` timestamp, no per-day 2026 table exists in the fixed corpus.

Run the best 2026 configuration forward and the weekly sheet diverges on nearly every line, in
directions already measured: **trade count 10–25 % high, win rate 4–13 points low, payoff ~2.4
against his ~1.8** — more trades, winning less often, wrong size distribution in both directions.

---

## 2. WHICH ninZa COMPONENTS HE PLAUSIBLY COMBINED

**The frame that makes this answerable.** NinjaTrader never surfaces an internally-instantiated
indicator's properties in a strategy's grid, so *every* row in his panel is his own re-declaration
**by construction**. The absence of a vendor property grid is therefore **uninformative** and is
never used below as evidence against use. The vendor's own documented workflow — *"you can rely on
the signals below to build your own strategy"*, with per-product Strategy Builder tutorials — makes
"consume `Signal_*` inside a private wrapper" the **expected** architecture, leaving exactly the
trace observed and no other.

| product | level | verdict |
|---|---|---|
| **Solar Wave RK** | **B (strong)** | Solar-family geometry in the 2023–2025 build — the best-supported component claim in the campaign |
| **"Solar Wind" (a distinct product)** | **A on the name string** | **NEW — see below** |
| **VWAP Flux** | **B (top of B)** | 13/13 parameter surface by concept + order + verbatim enum; the computing engine is UNKNOWN, 5 live hypotheses |
| Super JumpBoo$t | B (weak), genuinely OPEN | best non-VF motif; but matches the **wrong preset for his bar type**, and its falsifier is untestable |
| Cosmik Z-TP | C | architectural similarity only; both numeric mappings that once supported it are dead |
| Multi-Osc OB/OS | NONE | panel reading falsified twice; **use not excluded**, zero positive evidence |
| King Kong Trading RK | void | a 4-product bundle with no script and no panel — the question is malformed for this SKU |
| ThunderZilla | NONE | survives only because no property list was ever published — that is not evidence |
| ApexFlow Zignal | ~NONE | downgraded; only vendor *marketing* pairs it with VF |
| Cumulative / Volume Delta | NONE→C | VF's own `Signal_Cum_Delta` supplies delta without a second product |
| Infinity Algo Engine$ | excluded | 19 rows vs ~497, and its manual has **no Strategy Analyzer path at all** |
| Captain Optimus Strong | excluded | ~43 rows; v2 postdates the growth curve; four structural contradictions on time encoding |

### The new finding: "Solar Wind" is a real, distinct vendor product

His strategy class is named **`SolarWindRKSelTime`** — a pixel-read FACT across ≥4 frames. The
campaign had always read "SolarWind" as his own coinage. It is not: **"Solar Wind" is a real
vendor-named signal-generating indicator in this ecosystem**, distinct from Solar Wave RK, and it
appears in a published package described as combining *"the Solar Wind as a signal generator and MA
Crossover as a trend identifier."*

So his class name is **a verbatim vendor product name + the RenkoKings brand suffix `RK` + his own
token `SelTime`**. Under §43 that is **the only direct product-name string in the entire corpus** —
and the campaign had it buried in one file and never exploited it.

It does **not** identify a component: a name in *his* class does not prove he instantiated the
vendor's type, and the parameter ladder (90/179, the 2× relation) is documented **Solar Wave**
shape, not Solar Wind's. But it is the strongest name-level evidence we have and it deserves the
next free investigation.

### Probability, stated plainly
**~4 in 5** that Solar-Wave-family geometry is present in the 2023–2025 build. Whether the
computation is the licensed indicator or his own re-implementation of the same geometry is
**genuinely open — roughly even odds — and no evidence in the fixed corpus can decide it.**

---

## 3. WHAT TO BUY — **BUY VWAP FLUX (~$300). Nothing else.**

Reversing `PURCHASE_GATE_v2`'s "UNNECESSARY". Two of its four findings fail audit.

**The load-bearing error.** `PURCHASE_GATE_v2` finding 1 says vendor geometry is worth 2.9 % of
reconstruction distance. But `run_r26_geometry_evi.py` takes the **minimum over all 144 members**
within each geometry — so it **marginalised out four other vendor axes (T, P, C, H) and reported
the residue as the value of the whole vendor oracle.** That is a conditioning error, and it is the
main pillar of the anti-buy case.

**What the axes are actually worth, from our own numbers:**

| axis | owner | measured movement in §40 distance |
|---|---|---|
| cloud geometry (lifecycle × rail formula) | vendor | 0.023 |
| trailing-exit family, entry frozen | **author** | **worse than baseline** in every variant |
| **Layer-A trigger (`P_MED→P_IN`, `C_DIR→C_REC`)** | **vendor** | **0.4768 → 0.4368 fit; 0.4546 → 0.3503 holdout** |

`vf_layer_ab.py` settles ownership beyond argument: `layer_a()` — *"Pure indicator… knows nothing
about positions"* — takes `P`, `C`, `H`. `layer_b()`, the author's wrapper, takes only `X` and
`stop`. **`P_IN` and `C_REC` are vendor semantics.** The single largest fit-and-holdout improvement
of the entire 2026 programme sits on a **vendor** axis.

**And here is why free research can never close it.** §5 forbids identifying a vendor component
from numeric coincidence. So **no backtest, ever, can resolve `P`, `C`, `H` or `T`.** R32's
`P_IN|C_REC` is the best configuration on both samples *and we are forbidden to conclude the vendor
uses it*. That axis is **permanently closed to free research and permanently open to a $300 direct
observation.** Direct product output is LEVEL A evidence; a fit ranking is not evidence at all.

**What $300 resolves:** the exact Layer-A trigger geometry, Fair Value, the five rails,
`Signal_Trend`, `Signal_Trade`, `Signal_Cum_Delta` — i.e. the entry side, which `RESUME_HERE`
already names as the one open question.

**What it does NOT resolve, and this limit is real:** there is no 2026 per-day MAE/MFE table
anywhere in the corpus, so exact path reconstruction stays impossible. His wrapper — the
suppression layer, the exits, the long/short asymmetry — is untouched. Expect the entry axis to
collapse and the wrapper to remain open.

**Buy nothing else.** Every other product is excluded, void, unfalsifiable, or supported only by
conceptual similarity.

---

## 4. AFTER 2026-08-14 — there is no evidence, and none obtainable

The corpus's last dated record is **OTRIMG-0164, window 8/2 → 8/14/2026**. All 164 images were
exported 2026-08-24. `LOCKED_FORWARD` seals 2026-08-01 onward for selection in any case.

**There is zero evidence of any kind about what he ran after 2026-08-14** — not weak evidence, none.
Any claim about his post-corpus system would be invention.
