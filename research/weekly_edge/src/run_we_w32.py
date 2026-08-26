"""WE_W32 CLOCK (spec preregistered): multi-clock members + TOD-normalised threshold.

Both change WHERE AND HOW OFTEN FLIPS OCCUR, the only production lever left after W31.
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
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT                      # noqa: E402
from run_we_w03 import cd_signals                                        # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, weekly, sharpe                           # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w30 import position_series                                   # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W32_CLOCK", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260832)
TICK = 0.25
SMIN, SMAX, STOPM = 40 * TICK, 1200 * TICK, 179 * TICK


def ratchet_targets(D, volmults, clock=1, price=None, vol_period=460):
    """Long-only ratchet target path. `clock` = how many 1-min bars per ratchet update.
    `price` lets the machine run on a transformed (e.g. devolatilised) path while fills stay
    on real prices. Fully causal: the update at bar i uses closes through i."""
    c = D["c"] if price is None else price
    fb, n = D["fb"], D["n"]
    K = len(volmults)
    up = [False] * K; anc = [0.0] * K; S = [STOPM] * K
    pos = [0] * K; pend = [0] * K
    vol_sum, vol_cnt, prev = 0.0, 0, np.nan
    diffs = []
    init = False
    tick_ct = 0
    out = np.zeros(n, np.int8)
    nflip = 0
    flip_bars = []

    def sig():
        return (vol_sum / vol_cnt) if vol_cnt >= 30 else np.nan

    def rs(mult):
        sg = sig()
        if np.isnan(sg) or sg <= 0:
            return STOPM
        return min(max(mult * sg, SMIN), SMAX)

    for i in range(n):
        px = c[i]
        for m in range(K):
            pos[m] = pend[m]
        if not np.isnan(prev):
            d = abs(px - prev)
            vol_sum += d; vol_cnt += 1; diffs.append(d)
            if vol_cnt > vol_period:
                diffs = diffs[-vol_period:]
                vol_sum = float(sum(diffs)); vol_cnt = len(diffs)
        prev = px
        tick_ct += 1
        advance = (tick_ct % clock == 0) or fb[i]
        if advance:
            for m in range(K):
                if not init:
                    up[m] = False; anc[m] = px; S[m] = rs(volmults[m]); continue
                if up[m]:
                    if px >= anc[m]:
                        anc[m] = px
                    elif px < anc[m] - S[m]:
                        up[m] = False; S[m] = rs(volmults[m]); anc[m] = px
                        pend[m] = 0; nflip += 1; flip_bars.append(i)
                else:
                    if px <= anc[m]:
                        anc[m] = px
                    elif px > anc[m] + S[m]:
                        up[m] = True; S[m] = rs(volmults[m]); anc[m] = px
                        pend[m] = 1; nflip += 1; flip_bars.append(i)
            if not init:
                init = True
        for m in range(K):
            if i < 20:
                pend[m] = pos[m]; continue
            xl = anc[m] - S[m] if up[m] else anc[m] + S[m]
            if pos[m] > 0 and px <= xl:
                pend[m] = 0
            elif pos[m] != 0:
                pend[m] = pos[m]
        if D["lb"][i]:
            for m in range(K):
                pos[m] = 0; pend[m] = 0
        out[i] = 1 if sum(pend) * 2 >= K else 0
    return out, nflip, np.array(flip_bars, dtype=np.int64)


def tod_factor(D):
    """f[i] = mean(|dclose|/sigma460) for bar i's minute-of-day, from PRIOR sessions only."""
    n = D["n"]
    c = D["c"]
    dcl = np.abs(np.diff(c, prepend=c[0]))
    sg = pd.Series(dcl).rolling(460, min_periods=30).mean().values
    sg = np.concatenate([[np.nan], sg[:-1]])
    ratio = np.where((sg > 0) & ~np.isnan(sg), dcl / np.maximum(sg, 1e-9), np.nan)
    mod = ((D["t"] - D["t"].astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60)
    f = np.ones(n)
    hist = {}
    idx = np.arange(n)
    for s in range(D["n_sess"]):
        m = idx[D["sid"] == s]
        for i in m:
            h = hist.get(int(mod[i]))
            if h and len(h) >= 20:
                f[i] = float(np.mean(h[-120:]))
        for i in m:
            if not np.isnan(ratio[i]):
                hist.setdefault(int(mod[i]), []).append(ratio[i])
                if len(hist[int(mod[i])]) > 400:
                    hist[int(mod[i])].pop(0)
    assert np.all(f > 0)
    return np.clip(f, 0.2, 8.0), mod


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
    out = open(os.path.join(OUT, "clock.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    rows = []

    def build_and_score(nm, paths_by_member):
        vs = []
        for mem, base in paths_by_member.items():
            for q in (None, 0.7, 0.8, 0.9):
                okv = np.ones(n, bool) if q is None else ((norm <= 0) | (ratio >= q))
                for dg in (True, False):
                    a = okv & (dL if dg else True)
                    vs.append((base & a).astype(np.int8))
        frac = np.vstack(vs).mean(axis=0)
        pos = (frac >= 0.5).astype(np.int8)
        trl = fills_daily(D, pos, halt=1300, target=1000)
        ip = position_series(D, trl) & win
        p = np.array([x["pnl"] for x in trl if A <= np.datetime64(x["et"]) < B])
        d = weekly(trl, wk_of, A, B)
        s, net, wp = sharpe(d)
        v = np.array(list(d.values()))
        st = float((v - STRESS_RT * len(p) / max(len(v), 1)).mean())
        P_(f"{nm:<26}{p.sum()/PV/nsw:>10.2f}{100*ip.sum()/win.sum():>9.2f}"
           f"{p.sum()/PV/max(ip.sum(),1):>10.4f}{len(p)/max(len(v),1):>8.1f}"
           f"{p.mean():>9.1f}{v.mean():>9,.0f}{wp:>8.1f}{v.min():>10,.0f}{s:>7.3f}"
           f"{st:>8,.0f}")
        rows.append(dict(arm=nm, pts=round(p.sum() / PV / nsw, 2),
                         inpos=round(100 * ip.sum() / win.sum(), 2),
                         dens=round(p.sum() / PV / max(ip.sum(), 1), 4),
                         sharpe=round(s, 3), worst=round(float(v.min())),
                         stress=round(st)))
        return rows[-1], pos

    P_(f"{'arm':<26}{'pts/sess':>10}{'inPos%':>9}{'pts/bar':>10}{'tr/wk':>8}{'$/trade':>9}"
       f"{'wkMean':>9}{'wkPos%':>8}{'worst':>10}{'shrp':>7}{'stress':>8}")
    P_("=== AXIS C: MULTI-CLOCK MEMBERS (decisions and fills stay 1-min) ===")
    base_paths, flips = {}, {}
    for ck in (1, 3, 5):
        pm = {}
        tot = 0
        for mem in MEMBERS:
            b, nf, _ = ratchet_targets(D, MEMBERS[mem], clock=ck)
            pm[mem] = b.astype(bool); tot += nf
        base_paths[ck] = pm; flips[ck] = tot
        r, _ = build_and_score(f"C clock={ck}min", pm)
        print(f"   clock {ck} done, flips {tot:,} [{_time.time()-t0:.0f}s]", flush=True)
    union = {f"{mem}@{ck}": base_paths[ck][mem] for ck in (1, 3, 5) for mem in MEMBERS}
    build_and_score("C union {1,3,5}min", union)
    P_(f"   flips: 1min {flips[1]:,} | 3min {flips[3]:,} | 5min {flips[5]:,}")

    P_("\n=== AXIS T: TOD-NORMALISED THRESHOLD ===")
    f, mod = tod_factor(D)
    P_(f"   f range {f.min():.3f}-{f.max():.3f}; 09:31 slot mean "
       f"{f[mod == 571].mean():.3f}; 14:00 {f[mod == 840].mean():.3f}; "
       f"19:00 {f[mod == 1140].mean():.3f}")
    dcl = np.diff(D["c"], prepend=D["c"][0])
    ptil = D["c"][0] + np.cumsum(dcl / f)
    pm = {}
    fl_t = 0
    for mem in MEMBERS:
        b, nf, fb_ = ratchet_targets(D, MEMBERS[mem], clock=1, price=ptil)
        pm[mem] = b.astype(bool); fl_t += nf
        if mem == "narrow6":
            P_(f"   M1 failure signature: E[f|flip] {f[fb_].mean():.3f} vs E[f|all] "
               f"{f.mean():.3f}  (M1 failed at 1.536 vs 1.000)")
    build_and_score("T tod-normalised", pm)
    P_(f"   flips: normalised {fl_t:,} vs raw 1min {flips[1]:,}")

    base = [r for r in rows if r["arm"] == "C clock=1min"][0]
    P_("\n=== ADOPTION (pts up, density loss <15%, Sharpe not down, stress>0) ===")
    ok_arms = []
    for r in rows:
        if r["arm"] == "C clock=1min":
            continue
        ok = (r["pts"] > base["pts"] and r["dens"] >= 0.85 * base["dens"]
              and r["sharpe"] >= base["sharpe"] and r["stress"] > 0)
        P_(f"  {r['arm']:<26} pts {r['pts']:.2f} vs {base['pts']:.2f} | dens "
           f"{100*r['dens']/base['dens']:.0f}% | shrp {r['sharpe']:.3f} vs "
           f"{base['sharpe']:.3f} | {'ADOPT' if ok else 'reject'}")
        if ok:
            ok_arms.append(r["arm"])
    if not ok_arms:
        P_("  NONE -> falsifier: production is capped at ~10.6 pts/session per contract with")
        P_("  this model; the remaining levers are exposure and a different model.")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
