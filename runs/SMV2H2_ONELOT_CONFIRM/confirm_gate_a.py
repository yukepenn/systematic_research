"""SMV2H2_ONELOT_CONFIRM — Gate A (dev paired bootstrap), LOYO, top-10 retention.

R2 CONFIRMATION, seq 358-360. Spec: runs/SMV2H2_ONELOT_CONFIRM/spec.yaml (frozen).

Regenerates the four dev policy curves (A_dom s5/s7/s9 + SM14 oldM(3,1)) on BOTH
instruments by replicating runs/SMV2H_ONECONTRACT/smv2h.py verbatim (state
construction, run_policy executor, cost tuples), cross-checks against the saved
canonical outputs, then runs the PREREGISTERED paired moving-block bootstrap
(block=5, B=10000, seed=20260808, house circular-block index construction from
src/analytics/smv2_common.boot_ci_mean) on the paired daily vectors.

statistic_1: delta_Sharpe = Sharpe(A_dom) - Sharpe(SM14) per resample path
statistic_2: delta_CDaR  = CDaR_0.95(SM14) - CDaR_0.95(A_dom) per path (+ = challenger better)
CDaR_0.95   : mean of the worst 5% of daily drawdown values d_t = (peak-to-date - equity)
              on the cumulative EOD curve; k = max(1, int(0.05*n)) days.

Run from repo root: python runs/SMV2H2_ONELOT_CONFIRM/confirm_gate_a.py
"""
import sys, os, json
import numpy as np, pandas as pd

sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m, _fill
from sm_bmom import rth_3m, BAND_DAYS

RUN = "runs/SMV2H2_ONELOT_CONFIRM"
OUT = f"{RUN}/out"; os.makedirs(OUT, exist_ok=True)
PAR = "runs/SMV2H_ONECONTRACT/out"
MNQ = (0.65, 2.0); NQ = (2.18, 20.0)
SEED, BLOCK, NBOOT = 20260808, 5, 10000
DEV_END = pd.Timestamp("2026-05-31")

def rha(x): return np.sign(x) * np.floor(np.abs(x) + 0.5)

# ---------------- substrate (dev prefix only; states are causal => identical to
# smv2h.py's compute-full-then-subset on the dev window) ----------------
print("substrate ...", flush=True)
bars_full = load_bars_3m()
sess_full = pd.to_datetime(bars_full["sess_date"])
devmask = (sess_full <= DEV_END).to_numpy()
assert bars_full.loc[devmask].index.max() == devmask.sum() - 1, "dev window must be a prefix"
bars = bars_full.loc[devmask].reset_index(drop=True)   # dev prefix; nothing >= 2026-06 used
del bars_full

bp = pd.read_parquet("runs/SM01_SUBSTRATE/out/e10_bar_pnl.parquet")
assert len(bp) == len(devmask)
T = bp["tgt"].to_numpy().astype(float)[devmask]

# HTF: prior-session close vs SMA50 of session closes (verbatim smv2h.py)
sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
htf = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
st_bar = np.array([htf.get(d, np.nan) for d in bars["sess_date"]])

agree = (np.sign(T) != 0) & (st_bar == np.sign(T))
m = np.where(agree, 1.25, 1.0)
s = np.where((T < 0) & (st_bar > 0), 0.5, 1.0)
Tpp = np.clip(rha(T * m * s * 0.9026), -13, 13)          # DUAL_HTF target (T-dd)
Tp_old = np.clip(rha(T * m * 0.9026), -13, 13)           # SM14 (no DUAL halving)
np.save(f"{OUT}/tdd_dev_from_tgt.npy", Tpp)              # evidence for gate-B verification

# B-MOM pending position per bar (frozen state machine, verbatim smv2h.py)
print("bmom state ...", flush=True)
def bmom_pos_series(bars3):
    r = rth_3m(bars3)
    pos_arr = np.zeros(len(bars3))
    hist, day_count = {}, 0
    for d, g in r.groupby("date", sort=True):
        g = g.sort_values("hm")
        if g["hm"].iloc[0] != 933:
            continue
        open0930 = g["open"].iloc[0]
        close = g["close"].to_numpy(); vol = g["volume"].to_numpy(); hm = g["hm"].to_numpy()
        vwap = np.cumsum(close * vol) / np.maximum(np.cumsum(vol), 1e-9)
        gidx = g.index.to_numpy()
        pos = 0
        flat_hm = int(hm[hm <= 1557].max()) if (hm <= 1557).any() else None
        if day_count >= BAND_DAYS:
            for i in range(len(g)):
                h = int(hm[i])
                if flat_hm is not None and h == flat_hm:
                    pos = 0
                    pos_arr[gidx[i]] = pos
                    break
                if h > 1554:
                    pos_arr[gidx[i]] = pos
                    continue
                past = hist.get(h)
                if past is not None and len(past) >= 1:
                    m_tod = float(np.mean(past[-BAND_DAYS:]))
                    upper, lower = open0930 + m_tod, open0930 - m_tod
                    if close[i] > max(upper, vwap[i]): pos = 1
                    elif close[i] < min(lower, vwap[i]): pos = -1
                pos_arr[gidx[i]] = pos
        for i in range(len(g)):
            hist.setdefault(int(hm[i]), []).append(abs(close[i] - open0930))
        day_count += 1
    return pos_arr

B = bmom_pos_series(bars)
Mp_old = 0.7086 * Tp_old + 2.83 * B

# ---------------- one-lot executor (verbatim smv2h.py run_policy) ----------------
def run_policy(bars, desired, comm, pv):
    n = len(bars)
    o = bars["open"].to_numpy(); h = bars["high"].to_numpy(); l = bars["low"].to_numpy()
    c = bars["close"].to_numpy(); last = bars["is_last_of_sess"].to_numpy()
    hm = bars["time"].dt.hour.to_numpy() * 100 + bars["time"].dt.minute.to_numpy()
    sd = bars["sess_date"].to_numpy()
    cash = 0.0; p = 0; pend = 0; daily = {}; prev = 0.0
    fills = 0; eq = np.empty(n)
    for t in range(n):
        if pend != p:
            d = pend - p; side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * pv; cash -= abs(d) * comm
            p = pend; fills += 1
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * pv; cash -= abs(p) * comm
            fills += 1; p = 0; pend = 0
        else:
            want = int(desired[t])
            if hm[t] == 1639:
                pend = 0
            elif 1630 <= hm[t] < 1803:
                pend = p if hm[t] < 1639 else 0
            else:
                pend = want
        eq[t] = cash + p * c[t] * pv
        if last[t]:
            eqv = cash + p * c[t] * pv
            daily[sd[t]] = eqv - prev; prev = eqv
    dl = pd.Series(daily); dl.index = pd.to_datetime(dl.index)
    return dl, fills, eq

def pol_hyst(M, a, b):
    n = len(M); out = np.zeros(n, dtype=np.int64); p = 0
    for t in range(n):
        Mt = M[t]
        if p == 0:
            p = 1 if Mt >= a else (-1 if Mt <= -a else 0)
        elif p == 1:
            p = -1 if Mt <= -a else (0 if Mt <= b else 1)
        else:
            p = 1 if Mt >= a else (0 if Mt >= -b else -1)
        out[t] = p
    return out

def pol_dominant(Tpp, B, solar_min):
    return np.where(B != 0, np.sign(B),
                    np.where(np.abs(Tpp) >= solar_min, np.sign(Tpp), 0)).astype(np.int64)

cells = {
    350: ("A_dominant(solar>=5)", pol_dominant(Tpp, B, 5)),
    351: ("A_dominant(solar>=7)", pol_dominant(Tpp, B, 7)),
    357: ("A_dominant(solar>=9)", pol_dominant(Tpp, B, 9)),
    355: ("SM14_ref_oldM(3,1)",   pol_hyst(Mp_old, 3, 1)),
}

# ---------------- regenerate curves, both instruments ----------------
print("replay ...", flush=True)
def battery(dl):
    net = dl.values; eqd = np.cumsum(net); pk = np.maximum.accumulate(eqd); dd = pk - eqd
    k = max(1, int(0.05 * len(net)))
    cdar = np.sort(dd)[::-1][:k].mean()
    sd_ = net.std(ddof=1)
    return {"n_days": len(net), "net": net.sum(),
            "sharpe": net.mean() / sd_ * np.sqrt(252),
            "maxDD_eod": dd.max(), "CDaR5": cdar, "k_worst_days": k}

curves = {}; stats = {}
for seq, (name, des) in cells.items():
    dl_m, f_m, _ = run_policy(bars, des, *MNQ)
    dl_q, f_q, _ = run_policy(bars, des, *NQ)
    curves[(seq, "MNQ")] = dl_m; curves[(seq, "NQ")] = dl_q
    stats[(seq, "MNQ")] = battery(dl_m) | {"fills": f_m}
    stats[(seq, "NQ")] = battery(dl_q) | {"fills": f_q}
    print(f"{seq} {name:24s} MNQ net {dl_m.sum():9.1f} | NQ net {dl_q.sum():10.1f} fills {f_m}", flush=True)

regen = pd.DataFrame({f"{seq}_{cells[seq][0]}_{inst}": c for (seq, inst), c in curves.items()})
regen.to_csv(f"{OUT}/regen_daily_curves.csv")

# ---------------- cross-check vs canonical saved outputs ----------------
print("cross-check ...", flush=True)
saved_dc = pd.read_csv(f"{PAR}/daily_curves.csv", index_col=0, parse_dates=True)
saved_rs = pd.read_csv(f"{PAR}/results.csv").set_index("seq")
xrows = []
for seq, (name, _) in cells.items():
    col = f"{seq}_{name}"
    dmax = float(np.abs(curves[(seq, "MNQ")].values - saved_dc[col].values).max())
    st_m, st_q = stats[(seq, "MNQ")], stats[(seq, "NQ")]
    r = saved_rs.loc[seq]
    xrows.append({
        "seq": seq, "policy": name,
        "mnq_daily_max_abs_diff": dmax,
        "mnq_net_regen": st_m["net"], "mnq_net_saved": r["net"], "d_net": st_m["net"] - r["net"],
        "mnq_sharpe_regen": st_m["sharpe"], "mnq_sharpe_saved": r["sharpe"], "d_sharpe": st_m["sharpe"] - r["sharpe"],
        "mnq_maxDD_regen": st_m["maxDD_eod"], "mnq_maxDD_saved": r["maxDD_eod"],
        "mnq_CDaR5_regen": st_m["CDaR5"], "mnq_CDaR5_saved": r["CDaR5"], "d_CDaR5": st_m["CDaR5"] - r["CDaR5"],
        "fills_regen": st_m["fills"], "fills_saved": int(r["fills"]),
        "nq_net_regen": st_q["net"], "nq_net_saved": r["nq_net"], "d_nq_net": st_q["net"] - r["nq_net"],
        "nq_sharpe_regen": st_q["sharpe"], "nq_sharpe_saved": r["nq_sharpe"],
        "nq_maxDD_regen": st_q["maxDD_eod"], "nq_maxDD_saved": r["nq_maxDD"],
    })
xdf = pd.DataFrame(xrows)
xdf.to_csv(f"{OUT}/crosscheck_dev.csv", index=False)
recon_ok = (xdf["mnq_daily_max_abs_diff"].max() < 1e-6
            and xdf["d_net"].abs().max() < 0.05 and xdf["d_nq_net"].abs().max() < 0.05
            and (xdf["fills_regen"] == xdf["fills_saved"]).all())
print(xdf.round(4).to_string())
print("RECONCILED:", recon_ok, flush=True)

# ---------------- paired moving-block bootstrap (house circular construction) ----------------
print("bootstrap ...", flush=True)
n = stats[(355, "MNQ")]["n_days"]
k5 = max(1, int(0.05 * n))
rng = np.random.default_rng(SEED)
nb = int(np.ceil(n / BLOCK))
starts = rng.integers(0, n, size=(NBOOT, nb))
idx = ((starts[:, :, None] + np.arange(BLOCK)[None, None, :]) % n).reshape(NBOOT, -1)[:, :n]

def path_stats(x, idx, chunk=2000):
    """per-resample-path Sharpe and CDaR_0.95 for daily vector x."""
    shp = np.empty(len(idx)); cdr = np.empty(len(idx))
    for i in range(0, len(idx), chunk):
        X = x[idx[i:i + chunk]]
        mu = X.mean(axis=1); sd_ = X.std(axis=1, ddof=1)
        shp[i:i + chunk] = mu / sd_ * np.sqrt(252)
        eq = np.cumsum(X, axis=1)
        dd = np.maximum.accumulate(eq, axis=1) - eq
        cdr[i:i + chunk] = (-np.partition(-dd, k5 - 1, axis=1)[:, :k5]).mean(axis=1)
    return shp, cdr

ref_paths = {inst: path_stats(curves[(355, inst)].values, idx) for inst in ("MNQ", "NQ")}
grows = []
for seq in (350, 351, 357):
    for inst in ("MNQ", "NQ"):
        x = curves[(seq, inst)].values
        shp, cdr = path_stats(x, idx)
        rshp, rcdr = ref_paths[inst]
        d_shp = shp - rshp                    # statistic_1
        d_cdr = rcdr - cdr                    # statistic_2 (+ = challenger better)
        st, rf = stats[(seq, inst)], stats[(355, inst)]
        grows.append({
            "seq": seq, "policy": cells[seq][0], "instrument": inst,
            "n_days": n, "k_worst_days": k5,
            "sharpe": st["sharpe"], "sharpe_sm14": rf["sharpe"],
            "point_delta_sharpe": st["sharpe"] - rf["sharpe"],
            "CDaR5": st["CDaR5"], "CDaR5_sm14": rf["CDaR5"],
            "point_delta_CDaR": rf["CDaR5"] - st["CDaR5"],
            "P_dSharpe_gt0": (d_shp > 0).mean(), "P_dCDaR_gt0": (d_cdr > 0).mean(),
            "dSharpe_q05": np.quantile(d_shp, 0.05), "dSharpe_q50": np.quantile(d_shp, 0.50),
            "dSharpe_q95": np.quantile(d_shp, 0.95),
            "dCDaR_q05": np.quantile(d_cdr, 0.05), "dCDaR_q50": np.quantile(d_cdr, 0.50),
            "dCDaR_q95": np.quantile(d_cdr, 0.95),
        })
        print(f"{seq} {inst:3s} P(dSharpe>0)={grows[-1]['P_dSharpe_gt0']:.4f} "
              f"P(dCDaR>0)={grows[-1]['P_dCDaR_gt0']:.4f} "
              f"pt dShp {grows[-1]['point_delta_sharpe']:+.4f} pt dCDaR {grows[-1]['point_delta_CDaR']:+.1f}", flush=True)

ga = pd.DataFrame(grows)
# gate evaluation (spec: bootstrap gate on s7 both instruments; s5/s9 point-delta plateau support)
ga["gate_role"] = np.where(ga["seq"] == 351, "CENTER_bootstrap_gate", "plateau_point_support")
ga["passes"] = np.where(
    ga["seq"] == 351,
    (ga["P_dSharpe_gt0"] >= 0.85) & (ga["P_dCDaR_gt0"] >= 0.85),
    (ga["point_delta_sharpe"] > 0) & (ga["point_delta_CDaR"] > 0))
ga.to_csv(f"{OUT}/gate_A.csv", index=False)

center = ga[ga.seq == 351]
gateA_pass = bool(center["passes"].all())
plateau_pass = bool(ga[ga.seq != 351]["passes"].all())
print(f"\nGATE A center s7 pass: {gateA_pass} | plateau s5/s9 support: {plateau_pass}", flush=True)

# ---------------- LOYO (per-year delta table, verification of published addendum) ----------------
lrows = []
for seq in (350, 351, 357):
    for inst in ("MNQ", "NQ"):
        c = curves[(seq, inst)]; r = curves[(355, inst)]
        for yr in sorted(c.index.year.unique()):
            cy = c[c.index.year == yr].values; ry = r[r.index.year == yr].values
            shp_c = cy.mean() / cy.std(ddof=1) * np.sqrt(252)
            shp_r = ry.mean() / ry.std(ddof=1) * np.sqrt(252)
            lrows.append({"seq": seq, "policy": cells[seq][0], "instrument": inst, "year": yr,
                          "net_pol": cy.sum(), "net_sm14": ry.sum(), "d_net": cy.sum() - ry.sum(),
                          "sharpe_pol": shp_c, "sharpe_sm14": shp_r, "d_sharpe": shp_c - shp_r})
loyo = pd.DataFrame(lrows)
loyo.to_csv(f"{OUT}/loyo.csv", index=False)
chk = loyo[(loyo.seq == 350) & (loyo.instrument == "MNQ")]
print("\nLOYO 350 MNQ (addendum check):")
print(chk[["year", "d_net", "d_sharpe"]].round({"d_net": 1, "d_sharpe": 2}).to_string(index=False))

# ---------------- top-10-day retention (right tail) ----------------
trows = []
for inst in ("MNQ", "NQ"):
    ref = curves[(355, inst)]; ch = curves[(351, inst)]
    top10 = ref.nlargest(10)
    ch_on = ch.loc[top10.index]
    own10 = ch.nlargest(10)
    for d in top10.index:
        trows.append({"instrument": inst, "kind": "sm14_top_day", "date": d.date(),
                      "sm14_pnl": ref.loc[d], "adom7_pnl": ch.loc[d]})
    trows.append({"instrument": inst, "kind": "SUMMARY", "date": None,
                  "sm14_pnl": top10.sum(), "adom7_pnl": ch_on.sum(),
                  "retention": ch_on.sum() / top10.sum(),
                  "adom7_own_top10_sum": own10.sum(),
                  "overlap_days": len(set(top10.index) & set(own10.index))})
t10 = pd.DataFrame(trows)
t10.to_csv(f"{OUT}/top10_retention.csv", index=False)
print("\ntop-10 retention:")
print(t10[t10.kind == "SUMMARY"].to_string(index=False))

json.dump({"recon_ok": bool(recon_ok), "gateA_center_pass": gateA_pass,
           "plateau_support_pass": plateau_pass, "n_days": int(n), "k5": int(k5),
           "seed": SEED, "block": BLOCK, "n_boot": NBOOT},
          open(f"{OUT}/gate_A_summary.json", "w"), indent=2)
print("\ndone gate A")
