"""W19R1_SELECTIVITY — score construction and the exposure-neutral transform.

Implements frozen spec.yaml §1 (framework) and §2 (arm_ER, arm_TOD) exactly. Every place this
module makes an interpretive choice the frozen spec text does not pin down, the choice is stated
in a docstring and repeated in REPORT.md — nothing is silently decided.
"""
import os, sys
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
import common as C1  # W18R1's validated common.py: load_dev_bars, build_pend, e10_exec, rha, ...

BETA = 0.5  # frozen, spec §1 "why_BETA_is_0.5_and_not_searched" — never swept.


# --------------------------------------------------------------------- causal expanding mean
def causal_expanding_session_mean(sess, x):
    """s_bar_causal[t] = mean(x) over all bars in sessions STRICTLY BEFORE session(t).

    First session (no prior data): s_bar_causal[t] := x[t] itself, i.e. g_raw=1 trivially for
    every bar in the first session. This is the same cold-start convention W18R1's
    causal_seasonal_factor uses (behave as the unmodified control until there is any history),
    stated explicitly because the frozen spec does not itself specify a first-session convention.
    """
    x = np.asarray(x, dtype=float)
    n = len(x)
    out = np.empty(n)
    cur_sess = sess[0]
    tot_sum = 0.0; tot_cnt = 0
    pend_sum = 0.0; pend_cnt = 0
    cur_mean = None
    for t in range(n):
        if sess[t] != cur_sess:
            tot_sum += pend_sum; tot_cnt += pend_cnt
            pend_sum = 0.0; pend_cnt = 0
            cur_mean = (tot_sum / tot_cnt) if tot_cnt > 0 else None
            cur_sess = sess[t]
        out[t] = x[t] if cur_mean is None else cur_mean
        pend_sum += x[t]; pend_cnt += 1
    return out


# --------------------------------------------------------------------- arm_ER
def er150_score(bars, period=150):
    """ER150_t = |close_t - close_{t-period}| / sum_{i=t-period+1..t} |Delta close_i|, in [0,1].

    First `period` bars of the WHOLE series (only ever the very start of the dev window, 2022-01-03)
    use a shortened window (as many prior differences as exist) rather than being undefined —
    affects at most the first ~150 bars out of ~615,000, disclosed here and in REPORT.md.
    """
    close = bars["close"].to_numpy()
    n = len(close)
    d = C1.abs_dclose(bars)  # d[0]=0 by convention; d[t]=|close_t-close_{t-1}| for t>=1
    csum = np.concatenate(([0.0], np.cumsum(d)))
    lo = np.maximum(0, np.arange(n) - (period - 1))
    window_sum = csum[np.arange(n) + 1] - csum[lo]
    num = np.abs(close - close[np.maximum(0, np.arange(n) - period)])
    with np.errstate(invalid="ignore", divide="ignore"):
        er = np.where(window_sum > 0, num / window_sum, 0.0)
    return np.clip(er, 0.0, 1.0)


# --------------------------------------------------------------------- arm_TOD
XINST = {  # verbatim W18R2_M5_XINST INST dict (tick, point_value); COMM_SIDE=2.18 stated, shared
    "ES":  (os.path.join(ROOT, "runs", "W18_XINST_BARS", "es_3m_2022_2026.csv"), 0.25, 50.0),
    "RTY": (os.path.join(ROOT, "runs", "W18_XINST_BARS", "rty_3m_2022_2026.csv"), 0.10, 50.0),
    "YM":  (os.path.join(ROOT, "runs", "W18_XINST_BARS", "ym_3m_2022_2026.csv"), 1.00, 5.00),
}
COMM_SIDE_XINST = 2.18


def _cohort(bars):
    hh = pd.to_datetime(bars["time"]).dt.hour.to_numpy()
    return np.where(hh >= 18, "EVENING", np.where(hh < 9, "OVERNIGHT", "RTH"))


def build_xinst_control(name, dev_end):
    """Unmodified E10 control on one of ES/RTY/YM: own sigma460, own 13-member ensemble, own
    tick/point-value economics (sm.TICK monkey-patched in try/finally, verbatim M5 pattern)."""
    path, tick, pv = XINST[name]
    b = sm.load_bars_3m(path)
    b = b[b["sess_date"] <= dev_end].reset_index(drop=True)
    sig = sm.sigma_series(b["close"].to_numpy())
    old_tick = sm.TICK
    sm.TICK = tick
    try:
        PEND = C1.build_pend(b, sig)
        tgt = sm.e10_target(PEND)
        daily, bar_pos, bar_pnl = C1.e10_exec(b, tgt, comm_side=COMM_SIDE_XINST, point_value=pv)
    finally:
        sm.TICK = old_tick
    return b, sig, tgt, daily, bar_pos, bar_pnl


def tod_score_from_xinst(nq_bars, dev_end):
    """arm_TOD's score, built ENTIRELY from ES/RTY/YM P&L, never from NQ's (frozen spec §2).

    Interpretive disclosure (not pinned down by the frozen spec text): the per-cohort P&L
    fraction is computed ONCE from the full 2022-2026 ES/RTY/YM dev window (not causally
    re-estimated bar-by-bar), because the object under test is a claim about a persistent
    structural property of index-futures intraday flow (the same status as D4's own descriptive
    NQ cohort split), not an adaptively-learned signal. This is a look-ahead simplification
    relative to a literal live-trading rule; if arm_TOD becomes a CANDIDATE, a causal/expanding
    version of the cohort ranking is the natural R2 follow-up. Regardless of this, the
    exposure-neutrality transform applied on top (g's s_bar_causal, and k(d)) IS fully causal —
    only the score's own construction is a one-shot full-window statistic.

    Returns (s_tod_per_nq_bar, cohort_table_disclosure_df).
    """
    frac_by_cohort = {}
    per_inst_rows = []
    for name in XINST:
        b, sig, tgt, daily, bar_pos, bar_pnl = build_xinst_control(name, dev_end)
        cohort = _cohort(b)
        total = bar_pnl.sum()
        for c in ("EVENING", "OVERNIGHT", "RTH"):
            frac = float(bar_pnl[cohort == c].sum() / total) if total != 0 else 0.0
            frac_by_cohort.setdefault(c, []).append(frac)
            per_inst_rows.append({"instrument": name, "cohort": c, "pnl_fraction": frac,
                                   "cohort_net": float(bar_pnl[cohort == c].sum()),
                                   "total_net": float(total)})
    avg_frac = {c: float(np.mean(v)) for c, v in frac_by_cohort.items()}
    # rank-normalise the 3 cohort-level averaged fractions: (rank-0.5)/3 -> {1/6, 3/6, 5/6}
    order = sorted(avg_frac, key=lambda c: avg_frac[c])
    score_by_cohort = {c: (i + 0.5) / len(order) for i, c in enumerate(order)}

    nq_cohort = _cohort(nq_bars)
    s_tod = np.array([score_by_cohort[c] for c in nq_cohort], dtype=float)

    disclosure = pd.DataFrame(per_inst_rows)
    disclosure["avg_pnl_fraction_across_instruments"] = disclosure["cohort"].map(avg_frac)
    disclosure["rank_normalised_score"] = disclosure["cohort"].map(score_by_cohort)
    return s_tod, disclosure, score_by_cohort, avg_frac


# --------------------------------------------------------------------- exposure-neutral transform
def exposure_neutral_transform(sess, T, s, beta=BETA):
    """T'_t = RHA(T_t * g_final(s_t)), clamp +-10 (frozen spec §1).

    g_raw(s_t)  = 1 + beta*(s_t - s_bar_causal_t)                          in [1-beta/2, 1+beta/2]
                  since s in [0,1] => s_t - s_bar_causal_t in [-1,1] and here beta=0.5, but s_bar
                  is itself a mean of values in [0,1] so the realised range is typically much
                  tighter than the theoretical [-1,1]; g_raw is provably positive for beta<=1,
                  so |T*g_raw| == |T|*g_raw and no sign flip from the transform ever occurs.
    k(d)        = (sum|T| over PRIOR sessions) / (sum|T*g_raw| over PRIOR sessions), first
                  session (no prior data) -> k=1 (neutral), same cold-start convention as above.
    g_final_t   = g_raw_t * k(session(t))
    """
    sbar = causal_expanding_session_mean(sess, s)
    g_raw = 1.0 + beta * (s - sbar)
    assert np.all(g_raw > 0), "g_raw must stay positive for |T*g|==|T|*g; beta/s range violated"
    absT = np.abs(T).astype(float)
    absTg = absT * g_raw

    n = len(T)
    g_final = np.empty(n)
    cur_sess = sess[0]
    tot_absT = 0.0; tot_absTg = 0.0
    pend_absT = 0.0; pend_absTg = 0.0
    cur_k = 1.0
    for t in range(n):
        if sess[t] != cur_sess:
            tot_absT += pend_absT; tot_absTg += pend_absTg
            pend_absT = 0.0; pend_absTg = 0.0
            cur_k = (tot_absT / tot_absTg) if tot_absTg > 0 else 1.0
            cur_sess = sess[t]
        g_final[t] = g_raw[t] * cur_k
        pend_absT += absT[t]; pend_absTg += absTg[t]

    Tp = C1.rha(T.astype(float) * g_final)
    Tp = np.clip(Tp, -10, 10).astype(int)
    return Tp, g_raw, g_final, sbar
