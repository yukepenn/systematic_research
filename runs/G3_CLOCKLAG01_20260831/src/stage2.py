"""G3_CLOCKLAG01 - Stage 2 economics. RUNS ONLY ON A STAGE 1 PASS (spec S2_precondition).

The rule was frozen in the spec before any statistic existed:

    at the OPEN of bucket b on day d take a position of sign( r(b, d-1) ), held to the CLOSE of
    bucket b, size 1 contract, ALL 13 BUCKETS EVERY DAY.

No sizing layer, no filter, no threshold, NO BUCKET SELECTION. `refuse_bucket_subset` below is the
program's enforcement of spec prohibition 4: selecting a subset of buckets after seeing Stage 1 is
prohibited, and this module raises rather than obeying such a request.

COSTS. The WAVE B candidate's ~0.9 point assumption is STALE and the spec names it as the single
most likely way this candidate dies. Three lines are always printed together:

    $4.36 /ctrRT   commission only        0.218 NQ points   A FLOOR, NEVER A HEADLINE
    $20.65/ctrRT   EXEC01 measured        1.033 NQ points   <-- THE PRIMARY LINE
    $25.01/ctrRT   standing all-in        1.251 NQ points

13 round turns/session x ~250 sessions = ~3,250 RT/yr, so the annual cost at the primary line is
~$67,000 and that number is printed beside every gross figure.
"""
from __future__ import annotations

import numpy as np

PV = 20.0                     # $ per NQ point
COST_LINES = {               # $ per contract round turn
    "COMMISSION_ONLY_4.36": 4.36,
    "EXEC01_PRIMARY_20.65": 20.65,
    "ALL_IN_25.01": 25.01,
}
PRIMARY_LINE = "EXEC01_PRIMARY_20.65"
RT_PER_SESSION = 13
SESSIONS_PER_YEAR = 250


def refuse_bucket_subset(buckets):
    """spec prohibition 4 - the program must refuse to trade a post-hoc bucket subset."""
    b = sorted(int(x) for x in buckets)
    if b != list(range(13)):
        raise RuntimeError(
            "REFUSED: Stage 2 was asked to trade buckets " + repr(b) + ". The frozen rule trades "
            "ALL 13 BUCKETS EVERY DAY; selecting a subset after seeing the Stage 1 table is "
            "prohibited by spec.yaml prohibition 4 and this program will not do it.")
    return np.arange(13)


def signal_and_pnl(P, B, R, cost_rt, buckets=range(13), predictor=None):
    """Gross and net per-(day, bucket) P&L in dollars for the frozen rule.

    P, B, R are the (n_sess, 13) close / base / return matrices of ONE era in session order.
    `predictor` defaults to R itself; the circular-shift null passes a day-shifted matrix so that
    the SIGNAL is nulled while the price path traded, the trade count and the costs are identical.
    """
    refuse_bucket_subset(buckets)
    pred = R if predictor is None else predictor
    sig = np.sign(pred[:-1])                  # sign( r(b, d-1) ), formed strictly before the entry
    move = (P - B)[1:]                        # bucket close minus bucket open, in NQ points
    gross = sig * move * PV
    net = gross - cost_rt
    return gross, net, sig


def annual_cost(cost_rt=COST_LINES[PRIMARY_LINE]):
    return cost_rt * RT_PER_SESSION * SESSIONS_PER_YEAR


def null_net_distribution(P, B, R, cost_rt, n_draws, seed, buffer=5):
    """The SAME circular shift used in Stage 1, with costs applied identically on every draw."""
    rng = np.random.default_rng(seed)
    n = len(R)
    ks = rng.integers(buffer, n - buffer + 1, size=n_draws)
    out = np.empty(n_draws)
    for i, k in enumerate(ks):
        _, net, _ = signal_and_pnl(P, B, R, cost_rt, predictor=np.roll(R, int(k), axis=0))
        out[i] = net.sum()
    return out
