"""G0 - PORT VALIDATION. The parameterized bench, instantiated on NQ with NQ's own
PV/commission/spread and the identical mechanism, MUST reproduce the committed P1/PCT weekly
figures (CURRENT_BASELINE A / WE_W103): weekly $1393.57, maxDD $22930.67, t 4.1636, trades 2401,
spread rate $14.436/ctrRT. Assert FIRST; RAISE on failure; write out/port_validation.txt.
"""
from __future__ import annotations

import os
import sys
import time as _t

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import xinst_bench as XB                                            # noqa: E402
from we_lab import spread_profile                                  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "out")
os.makedirs(OUT, exist_ok=True)

# committed P1/PCT targets (WE_W103_CONSOLIDATE/out/components.csv)
TGT = dict(weekly=1393.5736634670018, maxdd=22930.665852795442, t=4.1636115325867715,
           trades=2401, rate=14.436482661004954)
NQ = "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet"


def main():
    t0 = _t.time()
    lines = []

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True); lines.append(s)

    P("=" * 100)
    P("=== G0 PORT VALIDATION - reproduce NQ P1/PCT with the parameterized bench")
    P("=" * 100)
    D, bnd = XB.load_substrate(NQ, "NQ")
    P(f"  substrate: {bnd['n_bars']:,} bars / {bnd['n_sess']:,} sessions  "
      f"{bnd['first_sess']} -> {bnd['last_sess']}   dropped>=seal {bnd['n_dropped']}")
    P(f"  SEAL: max session {bnd['last_sess']} < 2026-08-01 ? {bnd['seal_ok']}")
    if not bnd["seal_ok"]:
        raise RuntimeError("SEAL VIOLATION on NQ load")

    tr, meta = XB.build_p1pct(D, PV=20.0, comm=4.36, halt_pts=XB.NQ_HALT_PTS,
                              tgt_pts=XB.NQ_TGT_PTS, smin_pts=None, smax_pts=None,
                              stopm_pts=None, win_a="2022-07-01", win_b="2026-08-01")
    P(f"  P1/PCT rebuilt: {len(tr):,} in-window trades, {meta['n_entries']:,} entries, "
      f"size-2 share {100*meta['size2_share']:.1f}%   [{_t.time()-t0:.0f}s]")

    prof = spread_profile()
    net, ct, rate, ntr = XB.net_series(D, tr, PV=20.0, tick=0.25,
                                       spread_model=("nq_profile", prof),
                                       sess_in=meta["sess_in"], i_of=meta["i_of"])
    w, wk = XB.weekly(D, net, meta["sess_in"])
    pan = XB.panel(w)
    P("")
    P(f"  {'metric':<12}{'REBUILT':>18}{'COMMITTED':>18}{'rel diff':>12}")
    checks = []
    for k, obs in (("weekly", pan["weekly"]), ("maxdd", pan["maxdd"]), ("t", pan["t"]),
                   ("trades", float(ntr)), ("rate", rate)):
        exp = TGT[k]
        rd = abs(obs - exp) / abs(exp) if exp else float("nan")
        P(f"  {k:<12}{obs:>18.6f}{exp:>18.6f}{100*rd:>11.4f}%")
        checks.append((k, obs, exp, rd))

    # tolerance: reproduce to rounding. weekly/maxdd/rate within 0.1%, t within 0.1%, trades exact-ish
    tol = {"weekly": 1e-3, "maxdd": 1e-3, "t": 1e-3, "rate": 1e-3, "trades": 2 / 2401}
    ok = all(rd <= tol[k] for k, _, _, rd in checks)

    # cross-check: rebuilt mem/bmom/tilt vs the committed cache (bit-identity of the ratchet)
    cache = os.path.join(XB.REPO, "runs", "WE_W76_FORWARD2026", "out", "mem_ext.npz")
    cache_note = ""
    if os.path.exists(cache):
        z = np.load(cache)
        cm, cb, ctl = z["mem"], z["bmom"], z["tilt"]
        if cm.shape == meta["mem"].shape:
            dm = int((cm != meta["mem"]).sum())
            db = int((cb != meta["bmom"]).sum())
            dt = int((ctl != meta["tilt"]).sum())
            cache_note = (f"mem mismatch {dm} / {cm.size}, bmom {db} / {cb.size}, "
                          f"tilt {dt} / {ctl.size}")
            P("")
            P(f"  RATCHET BIT-IDENTITY vs committed cache: {cache_note}")
        else:
            cache_note = f"shape differs {cm.shape} vs {meta['mem'].shape}"
            P(f"  cache shape {cm.shape} vs rebuilt {meta['mem'].shape} (start-of-warmup offset)")

    P("")
    P(f"  PORT VALIDATION: {'PASS - reproduces P1/PCT to rounding' if ok else 'FAIL'}")
    P(f"  [done {_t.time()-t0:.0f}s]")
    with open(os.path.join(OUT, "port_validation.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    if not ok:
        raise SystemExit("G0 FAILED: bench does not reproduce P1/PCT. All ports void.")
    return ok


if __name__ == "__main__":
    main()
