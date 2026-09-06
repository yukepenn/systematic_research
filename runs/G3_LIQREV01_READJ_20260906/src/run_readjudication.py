#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G3_LIQREV01_READJ_20260906 -- regime-local standalone re-adjudication of the frozen
LIQREV01 s90_q20 object. Executes DESIGN_FROZEN.md (sha 45fedf86...) EXACTLY.
Zero retuning: D1 replicates research/system_master/LIQREV01_STRESS_REVERSAL/src/01_liqrev01.py
verbatim (all constants byte-frozen) and sha-matches the canonical trade table; D2-D8 are
read-only computations on that reproduced ledger. Every gate printed BY THIS PROGRAM.

Evidence status: DISCOVERY_CONSUMED throughout (the object was selected on this window).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "G3_LIQREV01_READJ_20260906")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, ROOT)

from research_sdk import eval_battery  # noqa: E402

# ---------------------------------------------------------------- frozen constants (dev)
SEED = 20260819
NB = 10_000
TICK = 0.25
PV = 20.0
COMM_SIDE = 2.18
RT_COST = 2 * COMM_SIDE
STRESS_PCT = 0.90
QLO, QHI = 0.20, 0.80
VOL_WIN, PCT_WIN, RET_WIN = 5, 252, 63

SUBSTRATE = os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                         "nq1m_2005_202605.parquet")
CANON_TRADES = os.path.join(ROOT, "research", "system_master", "LIQREV01_STRESS_REVERSAL",
                            "out", "liqrev01_trades.csv")
P1_DAILY = os.path.join(ROOT, "runs", "WE_W56_BREADTH", "out", "p1_daily.csv")

POOL_FULL = 51_891.0
LIVE_ACCT = 10_206.0
BAR_WORST_TRADE_MNQ = 0.05 * POOL_FULL     # 2594.55
BAR_MAXDD_MNQ = 0.15 * POOL_FULL           # 7783.65

LOG_LINES = []


def log(s=""):
    print(s, flush=True)
    LOG_LINES.append(s)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def money(x):
    return ("-$" if x < 0 else "+$") + f"{abs(x):,.2f}"


# =========================================================================================
log("=" * 96)
log("G3_LIQREV01_READJ_20260906 -- LIQREV01 regime-local standalone re-adjudication")
log("DESIGN_FROZEN.md sha256 = 45fedf86bf0a209dd5571a2797f6cb51078634df3c251e5566d3ea3ce775cb79")
log("Evidence status: DISCOVERY_CONSUMED throughout. Seed %d, %d bootstrap reps." % (SEED, NB))
log("=" * 96)

# ---------------------------------------------------------------- seal + pool checks (S1)
log("\n[S1] DATA SEAL + FROZEN-POOL INTERSECTION CHECK (OQ-8 rule)")
sub_sha = sha256_file(SUBSTRATE)
log("  substrate: %s" % SUBSTRATE)
log("  sha256 = %s (asserting prefix dfd017ef)" % sub_sha)
assert sub_sha.startswith("dfd017ef"), "SUBSTRATE SHA DRIFT -- STOP"

log("[LIQREV01-repro] loading minute substrate ...")
df = pd.read_parquet(SUBSTRATE)
df["time"] = pd.to_datetime(df["time"])
max_day = df["time"].dt.date.max()
log("  max bar date in substrate       %s" % max_day)
assert str(max_day) < "2026-08-01", "SEAL VIOLATION: data >= 2026-08-01 present"
log("  ASSERT max session < 2026-08-01   PASS")

log("  Files READ by this run: [substrate parquet (materialized 2026-08, non-pool),")
log("    canonical liqrev01_trades.csv artifact, hist_calendar_2005_2021.csv,")
log("    w8bfade_trades.csv (release-date list), runs/WE_W56_BREADTH/out/p1_daily.csv].")
log("  Frozen-pool registers (runs/G2_WAVE5_CARDS_20260906/BBO_GOVERNANCE_MEMO.md; the")
log("    design's 'research/genesis2/' path does not exist -- actual location disclosed):")
log("    W5 PROTECTED 168 / MICRO_BLIND 141 / BBO_BLIND 19 / ESNQ_BLIND 15 are all TICK/BBO")
log("    session pools over 2025-08-13 -> 2026-07-31. This run reads NO tick/BBO file and")
log("    extracts NO new session; input-file-list  INTERSECT  pool-member-file-lists = EMPTY.")
log("  Disclosure (OQ-8 spirit): the minute LAST-price substrate predates the pools and its")
log("    calendar range overlaps pool member DATES; its Last-price minute content was already")
log("    materialized and consumed by the original 2026-08-19 run -- no NEW exposure created.")
log("  No blind/frozen pool touched: PASS")

# =========================================================================================
# D1 -- VERBATIM replication of research/system_master/LIQREV01_STRESS_REVERSAL/src/01_liqrev01.py
# (code below copied from the frozen dev source; only OUT paths differ)
# =========================================================================================
log("\n[D1] REPRODUCING THE FROZEN TRADE TABLE (verbatim dev pipeline) ...")

df["d"] = df["time"].dt.date
hm = df["time"].dt.hour * 100 + df["time"].dt.minute
rth = df[(hm >= 930) & (hm <= 1558)].copy()

g = rth.groupby("d")
nbars = g.size()
valid_days = nbars[nbars >= 200].index
sess_close = g["close"].last().loc[valid_days]


def day_rv2(sub):
    r = sub["close"].diff().dropna()
    return float((r * r).sum())


rv2 = g.apply(day_rv2, include_groups=False).loc[valid_days]

D = pd.DataFrame({"close": sess_close, "rv2": rv2}).sort_index()
D.index = pd.to_datetime(pd.Index(D.index))
D["ret"] = D["close"].diff()
D["rv5"] = np.sqrt(D["rv2"].rolling(VOL_WIN).sum())

rv5 = D["rv5"].to_numpy()
n = len(D)
pct = np.full(n, np.nan)
for i in range(PCT_WIN - 1, n):
    w = rv5[i - PCT_WIN + 1:i + 1]
    if np.isnan(w).any():
        continue
    pct[i] = (w <= rv5[i]).mean()
D["rv5_pct"] = pct

D["q20"] = D["ret"].rolling(RET_WIN).quantile(QLO).shift(1)
D["q80"] = D["ret"].rolling(RET_WIN).quantile(QHI).shift(1)

mu = D["ret"].rolling(120, min_periods=40).mean().shift(1)
sd = D["ret"].rolling(120, min_periods=40).std().shift(1)
D["gap_flag"] = ((D["ret"] - mu).abs() / sd) > 6

rel = set()
cal = pd.read_csv(os.path.join(ROOT, "research", "scalping_lab", "data",
                               "hist_calendar_2005_2021.csv"))
rel |= set(pd.to_datetime(cal["date"]).dt.normalize())
try:
    w8 = pd.read_csv(os.path.join(ROOT, "research", "scalping_lab", "artifacts",
                                  "w8_bfade", "w8bfade_trades.csv"))
    w8r = w8[w8["group"].astype(str).str.lower() != "placebo"]
    rel |= set(pd.to_datetime(w8r["date"]).dt.normalize())
    rel_src = "hist_calendar(2005-2021) + w8bfade release rows (2022+)"
except Exception as e:
    rel_src = f"hist_calendar only (w8bfade load failed: {e})"
log("  release source: %s" % rel_src)


def build_trades(stress_pct, qlo, qhi, stress=True, hold=1):
    ql = D["ret"].rolling(RET_WIN).quantile(qlo).shift(1)
    qh = D["ret"].rolling(RET_WIN).quantile(qhi).shift(1)
    in_state = (D["rv5_pct"] >= stress_pct) if stress else (D["rv5_pct"] < stress_pct)
    sig_long = in_state & (D["ret"] <= ql)
    sig_short = in_state & (D["ret"] >= qh)
    rows = []
    closes = D["close"].to_numpy()
    idx = D.index
    for i in range(n - hold):
        if not (sig_long.iloc[i] or sig_short.iloc[i]):
            continue
        side = 1 if sig_long.iloc[i] else -1
        entry = closes[i] + side * TICK
        exitp = closes[i + hold] - side * TICK
        pnl = side * (exitp - entry) * PV - RT_COST
        rows.append({"entry_date": idx[i], "exit_date": idx[i + hold], "side": side,
                     "pnl": pnl, "gap_flag_window": bool(D["gap_flag"].iloc[i + 1:i + hold + 1].any()),
                     "release_entry": idx[i].normalize() in rel})
    return pd.DataFrame(rows)


T = build_trades(STRESS_PCT, QLO, QHI, stress=True, hold=1)
repro_path = os.path.join(OUT, "liqrev01_trades_repro.csv")
T.to_csv(repro_path, index=False)
sha_repro = sha256_file(repro_path)
sha_canon = sha256_file(CANON_TRADES)
d1_pass = (sha_repro == sha_canon)
log("  canonical artifact sha256 = %s" % sha_canon)
log("  reproduction       sha256 = %s" % sha_repro)
log("  D1 (repro sha match): %s" % ("PASS" if d1_pass else "FAIL -- ENVIRONMENT DRIFT, STOP"))

GATES = []  # (gate, spec, observed, passfail)
GATES.append(("D1 repro", "regenerated trade-table sha == canonical artifact sha",
              "repro %s / canon %s" % (sha_repro[:16], sha_canon[:16]),
              "PASS" if d1_pass else "FAIL"))

if not d1_pass:
    log("\nD1 FAILED: the run does NOT adjudicate. Escalating as environment drift (DEFECT).")
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG_LINES))
    sys.exit(3)

# ---------------------------------------------------------------- windows + episode machinery
ENTRY = pd.to_datetime(T["entry_date"])
W2020 = T[ENTRY >= "2020-01-01"].reset_index(drop=True)
W2021 = T[ENTRY >= "2021-01-01"].reset_index(drop=True)
sess_pos = {d: i for i, d in enumerate(D.index)}

# SPEC-CONFORMANT episodes: maximal runs of STRESS SESSIONS with session gaps <= 5
stress_days = D.index[D["rv5_pct"] >= STRESS_PCT]
stress_idx = np.array([sess_pos[d] for d in stress_days])
ep_id_of_day = {}
eid = -1
prev = None
for k, si in enumerate(stress_idx):
    if prev is None or si - prev > 5:
        eid += 1
    ep_id_of_day[stress_days[k]] = eid
    prev = si
n_stress_episodes_all = eid + 1


def episode_arrays_spec(trades):
    """SPEC-conformant: trades grouped by the stress-session episode of their ENTRY day."""
    tt = trades.copy()
    tt["ep"] = tt["entry_date"].map(ep_id_of_day)
    assert tt["ep"].notna().all(), "trade entry day not a stress day?!"
    groups = [grp["pnl"].to_numpy() for _, grp in tt.groupby("ep")]
    return tt, groups


def episode_arrays_dev(trades):
    """DEV definition (disclosed deviation): maximal runs of TRADES with entry gaps <= 5 sessions."""
    td = trades.sort_values("entry_date").reset_index(drop=True)
    si = td["entry_date"].map(lambda d: sess_pos[d]).to_numpy()
    eps, cur = [], [0]
    for j in range(1, len(td)):
        if si[j] - si[j - 1] <= 5:
            cur.append(j)
        else:
            eps.append(cur)
            cur = [j]
    eps.append(cur)
    pnl = td["pnl"].to_numpy()
    return td, [pnl[e] for e in eps]


def boot_ci_episode(groups, seed=SEED, nb=NB):
    rng = np.random.default_rng(seed)
    m = np.empty(nb)
    ne = len(groups)
    for k in range(nb):
        pick = rng.integers(0, ne, ne)
        s = np.concatenate([groups[p] for p in pick])
        m[k] = s.mean()
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), ne


def max_dd_path(x):
    c = np.cumsum(np.asarray(x, float))
    z = np.concatenate([[0.0], c])
    return float(np.max(np.maximum.accumulate(z) - z))


# =========================================================================================
log("\n[D2] POST-2020 ECONOMICS (W2020: entries 2020-01-01 -> 2026-05-29)")
w0, w1 = pd.Timestamp("2020-01-01"), pd.Timestamp("2026-05-29")
weeks_span = (w1 - w0).days / 7.0
net20 = float(W2020["pnl"].sum())
npt20 = float(W2020["pnl"].mean())
log("  trade count                       %d  (expected 154)" % len(W2020))
log("  net (1 NQ)                        %s" % money(net20))
log("  $/trade                           %s" % money(npt20))
log("  $/wk over the %.1f-wk window     %s" % (weeks_span, money(net20 / weeks_span)))

# weekly grid (exit-date attributed, zero weeks included) -- lead metric via eval_battery
wk_index = pd.period_range(w0, w1, freq="W-SUN")
exd = pd.to_datetime(W2020["exit_date"])
wk_of = exd.dt.to_period("W-SUN")
wk_pnl = pd.Series(0.0, index=wk_index)
wk_sum = W2020.groupby(wk_of)["pnl"].sum()
wk_pnl.loc[wk_sum.index] = wk_sum.values
wk_arr = wk_pnl.to_numpy()
res_native = eval_battery.evaluate(wk_arr, wk_arr)  # native basis, same grid
wk_sharpe = float(wk_arr.mean() / wk_arr.std(ddof=1) * np.sqrt(52))
log("  weekly grid: %d weeks, %d non-zero; eval_battery native income  $%.2f/wk" %
    (len(wk_arr), int((wk_arr != 0).sum()), res_native["native"]))
log("  WEEKLY-VOL SHARPE (lead metric, annualized sqrt(52))   %.3f" % wk_sharpe)
log("  (No fixed-DD or fixed-CDaR improvement claim is made anywhere in this run, so no")
log("   thinning placebo is owed; maxDD below is a DESCRIPTOR, never a selection denominator.)")

mdd20_nq = max_dd_path(W2020["pnl"].to_numpy())
log("  trade-level-equity maxDD (1 NQ)   %s   [descriptor]" % money(-mdd20_nq))
log("  trade-level-equity maxDD (1 MNQ)  %s   [descriptor]" % money(-mdd20_nq / 10))

tt20, groups20_spec = episode_arrays_spec(W2020)
_, groups20_dev = episode_arrays_dev(W2020)
lo_s, hi_s, ne_s = boot_ci_episode(groups20_spec)
lo_d, hi_d, ne_d = boot_ci_episode(groups20_dev)
log("  episode definitions (BOTH printed; dev deviation disclosed):")
log("    SPEC-conformant: maximal runs of STRESS SESSIONS (rv5_pct>=0.90) with session")
log("      gaps <= 5; trade -> episode of its entry session. %d stress episodes exist" %
    n_stress_episodes_all)
log("      full-sample; %d contain W2020 trades." % ne_s)
log("    DEV (01_liqrev01.py): maximal runs of TRADES with entry gaps <= 5 sessions --")
log("      a deviation from SPEC wording (merges nothing across trade droughts inside a")
log("      stress run; splits stress runs whose interior days produced no trade).")
log("  episode-block bootstrap, %d reps, seed %d:" % (NB, SEED))
log("    SPEC-conformant episodes (n=%d): $/trade CI [%s, %s]" % (ne_s, money(lo_s), money(hi_s)))
log("    DEV episodes           (n=%d): $/trade CI [%s, %s]" % (ne_d, money(lo_d), money(hi_d)))
d2_pass = lo_s > 0
log("  D2 GATE (SPEC-episode CI_lo > 0 on W2020): CI_lo = %s -> %s" %
    (money(lo_s), "PASS" if d2_pass else "FAIL"))
GATES.append(("D2 W2020 economics", "episode-block bootstrap CI_lo > 0 (seed 20260819, 10k)",
              "CI_lo %s (dev-def CI_lo %s)" % (money(lo_s), money(lo_d)),
              "PASS" if d2_pass else "FAIL"))

# =========================================================================================
log("\n[D3] EPISODE DEPENDENCE / NOT-A-LOTTERY")
ep_rows = []
for e, grp in tt20.groupby("ep"):
    days = [d for d, i in ep_id_of_day.items() if i == e]
    ep_rows.append({"episode_id": int(e),
                    "first_stress_day": min(days).date(), "last_stress_day": max(days).date(),
                    "first_entry": grp["entry_date"].min().date(),
                    "last_entry": grp["entry_date"].max().date(),
                    "n_trades": int(len(grp)), "net": float(grp["pnl"].sum())})
EP = pd.DataFrame(ep_rows).sort_values("episode_id").reset_index(drop=True)
EP.to_csv(os.path.join(OUT, "episode_table.csv"), index=False)
srt_ep = EP.sort_values("net", ascending=False)
top1 = float(srt_ep["net"].iloc[0])
top3 = float(srt_ep["net"].head(3).sum())
log("  W2020 episodes (SPEC-conformant, ALL %d listed in out/episode_table.csv):" % len(EP))
for _, r in EP.iterrows():
    log("    ep%02d  %s -> %s  n=%2d  net %s" %
        (r["episode_id"], r["first_entry"], r["last_entry"], r["n_trades"], money(r["net"])))
log("  top-1 episode share of W2020 net  %s = %.1f%%" % (money(top1), 100 * top1 / net20))
log("  top-3 episode share of W2020 net  %s = %.1f%%" % (money(top3), 100 * top3 / net20))
top3_ids = set(srt_ep["episode_id"].head(3))
groups_ex3 = [grp["pnl"].to_numpy() for e, grp in tt20.groupby("ep") if e not in top3_ids]
lo_x, hi_x, ne_x = boot_ci_episode(groups_ex3)
net_ex3 = float(sum(g.sum() for g in groups_ex3))
log("  ex-top-3-episode: net %s over %d episodes, $/trade CI [%s, %s]  (NON-GATING)" %
    (money(net_ex3), ne_x, money(lo_x), money(hi_x)))
ent_sorted = pd.to_datetime(W2020["entry_date"]).sort_values()
gaps = ent_sorted.diff().dt.days.dropna()
gmax = int(gaps.max())
gi = gaps.idxmax()
log("  drought statistics: max inter-trade entry gap in W2020 = %d days" % gmax)
log("    (%s -> %s). In words: after 2022-05-17 the stress gate went fully dark for 661" %
    (ent_sorted.loc[:gi].iloc[-2].date() if len(ent_sorted.loc[:gi]) > 1 else "-",
     ent_sorted.loc[gi].date()))
log("    days until 2024-03-08 -- calendar 2023 produced ZERO trades, as did calendar 2019.")
log("    A 1.8-year silent stretch is NORMAL for this object; absence of trades is not")
log("    regime death (D5 handles this via the 36-month lookback).")
tt21, groups21_spec = episode_arrays_spec(W2021)
lo21, hi21, ne21 = boot_ci_episode(groups21_spec)
net21 = float(W2021["pnl"].sum())
log("  W2021 (entries >= 2021-01-01, calendar COVID-exclusion): %d trades, net %s, $/t %s" %
    (len(W2021), money(net21), money(float(W2021["pnl"].mean()))))
d3_pass = lo21 > 0
log("  D3 GATE (W2021 episode-block CI_lo > 0): CI [%s, %s] over %d episodes -> %s" %
    (money(lo21), money(hi21), ne21, "PASS" if d3_pass else "FAIL"))
GATES.append(("D3 W2021 ex-COVID", "episode-block bootstrap CI_lo > 0 on entries >= 2021-01-01",
              "CI_lo %s (n_ep %d, n_trades %d)" % (money(lo21), ne21, len(W2021)),
              "PASS" if d3_pass else "FAIL"))

# =========================================================================================
log("\n[D4] TAIL AT SIZE -- deployment unit 1 MNQ ($2/pt = exactly 1/10 of the NQ ledger)")
mnq = W2020["pnl"].to_numpy() / 10.0
mnq_full = T["pnl"].to_numpy() / 10.0
worst_full_mnq = float(mnq_full.min())
worst_w20_mnq = float(mnq.min())
k5 = max(1, int(0.05 * len(mnq)))
es5_mnq = float(np.sort(mnq)[:k5].mean())
worst_ep_mnq = float(EP["net"].min() / 10.0)
mon = W2020.groupby(pd.to_datetime(W2020["exit_date"]).dt.to_period("M"))["pnl"].sum() / 10.0
worst_mon_mnq = float(mon.min())
log("  worst historical trade (FULL sample, 1 MNQ)  %s  (2025-04-03 long)" % money(worst_full_mnq))
log("  worst W2020 trade (1 MNQ)                    %s" % money(worst_w20_mnq))
log("  ES5 W2020 (mean of worst %d trades, 1 MNQ)    %s" % (k5, money(es5_mnq)))
log("  worst episode (1 MNQ)                        %s" % money(worst_ep_mnq))
log("  worst calendar month (1 MNQ, %s)        %s" % (mon.idxmin(), money(worst_mon_mnq)))

# drawdown TWO WAYS (CAP01 lesson) -- each stated in words
dd_way1 = max_dd_path(mnq)
daily_all = W2020.groupby(pd.to_datetime(W2020["exit_date"]))["pnl"].sum() / 10.0
cal_grid = D.index[(D.index >= w0) & (D.index <= w1)]
daily_grid = pd.Series(0.0, index=cal_grid)
daily_grid.loc[daily_all.index] = daily_all.values
dd_way2 = max_dd_path(daily_grid.to_numpy())
dd_check_identity = max_dd_path(np.concatenate([g for g in groups20_spec]) / 10.0)
log("  maxDD computed TWO ways (the CAP01 lesson -- each states its event in words):")
log("   WAY 1 (direct trade-path scan): the largest peak-to-trough decline of CUMULATIVE")
log("     TRADE-LEVEL equity, trades in entry order, W2020 at 1 MNQ:      %s" % money(-dd_way1))
log("   WAY 2 (calendar-daily reconstruction): the largest peak-to-trough decline of the")
log("     CALENDAR-DAY equity path (exit-date-attributed daily P&L incl. %d zero" % int((daily_grid == 0).sum()))
log("     sessions), W2020 at 1 MNQ:                                      %s" % money(-dd_way2))
log("   agreement: |way1 - way2| = $%.2f %s" % (abs(dd_way1 - dd_way2),
    "(identical event, two constructions)" if abs(dd_way1 - dd_way2) < 1e-6
    else "(differ only by same-day trade ordering inside the path; both shown)"))
log("   pipeline identity check (episode concat in original order): $%.2f" % dd_check_identity)
log("  Neither figure is 'P(losing the account)'. Each is a maximum historical drawdown of")
log("  an equity PATH -- an order statistic of this one realized sequence.")
d4a = abs(worst_full_mnq) <= BAR_WORST_TRADE_MNQ
d4b = max(dd_way1, dd_way2) <= BAR_MAXDD_MNQ
log("  D4 GATE (a): |worst historical trade @1MNQ| <= $%.2f (5.0%% of $51,891 full pool):" % BAR_WORST_TRADE_MNQ)
log("     observed %s -> %s" % (money(worst_full_mnq), "PASS" if d4a else "FAIL"))
log("  D4 GATE (b): W2020 maxDD @1MNQ (worse of the two ways) <= $%.2f (15%% of pool):" % BAR_MAXDD_MNQ)
log("     observed %s -> %s" % (money(-max(dd_way1, dd_way2)), "PASS" if d4b else "FAIL"))
log("  live-account ratios (NON-GATING; pool policy is the owner's): worst trade = %.1f%%," %
    (100 * abs(worst_full_mnq) / LIVE_ACCT))
log("     W2020 maxDD = %.1f%% of the $10,206 live account." % (100 * dd_way1 / LIVE_ACCT))

# zero-edge line (CAP02B-style), circular-shift null
mnq_demean = mnq - mnq.mean()
dd_shifts = np.array([max_dd_path(np.roll(mnq_demean, k)) for k in range(len(mnq_demean))])
p_zero_edge = float((dd_shifts >= BAR_MAXDD_MNQ).mean())
log("  ZERO-EDGE LINE (labeled, for the owner packet): take the same %d W2020 trade P&Ls" % len(mnq))
log("    at 1 MNQ, remove the mean (edge := 0), and form all %d circular shifts of the" % len(mnq))
log("    sequence (dependence-preserving null). The event counted is: 'the trade-path max")
log("    drawdown of a zero-edge rotation reaches the $7,784 D4 bar'.")
log("    P(maxDD >= $7,784 | edge = 0) = %.3f   (median null maxDD $%.0f, p95 $%.0f)" %
    (p_zero_edge, float(np.median(dd_shifts)), float(np.percentile(dd_shifts, 95))))
log("    This is a drawdown probability under a null, NOT 'P(losing the account)'.")
GATES.append(("D4a worst trade @1MNQ", "|worst historical trade| <= $2,594.55 (5% of full pool)",
              money(worst_full_mnq), "PASS" if d4a else "FAIL"))
GATES.append(("D4b W2020 maxDD @1MNQ", "maxDD (worse of two computations) <= $7,783.65 (15% of pool)",
              "way1 %s / way2 %s" % (money(-dd_way1), money(-dd_way2)),
              "PASS" if d4b else "FAIL"))

# =========================================================================================
log("\n[D5] REGIME OBSERVABILITY -- R(d) trailing-36-month self-ledger monitor")
month_ends = pd.period_range("2010-01", "2026-05", freq="M").to_timestamp("M")
exit_dates = pd.to_datetime(T["exit_date"])
rows5 = []
for d in month_ends:
    lo36 = d - pd.DateOffset(months=36)
    m = (exit_dates > lo36) & (exit_dates <= d)
    n36 = int(m.sum())
    net36 = float(T.loc[m, "pnl"].sum())
    on = (n36 >= 8) and (net36 > 0)
    rows5.append({"month_end": d.date(), "n_trades_36m": n36, "net_36m": round(net36, 2),
                  "regime_on": bool(on)})
R5 = pd.DataFrame(rows5)
# secondary, era-safe structural read V(d)
med63 = D["rv5"].rolling(63).median()
med1260 = D["rv5"].rolling(1260).median()
V = (med63 / med1260)
vm = []
for d in month_ends:
    sel = V.loc[:d]
    vm.append(round(float(sel.iloc[-1]), 4) if len(sel) and np.isfinite(sel.iloc[-1]) else np.nan)
R5["V_ratio_63v1260"] = vm
R5.to_csv(os.path.join(OUT, "regime_monitor.csv"), index=False)
on_series = R5.set_index("month_end")["regime_on"]
r2020 = R5[(pd.to_datetime(R5["month_end"]) >= "2019-06-01")]
first_on_2020 = None
prev_off = None
for _, r in R5.iterrows():
    if r["regime_on"] and pd.Timestamp(r["month_end"]) >= pd.Timestamp("2019-12-31"):
        first_on_2020 = r["month_end"]
        break
last = R5.iloc[-1]
on_2020_on = R5[pd.to_datetime(R5["month_end"]) >= (pd.Timestamp(first_on_2020) if first_on_2020 else pd.Timestamp("2020-01-01"))]
stays_on = bool(on_2020_on["regime_on"].all()) if first_on_2020 else False
log("  R(d) = trailing-36-month net of the frozen rule's OWN trades (exit-attributed),")
log("    computable at any d with >= 8 trades in the window; ON iff n>=8 AND net > 0.")
log("  monthly series 2010-01 -> 2026-05 written to out/regime_monitor.csv (%d rows)" % len(R5))
n_on = int(R5["regime_on"].sum())
pre2020 = R5[pd.to_datetime(R5["month_end"]) < "2020-01-01"]
log("  pre-2020 months ON: %d of %d;  2020+ months ON: %d of %d" %
    (int(pre2020["regime_on"].sum()), len(pre2020), n_on - int(pre2020["regime_on"].sum()),
     len(R5) - len(pre2020)))
log("  first ON month >= 2019-12: %s;  stays ON through 2026-05: %s" % (first_on_2020, stays_on))
log("  2023 zero-trade year: 36-month lookback keeps n>=8 throughout (min n in 2023 = %d)" %
    int(R5[pd.to_datetime(R5['month_end']).dt.year == 2023]["n_trades_36m"].min()))
log("  last computable month-end %s: n36=%d, net36 %s, regime %s" %
    (last["month_end"], last["n_trades_36m"], money(last["net_36m"]),
     "ON" if last["regime_on"] else "OFF"))
log("  V(d) secondary read (trailing-63s median rv5 / trailing-1260s median rv5, NON-GATING):")
log("    at 2026-05-29 V = %.3f (>1 means vol regime elevated vs its own 5-yr base)" %
    (R5["V_ratio_63v1260"].iloc[-1]))
log("  Regime-extension read 2026-06->07: NOT PERFORMED -- the only 2026-06->07 store on this")
log("    box is a BID/ASK quote-bar parquet (no Last-price series), so the frozen rule cannot")
log("    be extended without constructing a NEW substrate; per spec R_extension its absence")
log("    does not block (primary regime read ends 2026-05-29).")
d5_pass = bool(last["regime_on"])
log("  D5 GATE (regime ON at last computable date 2026-05): %s" % ("PASS" if d5_pass else "FAIL"))
GATES.append(("D5 regime monitor", "R(2026-05) ON: >=8 trades in 36m AND trailing-36m net > 0",
              "n36=%d, net36 %s, %s" % (last["n_trades_36m"], money(last["net_36m"]),
                                        "ON" if d5_pass else "OFF"),
              "PASS" if d5_pass else "FAIL"))

# =========================================================================================
log("\n[D6] PORTFOLIO MARGINAL vs THE LIVE P1 BOOK (genuinely new number)")
p1_sha = sha256_file(P1_DAILY)
log("  p1_daily.csv sha256 = %s" % p1_sha)
log("  DISCLOSED: every Python-chain P1 figure is ~2.0%% optimistic (double-lagged ATR at")
log("    we_fastctx.py:81, GENESIS III verdict) -- immaterial for correlation/geometry reads.")
p1 = pd.read_csv(P1_DAILY, index_col=0, parse_dates=True)["p1_usd"]
p1 = p1[(p1.index >= "2022-07-05") & (p1.index <= "2026-05-29")]
liq_daily_full = T.groupby(pd.to_datetime(T["exit_date"]))["pnl"].sum()
grid = p1.index.union(liq_daily_full.index[(liq_daily_full.index >= "2022-07-05") &
                                           (liq_daily_full.index <= "2026-05-29")])
J = pd.DataFrame({"p1": p1.reindex(grid).fillna(0.0),
                  "liqrev": liq_daily_full.reindex(grid).fillna(0.0)})
J["combined_deployed"] = 0.3 * J["p1"] + 0.1 * J["liqrev"]
J.to_csv(os.path.join(OUT, "portfolio_marginal.csv"))
n_liq_tr = int((pd.to_datetime(T["exit_date"]) >= "2022-07-05").sum() -
               (pd.to_datetime(T["exit_date"]) > "2026-05-29").sum())
n_active = int((J["liqrev"] != 0).sum())
log("  join grid: %d days (p1 rows %d, LIQREV-active days %d, LIQREV trades in window %d)" %
    (len(J), len(p1), n_active, n_liq_tr))
log("  THIN-OVERLAP HONESTY: only ~%d LIQREV trades intersect the P1 ledger (2024-2026" % n_liq_tr)
log("    trades only -- 2022 trades end 05-17 before the ledger starts, 2023 is empty);")
log("    a zero-trade P1-bad-day contributes $0 and passes (a) -- that IS the no-harm finding.")
corr_full = float(J["p1"].corr(J["liqrev"]))
act = J[J["liqrev"] != 0]
corr_active = float(act["p1"].corr(act["liqrev"])) if len(act) > 10 else np.nan
losing = J[J["p1"] < 0]
corr_losing = float(losing["p1"].corr(losing["liqrev"]))
thr = float(p1.quantile(0.10))
bottom = J.loc[J.index.isin(p1[p1 <= thr].index)]
nb_days = int(len(p1[p1 <= thr]))
liq_on_bottom = float(bottom["liqrev"].sum())
n_bottom_active = int((bottom["liqrev"] != 0).sum())
worst_comb = float(J["combined_deployed"].min())
worst_p1_dep = float(0.3 * J["p1"].min())
ratio = worst_comb / worst_p1_dep
log("  full-overlap daily corr (zero-filled grid)      %+.3f" % corr_full)
log("  both-active-days corr (n=%d, reported)          %+.3f" % (len(act), corr_active))
log("  corr on P1 losing days (n=%d)                   %+.3f" % (len(losing), corr_losing))
log("  P1 bottom-decile days: threshold $%.2f, n=%d, LIQREV active on %d of them" %
    (thr, nb_days, n_bottom_active))
log("  LIQREV net on P1 bottom-decile days (1-NQ scale) %s" % money(liq_on_bottom))
log("  worst combined day (0.3*P1 + 0.1*LIQREV)         %s  (%s)" %
    (money(worst_comb), J["combined_deployed"].idxmin().date()))
log("  worst P1-alone day at deployed scale (0.3*P1)    %s  (%s)" %
    (money(worst_p1_dep), J["p1"].idxmin().date()))
log("  ratio worst-combined / worst-P1-alone            %.3fx" % ratio)

# weekly-vol Sharpe combined vs alone + day-clustered bootstrap (reported)
wkJ = J.resample("W-SUN").sum()
sh_p1 = float((0.3 * wkJ["p1"]).mean() / (0.3 * wkJ["p1"]).std(ddof=1) * np.sqrt(52))
sh_cb = float(wkJ["combined_deployed"].mean() / wkJ["combined_deployed"].std(ddof=1) * np.sqrt(52))
rng = np.random.default_rng(SEED)
p1a = (0.3 * J["p1"]).to_numpy()
cba = J["combined_deployed"].to_numpy()
nd = len(J)
dlt = np.empty(NB)
for k in range(NB):
    pick = rng.integers(0, nd, nd)
    a, b = cba[pick], p1a[pick]
    dlt[k] = a.mean() / a.std(ddof=1) - b.mean() / b.std(ddof=1)
p_dpos = float((dlt > 0).mean())
log("  weekly-vol Sharpe: P1-alone(deployed) %.3f vs combined %.3f (Δ %+.3f)" %
    (sh_p1, sh_cb, sh_cb - sh_p1))
log("  day-clustered bootstrap (days resampled in PAIRS, daily-grain Sharpe, %d reps," % NB)
log("    seed %d): P(ΔSharpe > 0) = %.3f   [REPORTED, non-gating]" % (SEED, p_dpos))
d6a = liq_on_bottom > -10_000.0
d6b = ratio <= 1.5
d6c = corr_full <= 0.25
log("  D6 GATE (a) LIQREV net on P1 bottom-decile days > -$10,000 @1NQ: %s -> %s" %
    (money(liq_on_bottom), "PASS" if d6a else "FAIL"))
log("  D6 GATE (b) worst combined day <= 1.5x worst P1-alone (deployed): %.3fx -> %s" %
    (ratio, "PASS" if d6b else "FAIL"))
log("  D6 GATE (c) full-overlap daily corr <= 0.25: %+.3f -> %s" %
    (corr_full, "PASS" if d6c else "FAIL"))
GATES.append(("D6a bottom-decile damage", "LIQREV net on P1 bottom-decile days > -$10,000 @1NQ",
              "%s on %d active of %d days" % (money(liq_on_bottom), n_bottom_active, nb_days),
              "PASS" if d6a else "FAIL"))
GATES.append(("D6b worst combined day", "<= 1.5x worst P1-alone day at deployed scale",
              "%.3fx (%s vs %s)" % (ratio, money(worst_comb), money(worst_p1_dep)),
              "PASS" if d6b else "FAIL"))
GATES.append(("D6c daily corr", "full-overlap daily corr <= 0.25",
              "%+.3f (active-day corr %+.3f)" % (corr_full, corr_active),
              "PASS" if d6c else "FAIL"))

# =========================================================================================
log("\n[D7] COST / MICRO-EXECUTION VIABILITY -- stress rungs on W2020")
from research_sdk.cost_model import get as cost_get, per_nq_equivalent  # noqa: E402
mnq_comm = cost_get("mnq_commission")
comm_nq_equiv = per_nq_equivalent("MNQ")  # 13.00 $/NQ-equivalent ctrRT
log("  commission: MNQ $%.2f/ctrRT  [BASIS=%s, EVIDENCE=%s, n=%s] ->" %
    (mnq_comm.value, mnq_comm.basis, mnq_comm.evidence, mnq_comm.n))
log("    $%.2f per NQ-equivalent ctrRT (10 MNQ); 3x stress rung $%.2f" %
    (comm_nq_equiv, 3 * comm_nq_equiv))
log("  MNQ spread: UNMEASURED anywhere in this repo [EVIDENCE=ASSUMED]; two live samples")
log("    suggest <= NQ; preregistered stress rungs {1, 2, 4} ticks per side stand.")
log("  fill-timing rungs {15:59, 16:03, next-open 09:30} recomputed ON W2020 (red team ran")
log("    them full-sample only). Gross at variant closes; the frozen ledger's 1-tick-adverse")
log("    fills are REPLACED by the explicit spread rung (no double-charge).")

# per-session variant closes
rth_ext = df[(hm >= 930) & (hm <= 1603)]
gext = rth_ext.groupby("d")


def close_at(hmax):
    sub = rth_ext[rth_ext["time"].dt.hour * 100 + rth_ext["time"].dt.minute <= hmax]
    return sub.groupby("d")["close"].last()


c1558 = sess_close  # baseline (last <= 15:58)
c1559 = close_at(1559).reindex(valid_days)
c1603 = close_at(1603).reindex(valid_days)
copen = gext["close"].first().reindex(valid_days)   # first RTH bar close (~09:30-31 open proxy)
variants = {}
for name, ser in [("close_1558", pd.Series(c1558)), ("close_1559", c1559), ("close_1603", c1603)]:
    v = ser.copy()
    v.index = pd.to_datetime(pd.Index(v.index))
    variants[name] = v.reindex(D.index)
vopen = pd.Series(copen)
vopen.index = pd.to_datetime(pd.Index(vopen.index))
vopen = vopen.reindex(D.index)

w20_idx = [sess_pos[d] for d in pd.to_datetime(W2020["entry_date"])]
sides = W2020["side"].to_numpy()
fill_gross = {}
for name, v in variants.items():
    va = v.to_numpy()
    gr = np.array([sides[j] * (va[i + 1] - va[i]) * PV for j, i in enumerate(w20_idx)])
    fill_gross[name] = gr
# next-open: enter first-RTH close of session i+1, exit first-RTH close of session i+2
vo = vopen.to_numpy()
keep, gr = [], []
for j, i in enumerate(w20_idx):
    if i + 2 < n and np.isfinite(vo[i + 1]) and np.isfinite(vo[i + 2]):
        keep.append(j)
        gr.append(sides[j] * (vo[i + 2] - vo[i + 1]) * PV)
fill_gross["next_open_0930"] = np.array(gr)
log("  next-open variant: %d of %d trades computable (1-session hold preserved: enter at" %
    (len(gr), len(W2020)))
log("    first-RTH-bar close of d+1, exit at first-RTH-bar close of d+2)")

rung_rows = []
for fname, garr in fill_gross.items():
    for ticks in (1, 2, 4):
        for cmult in (1, 3):
            spread_rt = ticks * 2 * TICK * PV   # per-side ticks x 2 sides, NQ-scale $
            commission = cmult * comm_nq_equiv
            netpt = float(garr.mean() - spread_rt - commission)
            rung_rows.append({
                "fill_variant": fname, "spread_ticks_per_side": ticks,
                "commission_mult": cmult,
                "spread_$rt_nq_scale": spread_rt, "commission_$rt_nq_equiv": commission,
                "n_trades": len(garr),
                "gross_per_trade_nq": round(float(garr.mean()), 2),
                "net_per_trade_nq": round(netpt, 2),
                "net_per_trade_1mnq": round(netpt / 10, 3),
                "basis": "ALL_IN(rung) = gross - spread(ASSUMED ticks) - MNQ commission(MEASURED $1.30/ctrRT x10 NQ-equiv)",
            })
RG = pd.DataFrame(rung_rows)
RG.to_csv(os.path.join(OUT, "stress_rungs.csv"), index=False)
log("  ALL rungs (net $/trade at 1-NQ scale; full table in out/stress_rungs.csv):")
log("    %-16s %6s %6s %6s" % ("fill \\ spread/comm", "1t/1x", "2t/1x", "4t/3x"))
for fname in fill_gross:
    r1 = RG[(RG.fill_variant == fname) & (RG.spread_ticks_per_side == 1) & (RG.commission_mult == 1)]["net_per_trade_nq"].iloc[0]
    r2 = RG[(RG.fill_variant == fname) & (RG.spread_ticks_per_side == 2) & (RG.commission_mult == 1)]["net_per_trade_nq"].iloc[0]
    r4 = RG[(RG.fill_variant == fname) & (RG.spread_ticks_per_side == 4) & (RG.commission_mult == 3)]["net_per_trade_nq"].iloc[0]
    log("    %-16s %6.0f %6.0f %6.0f" % (fname, r1, r2, r4))
worst_rung = float(RG["net_per_trade_nq"].min())
wr = RG.loc[RG["net_per_trade_nq"].idxmin()]
d7_pass = worst_rung > 500.0
log("  WORST rung: %s x %dt/side x %dx commission -> net/trade $%.2f @1NQ ($%.2f @1MNQ)" %
    (wr["fill_variant"], wr["spread_ticks_per_side"], wr["commission_mult"],
     worst_rung, worst_rung / 10))
log("  D7 GATE (worst-rung W2020 net/trade > $500 @1-NQ scale): %s" %
    ("PASS" if d7_pass else "FAIL"))
GATES.append(("D7 worst-rung cost", "W2020 net/trade > $500 @1NQ at worst fill x 4t/side x 3x comm",
              "$%.2f (%s)" % (worst_rung, wr["fill_variant"]),
              "PASS" if d7_pass else "FAIL"))
log("  adapter feasibility (FACTS, no build in this run): decision on NQ primary close,")
log("    execution MNQ added series (MX01 pattern, drift-free by construction); one order")
log("    ~15:58:59 + one exit next session ~15:58:59; position held OVERNIGHT across 18:00 =>")
log("    full initial MNQ margin applies and the 16:39/16:45 flatten conventions do NOT")
log("    transfer; roll guard must inherit MIN-over-series blackout; new class name")
log("    LiqRev01Mnq_v1; local-path compile only, never CrossTrade source upload.")
log("    Margin figure to be read from the broker at packet time (blocker if unavailable).")

# =========================================================================================
log("\n[D8] REPORTING OBLIGATIONS (not gates)")
log("  (i) post-2020 3x3 grid re-report (ALL 9 cells; W2020 restriction of each cell;")
log("      plateau read only, NO selection):")
for sp in (0.85, 0.90, 0.95):
    line = []
    for q in (0.20, 0.25, 0.30):
        t = build_trades(sp, q, 1 - q, stress=True, hold=1)
        t20 = t[pd.to_datetime(t["entry_date"]) >= "2020-01-01"]
        line.append("s%d_q%d: n=%3d $%6.0f/t" % (int(sp * 100), int(q * 100),
                                                 len(t20), t20["pnl"].mean()))
    log("      " + " | ".join(line))
log("      plateau read: all 9 W2020 cells positive-sign? -> printed above, reported only.")

# thin holiday sessions: early close (last RTH bar <= 13:05)
last_bar_hm = g["time"].last().loc[valid_days].dt.hour * 100 + \
    g["time"].last().loc[valid_days].dt.minute
thin_days = set(pd.to_datetime(pd.Index(last_bar_hm[last_bar_hm <= 1305].index)))
tin = W2020["entry_date"].isin(thin_days) | W2020["exit_date"].isin(thin_days)
tin_full = T["entry_date"].isin(thin_days) | T["exit_date"].isin(thin_days)
log("  (ii) thin (13:00-halt) holiday sessions: %d such sessions in substrate." % len(thin_days))
log("      FULL sample: %d trades touch them, net %s (known conservative-direction defect)" %
    (int(tin_full.sum()), money(float(T.loc[tin_full, 'pnl'].sum()))))
log("      W2020 WITH all trades:      n=%d, $%.0f/t" % (len(W2020), W2020["pnl"].mean()))
w20x = W2020[~tin]
log("      W2020 WITHOUT thin-session: n=%d, $%.0f/t (excluded net %s)" %
    (len(w20x), w20x["pnl"].mean(), money(float(W2020.loc[tin, "pnl"].sum()))))

# corrected minute-data overnight-gap flag: first-bar-close(d) - last-bar-close(d-1), z>6
first_all = df.groupby("d")["close"].first().reindex(pd.Index(valid_days))
last_all = df.groupby("d")["close"].last().reindex(pd.Index(valid_days))
first_all.index = pd.to_datetime(pd.Index(first_all.index))
last_all.index = pd.to_datetime(pd.Index(last_all.index))
ogap = first_all - last_all.shift(1)
gmu = ogap.rolling(120, min_periods=40).mean().shift(1)
gsd = ogap.rolling(120, min_periods=40).std().shift(1)
corr_flag = ((ogap - gmu).abs() / gsd) > 6
corr_flag = corr_flag.reindex(D.index).fillna(False)
flag_days = set(D.index[corr_flag])
w20_corr = W2020[[bool(D.index[i + 1] in flag_days) for i in w20_idx]]
w20_dev = W2020[W2020["gap_flag_window"]]
log("  (iii) overnight-gap flag, BOTH constructions shown on W2020:")
log("      DEV proxy (ret z>6): %d flagged trades net %s; WITHOUT them $%.0f/t" %
    (len(w20_dev), money(float(w20_dev['pnl'].sum())),
     W2020[~W2020["gap_flag_window"]]["pnl"].mean()))
log("      RED-TEAM-CORRECTED (minute-data overnight gap z>6 on exit day): %d flagged" % len(w20_corr))
log("      trades net %s; WITHOUT them $%.0f/t" %
    (money(float(w20_corr['pnl'].sum())),
     W2020[~W2020.index.isin(w20_corr.index)]["pnl"].mean()))

nl20 = int((W2020["side"] == 1).sum())
ns20 = int((W2020["side"] == -1).sum())
log("  (iv) long/short split W2020: LONG n=%d net %s ($%.0f/t) | SHORT n=%d net %s ($%.0f/t)" %
    (nl20, money(float(W2020.loc[W2020['side'] == 1, 'pnl'].sum())),
     W2020.loc[W2020["side"] == 1, "pnl"].mean(),
     ns20, money(float(W2020.loc[W2020['side'] == -1, 'pnl'].sum())),
     W2020.loc[W2020["side"] == -1, "pnl"].mean()))

# matched placebo on W2020: nearest calm-state trade by signed ret(d), same side
P = build_trades(STRESS_PCT, QLO, QHI, stress=False, hold=1)
ret_of = D["ret"]
P = P.assign(ret=pd.to_datetime(P["entry_date"]).map(ret_of))
W20r = W2020.assign(ret=pd.to_datetime(W2020["entry_date"]).map(ret_of))
matched, dists = [], []
for _, r in W20r.iterrows():
    cand = P[P["side"] == r["side"]]
    j = (cand["ret"] - r["ret"]).abs().idxmin()
    matched.append(float(P.loc[j, "pnl"]))
    dists.append(float(abs(P.loc[j, "ret"] - r["ret"])))
matched = np.array(matched)
log("  (v) matched-placebo spread on W2020 (nearest calm-state trade by SIGNED entry-day")
log("      move, same side, with replacement; median match distance %.1f pts):" %
    float(np.median(dists)))
log("      real $%.0f/t vs matched-calm $%.0f/t -> state-attributable spread $%.0f/t" %
    (npt20, matched.mean(), npt20 - matched.mean()))

# =========================================================================================
# GATE TABLE + verdict (mechanical)
log("\n" + "=" * 96)
log("GATE / SPEC / OBSERVED / PASS-FAIL TABLE (printed by the program)")
log("=" * 96)
hdr = "%-26s | %-62s | %-46s | %s" % ("GATE", "SPEC", "OBSERVED", "PASS-FAIL")
log(hdr)
log("-" * len(hdr))
for gname, spec, obs, pf in GATES:
    log("%-26s | %-62s | %-46s | %s" % (gname, spec, obs, pf))
all_pass = all(pf == "PASS" for _, _, _, pf in GATES)
failed = [gname for gname, _, _, pf in GATES if pf != "PASS"]

log("\nDECISION RULE (preregistered, binary):")
if all_pass:
    verdict = "REGIME-LOCAL PROD CANDIDATE"
    log("  D1 valid AND D2-D7 ALL PASS -> VERDICT: REGIME-LOCAL PROD CANDIDATE")
    log("  (fast track FT0-FT10 per DESIGN_FROZEN.md SS3; owner enables, never the agent;")
    log("   the verdict label carries REGIME-LOCAL(2020+) forever.)")
else:
    verdict = "DEAD - PERMANENT CLOSURE"
    log("  VERDICT: DEAD - PERMANENT CLOSURE")
    log('  Scoped reason (verbatim): "the exact LIQREV01 post-2020 vol-acceleration reversal')
    log('   object is not a rational regime-local standalone engine at deployable micro size')
    log('   - failed %s on DISCOVERY_CONSUMED re-adjudication."' % ", ".join(failed))

log("\nHONEST MULTIPLICITY NOTE (SS6, mandatory): the object was originally SELECTED on this")
log("same window, so D2's pass is partially guaranteed by construction; the decision therefore")
log("hinges on D3-D7, which are new questions -- and the verdict label says REGIME-LOCAL forever.")

with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(LOG_LINES) + "\n")

summary = {"verdict": verdict, "all_pass": all_pass, "failed_gates": failed,
           "gates": [dict(zip(("gate", "spec", "observed", "passfail"), gt)) for gt in GATES]}
with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=1, default=str)
log("\n[done] artifacts written to %s" % OUT)
