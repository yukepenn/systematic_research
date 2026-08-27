"""P1/PCT STRATEGY ANALYZER PARITY - ENGINEERING RECONCILIATION, NOT A RESEARCH WAVE.

Spec: runs/WE_P1PCT_PARITY_20260827/spec.yaml, committed BEFORE this ran.

Phase 1 rebuilds the Python P1/PCT reference by IMPORTING run_we_w98.gfills with per_ctr=True -
the PCT arm exactly as W98 defined it - rather than reimplementing it, so a divergence here cannot
be a transcription bug in the reference itself.

Phase 2 compares it against the NinjaTrader Strategy Analyzer run trade-by-trade.

COST CONVENTION (declared in the spec, restated because it is the single easiest way to produce a
false mismatch): the reference is COMMISSION ONLY. gfills already charges COMM_RT per contract and
nothing else. Research's $14.44/ctrRT modelled spread is NOT applied on either side.
"""
from __future__ import annotations

import json
import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, COMM_RT                                     # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w97 import votes                                             # noqa: E402
from run_we_w98 import gfills                                            # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_P1PCT_PARITY_20260827", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")


def nt8_trades(path):
    """NT8 job JSON -> DataFrame of round-turn trades, commission included by the engine."""
    d = json.loads(open(path, encoding="utf-8").read())
    r = d["result"]
    rows = []
    for t in r["trades"]:
        e, x = t["entry"], t["exit"]
        rows.append(dict(
            et=pd.Timestamp(e["time"]), xt=pd.Timestamp(x["time"]),
            d=1 if e["market_position"] == "Long" else -1,
            u=int(t["Quantity"]), epx=float(e["price"]), xpx=float(x["price"]),
            pnl=float(t["ProfitCurrency"])))
    T = pd.DataFrame(rows).sort_values("et").reset_index(drop=True)
    return T, r["performance"]["all"], r["trace"]


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "parity.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    P_("=" * 122)
    P_("=== P1/PCT PARITY - NinjaTrader Strategy Analyzer vs the Python research object")
    P_("=== ENGINEERING RECONCILIATION. Nothing is selected, tuned or promoted here.")
    P_("=" * 122)

    # ================================================================= phase 1: reference
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, fb = D["n"], D["t"], D["sid"], D["fb"]
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    st = np.zeros(D["n_sess"], np.int64); st[sid[fb]] = np.flatnonzero(fb)
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    P_(f"    substrate {n:,} bars / {D['n_sess']:,} sessions; "
       f"in-window {len(sess_in):,} sessions  [{_time.time()-t0:.0f}s]")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    vl, _ = votes(D, mem, bmom, tilt, X, bmom)
    p = vl.astype(np.int8)
    bb = fills_daily(D, p, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    s_, _ = causal_score(X, ee, window=WIN)
    sz = np.where(s_ >= 3, 2, 1).astype(np.int8)
    PY = gfills(D, p, size_at_entry=sz, halt=1300, target=1000, per_ctr=True)
    R = pd.DataFrame([dict(et=pd.Timestamp(x["et"]), xt=pd.Timestamp(x["xt"]),
                           d=x["d"], u=x["u"], pnl=x["pnl"]) for x in PY])
    R["in_win"] = [in_win[int(sid[i_of(t)])] for t in R["et"]]
    RW = R[R["in_win"]].drop(columns="in_win").reset_index(drop=True)
    RW.to_csv(os.path.join(OUT, "py_trades_p1pct.csv"), index=False)
    P_(f"    PYTHON P1/PCT reference: {len(R):,} trades total, {len(RW):,} in-window "
       f"[{_time.time()-t0:.0f}s]")

    # ================================================================= phase 2: NT8
    NT, perf, trace = nt8_trades(os.path.join(OUT, "nt8_raw_p1pct.json"))
    NTC, perfC, _ = nt8_trades(os.path.join(OUT, "nt8_raw_p1v3.json"))
    NT.to_csv(os.path.join(OUT, "nt8_trades_p1pct.csv"), index=False)
    NTW = NT[(NT["et"] >= pd.Timestamp("2022-07-01")) & (NT["et"] < pd.Timestamp("2026-08-01"))]
    NTW = NTW.reset_index(drop=True)
    NTCW = NTC[(NTC["et"] >= pd.Timestamp("2022-07-01"))
               & (NTC["et"] < pd.Timestamp("2026-08-01"))].reset_index(drop=True)
    P_("")
    P_("    NT8 trace:")
    for t in trace:
        P_(f"        {t}")
    P_("")
    P_(f"    NT8 P1/PCT: {len(NT):,} serialized trades, {len(NTW):,} in-window; "
       f"engine TradesCount {perf['TradesCount']:,}, net ${perf['NetProfit']:,.2f}")
    P_(f"    NT8 P1_v3 CONTROL: {len(NTC):,} serialized, {len(NTCW):,} in-window; "
       f"engine TradesCount {perfC['TradesCount']:,}, net ${perfC['NetProfit']:,.2f}")

    # ================================================================= headline table
    def stats(T):
        wk = T["et"].dt.isocalendar()
        key = wk["year"].astype(str) + "-W" + wk["week"].astype(str).str.zfill(2)
        w = T.groupby(key.to_numpy())["pnl"].sum()
        eq = T["pnl"].cumsum().to_numpy()
        dd = float((np.maximum.accumulate(eq) - eq).max()) if len(eq) else 0.0
        return dict(n=len(T), net=float(T["pnl"].sum()), sz2=float((T["u"] == 2).mean()),
                    weeks=len(w), wmean=float(w.mean()), dd=dd, w=w)

    a, b = stats(RW), stats(NTW)
    P_("")
    P_("=" * 122)
    P_("=== IN-WINDOW HEADLINE 2022-07-01 -> 2026-08-01, COMMISSION ONLY ON BOTH SIDES")
    P_("=" * 122)
    P_(f"{'':<34}{'PYTHON (research object)':>28}{'NT8 Strategy Analyzer':>26}{'delta':>16}")
    for lab, k, f in (("trades", "n", "{:,.0f}"), ("net $", "net", "${:,.0f}"),
                      ("size-2 share", "sz2", "{:.1%}"), ("weeks", "weeks", "{:,.0f}"),
                      ("weekly mean $", "wmean", "${:,.0f}"), ("max drawdown $", "dd", "${:,.0f}")):
        dl = (b[k] - a[k]) / a[k] * 100 if a[k] else float("nan")
        P_(f"{lab:<34}{f.format(a[k]):>28}{f.format(b[k]):>26}{dl:>15.2f}%")
    w = pd.concat([a["w"].rename("py"), b["w"].rename("nt")], axis=1).fillna(0.0)
    rho = float(w["py"].corr(w["nt"]))
    P_(f"{'weekly series correlation':<34}{'':>28}{rho:>26.4f}")

    # ================================================================= trade matching
    P_("")
    P_("=" * 122)
    P_("=== TRADE-BY-TRADE MATCH (the discriminating test: the 14-line diff perturbs the SCHEDULE)")
    P_("=" * 122)
    kp = set(zip(RW["et"].astype("int64"), RW["d"]))
    kn = set(zip(NTW["et"].astype("int64"), NTW["d"]))
    both = kp & kn
    P_(f"    entry-timestamp + direction matched : {len(both):,}")
    P_(f"    in PYTHON only                      : {len(kp - kn):,}")
    P_(f"    in NT8 only                         : {len(kn - kp):,}")
    mrate = len(both) / max(len(kp), 1)
    P_(f"    MATCHED RATE (of Python trades)     : {100*mrate:.3f} %")
    M = RW.merge(NTW, on=["et", "d"], suffixes=("_py", "_nt"))
    qty_ok = float((M["u_py"] == M["u_nt"]).mean()) if len(M) else float("nan")
    xt_ok = float((M["xt_py"] == M["xt_nt"]).mean()) if len(M) else float("nan")
    P_(f"    on matched trades: QUANTITY agrees  : {100*qty_ok:.3f} %")
    P_(f"    on matched trades: EXIT BAR agrees  : {100*xt_ok:.3f} %")
    if len(M):
        dpnl = (M["pnl_nt"] - M["pnl_py"]).abs()
        P_(f"    on matched trades: |pnl| diff       : mean ${dpnl.mean():,.2f}  "
           f"median ${dpnl.median():,.2f}  max ${dpnl.max():,.2f}")
    M.to_csv(os.path.join(OUT, "matched_trades.csv"), index=False)
    pd.DataFrame(sorted(kp - kn), columns=["et_ns", "d"]).to_csv(
        os.path.join(OUT, "python_only.csv"), index=False)
    pd.DataFrame(sorted(kn - kp), columns=["et_ns", "d"]).to_csv(
        os.path.join(OUT, "nt8_only.csv"), index=False)

    # ================================================================= control
    P_("")
    P_("=" * 122)
    P_("=== SECTION 18 CONTROL - does P1_v3 still reproduce W52's reference?")
    P_("=" * 122)
    c = stats(NTCW)
    P_(f"    W52 recorded P1_v3 on 2022-07 -> 2026-05: 1,948 NT8 trades, net $296,423")
    P_(f"    THIS RUN, P1_v3 on 2022-07 -> 2026-08 : {c['n']:,} NT8 trades, net ${c['net']:,.0f}")
    P_("    (the windows differ by two extra months, so these are consistent rather than equal;")
    P_("     the control's job is to prove the ENVIRONMENT still resolves and trades sanely)")

    # ================================================================= gates
    P_("")
    P_("=" * 122)
    P_("=== GATES - every clause coded, spec / observed / verdict (directive section 29 habit)")
    P_("=" * 122)
    g = [("G1", "in-window trade counts within 2 %",
          f"{a['n']:,} vs {b['n']:,} = {100*abs(b['n']-a['n'])/a['n']:.2f} %",
          abs(b["n"] - a["n"]) / a["n"] <= 0.02),
         ("G2", "matched rate (entry ts + direction) >= 99 %", f"{100*mrate:.3f} %", mrate >= 0.99),
         ("G3", "net P&L within 2 %, commission-only",
          f"${a['net']:,.0f} vs ${b['net']:,.0f} = {100*abs(b['net']-a['net'])/abs(a['net']):.2f} %",
          abs(b["net"] - a["net"]) / abs(a["net"]) <= 0.02),
         ("G4", "size-2 share within 3 pp",
          f"{100*a['sz2']:.1f} vs {100*b['sz2']:.1f} = {100*abs(b['sz2']-a['sz2']):.2f} pp",
          abs(b["sz2"] - a["sz2"]) <= 0.03),
         ("G5", "control P1_v3 resolves and trades", f"{c['n']:,} trades", c["n"] > 1500)]
    P_(f"{'gate':<6}{'spec':<46}{'observed':>34}{'verdict':>10}")
    for gg, spec, obsv, ok in g:
        P_(f"{gg:<6}{spec:<46}{obsv:>34}{('PASS' if ok else 'FAIL'):>10}")
    passed = all(x[3] for x in g)
    P_("")
    P_(f"    PARITY VERDICT: {'CERTIFIED' if passed else 'NOT CERTIFIED - localize per section 47'}")
    pd.DataFrame([dict(gate=x[0], spec=x[1], observed=x[2], verdict="PASS" if x[3] else "FAIL")
                  for x in g]).to_csv(os.path.join(OUT, "gates.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
