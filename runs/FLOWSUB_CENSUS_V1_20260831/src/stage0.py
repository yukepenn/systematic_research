"""STAGE 0 -- CAPABILITY EXPERIMENT.  Can cheap Last-only proxies stand in for L1 BBO?

NOT A STRATEGY.  No P&L, no cost model, no position, no equity curve, no threshold search.
Every output is a correlation / agreement / markout statistic.

GOVERNANCE, asserted in code (see guard()):
  * only sessions ALREADY MATERIALIZED as parquet (=> already outcome-consumed) are read.
  * the 33-session blind BBO pool and the 141-session Last-only pool are never opened.
  * nothing >= 2026-08-01 is opened.

THE THREE QUESTIONS, frozen before any number was produced:
 (a) does CLV = (C-L)/(H-L) - 0.5, computable from trade-only OHLC, reproduce the signed
     order-flow imbalance that only BBO can measure?  And does it add anything BEYOND the
     bar return, which is free?
 (b) does a tick-rule (Last-only) classification preserve the Lee-Ready/quote-rule signs,
     i.e. can signed flow be extended into the Last-only dates?  Including: how ORDER-SENSITIVE
     is that answer (the MS-LAST closure recorded 274 % order sensitivity for a tick-rule family).
 (c) how much information is lost without BBO -- measured as the share of quote-rule imbalance
     variance recoverable from Last-only features, and as markout consistency.

DEFINITIONS
  quote-rule (Lee-Ready) sign: prevailing bid/ask = last Bid / last Ask event STRICTLY EARLIER
  in the as-recorded event stream.  sign = sign(price - mid); ties fall back to the tick rule.
  tick rule: sign of the change in trade price vs the previous DIFFERENT trade price.
  bar = 1 minute of exchange (ET) time, built from trades only.
"""
from __future__ import annotations

import glob
import os
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
V2 = os.path.join(ROOT, "research", "data_microstructure_v2", "raw", "NQ")
OLD = os.path.join(ROOT, "research", "scalping_lab", "substrate", "raw", "NQ")
BLIND = os.path.join(ROOT, "runs", "BBO_COMPLETENESS_RECENSUS_V1_20260828", "out",
                     "BBO_BLIND_POOL_MANIFEST.csv")
SEAL = "2026-08-01"
L = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    L.append(s)


def guard(paths):
    blind = set(pd.read_csv(BLIND).session_date.str.replace("-", ""))
    for p in paths:
        d = os.path.basename(p)[1:9]
        assert d not in blind, f"REFUSED: {d} is in the frozen blind BBO pool"
        assert f"{d[:4]}-{d[4:6]}-{d[6:]}" < SEAL, f"REFUSED: {d} is sealed"
    P(f"    GUARD: {len(paths)} sessions, none in the frozen blind pool, none sealed.  OK")


def ffill(a):
    idx = np.where(~np.isnan(a), np.arange(a.size), 0)
    np.maximum.accumulate(idx, out=idx)
    return a[idx]


def tickrule(px):
    """sign vs previous DIFFERENT price; zeros carried forward."""
    d = np.sign(np.diff(px, prepend=px[0]))
    d[0] = 0.0
    nz = np.where(d != 0, np.arange(d.size), 0)
    np.maximum.accumulate(nz, out=nz)
    return d[nz]


def load(f):
    t = pq.read_table(f, columns=["bip", "time", "price", "volume"])
    bip = np.asarray(t["bip"].to_numpy(zero_copy_only=False), dtype=np.int8)
    tm = t["time"].to_numpy()
    px = np.asarray(t["price"].to_numpy(zero_copy_only=False), dtype=np.float64)
    vol = np.asarray(t["volume"].to_numpy(zero_copy_only=False), dtype=np.float64)
    return bip, tm, px, vol


def session_stats(f, rng):
    bip, tm, px, vol = load(f)
    n = bip.size
    bidr = np.where(bip == 1, px, np.nan)
    askr = np.where(bip == 2, px, np.nan)
    bid, ask = ffill(bidr), ffill(askr)
    m = bip == 0
    tpx, tvol, ttm = px[m], vol[m], tm[m]
    tbid, task = bid[m], ask[m]
    mid = (tbid + task) / 2.0
    ok = np.isfinite(mid) & (task > tbid)                 # drop crossed/locked/unset
    crossed = float(np.mean(~ok))
    # ---- quote rule + Lee-Ready tie-break
    qs = np.sign(tpx - mid)
    tr = tickrule(tpx)
    tie = (qs == 0) | ~ok
    lr = np.where(tie, tr, qs)
    # ---- order sensitivity of the TICK rule: reshuffle within identical timestamps
    same_ms = float(np.mean(np.diff(ttm.astype("datetime64[ms]").astype(np.int64),
                                    prepend=0) == 0))
    key = ttm.astype("datetime64[ms]").astype(np.int64)
    perm = np.lexsort((rng.random(tpx.size), key))        # random order inside each ms
    tr2 = np.empty_like(tr)
    tr2[perm] = tickrule(tpx[perm])
    order_flip = float(np.mean(tr != tr2))
    # ---- 1-minute bars from trades only
    minute = ttm.astype("datetime64[m]")
    D = pd.DataFrame({"m": minute, "px": tpx, "v": tvol,
                      "lr": lr, "tr": tr, "mid": np.where(ok, mid, np.nan),
                      "hh": ttm.astype("datetime64[h]").astype("datetime64[ns]")})
    D["lrv"], D["trv"] = D.lr * D.v, D.tr * D.v
    g = D.groupby("m", sort=True)
    B = g.agg(O=("px", "first"), H=("px", "max"), Lo=("px", "min"), C=("px", "last"),
              V=("v", "sum"), N=("px", "size"), lrd=("lrv", "sum"), trd=("trv", "sum"),
              mid0=("mid", "first"), mid1=("mid", "last"))
    B = B[B.V > 0]
    rngHL = (B.H - B.Lo).values
    B["clv"] = np.where(rngHL > 0, (B.C.values - B.Lo.values) / np.where(rngHL > 0, rngHL, 1) - 0.5, 0.0)
    B["ret"] = B.C - B.O
    B["true_imb"] = B.lrd / B.V
    B["tick_imb"] = B.trd / B.V
    B["hour"] = pd.to_datetime(B.index.values).hour
    B["rth"] = (B.hour >= 9) & (B.hour < 16)
    # ---- trade-level agreement
    agree = float(np.mean(tr[~tie] == qs[~tie])) if (~tie).sum() else np.nan
    vw_agree = (float(np.sum(tvol[~tie] * (tr[~tie] == qs[~tie])) / np.sum(tvol[~tie]))
                if (~tie).sum() else np.nan)
    # ---- markouts on a 1-second mid grid
    sec = tm.astype("datetime64[s]")
    midall = (bid + ask) / 2.0
    midall = np.where((ask > bid) & np.isfinite(bid) & np.isfinite(ask), midall, np.nan)
    G = pd.Series(midall).groupby(sec).last()
    G = G.reindex(pd.date_range(G.index.min(), G.index.max(), freq="1s")).ffill()
    ts_i = np.searchsorted(G.index.values, ttm.astype("datetime64[s]"))
    gv = G.values
    mo = {}
    for h in (1, 5, 30):
        j = np.clip(ts_i + h, 0, gv.size - 1)
        dmid = gv[j] - gv[np.clip(ts_i, 0, gv.size - 1)]
        good = np.isfinite(dmid)
        mo[f"mo{h}_true"] = float(np.mean(dmid[good] * lr[good]))
        mo[f"mo{h}_tick"] = float(np.mean(dmid[good] * tr[good]))
    return B, dict(session=os.path.basename(f)[:9], events=n, trades=int(m.sum()),
                   crossed_or_unset=round(crossed, 5), tie_frac=round(float(np.mean(tie)), 5),
                   same_ms_frac=round(same_ms, 4), tickrule_order_flip=round(order_flip, 5),
                   trade_sign_agree=round(agree, 4), vw_sign_agree=round(vw_agree, 4), **mo)


def corrs(B, tag):
    x = B.dropna(subset=["clv", "true_imb", "tick_imb", "ret"])
    out = {"scope": tag, "bars": len(x)}
    if len(x) < 30:
        return out
    out["pearson_clv_trueimb"] = round(float(x.clv.corr(x.true_imb)), 4)
    out["spearman_clv_trueimb"] = round(float(x.clv.corr(x.true_imb, method="spearman")), 4)
    out["sign_agree_clv_trueimb"] = round(float(np.mean(np.sign(x.clv) == np.sign(x.true_imb))), 4)
    out["pearson_tickimb_trueimb"] = round(float(x.tick_imb.corr(x.true_imb)), 4)
    out["spearman_tickimb_trueimb"] = round(float(x.tick_imb.corr(x.true_imb, method="spearman")), 4)
    out["sign_agree_tickimb_trueimb"] = round(
        float(np.mean(np.sign(x.tick_imb) == np.sign(x.true_imb))), 4)
    out["pearson_ret_trueimb"] = round(float(x.ret.corr(x.true_imb)), 4)
    out["pearson_clv_ret"] = round(float(x.clv.corr(x.ret)), 4)
    # partial correlation of CLV with true_imb, controlling for bar return
    def resid(a, b):
        b1 = np.c_[np.ones(len(b)), b]
        return a - b1 @ np.linalg.lstsq(b1, a, rcond=None)[0]
    r1 = resid(x.clv.values, x.ret.values.reshape(-1, 1))
    r2 = resid(x.true_imb.values, x.ret.values.reshape(-1, 1))
    out["partial_clv_trueimb_given_ret"] = round(float(np.corrcoef(r1, r2)[0, 1]), 4)
    # information recoverable from Last-only features
    for name, cols in (("ret", ["ret"]), ("ret+clv", ["ret", "clv"]),
                       ("ret+clv+tickimb", ["ret", "clv", "tick_imb"])):
        A = np.c_[np.ones(len(x)), x[cols].values]
        beta, *_ = np.linalg.lstsq(A, x.true_imb.values, rcond=None)
        e = x.true_imb.values - A @ beta
        out["R2_trueimb_from_" + name] = round(
            float(1 - e.var() / x.true_imb.values.var()), 4)
    # lead / lag: does either carry FORWARD information, and do they agree on the shape?
    for j in (1, 2, 3):
        fut = x.ret.shift(-j)
        k = fut.notna()
        out[f"corr_trueimb_ret_fwd{j}"] = round(float(x.true_imb[k].corr(fut[k])), 4)
        out[f"corr_clv_ret_fwd{j}"] = round(float(x.clv[k].corr(fut[k])), 4)
        out[f"corr_tickimb_ret_fwd{j}"] = round(float(x.tick_imb[k].corr(fut[k])), 4)
    return out


def main(k=16):
    rng = np.random.default_rng(20260831)
    fs = sorted(glob.glob(os.path.join(V2, "s*.parquet")))
    sel = [fs[i] for i in np.linspace(0, len(fs) - 1, k).round().astype(int)]
    P("=" * 100)
    P("=== STAGE 0  CAPABILITY EXPERIMENT -- correlations only, NO P&L")
    P("=" * 100)
    P(f"    substrate  research/data_microstructure_v2/raw/NQ   {len(fs)} consumed sessions")
    P(f"    sampled    {len(sel)} evenly across the span (seed 20260831)")
    guard(sel)
    P("")
    diag, bars = [], []
    for f in sel:
        B, d = session_stats(f, rng)
        B["session"] = d["session"]
        bars.append(B)
        diag.append(d)
        P(f"    {d['session']}  events {d['events']:>9,}  trades {d['trades']:>8,}"
          f"  tie {d['tie_frac']:.4f}  same-ms {d['same_ms_frac']:.3f}"
          f"  tickrule_order_flip {d['tickrule_order_flip']:.4f}"
          f"  trade_sign_agree {d['trade_sign_agree']:.4f}")
    DG = pd.DataFrame(diag)
    DG.to_csv(os.path.join(OUT, "stage0_session_diagnostics.csv"), index=False)
    ALL = pd.concat(bars)
    ALL.to_csv(os.path.join(OUT, "stage0_bars.csv"))

    P("")
    P("=" * 100)
    P("=== (b) LEE-READY / TICK-RULE EXTENSION INTO Last-only  (trade level)")
    P("=" * 100)
    for c in ("trade_sign_agree", "vw_sign_agree", "tie_frac", "tickrule_order_flip",
              "same_ms_frac", "crossed_or_unset"):
        s = DG[c]
        P(f"    {c:<22} mean {s.mean():.4f}  median {s.median():.4f}"
          f"  min {s.min():.4f}  max {s.max():.4f}")
    P("")
    P("    markout of a signed trade against the mid, mean NQ points per trade:")
    for h in (1, 5, 30):
        P(f"      h={h:>2}s   quote-rule sign {DG[f'mo{h}_true'].mean():+.5f}"
          f"    tick-rule sign {DG[f'mo{h}_tick'].mean():+.5f}"
          f"    ratio {DG[f'mo{h}_tick'].mean()/DG[f'mo{h}_true'].mean():.3f}")

    P("")
    P("=" * 100)
    P("=== (a)+(c) BAR LEVEL: CLV AND TICK-RULE VS THE BBO TRUTH")
    P("=" * 100)
    rows = [corrs(ALL, "POOLED all-hours"), corrs(ALL[ALL.rth], "POOLED RTH 09-16 ET"),
            corrs(ALL[~ALL.rth], "POOLED ETH outside RTH")]
    per = [dict(corrs(ALL[ALL.session == s], s)) for s in sorted(ALL.session.unique())]
    R = pd.DataFrame(rows)
    PER = pd.DataFrame(per)
    R.to_csv(os.path.join(OUT, "stage0_pooled.csv"), index=False)
    PER.to_csv(os.path.join(OUT, "stage0_per_session.csv"), index=False)
    cols = ["scope", "bars", "pearson_clv_trueimb", "spearman_clv_trueimb",
            "sign_agree_clv_trueimb", "pearson_tickimb_trueimb",
            "spearman_tickimb_trueimb", "sign_agree_tickimb_trueimb",
            "pearson_ret_trueimb", "pearson_clv_ret", "partial_clv_trueimb_given_ret",
            "R2_trueimb_from_ret", "R2_trueimb_from_ret+clv",
            "R2_trueimb_from_ret+clv+tickimb"]
    for _, r in R.iterrows():
        P("")
        P(f"    --- {r['scope']}   bars {int(r['bars']):,}")
        for c in cols[2:]:
            P(f"        {c:<34} {r[c]:+.4f}")
    P("")
    P("    PER-SESSION SPREAD (n=%d sessions, so no pooling illusion):" % len(PER))
    for c in ("pearson_clv_trueimb", "spearman_clv_trueimb", "pearson_tickimb_trueimb",
              "sign_agree_tickimb_trueimb", "partial_clv_trueimb_given_ret",
              "R2_trueimb_from_ret+clv", "R2_trueimb_from_ret+clv+tickimb"):
        s = PER[c]
        P(f"        {c:<34} mean {s.mean():+.4f}  sd {s.std():.4f}"
          f"  min {s.min():+.4f}  max {s.max():+.4f}"
          f"  all-same-sign {bool((np.sign(s) == np.sign(s.iloc[0])).all())}")
    P("")
    P("    LEAD/LAG -- correlation with FORWARD bar return (information, not P&L):")
    for _, r in R.iterrows():
        P(f"      {r['scope']:<24}"
          + "".join(f"  fwd{j}: true {r[f'corr_trueimb_ret_fwd{j}']:+.4f}"
                    f" clv {r[f'corr_clv_ret_fwd{j}']:+.4f}"
                    f" tick {r[f'corr_tickimb_ret_fwd{j}']:+.4f}" for j in (1, 2, 3)))
    with open(os.path.join(OUT, "stage0.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 16)
