"""WE_W31 RESTORE (spec preregistered): session-open trend-state restore + Type-3 entries."""
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

OUT = os.path.join(ROOT, "runs", "WE_W31_RESTORE", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260831)
NAR = [6, 8, 10, 12, 14, 16]


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    rng_, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)

    def lag_b(x):
        return np.concatenate([[True], x[:-1]])
    _, cd = cd_signals(D)
    dL = lag_b(cd >= 0)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), n - 1))
        return wkmap[int(D["sid"][i])]
    win = (tarr >= A) & (tarr < B)
    nsw = len(np.unique(D["sid"][win]))

    ARMS = {"R0 baseline": dict(),
            "R1 restore": dict(restore="plain"),
            "R2 restore+conf": dict(restore="conf"),
            "R3 type3": dict(type3=True),
            "R4 restore+type3": dict(restore="plain", type3=True)}
    out = open(os.path.join(OUT, "restore.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    P_(f"{'arm':<20}{'pts/sess':>10}{'inPos%':>9}{'pts/bar':>10}{'tr/wk':>8}{'$/trade':>9}"
       f"{'wkMean':>9}{'wkPos%':>8}{'worst':>10}{'shrp':>7}{'stress':>8}")
    rows = {}
    for nm, kw in ARMS.items():
        vs = []
        for mem in MEMBERS:
            tg = sm14_1m(D, 460, return_targets=True, volmults=MEMBERS[mem], **kw)
            for q in (None, 0.7, 0.8, 0.9):
                okv = np.ones(n, bool) if q is None else ((norm <= 0) | (ratio >= q))
                for dg in (True, False):
                    a = okv & (dL if dg else True)
                    vs.append(np.where((tg > 0) & a, 1, 0).astype(np.int8))
        frac = np.vstack(vs).mean(axis=0)
        pos = (frac >= 0.5).astype(np.int8)
        trl = fills_daily(D, pos, halt=1300, target=1000)
        ip = position_series(D, trl) & win
        p = np.array([x["pnl"] for x in trl if A <= np.datetime64(x["et"]) < B])
        d = weekly(trl, wk_of, A, B)
        s, net, wp = sharpe(d)
        v = np.array(list(d.values()))
        st = float((v - STRESS_RT * len(p) / max(len(v), 1)).mean())
        P_(f"{nm:<20}{p.sum()/PV/nsw:>10.2f}{100*ip.sum()/win.sum():>9.2f}"
           f"{p.sum()/PV/max(ip.sum(),1):>10.4f}{len(p)/max(len(v),1):>8.1f}"
           f"{p.mean():>9.1f}{v.mean():>9,.0f}{wp:>8.1f}{v.min():>10,.0f}{s:>7.3f}{st:>8,.0f}")
        rows[nm] = dict(pts=p.sum() / PV / nsw, inpos=100 * ip.sum() / win.sum(),
                        dens=p.sum() / PV / max(ip.sum(), 1), sharpe=s,
                        worst=float(v.min()), stress=st, pos=pos, wk=v.mean(), trl=trl)
        print(f"   {nm} done [{_time.time()-t0:.0f}s]", flush=True)

    b = rows["R0 baseline"]
    P_("\n=== ADOPTION (pts/session up, density loss <15%, Sharpe not down, stress>0) ===")
    adopted = []
    for nm, r in rows.items():
        if nm.startswith("R0"):
            continue
        ok = (r["pts"] > b["pts"] and r["dens"] >= 0.85 * b["dens"]
              and r["sharpe"] >= b["sharpe"] and r["stress"] > 0)
        P_(f"  {nm:<20} pts {r['pts']:.2f} vs {b['pts']:.2f} | density {r['dens']:.4f} vs "
           f"{b['dens']:.4f} ({100*r['dens']/b['dens']:.0f}%) | shrp {r['sharpe']:.3f} vs "
           f"{b['sharpe']:.3f} | {'ADOPT' if ok else 'reject'}")
        if ok:
            adopted.append(nm)
    if adopted:
        best = max(adopted, key=lambda k: rows[k]["pts"])
        P_(f"\n=== NULL (binding) on {best}: 100 circular shifts ===")
        pos = rows[best]["pos"]
        real = rows[best]["sharpe"]
        nulls = []
        for j in range(100):
            off = int(RNG.integers(20_000, n - 20_000))
            s_, _, _ = sharpe(weekly(fills_daily(D, np.roll(pos, off), halt=1300, target=1000),
                                     wk_of, A, B))
            if s_ > -9:
                nulls.append(s_)
            if (j + 1) % 50 == 0:
                print(f"   nulls {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
        nulls = np.array(nulls)
        pct = 100.0 * (nulls < real).mean()
        P_(f"real {real:.3f} | null mean {nulls.mean():.3f} | p95 "
           f"{np.percentile(nulls, 95):.3f} | percentile {pct:.1f} | "
           f"p {(nulls >= real).mean():.3f} -> "
           f"{'EVIDENCE' if pct >= 95 else ('weak' if pct >= 80 else 'NOT EVIDENCE')}")
    else:
        P_("  NONE -> falsifier: the absent bars are absent for a reason.")
    pd.DataFrame([dict(arm=k, pts_per_session=round(r["pts"], 2),
                       in_pos_pct=round(r["inpos"], 2), density=round(r["dens"], 4),
                       wk_mean=round(r["wk"]), sharpe=round(r["sharpe"], 3),
                       worst=round(r["worst"]), stress=round(r["stress"]))
                 for k, r in rows.items()]).to_csv(os.path.join(OUT, "summary.csv"),
                                                   index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
