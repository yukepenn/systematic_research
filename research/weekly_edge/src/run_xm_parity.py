"""XM_CONFLICT STRATEGY ANALYZER PARITY - DECISION SERIES FIRST, DOLLARS SECOND.

Spec: runs/WE_XM_PARITY_20260827/spec.yaml, committed BEFORE this ran.

Directive section 21: "Never compare only final dollars." The decision series IS the object. This
script reduces the strategy's own per-bar export to the 09:45 decision bar of each session and
compares nq_drive / broad_composite / conflict_flag / desired_direction against the committed
sequential reference, session by session, before it looks at a single P&L figure.

Section 23: the reference is the SEQUENTIAL 346-trade variant - the one the C# can implement - not
the 348-trade vectorised pandas headline.
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
from run_we_w01 import ROOT                                              # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_XM_PARITY_20260827", "out")
REF = os.path.join(ROOT, "research", "weekly_edge", "ninjascript", "reference",
                   "xm_reference_decisions.csv")
LEDGER = os.path.join(OUT, "we_xm_xmparity.csv")


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "parity.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    P_("=" * 122)
    P_("=== XM_CONFLICT PARITY - NinjaTrader Strategy Analyzer vs the committed SEQUENTIAL reference")
    P_("=== DECISION SERIES FIRST (section 21/22). Dollars are reported last and are not a gate.")
    P_("=" * 122)

    R = pd.read_csv(REF)
    R["session_date"] = pd.to_datetime(R["session_date"]).dt.date
    P_(f"    reference: {len(R):,} sessions {min(R.session_date)} -> {max(R.session_date)}; "
       f"{int((R.desired_direction!=0).sum())} non-zero directions "
       f"({int((R.desired_direction>0).sum())} long / {int((R.desired_direction<0).sum())} short), "
       f"{int(R.disqualified.sum())} disqualified")

    # ---------------------------------------------------------------- reduce the per-bar ledger
    usecols = ["timestamp", "nq_drive", "broad_composite", "conflict_flag",
               "desired_direction", "decision_ready", "entry_request", "exit_request",
               "position", "realized_pnl"]
    P_(f"    reading the per-bar export ({os.path.getsize(LEDGER)/1e6:.0f} MB) in chunks ...")
    keep = []
    for ch in pd.read_csv(LEDGER, usecols=usecols, chunksize=400_000):
        ts = pd.to_datetime(ch["timestamp"])
        mod = ts.dt.hour * 60 + ts.dt.minute
        k = ch[mod == 9 * 60 + 45].copy()
        if len(k):
            k["ts"] = ts[mod == 9 * 60 + 45]
            keep.append(k)
    N = pd.concat(keep, ignore_index=True)
    # session date: the RTH 09:45 bar belongs to the session that STARTED 18:00 the previous day,
    # but the reference labels sessions by their RTH calendar date, which is this bar's own date.
    N["session_date"] = N["ts"].dt.date
    N = N.drop_duplicates("session_date", keep="last")
    P_(f"    NT8 09:45 decision bars: {len(N):,} sessions  [{_time.time()-t0:.0f}s]")
    N[["session_date", "nq_drive", "broad_composite", "conflict_flag", "desired_direction",
       "decision_ready"]].to_csv(os.path.join(OUT, "nt8_decisions.csv"), index=False)

    M = R.merge(N, on="session_date", suffixes=("_ref", "_nt"), how="inner")
    P_(f"    sessions present in BOTH: {len(M):,} of {len(R):,} reference sessions")

    # ---------------------------------------------------------------- decision-series comparison
    P_("")
    P_("=" * 122)
    P_("=== DECISION SERIES, session by session (this is the object)")
    P_("=" * 122)
    dd = (M["desired_direction_ref"].astype(int) == M["desired_direction_nt"].astype(int))
    cf = (M["conflict_flag_ref"].astype(int) == M["conflict_flag_nt"].astype(int))
    ds = np.sign(M["nq_drive_ref"].astype(float)) == np.sign(M["nq_drive_nt"].astype(float))
    bc = (M["broad_composite_ref"].astype(float) - M["broad_composite_nt"].astype(float)).abs()
    P_(f"{'field':<28}{'agreement':>14}{'disagreeing sessions':>24}")
    P_(f"{'desired_direction':<28}{100*dd.mean():>13.3f}%{int((~dd).sum()):>24,}")
    P_(f"{'conflict_flag':<28}{100*cf.mean():>13.3f}%{int((~cf).sum()):>24,}")
    P_(f"{'sign(nq_drive)':<28}{100*ds.mean():>13.3f}%{int((~ds).sum()):>24,}")
    P_(f"{'broad_composite |diff|':<28}{'mean %.6f' % bc.mean():>14}{'max %.6f' % bc.max():>24}")

    nz_ref = int((M["desired_direction_ref"] != 0).sum())
    nz_nt = int((M["desired_direction_nt"] != 0).sum())
    P_("")
    P_(f"    non-zero directions: reference {nz_ref:,}   NT8 {nz_nt:,}   "
       f"delta {100*(nz_nt-nz_ref)/max(nz_ref,1):+.2f} %")
    P_(f"    reference long/short {int((M.desired_direction_ref>0).sum())}/"
       f"{int((M.desired_direction_ref<0).sum())}   "
       f"NT8 long/short {int((M.desired_direction_nt>0).sum())}/"
       f"{int((M.desired_direction_nt<0).sum())}")

    bad = M[~dd]
    if len(bad):
        P_("")
        P_(f"    EVERY disagreeing session, classified (section 22 forbids averaging these away):")
        cols = ["session_date", "desired_direction_ref", "desired_direction_nt",
                "conflict_flag_ref", "conflict_flag_nt", "nq_drive_ref", "nq_drive_nt",
                "broad_composite_ref", "broad_composite_nt", "disqualified", "decision_ready"]
        bad[cols].to_csv(os.path.join(OUT, "decision_mismatches.csv"), index=False)
        for _, r in bad.head(40).iterrows():
            P_(f"        {r.session_date}  dir ref {int(r.desired_direction_ref):+d} vs nt "
               f"{int(r.desired_direction_nt):+d} | conflict {int(r.conflict_flag_ref)}/"
               f"{int(r.conflict_flag_nt)} | drive {r.nq_drive_ref:+.1f}/{r.nq_drive_nt:+.1f} | "
               f"comp {r.broad_composite_ref:+.4f}/{r.broad_composite_nt:+.4f} | "
               f"disq {int(r.disqualified)} | ready {int(r.decision_ready)}")
        if len(bad) > 40:
            P_(f"        ... {len(bad)-40} more in decision_mismatches.csv")

    # ---------------------------------------------------------------- dollars, reported LAST
    P_("")
    P_("=" * 122)
    P_("=== DOLLARS - reported LAST and NOT a gate (section 21)")
    P_("=" * 122)
    d = json.loads(open(os.path.join(OUT, "nt8_raw_xm.json"), encoding="utf-8").read())
    rr = d["result"]
    T = pd.DataFrame([dict(et=pd.Timestamp(t["entry"]["time"]),
                           d=1 if t["entry"]["market_position"] == "Long" else -1,
                           pnl=float(t["ProfitCurrency"])) for t in rr["trades"]])
    T["session_date"] = T["et"].dt.date
    lo, hi = min(R.session_date), max(R.session_date)
    TW = T[(T.session_date >= lo) & (T.session_date <= hi)]
    P_(f"    NT8 full-run trades {len(T):,} (from 2022-01-03); "
       f"IN REFERENCE WINDOW {len(TW):,}, net ${TW.pnl.sum():,.0f}")
    P_(f"    reference sequential  {nz_ref:,} trades, "
       f"net ${R.pnl_nt8_convention.sum():,.0f} (nt8 exit convention) / "
       f"${R.pnl_research.sum():,.0f} (research exit convention)")
    P_(f"    NT8 long/short trades {int((TW.d>0).sum())}/{int((TW.d<0).sum())}")

    # ---------------------------------------------------------------- gates
    P_("")
    P_("=" * 122)
    P_("=== GATES - every clause coded")
    P_("=" * 122)
    g = [("G1", "desired_direction agreement >= 99 %", f"{100*dd.mean():.3f} %", dd.mean() >= 0.99),
         ("G2", "trade counts within 2 % of sequential 346",
          f"{len(TW):,} vs {nz_ref:,} = {100*abs(len(TW)-nz_ref)/nz_ref:.2f} %",
          abs(len(TW) - nz_ref) / nz_ref <= 0.02),
         ("G3", "conflict_flag agreement >= 99 %", f"{100*cf.mean():.3f} %", cf.mean() >= 0.99),
         ("G4", "sign(nq_drive) agreement >= 99 %", f"{100*ds.mean():.3f} %", ds.mean() >= 0.99),
         ("G5", "two-sided on both sides",
          f"{int((TW.d>0).sum())} long / {int((TW.d<0).sum())} short",
          int((TW.d > 0).sum()) > 50 and int((TW.d < 0).sum()) > 50)]
    P_(f"{'gate':<6}{'spec':<46}{'observed':>30}{'verdict':>10}")
    for gg, spec, obsv, ok in g:
        P_(f"{gg:<6}{spec:<46}{obsv:>30}{('PASS' if ok else 'FAIL'):>10}")
    passed = all(x[3] for x in g)
    P_("")
    P_(f"    VERDICT: {'VALIDATED' if passed else 'NOT VALIDATED - classify every mismatch'}")
    pd.DataFrame([dict(gate=x[0], spec=x[1], observed=x[2], verdict="PASS" if x[3] else "FAIL")
                  for x in g]).to_csv(os.path.join(OUT, "gates.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
