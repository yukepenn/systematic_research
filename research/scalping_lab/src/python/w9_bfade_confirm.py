"""W9-3 — B-FADE pre-2022 confirmation (the real out-of-sample test).

Frozen spec: research/scalping_lab/specs/W9_nq_minute_resolutions.md section W9-3
INCLUDING the 2026-08-08 decay AMENDMENT (the four-way verdict REPLACES the binary
rule; both committed BEFORE this readout). Frozen rule identical to W8-2
(specs/W8_programs_final.md section W8-2; construction mirrors src/python/w8_bfade.py).

CONFIRMATION WINDOW: 2006-01-05 .. 2021-12-31 ONLY. The minute substrate
substrate/minute/NQ/nq1m_2005_202605.parquet actually starts 2006-01-05 (the "2005"
in the name is the requested export start; no 2005 bars exist), so the amendment's
nominal "2005-2021" window is realized as 2006-2021 — a data fact, not a choice.
CONTAMINATION GUARD: bar rows stamped >= 2022-01-01 are dropped at load and NEVER
enter any statistic here; 2022+ appears ONLY via the committed w8_bfade artifacts
(reconciliation printout, context only, never pooled).

RULE (frozen, W8-2 ported to 1-min END-stamped bars; empirical stamp verification
printed in-run for 3 sample days):
  pre-release close = close of the LAST bar end-stamped strictly before 08:30 ET
    (guard >= 08:00) -> the 08:29-stamped bar (covers 08:28->08:29) on complete data.
    [3-min analogue was the 08:27-stamped bar: the same "last stamp strictly before
    08:30" rule, resolution-adapted.]
  entry = close of the bar end-stamped exactly 09:30 ET (covers 09:29->09:30; its
    close is the last print at/just before 09:30:00 = the price at the RTH open;
    the SAME price point as the W8-2 3-min 09:30-stamped-bar close). Verified
    empirically: RTH volume spike sits in the 09:31-stamped bar and
    close(09:30-stamp) ~ open(09:31-stamp); release volume spike sits in the
    08:31-stamped bar (reaction inside 08:30:00->08:31:00).
  signal: FADE — trade AGAINST sign(entry - pre_close); zero reaction -> no trade.
  exits: LAST bar end-stamped <= entry_tod + h*60 and > entry_tod, h in {15,30,60}.
  costs: C1 = 2.872 ticks round trip; NQ tick = 0.25 pt = $5 (1 NQ, context only).
  placebo: same rule on ALL non-release weekdays. (W8-2 additionally carved out
    FOMC-only 14:00 days; the 2005-2021 calendar contains only 08:30 NFP/CPI rows,
    so pre-2022 FOMC days sit inside the placebo — disclosed. FOMC is 14:00 ET and
    cannot touch an 08:29->10:30 trade.)

ROLL-GAP GUARD (design iterated IN THIS RUN, disclosed; the verdict is identical
under every variant, verified below):
  Purpose: exclude trades whose window spans a back-adjustment SPLICE artifact
  ("detected 8-sigma jump"). Detector pass 1 (pooled 16-year sigma of 1-min diffs
  in TICKS, flag > 8 sigma) was computed first and REJECTED as a roll detector:
  with a 5x price-level rise 2006->2021 a fixed tick threshold is a recency-biased
  VOLATILITY filter — it excluded 100/471 morning trades, all at genuine macro
  minutes (2020 COVID, 2018 Volmageddon, 08:31 reaction bursts), including 17 of
  23 traded 2021 release days, i.e. it deletes the very reactions under test.
  Corrected detector (primary): a CANDIDATE 8-sigma jump is a 1-min fractional
  return > 8 x local sigma (trailing 90 weekdays' within-(08:29,10:30] 1-min
  returns, strictly prior, min 30 days) AND > 8 x same-day isolation sigma (std of
  the day's OTHER window minutes) — a splice must be extreme vs both its era and
  its own day. Candidates are then splice-tested: an NT8 back-adjusted merge
  switches contracts at a roll SESSION BOUNDARY (17:00/18:00 ET), which an
  08:29->10:30 intra-session window can never span; empirically every candidate
  minute sits at a macro stamp (08:31 release reaction, 09:31 RTH open, 10:01
  data/Fed) and the max same-day isolation z in the whole sample is ~19 — a true
  splice (quiet day, permanent one-minute re-basing) would print isolation z >> 20
  at an arbitrary minute. Roll-gap exclusions therefore = the candidates that are
  actual splices; count reported. Sensitivity rows: (A) all candidate extreme-vol
  days excluded; (B) the rejected pass-1 tick-sigma filter — both labeled, both in
  the summary CSV, neither primary.

PRIMARY frozen readout: the 15-min exit (named before any readout, in-sample-
strongest horizon per W8-2). AMENDED four-way verdict (evaluated in this order):
  CONFIRMED                iff full-window net C1 > 0 with CI_lo > 0 at 15min
                           AND 2015-2021 subperiod POINT estimate > 0;
  PARTIALLY-SUPPORTED      iff 2015-2021 alone passes CI_lo > 0 while the full
                           window does not;
  REFUTED                  iff full-window CI_hi < 0 at 15min;
  UNCONFIRMED-POSSIBLY-RECENT otherwise (flat/negative but not significantly so).
Placebo flatness (the original binary rule's second clause) is reported as context;
the four-way rule governs.

Stats: seed 20260808, 1000 bootstrap reps, day-clustered CIs (one trade per day =>
day resampling; CI draws are deterministic given the seed and the fixed block
order of this script). LOCAL ONLY, no git commit from this script.

Artifacts -> research/scalping_lab/artifacts/w9_bfade/:
  w9bfade_stdout.txt, w9bfade_trades.csv, w9bfade_summary.csv,
  w9bfade_rolling_3y.csv, w9bfade_excluded.csv, w9bfade_concentration.csv,
  w9bfade_guard_scan.csv, w9bfade_report.md (written after the run).
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]  # systematic_research/
BARS_PARQUET = ROOT / "research" / "scalping_lab" / "substrate" / "minute" / "NQ" / "nq1m_2005_202605.parquet"
CAL = ROOT / "research" / "scalping_lab" / "data" / "hist_calendar_2005_2021.csv"
W8SUM = ROOT / "research" / "scalping_lab" / "artifacts" / "w8_bfade" / "w8bfade_summary.csv"
ART = ROOT / "research" / "scalping_lab" / "artifacts" / "w9_bfade"

CONFIRM_END = pd.Timestamp("2022-01-01")   # exclusive — the contamination boundary
SEED = 20260808
NBOOT = 1000
C1 = 2.872
TICK = 0.25
USD_PER_TICK = 5.0
OUTLIER_SIGMA = 8.0
T_PRE = 8 * 3600 + 30 * 60      # 08:30 release
T_GUARD = 8 * 3600              # pre bar must be >= 08:00
T_ENT = 9 * 3600 + 30 * 60      # 09:30 entry stamp
HORIZONS = (15, 30, 60)
EXITS = {h: T_ENT + h * 60 for h in HORIZONS}
ERAS = [(2006, 2009), (2010, 2013), (2014, 2017), (2018, 2021)]
LOCAL_WIN_DAYS = 90             # trailing weekdays for local sigma
LOCAL_MIN_DAYS = 30

SAMPLE_STAMP_DAYS = ["2006-02-03", "2013-07-05", "2021-11-05"]  # NFP: early/mid/late era


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)

    def flush(self):
        for st in self.streams:
            st.flush()


def boot_ci(x, rng, nboot=NBOOT):
    """Day-clustered bootstrap 95% CI of the mean (one trade per day => day resample)."""
    x = np.asarray(x, float)
    n = len(x)
    if n == 0:
        return np.nan, np.nan
    idx = rng.integers(0, n, size=(nboot, n))
    means = x[idx].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def main():
    ART.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print("W9-3  B-FADE pre-2022 CONFIRMATION — the real out-of-sample test")
    print("Spec: W9_nq_minute_resolutions.md §W9-3 + decay AMENDMENT (four-way verdict,")
    print("frozen before readout). Rule identical to W8-2. Primary readout: 15-min exit.")
    print("=" * 78)

    # ------------------------------------------------------------------ bars
    bars = pd.read_parquet(BARS_PARQUET)
    bars["time"] = pd.to_datetime(bars["time"])
    n_raw = len(bars)
    bars = bars[bars["time"] < CONFIRM_END].sort_values("time").reset_index(drop=True)
    assert bars["time"].max() < CONFIRM_END, "contamination guard failed"
    print(f"\n[FACT] Bars: {n_raw} rows raw; {len(bars)} kept < {CONFIRM_END.date()} "
          f"(contamination guard; {n_raw - len(bars)} rows >= 2022 dropped unread).")
    print(f"[FACT] Kept stamp range: {bars['time'].iloc[0]} -> {bars['time'].iloc[-1]} "
          f"(exchange ET, END-stamped).")

    # ---------------------------------------------- empirical stamp verification
    print("\n--- EMPIRICAL STAMP VERIFICATION (3 sample NFP days) ---")
    print("Claim: END-stamped => 09:30-stamped close = price at the 09:30:00 RTH open")
    print("(the W8-2 3-min entry price point); first full RTH minute is stamped 09:31.")
    for d in SAMPLE_STAMP_DAYS:
        day = bars[(bars["time"] >= f"{d} 08:26") & (bars["time"] <= f"{d} 09:33")]
        keep = day["time"].dt.strftime("%H:%M").isin(
            ["08:29", "08:30", "08:31", "09:29", "09:30", "09:31"])
        sub = day[keep][["time", "open", "close", "volume"]]
        print(f"  {d}:")
        for _, r in sub.iterrows():
            print(f"    {r['time'].strftime('%H:%M')}  open {r['open']:>9.2f}  "
                  f"close {r['close']:>9.2f}  vol {int(r['volume']):>5d}")
        g = {r["time"].strftime("%H:%M"): r for _, r in sub.iterrows()}
        print(f"    -> close(09:30)={g['09:30']['close']} vs open(09:31)={g['09:31']['open']} "
              f"(diff {g['09:31']['open'] - g['09:30']['close']:+.2f} pt); "
              f"RTH vol spike 09:31 ({int(g['09:31']['volume'])} vs {int(g['09:30']['volume'])}); "
              f"release vol spike 08:31 ({int(g['08:31']['volume'])} vs {int(g['08:30']['volume'])})")
    print("  VERDICT on stamps: END-stamped confirmed on all 3 days -> entry stamp = 09:30;")
    print("  pre-release stamp = 08:29 (last close strictly before 08:30, guard >= 08:00).")

    # ------------------------------------------------------------------ calendar
    cal = pd.read_csv(CAL)
    cal["date"] = pd.to_datetime(cal["date"])
    cal = cal[cal["date"] < CONFIRM_END]
    assert (cal["time_et"] == "08:30").all(), "calendar must be all-08:30 rows"
    cal_2005 = cal[cal["date"] < pd.Timestamp("2006-01-01")]
    cal_use = cal[cal["date"] >= pd.Timestamp("2006-01-01")]
    etype = (cal_use.groupby(cal_use["date"].dt.date)["event"]
             .apply(lambda s: "+".join(sorted(set(s)))).to_dict())
    rel_days = set(etype.keys())
    n_same_day = sum(1 for v in etype.values() if "+" in v)
    print(f"\n[FACT] Calendar (BLS primary-source, all 08:30 ET): {len(cal)} rows "
          f"{cal['date'].min().date()} -> {cal['date'].max().date()}.")
    print(f"[FACT] 2005 rows {len(cal_2005)} (find no bars — data starts 2006-01-05; dropped).")
    print(f"[FACT] 2006-2021 release DAYS: {len(rel_days)} "
          f"(events: {cal_use['event'].value_counts().to_dict()}; same-day NFP+CPI: {n_same_day}).")

    # ------------------------------------------------------------ trade construction
    bars["date"] = bars["time"].dt.date
    bars["tod"] = (bars["time"].dt.hour * 3600 + bars["time"].dt.minute * 60
                   + bars["time"].dt.second)

    trades, excluded_rows = [], []
    skip = {"weekend": 0, "no_pre": 0, "no_entry": 0, "no_exit": 0, "zero_sig": 0}
    bar_dates = set()
    day_rets = {}      # date -> (ret array, tod-of-second-bar array) for guard scan
    for date, day in bars.groupby("date", sort=True):
        bar_dates.add(date)
        if pd.Timestamp(date).weekday() >= 5:
            skip["weekend"] += 1
            continue
        tod = day["tod"].values
        close = day["close"].values
        grp = "release" if date in rel_days else "placebo"
        # guard-scan population: within-day 1-min fractional returns, stamps [08:29,10:30]
        wix = np.where((tod >= T_PRE - 60) & (tod <= EXITS[60]))[0]
        if len(wix) >= 3:
            wc = close[wix]
            day_rets[date] = (np.diff(wc) / wc[:-1], tod[wix[1:]])
        pre_ix = np.where((tod < T_PRE) & (tod >= T_GUARD))[0]
        if len(pre_ix) == 0:
            skip["no_pre"] += 1
            if grp == "release":
                excluded_rows.append(dict(date=date, group=grp, reason="no_pre_bar",
                                          event_type=etype.get(date, "")))
            continue
        pre_close = close[pre_ix[-1]]
        pre_tod = int(tod[pre_ix[-1]])
        ent_ix = np.where(tod == T_ENT)[0]
        if len(ent_ix) == 0:
            skip["no_entry"] += 1
            if grp == "release":
                excluded_rows.append(dict(date=date, group=grp, reason="no_0930_entry_bar",
                                          event_type=etype.get(date, "")))
            continue
        ent = close[ent_ix[0]]
        reaction = np.sign(ent - pre_close)
        if reaction == 0:
            skip["zero_sig"] += 1
            if grp == "release":
                excluded_rows.append(dict(date=date, group=grp, reason="zero_reaction",
                                          event_type=etype.get(date, "")))
            continue
        sig = -int(reaction)                       # FADE: against the pre-open reaction
        row = dict(date=date, group=grp, event_type=etype.get(date, ""),
                   pre_tod=pre_tod, pre_close=float(pre_close), entry=float(ent),
                   reaction=int(reaction), signal=sig)
        ok = True
        for h in HORIZONS:
            ex_ix = np.where((tod <= EXITS[h]) & (tod > T_ENT))[0]
            if len(ex_ix) == 0:
                ok = False
                break
            row[f"exit{h}_tod"] = int(tod[ex_ix[-1]])
            row[f"gross{h}"] = sig * (close[ex_ix[-1]] - ent) / TICK
            row[f"net{h}"] = row[f"gross{h}"] - C1
        if not ok:
            skip["no_exit"] += 1
            if grp == "release":
                excluded_rows.append(dict(date=date, group=grp, reason="no_exit_bar",
                                          event_type=etype.get(date, "")))
            continue
        # raw max |1-min diff| in ticks per horizon window (for sensitivity B)
        for h in HORIZONS:
            win = np.where((tod >= pre_tod) & (tod <= row[f"exit{h}_tod"]))[0]
            d_t = np.abs(np.diff(close[win])) / TICK
            row[f"jump{h}_t"] = float(d_t.max()) if len(d_t) else 0.0
        trades.append(row)

    T = pd.DataFrame(trades)
    missing = sorted(d for d in rel_days if d not in bar_dates)
    for d in missing:
        excluded_rows.append(dict(date=d, group="release", reason="no_bars_holiday",
                                  event_type=etype.get(d, "")))
    print(f"\n[FACT] Weekdays simulated: {len(T)} | skip counts (all weekdays): {skip}")
    print(f"[FACT] Release calendar days with NO bars at all (exchange holiday): "
          f"{len(missing)} -> {[str(d) for d in missing]}")
    excl_df = pd.DataFrame(excluded_rows).sort_values("date") if excluded_rows else \
        pd.DataFrame(columns=["date", "group", "reason", "event_type"])
    not_traded_rel = excl_df[excl_df["group"] == "release"]
    print(f"[FACT] Release days NOT traded (itemized): {len(not_traded_rel)}")
    for _, r in not_traded_rel.iterrows():
        print(f"    {r['date']}  {r['event_type']:>8}  {r['reason']}")
    print("  (no_0930_entry_bar days are Good-Friday NFP shortened sessions: CME opened")
    print("   for the release, closed before RTH; zero_reaction days are rule-mandated")
    print("   no-trades, not data losses.)")

    # ------------------------------------------------------------ roll-gap guard
    print("\n" + "=" * 78)
    print("ROLL-GAP GUARD — splice detector (pass-1 tick-sigma variant REJECTED, kept")
    print("only as sensitivity B; see script docstring for the full design record)")
    print("=" * 78)
    scan_dates = sorted(day_rets)
    guard_rows = []
    for i, d in enumerate(scan_dates):
        prior = scan_dates[max(0, i - LOCAL_WIN_DAYS):i]
        r, tods = day_rets[d]
        j = int(np.abs(r).argmax())
        others = np.delete(r, j)
        sd_others = float(np.std(others, ddof=1)) if len(others) > 2 else np.nan
        iso_z = abs(float(r[j])) / sd_others if sd_others and sd_others > 0 else np.nan
        if len(prior) >= LOCAL_MIN_DAYS:
            loc_sig = float(np.std(np.concatenate([day_rets[p][0] for p in prior]), ddof=1))
            loc_z = abs(float(r[j])) / loc_sig if loc_sig > 0 else np.nan
        else:
            loc_z = np.nan
        guard_rows.append(dict(date=d, max_abs_ret=abs(float(r[j])),
                               jump_tod=int(tods[j]), local_z=loc_z, iso_z=iso_z,
                               candidate=bool(loc_z > OUTLIER_SIGMA and iso_z > OUTLIER_SIGMA)
                               if np.isfinite(loc_z) and np.isfinite(iso_z) else False))
    G = pd.DataFrame(guard_rows)
    cand = G[G["candidate"]]
    iso_all = G["iso_z"].dropna()
    print(f"[FACT] Days scanned: {len(G)} (window [08:29,10:30], 1-min fractional returns).")
    print(f"[FACT] CANDIDATE 8-sigma jumps (local_z > 8 AND same-day isolation_z > 8): "
          f"{len(cand)} days.")
    print(f"[FACT] Same-day isolation z distribution: p50 {iso_all.quantile(.5):.2f}, "
          f"p99 {iso_all.quantile(.99):.2f}, p99.9 {iso_all.quantile(.999):.2f}, "
          f"MAX {iso_all.max():.1f} — a true splice (permanent one-minute re-basing on an")
    print("  otherwise ordinary day) would print isolation z >> 20; none exists.")
    stamps = cand["jump_tod"].apply(lambda s: f"{s // 3600:02d}:{(s % 3600) // 60:02d}")
    print(f"[FACT] Candidate jump minute stamps: {stamps.value_counts().to_dict()}")
    print("  -> every candidate sits at a macro stamp (08:31 release reaction burst,")
    print("     09:30/09:31 RTH open, 10:01 US data / Fed announcements) — genuine")
    print("     volatility, not contract-roll artifacts.")
    print("[FACT] Structural splice test: the NT8 back-adjusted merge switches contracts")
    print("  at a roll SESSION BOUNDARY (17:00/18:00 ET). An 08:29->10:30 window lies")
    print("  strictly inside one session and can never span a splice.")
    n_roll_excl = 0
    print(f"[VERDICT-INPUT] ROLL-GAP EXCLUSIONS: {n_roll_excl} trades "
          f"(candidates failing the splice test are retained; count reported per spec).")

    # sensitivity masks -----------------------------------------------------
    cand_map = dict(zip(G["date"], zip(G["candidate"], G["jump_tod"])))

    def sens_a_mask(dfr, h):
        """Sensitivity A: drop day at horizon h iff a candidate extreme-vol minute
        falls at or before the horizon's exit stamp."""
        out = []
        for _, rr in dfr.iterrows():
            c, jt = cand_map.get(rr["date"], (False, -1))
            out.append(bool(c and jt <= rr[f"exit{h}_tod"]))
        return np.array(out)

    # sensitivity B: rejected pass-1 detector (pooled tick sigma, release mornings)
    rel_traded = set(T.loc[T["group"] == "release", "date"])
    tick_pop = []
    for date, day in bars.groupby("date", sort=True):
        if date not in rel_traded:
            continue
        m = day[(day["tod"] > T_PRE - 60) & (day["tod"] <= EXITS[60])]
        if len(m) > 1:
            tick_pop.append(np.diff(m["close"].values) / TICK)
    tick_pop = np.concatenate(tick_pop)
    sigma_tick = float(np.std(tick_pop, ddof=1))
    thresh_tick = OUTLIER_SIGMA * sigma_tick
    for h in HORIZONS:
        T[f"exclB{h}"] = T[f"jump{h}_t"] > thresh_tick
    print(f"\n[SENSITIVITY B — rejected pass-1 detector] pooled tick sigma "
          f"{sigma_tick:.3f} t -> threshold {thresh_tick:.1f} t; excluded trades: "
          f"{ {f'{h}min': int(T[f'exclB{h}'].sum()) for h in HORIZONS} } "
          f"(recency-biased: a fixed tick bar over a 5x price rise).")

    T["year"] = pd.to_datetime(T["date"].astype(str)).dt.year
    era_lbl = {e: f"{e[0]}-{e[1]}" for e in ERAS}
    T["era"] = pd.cut(T["year"], [e[0] - 1 for e in ERAS] + [2021],
                      labels=[era_lbl[e] for e in ERAS]).astype(str)
    for h in HORIZONS:
        T[f"exclA{h}"] = False
    for h in HORIZONS:
        T.loc[:, f"exclA{h}"] = sens_a_mask(T, h)

    R = T[T["group"] == "release"].sort_values("date").reset_index(drop=True)
    P = T[T["group"] == "placebo"].sort_values("date").reset_index(drop=True)
    print(f"\n[FACT] RELEASE DAYS TRADED (PRIMARY, roll-guard exclusions 0): {len(R)} of "
          f"{len(rel_days)} calendar days 2006-2021 (expectation was ~380; the gap is "
          f"13 itemized days above). Placebo weekdays traded: {len(P)}.")

    # ------------------------------------------------------------ summary blocks
    rng = np.random.default_rng(SEED)
    summary = []

    def block(scope, group, G_, mask_fn=None, with_ci=True):
        for h in HORIZONS:
            g = G_[~mask_fn(G_, h)] if mask_fn is not None else G_
            x = g[f"net{h}"].values
            lo, hi = boot_ci(x, rng) if (with_ci and len(x)) else (np.nan, np.nan)
            summary.append(dict(scope=scope, group=group, horizon=h, n=len(x),
                                net_c1_t=float(np.mean(x)) if len(x) else np.nan,
                                ci_lo=lo, ci_hi=hi,
                                gross_t=float(g[f"gross{h}"].mean()) if len(x) else np.nan,
                                win_rate=float((x > 0).mean()) if len(x) else np.nan))
        return summary[-3:]

    mA = lambda d, h: d[f"exclA{h}"].values
    mB = lambda d, h: d[f"exclB{h}"].values

    def show(rows, label_w=16):
        for r in rows:
            print(f"{r['group']:>{label_w}} {r['horizon']:>4} {r['n']:>5} "
                  f"{r['net_c1_t']:>+9.3f} {r['ci_lo']:>+9.3f} {r['ci_hi']:>+9.3f} "
                  f"{r['gross_t']:>+9.3f} {100 * r['win_rate']:>5.1f}")

    hdr = (f"{'group':>16} {'h':>4} {'n':>5} {'netC1_t':>9} {'CI_lo':>9} {'CI_hi':>9} "
           f"{'gross_t':>9} {'win%':>6}")

    print("\n" + "=" * 78)
    print(f"POOLED 2006-2021 (PRIMARY) — net C1={C1}t/RT, day-clustered 95% CI, "
          f"{NBOOT} reps, seed {SEED}")
    print("=" * 78)
    print(hdr)
    full_rows = block("full_2006_2021", "release", R)
    show(full_rows)
    plac_rows = block("full_2006_2021", "placebo", P)
    show(plac_rows)
    print("  sensitivity A (extreme-vol candidate days excluded — NOT roll artifacts):")
    show(block("full_sensA_extremevol", "release_sensA", R, mA))
    print("  sensitivity B (rejected pass-1 tick-sigma filter, recency-biased):")
    show(block("full_sensB_ticksigma", "release_sensB", R, mB))

    print("\n" + "=" * 78)
    print("SUBPERIOD 2015-2021 (verdict input) + 2006-2014 complement (PRIMARY)")
    print("=" * 78)
    print(hdr)
    sub_rows = block("sub_2015_2021", "release", R[R["year"] >= 2015])
    show(sub_rows)
    show(block("sub_2015_2021", "placebo", P[P["year"] >= 2015]))
    show(block("sub_2006_2014", "release", R[R["year"] < 2015]))
    show(block("sub_2006_2014", "placebo", P[P["year"] < 2015]))

    print("\n" + "=" * 78)
    print("BY 4-YEAR ERA (PRIMARY; release with placebo alongside)")
    print("=" * 78)
    print(hdr)
    for e in ERAS:
        lbl = era_lbl[e]
        show(block(f"era_{lbl}", f"rel {lbl}", R[R["era"] == lbl]))
        show(block(f"era_{lbl}", f"plc {lbl}", P[P["era"] == lbl]))

    print("\n" + "=" * 78)
    print("BY EVENT TYPE (PRIMARY release)")
    print("=" * 78)
    print(hdr)
    for et in sorted(R["event_type"].unique()):
        show(block(f"etype_{et}", et, R[R["event_type"] == et]))

    print("\n" + "=" * 78)
    print("BY YEAR (PRIMARY release; all horizons in CSV)")
    print("=" * 78)
    print(hdr)
    for y in sorted(R["year"].unique()):
        show(block(f"year{y}", f"rel {y}", R[R["year"] == y]))

    S = pd.DataFrame(summary)

    # ------------------------------------------ concentration / worst / equity
    print("\n" + "=" * 78)
    print("CONCENTRATION / WORST TRADE (PRIMARY release; $ at 1 NQ = $5/t, context)")
    print("=" * 78)
    conc = []
    for h in HORIZONS:
        net = R[f"net{h}"]
        tot = float(net.sum())
        top5 = net.nlargest(5)
        bot5 = net.nsmallest(5)
        pos_sum = float(net[net > 0].sum())
        iw = int(net.idxmin())
        cum = net.cumsum()
        dd = cum - cum.cummax()
        conc.append(dict(horizon=h, n=len(net), total_net_t=tot,
                         total_net_usd_1nq=tot * USD_PER_TICK,
                         max_dd_t=float(dd.min()),
                         worst_trade_t=float(net.iloc[iw]),
                         worst_trade_date=str(R.loc[iw, "date"]),
                         worst_trade_event=R.loc[iw, "event_type"],
                         top5_sum_t=float(top5.sum()),
                         top5_share_of_total=(float(top5.sum() / tot) if tot > 0 else np.nan),
                         top5_share_of_gross_wins=(float(top5.sum() / pos_sum) if pos_sum > 0 else np.nan),
                         top5_dates=";".join(str(R.loc[i, "date"]) for i in top5.index),
                         bot5_sum_t=float(bot5.sum()),
                         bot5_dates=";".join(str(R.loc[i, "date"]) for i in bot5.index)))
        c = conc[-1]
        print(f"  h={h}min: total {tot:+.1f} t (${tot * USD_PER_TICK:+,.0f}) on n={len(net)}; "
              f"max DD {c['max_dd_t']:+.1f} t")
        print(f"    worst {c['worst_trade_t']:+.1f} t on {c['worst_trade_date']} "
              f"({c['worst_trade_event']})")
        ts = c['top5_share_of_total']
        print(f"    top-5 winners {c['top5_sum_t']:+.1f} t = "
              f"{('n/a (total<=0)' if not np.isfinite(ts) else f'{100 * ts:.1f}% of total net')}, "
              f"{100 * c['top5_share_of_gross_wins']:.1f}% of gross wins")
        print(f"    top-5 dates: {c['top5_dates']}")
        print(f"    bottom-5 {c['bot5_sum_t']:+.1f} t ({c['bot5_dates']})")
    conc_df = pd.DataFrame(conc)

    # ------------------------------------------------------- rolling 3-year mean
    ser = R.set_index(pd.to_datetime(R["date"].astype(str)))["net15"]
    roll = ser.rolling("1095D", min_periods=24).mean()
    roll_df = pd.DataFrame({"date": roll.index,
                            "rolling_1095d_mean_net15_t": roll.values,
                            "n_in_window": ser.rolling("1095D", min_periods=24).count().values})
    rv = roll.dropna()
    print(f"\n[FACT] Rolling 3-year (1095D, min 24 trades) mean of PRIMARY release net15:")
    print(f"  first {rv.index[0].date()} = {rv.iloc[0]:+.2f} t | min {rv.min():+.2f} t "
          f"({rv.idxmin().date()}) | max {rv.max():+.2f} t ({rv.idxmax().date()}) | "
          f"last {rv.index[-1].date()} = {rv.iloc[-1]:+.2f} t")
    print(f"  share of rolling observations < 0: {float((rv < 0).mean()):.3f}")

    # ------------------------------------------------- w8 2022+ reconciliation
    print("\n" + "=" * 78)
    print("RECONCILIATION — 2022+ IN-SAMPLE numbers from committed w8_bfade artifacts")
    print("(context ONLY; never pooled with the 2006-2021 confirmation stats)")
    print("=" * 78)
    w8 = pd.read_csv(W8SUM)
    w8p = w8[(w8["scope"] == "pooled") & (w8["group"] == "release")]
    print(f"{'window':>22} {'h':>4} {'n':>5} {'netC1_t':>9} {'CI_lo':>9} {'CI_hi':>9}")
    for h in HORIZONS:
        r8 = w8p[w8p["horizon"] == h].iloc[0]
        print(f"{'w8 2022-2026-05 (IS)':>22} {h:>4} {int(r8['n']):>5} {r8['net_c1_t']:>+9.3f} "
              f"{r8['ci_lo']:>+9.3f} {r8['ci_hi']:>+9.3f}")
        rf = [r for r in full_rows if r["horizon"] == h][0]
        print(f"{'w9 2006-2021 (OOS)':>22} {h:>4} {rf['n']:>5} {rf['net_c1_t']:>+9.3f} "
              f"{rf['ci_lo']:>+9.3f} {rf['ci_hi']:>+9.3f}")

    # ------------------------------------------------------------------ verdict
    f15 = [r for r in full_rows if r["horizon"] == 15][0]
    s15 = [r for r in sub_rows if r["horizon"] == 15][0]
    p15 = [r for r in plac_rows if r["horizon"] == 15][0]
    full_pass = (f15["net_c1_t"] > 0) and (f15["ci_lo"] > 0)
    sub_point_pos = s15["net_c1_t"] > 0
    sub_ci_pass = (s15["n"] > 0) and (s15["ci_lo"] > 0)
    refuted = f15["ci_hi"] < 0
    if full_pass and sub_point_pos:
        verdict = "CONFIRMED"
    elif sub_ci_pass and not full_pass:
        verdict = "PARTIALLY-SUPPORTED"
    elif refuted:
        verdict = "REFUTED"
    else:
        verdict = "UNCONFIRMED-POSSIBLY-RECENT"
    placebo_flat = (p15["ci_lo"] <= 0 <= p15["ci_hi"])
    print("\n" + "=" * 78)
    print("AMENDED FOUR-WAY VERDICT (frozen; PRIMARY = 15-min exit, all traded release")
    print("days — roll-gap guard excluded 0 trades)")
    print("=" * 78)
    print(f"  full 2006-2021 @15min : net {f15['net_c1_t']:+.3f} t, "
          f"CI [{f15['ci_lo']:+.3f}, {f15['ci_hi']:+.3f}], n={f15['n']} "
          f"-> net>0 & CI_lo>0: {'PASS' if full_pass else 'FAIL'}")
    print(f"  sub 2015-2021 @15min  : net {s15['net_c1_t']:+.3f} t, "
          f"CI [{s15['ci_lo']:+.3f}, {s15['ci_hi']:+.3f}], n={s15['n']} "
          f"-> point>0: {'PASS' if sub_point_pos else 'FAIL'}; CI_lo>0: "
          f"{'PASS' if sub_ci_pass else 'FAIL'}")
    print(f"  refutation check      : full CI_hi {f15['ci_hi']:+.3f} < 0 ? "
          f"{'YES -> REFUTED' if refuted else 'no'}")
    print(f"  placebo @15min (ctx)  : net {p15['net_c1_t']:+.3f} t, "
          f"CI [{p15['ci_lo']:+.3f}, {p15['ci_hi']:+.3f}], n={p15['n']} "
          f"-> flat (CI covers 0): {placebo_flat}")
    print(f"\n  VERDICT: {verdict}")
    if verdict == "CONFIRMED":
        print("  -> per spec: Program-B candidate freeze (robustness -> Tier-3 single holdout).")
    elif verdict == "PARTIALLY-SUPPORTED":
        print("  -> per spec: park as candidate-with-caveat, weight on recent regime.")
    elif verdict == "UNCONFIRMED-POSSIBLY-RECENT":
        print("  -> per spec: PARKED, not closed — possibly a post-2020 regime product;")
        print("     resolution only via forward data or Tier-3 holdout with a frozen candidate.")
    else:
        print("  -> per spec: B-FADE CLOSED — old data actively contradicts the fade.")

    # ------------------------------------------------------------------ artifacts
    T.to_csv(ART / "w9bfade_trades.csv", index=False)
    S.to_csv(ART / "w9bfade_summary.csv", index=False)
    roll_df.to_csv(ART / "w9bfade_rolling_3y.csv", index=False)
    excl_df.to_csv(ART / "w9bfade_excluded.csv", index=False)
    conc_df.to_csv(ART / "w9bfade_concentration.csv", index=False)
    G.to_csv(ART / "w9bfade_guard_scan.csv", index=False)
    print(f"\n[FACT] Artifacts written to {ART.relative_to(ROOT)}: w9bfade_trades.csv, "
          f"w9bfade_summary.csv, w9bfade_rolling_3y.csv, w9bfade_excluded.csv, "
          f"w9bfade_concentration.csv, w9bfade_guard_scan.csv, w9bfade_stdout.txt")
    print("\nW9BFADE CONFIRMATION DONE")
    return verdict


if __name__ == "__main__":
    ART.mkdir(parents=True, exist_ok=True)
    with open(ART / "w9bfade_stdout.txt", "w", encoding="utf-8") as f:
        sys.stdout = Tee(sys.__stdout__, f)
        try:
            main()
        finally:
            sys.stdout = sys.__stdout__
