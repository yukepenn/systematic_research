"""W8-2 — B-FADE: release-day fade (NEW preregistration of the W7-3 post-hoc mirror).
Frozen spec: research/scalping_lab/specs/W8_programs_final.md (committed cf7041f), section W8-2.

HONESTY CLAUSE (frozen, binding): the fade direction was OBSERVED on this same dev
sample (W7-3 continuation net -53t@15min => implied fade ~ +47t@15min); therefore
EVERY number in this readout is IN-SAMPLE CHARACTERIZATION, NOT CONFIRMATION.
No promotion from this wave. CONFIRMATION PLAN (frozen): pre-2022 minute data
(2005-2021, unseen, pending exporter) is the primary out-of-sample test; sealed
holdout only at Tier-3 if pre-2022 passes.

Rule (frozen): 08:30 release days (calendar); at the 09:30 bar close enter AGAINST
sign(09:30 close - pre-release 08:27 close); exits {15,30,60} min (market at bar
close); C1 costs. Placebo = non-release days, same rule off the 09:30-vs-08:27 sign.

Conventions reused from w7_e1_events.py (same event join, same bar conventions):
3-min CSV is END-stamped ET; pre-release close = LAST bar end-stamped strictly
before 08:30 (guard >= 08:00) -> the 08:27-stamped bar; entry bar end-stamped
exactly 09:30; exit = last bar end-stamped <= entry_tod + h*60 and > entry_tod.
FOMC-only (14:00) days are excluded from both release and placebo (as in W7-3),
reported separately as sensitivity. Prices in points, NQ tick = 0.25 -> t = pts*4.
C1 = 2.872t round trip. Seed 20260808, 1000 day-clustered bootstrap reps
(1 trade/day => day resampling). LOCAL ONLY. Dev guard: CSV rows and calendar
dates >= 2026-06-01 are dropped at read.

RECONCILIATION (printed below): with identical days/exits, fade_net(h) must equal
-cont_net(h) - 2*C1 (flip the sign of the W7-3 continuation gross, pay C1 once
here and un-pay the C1 embedded in the continuation net => double friction).
"""
import os
import sys
import numpy as np
import pandas as pd

SEED = 20260808
NBOOT = 1000
C1 = 2.872
TICK = 0.25
DOLLAR_PER_TICK_1NQ = 5.0  # 1 NQ: $20/pt * 0.25 pt/tick (context only)

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
CAL = os.path.join(REPO, "research", "04_complementary_family", "c01_announcement_calendar.csv")
CSV = os.path.join(REPO, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv")
W7SUM = os.path.join(REPO, "research", "scalping_lab", "artifacts", "w7_e1", "w7e1_minute_summary.csv")
OUTD = os.path.join(REPO, "research", "scalping_lab", "artifacts", "w8_bfade")
os.makedirs(OUTD, exist_ok=True)

DEV_END = pd.Timestamp("2026-06-01")


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

print("W8-2 B-FADE — release-day fade. HONESTY CLAUSE: every performance table below")
print("is IN-SAMPLE CHARACTERIZATION (fade direction was observed on this same dev")
print("sample in W7-3). NOT confirmation. No promotion from this wave.")

# ---------------------------------------------------------------------------
# Calendar (FACT) + pre-2022 confirmation sample size check
# ---------------------------------------------------------------------------
cal = pd.read_csv(CAL)
cal["date"] = pd.to_datetime(cal["date"]).dt.date
print(f"\n[FACT] Calendar rows: {len(cal)} | range {min(cal['date'])} -> {max(cal['date'])}")
print(f"[FACT] events: {cal['event'].value_counts().to_dict()} | times: {cal['time_et'].value_counts().to_dict()}")

pre2022_830 = cal[(cal["time_et"] == "08:30") & (cal["date"] < pd.Timestamp("2022-01-01").date())]
print(f"\n=== CONFIRMATION SAMPLE SIZE (pre-2022 08:30 releases in calendar): {len(pre2022_830)} ===")
if len(pre2022_830) == 0:
    print("[FACT] The calendar STARTS 2022-01-07 — it does NOT extend to 2005-2021.")
    print("[DEPENDENCY] The frozen confirmation plan (pre-2022 minute data 2005-2021)")
    print("  therefore needs TWO inputs, not one: (1) SWMinuteExport_v1 1-min data")
    print("  2005+ (already in the blocked queue), AND (2) a historical 08:30 release")
    print("  calendar 2005-2021 (NFP + CPI dates from bls.gov) — NOT yet built.")
    print("[INFERENCE] Expected pre-2022 sample if built: ~12 NFP + ~12 CPI per year")
    print("  x 17 years (2005-2021) ~ 408 release days (~4x the dev n) — an estimate,")
    print("  not a count; the actual calendar must be sourced from BLS archives.")

cal_dev = cal[cal["date"] < DEV_END.date()]
d830 = set(cal_dev.loc[cal_dev["time_et"] == "08:30", "date"])
d1400 = set(cal_dev.loc[cal_dev["time_et"] == "14:00", "date"])
fomc_only = d1400 - d830
# event type per 08:30 release day (NFP / CPI / NFP+CPI if same-day)
etype = (cal_dev[cal_dev["time_et"] == "08:30"].groupby("date")["event"]
         .apply(lambda s: "+".join(sorted(set(s)))).to_dict())
n_both = sum(1 for v in etype.values() if "+" in v)
print(f"\n[FACT] Dev-window calendar days: 08:30-release {len(d830)} "
      f"(types: { {k: sum(1 for v in etype.values() if v == k) for k in sorted(set(etype.values()))} }), "
      f"FOMC 14:00 {len(d1400)}, FOMC-only {len(fomc_only)}, same-day NFP+CPI {n_both}")

# ---------------------------------------------------------------------------
# Bars (dev guard) and trade construction — identical join to w7_e1_events.py,
# with the SIGN FLIPPED (fade) at entry.
# ---------------------------------------------------------------------------
bars = pd.read_csv(CSV, usecols=["time", "close"])
bars["time"] = pd.to_datetime(bars["time"])
n_all = len(bars)
bars = bars[bars["time"] < DEV_END].reset_index(drop=True)  # DEV GUARD
print(f"\n[FACT] CSV rows read {n_all}, kept {len(bars)} (< 2026-06-01), "
      f"range {bars['time'].iloc[0]} -> {bars['time'].iloc[-1]}")
bars["date"] = bars["time"].dt.date
bars["tod"] = bars["time"].dt.hour * 3600 + bars["time"].dt.minute * 60 + bars["time"].dt.second

T_PRE, T_ENT = 8 * 3600 + 30 * 60, 9 * 3600 + 30 * 60
EXITS = {15: T_ENT + 15 * 60, 30: T_ENT + 30 * 60, 60: T_ENT + 60 * 60}

trades = []
skip = {"no_pre": 0, "no_entry": 0, "no_exit": 0, "zero_sig": 0}
for date, day in bars.groupby("date", sort=True):
    if pd.Timestamp(date).weekday() >= 5:
        continue
    tod = day["tod"].values; close = day["close"].values
    pre_ix = np.where((tod < T_PRE) & (tod >= 8 * 3600))[0]
    if len(pre_ix) == 0:
        skip["no_pre"] += 1; continue
    pre_close = close[pre_ix[-1]]; pre_tod = tod[pre_ix[-1]]
    ent_ix = np.where(tod == T_ENT)[0]
    if len(ent_ix) == 0:
        skip["no_entry"] += 1; continue
    ent = close[ent_ix[0]]
    reaction = np.sign(ent - pre_close)          # 08:27 -> 09:30 pre-open reaction
    if reaction == 0:
        skip["zero_sig"] += 1; continue
    sig = -int(reaction)                          # FADE: against the reaction
    row = dict(date=date, pre_tod=pre_tod, pre_close=pre_close, entry=ent,
               reaction=int(reaction), signal=sig,
               group=("release" if date in d830 else "fomc_only" if date in fomc_only
                      else "placebo"),
               event_type=etype.get(date, ""))
    ok = True
    for h, tx in EXITS.items():
        ex_ix = np.where((tod <= tx) & (tod > T_ENT))[0]
        if len(ex_ix) == 0:
            ok = False; break
        row[f"exit{h}_tod"] = tod[ex_ix[-1]]
        row[f"gross{h}"] = sig * (close[ex_ix[-1]] - ent) / TICK
        row[f"net{h}"] = row[f"gross{h}"] - C1
    if not ok:
        skip["no_exit"] += 1; continue
    trades.append(row)

T = pd.DataFrame(trades)
T.to_csv(os.path.join(OUTD, "w8bfade_trades.csv"), index=False)
print(f"[FACT] Days simulated: {len(T)} | skipped: {skip}")
print("[FACT] Group counts:", T["group"].value_counts().to_dict())
pre_tods = T["pre_tod"].value_counts().head(4)
print("[FACT] Pre-release bar end-stamp distribution (top):",
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


def block(scope, group, G, with_ci=True):
    for h in (15, 30, 60):
        x = G[f"net{h}"].values
        lo, hi = boot_ci(x, rng) if (with_ci and len(x)) else (np.nan, np.nan)
        summary.append(dict(scope=scope, group=group, horizon=h, n=len(x),
                            net_c1_t=float(np.mean(x)) if len(x) else np.nan,
                            ci_lo=lo, ci_hi=hi,
                            gross_t=float(G[f"gross{h}"].mean()) if len(x) else np.nan,
                            win_rate=float((x > 0).mean()) if len(x) else np.nan))


# ---------------------------------------------------------------------------
# Pooled by group x horizon
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("POOLED fade by group x horizon — IN-SAMPLE CHARACTERIZATION (honesty clause)")
print(f"(net C1={C1}t; day-clustered 95% CI, {NBOOT} reps, seed {SEED})")
print("=" * 78)
print(f"{'group':>10} {'h':>4} {'n':>5} {'netC1_t':>8} {'CI_lo':>8} {'CI_hi':>8} "
      f"{'gross_t':>8} {'win%':>6}")
for grp in ("release", "placebo", "fomc_only"):
    G = T[T["group"] == grp]
    block("pooled", grp, G)
    for r in summary[-3:]:
        print(f"{grp:>10} {r['horizon']:>4} {r['n']:>5} {r['net_c1_t']:>+8.3f} "
              f"{r['ci_lo']:>+8.3f} {r['ci_hi']:>+8.3f} {r['gross_t']:>+8.3f} "
              f"{100*r['win_rate']:>5.1f}")

# ---------------------------------------------------------------------------
# RECONCILIATION vs W7-3 continuation (frozen requirement)
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("RECONCILIATION vs W7-3 continuation (w7e1_minute_summary.csv, pooled release):")
print("expected fade_net(h) = -cont_net(h) - 2*C1  (flipped sign minus double friction)")
print("=" * 78)
w7 = pd.read_csv(W7SUM)
recon_ok = True
for grp in ("release", "placebo", "fomc_only"):
    for h in (15, 30, 60):
        w = w7[(w7["scope"] == "pooled") & (w7["group"] == grp) & (w7["horizon"] == h)]
        m = [r for r in summary if r["scope"] == "pooled" and r["group"] == grp
             and r["horizon"] == h][0]
        if len(w) == 0 or m["n"] == 0:
            continue
        cont_net = float(w["net_c1_t"].iloc[0]); n7 = int(w["n"].iloc[0])
        expect = -cont_net - 2 * C1
        diff = m["net_c1_t"] - expect
        same_n = (m["n"] == n7)
        ok = same_n and abs(diff) < 1e-9
        recon_ok &= ok
        print(f"  {grp:>10} h={h:>2}: W7 cont_net={cont_net:+9.3f} (n={n7}) -> expected "
              f"fade={expect:+9.3f} | this run fade={m['net_c1_t']:+9.3f} (n={m['n']}) "
              f"| diff={diff:+.2e} {'OK' if ok else 'MISMATCH'}")
print(f"RECONCILIATION: {'PASS — exact mirror of W7-3 minus double friction' if recon_ok else 'FAIL — investigate'}")

# ---------------------------------------------------------------------------
# By event type (NFP vs CPI vs same-day both) — release days only
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("BY EVENT TYPE (release days) — IN-SAMPLE CHARACTERIZATION")
print("=" * 78)
Trel = T[T["group"] == "release"].copy()
print(f"{'type':>10} {'h':>4} {'n':>4} {'netC1_t':>8} {'CI_lo':>8} {'CI_hi':>8} {'win%':>6}")
for et in sorted(Trel["event_type"].unique()):
    G = Trel[Trel["event_type"] == et]
    block(f"etype_{et}", et, G)
    for r in summary[-3:]:
        print(f"{et:>10} {r['horizon']:>4} {r['n']:>4} {r['net_c1_t']:>+8.3f} "
              f"{r['ci_lo']:>+8.3f} {r['ci_hi']:>+8.3f} {100*r['win_rate']:>5.1f}")

# ---------------------------------------------------------------------------
# By year (release, with placebo alongside) — stability
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("BY YEAR (release fade, placebo alongside) — IN-SAMPLE CHARACTERIZATION")
print("=" * 78)
Trel["year"] = pd.to_datetime(Trel["date"]).dt.year
Tpla = T[T["group"] == "placebo"].copy()
Tpla["year"] = pd.to_datetime(Tpla["date"]).dt.year
print(f"{'year':>6} {'h':>4} {'n':>4} {'netC1_t':>8} {'CI_lo':>8} {'CI_hi':>8} {'win%':>6}"
      f"   | placebo: {'n':>4} {'netC1_t':>8}")
for y in sorted(Trel["year"].unique()):
    Gy = Trel[Trel["year"] == y]; Py = Tpla[Tpla["year"] == y]
    block(f"year{y}", "release", Gy)
    yr_rows = summary[-3:]
    block(f"year{y}", "placebo", Py, with_ci=False)
    pl_rows = summary[-3:]
    for r, p in zip(yr_rows, pl_rows):
        print(f"{y:>6} {r['horizon']:>4} {r['n']:>4} {r['net_c1_t']:>+8.3f} "
              f"{r['ci_lo']:>+8.3f} {r['ci_hi']:>+8.3f} {100*r['win_rate']:>5.1f}"
              f"   | {p['n']:>4} {p['net_c1_t']:>+8.3f}")

S = pd.DataFrame(summary)
S.to_csv(os.path.join(OUTD, "w8bfade_summary.csv"), index=False)

# ---------------------------------------------------------------------------
# Equity path, drawdown, worst trade, concentration — release days
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("EQUITY PATH / DRAWDOWN / WORST TRADE / CONCENTRATION (release fade)")
print("IN-SAMPLE CHARACTERIZATION — $ figures at 1 NQ = $5/tick, context only")
print("=" * 78)
Trel = Trel.sort_values("date").reset_index(drop=True)
eq = Trel[["date"]].copy()
conc_rows = []
for h in (15, 30, 60):
    net = Trel[f"net{h}"]
    eq[f"net{h}"] = net
    eq[f"cum{h}"] = net.cumsum()
    eq[f"dd{h}"] = eq[f"cum{h}"] - eq[f"cum{h}"].cummax()
    tot = float(net.sum())
    maxdd = float(eq[f"dd{h}"].min())
    i_dd = int(eq[f"dd{h}"].idxmin())
    iw = int(net.idxmin()); ib = int(net.idxmax())
    top5 = net.nlargest(5)
    bot5 = net.nsmallest(5)
    top5_share = float(top5.sum() / tot) if tot > 0 else np.nan
    pos_sum = float(net[net > 0].sum())
    top5_share_pos = float(top5.sum() / pos_sum) if pos_sum > 0 else np.nan
    conc_rows.append(dict(horizon=h, total_net_t=tot,
                          total_net_usd_1nq=tot * DOLLAR_PER_TICK_1NQ,
                          max_dd_t=maxdd, max_dd_usd_1nq=maxdd * DOLLAR_PER_TICK_1NQ,
                          max_dd_date=str(eq.loc[i_dd, "date"]),
                          worst_trade_t=float(net.iloc[iw]),
                          worst_trade_date=str(Trel.loc[iw, "date"]),
                          worst_trade_event=Trel.loc[iw, "event_type"],
                          best_trade_t=float(net.iloc[ib]),
                          best_trade_date=str(Trel.loc[ib, "date"]),
                          top5_sum_t=float(top5.sum()), top5_share_of_total=top5_share,
                          top5_share_of_gross_wins=top5_share_pos,
                          top5_dates=";".join(str(Trel.loc[i, "date"]) for i in top5.index),
                          bot5_sum_t=float(bot5.sum()),
                          bot5_dates=";".join(str(Trel.loc[i, "date"]) for i in bot5.index)))
    c = conc_rows[-1]
    print(f"\n  h={h}min: total net {tot:+.1f}t (${tot*DOLLAR_PER_TICK_1NQ:+,.0f} at 1 NQ) "
          f"over n={len(net)} trades")
    print(f"    max drawdown {maxdd:+.1f}t (${maxdd*DOLLAR_PER_TICK_1NQ:+,.0f}), trough {c['max_dd_date']}")
    print(f"    worst trade {c['worst_trade_t']:+.1f}t on {c['worst_trade_date']} "
          f"({c['worst_trade_event']}) | best {c['best_trade_t']:+.1f}t on {c['best_trade_date']}")
    print(f"    top-5 winners sum {c['top5_sum_t']:+.1f}t = "
          f"{100*top5_share:.1f}% of total net, {100*top5_share_pos:.1f}% of gross wins")
    print(f"    top-5 dates: {c['top5_dates']}")
    print(f"    bottom-5 sum {c['bot5_sum_t']:+.1f}t ({c['bot5_dates']})")
eq.to_csv(os.path.join(OUTD, "w8bfade_equity.csv"), index=False)
pd.DataFrame(conc_rows).to_csv(os.path.join(OUTD, "w8bfade_concentration.csv"), index=False)

print("\n[FACT] Artifacts written to research/scalping_lab/artifacts/w8_bfade/:")
print("  w8bfade_trades.csv, w8bfade_summary.csv, w8bfade_equity.csv,")
print("  w8bfade_concentration.csv, stdout.txt")
print("\nVERDICT SCOPE (frozen): CHARACTERIZATION ONLY — no promotion from this wave;")
print("primary out-of-sample test = pre-2022 minute data (pending SWMinuteExport_v1")
print("AND a 2005-2021 historical 08:30 release calendar, see dependency above).")
print("\nW8BFADE DONE")
