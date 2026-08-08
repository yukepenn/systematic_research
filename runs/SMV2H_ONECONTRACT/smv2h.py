"""SMV2H — one-contract policy search on DUAL_HTF state (seq 347-357) + SM14 DD autopsy."""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m, _fill
from sm_bmom import rth_3m, BAND_DAYS
from smv2_common import dd_battery, boot_ci_mean

OUT = "runs/SMV2H_ONECONTRACT/out"; os.makedirs(OUT, exist_ok=True)
MNQ = (0.65, 2.0); NQ = (2.18, 20.0)

def rha(x): return np.sign(x) * np.floor(np.abs(x) + 0.5)

# ---------------- substrate ----------------
print("substrate ...")
bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"]); dev = sess <= pd.Timestamp("2026-05-31")
bars_dev = bars[dev].reset_index(drop=True)
bp = pd.read_parquet("runs/SM01_SUBSTRATE/out/e10_bar_pnl.parquet")
T = bp["tgt"].to_numpy().astype(float)

sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
htf = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
st_bar = np.array([htf.get(d, np.nan) for d in bars["sess_date"]])

agree = (np.sign(T) != 0) & (st_bar == np.sign(T))
m = np.where(agree, 1.25, 1.0)
s = np.where((T < 0) & (st_bar > 0), 0.5, 1.0)
Tpp = np.clip(rha(T * m * s * 0.9026), -13, 13)          # DUAL_HTF target
Tp_old = np.clip(rha(T * m * 0.9026), -13, 13)           # SM14 (no DUAL)

# B-MOM pending position per bar (frozen signal state machine)
print("bmom state ...")
def bmom_pos_series(bars3):
    r = rth_3m(bars3)
    pos_arr = np.zeros(len(bars3))
    hist, day_count = {}, 0
    idx_by_pos = r.index.to_numpy()
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
Mp = 0.7086 * Tpp + 2.83 * B
Mp_old = 0.7086 * Tp_old + 2.83 * B
devnp = dev.to_numpy()

# ---------------- one-lot executor over a desired-position function ----------------
def run_policy(bars, desired, comm, pv):
    """desired[t] in {-1,0,1}: the position wanted as of bar t close (before ops constraints)."""
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
                pend = want if (want == 0 or want == p or True) else p
                # entries/flips/exits all allowed outside the ops window
                pend = want
        eq[t] = cash + p * c[t] * pv
        if last[t]:
            eqv = cash + p * c[t] * pv
            daily[sd[t]] = eqv - prev; prev = eqv
    dl = pd.Series(daily); dl.index = pd.to_datetime(dl.index)
    return dl, fills, eq

# ---------------- desired-position generators (stateful maps run on full series) ----------------
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

def pol_sign_db(M, enter, exit_at=0.0):
    n = len(M); out = np.zeros(n, dtype=np.int64); p = 0
    for t in range(n):
        Mt = M[t]
        if p == 0:
            p = 1 if Mt >= enter else (-1 if Mt <= -enter else 0)
        elif p == 1:
            p = -1 if Mt <= -enter else (0 if Mt <= exit_at else 1)
        else:
            p = 1 if Mt >= enter else (0 if Mt >= -exit_at else -1)
        out[t] = p
    return out

def pol_dominant(Tpp, B, solar_min):
    return np.where(B != 0, np.sign(B),
                    np.where(np.abs(Tpp) >= solar_min, np.sign(Tpp), 0)).astype(np.int64)

def pol_conflict_flat(Tpp, B, solar_min):
    base = pol_dominant(Tpp, B, solar_min)
    conflict = (np.sign(Tpp) * B) < 0
    return np.where(conflict, 0, base).astype(np.int64)

def pol_router(Mp, Tpp, B, st_bar, a=3, b=1):
    base = pol_hyst(Mp, a, b)
    veto = (base < 0) & (st_bar > 0) & ~((Tpp < 0) & (B < 0))
    return np.where(veto, 0, base).astype(np.int64)

cells = {
    347: ("C_hyst(3,1)", pol_hyst(Mp, 3, 1)),
    348: ("C_hyst(4,1)", pol_hyst(Mp, 4, 1)),
    349: ("B_sign_db(enter3,exit0)", pol_sign_db(Mp, 3, 0)),
    350: ("A_dominant(solar>=5)", pol_dominant(Tpp, B, 5)),
    351: ("A_dominant(solar>=7)", pol_dominant(Tpp, B, 7)),
    352: ("E_conflictflat(solar>=5)", pol_conflict_flat(Tpp, B, 5)),
    353: ("E_conflictflat(solar>=7)", pol_conflict_flat(Tpp, B, 7)),
    354: ("G_router_htf(3,1)", pol_router(Mp, Tpp, B, st_bar, 3, 1)),
    355: ("SM14_ref_oldM(3,1)", pol_hyst(Mp_old, 3, 1)),
    356: ("C_hyst_lowDD(5,2)", pol_hyst(Mp, 5, 2)),
    357: ("A_dominant(solar>=9)", pol_dominant(Tpp, B, 9)),
}

# crisis days (same def as SMV2E)
sret = sclose.pct_change(); sret_dev = sret[sret.index <= pd.Timestamp("2026-05-31").date()]
worst20 = pd.to_datetime(pd.Series(sret_dev.nsmallest(20).index))

rows = []; curves = {}
for seq, (name, des_full) in cells.items():
    des = des_full[devnp]
    dl, fills, eq = run_policy(bars_dev, des, *MNQ)
    dlq, _, eqq = run_policy(bars_dev, des, *NQ)
    b = dd_battery(dl.index, dl.values, bar_eq=eq, label=f"{seq}_{name}")
    bq = dd_battery(dlq.index, dlq.values, bar_eq=eqq, label="")
    yr = dl.groupby(dl.index.year).sum()
    h1 = dl[dl.index <= "2024-03-31"].sum(); h2 = dl[dl.index > "2024-03-31"].sum()
    b.update({"seq": seq, "fills": fills, "years_pos": int((yr > 0).sum()), "n_years": len(yr),
              "h1": h1, "h2": h2, "crisis20": dl[dl.index.isin(worst20)].sum(),
              "nq_net": bq["net"], "nq_sharpe": bq["sharpe"], "nq_maxDD": bq["maxDD_eod"],
              "nq_maxDD_bar": bq.get("maxDD_bar", np.nan)})
    rows.append(b); curves[f"{seq}_{name}"] = dl
    print(f"{seq} {name:28s} MNQ net {b['net']:7.0f} shp {b['sharpe']:.2f} DD {b['maxDD_eod']:6.0f} "
          f"wm {b['worst_month']:6.0f} TUW {b['longest_TUW_days']:3d} | NQ net {bq['net']:8.0f} "
          f"shp {bq['sharpe']:.2f} DD {bq['maxDD_eod']:6.0f} | yrs+{b['years_pos']}/{b['n_years']} "
          f"crisis {b['crisis20']:6.0f} fills {fills}")

df = pd.DataFrame(rows).set_index("seq")
df.to_csv(f"{OUT}/results.csv")
pd.DataFrame(curves).to_csv(f"{OUT}/daily_curves.csv")

# replacement gate vs seq 355 reference
ref = curves["355_SM14_ref_oldM(3,1)"]
print("\n--- replacement gate vs SM14 reference (355) ---")
for seq, (name, _) in cells.items():
    if seq == 355: continue
    c = curves[f"{seq}_{name}"]
    diff = c.values - ref.values
    lo, hi, p = boot_ci_mean(diff, n_boot=4000)
    crisis_ret = df.loc[seq, "crisis20"] / df.loc[355, "crisis20"]
    wins = 0
    for col, sgn in [("sharpe", 1), ("calmar", 1), ("maxDD_eod", -1), ("worst_month", 1), ("longest_TUW_days", -1)]:
        wins += (df.loc[seq, col] - df.loc[355, col]) * sgn > 0
    print(f"{seq} {name:28s} wins {wins}/5  P(diff>0)={p:.3f}  crisis_ret {crisis_ret:.2f}")

# ---------------- SM14 top-10 DD autopsy ----------------
print("\n--- SM14 OneLot top-10 DD autopsy (canonical replay, MNQ basis) ---")
g = ref  # SM14-form curve on canonical executor
eqd = g.cumsum(); peak = eqd.cummax(); dd = peak - eqd
episodes = []
in_ep = False
for i in range(len(dd)):
    if dd.iloc[i] > 0 and not in_ep:
        in_ep = True; start = i; trough = i
    elif in_ep:
        if dd.iloc[i] > dd.iloc[trough]: trough = i
        if dd.iloc[i] == 0:
            episodes.append((start, trough, i, dd.iloc[trough])); in_ep = False
if in_ep: episodes.append((start, trough, len(dd) - 1, dd.iloc[trough]))
episodes.sort(key=lambda e: -e[3])
au = []
sd_dev = bars_dev["sess_date"].to_numpy()
des355 = cells[355][1][devnp]
bar_sess = pd.to_datetime(bars_dev["sess_date"])
for (s0, tr, e0, depth) in episodes[:10]:
    d0, d1 = g.index[s0], g.index[tr]
    mask = (bar_sess >= d0) & (bar_sess <= d1)
    seg = des355[mask.to_numpy()]
    B_seg = B[devnp][mask.to_numpy()]
    Tpp_seg = Tp_old[devnp][mask.to_numpy()]
    au.append({"start": d0.date(), "trough": d1.date(), "depth": depth,
               "days": (tr - s0), "pct_short": (seg < 0).mean(), "pct_long": (seg > 0).mean(),
               "pct_flat": (seg == 0).mean(),
               "bmom_active": (B_seg != 0).mean(), "solar_strong": (np.abs(Tpp_seg) >= 5).mean(),
               "htf_up": np.nanmean(st_bar[devnp][mask.to_numpy()] > 0)})
audf = pd.DataFrame(au); audf.to_csv(f"{OUT}/sm14_dd_autopsy.csv", index=False)
print(audf.round(2).to_string())
print("done")
