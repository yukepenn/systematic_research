"""SMV2X_ENGINE3_S3 -- R1 FAMILY TEST, seq 396-398 (Engine #3 slate 3, calendar/event family,
D2 expansion-pass ranks 2/5/6). Third and final slate of the "engine-3" mechanism-expansion
program (slate 1 = SMV2K seq 368-370, KILLED; slate 2 = SMV2P seq 377-379, KILLED).

e396  shock-continuation      60-session trailing realized vol (causal, expanding, 12mo
                               burn-in), |daily log return| > 3 sigma -> trade WITH the shock.
e397  macro-drift             FOMC (2pm ET) / CPI (8:30am ET) -- see calendars.py for the
                               CPI-ONLY scope note on the spec's "CPI/NFP/PCE" cell.
e398  opex-unclamp            flat T-3..T (pinning window), breakout continuation T+1 after
                               3rd-Friday index-option expiration.

All economics NET of $4.36/RT + 1 tick/side slippage (NQ, $20/pt, tick 0.25). Dev window:
sessions <= 2026-05-31. No data >= 2026-08-01 is ever used (VIRGIN).

Frozen bar/fill conventions (same substrate and idiom as SMV2K/SMV2P, disclosed here again):
  - Bars: END-stamped 3m via sm01_solarsim.load_bars_3m (same substrate as every SMV2 run).
  - "HH:MM open" = the open occurring at wall time HH:MM = open of the bar STAMPED HH:MM+3.
  - RTH = stamps 0933..1600 (0933 bar's open is the 09:30 open).
  - "session close" = the true last 3m bar of the session (~17:00 ET), matching the campaign's
    universal exit-on-session-close convention -- NOT the 1600 (4pm) RTH close.
  - Entry/exit fills: sm01_solarsim._fill (1-tick adverse slip capped by the fill bar's range);
    open-based fills for entries and mid-session timed exits, at_close fills for session-close
    exits, exactly as common_exec.e10_exec and every SMV2K/P engine already does it.
  - NW t-stat: mean per-event net, SE clustered by session, Bartlett/Newey-West lag 5 (house
    convention, matches SMV2K/SMV2P). House bootstrap (moving block=5, B=10000, seed=20260808)
    reported alongside as P(mean>0), supplementary to the frozen t_NW>=2 gate.

Engine-specific mechanical choices not fully pinned by the frozen spec text, disclosed here
(each is a reasonable, literal-consistent reading, not an improvised gate/grid/data choice --
 see REPORT.md "Interpretive choices" for the INFERENCE-labeled rationale of each):
  - e396: sigma_t = std of log returns over sessions [t-60..t-1] causally (shift(1).rolling(60,
    min_periods=2)) -- naturally "expanding" for t-1 < 60 sessions, exactly the spec's "trailing
    60-session ... expanding" phrase. 12mo burn-in = no event fires until session_date >=
    first_dev_session + 365 calendar days. Entry = open of the entry session's 0936-stamped bar
    (the 09:33 wall-clock open). Hold N sessions counts the entry session as day 1 (hold=1 exits
    the entry session's own close; hold=2/3 exit one/two further sessions' close).
  - e397 FOMC: move measured from the 1403-bar open (2:00pm) to the 1433-bar open (2:30pm);
    entered at the 1433-bar open; held to session close same day.
    e397 CPI (pre-open handling, ALWAYS active since 8:30am releases are always pre-RTH): move
    measured from the 0933-bar open (9:30 RTH open) to the 1003-bar open (10:00, +30min);
    entered at the 1003-bar open; held 60 minutes, exit at the first bar closing at/after 11:00
    (the 1103-stamped bar's close).
  - e398: T-3..T realized range = RTH high/low over those 4 trading sessions (not full-session,
    not overnight -- matches the RTH-anchored range convention every prior engine-3 slate used).
    Breakout scan starts at T+1's first RTH bar (0933-stamped); a bar that breaches both sides
    simultaneously is skipped as ambiguous (documented as a modeling choice; expected to be rare
    to never given 3m-bar ranges vs a 4-session range). Entry fill uses the gap-through-aware
    stop idiom already established in SMV2K's sim_e368 (base = max(open, level) or min(open,
    level), then 1-tick slip capped by the bar's high/low).
"""
import sys, os, json
import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
os.chdir(REPO)
sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m, _fill, TICK
from smv2_common import boot_ci_mean

from calendars import FOMC_DATES, CPI_DATES

RUN = "runs/SMV2X_ENGINE3_S3"
OUT = f"{RUN}/out"
os.makedirs(OUT, exist_ok=True)

PV = 20.0            # NQ point value ($/pt)
COMM_RT = 4.36        # $/round trip (NQ Lifetime, $2.18/side, matches CLAUDE.md frozen truth)
DEV_END = pd.Timestamp("2026-05-31")
NW_LAG = 5
SPLIT = pd.Timestamp("2024-12-31")     # 2022-24 vs 2025-26 (house convention)
BOOT_BLOCK, BOOT_B, BOOT_SEED = 5, 10000, 20260808

# =============================================================================== substrate
print("loading substrate ...", flush=True)
bars = load_bars_3m()
bars["sd"] = pd.to_datetime(bars["sess_date"])
assert bars["sd"].max() < pd.Timestamp("2026-08-01"), "VIRGIN data in file?!"
bars = bars[bars["sd"] <= DEV_END].reset_index(drop=True)
t = pd.to_datetime(bars["time"])
bars["hm"] = t.dt.hour * 100 + t.dt.minute
print(f"dev bars {len(bars)}  sessions {bars['sd'].nunique()}  "
      f"range {bars['sd'].min().date()} .. {bars['sd'].max().date()}", flush=True)

sess_rows = []
rth_arrays = {}
for sd, g in bars.groupby("sd", sort=True):
    g = g.sort_values("time")
    hm = g["hm"].to_numpy()
    last = g.iloc[-1]
    row = {"sd": sd, "s_open": g["open"].iloc[0], "s_high": g["high"].max(),
           "s_low": g["low"].min(), "s_close": last["close"],
           "last_o": last["open"], "last_h": last["high"], "last_l": last["low"],
           "last_c": last["close"]}
    r = g[(hm >= 933) & (hm <= 1600)]
    if len(r):
        rhm = r["hm"].to_numpy()
        row["rth_first_hm"] = rhm[0]
        row["rth_high"] = r["high"].max()
        row["rth_low"] = r["low"].min()
        rth_arrays[sd] = {"o": r["open"].to_numpy(dtype=float), "h": r["high"].to_numpy(dtype=float),
                          "l": r["low"].to_numpy(dtype=float), "c": r["close"].to_numpy(dtype=float),
                          "hm": rhm}
    else:
        row["rth_first_hm"] = np.nan; row["rth_high"] = np.nan; row["rth_low"] = np.nan
    sess_rows.append(row)

S = pd.DataFrame(sess_rows).sort_values("sd").reset_index(drop=True)
S["logret"] = np.log(S["s_close"] / S["s_close"].shift(1))
ALL_SD = pd.DatetimeIndex(S["sd"])  # Timestamp elements (NOT .to_numpy() -- that yields
                                     # numpy.datetime64, which does not hash-match the Timestamp
                                     # keys pandas groupby("sd") produces; caught in dev testing)
SD_POS = {sd: i for i, sd in enumerate(ALL_SD)}
SESS_CLOSE = dict(zip(S["sd"], S["s_close"]))
FIRST_SD = S["sd"].iloc[0]
BURNIN_CUTOFF = FIRST_SD + pd.Timedelta(days=365)
print(f"session table: {len(S)} rows; first {FIRST_SD.date()}; 12mo burn-in cutoff "
      f"{BURNIN_CUTOFF.date()}", flush=True)
S.to_csv(f"{OUT}/session_table.csv", index=False)


def bar_at(a, hm_target):
    idx = np.searchsorted(a["hm"], hm_target)
    if idx < len(a["hm"]) and a["hm"][idx] == hm_target:
        return {"o": a["o"][idx], "h": a["h"][idx], "l": a["l"][idx], "c": a["c"][idx]}
    return None


def first_bar_ge(a, hm_target):
    idx = np.searchsorted(a["hm"], hm_target)
    if idx < len(a["hm"]):
        return idx
    return None


def fill_open(bar, side):
    return _fill(bar["o"], bar["h"], bar["l"], side)


def fill_close(bar, side):
    return _fill(bar["o"], bar["h"], bar["l"], side, at_close=bar["c"])


def last_bar_of(sd):
    r = S.loc[S["sd"] == sd].iloc[0]
    return {"o": r["last_o"], "h": r["last_h"], "l": r["last_l"], "c": r["last_c"]}


# =============================================================================== stats battery
def nw_stats(x, sess_dates, lag=NW_LAG):
    x = np.asarray(x, dtype=float); n = len(x)
    out = {"n": n, "mean": np.nan, "total": np.nan, "t_nw": np.nan, "n_sessions": 0}
    if n == 0:
        return out
    xbar = x.mean()
    out["mean"] = xbar; out["total"] = x.sum()
    if n < 3:
        return out
    df = pd.DataFrame({"x": x - xbar, "s": pd.to_datetime(list(sess_dates))})
    z = df.groupby("s", sort=True)["x"].sum().to_numpy()
    out["n_sessions"] = len(z)
    Snw = float((z ** 2).sum())
    L = min(lag, len(z) - 1)
    for l in range(1, L + 1):
        w = 1.0 - l / (lag + 1.0)
        Snw += 2.0 * w * float((z[l:] * z[:-l]).sum())
    if Snw > 0:
        out["t_nw"] = xbar / (np.sqrt(Snw) / n)
    return out


def split_stats(sd, net):
    sd = pd.to_datetime(pd.Series(sd)); net = pd.Series(net)
    h1 = net[sd.values <= SPLIT]; h2 = net[sd.values > SPLIT]
    a = nw_stats(h1, sd[sd.values <= SPLIT]); b = nw_stats(h2, sd[sd.values > SPLIT])
    return a, b


def boot_p(net):
    if len(net) < 5:
        return np.nan
    lo, hi, p = boot_ci_mean(net, block=BOOT_BLOCK, n_boot=BOOT_B, seed=BOOT_SEED)
    return p


def sgn(v):
    return int(np.sign(v)) if np.isfinite(v) else 0


def mtm_decompose(entry_sd, exit_sd, entry_px, exit_px, direction, comm_rt=COMM_RT):
    """Per-session MTM P&L for a trade spanning entry_sd..exit_sd (inclusive), marking to
    each interior session's true close. Commission charged once, at the exit session (same
    convention as SMV2P e378_mtm)."""
    pe, px_ = SD_POS[entry_sd], SD_POS[exit_sd]
    out = {}
    for si in range(pe, px_ + 1):
        sd_i = ALL_SD[si]
        ref_prev = entry_px if si == pe else SESS_CLOSE[ALL_SD[si - 1]]
        ref_now = exit_px if si == px_ else SESS_CLOSE[sd_i]
        pnl = direction * (ref_now - ref_prev) * PV
        if si == px_:
            pnl -= comm_rt
        out[sd_i] = out.get(sd_i, 0.0) + pnl
    return out


def daily_series_from_mtm(list_of_dicts):
    tot = {}
    for d in list_of_dicts:
        for k, v in d.items():
            tot[k] = tot.get(k, 0.0) + v
    return pd.Series(tot).reindex(ALL_SD, fill_value=0.0)


# =============================================================================== ENGINE 396
print("\n=== e396 shock-continuation ===", flush=True)
sigma60 = S["logret"].shift(1).rolling(60, min_periods=2).std(ddof=1)
S["sigma60"] = sigma60.to_numpy()
shock_mask = (S["logret"].abs() > 3 * S["sigma60"]) & S["sd"].ge(BURNIN_CUTOFF) & S["sigma60"].notna()
n_burnin_eligible = int(S["sd"].ge(BURNIN_CUTOFF).sum())
print(f"burn-in-eligible sessions {n_burnin_eligible}; shock days flagged {int(shock_mask.sum())}",
      flush=True)

e396_rows = []
for i in np.nonzero(shock_mask.to_numpy())[0]:
    sd_shock = ALL_SD[i]
    direction = int(np.sign(S["logret"].iloc[i]))
    if direction == 0 or i + 1 >= len(ALL_SD):
        continue
    sd_entry = ALL_SD[i + 1]
    a = rth_arrays.get(sd_entry)
    if a is None or len(a["hm"]) < 2 or a["hm"][0] != 933 or a["hm"][1] != 936:
        continue
    entry_bar = bar_at(a, 936)
    entry_px = fill_open(entry_bar, direction)
    row = {"sd_shock": sd_shock, "sd_entry": sd_entry, "dir": direction,
           "logret": S["logret"].iloc[i], "sigma60": S["sigma60"].iloc[i],
           "entry_px": entry_px}
    for hold in (1, 2, 3):
        j = i + 1 + (hold - 1)
        if j >= len(ALL_SD):
            row[f"sd_exit_h{hold}"] = np.nan; row[f"net_h{hold}"] = np.nan
            continue
        sd_exit = ALL_SD[j]
        exit_px = fill_close(last_bar_of(sd_exit), -direction)
        net = direction * (exit_px - entry_px) * PV - COMM_RT
        row[f"sd_exit_h{hold}"] = sd_exit
        row[f"net_h{hold}"] = net
    e396_rows.append(row)
e396 = pd.DataFrame(e396_rows)
e396.to_csv(f"{OUT}/e396_events.csv", index=False)
print(f"e396 events: {len(e396)}", flush=True)

e396_summary_rows = []
for hold in (1, 2, 3):
    col = f"net_h{hold}"
    ev = e396.dropna(subset=[col]) if len(e396) else e396
    st = nw_stats(ev[col], ev["sd_entry"]) if len(ev) else nw_stats([], [])
    st.update({"hold": hold, "p_boot": boot_p(ev[col].to_numpy()) if len(ev) else np.nan})
    if len(ev):
        h1, h2 = split_stats(ev["sd_entry"], ev[col])
        st["wf_2022_24_mean"] = h1["mean"]; st["wf_2022_24_t"] = h1["t_nw"]
        st["wf_2025_26_mean"] = h2["mean"]; st["wf_2025_26_t"] = h2["t_nw"]
    e396_summary_rows.append(st)
e396_summary = pd.DataFrame(e396_summary_rows)
e396_summary.to_csv(f"{OUT}/e396_summary.csv", index=False)
print(e396_summary[["hold", "n", "mean", "total", "t_nw", "p_boot",
                     "wf_2022_24_mean", "wf_2025_26_mean"]].round(3).to_string(), flush=True)

# center = hold 2 (per spec); MTM daily series for complementarity
e396_c = e396.dropna(subset=["net_h2"])
e396_mtm = daily_series_from_mtm([
    mtm_decompose(r.sd_entry, r.sd_exit_h2, r.entry_px,
                  fill_close(last_bar_of(r.sd_exit_h2), -r.dir), r.dir)
    for r in e396_c.itertuples()
]) if len(e396_c) else pd.Series(0.0, index=ALL_SD)
assert abs(e396_mtm.sum() - e396_c["net_h2"].sum()) < 1e-6, "e396 MTM decomposition mismatch"

# =============================================================================== ENGINE 397
print("\n=== e397 macro-drift (FOMC / CPI) ===", flush=True)


def sim_fomc(dates):
    rows = []
    for ds in dates:
        sd = pd.Timestamp(ds)
        if sd not in SD_POS:
            continue
        a = rth_arrays.get(sd)
        if a is None:
            continue
        b0 = bar_at(a, 1403); b30 = bar_at(a, 1433)
        if b0 is None or b30 is None:
            continue
        move = b30["o"] - b0["o"]
        if move == 0:
            continue
        d = int(np.sign(move))
        entry_px = fill_open(b30, d)
        exit_px = fill_close(last_bar_of(sd), -d)
        net = d * (exit_px - entry_px) * PV - COMM_RT
        rows.append({"sd": sd, "release_type": "FOMC", "dir": d, "move_pts": move,
                     "entry_px": entry_px, "exit_px": exit_px, "net": net})
    return pd.DataFrame(rows)


def sim_cpi(dates):
    rows = []
    for ds in dates:
        sd = pd.Timestamp(ds)
        if sd not in SD_POS:
            continue
        a = rth_arrays.get(sd)
        if a is None:
            continue
        b0 = bar_at(a, 933); b30 = bar_at(a, 1003)
        if b0 is None or b30 is None:
            continue
        move = b30["o"] - b0["o"]
        if move == 0:
            continue
        d = int(np.sign(move))
        entry_px = fill_open(b30, d)
        eidx = first_bar_ge(a, 1103)
        if eidx is None or a["hm"][eidx] != 1103:
            continue
        exit_bar = {"o": a["o"][eidx], "h": a["h"][eidx], "l": a["l"][eidx], "c": a["c"][eidx]}
        exit_px = fill_close(exit_bar, -d)
        net = d * (exit_px - entry_px) * PV - COMM_RT
        rows.append({"sd": sd, "release_type": "CPI", "dir": d, "move_pts": move,
                     "entry_px": entry_px, "exit_px": exit_px, "net": net})
    return pd.DataFrame(rows)


e397_fomc = sim_fomc(FOMC_DATES)
e397_cpi = sim_cpi(CPI_DATES)
e397 = pd.concat([e397_fomc, e397_cpi], ignore_index=True)
e397.to_csv(f"{OUT}/e397_events.csv", index=False)
print(f"e397 events: FOMC {len(e397_fomc)}  CPI {len(e397_cpi)}  "
      f"(FOMC dates supplied {len(FOMC_DATES)}, CPI dates supplied {len(CPI_DATES)})", flush=True)

e397_summary_rows = []
for label, ev in (("FOMC", e397_fomc), ("CPI", e397_cpi)):
    st = nw_stats(ev["net"], ev["sd"]) if len(ev) else nw_stats([], [])
    st.update({"cell": label, "p_boot": boot_p(ev["net"].to_numpy()) if len(ev) else np.nan})
    if len(ev):
        h1, h2 = split_stats(ev["sd"], ev["net"])
        st["wf_2022_24_mean"] = h1["mean"]; st["wf_2022_24_t"] = h1["t_nw"]
        st["wf_2025_26_mean"] = h2["mean"]; st["wf_2025_26_t"] = h2["t_nw"]
    e397_summary_rows.append(st)
e397_summary = pd.DataFrame(e397_summary_rows)
e397_summary.to_csv(f"{OUT}/e397_summary.csv", index=False)
print(e397_summary[["cell", "n", "mean", "total", "t_nw", "p_boot",
                     "wf_2022_24_mean", "wf_2025_26_mean"]].round(3).to_string(), flush=True)

e397_daily = e397.groupby("sd")["net"].sum().reindex(ALL_SD, fill_value=0.0) if len(e397) \
    else pd.Series(0.0, index=ALL_SD)

# =============================================================================== ENGINE 398
print("\n=== e398 opex-unclamp ===", flush=True)
expiry_candidates = pd.date_range(f"{FIRST_SD.year}-{FIRST_SD.month:02d}-01",
                                   DEV_END, freq="WOM-3FRI")
expiry_flags = []
e398_rows = []
flat_check = {}   # sd within any T-3..T window -> must stay untouched (0) by this engine
n_windows_checked = 0   # count of expirations actually contributing to the flat-window check
                        # (all valid-calendar T's with a full T-3..T window, NOT just the ones
                        # that ended up with a T+1 breakout event -- so this differs from len(e398))
for T in expiry_candidates:
    T = pd.Timestamp(T.date())
    in_calendar = T in SD_POS
    expiry_flags.append({"T": T, "in_session_calendar": in_calendar,
                         "quarterly": T.month in (3, 6, 9, 12)})
    if not in_calendar:
        continue
    pT = SD_POS[T]
    if pT < 3 or pT + 1 >= len(ALL_SD):
        continue
    window_sds = ALL_SD[pT - 3: pT + 1]
    n_windows_checked += 1
    for wsd in window_sds:
        flat_check[wsd] = flat_check.get(wsd, 0) + 0.0   # register, no PnL added -- engine flat
    rth_hi = S.loc[S["sd"].isin(window_sds), "rth_high"].max()
    rth_lo = S.loc[S["sd"].isin(window_sds), "rth_low"].min()
    sd_t1 = ALL_SD[pT + 1]
    a = rth_arrays.get(sd_t1)
    if a is None or not np.isfinite(rth_hi) or not np.isfinite(rth_lo):
        continue
    o, h, l = a["o"], a["h"], a["l"]
    n = len(o)
    ei = None; d = None; entry_px = None
    for i in range(n):
        up = h[i] > rth_hi
        dn = l[i] < rth_lo
        if up and dn:
            continue   # ambiguous same-bar dual breach -- skip bar, keep scanning
        if up:
            base = max(o[i], rth_hi); entry_px = min(base + TICK, h[i])
            ei = i; d = 1; break
        if dn:
            base = min(o[i], rth_lo); entry_px = max(base - TICK, l[i])
            ei = i; d = -1; break
    if ei is None:
        continue
    exit_px_t1 = fill_close(last_bar_of(sd_t1), -d)
    net_t1 = d * (exit_px_t1 - entry_px) * PV - COMM_RT
    row = {"T": T, "sd_entry": sd_t1, "dir": d, "range_hi": rth_hi, "range_lo": rth_lo,
           "entry_px": entry_px, "entry_hm": a["hm"][ei],
           "net_t1_only": net_t1}
    if pT + 3 < len(ALL_SD):
        sd_t3 = ALL_SD[pT + 3]
        exit_px_t3 = fill_close(last_bar_of(sd_t3), -d)
        net_t3 = d * (exit_px_t3 - entry_px) * PV - COMM_RT
        row["sd_exit_t3"] = sd_t3
        row["net_t1_t3"] = net_t3
    else:
        row["sd_exit_t3"] = np.nan; row["net_t1_t3"] = np.nan
    e398_rows.append(row)

e398 = pd.DataFrame(e398_rows)
e398.to_csv(f"{OUT}/e398_events.csv", index=False)
pd.DataFrame(expiry_flags).to_csv(f"{OUT}/e398_expiry_calendar.csv", index=False)
n_flagged_not_session = sum(1 for r in expiry_flags if not r["in_session_calendar"])
print(f"e398 expiry candidates {len(expiry_flags)}; not-a-trading-session {n_flagged_not_session}; "
      f"events (breakout found) {len(e398)}", flush=True)

e398_summary_rows = []
for label, col in (("T+1_only", "net_t1_only"), ("T+1..T+3", "net_t1_t3")):
    ev = e398.dropna(subset=[col]) if len(e398) else e398
    st = nw_stats(ev[col], ev["sd_entry"]) if len(ev) else nw_stats([], [])
    st.update({"cell": label, "p_boot": boot_p(ev[col].to_numpy()) if len(ev) else np.nan})
    if len(ev):
        h1, h2 = split_stats(ev["sd_entry"], ev[col])
        st["wf_2022_24_mean"] = h1["mean"]; st["wf_2022_24_t"] = h1["t_nw"]
        st["wf_2025_26_mean"] = h2["mean"]; st["wf_2025_26_t"] = h2["t_nw"]
    e398_summary_rows.append(st)
e398_summary = pd.DataFrame(e398_summary_rows)
e398_summary.to_csv(f"{OUT}/e398_summary.csv", index=False)
print(e398_summary[["cell", "n", "mean", "total", "t_nw", "p_boot",
                     "wf_2022_24_mean", "wf_2025_26_mean"]].round(3).to_string(), flush=True)

# center = T+1_only for the daily/complementarity series (T+1..T+3 double-counts T+1's own day
# inside a longer hold -- using the shorter cell avoids re-attributing that day's move twice)
e398_c = e398.dropna(subset=["net_t1_only"])
e398_daily_center = pd.Series(dict(zip(e398_c["sd_entry"], e398_c["net_t1_only"]))).reindex(
    ALL_SD, fill_value=0.0) if len(e398_c) else pd.Series(0.0, index=ALL_SD)

# T+1..T+3 MTM (for the flat-window verification + full disclosure only)
e398_t3 = e398.dropna(subset=["net_t1_t3"])
e398_mtm_t3 = daily_series_from_mtm([
    mtm_decompose(r.sd_entry, r.sd_exit_t3, r.entry_px,
                  fill_close(last_bar_of(r.sd_exit_t3), -r.dir), r.dir)
    for r in e398_t3.itertuples()
]) if len(e398_t3) else pd.Series(0.0, index=ALL_SD)

# ---- verify FLAT during T-3..T (explicit check per task instructions) ----
flat_window_sessions = sorted(flat_check.keys())
pnl_during_flat_windows_t1only = float(e398_daily_center.reindex(flat_window_sessions, fill_value=0.0).sum())
pnl_during_flat_windows_t3 = float(e398_mtm_t3.reindex(flat_window_sessions, fill_value=0.0).sum())
assert pnl_during_flat_windows_t1only == 0.0, "e398 FLAT-window violation (T+1_only series)"
assert pnl_during_flat_windows_t3 == 0.0, "e398 FLAT-window violation (T+1..T+3 MTM series)"
print(f"FLAT-window verification: {len(flat_window_sessions)} distinct T-3..T sessions across "
      f"{n_windows_checked} valid expiration windows ({len(e398)} of which also produced a "
      f"T+1 breakout event); engine PnL during those sessions = "
      f"{pnl_during_flat_windows_t1only:.2f} (T+1_only) / {pnl_during_flat_windows_t3:.2f} "
      f"(T+1..T+3 MTM) -- both exactly zero, constraint holds by construction.", flush=True)

# =============================================================================== gates
print("\n=== gate audit ===", flush=True)


def get_row(summary, key_col, key_val):
    m = summary[summary[key_col] == key_val]
    return m.iloc[0] if len(m) else None


g396_h2 = get_row(e396_summary, "hold", 2)
plateau396 = [get_row(e396_summary, "hold", h)["mean"] for h in (1, 2, 3)]
plateau396_signs = set(sgn(v) for v in plateau396)

g397_fomc = get_row(e397_summary, "cell", "FOMC")
g397_cpi = get_row(e397_summary, "cell", "CPI")

g398_t1 = get_row(e398_summary, "cell", "T+1_only")
g398_t3 = get_row(e398_summary, "cell", "T+1..T+3")
plateau398_signs = set(sgn(v) for v in (g398_t1["mean"], g398_t3["mean"]))

gates = pd.DataFrame([
    {"engine": "e396", "gate": "N>=40", "value": g396_h2["n"], "pass": bool(g396_h2["n"] >= 40)},
    {"engine": "e396", "gate": "t_nw>=2", "value": g396_h2["t_nw"], "pass": bool(g396_h2["t_nw"] >= 2)},
    {"engine": "e396", "gate": "WF_same_sign",
     "value": f"{g396_h2['wf_2022_24_mean']:.2f}|{g396_h2['wf_2025_26_mean']:.2f}",
     "pass": bool(sgn(g396_h2["wf_2022_24_mean"]) == sgn(g396_h2["wf_2025_26_mean"]) != 0)},
    {"engine": "e396", "gate": "plateau_hold_1_2_3_same_sign", "value": str(sorted(plateau396_signs)),
     "pass": bool(len(plateau396_signs) == 1)},

    {"engine": "e397_FOMC", "gate": "N>=25", "value": g397_fomc["n"], "pass": bool(g397_fomc["n"] >= 25)},
    {"engine": "e397_FOMC", "gate": "t_nw>=2", "value": g397_fomc["t_nw"], "pass": bool(g397_fomc["t_nw"] >= 2)},
    {"engine": "e397_FOMC", "gate": "WF_same_sign",
     "value": f"{g397_fomc['wf_2022_24_mean']:.2f}|{g397_fomc['wf_2025_26_mean']:.2f}",
     "pass": bool(sgn(g397_fomc["wf_2022_24_mean"]) == sgn(g397_fomc["wf_2025_26_mean"]) != 0)},

    {"engine": "e397_CPI", "gate": "N>=25", "value": g397_cpi["n"], "pass": bool(g397_cpi["n"] >= 25)},
    {"engine": "e397_CPI", "gate": "t_nw>=2", "value": g397_cpi["t_nw"], "pass": bool(g397_cpi["t_nw"] >= 2)},
    {"engine": "e397_CPI", "gate": "WF_same_sign",
     "value": f"{g397_cpi['wf_2022_24_mean']:.2f}|{g397_cpi['wf_2025_26_mean']:.2f}",
     "pass": bool(sgn(g397_cpi["wf_2022_24_mean"]) == sgn(g397_cpi["wf_2025_26_mean"]) != 0)},

    {"engine": "e398", "gate": "N>=40", "value": g398_t1["n"], "pass": bool(g398_t1["n"] >= 40)},
    {"engine": "e398", "gate": "t_nw>=2", "value": g398_t1["t_nw"], "pass": bool(g398_t1["t_nw"] >= 2)},
    {"engine": "e398", "gate": "WF_same_sign",
     "value": f"{g398_t1['wf_2022_24_mean']:.2f}|{g398_t1['wf_2025_26_mean']:.2f}",
     "pass": bool(sgn(g398_t1["wf_2022_24_mean"]) == sgn(g398_t1["wf_2025_26_mean"]) != 0)},
    {"engine": "e398", "gate": "plateau_T1only_T1T3_same_sign", "value": str(sorted(plateau398_signs)),
     "pass": bool(len(plateau398_signs) == 1)},
])
gates.to_csv(f"{OUT}/gates.csv", index=False)
print(gates.to_string(), flush=True)

verdicts = {}
for eng in ("e396", "e397_FOMC", "e397_CPI", "e398"):
    sub = gates[gates["engine"] == eng]
    verdicts[eng] = "PASS" if bool(sub["pass"].all()) else "FAIL"
print("\nVERDICTS:", verdicts, flush=True)
with open(f"{OUT}/verdicts.json", "w") as f:
    json.dump(verdicts, f, indent=2)

# =============================================================================== complementarity
print("\n=== complementarity vs champion + SMV2Q joint-loss weeks ===", flush=True)
rc = pd.read_csv("runs/SMV2H_ONECONTRACT/out/rerank_curves.csv", parse_dates=["sess"])
rc = rc[rc["sess"] <= DEV_END].set_index("sess")
champ = rc["60_40"].reindex(ALL_SD, fill_value=0.0)

jl = pd.read_csv("runs/SMV2Q_DIAGNOSTICS/out/joint_loss_periods.csv")
jl_weeks = set(jl.loc[jl["freq"] == "weekly", "period"].astype(int))
print(f"SMV2Q joint-loss weekly periods reused: {len(jl_weeks)} (expect 50)", flush=True)


def wkey(idx):
    iso = pd.DatetimeIndex(idx).isocalendar()
    return (iso["year"].astype(int) * 100 + iso["week"].astype(int)).to_numpy()


WK = pd.Series(wkey(ALL_SD), index=ALL_SD)
jl_mask = WK.isin(jl_weeks)
n_dev_weeks = WK.nunique()
print(f"dev sessions map to {n_dev_weeks} distinct ISO weeks; {int(jl_mask.groupby(WK).first().sum())} "
      f"of those are SMV2Q joint-loss weeks", flush=True)

ENGINE_DAILY = {
    "e396_shock_continuation_h2": e396_mtm,
    "e397_FOMC": pd.Series(dict(zip(e397_fomc["sd"], e397_fomc["net"]))).reindex(
        ALL_SD, fill_value=0.0) if len(e397_fomc) else pd.Series(0.0, index=ALL_SD),
    "e397_CPI": pd.Series(dict(zip(e397_cpi["sd"], e397_cpi["net"]))).reindex(
        ALL_SD, fill_value=0.0) if len(e397_cpi) else pd.Series(0.0, index=ALL_SD),
    "e398_opex_unclamp_t1only": e398_daily_center,
}

comp_rows = []
for name, ed in ENGINE_DAILY.items():
    ed = ed.reindex(ALL_SD, fill_value=0.0)
    ew = ed.groupby(WK).sum()
    cw = champ.groupby(WK).sum()
    corr_daily = float(ed.corr(champ))
    corr_weekly = float(ew.corr(cw))
    ew_jl = ew[ew.index.isin(jl_weeks)]
    ew_all = ew
    cw_jl = cw[cw.index.isin(jl_weeks)]
    comp_rows.append({
        "engine": name, "n_days_dev": len(ed), "n_event_days": int((ed != 0).sum()),
        "corr_daily_vs_champ": corr_daily, "corr_weekly_vs_champ": corr_weekly,
        "n_weeks_dev": len(ew_all), "n_jointloss_weeks": len(ew_jl),
        "engine_mean_week_all": float(ew_all.mean()),
        "engine_mean_week_jointloss": float(ew_jl.mean()) if len(ew_jl) else np.nan,
        "engine_total_jointloss": float(ew_jl.sum()) if len(ew_jl) else 0.0,
        "engine_n_jl_weeks_with_events": int((ew_jl != 0).sum()) if len(ew_jl) else 0,
        "champ_mean_week_all": float(cw.mean()),
        "champ_mean_week_jointloss": float(cw_jl.mean()) if len(cw_jl) else np.nan,
    })
comp = pd.DataFrame(comp_rows)
comp.to_csv(f"{OUT}/jointloss_complementarity.csv", index=False)
print(comp.round(3).to_string(), flush=True)

print("\ndone.", flush=True)
