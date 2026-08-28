"""GENESIS_BASELINES_20260828 — preregistered baseline controls B0..B6.

Executes the frozen spec at runs/GENESIS_BASELINES_20260828/spec.yaml. ZERO parameter
search: every constant below is the spec's frozen value. Baselines are CONTROLS and can
never be promoted. All gate/verdict tables are printed BY THIS PROGRAM (rule 7).

Conventions (stated per orchestrator instruction, frozen before results):
- Substrate: runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet — 1-min END-stamped bars in
  exchange-session (ET) wall-clock time. The bar stamped 09:31 covers 09:30:00-09:31:00,
  so its OPEN is the 09:30:00 price (TRUE RTH open). Sessions 18:00->17:00 ET:
  session_id = calendar date, with hour>=18 rolling forward to the next day's label
  (runlib/session_boundary convention).
- SEAL: program asserts max bar timestamp < 2026-08-01 BEFORE computing anything.
- Weekly bucket: ISO (year, week) of the session date. The common week grid = every ISO
  week containing >=1 session in the population; a baseline that does not trade in a week
  contributes $0 that week (incumbent's-population convention, identical across rows).
- Costs: $4.36 commission + $14.44 modelled spread = $18.80 per contract round trip.
  * B1a: ONE round trip total across the whole window (entry at first bar's open, exit at
    window edge). Charged $9.40 in the first week and $9.40 in the last week; weekly P&L
    is mark-to-market of session closes. NO other RT ever (per instruction).
  * B1b / B3: one RT per session traded, charged in that session's week.
  * B2 / B4: daily sign positions; one RT charged ONLY when the position changes sign
    (including 0->+1/0->-1 entries; a +1->-1 reversal is charged as ONE RT per the
    orchestrator's stated convention — this understates a true reversal cost, documented).
- $20/pt, 1 contract throughout. Metrics: gross $/wk, net $/wk, weekly Sharpe
  (mean/std of net weekly), weekly t (Sharpe*sqrt(Nweeks)), maxDD on cumulative net
  weekly equity, net at fixed $20,245 DD = net$/wk * 20245/maxDD, % positive weeks
  (net>0), worst week (net).
- B5: read-only from runs/WE_W103_CONSOLIDATE/out artifacts; NOTHING recomputed. The out/
  directory contains ONLY aggregate rows (components.csv etc.), no per-week series file,
  so gross $/wk and weekly Sharpe are unobtainable -> row filled from the artifact's own
  aggregates where they exist, remaining cells NA, ledger result DEFECT (missing input;
  rule: never improvise a different baseline).
- B6: convex combination (weights sum to 1) of B1a and B2 WEEKLY NET series. At each week
  boundary, weight_i ∝ 1 / vol_i where vol_i = std of component i's NET daily P&L over
  the trailing 63 sessions strictly before the week's first session (frozen a priori;
  63 is the spec's only trailing constant). If fewer than 63 prior sessions exist or
  either vol is 0, weights are 0.5/0.5 (a priori rule, no search).
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "GENESIS_BASELINES_20260828")
OUT = os.path.join(RUN, "out")
PARQUET = os.path.join(ROOT, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet")
W103_COMPONENTS = os.path.join(ROOT, "runs", "WE_W103_CONSOLIDATE", "out", "components.csv")

POINT_VALUE = 20.0          # $/pt, spec
RT_COST = 4.36 + 14.44      # $18.80 per contract round trip, spec
LOOKBACK = 63               # spec-frozen, B2 and B6 only
FIXED_DD = 20245.0          # P1's normalization, spec
SEAL_DATE = pd.Timestamp("2026-08-01")

TRIAL_IDS = {"B0": "G00001", "B1a": "G00002", "B1b": "G00003", "B2": "G00004",
             "B3": "G00005", "B4": "G00006", "B5": "G00007", "B6": "G00008"}


def log(msg: str) -> None:
    print(msg, flush=True)


def session_id(ts: pd.Series) -> pd.Series:
    """END-stamped ET bar timestamp -> session date (hour>=18 rolls to next day)."""
    d = ts.dt.normalize()
    return (d + pd.to_timedelta((ts.dt.hour >= 18).astype(int), unit="D")).dt.date


def iso_week_label(dates: pd.Series) -> pd.Series:
    iso = pd.to_datetime(dates).dt.isocalendar()
    return iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)


def metrics_from_weekly(gross_w: pd.Series, net_w: pd.Series) -> dict:
    """All headline metrics from aligned weekly gross/net series on the common grid."""
    n = len(net_w)
    mean_net = float(net_w.mean())
    std_net = float(net_w.std(ddof=1))
    sharpe = mean_net / std_net if std_net > 0 else float("nan")
    tstat = sharpe * math.sqrt(n) if std_net > 0 else float("nan")
    eq = net_w.cumsum()
    dd = float((eq.cummax() - eq).max())
    fixdd = mean_net * FIXED_DD / dd if dd > 0 else float("nan")
    return {
        "gross_per_wk": float(gross_w.mean()),
        "net_per_wk": mean_net,
        "weekly_sharpe": sharpe,
        "weekly_t": tstat,
        "maxDD": dd,
        "net_at_fixed_20245_DD": fixdd,
        "pct_positive_weeks": float((net_w > 0).mean() * 100.0),
        "worst_week": float(net_w.min()),
        "n_weeks": n,
    }


def main() -> None:
    os.makedirs(OUT, exist_ok=True)

    log("loading substrate ...")
    df = pd.read_parquet(PARQUET)
    df = df.sort_values("time").reset_index(drop=True)

    # ---- SEAL assertion BEFORE anything else ----
    max_ts = df["time"].max()
    seal_ok = max_ts < SEAL_DATE
    if not seal_ok:
        raise RuntimeError(f"SEAL VIOLATION: substrate max timestamp {max_ts} >= 2026-08-01")

    df["sid"] = session_id(df["time"])
    sessions = pd.Index(sorted(df["sid"].unique()))
    n_sessions = len(sessions)
    first_sid, last_sid = sessions[0], sessions[-1]
    log(f"sessions: {n_sessions}  [{first_sid} .. {last_sid}]  bars={len(df)}")

    # per-session aggregates
    g = df.groupby("sid", sort=True)
    sess_close = g["close"].last()                       # session close (last bar's close)
    sess_last_time = g["time"].last()

    # common ISO week grid
    sid_series = pd.Series(sessions)
    week_of_sid = pd.Series(iso_week_label(sid_series).values, index=sessions)
    week_grid = pd.Index(pd.unique(week_of_sid.values))  # ordered by first appearance (sorted sids)
    n_weeks = len(week_grid)
    log(f"ISO week grid: {n_weeks} weeks  [{week_grid[0]} .. {week_grid[-1]}]")

    def to_weekly(by_session: pd.Series) -> pd.Series:
        """Sum a per-session $ series into the common week grid (0 where absent)."""
        s = pd.Series(by_session, index=sessions).fillna(0.0)
        wk = s.groupby(week_of_sid.values).sum()
        return wk.reindex(week_grid, fill_value=0.0)

    rows = {}
    ledger = []
    conventions_extra = []

    # ================= B0: cash =================
    zero_w = pd.Series(0.0, index=week_grid)
    m = metrics_from_weekly(zero_w, zero_w)
    rows["B0_cash"] = m
    ledger.append({"trial_id": TRIAL_IDS["B0"], "metrics": m, "result": "NULL",
                   "note": "cash anchor, $0/wk by definition; control, not promotable"})

    # ================= B1a: always-long, held =================
    entry_price = float(df["open"].iloc[0])              # first bar's open of window
    daily_mark = sess_close.diff() * POINT_VALUE
    daily_mark.iloc[0] = (sess_close.iloc[0] - entry_price) * POINT_VALUE
    gross_w_b1a = to_weekly(daily_mark)
    cost_w_b1a = pd.Series(0.0, index=week_grid)
    cost_w_b1a.iloc[0] += RT_COST / 2.0                  # entry half-RT, first week
    cost_w_b1a.iloc[-1] += RT_COST / 2.0                 # window-edge exit half-RT, last week
    net_w_b1a = gross_w_b1a - cost_w_b1a
    m = metrics_from_weekly(gross_w_b1a, net_w_b1a)
    m["total_RT"] = 1
    rows["B1a_always_long_held"] = m
    ledger.append({"trial_id": TRIAL_IDS["B1a"], "metrics": m, "result": "NULL",
                   "note": ("always-long 1 NQ entered once at first bar open "
                            f"({entry_price}), weekly M2M; ONE total RT split $9.40 first / "
                            "$9.40 last week (window edges only); control")})

    # ================= B1b: always-long RTH only =================
    b931 = df[(df["time"].dt.hour == 9) & (df["time"].dt.minute == 31)].set_index("sid")
    b1559 = df[(df["time"].dt.hour == 15) & (df["time"].dt.minute == 59)].set_index("sid")
    common = b931.index.intersection(b1559.index)
    pnl_b1b = (b1559.loc[common, "close"] - b931.loc[common, "open"]) * POINT_VALUE
    skipped_b1b = n_sessions - len(common)
    gross_w = to_weekly(pnl_b1b)
    net_w = to_weekly(pnl_b1b - RT_COST)
    m = metrics_from_weekly(gross_w, net_w)
    m["sessions_traded"] = int(len(common))
    m["sessions_skipped_missing_bars"] = int(skipped_b1b)
    rows["B1b_always_long_RTH"] = m
    ledger.append({"trial_id": TRIAL_IDS["B1b"], "metrics": m, "result": "NULL",
                   "note": ("buy open of 09:31-stamped bar (=09:30:00 TRUE RTH open), exit "
                            "close of 15:59-stamped bar; 1 RT/session; sessions missing "
                            "either bar (holidays/early closes) not traded; control")})

    # ================= B2: daily TSMOM 63 =================
    c = sess_close
    sig_b2 = np.sign(c - c.shift(LOOKBACK))              # signal known at close t
    pos_b2 = sig_b2.shift(1).fillna(0.0)                 # applied to NEXT session t+1
    ret_d = c.diff() * POINT_VALUE
    pnl_b2 = pos_b2 * ret_d.fillna(0.0)
    chg_b2 = pos_b2 != pos_b2.shift(1).fillna(0.0)
    cost_b2 = chg_b2.astype(float) * RT_COST
    n_rt_b2 = int(chg_b2.sum())
    gross_w = to_weekly(pnl_b2)
    net_w = to_weekly(pnl_b2 - cost_b2)
    m = metrics_from_weekly(gross_w, net_w)
    m["n_position_changes_RT"] = n_rt_b2
    rows["B2_tsmom_63"] = m
    ledger.append({"trial_id": TRIAL_IDS["B2"], "metrics": m, "result": "NULL",
                   "note": ("sign(trailing 63-session close-to-close) applied to next "
                            "session c2c; flat first 63 sessions; 1 RT per sign change "
                            "(incl. entries; reversal charged as ONE RT per stated "
                            "convention); control")})
    net_w_b2 = net_w
    pnl_net_daily_b2 = pnl_b2 - cost_b2

    # ================= B3: opening-range breakout =================
    hm = df["time"].dt.hour * 100 + df["time"].dt.minute
    or_bars = df[(hm >= 931) & (hm <= 1000)]
    or_high = or_bars.groupby("sid")["high"].max()
    or_low = or_bars.groupby("sid")["low"].min()
    scan = df[(hm >= 1001) & (hm <= 1559)]
    exit_close = b1559["close"]

    pnl_b3 = {}
    n_long = n_short = n_ambig = n_skip = 0
    scan_g = dict(tuple(scan.groupby("sid")))
    for sid in sessions:
        if sid not in or_high.index or sid not in exit_close.index or sid not in scan_g:
            n_skip += 1
            continue
        oh, ol = or_high.loc[sid], or_low.loc[sid]
        sbars = scan_g[sid]
        up = sbars["high"].values > oh
        dn = sbars["low"].values < ol
        hit = up | dn
        if not hit.any():
            continue
        i = int(np.argmax(hit))
        if up[i] and dn[i]:
            n_ambig += 1                                  # bar breaks both sides: no trade
            continue
        o = float(sbars["open"].values[i])
        if up[i]:
            entry = max(oh, o)                            # stop-entry fill
            pnl_b3[sid] = (float(exit_close.loc[sid]) - entry) * POINT_VALUE
            n_long += 1
        else:
            entry = min(ol, o)
            pnl_b3[sid] = (entry - float(exit_close.loc[sid])) * POINT_VALUE
            n_short += 1
    pnl_b3 = pd.Series(pnl_b3, dtype=float)
    gross_w = to_weekly(pnl_b3)
    net_w = to_weekly(pnl_b3 - RT_COST)
    m = metrics_from_weekly(gross_w, net_w)
    m.update({"trades_long": n_long, "trades_short": n_short,
              "ambiguous_both_side_bars_skipped": n_ambig,
              "sessions_skipped_missing_bars": n_skip})
    rows["B3_orb_0930_1000"] = m
    ledger.append({"trial_id": TRIAL_IDS["B3"], "metrics": m, "result": "NULL",
                   "note": ("OR=09:30-10:00 (bars stamped 09:31..10:00); first strict "
                            "break after 10:00, stop-entry fill max/min(level, bar open); "
                            "bar breaking both sides in one minute = no trade (ambiguous); "
                            "exit 15:59 close; no stop; 1 RT/session traded; control")})

    # ================= B4: daily mean reversion lag-1 =================
    sig_b4 = -np.sign(c.diff())
    pos_b4 = sig_b4.shift(1).fillna(0.0)
    pnl_b4 = pos_b4 * ret_d.fillna(0.0)
    chg_b4 = pos_b4 != pos_b4.shift(1).fillna(0.0)
    cost_b4 = chg_b4.astype(float) * RT_COST
    gross_w = to_weekly(pnl_b4)
    net_w = to_weekly(pnl_b4 - cost_b4)
    m = metrics_from_weekly(gross_w, net_w)
    m["n_position_changes_RT"] = int(chg_b4.sum())
    rows["B4_meanrev_lag1"] = m
    ledger.append({"trial_id": TRIAL_IDS["B4"], "metrics": m, "result": "NULL",
                   "note": ("fade sign of prior session c2c over next session, mirror of "
                            "B2 at lag 1; 1 RT per sign change (stated convention); "
                            "control")})

    # ================= B5: incumbent P1_PCT from W103 artifacts (read-only) =================
    comp = pd.read_csv(W103_COMPONENTS)
    p1 = comp[comp["component"] == "P1_PCT"].iloc[0]
    m = {
        "gross_per_wk": float("nan"),                    # not present in artifacts
        "net_per_wk": float(p1["weekly"]),
        "weekly_sharpe": float("nan"),                   # weekly series not in artifacts
        "weekly_t": float(p1["t"]),
        "maxDD": float(p1["maxdd"]),
        "net_at_fixed_20245_DD": float(p1["fixdd"]),
        "pct_positive_weeks": float(p1["poswk"]),
        "worst_week": float(p1["worst"]),
        "n_weeks": float("nan"),
        "trades": int(p1["trades"]),
    }
    rows["B5_incumbent_P1_PCT"] = m
    ledger.append({"trial_id": TRIAL_IDS["B5"], "metrics": m, "result": "DEFECT",
                   "note": ("WE_W103_CONSOLIDATE/out contains ONLY aggregate artifacts "
                            "(components.csv etc.), no per-week series file; per spec "
                            "nothing recomputed. Row filled from the artifact's own "
                            "aggregate P1_PCT line; gross/wk and weekly Sharpe "
                            "unobtainable -> DEFECT (missing input), not improvised.")})

    # ================= B6: inverse-vol combo of B1a + B2 =================
    d_b1a = pd.Series(daily_mark, index=sessions).fillna(0.0)   # B1a net daily = gross (edge costs excluded from vol input)
    d_b2 = pd.Series(pnl_net_daily_b2, index=sessions).fillna(0.0)
    week_first_pos = {}                                   # first session ordinal per week
    sid_pos = {s: i for i, s in enumerate(sessions)}
    for s in sessions:
        w = week_of_sid.loc[s]
        week_first_pos.setdefault(w, sid_pos[s])
    w1 = pd.Series(index=week_grid, dtype=float)
    w2 = pd.Series(index=week_grid, dtype=float)
    a1, a2 = d_b1a.values, d_b2.values
    for w in week_grid:
        p = week_first_pos[w]
        if p < LOOKBACK:
            w1[w], w2[w] = 0.5, 0.5
            continue
        v1 = float(np.std(a1[p - LOOKBACK:p], ddof=1))
        v2 = float(np.std(a2[p - LOOKBACK:p], ddof=1))
        if v1 <= 0 or v2 <= 0:
            w1[w], w2[w] = 0.5, 0.5
        else:
            iv1, iv2 = 1.0 / v1, 1.0 / v2
            w1[w] = iv1 / (iv1 + iv2)
            w2[w] = iv2 / (iv1 + iv2)
    gross_w = w1 * gross_w_b1a + w2 * to_weekly(pnl_b2)
    net_w = w1 * net_w_b1a + w2 * net_w_b2
    m = metrics_from_weekly(gross_w, net_w)
    m["mean_weight_B1a"] = float(w1.mean())
    m["mean_weight_B2"] = float(w2.mean())
    rows["B6_invvol_B1a_B2"] = m
    ledger.append({"trial_id": TRIAL_IDS["B6"], "metrics": m, "result": "NULL",
                   "note": ("convex combo of B1a+B2 weekly NET; weights inverse of std of "
                            "each component's daily P&L over trailing 63 sessions strictly "
                            "before each week (a priori); 0.5/0.5 before 63 sessions or on "
                            "zero vol; control")})

    # ================= outputs =================
    order = ["B0_cash", "B1a_always_long_held", "B1b_always_long_RTH", "B2_tsmom_63",
             "B3_orb_0930_1000", "B4_meanrev_lag1", "B5_incumbent_P1_PCT",
             "B6_invvol_B1a_B2"]
    cols = ["gross_per_wk", "net_per_wk", "weekly_sharpe", "weekly_t", "maxDD",
            "net_at_fixed_20245_DD", "pct_positive_weeks", "worst_week", "n_weeks"]
    table = pd.DataFrame({k: {c: rows[k].get(c, float("nan")) for c in cols}
                          for k in order}).T
    table.index.name = "baseline"
    table.to_csv(os.path.join(OUT, "baseline_table.csv"), float_format="%.4f")

    # weekly net series artifact (computed rows only)
    weekly_df = pd.DataFrame({
        "B0_cash": zero_w, "B1a_always_long_held": net_w_b1a,
        "B1b_always_long_RTH": to_weekly(pnl_b1b - RT_COST),
        "B2_tsmom_63": net_w_b2,
        "B3_orb_0930_1000": to_weekly(pnl_b3 - RT_COST),
        "B4_meanrev_lag1": to_weekly(pnl_b4 - cost_b4),
        "B6_invvol_B1a_B2": net_w,
    })
    weekly_df.index.name = "iso_week"
    weekly_df.to_csv(os.path.join(OUT, "weekly_net_series.csv"), float_format="%.2f")

    with open(os.path.join(OUT, "ledger_result_pending.json"), "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, default=float)

    # ---- gate table, printed by program ----
    lines = []
    ap = lines.append
    ap("GENESIS_BASELINES_20260828 — GATE / SPEC / OBSERVED / VERDICT (printed by src/run_baselines.py)")
    ap("=" * 118)
    ap(f"{'GATE':<28} {'SPEC':<44} {'OBSERVED':<32} VERDICT")
    ap("-" * 118)
    ap(f"{'SEAL':<28} {'max bar ts < 2026-08-01':<44} {str(max_ts):<32} {'PASS' if seal_ok else 'FAIL'}")
    pop_ok = (str(first_sid) == "2022-01-03") and (str(last_sid) == "2026-07-31")
    ap(f"{'POPULATION':<28} {'sessions 2022-01 .. 2026-07-31':<44} {f'{first_sid}..{last_sid} n={n_sessions}':<32} {'PASS' if pop_ok else 'FAIL'}")
    ap(f"{'COST_MODEL':<28} {'$4.36 + $14.44 = $18.80/ctrRT':<44} {f'{RT_COST:.2f} $/ctrRT':<32} {'PASS' if abs(RT_COST-18.80)<1e-9 else 'FAIL'}")
    ap(f"{'MULTIPLICITY':<28} {'exactly 8 preregistered rows, zero search':<44} {f'{len(order)} rows, 0 searched params':<32} {'PASS' if len(order)==8 else 'FAIL'}")
    ap(f"{'WEEK_GRID':<28} {'ISO week of session date, common grid':<44} {f'{n_weeks} weeks':<32} INFO")
    ap("-" * 118)
    ap("BASELINE OUTCOMES (controls: no promotion gate exists; factual record only; ledger token NULL, B5 DEFECT)")
    ap("-" * 118)
    ap(f"{'baseline':<24} {'gross$/wk':>10} {'net$/wk':>10} {'wkSharpe':>9} {'t':>7} {'maxDD':>10} {'net@$20,245DD':>14} {'%pos':>6} {'worst wk':>10}  outcome")
    for k in order:
        r = rows[k]
        def fmt(v, p=2):
            return "NA" if (v is None or (isinstance(v, float) and math.isnan(v))) else f"{v:,.{p}f}"
        outcome = "DEFECT (no weekly series in artifacts)" if k == "B5_incumbent_P1_PCT" else (
            "NULL (loses/flat net)" if (rows[k]["net_per_wk"] <= 0 or math.isnan(rows[k]["net_per_wk"])) else "NULL (control; positive net, not promotable)")
        ap(f"{k:<24} {fmt(r['gross_per_wk']):>10} {fmt(r['net_per_wk']):>10} {fmt(r['weekly_sharpe'],3):>9} {fmt(r['weekly_t'],2):>7} {fmt(r['maxDD']):>10} {fmt(r['net_at_fixed_20245_DD']):>14} {fmt(r['pct_positive_weeks'],1):>6} {fmt(r['worst_week']):>10}  {outcome}")
    ap("-" * 118)
    ap("Conventions: B1a one RT total split across window edges ($9.40 first wk / $9.40 last wk), weekly mark-to-market;")
    ap("  B2/B4 one RT only when the daily position changes sign (reversal charged as ONE RT per stated convention);")
    ap("  B1b/B3 one RT per session traded; 09:31-stamped bar's OPEN is the 09:30:00 TRUE RTH open (END-stamped bars);")
    ap("  B3 stop-entry fill at max/min(OR level, bar open), both-side breakout bar = no trade; untraded weeks = $0 on the")
    ap("  common ISO-week grid; Sharpe/t on weekly nets (weekly aggregation absorbs within-week session clustering).")
    ap(f"B1b sessions traded={rows['B1b_always_long_RTH']['sessions_traded']}, skipped={rows['B1b_always_long_RTH']['sessions_skipped_missing_bars']}; "
       f"B2 RTs={rows['B2_tsmom_63']['n_position_changes_RT']}; B4 RTs={rows['B4_meanrev_lag1']['n_position_changes_RT']}; "
       f"B3 long={rows['B3_orb_0930_1000']['trades_long']}, short={rows['B3_orb_0930_1000']['trades_short']}, ambiguous={rows['B3_orb_0930_1000']['ambiguous_both_side_bars_skipped']}, skipped={rows['B3_orb_0930_1000']['sessions_skipped_missing_bars']}")
    ap("B5 read-only from WE_W103_CONSOLIDATE/out/components.csv (P1_PCT row); no weekly-series artifact exists there ->")
    ap("  gross$/wk and weekly Sharpe NA, ledger DEFECT; its t/maxDD/fixDD/%pos/worst are the artifact's own numbers.")
    gate_txt = "\n".join(lines) + "\n"
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write(gate_txt)
    log(gate_txt)
    log("DONE")


if __name__ == "__main__":
    sys.exit(main())
