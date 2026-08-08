"""SMV2K_ENGINE3_S1 — R1 FAMILY TEST, seq 368-370 (Engine #3 slate, DR pass A ranks 1/2/11).

e368  failed range-break fade  (PDH/PDL/ONH/ONL/IBH/IBL sweep + close-back-inside -> fade to VWAP)
e369  small-gap fade           (|gap| < 0.5 ATR14d, open inside prior RTH range -> fade to prior close)
e370  overnight drift cheap kill (long 16:42 -> next 09:33 after down RTH day; + unconditional)

All economics NET of $4.36/RT + 1 tick/side slippage (NQ, $20/pt, tick 0.25).
Dev window: sessions <= 2026-05-31. No data >= 2026-08-01 is ever used.

Frozen conventions (disclosed in REPORT.md):
- Bars: END-stamped 3m via sm01_solarsim.load_bars_3m (same substrate as every SMV2 run).
- "HH:MM open" = the open occurring at wall time HH:MM = open of the bar STAMPED HH:MM+3
  (anchored by e369's "fade ... from 09:33 next-bar open" = open of the 0936-stamped bar).
- RTH = stamps 0933..1600 (0933 bar's open is the 09:30 open); ON = stamps >=1803 or <=0930
  within the same sess_date; IB = stamps 0933..1030; session VWAP = RTH-anchored
  cum(close*vol)/cum(vol) incl. current bar (B-MOM convention, runs/SMV2B smv2b.py).
- ATR14d = mean of true range over the 14 PRIOR sessions (full-session H/L/C, causal shift(1)).
- e368 episode: first bar k (stamps 0933..1530; >=1033 for IB levels) whose high(low) exceeds
  the level after being inside; confirmation = first close strictly back inside at j<=k+conf-1;
  sweep extreme = max excursion over k..j; qualifies iff 0 < depth <= pen_mult*ATR14d.
  First qualifying episode per level per session. Direction = fade side (short upper/long lower).
  Entry _fill at open of bar j+1; exits: stop 2 ticks beyond sweep extreme (stop-first on ties),
  VWAP touch, 60-min time stop (close of entry_bar+19), forced RTH-end exit at the 1600 bar close.
- NW t-stat: mean per-event net, SE clustered by session with Bartlett/Newey-West lag 5 across
  event-session order (lag choice disclosed; lag-0 cluster t and iid t also reported).
"""
import sys, os
import numpy as np
import pandas as pd

sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m, _fill, TICK

RUN = "runs/SMV2K_ENGINE3_S1"
OUT = f"{RUN}/out"
os.makedirs(OUT, exist_ok=True)

PV = 20.0          # NQ point value
COMM_RT = 4.36     # $/round trip
DEV_END = pd.Timestamp("2026-05-31")
NW_LAG = 5
SPLIT = pd.Timestamp("2024-12-31")   # 2022-24 vs 2025-26

# ---------------------------------------------------------------- substrate
print("loading substrate ...")
bars = load_bars_3m()
bars["sd"] = pd.to_datetime(bars["sess_date"])
assert bars["sd"].max() < pd.Timestamp("2026-08-01"), "VIRGIN data in file?!"
bars = bars[bars["sd"] <= DEV_END].reset_index(drop=True)
t = pd.to_datetime(bars["time"])
bars["hm"] = t.dt.hour * 100 + t.dt.minute
print(f"dev bars {len(bars)}  sessions {bars['sd'].nunique()}  "
      f"range {bars['sd'].min().date()} .. {bars['sd'].max().date()}")

# ------------------------------------------------- per-session tables/arrays
sess_rows = []
rth_arrays = {}     # sd -> dict of np arrays for RTH bars
bar1645 = {}        # sd -> (o,h,l) of the 1645-stamped bar (opens 16:42)
for sd, g in bars.groupby("sd", sort=True):
    g = g.sort_values("time")
    hm = g["hm"].to_numpy()
    row = {"sd": sd,
           "s_high": g["high"].max(), "s_low": g["low"].min(),
           "s_close": g["close"].iloc[-1]}
    on = g[(hm >= 1803) | (hm <= 930)]
    row["on_high"] = on["high"].max() if len(on) else np.nan
    row["on_low"] = on["low"].min() if len(on) else np.nan
    r = g[(hm >= 933) & (hm <= 1600)]
    if len(r):
        rhm = r["hm"].to_numpy()
        row["rth_first_hm"] = rhm[0]
        row["open0930"] = r["open"].iloc[0]
        row["rth_high"] = r["high"].max()
        row["rth_low"] = r["low"].min()
        row["rth_close"] = r["close"].iloc[-1]
        row["rth_last_hm"] = rhm[-1]
        ib = r[rhm <= 1030]
        row["ib_high"] = ib["high"].max() if (rhm <= 1030).any() and 1030 in set(rhm) else np.nan
        row["ib_low"] = ib["low"].min() if (rhm <= 1030).any() and 1030 in set(rhm) else np.nan
        v = r["volume"].to_numpy(dtype=float)
        c = r["close"].to_numpy(dtype=float)
        rth_arrays[sd] = {
            "o": r["open"].to_numpy(dtype=float), "h": r["high"].to_numpy(dtype=float),
            "l": r["low"].to_numpy(dtype=float), "c": c, "hm": rhm,
            "vwap": np.cumsum(c * v) / np.maximum(np.cumsum(v), 1e-9)}
    else:
        row.update({"rth_first_hm": np.nan, "open0930": np.nan, "rth_high": np.nan,
                    "rth_low": np.nan, "rth_close": np.nan, "rth_last_hm": np.nan,
                    "ib_high": np.nan, "ib_low": np.nan})
    b45 = g[hm == 1645]
    if len(b45):
        bar1645[sd] = (b45["open"].iloc[0], b45["high"].iloc[0], b45["low"].iloc[0])
    sess_rows.append(row)

S = pd.DataFrame(sess_rows).sort_values("sd").reset_index(drop=True)
cp = S["s_close"].shift(1)
tr = np.maximum(S["s_high"] - S["s_low"],
                np.maximum((S["s_high"] - cp).abs(), (S["s_low"] - cp).abs()))
S["atr14"] = tr.rolling(14).mean().shift(1)           # prior 14 sessions only (causal)
S["pdh"] = S["rth_high"].shift(1)
S["pdl"] = S["rth_low"].shift(1)
S["pclose"] = S["rth_close"].shift(1)
S.to_csv(f"{OUT}/session_table.csv", index=False)
print(f"session table: {len(S)} rows, ATR valid {S['atr14'].notna().sum()}, "
      f"rth_first==933: {(S['rth_first_hm'] == 933).sum()}")

# ---------------------------------------------------------------- statistics
def nw_stats(x, sess_dates, lag=NW_LAG):
    """t-stat of the mean of per-event x, SE clustered by session with NW(lag)
    Bartlett weights across chronologically ordered event-sessions."""
    x = np.asarray(x, dtype=float); n = len(x)
    out = {"n": n, "mean": np.nan, "total": np.nan,
           "t_nw": np.nan, "t_cluster": np.nan, "t_iid": np.nan, "n_sessions": 0}
    if n == 0:
        return out
    xbar = x.mean()
    out["mean"] = xbar; out["total"] = x.sum()
    if n < 3:
        return out
    df = pd.DataFrame({"x": x - xbar, "s": pd.to_datetime(list(sess_dates))})
    z = df.groupby("s", sort=True)["x"].sum().to_numpy()
    out["n_sessions"] = len(z)
    S0 = float((z ** 2).sum())
    Snw = S0
    L = min(lag, len(z) - 1)
    for l in range(1, L + 1):
        w = 1.0 - l / (lag + 1.0)
        Snw += 2.0 * w * float((z[l:] * z[:-l]).sum())
    if Snw > 0:
        out["t_nw"] = xbar / (np.sqrt(Snw) / n)
    if S0 > 0:
        out["t_cluster"] = xbar / (np.sqrt(S0) / n)
    sd = x.std(ddof=1)
    if sd > 0:
        out["t_iid"] = xbar / (sd / np.sqrt(n))
    return out


def split_stats(ev, col="net"):
    h1 = ev[ev["sd"] <= SPLIT]; h2 = ev[ev["sd"] > SPLIT]
    a = nw_stats(h1[col], h1["sd"]); b = nw_stats(h2[col], h2["sd"])
    return a, b

# ================================================================= ENGINE 368
LEVELS = [("PDH", "pdh", +1, 933), ("PDL", "pdl", -1, 933),
          ("ONH", "on_high", +1, 933), ("ONL", "on_low", -1, 933),
          ("IBH", "ib_high", +1, 1033), ("IBL", "ib_low", -1, 1033)]

def scan_episode(a, L, upper, min_stamp, conf_bars, pen_lim):
    """First qualifying failed-break episode for one level in one session.
    Returns (k, j, sweep_ext) or None. a = rth arrays dict."""
    hm, h, l, c = a["hm"], a["h"], a["l"], a["c"]
    n = len(hm)
    in_ep = False; k = -1; ext = np.nan
    for i in range(n):
        if hm[i] < min_stamp:
            continue
        if not in_ep:
            if hm[i] > 1530:
                return None                      # penetration must start by 15:30
            pen = (h[i] > L) if upper else (l[i] < L)
            if pen:
                in_ep = True; k = i; ext = h[i] if upper else l[i]
        else:
            ext = max(ext, h[i]) if upper else min(ext, l[i])
        if in_ep:
            back = (c[i] < L) if upper else (c[i] > L)
            if back:
                depth = (ext - L) if upper else (L - ext)
                if (i - k) <= conf_bars - 1 and 0 < depth <= pen_lim:
                    return (k, i, ext)
                in_ep = False                    # failed episode (late/deep); keep scanning
    return None


def sim_e368(pen_mult, conf_bars):
    events = []
    for r in S.itertuples():
        if not np.isfinite(r.atr14) or r.rth_first_hm != 933:
            continue
        a = rth_arrays.get(r.sd)
        if a is None:
            continue
        pen_lim = pen_mult * r.atr14
        for name, col, side_up, min_stamp in LEVELS:
            L = getattr(r, col)
            if not np.isfinite(L):
                continue
            upper = side_up > 0
            ep = scan_episode(a, L, upper, min_stamp, conf_bars, pen_lim)
            if ep is None:
                continue
            k, j, ext = ep
            e = j + 1
            n = len(a["hm"])
            if e >= n:
                continue                          # confirmation on last RTH bar; no entry bar
            o, h, l, c, vw, hm = a["o"], a["h"], a["l"], a["c"], a["vwap"], a["hm"]
            d = -1 if upper else +1               # fade side: short upper sweep, long lower sweep
            entry_px = _fill(o[e], h[e], l[e], d)
            stop_px = ext + 2 * TICK if upper else ext - 2 * TICK
            deadline = min(e + 19, n - 1)         # 60-min time stop, capped at RTH end (1600 bar)
            exit_px = np.nan; exit_i = deadline; reason = "time"
            for i2 in range(e, deadline + 1):
                if d < 0:                          # short
                    if h[i2] >= stop_px:           # stop first (conservative)
                        base = o[i2] if o[i2] >= stop_px else stop_px
                        exit_px = min(base + TICK, h[i2]); exit_i = i2; reason = "stop"; break
                    if l[i2] <= vw[i2]:            # VWAP touch
                        base = o[i2] if o[i2] <= vw[i2] else vw[i2]
                        exit_px = min(base + TICK, h[i2]); exit_i = i2; reason = "vwap"; break
                else:                              # long
                    if l[i2] <= stop_px:
                        base = o[i2] if o[i2] <= stop_px else stop_px
                        exit_px = max(base - TICK, l[i2]); exit_i = i2; reason = "stop"; break
                    if h[i2] >= vw[i2]:
                        base = o[i2] if o[i2] >= vw[i2] else vw[i2]
                        exit_px = max(base - TICK, l[i2]); exit_i = i2; reason = "vwap"; break
            if not np.isfinite(exit_px):           # time/RTH-end exit at bar close
                i2 = deadline
                exit_px = (min(c[i2] + TICK, h[i2]) if d < 0 else max(c[i2] - TICK, l[i2]))
                reason = "time" if deadline == e + 19 else "rth_end"
                exit_i = i2
            pts = d * (exit_px - entry_px)
            net = pts * PV - COMM_RT
            events.append({
                "sd": r.sd, "level": name, "dir": d, "level_px": L,
                "k_hm": hm[k], "j_hm": hm[j], "entry_hm": hm[e], "exit_hm": hm[exit_i],
                "entry_i": e, "exit_i": exit_i, "sweep_ext": ext,
                "depth_pts": (ext - L) if upper else (L - ext), "atr14": r.atr14,
                "entry_px": entry_px, "exit_px": exit_px, "exit_reason": reason,
                "pts": pts, "net": net, "hold_bars": exit_i - e + 1,
                "vwap_wrong_side": bool((vw[j] > c[j]) if upper else (vw[j] < c[j])),
                "open_outside": bool((r.open0930 > L) if upper else (r.open0930 < L))})
    ev = pd.DataFrame(events)
    if len(ev):
        ev["simultaneous"] = ev.duplicated(subset=["sd", "entry_i"], keep=False)
        ev["dup_drop"] = ev.duplicated(subset=["sd", "entry_i"], keep="first")
        ov = np.zeros(len(ev), dtype=bool)
        for sd, g in ev.groupby("sd"):
            idx = g.index.to_numpy()
            for ii in range(len(idx)):
                for jj in range(len(idx)):
                    if ii == jj:
                        continue
                    a1, b1 = g.loc[idx[ii], ["entry_i", "exit_i"]]
                    a2, b2 = g.loc[idx[jj], ["entry_i", "exit_i"]]
                    if a1 <= b2 and a2 <= b1:
                        ov[ev.index.get_loc(idx[ii])] = True
        ev["interval_overlap"] = ov
    return ev


print("\n=== e368 failed range-break fade (center 0.25 x ATR, 15 min) ===")
e368 = sim_e368(0.25, 5)
e368.to_csv(f"{OUT}/e368_events.csv", index=False)
rows = []
p = nw_stats(e368["net"], e368["sd"]); p.update({"cell": "pooled_all"})
rows.append(p)
dd = e368[~e368["dup_drop"]]
p = nw_stats(dd["net"], dd["sd"]); p.update({"cell": "pooled_dedup_simultaneous"})
rows.append(p)
h1, h2 = split_stats(e368)
h1.update({"cell": "split_2022_24"}); h2.update({"cell": "split_2025_26"})
rows += [h1, h2]
for lev, g in e368.groupby("level"):
    q = nw_stats(g["net"], g["sd"]); q.update({"cell": f"level_{lev}"})
    rows.append(q)
for reas, g in e368.groupby("exit_reason"):
    q = nw_stats(g["net"], g["sd"]); q.update({"cell": f"exit_{reas}"})
    rows.append(q)
q = nw_stats(e368.loc[~e368["vwap_wrong_side"], "net"], e368.loc[~e368["vwap_wrong_side"], "sd"])
q.update({"cell": "excl_vwap_wrong_side"}); rows.append(q)
e368_summary = pd.DataFrame(rows)
e368_summary["frac_of_pooled"] = e368_summary["n"] / max(len(e368), 1)
e368_summary.to_csv(f"{OUT}/e368_summary.csv", index=False)
print(e368_summary[["cell", "n", "mean", "total", "t_nw", "t_cluster", "t_iid"]].round(3).to_string())

print("\n--- e368 plateau 3x3 (pen x conf) ---")
prows = []
for pm in (0.15, 0.25, 0.35):
    for cb, cmin in ((3, 9), (5, 15), (7, 21)):
        evg = sim_e368(pm, cb)
        st = nw_stats(evg["net"], evg["sd"])
        prows.append({"pen_mult": pm, "conf_min": cmin, "n": st["n"],
                      "mean_net": st["mean"], "t_nw": st["t_nw"]})
        print(f"pen {pm:.2f} conf {cmin:2d}min  N {st['n']:4d}  mean {st['mean']:8.2f}  t_nw {st['t_nw']:6.2f}")
e368_plateau = pd.DataFrame(prows)
e368_plateau.to_csv(f"{OUT}/e368_plateau.csv", index=False)

# ================================================================= ENGINE 369
def sim_e369(gap_mult):
    events = []
    for r in S.itertuples():
        if (not np.isfinite(r.atr14) or r.rth_first_hm != 933
                or not np.isfinite(r.pclose) or not np.isfinite(r.pdh)):
            continue
        a = rth_arrays.get(r.sd)
        if a is None or len(a["hm"]) < 2 or a["hm"][1] != 936:
            continue
        gap = r.open0930 - r.pclose
        if gap == 0 or abs(gap) >= gap_mult * r.atr14:
            continue
        if not (r.pdl < r.open0930 < r.pdh):
            continue
        d = -1 if gap > 0 else +1                 # fade toward prior close
        o, h, l, c, hm = a["o"], a["h"], a["l"], a["c"], a["hm"]
        pc = r.pclose
        entry_px = _fill(o[1], h[1], l[1], d)
        stop_i = int(np.where(hm <= 1130)[0].max())
        exit_px = np.nan; exit_i = stop_i; filled = False; tfill = np.nan
        for i2 in range(1, stop_i + 1):
            if d < 0 and l[i2] <= pc:
                base = o[i2] if o[i2] <= pc else pc
                exit_px = min(base + TICK, h[i2]); exit_i = i2; filled = True
            elif d > 0 and h[i2] >= pc:
                base = o[i2] if o[i2] >= pc else pc
                exit_px = max(base - TICK, l[i2]); exit_i = i2; filled = True
            if filled:
                tfill = (hm[i2] // 100) * 60 + hm[i2] % 100 - (9 * 60 + 33)
                break
        if not filled:
            i2 = stop_i
            exit_px = min(c[i2] + TICK, h[i2]) if d < 0 else max(c[i2] - TICK, l[i2])
        pts = d * (exit_px - entry_px)
        events.append({"sd": r.sd, "gap_pts": gap, "atr14": r.atr14, "dir": d,
                       "entry_px": entry_px, "exit_px": exit_px, "prior_close": pc,
                       "filled": filled, "t_fill_min": tfill, "exit_hm": hm[exit_i],
                       "pts": pts, "net": pts * PV - COMM_RT})
    return pd.DataFrame(events)


print("\n=== e369 small-gap fade (center 0.5 x ATR) ===")
e369 = sim_e369(0.5)
e369.to_csv(f"{OUT}/e369_events.csv", index=False)
rows = []
p = nw_stats(e369["net"], e369["sd"]); p.update({"cell": "pooled"})
rows.append(p)
h1, h2 = split_stats(e369)
h1.update({"cell": "split_2022_24"}); h2.update({"cell": "split_2025_26"})
rows += [h1, h2]
for f, g in e369.groupby("filled"):
    q = nw_stats(g["net"], g["sd"]); q.update({"cell": f"filled_{f}"})
    rows.append(q)
e369_summary = pd.DataFrame(rows)
e369_summary["fill_rate"] = e369["filled"].mean()
e369_summary["median_t_fill_min"] = e369.loc[e369["filled"], "t_fill_min"].median()
e369_summary.to_csv(f"{OUT}/e369_summary.csv", index=False)
print(e369_summary[["cell", "n", "mean", "total", "t_nw", "t_cluster"]].round(3).to_string())
print(f"fill rate {e369['filled'].mean():.3f}  median t_fill {e369.loc[e369['filled'], 't_fill_min'].median():.0f} min")

prows = []
for gm in (0.3, 0.5, 0.7):
    evg = sim_e369(gm)
    st = nw_stats(evg["net"], evg["sd"])
    prows.append({"gap_mult": gm, "n": st["n"], "mean_net": st["mean"], "t_nw": st["t_nw"],
                  "fill_rate": evg["filled"].mean() if len(evg) else np.nan})
    print(f"gap {gm:.1f}xATR  N {st['n']:4d}  mean {st['mean']:8.2f}  t_nw {st['t_nw']:6.2f}")
e369_plateau = pd.DataFrame(prows)
e369_plateau.to_csv(f"{OUT}/e369_plateau.csv", index=False)

# ================================================================= ENGINE 370
print("\n=== e370 overnight drift cheap kill ===")
trades370 = []
for i in range(len(S) - 1):
    r = S.iloc[i]; nx = S.iloc[i + 1]
    if r.sd not in bar1645:
        continue
    a2 = rth_arrays.get(nx.sd)
    if a2 is None or len(a2["hm"]) < 2 or a2["hm"][0] != 933 or a2["hm"][1] != 936:
        continue
    if not (np.isfinite(r.rth_close) and np.isfinite(r.open0930)):
        continue
    o45, h45, l45 = bar1645[r.sd]
    entry_px = _fill(o45, h45, l45, +1)                       # long at 16:42 open
    exit_px = _fill(a2["o"][1], a2["h"][1], a2["l"][1], -1)   # exit next 09:33 open
    net = (exit_px - entry_px) * PV - COMM_RT
    trades370.append({"sd_entry": r.sd, "sd": nx.sd, "down_day": bool(r.rth_close < r.open0930),
                      "entry_px": entry_px, "exit_px": exit_px, "net": net})
t370 = pd.DataFrame(trades370)
t370.to_csv(f"{OUT}/e370_trades.csv", index=False)
rows = []
cond = t370[t370["down_day"]]
for nm, g in (("conditional_down_day", cond), ("unconditional", t370)):
    p = nw_stats(g["net"], g["sd"]); p.update({"cell": nm})
    rows.append(p)
    a, b = split_stats(g)
    a.update({"cell": f"{nm}_2022_24"}); b.update({"cell": f"{nm}_2025_26"})
    rows += [a, b]
e370_summary = pd.DataFrame(rows)
e370_summary.to_csv(f"{OUT}/e370_summary.csv", index=False)
print(e370_summary[["cell", "n", "mean", "total", "t_nw", "t_cluster"]].round(3).to_string())

# ============================================================ COMPLEMENTARITY
print("\n=== complementarity vs DAYONLY_DUAL6040 (60_40) ===")
rc = pd.read_csv("runs/SMV2H_ONECONTRACT/out/rerank_curves.csv")
rc["sess"] = pd.to_datetime(rc["sess"])
rc = rc[rc["sess"] <= DEV_END].set_index("sess")
champ = rc["60_40"]
nbot = max(1, int(np.floor(len(champ) * 0.10)))
bot_idx = champ.nsmallest(nbot).index
lose_idx = champ[champ < 0].index

def eng_daily(ev, col="net"):
    d = ev.groupby("sd")[col].sum()
    return d.reindex(champ.index, fill_value=0.0)

crows = []
for nm, ev in (("e368_center", e368), ("e369_center", e369),
               ("e370_conditional", cond), ("e370_unconditional", t370)):
    ed = eng_daily(ev)
    nz = int((ed != 0).sum())
    corr_all = float(ed.corr(champ)) if nz > 2 else np.nan
    el = ed.loc[lose_idx]; cl = champ.loc[lose_idx]
    corr_lose = float(el.corr(cl)) if (el != 0).sum() > 2 else np.nan
    crows.append({"engine": nm, "n_days": len(champ), "n_event_days": nz,
                  "corr_all_days": corr_all, "corr_champ_losing_days": corr_lose,
                  "n_losing_days": len(lose_idx), "n_bottom_decile_days": nbot,
                  "mean_pnl_bottom_decile": float(ed.loc[bot_idx].mean()),
                  "engine_total_net": float(ed.sum()),
                  "champ_mean_bottom_decile": float(champ.loc[bot_idx].mean())})
comp = pd.DataFrame(crows)
comp.to_csv(f"{OUT}/complementarity.csv", index=False)
print(comp.round(3).to_string())

# ---------------------------------------------------------------- gate audit
def sign_ok(v):
    return np.sign(v) if np.isfinite(v) else 0

g368_pool = e368_summary[e368_summary["cell"] == "pooled_all"].iloc[0]
g368_h1 = e368_summary[e368_summary["cell"] == "split_2022_24"].iloc[0]
g368_h2 = e368_summary[e368_summary["cell"] == "split_2025_26"].iloc[0]
plateau_signs_368 = set(np.sign(e368_plateau["mean_net"]))
g369_pool = e369_summary[e369_summary["cell"] == "pooled"].iloc[0]
g369_h1 = e369_summary[e369_summary["cell"] == "split_2022_24"].iloc[0]
g369_h2 = e369_summary[e369_summary["cell"] == "split_2025_26"].iloc[0]
plateau_signs_369 = set(np.sign(e369_plateau["mean_net"]))

gates = pd.DataFrame([
    {"engine": "e368", "gate": "t_nw>=2", "value": g368_pool["t_nw"], "pass": bool(g368_pool["t_nw"] >= 2)},
    {"engine": "e368", "gate": "N>=300", "value": g368_pool["n"], "pass": bool(g368_pool["n"] >= 300)},
    {"engine": "e368", "gate": "split_sign_stable",
     "value": f"{g368_h1['mean']:.2f}|{g368_h2['mean']:.2f}",
     "pass": bool(sign_ok(g368_h1["mean"]) == sign_ok(g368_h2["mean"]) != 0)},
    {"engine": "e368", "gate": "plateau_all_same_sign", "value": str(sorted(plateau_signs_368)),
     "pass": bool(len(plateau_signs_368) == 1)},
    {"engine": "e369", "gate": "t_nw>=2", "value": g369_pool["t_nw"], "pass": bool(g369_pool["t_nw"] >= 2)},
    {"engine": "e369", "gate": "N>=250", "value": g369_pool["n"], "pass": bool(g369_pool["n"] >= 250)},
    {"engine": "e369", "gate": "split_sign_stable",
     "value": f"{g369_h1['mean']:.2f}|{g369_h2['mean']:.2f}",
     "pass": bool(sign_ok(g369_h1["mean"]) == sign_ok(g369_h2["mean"]) != 0)},
    {"engine": "e369", "gate": "plateau_all_same_sign", "value": str(sorted(plateau_signs_369)),
     "pass": bool(len(plateau_signs_369) == 1)},
])
gates.to_csv(f"{OUT}/gates.csv", index=False)
print("\n--- gates ---")
print(gates.to_string())
print("\ndone.")
