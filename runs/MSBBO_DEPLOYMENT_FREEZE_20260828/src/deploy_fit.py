"""MS-BBO-CANDIDATE-1-DEPLOY - turn a surviving candidate into ONE deployable object.

THIS IS ENGINEERING, NOT EVIDENCE.  Frozen by SPEC.md before it ran.

THE DEFECT BEING FIXED.  bbo_v1.py evaluates five chronological out-of-fold Ridge fits and names
none of them as THE model. Nothing in the frozen artifact determines the prediction for
2026-09-02 10:00:00 ET, so two honest implementations could disagree - which makes the candidate
unfalsifiable prospectively.

THE ONE RULE, declared in SPEC before any coefficient existed:
    FULL FIT OF THE FROZEN PRIMARY ESTIMATOR (Ridge alpha=10.0)
    ON THE FROZEN CONSUMED DISCOVERY POPULATION.
No comparison against fold-average / last-fold / ensemble / recalibrated / other-alpha. That
comparison would be a selection machine wearing engineering clothes.

>>> The deployment model's HISTORICAL IN-SAMPLE RESULT HAS ZERO EVIDENTIARY WEIGHT. <<<
It is not compared to $5,124.76 and may never enter a promotion argument.

The alpha definition is IMPORTED from bbo_v1.py unmodified, never restated, so drift is
structurally impossible and the frozen sha256 stays valid.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import Ridge

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(RUN), "MSBBO_V1_20260828", "src"))
import bbo_v1 as B                                                      # noqa: E402

OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
_fh = open(os.path.join(OUT, "deploy_fit.txt"), "w", encoding="utf-8")

FROZEN_BBO_SHA = "36dee22cdb001f0a36f6f7de112e97d3590f0be8eb9b6338d8d33383bb65dc6d"
SEAL = "2026-08-01"
RIDGE_ALPHA = 10.0
D1_TOL = 1e-9


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    P("=" * 104)
    P("=== MS-BBO-CANDIDATE-1-DEPLOY  -  DEPLOYMENT DEFINITION, NOT EVIDENCE")
    P("=" * 104)

    # ---------------------------------------------------------------- D5 first
    bbo_path = os.path.join(os.path.dirname(RUN), "MSBBO_V1_20260828", "src", "bbo_v1.py")
    got = sha(bbo_path)
    P(f"    D5  frozen bbo_v1.py sha256 {got}")
    assert got == FROZEN_BBO_SHA, "ALPHA DEFINITION CHANGED - abort"
    P("    D5  PASS - the alpha definition this run imports is byte-identical to the frozen one")

    # ---------------------------------------------------------------- build the frozen population
    files = sorted(glob.glob(os.path.join(B.V2, "s*.parquet")))
    P("")
    P(f"    building the frozen discovery population from {len(files)} session files ...")
    parts, srcsha, manifest = [], {}, []
    for fp in files:
        x = B.session_features(fp)                       # SEAL filter lives inside, unmodified
        if x is None:
            continue
        parts.append(x)
        srcsha[os.path.basename(fp)] = sha(fp)
        manifest.append(x["session"].iloc[0])
    d = pd.concat(parts, ignore_index=True)

    meta = ("t", "mid", "long_gross", "short_gross", "wait_ok", "session")
    feats = [c for c in d.columns if c not in meta]      # EXACT frozen order, from the frozen code
    d = d[d["wait_ok"] & d[feats].notna().all(axis=1)
          & d["long_gross"].notna() & d["short_gross"].notna()].copy()
    d = d.sort_values("t").reset_index(drop=True)

    # ---------------------------------------------------------------- D3 BLOCKING seal assertion
    tmax = pd.Timestamp(d["t"].max())
    P("")
    P(f"    D3  max training source timestamp {tmax}")
    assert tmax < pd.Timestamp(SEAL), f"SEAL VIOLATION {tmax} >= {SEAL}"
    P(f"    D3  PASS - strictly before the {SEAL} seal")

    X = np.nan_to_num(d[feats].values.astype(float), posinf=0, neginf=0)
    y = (d["long_gross"].values + (-d["short_gross"].values)) / 2.0
    sess = d["session"].values
    order = pd.unique(sess)
    P(f"    sessions {len(order)}   decisions {len(d):,}   features {len(feats)}")
    assert len(feats) == 20, f"expected the frozen 20 features, got {len(feats)}"
    P(f"    features (exact order): {', '.join(feats)}")

    # ================================================================ §8 FIDELITY: reproduce OOF
    P("")
    P("=" * 104)
    P("=== FIDELITY CHECK - reproduce the reported DISCOVERY figure from the unmodified module")
    P("=== (this closes the 0-byte log gap; it is NOT a new measurement)")
    P("=" * 104)
    blocks = np.array_split(order, B.N_FOLD + 1)
    ix, pr = B.oof(X, y, sess, blocks, lambda: Ridge(alpha=RIDGE_ALPHA))
    net_oof, act_oof = B.policy_pnl(pr, d.iloc[ix], 0.0)
    ss = pd.Series(net_oof).groupby(sess[ix]).sum()
    P(f"    OOF Ridge  ${ss.mean():>10,.2f}/session   net ${ss.sum():>12,.0f}   "
      f"sessions {len(ss)}   trade {100*np.mean(act_oof != 0):.1f}%")
    P(f"    reported in MSBBO_V1/REPORT.md: $5,124.76/session, net $245,989, 48 sessions")
    delta = abs(ss.mean() - 5124.76)
    P(f"    |difference| ${delta:,.4f}   ->  "
      f"{'REPRODUCED' if delta < 0.01 else '*** DOES NOT REPRODUCE ***'}")

    # ================================================================ THE DEPLOYMENT FIT
    P("")
    P("=" * 104)
    P("=== THE DEPLOYMENT FIT - the frozen primary estimator, fit ONCE on the whole population")
    P("=" * 104)
    mu, sd = X.mean(0), X.std(0)
    sd_fix = sd.copy()
    sd_fix[sd_fix == 0] = 1.0
    model = Ridge(alpha=RIDGE_ALPHA).fit((X - mu) / sd_fix, y)
    P(f"    Ridge(alpha={RIDGE_ALPHA})  fit on {len(d):,} decisions x {len(feats)} features")
    P(f"    intercept {model.intercept_:+.12e}")
    P("")
    P(f"    {'#':>3}  {'feature':<20} {'mean':>16} {'sd':>16} {'coef (z-units, $)':>20}")
    for j, f in enumerate(feats):
        P(f"    {j+1:>3}  {f:<20} {mu[j]:>16.8f} {sd[j]:>16.8f} {model.coef_[j]:>20.10f}")

    # ================================================================ SERIALIZE
    art = {
        "strategy_id": "MS-BBO-CANDIDATE-1-DEPLOY",
        "candidate_id": "MS-BBO-CANDIDATE-1",
        "created": "2026-08-28",
        "provenance_warning": (
            "This full fit was created AFTER the discovery candidate survived its gates, SOLELY to "
            "define the future executable object. Its historical in-sample performance has ZERO "
            "evidentiary weight and MUST NOT appear in any promotion argument."),
        "evidence_class": "DISCOVERY-GRADE ONLY - deployment definition adds no evidence",
        "live_enabled": False,
        "training": {
            "start": str(pd.Timestamp(d["t"].min())),
            "end": str(pd.Timestamp(d["t"].max())),
            "seal_assertion": f"max(training_source_timestamp) < {SEAL}",
            "n_sessions": int(len(order)),
            "n_decisions": int(len(d)),
            "session_manifest": [str(s) for s in order],
        },
        "model": {
            "family": "sklearn.linear_model.Ridge",
            "alpha": RIDGE_ALPHA,
            "fit_rule": "FULL FIT on ALL admissible consumed discovery decisions, exactly once",
            "feature_names_ordered": list(feats),
            "feature_mean": [float(v) for v in mu],
            "feature_std": [float(v) for v in sd],
            "zero_std_rule": "std_j == 0  ->  z_j := 0",
            "nan_inf_rule": ("np.nan_to_num on the raw feature matrix BEFORE standardisation: "
                             "nan->0, +inf->0, -inf->0 (matches the frozen runner exactly)"),
            "coef": [float(v) for v in model.coef_],
            "intercept": float(model.intercept_),
            "prediction_formula": "intercept + sum_j coef_j * (x_j - mean_j)/std_j",
        },
        "target": ("(long_gross + (-short_gross))/2 in dollars, where "
                   "long_gross=(bid_{t+h}-ask_t)*20, short_gross=(bid_t-ask_{t+h})*20"),
        "schedule": {"grid_s": B.GRID_S, "horizon_s": B.HORIZON_S,
                     "rth_start_et": B.RTH_START, "rth_end_et": B.RTH_END,
                     "decisions_per_session_expected": 331},
        "information_rule": {
            "features": "events with timestamp STRICTLY < t",
            "execution": "first quote at a DISTINCT timestamp > t (entry) and > t+h (exit)",
            "same_ms": "mean by side within one identical timestamp; row order NEVER used",
        },
        "execution": {"max_fill_wait_ms": B.MAX_FILL_WAIT_MS, "tick": B.TICK,
                      "point_value": B.DPP, "commission_rt": B.COMMISSION_RT},
        "policy": {"threshold": "spread_tk*TICK*DPP + COMMISSION_RT + 2*extra_ticks*TICK*DPP",
                   "action": "LONG if pred > thr; SHORT if pred < -thr; else FLAT"},
        "stress_ladder_ticks_per_side": list(B.STRESS_TICKS),
        "blocked": ["quote size", "true aggressor side", "queue position",
                    "quote-then-trade causality inside a millisecond",
                    "displayed-depth absorption", "BBO size imbalance", "true microprice",
                    "depth sweep"],
        "versions": {"python": sys.version.split()[0], "numpy": np.__version__,
                     "pandas": pd.__version__, "sklearn": sklearn.__version__},
        "hashes": {"bbo_v1.py": got, "deploy_fit.py": sha(os.path.abspath(__file__)),
                   "spec.md": sha(os.path.join(RUN, "SPEC.md")),
                   "source_files": srcsha},
    }
    mp = os.path.join(RUN, "model.json")
    blob = json.dumps(art, indent=2, sort_keys=True).encode("utf-8")
    with open(mp, "wb") as fh:
        fh.write(blob)
    art_sha = hashlib.sha256(blob).hexdigest()
    with open(os.path.join(RUN, "model.sha256"), "w", encoding="utf-8") as fh:
        fh.write(art_sha + "  model.json\n")

    # ================================================================ D1 / D2 SELF-PARITY
    P("")
    P("=" * 104)
    P("=== D1 / D2  SELF-PARITY - sklearn.predict() vs the authoritative model.json formula")
    P("=" * 104)
    J = json.loads(open(mp, "r", encoding="utf-8").read())["model"]
    jm = np.array(J["feature_mean"])
    js = np.array(J["feature_std"])
    jc = np.array(J["coef"])
    ji = J["intercept"]
    assert list(J["feature_names_ordered"]) == list(feats), "FEATURE ORDER DRIFT"

    Xj = np.nan_to_num(d[J["feature_names_ordered"]].values.astype(float), posinf=0, neginf=0)
    Z = np.zeros_like(Xj)
    nz = js != 0
    Z[:, nz] = (Xj[:, nz] - jm[nz]) / js[nz]            # zero-sd -> z := 0, per the declared rule
    pred_json = ji + Z @ jc
    pred_skl = model.predict((X - mu) / sd_fix)

    dmax = float(np.max(np.abs(pred_json - pred_skl)))
    P(f"    D1  max |sklearn.predict - model.json formula|  {dmax:.3e}   tolerance {D1_TOL:.0e}")
    d1 = dmax <= D1_TOL
    P(f"    D1  {'PASS' if d1 else '*** FAIL ***'}")

    _, act_j = B.policy_pnl(pred_json, d, 0.0)
    _, act_s = B.policy_pnl(pred_skl, d, 0.0)
    agree = int((act_j == act_s).sum())
    P(f"    D2  action parity  {agree:,} / {len(d):,}  = {100*agree/len(d):.6f} %")
    P(f"    D2  {'PASS - exact' if agree == len(d) else '*** FAIL ***'}")
    for v, nm in ((1, "LONG"), (-1, "SHORT"), (0, "FLAT")):
        P(f"        {nm:<6} json {int((act_j == v).sum()):>7,}   sklearn {int((act_s == v).sum()):>7,}")

    # D4
    P("")
    re_sha = sha(mp)
    P(f"    D4  model.json sha256 {art_sha}")
    P(f"    D4  re-hash of the written file  {re_sha}")
    P(f"    D4  {'PASS' if re_sha == art_sha else '*** FAIL ***'}")

    ok = d1 and agree == len(d) and re_sha == art_sha
    P("")
    P("=" * 104)
    P(f"=== DEPLOYMENT FREEZE {'COMPLETE - MS-BBO-CANDIDATE-1-DEPLOY EXISTS' if ok else 'FAILED'}")
    P("=== The object is now uniquely determined for any future decision instant.")
    P("=== EVIDENCE CLASS UNCHANGED: DISCOVERY-GRADE ONLY.  LIVE ENABLED: NO.")
    P("=" * 104)

    # per-decision predictions, for the streaming-parity reference
    pd.DataFrame({"session": sess, "t": d["t"].values, "pred": pred_json,
                  "spread_tk": d["spread_tk"].values, "action": act_j,
                  "long_gross": d["long_gross"].values,
                  "short_gross": d["short_gross"].values}).to_parquet(
        os.path.join(OUT, "deploy_predictions.parquet"), index=False)
    d[list(feats) + ["session", "t"]].to_parquet(
        os.path.join(OUT, "batch_features.parquet"), index=False)
    _fh.close()
    assert ok, "deployment self-parity FAILED"


if __name__ == "__main__":
    main()
