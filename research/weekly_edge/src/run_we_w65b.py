"""WE_W65 phase 1b (amendment_1) - the same measurement on three WIDER pairs.

NQ/ES are two cap-weighted US large-cap index futures with heavily overlapping constituents;
their divergence being arbitraged to inside two round turns is what efficient-markets reasoning
predicts, and phase 1 measured exactly that (variance ratio 0.76, reversion $12.76 against
$8.72 of pure commission).

The interesting question is whether a WIDER pair - legs that are genuinely different exposures -
diverges enough to clear the same floor. W43 measured RTY and YM as the most decoupled
instruments this campaign has seen (weekly rho 0.10 with NQ, and 0.04/0.03 INSIDE NQ's
worst-decile weeks). That decoupling is why they failed as directional sleeves and it is exactly
what a SPREAD needs.

The friction floor is RECOMPUTED per pair from each instrument's own point value and tick size.
Carrying NQ's numbers to another instrument is the error W43's read 1 was voided for.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT                                              # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W65_RELVALUE", "out")
os.makedirs(OUT, exist_ok=True)
# instrument -> (path, point value $, tick size in points, commission $/RT)
INST = {
    "NQ": (os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                        "nq1m_2005_202605.parquet"), 20.0, 0.25, 4.36),
    "ES": (os.path.join(ROOT, "runs", "SM1M_ES_SUBSTRATE", "out",
                        "es_1m_2022_2026.parquet"), 50.0, 0.25, 4.36),
    "RTY": (os.path.join(ROOT, "runs", "SM1M_RTY_SUBSTRATE", "out",
                         "rty_1m_2022_2026.parquet"), 50.0, 0.10, 4.36),
    "YM": (os.path.join(ROOT, "runs", "SM1M_YM_SUBSTRATE", "out",
                        "ym_1m_2022_2026.parquet"), 5.0, 1.0, 4.36),
}
PAIRS = [("NQ", "RTY"), ("NQ", "YM"), ("ES", "RTY"), ("NQ", "ES")]
BETA_WIN = 390
HORIZONS = (5, 15, 30, 60, 120)
QS = (0.90, 0.95, 0.99)
RNG = np.random.default_rng(20260865)
_cache = {}


def load(sym):
    if sym not in _cache:
        p, _, _, _ = INST[sym]
        d = pd.read_parquet(p, columns=["time", "close"])
        d["time"] = pd.to_datetime(d["time"])
        _cache[sym] = d.rename(columns={"close": sym})
    return _cache[sym]


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "relvalue2.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    P_("=== friction floor per pair, from each instrument's OWN contract spec ===")
    P_(f"{'pair':<10}{'legs ($/pt, tick pts)':<34}{'commission both legs':>22}"
       f"{'2 ticks both legs':>20}{'stress floor $/RT':>20}")
    floors = {}
    for a, b in PAIRS:
        _, pva, tka, ca = INST[a]
        _, pvb, tkb, cb = INST[b]
        comm = ca + cb
        slip = 2 * tka * pva + 2 * tkb * pvb
        floors[(a, b)] = (comm, comm + slip)
        P_(f"{a+'/'+b:<10}{f'{a} ${pva:.0f}/{tka}  {b} ${pvb:.0f}/{tkb}':<34}"
           f"{comm:>21,.2f}{slip:>20,.2f}{comm+slip:>20,.2f}")

    allrows, econrows = [], []
    for a, b in PAIRS:
        M = load(a).merge(load(b), on="time")
        M = M[M["time"] >= "2022-01-02"].sort_values("time").reset_index(drop=True)
        if len(M) < 100000:
            P_(f"\n   {a}/{b}: only {len(M)} matched minutes, skipped")
            continue
        t = M["time"].values.astype("datetime64[s]")
        fb = np.zeros(len(M), bool); fb[0] = True
        fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
        sid = np.cumsum(fb) - 1
        ca_, cb_ = M[a].values, M[b].values
        ra = np.zeros(len(M)); rb = np.zeros(len(M))
        ra[1:] = np.diff(ca_) / ca_[:-1]
        rb[1:] = np.diff(cb_) / cb_[:-1]
        ra[fb] = 0.0; rb[fb] = 0.0
        sxy = pd.Series(ra * rb).rolling(BETA_WIN, min_periods=120).sum().shift(1).values
        sxx = pd.Series(rb * rb).rolling(BETA_WIN, min_periods=120).sum().shift(1).values
        beta = np.clip(np.nan_to_num(np.where(sxx > 1e-18, sxy / np.maximum(sxx, 1e-18), 1.0),
                                     nan=1.0), 0.2, 3.0)
        resid = ra - beta * rb
        div = np.zeros(len(M)); acc = 0.0
        for i in range(len(M)):
            if fb[i]:
                acc = 0.0
            acc += resid[i]
            div[i] = acc
        d1 = np.zeros(len(M)); d1[1:] = np.diff(div); d1[fb] = 0.0
        pva = INST[a][1]
        notional = pva * ca_
        comm, stress = floors[(a, b)]
        P_(f"\n{'='*112}\n=== {a} / {b}: {len(M):,} matched minutes, "
           f"{int(sid[-1]+1):,} sessions, causal beta median {np.median(beta):.3f}")
        P_(f"{'='*112}")
        P_(f"{'horizon':<10}{'variance ratio':>17}{'bootstrap 5th-95th':>26}"
           f"{'daily sigma of div (bp)':>26}")
        starts = np.flatnonzero(fb); ends = np.append(starts[1:], len(M))
        for k in HORIZONS:
            dk = np.zeros(len(M)); dk[k:] = div[k:] - div[:-k]
            mk = np.zeros(len(M), bool); mk[k:] = sid[k:] == sid[:-k]
            v1 = float(np.var(d1[~fb], ddof=1)); vk = float(np.var(dk[mk], ddof=1))
            vr = vk / (k * v1) if v1 > 0 else np.nan
            bs = []
            for _ in range(150):
                pick = RNG.integers(0, len(starts), min(300, len(starts)))
                idx = np.concatenate([np.arange(starts[p], ends[p]) for p in pick])
                a1 = d1[idx]; a1 = a1[a1 != 0]; ak = dk[idx][mk[idx]]
                if len(a1) > 100 and len(ak) > 100 and a1.var(ddof=1) > 0:
                    bs.append(float(ak.var(ddof=1) / (k * a1.var(ddof=1))))
            bs = np.array(bs)
            P_(f"{k:<10}{vr:>17.4f}"
               f"{f'{np.percentile(bs,5):.4f} - {np.percentile(bs,95):.4f}' if len(bs) else 'n/a':>26}"
               f"{1e4*np.std(dk[mk]):>26.2f}")
            allrows.append(dict(pair=f"{a}/{b}", horizon=k, vr=vr,
                                lo=float(np.percentile(bs, 5)) if len(bs) else np.nan,
                                hi=float(np.percentile(bs, 95)) if len(bs) else np.nan))
        absdiv = np.abs(div)
        P_(f"\n{'threshold':<11}{'horizon':>9}{'events':>10}{'mean rev $':>14}"
           f"{'median $':>12}{'vs commission':>15}{'vs stress':>12}{'verdict':>12}")
        best = -1e18
        for q in QS:
            thr = pd.Series(absdiv).rolling(20 * 390, min_periods=5000).quantile(q).shift(1).values
            for k in HORIZONS:
                fwd = np.full(len(M), np.nan); fwd[:-k] = div[k:] - div[:-k]
                same = np.zeros(len(M), bool); same[:-k] = sid[k:] == sid[:-k]
                hit = np.isfinite(thr) & (absdiv > thr) & same & np.isfinite(fwd)
                if hit.sum() < 200:
                    continue
                pnl = -np.sign(div[hit]) * fwd[hit] * notional[hit]
                mn = float(pnl.mean())
                v = ("TRADEABLE" if mn > stress else
                     ("commission only" if mn > comm else "no"))
                P_(f"{f'q{int(q*100)}':<11}{k:>9}{int(hit.sum()):>10}{mn:>14,.2f}"
                   f"{float(np.median(pnl)):>12,.2f}{mn-comm:>+15,.2f}{mn-stress:>+12,.2f}{v:>12}")
                econrows.append(dict(pair=f"{a}/{b}", q=q, horizon=k, n=int(hit.sum()),
                                     mean=mn, net_comm=mn - comm, net_stress=mn - stress))
                best = max(best, mn - stress)
        P_(f"   -> {a}/{b}: best cell is {best:+,.2f} $ against the stress floor -> "
           + ("PHASE 2 AUTHORISED" if best > 0 else "NOT TRADEABLE, stopping rule fires"))
    pd.DataFrame(allrows).to_csv(os.path.join(OUT, "varratio_all.csv"), index=False)
    E = pd.DataFrame(econrows)
    E.to_csv(os.path.join(OUT, "reversion_all.csv"), index=False)

    P_(f"\n{'='*112}\n=== VERDICT ACROSS ALL PAIRS")
    P_(f"{'='*112}")
    P_(f"{'pair':<12}{'best VR (any horizon)':>24}{'best net of commission':>26}"
       f"{'best net of stress':>22}{'verdict':>12}")
    for p in E["pair"].unique():
        q = E[E["pair"] == p]
        v = pd.DataFrame(allrows)
        vv = v[v["pair"] == p]["vr"].min()
        bc, bs2 = q["net_comm"].max(), q["net_stress"].max()
        P_(f"{p:<12}{vv:>24.4f}{bc:>+26,.2f}{bs2:>+22,.2f}"
           f"{('TRADEABLE' if bs2 > 0 else 'no'):>12}")
    if (E["net_stress"] <= 0).all():
        P_(f"\n   NO PAIR CLEARS TWO ROUND TURNS AT STRESS FRICTION AT ANY HORIZON OR")
        P_(f"   THRESHOLD. Relative value is CLOSED at the minute-to-hour frequency on the")
        P_(f"   instruments this repo holds. The divergences between US index futures are")
        P_(f"   mean-reverting - measurably so - and arbitraged to inside transaction costs.")
        P_(f"   That is a first-principles result and it is now measured rather than assumed.")
    P_(f"\n=== STATUS: measurement only. Nothing adopted, no rule built. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
