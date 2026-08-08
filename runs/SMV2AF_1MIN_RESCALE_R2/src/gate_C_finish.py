"""SMV2AF_1MIN_RESCALE_R2 -- Gate C finish: resume from the already-saved
gate_C_old_regime_daily.csv (the full simulation completed and was written to disk;
gate_C_build_old_regime.py crashed only in the FINAL summary-dict assembly on a key-name
typo, "maxDD_eod" vs metric_row's actual "max_dd" key -- no re-simulation needed, no data
was lost). Computes the bootstrap + era-stats + summary that the original script's tail
half was going to produce.
"""
import os, json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2AF_1MIN_RESCALE_R2")
OUT = os.path.join(RUN, "out")

daily = pd.read_csv(os.path.join(OUT, "gate_C_old_regime_daily.csv"), parse_dates=["sess"])
m = pd.read_csv(os.path.join(OUT, "gate_C_old_regime.csv")).iloc[0]
calendar_check = json.load(open(os.path.join(OUT, "gate_C_session_calendar_check.json")))
sm06_res = json.load(open(os.path.join(ROOT, "runs", "SM06_SOLAR_HISTORY", "out", "result.json")))

SEED, BLOCK, NBOOT = 20260808, 5, 10000
x = daily["net"].to_numpy()
n = len(x)
rng = np.random.default_rng(SEED)
nb = int(np.ceil(n / BLOCK))
starts = rng.integers(0, n, size=(NBOOT, nb))
idx = ((starts[:, :, None] + np.arange(BLOCK)[None, None, :]) % n).reshape(NBOOT, -1)[:, :n]

def path_sharpe(x, idx, chunk=2000):
    shp = np.empty(len(idx))
    for i in range(0, len(idx), chunk):
        X = x[idx[i:i + chunk]]
        mu = X.mean(axis=1); sd_ = X.std(axis=1, ddof=1)
        shp[i:i + chunk] = mu / sd_ * np.sqrt(252)
    return shp

boot_sharpe = path_sharpe(x, idx)
P_gt0 = float((boot_sharpe > 0).mean())
q05, q50, q95 = np.quantile(boot_sharpe, [0.05, 0.50, 0.95])

d = pd.Series(daily["net"].to_numpy(), index=pd.to_datetime(daily["sess"]))
def sharpe(v):
    v = np.asarray(v, dtype=float)
    sd = v.std(ddof=1)
    return v.mean() / sd * np.sqrt(252) if sd > 0 else np.nan
eras = {"2006-09": d["2006":"2009"], "2010-13": d["2010":"2013"],
        "2014-17": d["2014":"2017"], "2018-21": d["2018":"2021"]}
era_stats = {k: {"n_days": len(v), "net": float(v.sum()), "sharpe": sharpe(v)} for k, v in eras.items()}

summary = {
    "gate_verdict": "NOT_BLOCKED -- native 1-minute raw substrate exists and was used directly "
                    "(see gate_C_resolution_check.json; this deviates from SMV2W's 5-minute "
                    "BLOCKED-BY-DATA precedent -- flagged interpretive call, disclosed in "
                    "gate_C_build_old_regime.py's module docstring)",
    "old_regime_window": "2006-01-05 to 2021-12-31 (native 1m bars, gap>1hr session tagging)",
    "n_sessions": int(m["n_sessions"]), "n_bars": int(m["n_bars"]),
    "net_$": float(m["net"]), "sharpe": float(m["sharpe"]), "maxDD_eod": float(m["max_dd"]),
    "CDaR5": float(m["CDaR5"]), "friction_share": float(m["friction_share"]),
    "tgt_changes_per_day": float(m["tgt_changes_per_day"]),
    "boot_sharpe_q05": float(q05), "boot_sharpe_q50": float(q50), "boot_sharpe_q95": float(q95),
    "boot_P_sharpe_gt0": P_gt0,
    "sm06_3m_incumbent_hist_2006_2021_net": sm06_res["net_total"],
    "sm06_3m_incumbent_hist_2006_2021_sharpe": sm06_res["sharpe"],
    "sm06_3m_incumbent_verdict": sm06_res["verdict"],
    "era_stats_1m_rescaled": era_stats,
    "session_calendar_match_rate_vs_sm06": calendar_check["match_rate_vs_sm06"],
}
json.dump(summary, open(os.path.join(OUT, "gate_C_summary.json"), "w"), indent=2)
print(json.dumps(summary, indent=2, default=str))
print("\ndone gate C finish")
