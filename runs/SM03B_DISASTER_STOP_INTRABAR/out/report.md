# SM03B — Intrabar Disaster Stop: ALL ARMS FAIL FROZEN GATES → STOP/EXIT FRONTIER CLOSED

_2026-08-08. Spec frozen before read (seq 301-306). Results: `out/results.csv`._

## Verdict: NO PROMOTION

Real trigger populations this time (593 stops, mid-only m=1.0), and the right-tail
gates PASS everywhere (top-1% retention 0.983-1.000, top-10-day 0.984-1.000) — but no
arm reaches the preregistered ≥5% improvement in any of maxDD/ES5/worst-month:

| arm (seq) | stops | ΔmaxDD | Δnet | ΔSharpe | P(dSharpe≤0) | hist ΔmaxDD |
|---|---|---|---|---|---|---|
| mid_only 1.0 (301) | 593 | **+3.9%** | +$7.5k | +0.040 | 0.210 | **−6.1% (worse)** |
| tiered (305) | 704 | +4.4% | +$4.6k | +0.027 | 0.307 | −6.8% (worse) |
| others | — | ≤3.9% | ≤+$1.8k | ≤0.010 | ≥0.23 | — |

- FACT: the E10-level effect is diluted ~13× by member netting (single-member stops
  barely move the aggregate target), and the stopped member waits flat until the next
  flip (natural re-entry), missing recoveries.
- FACT: in the 2006-2021 dead regime the stop consistently WORSENS both net and maxDD
  (locks in losses that the whipsaw regime recovered) — the "regime-insurance" framing
  is falsified for this stop family.

## Track-2 conclusion (with SM03, SM02B, and inherited kills)

Every stop/exit family is now closed with evidence: split exits (H-007), resting stop
orders (H-011), timed exits (SW02a/H-005 family), pure time-to-progress (SM02B:
positive remaining everywhere + tail-unsafe), loss-reactive throttles (SM02B:
anti-edge), close-basis disaster stops (SM03: algebraically impossible), intrabar
disaster stops (SM03B: sub-threshold, hist-adverse). **Directive Q3 = NO within this
architecture; drawdown engineering must come from exposure/allocation layers.**
Registry: seq 301-306 FAIL.
