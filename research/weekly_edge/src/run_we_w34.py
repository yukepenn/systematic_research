"""WE_W34 QUALITY (spec preregistered): size on NEW information; the leverage law's real test."""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, sm14_1m             # noqa: E402
from run_we_w03 import cd_signals                                        # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, weekly, sharpe                           # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w30 import position_series                                   # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W34_QUALITY", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260834)


def sized_fills(D, pos_arr, size_at_entry, halt=1300.0, target=1000.0):
    """Long-only fills where the size is read from size_at_entry at the ENTRY bar."""
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False
        want = int(pos_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped:
            want = 0
        if (want > 0) != (u > 0):
            if u > 0:
                pnl = u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += pnl
                if spnl <= -halt or (target is not None and spnl >= target):
                    stopped = True; want = 0
            if want > 0:
                u = int(size_at_entry[i]); epx, eti = o[i], i
                if u < 1:
                    u = 0
            else:
                u = 0
        if lb[i] and u > 0:
            pnl = u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            u = 0
    return trades


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    c, o, h, v = D["c"], D["o"], D["h"], D["v"]
    rng_, dmove, atr14, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)

    def lag_b(x):
        return np.concatenate([[True], x[:-1]])
    _, cd = cd_signals(D)
    dL = lag_b(cd >= 0)
    vs = []
    for mem in MEMBERS:
        tg = sm14_1m(D, 460, return_targets=True, volmults=MEMBERS[mem])
        for q in (None, 0.7, 0.8, 0.9):
            okv = np.ones(n, bool) if q is None else ((norm <= 0) | (ratio >= q))
            for dg in (True, False):
                a = okv & (dL if dg else True)
                vs.append(np.where((tg > 0) & a, 1, 0).astype(np.int8))
    frac = np.vstack(vs).mean(axis=0)
    pos = (frac >= 0.5).astype(np.int8)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), n - 1))
        return wkmap[int(D["sid"][i])]
    win = (tarr >= A) & (tarr < B)
    nsw = len(np.unique(D["sid"][win]))
    base_trl = fills_daily(D, pos, halt=1300, target=1000)
    d0 = weekly(base_trl, wk_of, A, B)
    s0, _, wp0 = sharpe(d0)
    p0 = np.array([x["pnl"] for x in base_trl if A <= np.datetime64(x["et"]) < B])
    ok_h = abs(s0 - 0.305) < 0.02 and abs(p0.sum() / PV / nsw - 10.62) < 0.6
    print(f"HARNESS: Sharpe {s0:.3f}, pts/session {p0.sum()/PV/nsw:.2f} -> "
          f"{'PASS' if ok_h else 'FAIL - VOID'}", flush=True)
    if not ok_h:
        return

    # --------- the five admitted features, as per-bar arrays (causal) ---------------------
    idx = np.arange(n)
    pv_ = 0.0; vv_ = 0.0
    vwap = np.full(n, np.nan); sopen = np.zeros(n)
    for i in range(n):
        if D["fb"][i]:
            pv_ = 0.0; vv_ = 0.0
        pv_ += c[i] * v[i]; vv_ += v[i]
        vwap[i] = pv_ / vv_ if vv_ > 0 else np.nan
    for s in range(D["n_sess"]):
        m = idx[D["sid"] == s]
        sopen[m] = o[m[0]]
    atr_l = np.concatenate([[atr14[0]], atr14[:-1]])
    vwap_l = np.concatenate([[np.nan], vwap[:-1]])
    c_l = np.concatenate([[c[0]], c[:-1]])
    sess_ret = np.zeros(D["n_sess"])
    for s in range(D["n_sess"]):
        m = idx[D["sid"] == s]
        sess_ret[s] = c[m[-1]] - o[m[0]]
    prev_ret = np.concatenate([[0.0], sess_ret[:-1]])[D["sid"]]
    up = np.concatenate([[0], np.sign(np.diff(c))])
    runlen = np.zeros(n); r = 0
    for i in range(1, n):
        r = r + 1 if up[i] == up[i - 1] and up[i] != 0 else (1 if up[i] != 0 else 0)
        runlen[i] = r * (1 if up[i] > 0 else -1)
    runlen_l = np.concatenate([[0], runlen[:-1]])
    volnorm = pd.Series(v).rolling(240, min_periods=30).mean().values
    F = {"F5 dist-open/ATR": (c_l - sopen) / np.maximum(atr_l, 1e-9),
         "F11 prior-sess ret": prev_ret,
         "F14 run length": runlen_l,
         "F4 dist-VWAP/ATR": (c_l - vwap_l) / np.maximum(atr_l, 1e-9),
         # amendment_1: F2 lagged one bar - cd and volnorm both include bar i's own
         # close/volume, while the sized position fills at bar i's OPEN
         "F2 |delta|/vol": np.concatenate(
             [[0.0], (np.abs(cd) / np.maximum(volnorm, 1e-9))[:-1]])}
    ent_i = np.array([int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1))
                      for x in base_trl if A <= np.datetime64(x["et"]) < B])

    out = open(os.path.join(OUT, "quality.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    P_("=== PRE-TEST: mutual correlation at the entry bars (|r|>0.7 would collapse to one) ===")
    ks = list(F)
    M = np.array([np.nan_to_num(F[k][ent_i]) for k in ks])
    C = np.corrcoef(M)
    P_("        " + "".join(f"{k[:12]:>14}" for k in ks))
    for i_, k in enumerate(ks):
        P_(f"{k[:7]:<8}" + "".join(f"{C[i_, j]:>14.2f}" for j in range(len(ks))))
    dup = [(ks[i_], ks[j]) for i_ in range(len(ks)) for j in range(i_ + 1, len(ks))
           if abs(C[i_, j]) > 0.7]
    P_(f"pairs above |0.7|: {dup if dup else 'none -> all five count separately'}")
    use = list(ks)
    for a_, b_ in dup:
        if b_ in use:
            use.remove(b_)
    P_(f"features entering the score: {use}\n")

    # thresholds from the ENTRY-BAR distribution, as W33 defined them
    thr = {}
    for k in use:
        x = F[k][ent_i]
        thr[k] = (np.nanquantile(x, 2 / 3) if k != "F11 prior-sess ret"
                  else np.nanquantile(x, 1 / 3))
    score = np.zeros(n)
    for k in use:
        if k == "F11 prior-sess ret":
            score += (F[k] <= thr[k]).astype(float)
        elif k == "F14 run length":
            score += (F[k] >= np.nanquantile(F[k][ent_i], 0.9)).astype(float)
        else:
            score += (F[k] >= thr[k]).astype(float)
    P_(f"score distribution at entries: " +
       ", ".join(f"{int(kk)}:{int((score[ent_i]==kk).sum())}"
                 for kk in sorted(set(score[ent_i]))))

    rows = []

    def rep(nm, trl, is_size):
        d = weekly(trl, wk_of, A, B)
        s, net, wp = sharpe(d)
        vv = np.array(list(d.values()))
        p = np.array([x["pnl"] for x in trl if A <= np.datetime64(x["et"]) < B])
        u = np.array([x.get("u", 1) for x in trl if A <= np.datetime64(x["et"]) < B])
        P_(f"{nm:<26}{len(p):>7}{u.mean():>7.2f}{p.sum()/PV/nsw:>11.2f}{p.mean():>9.1f}"
           f"{vv.mean():>9,.0f}{wp:>8.1f}{vv.min():>10,.0f}{s:>8.3f}")
        rows.append(dict(arm=nm, n=len(p), avg_size=round(float(u.mean()), 2),
                         pts=round(p.sum() / PV / nsw, 2), per_trade=round(p.mean(), 1),
                         wk_mean=round(vv.mean()), wk_pos=round(wp, 1),
                         worst=round(float(vv.min())), sharpe=round(s, 3),
                         is_size=is_size))
        return s, float(vv.min())

    P_(f"\n{'arm':<26}{'n':>7}{'avgSz':>7}{'pts/sess':>11}{'$/trade':>9}{'wkMean':>9}"
       f"{'wkPos%':>8}{'worst':>10}{'sharpe':>8}")
    s_base, w_base = rep("S0 base (1 contract)", base_trl, False)
    for k in (2, 3):
        keep = pos.copy()
        keep[score < k] = 0
        rep(f"S1 filter score>={k}", fills_daily(D, keep, halt=1300, target=1000), False)
    for k in (2, 3):
        sz = np.where(score >= k, 2, 1).astype(np.int8)
        rep(f"S2 size2 @score>={k}", sized_fills(D, pos, sz), True)
    sz = np.where(score >= 4, 3, np.where(score >= 3, 2, 1)).astype(np.int8)
    rep("S3 size 1/2/3 @3,4", sized_fills(D, pos, sz), True)

    P_("\n=== ADOPTION (filters: pts up & Sharpe not down | sizing: SHARPE MUST RISE) ===")
    adopted = []
    for r in rows[1:]:
        if r["is_size"]:
            ok = r["sharpe"] > s_base
            P_(f"  {r['arm']:<26} Sharpe {r['sharpe']:.3f} vs {s_base:.3f} | "
               f"pts {r['pts']:.2f} | worst {r['worst']:,} | "
               f"{'ADOPT' if ok else 'reject (leverage)'}")
        else:
            ok = r["pts"] > rows[0]["pts"] and r["sharpe"] >= s_base
            P_(f"  {r['arm']:<26} pts {r['pts']:.2f} vs {rows[0]['pts']:.2f} | Sharpe "
               f"{r['sharpe']:.3f} | {'ADOPT' if ok else 'reject'}")
        if ok:
            adopted.append(r)
    if not adopted:
        P_("\n  NONE -> the leverage law is GENERAL, not conditional on information novelty.")
        P_("  Exposure is closed as a research axis; contract count remains the owner's choice.")
    else:
        best = max(adopted, key=lambda r: r["sharpe"])
        P_(f"\n=== NULL (binding) on {best['arm']}: 100 circular shifts of the score ===")
        k = 2 if ">=2" in best["arm"] else (3 if ">=3" in best["arm"] else 3)
        nulls = []
        for j in range(100):
            off = int(RNG.integers(20_000, n - 20_000))
            sc = np.roll(score, off)
            if best["is_size"]:
                szn = np.where(sc >= k, 2, 1).astype(np.int8)
                trl = sized_fills(D, pos, szn)
            else:
                kp = pos.copy(); kp[sc < k] = 0
                trl = fills_daily(D, kp, halt=1300, target=1000)
            s_, _, _ = sharpe(weekly(trl, wk_of, A, B))
            if s_ > -9:
                nulls.append(s_)
            if (j + 1) % 50 == 0:
                print(f"   nulls {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
        nulls = np.array(nulls)
        pct = 100.0 * (nulls < best["sharpe"]).mean()
        P_(f"real {best['sharpe']:.3f} | null mean {nulls.mean():.3f} | p95 "
           f"{np.percentile(nulls,95):.3f} | percentile {pct:.1f} | "
           f"p {(nulls>=best['sharpe']).mean():.3f} -> "
           f"{'EVIDENCE' if pct>=95 else ('weak' if pct>=80 else 'NOT EVIDENCE')}")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
