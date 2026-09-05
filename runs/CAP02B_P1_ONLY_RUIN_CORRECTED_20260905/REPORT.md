# CAP02B — the P1-ONLY ruin table

**All six gates PASS.** Spec committed before results. `out/cap02b.txt` is the program's own
output; nothing in this report is assembled by hand.

**Evidence status: `DISCOVERY_CONSUMED`** — in-sample, post-selection, on the pool P1 was
selected on. **A LOWER BOUND on risk, not a forecast.** No forward or blind data touched.

---

## 0 · WHY THIS RUN EXISTS

On 2026-09-03 the owner redeployed **only P1**, at `MnqPerNq = 3`. XM is not deployed.

🔴 **The live object is therefore no longer M_11.** M_11 is the owner-ratified pair
(P1 ×1 NQ + XM ×1 NQ); the live book was its MNQ port at 3/10. **Dropping a leg does not make
a smaller M_11 — it makes a different object**, and that object had no risk number anywhere in
this repo. CAP01B's headline (2-year P(ruin) 6.5 %, band 6–22 %) is a **pair** number.
Quoting it for one leg would repeat the class of error CAP01 made: arithmetic that is fine,
about the wrong thing.

## 1 · THE ANSWER — P1 alone is materially safer than the pair, at the same size

**2-year P(ruin) at `MnqPerNq = 3`, measured-spread basis, MNQ commission charged,
E = $10,260.14:**

| pool | **P1 alone** | pair (control) | ratio |
|---|---:|---:|---:|
| full | **0.025** | 0.061 | **2.4× safer** |
| warm | **0.008** | 0.017 | **2.1× safer** |

Median 2-year drawdown at 3 MNQ: **$7,817 (76 % of equity)** full, **$6,784 (66 %)** warm —
against the pair's $10,251 / $8,3xx. The full table, all sizes 1–5, is in `out/cap02b.txt`.

**Why safer, mechanically:** the pair saves only ~14 % of the sum of its legs' risk, so it is
close to additive. Removing a leg removes nearly all of that leg's risk and its return with it.
This run says nothing about which is the better *investment* — only what each one's ruin
probability is.

## 2 · THE ASSUMPTION-FREE ANCHOR — G6, the single realised path, no resampling

At 3 MNQ, walking the actual historical session P&L from the current equity:

| object | worst equity trough | | |
|---|---:|---:|---|
| **P1 alone, full history** | **$7,077** | 69 % of equity | ✅ **survived** |
| pair, full history | **$14,380** | **140 %** | 🔴 **would have been wiped out** |
| P1 alone, warm | $399 | 3.9 % | survived |
| pair, warm | $0 | 0 % | survived |

n = 1, so this cannot estimate a tail probability and is **reported, not gated**. But it is
assumption-free and checkable by hand, and it points the same way as the bootstrap: **the
realised history would have ended this account on the pair and would not have ended it on P1.**
Both troughs sit in **March–May 2022** — the same regime, which is why the warm pool (cut at
2022-03-16) is so much gentler for both objects. **The warm number is not "the better estimate";
it is the same estimate with the worst regime removed.**

## 3 · WHAT DOMINATES THE ANSWER — the edge, not the sizing

| edge assumption | **P1 alone** | pair |
|---|---:|---:|
| in-sample (as is) | 0.023 | 0.061 |
| 70 % of in-sample | 0.077 | 0.127 |
| 40 % of in-sample | **0.196** | 0.265 |
| **edge is ZERO** | **0.483** | 0.594 |

**Honest band for P1 alone at 3 MNQ: ~2 % to ~20 %** across in-sample down to a 40 % edge —
against the pair's ~6 % to ~27 %. **If the edge is not real, it is ~48 %**, and roughly 70 % of
the time two years of live data will not settle which of those rows is the live one.

## 4 · THE GATES

| gate | spec | observed | |
|---|---|---|---|
| G1a | pair FULL 2 yr 3 MNQ == CAP01B 0.06535 | 0.0617 | ✅ |
| G1b | pair WARM == CAP01B 0.0167 | 0.0169 | ✅ |
| G2 | `maxdd ≥ worst_equity` on every draw, 4 object×pool | True | ✅ |
| G3 | P1 series unpadded; warm cut by **date**, not index | 726 == 726 | ✅ |
| **G4** | **semantic** — reported P(ruin) is `worst_equity`, not `maxdd` | 0.184 apart | ✅ |
| **G5** | **second method** — absorbing-barrier walk agrees | 0.0017 | ✅ |

**G4 and G5 exist because of CAP01**, which passed four gates and still published a 10×-wrong
headline: every gate tested the *reconstruction*, none tested what the output *meant*.
G4 tests the **meaning** (and the 0.184 gap between the drawdown figure and the ruin figure at
3 MNQ is exactly the size of the error CAP01 made). G5 tests the **implementation**.

⭐ **G3 is not a formality.** Two traps were coded out in advance:
1. **Never pad the P1 series with XM-only sessions as zero rows.** That adds flat days, cuts
   per-session variance, and *understates* ruin.
2. **The warm trim is by calendar date, not ordinal index.** CAP01B cut the pair at `iloc[37:]`;
   cutting P1 at index 37 would remove a different span of history, because the legs trade 726
   vs 873 sessions. Both objects are cut at the same instant, **2022-03-16**.

## 5 · WHAT THIS RUN MAY NOT BE USED FOR

- **No size is recommended.** That is the owner's decision.
- **It is not an argument for or against dropping XM.** It reports one object's ruin
  probability; it says nothing about return, and dropping a leg drops return too.
- **It is `DISCOVERY_CONSUMED`** — a lower bound, on the pool the strategy was selected on.
- The `eval_battery` fixed-DD placebo rule is **noted and not triggered**: this run reports a
  probability, not a drawdown-normalised performance figure.

## 6 · PREDECESSOR

**`CAP02` ran first and its G1 FAILED. It is recorded failed and was not edited or re-run.**
The fault was in my spec, not the machine: G1 named "warm pool = 0.065", but 0.06535 is
CAP01B's **full**-pool figure and its warm figure is 0.0167 — and CAP02 observed 0.016, i.e. it
reproduced the warm pool correctly against a target that named the wrong pool. Correcting a
mis-transcribed reproduction target is not redefining a population, so it was allowed — but
**only under a strictly harder gate: CAP02B must reproduce both pools, and it does.**
