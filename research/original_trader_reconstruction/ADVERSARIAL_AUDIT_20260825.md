# ADVERSARIAL AUDIT — 2026-08-25

Eight independent skeptics were run against the eight load-bearing claims surviving at the end of
the v5.0 / R31 / R32 work, each instructed to **try to refute**, with access to the repo and to the
vendor documents. Seven have reported.

**Result: 0 CONFIRMED. 2 REFUTED. 6 WEAKER_THAN_STATED.** Every one of the eight claims audited was
overstated in at least one respect, and several errors were mine from *this session*. Recorded here
in full; nothing below is softened.

---

## C1 — "VF13 rows are his own re-declarations" · **WEAKER_THAN_STATED, LEVEL B (I claimed A)**

**The conclusion survives. The stated basis largely does not — only 1 of my 4 "independent
differences" holds as written.**

**A FALSE VENDOR FACT, and it was load-bearing.** `VENDOR_FORENSICS_v2.md` §1 asserts
*"`Volume Base` (FIRST) vs `Volume Base` (LAST, after `Zone Period`) — order differs"*. The manual
shows the **opposite**: Volume Base is the **first** row of the vendor's `Parameters` group, and
`Zone Period` sits in a separate `General` group. The repo's own
`VENDOR_PROPERTY_FINGERPRINTS.csv` independently records the vendor order with Volume Base first.

**That is a MATCH, not a difference**, and I published it as a difference. I took it from a
subagent's report and did not check it against an artifact already committed in this repo.

What still holds: the `Percent` vs `(%)` label difference, and — decisively and independently of
any label — the **architectural** argument that NinjaTrader never surfaces an internally
instantiated indicator's properties in a strategy's grid. The conclusion is right. The evidence is
LEVEL B, not LEVEL A.

## C2 — "q=1 forced on four records, so 130 points" · **REFUTED**

**A non sequitur, and it violates my own preregistered constraint.**

In all three bucket-A records (0121, 0129, 0146) the odd-$5 cell is **`largest_win_all` — never the
−$2,600 cell.** In **all 18** −$2,600 occurrences the loss cell is 520 units of $5, i.e. **EVEN**,
and therefore parity-unconstrained. Getting from *"the largest WINNER had odd quantity"* to
*"the −$2,600 LOSER had quantity 1"* requires assuming **uniform quantity within a record** — which
`spec.yaml part_a.forbidden` bans in as many words:

> *"Do not assume uniform quantity across trades within a record... Only single-trade cells
> constrain a single trade's quantity."*

I wrote that constraint and then broke it two sections later.

**The count is also wrong.** Bucket A = **3**, not 4. OTRIMG-0113 is the fourth odd-cell record and
its largest loss is −$1,365 — it is the *only* record where parity constrains a **losing** trade,
and it is the only one of the four with no −$2,600 at all. My "4 forced + 15 other" gives 19
against the artifact's 18.

**So no −$2,600 trade is constrained by parity anywhere in the corpus.**

What survives: *conditional on the incumbent entry path* (which the same run calls suspect, and
which R32 shows is beaten), stops of 32.5 / 26 / 13 / 10 points fit materially worse than 130 or
65 — and **130 vs 65 differ by 0.0234, with 65 fitting hold better.**

**Consequence for the stop.** "130 points, settled" loses its arithmetic leg entirely. What remains
is **AS-9** ("generally traded one contract") + **AS-2** (Strategy Analyzer = per-strategy) — real
Class A testimony, but testimony, and "generally" is not "always". Correct status:
**130 points is supported by author testimony, not by arithmetic; 65 × 2 is not excluded.**

## C3 — "a UNIQUE 89-trade path" · **WEAKER_THAN_STATED**

**Core result CONFIRMED and independently reproduced**: all 88 constrained cells across 11 days
reproduce cent- and tick-exact. (The auditor's one apparent mismatch was their own banker's-rounding
bug; NT8 uses `MidpointRounding.AwayFromZero`.)

**But "UNIQUE" is refuted by its own source.** `runs/OTR_R11_INVERSE/out/r22_log.txt` line 5:
`exit=STRICT: global 11-day paths = 2`. **There are two.** `GLOBAL_PATH_JAN2023.md` says so
explicitly and honestly — and the word "unique" was nevertheless propagated into `RESUME_HERE.md`,
**by me, in this session**, and into the campaign memory. Only one of the two paths was serialized.

Correct statement: **two global solutions, of which one is serialized.**

## C4 — "corr(ATR, avg_loss) is robust out of sample" · **WEAKER_THAN_STATED, LEVEL C**

**The single worst methodological error of the session.**

The 17-window and 23-window samples are **nested** — the 23 *contains* the 17. Only **6 windows are
genuinely new**. On those six alone:

| | 6 genuinely new windows |
|---|---|
| corr(ATR, avg_loss) — the claim I **KEPT** | **−0.114**, p = 0.83 |
| corr(max_run, payoff) — the claim I **WITHDREW** | **+0.109** |

**They are indistinguishable out of sample.** I withdrew one for "collapsing" and retained the
other as "robust", on the same six windows, applying the standard asymmetrically. "Robust out of
sample" is withdrawn; the honest statement is that the pooled correlation is a real feature of the
pooled data and has **no out-of-sample support**.

## C5 — "avg_loss/stop = 0.365 vs 7–21 %, scale-invariant" · **REFUTED**

- **"Scale-invariant" is false as used.** Under a 65-point stop our families move to 0.137–0.369,
  and the incumbent lands at **0.369 — above his 0.365.** The invariance holds for *his* side only,
  not for the comparison, which is the whole content of the claim.
- **"Every configuration we have"** meant nine exit families on **one** of the 288 entries the same
  run scanned. That run's own leading entry (`P_IN|C_REC`) reaches **0.339** — essentially his
  0.365.

The gap I described as a durable structural constraint is largely an artifact of comparing against
a single entry configuration.

## C6 — "fade is tested and disfavoured" · **WEAKER_THAN_STATED**

All four numbers reproduce, and the premise (fade was genuinely unrepresentable in the 144-member
grid) is correct and independently checkable.

**But the fade arm was never given a fade-appropriate exit.** `layer_b_exit` was inherited verbatim
from R30, where it was written for momentum entries. It contains **no take-profit at Fair Value** —
the one exit a value-fading architecture actually needs. Worse, **three of its eight exit families
fire on the entry bar for a fade**: `X_FV` exits a long when `close < FV`, but a fade long is
entered at the *lower rail*, already below FV.

**So "fade is disfavoured" is not sound.** Fade was tested with exits that are structurally void
for it. This is a design flaw I introduced by reusing machinery without re-checking its
assumptions — the specific risk the "don't reinvent the wheel" instruction carries.

## C7 — "13 of ~497 August rows (2.6 %) have labels" · **WEAKER_THAN_STATED**

The arithmetic reproduces exactly and the ledger is internally consistent (63 rows). But the
13 / 63 / 421 split **pools observations from Jan-2026 through Aug-2026 and attributes them all to
the August panel** — 61 of the 63 value-only slots are Feb/Apr/Jun-only.

My own report's §3 already gives the August-specific figure and it differs:
**~15 of ~497, about 3 %.** I quoted the pooled number as the August number. **A base-mixing error
of exactly the kind I had corrected twice earlier in the same session.**

## C8 — "all five motifs contradicted" · **WEAKER_THAN_STATED**

Refuted by the cited artifact's **own** §8 table: one motif is the campaign's **leading vendor
candidate** (Super JumpBoo$t, `30|70|2|20` matching values 4/4 + order + control types +
group-terminal position), and one is an **identified NinjaTrader platform group**.

Defensible: **three of five** contradicted against published ninZa Parameters lists; one is a
strong open candidate; one is platform boilerplate. Also, "structurally impossible" for Multi-Osc
is an overstated modal — it holds for the *documented Parameters section*, which the manuals
themselves say is not the complete property grid.

Confirmed at LEVEL A on the vendor side: Multi-Osc's 16-row order with dropdowns between every
threshold pair, and ApexFlow's 14 documented parameters.

---

## What this audit changes

**Downgraded:** C1 to LEVEL B; C4 to "pooled feature, no out-of-sample support"; C7 to ~3 %
August-specific; C8 to three of five.
**Withdrawn:** C5 (scale-invariance), C3's "unique", C6's "disfavoured" verdict pending a
fade-appropriate exit.

**The pattern across all seven is one failure mode, not seven**: a correct measurement, described
with a stronger word than the measurement supports — "unique", "robust", "scale-invariant",
"every", "all five", "LEVEL A". The arithmetic was right nearly everywhere. The **quantifiers**
were wrong nearly everywhere.

**Standing rule added:** before any claim leaves a run report, the quantifier in it
(*unique / robust / all / every / invariant / proven*) must be checked against the artifact that
would falsify it — and for out-of-sample claims, the samples must be checked for **nesting**.
