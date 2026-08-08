"""Seq 361 — C-P1 static blend LP frontier (spec-frozen grid, no finer).

Grid w_solar in {0.35..0.65 step .05}; each portfolio built on the rerank equal-vol basis:
p_w = vm(w*DUAL + (1-w)*vm(BM)) (outer vol-match to SIG, identical to champion construction).
Objectives on FIT window (2022-01-01..2024-12-31): CDaR_0.90, EDaR_0.90 (entropic), Ulcer
($100k base), subject to mean daily PnL >= 0.95 x mean(60/40) on fit.
Eval window 2025-01-01..2026-05-31 re-read for ordering preservation. RTC floor vs champion
top-decile up-days over full dev window.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
from smv2i_lib import (OUT, FIT_END, repro_gate, champion, cdar, edar, ulcer_100k,
                       max_dd, rtc_ratio)

res, DUAL, BM, SIG, vm, cal, champ = repro_gate()
assert res["gate_60_40_atol1e-6"]

fit = cal <= FIT_END
ev = ~fit
GRID = [0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65]

champ_fit_mean = champ.values[fit].mean()
rows = []
curves = {}
for w in GRID:
    p = champion(DUAL, BM, vm, w)
    curves[w] = p
    x_fit = p.values[fit]
    x_ev = p.values[ev]
    rr, k = rtc_ratio(p.values, champ.values)
    rows.append({
        "w_solar": w,
        "fit_mean_daily": x_fit.mean(),
        "fit_mean_ratio_vs_6040": x_fit.mean() / champ_fit_mean,
        "constraint_mean_ok": x_fit.mean() >= 0.95 * champ_fit_mean,
        "fit_CDaR90": cdar(x_fit, 0.90),
        "fit_EDaR90": edar(x_fit, 0.90),
        "fit_Ulcer100k": ulcer_100k(x_fit),
        "fit_maxDD": max_dd(x_fit),
        "eval_mean_daily": x_ev.mean(),
        "eval_CDaR90": cdar(x_ev, 0.90),
        "eval_EDaR90": edar(x_ev, 0.90),
        "eval_Ulcer100k": ulcer_100k(x_ev),
        "eval_maxDD": max_dd(x_ev),
        "rtc_ratio_fulldev": rr,
        "rtc_floor_ok": rr >= 0.97,
    })
df = pd.DataFrame(rows)

# sanity: EDaR >= CDaR must hold everywhere
assert (df["fit_EDaR90"] >= df["fit_CDaR90"] - 1e-6).all()
assert (df["eval_EDaR90"] >= df["eval_CDaR90"] - 1e-6).all()

OBJ = ["CDaR90", "EDaR90", "Ulcer100k"]
opt = {}
for o in OBJ:
    sub = df[df["constraint_mean_ok"]]
    opt[f"fit_opt_{o}"] = float(sub.loc[sub[f"fit_{o}"].idxmin(), "w_solar"])
    opt[f"eval_opt_{o}"] = float(sub.loc[sub[f"eval_{o}"].idxmin(), "w_solar"])
    # eval ordering preservation reads
    fr = df[f"fit_{o}"].rank()
    er = df[f"eval_{o}"].rank()
    opt[f"spearman_fit_eval_{o}"] = float(np.corrcoef(fr, er)[0, 1])
    wf = opt[f"fit_opt_{o}"]
    ev_at_fitopt = float(df.loc[df["w_solar"] == wf, f"eval_{o}"].iloc[0])
    ev_at_6040 = float(df.loc[df["w_solar"] == 0.60, f"eval_{o}"].iloc[0])
    opt[f"eval_fitopt_beats_6040_{o}"] = bool(ev_at_fitopt <= ev_at_6040)

fit_opts = [opt[f"fit_opt_{o}"] for o in OBJ]
opt["fit_optima_agree_007"] = bool(max(fit_opts) - min(fit_opts) <= 0.07 + 1e-12)
opt["fit_eval_opt_agree_007"] = bool(all(abs(opt[f"fit_opt_{o}"] - opt[f"eval_opt_{o}"]) <= 0.07 + 1e-12 for o in OBJ))
opt["joint_opt_in_6040_zone"] = bool(opt["fit_optima_agree_007"]
                                     and all(w in (0.55, 0.60, 0.65) for w in fit_opts))
rtc_ok_at_opts = all(bool(df.loc[df["w_solar"] == w, "rtc_floor_ok"].iloc[0]) for w in fit_opts)
opt["rtc_ok_at_fit_optima"] = bool(rtc_ok_at_opts)

df.to_csv(os.path.join(OUT, "c_p1_frontier.csv"), index=False)
pd.DataFrame([opt]).to_csv(os.path.join(OUT, "c_p1_verdict.csv"), index=False)
pd.DataFrame({"sess": cal, **{f"w{int(round(w*100)):02d}": curves[w].values for w in GRID}}
             ).to_csv(os.path.join(OUT, "c_p1_curves.csv"), index=False)

pd.set_option("display.width", 250)
print(df.round(3).to_string())
print()
for k, v in opt.items():
    print(f"{k}: {v}")
