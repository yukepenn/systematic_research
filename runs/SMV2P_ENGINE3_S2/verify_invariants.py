"""SMV2P invariant checks over out/*.csv — writes out/verify_invariants.txt.
Recomputes VA bands for a sample of sessions and checks structural invariants
of every event row. Any FAIL line means the executor has a bug."""
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "src/analytics")
from sm01_solarsim import TICK, load_bars_3m

RUN = "runs/SMV2P_ENGINE3_S2"
OUT = f"{RUN}/out"
DEV_END = pd.Timestamp("2026-05-31")

lines = []
def chk(name, ok, detail=""):
    lines.append(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")

bars = load_bars_3m()
bars["sd"] = pd.to_datetime(bars["sess_date"])
bars = bars[bars["sd"] <= DEV_END].reset_index(drop=True)
t = pd.to_datetime(bars["time"])
bars["hm"] = t.dt.hour * 100 + t.dt.minute

rth = {}
for sd, g in bars.groupby("sd", sort=True):
    r = g[(g["hm"] >= 933) & (g["hm"] <= 1600)]
    if len(r):
        rth[sd] = r
ALL_SD = sorted(rth.keys() | set(bars["sd"].unique()))
ALL_SD = sorted(set(bars["sd"]))
POS = {sd: i for i, sd in enumerate(ALL_SD)}

# ------------------------------------------------------------------- e377
ev = pd.read_csv(f"{OUT}/e377_events.csv", parse_dates=["sd"])
chk("e377 val<=vah", bool((ev["val"] <= ev["vah"]).all()))
out_ok = ((ev["open0930"] > ev["vah"]) & (ev["dir"] == -1)) | \
         ((ev["open0930"] < ev["val"]) & (ev["dir"] == 1))
chk("e377 open outside VA & dir matches side", bool(out_ok.all()))
chk("e377 entry after acceptance", bool((ev["entry_hm"] > ev["accept_hm"]).all()))
chk("e377 exit_hm<=1554", bool((ev["exit_hm"] <= 1554).all()))
pts_ok = np.allclose(ev["pts"], ev["dir"] * (ev["exit_px"] - ev["entry_px"]))
chk("e377 pts identity", pts_ok)
chk("e377 net identity", np.allclose(ev["net"], ev["pts"] * 20.0 - 4.36))
chk("e377 one event/session", bool(ev["sd"].is_unique))
# VA recompute on 25 sampled events
rng = np.random.default_rng(20260808)
bad = 0
for _, e in ev.iloc[rng.choice(len(ev), 25, replace=False)].iterrows():
    p = ALL_SD[POS[e["sd"]] - 1]
    r = rth.get(p)
    if r is None:
        bad += 1; continue
    c = r["close"].to_numpy(float); v = r["volume"].to_numpy(float)
    tot = v.sum()
    k = np.round(c / TICK).astype(np.int64)
    hist = pd.Series(v).groupby(k).sum()
    klo, khi = int(round(e["val"] / TICK)), int(round(e["vah"] / TICK))
    inband = hist[(hist.index >= klo) & (hist.index <= khi)].sum()
    vwap = float((c * v).sum() / tot)
    k0 = min(max(int(np.floor(vwap / TICK)), int(k.min())), int(k.max()))
    if inband < 0.70 * tot - 1e-6 or not (klo <= k0 <= khi):
        bad += 1
chk("e377 VA recompute (25 samples): band holds >=70% vol & contains VWAP bin",
    bad == 0, f"bad={bad}")

# ------------------------------------------------------------------- e378
ev = pd.read_csv(f"{OUT}/e378_events.csv",
                 parse_dates=["sd_break", "sd_reclaim", "sd", "sd_exit"])
brk_ok = ((ev["dir"] == -1) & (ev["break_close"] > ev["rng_hi"])) | \
         ((ev["dir"] == 1) & (ev["break_close"] < ev["rng_lo"]))
chk("e378 break beyond frozen range & dir fades it", bool(brk_ok.all()))
chk("e378 reclaim close strictly inside range",
    bool(((ev["reclaim_close"] > ev["rng_lo"]) & (ev["reclaim_close"] < ev["rng_hi"])).all()))
chk("e378 target = range midpoint",
    np.allclose(ev["target"], 0.5 * (ev["rng_lo"] + ev["rng_hi"])))
gap_rb = ev.apply(lambda r: POS[r["sd_reclaim"]] - POS[r["sd_break"]], axis=1)
chk("e378 reclaim within 2 sessions of break", bool(gap_rb.isin([1, 2]).all()))
gap_er = ev.apply(lambda r: POS[r["sd"]] - POS[r["sd_reclaim"]], axis=1)
chk("e378 entry = next session after reclaim", bool((gap_er == 1).all()))
chk("e378 sessions_held in 1..3", bool(ev["sessions_held"].isin([1, 2, 3]).all()))
ev2 = ev.sort_values("entry_gidx")
chk("e378 no overlapping positions",
    bool((ev2["entry_gidx"].iloc[1:].to_numpy() > ev2["exit_gidx"].iloc[:-1].to_numpy()).all()))
chk("e378 pts identity", np.allclose(ev["pts"], ev["dir"] * (ev["exit_px"] - ev["entry_px"])))
chk("e378 net identity", np.allclose(ev["net"], ev["pts"] * 20.0 - 4.36))
mtm = pd.read_csv(f"{OUT}/e378_daily_mtm.csv", index_col=0)
chk("e378 MTM total == event total",
    np.isclose(mtm.iloc[:, 0].sum(), ev["net"].sum()),
    f"{mtm.iloc[:, 0].sum():.2f} vs {ev['net'].sum():.2f}")

# ------------------------------------------------------------------- e379
ev = pd.read_csv(f"{OUT}/e379_events.csv", parse_dates=["sd"])
chk("e379 sign = -sign(MTD)", bool((ev["sign"] == -np.sign(ev["mtd_pts"])).all()))
last2 = set()
S_ = bars.groupby("sd", as_index=False).last()
S_["ym"] = S_["sd"].dt.to_period("M")
for m, g in S_.groupby("ym"):
    for sd in g["sd"].iloc[-2:]:
        last2.add(sd)
chk("e379 all events on last-2 sessions of their month", bool(ev["sd"].isin(last2).all()))
chk("e379 2 day-events per month", bool((ev.groupby("month").size() == 2).all()))
chk("e379 net identity", np.allclose(ev["net"], ev["pts"] * 20.0 - 4.36))
chk("e379 N months = 52 (2022-02..2026-05)", ev["month"].nunique() == 52,
    f"months={ev['month'].nunique()}")
h = pd.read_csv(f"{OUT}/e379_hist_check.csv", parse_dates=["sd_sig", "sd_end"])
chk("e379 hist sign = -sign(MTD)", bool((h["sign"] == -np.sign(h["mtd_pts"])).all()))
chk("e379 hist signed identity", np.allclose(h["signed_pts"], h["sign"] * h["win_pts"]))
chk("e379 hist months = 191", len(h) == 191, f"n={len(h)}")
chk("e379 hist window <= 2021-12-31", bool(h["sd_end"].max() <= pd.Timestamp("2021-12-31")))

# ------------------------------------------------------------------- VIRGIN
chk("VIRGIN: no event/exit date >= 2026-06-01 in any event file", True)
for f, cols in (("e377_events.csv", ["sd"]), ("e378_events.csv", ["sd", "sd_exit"]),
                ("e379_events.csv", ["sd"])):
    d = pd.read_csv(f"{OUT}/{f}")
    for c in cols:
        mx = pd.to_datetime(d[c]).max()
        chk(f"  {f}:{c} max={mx.date()}", mx <= DEV_END)

txt = "\n".join(lines)
open(f"{OUT}/verify_invariants.txt", "w").write(txt + "\n")
print(txt)
print("\nFAILURES:", sum(1 for l in lines if l.startswith("FAIL")))
