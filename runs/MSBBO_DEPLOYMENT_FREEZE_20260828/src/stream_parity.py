"""BATCH -> STREAMING PARITY on consumed historical BBO data.  ENGINEERING, NOT EVIDENCE.

The question is NOT "are the two implementations correlated". Prediction rho 0.999 is not parity:
the policy is a threshold, so a tiny numerical disagreement flips a recorded ACTION, and the action
is what a shadow ledger stores as evidence.

    decision schedule       100 % identical intended timestamps
    features                per-feature max |batch - stream|, reported feature by feature
    prediction              numerical tolerance
    threshold               numerical tolerance
    ACTION                  100 % LONG/SHORT/FLAT parity            <-- the gate that matters
    entry / exit fills      numerical tolerance
    fill-timeout class      exact
    data_quality            exact

This run may NOT tune anything to improve parity. A mismatch is a defect in stream_engine.py.
"""
from __future__ import annotations

import glob
import os
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(RUN), "MSBBO_V1_20260828", "src"))
import bbo_v1 as B                                                      # noqa: E402
import stream_engine as S                                               # noqa: E402

OUT = os.path.join(RUN, "out")
_fh = open(os.path.join(OUT, "stream_parity.txt"), "w", encoding="utf-8")
TOL_F, TOL_P = 1e-6, 1e-6


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def main():
    P("=" * 104)
    P("=== BATCH -> STREAMING PARITY   (engineering fidelity, not evidence)")
    P("=" * 104)
    model = S.load_model()
    names = list(model["model"]["feature_names_ordered"])
    files = sorted(glob.glob(os.path.join(B.V2, "s*.parquet")))

    fmax = {n: 0.0 for n in names}
    tot = dict(rows=0, sched=0, act_ok=0, dq_ok=0, wait_ok=0, sess=0)
    pmax = tmax_ = fill_max = 0.0
    mism = []
    delays = []
    states = []

    for fp in files:
        bat = B.session_features(fp)                    # the frozen batch definition, unmodified
        if bat is None:
            continue
        d = pq.read_table(fp, columns=["bip", "time", "price", "volume"]).to_pandas()
        ti = d["time"].values.astype("datetime64[ns]").astype("int64")
        assert np.all(np.diff(ti) >= 0), f"{os.path.basename(fp)} timestamps not monotone"
        day = pd.Timestamp(d["time"].max()).normalize().value
        bip = d["bip"].values
        px = d["price"].values
        vol = d["volume"].values.astype(float)

        eng = S.StreamEngine(model, day)
        for k in range(len(ti)):
            eng.on_event(bip[k], ti[k], px[k], vol[k])
        rows = eng.finish()
        states.append(eng.max_state)

        st = pd.DataFrame([{**{n: r["feat"][j] for j, n in enumerate(names)},
                            "t": r["t"], "pred": r["pred"], "thr": r["thr"],
                            "action": r["action"], "long_gross": r["long_gross"],
                            "short_gross": r["short_gross"], "wait_ok": r["wait_ok"],
                            "dq": r["data_quality"],
                            "fin": r["fin_delay_ms"]} for r in rows])
        delays += [v for v in st["fin"].tolist() if v is not None and np.isfinite(v)]

        # ---- schedule
        same_sched = len(st) == len(bat) and np.array_equal(st["t"].values, bat["t"].values)
        tot["sched"] += int(same_sched)
        tot["sess"] += 1
        if not same_sched:
            P(f"    !! {os.path.basename(fp)} SCHEDULE MISMATCH {len(st)} vs {len(bat)}")
            continue

        # ---- features
        for n in names:
            a = bat[n].values.astype(float)
            b = st[n].values.astype(float)
            both = ~(np.isnan(a) | np.isnan(b))
            if (np.isnan(a) != np.isnan(b)).any():
                mism.append((os.path.basename(fp), n, "NaN pattern differs"))
            if both.any():
                fmax[n] = max(fmax[n], float(np.max(np.abs(a[both] - b[both]))))

        # ---- batch prediction through the SAME deployed model, for a like-for-like comparison
        Xb = np.nan_to_num(bat[names].values.astype(float), posinf=0, neginf=0)
        m = model["model"]
        mu, sd = np.array(m["feature_mean"]), np.array(m["feature_std"])
        Z = np.zeros_like(Xb)
        nz = sd != 0
        Z[:, nz] = (Xb[:, nz] - mu[nz]) / sd[nz]
        pb = float(m["intercept"]) + Z @ np.array(m["coef"])
        tb = bat["spread_tk"].values * B.TICK * B.DPP + B.COMMISSION_RT
        ab = np.where(pb > tb, 1, np.where(pb < -tb, -1, 0))

        pmax = max(pmax, float(np.nanmax(np.abs(pb - st["pred"].values))))
        tmax_ = max(tmax_, float(np.nanmax(np.abs(tb - st["thr"].values))))
        agree = int((ab == st["action"].values).sum())
        tot["act_ok"] += agree
        tot["rows"] += len(st)
        if agree != len(st):
            bad = np.where(ab != st["action"].values)[0][:5]
            for i in bad:
                mism.append((os.path.basename(fp), f"ACTION@{i}",
                             f"batch {ab[i]} stream {st['action'].values[i]} "
                             f"pred {pb[i]:.6f} vs {st['pred'].values[i]:.6f}"))

        for c in ("long_gross", "short_gross"):
            a, b = bat[c].values.astype(float), st[c].values.astype(float)
            both = ~(np.isnan(a) | np.isnan(b))
            if both.any():
                fill_max = max(fill_max, float(np.max(np.abs(a[both] - b[both]))))
        tot["wait_ok"] += int((bat["wait_ok"].values == st["wait_ok"].values).sum())

        # data_quality: the batch admissible set is wait_ok & all features present & fills present
        bq = np.where(~bat[names].notna().all(axis=1).values, "GAP",
                      np.where(bat[["long_gross", "short_gross"]].notna().all(axis=1).values == 0,
                               "NO_FILL",
                               np.where(~bat["wait_ok"].values, "FILL_TIMEOUT", "OK")))
        tot["dq_ok"] += int((bq == st["dq"].values).sum())

    P("")
    P(f"    sessions replayed {tot['sess']}   decisions {tot['rows']:,}")
    P("")
    P("=== 1. DECISION SCHEDULE")
    P(f"    identical intended timestamps: {tot['sched']}/{tot['sess']} sessions "
      f"= {100*tot['sched']/tot['sess']:.4f} %")
    P("")
    P("=== 2. FEATURES - per-feature max |batch - stream|")
    worst = sorted(fmax.items(), key=lambda kv: -kv[1])
    for n, v in worst:
        flag = "" if v <= TOL_F else "   *** EXCEEDS TOLERANCE ***"
        P(f"    {n:<20} {v:>12.3e}{flag}")
    P("")
    P("=== 3. PREDICTION / THRESHOLD / FILLS")
    P(f"    max |prediction difference|   {pmax:>12.3e}   tolerance {TOL_P:.0e}")
    P(f"    max |threshold difference|    {tmax_:>12.3e}")
    P(f"    max |fill P&L difference|     {fill_max:>12.3e}")
    P("")
    P("=== 4. ACTION PARITY  <-- the gate that matters")
    P(f"    {tot['act_ok']:,} / {tot['rows']:,} = {100*tot['act_ok']/max(tot['rows'],1):.6f} %")
    P("")
    P("=== 5. CLASSIFICATION PARITY (must be EXACT)")
    P(f"    fill-timeout (wait_ok)  {tot['wait_ok']:,}/{tot['rows']:,} = "
      f"{100*tot['wait_ok']/max(tot['rows'],1):.6f} %")
    P(f"    data_quality            {tot['dq_ok']:,}/{tot['rows']:,} = "
      f"{100*tot['dq_ok']/max(tot['rows'],1):.6f} %")
    P("")
    P("=== 6. RESOURCE BOUND - retained buckets, the whole point of the ring design")
    P(f"    max simultaneously retained buckets across all sessions: {max(states):,}")
    P(f"    median per session {int(np.median(states)):,}   "
      f"(a full session holds ~7,000,000 raw events)")
    P("")
    P("=== 7. BUCKET-FINALIZATION DELAY  (NOT alpha latency - directive s7)")
    if delays:
        dl = np.array(delays)
        P(f"    n {len(dl):,}   median {np.median(dl):.3f} ms   p95 {np.percentile(dl,95):.3f}   "
          f"p99 {np.percentile(dl,99):.3f}   max {dl.max():.3f}")
    P("")
    if mism:
        P(f"=== MISMATCH TABLE ({len(mism)} rows, first 40)")
        for r in mism[:40]:
            P(f"    {r[0]:<22} {r[1]:<22} {r[2]}")
    else:
        P("=== MISMATCH TABLE: EMPTY")
    ok = (tot["sched"] == tot["sess"] and tot["act_ok"] == tot["rows"]
          and tot["dq_ok"] == tot["rows"] and tot["wait_ok"] == tot["rows"]
          and pmax <= TOL_P and max(fmax.values()) <= TOL_F)
    P("")
    P("=" * 104)
    P(f"=== STREAMING PARITY {'PASS' if ok else '*** FAIL ***'}")
    P("=" * 104)
    _fh.close()
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
