"""WE_W119 - THE BOOK_LOSS_LEDGER. Where does the research book actually lose DOLLARS?

Spec: runs/WE_W119_BOOKLOSS/spec.yaml, committed BEFORE this ran (5677472).

W117 answered this at WEEKLY resolution on 87 observations and produced a PHENOTYPE. Section 12
says the DOLLAR decomposition must come before any further feature search, because it sets EVI:
do not spend a wave solving a loss source worth 5 % of the damage.

EXPOST_ columns are DIAGNOSIS ONLY and are prefixed so they can never be mistaken for inputs
(section 13). Causal columns each carry their exact availability minute; nothing later than 11:48
is recorded as causal.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import classify, session_frames                          # noqa: E402
from run_we_w97 import votes                                             # noqa: E402
from run_we_w98 import gfills, arm_kw                                    # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W119_BOOKLOSS", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
W110O = os.path.join(ROOT, "runs", "WE_W110_XMDIVERSE", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
TICKV = 5.0
RTH0, RTHC, DEC1148 = 571, 960, 708
HALT, TARGET = 1300.0, 1000.0
XMP = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
       "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
       "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "bookloss.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    o, c, h, l, v = D["o"], D["c"], D["h"], D["l"], D["v"]
    st_, en_, _ = session_frames(D)
    klass = classify(D, st_, en_)
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    NS = D["n_sess"]
    sdate = pd.to_datetime(D["sess_date"])
    iso = sdate.isocalendar()
    wkall = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    win = np.array([A <= tarr[st_[s]] < B for s in range(NS)])
    sess_in = np.flatnonzero(win)
    P_(f"    {len(sess_in):,} in-window sessions [{_time.time()-t0:.0f}s]")

    def at(mv, arr=None, uo=False):
        r = np.full(NS, np.nan)
        m = mod == mv
        r[sid[m]] = (o[m] if uo else (c[m] if arr is None else arr[m]))
        return r

    # ------------------------------------------------------------------ P1/PCT
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))
    vl, _ = votes(D, mem, bmom, tilt, X, bmom)
    p1 = vl.astype(np.int8)
    bb = fills_daily(D, p1, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, ee, window=WIN)
    tr = gfills(D, p1, np.where(sc >= 3, 2, 1).astype(np.int8), **arm_kw("PCT", 1.183))
    wq = {}
    for x in tr:
        for ts in (x["et"], x["xt"]):
            pp = pd.Timestamp(ts); m2 = pp.hour * 60 + pp.minute
            wq[m2] = wq.get(m2, 0.0) + x["u"]
    rP = TICKV * sum(float(prof.get(m2, 3.0)) * q for m2, q in wq.items()) / max(sum(wq.values()), 1)
    P_(f"    P1/PCT {len(tr):,} trades, spread ${rP:.2f}/ctrRT [{_time.time()-t0:.0f}s]")

    p1_pnl = np.zeros(NS); p1_gross = np.zeros(NS); p1_cost = np.zeros(NS)
    p1_n = np.zeros(NS, int); p1_cm = np.zeros(NS); p1_max = np.zeros(NS, int)
    boxfire = np.zeros(NS, bool)
    bysess = {}
    for x in tr:
        s = int(sid[i_of(x["et"])])
        bysess.setdefault(s, []).append(x)
    for s, xs in bysess.items():
        if not win[s]:
            continue
        spnl = 0.0
        for x in xs:
            u = int(x["u"])
            net = x["pnl"] - rP * u                        # gfills already charged commission
            p1_pnl[s] += net
            p1_gross[s] += x["pnl"] + COMM_RT * u
            p1_cost[s] += COMM_RT * u + rP * u
            p1_n[s] += 1
            p1_cm[s] += u * max((pd.Timestamp(x["xt"]) - pd.Timestamp(x["et"])).total_seconds()
                                / 60.0, 0.0)
            p1_max[s] = max(p1_max[s], u)
            spnl += x["pnl"] / u                            # PCT: per-contract box
            if spnl <= -HALT or spnl >= TARGET:
                boxfire[s] = True

    # ------------------------------------------------------------------ XM
    TF = pd.read_csv(os.path.join(W110O, "trade_features.csv"))
    TF["date"] = pd.to_datetime(TF["date"]).dt.date
    d2s = {sdate[s].date(): s for s in range(NS)}
    xm_pnl = np.zeros(NS); xm_dir = np.zeros(NS); xm_act = np.zeros(NS, bool)
    for _, r_ in TF.iterrows():
        s = d2s.get(r_["date"])
        if s is None or not win[s]:
            continue
        xm_pnl[s] += float(r_["pnl"]); xm_act[s] = True
        xm_dir[s] = 1.0 if r_["is_long"] > 0.5 else -1.0
    P_(f"    XM {int(xm_act.sum()):,} active sessions")

    # ------------------------------------------------------------------ the book
    wp = pd.Series(p1_pnl[sess_in]).groupby(wkall[sess_in]).sum()
    wx = pd.Series(xm_pnl[sess_in]).groupby(wkall[sess_in]).sum()
    sp, sx = wp.std(ddof=1), wx.std(ddof=1)
    w1 = (1 / sp) / ((1 / sp) + (1 / sx))
    book = w1 * p1_pnl + (1 - w1) * xm_pnl
    P_(f"    book = {w1:.3f} x P1/PCT + {1-w1:.3f} x XM  (inverse-vol on weekly, as W110/W117)")

    # ------------------------------------------------------------------ market + causal
    rth_o = at(RTH0, uo=True); rth_c = at(RTHC)
    move = rth_c - rth_o
    m = (mod >= RTH0) & (mod <= RTHC)
    ii = np.flatnonzero(m)
    sh = np.full(NS, -np.inf); sl = np.full(NS, np.inf); vol = np.zeros(NS)
    np.maximum.at(sh, sid[ii], h[ii]); np.minimum.at(sl, sid[ii], l[ii])
    np.add.at(vol, sid[ii], v[ii])
    rng_pts = np.where(sh > -np.inf, sh - sl, np.nan)

    onh = np.full(NS, -np.inf); onl = np.full(NS, np.inf)
    om = (mod >= 1081) | (mod < RTH0)
    np.maximum.at(onh, sid[om], h[om]); np.minimum.at(onl, sid[om], l[om])
    on_rng = np.where(onh > -np.inf, onh - onl, np.nan)
    lastc = at(1020); prevc = np.full(NS, np.nan); prevc[1:] = lastc[:-1]
    gap = rth_o - prevc
    drive = at(585) - rth_o
    nqf = pd.DataFrame({"time": pd.to_datetime(tarr)}).set_index("time")
    acc = np.zeros(NS); cnt = np.zeros(NS)
    for k, pth in XMP.items():
        f = os.path.join(ROOT, pth)
        if not os.path.exists(f):
            continue
        d_ = pd.read_parquet(f, columns=["time", "close"]); d_["time"] = pd.to_datetime(d_["time"])
        arr = nqf.join(d_.set_index("time")["close"].rename(k), how="left")[k].to_numpy()
        aa, bbv = at(RTH0, arr=arr), at(585, arr=arr)
        with np.errstate(divide="ignore", invalid="ignore"):
            rr = np.log(bbv / aa)
        sg = pd.Series(rr).rolling(60, min_periods=20).std().shift(1).to_numpy()
        zz = rr / np.maximum(sg, 1e-12)
        g = np.isfinite(zz); acc[g] += zz[g]; cnt[g] += 1
    comp = np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan)
    path = np.zeros(NS)
    mm = (mod >= RTH0) & (mod <= DEC1148)
    jj = np.flatnonzero(mm)
    np.add.at(path, sid[jj], np.abs(np.r_[0.0, np.diff(c)])[jj])
    peff = np.abs(at(DEC1148) - rth_o) / np.maximum(path, 1e-9)

    L = pd.DataFrame(dict(
        date=[sdate[s].date() for s in range(NS)], session=np.arange(NS), week=wkall,
        p1_pnl=p1_pnl, xm_pnl=xm_pnl, book_pnl=book,
        p1_gross=p1_gross, p1_cost=p1_cost, xm_active=xm_act, xm_dir=xm_dir,
        p1_trades=p1_n, p1_contract_minutes=p1_cm, p1_max_size=p1_max, p1_box_fired=boxfire,
        rth_open=rth_o, rth_close=rth_c, rth_move_pts=move, rth_range_pts=rng_pts,
        session_volume=vol,
        EXPOST_CLASS=klass,
        c0931_on_range=on_rng, c0931_gap=gap,
        c0945_drive=drive, c0945_composite_z=comp,
        c1148_path_eff=peff,
    ))[win]
    L.to_csv(os.path.join(OUT, "book_loss_ledger.csv"), index=False)
    P_(f"    ledger written: {len(L)} rows x {L.shape[1]} cols "
       f"-> out/book_loss_ledger.csv  [{_time.time()-t0:.0f}s]")
    P_("    causal columns carry their availability minute in the name: c0931_ / c0945_ / c1148_.")
    P_("    EXPOST_CLASS is DIAGNOSIS ONLY and is prefixed so it cannot be mistaken for an input.")

    # ================================================================== decomposition
    d = L
    lose = d["book_pnl"] < 0
    tot_loss = float(d.loc[lose, "book_pnl"].sum())
    P_("")
    P_("=" * 124)
    P_("=== SECTION 12 DECOMPOSITION - dollars AND frequency. OVERLAPPING LENSES, not a partition.")
    P_("=" * 124)
    P_(f"    {int(lose.sum())} losing sessions of {len(d)} ({100*lose.mean():.1f} %). "
       f"Total book loss on them: ${tot_loss:,.0f}. Book net over the window: "
       f"${d['book_pnl'].sum():,.0f}")
    big = d["rth_move_pts"].abs() >= d["rth_move_pts"].abs().quantile(0.90)
    p1t = d["p1_trades"] > 0
    p1l = d["p1_pnl"] < 0
    xml = d["xm_active"] & (d["xm_pnl"] < 0)
    CAT = {
        "A_P1_WRONGWAY  (P1 traded & lost, session DOWN)": p1t & p1l & (d["rth_move_pts"] < 0),
        "B_P1_WHIPSAW   (P1 traded & lost, session UP)": p1t & p1l & (d["rth_move_pts"] > 0),
        "C_XM_LOSS      (XM active & lost)": xml,
        "D_BOTH         (both legs lost)": p1l & xml,
        "E_NO_ENGINE    (neither active, top-decile |move|)": (~p1t) & (~d["xm_active"]) & big,
        "G_RISK_TRUNC   (P1 session box fired)": d["p1_box_fired"],
    }
    P_("")
    P_(f"{'lens':<50}{'sessions':>10}{'% of all':>10}{'book $ there':>15}"
       f"{'% of total loss':>17}")
    for k, msk in CAT.items():
        mm2 = msk & lose
        dol = float(d.loc[mm2, "book_pnl"].sum())
        P_(f"{k:<50}{int(mm2.sum()):>10}{100*mm2.mean():>9.1f}%{dol:>15,.0f}"
           f"{100*dol/max(abs(tot_loss),1e-9):>16.1f}%")
    cost_l = float(d.loc[lose, "p1_cost"].sum())
    gross_l = float(d.loc[lose, "p1_gross"].sum())
    P_(f"{'F_COST         (P1 friction on losing sessions)':<50}{'-':>10}{'-':>10}"
       f"{-cost_l:>15,.0f}{100*cost_l/max(abs(tot_loss),1e-9):>16.1f}%")
    P_(f"    (P1 gross on losing sessions ${gross_l:,.0f}; friction ${cost_l:,.0f} = "
       f"{100*cost_l/max(abs(gross_l),1e-9):.1f} % of |gross|)")
    P_("")
    P_("    OVERLAPS, stated rather than hidden:")
    P_(f"        A and B are mutually exclusive by construction: "
       f"{int((CAT['A_P1_WRONGWAY  (P1 traded & lost, session DOWN)'] & CAT['B_P1_WHIPSAW   (P1 traded & lost, session UP)']).sum())} sessions in both")
    for a_, b_ in (("D_BOTH         (both legs lost)", "C_XM_LOSS      (XM active & lost)"),
                   ("G_RISK_TRUNC   (P1 session box fired)",
                    "A_P1_WRONGWAY  (P1 traded & lost, session DOWN)"),
                   ("G_RISK_TRUNC   (P1 session box fired)",
                    "B_P1_WHIPSAW   (P1 traded & lost, session UP)")):
        P_(f"        {a_.split()[0]} ∩ {b_.split()[0]}: {int((CAT[a_] & CAT[b_] & lose).sum())} sessions")

    # ------------------------------------------------------------------ worst decile
    P_("")
    P_("=" * 124)
    P_("=== WORST DECILE of sessions - does tail damage share a cause with typical damage?")
    P_("=" * 124)
    q10 = d["book_pnl"].quantile(0.10)
    tail = d["book_pnl"] <= q10
    P_(f"    {int(tail.sum())} sessions at or below ${q10:,.0f}; they carry "
       f"${float(d.loc[tail,'book_pnl'].sum()):,.0f} = "
       f"{100*float(d.loc[tail,'book_pnl'].sum())/max(abs(tot_loss),1e-9):.1f} % of all loss")
    P_(f"{'lens':<50}{'in worst decile':>17}{'share of decile':>18}{'vs all-loss share':>20}")
    for k, msk in CAT.items():
        a_ = float((msk & tail).sum()) / max(int(tail.sum()), 1)
        b_ = float((msk & lose).sum()) / max(int(lose.sum()), 1)
        P_(f"{k:<50}{int((msk & tail).sum()):>17}{100*a_:>17.1f}%{100*(a_-b_):>+19.1f}pp")

    # ------------------------------------------------------------------ expost class + control
    P_("")
    P_("=" * 124)
    P_("=== EXPOST_CLASS on losing sessions, WITH its matched unconditional control (W108 rule)")
    P_("=" * 124)
    P_(f"{'class':<14}{'losing sess':>13}{'share':>9}{'ALL sess share':>17}{'difference':>13}"
       f"{'book $ there':>15}")
    for k in ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED"):
        mk = d["EXPOST_CLASS"] == k
        a_ = float((mk & lose).sum()) / max(int(lose.sum()), 1)
        b_ = float(mk.mean())
        P_(f"{k:<14}{int((mk & lose).sum()):>13}{100*a_:>8.1f}%{100*b_:>16.1f}%"
           f"{100*(a_-b_):>+12.1f}pp{float(d.loc[mk & lose,'book_pnl'].sum()):>15,.0f}")

    # ------------------------------------------------------------------ exposure
    P_("")
    P_("=" * 124)
    P_("=== EXPOSURE - is the book losing while OVER-exposed or UNDER-exposed?")
    P_("=" * 124)
    P_(f"{'':<22}{'losing sessions':>18}{'winning sessions':>19}{'difference':>13}")
    for lab, col in (("P1 trades", "p1_trades"), ("P1 contract-minutes", "p1_contract_minutes"),
                     ("P1 max size", "p1_max_size"), ("P1 box fired rate", "p1_box_fired"),
                     ("XM active rate", "xm_active"),
                     ("|RTH move| pts", None), ("RTH range pts", "rth_range_pts")):
        x = d["rth_move_pts"].abs() if col is None else d[col].astype(float)
        P_(f"{lab:<22}{x[lose].mean():>18.3f}{x[~lose].mean():>19.3f}"
           f"{x[lose].mean()-x[~lose].mean():>+13.3f}")

    # ------------------------------------------------------------------ weekly reconciliation
    P_("")
    P_("=" * 124)
    P_("=== SESSION vs WEEKLY - did W117's weekly phenotype survive at session resolution?")
    P_("=" * 124)
    P_("    W117 (weekly, n=87): TREND-UP share 0.167 losing vs 0.238 winning (p 0.005);")
    P_("    REVERSAL 0.299 vs 0.230 (p 0.011); TREND-DOWN 0.147 vs 0.143 (p 0.880).")
    P_("    Session-resolution equivalents are the EXPOST_CLASS table above. Compare directly.")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
