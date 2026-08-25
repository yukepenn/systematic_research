"""WE_W25 NONSOLAR (spec preregistered): trend engines with zero Solar content."""
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
from run_we_w23 import signed_fills, build_side_paths                    # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                    # noqa: E402
import inverse_core as IC                                                # noqa: E402
from run_r13_strict_master import run_master                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W25_NONSOLAR", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260826)


def ema(x, p):
    a = 2.0 / (p + 1)
    o = np.empty_like(x)
    o[0] = x[0]
    for i in range(1, len(x)):
        o[i] = a * x[i] + (1 - a) * o[i - 1]
    return o


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    c = D["c"]
    n = D["n"]
    rng_, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)
    ok = (norm <= 0) | (ratio >= 0.8)
    tarr = D["t"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), n - 1))
        return wkmap[int(D["sid"][i])]

    def lag(a):
        return np.concatenate([[False], a[:-1]])

    sig = {}
    for P in (60, 240):
        hh = pd.Series(c).rolling(P).max().values
        sig[f"N1_donchian{P}"] = lag(c >= hh)
    for f, s in ((20, 100), (60, 480)):
        sig[f"N2_ema{f}x{s}"] = lag(ema(c, f) > ema(c, s))
    r60 = pd.Series(c).pct_change(60).values
    r60p = np.concatenate([np.full(60, np.nan), r60[:-60]])
    sig["N3_accel"] = lag((r60 > 0) & (r60 > r60p))
    for P in (240,):
        hh = pd.Series(c).rolling(P).max().values
        ll = pd.Series(c).rolling(P).min().values
        pos = (c - ll) / np.maximum(hh - ll, 1e-9)
        sig["N4_rangepos"] = lag(pos >= 0.75)
    print(f"signals ready [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "nonsolar.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    # reference objects
    pl, _, _, _ = build_side_paths(D, "long")
    fl = np.vstack([pl[k] for k in pl]).mean(axis=0)
    e5 = signed_fills(D, (fl >= 0.5).astype(np.int8), halt=1300)
    d_e5 = weekly(e5, wk_of, A, B)
    s_e5, _, p_e5 = sharpe(d_e5)
    w_e5 = min(d_e5.values()); m_e5 = float(np.mean(list(d_e5.values())))
    bb = IC.prepare(D["df"], SolarWaveParams())
    s1 = [dict(d=x["d"], pnl=x["pnl"], et=str(bb["t"][x["ei"]]), xt=str(bb["t"][x["xi"]]))
          for x in run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)]
    d_s1 = weekly(s1, wk_of, A, B)
    d_pair = {w: d_e5.get(w, 0.0) + d_s1.get(w, 0.0) for w in set(d_e5) | set(d_s1)}
    s_pair, _, p_pair = sharpe(d_pair)
    w_pair = min(d_pair.values()); m_pair = float(np.mean(list(d_pair.values())))
    P_(f"REFERENCE E5halt1300      Sharpe {s_e5:.3f}  wk ${m_e5:,.0f}  pos {p_e5:.1f}%  "
       f"worst ${w_e5:,.0f}")
    P_(f"REFERENCE E5halt+S1       Sharpe {s_pair:.3f}  wk ${m_pair:,.0f}  "
       f"pos {p_pair:.1f}%  worst ${w_pair:,.0f}\n")

    P_(f"{'non-Solar engine':<22}{'n':>7}{'net':>11}{'wkMean':>9}{'pos%':>7}{'worst':>10}"
       f"{'shrp':>7}{'stress':>8}{'corrE5':>8}")
    rows = []
    dd = {}
    for nm, s in sig.items():
        arr = (s & ok).astype(np.int8)
        trl = signed_fills(D, arr, halt=1300)
        if len(trl) < 60:
            P_(f"{nm:<22} only {len(trl)} trades")
            continue
        d = weekly(trl, wk_of, A, B)
        dd[nm] = d
        sh, net, pos = sharpe(d)
        v = np.array(list(d.values()))
        ntr = len(trl)
        stress = float((v - STRESS_RT * ntr / max(len(v), 1)).mean())
        ws = sorted(set(d) & set(d_e5))
        cr = float(np.corrcoef([d[w] for w in ws], [d_e5[w] for w in ws])[0, 1])
        P_(f"{nm:<22}{ntr:>7}{net:>11,.0f}{v.mean():>9,.0f}{pos:>7.1f}{v.min():>10,.0f}"
           f"{sh:>7.3f}{stress:>8,.0f}{cr:>8.2f}")
        rows.append(dict(name=nm, n=ntr, wk_mean=round(v.mean()), pos=round(pos, 1),
                         worst=round(v.min()), sharpe=round(sh, 3), stress=round(stress),
                         corr_e5=round(cr, 2)))

    # N5 vote across all non-Solar variants
    M = np.vstack([(sig[k] & ok).astype(np.int8) for k in sig])
    n5 = (M.mean(axis=0) >= 0.5).astype(np.int8)
    trl5 = signed_fills(D, n5, halt=1300)
    d5 = weekly(trl5, wk_of, A, B)
    sh5, net5, pos5 = sharpe(d5)
    v5 = np.array(list(d5.values()))
    ws = sorted(set(d5) & set(d_e5))
    cr5 = float(np.corrcoef([d5[w] for w in ws], [d_e5[w] for w in ws])[0, 1])
    st5 = float((v5 - STRESS_RT * len(trl5) / max(len(v5), 1)).mean())
    P_(f"{'N5_vote_nonsolar':<22}{len(trl5):>7}{net5:>11,.0f}{v5.mean():>9,.0f}{pos5:>7.1f}"
       f"{v5.min():>10,.0f}{sh5:>7.3f}{st5:>8,.0f}{cr5:>8.2f}")
    rows.append(dict(name="N5_vote_nonsolar", n=len(trl5), wk_mean=round(v5.mean()),
                     pos=round(pos5, 1), worst=round(v5.min()), sharpe=round(sh5, 3),
                     stress=round(st5), corr_e5=round(cr5, 2)))

    P_("\n--- T3 COMBINATION ---")
    P_(f"{'portfolio':<28}{'wkMean':>9}{'pos%':>7}{'worst':>10}{'shrp':>7}  verdict")
    for nm, base_d, bs, bp, bw, bm in (("E5halt + N5", d_e5, s_e5, p_e5, w_e5, m_e5),
                                       ("E5halt + S1 + N5", d_pair, s_pair, p_pair,
                                        w_pair, m_pair)):
        dc = {w: base_d.get(w, 0.0) + d5.get(w, 0.0) for w in set(base_d) | set(d5)}
        s2, _, p2 = sharpe(dc)
        v2 = np.array(list(dc.values()))
        gain = 100 * (v2.mean() - bm) / abs(bm)
        deg = 100 * (bw - v2.min()) / abs(bw)
        okc = (s2 >= bs and p2 > bp and deg < gain)
        P_(f"{nm:<28}{v2.mean():>9,.0f}{p2:>7.1f}{v2.min():>10,.0f}{s2:>7.3f}"
           f"  {'ADOPT' if okc else 'reject'}  (prod {gain:+.1f}% vs tail {deg:+.1f}%)")
        rows.append(dict(name=nm, wk_mean=round(v2.mean()), pos=round(p2, 1),
                         worst=round(v2.min()), sharpe=round(s2, 3),
                         verdict="ADOPT" if okc else "reject"))

    P_("\n--- T4 NULL on the non-Solar vote (100 circular shifts) ---")
    nulls = []
    for j in range(100):
        off = int(RNG.integers(20_000, n - 20_000))
        arr = np.roll(n5, off)
        s_, _, _ = sharpe(weekly(signed_fills(D, arr, halt=1300), wk_of, A, B))
        if s_ > -9:
            nulls.append(s_)
        if (j + 1) % 25 == 0:
            print(f"   nulls {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
    nulls = np.array(nulls)
    pct = 100.0 * (nulls < sh5).mean()
    P_(f"real {sh5:.3f} | null mean {nulls.mean():.3f} | p95 {np.percentile(nulls,95):.3f} "
       f"| percentile {pct:.1f} | p {(nulls>=sh5).mean():.3f} -> "
       f"{'EVIDENCE' if pct>=95 else ('weak' if pct>=80 else 'NOT EVIDENCE')}")

    P_("\n=== MODEL-RISK STATEMENT ===")
    best_corr = min(r.get("corr_e5", 9) for r in rows if r.get("corr_e5") is not None)
    if any(r.get("corr_e5", 9) < 0.30 and r.get("stress", -1) > 0 for r in rows):
        P_("At least one non-Solar engine is stress-positive AND correlates < 0.30 with E5 ->")
        P_("the campaign has its first genuine MODEL-RISK diversification.")
    else:
        P_(f"No non-Solar engine is both stress-positive and <0.30 correlated (min corr "
           f"{best_corr:.2f}). The campaign owns ONE model (the Solar ratchet), and that")
        P_("model risk must be stated in every future summary.")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
