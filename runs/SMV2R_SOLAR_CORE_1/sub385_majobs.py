"""SMV2R sub_385 — MA state jobs (DIAGNOSTIC, seq 385). States on dev 3m closes:
  ST1 = MA30/59 cross, ST2 = MA100/400 (broad neighbor / HTF control),
  ER  = ER150 tercile (non-MA reference; terciles from dev distribution).
JOB A entry-confirmation counterfactual: delay each E10 target change that INCREASES
      exposure until the state agrees (MA: sign match; ER: top tercile). Risk-reducing
      changes execute immediately. Report net / right-tail cost.
JOB B soft confidence: daily state-agreement vs NEXT-day E10 PnL, controlling for ST2
      (HTF). NW lag 5.
JOB C failure warning: state flip against an open ensemble position -> remaining-episode
      PnL vs random-flip placebo matched by count (seed 20260808).
JOB D re-entry timing: exit-at-conflict / re-enter-at-resolution counterfactual within
      episodes (round-trip cost = |pos| * 2 * ($0.65 + $0.50 slip)).
All information reads; |t_NW| > 2 bar; NO POLICY. Undefined (warmup) states = AGREE
(no gating) and are excluded from B/C/D stats.
"""
import sys, os, json, datetime as dt
import numpy as np, pandas as pd

RUN = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\SMV2R_SOLAR_CORE_1"
sys.path.insert(0, RUN)
from common_exec import sm, e10_exec, metric_row, ROOT

OUT = os.path.join(RUN, "out")
DEV_END = dt.date(2026, 5, 31)
SEED = 20260808

bars = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
bars = bars[bars["sess_date"] <= DEV_END].reset_index(drop=True)
close = bars.close.to_numpy(); n = len(bars)
last_of_sess = bars["is_last_of_sess"].to_numpy()
sess_date = bars["sess_date"].to_numpy()

cache = np.load(os.path.join(OUT, "cache_incumbent.npz"))
tgt = cache["tgt"]; bar_pos = cache["bar_pos"]; bar_pnl = cache["bar_pnl"]
base_daily = pd.read_csv(os.path.join(OUT, "e10_daily_dev_incumbent.csv"))
base_daily["sess"] = pd.to_datetime(base_daily["sess"]).dt.date

cs = pd.Series(close)
def sma(w): return cs.rolling(w).mean().to_numpy()
ma30, ma59, ma100, ma400 = sma(30), sma(59), sma(100), sma(400)
st1 = np.where(np.isnan(ma59), 0, np.where(ma30 >= ma59, 1, -1)).astype(int)
st2 = np.where(np.isnan(ma400), 0, np.where(ma100 >= ma400, 1, -1)).astype(int)
dabs = np.abs(np.diff(close, prepend=close[0])); dabs[0] = 0
csum = np.cumsum(dabs)
er = np.full(n, np.nan)
er[150:] = np.abs(close[150:] - close[:-150]) / np.maximum(csum[150:] - csum[:-150], 1e-9)
fin = np.isfinite(er)
q33, q67 = np.percentile(er[fin], [100/3, 200/3])
st_er = np.full(n, -1, dtype=int)  # -1 = undefined
st_er[fin] = np.digitize(er[fin], [q33, q67])  # 0/1/2

STATES = {"MA30_59": st1, "MA100_400": st2, "ER150": st_er}

def agree_fn(sname, d, t):
    s = STATES[sname][t]
    if sname == "ER150":
        return (s == 2) or (s == -1)      # top tercile; undefined = agree
    return (s == d) or (s == 0)           # sign match; undefined = agree

# ---------------- JOB A: gated executor ----------------
def e10_exec_gated(sname):
    open_ = bars["open"].to_numpy(); high = bars["high"].to_numpy()
    low = bars["low"].to_numpy()
    cash = 0.0; p = 0; pend_ = 0
    daily = {}; contracts = {}
    prev_equity = 0.0
    n_changes = n_gated_changes = n_gated_bars = 0
    for t in range(n):
        if pend_ != p:
            d = pend_ - p; side = 1 if d > 0 else -1
            px = sm._fill(open_[t], high[t], low[t], side)
            cash -= d * px * sm.MNQ_POINT_VALUE; cash -= abs(d) * sm.MNQ_COMM_SIDE
            contracts[sess_date[t]] = contracts.get(sess_date[t], 0) + abs(d)
            p = pend_
        if last_of_sess[t] and p != 0:
            px = sm._fill(open_[t], high[t], low[t], -1 if p > 0 else 1, at_close=close[t])
            cash += p * px * sm.MNQ_POINT_VALUE; cash -= abs(p) * sm.MNQ_COMM_SIDE
            contracts[sess_date[t]] = contracts.get(sess_date[t], 0) + abs(p)
            p = 0; pend_ = 0
        else:
            desired = int(tgt[t])
            if desired != p: n_changes += 1
            if desired == p:
                pend_ = desired
            elif desired * p >= 0 and abs(desired) < abs(p):
                pend_ = desired                       # pure reduction: immediate
            elif desired * p >= 0:                    # same-side increase (or from 0)
                if agree_fn(sname, 1 if desired > 0 else -1, t):
                    pend_ = desired
                else:
                    pend_ = p; n_gated_changes += 1
            else:                                     # sign flip
                if agree_fn(sname, 1 if desired > 0 else -1, t):
                    pend_ = desired
                else:
                    pend_ = 0; n_gated_changes += 1   # reduce to flat, hold entry
            if pend_ != desired: n_gated_bars += 1
        if last_of_sess[t]:
            eq = cash + p * close[t] * sm.MNQ_POINT_VALUE
            daily[sess_date[t]] = eq - prev_equity
            prev_equity = eq
            contracts.setdefault(sess_date[t], 0)
    dd = pd.DataFrame({"sess": list(daily.keys()), "net": list(daily.values())})
    dd["contracts"] = [contracts[s] for s in daily.keys()]
    return dd, n_changes, n_gated_changes, n_gated_bars

rowsA = []
base_row = metric_row("baseline", base_daily.assign(contracts=0))
base_top10_days = base_daily.set_index("sess")["net"].nlargest(10)
for sname in STATES:
    d, nc, ngc, ngb = e10_exec_gated(sname)
    r = metric_row(sname, d)
    dser = d.copy(); dser["sess"] = pd.to_datetime(dser["sess"]).dt.date
    dser = dser.set_index("sess")["net"]
    r.update({"job": "A", "state": sname,
              "d_net_vs_base": r["net"] - base_row["net"],
              "pnl_on_base_top10_days": float(dser.reindex(base_top10_days.index).fillna(0).sum()),
              "base_top10_sum": float(base_top10_days.sum()),
              "n_target_changes": nc, "n_gated_change_events": ngc,
              "pct_bars_gated": ngb / n * 100})
    r["right_tail_retention"] = r["pnl_on_base_top10_days"] / r["base_top10_sum"]
    rowsA.append(r)
    print("JOB A", sname, f"net={r['net']:.0f} (base {base_row['net']:.0f}) "
          f"tail_ret={r['right_tail_retention']:.3f}", flush=True)

# ---------------- helpers ----------------
def nw_ols(y, X, lag):
    """OLS with Newey-West; returns beta, t. X includes const col."""
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    u = y - X @ beta
    XtX_inv = np.linalg.inv(X.T @ X)
    Xu = X * u[:, None]
    S = Xu.T @ Xu
    for L in range(1, lag + 1):
        w = 1 - L / (lag + 1)
        G = Xu[:-L].T @ Xu[L:]
        S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    return beta, beta / np.sqrt(np.maximum(np.diag(V), 1e-300))

# ---------------- JOB B: daily agreement vs next-day PnL ----------------
df = pd.DataFrame({"sess": sess_date, "pos": bar_pos,
                   "st1": st1, "st2": st2, "st_er": st_er})
df = df[df.pos != 0]
sgn = np.sign(df.pos)
g = df.assign(a1=(df.st1 == sgn), a2=(df.st2 == sgn), aer=(df.st_er == 2),
              def1=df.st1 != 0, def2=df.st2 != 0, defer_=df.st_er >= 0)
day = g.groupby("sess").agg(a1=("a1", "mean"), a2=("a2", "mean"), aer=("aer", "mean"),
                            def1=("def1", "mean"), def2=("def2", "mean"))
day = day.join(base_daily.set_index("sess")["net"], how="inner")
day["next_net"] = day["net"].shift(-1)
day = day.dropna()
Z = lambda v: (v - v.mean()) / v.std(ddof=1)
rowsB = []
y = day["next_net"].to_numpy()
X12 = np.column_stack([np.ones(len(day)), Z(day.a1), Z(day.a2)])
b, t = nw_ols(y, X12, 5)
rowsB.append({"job": "B", "state": "MA30_59|HTF", "coef_$_per_sd": b[1], "t_NW": t[1],
              "n_days": len(day), "note": "next-day net ~ z(agree30/59)+z(agree100/400)"})
rowsB.append({"job": "B", "state": "MA100_400", "coef_$_per_sd": b[2], "t_NW": t[2],
              "n_days": len(day), "note": "HTF control coef in same regression"})
Xer = np.column_stack([np.ones(len(day)), Z(day.aer), Z(day.a2)])
b2, t2 = nw_ols(y, Xer, 5)
rowsB.append({"job": "B", "state": "ER150_top|HTF", "coef_$_per_sd": b2[1], "t_NW": t2[1],
              "n_days": len(day), "note": "next-day net ~ z(fracER_top)+z(agree100/400)"})
# same-day (contemporaneous, context only)
Xc = np.column_stack([np.ones(len(day)), Z(day.a1), Z(day.a2)])
bc, tc = nw_ols(day["net"].to_numpy(), Xc, 5)
rowsB.append({"job": "B", "state": "MA30_59_SAMEDAY", "coef_$_per_sd": bc[1], "t_NW": tc[1],
              "n_days": len(day), "note": "context only (contemporaneous)"})
print("JOB B done", flush=True)

# ---------------- episodes ----------------
sgn_all = np.sign(bar_pos)
episodes = []  # (start, end, dir) inclusive bar indices, constant sign != 0
s = None
for t in range(n):
    if s is None:
        if sgn_all[t] != 0: s = t
    else:
        if sgn_all[t] != sgn_all[s]:
            episodes.append((s, t - 1, int(sgn_all[s])))
            s = t if sgn_all[t] != 0 else None
if s is not None:
    episodes.append((s, n - 1, int(sgn_all[s])))
episodes = [(a, b_, d) for a, b_, d in episodes if b_ - a >= 2]

def conflicts_for(sname):
    st = STATES[sname]
    out = []
    for (a, b_, d) in episodes:
        if sname == "ER150":
            bad = lambda t: st[t] == 0
        else:
            bad = lambda t: st[t] == -d
        for t in range(a + 1, b_):          # need remaining bars after t
            if bad(t) and not bad(t - 1):
                if sname != "ER150" and st[t - 1] == 0:
                    continue                # warmup transition, skip
                out.append((a, b_, d, t))
                break                        # first conflict per episode
    return out

rng = np.random.default_rng(SEED)
pool = [(a, b_, d, t) for (a, b_, d) in episodes for t in range(a + 1, b_)]
cum_pnl = np.cumsum(bar_pnl)
def remaining(a, b_, t): return cum_pnl[b_] - cum_pnl[t]

rowsC = []
for sname in STATES:
    real = conflicts_for(sname)
    if len(real) < 10:
        rowsC.append({"job": "C", "state": sname, "n_real": len(real), "note": "too few"})
        continue
    idx = rng.choice(len(pool), size=len(real), replace=False)
    plc = [pool[i] for i in idx]
    xr = np.array([remaining(a, b_, t) for a, b_, d, t in real])
    xp = np.array([remaining(a, b_, t) for a, b_, t in [(p[0], p[1], p[3]) for p in plc]])
    vr, vp = xr.var(ddof=1) / len(xr), xp.var(ddof=1) / len(xp)
    t_welch = (xr.mean() - xp.mean()) / np.sqrt(vr + vp)
    rowsC.append({"job": "C", "state": sname, "n_real": len(real),
                  "n_episodes": len(episodes),
                  "frac_episodes_with_conflict": len(real) / len(episodes),
                  "mean_remaining_real_$": xr.mean(), "mean_remaining_placebo_$": xp.mean(),
                  "median_remaining_real_$": float(np.median(xr)),
                  "median_remaining_placebo_$": float(np.median(xp)),
                  "mean_remaining_bars_real": float(np.mean([b_ - t for a, b_, d, t in real])),
                  "mean_remaining_bars_placebo": float(np.mean([p[1] - p[3] for p in plc])),
                  "t_welch_real_vs_placebo": t_welch})
    print("JOB C", sname, f"real={xr.mean():.1f} placebo={xp.mean():.1f} t={t_welch:.2f}", flush=True)

# ---------------- JOB D: conflict resolution re-entry ----------------
rowsD = []
for sname in STATES:
    st = STATES[sname]
    evs = []
    for (a, b_, d, u) in conflicts_for(sname):
        ok = (lambda t: st[t] == 2) if sname == "ER150" else (lambda t: st[t] == d)
        r_ = next((t for t in range(u + 1, b_) if ok(t)), None)
        if r_ is None:
            continue
        w1 = cum_pnl[r_] - cum_pnl[u]      # PnL over conflict window (u+1..r]
        rt_cost = abs(bar_pos[u]) * 2 * (sm.MNQ_COMM_SIDE + sm.TICK * sm.MNQ_POINT_VALUE)
        evs.append((r_ - u, w1, -w1 - rt_cost))
    if len(evs) < 10:
        rowsD.append({"job": "D", "state": sname, "n_resolved": len(evs), "note": "too few"})
        continue
    dur = np.array([e[0] for e in evs]); w1 = np.array([e[1] for e in evs])
    ben = np.array([e[2] for e in evs])
    tb = ben.mean() / (ben.std(ddof=1) / np.sqrt(len(ben)))
    rowsD.append({"job": "D", "state": sname, "n_resolved": len(evs),
                  "mean_conflict_dur_bars": float(dur.mean()),
                  "median_conflict_dur_bars": float(np.median(dur)),
                  "mean_conflict_window_pnl_$": float(w1.mean()),
                  "mean_exit_reenter_benefit_$": float(ben.mean()),
                  "t_benefit": float(tb),
                  "frac_benefit_pos": float((ben > 0).mean())})
    print("JOB D", sname, f"benefit={ben.mean():.1f} t={tb:.2f}", flush=True)

all_rows = rowsA + rowsB + rowsC + rowsD
out = pd.DataFrame(all_rows)
out.to_csv(os.path.join(OUT, "ma_jobs.csv"), index=False)
meta = {"er_terciles": [float(q33), float(q67)], "n_episodes": len(episodes),
        "seed": SEED, "baseline_net": base_row["net"],
        "baseline_sharpe": base_row["sharpe"], "baseline_top10_sum": float(base_top10_days.sum())}
with open(os.path.join(OUT, "ma_jobs_meta.json"), "w") as f:
    json.dump(meta, f, indent=2)
print(out.to_string(index=False))
