"""SMV2P_ENGINE3_S2 — R1 FAMILY TEST, seq 377-379 (Engine #3 slate 2, DR pass A H2/H9/H12).

e377  value-area rotation      (open outside prior-RTH VA + 30min acceptance inside -> rotate to far edge)
e378  multi-day balance false-break (RTH close beyond 20-sess close extreme, reclaimed <=2 sess -> to range mid, hold <=3 sess)
e379  month-end flow tilt      (last 2 trading days, fade month-to-date sign, RTH-only day trades)

All economics NET of $4.36/RT + 1 tick/side slippage (NQ, $20/pt, tick 0.25).
Dev window: sessions <= 2026-05-31. No data >= 2026-08-01 is ever used.
Old-regime check (e379 only): SM06 hist substrate closes 2006-2021 (committed artifact).

Frozen conventions (disclosed in REPORT.md; identical to SMV2K slate 1 where shared):
- Bars: END-stamped 3m via sm01_solarsim.load_bars_3m (same substrate as every SMV2 run).
- "HH:MM open" = open at wall time HH:MM = open of the bar STAMPED HH:MM+3 (SMV2K anchor:
  "09:33 open" = open of the 0936-stamped bar). "15:57 exit" = open of the 1600-stamped bar.
- RTH = stamps 0933..1600 (0933 bar's open is the 09:30 open).
- e377 VA algorithm (EXACT): histogram prior-session RTH 3m closes x volume in 25c bins
  (NQ trades on a 25c grid so each bin is one price level, k = round(close/0.25)); seed bin =
  floor(prior RTH VWAP / 0.25); grow the contiguous band one bin at a time toward the adjacent
  side with the LARGER volume (tie -> up; exhausted side -> other side) until cumulative
  volume >= coverage x total RTH volume. VAL/VAH = lowest/highest included level.
  VWAP = sum(close*vol)/sum(vol) over prior RTH bars.
- e377 event: 09:30 RTH open (open of 0933 bar) strictly outside [VAL,VAH]; acceptance = first
  run of `accept` CONSECUTIVE RTH closes inside [VAL,VAH]; entry at next 3m open; target =
  far edge (short->VAL if open above, long->VAH if open below); exit at target touch
  (level-touch fill: base = open if open beyond level else level, +/-1 tick capped by bar
  range — SMV2K e368 semantics) or time-stop at the close of the last RTH bar stamped <=1554
  (wall 15:54), fill close +/-1 tick capped. Entry bar must be stamped <=1554 else event void.
  One event per session (first acceptance).
- e378 event: session table of sessions with valid RTH close; break day s: RTH close > max
  (resp. < min) of the prior `lb` sessions' RTH closes (rolling, shift(1)); range frozen at s:
  [rng_lo, rng_hi] = that rolling min/max; reclaim day r in {s+1, s+2}: rng_lo < RTH close <
  rng_hi (strict). Entry next session (r+1) at 09:33 open (0936 bar, _fill). Direction: short
  after failed up-break, long after failed down-break. Target = (rng_lo+rng_hi)/2. Exit at
  target touch on ANY bar incl. overnight (level-touch fill) or at the SESSION close (last bar
  ~17:00, at_close fill) of the 3rd session counting entry session as 1. ONE position at a
  time: signals whose entry bar falls at or before the open trade's exit bar are dropped
  (counted). Signals whose 3-session window would extend past the dev end are dropped
  (right-censoring, counted). If several break episodes are active when a reclaim close
  occurs, the MOST RECENT break's range is used and all episodes clear on entry.
- e379 event: for each calendar month with >=3 dev sessions AND a prior-month final session
  close available: D_n, D_{n-1} = last two sessions of the month; MTD reference = SESSION
  close (last bar of session) of D_{n-2} minus prior-month final session close (POINT diff);
  sign = -sign(MTD), computed ONCE per month, used for both day-events. Each day-event:
  enter 09:33 open (0936 bar), exit 15:57 (1600 bar OPEN, _fill); on early-close sessions
  with no 1600 bar, forced exit at the last RTH bar close (at_close fill, counted+flagged).
  Sessions with no 0936 bar are skipped (counted).
- e379 hist direction check (GROSS, no execution): SM06 vote_state_3m_hist closes; per month
  2006-02..2021-12, signed 2-day window = sign x (close(D_n) - close(D_{n-2})) in points,
  sign = -sign(close(D_{n-2}) - prior-month final close). Session closes = is_last_of_sess.
  Point diffs (not ratios) — exact under additive back-adjustment.
- NW t-stat: mean per-event net, SE clustered by session with Bartlett/NW lag 5 across
  event-session order (SMV2K convention); t_cluster (lag 0) and t_iid also reported.
- House bootstrap: moving block = 5 over chronological events, B = 10000, seed = 20260808;
  p_boot = fraction of resampled means <= 0.
- Joint-loss weeks: weekly (W-FRI on sess date) sums of the champion's two alpha legs —
  PRIMARY: Solar_DUAL = DUAL column of runs/SMV2H_ONECONTRACT/out/rerank_curves.csv;
  BMOM = SMV2B ledger_E2 net_c1_ticks x $5 by session (verified identical to BM_E2 column,
  max abs diff 0.0). SECONDARY (robustness): champion twin daily (SMV2M twin_daily.csv,
  dev-clipped) AND BMOM. Joint-loss week = both legs' weekly sums < 0.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "src/analytics")
from sm01_solarsim import TICK, _fill, load_bars_3m

RUN = "runs/SMV2P_ENGINE3_S2"
OUT = f"{RUN}/out"
os.makedirs(OUT, exist_ok=True)

PV = 20.0
COMM_RT = 4.36
DEV_END = pd.Timestamp("2026-05-31")
NW_LAG = 5
SPLIT = pd.Timestamp("2024-12-31")
SEED = 20260808
B_BOOT = 10000
BLOCK = 5

# ---------------------------------------------------------------- substrate
print("loading substrate ...")
bars = load_bars_3m()
bars["sd"] = pd.to_datetime(bars["sess_date"])
assert bars["sd"].max() < pd.Timestamp("2026-08-01"), "VIRGIN data in file?!"
bars = bars[bars["sd"] <= DEV_END].reset_index(drop=True)
t = pd.to_datetime(bars["time"])
bars["hm"] = t.dt.hour * 100 + t.dt.minute
GO = bars["open"].to_numpy(float)
GH = bars["high"].to_numpy(float)
GL = bars["low"].to_numpy(float)
GC = bars["close"].to_numpy(float)
GHM = bars["hm"].to_numpy()
print(f"dev bars {len(bars)}  sessions {bars['sd'].nunique()}  "
      f"range {bars['sd'].min().date()} .. {bars['sd'].max().date()}")

# per-session structures
sess_rows, rth_arrays, sess_span, bar0936 = [], {}, {}, {}
for sd, g in bars.groupby("sd", sort=True):
    g = g.sort_values("time")
    hm = g["hm"].to_numpy()
    gi = g.index.to_numpy()
    sess_span[sd] = (gi[0], gi[-1])
    row = {"sd": sd, "sess_close": g["close"].iloc[-1]}
    r = g[(hm >= 933) & (hm <= 1600)]
    if len(r):
        rhm = r["hm"].to_numpy()
        row["rth_first_hm"] = rhm[0]
        row["open0930"] = r["open"].iloc[0]
        row["rth_close"] = r["close"].iloc[-1]
        row["rth_last_hm"] = rhm[-1]
        rth_arrays[sd] = {
            "o": r["open"].to_numpy(float), "h": r["high"].to_numpy(float),
            "l": r["low"].to_numpy(float), "c": r["close"].to_numpy(float),
            "v": r["volume"].to_numpy(float), "hm": rhm, "gi": r.index.to_numpy()}
    else:
        row.update({"rth_first_hm": np.nan, "open0930": np.nan,
                    "rth_close": np.nan, "rth_last_hm": np.nan})
    b36 = g[hm == 936]
    if len(b36):
        bar0936[sd] = int(b36.index[0])
    sess_rows.append(row)
S = pd.DataFrame(sess_rows).sort_values("sd").reset_index(drop=True)
ALL_SD = S["sd"].tolist()
SD_POS = {sd: i for i, sd in enumerate(ALL_SD)}
SESS_CLOSE = dict(zip(S["sd"], S["sess_close"]))
print(f"sessions {len(S)}, rth_first==933: {(S['rth_first_hm'] == 933).sum()}, "
      f"with 0936 bar: {len(bar0936)}")

# ---------------------------------------------------------------- statistics
def nw_stats(x, sess_dates, lag=NW_LAG):
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
    sd_ = x.std(ddof=1)
    if sd_ > 0:
        out["t_iid"] = xbar / (sd_ / np.sqrt(n))
    return out


def split_stats(ev, col="net", dcol="sd"):
    h1 = ev[ev[dcol] <= SPLIT]; h2 = ev[ev[dcol] > SPLIT]
    return nw_stats(h1[col], h1[dcol]), nw_stats(h2[col], h2[dcol])


def block_boot_p(x, block=BLOCK, B=B_BOOT, seed=SEED):
    """Moving-block bootstrap of the mean over the chronological event series.
    Returns fraction of resampled means <= 0."""
    x = np.asarray(x, dtype=float); n = len(x)
    if n < block + 1:
        return np.nan
    rng = np.random.default_rng(seed)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n - block + 1, size=(B, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(B, -1)[:, :n]
    means = x[idx].mean(axis=1)
    return float((means <= 0).mean())


def touch_exit_short(o, h, l, L):
    """Buy-to-cover at level L touched this bar (low <= L). SMV2K e368 semantics."""
    base = o if o <= L else L
    return min(base + TICK, h)


def touch_exit_long(o, h, l, L):
    base = o if o >= L else L
    return max(base - TICK, l)


# ================================================================= ENGINE 377
def value_area(a, coverage):
    """(val, vah, vwap, total_vol) from one session's RTH arrays. 25c bins on the
    25c price grid; grow band around the VWAP bin toward the larger-volume side."""
    c, v = a["c"], a["v"]
    tot = v.sum()
    if tot <= 0:
        return None
    vwap = float((c * v).sum() / tot)
    k = np.round(c / TICK).astype(np.int64)
    hist = {}
    for ki, vi in zip(k, v):
        hist[ki] = hist.get(ki, 0.0) + vi
    kmin, kmax = int(k.min()), int(k.max())
    k0 = int(np.floor(vwap / TICK))
    k0 = min(max(k0, kmin), kmax)
    lo = hi = k0
    cum = hist.get(k0, 0.0)
    target = coverage * tot
    while cum < target and (lo > kmin or hi < kmax):
        vu = hist.get(hi + 1, 0.0) if hi < kmax else -1.0
        vd = hist.get(lo - 1, 0.0) if lo > kmin else -1.0
        if vu >= vd:          # tie -> up; exhausted side has -1
            hi += 1; cum += max(vu, 0.0)
        else:
            lo -= 1; cum += max(vd, 0.0)
    return lo * TICK, hi * TICK, vwap, tot


def sim_e377(coverage, accept_bars):
    events = []
    n_open_outside = 0
    for i in range(1, len(S)):
        r = S.iloc[i]; pr = S.iloc[i - 1]
        if r.rth_first_hm != 933:
            continue
        ap = rth_arrays.get(pr.sd)
        if ap is None:
            continue
        va = value_area(ap, coverage)
        if va is None:
            continue
        val, vah, vwap_p, _ = va
        a = rth_arrays[r.sd]
        o, h, l, c, hm = a["o"], a["h"], a["l"], a["c"], a["hm"]
        op = o[0]
        if val <= op <= vah:
            continue                          # open inside VA -> no event
        n_open_outside += 1
        d = -1 if op > vah else +1            # short from above, long from below
        tgt = val if d < 0 else vah           # opposite (far) edge
        nb = len(hm)
        run = 0; entry_i = -1
        for j in range(nb):
            run = run + 1 if (val <= c[j] <= vah) else 0
            if run >= accept_bars:
                if j + 1 < nb and hm[j + 1] <= 1554:
                    entry_i = j + 1
                break                          # first acceptance only (event void if late)
        if entry_i < 0:
            continue
        dl_cand = np.where(hm <= 1554)[0]
        deadline = int(dl_cand.max())
        entry_px = _fill(o[entry_i], h[entry_i], l[entry_i], d)
        exit_px = np.nan; exit_i = deadline; reason = "time_1554"
        for i2 in range(entry_i, deadline + 1):
            if d < 0 and l[i2] <= tgt:
                exit_px = touch_exit_short(o[i2], h[i2], l[i2], tgt)
                exit_i = i2; reason = "target"; break
            if d > 0 and h[i2] >= tgt:
                exit_px = touch_exit_long(o[i2], h[i2], l[i2], tgt)
                exit_i = i2; reason = "target"; break
        if not np.isfinite(exit_px):
            i2 = deadline
            exit_px = (min(c[i2] + TICK, h[i2]) if d < 0
                       else max(c[i2] - TICK, l[i2]))
        pts = d * (exit_px - entry_px)
        events.append({
            "sd": r.sd, "dir": d, "val": val, "vah": vah, "vwap_prior": vwap_p,
            "open0930": op, "va_width": vah - val,
            "accept_hm": hm[entry_i - 1], "entry_hm": hm[entry_i],
            "exit_hm": hm[exit_i], "entry_px": entry_px, "exit_px": exit_px,
            "exit_reason": reason, "pts": pts, "net": pts * PV - COMM_RT,
            "hold_bars": exit_i - entry_i + 1})
    ev = pd.DataFrame(events)
    return ev, n_open_outside


print("\n=== e377 value-area rotation (center 70% / 30min) ===")
e377, n_out = sim_e377(0.70, 10)
e377.to_csv(f"{OUT}/e377_events.csv", index=False)
rows = []
p = nw_stats(e377["net"], e377["sd"]); p.update({"cell": "pooled"})
p["p_boot"] = block_boot_p(e377["net"])
rows.append(p)
h1, h2 = split_stats(e377)
h1.update({"cell": "split_2022_24"}); h2.update({"cell": "split_2025_26"})
rows += [h1, h2]
for dd, g in e377.groupby("dir"):
    q = nw_stats(g["net"], g["sd"]); q.update({"cell": f"dir_{'short' if dd < 0 else 'long'}"})
    rows.append(q)
for reas, g in e377.groupby("exit_reason"):
    q = nw_stats(g["net"], g["sd"]); q.update({"cell": f"exit_{reas}"})
    rows.append(q)
e377_summary = pd.DataFrame(rows)
e377_summary["n_open_outside_sessions"] = n_out
e377_summary.to_csv(f"{OUT}/e377_summary.csv", index=False)
print(e377_summary[["cell", "n", "mean", "total", "t_nw", "t_cluster", "t_iid"]].round(3).to_string())
print(f"open-outside sessions {n_out}; events {len(e377)}; p_boot {p['p_boot']}")

print("\n--- e377 plateau 3x3 (coverage x acceptance) ---")
prows = []
for cov in (0.60, 0.70, 0.80):
    for ab, mins in ((7, 21), (10, 30), (13, 39)):
        evg, _ = sim_e377(cov, ab)
        st = nw_stats(evg["net"], evg["sd"])
        prows.append({"coverage": cov, "accept_min": mins, "n": st["n"],
                      "mean_net": st["mean"], "t_nw": st["t_nw"]})
        print(f"cov {cov:.2f} acc {mins:2d}min  N {st['n']:4d}  mean {st['mean']:8.2f}  t_nw {st['t_nw']:6.2f}")
e377_plateau = pd.DataFrame(prows)
e377_plateau.to_csv(f"{OUT}/e377_plateau.csv", index=False)

# ================================================================= ENGINE 378
S378 = S[np.isfinite(S["rth_close"])].reset_index(drop=True)


def sim_e378(lb):
    rc = S378["rth_close"]
    roll_hi = rc.rolling(lb).max().shift(1)
    roll_lo = rc.rolling(lb).min().shift(1)
    sds = S378["sd"].tolist()
    n = len(S378)
    events = []
    dropped_overlap = dropped_censor = dropped_nobar = 0
    episodes = []            # (idx_break, dir, rng_lo, rng_hi), active idx+1..idx+2
    busy_until = -1          # global bar index of the open trade's exit
    for i in range(n):
        cl = rc.iloc[i]
        hi_i, lo_i = roll_hi.iloc[i], roll_lo.iloc[i]
        if not (np.isfinite(hi_i) and np.isfinite(lo_i)):
            continue
        # 1) reclaim check against active episodes (most recent first)
        trig = None
        for ep in sorted(episodes, key=lambda e: -e[0]):
            bidx, bdir, rlo, rhi = ep
            if i - bidx <= 2 and rlo < cl < rhi:
                trig = ep
                break
        episodes = [ep for ep in episodes if i - ep[0] < 2]   # expire
        if trig is not None:
            episodes = []                                      # clear on signal
            bidx, bdir, rlo, rhi = trig
            d = -1 if bdir > 0 else +1
            tgt = 0.5 * (rlo + rhi)
            sd_r = sds[i]
            p_r = SD_POS[sd_r]
            if p_r + 1 >= len(ALL_SD):
                dropped_censor += 1
            else:
                sd_e = ALL_SD[p_r + 1]
                if p_r + 3 >= len(ALL_SD):
                    dropped_censor += 1
                elif sd_e not in bar0936:
                    dropped_nobar += 1
                else:
                    eidx = bar0936[sd_e]
                    if eidx <= busy_until:
                        dropped_overlap += 1
                    else:
                        sd_dl = ALL_SD[p_r + 3]        # 3rd held session
                        dl_idx = sess_span[sd_dl][1]   # its last bar (session close)
                        entry_px = _fill(GO[eidx], GH[eidx], GL[eidx], d)
                        exit_px = np.nan; exit_i = dl_idx; reason = "time_3sess"
                        for k in range(eidx, dl_idx + 1):
                            if d < 0 and GL[k] <= tgt:
                                exit_px = touch_exit_short(GO[k], GH[k], GL[k], tgt)
                                exit_i = k; reason = "target"; break
                            if d > 0 and GH[k] >= tgt:
                                exit_px = touch_exit_long(GO[k], GH[k], GL[k], tgt)
                                exit_i = k; reason = "target"; break
                        if not np.isfinite(exit_px):
                            k = dl_idx
                            side = -d
                            exit_px = _fill(GO[k], GH[k], GL[k], side, at_close=GC[k])
                        busy_until = exit_i
                        pts = d * (exit_px - entry_px)
                        events.append({
                            "sd_break": sds[bidx], "sd_reclaim": sd_r, "sd": sd_e,
                            "sd_exit": bars["sd"].iloc[exit_i], "dir": d,
                            "rng_lo": rlo, "rng_hi": rhi, "target": tgt,
                            "break_close": rc.iloc[bidx], "reclaim_close": cl,
                            "entry_px": entry_px, "exit_px": exit_px,
                            "exit_reason": reason, "pts": pts,
                            "net": pts * PV - COMM_RT,
                            "sessions_held": SD_POS[bars["sd"].iloc[exit_i]] - SD_POS[sd_e] + 1,
                            "entry_gidx": eidx, "exit_gidx": exit_i})
        # 2) new break episode on this session
        if cl > hi_i:
            episodes.append((i, +1, lo_i, hi_i))
        elif cl < lo_i:
            episodes.append((i, -1, lo_i, hi_i))
    ev = pd.DataFrame(events)
    return ev, {"dropped_overlap": dropped_overlap, "dropped_censor": dropped_censor,
                "dropped_nobar": dropped_nobar}


print("\n=== e378 multi-day balance false-break (center lookback 20) ===")
e378, drops378 = sim_e378(20)
e378.to_csv(f"{OUT}/e378_events.csv", index=False)
rows = []
p = nw_stats(e378["net"], e378["sd"]); p.update({"cell": "pooled"})
p["p_boot"] = block_boot_p(e378["net"])
rows.append(p)
h1, h2 = split_stats(e378)
h1.update({"cell": "split_2022_24"}); h2.update({"cell": "split_2025_26"})
rows += [h1, h2]
for dd, g in e378.groupby("dir"):
    q = nw_stats(g["net"], g["sd"]); q.update({"cell": f"dir_{'short' if dd < 0 else 'long'}"})
    rows.append(q)
for reas, g in e378.groupby("exit_reason"):
    q = nw_stats(g["net"], g["sd"]); q.update({"cell": f"exit_{reas}"})
    rows.append(q)
e378_summary = pd.DataFrame(rows)
for k, v in drops378.items():
    e378_summary[k] = v
e378_summary.to_csv(f"{OUT}/e378_summary.csv", index=False)
print(e378_summary[["cell", "n", "mean", "total", "t_nw", "t_cluster", "t_iid"]].round(3).to_string())
print(f"drops {drops378}; p_boot {p['p_boot']}")

print("\n--- e378 plateau lookback {10,20,40} ---")
prows = []
for lb in (10, 20, 40):
    evg, dr = sim_e378(lb)
    st = nw_stats(evg["net"], evg["sd"])
    prows.append({"lookback": lb, "n": st["n"], "mean_net": st["mean"],
                  "t_nw": st["t_nw"], **dr})
    print(f"lb {lb:2d}  N {st['n']:4d}  mean {st['mean']:8.2f}  t_nw {st['t_nw']:6.2f}  {dr}")
e378_plateau = pd.DataFrame(prows)
e378_plateau.to_csv(f"{OUT}/e378_plateau.csv", index=False)

# e378 daily MTM at session closes (for complementarity)
mtm = {}
for tr in e378.itertuples():
    pe, px_ = SD_POS[tr.sd], SD_POS[tr.sd_exit]
    for si in range(pe, px_ + 1):
        ref_prev = tr.entry_px if si == pe else SESS_CLOSE[ALL_SD[si - 1]]
        ref_now = tr.exit_px if si == px_ else SESS_CLOSE[ALL_SD[si]]
        pnl = tr.dir * (ref_now - ref_prev) * PV
        if si == px_:
            pnl -= COMM_RT
        mtm[ALL_SD[si]] = mtm.get(ALL_SD[si], 0.0) + pnl
e378_mtm = pd.Series(mtm).sort_index()
e378_mtm.rename("mtm_net").to_csv(f"{OUT}/e378_daily_mtm.csv")
print(f"e378 MTM total {e378_mtm.sum():.2f} vs event net total {e378['net'].sum():.2f}")

# ================================================================= ENGINE 379
def month_end_events():
    events = []
    skipped = {"no_prior_ref": 0, "short_month": 0, "no_0936": 0, "early_exit": 0,
               "mtd_zero": 0}
    S_ = S.copy()
    S_["ym"] = S_["sd"].dt.to_period("M")
    months = list(S_["ym"].drop_duplicates())
    by_m = {m: g for m, g in S_.groupby("ym")}
    for mi, m in enumerate(months):
        if mi == 0:
            skipped["no_prior_ref"] += 1
            continue
        g = by_m[m]
        if len(g) < 3:
            skipped["short_month"] += 1
            continue
        prev_g = by_m[months[mi - 1]]
        ref0 = prev_g["sess_close"].iloc[-1]
        dwin = g.iloc[-2:]                     # last 2 sessions
        ref_sig = g["sess_close"].iloc[-3]     # close of D_{n-2}
        mtd = ref_sig - ref0
        if mtd == 0:
            skipped["mtd_zero"] += 1
            continue
        sign = -int(np.sign(mtd))
        for k, (_, day) in enumerate(dwin.iterrows()):
            sd = day["sd"]
            if sd not in bar0936:
                skipped["no_0936"] += 1
                continue
            ei = bar0936[sd]
            entry_px = _fill(GO[ei], GH[ei], GL[ei], sign)
            a = rth_arrays.get(sd)
            hm = a["hm"]
            early = False
            if 1600 in set(hm):
                xi = a["gi"][int(np.where(hm == 1600)[0][0])]
                exit_px = _fill(GO[xi], GH[xi], GL[xi], -sign)   # 15:57 open
                exit_hm = 1600
            else:                                # early close: last RTH bar close
                j = len(hm) - 1
                gi = a["gi"][j]
                exit_px = _fill(GO[gi], GH[gi], GL[gi], -sign, at_close=GC[gi])
                exit_hm = hm[j]
                early = True
                skipped["early_exit"] += 1
            pts = sign * (exit_px - entry_px)
            events.append({"month": str(m), "sd": sd, "day_idx": k + 1,
                           "mtd_pts": mtd, "sign": sign, "entry_px": entry_px,
                           "exit_px": exit_px, "exit_hm": exit_hm,
                           "early_close_exit": early, "pts": pts,
                           "net": pts * PV - COMM_RT})
    return pd.DataFrame(events), skipped


print("\n=== e379 month-end flow tilt ===")
e379, skip379 = month_end_events()
e379.to_csv(f"{OUT}/e379_events.csv", index=False)
rows = []
p = nw_stats(e379["net"], e379["sd"]); p.update({"cell": "pooled"})
p["p_boot"] = block_boot_p(e379["net"])
rows.append(p)
h1, h2 = split_stats(e379)
h1.update({"cell": "split_2022_24"}); h2.update({"cell": "split_2025_26"})
rows += [h1, h2]
for y, g in e379.groupby(e379["sd"].dt.year):
    q = nw_stats(g["net"], g["sd"]); q.update({"cell": f"year_{y}"})
    rows.append(q)
for sgn, g in e379.groupby("sign"):
    q = nw_stats(g["net"], g["sd"]); q.update({"cell": f"sign_{'long' if sgn > 0 else 'short'}"})
    rows.append(q)
for di, g in e379.groupby("day_idx"):
    q = nw_stats(g["net"], g["sd"]); q.update({"cell": f"day{di}"})
    rows.append(q)
e379_summary = pd.DataFrame(rows)
for k, v in skip379.items():
    e379_summary[f"skip_{k}"] = v
e379_summary.to_csv(f"{OUT}/e379_summary.csv", index=False)
print(e379_summary[["cell", "n", "mean", "total", "t_nw", "t_cluster"]].round(3).to_string())
print(f"skips {skip379}; p_boot {p['p_boot']}")

# --- old-regime direction check (2006-2021), gross close-to-close points
print("\n--- e379 hist direction check 2006-2021 ---")
hv = pd.read_parquet("runs/SM06_SOLAR_HISTORY/out/vote_state_3m_hist.parquet")
hc = hv[hv["is_last_of_sess"]][["sess_date", "close"]].copy()
hc["sd"] = pd.to_datetime(hc["sess_date"])
hc = hc.sort_values("sd").reset_index(drop=True)
assert hc["sd"].max() <= pd.Timestamp("2021-12-31")
hc["ym"] = hc["sd"].dt.to_period("M")
months = list(hc["ym"].drop_duplicates())
by_m = {m: g for m, g in hc.groupby("ym")}
hrows = []
for mi, m in enumerate(months):
    if mi == 0:
        continue
    g = by_m[m]
    if len(g) < 3:
        continue
    ref0 = by_m[months[mi - 1]]["close"].iloc[-1]
    ref_sig = g["close"].iloc[-3]
    mtd = ref_sig - ref0
    if mtd == 0:
        continue
    sign = -int(np.sign(mtd))
    win = g["close"].iloc[-1] - ref_sig       # 2-day window, points
    hrows.append({"month": str(m), "sd_sig": g["sd"].iloc[-3], "sd_end": g["sd"].iloc[-1],
                  "mtd_pts": mtd, "sign": sign, "win_pts": win,
                  "signed_pts": sign * win,
                  "signed_bps": sign * win / ref_sig * 1e4})
hist379 = pd.DataFrame(hrows)
hist379.to_csv(f"{OUT}/e379_hist_check.csv", index=False)
hrows2 = []
for nm, g in [("pooled_2006_2021", hist379)] + [
        (f"era_{a}_{b}", hist379[(hist379["sd_end"].dt.year >= a) & (hist379["sd_end"].dt.year <= b)])
        for a, b in ((2006, 2009), (2010, 2013), (2014, 2017), (2018, 2021))]:
    st = nw_stats(g["signed_pts"], g["sd_end"])
    st_b = nw_stats(g["signed_bps"], g["sd_end"])
    hrows2.append({"cell": nm, "n_months": st["n"], "mean_signed_pts": st["mean"],
                   "t_nw_pts": st["t_nw"], "mean_signed_bps": st_b["mean"],
                   "t_nw_bps": st_b["t_nw"],
                   "hit_rate": float((g["signed_pts"] > 0).mean()) if len(g) else np.nan})
hist_sum = pd.DataFrame(hrows2)
hist_sum["p_boot_bps"] = block_boot_p(hist379["signed_bps"])
hist_sum.to_csv(f"{OUT}/e379_hist_summary.csv", index=False)
print(hist_sum.round(3).to_string())

# dev-side monthly signed 2-day window in the SAME units (context for structural read)
dev_m = e379.groupby("month")["net"].sum()

# ============================================================ COMPLEMENTARITY
print("\n=== joint-loss-week complementarity ===")
rc_ = pd.read_csv("runs/SMV2H_ONECONTRACT/out/rerank_curves.csv")
rc_["sess"] = pd.to_datetime(rc_["sess"])
rc_ = rc_[rc_["sess"] <= DEV_END].set_index("sess")
led = pd.read_parquet("runs/SMV2B_BMOM_EXEC_AUDIT/out/ledger_E2_next_open.parquet")
led["sess"] = pd.to_datetime(led["sess"])
led = led[led["sess"] <= DEV_END]
bmom_d = (led.groupby("sess")["net_c1_ticks"].sum() * 5.0).reindex(rc_.index, fill_value=0.0)
assert float((rc_["BM_E2"] - bmom_d).abs().max()) < 1e-6, "ledger != BM_E2 column"
solar_d = rc_["DUAL"]
champ_d = rc_["60_40"]
twin = pd.read_csv("runs/SMV2M_MASTER_BUILD/out/twin_daily.csv", index_col=0, parse_dates=True)["0"]
twin = twin[twin.index <= DEV_END].reindex(rc_.index).fillna(0.0)

cal = rc_.index
wk = cal.to_period("W-FRI")
def weekly(s):
    return s.groupby(wk).sum()

solar_w, bmom_w, champ_w, twin_w = weekly(solar_d), weekly(bmom_d), weekly(champ_d), weekly(twin)
jl_primary = (solar_w < 0) & (bmom_w < 0)
jl_secondary = (twin_w < 0) & (bmom_w < 0)
print(f"weeks {len(solar_w)}  joint-loss primary {jl_primary.sum()}  secondary {jl_secondary.sum()}")

eng_daily = {
    "e377_value_area": e377.groupby("sd")["net"].sum().reindex(cal, fill_value=0.0),
    "e378_false_break_mtm": e378_mtm.reindex(cal, fill_value=0.0),
    "e379_month_end": e379.groupby("sd")["net"].sum().reindex(cal, fill_value=0.0),
}
crows = []
for defname, mask in (("primary_DUAL_leg_and_BMOM", jl_primary),
                      ("secondary_champ_twin_and_BMOM", jl_secondary)):
    for nm, ed in eng_daily.items():
        ew = weekly(ed)
        ej = ew[mask]
        crows.append({
            "definition": defname, "engine": nm,
            "n_weeks": len(ew), "n_jointloss_weeks": int(mask.sum()),
            "n_jl_weeks_with_events": int((ej != 0).sum()),
            "engine_mean_week_all": float(ew.mean()),
            "engine_mean_week_jointloss": float(ej.mean()),
            "engine_total_jointloss": float(ej.sum()),
            "engine_total_all": float(ew.sum()),
            "champ_mean_week_jointloss": float(champ_w[mask].mean()),
            "solar_mean_week_jointloss": float(solar_w[mask].mean()),
            "bmom_mean_week_jointloss": float(bmom_w[mask].mean()),
            "corr_weekly_engine_vs_champ": float(ew.corr(champ_w)),
        })
comp = pd.DataFrame(crows)
comp.to_csv(f"{OUT}/jointloss_complementarity.csv", index=False)
print(comp.round(2).to_string())

# ---------------------------------------------------------------- gate audit
def sgn(v):
    return int(np.sign(v)) if np.isfinite(v) else 0

def cell(df, c):
    return df[df["cell"] == c].iloc[0]

g77, g77a, g77b = cell(e377_summary, "pooled"), cell(e377_summary, "split_2022_24"), cell(e377_summary, "split_2025_26")
g78, g78a, g78b = cell(e378_summary, "pooled"), cell(e378_summary, "split_2022_24"), cell(e378_summary, "split_2025_26")
g79, g79a, g79b = cell(e379_summary, "pooled"), cell(e379_summary, "split_2022_24"), cell(e379_summary, "split_2025_26")
hist_pool = hist_sum[hist_sum["cell"] == "pooled_2006_2021"].iloc[0]
pl77 = set(np.sign(e377_plateau["mean_net"]))
pl78 = set(np.sign(e378_plateau["mean_net"]))
gates = pd.DataFrame([
    {"engine": "e377", "gate": "t_nw>=2", "value": round(g77["t_nw"], 3), "pass": bool(g77["t_nw"] >= 2)},
    {"engine": "e377", "gate": "N>=150", "value": g77["n"], "pass": bool(g77["n"] >= 150)},
    {"engine": "e377", "gate": "WF_sign_stable", "value": f"{g77a['mean']:.2f}|{g77b['mean']:.2f}",
     "pass": bool(sgn(g77a["mean"]) == sgn(g77b["mean"]) != 0)},
    {"engine": "e377", "gate": "plateau_9cells_same_sign", "value": str(sorted(pl77)),
     "pass": bool(len(pl77) == 1)},
    {"engine": "e378", "gate": "t_nw>=2", "value": round(g78["t_nw"], 3), "pass": bool(g78["t_nw"] >= 2)},
    {"engine": "e378", "gate": "N>=80", "value": g78["n"], "pass": bool(g78["n"] >= 80)},
    {"engine": "e378", "gate": "WF_sign_stable", "value": f"{g78a['mean']:.2f}|{g78b['mean']:.2f}",
     "pass": bool(sgn(g78a["mean"]) == sgn(g78b["mean"]) != 0)},
    {"engine": "e378", "gate": "plateau_3cells_same_sign", "value": str(sorted(pl78)),
     "pass": bool(len(pl78) == 1)},
    {"engine": "e379", "gate": "t_nw>=2", "value": round(g79["t_nw"], 3), "pass": bool(g79["t_nw"] >= 2)},
    {"engine": "e379", "gate": "N>=100_day_events", "value": g79["n"], "pass": bool(g79["n"] >= 100)},
    {"engine": "e379", "gate": "dev_sign_2022_24_vs_2025_26", "value": f"{g79a['mean']:.2f}|{g79b['mean']:.2f}",
     "pass": bool(sgn(g79a["mean"]) == sgn(g79b["mean"]) != 0)},
    {"engine": "e379", "gate": "old_regime_same_sign", "value":
     f"dev_mean {g79['mean']:.2f} | hist_bps {hist_pool['mean_signed_bps']:.2f} (t {hist_pool['t_nw_bps']:.2f})",
     "pass": bool(sgn(g79["mean"]) == sgn(hist_pool["mean_signed_bps"]) != 0 and sgn(g79["mean"]) > 0)},
])
gates.to_csv(f"{OUT}/gates.csv", index=False)
print("\n--- gates ---")
print(gates.to_string())
verdicts = {e: bool(gates[gates["engine"] == e]["pass"].all()) for e in ("e377", "e378", "e379")}
print("verdicts:", verdicts)
print("\ndone.")
