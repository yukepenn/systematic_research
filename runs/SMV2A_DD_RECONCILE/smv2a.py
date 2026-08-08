"""SMV2A DD-RECONCILE: all seven objects on one accounting basis.
Run from repo root: python runs/SMV2A_DD_RECONCILE/smv2a.py
"""
import sys, os, json
import numpy as np, pandas as pd

sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m, TICK, _fill

MNQ_COMM, MNQ_PV = 0.65, 2.0
NQ_COMM, NQ_PV = 2.18, 20.0
OUT = "runs/SMV2A_DD_RECONCILE/out"
os.makedirs(OUT, exist_ok=True)

def rha(x):  # round half away from zero
    return np.sign(x) * np.floor(np.abs(x) + 0.5)

# ---------- generic bar-level target executor (e10_sim semantics + bar equity + pos) ----------
def sim_bars(bars, tgt, comm_side, pv, onelot_mode=False, a=3, b=1):
    n = len(bars)
    o = bars["open"].to_numpy(); h = bars["high"].to_numpy()
    l = bars["low"].to_numpy(); c = bars["close"].to_numpy()
    last = bars["is_last_of_sess"].to_numpy()
    hm = bars["time"].dt.hour.to_numpy() * 100 + bars["time"].dt.minute.to_numpy()
    cash = 0.0; p = 0; pend = 0
    eq = np.empty(n); pos_out = np.empty(n, dtype=np.int64)
    fills = 0; contracts_traded = 0
    for t in range(n):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * pv
            cash -= abs(d) * comm_side
            p = pend
            fills += 1; contracts_traded += abs(d)
        if last[t] and p != 0:  # backstop flatten (early closes; normal days already flat if onelot)
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * pv
            cash -= abs(p) * comm_side
            fills += 1; contracts_traded += abs(p)
            p = 0; pend = 0
        else:
            if onelot_mode:
                M = tgt[t]
                tgt_new = p
                if hm[t] == 1639:
                    tgt_new = 0
                elif 1630 <= hm[t] < 1803:
                    tgt_new = 0 if p == 0 else (p if hm[t] < 1639 else 0)
                else:
                    if p == 0:
                        tgt_new = 1 if M >= a else (-1 if M <= -a else 0)
                    elif p == 1:
                        tgt_new = -1 if M <= -a else (0 if M <= b else 1)
                    else:
                        tgt_new = 1 if M >= a else (0 if M >= -b else -1)
                pend = tgt_new
            else:
                pend = int(tgt[t])
        eq[t] = cash + p * c[t] * pv
        pos_out[t] = p
    bar_pnl = np.diff(np.concatenate([[0.0], eq]))
    return eq, bar_pnl, pos_out, fills, contracts_traded

# ---------- DD battery ----------
def dd_battery(dates, net, bar_eq=None, label=""):
    dates = pd.to_datetime(pd.Series(dates)); net = np.asarray(net, dtype=float)
    eqd = np.cumsum(net); peak = np.maximum.accumulate(eqd); dd = peak - eqd
    res = {"label": label, "n_days": len(net), "net": net.sum(),
           "daily_vol": net.std(ddof=1), "ann_vol": net.std(ddof=1) * np.sqrt(252),
           "sharpe": net.mean() / net.std(ddof=1) * np.sqrt(252) if net.std(ddof=1) > 0 else np.nan,
           "maxDD_eod": dd.max()}
    dn = net[net < 0]
    res["sortino"] = net.mean() / dn.std(ddof=1) * np.sqrt(252) if len(dn) > 1 else np.nan
    ann_ret = net.mean() * 252
    res["calmar"] = ann_ret / dd.max() if dd.max() > 0 else np.nan
    if bar_eq is not None:
        pk = np.maximum.accumulate(bar_eq); res["maxDD_bar"] = (pk - bar_eq).max()
    ddpos = np.sort(dd[dd > 0])[::-1]
    res["CDaR5"] = ddpos[:max(1, int(0.05 * len(dd)))].mean() if len(ddpos) else 0.0
    res["avgDD"] = dd.mean()  # pain index
    res["ulcer"] = np.sqrt((dd ** 2).mean())
    uw = dd > 1e-9; tuw_max = 0; cur = 0; rec = []
    ep_start = None
    for i, u in enumerate(uw):
        if u: cur += 1; tuw_max = max(tuw_max, cur); ep_start = ep_start if ep_start is not None else i
        else:
            if ep_start is not None: rec.append(i - ep_start); ep_start = None
            cur = 0
    res["longest_TUW_days"] = tuw_max
    res["median_recovery"] = float(np.median(rec)) if rec else 0.0
    res["p95_recovery"] = float(np.percentile(rec, 95)) if rec else 0.0
    for w in (20, 40, 60, 120):
        res[f"worst_{w}D"] = pd.Series(net).rolling(w).sum().min() if len(net) >= w else np.nan
    s = pd.Series(net, index=dates)
    mo = s.resample("ME").sum(); qt = s.resample("QE").sum(); wk = s.resample("W").sum()
    res["worst_month"] = mo.min(); res["worst_quarter"] = qt.min()
    res["pos_day_pct"] = (net > 0).mean()
    res["pos_week_pct"] = (wk > 0).mean(); res["pos_month_pct"] = (mo > 0).mean()
    def max_streak(x):
        best = cur = 0
        for v in x:
            cur = cur + 1 if v < 0 else 0; best = max(best, cur)
        return best
    res["losing_month_streak"] = max_streak(mo.values); res["losing_week_streak"] = max_streak(wk.values)
    res["rolling60_min"] = pd.Series(net).rolling(60).sum().min() if len(net) >= 60 else np.nan
    return res

def exposure_stats(bars, pos_mnq_equiv, label=""):
    """pos in MNQ-contract equivalents (1 NQ = 10). Notional = |pos|*price*$2."""
    px = bars["close"].to_numpy(); ap = np.abs(pos_mnq_equiv)
    notional = ap * px * MNQ_PV
    return {"label": label, "avg_gross_mnq": ap.mean(), "median_gross_mnq": np.median(ap),
            "rms_mnq": np.sqrt((ap.astype(float) ** 2).mean()), "p95_mnq": np.percentile(ap, 95),
            "max_mnq": ap.max(), "time_in_mkt": (ap > 1e-9).mean(),
            "avg_notional_$": notional.mean(), "max_notional_$": notional.max()}

# ================= LOAD =================
print("loading bars/substrate ...")
bars = load_bars_3m()
n = len(bars); assert n == 540232, n
sess_dates = pd.to_datetime(bars["sess_date"])
DEV_END = pd.Timestamp("2026-05-31")
dev_bar = sess_dates <= DEV_END
bars_dev = bars[dev_bar].reset_index(drop=True)

bp = pd.read_parquet("runs/SM01_SUBSTRATE/out/e10_bar_pnl.parquet")
vs = pd.read_parquet("runs/SM01_SUBSTRATE/out/vote_state_3m.parquet")
M = np.load("runs/SM14_ONELOT_DAYMARGIN/out/M_target.npy")

e10d = pd.read_csv("runs/SM01_SUBSTRATE/out/e10_daily_py.csv", parse_dates=["sess"])
tiltd = pd.read_csv("runs/SM08_HTF_TILT/out/tilt50_rounded_daily.csv")
tiltd.columns = ["sess", "net"]; tiltd["sess"] = pd.to_datetime(tiltd["sess"])
p532 = pd.read_csv("runs/SM09_LEVERAGE_FRONTIER/out/port_532_daily.csv", parse_dates=["sess"])
pt532 = pd.read_csv("runs/SM09_LEVERAGE_FRONTIER/out/port_tilt_532_daily.csv", parse_dates=["sess"])
bmomd = pd.read_csv("research/scalping_lab/artifacts/w8_bmom/w8bmom_w14_daily.csv", parse_dates=["sess"])
b1n = pd.read_csv("research/scalping_lab/artifacts/w9_b1/w9b1_nightly.csv", parse_dates=["session_date", "exit_session_date"])

cal = pd.DatetimeIndex(sorted(sess_dates[dev_bar].unique()))
def on_cal(df, dcol, vcol):
    s = df.set_index(dcol)[vcol]
    s = s[~s.index.duplicated()]
    return s.reindex(cal).fillna(0.0)

A = on_cal(e10d[e10d.sess <= DEV_END], "sess", "net")             # Solar E10 native
B = on_cal(tiltd, "sess", "net")                                   # tilt-Solar (implementable form)
D = on_cal(p532, "sess", "net")
E = on_cal(pt532, "sess", "net")
BM = on_cal(bmomd[bmomd.sess <= DEV_END], "sess", "net_c1_usd")    # 1 NQ, C1 friction
b1dev = b1n[(b1n.exit_session_date >= cal[0]) & (b1n.exit_session_date <= DEV_END)]
B1 = on_cal(b1dev.groupby("exit_session_date")["net2.0_usd"].sum().reset_index(),
            "exit_session_date", "net2.0_usd")                     # 1 NQ, 2.0t friction, exit-session attribution

# verify port reconstruction
SC_B, SC_B1, SC_T, SC_P = 0.6588, 0.8270, 0.9904, 1.431
rec_E = SC_P * (0.5 * SC_T * B + 0.3 * SC_B * BM + 0.2 * SC_B1 * B1)
rec_D = SC_P * (0.5 * A + 0.3 * SC_B * BM + 0.2 * SC_B1 * B1)
print("RECON port_tilt_532: corr=%.6f  net_delta=%.0f  maxAbsDaily=%.0f" % (
    rec_E.corr(E), rec_E.sum() - E.sum(), (rec_E - E).abs().max()))
print("RECON port_532     : corr=%.6f  net_delta=%.0f  maxAbsDaily=%.0f" % (
    rec_D.corr(D), rec_D.sum() - D.sum(), (rec_D - D).abs().max()))

# ================= C: SOLAR+BMOM day-only (SM05 frozen expression) =================
C = SC_P * (0.5 * SC_T * B + 0.3 * SC_B * BM) / (0.8)  # renormalized 0.625/0.375, same vm scales
# NOTE: this is P1-form; exact SM05 cell used 50/50..80/20 grid — we take the 532-consistent renorm.

# ================= OneLot replays =================
print("replaying OneLot a=3,b=1 ...")
Mdev = M[dev_bar.to_numpy()]
eqF, barF, posF, fillsF, ctF = sim_bars(bars_dev, Mdev, MNQ_COMM, MNQ_PV, onelot_mode=True, a=3, b=1)
eqG, barG, posG, fillsG, ctG = sim_bars(bars_dev, Mdev, NQ_COMM, NQ_PV, onelot_mode=True, a=3, b=1)
sdd = bars_dev["sess_date"].to_numpy()
F = pd.Series(barF).groupby(sdd).sum(); F.index = pd.to_datetime(F.index); F = F.reindex(cal).fillna(0)
G = pd.Series(barG).groupby(sdd).sum(); G.index = pd.to_datetime(G.index); G = G.reindex(cal).fillna(0)
print("OneLot MNQ: net=%.0f fills=%d | SM14 said net 27287, trades 4039" % (F.sum(), fillsF))
print("OneLot NQ : net=%.0f | SM14 said 298040" % G.sum())

# ================= bar-level curves =================
bp_dev = bp[dev_bar.to_numpy()]
barA = bp_dev["delta"].to_numpy(); eqA = np.cumsum(barA)
posA = bp_dev["pos"].to_numpy()

# tilt bar-level: rebuild T' and replay
print("rebuilding tilt bar-level ...")
tgtA = bp["tgt"].to_numpy()
sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
sma50 = sclose.rolling(50).mean()
state = np.sign(sclose - sma50)                 # state of session s (its own close vs its SMA50)
state_prior = state.shift(1)                    # applied to next session
st_map = state_prior.to_dict()
st_bar = np.array([st_map.get(d, np.nan) for d in bars["sess_date"]])
agree = (np.sign(tgtA) != 0) & (st_bar == np.sign(tgtA))
mfac = np.where(agree, 1.25, 1.0)
Tp = np.clip(rha(tgtA * mfac * 0.9026), -13, 13)
eqB, barB, posB, fillsB, ctB = sim_bars(bars_dev, Tp[dev_bar.to_numpy()], MNQ_COMM, MNQ_PV)
Bchk = pd.Series(barB).groupby(sdd).sum(); Bchk.index = pd.to_datetime(Bchk.index); Bchk = Bchk.reindex(cal).fillna(0)
print("TILT rebuild: corr=%.6f net=%.0f vs stored %.0f  maxAbsDaily=%.0f" % (
    Bchk.corr(B), Bchk.sum(), B.sum(), (Bchk - B).abs().max()))

# BMOM bar-level (positions on RTH 3m bars)
print("rebuilding BMOM bar-level ...")
from sm_bmom import bmom_trades
bt = bmom_trades(bars_dev)
hm_all = bars_dev["time"].dt.hour.to_numpy() * 100 + bars_dev["time"].dt.minute.to_numpy()
key = pd.Series(np.arange(len(bars_dev)),
                index=pd.MultiIndex.from_arrays([pd.to_datetime(bars_dev["sess_date"]), hm_all]))
key = key[~key.index.duplicated()]
cl = bars_dev["close"].to_numpy()
posBM = np.zeros(len(bars_dev))
cost_per_rt = 2.872 * 5.0
cost_arr = np.zeros(len(bars_dev))
skipped = 0
for _, tr in bt.iterrows():
    k0 = (pd.Timestamp(tr["sess"]), int(tr["entry_hm"])); k1 = (pd.Timestamp(tr["sess"]), int(tr["exit_hm"]))
    if k0 not in key.index or k1 not in key.index:
        skipped += 1; continue
    i0, i1 = int(key[k0]), int(key[k1])
    sd_ = 1 if tr["side"] == "L" else -1
    posBM[i0 + 1:i1 + 1] += sd_
    cost_arr[i0] += cost_per_rt
print("bmom trades mapped:", len(bt) - skipped, "skipped:", skipped)
mtmBM = np.concatenate([[0.0], np.diff(cl)]) * posBM * NQ_PV - cost_arr
BMchk = pd.Series(mtmBM).groupby(sdd).sum(); BMchk.index = pd.to_datetime(BMchk.index); BMchk = BMchk.reindex(cal).fillna(0)
print("BMOM rebuild: corr=%.6f net=%.0f vs stored %.0f" % (BMchk.corr(BM), BMchk.sum(), BM.sum()))

# B1 bar-level: nightly steps at exit bars (disclosed approximation for intraday DD)
b1_step = np.zeros(len(bars_dev))
exit_by_sess = b1dev.groupby("exit_session_date")["net2.0_usd"].sum().to_dict()
last_idx = bars_dev.index[bars_dev["is_last_of_sess"]].to_numpy()
sess_of_last = bars_dev.loc[bars_dev["is_last_of_sess"], "sess_date"].to_numpy()
for i, d in zip(last_idx, sess_of_last):
    v = exit_by_sess.get(pd.Timestamp(d), 0.0)
    if v: b1_step[i] += v

# portfolio bar curves
barE = SC_P * (0.5 * SC_T * barB + 0.3 * SC_B * mtmBM + 0.2 * SC_B1 * b1_step)
barD = SC_P * (0.5 * barA + 0.3 * SC_B * mtmBM + 0.2 * SC_B1 * b1_step)
barC = SC_P * (0.5 * SC_T * barB + 0.3 * SC_B * mtmBM) / 0.8

# ================= batteries =================
print("computing batteries ...")
objs = {
    "A_SOLAR_E10": (A, np.cumsum(barA)),
    "B_TILT_SOLAR": (B, np.cumsum(barB)),
    "C_SOLAR_BMOM_dayonly": (C, np.cumsum(barC)),
    "D_PORT_532": (D, np.cumsum(barD)),
    "E_PORT_TILT_532": (E, np.cumsum(barE)),
    "F_ONELOT_MNQ": (F, eqF),
    "G_ONELOT_NQ": (G, eqG),
}
rows = [dd_battery(cal, s.values, bar_eq=be, label=k) for k, (s, be) in objs.items()]
bat = pd.DataFrame(rows).set_index("label")
bat.to_csv(f"{OUT}/dd_battery.csv")
print(bat[["net", "ann_vol", "sharpe", "maxDD_eod", "maxDD_bar", "calmar", "worst_month", "longest_TUW_days", "pos_month_pct"]].round(1).to_string())

# exposures (MNQ-equiv)
pos_map = {
    "A_SOLAR_E10": posA,
    "B_TILT_SOLAR": posB,
    "C_SOLAR_BMOM_dayonly": SC_P / 0.8 * (0.5 * SC_T * posB + 0.3 * SC_B * 10 * posBM),
    "D_PORT_532": SC_P * (0.5 * posA + 0.3 * SC_B * 10 * posBM),   # + B1 overnight leg, added below
    "E_PORT_TILT_532": SC_P * (0.5 * SC_T * posB + 0.3 * SC_B * 10 * posBM),
    "F_ONELOT_MNQ": posF,
    "G_ONELOT_NQ": 10 * posG,
}
# B1 overnight exposure: 1 NQ held ~16:15->09:30 next day; mark bars in that window
b1_pos = np.zeros(len(bars_dev))
hm_dev = bars_dev["time"].dt.hour.to_numpy() * 100 + bars_dev["time"].dt.minute.to_numpy()
overnight = (hm_dev >= 1618) | (hm_dev <= 930)
b1_pos[overnight] = 1.0
for k in ("D_PORT_532", "E_PORT_TILT_532"):
    pos_map[k] = np.abs(pos_map[k]) + SC_P * 0.2 * SC_B1 * 10 * b1_pos
exp_rows = [exposure_stats(bars_dev, np.abs(np.asarray(p, dtype=float)), label=k) for k, p in pos_map.items()]
expdf = pd.DataFrame(exp_rows).set_index("label")
expdf.to_csv(f"{OUT}/exposure_stats.csv")
print(expdf.round(2).to_string())

# ================= normalizations =================
tv = bat.loc["A_SOLAR_E10", "daily_vol"]
norm_rows = []
for k, (s, be) in objs.items():
    sv = s.values.std(ddof=1)
    for mode, scale in [("native", 1.0),
                        ("equal_vol", tv / sv if sv > 0 else np.nan),
                        ("equal_avg_exposure", expdf.loc["A_SOLAR_E10", "avg_gross_mnq"] / max(expdf.loc[k, "avg_gross_mnq"], 1e-9)),
                        ("equal_maxdd", bat.loc["A_SOLAR_E10", "maxDD_eod"] / bat.loc[k, "maxDD_eod"])]:
        x = s.values * scale
        eq = np.cumsum(x); ddm = (np.maximum.accumulate(eq) - eq).max()
        norm_rows.append({"label": k, "mode": mode, "scale": scale, "net": x.sum(),
                          "ann_vol": x.std(ddof=1) * np.sqrt(252), "maxDD": ddm,
                          "sharpe": bat.loc[k, "sharpe"]})
ndf = pd.DataFrame(norm_rows)
ndf.to_csv(f"{OUT}/normalized_comparison.csv", index=False)
print(ndf.pivot_table(index="label", columns="mode", values="maxDD").round(0).to_string())

# ================= decomposition ladder =================
print("decomposition ladder ...")
sgn10 = np.sign(tgtA[dev_bar.to_numpy()]) * 10
eqS, barS, posS, _, _ = sim_bars(bars_dev, sgn10, MNQ_COMM, MNQ_PV)
S10 = pd.Series(barS).groupby(sdd).sum(); S10.index = pd.to_datetime(S10.index); S10 = S10.reindex(cal).fillna(0)
PT_noB1 = SC_P * (0.5 * SC_T * B + 0.3 * SC_B * BM)
lad = []
def dd_of(s):
    eq = np.cumsum(np.asarray(s, dtype=float)); return (np.maximum.accumulate(eq) - eq).max()
for name, s in [("L0_PORT_TILT_532", E), ("L1_drop_B1(day-only, no renorm)", PT_noB1),
                ("L2_full-size tilt-Solar (x1 not x0.7086)", B),
                ("L2b_full-size UNtilted Solar (A)", A),
                ("L3_sign(T)x10 no grading", S10),
                ("L4_OneLot_MNQ x10 (pure scale)", F * 10),
                ("L5_OneLot_NQ native", G)]:
    x = np.asarray(s, dtype=float)
    lad.append({"step": name, "net": x.sum(), "ann_vol": x.std(ddof=1) * np.sqrt(252),
                "maxDD_eod": dd_of(x), "sharpe": x.mean() / x.std(ddof=1) * np.sqrt(252)})
laddf = pd.DataFrame(lad); laddf.to_csv(f"{OUT}/decomposition_ladder.csv", index=False)
print(laddf.round(1).to_string())

# friction split OneLot MNQx10 vs NQ
fr = {"onelot_fills": fillsF, "contracts_MNQ": ctF, "comm_MNQ_x10": ctF * MNQ_COMM * 2 * 10 / 2,  # per-side comm already; x10 scale
      "comm_NQ": ctG * NQ_COMM, "slip_same": "1 tick == $5 per 10-MNQ-equiv on both"}
json.dump({k: (float(v) if isinstance(v, (int, float, np.floating, np.integer)) else v) for k, v in fr.items()},
          open(f"{OUT}/friction_split.json", "w"), indent=1)

# save curves
pd.DataFrame({"sess": cal, "A": A.values, "B": B.values, "C": C.values, "D": D.values,
              "E": E.values, "F": F.values, "G": G.values, "S10": S10.values,
              "PT_noB1": PT_noB1.values, "BM": BM.values, "B1": B1.values}).to_csv(f"{OUT}/daily_curves.csv", index=False)
np.save(f"{OUT}/pos_onelot.npy", posF)
print("done.")
