"""XM_EXEC_COST_AUDIT_V1 — ADDENDUM (Y1..Y7), run after the frozen main verdict.

Everything here is a robustness / diagnostic extension of the already-printed verdict. It
changes no gate and proposes no policy. Additions, all named in advance of computation:

  Y1 drive-conditioned entry spread on EVERY quote session (n~97 instead of n=30) — the
     two-sided BUY-vs-SELL question at real power, using the sign of the NQ 09:31->09:45
     drive, which is defined on every session whether XM traded it or not.
  Y2 freshness / tail forensics: quote ages at the two instants, the widest sessions named,
     trimmed and winsorized means, bootstrap CI on the paired clock RT.
  Y3 era-coverage honesty: what share of XM's 346 trades sits in the era the quote evidence
     actually covers, and what the pooled measured rate over-charges as a result.
  Y4 comparable instrument: ES at the identical instants from research/data_esnq/parquet/ES.
  Y5 +1-minute delayed fill on the FROZEN XM action set (pure execution perturbation).
  Y6 median-vs-mean decomposition: the W82 model is a per-minute MEDIAN; expected cost is a
     mean. How much of the gap is that, and how much is level?
  Y7 extra funded-cost scenarios, including recent-era + adverse-tick.
"""
from __future__ import annotations

import os
import sys
import time as _time

os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "XM_EXEC_COST_AUDIT_V1_20260831")
OUT = os.path.join(RUN, "out")
SRC = os.path.join(ROOT, "research", "weekly_edge", "src")
sys.path.insert(0, SRC)
sys.path.insert(0, ROOT)

from research_sdk.seal_guard import assert_presealed                     # noqa: E402
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import PV, COMM_RT                                       # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w51 import session_frames                                    # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

T0 = _time.time()
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICK, TICKV = 0.25, 5.0
STALE_NS = 5_000_000_000
ONE_MIN = np.timedelta64(60, "s")
ANCH, DEC, ENTM, EXITNB = 571, 585, 586, 946
ESNQ_ES = os.path.join(ROOT, "research", "data_esnq", "parquet", "ES")
ALLOWLIST_PATH = os.path.join(ROOT, "research", "data_esnq", "ALLOWLIST_DEV_44.txt")


def log(*a):
    print(f"[{_time.time()-T0:6.0f}s]", *a, flush=True)


def era(d_):
    if d_ < "20260101":
        return "2025H2"
    if d_ < "20260601":
        return "2026_Jan_May"
    return "2026_Jun_Jul"


def main():
    L = []

    def G(*a):
        s = " ".join(str(x) for x in a)
        L.append(s)
        print(s, flush=True)

    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    o, c = D["o"], D["c"]
    st_, en_, _ = session_frames(D)
    NSESS = D["n_sess"]
    sdate = pd.to_datetime(D["sess_date"])
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    win = np.array([A <= tarr[st_[s]] < B for s in range(NSESS)])
    sess_in = np.flatnonzero(win)
    iso = sdate.isocalendar()
    wkall = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    wk = wkall[sess_in]
    NW = len(set(wk))
    assert_presealed(pd.DataFrame({"t": pd.to_datetime(tarr)}), "t", "substrate")

    def at2(mv, arr, uo=False):
        r = np.full(NSESS, np.nan)
        ix = np.full(NSESS, -1, np.int64)
        m_ = mod == mv
        r[sid[m_]] = (o[m_] if uo else arr[m_])
        ix[sid[m_]] = np.flatnonzero(m_)
        return r, ix

    pa, _ = at2(ANCH, o, True)
    pdc, _ = at2(DEC, c)
    drive_all = np.sign(pdc - pa)
    date_of = {sdate[s].strftime("%Y%m%d"): s for s in range(NSESS)}

    CK = pd.read_csv(os.path.join(OUT, "clock_spread.csv"))
    TT = pd.read_csv(os.path.join(OUT, "xm_trades.csv"), dtype={"sess_date": str})
    LEG = pd.read_csv(os.path.join(OUT, "leg_costs.csv"), dtype={"date": str})
    CK["date"] = CK["date"].astype(str).str.zfill(8)
    CKok = CK[CK["status"] == "ok"].copy()
    CKok["era"] = CKok["date"].map(era)
    CKok["sess"] = CKok["date"].map(date_of)
    CKok["drive"] = CKok["sess"].map(lambda s: drive_all[int(s)] if pd.notna(s) else np.nan)

    G("=" * 112)
    G("XM_EXEC_COST_AUDIT_V1_20260831 — ADDENDUM Y1..Y7 (robustness; changes no gate)")
    G("=" * 112)

    # ------------------------------------------------------------------ Y1
    G("")
    G("Y1 — TWO-SIDED QUESTION AT FULL POWER (every quote session, not only XM trade days)")
    G("    XM's direction IS the sign of the NQ 09:31->09:45 drive, which exists on every")
    G("    session. Entry side = BUY when drive>0, SELL when drive<0.")
    ent = CKok[CKok["role"] == "entry"].copy()
    ext = CKok[CKok["role"] == "exit"].copy()
    for nm, sub in (("entry 09:45:00", ent), ("exit  15:45:00", ext)):
        up = sub[sub["drive"] > 0]["spread_ticks"]
        dn = sub[sub["drive"] < 0]["spread_ticks"]
        if len(up) > 2 and len(dn) > 2:
            t_ = ((up.mean() - dn.mean())
                  / np.sqrt(up.var(ddof=1) / len(up) + dn.var(ddof=1) / len(dn)))
        else:
            t_ = np.nan
        G(f"  {nm}:  drive>0 (XM would BUY)  n={len(up):<3} mean {up.mean():.2f} tk "
          f"med {up.median():.2f}   |   drive<0 (XM would SELL) n={len(dn):<3} "
          f"mean {dn.mean():.2f} tk med {dn.median():.2f}   diff t={t_:+.2f}")
    G("  READ: the sign-inversion the convention forces on shorts is handled explicitly in X3;")
    G("        this is the question of whether the BUY side is systematically more expensive.")

    # ------------------------------------------------------------------ Y2
    G("")
    G("Y2 — FRESHNESS AND TAIL FORENSICS (is the mean an artifact?)")
    for nm, sub in (("entry", ent), ("exit", ext)):
        ages = np.maximum(sub["age_bid_ms"], sub["age_ask_ms"])
        G(f"  {nm}: quote age at the instant  median {ages.median():.0f} ms  "
          f"p90 {np.percentile(ages,90):.0f} ms  max {ages.max():.0f} ms  "
          f"(5,000 ms staleness cap already applied)")
    piv = CKok.pivot_table(index="date", columns="role", values="spread_ticks").dropna()
    piv["rt_usd"] = TICKV * (piv["entry"] + piv["exit"]) / 2.0
    piv["era"] = piv.index.map(era)
    v = piv["rt_usd"].to_numpy()
    rng = np.random.default_rng(20260831)
    bs = v[rng.integers(0, len(v), size=(8000, len(v)))].mean(axis=1)
    tr10 = float(np.mean(np.sort(v)[int(0.05 * len(v)):len(v) - int(0.05 * len(v))]))
    wz = np.clip(v, np.percentile(v, 5), np.percentile(v, 95))
    G(f"  paired clock RT (n={len(v)}): mean ${v.mean():.2f} "
      f"[95% bootstrap CI ${np.percentile(bs,2.5):.2f}..${np.percentile(bs,97.5):.2f}]  "
      f"median ${np.median(v):.2f}  10%-trimmed ${tr10:.2f}  5/95-winsorized ${wz.mean():.2f}")
    top = piv.sort_values("rt_usd", ascending=False).head(8)
    G("  widest 8 sessions (named, not hidden):")
    for d_, r_ in top.iterrows():
        G(f"    {d_}  entry {r_['entry']:.1f} tk  exit {r_['exit']:.1f} tk  "
          f"RT ${r_['rt_usd']:.2f}   [{r_['era']}]")
    piv.to_csv(os.path.join(OUT, "paired_clock_rt.csv"))

    # ------------------------------------------------------------------ Y3
    G("")
    G("Y3 — ERA-COVERAGE HONESTY (the measured rate is an UPPER bound for the full window)")
    tdates = TT["sess_date"].astype(str).str.zfill(8)
    cov_lo = piv.index.min()
    in_cov = (tdates >= cov_lo).sum()
    G(f"  quote evidence spans {cov_lo} .. {piv.index.max()} — "
      f"{len(piv)} sessions")
    G(f"  XM trades inside that span: {int(in_cov)} of {len(TT)} "
      f"({100*in_cov/len(TT):.1f}%). The other {len(TT)-int(in_cov)} trades "
      f"({100*(len(TT)-int(in_cov))/len(TT):.1f}%) have NO quote evidence at all.")
    es = piv.groupby("era")["rt_usd"].agg(["size", "mean", "median"])
    for e_, r_ in es.iterrows():
        G(f"    {e_:<14} n={int(r_['size']):<4} mean ${r_['mean']:.2f} "
          f"median ${r_['median']:.2f}")
    G("  The measured pooled mean is dominated by the WIDEST era. Applying it to all 346")
    G("  trades therefore OVER-charges 2022-2025H1, where no quote exists. Stated, not fixed:")
    G("  inventing a pre-2025 spread would be modelling, which this run is forbidden to do.")

    # ------------------------------------------------------------------ Y4
    G("")
    G("Y4 — COMPARABLE INSTRUMENT: ES at the identical instants (store-quality cross-check)")
    with open(ALLOWLIST_PATH, "r", encoding="utf-8") as f:
        allow = {ln.strip() for ln in f if ln.strip()}
    es_rows = []
    es_dates = sorted({f[1:9] for f in os.listdir(ESNQ_ES) if f.endswith(".parquet")} & allow)
    for d_ in es_dates:
        if d_ not in date_of:
            continue
        s = date_of[d_]
        tb = pq.read_table(os.path.join(ESNQ_ES, f"s{d_}.parquet"),
                           columns=["bip", "time", "price"])
        qt = tb.column("time").to_numpy().astype("datetime64[ns]")
        qb = tb.column("bip").to_numpy()
        qp = tb.column("price").to_numpy()
        del tb
        assert_presealed(pd.DataFrame({"time": qt}), "time", f"ES quotes s{d_}")
        bt = qt[qb == 1].astype("int64"); bp = qp[qb == 1]
        at_ = qt[qb == 2].astype("int64"); ap = qp[qb == 2]
        if len(bt) == 0 or len(at_) == 0:
            continue
        for role, mv in (("entry", ENTM), ("exit", EXITNB)):
            _, ixx = at2(mv, o, True)
            bar = int(ixx[s])
            if bar < 0:
                continue
            inst = int((tarr[bar] - ONE_MIN).astype("datetime64[ns]").astype("int64"))
            ib = np.searchsorted(bt, inst, side="right") - 1
            ia = np.searchsorted(at_, inst, side="right") - 1
            if ib < 0 or ia < 0:
                continue
            if inst - bt[ib] > STALE_NS or inst - at_[ia] > STALE_NS:
                continue
            if ap[ia] < bp[ib]:
                continue
            es_rows.append(dict(date=d_, role=role, spread_pts=ap[ia] - bp[ib],
                                spread_ticks=(ap[ia] - bp[ib]) / 0.25))
    ES = pd.DataFrame(es_rows)
    if len(ES):
        ES.to_csv(os.path.join(OUT, "es_comparable.csv"), index=False)
        for role in ("entry", "exit"):
            s_ = ES[ES["role"] == role]["spread_ticks"]
            nqs = CKok[CKok["role"] == role]
            nqs = nqs[nqs["date"].isin(set(ES["date"]))]["spread_ticks"]
            G(f"  {role:<6} ES n={len(s_):<3} mean {s_.mean():.2f} tk med {s_.median():.2f}  "
              f"|  NQ same dates n={len(nqs):<3} mean {nqs.mean():.2f} tk "
              f"med {nqs.median():.2f}")
        G("  ES is a DIFFERENT contract (tick 0.25 index pts, ~1/5 the notional per tick). This")
        G("  is a store-quality and clock-shape check only — never an XM cost input.")
    else:
        G("  ES store produced no usable observation at these instants.")

    # ------------------------------------------------------------------ Y5
    G("")
    G("Y5 — +1 MINUTE DELAYED FILL ON THE FROZEN XM ACTION SET (execution perturbation)")
    _, ie = at2(ENTM, o, True)
    _, ixn = at2(EXITNB, o, True)
    deltas = np.zeros(NSESS)
    n_shift = n_cap = 0
    for r_ in TT.itertuples():
        s = int(r_.sess)
        e2, x2 = int(r_.eti) + 1, int(r_.xti) + 1
        ep2 = o[e2] if (e2 < n and sid[e2] == s) else float(r_.epx)
        xp2 = o[x2] if (x2 < n and sid[x2] == s) else float(r_.xpx)
        if (e2 < n and sid[e2] == s) and (x2 < n and sid[x2] == s):
            n_shift += 1
        else:
            n_cap += 1
        deltas[s] += int(r_.d) * ((xp2 - ep2) - (float(r_.xpx) - float(r_.epx))) * PV
    wd = pd.Series(deltas[sess_in]).groupby(wk).sum()
    G(f"  trades shifted on both legs {n_shift}, session-end-capped {n_cap}")
    G(f"  delta net/week ${wd.mean():+.2f}  (SE ${wd.std(ddof=1)/np.sqrt(len(wd)):.2f}, "
      f"{len(wd)} wks; total ${wd.sum():+,.0f})")
    G(f"  vs XM baseline $936.32/wk : {100*wd.mean()/936.32:+.1f}%   "
      f"[P1 comparator: -$89.62/wk = -6.4%]")

    # ------------------------------------------------------------------ Y6
    G("")
    G("Y6 — WHY THE MODEL MISSES: MEDIAN vs MEAN, not level")
    for role, mv in (("entry", ENTM), ("exit", EXITNB)):
        s_ = CKok[CKok["role"] == role]["spread_ticks"]
        G(f"  {role:<6} model {float(prof.loc[mv]):.2f} tk (a W82 per-minute MEDIAN)  vs  "
          f"measured median {s_.median():.2f} tk  vs  measured MEAN {s_.mean():.2f} tk  "
          f"(skew {s_.skew():.2f})")
    med_rt = TICKV * (ent["spread_ticks"].median() + ext["spread_ticks"].median()) / 2.0
    mean_rt = TICKV * (ent["spread_ticks"].mean() + ext["spread_ticks"].mean()) / 2.0
    G(f"  RT on medians ${med_rt:.2f}   RT on means ${mean_rt:.2f}   model ${12.50:.2f}")
    G(f"  -> of the ${mean_rt-12.50:.2f} miss, ${med_rt-12.50:.2f} is level and "
      f"${mean_rt-med_rt:.2f} is the right tail the median throws away.")

    # ------------------------------------------------------------------ Y7
    G("")
    G("Y7 — FUNDED-COST SCENARIOS (all applied to the frozen 346-trade action set)")
    gross_tot = float(TT["gross"].sum())
    gs = np.zeros(NSESS)
    for r_ in TT.itertuples():
        gs[int(r_.sess)] = float(r_.gross)
    traded = np.zeros(NSESS, bool)
    traded[TT["sess"].to_numpy().astype(int)] = True

    def econ(spread, label):
        C = COMM_RT + spread
        ser = np.where(traded, gs - C, 0.0)
        w_ = pd.Series(ser[sess_in]).groupby(wk).sum().to_numpy()
        dp = dd_profile(w_)
        return dict(scenario=label, spread=spread, all_in=C,
                    net=float(ser[sess_in].sum()), weekly=float(w_.mean()),
                    maxdd=float(dp["maxdd"]),
                    fixdd=float(w_.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    t=float(w_.mean()) / max(w_.std(ddof=1) / np.sqrt(len(w_)), 1e-9))

    x1_mean = 18.42
    rows = [econ(12.50, "MODELLED (booked)"),
            econ(13.75, "clock medians"),
            econ(x1_mean, "MEASURED matched (X1)"),
            econ(float(v.mean()), "MEASURED clock mean (X2)"),
            econ(x1_mean + 10.0, "PESSIMISTIC (+1 tk/leg)"),
            econ(float(es.loc["2026_Jun_Jul", "mean"]), "recent era only"),
            econ(float(es.loc["2026_Jun_Jul", "mean"]) + 10.0, "recent era + 1 tk/leg"),
            econ(float(np.percentile(v, 90)), "clock p90 every trade"),
            econ(50.0, "absurd stress $50"),
            econ(100.0, "absurd stress $100")]
    EC = pd.DataFrame(rows)
    EC.to_csv(os.path.join(OUT, "scenarios.csv"), index=False)
    G(f"{'scenario':<26}{'spread':>8}{'all-in':>8}{'net total':>13}{'$/wk':>9}"
      f"{'% of booked':>12}{'maxDD':>10}{'t':>7}")
    base = float(EC.loc[0, "weekly"])
    for _, r_ in EC.iterrows():
        G(f"{r_['scenario']:<26}{r_['spread']:>8.2f}{r_['all_in']:>8.2f}"
          f"{r_['net']:>13,.0f}{r_['weekly']:>9.2f}{100*r_['weekly']/base:>11.1f}%"
          f"{r_['maxdd']:>10,.0f}{r_['t']:>7.2f}")
    G(f"  gross-of-all-cost ${gross_tot:,.2f} over {len(TT)} RTs => BREAKEVEN spread "
      f"${gross_tot/len(TT) - COMM_RT:,.2f}/ctrRT (all-in ${gross_tot/len(TT):,.2f})")
    G("")
    G("compliance: read-only on all stores; no blind session; no sealed value; no order/deploy;")
    G("no policy proposed; no model fitted; $0 spent.")
    G(f"wall {_time.time()-T0:.0f}s")
    with open(os.path.join(OUT, "addendum.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
