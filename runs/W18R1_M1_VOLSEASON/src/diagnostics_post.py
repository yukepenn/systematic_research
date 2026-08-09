"""W18R1 post-hoc diagnostics — committed so every figure in REPORT.md is reproducible.

Two of these were originally run inline from the shell rather than from a committed script,
which the red team correctly flagged (D10): `root_cause_S_freeze.csv` and
`warmup_convergence.csv` existed as outputs with no script behind them. This file is that
script. It regenerates both, plus the verification of the red team's D3/D4/D5 findings that
the orchestrator ran independently before ingesting them.

    python diagnostics_post.py
"""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd

import common as C
import sm01_solarsim as sm

bars = C.load_dev_bars()
sess = bars["sess_date"].to_numpy()
close = bars["close"].to_numpy()
sigma = np.load(os.path.join(C.OUT, "sigma460_dev.npy"))
f_bar = np.load(os.path.join(C.OUT, "f_causal.npy"))
hh = pd.to_datetime(bars["time"]).dt.hour.to_numpy()
cohort = np.where(hh >= 18, "EVENING", np.where(hh < 9, "OVERNIGHT", "RTH"))


# ------------------------------------------------------------------ 1. S-freeze root cause
def s_freeze_table():
    rows = []
    for label, sig in (("control", sigma), ("arm_FULL", sigma * f_bar)):
        S_all, F_at_flip, nflip = [], [], 0
        for vm in C.INCUMBENT_VMS:
            is_up, flip, s_eff, anchor = sm.member_states(close, sig, float(vm))
            S_all.append(s_eff)
            m = flip != 0
            nflip += int(m.sum())
            F_at_flip.append(f_bar[m])
        S = np.column_stack(S_all)
        Fq = np.concatenate(F_at_flip)
        r = {"arm": label, "n_flips": nflip, "mean_S_pts": float(S.mean()),
             "median_S_pts": float(np.median(S)),
             "mean_f_at_flip_bars": float(Fq.mean()),
             "median_f_at_flip_bars": float(np.median(Fq)),
             # RED TEAM D6: mean_S over BARS is time-in-trend weighted, so it is partly an
             # EFFECT of the flip collapse. The flip-weighted figure is the honest one for
             # "how much wider is the threshold the machine actually chooses".
             "mean_S_flip_weighted_pts": float(np.concatenate(
                 [np.column_stack(S_all)[:, i][sm.member_states(close, sig, float(vm))[1] != 0]
                  for i, vm in enumerate(C.INCUMBENT_VMS)]).mean()),
             # RED TEAM D8: clamp contamination.
             "pct_member_bars_at_1200t_ceiling": float((S >= 1200 * 0.25 - 1e-9).mean() * 100)}
        for c in ("EVENING", "OVERNIGHT", "RTH"):
            r["meanS_" + c] = float(S[cohort == c].mean())
        rows.append(r)
    d = pd.DataFrame(rows)
    d.loc[len(d)] = {"arm": "ALL_BARS_reference", "mean_f_at_flip_bars": float(f_bar.mean()),
                     "median_f_at_flip_bars": float(np.median(f_bar))}
    d.to_csv(os.path.join(C.OUT, "root_cause_S_freeze.csv"), index=False)
    return d


# ------------------------------------------------------------------ 2. warmup convergence
def warmup_table():
    tgt_full = np.load(os.path.join(C.OUT, "tgt_control.npy"))
    rows = []
    for start in ("2023-01-03", "2024-01-02", "2025-01-02"):
        sd = dt.date.fromisoformat(start)
        i0 = int(np.argmax(sess >= sd))
        b2 = bars.iloc[i0:].reset_index(drop=True)
        t2 = sm.e10_target(C.build_pend(b2, sm.sigma_series(b2["close"].to_numpy())))
        t1 = tgt_full[i0:]
        diff = t1 != t2
        s2 = b2["sess_date"].to_numpy()
        bad = pd.unique(s2[diff])
        su = list(pd.unique(s2))
        rows.append({"fresh_start": start, "n_bars": len(b2), "n_sessions": len(su),
                     "bars_disagreeing": int(diff.sum()),
                     "pct_bars_disagreeing": float(diff.mean() * 100),
                     "sessions_with_any_disagreement": int(len(bad)),
                     "LAST_session_with_disagreement": str(bad[-1]) if len(bad) else None,
                     "sessions_until_last_disagreement":
                         (su.index(bad[-1]) + 1) if len(bad) else 0})
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(C.OUT, "warmup_convergence.csv"), index=False)
    return d


# ------------------------------------- 3. independent verification of red-team D3/D4/D5
def redteam_verification():
    c = pd.read_csv(os.path.join(C.OUT, "daily_control.csv"))
    f = pd.read_csv(os.path.join(C.OUT, "daily_arm_FULL.csv"))
    c["sess"] = c["sess"].astype(str); f["sess"] = f["sess"].astype(str)
    m = c.merge(f, on="sess", suffixes=("_c", "_f")); m["y"] = m["sess"].str[:4]
    own_top10 = {"control": float(np.sort(c.net)[-10:].sum()),
                 "arm_FULL": float(np.sort(f.net)[-10:].sum())}
    own_top10["ratio_own_dates"] = own_top10["arm_FULL"] / own_top10["control"]
    d = (m.net_f - m.net_c)
    yr = m.groupby("y").apply(lambda x: pd.Series({
        "n": len(x), "net_c": x.net_c.sum(), "net_f": x.net_f.sum(),
        "gap": (x.net_f - x.net_c).sum(),
        "sharpe_c": x.net_c.mean() / x.net_c.std(ddof=1) * 252 ** .5,
        "sharpe_f": x.net_f.mean() / x.net_f.std(ddof=1) * 252 ** .5}), include_groups=False)
    yr["gap_share"] = yr["gap"] / d.sum()
    yr.to_csv(os.path.join(C.OUT, "yearly_breakdown.csv"))

    x, y = m.net_c.to_numpy(), m.net_f.to_numpy()
    n = len(x); rng = np.random.default_rng(20260808); B, blk = 10000, 5
    nb = int(np.ceil(n / blk))
    st = rng.integers(0, n, size=(B, nb))
    idx = ((st[:, :, None] + np.arange(blk)[None, None, :]) % n).reshape(B, -1)[:, :n]
    sh = lambda a: (lambda A: A.mean(1) / A.std(1, ddof=1) * 252 ** .5)(a[idx])
    d_sh = sh(y) - sh(x)
    out = {"own_dates_top10": own_top10,
           "total_gap": float(d.sum()),
           "gap_share_2026_stub": float(yr.loc["2026", "gap_share"]),
           "dSharpe_q05": float(np.quantile(d_sh, .05)),
           "dSharpe_q50": float(np.quantile(d_sh, .50)),
           "dSharpe_q95": float(np.quantile(d_sh, .95)),
           "P_dSharpe_gt0": float((d_sh > 0).mean())}
    json.dump(out, open(os.path.join(C.OUT, "redteam_verification.json"), "w"), indent=2)
    return yr, out


if __name__ == "__main__":
    print(s_freeze_table().to_string(index=False), flush=True)
    print()
    print(warmup_table().to_string(index=False), flush=True)
    print()
    yr, out = redteam_verification()
    print(yr.round(3).to_string())
    print(json.dumps(out, indent=2))
