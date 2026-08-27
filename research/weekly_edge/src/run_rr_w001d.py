"""RR_W001 addendum - the ACTIVITY-MATCHED RANDOM ABSTENTION PLACEBO.

Spec: secondary_measurements. This is a CONTROL, not a new hypothesis. It can only make the
finding weaker or clearer, never stronger.

W121 is the reason this exists: entry-count caps sat at the 0.0/4.0/1.0/0.0th percentile of a
count-matched random-halt placebo - removing the same entries AT RANDOM beat removing them by the
rule. Any abstention curve in this repo must be read against that placebo or it is not evidence.

The oracle curve is EX-POST by construction, so it must beat the placebo. The question is BY HOW
MUCH, because that margin is the part of the uplift that is SELECTION rather than simply trading
less.
"""
from __future__ import annotations

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
from run_we_w26 import fills_daily                                        # noqa: E402
from run_we_w37 import causal_score                                       # noqa: E402
from run_we_w39 import WIN                                                # noqa: E402
from run_we_w97 import votes                                              # noqa: E402
from run_we_w98 import gfills, TICKV                                      # noqa: E402
from we_fastctx import fast_build_context                                 # noqa: E402
from run_rr_w001 import gfills_sess, runs_in, score_to_size               # noqa: E402

OUT = os.path.join(ROOT, "runs", "RR_W001_ACTION_VALUE_LEDGER", "out")
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
W82OUT = os.path.join(ROOT, "runs", "WE_W82_FILLAUDIT", "out")
A, B = np.datetime64("2022-07-01"), np.datetime64("2026-08-01")
HALT, TARGET = 1300.0, 1000.0
FRACS = [0.05, 0.10, 0.20, 0.30]
NDRAW = 40
SEED = 1001
_t0 = _time.time()
fh = open(os.path.join(OUT, "rr_w001d.txt"), "w", encoding="utf-8")


def P_(*a):
    print(*a, flush=True)
    print(*a, file=fh)
    fh.flush()


def main():
    rng = np.random.default_rng(SEED)
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    X = fast_build_context(D)
    zz = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    vl, _ = votes(D, zz["mem"], zz["bmom"], zz["tilt"], X, zz["bmom"])
    p = vl.astype(np.int8)
    n, tarr, sid, fb, lb = D["n"], D["t"], D["sid"], D["fb"], D["lb"]
    NS = D["n_sess"]
    sess_lo = {int(sid[i]): int(i) for i in np.flatnonzero(fb)}
    sess_hi = {int(sid[i]): int(i) for i in np.flatnonzero(lb)}
    prof = pd.read_csv(os.path.join(W82OUT, "spread_by_minute.csv")).set_index("mod")["sp_tk"]
    prof_d = {int(k): float(v) for k, v in prof.items()}
    modarr = np.array([pd.Timestamp(x).hour * 60 + pd.Timestamp(x).minute for x in tarr])
    spk = np.array([prof_d.get(int(m), 3.0) for m in modarr])

    def net_res(t):
        return t["pnl"] - t["u"] * TICKV * (spk[t["eti"]] + spk[t["xti"]]) / 2.0

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    in_win = np.zeros(NS, bool)
    for s in range(NS):
        if A <= tarr[sess_lo[s]] < B:
            in_win[s] = True
    bb = fills_daily(D, p, halt=HALT, target=TARGET)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    s_, _ = causal_score(X, ee, window=WIN)
    sz = score_to_size(s_, n)
    BASE = []
    for s in range(NS):
        BASE.extend(gfills_sess(D, p, sz, sess_lo[s], sess_hi[s]))
    bin_ = np.array([in_win[int(sid[t["eti"]])] for t in BASE])
    base_total = float(sum(net_res(t) for t, m in zip(BASE, bin_) if m))
    base_ctrmin = float(sum(t["u"] * (t["xti"] - t["eti"]) for t, m in zip(BASE, bin_) if m))

    L = pd.read_csv(os.path.join(OUT, "ledger_p1pct.csv"))
    LW = L[L["in_window_session"]].reset_index(drop=True)
    dav = LW["delta_action_value"].to_numpy()
    run_of = {}
    for _, row in LW.iterrows():
        eti = i_of(row["decision_ts"])
        s = int(sid[eti])
        r = next((r for r in runs_in(p, fb, sess_lo[s], sess_hi[s]) if r[0] <= eti - 1 <= r[1]),
                 None)
        run_of[int(str(row["event_id"]).split("-")[1])] = r
    keys_all = [int(str(e).split("-")[1]) for e in LW["event_id"]]

    def joint(keys):
        p2 = p.copy()
        for k in keys:
            r = run_of.get(k)
            if r is not None:
                p2[r[0]:r[1] + 1] = 0
        new_ent = []
        for s in range(NS):
            new_ent.extend(t["eti"] for t in gfills_sess(D, p2, None, sess_lo[s], sess_hi[s]))
        ee2 = np.array([e for e in new_ent if A <= tarr[e] < B], dtype=np.int64)
        s2_, _ = causal_score(X, ee2, window=WIN)
        TR = gfills(D, p2, size_at_entry=score_to_size(s2_, n), halt=HALT, target=TARGET,
                    per_ctr=True)
        TR = [dict(t, eti=i_of(t["et"]), xti=i_of(t["xt"])) for t in TR]
        TR = [t for t in TR if in_win[int(sid[t["eti"]])]]
        net = float(sum(net_res(t) for t in TR))
        cm = float(sum(t["u"] * (t["xti"] - t["eti"]) for t in TR))
        eq = np.cumsum([net_res(t) for t in TR])
        dd = float((np.maximum.accumulate(eq) - eq).max()) if len(eq) else 0.0
        return net, len(TR), cm, dd

    P_("=" * 122)
    P_("=== RR_W001d - ACTIVITY-MATCHED RANDOM ABSTENTION PLACEBO (the W121 template)")
    P_("=== A CONTROL, not a new hypothesis. The oracle is ex-post so it MUST win; the question is")
    P_("=== by how much, because that margin is the SELECTION and the rest is just trading less.")
    P_("=" * 122)
    P_(f"    baseline net ${base_total:,.0f}   trades {int(bin_.sum()):,}   "
       f"contract-minutes {base_ctrmin:,.0f}")
    P_(f"    {NDRAW} random draws per fraction, seed {SEED}")
    P_("")
    P_(f"{'f':>6}{'ORACLE net':>14}{'ORACLE uplift':>15}{'RANDOM mean':>14}{'RANDOM p95':>13}"
       f"{'pctile':>9}{'SELECTION $':>14}{'sel share':>11}{'exposure':>11}")
    rows = []
    ordr = np.argsort(dav)
    for f in FRACS:
        k = int(round(f * len(dav)))
        onet, otr, ocm, odd = joint([keys_all[j] for j in ordr[:k]])
        rnet, rcm = [], []
        for _ in range(NDRAW):
            pick = rng.choice(len(dav), size=k, replace=False)
            rn, _rt, rc, _rd = joint([keys_all[j] for j in pick])
            rnet.append(rn)
            rcm.append(rc)
        rnet = np.array(rnet)
        pct = 100.0 * float((rnet < onet).mean())
        sel = onet - float(rnet.mean())
        rows.append(dict(f=f, k=k, oracle_net=onet, oracle_uplift=onet - base_total,
                         random_mean=float(rnet.mean()), random_p95=float(np.percentile(rnet, 95)),
                         pctile=pct, selection=sel,
                         sel_share=sel / max(onet - base_total, 1e-9),
                         oracle_ctrmin=ocm, random_ctrmin=float(np.mean(rcm)),
                         oracle_dd=odd, base_ctrmin=base_ctrmin))
        P_(f"{f:>6.2f}{onet:>14,.0f}{onet - base_total:>15,.0f}{rnet.mean():>14,.0f}"
           f"{np.percentile(rnet, 95):>13,.0f}{pct:>8.1f}%{sel:>14,.0f}"
           f"{100 * sel / max(onet - base_total, 1e-9):>10.1f}%"
           f"{100 * ocm / base_ctrmin:>10.1f}%")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "matched_random_placebo.csv"), index=False)
    P_("")
    P_("    READING. 'SELECTION $' is ORACLE minus the MEAN of the activity-matched random draws:")
    P_("    the part of the uplift that comes from choosing WHICH events to drop rather than from")
    P_("    dropping that many events at all. 'sel share' is that part as a fraction of the total")
    P_("    oracle uplift; the remainder is exposure reduction and is NOT information.")
    P_("    'exposure' is the oracle arm's contract-minutes as a share of baseline, so a reader can")
    P_("    see directly how much risk was removed to get the uplift.")
    P_(f"[{_time.time() - _t0:.0f}s] done")
    fh.close()


if __name__ == "__main__":
    main()
