"""P0 ENGINEERING - the PER-BAR Python reference export for WeeklyEdgeXMConflict_v1.cs.

Owner directive V4 amendment section 3. This is not a wave; it is the artifact the Strategy
Analyzer parity check is compared against, and the comparison is on SIGNAL and DECISION states,
not only on final P&L (runs/WE_W52_NINJASCRIPT/REPORT.md: "export per-bar components, not just
trades"; primary comparison is the decision series).

It also settles one convention that the Python research object and NinjaTrader cannot both hold:

    the research object entered at the 09:46 bar's OPEN (next-bar-open, correct)
    but exited at the 15:45 bar's CLOSE (same-bar-close, a DIFFERENT convention).

NinjaTrader with Calculate.OnBarClose can only do next-bar-open for both. The two exit
conventions are computed side by side here and the difference is measured rather than assumed.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w51 import session_frames                                    # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "research", "weekly_edge", "ninjascript", "reference")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
EXPORT_FROM = np.datetime64("2025-08-01")        # per-bar export window (keeps the CSV sane)
TICKV = 5.0
ANCH, DEC, ENTM, EXITM, EXITNB = 571, 585, 586, 945, 946
SIG_LB, SIG_MIN, MAXSTALE = 60, 20, 3
XM = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
      "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
      "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}


def main():
    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    o, c, h, l = D["o"], D["c"], D["h"], D["l"]
    st_, _, _ = session_frames(D)
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    NS = D["n_sess"]
    sdate = pd.to_datetime(D["sess_date"])
    win = np.array([A <= tarr[st_[s]] < B for s in range(NS)])
    nq = pd.DataFrame({"time": pd.to_datetime(tarr), "nq": c}).set_index("time")
    XD, XTS = {}, {}
    for k, path in XM.items():
        d_ = pd.read_parquet(os.path.join(ROOT, path), columns=["time", "close"])
        d_["time"] = pd.to_datetime(d_["time"])
        j = nq.join(d_.set_index("time")["close"].rename(k), how="left")
        XD[k] = j[k].to_numpy()
        XTS[k] = ~np.isnan(XD[k])          # a NaN here IS the missing-bar case

    def at(mv, arr, uo=False):
        r = np.full(NS, np.nan); ix = np.full(NS, -1, np.int64)
        m_ = mod == mv
        r[sid[m_]] = (o[m_] if uo else arr[m_]); ix[sid[m_]] = np.flatnonzero(m_)
        return r, ix
    pa, ia = at(ANCH, o, True)
    pdc, idc = at(DEC, c)
    pe, ie = at(ENTM, o, True)
    px_close, ix_c = at(EXITM, c)
    px_nbo, ix_n = at(EXITNB, o, True)

    # --- the composite, built session by session so the sigma history is provably causal
    HIST = {k: [] for k in XM}
    drive = np.zeros(NS); comp = np.full(NS, np.nan)
    conflict = np.zeros(NS, np.int8); desired = np.zeros(NS, np.int8)
    disq = np.zeros(NS, bool)
    for s in range(NS):
        # NOTE the `win` test is deliberately NOT here. The sigma history must warm up on every
        # session the platform loads, including the pre-window months, exactly as the Analyzer
        # will. Gating the history on `win` cost 4 trades against the canonical object.
        if not np.isfinite(pa[s]) or not np.isfinite(pdc[s]):
            continue
        ok = True
        for k in XM:
            if ia[s] < 0 or idc[s] < 0 or not XTS[k][ia[s]] or not XTS[k][idc[s]]:
                ok = False
        if not ok:
            disq[s] = True                  # the staleness / missing-bar disqualification
            continue
        if not win[s]:
            # outside the study window: still feed the sigma history, never signal
            for k in XM:
                HIST[k].append(np.log(XD[k][idc[s]] / XD[k][ia[s]]))
            continue
        drive[s] = np.sign(pdc[s] - pa[s])
        acc, cnt = 0.0, 0
        for k in XM:
            r_ = np.log(XD[k][idc[s]] / XD[k][ia[s]])
            hh = HIST[k]
            if len(hh) >= SIG_MIN:
                w = hh[-SIG_LB:]
                sg = float(np.std(w, ddof=1))
                if sg > 1e-12:
                    acc += r_ / sg; cnt += 1
            hh.append(r_)                   # appended AFTER use - today never in its own sigma
        if cnt:
            comp[s] = acc / cnt
            xs = np.sign(comp[s])
            if xs != 0 and drive[s] != 0 and xs != drive[s]:
                conflict[s] = 1; desired[s] = int(drive[s])

    cst_c = COMM_RT + TICKV * (float(prof.loc[ENTM]) + float(prof.loc[EXITM])) / 2.0
    cst_n = COMM_RT + TICKV * (float(prof.loc[ENTM]) + float(prof.loc[EXITNB])) / 2.0
    take = (desired != 0) & np.isfinite(pe) & np.isfinite(px_close) & np.isfinite(px_nbo)
    desired = np.where(take, desired, 0).astype(np.int8)   # a signal with no tradeable bar is not a trade
    pnl_close = np.where(take & np.isfinite(px_close),
                         desired * (px_close - pe) * PV - cst_c, 0.0)
    pnl_nbo = np.where(take & np.isfinite(px_nbo),
                       desired * (px_nbo - pe) * PV - cst_n, 0.0)
    print("=" * 110)
    print("=== THE EXIT-CONVENTION QUESTION, settled by measurement rather than assumption")
    print("=" * 110)
    nA = int((take & np.isfinite(px_close)).sum()); nB = int((take & np.isfinite(px_nbo)).sum())
    print(f"    research convention  exit at the CLOSE of the 15:45 bar  N={nA}  "
          f"${pnl_close.sum():>12,.0f}  ${pnl_close[take].mean():>8,.0f}/trade")
    print(f"    NT8-consistent       exit at the OPEN of the 15:46 bar   N={nB}  "
          f"${pnl_nbo.sum():>12,.0f}  ${pnl_nbo[take].mean():>8,.0f}/trade")
    d = pnl_nbo[take] - pnl_close[take]
    print(f"    difference: ${d.sum():,.0f} total, ${d.mean():.2f}/trade, "
          f"sd ${d.std(ddof=1):.2f}, |max| ${np.abs(d).max():,.0f}")
    print(f"    -> {100*abs(d.sum())/max(abs(pnl_close.sum()),1e-9):.2f} % of net. The NinjaScript "
          f"uses the NT8-consistent form; both are exported.")
    print(f"    sessions disqualified by a missing/stale secondary bar: {int(disq.sum())}")

    # --- decision-level reference: one row per session. THIS is what parity compares.
    rows = []
    for s in range(NS):
        if not win[s]:
            continue
        rows.append(dict(session_date=sdate[s].strftime("%Y-%m-%d"),
                         anchor_px=pa[s], decision_px=pdc[s], entry_px=pe[s],
                         exit_px_close1545=px_close[s], exit_px_open1546=px_nbo[s],
                         nq_drive=drive[s], broad_composite=comp[s],
                         conflict_flag=int(conflict[s]), desired_direction=int(desired[s]),
                         disqualified=int(disq[s]),
                         pnl_research=pnl_close[s], pnl_nt8_convention=pnl_nbo[s]))
    DEC_ = pd.DataFrame(rows)
    DEC_.to_csv(os.path.join(OUT, "xm_reference_decisions.csv"), index=False)
    print(f"\n    wrote xm_reference_decisions.csv  {len(DEC_):,} sessions "
          f"({int((DEC_.desired_direction != 0).sum())} trades)")

    # --- per-bar reference over the export window
    m = (tarr >= EXPORT_FROM) & (tarr < B)
    idxs = np.flatnonzero(m)
    pos = np.zeros(n, np.int8); ent = np.zeros(n, np.int8); ex = np.zeros(n, np.int8)
    real = np.zeros(n)
    run = 0.0
    for s in np.flatnonzero(desired != 0):
        a_, b_ = int(ie[s]), int(ix_n[s])
        if a_ < 0 or b_ < 0:
            continue
        pos[a_:b_] = desired[s]
        ent[a_] = desired[s]; ex[b_] = 1
    cum = 0.0
    for i in range(n):
        if ex[i]:
            s = int(sid[i]); cum += pnl_nbo[s]
        real[i] = cum
    esm = np.full(n, np.nan); rtym = np.full(n, np.nan); ymm = np.full(n, np.nan)
    for s in range(NS):
        if ia[s] < 0 or not win[s]:
            continue
        a_ = int(ia[s]); b_ = int(st_[s + 1]) if s + 1 < NS else n
        for k, tgt in (("ES", esm), ("RTY", rtym), ("YM", ymm)):
            base = XD[k][a_]
            if base and base > 0:
                tgt[a_:b_] = np.log(XD[k][a_:b_] / base)
    PB = pd.DataFrame(dict(
        timestamp=pd.to_datetime(tarr[idxs]).strftime("%Y-%m-%d %H:%M:%S"),
        nq_open=o[idxs], nq_high=h[idxs], nq_low=l[idxs], nq_close=c[idxs],
        es_close=XD["ES"][idxs], es_move=esm[idxs],
        rty_close=XD["RTY"][idxs], rty_move=rtym[idxs],
        ym_close=XD["YM"][idxs], ym_move=ymm[idxs],
        nq_drive=drive[sid[idxs]], broad_composite=comp[sid[idxs]],
        conflict_flag=conflict[sid[idxs]], desired_direction=desired[sid[idxs]],
        decision_ready=(mod[idxs] >= DEC).astype(np.int8),
        entry_request=ent[idxs], exit_request=ex[idxs],
        position=pos[idxs], realized_pnl=real[idxs]))
    p_ = os.path.join(OUT, "xm_reference_bars.csv")
    PB.to_csv(p_, index=False, float_format="%.6f")
    print(f"    wrote xm_reference_bars.csv       {len(PB):,} bars "
          f"({pd.to_datetime(tarr[idxs]).min()} -> {pd.to_datetime(tarr[idxs]).max()}, "
          f"{os.path.getsize(p_)/1e6:.1f} MB)")
    print("\n    PARITY PROTOCOL (WE_W52's, binding): compare the DECISION series first.")
    print("      >= 99 % agreement on desired_direction AND trade counts within 2 %  -> VALIDATED")
    print("      90-99 %  -> report bar-by-bar and classify every mismatch")
    print("      < 90 %   -> the C# is not the object")
    print("    Expect a cold-start difference: the sigma history needs 20 prior sessions, so an")
    print("    Analyzer window shorter than that will arm later than this reference does.")


if __name__ == "__main__":
    main()
