"""W7-3 — E1 event-anchored windows (honest sample-limited handling).
Frozen spec: research/scalping_lab/specs/W7_rt2_discharge.md (committed 1d76c14), section W7-3.

(a) TICK DESCRIPTIVE (n<=4, NO kill/pass claims): discovery sessions containing a
    scheduled release; describe 08:30-09:45 (pre-RTH releases) / 14:00-14:30 (FOMC)
    windows from sechilo/grid1s — path, max excursions, spread_t trajectory,
    realized vol vs session baseline.
(b) MINUTE-POWERED (Program-B study, 3-min CSV, dev window 2022-01 -> 2026-05-31 ONLY):
    signal = sign(close@09:30 bar - close of last bar strictly before 08:30);
    trade at the 09:30 bar close in that direction, fixed exits {15,30,60} min
    (market at bar close), C1 costs; release days only; placebo = non-event days.
    FROZEN verdict rule: promising iff net C1 > 0 with CI_lo > 0 at any exit horizon
    AND the placebo shows no comparable effect; else negative.

Units: sechilo mid_* columns are in TICK units (price*4, house convention per
w31_snapback.py); grid1s prices in points, spread_t in ticks; CSV prices in points,
NQ tick = 0.25 -> ticks = points*4. Costs C1=2.872t round trip.
Seed 20260808, 1000 session-bootstrap reps, day-clustered (1 trade/day => day bootstrap).
LOCAL ONLY. Dev-window guard: CSV rows with time >= 2026-06-01 are dropped at read.
"""
import os
import sys
import numpy as np
import pandas as pd

SEED = 20260808
NBOOT = 1000
C1 = 2.872
TICK = 0.25

ROOT = "research/scalping_lab"
SH = os.path.join(ROOT, "substrate", "sechilo", "NQ")
GR = os.path.join(ROOT, "substrate", "grid1s", "NQ")
CAL = "research/04_complementary_family/c01_announcement_calendar.csv"
CSV = "runs/AUDIT03_BARS/nq_3m_2022_2026.csv"
OUTD = os.path.join(ROOT, "artifacts", "w7_e1")
os.makedirs(OUTD, exist_ok=True)


class Tee:
    def __init__(self, path):
        self.f = open(path, "w", encoding="utf-8")
        self.stdout = sys.stdout

    def write(self, s):
        self.f.write(s)
        self.stdout.write(s)

    def flush(self):
        self.f.flush()
        self.stdout.flush()


sys.stdout = Tee(os.path.join(OUTD, "stdout.txt"))

cal = pd.read_csv(CAL)
cal["date"] = pd.to_datetime(cal["date"]).dt.date
print("Calendar rows:", len(cal), "| events:", cal["event"].value_counts().to_dict(),
      "| times:", cal["time_et"].value_counts().to_dict())

# ---------------------------------------------------------------------------
# (a) TICK DESCRIPTIVE — which discovery sessions contain a scheduled release
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("(a) TICK DESCRIPTIVE — event sessions in the 37-session discovery substrate")
print("    LABEL: DESCRIPTIVE ONLY. n<=4 -> no kill/pass claims are made or implied.")
print("=" * 78)

import glob
sess_tags = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(SH, "s*.parquet")))
sess_dates = {pd.to_datetime(t[1:], format="%Y%m%d").date(): t for t in sess_tags}
ev_sessions = cal[cal["date"].isin(sess_dates)].copy()
ev_sessions["tag"] = ev_sessions["date"].map(sess_dates)
print("\nDiscovery sessions (sechilo):", len(sess_tags))
print("Calendar joins (release inside a discovery session):")
print(ev_sessions[["date", "event", "time_et", "tag"]].to_string(index=False))

sess_rows = []
min_rows = []
for _, ev in ev_sessions.iterrows():
    tag, event, time_et = ev["tag"], ev["event"], ev["time_et"]
    d0 = pd.Timestamp(ev["date"])
    s = pd.read_parquet(os.path.join(SH, tag + ".parquet"))
    g = pd.read_parquet(os.path.join(GR, tag + ".parquet"))
    s["time"] = pd.to_datetime(s["time"])
    g["time"] = pd.to_datetime(g["time"])
    # full 1-second grid, ffilled mids (sechilo skips empty seconds)
    full = pd.DataFrame({"time": pd.date_range(s["time"].iloc[0], s["time"].iloc[-1], freq="1s")})
    f = full.merge(s, on="time", how="left").merge(
        g[["time", "spread_t", "bid_upd", "ask_upd"]], on="time", how="left")
    f["mid_last"] = f["mid_last"].ffill()
    f["mid_high"] = f["mid_high"].fillna(f["mid_last"])
    f["mid_low"] = f["mid_low"].fillna(f["mid_last"])
    upd60 = (f["bid_upd"].fillna(0) + f["ask_upd"].fillna(0)).rolling(60, min_periods=1).sum()
    f["alive"] = upd60 > 0
    sec = (f["time"] - d0).dt.total_seconds()  # seconds since session-date midnight ET

    hh, mm = map(int, time_et.split(":"))
    t_ev = hh * 3600 + mm * 60
    win_end = t_ev + (75 * 60 if time_et == "08:30" else 30 * 60)  # 09:45 / 14:30

    ref_mask = sec < t_ev
    ref = f.loc[ref_mask, "mid_last"].iloc[-1]  # mid at last second before release (ticks)
    win = f[(sec >= t_ev) & (sec < win_end)]
    wsec = sec[(sec >= t_ev) & (sec < win_end)]

    # path: mid delta (ticks) at fixed offsets after the event
    offs = ([10, 30, 60, 120, 300, 600, 900, 1800, 2700, 3600, 4500]
            if time_et == "08:30" else [10, 30, 60, 120, 300, 600, 900, 1200, 1500, 1800])
    path = {}
    for o in offs:
        m = f.loc[sec <= t_ev + o, "mid_last"].iloc[-1]
        path[f"d{o}s"] = m - ref
    # max excursions (ticks) from ref within window
    up = win["mid_high"] - ref
    dn = ref - win["mid_low"]
    i_up = up.idxmax(); i_dn = dn.idxmax()
    t_up = wsec.loc[i_up] - t_ev; t_dn = wsec.loc[i_dn] - t_ev
    # realized vol: per-minute tick RV = sqrt(sum dmid^2); travel = sum |dmid|
    dmid = f["mid_last"].diff()
    minute = (sec // 60).astype(int)
    rv = pd.DataFrame({"minute": minute, "d2": dmid ** 2, "ad": dmid.abs(),
                       "sp": f["spread_t"], "alive": f["alive"], "mid": f["mid_last"]})
    per_min = rv.groupby("minute").agg(
        rv_t=("d2", lambda x: float(np.sqrt(np.nansum(x)))),
        travel_t=("ad", "sum"),
        sp_med=("sp", "median"),
        sp_p90=("sp", lambda x: float(np.nanquantile(x.dropna(), 0.9)) if x.notna().any() else np.nan),
        alive_frac=("alive", "mean"),
        mid_close=("mid", "last")).reset_index()
    ev_min0 = t_ev // 60
    win_min = per_min[(per_min["minute"] >= ev_min0) & (per_min["minute"] < win_end // 60)]
    if time_et == "08:30":
        base_pre = per_min[(per_min["minute"] >= 7 * 60) & (per_min["minute"] < 8 * 60 + 15)]
        base_rth = per_min[(per_min["minute"] >= 9 * 60 + 45) & (per_min["minute"] < 16 * 60)]
        base_pre_name, base_rth_name = "pre 07:00-08:15", "RTH 09:45-16:00"
    else:
        base_pre = per_min[(per_min["minute"] >= 9 * 60 + 30) & (per_min["minute"] < 13 * 60 + 45)]
        base_rth = per_min[(per_min["minute"] >= 14 * 60 + 30) & (per_min["minute"] < 16 * 60)]
        base_pre_name, base_rth_name = "RTH 09:30-13:45 (pre-event)", "post 14:30-16:00"

    # spread trajectory sub-windows (minutes rel. to event)
    sub = ([(-15, 0), (0, 1), (1, 5), (5, 15), (15, 45), (45, 75)]
           if time_et == "08:30" else [(-15, 0), (0, 1), (1, 5), (5, 15), (15, 30)])
    sp_traj = {}
    for a, b in sub:
        m = rv[(sec >= t_ev + a * 60) & (sec < t_ev + b * 60)]
        sp_traj[f"sp_med[{a},{b})"] = float(np.nanmedian(m["sp"])) if m["sp"].notna().any() else np.nan

    row = dict(session=tag, event=event, time_et=time_et,
               ref_mid_ticks=float(ref), ref_price_pts=float(ref) / 4.0,
               max_up_t=float(up.max()), t_max_up_s=int(t_up),
               max_dn_t=float(dn.max()), t_max_dn_s=int(t_dn),
               win_close_delta_t=float(win["mid_last"].iloc[-1] - ref),
               rv_win_per_min=float(win_min["rv_t"].mean()),
               rv_base_pre=float(base_pre["rv_t"].mean()),
               rv_base_rth=float(base_rth["rv_t"].mean()),
               rv_ratio_vs_pre=float(win_min["rv_t"].mean() / base_pre["rv_t"].mean()),
               rv_ratio_vs_rth=float(win_min["rv_t"].mean() / base_rth["rv_t"].mean()),
               alive_frac_win=float(win["alive"].mean()),
               **sp_traj, **{k: float(v) for k, v in path.items()})
    sess_rows.append(row)

    pm = per_min[(per_min["minute"] >= ev_min0 - 15) & (per_min["minute"] < win_end // 60)].copy()
    pm.insert(0, "session", tag); pm.insert(1, "event", event)
    pm["min_rel"] = pm["minute"] - ev_min0
    pm["mid_delta_t"] = pm["mid_close"] - ref
    min_rows.append(pm)

    print(f"\n--- {tag}  {event} {time_et} ET  (window {'08:30-09:45' if time_et=='08:30' else '14:00-14:30'}) ---")
    print(f"  ref mid (last pre-event second): {ref:.1f} ticks = {ref/4.0:.2f} pts")
    print("  path (mid delta from ref, ticks): " +
          "  ".join(f"+{o}s:{path[f'd{o}s']:+.1f}" for o in offs))
    print(f"  max excursion: UP +{up.max():.1f}t @ +{int(t_up)}s | DOWN -{dn.max():.1f}t @ +{int(t_dn)}s"
          f" | window close {win['mid_last'].iloc[-1]-ref:+.1f}t")
    print("  spread_t median by sub-window (min rel event): " +
          "  ".join(f"[{a},{b}):{sp_traj[f'sp_med[{a},{b})']:.1f}" for a, b in sub))
    print(f"  realized vol (per-minute tick RV): window {win_min['rv_t'].mean():.1f}"
          f" vs {base_pre_name} {base_pre['rv_t'].mean():.1f} (x{win_min['rv_t'].mean()/base_pre['rv_t'].mean():.1f})"
          f" vs {base_rth_name} {base_rth['rv_t'].mean():.1f} (x{win_min['rv_t'].mean()/base_rth['rv_t'].mean():.1f})")
    print(f"  quote-alive fraction in window: {win['alive'].mean():.3f}")

pd.DataFrame(sess_rows).to_csv(os.path.join(OUTD, "w7e1_tick_sessions.csv"), index=False)
pd.concat(min_rows, ignore_index=True).to_csv(os.path.join(OUTD, "w7e1_tick_minutes.csv"), index=False)
print("\n[DESCRIPTIVE ONLY — n=%d event sessions (3 pre-RTH 08:30 + 1 FOMC 14:00); "
      "no kill/pass verdict is possible or claimed at this n.]" % len(sess_rows))

# ---------------------------------------------------------------------------
# (b) MINUTE-POWERED — Program-B study on the 3-min CSV, dev window only
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("(b) MINUTE-POWERED — initial-reaction continuation, 3-min CSV, dev window")
print("=" * 78)

bars = pd.read_csv(CSV, usecols=["time", "close"])
bars["time"] = pd.to_datetime(bars["time"])
n_all = len(bars)
bars = bars[bars["time"] < pd.Timestamp("2026-06-01")].reset_index(drop=True)  # DEV GUARD
print(f"CSV rows read {n_all}, kept {len(bars)} (< 2026-06-01), "
      f"range {bars['time'].iloc[0]} -> {bars['time'].iloc[-1]}")
bars["date"] = bars["time"].dt.date
bars["tod"] = bars["time"].dt.hour * 3600 + bars["time"].dt.minute * 60 + bars["time"].dt.second

# release-day sets (dev window). Signal is anchored at the 08:30 release =>
# primary release set = 08:30 events (NFP/CPI). FOMC 14:00 days are NOT 08:30-release
# days: excluded from both primary and placebo, reported separately as sensitivity.
cal_dev = cal[cal["date"] < pd.Timestamp("2026-06-01").date()]
d830 = set(cal_dev.loc[cal_dev["time_et"] == "08:30", "date"])
d1400 = set(cal_dev.loc[cal_dev["time_et"] == "14:00", "date"])
fomc_only = d1400 - d830
any_ev = d830 | d1400
print(f"Dev-window calendar days: 08:30-release {len(d830)}, FOMC 14:00 {len(d1400)}, "
      f"overlap (both same day) {len(d830 & d1400)}, FOMC-only {len(fomc_only)}")

T_PRE, T_ENT = 8 * 3600 + 30 * 60, 9 * 3600 + 30 * 60
EXITS = {15: T_ENT + 15 * 60, 30: T_ENT + 30 * 60, 60: T_ENT + 60 * 60}

trades = []
skip = {"no_pre": 0, "no_entry": 0, "no_exit": 0, "zero_sig": 0}
for date, day in bars.groupby("date", sort=True):
    if pd.Timestamp(date).weekday() >= 5:
        continue
    tod = day["tod"].values; close = day["close"].values
    # pre-release bar: LAST bar end-stamped strictly before 08:30 (guard: >= 08:00)
    pre_ix = np.where((tod < T_PRE) & (tod >= 8 * 3600))[0]
    if len(pre_ix) == 0:
        skip["no_pre"] += 1; continue
    pre_close = close[pre_ix[-1]]; pre_tod = tod[pre_ix[-1]]
    # entry: bar end-stamped exactly 09:30 (close = price at the 09:30 RTH open)
    ent_ix = np.where(tod == T_ENT)[0]
    if len(ent_ix) == 0:
        skip["no_entry"] += 1; continue
    ent = close[ent_ix[0]]
    sig = np.sign(ent - pre_close)
    if sig == 0:
        skip["zero_sig"] += 1; continue
    row = dict(date=date, pre_tod=pre_tod, pre_close=pre_close, entry=ent, signal=int(sig),
               group=("release" if date in d830 else "fomc_only" if date in fomc_only
                      else "placebo"))
    ok = True
    for h, tx in EXITS.items():
        ex_ix = np.where((tod <= tx) & (tod > T_ENT))[0]
        if len(ex_ix) == 0:
            ok = False; break
        row[f"exit{h}_tod"] = tod[ex_ix[-1]]
        row[f"net{h}"] = sig * (close[ex_ix[-1]] - ent) / TICK - C1
        row[f"gross{h}"] = sig * (close[ex_ix[-1]] - ent) / TICK
    if not ok:
        skip["no_exit"] += 1; continue
    trades.append(row)

T = pd.DataFrame(trades)
T.to_csv(os.path.join(OUTD, "w7e1_minute_trades.csv"), index=False)
print(f"Days simulated: {len(T)} | skipped: {skip}")
print("Group counts:", T["group"].value_counts().to_dict())
pre_tods = T["pre_tod"].value_counts().head(4)
print("Pre-release bar end-stamp distribution (top):",
      {f"{v//3600:02d}:{(v%3600)//60:02d}": int(c) for v, c in pre_tods.items()})

rng = np.random.default_rng(SEED)


def boot_ci(x, rng, nboot=NBOOT):
    """Day-clustered bootstrap CI of the mean (one trade per day => day resampling)."""
    x = np.asarray(x, float); n = len(x)
    if n == 0:
        return np.nan, np.nan
    means = np.array([x[rng.integers(0, n, n)].mean() for _ in range(nboot)])
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


summary = []
print(f"\n=== pooled by group x horizon (net C1={C1}t; day-clustered 95% CI, "
      f"{NBOOT} reps, seed {SEED}) ===")
print(f"{'group':>10} {'h':>4} {'n':>5} {'netC1_t':>8} {'CI_lo':>8} {'CI_hi':>8} "
      f"{'gross_t':>8} {'win%':>6}")
for grp in ("release", "placebo", "fomc_only"):
    G = T[T["group"] == grp]
    for h in (15, 30, 60):
        x = G[f"net{h}"].values
        lo, hi = boot_ci(x, rng)
        wr = float((x > 0).mean()) if len(x) else np.nan
        summary.append(dict(scope="pooled", group=grp, horizon=h, n=len(x),
                            net_c1_t=float(np.mean(x)) if len(x) else np.nan,
                            ci_lo=lo, ci_hi=hi,
                            gross_t=float(G[f"gross{h}"].mean()) if len(x) else np.nan,
                            win_rate=wr))
        print(f"{grp:>10} {h:>4} {len(x):>5} {np.mean(x):>+8.3f} {lo:>+8.3f} {hi:>+8.3f} "
              f"{G[f'gross{h}'].mean():>+8.3f} {100*wr:>5.1f}")

print("\n=== release days by year (net C1 ticks) ===")
Trel = T[T["group"] == "release"].copy()
Trel["year"] = pd.to_datetime(Trel["date"]).dt.year
Tpla = T[T["group"] == "placebo"].copy()
Tpla["year"] = pd.to_datetime(Tpla["date"]).dt.year
print(f"{'year':>6} {'h':>4} {'n':>4} {'netC1_t':>8} {'CI_lo':>8} {'CI_hi':>8} {'win%':>6}"
      f"   | placebo: {'n':>4} {'netC1_t':>8}")
for y in sorted(Trel["year"].unique()):
    Gy = Trel[Trel["year"] == y]; Py = Tpla[Tpla["year"] == y]
    for h in (15, 30, 60):
        x = Gy[f"net{h}"].values
        lo, hi = boot_ci(x, rng)
        summary.append(dict(scope=f"year{y}", group="release", horizon=h, n=len(x),
                            net_c1_t=float(np.mean(x)), ci_lo=lo, ci_hi=hi,
                            gross_t=float(Gy[f"gross{h}"].mean()),
                            win_rate=float((x > 0).mean())))
        px = Py[f"net{h}"].values
        summary.append(dict(scope=f"year{y}", group="placebo", horizon=h, n=len(px),
                            net_c1_t=float(np.mean(px)) if len(px) else np.nan,
                            ci_lo=np.nan, ci_hi=np.nan,
                            gross_t=float(Py[f"gross{h}"].mean()) if len(px) else np.nan,
                            win_rate=float((px > 0).mean()) if len(px) else np.nan))
        print(f"{y:>6} {h:>4} {len(x):>4} {np.mean(x):>+8.3f} {lo:>+8.3f} {hi:>+8.3f} "
              f"{100*(x>0).mean():>5.1f}   | {len(px):>4} {np.mean(px):>+8.3f}")

S = pd.DataFrame(summary)
S.to_csv(os.path.join(OUTD, "w7e1_minute_summary.csv"), index=False)

# frozen verdict rule
print("\n=== FROZEN VERDICT RULE (spec W7-3b) ===")
rel = S[(S["scope"] == "pooled") & (S["group"] == "release")]
pla = S[(S["scope"] == "pooled") & (S["group"] == "placebo")]
promising_h = []
for h in (15, 30, 60):
    r = rel[rel["horizon"] == h].iloc[0]
    p = pla[pla["horizon"] == h].iloc[0]
    cond = (r["net_c1_t"] > 0) and (r["ci_lo"] > 0)
    placebo_comparable = (p["net_c1_t"] > 0) and (p["ci_lo"] > 0)
    print(f"  h={h}: release net={r['net_c1_t']:+.3f} CI_lo={r['ci_lo']:+.3f} -> "
          f"{'POS' if cond else 'no'}; placebo net={p['net_c1_t']:+.3f} "
          f"CI_lo={p['ci_lo']:+.3f} -> comparable={placebo_comparable}")
    if cond and not placebo_comparable:
        promising_h.append(h)
verdict = "PROMISING" if promising_h else "NEGATIVE"
print(f"VERDICT (b): {verdict}" +
      (f" at horizons {promising_h}" if promising_h else
       " — no horizon has net C1 > 0 with CI_lo > 0 absent a comparable placebo effect"))
print("\nZone-F variant (5-120 s event-anchored tick-resolution scalp at the release):"
      "\n  UNTESTABLE-IN-CURRENT-TICK-SAMPLE — the discovery substrate holds only 4"
      "\n  event sessions (3 pre-RTH 08:30 + 1 FOMC 14:00); recorded either way per spec.")
print("\nW7E1 DONE")
