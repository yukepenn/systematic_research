"""WE_W27 MIXVOTE (spec preregistered): non-Solar strategies as VOTERS, not sleeves."""
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
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import weekly, sharpe                                    # noqa: E402
from run_we_w23 import build_side_paths                                  # noqa: E402
from run_we_w25 import ema                                               # noqa: E402
from run_we_w26 import fills_daily, daily_stats                          # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                    # noqa: E402
import inverse_core as IC                                                # noqa: E402
from run_r13_strict_master import run_master                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W27_MIXVOTE", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260827)


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    c, n = D["c"], D["n"]
    tarr = D["t"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), n - 1))
        return wkmap[int(D["sid"][i])]

    def lagb(a):
        return np.concatenate([[False], a[:-1]])

    pl, _, ratio, norm = build_side_paths(D, "long")
    solar = [pl[k].astype(bool) for k in pl]
    ok = (norm <= 0) | (ratio >= 0.8)
    ns = {}
    for P in (60, 240):
        ns[f"donch{P}"] = lagb(c >= pd.Series(c).rolling(P).max().values) & ok
    for f, s in ((20, 100), (60, 480)):
        ns[f"ema{f}x{s}"] = lagb(ema(c, f) > ema(c, s)) & ok
    r60 = pd.Series(c).pct_change(60).values
    r60p = np.concatenate([np.full(60, np.nan), r60[:-60]])
    ns["accel"] = lagb((r60 > 0) & (r60 > r60p)) & ok
    hh = pd.Series(c).rolling(240).max().values
    ll = pd.Series(c).rolling(240).min().values
    ns["rangepos"] = lagb((c - ll) / np.maximum(hh - ll, 1e-9) >= 0.75) & ok
    print(f"voters ready: {len(solar)} solar + {len(ns)} non-solar "
          f"[{_time.time()-t0:.0f}s]", flush=True)

    bb = IC.prepare(D["df"], SolarWaveParams())
    s1_raw = run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)
    s1 = [dict(d=x["d"], pnl=x["pnl"], et=str(bb["t"][x["ei"]]), xt=str(bb["t"][x["xi"]]))
          for x in s1_raw]

    out = open(os.path.join(OUT, "mix.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    rows = []

    def run_vote(voters, tag, target=1000, halt=1300, solar_mask=None, quiet=False):
        M = np.vstack([v.astype(np.int8) for v in voters])
        frac = M.mean(axis=0)
        pos = (frac >= 0.5).astype(np.int8)
        trl = fills_daily(D, pos, halt=halt, target=target)
        d = weekly(trl, wk_of, A, B)
        s, net, wp = sharpe(d)
        v = np.array(list(d.values()))
        ds = daily_stats(D, trl, tarr)
        share = np.nan
        if solar_mask is not None and pos.sum() > 0:
            on = pos.astype(bool)
            share = 100 * M[solar_mask][:, on].sum() / max(M[:, on].sum(), 1)
        if not quiet:
            P_(f"{tag:<30}{len(voters):>4}{len(trl):>7}{v.mean():>9,.0f}{wp:>8.1f}"
               f"{ds['pos_of_traded']:>8.1f}{v.min():>10,.0f}{s:>8.3f}"
               f"{share:>9.1f}")
            rows.append(dict(name=tag, voters=len(voters), n=len(trl),
                             wk_mean=round(v.mean()), wk_pos=round(wp, 1),
                             day_pos=round(ds["pos_of_traded"], 1), worst=round(v.min()),
                             sharpe=round(s, 3), solar_share=round(float(share), 1)))
        return s, float(v.min()), d, trl

    P_("=== A MIXED-MODEL VOTE (same 1 contract, session box -1300/+1000) ===")
    P_(f"{'vote':<30}{'vtrs':>4}{'n':>7}{'wkMean':>9}{'wkPos%':>8}{'dPos%':>8}{'worst':>10}"
       f"{'shrp':>8}{'solar%':>9}")
    sm_all = np.array([True] * len(solar) + [False] * len(ns))
    base_s, base_w, d_base, trl_base = run_vote(
        solar, "PURE SOLAR (32)", solar_mask=np.array([True] * len(solar)))
    v_all = solar + [ns[k] for k in ns]
    run_vote(v_all, "V_ALL (32 + 6)", solar_mask=sm_all)
    prof = [k for k in ns if not k.startswith("donch")]
    sm_p = np.array([True] * len(solar) + [False] * len(prof))
    run_vote(solar + [ns[k] for k in prof], "V_PROFITABLE (32 + 4)", solar_mask=sm_p)
    half = solar[::2]
    sm_h = np.array([True] * len(half) + [False] * len(ns))
    run_vote(half + [ns[k] for k in ns], "V_HALF (16 + 6, balanced)", solar_mask=sm_h)

    P_("\n=== B SESSION-TARGET NULL (binding, 100 circular shifts of the mechanism) ===")
    M = np.vstack([v.astype(np.int8) for v in solar])
    pos = (M.mean(axis=0) >= 0.5).astype(np.int8)
    real_s, _, _ = sharpe(weekly(fills_daily(D, pos, halt=1300, target=1000), wk_of, A, B))
    no_t, _, _ = sharpe(weekly(fills_daily(D, pos, halt=1300), wk_of, A, B))
    nulls = []
    for j in range(100):
        off = int(RNG.integers(20_000, n - 20_000))
        # shift the POSITION path, keep the target rule fixed: this asks whether the target
        # helps a path aligned with the market more than an arbitrary path of the same shape
        s_, _, _ = sharpe(weekly(fills_daily(D, np.roll(pos, off), halt=1300, target=1000),
                                 wk_of, A, B))
        s0, _, _ = sharpe(weekly(fills_daily(D, np.roll(pos, off), halt=1300), wk_of, A, B))
        nulls.append(s_ - s0)
        if (j + 1) % 25 == 0:
            print(f"   target nulls {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
    nulls = np.array(nulls)
    gain = real_s - no_t
    pct = 100.0 * (nulls < gain).mean()
    P_(f"target gain on the real path {gain:+.3f} (0.273 -> 0.305); null gains: "
       f"mean {nulls.mean():+.3f}, p95 {np.percentile(nulls, 95):+.3f}")
    P_(f"percentile {pct:.1f}, p {(nulls >= gain).mean():.3f} -> "
       f"{'EVIDENCE' if pct >= 95 else ('weak' if pct >= 80 else 'NOT EVIDENCE')}")

    P_("\n=== C SESSION BOX ON S1 ===")
    P_(f"{'variant':<30}{'wkMean':>9}{'wkPos%':>8}{'worst':>10}{'shrp':>8}")

    def s1_box(halt=None, target=None):
        outl = []
        cur = {}
        for x in sorted(s1, key=lambda z: z["et"]):
            i = int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1))
            s_ = int(D["sid"][i])
            acc = cur.get(s_, 0.0)
            if halt is not None and acc <= -halt:
                continue
            if target is not None and acc >= target:
                continue
            outl.append(x)
            cur[s_] = acc + x["pnl"]
        return outl
    for tag, kw in (("S1 raw", {}), ("S1 box -1300/+1000", dict(halt=1300, target=1000)),
                    ("S1 halt -1300", dict(halt=1300)),
                    ("S1 target +1000", dict(target=1000))):
        trl = s1_box(**kw)
        d = weekly(trl, wk_of, A, B)
        s, _, wp = sharpe(d)
        v = np.array(list(d.values()))
        P_(f"{tag:<30}{v.mean():>9,.0f}{wp:>8.1f}{v.min():>10,.0f}{s:>8.3f}")
        rows.append(dict(name=tag, wk_mean=round(v.mean()), wk_pos=round(wp, 1),
                         worst=round(v.min()), sharpe=round(s, 3)))

    P_("\n=== D BEST OBJECT ===")
    P_(f"{'portfolio':<38}{'wkMean':>9}{'wkPos%':>8}{'dPos%':>8}{'worst':>10}{'shrp':>8}")
    ps, _, _, _ = build_side_paths(D, "short")
    fs = -np.vstack([ps[k] for k in ps]).mean(axis=0)
    sh = fills_daily(D, -(fs >= 0.5).astype(np.int8), halt=1300, target=1000)
    d_sh = weekly(sh, wk_of, A, B)
    s1b = s1_box(halt=1300, target=1000)
    d_s1b = weekly(s1b, wk_of, A, B)
    d_s1r = weekly(s1, wk_of, A, B)
    for tag, parts, trls in (
            ("E5box + S1raw + shortbox", (d_base, d_s1r, d_sh), (trl_base, s1, sh)),
            ("E5box + S1box + shortbox", (d_base, d_s1b, d_sh), (trl_base, s1b, sh))):
        dc = {}
        for dd_ in parts:
            for w, val in dd_.items():
                dc[w] = dc.get(w, 0.0) + val
        s, _, wp = sharpe(dc)
        v = np.array(list(dc.values()))
        ds = daily_stats(D, [x for t_ in trls for x in t_], tarr)
        P_(f"{tag:<38}{v.mean():>9,.0f}{wp:>8.1f}{ds['pos_of_traded']:>8.1f}"
           f"{v.min():>10,.0f}{s:>8.3f}")
        rows.append(dict(name=tag, wk_mean=round(v.mean()), wk_pos=round(wp, 1),
                         day_pos=round(ds["pos_of_traded"], 1), worst=round(v.min()),
                         sharpe=round(s, 3)))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
