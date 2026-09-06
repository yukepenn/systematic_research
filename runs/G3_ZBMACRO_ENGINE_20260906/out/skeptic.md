# ZBMACRO01 adversarial skeptic -- G3_ZBMACRO_ENGINE_20260906 (ledger G00079)

**Framing: refuter.** The job of this section is to kill the engine. Kill criteria were
preregistered in `src/run_engine.py` (header) BEFORE any result existed and are applied
mechanically. **EVIDENCE STATUS: DISCOVERY_CONSUMED.**

## Lens 1 -- DUPLICATION ("this is just published post-announcement drift")

**Attack.** r1 = close(08:45)-close(08:30) on a release morning is close to a linear read of
the macro surprise: a down first response IS "the number came in hawkish/strong". Bond-market
post-announcement drift after macro surprises is published literature (announcement-day
momentum/underreaction). If every rates desk knows it, the residual after their arbitrage
should be zero, and our +$177/ct is a measurement artifact of a lucky window.

**What the attack must show to kill (preregistered):** the effect is tradable-known AND
arbitraged post-publication -- operationalized in-sample as last-half after-cost mean >= 0.

**Observed:** last-20 after-cost mean -0.1363 pt (+136.3 $/ct) -- still profitable
through 2026. The shift-null (G00072 G3) put the effect at the 0.5th percentile with a
POSITIVE null mean: generic down-momentum on non-release days LOSES money, so this is not a
generic drift harvest either. **Verdict: NO KILL.** The lens instead assigns the mechanism
LABEL: **behavioral underreaction / slow repricing of an 08:30 macro surprise** -- a known
mechanism family. That label cuts both ways: it makes the effect more credible ex ante and
predicts it is crowded-fragile ex post; the regime lens owns the monitoring consequence.

## Lens 2 -- FRAGILITY ("the edge lives in 5 minutes and 3 trades")

**Attack.** (i) Latency: the G00072 neighborhood showed the 08:50-conditioned cell at
$17.7/ct. If the executable 08:46 fill cannot hold the edge, the claim dies. (ii)
Concentration: top-3 trades = 66% of net; drop-k dies at k~5. (iii) Power: |mean| 0.1777 pt
< MDE_80 0.2641 pt at n=40. (iv) Family: E1 came out of the G00067 event screen -- some
selection debt is unpaid even after the falsifier.

**Preregistered kill:** G_delay = KILLED-AT-EXECUTION.

**Observed delay curve (net $/ct, PRIMARY):** 08:45 +177.7  08:46 +186.3  08:47 +203.5  08:48 +202.7  08:50 +197.2;
08:46 CI [+44.8, +432.4] $/ct; retention 1.048;
monotone False. **G_delay = PASS -> NO KILL.**

**The single most likely way this is nothing (stated, as required):** a tail-carried n=40
object below its own 80%-power MDE, drawn from an event-screen family -- i.e., three good
CPI mornings in 2023 doing 66% of the work, with the rest near noise. The falsifier's CI,
null, chronology and drop-k clauses all passed, but every one of them is a point-in-time
in-sample statement on the same consumed substrate. This risk is IRREDUCIBLE at n=40 and is
carried forward as the engine's stated fragility, to be discharged only by forward trades.

## Lens 3 -- REGIME ("2023-2026 is the inflation-attention era")

**Attack.** The sample is exactly the era when CPI/NFP were THE bond-market events. In a
2% -inflation regime CPI mornings stop moving ZB; the conditioning event (|r1| large enough
to matter) thins out and the drift mechanism starves.

**Preregistered kill:** both chronology halves wrong-sign. **Observed:** -0.2191 /
-0.1363 pt -- both profitable. **NO KILL.**

**Decay condition (named):** the edge requires (i) scheduled 08:30 releases that still move
ZB (measurable: |r1| level) and (ii) minutes-scale underreaction persisting. **Regime
indicator:** rolling median |r1| over the trailing 12 events vs the 2023-2026 sample median
(0.656 pt on the 40 events); a sustained fall below HALF that
level says the conditioning regime has left.

**Prospective kill rule (proposed for FT-stage preregistration; a chronology-half monitor):**
maintain the cumulative FORWARD after-cost mean at the executable 08:46 entry; evaluate at
every 10th forward trade; **KILL if at n_fwd >= 20 the cumulative forward after-cost mean
<= 0**, and REVIEW (owner packet) if at n_fwd >= 10 it is below -$100/ct. At ~11 trades/yr
the kill point arrives in ~2 years -- stated so nobody mistakes this for a fast-falsifying
object.

## Lens 4 -- IMPLEMENTATION ("the NT8 path will not be the research object")

**Attack surface (FT4-FT9 risks, enumerated):**
1. **New class** -- no shared lineage with the certified P1/XM classes; every W52-class
   parity lesson (decision-series first, dollars last) must be re-earned on ZB.
2. **Roll guard inheritance** -- ZB's quarterly roll differs from NQ/MNQ's; the W98-family
   roll fail-safe LATCHES; a wrong ZB rollover date would block entries silently. The ZB
   rollover table must be built from scratch, never inherited.
3. **Session flatten at 15:00** -- CBOT 30Y trades to 17:00; the 15:00 exit is a strategy
   order, not a session end. A missed flatten holds overnight -- the object explicitly
   forbids that; the flatten needs its own fail-safe (flatten-or-disable).
4. **Fail-closed on missing bars** -- ZB prints no bar in zero-trade minutes. The signal
   needs the 08:30 and 08:45 closes; if either bar is missing/stale the engine must STAND
   ASIDE (no as-of improvisation live), and the 08:46 fill is at the next print.
5. **Calendar dependency** -- NFP/CPI dates must come from a maintained calendar with
   holiday shifts; a stale calendar file = silent no-trade (fail-closed, but silently
   idle -- needs a heartbeat).
6. **Cost reality** -- the modeled 1 tk/side ZB spread is plausible for the deepest
   treasury book but was never measured on this box; the STRESS arm (2 tk/side) is the
   honest floor: 08:45 +115.2  08:46 +123.8  08:47 +141.0  08:48 +140.2  08:50 +134.7 $/ct.
7. **Margin** -- day margin ASSUMED ~$2,000/ct, not broker-verified.

**Preregistered kill:** a blocking impossibility (cannot be implemented fail-closed).
**Assessment:** none found -- every risk above has a standard fail-closed treatment already
used by the live P1 class (stand-aside guards, flatten fail-safe, explicit roll table).
**NO KILL.** These seven items are the FT4-FT9 work list, not reasons the object cannot
exist.

## Verdict (mechanical)

kills = {'duplication': False, 'fragility': False, 'regime': False, 'implementation': False} -> **SURVIVES**.

The skeptic did not kill the engine. Per the preregistered decision rule with G_delay = PASS, the run is ledger PASS and FT0 (freeze: rule + entry close(08:46) + k=2) is licensed. The fragility statement in Lens 2 and the FT-stage monitor in Lens 3 are BINDING riders on that license.
