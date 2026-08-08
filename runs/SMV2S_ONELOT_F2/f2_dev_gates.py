"""SMV2S_ONELOT_F2 — dev gates for the HTF-GATED DOMINANT one-lot family (seq 386-388).

Spec: runs/SMV2S_ONELOT_F2/spec.yaml (frozen at 58dc2d2 before execution).

Policy (NEW family, side-blind HTF gate on the Solar leg; B-MOM keeps priority):
    pos_t = sign(B_t)        if B_t != 0
          = sign(T_dd_t)     if B_t == 0 AND |T_dd_t| >= thr AND HTF_state_t == sign(T_dd_t)
          = 0                otherwise
Cells: thr in {3, 5, 7}; center = thr 5 (seq 387). Reference = SM14 oldM(3,1).

Steps:
  0. Rebuild the dev substrate exactly as runs/SMV2H_ONECONTRACT/smv2h.py /
     runs/SMV2H2_ONELOT_CONFIRM/confirm_gate_a.py (verbatim state + executor code).
  1. REQUIRED RECONCILIATION: regenerate the SM14 reference (and, as extra evidence,
     A_dom 350/351/357) on both instruments and require EXACT match against
     runs/SMV2H2_ONELOT_CONFIRM/out/regen_daily_curves.csv before any new read.
  2. Run the three new cells on MNQ + NQ -> out/cells.csv, out/dev_daily_curves.csv.
  3. Gate A: preregistered paired moving-block bootstrap (block=5, B=10000,
     seed=20260808, house circular construction): center thr5 needs
     P(dSharpe>0) >= 0.85 AND P(dCDaR>0) >= 0.85 vs SM14 on BOTH instruments;
     neighbors thr3/thr7 point-positive on both metrics, both instruments.
  4. Gate B (HARD): top-10-day retention vs SM14 >= 0.90 on both instruments
     (center cell = candidate; neighbors reported for information).

Run from repo root: python runs/SMV2S_ONELOT_F2/f2_dev_gates.py
"""
import sys, os, json
import numpy as np, pandas as pd

sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m, _fill
from sm_bmom import rth_3m, BAND_DAYS

RUN = "runs/SMV2S_ONELOT_F2"
OUT = f"{RUN}/out"; os.makedirs(OUT, exist_ok=True)
H2 = "runs/SMV2H2_ONELOT_CONFIRM/out"
MNQ = (0.65, 2.0); NQ = (2.18, 20.0)
SEED, BLOCK, NBOOT = 20260808, 5, 10000
DEV_END = pd.Timestamp("2026-05-31")

def rha(x): return np.sign(x) * np.floor(np.abs(x) + 0.5)

# ---------------- substrate (dev prefix; verbatim confirm_gate_a.py) ----------------
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
np.save(f"{OUT}/tdd_dev_from_tgt.npy", Tpp)              # evidence for gate-C verification

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

def pol_htf_dominant(Tpp, B, st_bar, thr):
    """HTF-GATED DOMINANT (spec verbatim): B-MOM priority; Solar leg only WITH the
    HTF state (side-blind gate). NaN/0 HTF blocks the Solar leg (no agreement)."""
    solar_ok = (np.abs(Tpp) >= thr) & (st_bar == np.sign(Tpp))
    solar = np.where(solar_ok, np.sign(Tpp), 0)
    return np.where(B != 0, np.sign(B), solar).astype(np.int64)

def battery(dl):
    net = dl.values; eqd = np.cumsum(net); pk = np.maximum.accumulate(eqd); dd = pk - eqd
    k = max(1, int(0.05 * len(net)))
    cdar = np.sort(dd)[::-1][:k].mean()
    sd_ = net.std(ddof=1)
    return {"n_days": len(net), "net": net.sum(),
            "sharpe": net.mean() / sd_ * np.sqrt(252),
            "maxDD_eod": dd.max(), "CDaR5": cdar, "k_worst_days": k}

# ---------------- step 1: REQUIRED reconciliation vs SMV2H2 regen curves ----------------
print("reconciliation vs SMV2H2 regen_daily_curves.csv ...", flush=True)
recon_cells = {
    355: ("SM14_ref_oldM(3,1)",   pol_hyst(Mp_old, 3, 1)),
    350: ("A_dominant(solar>=5)", pol_dominant(Tpp, B, 5)),
    351: ("A_dominant(solar>=7)", pol_dominant(Tpp, B, 7)),
    357: ("A_dominant(solar>=9)", pol_dominant(Tpp, B, 9)),
}
# float_precision="round_trip": pandas' default ("high") CSV parser is off by a few
# ulp vs the stored decimal strings; round_trip recovers the exact written floats
# (verified: SMV2H daily_curves.csv vs SMV2H2 regen agree at 0.0 under round_trip).
h2regen = pd.read_csv(f"{H2}/regen_daily_curves.csv", index_col=0, parse_dates=True,
                      float_precision="round_trip")
curves = {}   # (seq, inst) -> daily Series ; SM14 curves reused as gate reference
fills_map = {}
rrows = []
for seq, (name, des) in recon_cells.items():
    for inst, cost in [("MNQ", MNQ), ("NQ", NQ)]:
        dl, f, _ = run_policy(bars, des, *cost)
        col = f"{seq}_{name}_{inst}"
        ref = h2regen[col]
        assert len(dl) == len(ref) and (dl.index == ref.index).all(), f"index mismatch {col}"
        dmax = float(np.abs(dl.values - ref.values).max())
        rrows.append({"column": col, "n_days": len(dl), "max_abs_daily_diff": dmax,
                      "net_regen": dl.sum(), "net_smv2h2": ref.sum(),
                      "exact": dmax == 0.0})
        if seq == 355:
            curves[(355, inst)] = dl; fills_map[(355, inst)] = f
        print(f"  {col:38s} max|diff| {dmax:.3e} exact={dmax == 0.0}", flush=True)
rdf = pd.DataFrame(rrows)
rdf.to_csv(f"{OUT}/sm14_reconcile.csv", index=False)
sm14_exact = bool(rdf.loc[rdf["column"].str.startswith("355_"), "exact"].all())
all_exact = bool(rdf["exact"].all())
print(f"RECONCILED SM14 exact: {sm14_exact} | all four cells exact: {all_exact}", flush=True)
assert sm14_exact, "SM14 reference reconciliation FAILED (spec requires exact match) — STOP"

# ---------------- step 2: the three new cells ----------------
print("new cells ...", flush=True)
cells = {
    386: ("HTFG_dom(thr3)", pol_htf_dominant(Tpp, B, st_bar, 3)),
    387: ("HTFG_dom(thr5)", pol_htf_dominant(Tpp, B, st_bar, 5)),   # CENTER
    388: ("HTFG_dom(thr7)", pol_htf_dominant(Tpp, B, st_bar, 7)),
}
stats = {}
for seq, (name, des) in cells.items():
    for inst, cost in [("MNQ", MNQ), ("NQ", NQ)]:
        dl, f, _ = run_policy(bars, des, *cost)
        curves[(seq, inst)] = dl; fills_map[(seq, inst)] = f
        stats[(seq, inst)] = battery(dl) | {"fills": f}
    print(f"{seq} {name:16s} MNQ net {curves[(seq,'MNQ')].sum():9.1f} | "
          f"NQ net {curves[(seq,'NQ')].sum():10.1f} fills {fills_map[(seq,'MNQ')]}", flush=True)
for inst in ("MNQ", "NQ"):
    stats[(355, inst)] = battery(curves[(355, inst)]) | {"fills": fills_map[(355, inst)]}

names = {**{k: v[0] for k, v in cells.items()}, 355: "SM14_ref_oldM(3,1)"}
crows = []
for (seq, inst), st in sorted(stats.items()):
    dl = curves[(seq, inst)]
    yr = dl.groupby(dl.index.year).sum()
    crows.append({"seq": seq, "policy": names[seq], "instrument": inst, **st,
                  "years_pos": int((yr > 0).sum()), "n_years": len(yr),
                  **{f"net_{y}": v for y, v in yr.items()}})
pd.DataFrame(crows).to_csv(f"{OUT}/cells.csv", index=False)
pd.DataFrame({f"{seq}_{names[seq]}_{inst}": c for (seq, inst), c in curves.items()
              if seq in (386, 387, 388, 355)}).to_csv(f"{OUT}/dev_daily_curves.csv")

# ---------------- step 3: gate A — paired moving-block bootstrap ----------------
print("bootstrap ...", flush=True)
n = stats[(355, "MNQ")]["n_days"]
k5 = max(1, int(0.05 * n))
rng = np.random.default_rng(SEED)
nb = int(np.ceil(n / BLOCK))
starts = rng.integers(0, n, size=(NBOOT, nb))
idx = ((starts[:, :, None] + np.arange(BLOCK)[None, None, :]) % n).reshape(NBOOT, -1)[:, :n]

def path_stats(x, idx, chunk=2000):
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
for seq in (386, 387, 388):
    for inst in ("MNQ", "NQ"):
        x = curves[(seq, inst)].values
        shp, cdr = path_stats(x, idx)
        rshp, rcdr = ref_paths[inst]
        d_shp = shp - rshp                    # statistic_1
        d_cdr = rcdr - cdr                    # statistic_2 (+ = challenger better)
        st, rf = stats[(seq, inst)], stats[(355, inst)]
        grows.append({
            "seq": seq, "policy": names[seq], "instrument": inst,
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
              f"pt dShp {grows[-1]['point_delta_sharpe']:+.4f} "
              f"pt dCDaR {grows[-1]['point_delta_CDaR']:+.1f}", flush=True)

ga = pd.DataFrame(grows)
ga["gate_role"] = np.where(ga["seq"] == 387, "CENTER_bootstrap_gate", "plateau_point_support")
ga["passes"] = np.where(
    ga["seq"] == 387,
    (ga["P_dSharpe_gt0"] >= 0.85) & (ga["P_dCDaR_gt0"] >= 0.85),
    (ga["point_delta_sharpe"] > 0) & (ga["point_delta_CDaR"] > 0))
ga.to_csv(f"{OUT}/gate_A.csv", index=False)
gateA_center = bool(ga[ga.seq == 387]["passes"].all())
gateA_plateau = bool(ga[ga.seq != 387]["passes"].all())
gateA_pass = gateA_center and gateA_plateau
print(f"\nGATE A center thr5 pass: {gateA_center} | plateau thr3/thr7 support: {gateA_plateau}", flush=True)

# ---------------- step 4: gate B — top-10-day retention (HARD, >= 0.90) ----------------
trows = []
for seq in (386, 387, 388):
    for inst in ("MNQ", "NQ"):
        ref = curves[(355, inst)]; ch = curves[(seq, inst)]
        top10 = ref.nlargest(10)
        ch_on = ch.loc[top10.index]
        own10 = ch.nlargest(10)
        for d in top10.index:
            trows.append({"seq": seq, "policy": names[seq], "instrument": inst,
                          "kind": "sm14_top_day", "date": d.date(),
                          "sm14_pnl": ref.loc[d], "cell_pnl": ch.loc[d]})
        trows.append({"seq": seq, "policy": names[seq], "instrument": inst,
                      "kind": "SUMMARY", "date": None,
                      "sm14_pnl": top10.sum(), "cell_pnl": ch_on.sum(),
                      "retention": ch_on.sum() / top10.sum(),
                      "own_top10_sum": own10.sum(),
                      "overlap_days": len(set(top10.index) & set(own10.index)),
                      "hard_gate_ge_0.90": (ch_on.sum() / top10.sum()) >= 0.90})
t10 = pd.DataFrame(trows)
t10.to_csv(f"{OUT}/gate_B_retention.csv", index=False)
summ = t10[t10.kind == "SUMMARY"]
print("\ntop-10 retention (HARD gate 0.90 on center 387):")
print(summ[["seq", "instrument", "retention", "hard_gate_ge_0.90",
            "overlap_days"]].to_string(index=False))
gateB_pass = bool(summ[summ.seq == 387]["hard_gate_ge_0.90"].all())
print(f"\nGATE B (center thr5) HARD pass: {gateB_pass}", flush=True)

json.dump({"sm14_reconcile_exact": sm14_exact, "all_four_cells_exact": all_exact,
           "gateA_center_pass": gateA_center, "gateA_plateau_pass": gateA_plateau,
           "gateA_pass": gateA_pass, "gateB_retention_pass": gateB_pass,
           "n_days": int(n), "k5": int(k5), "seed": SEED, "block": BLOCK, "n_boot": NBOOT,
           "retention_center": {r["instrument"]: r["retention"]
                                for _, r in summ[summ.seq == 387].iterrows()}},
          open(f"{OUT}/dev_gates_summary.json", "w"), indent=2)
print("\ndone dev gates")
