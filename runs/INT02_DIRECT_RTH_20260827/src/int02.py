"""INT02 - market internals -> DIRECT RTH NQ return.  Frozen by SPEC.md before this ran.

INT01 closed internals -> P1 ACTION VALUE. This is a DIFFERENT MAPPING: internals -> the direct
60-minute RTH NQ return. INT01's null says nothing about it, and a null here says nothing about
internals in general - only about this mapping, at this horizon, with this feature budget.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy import stats as st
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)

DECISIONS = ["09:45", "10:45", "11:45", "12:45", "13:45", "14:45"]
HORIZON_MIN = 60
DOLLARS_PER_POINT = 20.0
COST_PRIMARY = 19.36            # 3 ticks x $5 + $4.36, from MSLAST_CONTRACT's RTH measurement
COST_STRESS = 29.36             # 5 ticks x $5 + $4.36
END_DATE = "2026-05-30"         # BURNED window and the >= 2026-08-01 seal both excluded
SEAL = "2026-08-01"
N_FOLD = 5
SEED = 20260827
MATERIALITY_WEAK = 49.0
MATERIALITY_STRONG = 246.0
ATTEMPTS = []
_fh = open(os.path.join(OUT, "int02.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def load():
    d = {}
    for k in ("TICK", "TRIN", "VIX"):
        x = pd.read_parquet(os.path.join(ROOT, f"research/data_internals/{k}_1m.parquet"))
        x = x[["time", "close"]].rename(columns={"close": k}).set_index("time")
        d[k] = x
    nq = pd.read_parquet(os.path.join(ROOT, "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet"))
    tcol = "time" if "time" in nq.columns else nq.columns[0]
    nq = nq.rename(columns={tcol: "time"})
    nq = nq[["time", "close"]].rename(columns={"close": "NQ"}).set_index("time")
    m = d["TICK"].join(d["TRIN"], how="outer").join(d["VIX"], how="outer").join(nq, how="outer")
    m = m.sort_index()
    m = m[(m.index < pd.Timestamp(SEAL)) & (m.index <= pd.Timestamp(END_DATE) + pd.Timedelta("1D"))]
    assert m.index.max() < pd.Timestamp(SEAL), "SEAL VIOLATION"
    return m


def build(m):
    m = m.copy()
    m["date"] = m.index.normalize()
    # trailing statistics on the 1-minute grid; every one is causal by construction
    for k in ("TICK", "TRIN", "VIX"):
        m[k] = m[k].ffill(limit=5)
    m["NQ"] = m["NQ"].ffill(limit=5)
    m["nq_ret30"] = (m["NQ"] - m["NQ"].shift(30)) * DOLLARS_PER_POINT
    m["nq_rv30"] = (m["NQ"].diff() * DOLLARS_PER_POINT).rolling(30).std()
    m["tick_d15"] = m["TICK"] - m["TICK"].shift(15)
    m["tick_d30"] = m["TICK"] - m["TICK"].shift(30)
    m["vix_d30"] = m["VIX"] - m["VIX"].shift(30)
    m["tick_extreme30"] = (m["TICK"].abs() > 800).rolling(30).mean()
    m["tick_persist15"] = np.sign(m["TICK"]).rolling(15).mean()

    # 20-SESSION z-scores: computed from PRIOR sessions only (shifted by one full session)
    daily = m.groupby("date")[["TICK", "TRIN", "VIX"]].agg(["mean", "std"])
    daily.columns = [f"{a}_{b}" for a, b in daily.columns]
    roll = daily.rolling(20, min_periods=10).mean().shift(1)      # <- strictly prior sessions
    m = m.join(roll, on="date")
    for k in ("TICK", "TRIN", "VIX"):
        m[f"z_{k}"] = (m[k] - m[f"{k}_mean"]) / m[f"{k}_std"].replace(0, np.nan)
    m["disagree"] = (np.sign(m["z_TICK"]) != np.sign(-m["z_TRIN"])).astype(float)

    feats = ["TICK", "TRIN", "VIX", "z_TICK", "z_TRIN", "z_VIX", "tick_d15", "tick_d30",
             "vix_d30", "tick_extreme30", "tick_persist15", "disagree", "nq_rv30", "nq_ret30"]

    rows = []
    for dstr in DECISIONS:
        hh, mm = int(dstr[:2]), int(dstr[3:])
        # INFORMATION STRICTLY BEFORE t: bars are END-stamped, so the bar labelled t closes AT t
        # and is excluded. Take the bar one minute earlier.
        tinfo = m.index.normalize() + pd.Timedelta(hours=hh, minutes=mm) - pd.Timedelta(minutes=1)
        sel = m.reindex(pd.DatetimeIndex(sorted(set(tinfo))))
        sel = sel[sel[feats].notna().all(axis=1)]
        if len(sel) == 0:
            continue
        entry_t = sel.index + pd.Timedelta(minutes=1)
        exit_t = entry_t + pd.Timedelta(minutes=HORIZON_MIN)
        px_e = m["NQ"].reindex(entry_t).values
        px_x = m["NQ"].reindex(exit_t).values
        f = sel[feats].copy()
        f["date"] = sel.index.normalize()
        f["tod"] = hh + mm / 60.0
        f["move"] = (px_x - px_e) * DOLLARS_PER_POINT
        rows.append(f)
    d = pd.concat(rows).dropna(subset=["move"]).sort_index()
    d = d[d["date"] <= pd.Timestamp(END_DATE)]
    return d, feats + ["tod"]


def policy(pred, move, cost):
    act = np.where(pred > cost, 1, np.where(pred < -cost, -1, 0))
    return act * move - np.abs(act) * cost, act


def oof(X, y, sess, blocks, make):
    pr, ix = [], []
    for k in range(1, N_FOLD + 1):
        tr = np.concatenate(blocks[:k])
        mtr, mte = np.isin(sess, tr), np.isin(sess, blocks[k])
        if mtr.sum() == 0 or mte.sum() == 0:
            continue
        mu, sd = X[mtr].mean(0), X[mtr].std(0)
        sd[sd == 0] = 1
        mo = make().fit((X[mtr] - mu) / sd, y[mtr])
        pr.append(mo.predict((X[mte] - mu) / sd))
        ix.append(np.where(mte)[0])
    return np.concatenate(ix), np.concatenate(pr)


def main():
    m = load()
    d, feats = build(m)
    X = np.nan_to_num(d[feats].values.astype(float), posinf=0, neginf=0)
    y = d["move"].values.astype(float)
    sess = d["date"].values
    order = pd.unique(d["date"])
    blocks = np.array_split(order, N_FOLD + 1)

    P("=" * 104)
    P("=== INT02 - internals -> DIRECT RTH NQ 60-minute return.  Frozen by SPEC.md.")
    P("=" * 104)
    P(f"    decisions {len(d):,}   sessions {len(order)}   features {len(feats)}")
    P(f"    span {pd.Timestamp(d['date'].min()).date()} -> {pd.Timestamp(d['date'].max()).date()}"
      f"   (seal >= {SEAL} not read)")
    P(f"    mean |60-min move| ${np.abs(y).mean():,.2f}   PRIMARY cost ${COST_PRIMARY}   "
      f"STRESS ${COST_STRESS}")
    P("    THE SESSION IS THE DEPENDENCE UNIT: "
      f"{len(order)} sessions, not {len(d):,} decisions.")

    mk = {"RIDGE (primary)": lambda: Ridge(alpha=10.0),
          "GBM shallow (challenger)": lambda: HistGradientBoostingRegressor(
              max_depth=3, max_iter=150, learning_rate=0.05, random_state=SEED)}
    P("")
    P("=" * 104)
    P("=== ARMS")
    P("=" * 104)
    res = {}
    for nm, f in mk.items():
        ATTEMPTS.append(nm)
        ix, pr = oof(X, y, sess, blocks, f)
        pnl, act = policy(pr, y[ix], COST_PRIMARY)
        ss = pd.Series(pnl).groupby(sess[ix]).sum()
        pnlS, _ = policy(pr, y[ix], COST_STRESS)
        ssS = pd.Series(pnlS).groupby(sess[ix]).sum()
        tr = act != 0
        acc = float(np.mean(np.sign(y[ix][tr]) == act[tr])) if tr.sum() else np.nan
        res[nm] = dict(ix=ix, pr=pr, pnl=pnl, act=act, ss=ss, ssS=ssS)
        se = ss.std(ddof=1) / np.sqrt(len(ss))
        P(f"    {nm:<26} ${ss.mean():>8,.2f}/session  t {ss.mean()/se if se>0 else np.nan:>6.2f}  "
          f"net ${ss.sum():>10,.0f}  trade {100*np.mean(tr):>5.1f}%  dir acc {100*acc:>5.1f}%")
        P(f"    {'':<26} STRESS ${ssS.mean():>8,.2f}/session  net ${ssS.sum():>10,.0f}")

    # ---------------------------------------------------------------- nulls (PRIMARY arm)
    nm = "RIDGE (primary)"
    r = res[nm]
    ix, ss = r["ix"], r["ss"]
    obs = float(ss.mean())
    P("")
    P("=" * 104)
    P("=== REFITTED SESSION-BLOCK NULL - model refit from scratch inside every replicate")
    P("=" * 104)
    per_sess_y = [y[sess == s] for s in order]
    n_s = len(order)
    nulls, nrate = [], []
    shifts = list(range(1, min(n_s, 121)))
    for k in shifts:
        yk = np.empty_like(y)
        for i, s in enumerate(order):
            msk = sess == s
            yk[msk] = np.resize(per_sess_y[(i + k) % n_s], int(msk.sum()))
        ixk, prk = oof(X, yk, sess, blocks, mk[nm])
        pk, ak = policy(prk, yk[ixk], COST_PRIMARY)
        nulls.append(float(pd.Series(pk).groupby(sess[ixk]).sum().mean()))
        nrate.append(float(np.mean(ak != 0)))
    nulls = np.array(nulls)
    pct_null = 100.0 * float((nulls < obs).mean())
    P(f"    replicates {len(nulls)}   DISTINCT VALUES {len(np.unique(np.round(nulls,6)))}   "
      f"sd ${nulls.std(ddof=1):,.2f}")
    assert len(np.unique(np.round(nulls, 6))) > 1, "NULL HAS ONE DISTINCT VALUE - it is not a null"
    P(f"    null mean ${nulls.mean():>8,.2f}/session   range [${nulls.min():,.2f}, ${nulls.max():,.2f}]")
    P(f"    observed  ${obs:>8,.2f}/session   ->  {pct_null:.1f}th percentile")

    rng = np.random.default_rng(SEED)
    pl = []
    for _ in range(500):
        rs = np.where(rng.random(len(ix)) < .5, 1, -1) * (r["act"] != 0)
        pp = rs * y[ix] - np.abs(rs) * COST_PRIMARY
        pl.append(float(pd.Series(pp).groupby(sess[ix]).sum().mean()))
    pl = np.array(pl)
    pct_pl = 100.0 * float((pl < obs).mean())
    P("")
    P(f"    activity-matched random-direction placebo: mean ${pl.mean():,.2f}/session   "
      f"observed at {pct_pl:.1f}th percentile")

    # ---------------------------------------------------------------- power
    sd_s = ss.std(ddof=1)
    mde = 2.80 * sd_s / np.sqrt(len(ss))
    P("")
    P("=" * 104)
    P("=== POWER")
    P("=" * 104)
    P(f"    sessions {len(ss)}   per-session sd ${sd_s:,.2f}   MDE ${mde:,.2f}/session")
    P(f"    materiality  WEAK ${MATERIALITY_WEAK:,.0f}  ->  MDE/threshold {mde/MATERIALITY_WEAK:.2f}x")
    P(f"    materiality  STRONG ${MATERIALITY_STRONG:,.0f} ->  MDE/threshold {mde/MATERIALITY_STRONG:.2f}x")
    tcrit = float(st.t.ppf(0.95, len(ss) - 1))
    ub = obs + tcrit * sd_s / np.sqrt(len(ss))
    P(f"    one-sided upper 95 % bound ${ub:,.2f}/session")

    # ---------------------------------------------------------------- gates
    P("")
    P("=" * 104)
    P("=== PREREGISTERED GATES (SPEC.md, fixed before this ran)")
    P("=" * 104)
    g = [("I1 net/session > 0 at PRIMARY", obs > 0, f"${obs:,.2f}"),
         ("I2 > 95th pctile of refitted null", pct_null > 95, f"{pct_null:.1f}th"),
         ("I3 > 95th pctile of placebo", pct_pl > 95, f"{pct_pl:.1f}th"),
         ("I4 net > 0 at STRESS", float(r["ssS"].mean()) > 0, f"${r['ssS'].mean():,.2f}")]
    P(f"    {'gate':<38}{'observed':>18}   verdict")
    P("    " + "-" * 68)
    for nme, ok, obsv in g:
        P(f"    {nme:<38}{obsv:>18}   {'PASS' if ok else '*** FAIL ***'}")
    allp = all(x[1] for x in g)
    P("")
    P(f"    attempts counted: {len(ATTEMPTS)} -> {ATTEMPTS}")
    P("")
    if allp:
        P("    ALL GATES PASS -> a CANDIDATE exists. Freeze it before anything further.")
    else:
        underpowered = mde > MATERIALITY_WEAK
        P("    *** NO CANDIDATE ***")
        P(f"    Verdict: {'CLOSED-BY-POWER' if underpowered and obs > 0 else 'NO CANDIDATE / NO DETECTED SIGNAL'}"
          " for THIS mapping, THIS horizon, THIS feature budget.")
        P("    NOT generalized to 'internals are null'. Does NOT authorize a horizon sweep, a")
        P("    feature expansion or a model upgrade - each is a new hypothesis needing its own spec.")
    _fh.close()


if __name__ == "__main__":
    main()
