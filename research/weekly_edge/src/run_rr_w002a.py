"""RR_W002A - DOES CAUSAL INFORMATION PREDICT FULL-HORIZON ACTION VALUE?

Spec: runs/RR_W002A_ACTION_VALUE_INFORMATION/spec.yaml, committed at f5d4e01 BEFORE this file
existed.

STAGE A INFORMATION ONLY. No router, no policy, no abstention, no sizing, no exit change, no HMM.
Nothing here becomes a rule.

Target: delta_total_window - the FULL-HORIZON causal action value from RR_W001.

Usage:
    python run_rr_w002a.py --gate     # Phase 0 causality gate only (blocking)
    python run_rr_w002a.py            # full wave
"""
from __future__ import annotations

import argparse
import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                   # noqa: E402
from run_we_w01 import ROOT                                               # noqa: E402
from run_we_w17 import load_deep                                          # noqa: E402
from we_fastctx import fast_build_context                                 # noqa: E402

RUN = os.path.join(ROOT, "runs", "RR_W002A_ACTION_VALUE_INFORMATION")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
LEDGER = os.path.join(ROOT, "runs", "RR_W001_ACTION_VALUE_LEDGER", "out", "ledger_p1pct.csv")
XMP = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
       "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
       "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}
A, B = np.datetime64("2022-07-01"), np.datetime64("2026-08-01")
SEED = 2002
NSHIFT = 200
FIRST_FIT = 250
BLOCK = 63
RIDGE_ALPHA = 10.0

_t0 = _time.time()
_fh = None


def P_(*a):
    print(*a, flush=True)
    if _fh is not None:
        print(*a, file=_fh)
        _fh.flush()


def el():
    return f"[{_time.time() - _t0:6.0f}s]"


# ===================================================================== feature construction
ENGINE_CTX = ["dist_open", "dist_vwap", "runlen", "delta_mag", "prev_ret", "atr_l"]
NQ_STATE = ["nq_move_5m", "nq_move_15m", "nq_move_30m", "nq_path_eff_30m",
            "nq_atr_z", "session_move_so_far"]
TIME_F = ["minute_of_session"]
NEGCTRL = ["rel_volume_1m", "xm_support_mag_15m"]


def build_market_features(D, X, ent, xm_arrays):
    """Every column is computed from bars <= i-1. The causality gate proves it rather than
    asserting it: P1/PCT fills at the OPEN of bar i, so bar i's own OHLCV is unavailable."""
    c, v, h, l_ = D["c"], D["v"], D["h"], D["l"]
    o, sid, fb = D["o"], D["sid"], D["fb"]
    n = D["n"]
    out = {}
    for k in ENGINE_CTX:
        out[k] = X[k][ent].astype(float)

    prev = ent - 1                                     # the last CLOSED bar at decision time
    atr = np.maximum(X["atr_l"][ent], 1e-9)

    def mv(k):
        a = np.where(prev - k >= 0, c[np.maximum(prev - k, 0)], np.nan)
        return (c[prev] - a) / atr

    out["nq_move_5m"] = mv(5)
    out["nq_move_15m"] = mv(15)
    out["nq_move_30m"] = mv(30)

    absdiff = np.abs(np.diff(c, prepend=c[0]))
    cum = np.cumsum(absdiff)
    path = cum[prev] - cum[np.maximum(prev - 30, 0)]
    out["nq_path_eff_30m"] = (c[prev] - c[np.maximum(prev - 30, 0)]) / np.maximum(path, 1e-9)

    atr_full = X["atr_l"]
    atr_s = pd.Series(atr_full)
    z = (atr_s - atr_s.rolling(2000, min_periods=200).mean()) / \
        atr_s.rolling(2000, min_periods=200).std()
    out["nq_atr_z"] = z.to_numpy()[ent]

    lo_of = np.zeros(n, np.int64)
    starts = np.flatnonzero(fb)
    lo_of[starts] = starts
    lo_of = np.maximum.accumulate(lo_of)
    out["session_move_so_far"] = (c[prev] - o[lo_of[ent]]) / atr

    mod = np.array([pd.Timestamp(t).hour * 60 + pd.Timestamp(t).minute for t in D["t"][ent]])
    out["minute_of_session"] = mod.astype(float)

    vs = pd.Series(v)
    relv = v / np.maximum(vs.rolling(240, min_periods=30).mean().to_numpy(), 1e-9)
    out["rel_volume_1m"] = relv[prev]

    # W122 B_SUPPORT_MAG at 15 minutes, signed by NQ's own direction - a KNOWN-NULL negative control
    acc = np.zeros(len(ent)); cnt = np.zeros(len(ent))
    for k, arr in xm_arrays.items():
        with np.errstate(divide="ignore", invalid="ignore"):
            r = np.log(arr[prev] / arr[np.maximum(prev - 15, 0)])
        sr = pd.Series(np.log(arr / np.roll(arr, 15)))
        sg = sr.rolling(1200, min_periods=200).std().to_numpy()[prev]
        zz = r / np.maximum(sg, 1e-12)
        g = np.isfinite(zz)
        acc[g] += zz[g]; cnt[g] += 1
    nqdir = np.sign(out["nq_move_15m"])
    out["xm_support_mag_15m"] = np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan) * nqdir
    return out


def load_xm(D):
    nq = pd.DataFrame({"time": pd.to_datetime(D["t"])}).set_index("time")
    arrs = {}
    for k, path_ in XMP.items():
        f = os.path.join(ROOT, path_)
        if not os.path.exists(f):
            continue
        d_ = pd.read_parquet(f, columns=["time", "close"])
        d_["time"] = pd.to_datetime(d_["time"])
        arrs[k] = nq.join(d_.set_index("time")["close"].rename(k), how="left")[k].to_numpy()
    return arrs


def main(gate_only: bool):
    global _fh
    _fh = open(os.path.join(OUT, "gate.txt" if gate_only else "rr_w002a.txt"), "w",
               encoding="utf-8")
    P_("=" * 124)
    P_("=== RR_W002A - DOES CAUSAL INFORMATION PREDICT FULL-HORIZON ACTION VALUE?")
    P_("=== Spec f5d4e01.  STAGE A INFORMATION ONLY.  Nothing here becomes a policy.")
    P_("=" * 124)

    L = pd.read_csv(LEDGER)
    L = L[L["in_window_session"]].reset_index(drop=True)
    P_(f"{el()} ledger {len(L):,} in-window decisions")
    assert len(L) == 2131

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    X = fast_build_context(D)
    tarr, n = D["t"], D["n"]
    ent = np.array([int(min(np.searchsorted(tarr, np.datetime64(t)), n - 1))
                    for t in L["decision_ts"]])
    assert (np.abs(np.array([np.datetime64(t) for t in L["decision_ts"]]) - tarr[ent])
            == np.timedelta64(0, "s")).all(), "decision timestamps do not land on bars"
    P_(f"{el()} substrate {n:,} bars; {len(ent):,} decision bars located exactly")

    xm = load_xm(D)
    P_(f"{el()} cross-market substrates loaded: {sorted(xm)}")
    F = build_market_features(D, X, ent, xm)

    # ================================================================= PHASE 0 CAUSALITY GATE
    P_("")
    P_("=" * 124)
    P_("=== PHASE 0 - CAUSALITY GATE.  BLOCKING: perturb bar i and the feature must NOT move.")
    P_("===              The lag profile is DIAGNOSTIC. Liveness is tested by variation, not response.")
    P_("=" * 124)
    rng = np.random.default_rng(SEED)

    # Bars must be perturbed FAR APART. A first version perturbed 300 decision bars at once and
    # every long-window feature failed, because perturbing bar i legitimately moves the feature at
    # bar i+1 .. i+240 and those neighbours were also in the test set. The gate was contaminating
    # itself. Minimum separation exceeds the longest lookback used anywhere here (2,000 bars).
    SEP = 5000
    order = np.sort(ent)
    sel, last = [], -10 ** 9
    for e in order:
        if e - last >= SEP:
            sel.append(int(e)); last = int(e)
    tb = np.array(sel)
    pos = {int(e): j for j, e in enumerate(ent)}
    idx = np.array([pos[int(e)] for e in tb])
    P_(f"    perturbation sample: {len(tb):,} decision bars, minimum separation {SEP:,} bars")

    # A known-BAD and a known-GOOD feature are injected so the gate proves it can tell them apart.
    def with_probes(Dx, Xx):
        f = build_market_features(Dx, Xx, ent, xm)
        at = np.maximum(Xx["atr_l"][ent], 1e-9)
        f["PROBE_LEAK_close_i"] = Dx["c"][ent] / at          # reads its OWN bar - must DROP
        f["PROBE_SAFE_close_prev"] = Dx["c"][ent - 1] / at   # reads bar i-1 - must KEEP
        return f

    F = with_probes(D, X)

    def rebuild(shift):
        D2 = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in D.items()}
        tgt = tb - shift
        for key, mult in (("h", 1.004), ("l", 0.996), ("c", 1.003), ("o", 1.002), ("v", 1.5)):
            D2[key][tgt] = D2[key][tgt] * mult
        return with_probes(D2, fast_build_context(D2))

    LAGS = [0, 1, 5, 30, 400]
    R = {sh: rebuild(sh) for sh in LAGS}
    P_(f"{el()} perturbation rebuilds complete for lags {LAGS}")

    # The BLOCKING clause is causality: immune to its own bar. The lag profile is DIAGNOSTIC only.
    # A first version also required a response to a perturbed NQ bar, and that wrongly dropped
    # prev_ret (the PREVIOUS SESSION's return - no tested lag reaches back that far) and
    # xm_support_mag_15m (a CROSS-MARKET feature, whose inputs are ES/RTY/YM and are not perturbed
    # at all). Neither is a defect. Liveness is now tested where it belongs: does the feature vary
    # across decisions at all?
    rows, keep = [], []
    for k in list(F):
        base = F[k][idx]
        moved = {}
        for sh in LAGS:
            d_ = np.abs(np.nan_to_num(base - R[sh][k][idx]))
            moved[sh] = float(np.mean(d_ > 1e-9))
        causal = moved[0] < 1e-12
        col = F[k]
        alive = bool(np.nanstd(col) > 0) and int(len(np.unique(col[np.isfinite(col)]))) > 5
        ok = causal and alive
        rows.append(dict(feature=k, moved_by_own_bar=moved[0], lag1=moved[1], lag5=moved[5],
                         lag30=moved[30], lag400=moved[400], causal=causal, alive=alive,
                         n_unique=int(len(np.unique(col[np.isfinite(col)]))),
                         verdict="KEEP" if ok else "DROP"))
        if ok and not k.startswith("PROBE_"):
            keep.append(k)

    P_("")
    P_(f"{'feature':<26}{'own bar':>9}{'lag1':>8}{'lag5':>8}{'lag30':>8}{'lag400':>8}{'verdict':>9}")
    for r in rows:
        P_(f"{r['feature']:<26}{100*r['moved_by_own_bar']:>8.1f}%{100*r['lag1']:>7.1f}%"
           f"{100*r['lag5']:>7.1f}%{100*r['lag30']:>7.1f}%{100*r['lag400']:>7.1f}%{r['verdict']:>9}")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "causality_gate.csv"), index=False)

    vb = next(r for r in rows if r["feature"] == "PROBE_LEAK_close_i")["verdict"]
    vg = next(r for r in rows if r["feature"] == "PROBE_SAFE_close_prev")["verdict"]
    P_("")
    P_("    SELF-TEST - can this gate tell a leak from a lag?")
    P_(f"      PROBE_LEAK_close_i   (reads its OWN bar)  -> {vb}   expected DROP")
    P_(f"      PROBE_SAFE_close_prev(reads bar i-1)      -> {vg}   expected KEEP")
    if vb != "DROP" or vg != "KEEP":
        P_("    THE GATE ITSELF IS BROKEN. No model is fitted. (harness rule: a causality validator")
        P_("    must be shown able to detect a known-bad construction before it is trusted)")
        _fh.close(); sys.exit(1)
    P_("      -> the gate detects a known-bad construction and passes a known-good one.")

    dropped = [r["feature"] for r in rows if r["verdict"] == "DROP" and not r["feature"].startswith("PROBE_")]
    P_("")
    P_(f"    KEPT {len(keep)} features; DROPPED {len(dropped)}: {dropped if dropped else 'none'}")
    P_("    A DROP is not a repair. A feature that reads its own bar is removed, never hand-lagged.")
    if not keep:
        P_("    GATE FAILED - no feature survives. No model is fitted.")
        _fh.close(); sys.exit(1)

    np.save(os.path.join(OUT, "_ent.npy"), ent)
    pd.DataFrame({k: F[k] for k in F if not k.startswith("PROBE_")}).assign(
        session_id=L["session_id"].to_numpy(),
        session_date=L["session_date"].to_numpy(),
        target_full=L["delta_total_window"].to_numpy(),
        target_sess=L["delta_action_value"].to_numpy(),
        own_net=L["baseline_trade_net"].to_numpy(),
        causal_quality_score=L["causal_quality_score"].to_numpy(),
        quality_score_is_warmup=L["quality_score_is_warmup"].to_numpy(),
        size_at_entry=L["size_at_entry"].to_numpy(),
        strategy_session_pnl_before_per_ctr=L["strategy_session_pnl_before_per_ctr"].to_numpy(),
        entry_ordinal_in_session=L["entry_ordinal_in_session"].to_numpy(),
    ).to_csv(os.path.join(OUT, "features.csv"), index=False)
    pd.Series(keep).to_csv(os.path.join(OUT, "kept_features.csv"), index=False, header=["feature"])
    P_(f"{el()} feature matrix written: {len(keep)} market columns + 5 expert-internal")
    if gate_only:
        P_(f"\n{el()} --gate: stopping. No model was fitted.")
        _fh.close(); return
    P_(f"\n{el()} PHASE 0 complete. Modelling continues in run_rr_w002b.py")
    _fh.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true")
    a_ = ap.parse_args()
    main(a_.gate)
