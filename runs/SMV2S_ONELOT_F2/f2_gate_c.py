"""SMV2S_ONELOT_F2 — Gate C: old-regime (2006-2021) non-inferiority stress.

Spec: runs/SMV2S_ONELOT_F2/spec.yaml (frozen). Solar-only mode (B-MOM silent), so the
HTF-GATED DOMINANT policy degenerates to HTF-gated Solar:
    pos = sign(T_dd) iff |T_dd| >= thr AND HTF_state == sign(T_dd), else 0.
Reference: SM14 = hysteresis(a=3,b=1) on M = 0.7086*T_tilt with B = 0.

Replay conventions IDENTICAL to runs/SMV2H2_ONELOT_CONFIRM/confirm_gate_b.py
(committed): decisions at 3m close; fills at NEXT 3m close +-1 tick slip, uncapped
(hist substrate has NO OHLC — DISCLOSED approximation, applied identically to both
policies); session-close flatten at last-bar close -+1 tick; dev ops windows verbatim
(flatten decided 16:39, freeze 16:30-18:03); NQ basis $2.18/side, point value $20.

Step 1 (dev verification, required before history): rebuild T-dd from vote_pend on
runs/SM01_SUBSTRATE/out/vote_state_3m.parquet and require EXACT equality with the
T-dd series the dev gates derived from e10_bar_pnl.parquet tgt
(out/tdd_dev_from_tgt.npy) on every dev bar.

Gate (preregistered, evaluated on the CENTER cell thr=5; thr 3/7 informational):
    net >= net(SM14) - $10,000  AND  maxDD <= 1.25 x maxDD(SM14)
    AND trades/yr <= 1.5 x SM14 (entries/yr and fills/yr both, as SMV2H2 gate B).

Run from repo root: python runs/SMV2S_ONELOT_F2/f2_gate_c.py
"""
import os, json
import numpy as np, pandas as pd

RUN = "runs/SMV2S_ONELOT_F2"
OUT = f"{RUN}/out"; os.makedirs(OUT, exist_ok=True)
TICK = 0.25; COMM = 2.18; PV = 20.0
DEV_END = pd.Timestamp("2026-05-31")

def rha(x): return np.sign(x) * np.floor(np.abs(x) + 0.5)

def build_states(df):
    """vote_pend -> (T, st_bar, Tpp [T-dd DUAL_HTF], Tp_old [SM14 tilt-only]).
    Construction verbatim from runs/SMV2H_ONECONTRACT/smv2h.py /
    runs/SMV2H2_ONELOT_CONFIRM/confirm_gate_b.py."""
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
tdd_ref = np.load(f"{OUT}/tdd_dev_from_tgt.npy")      # dev gates' T-dd (from e10 tgt)
tdd_match = int((Tpp_dev == tdd_ref).sum())
ver = {
    "n_dev_bars": len(vd),
    "tgt_eq_clip_rha_10votepend_over13": tgt_match, "tgt_mismatch": len(vd) - tgt_match,
    "tdd_from_vote_eq_tdd_from_tgt": tdd_match, "tdd_mismatch": len(vd) - tdd_match,
}
print(ver, flush=True)
json.dump(ver, open(f"{OUT}/vote_tdd_verify.json", "w"), indent=2)
assert ver["tgt_mismatch"] == 0 and ver["tdd_mismatch"] == 0, "dev vote->T-dd verification FAILED"

# ---------------- step 2: history replay ----------------
print("history states ...", flush=True)
hd = pd.read_parquet("runs/SM06_SOLAR_HISTORY/out/vote_state_3m_hist.parquet")
assert str(hd["sess_date"].max()) <= "2021-12-31"
T_h, st_h, Tpp_h, Tp_old_h = build_states(hd)

def des_htfg(Tpp, st, thr):
    """HTF-gated Solar (B silent): sign(T_dd) iff |T_dd| >= thr AND HTF == sign(T_dd)."""
    ok = (np.abs(Tpp) >= thr) & (st == np.sign(Tpp))
    return np.where(ok, np.sign(Tpp), 0).astype(np.int64)

policies = {
    "HTFG_s3": des_htfg(Tpp_h, st_h, 3),
    "HTFG_s5": des_htfg(Tpp_h, st_h, 5),     # CENTER (gate cell)
    "HTFG_s7": des_htfg(Tpp_h, st_h, 7),
    "SM14":    pol_hyst(0.7086 * Tp_old_h, 3, 1),
}

def run_policy_hist(df, desired, comm, pv):
    """smv2h.py run_policy adapted to a close-only substrate (verbatim from
    confirm_gate_b.py): pending change decided at bar t-1 close fills at bar t
    CLOSE +-1 tick (uncapped); session-close flatten at last-bar close;
    identical ops windows."""
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
for name, des in policies.items():
    dl, fills, entries = run_policy_hist(hd, des, COMM, PV)
    res[name] = (dl, fills, entries)
    print(f"{name:9s} net {dl.sum():12.1f}  fills {fills}  entries {entries}", flush=True)

dl_s = res["SM14"][0]
for name in ("HTFG_s3", "HTFG_s5", "HTFG_s7"):
    assert (res[name][0].index == dl_s.index).all()
pd.DataFrame({name: r[0] for name, r in res.items()}).to_csv(f"{OUT}/gate_C_daily_curves.csv")

def battery(dl):
    net = dl.values; eqd = np.cumsum(net); pk = np.maximum.accumulate(eqd); dd = pk - eqd
    k = max(1, int(0.05 * len(net)))
    sd_ = net.std(ddof=1)
    return {"n_days": len(net), "net": net.sum(),
            "sharpe": net.mean() / sd_ * np.sqrt(252) if sd_ > 0 else np.nan,
            "maxDD_eod": dd.max(), "CDaR5": np.sort(dd)[::-1][:k].mean()}

yrs_span = (dl_s.index.max() - dl_s.index.min()).days / 365.25
bat = {name: battery(r[0]) for name, r in res.items()}
bs = bat["SM14"]; f_s, e_s = res["SM14"][1], res["SM14"][2]

rows = []
for name in ("HTFG_s3", "HTFG_s5", "HTFG_s7", "SM14"):
    b = bat[name]; _, fills, entries = res[name]
    row = b | {"policy": name, "fills": fills, "entries": entries,
               "fills_per_yr": fills / yrs_span, "entries_per_yr": entries / yrs_span,
               "years_span": yrs_span, "gate_role": ("CENTER_gate" if name == "HTFG_s5" else
                                                     "reference" if name == "SM14" else "info")}
    if name != "SM14":
        row["c1_net_noninferior"] = b["net"] >= bs["net"] - 10000.0
        row["c2_maxDD_le_1.25x"] = b["maxDD_eod"] <= 1.25 * bs["maxDD_eod"]
        row["c3_entriesyr_le_1.5x"] = (entries / yrs_span) <= 1.5 * (e_s / yrs_span)
        row["c3_fillsyr_le_1.5x"] = (fills / yrs_span) <= 1.5 * (f_s / yrs_span)
        row["all_criteria"] = bool(row["c1_net_noninferior"] and row["c2_maxDD_le_1.25x"]
                                   and row["c3_entriesyr_le_1.5x"] and row["c3_fillsyr_le_1.5x"])
    rows.append(row)
gc = pd.DataFrame(rows).set_index("policy")
gateC_pass = bool(gc.loc["HTFG_s5", "all_criteria"])
gc["gateC_pass_center"] = [gateC_pass if n_ == "HTFG_s5" else "" for n_ in gc.index]
gc.to_csv(f"{OUT}/gate_C_oldregime.csv")

# yearly nets + kill screen
yearly = pd.DataFrame({name: r[0].groupby(r[0].index.year).sum() for name, r in res.items()})
yearly["d_net_s5_vs_SM14"] = yearly["HTFG_s5"] - yearly["SM14"]
yearly.to_csv(f"{OUT}/gate_C_yearly.csv")
kill = {name: {int(k): float(v) for k, v in yearly[name][yearly[name] < -25000].items()}
        for name in policies}

b5 = bat["HTFG_s5"]; f_5, e_5 = res["HTFG_s5"][1], res["HTFG_s5"][2]
summary = {
    "net_center_s5": b5["net"], "net_SM14": bs["net"], "net_gap": b5["net"] - bs["net"],
    "maxDD_center_s5": b5["maxDD_eod"], "maxDD_SM14": bs["maxDD_eod"],
    "maxDD_ratio": b5["maxDD_eod"] / bs["maxDD_eod"],
    "sharpe_center_s5": b5["sharpe"], "sharpe_SM14": bs["sharpe"],
    "entries_per_yr_center": e_5 / yrs_span, "entries_per_yr_SM14": e_s / yrs_span,
    "fills_per_yr_center": f_5 / yrs_span, "fills_per_yr_SM14": f_s / yrs_span,
    "c1_net": bool(gc.loc["HTFG_s5", "c1_net_noninferior"]),
    "c2_dd": bool(gc.loc["HTFG_s5", "c2_maxDD_le_1.25x"]),
    "c3_entries": bool(gc.loc["HTFG_s5", "c3_entriesyr_le_1.5x"]),
    "c3_fills": bool(gc.loc["HTFG_s5", "c3_fillsyr_le_1.5x"]),
    "gateC_pass": gateC_pass,
    "kill_years_below_-25k": kill,
    "worst_year_center_s5": {"year": int(yearly["HTFG_s5"].idxmin()),
                             "net": float(yearly["HTFG_s5"].min())},
    "worst_year_SM14": {"year": int(yearly["SM14"].idxmin()),
                        "net": float(yearly["SM14"].min())},
    "net_s3": bat["HTFG_s3"]["net"], "net_s7": bat["HTFG_s7"]["net"],
}
json.dump(summary, open(f"{OUT}/gate_C_summary.json", "w"), indent=2)
print(json.dumps(summary, indent=2))
print("\nyearly:")
print(yearly.round(0).to_string())
print("\nGATE C PASS (center thr5):", gateC_pass)
print("done gate C")
