# TRACK P — multi-strategy / account layer (Phase 9 arithmetic notes, 2026-08-23)

**Status: UNDERDETERMINED — Trade Performance aggregates are consistent with ≥2
simultaneous strategies including at least one UNIDENTIFIED short-hold component;
H1 vs H2 position semantics cannot be discriminated from available aggregates.**

## The arithmetic (no new backtests; candidates frozen)

TP 2026-06-07→12 (POSSIBLE_ACCOUNT_OR_MULTI_STRATEGY_EVIDENCE): 136 trades = 32.83/day,
hold 20.49m, WR 50.00%, avg trade +$87.21, commission $141.20 (= $1.04/trade).

Frozen candidates' 2026 behavior:
- Family V proxy: ~18.9 trades/day, hold ~36m, WR ~30%.
- Family S candidate: ~8-9 trades/day in 2026, hold ~75m — and LOSING in 2026 (S13:
  −$78k Jan-May); the trader plausibly no longer ran it.
- V + S sum ≈ 27-28/day at blended hold ~45m — matches NEITHER the 32.8/day nor the
  20.5m hold nor the 50% WR.

Conclusion (Class C): the June TP output requires a higher-frequency, shorter-hold,
higher-WR component beyond V and S — most plausibly Family B (mechanism unknown) or a
V-variant. Consistent with AS-1 (several strategies simultaneously); NOT provable as
"all strategies combined" (TP filters unknown, §26).

## H1 vs H2 (±1 account cap vs overlapping qty-1 sleeves)

32.83 trades/day × 20.49m ≈ 672 in-market min/day < 1,380 session minutes — a single
serialized contract (H1) is arithmetically POSSIBLE, and overlapping sleeves (H2) equally
so. The only discriminating evidence would be simultaneous-position artifacts (e.g.,
2-lot exposure moments in a Trade Performance execution list) — not present in the
available screenshots. BOTH hypotheses remain open (§27: do not choose by preference).

## Commission evidence (Q16 input)

$141.20 / 136 trades = $1.038/trade RT. Inconsistent with the author's ~$2/RT estimate
(AS-4) and with NQ Lifetime $4.36/RT; close to MNQ-class or a discounted/exchange-only
template. Possibilities (all Class C): some sleeves trade MNQ; a partial commission
template; TP commission column semantics differ. Recorded, unresolved.
