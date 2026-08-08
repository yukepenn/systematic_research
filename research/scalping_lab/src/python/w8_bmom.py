"""W8-1 — B-MOM: intraday momentum family build (Program B; frozen spec W8_programs_final.md §W8-1).

Frozen rule (implemented EXACTLY as specified, commit cf7041f)
--------------------------------------------------------------
- Data: runs/AUDIT03_BARS/nq_3m_2022_2026.csv (3-min bars, END-stamped, exchange ET).
  CONTAMINATION RULE: dev window ends 2026-05-31; rows with timestamp >= 2026-06-01
  are dropped at load and never used (sealed holdout).
- RTH bars 09:30-16:00 (END stamps 09:33 .. 16:00; the 09:33-stamped bar's open is
  the 09:30 open — verified present on every RTH session).
- Noise band around the 09:30 open: upper/lower = open0930 +/- m_tod, where m_tod is
  the trailing 14-day mean of |close(slot) - open0930| for the SAME 3-min slot-of-day,
  PRIOR days only (asserted: no same-day leakage). Per-slot rolling over that slot's
  prior observations (half-day sessions simply lack afternoon slots).
- RTH-anchored VWAP from bar close x volume (cumulative, includes current bar).
- LONG when close > max(upper, VWAP); SHORT when close < min(lower, VWAP); otherwise
  signal persistence: hold current position until opposite signal or the 15:57
  close-out (always flat overnight). Early-close sessions force-flat at the last RTH
  bar stamped <= 15:57. One position, 1 NQ. Fills at signal-bar close (family
  convention); C1 = 2.872 ticks per round trip; C2 = 4.872 stress.
- First 14 sessions of the CSV have no band history -> excluded (count reported).
- Neighbors 10/20-day noise windows: REPORTED, NEVER SELECTED.
- Frozen promotion gate (evaluated at C1 on the 14-day frozen rule only):
    (1) mean daily net C1 > 0 with bootstrap CI_lo > 0
    (2) trade-level PF >= 1.10
    (3) rho_full (daily P&L vs Solar net_v1) < 0.3
    (4) losing-day rho (Solar net_v1 < 0 subset) <= 0.1
    (5) top-5-day concentration (top-5 daily net / total net) < 40%
- Seed 20260808; 1000 bootstrap reps; day-clustered CIs.

Outputs -> research/scalping_lab/artifacts/w8_bmom/
"""

from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]  # .../systematic_research
BARS_CSV = ROOT / "runs" / "AUDIT03_BARS" / "nq_3m_2022_2026.csv"
LEDGER_CSV = ROOT / "runs" / "E10MASTER_V2" / "out" / "daily_v1_v2.csv"
ART = ROOT / "research" / "scalping_lab" / "artifacts" / "w8_bmom"

DEV_END = pd.Timestamp("2026-05-31 23:59:59")  # contamination boundary (inclusive)
TICK_USD = 5.0            # NQ $ per tick (0.25 pt)
TICKS_PER_PT = 4.0
C1_TICKS = 2.872          # frozen friction per round trip, ticks
C2_TICKS = 4.872          # stress friction
SEED = 20260808
N_BOOT = 1000
WINDOW_FROZEN = 14
NEIGHBOR_WINDOWS = [10, 20]

RTH_FIRST = "09:33"       # END stamp of the first RTH bar (covers 09:30-09:33)
RTH_LAST = "16:00"
DECISION_LAST = "15:54"   # last END stamp at which a new/flip signal may act
CLOSEOUT_TOD = "15:57"    # force-flat at close of this END stamp (or last bar <= it)


# ----------------------------------------------------------------------------- load
def load_bars() -> pd.DataFrame:
    df = pd.read_csv(BARS_CSV, parse_dates=["time"])
    n_total = len(df)
    df = df[df["time"] <= DEV_END].copy()  # contamination truncation, applied at load
    print(f"[load] bars rows total={n_total}, kept (<= {DEV_END.date()})={len(df)}, "
          f"dropped sealed-holdout rows={n_total - len(df)}")
    print(f"[load] bar time range kept: {df['time'].min()} .. {df['time'].max()}")
    df["date"] = df["time"].dt.normalize()
    df["tod"] = df["time"].dt.strftime("%H:%M")
    rth = df[(df["tod"] > "09:30") & (df["tod"] <= RTH_LAST)].copy()
    rth = rth.sort_values("time").reset_index(drop=True)
    n_days = rth["date"].nunique()
    first_stamps = rth.groupby("date")["tod"].min()
    assert (first_stamps == RTH_FIRST).all(), "some RTH session lacks the 09:33 bar"
    print(f"[load] RTH bars={len(rth)}, RTH sessions={n_days} "
          f"(every session's first RTH bar END-stamped {RTH_FIRST}; its open = 09:30 open)")
    return rth


# ----------------------------------------------------------------- band construction
def build_bands(rth: pd.DataFrame, window: int) -> pd.DataFrame:
    """Attach open0930, dev=|close-open0930|, m_tod (trailing <window>-day per-slot
    mean of dev, prior days only), and RTH-anchored VWAP. Returns bar-level frame."""
    b = rth.copy()
    o = b[b["tod"] == RTH_FIRST].set_index("date")["open"]
    b["open0930"] = b["date"].map(o)
    b["dev"] = (b["close"] - b["open0930"]).abs()

    piv = b.pivot(index="date", columns="tod", values="dev").sort_index()
    band = pd.DataFrame(index=piv.index, columns=piv.columns, dtype=float)
    for col in piv.columns:
        s = piv[col].dropna()  # this slot's available prior observations, date order
        band.loc[s.index, col] = (
            s.rolling(window, min_periods=window).mean().shift(1).to_numpy()
        )
    m = band.stack().rename("m_tod").reset_index()
    b = b.merge(m, on=["date", "tod"], how="left")

    # RTH-anchored VWAP from close x volume (cumulative, includes current bar)
    b = b.sort_values("time").reset_index(drop=True)
    g = b.groupby("date", sort=False)
    cum_cv = g.apply(lambda d: (d["close"] * d["volume"]).cumsum(),
                     include_groups=False).reset_index(drop=True)
    cum_v = g["volume"].cumsum()
    assert (cum_v > 0).all(), "zero cumulative volume in RTH"
    b["vwap"] = cum_cv.to_numpy() / cum_v.to_numpy()
    return b


def assert_no_same_day_leakage(rth: pd.DataFrame, bars: pd.DataFrame, window: int,
                               rng: np.random.Generator) -> None:
    """(a) manual recomputation on random (date, slot) samples; (b) per-slot NaN head;
    (c) perturbation test: scaling one day's closes leaves that day's m_tod unchanged."""
    piv = rth.assign(dev=(rth["close"] - rth["date"].map(
        rth[rth["tod"] == RTH_FIRST].set_index("date")["open"])).abs()) \
        .pivot(index="date", columns="tod", values="dev").sort_index()

    valid = bars.dropna(subset=["m_tod"])
    take = valid.sample(n=min(300, len(valid)), random_state=int(rng.integers(2**31)))
    for _, r in take.iterrows():
        s = piv[r["tod"]].dropna()
        pos = s.index.get_loc(r["date"])
        manual = s.iloc[pos - window:pos].mean()
        assert np.isclose(manual, r["m_tod"], rtol=0, atol=1e-9), \
            f"band mismatch at {r['date']} {r['tod']}"

    for col in piv.columns:  # first <window> observations of every slot must be NaN band
        s = piv[col].dropna()
        head = bars.set_index(["date", "tod"]).loc[
            [(d, col) for d in s.index[:window]], "m_tod"]
        assert head.isna().all(), f"band present inside the first {window} obs of slot {col}"

    # perturbation: blow up one mid-sample day's closes; its own m_tod must not move
    dates = sorted(rth["date"].unique())
    d_perturb = dates[len(dates) // 2]
    pert = rth.copy()
    mask = pert["date"] == d_perturb
    pert.loc[mask, "close"] = pert.loc[mask, "close"] * 1.5
    bars_p = build_bands(pert, window)
    a = bars.loc[bars["date"] == d_perturb, ["tod", "m_tod"]].set_index("tod")["m_tod"]
    p = bars_p.loc[bars_p["date"] == d_perturb, ["tod", "m_tod"]].set_index("tod")["m_tod"]
    assert np.allclose(a.fillna(-1), p.fillna(-1), atol=1e-9), \
        "same-day leakage: perturbing a day's closes changed that day's own band"
    print(f"[leakage] PASSED: {len(take)} random (date,slot) manual recomputations, "
          f"per-slot first-{window}-obs NaN check, and same-day perturbation test "
          f"(day {pd.Timestamp(d_perturb).date()})")


# ------------------------------------------------------------------- trade generation
def run_rule(bars: pd.DataFrame, window: int) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """State machine per session. Returns (trades, daily, diag)."""
    all_days = sorted(bars["date"].unique())
    excluded = all_days[:window]               # no band history -> excluded per spec
    included = all_days[window:]
    diag = {"n_sessions_total": len(all_days),
            "n_sessions_excluded_no_band_history": len(excluded),
            "excluded_range": f"{pd.Timestamp(excluded[0]).date()}.."
                              f"{pd.Timestamp(excluded[-1]).date()}",
            "n_sessions_included": len(included),
            "included_range": f"{pd.Timestamp(included[0]).date()}.."
                              f"{pd.Timestamp(included[-1]).date()}"}

    nan_band_decision_bars = 0
    early_closeout_days = 0
    trades = []
    day_rows = []
    bars_i = bars[bars["date"].isin(included)]
    for date, day in bars_i.groupby("date", sort=True):
        day = day.sort_values("time")
        elig = day[day["tod"] <= CLOSEOUT_TOD]
        if elig.empty:
            day_rows.append({"sess": date, "n_trades": 0, "gross_ticks": 0.0})
            continue
        closeout_idx = elig.index[-1]
        if elig.iloc[-1]["tod"] != CLOSEOUT_TOD:
            early_closeout_days += 1
        pos, entry_px, entry_t = 0, np.nan, None
        day_trades = []
        for idx, r in day.iterrows():
            if idx == closeout_idx:
                if pos != 0:
                    day_trades.append({"sess": date, "side": pos, "entry_time": entry_t,
                                       "exit_time": r["time"], "entry_px": entry_px,
                                       "exit_px": r["close"], "exit_reason": "closeout"})
                    pos = 0
                break  # nothing after the close-out bar is used
            if r["tod"] > DECISION_LAST:
                continue
            if np.isnan(r["m_tod"]):
                nan_band_decision_bars += 1
                continue
            upper = r["open0930"] + r["m_tod"]
            lower = r["open0930"] - r["m_tod"]
            sig = 0
            if r["close"] > max(upper, r["vwap"]):
                sig = 1
            elif r["close"] < min(lower, r["vwap"]):
                sig = -1
            if sig != 0 and sig != pos:
                if pos != 0:  # opposite signal -> flip: close old, open new, same close
                    day_trades.append({"sess": date, "side": pos, "entry_time": entry_t,
                                       "exit_time": r["time"], "entry_px": entry_px,
                                       "exit_px": r["close"], "exit_reason": "flip"})
                pos, entry_px, entry_t = sig, r["close"], r["time"]
        assert pos == 0, f"position open after close-out on {date}"
        gross = sum(t["side"] * (t["exit_px"] - t["entry_px"]) * TICKS_PER_PT
                    for t in day_trades)
        day_rows.append({"sess": date, "n_trades": len(day_trades),
                         "gross_ticks": gross})
        trades.extend(day_trades)

    tr = pd.DataFrame(trades)
    if not tr.empty:
        tr["pts"] = tr["side"] * (tr["exit_px"] - tr["entry_px"])
        tr["gross_ticks"] = tr["pts"] * TICKS_PER_PT
        tr["net_c1_ticks"] = tr["gross_ticks"] - C1_TICKS
        tr["net_c2_ticks"] = tr["gross_ticks"] - C2_TICKS
    daily = pd.DataFrame(day_rows).sort_values("sess").reset_index(drop=True)
    daily["net_c1_ticks"] = daily["gross_ticks"] - C1_TICKS * daily["n_trades"]
    daily["net_c2_ticks"] = daily["gross_ticks"] - C2_TICKS * daily["n_trades"]
    daily["net_c1_usd"] = daily["net_c1_ticks"] * TICK_USD
    daily["net_c2_usd"] = daily["net_c2_ticks"] * TICK_USD
    diag["nan_band_decision_bars_after_exclusion"] = nan_band_decision_bars
    diag["early_closeout_days"] = early_closeout_days
    # consistency: daily sums equal trade sums
    if not tr.empty:
        assert np.isclose(daily["gross_ticks"].sum(), tr["gross_ticks"].sum(), atol=1e-6)
        assert int(daily["n_trades"].sum()) == len(tr)
    return tr, daily, diag


# ------------------------------------------------------------------------- statistics
def boot_ci_mean(values: np.ndarray, rng: np.random.Generator,
                 n_boot: int = N_BOOT) -> tuple[float, float]:
    """Percentile bootstrap 95% CI of the mean, resampling day-level values."""
    n = len(values)
    idx = rng.integers(0, n, size=(n_boot, n))
    means = values[idx].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi)


def boot_ci_per_trade(daily_key: np.ndarray, trade_day: np.ndarray,
                      trade_net: np.ndarray, rng: np.random.Generator,
                      n_boot: int = N_BOOT) -> tuple[float, float]:
    """Day-clustered bootstrap 95% CI of mean net/trade (resample days, pool trades)."""
    day_to_trades: dict = {}
    for d, v in zip(trade_day, trade_net):
        day_to_trades.setdefault(d, []).append(v)
    day_arrays = [np.asarray(day_to_trades.get(d, []), dtype=float) for d in daily_key]
    n = len(day_arrays)
    out = np.empty(n_boot)
    for i in range(n_boot):
        sel = rng.integers(0, n, size=n)
        pooled = np.concatenate([day_arrays[j] for j in sel]) if n else np.array([])
        out[i] = pooled.mean() if pooled.size else np.nan
    lo, hi = np.nanpercentile(out, [2.5, 97.5])
    return float(lo), float(hi)


def profit_factor(x: pd.Series) -> float:
    gp = x[x > 0].sum()
    gl = -x[x < 0].sum()
    return float(gp / gl) if gl > 0 else float("inf")


def max_drawdown(daily_usd: pd.Series) -> float:
    cum = daily_usd.cumsum()
    return float((cum.cummax() - cum).max())


def variant_stats(label: str, tr: pd.DataFrame, daily: pd.DataFrame, diag: dict,
                  ledger: pd.DataFrame) -> dict:
    rng = np.random.default_rng(SEED)  # fresh per variant -> order-independent
    n_days = len(daily)
    n_trades = len(tr)
    s: dict = {"label": label, **diag,
               "n_trades": n_trades,
               "trades_per_day": n_trades / n_days,
               "zero_trade_days": int((daily["n_trades"] == 0).sum())}

    for tag, cost_col, dcol in [("c1", "net_c1_ticks", "net_c1_usd"),
                                ("c2", "net_c2_ticks", "net_c2_usd")]:
        tt = tr[cost_col]
        dd_ = daily[dcol]
        ci_day = boot_ci_mean(dd_.to_numpy(float), np.random.default_rng(SEED))
        ci_trd = boot_ci_per_trade(daily["sess"].to_numpy(),
                                   tr["sess"].to_numpy(), tt.to_numpy(float),
                                   np.random.default_rng(SEED))
        s[tag] = {
            "total_net_ticks": float(tr[cost_col].sum()),
            "total_net_usd": float(dd_.sum()),
            "net_per_trade_ticks": float(tt.mean()),
            "net_per_trade_ci95_ticks_dayclustered": [ci_trd[0] / 1.0, ci_trd[1] / 1.0],
            "pf_trade_level": profit_factor(tt),
            "pf_daily_level": profit_factor(dd_),
            "win_rate_trades": float((tt > 0).mean()),
            "mean_daily_usd": float(dd_.mean()),
            "mean_daily_ticks": float(dd_.mean() / TICK_USD),
            "daily_ci95_usd_bootstrap": list(ci_day),
            "std_daily_usd": float(dd_.std()),
            "ann_sharpe_daily": float(dd_.mean() / dd_.std() * np.sqrt(252))
            if dd_.std() > 0 else float("nan"),
            "max_dd_usd": max_drawdown(dd_),
            "max_dd_ticks": max_drawdown(dd_) / TICK_USD,
        }
        top5 = dd_.nlargest(5).sum()
        total = dd_.sum()
        s[tag]["top5_day_sum_usd"] = float(top5)
        s[tag]["top5_day_share_pct"] = float(top5 / total * 100) if total > 0 else float("nan")
        s[tag]["net_excl_top5_days_usd"] = float(total - top5)

    # yearly split (C1)
    y = daily.assign(year=pd.to_datetime(daily["sess"]).dt.year)
    ty = tr.assign(year=pd.to_datetime(tr["sess"]).dt.year) if n_trades else None
    yearly = {}
    for yr, grp in y.groupby("year"):
        tg = ty[ty["year"] == yr]["net_c1_ticks"] if ty is not None else pd.Series(dtype=float)
        yearly[int(yr)] = {
            "sessions": int(len(grp)),
            "trades": int(grp["n_trades"].sum()),
            "trades_per_day": float(grp["n_trades"].mean()),
            "net_c1_ticks": float(grp["net_c1_ticks"].sum()),
            "net_c1_usd": float(grp["net_c1_usd"].sum()),
            "net_per_trade_ticks": float(tg.mean()) if len(tg) else float("nan"),
            "pf_trade_level": profit_factor(tg) if len(tg) else float("nan"),
            "win_rate": float((tg > 0).mean()) if len(tg) else float("nan"),
        }
    s["yearly_c1"] = yearly

    # exits / sides (structure)
    if n_trades:
        s["exit_reason_counts"] = tr["exit_reason"].value_counts().to_dict()
        s["side_counts"] = {"long": int((tr["side"] == 1).sum()),
                            "short": int((tr["side"] == -1).sum())}
        s["net_c1_by_side_ticks"] = {
            "long": float(tr.loc[tr["side"] == 1, "net_c1_ticks"].sum()),
            "short": float(tr.loc[tr["side"] == -1, "net_c1_ticks"].sum())}

    # correlations vs Solar net_v1 (C1 daily $; Pearson; zero-trade days included)
    j = daily.merge(ledger, on="sess", how="inner").sort_values("sess")
    x, v1 = j["net_c1_usd"], j["net_v1"]
    rho_full = float(np.corrcoef(x, v1)[0, 1])
    losing = j[j["net_v1"] < 0]
    rho_losing = float(np.corrcoef(losing["net_c1_usd"], losing["net_v1"])[0, 1])
    s["corr_vs_solar_net_v1"] = {
        "n_overlap_days": int(len(j)),
        "overlap_range": f"{j['sess'].min().date()}..{j['sess'].max().date()}",
        "rho_full": rho_full,
        "n_solar_losing_days": int(len(losing)),
        "rho_losing_day": rho_losing,
    }
    s["_joined"] = j  # for artifact write (stripped before json)
    return s


def evaluate_gate(s: dict) -> dict:
    c1 = s["c1"]
    corr = s["corr_vs_solar_net_v1"]
    crit = {
        "daily_net_c1_pos_with_ci_lo_pos": {
            "value": f"mean={c1['mean_daily_usd']:+.2f} USD/day, "
                     f"CI95=[{c1['daily_ci95_usd_bootstrap'][0]:+.2f}, "
                     f"{c1['daily_ci95_usd_bootstrap'][1]:+.2f}]",
            "pass": bool(c1["mean_daily_usd"] > 0 and c1["daily_ci95_usd_bootstrap"][0] > 0)},
        "pf_ge_1p10": {"value": f"PF(trade)={c1['pf_trade_level']:.4f}",
                       "pass": bool(c1["pf_trade_level"] >= 1.10)},
        "rho_full_lt_0p3": {"value": f"rho_full={corr['rho_full']:+.4f}",
                            "pass": bool(corr["rho_full"] < 0.3)},
        "rho_losing_le_0p1": {"value": f"rho_losing={corr['rho_losing_day']:+.4f}",
                              "pass": bool(corr["rho_losing_day"] <= 0.1)},
        "top5_concentration_lt_40pct": {
            "value": f"top5_share={c1['top5_day_share_pct']:.2f}%"
            if np.isfinite(c1["top5_day_share_pct"]) else "total net <= 0 (undefined)",
            "pass": bool(np.isfinite(c1["top5_day_share_pct"])
                         and c1["top5_day_share_pct"] < 40.0)},
    }
    verdict = "PROMOTE_CANDIDATE_FREEZE" if all(v["pass"] for v in crit.values()) \
        else "NOT_PROMOTED"
    return {"criteria": crit, "verdict": verdict}


def print_variant(s: dict) -> None:
    c1, c2, corr = s["c1"], s["c2"], s["corr_vs_solar_net_v1"]
    print(f"\n===== {s['label']} =====")
    print(f"sessions total={s['n_sessions_total']}, excluded (no band history)="
          f"{s['n_sessions_excluded_no_band_history']} [{s['excluded_range']}], "
          f"included={s['n_sessions_included']} [{s['included_range']}]")
    print(f"early-closeout sessions (last bar < {CLOSEOUT_TOD})={s['early_closeout_days']}, "
          f"NaN-band decision bars after exclusion={s['nan_band_decision_bars_after_exclusion']}")
    print(f"trades={s['n_trades']}, trades/day={s['trades_per_day']:.3f}, "
          f"zero-trade days={s['zero_trade_days']}")
    if "exit_reason_counts" in s:
        print(f"exits: {s['exit_reason_counts']}   sides: {s['side_counts']}   "
              f"net C1 by side (t): {{long: {s['net_c1_by_side_ticks']['long']:+.1f}, "
              f"short: {s['net_c1_by_side_ticks']['short']:+.1f}}}")
    for tag, cc in [("C1", c1), ("C2 stress", c2)]:
        print(f"[{tag}] net/trade={cc['net_per_trade_ticks']:+.3f}t "
              f"(day-clustered CI [{cc['net_per_trade_ci95_ticks_dayclustered'][0]:+.3f}, "
              f"{cc['net_per_trade_ci95_ticks_dayclustered'][1]:+.3f}]), "
              f"PF(trade)={cc['pf_trade_level']:.4f}, PF(daily)={cc['pf_daily_level']:.4f}, "
              f"win={cc['win_rate_trades']:.4f}")
        print(f"[{tag}] total={cc['total_net_ticks']:+.1f}t (${cc['total_net_usd']:+,.0f}), "
              f"mean/day=${cc['mean_daily_usd']:+.2f} "
              f"(CI95 [{cc['daily_ci95_usd_bootstrap'][0]:+.2f}, "
              f"{cc['daily_ci95_usd_bootstrap'][1]:+.2f}]), "
              f"annSharpe={cc['ann_sharpe_daily']:.3f}, maxDD=${cc['max_dd_usd']:,.0f}, "
              f"top5 share={cc['top5_day_share_pct']:.2f}%"
              if np.isfinite(cc['top5_day_share_pct']) else
              f"[{tag}] total={cc['total_net_ticks']:+.1f}t, top5 share undefined (net<=0)")
    print("yearly (C1):")
    ydf = pd.DataFrame(s["yearly_c1"]).T
    print(ydf.to_string(float_format=lambda v: f"{v:,.3f}"))
    print(f"corr vs Solar net_v1: rho_full={corr['rho_full']:+.6f} "
          f"(N={corr['n_overlap_days']}), rho_losing={corr['rho_losing_day']:+.6f} "
          f"(N={corr['n_solar_losing_days']} Solar-losing days)")


# ------------------------------------------------------------------------------ main
def main() -> dict:
    ART.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    rth = load_bars()
    ledger = pd.read_csv(LEDGER_CSV, parse_dates=["sess"])
    n_led = len(ledger)
    ledger = ledger[ledger["sess"] <= DEV_END].copy()
    print(f"[ledger] {LEDGER_CSV.name}: rows={n_led}, kept <= {DEV_END.date()}: "
          f"{len(ledger)}; column net_v1 (v1 frozen research champion)")

    results = {}
    for window in [WINDOW_FROZEN] + NEIGHBOR_WINDOWS:
        label = (f"w{window}_FROZEN" if window == WINDOW_FROZEN
                 else f"w{window}_neighbor_REPORTED_NEVER_SELECTED")
        bars = build_bands(rth, window)
        if window == WINDOW_FROZEN:
            assert_no_same_day_leakage(rth, bars, window, rng)
        tr, daily, diag = run_rule(bars, window)
        s = variant_stats(label, tr, daily, diag, ledger)
        print_variant(s)
        j = s.pop("_joined")
        stem = f"w8bmom_w{window}"
        tr.to_csv(ART / f"{stem}_trades.csv", index=False)
        daily.to_csv(ART / f"{stem}_daily.csv", index=False)
        if window == WINDOW_FROZEN:
            j[["sess", "n_trades", "net_c1_ticks", "net_c1_usd", "net_c2_usd",
               "net_v1", "net_v2"]].to_csv(ART / f"{stem}_joined_daily.csv", index=False)
        results[label] = s

    gate = evaluate_gate(results[f"w{WINDOW_FROZEN}_FROZEN"])
    print("\n===== FROZEN PROMOTION GATE (14-day frozen rule, C1) =====")
    for name, c in gate["criteria"].items():
        print(f"  {'PASS' if c['pass'] else 'FAIL'}  {name}: {c['value']}")
    print(f"GATE VERDICT: {gate['verdict']}")

    stats = {"spec": "W8_programs_final.md §W8-1 (frozen, cf7041f)",
             "seed": SEED, "n_boot": N_BOOT,
             "dev_window_end": str(DEV_END.date()),
             "costs_ticks_rt": {"C1": C1_TICKS, "C2": C2_TICKS},
             "fill_convention": "signal-bar close fills; entries/flips on END stamps "
                                "09:33..15:54; force-flat at close of last bar <= 15:57",
             "band_convention": "per-slot trailing mean over that slot's prior "
                                "observations (prior days only, asserted)",
             "variants": results, "frozen_gate": gate}
    with open(ART / "w8bmom_stats.json", "w") as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"\n[artifacts] written to {ART}")
    return stats


if __name__ == "__main__":
    buf = io.StringIO()

    class Tee(io.TextIOBase):
        def write(self, sxt):
            buf.write(sxt)
            sys.__stdout__.write(sxt)
            return len(sxt)

    with redirect_stdout(Tee()):
        main()
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "w8bmom_stdout.txt").write_text(buf.getvalue())
