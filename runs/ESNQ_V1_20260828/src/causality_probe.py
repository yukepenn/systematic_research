"""P0-1 TWO-SIDED CAUSALITY PROBE, corrected.  A probe with teeth, tested per-decision.

WHY THE FIRST VERSION WAS WRONG -- recorded, because the pattern recurs (discipline rule 55: the
probe was wrong, the engine was right):

  1. The ES embargo cutoff is PER DECISION (t - 200ms). The first probe corrupted every ES event
     after ONE global cutoff taken from the first grid point, so for every later decision it was
     corrupting data that legitimately sits BEFORE that decision's own cutoff. The features moved
     because they were SUPPOSED to move. That is not a look-ahead.
  2. The positive clause added +500 to BOTH quote sides. A parallel shift leaves the SPREAD
     unchanged and cannot change an event COUNT, so es_spread_tk / es_bid_upd_30s / es_ask_upd_30s
     could not possibly respond. Three families were recorded as "did not move" by construction.

CORRECTED DESIGN. Test ONE decision at a time against ITS OWN cutoff, and use a perturbation that
can actually reach each family:
    NEG-A  corrupt NQ quotes strictly after t              -> NQ-native features must not move
    NEG-B  corrupt ES quotes strictly after t-200ms        -> ES features must not move
    POS-A  shift ES ASK only, before the cutoff            -> spread / rel_move / rvol must move
    POS-B  delete ES quote events before the cutoff        -> update counts must move
A price perturbation CANNOT test a count feature; that needs an event perturbation. Saying so is
the difference between a probe and a ritual.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "research_sdk"))
import esnq_batch as B                                                  # noqa: E402

PARQ = os.path.join(ROOT, "research", "data_esnq", "parquet")
EMB = B.ES_EMBARGO_NS
ES_F = ["rel_move_1s", "rel_move_5s", "rel_move_15s", "rel_move_30s",
        "es_spread_tk", "es_rvol_30s", "es_bid_upd_30s", "es_ask_upd_30s"]
NQ_F = ["nq_spread_tk", "nq_rvol_30s"]
CNT_F = ["es_bid_upd_30s", "es_ask_upd_30s"]


def _feat_one(sd, t, nq_mod=None, es_mod=None):
    """Recompute the 11 features for ONE decision instant t, with optional stream edits."""
    nb_t, nb_p, na_t, na_p = B.distinct_sides(os.path.join(PARQ, "NQ", f"s{sd}.parquet"))
    eb_t, eb_p, ea_t, ea_p = B.distinct_sides(os.path.join(PARQ, "ES", f"s{sd}.parquet"))
    if nq_mod:
        nb_t, nb_p, na_t, na_p = nq_mod(nb_t, nb_p, na_t, na_p)
    if es_mod:
        eb_t, eb_p, ea_t, ea_p = es_mod(eb_t, eb_p, ea_t, ea_p)
    g = np.array([t], dtype=np.int64)
    tc = g - EMB
    fb, _ = B.prev_lt(nb_t, nb_p, g)
    fa, _ = B.prev_lt(na_t, na_p, g)
    nq_mid, nq_spread = (fb + fa) / 2.0, fa - fb
    eb, _ = B.prev_le(eb_t, eb_p, tc)
    ea, _ = B.prev_le(ea_t, ea_p, tc)
    es_mid, es_spread = (eb + ea) / 2.0, ea - eb
    F = {}
    for w in (1, 5, 15, 30):
        p1, _ = B.prev_lt(nb_t, nb_p, g - w * B.NS_PER_S)
        p2, _ = B.prev_lt(na_t, na_p, g - w * B.NS_PER_S)
        q1, _ = B.prev_le(eb_t, eb_p, tc - w * B.NS_PER_S)
        q2, _ = B.prev_le(ea_t, ea_p, tc - w * B.NS_PER_S)
        F[f"rel_move_{w}s"] = ((es_mid - (q1 + q2) / 2) / es_mid
                               - (nq_mid - (p1 + p2) / 2) / nq_mid)
    from timegrid import lookback_offsets_s
    npath, epath = [], []
    for o in lookback_offsets_s(30, 1):
        a, _ = B.prev_lt(nb_t, nb_p, g + o)
        b, _ = B.prev_lt(na_t, na_p, g + o)
        c, _ = B.prev_le(eb_t, eb_p, tc + o)
        e, _ = B.prev_le(ea_t, ea_p, tc + o)
        npath.append((a + b) / 2)
        epath.append((c + e) / 2)
    with np.errstate(all="ignore"):
        F["nq_rvol_30s"] = np.nanstd(np.diff(np.array(npath), axis=0), axis=0) * B.DPP_NQ
        F["es_rvol_30s"] = np.nanstd(np.diff(np.array(epath), axis=0), axis=0) / es_mid * 1e4
    for nm, t_ in (("es_bid_upd_30s", eb_t), ("es_ask_upd_30s", ea_t)):
        F[nm] = (np.searchsorted(t_, tc, "right")
                 - np.searchsorted(t_, tc - 30 * B.NS_PER_S, "right")).astype(float)
    F["es_spread_tk"] = es_spread / B.TICK_ES
    F["nq_spread_tk"] = nq_spread / B.TICK_NQ
    F["tod"] = np.array([0.0])
    return {k: float(np.asarray(v).ravel()[0]) for k, v in F.items()}


def run(sessions, n_probe=5, emit=print):
    rng = np.random.default_rng(B.SEED)
    res = {"negA": [], "negB": [], "posA": [], "posB": []}
    for sd_iso in sessions[:n_probe]:
        sd = sd_iso.replace("-", "")
        day = int(pd.Timestamp(sd_iso).value)
        from timegrid import session_grid_ns
        grid = session_grid_ns(day, B.RTH_START, B.RTH_END, B.GRID_S)
        t = int(grid[len(grid) // 2])
        tc = t - EMB
        base = _feat_one(sd, t)
        # NEG-A: NQ quotes strictly AFTER t
        m = _feat_one(sd, t, nq_mod=lambda bt, bp, at, ap:
                      (bt, np.where(bt > t, bp + 500., bp), at, np.where(at > t, ap + 500., ap)))
        res["negA"].append(max(abs(m[c] - base[c]) for c in NQ_F))
        # NEG-B: ES quotes strictly AFTER this decision's cutoff
        m = _feat_one(sd, t, es_mod=lambda bt, bp, at, ap:
                      (bt, np.where(bt > tc, bp + 500., bp), at, np.where(at > tc, ap + 500., ap)))
        res["negB"].append(max(abs(m[c] - base[c]) for c in ES_F))
        # POS-A: ES ASK only, BEFORE the cutoff -> spread must move
        m = _feat_one(sd, t, es_mod=lambda bt, bp, at, ap:
                      (bt, bp, at, np.where(at <= tc, ap + 5.0, ap)))
        res["posA"].append({c: abs(m[c] - base[c]) for c in ES_F if c not in CNT_F})
        # POS-B: DELETE half the ES quote events before the cutoff -> counts must move
        def drop(bt, bp, at, ap):
            kb = ~((bt <= tc) & (rng.random(len(bt)) < 0.5))
            ka = ~((at <= tc) & (rng.random(len(at)) < 0.5))
            return bt[kb], bp[kb], at[ka], ap[ka]
        m = _feat_one(sd, t, es_mod=drop)
        res["posB"].append({c: abs(m[c] - base[c]) for c in CNT_F})
        # POS-C: a LEVEL shift cancels inside a return, so rel_move_w needs a perturbation that
        # changes the ES RETURN. Shift only the last w seconds before the cutoff, per w.
        rc = {}
        for w in (1, 5, 15, 30):
            lo = tc - w * B.NS_PER_S
            mm = _feat_one(sd, t, es_mod=lambda bt, bp, at, ap, lo=lo:
                           (bt, np.where((bt > lo) & (bt <= tc), bp + 5., bp),
                            at, np.where((at > lo) & (at <= tc), ap + 5., ap)))
            rc[f"rel_move_{w}s"] = abs(mm[f"rel_move_{w}s"] - base[f"rel_move_{w}s"])
        res.setdefault("posC", []).append(rc)
    negA, negB = max(res["negA"]), max(res["negB"])
    posA = {c: max(r[c] for r in res["posA"]) for c in res["posA"][0]}
    posB = {c: max(r[c] for r in res["posB"]) for c in res["posB"][0]}
    posC = {c: max(r[c] for r in res["posC"]) for c in res["posC"][0]}
    emit(f"    probes on {n_probe} sessions, mid-session decision each")
    emit(f"    NEG-A  corrupt NQ after t          -> max |d| over NQ features  {negA:.3e}")
    emit(f"    NEG-B  corrupt ES after t-200ms    -> max |d| over ES features  {negB:.3e}")
    emit("    POS-A  ES ASK shifted before cutoff -> these MUST move:")
    for c, v in posA.items():
        emit(f"           {c:<16} {v:.3e}  {'MOVED' if v > 0 else '*** DID NOT MOVE ***'}")
    emit("    POS-B  ES events deleted before cutoff -> counts MUST move:")
    for c, v in posB.items():
        emit(f"           {c:<16} {v:.3e}  {'MOVED' if v > 0 else '*** DID NOT MOVE ***'}")
    emit("    POS-C  ES shifted ONLY in the last w s before the cutoff -> each rel_move_w MUST move")
    emit("           (a uniform level shift cancels inside a return; the probe must reach the family)")
    for c, v in posC.items():
        emit(f"           {c:<16} {v:.3e}  {'MOVED' if v > 0 else '*** DID NOT MOVE ***'}")
    neg_ok = negA == 0.0 and negB == 0.0
    # Each of the 8 ES families must be moved by AT LEAST ONE probe capable of reaching it.
    # POS-A cannot move a count; POS-B cannot move a spread; a uniform level shift cannot move a
    # RETURN. Requiring every probe to move every family would be requiring an impossibility and
    # would make the gate unpassable for reasons that have nothing to do with causality.
    reach = {f: max(posA.get(f, 0.0), posB.get(f, 0.0), posC.get(f, 0.0)) for f in ES_F}
    pos_ok = all(v > 0 for v in reach.values())
    emit("    FAMILY COVERAGE - each family must respond to at least one probe that can reach it:")
    for f in ES_F:
        emit(f"           {f:<16} best |d| {reach[f]:.3e}  "
             f"{'CERTIFIED' if reach[f] > 0 else '*** NOT CERTIFIED ***'}")
    emit(f"    >>> NEGATIVE {'PASS' if neg_ok else '*** FAIL - LOOK-AHEAD ***'}   "
         f"POSITIVE {'PASS - every family responds to its own inputs' if pos_ok else '*** FAIL - NO TEETH ***'}")
    return neg_ok, pos_ok, dict(negA=negA, negB=negB, posA=posA, posB=posB, posC=posC)


if __name__ == "__main__":
    import blindguard as BG
    s = sorted(BG.load_manifest(os.path.join(RUN, "manifests", "ESNQ_DEV_44.csv")))
    run(s)
