"""SMV2N_WINDFALL_POLICY — seq 372 (policy cells), 373 (placebo battery), 374 (chronology).

R2 of the C-P7 pre-test (parent SMV2I seq 365). Frozen spec: runs/SMV2N_WINDFALL_POLICY/spec.yaml.

Curve: runs/SMV2M_MASTER_BUILD/out/twin_daily.csv truncated to sessions <= 2026-05-31 (dev).
Policy (frozen from the pre-test form, no_moves):
  trigger day t: trailing-5-session PnL r5_t > +2.5 * sigma_t, where sigma_t is the EXPANDING
  std (ddof=1, min_periods=20) of the r5 series through t-1 (strictly prior, .shift(1)),
  zero-centered threshold, burn-in >= 365 calendar days from the first session
  (identical construction to runs/SMV2I_CURVE_READS/step4_cp7.py).
  Scale daily PnL by s for sessions t+1..t+5; retrigger extends the window (union);
  no compounding (scale is s on any in-window day, never s^2).
  SUSPENSION: session u is NOT scaled when the expanding percentile of the 20d realized vol
  of NQ close-to-close log returns, evaluated at the close of session u-1 (causal: exposure
  for session u is set with information through u-1), is > 85.
    vol construction: session closes = close of the LAST 3m bar of each session from
    runs/AUDIT03_BARS/nq_3m_2022_2026.csv via sm01_solarsim.load_bars_3m (sessions <= 2026-05-31
    only); r_t = ln(C_t / C_{t-1}); vol20_t = rolling(20).std(ddof=1); percentile_t = 100 *
    fraction of {vol20_j, j <= t, j valid} that are <= vol20_t (expanding, inclusive).
Cells: s in {0.7, 0.8, 0.9}; center 0.8 decides the verdict, 0.7/0.9 are the plateau read.

Metric conventions (dd_battery-exact, src/analytics/smv2_common.py):
  CDaR_0.95 = mean of the worst max(1, int(0.05*n)) positive EOD drawdowns ("CDaR5" col);
  TUW = longest run of consecutive sessions with EOD dd > 1e-9 ("longest_TUW_days");
  Sharpe = mean/std(ddof=1)*sqrt(252) on daily $ PnL.
  RTC = policy PnL summed over the champion (unscaled twin) top-decile days
        (k = ceil(0.10*n) largest daily PnL values) / champion's own sum over those days.

Placebo (seq 373): 200 paths, seeds 1..200. Each path places the SAME NUMBER and DURATIONS of
scaling windows as the real policy's actually-scaled runs, at uniform-random non-overlapping
positions in the burn-in-eligible region, overlapping neither each other nor ANY real designed
window day (superset of scaled days). No suspension applied to placebo windows (durations
already match the real post-suspension scaled runs). Improvement = unscaled_metric - path_metric.
Gate: real improvement > placebo median + 2*IQR, required for BOTH CDaR_0.95 and TUW.

Chronology (seq 374): dSharpe = Sharpe(policy) - Sharpe(unscaled). LOYO = leave-one-year-out
over {2022..2026}; gate: >= 4/5 leave-outs have sign(dSharpe_loyo) == sign(dSharpe_full)
AND leave-2022-out keeps sign(dSharpe_full). Per-year dSharpe reported as diagnostic.

HARD: no data >= 2026-08-01 is ever used; dev sessions <= 2026-05-31 only.
"""
import os
import sys

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(REPO, "runs", "SMV2N_WINDFALL_POLICY")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(REPO, "src", "analytics"))
from sm01_solarsim import load_bars_3m  # noqa: E402

DEV_END = pd.Timestamp("2026-05-31")
CELLS = [0.7, 0.8, 0.9]
CENTER = 0.8
VOL_PCTL_SUSPEND = 85.0
N_PLACEBO = 200

# ------------------------------------------------------------------ metric helpers

def dd_of(net):
    eq = np.cumsum(np.asarray(net, dtype=float))
    return np.maximum.accumulate(eq) - eq


def cdar95(net):
    """dd_battery 'CDaR5': mean of worst max(1, int(0.05*n)) POSITIVE dd values."""
    dd = dd_of(net)
    ddpos = np.sort(dd[dd > 0])[::-1]
    k = max(1, int(0.05 * len(dd)))
    return float(ddpos[:k].mean()) if len(ddpos) else 0.0


def tuw_longest(net):
    """dd_battery 'longest_TUW_days': longest run of sessions with dd > 1e-9."""
    dd = dd_of(net)
    uw = dd > 1e-9
    tuw = 0
    cur = 0
    for u in uw:
        cur = cur + 1 if u else 0
        tuw = max(tuw, cur)
    return int(tuw)


def sharpe(net):
    net = np.asarray(net, dtype=float)
    sd = net.std(ddof=1)
    return float(net.mean() / sd * np.sqrt(252)) if sd > 0 else np.nan


def sgn(v):
    return 0 if v == 0 else (1 if v > 0 else -1)


# ------------------------------------------------------------------ 0. load + repro gate

tw = pd.read_csv(os.path.join(REPO, "runs", "SMV2M_MASTER_BUILD", "out", "twin_daily.csv"),
                 index_col=0, parse_dates=True)
pnl = tw.iloc[:, 0].astype(float)
pnl = pnl[pnl.index <= DEV_END]
cal = pnl.index
x = pnl.values
n = len(x)
assert cal.max() <= DEV_END, "VIRGIN guard: dev curve extends past 2026-05-31"

tb = pd.read_csv(os.path.join(REPO, "runs", "SMV2M_MASTER_BUILD", "out", "twin_battery.csv")
                 ).set_index("label").loc["MASTER_TWIN_dev"]
repro = {
    "n_days_expected": int(tb["n_days"]), "n_days_got": n,
    "net_expected": float(tb["net"]), "net_got": float(x.sum()),
    "sharpe_expected": float(tb["sharpe"]), "sharpe_got": sharpe(x),
    "cdar95_expected": float(tb["CDaR5"]), "cdar95_got": cdar95(x),
    "tuw_expected": int(tb["longest_TUW_days"]), "tuw_got": tuw_longest(x),
    "maxdd_expected": float(tb["maxDD_eod"]), "maxdd_got": float(dd_of(x).max()),
}
repro["pass"] = bool(
    repro["n_days_expected"] == repro["n_days_got"]
    and abs(repro["net_expected"] - repro["net_got"]) <= 1e-6
    and abs(repro["sharpe_expected"] - repro["sharpe_got"]) <= 1e-9
    and abs(repro["cdar95_expected"] - repro["cdar95_got"]) <= 1e-6
    and repro["tuw_expected"] == repro["tuw_got"]
    and abs(repro["maxdd_expected"] - repro["maxdd_got"]) <= 1e-6)
pd.DataFrame([repro]).to_csv(os.path.join(OUT, "repro_check.csv"), index=False)
print("REPRO:", repro)
if not repro["pass"]:
    print("REPRO FAILED — BLOCKED")
    sys.exit(2)

# ------------------------------------------------------------------ 1. vol suspension series

bars = load_bars_3m(os.path.join(REPO, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
last = bars[bars["is_last_of_sess"]]
closes = pd.Series(last["close"].values, index=pd.to_datetime(last["sess_date"].values))
closes = closes[closes.index <= DEV_END]
assert closes.index.equals(cal), (
    f"session calendar mismatch bars vs twin: {len(closes)} vs {n}")

lr = np.log(closes / closes.shift(1)).values          # close-to-close log returns
vol20 = pd.Series(lr, index=cal).rolling(20).std(ddof=1).values
pct = np.full(n, np.nan)
valid = ~np.isnan(vol20)
vidx = np.where(valid)[0]
hist = vol20[vidx]
for j, t in enumerate(vidx):                          # expanding percentile, inclusive
    pct[t] = 100.0 * (hist[:j + 1] <= vol20[t]).mean()
susp = np.zeros(n, dtype=bool)
susp[1:] = pct[:-1] > VOL_PCTL_SUSPEND                # causal: u suspended by pct at close u-1
pd.DataFrame({"sess": cal, "close": closes.values, "logret": lr, "vol20": vol20,
              "vol_pctl_expanding": pct, "suspended_next_rule_applied_to_this_day": susp}
             ).to_csv(os.path.join(OUT, "vol_suspension.csv"), index=False)

# ------------------------------------------------------------------ 2. trigger (frozen pre-test form)

r5 = pd.Series(x, index=cal).rolling(5).sum()
sig = r5.expanding(min_periods=20).std(ddof=1).shift(1)
burn = (cal - cal[0]).days >= 365
elig = burn & sig.notna().values & r5.notna().values
event = elig & (r5.values > 2.5 * sig.values)
tidx = np.where(event)[0]
n_clusters = int(1 + (np.diff(tidx) > 5).sum()) if len(tidx) else 0
cluster_id = np.zeros(len(tidx), dtype=int)
if len(tidx):
    cluster_id[1:] = np.cumsum(np.diff(tidx) > 5)

in_window = np.zeros(n, dtype=bool)
for t in tidx:
    in_window[t + 1:t + 6] = True
scaled = in_window & ~susp

first_elig = int(np.where(elig)[0][0])
lo = first_elig + 1                                    # earliest index a real window day can occupy

pd.DataFrame({"sess": cal[tidx].date, "r5": r5.values[tidx], "sigma_prior": sig.values[tidx],
              "z": r5.values[tidx] / sig.values[tidx], "cluster_id": cluster_id}
             ).to_csv(os.path.join(OUT, "triggers.csv"), index=False)

# actually-scaled contiguous runs (durations for the placebo battery)
run_lens = []
run_starts = []
i = 0
while i < n:
    if scaled[i]:
        j = i
        while j < n and scaled[j]:
            j += 1
        run_lens.append(j - i)
        run_starts.append(i)
        i = j
    else:
        i += 1

print(f"triggers={len(tidx)} clusters(declustered)={n_clusters} "
      f"designed_window_days={int(in_window.sum())} suspended_in_window={int((in_window & susp).sum())} "
      f"scaled_days={int(scaled.sum())} scaled_runs={len(run_lens)} run_lens={run_lens}")

# ------------------------------------------------------------------ 3. policy cells + daily artifact

cdar_un = cdar95(x)
tuw_un = tuw_longest(x)
sh_un = sharpe(x)
net_un = float(x.sum())
k_dec = int(np.ceil(0.10 * n))
top_idx = np.argsort(x)[::-1][:k_dec]
top_min = float(x[top_idx].min())
top_in_window = int(scaled[top_idx].sum())

daily = pd.DataFrame({"sess": cal, "pnl_unscaled": x, "trigger": event,
                      "in_window": in_window, "suspended": susp, "scaled": scaled})
cell_curves = {}
for s in CELLS:
    scale_vec = np.where(scaled, s, 1.0)
    pol = x * scale_vec
    cell_curves[s] = pol
    daily[f"pnl_s{s:.1f}"] = pol
daily.to_csv(os.path.join(OUT, "policy_daily.csv"), index=False)

# ------------------------------------------------------------------ 4. placebo battery (seq 373)

occupied_base = in_window.copy()                       # placebos avoid ALL designed window days
lens_desc = sorted(run_lens, reverse=True)
pl_rows = []
for seed in range(1, N_PLACEBO + 1):
    rng = np.random.default_rng(seed)
    occ = occupied_base.copy()
    mask = np.zeros(n, dtype=bool)
    ok = True
    for L in lens_desc:
        c = np.concatenate([[0], np.cumsum(occ.astype(int))])
        starts = np.arange(lo, n - L + 1)
        feas = starts[(c[starts + L] - c[starts]) == 0]
        if len(feas) == 0:
            ok = False
            break
        st = int(rng.choice(feas))
        occ[st:st + L] = True
        mask[st:st + L] = True
    row = {"seed": seed, "feasible": ok, "n_windows": len(lens_desc),
           "n_days": int(mask.sum())}
    for s in CELLS:
        if ok:
            pl = x * np.where(mask, s, 1.0)
            row[f"dcdar_s{s:.1f}"] = cdar_un - cdar95(pl)
            row[f"dtuw_s{s:.1f}"] = tuw_un - tuw_longest(pl)
        else:
            row[f"dcdar_s{s:.1f}"] = np.nan
            row[f"dtuw_s{s:.1f}"] = np.nan
    pl_rows.append(row)
plc = pd.DataFrame(pl_rows)
plc.to_csv(os.path.join(OUT, "placebo.csv"), index=False)
n_feas = int(plc["feasible"].sum())

# ------------------------------------------------------------------ 5. chronology battery (seq 374)

years = np.array([d.year for d in cal])
yr_list = [2022, 2023, 2024, 2025, 2026]
chron_rows = []
loyo_gate = {}
for s in CELLS:
    pol = cell_curves[s]
    dsh_full = sharpe(pol) - sh_un
    sign_full = sgn(dsh_full)
    chron_rows.append({"s": s, "scope": "full", "sharpe_unscaled": sh_un,
                       "sharpe_policy": sharpe(pol), "dsharpe": dsh_full,
                       "sign": sign_full, "n_days": n})
    agree = 0
    sign_loyo_2022 = None
    for y in yr_list:
        m = years != y
        dsh = sharpe(pol[m]) - sharpe(x[m])
        chron_rows.append({"s": s, "scope": f"loyo_{y}", "sharpe_unscaled": sharpe(x[m]),
                           "sharpe_policy": sharpe(pol[m]), "dsharpe": dsh,
                           "sign": sgn(dsh), "n_days": int(m.sum())})
        if sgn(dsh) == sign_full:
            agree += 1
        if y == 2022:
            sign_loyo_2022 = sgn(dsh)
    for y in yr_list:                                   # per-year diagnostic (not the gate)
        m = years == y
        dsh = sharpe(pol[m]) - sharpe(x[m])
        chron_rows.append({"s": s, "scope": f"year_{y}", "sharpe_unscaled": sharpe(x[m]),
                           "sharpe_policy": sharpe(pol[m]), "dsharpe": dsh,
                           "sign": sgn(dsh), "n_days": int(m.sum())})
    loyo_gate[s] = {"agree": agree,
                    "loyo2022_keeps_sign": bool(sign_loyo_2022 == sign_full),
                    "pass": bool(agree >= 4 and sign_loyo_2022 == sign_full)}
pd.DataFrame(chron_rows).to_csv(os.path.join(OUT, "chronology.csv"), index=False)

# ------------------------------------------------------------------ 6. gates + policy_cells.csv

cells_rows = []
for s in CELLS:
    pol = cell_curves[s]
    cd = cdar95(pol)
    tu = tuw_longest(pol)
    net_p = float(pol.sum())
    dcdar = cdar_un - cd
    dtuw = tuw_un - tu
    rtc = float(pol[top_idx].sum() / x[top_idx].sum())
    ret = net_p / net_un

    pc = plc[plc["feasible"]]
    med_c = float(pc[f"dcdar_s{s:.1f}"].median())
    iqr_c = float(pc[f"dcdar_s{s:.1f}"].quantile(0.75) - pc[f"dcdar_s{s:.1f}"].quantile(0.25))
    med_t = float(pc[f"dtuw_s{s:.1f}"].median())
    iqr_t = float(pc[f"dtuw_s{s:.1f}"].quantile(0.75) - pc[f"dtuw_s{s:.1f}"].quantile(0.25))
    thr_c = med_c + 2.0 * iqr_c
    thr_t = med_t + 2.0 * iqr_t

    g1_c = bool(cd < cdar_un)
    g1_t = bool(tu < tuw_un)
    g2_c = bool(dcdar > thr_c)
    g2_t = bool(dtuw > thr_t)
    g3 = loyo_gate[s]["pass"]
    g4 = bool(rtc >= 0.97)
    g5 = bool(ret >= 0.97)
    cells_rows.append({
        "s": s, "n_triggers": len(tidx), "n_clusters_declustered": n_clusters,
        "n_designed_window_days": int(in_window.sum()),
        "n_suspended_in_window": int((in_window & susp).sum()),
        "n_scaled_days": int(scaled.sum()), "n_scaled_runs": len(run_lens),
        "net_unscaled": net_un, "net_policy": net_p, "net_retention": ret,
        "cdar95_unscaled": cdar_un, "cdar95_policy": cd, "dcdar": dcdar,
        "tuw_unscaled": tuw_un, "tuw_policy": tu, "dtuw": dtuw,
        "maxdd_unscaled": float(dd_of(x).max()), "maxdd_policy": float(dd_of(pol).max()),
        "sharpe_unscaled": sh_un, "sharpe_policy": sharpe(pol),
        "dsharpe_full": sharpe(pol) - sh_un,
        "rtc": rtc, "rtc_k_days": k_dec, "rtc_topdecile_min_pnl": top_min,
        "rtc_topdecile_days_scaled": top_in_window,
        "placebo_n_feasible": n_feas,
        "placebo_dcdar_median": med_c, "placebo_dcdar_iqr": iqr_c, "placebo_dcdar_thresh": thr_c,
        "placebo_dtuw_median": med_t, "placebo_dtuw_iqr": iqr_t, "placebo_dtuw_thresh": thr_t,
        "loyo_agree_count": loyo_gate[s]["agree"],
        "loyo2022_keeps_sign": loyo_gate[s]["loyo2022_keeps_sign"],
        "gate1_cdar_improve": g1_c, "gate1_tuw_improve": g1_t,
        "gate2_cdar_gt_placebo": g2_c, "gate2_tuw_gt_placebo": g2_t,
        "gate3_loyo": g3, "gate4_rtc": g4, "gate5_retention": g5,
        "all_gates_pass": bool(g1_c and g1_t and g2_c and g2_t and g3 and g4 and g5),
    })
cells = pd.DataFrame(cells_rows)
cells.to_csv(os.path.join(OUT, "policy_cells.csv"), index=False)

center = cells[cells["s"] == CENTER].iloc[0]
verdict = "SURVIVES_R2" if center["all_gates_pass"] else "KILLED_AT_POLICY_LEVEL"
print(cells.T.to_string())
print("\nVERDICT (center s=0.8):", verdict)
