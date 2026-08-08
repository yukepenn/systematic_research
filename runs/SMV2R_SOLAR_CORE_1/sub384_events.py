"""SMV2R sub_384 — signal layer (DIAGNOSTIC, seq 384).
Emit T1 (flip, sig +-1), T2 (weak onset = pullback/slowdown), T3 (resumption, sig +-3)
event streams from the verified member simulator, using the E10Master_v2.cs
UpdateMachine ev/weak/wave semantics (SlowdownScan=5, WeakWeakSplit=10) transplanted
into sm01_solarsim.member_states arithmetic. Transplant is verified bar-for-bar
against sm.member_states (is_up/flip/s_eff must match exactly).

Conventions (stated in REPORT):
- Events timestamped at decision bar close t; direction = trend direction at t.
- Forward return: enter at bar t+1 open via _fill (1-tick adverse slip), exit at close
  of bar min(t+h, session end) via _fill at_close; net of 1-lot MNQ costs (2 x $0.65).
  h in {10, 20, 40} bars = 30/60/120 min. Events on the session's last bar are dropped.
- Events deduplicated across members to unique (bar, type, dir); member count kept.
- t-stats: Newey-West with lag = horizon bars on the event-ordered series (overlap
  correction); conditional analysis via OLS event-dummy with NW lag h on the
  positioned-bar series. DIAGNOSTIC ONLY — NO POLICY.
"""
import sys, os, json, time, datetime as dt
import numpy as np, pandas as pd

RUN = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\SMV2R_SOLAR_CORE_1"
sys.path.insert(0, RUN)
from common_exec import sm, ROOT

OUT = os.path.join(RUN, "out")
DEV_END = dt.date(2026, 5, 31)
SLOWDOWN_SCAN, WEAKWEAK_SPLIT = 5, 10
t0 = time.time()

bars = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
bars = bars[bars["sess_date"] <= DEV_END].reset_index(drop=True)
close = bars.close.to_numpy(); open_ = bars.open.to_numpy()
high = bars.high.to_numpy(); low = bars.low.to_numpy()
sess_id = bars.sess_id.to_numpy()
n = len(bars)
sig = sm.sigma_series(close)
cache = np.load(os.path.join(OUT, "cache_incumbent.npz"))
tgt = cache["tgt"]

# session end index per bar
sess_end = np.zeros(n, dtype=int)
_, first_idx = np.unique(sess_id, return_index=True)
bounds = np.append(first_idx, n)
for k in range(len(first_idx)):
    sess_end[bounds[k]:bounds[k+1]] = bounds[k+1] - 1


def member_states_events(close, sigma, vol_mult):
    """sm.member_states arithmetic + E10Master_v2 ev/weak/wave transplant."""
    nn = close.size
    lo, hi = 40 * sm.TICK, 1200 * sm.TICK
    fallback = 179 * sm.TICK

    def resolve_s(t):
        s = sigma[t]
        if not np.isfinite(s) or s <= 0:
            return fallback
        return min(max(vol_mult * s, lo), hi)

    is_up = np.zeros(nn, dtype=bool); flip = np.zeros(nn, dtype=np.int8)
    s_eff = np.empty(nn); anchor_out = np.empty(nn)
    sig_out = np.zeros(nn, dtype=np.int8)     # +-1 flip, +-3 resumption
    weak_onset = np.zeros(nn, dtype=np.int8)  # +-1 at weak-flag set (dir = trend)
    wave_out = np.zeros(nn, dtype=np.int32)

    up = False
    anchor = close[0]; S = resolve_s(0)
    weak = False; bse = 0; next_weak = -10**9; wave = 1
    is_up[0] = up; s_eff[0] = S; anchor_out[0] = anchor; wave_out[0] = wave

    for t in range(1, nn):
        px = close[t]; ev = 0
        if up:
            if px >= anchor:
                if px > anchor: ev = 1
                anchor = px
            elif px < anchor - S:
                up = False; ev = 2
                S = resolve_s(t); anchor = px
                flip[t] = -1
        else:
            if px <= anchor:
                if px < anchor: ev = 1
                anchor = px
            elif px > anchor + S:
                up = True; ev = 2
                S = resolve_s(t); anchor = px
                flip[t] = 1
        if ev == 2:
            weak = False; bse = 0; wave = 1
            sig_out[t] = 1 if up else -1
            next_weak = t + WEAKWEAK_SPLIT
        elif ev == 1:
            bse = 0
            if weak:
                wave += 1; weak = False
                sig_out[t] = 3 if up else -3
                next_weak = t + WEAKWEAK_SPLIT
        else:
            bse += 1
            if not weak and bse >= SLOWDOWN_SCAN and t >= next_weak:
                weak = True; next_weak = t + WEAKWEAK_SPLIT
                weak_onset[t] = 1 if up else -1
        is_up[t] = up; s_eff[t] = S; anchor_out[t] = anchor; wave_out[t] = wave
    return is_up, flip, s_eff, anchor_out, sig_out, weak_onset, wave_out


# ---- build events for all members; verify transplant vs committed simulator ----
ev_rows = []
for vm in sm.VMS:
    iu, fl, se, an, sg, wo, wv = member_states_events(close, sig, float(vm))
    iu0, fl0, se0, an0 = sm.member_states(close, sig, float(vm))
    assert (iu == iu0).all() and (fl == fl0).all(), f"transplant mismatch vm{vm}"
    assert np.allclose(se, se0) and np.allclose(an, an0), f"transplant S/anchor vm{vm}"
    for t in np.nonzero(sg)[0]:
        et = "T1" if abs(sg[t]) == 1 else "T3"
        ev_rows.append((t, et, int(np.sign(sg[t])), vm))
    for t in np.nonzero(wo)[0]:
        ev_rows.append((t, "T2", int(wo[t]), vm))
    print(f"vm{vm} events done {time.time()-t0:.0f}s", flush=True)

ev = pd.DataFrame(ev_rows, columns=["bar", "etype", "dir", "vm"])
ev = ev[ev.bar >= 20]
# dedupe to unique (bar, etype, dir), keep member count
evu = ev.groupby(["bar", "etype", "dir"]).size().rename("n_members").reset_index()
last_of_sess_mask = evu.bar.to_numpy() == sess_end[evu.bar.to_numpy()]
n_dropped_lastbar = int(last_of_sess_mask.sum())
evu = evu[~last_of_sess_mask].reset_index(drop=True)
evu = evu[evu.bar < n - 1].reset_index(drop=True)

PV, COMM = sm.MNQ_POINT_VALUE, sm.MNQ_COMM_SIDE
HORIZONS = {"30min": 10, "60min": 20, "120min": 40}

b = evu.bar.to_numpy(); d = evu.dir.to_numpy()
entry_px = np.array([sm._fill(open_[t+1], high[t+1], low[t+1], dd)
                     for t, dd in zip(b, d)])
for hname, h in HORIZONS.items():
    e_bar = np.minimum(b + h, sess_end[b])
    exit_px = np.array([sm._fill(open_[eb], high[eb], low[eb], -dd, at_close=close[eb])
                        for eb, dd in zip(e_bar, d)])
    evu[f"net_{hname}"] = d * (exit_px - entry_px) * PV - 2 * COMM
    evu[f"trunc_{hname}"] = e_bar < b + h
# MFE/MAE over the 120-min (truncated) window, points from entry fill
e_bar120 = np.minimum(b + 40, sess_end[b])
mfe = np.empty(len(evu)); mae = np.empty(len(evu))
for i, (t, dd, eb, epx) in enumerate(zip(b, d, e_bar120, entry_px)):
    hi_ = high[t+1:eb+1]; lo_ = low[t+1:eb+1]
    if dd == 1:
        mfe[i] = hi_.max() - epx; mae[i] = epx - lo_.min()
    else:
        mfe[i] = epx - lo_.min(); mae[i] = hi_.max() - epx
evu["mfe_pts"] = mfe; evu["mae_pts"] = mae
evu["tgt_at_event"] = tgt[b]
evu["overlap"] = np.select([np.sign(evu.tgt_at_event) == evu.dir,
                            evu.tgt_at_event == 0], ["same", "flat"], "opposite")
print(f"forward returns built {time.time()-t0:.0f}s", flush=True)


def nw_t(x, lag):
    x = np.asarray(x, float); m = x.mean(); u = x - m; nn = len(x)
    if nn < 10: return np.nan
    v = (u @ u) / nn
    for L in range(1, min(lag, nn - 1) + 1):
        w = 1 - L / (lag + 1)
        v += 2 * w * (u[:-L] @ u[L:]) / nn
    return m / np.sqrt(max(v, 1e-300) / nn)


# ---- summary per etype x dir x horizon ----
rows = []
for (et, dd), g in evu.groupby(["etype", "dir"]):
    g = g.sort_values("bar")
    for hname, h in HORIZONS.items():
        x = g[f"net_{hname}"].to_numpy()
        rows.append({
            "etype": et, "dir": dd, "horizon": hname,
            "N_unique": len(g), "N_member_events": int(g.n_members.sum()),
            "mean_net_$": x.mean(), "median_net_$": float(np.median(x)),
            "t_NW": nw_t(x, h), "win_frac": float((x > 0).mean()),
            "mfe_mean_pts": float(g.mfe_pts.mean()), "mae_mean_pts": float(g.mae_pts.mean()),
            "pct_overlap_same": float((g.overlap == "same").mean() * 100),
            "pct_overlap_flat": float((g.overlap == "flat").mean() * 100),
            "pct_overlap_opp": float((g.overlap == "opposite").mean() * 100),
            "mean_net_when_same_$": float(g.loc[g.overlap == "same", f"net_{hname}"].mean()),
            "mean_net_when_flat_$": float(g.loc[g.overlap == "flat", f"net_{hname}"].mean()),
            "mean_net_when_opp_$": float(g.loc[g.overlap == "opposite", f"net_{hname}"].mean()),
        })
summ = pd.DataFrame(rows)

# ---- incremental information conditional on ensemble positioned ----
# per-bar forward net (direction = sign(tgt[t])) for all positioned, non-last bars
pos_mask = (tgt != 0) & (np.arange(n) != sess_end) & (np.arange(n) < n - 1)
pb = np.nonzero(pos_mask)[0]
pdir = np.sign(tgt[pb]).astype(int)
pentry = np.array([sm._fill(open_[t+1], high[t+1], low[t+1], dd)
                   for t, dd in zip(pb, pdir)])
cond_rows = []
for hname, h in HORIZONS.items():
    e_bar = np.minimum(pb + h, sess_end[pb])
    pexit = np.array([sm._fill(open_[eb], high[eb], low[eb], -dd, at_close=close[eb])
                      for eb, dd in zip(e_bar, pdir)])
    fwd = pdir * (pexit - pentry) * PV - 2 * COMM
    base_mean = fwd.mean()
    for et in ("T1", "T2", "T3"):
        same = evu[(evu.etype == et) & (evu.overlap == "same")]
        dummy = np.zeros(len(pb), dtype=bool)
        idx = np.searchsorted(pb, same.bar.to_numpy())
        ok = (idx < len(pb)) & (pb[np.minimum(idx, len(pb)-1)] == same.bar.to_numpy())
        dummy[idx[ok]] = True
        # OLS fwd ~ 1 + dummy with NW lag h
        X = np.column_stack([np.ones(len(pb)), dummy.astype(float)])
        beta, *_ = np.linalg.lstsq(X, fwd, rcond=None)
        u = fwd - X @ beta
        XtX_inv = np.linalg.inv(X.T @ X)
        S0 = (X * u[:, None]).T @ (X * u[:, None])
        Sv = S0.copy()
        for L in range(1, h + 1):
            w = 1 - L / (h + 1)
            G = (X[:-L] * u[:-L, None]).T @ (X[L:] * u[L:, None])
            Sv += w * (G + G.T)
        V = XtX_inv @ Sv @ XtX_inv
        cond_rows.append({
            "etype": et, "horizon": hname, "n_events_same_dir": int(dummy.sum()),
            "n_positioned_bars": int(len(pb)),
            "baseline_mean_net_$": float(base_mean),
            "event_incremental_$": float(beta[1]),
            "t_NW_incremental": float(beta[1] / np.sqrt(max(V[1, 1], 1e-300))),
        })
    print(f"conditional {hname} done {time.time()-t0:.0f}s", flush=True)
cond = pd.DataFrame(cond_rows)

summ.to_csv(os.path.join(OUT, "signal_layer.csv"), index=False)
cond.to_csv(os.path.join(OUT, "signal_layer_conditional.csv"), index=False)
evu.to_parquet(os.path.join(OUT, "signal_events.parquet"), index=False)
meta = {"n_member_events": int(len(ev)), "n_unique_events": int(len(evu)),
        "n_dropped_last_bar": n_dropped_lastbar,
        "slowdown_scan": SLOWDOWN_SCAN, "weakweak_split": WEAKWEAK_SPLIT,
        "runtime_s": round(time.time() - t0, 1)}
with open(os.path.join(OUT, "signal_layer_meta.json"), "w") as f:
    json.dump(meta, f, indent=2)
print(summ.to_string(index=False))
print(cond.to_string(index=False))
print(json.dumps(meta, indent=2))
