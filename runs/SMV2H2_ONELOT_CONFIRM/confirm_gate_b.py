"""SMV2H2_ONELOT_CONFIRM — Gate B: old-regime (2006-2021) non-inferiority stress.

Spec: runs/SMV2H2_ONELOT_CONFIRM/spec.yaml (frozen). Solar-only mode (B-MOM silent).

Step 1 (dev verification, required before history): rebuild T-dd (DUAL_HTF) from
vote_pend on runs/SM01_SUBSTRATE/out/vote_state_3m.parquet via
T = clip(rha(10*vote_pend/13), +-10) and the exact smv2h.py HTF/tilt/halving
pipeline; require EXACT equality with the T-dd series gate A derived from
e10_bar_pnl.parquet tgt on every dev bar (out/tdd_dev_from_tgt.npy).

Step 2 (history): replay A_dom_s7 (pos = sign(T_dd) iff |T_dd|>=7) and SM14
(hysteresis a=3,b=1 on M = 0.7086*T_tilt, B=0) on
runs/SM06_SOLAR_HISTORY/out/vote_state_3m_hist.parquet. No OHLC on the hist
substrate: decisions at 3m close, fills at NEXT 3m close +-1 tick slip
(uncapped; DISCLOSED approximation, identical for both policies); session-close
flatten at last-bar close -+1 tick; dev ops windows kept verbatim (flatten
decided 16:39, freeze 16:30-18:03); NQ costs $2.18/side, point value $20.

Run from repo root: python runs/SMV2H2_ONELOT_CONFIRM/confirm_gate_b.py
"""
import os, json
import numpy as np, pandas as pd

RUN = "runs/SMV2H2_ONELOT_CONFIRM"
OUT = f"{RUN}/out"; os.makedirs(OUT, exist_ok=True)
TICK = 0.25; COMM = 2.18; PV = 20.0
DEV_END = pd.Timestamp("2026-05-31")

def rha(x): return np.sign(x) * np.floor(np.abs(x) + 0.5)

def build_states(df):
    """vote_pend -> (T, st_bar, Tpp [T-dd DUAL_HTF], Tp_old [SM14 tilt-only]).
    Construction verbatim from runs/SMV2H_ONECONTRACT/smv2h.py."""
    T = np.clip(rha(10.0 * df["vote_pend"].to_numpy() / 13.0), -10, 10)
    sclose = df.loc[df["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
    htf = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
    st_bar = np.array([htf.get(d, np.nan) for d in df["sess_date"]])
    agree = (np.sign(T) != 0) & (st_bar == np.sign(T))
    m = np.where(agree, 1.25, 1.0)
    s = np.where((T < 0) & (st_bar > 0), 0.5, 1.0)
    Tpp = np.clip(rha(T * m * s * 0.9026), -13, 13)
    Tp_old = np.clip(rha(T * m * 0.9026), -13, 13)
    return T, st_bar, Tpp, Tp_old

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

# ---------------- step 1: dev verification of the vote -> T-dd construction ----------------
print("dev verification ...", flush=True)
vd = pd.read_parquet("runs/SM01_SUBSTRATE/out/vote_state_3m.parquet")
devmask = (pd.to_datetime(vd["sess_date"]) <= DEV_END).to_numpy()
vd = vd.loc[devmask].reset_index(drop=True)          # dev prefix only; June/July 2026 excluded
bp = pd.read_parquet("runs/SM01_SUBSTRATE/out/e10_bar_pnl.parquet").loc[devmask].reset_index(drop=True)

T_dev, st_dev, Tpp_dev, _ = build_states(vd)
tgt_match = int((T_dev == bp["tgt"].to_numpy()).sum())
tdd_ref = np.load(f"{OUT}/tdd_dev_from_tgt.npy")      # gate A's T-dd (from e10 tgt)
tdd_match = int((Tpp_dev == tdd_ref).sum())
ver = {
    "n_dev_bars": len(vd),
    "tgt_eq_clip_rha_10votepend_over13": tgt_match, "tgt_mismatch": len(vd) - tgt_match,
    "tdd_from_vote_eq_tdd_from_tgt": tdd_match, "tdd_mismatch": len(vd) - tdd_match,
}
print(ver, flush=True)
assert ver["tgt_mismatch"] == 0 and ver["tdd_mismatch"] == 0, "dev vote->T-dd verification FAILED"

# sample sessions (evidence)
samp_rows = []
for sdate in ["2022-06-13", "2024-08-05", "2026-03-06"]:
    mm = vd["sess_date"].astype(str) == sdate
    ii = np.where(mm.to_numpy())[0]
    step = max(1, len(ii) // 8)
    for i in ii[::step]:
        samp_rows.append({"time": vd["time"].iloc[i], "sess_date": sdate,
                          "vote_pend": int(vd["vote_pend"].iloc[i]), "tgt_sm01": int(bp["tgt"].iloc[i]),
                          "T_from_vote": int(T_dev[i]), "htf": st_dev[i],
                          "Tdd_from_vote": int(Tpp_dev[i]), "Tdd_gateA": int(tdd_ref[i])})
pd.DataFrame(samp_rows).to_csv(f"{OUT}/vote_tdd_verify_samples.csv", index=False)
json.dump(ver, open(f"{OUT}/vote_tdd_verify.json", "w"), indent=2)

# ---------------- step 2: history replay ----------------
print("history states ...", flush=True)
hd = pd.read_parquet("runs/SM06_SOLAR_HISTORY/out/vote_state_3m_hist.parquet")
assert str(hd["sess_date"].max()) <= "2021-12-31"
T_h, st_h, Tpp_h, Tp_old_h = build_states(hd)

des_a7 = np.where(np.abs(Tpp_h) >= 7, np.sign(Tpp_h), 0).astype(np.int64)   # B silent
M_h = 0.7086 * Tp_old_h                                                     # B = 0
des_sm = pol_hyst(M_h, 3, 1)

def run_policy_hist(df, desired, comm, pv):
    """smv2h.py run_policy adapted to a close-only substrate: pending change
    decided at bar t-1 close fills at bar t CLOSE +-1 tick (uncapped);
    session-close flatten at last-bar close; identical ops windows."""
    n = len(df)
    c = df["close"].to_numpy(); last = df["is_last_of_sess"].to_numpy()
    tm = pd.to_datetime(df["time"])
    hm = tm.dt.hour.to_numpy() * 100 + tm.dt.minute.to_numpy()
    sd = df["sess_date"].to_numpy()
    cash = 0.0; p = 0; pend = 0; daily = {}; prev = 0.0
    fills = 0; entries = 0
    for t in range(n):
        if pend != p:
            d = pend - p; side = 1 if d > 0 else -1
            px = c[t] + side * TICK
            cash -= d * px * pv; cash -= abs(d) * comm
            if pend != 0:
                entries += 1
            p = pend; fills += 1
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = c[t] + side * TICK
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
        if last[t]:
            eqv = cash + p * c[t] * pv
            daily[sd[t]] = eqv - prev; prev = eqv
    dl = pd.Series(daily); dl.index = pd.to_datetime(dl.index)
    return dl, fills, entries

print("history replay ...", flush=True)
res = {}
for name, des in [("A_dom_s7", des_a7), ("SM14", des_sm)]:
    dl, fills, entries = run_policy_hist(hd, des, COMM, PV)
    res[name] = (dl, fills, entries)
    print(f"{name:9s} net {dl.sum():12.1f}  fills {fills}  entries {entries}", flush=True)

dl_a, f_a, e_a = res["A_dom_s7"]; dl_s, f_s, e_s = res["SM14"]
assert (dl_a.index == dl_s.index).all()
pd.DataFrame({"A_dom_s7": dl_a, "SM14": dl_s}).to_csv(f"{OUT}/gate_B_daily_curves.csv")

def battery(dl):
    net = dl.values; eqd = np.cumsum(net); pk = np.maximum.accumulate(eqd); dd = pk - eqd
    k = max(1, int(0.05 * len(net)))
    sd_ = net.std(ddof=1)
    return {"n_days": len(net), "net": net.sum(),
            "sharpe": net.mean() / sd_ * np.sqrt(252) if sd_ > 0 else np.nan,
            "maxDD_eod": dd.max(), "CDaR5": np.sort(dd)[::-1][:k].mean()}

yrs_span = (dl_a.index.max() - dl_a.index.min()).days / 365.25
ba, bs = battery(dl_a), battery(dl_s)
rows = []
for name, b, fills, entries in [("A_dom_s7", ba, f_a, e_a), ("SM14", bs, f_s, e_s)]:
    rows.append(b | {"policy": name, "fills": fills, "entries": entries,
                     "fills_per_yr": fills / yrs_span, "entries_per_yr": entries / yrs_span,
                     "years_span": yrs_span})
gb = pd.DataFrame(rows).set_index("policy")

# yearly nets + kill screen
ya = dl_a.groupby(dl_a.index.year).sum(); ys = dl_s.groupby(dl_s.index.year).sum()
yearly = pd.DataFrame({"A_dom_s7": ya, "SM14": ys})
yearly["d_net"] = yearly["A_dom_s7"] - yearly["SM14"]
yearly.to_csv(f"{OUT}/gate_B_yearly.csv")
kill_a = yearly[yearly["A_dom_s7"] < -25000]
kill_s = yearly[yearly["SM14"] < -25000]

# gate checks (spec, mechanical)
c1 = ba["net"] >= bs["net"] - 10000.0
c2 = ba["maxDD_eod"] <= 1.25 * bs["maxDD_eod"]
c3_entries = (e_a / yrs_span) <= 1.5 * (e_s / yrs_span)
c3_fills = (f_a / yrs_span) <= 1.5 * (f_s / yrs_span)
gateB_pass = bool(c1 and c2 and c3_entries and c3_fills)

gb["gate_c1_net_noninferior"] = [c1, ""]
gb["gate_c2_maxDD_le_1.25x"] = [c2, ""]
gb["gate_c3_tradesyr_le_1.5x_entries"] = [c3_entries, ""]
gb["gate_c3_tradesyr_le_1.5x_fills"] = [c3_fills, ""]
gb["gateB_pass"] = [gateB_pass, ""]
gb.to_csv(f"{OUT}/gate_B_oldregime.csv")

summary = {
    "net_A": ba["net"], "net_SM14": bs["net"], "net_gap": ba["net"] - bs["net"],
    "maxDD_A": ba["maxDD_eod"], "maxDD_SM14": bs["maxDD_eod"],
    "maxDD_ratio": ba["maxDD_eod"] / bs["maxDD_eod"],
    "sharpe_A": ba["sharpe"], "sharpe_SM14": bs["sharpe"],
    "entries_per_yr_A": e_a / yrs_span, "entries_per_yr_SM14": e_s / yrs_span,
    "fills_per_yr_A": f_a / yrs_span, "fills_per_yr_SM14": f_s / yrs_span,
    "c1_net": bool(c1), "c2_dd": bool(c2),
    "c3_entries": bool(c3_entries), "c3_fills": bool(c3_fills),
    "gateB_pass": gateB_pass,
    "kill_years_A_below_-25k": {int(k): float(v) for k, v in kill_a["A_dom_s7"].items()},
    "kill_years_SM14_below_-25k": {int(k): float(v) for k, v in kill_s["SM14"].items()},
    "worst_year_A": {"year": int(ya.idxmin()), "net": float(ya.min())},
    "worst_year_SM14": {"year": int(ys.idxmin()), "net": float(ys.min())},
}
json.dump(summary, open(f"{OUT}/gate_B_summary.json", "w"), indent=2)
print(json.dumps(summary, indent=2))
print("\nyearly:")
print(yearly.round(0).to_string())
print("\nGATE B PASS:", gateB_pass)
print("done gate B")
