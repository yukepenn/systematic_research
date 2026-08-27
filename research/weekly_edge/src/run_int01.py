"""INT01 - do market internals add information about P1 action value, beyond what RR_W002A had?

Spec: runs/INT01_STAGE_A/spec.yaml, committed at 96a0019 BEFORE this code existed.
STAGE A INFORMATION ONLY. No router, no policy, no threshold, no sizing, nothing promoted.

The increment is measured against RR_W002A's EXACT feature matrix, so the base population is
features.csv (2,131 in-window decisions), restricted to RTH. Using a different base would make
"X + internals beats X" a comparison between two different objects.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                   # noqa: E402
from run_we_w01 import ROOT                                               # noqa: E402
from run_we_w17 import load_deep                                          # noqa: E402

W2A = os.path.join(ROOT, "runs", "RR_W002A_ACTION_VALUE_INFORMATION", "out")
OUT = os.path.join(ROOT, "runs", "INT01_STAGE_A", "out")
INT = os.path.join(ROOT, "research", "data_internals")
os.makedirs(OUT, exist_ok=True)

A, B = np.datetime64("2022-07-01"), np.datetime64("2026-08-01")
SEED, NSHIFT, FIRST_FIT, BLOCK, RIDGE_ALPHA = 1701, 200, 250, 63, 10.0
SEP = 5000                          # bar separation for the causality gate (RR_W002A fix)
EXTREME = 600.0                     # |$TICK| threshold, declared in spec

XCOLS = ["dist_open", "dist_vwap", "runlen", "delta_mag", "prev_ret", "atr_l",
         "nq_move_5m", "nq_move_15m", "nq_move_30m", "nq_path_eff_30m",
         "nq_atr_z", "session_move_so_far", "minute_of_session",
         "rel_volume_1m", "xm_support_mag_15m",
         "causal_quality_score", "quality_score_is_warmup", "size_at_entry",
         "strategy_session_pnl_before_per_ctr", "entry_ordinal_in_session"]
INTCOLS = ["tick_last", "tick_cum15", "tick_persist15", "tick_extreme15",
           "trin_log", "trin_chg15", "vix_last", "vix_chg15", "vix_shock"]

_t0 = _time.time()
_fh = open(os.path.join(OUT, "int01.txt"), "w", encoding="utf-8")


def P_(*a):
    print(*a, flush=True)
    print(*a, file=_fh)
    _fh.flush()


def el():
    return f"[{_time.time() - _t0:6.0f}s]"


# ---------------------------------------------------------------------- internals series
def load_internals():
    S = {}
    for sym, f in (("TICK", "TICK_1m.parquet"), ("TRIN", "TRIN_1m.parquet"),
                   ("VIX", "VIX_1m.parquet")):
        d = pd.read_parquet(os.path.join(INT, f), columns=["time", "close"])
        d["time"] = pd.to_datetime(d["time"])
        d = d.sort_values("time").reset_index(drop=True)
        S[sym] = (d["time"].values.astype("datetime64[ns]").astype(np.int64),
                  d["close"].values.astype(float))
    return S


def build_int_features(S, cutoff_ns, sess_open_ns, corrupt_after=None):
    """Features from internals bars with t <= cutoff. corrupt_after: per-row ns; any bar strictly
    after it is replaced with garbage, which is how the causality contract is TESTED rather than
    asserted."""
    out = {}
    n = len(cutoff_ns)

    def series(sym):
        t, v = S[sym]
        if corrupt_after is None:
            return t, v, None
        return t, v, corrupt_after

    def win(sym, k):
        """values of the k bars ending at cutoff (inclusive), as an (n, k) array; NaN where absent"""
        t, v, ca = series(sym)
        idx = np.searchsorted(t, cutoff_ns, side="right") - 1
        M = np.full((n, k), np.nan)
        for j in range(k):
            jj = idx - (k - 1 - j)
            ok = jj >= 0
            M[ok, j] = v[jj[ok]]
            if ca is not None:
                # any bar STRICTLY AFTER this row's corruption point is garbage
                bad = ok & (t[np.clip(jj, 0, len(t) - 1)] > ca)
                M[bad, j] = 1e9
        return M

    tk = win("TICK", 15)
    out["tick_last"] = tk[:, -1]
    out["tick_cum15"] = np.nansum(tk, axis=1)
    out["tick_persist15"] = np.nanmean(tk > 0, axis=1)
    out["tick_extreme15"] = np.nansum(np.abs(tk) > EXTREME, axis=1)

    tr = win("TRIN", 16)
    with np.errstate(divide="ignore", invalid="ignore"):
        lg = np.log(np.where(tr > 0, tr, np.nan))
    out["trin_log"] = lg[:, -1]
    out["trin_chg15"] = lg[:, -1] - lg[:, 0]

    vx = win("VIX", 16)
    out["vix_last"] = vx[:, -1]
    out["vix_chg15"] = vx[:, -1] - vx[:, 0]

    t, v, ca = series("VIX")
    io = np.searchsorted(t, sess_open_ns, side="left")
    io = np.clip(io, 0, len(v) - 1)
    vopen = v[io]
    if ca is not None:
        vopen = np.where(t[io] > ca, 1e9, vopen)
    out["vix_shock"] = out["vix_last"] - vopen

    # PROBES, declared in the spec
    t, v, ca = series("TICK")
    return out


def probes(S, cutoff_ns, decision_ns, corrupt_after=None):
    t, v = S["TICK"]
    def at(ts):
        idx = np.searchsorted(t, ts, side="right") - 1
        ok = idx >= 0
        o = np.full(len(ts), np.nan)
        o[ok] = v[idx[ok]]
        if corrupt_after is not None:
            bad = ok & (t[np.clip(idx, 0, len(t) - 1)] > corrupt_after)
            o[bad] = 1e9
        return o
    # PROBE_LEAK reads the DECISION bar -> must be dropped.  PROBE_SAFE reads info_cutoff -> kept.
    return at(decision_ns), at(cutoff_ns)


# ---------------------------------------------------------------------- walk-forward
def walk(Xf, y, cols, sess_pos, folds):
    pred = np.full(len(y), np.nan)
    for tr_hi, te_lo, te_hi in folds:
        tr = sess_pos < tr_hi
        te = (sess_pos >= te_lo) & (sess_pos < te_hi)
        if tr.sum() < 50 or te.sum() == 0:
            continue
        Xtr, Xte = Xf[cols].to_numpy()[tr], Xf[cols].to_numpy()[te]
        med = np.nanmedian(Xtr, axis=0)
        med = np.where(np.isfinite(med), med, 0.0)
        Xtr = np.where(np.isfinite(Xtr), Xtr, med)
        Xte = np.where(np.isfinite(Xte), Xte, med)
        mu, sd = Xtr.mean(0), np.maximum(Xtr.std(0), 1e-9)
        Xtr, Xte = (Xtr - mu) / sd, (Xte - mu) / sd
        m = Ridge(alpha=RIDGE_ALPHA).fit(Xtr, y[tr])
        pred[te] = m.predict(Xte)
    return pred


def rho(pred, y):
    g = np.isfinite(pred) & np.isfinite(y)
    if g.sum() < 30 or np.nanstd(pred[g]) == 0:
        return 0.0
    return float(spearmanr(pred[g], y[g]).statistic)


def main():
    P_("=" * 122)
    P_("=== INT01 - MARKET INTERNALS STAGE-A.  Spec 96a0019, committed before this code existed.")
    P_("=== STAGE A INFORMATION ONLY. No router, no policy, no threshold, nothing promoted.")
    P_("=" * 122)

    F = pd.read_csv(os.path.join(W2A, "features.csv"))
    F["session_date"] = pd.to_datetime(F["session_date"])
    L = pd.read_csv(os.path.join(ROOT, "runs", "RR_W001_ACTION_VALUE_LEDGER", "out",
                                 "ledger_p1pct.csv"),
                    usecols=["session_date", "session_id", "entry_ordinal_in_session",
                             "decision_ts", "info_cutoff_ts"])
    L["session_date"] = pd.to_datetime(L["session_date"])
    # KEY MUST INCLUDE session_id. A calendar DATE can host two SESSIONS - the 18:00 evening open
    # belongs to the next session - so (session_date, entry_ordinal) is ambiguous and a first
    # version of this merge silently inflated 2,131 rows to 2,305 by duplicating matches.
    KEY = ["session_date", "session_id", "entry_ordinal_in_session"]
    assert not F.duplicated(KEY).any() and not L.duplicated(KEY).any(), "merge key not unique"
    n0 = len(F)
    F = F.merge(L, on=KEY, how="left")
    assert len(F) == n0, f"merge changed row count {n0} -> {len(F)}"
    assert F["decision_ts"].notna().all(), "unmatched rows after merge"
    F["decision_ts"] = pd.to_datetime(F["decision_ts"])
    F["info_cutoff_ts"] = pd.to_datetime(F["info_cutoff_ts"])
    P_(f"{el()} base population (RR_W002A features.csv)          {len(F):,}")

    S = load_internals()
    cov = set(pd.to_datetime(pd.read_parquet(os.path.join(INT, "TICK_1m.parquet"),
                                             columns=["time"])["time"]).dt.normalize())
    tt = F["decision_ts"].dt.time
    rth = (tt >= pd.Timestamp("09:31").time()) & (tt <= pd.Timestamp("15:59").time())
    F = F[rth & F["session_date"].isin(cov)].sort_values(
        ["session_date", "entry_ordinal_in_session"]).reset_index(drop=True)
    P_(f"{el()} RTH and internals-covered                        {len(F):,}   "
       f"(spec pre-declared ~764 off the 2,139 base; this is the 2,131 base)")

    cutoff = F["info_cutoff_ts"].values.astype("datetime64[ns]").astype(np.int64)
    dec = F["decision_ts"].values.astype("datetime64[ns]").astype(np.int64)
    sopen = (F["session_date"] + pd.Timedelta(hours=9, minutes=31)).values.astype(
        "datetime64[ns]").astype(np.int64)

    feats = build_int_features(S, cutoff, sopen)
    pl, ps = probes(S, cutoff, dec)
    feats["PROBE_LEAK"] = pl
    feats["PROBE_SAFE"] = ps
    for k, v in feats.items():
        F[k] = v

    # ------------------------------------------------------------------ G1 causality gate
    P_("")
    P_("=" * 122)
    P_("=== G1. CAUSALITY GATE - the contract is TESTED, not asserted.")
    P_("=== Every bar strictly after each row's info_cutoff is replaced with garbage and the")
    P_("=== features are rebuilt. Anything that MOVES was reading the future.")
    P_("=" * 122)
    f2 = build_int_features(S, cutoff, sopen, corrupt_after=cutoff)
    pl2, ps2 = probes(S, cutoff, dec, corrupt_after=cutoff)
    f2["PROBE_LEAK"], f2["PROBE_SAFE"] = pl2, ps2

    kept, dropped = [], []
    for k in INTCOLS + ["PROBE_LEAK", "PROBE_SAFE"]:
        a, b = np.asarray(feats[k], float), np.asarray(f2[k], float)
        moved = ~(np.isclose(a, b, equal_nan=True))
        frac = float(np.mean(moved))
        ok = frac < 1e-9
        (kept if ok else dropped).append(k)
        P_(f"    {k:<16} moved on {100*frac:6.2f} % of rows   -> {'KEEP' if ok else 'DROP'}")

    g1_leak = "PROBE_LEAK" in dropped
    g1_safe = "PROBE_SAFE" in kept
    P_("")
    P_(f"    injected LEAK dropped : {g1_leak}      injected SAFE kept : {g1_safe}")
    if not (g1_leak and g1_safe):
        P_("    *** G1 FAILED - the gate cannot tell a leak from a lag. ABORTING per spec. ***")
        _fh.close()
        return 1
    P_("    G1 PASS - the gate discriminates. Proceeding.")
    use_int = [c for c in INTCOLS if c in kept]
    P_(f"    internals features surviving: {len(use_int)} of {len(INTCOLS)}  {use_int}")

    # ------------------------------------------------------------------ walk-forward
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    cal = np.array(sorted(d for d in pd.to_datetime(D["sess_date"])
                          if A <= np.datetime64(d) < B))
    cal_pos = {pd.Timestamp(d): j for j, d in enumerate(cal)}
    sess_pos = F["session_date"].map(cal_pos).to_numpy()
    folds = []
    lo = FIRST_FIT
    while lo < len(cal):
        folds.append((lo, lo, min(lo + BLOCK, len(cal))))
        lo += BLOCK
    P_(f"{el()} {len(cal):,} calendar sessions, {len(folds)} folds")

    y = F["target_full"].to_numpy()
    P_(f"{el()} target delta_total_window   mean ${y.mean():,.2f}  sd ${y.std(ddof=1):,.2f}")

    rng = np.random.default_rng(SEED)
    NEGC = [f"NEG_{i}" for i in range(len(use_int))]
    for i, c in enumerate(NEGC):                      # known-null, matched in count
        F[c] = rng.standard_normal(len(F))

    ARMS = {"X": XCOLS, "X_plus_INT": XCOLS + use_int, "INT": use_int,
            "NEGCTRL": XCOLS + NEGC}
    P_("")
    P_("=" * 122)
    P_("=== ARMS - declared in the spec before any of this ran")
    P_("=" * 122)
    res = {}
    for name, cols in ARMS.items():
        p = walk(F, y, cols, sess_pos, folds)
        res[name] = (p, rho(p, y))
        P_(f"    {name:<12} {len(cols):>3} features   OOS rho {res[name][1]:+.4f}")

    # ------------------------------------------------------------------ refitted null
    P_("")
    P_("=" * 122)
    P_("=== NULL - session-boundary circular shifts, ENTIRE walk-forward refitted inside each")
    P_("=" * 122)
    uniq = np.array(sorted(set(sess_pos)))
    null = {k: [] for k in ARMS}
    for s in range(NSHIFT):
        k = rng.integers(1, len(uniq))
        m = {old: uniq[(i + k) % len(uniq)] for i, old in enumerate(uniq)}
        order = np.argsort([m[v] for v in sess_pos], kind="stable")
        ysh = y[order]
        for name, cols in ARMS.items():
            null[name].append(rho(walk(F, ysh, cols, sess_pos, folds), ysh))
        if (s + 1) % 50 == 0:
            P_(f"{el()}    {s+1}/{NSHIFT} shifts")

    P_("")
    P_(f"    {'arm':<12}{'OOS rho':>10}{'null p50':>11}{'null p95':>11}{'percentile':>12}")
    P_("    " + "-" * 56)
    pct = {}
    for name in ARMS:
        d = np.array(null[name])
        pct[name] = float((d < res[name][1]).mean() * 100)
        P_(f"    {name:<12}{res[name][1]:>+10.4f}{np.percentile(d,50):>+11.4f}"
           f"{np.percentile(d,95):>+11.4f}{pct[name]:>11.1f}th")

    # ------------------------------------------------------------------ gates
    fold_inc = []
    pX, pXI = res["X"][0], res["X_plus_INT"][0]
    for tr_hi, te_lo, te_hi in folds:
        te = (sess_pos >= te_lo) & (sess_pos < te_hi)
        if te.sum() < 30:
            continue
        fold_inc.append(rho(pXI[te], y[te]) - rho(pX[te], y[te]))
    fold_pos = float(np.mean(np.array(fold_inc) > 0)) if fold_inc else 0.0

    P_("")
    P_("=" * 122)
    P_("=== GATES - all declared in spec 96a0019 before results existed")
    P_("=" * 122)
    G = [
        ("G1", "causality gate drops the leak and keeps the safe probe", True),
        ("G2", "X_plus_INT OOS rho exceeds X", res["X_plus_INT"][1] > res["X"][1]),
        ("G3", "X_plus_INT exceeds the 95th pctile of its OWN refitted null", pct["X_plus_INT"] >= 95),
        ("G4", "X_plus_INT beats NEGCTRL and NEGCTRL does not beat its own null",
         (res["X_plus_INT"][1] > res["NEGCTRL"][1]) and (pct["NEGCTRL"] < 95)),
        ("G5", "increment positive in a majority of folds", fold_pos > 0.5),
    ]
    for k, txt, ok in G:
        P_(f"    {k}  {'PASS' if ok else 'FAIL'}   {txt}")
    P_("")
    P_(f"    fold-level increment positive in {100*fold_pos:.0f} % of {len(fold_inc)} folds")

    both_neg = (res["X"][1] < 0) and (res["X_plus_INT"][1] < 0)
    neg_tops = res["NEGCTRL"][1] >= max(res[k][1] for k in ("X", "X_plus_INT", "INT"))
    P_("")
    P_("    DECLARED READING RULES, applied:")
    P_(f"      both arms worse than chance?            {both_neg}"
       f"   {'-> any G2 pass carries NO WEIGHT' if both_neg else ''}")
    P_(f"      NEGCTRL >= every real arm?              {neg_tops}"
       f"   {'-> NULL regardless of other gates' if neg_tops else ''}")

    verdict = "NULL" if (neg_tops or not all(o for _, _, o in G)) else "SIGNAL"
    P_("")
    P_(f"    VERDICT: {verdict}")
    pd.DataFrame([dict(arm=k, oos_rho=res[k][1], null_pct=pct[k]) for k in ARMS]).to_csv(
        os.path.join(OUT, "arms.csv"), index=False)
    pd.DataFrame([dict(gate=k, passed=o, text=t) for k, t, o in G]).to_csv(
        os.path.join(OUT, "gates.csv"), index=False)
    P_(f"\n{el()} done")
    _fh.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
