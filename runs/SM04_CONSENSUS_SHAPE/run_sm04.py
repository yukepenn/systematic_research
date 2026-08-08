"""SM04 — consensus target-map shapes per frozen spec (seq 297-300)."""
import sys, os, json
sys.path.insert(0, "src/analytics")
import numpy as np, pandas as pd
import sm01_solarsim as sm
import sm_metrics as smm

OUT = "runs/SM04_CONSENSUS_SHAPE/out"
os.makedirs(OUT, exist_ok=True)
DEV_END = pd.Timestamp("2026-05-31").date()
H1_END = pd.Timestamp("2024-03-31")

bars = sm.load_bars_3m()
vote = pd.read_parquet("runs/SM01_SUBSTRATE/out/vote_state_3m.parquet")
pend = vote[[f"p{v}" for v in sm.VMS]].to_numpy()
s = pend.sum(axis=1)            # -13..13
m_bar = s / 13.0

def rnd(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)

BASE = np.clip(rnd(10 * m_bar), -10, 10).astype(int)

def u1(s, m_bar):
    t = rnd(10 * m_bar)
    boost = 2 * np.sign(s) * (np.abs(s) >= 11)
    return np.clip(t + boost, -12, 12).astype(int)

def u2(s, m_bar):
    return np.clip(rnd(10 * m_bar * (0.7 + 0.6 * np.abs(s) / 13.0)), -10, 10).astype(int)

def u3(s, m_bar):
    return np.clip(np.sign(m_bar) * rnd(10 * np.abs(m_bar) ** 1.5), -10, 10).astype(int)

def d1(s, m_bar):
    t = rnd(10 * m_bar)
    t[np.abs(s) <= 2] = 0
    return np.clip(t, -10, 10).astype(int)

MAPS = [(297, "U1_boost", u1), (298, "U2_tilt", u2), (299, "U3_convex", u3), (300, "D1_deadband", d1)]

def daily_of(tgt):
    d = sm.e10_sim(bars, tgt)
    d["sess"] = pd.to_datetime(d["sess"])
    return d.set_index("sess")["net"]

base_daily = daily_of(BASE)
bd = base_daily[base_daily.index.date <= DEV_END]
mb = smm.metrics(bd)
base_exp = np.abs(BASE).mean()
top10 = bd.nlargest(10)
top1pct_days = bd.nlargest(max(1, int(np.ceil(0.01 * len(bd)))))

rows = []
for seq, tag, fn in MAPS:
    tgt = fn(s.copy(), m_bar)
    d = daily_of(tgt)
    dd = d[d.index.date <= DEV_END]
    exp = np.abs(tgt).mean()
    scale = base_exp / exp if exp > 0 else np.nan   # matched average exposure
    dme = dd * scale
    m_me = smm.metrics(dme)
    ret10 = float(dme.reindex(top10.index).sum() / top10.sum())
    ret1p = float(dme.reindex(top1pct_days.index).sum() / top1pct_days.sum())
    delta = dme - bd.reindex(dme.index).fillna(0)
    h1 = delta[delta.index <= H1_END].mean(); h2 = delta[delta.index > H1_END].mean()
    bbs = smm.block_bootstrap_delta(dme.to_numpy(), bd.reindex(dme.index).fillna(0).to_numpy(),
                                    stat=lambda v: v.mean() / (v.std(ddof=1) + 1e-12))
    bbg = smm.block_bootstrap_delta(dme.to_numpy(), bd.reindex(dme.index).fillna(0).to_numpy())
    rows.append({
        "seq": seq, "arm": tag, "mean_abs_tgt": exp, "exp_scale": scale,
        "net_me": m_me["net"], "d_net": m_me["net"] - mb["net"],
        "sharpe": m_me["sharpe"], "d_sharpe": m_me["sharpe"] - mb["sharpe"],
        "logG": m_me["logG_100k"], "d_logG": m_me["logG_100k"] - mb["logG_100k"],
        "max_dd": m_me["max_dd"], "d_dd_pct": (m_me["max_dd"] - mb["max_dd"]) / abs(mb["max_dd"]) * 100,
        "worst_month": m_me["worst_month"],
        "top10day_ret": ret10, "top1pctday_ret": ret1p,
        "h1": h1, "h2": h2, "p_dsharpe": bbs["p_leq_0"], "p_dmean": bbg["p_leq_0"],
    })

df = pd.DataFrame(rows)
df.to_csv(f"{OUT}/results.csv", index=False)
pd.set_option("display.width", 250)
print("BASE:", {k: round(v, 3) for k, v in mb.items() if k in ("net", "sharpe", "logG_100k", "max_dd", "worst_month")}, "mean|tgt|", round(base_exp, 3))
print(df.round(3).to_string(index=False))
