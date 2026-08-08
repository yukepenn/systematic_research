"""Debug: find where BOCPD state goes non-finite on dev blocks (lam=100)."""
import os, math
import numpy as np
import pandas as pd
from scipy.special import gammaln

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
DEV_END = pd.Timestamp("2026-05-31")
RMAX = 2000
KAPPA0, ALPHA0, MU0 = 1.0, 2.0, 0.0

v = pd.read_parquet(os.path.join(ROOT, "runs/SM01_SUBSTRATE/out/vote_state_3m.parquet"),
                    columns=["time", "sess_date", "close", "sigma460"])
v["sess_date"] = pd.to_datetime(v["sess_date"])
v = v[v["sess_date"] <= DEV_END].reset_index(drop=True)
c = v["close"].to_numpy(float)
logc = np.log(c)
sd = v["sess_date"].to_numpy()
last_idx = np.flatnonzero(np.r_[sd[1:] != sd[:-1], True])
sess_dates = pd.DatetimeIndex(sd[last_idx])

xs = []
sess_last = np.full(len(last_idx), -1, dtype=int)
start = 0
for i, k in enumerate(last_idx):
    nbar = k - start + 1
    G = nbar // 10
    for g in range(G):
        end = start + 10 * g + 9
        anchor = start + 10 * g - 1
        if anchor < 0:
            anchor = 0
        xs.append(logc[end] - logc[anchor])
    sess_last[i] = len(xs) - 1
    start = k + 1
xs = np.asarray(xs)
sess_of_block = np.empty(len(xs), dtype=int)
prev = -1
for i, j in enumerate(sess_last):
    sess_of_block[prev + 1:j + 1] = i
    prev = j
cut12 = sess_dates[0] + pd.DateOffset(years=1)
in12 = sess_dates[sess_of_block] < cut12
beta0 = float(np.var(xs[in12], ddof=1))
print("nblocks", len(xs), "beta0", beta0, "min|x|", np.abs(xs).min(), "max|x|", np.abs(xs).max())
print("n zero-blocks", int((xs == 0).sum()))

lam = 100.0
H = 1.0 / lam
r_idx = np.arange(RMAX + 1, dtype=float)
kap_all = KAPPA0 + r_idx
alp_all = ALPHA0 + r_idx / 2.0
lconst_all = gammaln(alp_all + 0.5) - gammaln(alp_all) - 0.5 * np.log(2.0 * alp_all * np.pi)
P = np.array([1.0]); mu = np.array([MU0]); beta = np.array([beta0])
np.seterr(all="ignore")
for t in range(len(xs)):
    L = len(P)
    kap = kap_all[:L]; alp = alp_all[:L]
    s2 = beta * (kap + 1.0) / (alp * kap)
    if (s2 <= 0).any() or not np.isfinite(s2).all():
        bad = np.where((s2 <= 0) | ~np.isfinite(s2))[0]
        print(f"t={t} sess={sess_dates[sess_of_block[t]]} BAD s2 at r={bad[:10]}")
        print("  beta there:", beta[bad[:10]], "beta.min", beta.min(), "beta[0]", beta[0])
        break
    z2 = (xs[t] - mu) ** 2 / (2.0 * alp * s2)
    logpred = lconst_all[:L] - 0.5 * np.log(s2) - (alp + 0.5) * np.log1p(z2)
    w = P * np.exp(logpred)
    ws = w.sum()
    if not np.isfinite(ws):
        print(f"t={t} sess={sess_dates[sess_of_block[t]]} ws={ws}")
        print("  logpred max", np.nanmax(logpred), "min", np.nanmin(logpred),
              "n_naN", int(np.isnan(logpred).sum()), "s2.min", s2.min(), "beta.min", beta.min())
        break
    if ws <= 0.0:
        w = P.copy(); ws = w.sum()
        print(f"t={t} underflow-guard triggered, sess={sess_dates[sess_of_block[t]]}")
    cp = H * ws
    growth = (1.0 - H) * w
    mu_new = (kap * mu + xs[t]) / (kap + 1.0)
    beta_new = beta + kap * (xs[t] - mu) ** 2 / (2.0 * (kap + 1.0))
    if L <= RMAX:
        P = np.concatenate(([cp], growth))
        mu = np.concatenate(([MU0], mu_new))
        beta = np.concatenate(([beta0], beta_new))
    else:
        wa, wb = growth[RMAX - 1], growth[RMAX]
        tot = wa + wb
        P = np.concatenate(([cp], growth[:RMAX - 1], [tot]))
        if tot > 0:
            mu_cap = (wa * mu_new[RMAX - 1] + wb * mu_new[RMAX]) / tot
            beta_cap = (wa * beta_new[RMAX - 1] + wb * beta_new[RMAX]) / tot
        else:
            mu_cap, beta_cap = mu_new[RMAX], beta_new[RMAX]
        mu = np.concatenate(([MU0], mu_new[:RMAX - 1], [mu_cap]))
        beta = np.concatenate(([beta0], beta_new[:RMAX - 1], [beta_cap]))
    P /= P.sum()
    if not np.isfinite(P).all():
        print(f"t={t} sess={sess_dates[sess_of_block[t]]} P non-finite after normalize; Psum issue")
        break
else:
    print("completed with no non-finite states")
