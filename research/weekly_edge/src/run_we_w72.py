"""WE_W72 - is B-MOM SPECIAL, or is the OR-GATE SLOT architectural?

Spec: runs/WE_W72_ORCHANNEL/spec.yaml (committed before this ran).

W67 decoded the object to `(>= k of NMEM net-long) OR (channel == +1 and >= 1 member)`.
W68 asked whether the 51 % dependence on B-MOM can be reduced FROM INSIDE and answered no.
This wave asks the question W68 never asked: does a DIFFERENT occupant of the OR slot work?

Everything except the occupant is held fixed - the Solar members, the range throttle, the delta
gate, the 32-config vote, the causal quality score, the session box, the fills. The arms are
produced by rebuilding the combiner from W66's cached (mem, bmom, tilt) with the bmom vector
swapped out, so no re-tuning of any kind is possible.
"""
from __future__ import annotations

import itertools
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
from run_we_w19 import QS                                                # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import sfills                                            # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import A, B                                              # noqa: E402
from run_we_w51c import setup, dd_profile                                # noqa: E402
from run_we_w66 import WIDE                                              # noqa: E402
from we_channels import build_channels, channel_stats, session_clock     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W72_ORCHANNEL", "out")
os.makedirs(OUT, exist_ok=True)
W66OUT = os.path.join(ROOT, "runs", "WE_W66_INNER", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
CUTS = (14, 16, 18, 10 ** 9)
DD_TARGET = 20245.0
SPLIT = pd.Timestamp("2022-01-01")


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "orchannel.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    # ================================================================= PHASE 0: substrate
    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}
    P_(f"=== modern substrate {n:,} bars, {D['n_sess']:,} sessions [{_time.time()-t0:.0f}s]")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sess_wk = np.array([wkmap[s] for s in range(D["n_sess"])])
    keys_w = sorted(set(sess_wk[sess_in]))
    wk_idx = np.array([keys_w.index(sess_wk[s]) for s in sess_in])
    NW = len(keys_w)
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    yrs = sorted(set(sdate.year))

    z = np.load(os.path.join(W66OUT, f"mem460_clamp_{D['n']}.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    idx_of = {v: k for k, v in enumerate(WIDE)}
    cols13 = {c: [idx_of[v] for v in L13 if v <= c] for c in CUTS}
    fb, sess_end = D["fb"], D["sess_end"]
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    flat = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")

    # ================================================================= channels
    CH = build_channels(D)
    agree = 100.0 * float((CH["X0v_bmom"] == bmom).mean())
    P_(f"\n=== CHANNEL BUILDER CHECK: vectorised X0v vs the engine's cached bmom -> "
       f"{agree:.3f} % of {n:,} bars agree")
    if agree < 99.0:
        P_("   *** builder disagrees with the engine by more than 1 % of bars. Every non-X0 "
           "channel inherits that construction, so the wave is VOID. ***")
    CH = {"X0_bmom(cached,INCUMBENT)": bmom, **CH}

    P_(f"\n=== PHASE 1: what each candidate occupant DOES (the exposure control)")
    P_(f"{'channel':<28}{'fire %':>9}{'long %':>9}{'runs':>9}{'mean run (min)':>17}")
    st_rows = []
    for k, v in CH.items():
        s = channel_stats(v, D)
        P_(f"{k:<28}{s['fire_pct']:>9.2f}{s['long_pct']:>9.1f}{s['runs']:>9,}"
           f"{s['mean_run']:>17.1f}")
        st_rows.append(dict(channel=k, **s))
    pd.DataFrame(st_rows).to_csv(os.path.join(OUT, "channel_stats.csv"), index=False)

    # ================================================================= object rebuild
    def ra(x):
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))

    def hyst(M):
        tgt = np.zeros(n, np.int8)
        for i in range(n):
            p = 0 if (i == 0 or fb[i]) else tgt[i - 1]
            g = p
            if flat[i]:
                g = 0
            elif p == 0:
                if not blocked[i]:
                    g = 1 if M[i] >= 3.0 else (-1 if M[i] <= -3.0 else p)
            elif p > 0:
                g = -1 if (M[i] <= -3.0 and not blocked[i]) else (0 if M[i] <= 1.0 else p)
            else:
                g = 1 if (M[i] >= 3.0 and not blocked[i]) else (0 if M[i] >= -1.0 else p)
            tgt[i] = g
        return tgt

    def target(cols, chan, w=2.83):
        s = mem[:, cols].sum(axis=1).astype(np.int32)
        nm = len(cols)
        T = np.clip(ra(s / float(nm) * 10.0), -10, 10)
        ag = (np.sign(s) == tilt) & (s != 0) & (tilt != 0)
        Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
        return hyst(0.7086 * Tp + w * chan.astype(float))

    def object_from(chan, w=2.83):
        tgs = [target(cols13[c], chan, w) for c in CUTS if len(cols13[c]) >= 3]
        vs = []
        for tg in tgs:
            for q in QS:
                okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
                for dg in (True, False):
                    a = okv & (X["dL"] if dg else True)
                    vs.append(np.where((tg > 0) & a, 1, 0).astype(np.int8))
        pos = (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)
        base = fills_daily(D, pos, halt=1300, target=1000)
        e = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
        if len(e) < 150:
            return None
        sc, _ = causal_score(X, e, window=WIN)
        sz = np.where(sc >= 3, 2, 1).astype(np.int8)
        trl = [x for x in fills_qexit(D, pos, sz, sc) if in_win[int(sid[i_of(x["et"])])]]
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in], trl, pos

    def met(sp, ntr, name, inmkt):
        cnt = np.bincount(wk_idx, minlength=NW) > 0
        v = np.bincount(wk_idx, weights=sp, minlength=NW)[cnt]
        dp = dd_profile(v)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        tr = sp != 0
        stk = max((len(list(g)) for kk, g in itertools.groupby(v < 0) if kk), default=0)
        return dict(arm=name, ntr=ntr, pts=float(sp.sum() / PV / max(len(sp), 1)),
                    inmkt=inmkt,
                    daypos=100 * float((sp > 0).mean()),
                    trdpos=100 * float((sp[tr] > 0).mean()) if tr.any() else 0.0,
                    wkpos=100 * float((v > 0).mean()), wstreak=int(stk),
                    medwk=float(np.median(v)) * k, weekly=float(v.mean()) * k,
                    dd_top5=dp["dd_mean_top5"] * k, ulcer=dp["ulcer"] * k,
                    worst=float(v.min()) * k)

    HDR = (f"{'arm':<28}{'trds':>7}{'pts':>7}{'inMkt%':>8}{'day+%':>7}{'trdD+%':>8}{'wk+%':>7}"
           f"{'wStrk':>7}{'medWk$':>9}{'weekly$':>10}{'top5DD':>9}{'ulcer':>8}{'worst$':>9}")

    def show(r, tag=""):
        P_(f"{r['arm']:<28}{r['ntr']:>7}{r['pts']:>7.2f}{r['inmkt']:>8.1f}{r['daypos']:>7.1f}"
           f"{r['trdpos']:>8.1f}{r['wkpos']:>7.1f}{r['wstreak']:>7}{r['medwk']:>9,.0f}"
           f"{r['weekly']:>10,.0f}{r['dd_top5']:>9,.0f}{r['ulcer']:>8,.0f}"
           f"{r['worst']:>9,.0f}{tag}")

    P_(f"\n{'='*140}\n=== PHASE 2: THE SUBSTITUTION. Only the OR-slot occupant changes.")
    P_(f"{'='*140}")
    P_(HDR)
    rows, ledger, peryear = [], {}, {}
    sess_yr = sdate.year.to_numpy()
    for name, chan in CH.items():
        r = object_from(chan)
        if r is None:
            P_(f"{name:<28}   (fewer than 150 entries - skipped)")
            continue
        sp, trl, pos = r
        m_ = met(sp, len(trl), name, 100.0 * float(pos[np.isin(sid, sess_in)].mean()))
        show(m_, "   <- INCUMBENT" if name.startswith("X0_") else "")
        rows.append(m_); ledger[name] = sp
        peryear[name] = {int(y): float(sp[sess_yr == y].sum() / PV / max((sess_yr == y).sum(), 1))
                         for y in yrs}
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "arms.csv"), index=False)
    np.savez_compressed(os.path.join(OUT, f"ledgers_{n}.npz"), **ledger)

    inc_pts = [r["pts"] for r in rows if r["arm"].startswith("X0_")][0]
    P_(f"\n   B1 GATE: incumbent {inc_pts:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(inc_pts - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")

    P_(f"\n=== PER YEAR (pts/session) ===")
    P_(f"{'arm':<28}" + "".join(f"{y:>9}" for y in yrs) + f"{'yrs>0':>8}")
    py_rows = []
    for name in ledger:
        d = peryear[name]
        P_(f"{name:<28}" + "".join(f"{d[y]:>9.2f}" for y in yrs)
           + f"{sum(1 for y in yrs if d[y] > 0):>8}")
        py_rows.append(dict(arm=name, **{str(y): d[y] for y in yrs}))
    pd.DataFrame(py_rows).to_csv(os.path.join(OUT, "peryear.csv"), index=False)

    # ================================================================= PHASE 3: ERA TEST
    P_(f"\n{'='*140}")
    P_("=== PHASE 3: EACH CHANNEL STANDALONE, +-1 with the object's own session box, on BOTH")
    P_("===          ERAS. This is the W69 table, run for every candidate occupant.")
    P_("===          The object's MEMBERS are fitted to the modern era, so the era comparison")
    P_("===          must be made on the channel alone - that is why this is standalone.")
    P_(f"{'='*140}")
    DD = load_deep("2006-01-05", "2026-05-29 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    nd = DD["n"]
    P_(f"   deep substrate {nd:,} bars {DD['t'][0]} -> {DD['t'][-1]}, "
       f"{DD['n_sess']:,} sessions [{_time.time()-t0:.0f}s]")
    hh_d, seg_d, inr_d, _ = session_clock(DD)
    flat_d = DD["t"] >= DD["sess_end"][DD["sid"]] - np.timedelta64(21 * 60, "s")
    CHD = build_channels(DD)
    sd_d = pd.to_datetime(DD["sess_date"])

    P_(f"\n{'channel':<28}{'era':<12}{'sess':>8}{'trades':>9}{'net $':>13}{'$/trd':>9}"
       f"{'t':>8}{'win%':>7}{'PF':>7}")
    era_rows = []
    for name, chan in CHD.items():
        dirs = np.where(flat_d, 0, chan).astype(np.int8)
        trl = sfills(DD, dirs, halt=1300.0, target=1000.0)
        if len(trl) < 100:
            continue
        et = pd.to_datetime([x["et"] for x in trl])
        pnl = np.array([x["pnl"] for x in trl])
        df = pd.DataFrame(dict(et=et, pnl=pnl))
        df.to_csv(os.path.join(OUT, f"era_{name}.csv"), index=False)
        for lab, m in (("2006-2021", df["et"] < SPLIT), ("2022-2026", df["et"] >= SPLIT)):
            q = df[m]
            if len(q) < 50:
                continue
            se = q["pnl"].std(ddof=1) / np.sqrt(len(q))
            gw = q.loc[q["pnl"] > 0, "pnl"].sum(); gl = -q.loc[q["pnl"] < 0, "pnl"].sum()
            nse = int(((sd_d >= (sd_d.min() if lab.startswith("2006") else SPLIT))
                       & (sd_d < (SPLIT if lab.startswith("2006")
                                  else pd.Timestamp("2027-01-01")))).sum())
            P_(f"{name:<28}{lab:<12}{nse:>8,}{len(q):>9,}{q['pnl'].sum():>13,.0f}"
               f"{q['pnl'].mean():>9,.1f}{q['pnl'].mean()/se:>8.2f}"
               f"{100*float((q['pnl']>0).mean()):>6.1f}%{(gw/gl if gl else np.nan):>7.3f}")
            era_rows.append(dict(channel=name, era=lab, sessions=nse, trades=len(q),
                                 net=float(q["pnl"].sum()), per_trade=float(q["pnl"].mean()),
                                 t=float(q["pnl"].mean() / se),
                                 pf=float(gw / gl) if gl else np.nan))
        P_("")
    E = pd.DataFrame(era_rows)
    E.to_csv(os.path.join(OUT, "eras.csv"), index=False)

    # ================================================================= PHASE 4: VERDICT
    P_(f"\n{'='*140}\n=== PHASE 4: THE PREREGISTERED DECISION RULE")
    P_(f"{'='*140}")
    old = E[E["era"] == "2006-2021"].set_index("channel")
    A_ = {r["arm"]: r for r in rows}
    P_(f"{'arm':<28}{'A: >=90% prod':>16}{'B: pre-2022 t>=1.65':>22}"
       f"{'pre-2022 $/trd':>17}{'passes':>10}")
    verdicts = []
    for name in ledger:
        p = A_[name]["pts"]
        a_ok = p >= 0.90 * inc_pts
        key = name if name in old.index else name.replace("X0_bmom(cached,INCUMBENT)",
                                                          "X0v_bmom")
        t_old = float(old.loc[key, "t"]) if key in old.index else np.nan
        pt_old = float(old.loc[key, "per_trade"]) if key in old.index else np.nan
        b_ok = (t_old >= 1.65) and (pt_old > 0)
        P_(f"{name:<28}{('YES' if a_ok else 'no') + f' ({p:.2f})':>16}"
           f"{('YES' if b_ok else 'no') + f' (t={t_old:.2f})':>22}{pt_old:>17,.1f}"
           f"{('A+B' if (a_ok and b_ok) else ('A' if a_ok else ('B' if b_ok else '-'))):>10}")
        verdicts.append(dict(arm=name, pts=p, passes_A=bool(a_ok), t_pre2022=t_old,
                             per_trade_pre2022=pt_old, passes_B=bool(b_ok)))
    V = pd.DataFrame(verdicts); V.to_csv(os.path.join(OUT, "verdict.csv"), index=False)

    both = V[V["passes_A"] & V["passes_B"] & ~V["arm"].str.startswith("X0")]
    onlyA = V[V["passes_A"] & ~V["arm"].str.startswith("X0")]
    P_("")
    if len(both):
        P_(f"   -> OUTCOME 1: a DURABLE occupant of the OR slot EXISTS: "
           f"{', '.join(both['arm'])}.")
        P_(f"      The 51 % dependence on an in-sample component is a CHOICE, not a property of")
        P_(f"      the architecture. Promoted to a preregistered head-to-head (W74). NOT adopted")
        P_(f"      here - the C null and a walk-forward are still owed.")
    elif len(onlyA):
        P_(f"   -> OUTCOME 2: the SLOT IS ARCHITECTURAL. {len(onlyA)} non-B-MOM occupants reach")
        P_(f"      >=90 % of production ({', '.join(onlyA['arm'])}), so the money is in HAVING a")
        P_(f"      second low-threshold channel, not in B-MOM. But none of them is durable")
        P_(f"      pre-2022 either, so no better occupant exists in this universe. The fragility")
        P_(f"      is a property of the ARCHITECTURE, which is a stronger disclosure than W68's.")
    else:
        P_(f"   -> OUTCOME 3: ONLY B-MOM reaches 90 % of production. The OR slot is not")
        P_(f"      architectural; B-MOM is genuinely special. The 51 % dependence is")
        P_(f"      irreducible from OUTSIDE the object as well as from inside it, and the")
        P_(f"      disclosure becomes permanent.")
    P_(f"\n=== STATUS: diagnostic. NOTHING ADOPTED. [{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
