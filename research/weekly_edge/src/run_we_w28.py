"""WE_W28 VOTEHYST (spec preregistered): vote-level hysteresis, owed nulls, 2025 diagnostic."""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT                      # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import weekly, sharpe                                    # noqa: E402
from run_we_w23 import build_side_paths                                  # noqa: E402
from run_we_w26 import fills_daily, daily_stats                          # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W28_VOTEHYST", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260828)


def hyst_path(frac, h_in, h_out):
    """Position path with vote hysteresis: enter at >=h_in, exit below h_out."""
    n = len(frac)
    p = np.zeros(n, np.int8)
    on = False
    for i in range(n):
        if on:
            if frac[i] < h_out:
                on = False
        else:
            if frac[i] >= h_in:
                on = True
        p[i] = 1 if on else 0
    return p


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n = D["n"]
    tarr = D["t"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), n - 1))
        return wkmap[int(D["sid"][i])]
    pl, _, _, _ = build_side_paths(D, "long")
    frac = np.vstack([pl[k] for k in pl]).mean(axis=0)
    print(f"frac ready [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "hyst.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    rows = []

    def ev(tag, path, halt=1300, target=1000, quiet=False):
        trl = fills_daily(D, path, halt=halt, target=target)
        d = weekly(trl, wk_of, A, B)
        s, net, wp = sharpe(d)
        v = np.array(list(d.values()))
        if quiet:
            return s, float(v.min()), d, trl
        ds = daily_stats(D, trl, tarr)
        P_(f"{tag:<26}{len(trl):>7}{v.mean():>9,.0f}{wp:>8.1f}{ds['pos_of_traded']:>8.1f}"
           f"{v.min():>10,.0f}{s:>8.3f}")
        rows.append(dict(name=tag, n=len(trl), wk_mean=round(v.mean()),
                         wk_pos=round(wp, 1), day_pos=round(ds["pos_of_traded"], 1),
                         worst=round(v.min()), sharpe=round(s, 3)))
        return s, float(v.min()), d, trl

    P_("=== H VOTE HYSTERESIS (1 contract, halt -1300, target +1000) ===")
    P_(f"{'H_in / H_out':<26}{'n':>7}{'wkMean':>9}{'wkPos%':>8}{'dPos%':>8}{'worst':>10}"
       f"{'shrp':>8}")
    base_s, base_w, d_base, _ = ev("0.50 / 0.50 (baseline)",
                                   (frac >= 0.5).astype(np.int8))
    best = (None, base_s, base_w)
    for hi in (0.50, 0.60, 0.70):
        for lo in (0.30, 0.40, 0.50):
            if hi <= lo:
                continue
            s, w, _, _ = ev(f"{hi:.2f} / {lo:.2f}", hyst_path(frac, hi, lo))
            if s > best[1] and w >= base_w:
                best = ((hi, lo), s, w)
    P_(f"\nbest pair beating baseline on Sharpe without a worse tail: "
       f"{best[0] if best[0] else 'NONE -> falsifier fires'}")

    P_("\n=== N NULLS (100 circular shifts each) ===")

    def null_of(fn, real_gain, tag):
        nulls = []
        for j in range(100):
            off = int(RNG.integers(20_000, n - 20_000))
            nulls.append(fn(off))
            if (j + 1) % 50 == 0:
                print(f"   {tag} nulls {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
        nulls = np.array(nulls)
        pct = 100.0 * (nulls < real_gain).mean()
        P_(f"{tag:<34} real {real_gain:+.3f} | null mean {nulls.mean():+.3f} | "
           f"p95 {np.percentile(nulls, 95):+.3f} | pctile {pct:.1f} | "
           f"p {(nulls >= real_gain).mean():.3f} -> "
           f"{'EVIDENCE' if pct >= 95 else ('weak' if pct >= 80 else 'NOT EVIDENCE')}")
        return pct

    base_path = (frac >= 0.5).astype(np.int8)
    # owed: session HALT null (gain of halt vs no halt, on real vs shifted paths)
    s_halt, _, _, _ = ev("", base_path, halt=1300, target=None, quiet=True)
    s_nohalt, _, _, _ = ev("", base_path, halt=10 ** 9, target=None, quiet=True)
    null_of(lambda off: (sharpe(weekly(fills_daily(D, np.roll(base_path, off), halt=1300),
                                       wk_of, A, B))[0]
                         - sharpe(weekly(fills_daily(D, np.roll(base_path, off),
                                                     halt=10 ** 9), wk_of, A, B))[0]),
            s_halt - s_nohalt, "SESSION HALT gain (owed from W22)")
    if best[0]:
        hi, lo = best[0]
        gain = best[1] - base_s
        null_of(lambda off: (sharpe(weekly(fills_daily(
            D, hyst_path(np.roll(frac, off), hi, lo), halt=1300, target=1000),
            wk_of, A, B))[0]
            - sharpe(weekly(fills_daily(D, (np.roll(frac, off) >= 0.5).astype(np.int8),
                                        halt=1300, target=1000), wk_of, A, B))[0]),
            gain, f"HYSTERESIS {hi}/{lo} gain")

    P_("\n=== Y 2025 DIAGNOSTIC (the weak year) ===")
    trl = fills_daily(D, base_path, halt=1300, target=1000)
    by = {}
    for x in trl:
        i = int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1))
        yr = str(D["sess_date"][int(D["sid"][i])])[:4]
        by.setdefault(yr, []).append(x)
    P_(f"{'year':<7}{'trades':>8}{'net':>11}{'$/trade':>10}{'win%':>8}{'avgWin':>10}"
       f"{'avgLoss':>10}{'wkShrp':>9}")
    for yr in ("2022", "2023", "2024", "2025", "2026"):
        xs = by.get(yr, [])
        if not xs:
            continue
        p = np.array([x["pnl"] for x in xs])
        d = {w: v for w, v in weekly(xs, wk_of).items() if w.startswith(yr)}
        vv = np.array(list(d.values()))
        sh = vv.mean() / vv.std(ddof=1) if len(vv) > 1 else np.nan
        P_(f"{yr:<7}{len(p):>8}{p.sum():>11,.0f}{p.mean():>10.1f}"
           f"{100*(p>0).mean():>8.1f}{p[p>0].mean():>10.0f}{p[p<0].mean():>10.0f}{sh:>9.3f}")
        rows.append(dict(name=f"year {yr}", n=len(p), wk_mean=round(p.sum()),
                         sharpe=round(float(sh), 3)))
    # how much of 2025's weakness is the box firing?
    for tag, kw in (("2025 with box", dict(halt=1300, target=1000)),
                    ("2025 no box", dict(halt=10 ** 9, target=None))):
        t2 = fills_daily(D, base_path, **kw)
        d = {w: v for w, v in weekly(t2, wk_of).items() if w.startswith("2025")}
        vv = np.array(list(d.values()))
        P_(f"   {tag:<16} net {vv.sum():>9,.0f}  Sharpe "
           f"{vv.mean()/vv.std(ddof=1):>6.3f}  pos {100*(vv>0).mean():.1f}%")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
