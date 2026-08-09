"""S2_SELTIME R2 stage 2 -- full battery (return/drawdown/right-tail/behavior/chronology/
robustness/capital-map) + gate A/B/C on each product's incumbent-vs-S2 pair. Reads stage 1's
saved out/r2/*.csv,*.npy. Implements r2_spec.yaml's promotion_standard verbatim.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from smv2_common import dd_battery, boot_ci_mean

RUN = os.path.join(ROOT, "runs", "S2_SELTIME")
OUT = os.path.join(RUN, "out", "r2")
D7 = pd.Timestamp("2024-08-05")
SEED, BLOCK, NBOOT = 20260809, 5, 10000


def load(name):
    dd = pd.read_csv(os.path.join(OUT, f"daily_{name}.csv"))
    dd["sess"] = pd.to_datetime(dd["sess"])
    bp = np.load(os.path.join(OUT, f"barpos_{name}.npy"))
    bn = np.load(os.path.join(OUT, f"barpnl_{name}.npy"))
    return dd, bp, bn


def battery_full(dd, label):
    x = dd["net"].to_numpy()
    b = dd_battery(dd["sess"], x, label=label)
    top10_idx = np.argsort(x)[-10:]
    return {**b, "top10_day_sum": float(x[top10_idx].sum()),
            "worst_day": float(x.min()), "avg_contracts_per_day": float(dd["contracts"].mean()),
            "turnover_total_contracts": int(dd["contracts"].sum())}


def gate_A(dd_ctrl, dd_arm):
    bc = battery_full(dd_ctrl, "ctrl"); ba = battery_full(dd_arm, "arm")
    g_sharpe = bc["sharpe"] is not None and ba["sharpe"] > bc["sharpe"]
    g_cdar = ba["CDaR5"] < bc["CDaR5"]
    xc = dd_ctrl.set_index("sess")["net"]; xa = dd_arm.set_index("sess")["net"].reindex(xc.index)
    idx10 = xc.sort_values(ascending=False).index[:10]
    house = float(xa[idx10].sum() / xc[idx10].sum()) if xc[idx10].sum() != 0 else np.nan
    g_top10 = house >= 0.95
    return {"sharpe_ctrl": bc["sharpe"], "sharpe_arm": ba["sharpe"], "d_sharpe": ba["sharpe"] - bc["sharpe"],
            "CDaR_ctrl": bc["CDaR5"], "CDaR_arm": ba["CDaR5"], "d_CDaR": bc["CDaR5"] - ba["CDaR5"],
            "top10_house_retention": house, "PASS": bool(g_sharpe and g_cdar and g_top10)}


def gate_B(dd_ctrl, dd_arm):
    c = dd_ctrl.set_index("sess")["net"]; a = dd_arm.set_index("sess")["net"].reindex(c.index)
    df = pd.DataFrame({"c": c, "a": a}); df["year"] = df.index.year
    yearly = []
    agree = 0
    for y, g in df.groupby("year"):
        sc = g["c"].std(ddof=1); sa = g["a"].std(ddof=1)
        shc = g["c"].mean() / sc * np.sqrt(252) if sc > 0 else np.nan
        sha = g["a"].mean() / sa * np.sqrt(252) if sa > 0 else np.nan
        d = sha - shc
        yearly.append({"year": int(y), "d_sharpe": float(d), "sign": "positive" if d > 0 else "negative"})
        agree += int(d > 0)
    cal_sorted = sorted(c.index); trimmed = cal_sorted[:-106]
    ct = c.reindex(trimmed); at = a.reindex(trimmed)
    sct = ct.std(ddof=1); sat = at.std(ddof=1)
    shct = ct.mean() / sct * np.sqrt(252) if sct > 0 else np.nan
    shat = at.mean() / sat * np.sqrt(252) if sat > 0 else np.nan
    survives_trim = bool(shat > shct)
    n_years = len(yearly)
    return {"yearly": yearly, "n_years": n_years, "n_agree": agree,
            "agree_frac": agree / n_years, "survives_trim_106": survives_trim,
            "PASS": bool(agree >= max(1, round(0.8 * n_years)) and survives_trim)}


def gate_C(barpos_ctrl, barpnl_ctrl, barpos_arm, barpnl_arm):
    top1pct_k = max(1, int(0.01 * len(barpnl_ctrl)))
    idx1 = np.argsort(np.abs(barpnl_ctrl))[-top1pct_k:]
    top1_ret = float(barpnl_arm[idx1].sum() / barpnl_ctrl[idx1].sum()) if barpnl_ctrl[idx1].sum() else np.nan
    idx20 = np.argsort(np.abs(barpnl_ctrl))[-20:]
    top20_ret = float(barpnl_arm[idx20].sum() / barpnl_ctrl[idx20].sum()) if barpnl_ctrl[idx20].sum() else np.nan
    long_c = barpnl_ctrl[barpos_ctrl > 0].sum(); short_c = barpnl_ctrl[barpos_ctrl < 0].sum()
    long_a = barpnl_arm[barpos_arm > 0].sum(); short_a = barpnl_arm[barpos_arm < 0].sum()
    share_c = long_c / (long_c + abs(short_c)) if (long_c + abs(short_c)) else np.nan
    share_a = long_a / (long_a + abs(short_a)) if (long_a + abs(short_a)) else np.nan
    drift = abs(share_a - share_c) * 100 if np.isfinite(share_c) and np.isfinite(share_a) else np.nan
    return {"top1pct_retention": top1_ret, "top20_retention": top20_ret,
            "long_share_ctrl": float(share_c), "long_share_arm": float(share_a),
            "long_share_drift_pp": float(drift),
            "PASS": bool(top1_ret >= 0.90 and top20_ret >= 0.90 and drift <= 15.0)}


def d7_split(dd_ctrl, dd_arm):
    c = dd_ctrl.set_index("sess")["net"]; a = dd_arm.set_index("sess")["net"].reindex(c.index)
    pre = (c.index <= D7); post = ~pre
    out = {}
    for tag, m in (("pre_D7", pre), ("post_D7", post)):
        cc = c[m]; aa = a[m]
        sdc = cc.std(ddof=1); sda = aa.std(ddof=1)
        shc = cc.mean() / sdc * np.sqrt(252) if sdc > 0 else np.nan
        sha = aa.mean() / sda * np.sqrt(252) if sda > 0 else np.nan
        out[tag] = {"n": int(m.sum()), "d_sharpe": float(sha - shc),
                    "d_mean_per_day": float(aa.mean() - cc.mean())}
    return out


def cost_stress(dd_ctrl, dd_arm, tag, extra_comm_per_side, contracts_col="contracts"):
    """2-tick-equivalent friction stress: apply an EXTRA commission-equivalent charge scaled by
    each day's own realised turnover (contracts traded that day), on top of the already-modeled
    commission -- a conservative, disclosed approximation (not a full re-simulation with a
    different _fill tick assumption) applied identically to both arms for a fair comparison."""
    c = dd_ctrl.set_index("sess")["net"] - dd_ctrl.set_index("sess")[contracts_col] * extra_comm_per_side
    a = dd_arm.set_index("sess")["net"] - dd_arm.set_index("sess")[contracts_col] * extra_comm_per_side
    a = a.reindex(c.index)
    sdc = c.std(ddof=1); sda = a.std(ddof=1)
    shc = c.mean() / sdc * np.sqrt(252) if sdc > 0 else np.nan
    sha = a.mean() / sda * np.sqrt(252) if sda > 0 else np.nan
    return {"tag": tag, "extra_comm_per_side": extra_comm_per_side,
            "sharpe_ctrl_stressed": float(shc), "sharpe_arm_stressed": float(sha),
            "d_sharpe_stressed": float(sha - shc), "still_positive": bool(sha > shc)}


def capital_map(dd_arm_minus_ctrl_or_series, stress_mults=(1.0, 1.5, 2.0), thrs=(0.15, 0.20, 0.25),
                 nb=2000, seed=SEED):
    x = dd_arm_minus_ctrl_or_series.to_numpy(dtype=float)
    n_ = len(x)
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, n_, size=(nb, int(np.ceil(n_ / 5))))
    idx = (starts[:, :, None] + np.arange(5)[None, None, :]) % n_
    idx = idx.reshape(nb, -1)[:, :n_]
    rows = []
    for m in stress_mults:
        xs = x * m
        paths = xs[idx]
        eq = np.cumsum(paths, axis=1)
        peak = np.maximum.accumulate(eq, axis=1)
        dd_ = peak - eq
        maxdd = dd_.max(axis=1)
        p95 = np.percentile(maxdd, 95)
        for thr in thrs:
            rows.append({"stress_mult": m, "thr": thr, "p95_maxdd_dollar": float(p95),
                         "capital_needed": float(p95 / thr)})
    return pd.DataFrame(rows)


def run_product(name, ctrl_name, arm_name, extra_comm_per_side, contracts_col="contracts"):
    dd_ctrl, bp_ctrl, bn_ctrl = load(ctrl_name)
    dd_arm, bp_arm, bn_arm = load(arm_name)
    b_ctrl = battery_full(dd_ctrl, f"{name}_incumbent")
    b_arm = battery_full(dd_arm, f"{name}_S2")
    gA = gate_A(dd_ctrl, dd_arm)
    gB = gate_B(dd_ctrl, dd_arm)
    gC = gate_C(bp_ctrl, bn_ctrl, bp_arm, bn_arm)
    d7 = d7_split(dd_ctrl, dd_arm)
    boot_lo, boot_hi, p_pos_mean = boot_ci_mean(
        (dd_arm.set_index("sess")["net"] - dd_ctrl.set_index("sess")["net"]).to_numpy(),
        block=BLOCK, n_boot=NBOOT, seed=SEED)
    cstress = cost_stress(dd_ctrl, dd_arm, "2tick_equiv_extra_comm", extra_comm_per_side, contracts_col)
    cmap_ctrl = capital_map(dd_ctrl.set_index("sess")["net"])
    cmap_arm = capital_map(dd_arm.set_index("sess")["net"])
    exposure_ratio = float(np.abs(bp_arm).mean() / np.abs(bp_ctrl).mean()) if np.abs(bp_ctrl).mean() else np.nan
    max_abs_pos_ctrl = int(np.abs(bp_ctrl).max()); max_abs_pos_arm = int(np.abs(bp_arm).max())

    out = {
        "product": name, "battery_incumbent": b_ctrl, "battery_s2": b_arm,
        "gate_A": gA, "gate_B": gB, "gate_C": gC, "d7_split": d7,
        "bootstrap_d_mean_ci90": [boot_lo, boot_hi], "bootstrap_p_positive": p_pos_mean,
        "cost_stress_2tick": cstress,
        "exposure_ratio_arm_vs_ctrl": exposure_ratio,
        "max_abs_position_ctrl": max_abs_pos_ctrl, "max_abs_position_s2": max_abs_pos_arm,
    }
    with open(os.path.join(OUT, f"summary_{name}.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    cmap_ctrl.to_csv(os.path.join(OUT, f"capital_map_{name}_incumbent.csv"), index=False)
    cmap_arm.to_csv(os.path.join(OUT, f"capital_map_{name}_s2.csv"), index=False)
    print(f"\n=== {name} ===")
    print(f"  net: incumbent {b_ctrl['net']:.2f} -> S2 {b_arm['net']:.2f}  (d={b_arm['net']-b_ctrl['net']:+.2f})")
    print(f"  Sharpe: {gA['sharpe_ctrl']:.4f} -> {gA['sharpe_arm']:.4f}  (d={gA['d_sharpe']:+.4f})")
    print(f"  CDaR5: {gA['CDaR_ctrl']:.2f} -> {gA['CDaR_arm']:.2f}  (d={gA['d_CDaR']:+.2f} better if positive)")
    print(f"  maxDD_eod: {b_ctrl['maxDD_eod']:.2f} -> {b_arm['maxDD_eod']:.2f}")
    print(f"  gate_A={gA['PASS']}  gate_B={gB['PASS']} ({gB['n_agree']}/{gB['n_years']})  gate_C={gC['PASS']}")
    print(f"  bootstrap P(d_mean>0)={p_pos_mean:.3f}")
    print(f"  D7 split: pre={d7['pre_D7']['d_sharpe']:+.4f}  post={d7['post_D7']['d_sharpe']:+.4f}")
    print(f"  cost stress (2-tick equiv): d_sharpe_stressed={cstress['d_sharpe_stressed']:+.4f}  still_positive={cstress['still_positive']}")
    print(f"  exposure ratio (S2/incumbent, mean|pos|): {exposure_ratio:.4f}")
    print(f"  max|pos|: incumbent={max_abs_pos_ctrl}  S2={max_abs_pos_arm}")
    cn_ctrl = cmap_ctrl[(cmap_ctrl.stress_mult == 1.0) & (cmap_ctrl.thr == 0.20)]["capital_needed"].iloc[0]
    cn_arm = cmap_arm[(cmap_arm.stress_mult == 1.0) & (cmap_arm.thr == 0.20)]["capital_needed"].iloc[0]
    print(f"  capital needed (1x stress, 20% DD-thr): incumbent ${cn_ctrl:,.0f} -> S2 ${cn_arm:,.0f}")
    return out


# NQ direct: TICK=0.25 => 2-tick-equiv extra commission approximated as 2 ticks * point_value
# per contract per round-trip-equivalent-day, applied per contract traded that day (conservative)
r_A = run_product("A", "A_incumbent", "A_s2", extra_comm_per_side=2 * 0.25 * 2.0)   # MNQ pv=2.0
r_NQ = run_product("NQ", "NQ_incumbent", "NQ_s2", extra_comm_per_side=2 * 0.25 * 20.0)  # NQ pv=20.0
r_MNQ = run_product("MNQ", "MNQ_incumbent", "MNQ_s2", extra_comm_per_side=2 * 0.25 * 2.0)  # MNQ pv=2.0

print("\nSTAGE 2 (full battery) done.")
