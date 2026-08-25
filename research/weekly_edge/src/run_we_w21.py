"""WE_W21 VOTEAUDIT (spec preregistered): attack E5 before trusting it."""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, week_table, summarize, sm14_1m
from run_we_w03 import fills, cd_signals                                 # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS, weekly, sharpe                       # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                    # noqa: E402
import inverse_core as IC                                                # noqa: E402
from run_r13_strict_master import run_master                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W21_VOTEAUDIT", "out")
os.makedirs(OUT, exist_ok=True)
RNG = np.random.default_rng(20260825)


def build_paths(D):
    """The 32 long-only config position paths + their trade lists."""
    rng_, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)

    def lag_b(x):
        return np.concatenate([[True], x[:-1]])
    _, cd = cd_signals(D)
    dL = lag_b(cd >= 0)
    TG = {k: sm14_1m(D, 460, return_targets=True, volmults=v) for k, v in MEMBERS.items()}
    paths = {}
    for mem in MEMBERS:
        for q in QS:
            for dg in (True, False):
                okq = np.ones(D["n"], bool) if q is None else ((norm <= 0) | (ratio >= q))
                aL = okq & (dL if dg else True)
                tg = TG[mem]
                paths[(mem, q, dg)] = np.where((tg > 0) & aL, 1, 0).astype(np.int8)
    return paths


def vote_trades(D, paths, keys, thresh=0.5):
    M = np.vstack([paths[k] for k in keys])
    tgt = (M.sum(axis=0) >= thresh * len(keys)).astype(np.int8)
    return fills(D, tgt, allow_long=None, allow_short=None)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "audit.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    # ---------------- modern sample, A2 first (binding) ----------------
    Dm = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    pm = build_paths(Dm)
    keys = list(pm)
    print(f"modern paths ready [{_time.time()-t0:.0f}s]", flush=True)
    tarr = Dm["t"]
    wkmap = {s: Dm["wk"][s] for s in range(Dm["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), Dm["n"] - 1))
        return wkmap[int(Dm["sid"][i])]
    A = np.datetime64("2022-07-01"); B = np.datetime64("2026-08-01")
    real_trl = vote_trades(Dm, pm, keys)
    real_s, real_net, real_pos = sharpe(weekly(real_trl, wk_of, A, B))
    P(f"E5 (modern, 2022-07..2026-07): Sharpe {real_s:.3f}  net ${real_net:,.0f}  "
      f"pos {real_pos:.1f}%\n")

    P("=== A2 NULL CALIBRATION (binding): 100 common circular shifts of the vote's inputs ===")
    n = Dm["n"]
    nulls = []
    for j in range(100):
        off = int(RNG.integers(20_000, n - 20_000))
        shifted = {k: np.roll(v, off) for k, v in pm.items()}
        s, _, _ = sharpe(weekly(vote_trades(Dm, shifted, keys), wk_of, A, B))
        if s > -9:
            nulls.append(s)
        if (j + 1) % 25 == 0:
            print(f"   nulls {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
    nulls = np.array(nulls)
    pct = 100.0 * (nulls < real_s).mean()
    pval = float((nulls >= real_s).mean())
    verdict = "EVIDENCE" if pct >= 95 else ("weak" if pct >= 80 else "NOT EVIDENCE")
    P(f"real {real_s:.3f} | null mean {nulls.mean():.3f} | null p95 "
      f"{np.percentile(nulls, 95):.3f} | percentile {pct:.1f} | p {pval:.3f} -> {verdict}")
    if pct < 95:
        P("\nA2 is binding and E5 did not clear it. A1/A3 are still reported for the record,")
        P("but E5 is DEMOTED to 'not evidence' exactly as the wave gate was in W13.")

    # ---------------- A4 subfamily sensitivity ----------------
    P("\n=== A4 SUBFAMILY SENSITIVITY (leave-one-subfamily-out) ===")
    P(f"{'dropped':<22}{'configs':>9}{'sharpe':>9}{'delta':>9}")
    spread = [real_s]
    for mem in MEMBERS:
        sub = [k for k in keys if k[0] != mem]
        s, _, _ = sharpe(weekly(vote_trades(Dm, pm, sub), wk_of, A, B))
        spread.append(s)
        P(f"{'members=' + mem:<22}{len(sub):>9}{s:>9.3f}{s - real_s:>+9.3f}")
    for q in QS:
        sub = [k for k in keys if k[1] != q]
        s, _, _ = sharpe(weekly(vote_trades(Dm, pm, sub), wk_of, A, B))
        spread.append(s)
        P(f"{'q=' + str(q):<22}{len(sub):>9}{s:>9.3f}{s - real_s:>+9.3f}")
    sp = max(spread) - min(spread)
    P(f"spread {sp:.3f} -> {'SUBFAMILY-DEPENDENT' if sp > 0.05 else 'robust to subfamily removal'}")

    # ---------------- A3 orthogonal combination ----------------
    P("\n=== A3 E5 + S1 (max 2 contracts, disclosed) ===")
    bb = IC.prepare(Dm["df"], SolarWaveParams())
    s1 = [dict(d=x["d"], pnl=x["pnl"], et=str(bb["t"][x["ei"]]), xt=str(bb["t"][x["xi"]]))
          for x in run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)]
    d5 = weekly(real_trl, wk_of, A, B)
    d1 = weekly(s1, wk_of, A, B)
    dc = {w: d5.get(w, 0.0) + d1.get(w, 0.0) for w in set(d5) | set(d1)}
    for nm, d in (("S1 alone", d1), ("E5 alone", d5), ("E5+S1", dc)):
        s, net, pos = sharpe(d)
        v = np.array(list(d.values()))
        P(f"{nm:<12} Sharpe {s:>6.3f}  net ${net:>9,.0f}  wk ${v.mean():>6,.0f}  "
          f"pos {pos:>5.1f}%  worst ${v.min():>9,.0f}")
    ws = sorted(set(d5) & set(d1))
    P(f"  corr(E5,S1) = {np.corrcoef([d5[w] for w in ws], [d1[w] for w in ws])[0,1]:.2f}")

    # ---------------- A1 deep history ----------------
    P("\n=== A1 DEEP HISTORY: E5 unchanged on 2006-2021 ===")
    Dd = load_deep("2006-01-05", "2021-12-31 17:00")
    W1.DEV_END = pd.Timestamp("2021-12-31").date()
    pd_paths = build_paths(Dd)
    dtr = vote_trades(Dd, pd_paths, list(pd_paths))
    wt = week_table(dtr, Dd, lambda x: x["xt"])
    r = summarize(wt, Dd, "dev")
    st = float((np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])).mean())
    P(f"pooled: weeks {r['weeks']}  net ${r['total']:,.0f}  wk ${r['mean']:,.0f}  "
      f"pos {r['pos']:.1f}%  worst ${r['worst']:,.0f}  Sharpe {r['sharpe']:.3f}  "
      f"stress ${st:,.0f}")
    dv = {}
    for s_, (net, _) in wt.items():
        dv[Dd["wk"][s_]] = dv.get(Dd["wk"][s_], 0.0) + net
    npos = 0
    P(f"{'year':<7}{'sharpe':>9}{'pos%':>8}{'net':>11}")
    for yr in [str(y) for y in range(2006, 2022)]:
        v = np.array([x for w, x in dv.items() if w.startswith(yr)])
        if len(v) < 5:
            continue
        sh = v.mean() / v.std(ddof=1)
        npos += sh > 0
        P(f"{yr:<7}{sh:>9.3f}{100*(v>0).mean():>8.1f}{v.sum():>11,.0f}")
    P(f"positive years {npos}/16 -> "
      f"{'CROSS-ERA STRUCTURAL' if r['sharpe'] > 0 and npos >= 11 else 'modern-regime object'}")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
