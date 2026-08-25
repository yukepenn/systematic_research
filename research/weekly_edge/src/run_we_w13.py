"""WE_W13 NULL (spec preregistered): discipline wave — attack our own stack."""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, load, week_table, summarize, sm14_1m
from run_we_w03 import fills, cd_signals                                 # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w11 import seg_of                                            # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from solarwave import SolarWaveParams, solar_wave_full                   # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W13_NULL", "out")
os.makedirs(OUT, exist_ok=True)
RNG = np.random.default_rng(20260825)


def main():
    t0 = _time.time()
    D = load()
    n = D["n"]
    rng_, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)
    mod = ((D["t"] - D["t"].astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60)
    not_close = seg_of(mod) != "CLOSE"

    def lag_b(a):
        return np.concatenate([[True], a[:-1]])

    def lag_i(a):
        return np.concatenate([[0], a[:-1]])
    _, cd_arr = cd_signals(D)
    dL, dS = lag_b(cd_arr >= 0), lag_b(cd_arr <= 0)
    sw = solar_wave_full(D["o"], D["h"], D["l"], D["c"], SolarWaveParams())
    wv = lag_i(sw.signal_wave)
    wL, wS = (wv >= 0), (wv <= 0)
    NAR = {"narrow5": [6, 8, 10, 12, 14], "narrow6": [6, 8, 10, 12, 14, 16],
           "narrow7": [6, 8, 10, 12, 14, 16, 18]}
    TG = {k: sm14_1m(D, 460, return_targets=True, volmults=v) for k, v in NAR.items()}
    print(f"targets ready [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "null.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    def build(tg, q=0.8, delta=True, wave=True, dropclose=True):
        okq = (norm <= 0) | (ratio >= q)
        aL = okq.copy(); aS = okq.copy()
        if delta:
            aL &= dL; aS &= dS
        if wave:
            aL &= wL; aS &= wS
        if dropclose:
            aL &= not_close; aS &= not_close
        return fills(D, tg, allow_long=aL, allow_short=aS)

    def sharpe_of(trl, sample="dev"):
        if len(trl) < 50:
            return np.nan, None
        wt = week_table(trl, D, lambda x: x["xt"])
        r = summarize(wt, D, sample)
        return (r["sharpe"], r) if r else (np.nan, None)

    full, rfull = sharpe_of(build(TG["narrow6"]))
    P(f"FULL STACK dev Sharpe {full:.3f}  weekly ${rfull['mean']:,.0f}  "
      f"pos {rfull['pos']:.1f}%  worst ${rfull['worst']:,.0f}\n")

    # ---------- N1 null-calibrated gates ----------
    P("=== N1 NULL CALIBRATION (200 rate-matched random gates per real gate) ===")
    P(f"{'gate':<14}{'blockRate':>11}{'realShrp':>10}{'nullMean':>10}{'nullP95':>10}"
      f"{'pctile':>9}{'p':>8}  verdict")
    rows = []
    sid = D["sid"]
    n_sess = D["n_sess"]
    for gname in ("delta", "range", "wave", "close"):
        # the stack WITHOUT this gate, then this gate vs random gates of the same rate
        kw = dict(delta=True, wave=True, dropclose=True, q=0.8)
        if gname == "delta":
            kw["delta"] = False; mL, mS = dL, dS
        elif gname == "range":
            kw["q"] = 0.0; m = (norm <= 0) | (ratio >= 0.8); mL = mS = m
        elif gname == "wave":
            kw["wave"] = False; mL, mS = wL, wS
        else:
            kw["dropclose"] = False; mL = mS = not_close
        real_trl = build(TG["narrow6"])
        real_s, _ = sharpe_of(real_trl)
        # amendment_1: directional block rate, and CIRCULAR-SHIFT nulls (rate + structure
        # preserved exactly; only the alignment with the market is destroyed)
        rate = 1.0 - (float(mL.mean()) + float(mS.mean())) / 2.0
        nulls = []
        for _ in range(100):
            off = int(RNG.integers(10_000, n - 10_000))
            sL = np.roll(mL, off); sS = np.roll(mS, off)
            aL = sL.copy(); aS = sS.copy()
            if kw.get("delta", True):
                aL &= dL; aS &= dS
            if kw.get("wave", True):
                aL &= wL; aS &= wS
            if kw.get("dropclose", True):
                aL &= not_close; aS &= not_close
            okq = (norm <= 0) | (ratio >= kw["q"])
            s_, _ = sharpe_of(fills(D, TG["narrow6"], allow_long=aL & okq,
                                    allow_short=aS & okq))
            if not np.isnan(s_):
                nulls.append(s_)
        nulls = np.array(nulls)
        pct = 100.0 * (nulls < real_s).mean()
        pval = float((nulls >= real_s).mean())
        verdict = "EVIDENCE" if pct >= 95 else ("weak" if pct >= 80 else "NOT EVIDENCE")
        P(f"{gname:<14}{rate:>11.3f}{real_s:>10.3f}{nulls.mean():>10.3f}"
          f"{np.percentile(nulls, 95):>10.3f}{pct:>9.1f}{pval:>8.3f}  {verdict}")
        rows.append(dict(test="N1", gate=gname, block_rate=round(rate, 3),
                         real=round(real_s, 3), null_mean=round(float(nulls.mean()), 3),
                         null_p95=round(float(np.percentile(nulls, 95)), 3),
                         pctile=round(pct, 1), p=round(pval, 3), verdict=verdict))
        print(f"   {gname} nulls done [{_time.time()-t0:.0f}s]", flush=True)

    # ---------- N2 per-year ----------
    P("\n=== N2 PER-YEAR STABILITY (full stack) ===")
    trl = build(TG["narrow6"])
    wt = week_table(trl, D, lambda x: x["xt"])
    wv_ = {}
    for s, (net, ntr) in wt.items():
        w = D["wk"][s]
        a = wv_.setdefault(w, [0.0, 0]); a[0] += net; a[1] += ntr
    P(f"{'year':<8}{'weeks':>7}{'net':>12}{'mean':>9}{'pos%':>7}{'worst':>10}{'sharpe':>8}")
    for yr in ("2022", "2023", "2024", "2025", "2026"):
        v = np.array([x[0] for w, x in wv_.items() if w.startswith(yr)])
        if len(v) < 5:
            continue
        sh = v.mean() / v.std(ddof=1)
        P(f"{yr:<8}{len(v):>7}{v.sum():>12,.0f}{v.mean():>9,.0f}"
          f"{100*(v>0).mean():>7.1f}{v.min():>10,.0f}{sh:>8.3f}")
        rows.append(dict(test="N2", gate=yr, real=round(sh, 3),
                         verdict="positive" if sh > 0 else "NEGATIVE"))

    # ---------- N3 sensitivity ----------
    P("\n=== N3 PARAMETER SENSITIVITY (one at a time) ===")
    P(f"{'perturbation':<24}{'shrp':>8}{'delta':>8}")
    grid = [("q=0.7", dict(q=0.7)), ("q=0.8 (stack)", dict()), ("q=0.9", dict(q=0.9)),
            ("members=narrow5", dict()), ("members=narrow7", dict())]
    for nm, kw in grid:
        tg = TG["narrow5"] if "narrow5" in nm else (TG["narrow7"] if "narrow7" in nm
                                                   else TG["narrow6"])
        s, _ = sharpe_of(build(tg, **kw))
        P(f"{nm:<24}{s:>8.3f}{s-full:>+8.3f}")
        rows.append(dict(test="N3", gate=nm, real=round(s, 3), verdict=""))

    # ---------- N4 leave-one-out ----------
    P("\n=== N4 LEAVE-ONE-OUT (remove one component from the FULL stack) ===")
    P(f"{'removed':<24}{'shrp':>8}{'cost':>8}  verdict")
    for nm, kw in (("delta gate", dict(delta=False)), ("range throttle", dict(q=0.0)),
                   ("wave gate", dict(wave=False)), ("CLOSE drop", dict(dropclose=False))):
        s, _ = sharpe_of(build(TG["narrow6"], **kw))
        cost = full - s
        v = "KEEP" if cost >= 0.005 else "DEAD WEIGHT -> DROP"
        P(f"{nm:<24}{s:>8.3f}{cost:>+8.3f}  {v}")
        rows.append(dict(test="N4", gate=nm, real=round(s, 3), verdict=v))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
