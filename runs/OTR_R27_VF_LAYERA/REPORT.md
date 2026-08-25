# OTR_R27_VF_LAYERA — report

Spec preregistered before readout. Directive v4.0 §22/§23 and `PURCHASE_GATE_v2`
flip-condition 2. Code: `vwap_flux_family/src/vf_layer_ab.py`, `run_r27_layera.py`.

## The defect, and the fix

Vendor semantics: **Signal Quantity Per Trend** caps the number of *signals* emitted per
trend; **Signal Split (Bars)** is the minimum bar distance between consecutive
same-direction *signals*. Both belong to signal generation.

`run_r7_signal_id.run_member` advanced `cnt[sig]` / `last_sig[sig]` **only** in the
flat-entry branch and the X_OPP stop-and-reverse branch. A signal the indicator would emit
while the wrapper was already in a position therefore consumed no quota and did not start
the split clock — confirmed by code reading, not inferred.

The corrected architecture puts the counters in Layer A: a candidate that survives the quota
and split tests **is** emitted and consumes quota at that moment, whatever Layer B does.
Layer B never writes back.

## Regression, incumbent leader `T_C|P_MED|C_DIR|H1a|X_OPP`

| quantity | value |
|---|---|
| emitted signals (Layer A, corrected) | 2,730 |
| trades, OLD (counters on execution) | 1,722 |
| trades, NEW (counters on emission) | **1,705** |
| trader's observed trades across the same 17 windows | **1,214** |
| §40 distance OLD | 0.4761 |
| §40 distance NEW | **0.4768** |

**Preregistered P1 (trade count should fall): PASS** — but by 17 trades, 1.0 %.

The honest reading is that **the defect was real and its effect is negligible.** The spec
predicted a fall and got one; it also warned that landing near 1,214 was a hypothesis rather
than an expectation, and the correction closes ~3 % of the 508-trade gap. The §40 distance
moves by +0.0007, i.e. not at all.

Consequence for prior work: `VF_SIGNAL_GENERATOR_v2.md` listed a set of R7/R8 conclusions as
PROVISIONAL pending this rebuild. They are **no longer provisional** — the corrected
architecture reproduces them. The incumbent leader is unchanged, and so is its ranking.

## Six-geometry floor sweep under the corrected architecture

| lifecycle | rail formula | floor (corrected) | floor (R26, uncorrected) |
|---|---|---|---|
| block | percentile_linear | **0.4534** | 0.4624 |
| block | nearest_rank | **0.4534** | 0.4624 |
| anchor | percentile_linear | 0.4768 | 0.4761 |
| anchor | nearest_rank | 0.4768 | 0.4761 |
| anchor | minmax | 0.4894 | 0.4866 |
| block | minmax | 0.5378 | 0.5190 |

**`PURCHASE_GATE_v2` flip-condition 2 requires some geometry below 0.35. Best is 0.4534.
The DO-NOT-BUY verdict STANDS.**

## Three findings that survive the correction

1. **`percentile_linear` and `nearest_rank` are again byte-identical** (0.4768/0.4768 and
   0.4534/0.4534). Behavioural inertness at n = 5 with 95/75/50/25/5 is confirmed under the
   corrected architecture too. An oracle resolving that question buys nothing, twice over.
2. **`min-max` is again worst** in both lifecycles — EV-040's geometric rejection confirmed
   behaviourally for a second time.
3. **BLOCK again edges ANCHOR** (0.4534 vs 0.4768), and by slightly more than before
   (0.0234 vs 0.0137). This continues to vindicate the directive's instruction to reopen the
   lifecycle, and continues **not** to be grounds for selecting BLOCK: §6 forbids choosing a
   vendor semantic by score, and 0.023 is not a discriminator. Both stay alive.

## Where the 2026 residual actually is

Layer A emits **2,730** signals; the trader takes **1,214** trades. Our wrapper converts
those signals into **1,705** trades. So the mismatch is not primarily in the cloud geometry
(worth ≤ 0.023) nor in the signal-counting semantics (worth 0.0007) — it is in **how many
emitted signals his wrapper declines**, which is the same class of unidentified suppression
behaviour that R23 could not pin down for the 2023 era with 15 exact labels.

That is a wrapper/risk-layer question, not a vendor question, and no purchase addresses it.
