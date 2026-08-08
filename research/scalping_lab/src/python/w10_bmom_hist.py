"""W10 — B-MOM frozen rule on unseen 2006-2021 (spec W10_bmom_history.md, frozen e4e73a8).

The W8-1 rule is FROZEN — ZERO changes. This script imports w8_bmom and reuses its
rule implementation verbatim (build_bands, run_rule, assert_no_same_day_leakage,
boot_ci_mean, boot_ci_per_trade, profit_factor, max_drawdown). ONLY the data window
changes.

Data: substrate/minute/NQ/nq1m_2005_202605.parquet (1-min END-stamped ET bars,
back-adjusted NQ, 2006-01-05..2026-05-29). 3-min bars are built by aggregation to
match W8-1's bar basis exactly: END-stamp = last minute of each 3-min slot (a 3-min
bar END-stamped T aggregates the 1-min END stamps T-2m, T-1m, T), RTH slots aligned
09:33, 09:36, ..., 16:00.

Two runs:
  A. RECONCILIATION CONTROL (2022-01-01 .. DEV_END 2026-05-31): same window as the
     committed W8-1 artifacts. Validates the aggregation by reconciling trades/net
     vs artifacts/w8_bmom/w8bmom_stats.json and w8bmom_w14_trades.csv. If materially
     different -> STOP (exit 2). NEVER pooled into the readout.
  B. READOUT (CONFIRMATION WINDOW 2006-01 .. 2021-12-31 ONLY): frozen readout.
     No minute row stamped >= 2022-01-01 enters any readout statistic — the readout
     frame is filtered strictly < 2022-01-01 before aggregation.

Early-close / missing-slot handling (as in w8_bmom, documented):
  - Early-close sessions force-flat at the last RTH bar END-stamped <= 15:57
    (run_rule's close-out logic, unchanged).
  - Missing slots: the per-slot band rolls over that slot's PRIOR OBSERVATIONS only
    (half-days simply lack afternoon slots); decision bars with NaN band are skipped
    and counted.
  - W10-only data-quality precondition (w8 asserted this held on its CSV): sessions
    whose FIRST RTH 3-min stamp is not 09:33 cannot anchor the 09:30 open under the
    frozen rule; they are DROPPED entirely (band construction + trading) and listed.
  - Sessions where the 09:33 bucket exists but the 09:31 minute is missing keep the
    bucket's first available minute open as open0930 (first traded price after
    09:30); listed.

Roll-gap audit: overnight gap = open0930(d) - prior RTH session close. Days with
|z| >= 8 sigma (full-window z or trailing-120-session z, gap stats from prior days
only) are FLAGGED and reported; the frozen readout keeps them (sensitivity CI
excluding them is reported separately, non-frozen).

Frozen interpretation (evaluated at C1, daily-net day-clustered bootstrap CI,
seed 20260808, 1000 reps; precedence documented in the report):
  STRUCTURAL      iff full pre-2022 daily net C1 CI_lo > 0
  CONTRADICTED    iff full pre-2022 daily net C1 CI_hi < 0
  REVIVED-REGIME  iff 2018-21 era CI_lo > 0 while 2006-09, 2010-13, 2014-17 all fail
  REGIME-LOCAL    iff no era passes CI_lo > 0
  (any other pattern -> MIXED, outside the frozen taxonomy, reported as such)

No promotion from this wave. No parameter changes. Neighbors NOT run.
Outputs -> research/scalping_lab/artifacts/w10_bmom_hist/
"""

from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w8_bmom as w8  # noqa: E402  — frozen W8-1 rule logic, reused verbatim

ROOT = HERE.parents[3]  # .../systematic_research
PARQ = ROOT / "research" / "scalping_lab" / "substrate" / "minute" / "NQ" / \
    "nq1m_2005_202605.parquet"
W8ART = ROOT / "research" / "scalping_lab" / "artifacts" / "w8_bmom"
ART = ROOT / "research" / "scalping_lab" / "artifacts" / "w10_bmom_hist"

READOUT_BOUNDARY = pd.Timestamp("2022-01-01")   # readout uses rows STRICTLY BEFORE
SEED = 20260808
N_BOOT = 1000
WINDOW = w8.WINDOW_FROZEN                        # 14, frozen
ERAS = [("2006-09", 2006, 2009), ("2010-13", 2010, 2013),
        ("2014-17", 2014, 2017), ("2018-21", 2018, 2021)]
ROLL_SESSIONS = 504                              # 2 years of ~252 sessions

# Materiality thresholds for the reconciliation control (pre-declared)
RECON_MAX_TRADECOUNT_RELDIFF = 0.005   # 0.5 %
RECON_MAX_NET_RELDIFF = 0.01           # 1 % of committed C1 total net ticks

assert SEED == w8.SEED and N_BOOT == w8.N_BOOT, "seed/reps must match frozen W8-1"
assert WINDOW == 14, "frozen band window is 14 days"


# ------------------------------------------------------------------ 3-min aggregation
def to_3min(min_df: pd.DataFrame) -> pd.DataFrame:
    """1-min END-stamped bars -> 3-min END-stamped bars on the 09:33/09:36/... grid.
    A 1-min END stamp t belongs to the 3-min bucket ending ceil(t / 3min)."""
    d = min_df.sort_values("time").copy()
    assert (d["time"].dt.second == 0).all(), "non-zero seconds in minute stamps"
    mins = d["time"].dt.hour * 60 + d["time"].dt.minute
    bucket = (np.ceil(mins / 3) * 3).astype(int)
    d["bt"] = d["time"].dt.normalize() + pd.to_timedelta(bucket, "m")
    g = d.groupby("bt")
    out = pd.DataFrame({
        "open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
        "close": g["close"].last(), "volume": g["volume"].sum(),
        "n_minutes": g["close"].size(),
    }).reset_index().rename(columns={"bt": "time"})
    return out.sort_values("time").reset_index(drop=True)


def rth_frame(bars3: pd.DataFrame, label: str, strict: bool) -> pd.DataFrame:
    """Replicates w8.load_bars' RTH filter on an in-memory 3-min frame.
    strict=True: assert every session's first RTH stamp is 09:33 (w8 behavior).
    strict=False: DROP sessions whose first RTH stamp != 09:33 (documented)."""
    df = bars3.copy()
    df["date"] = df["time"].dt.normalize()
    df["tod"] = df["time"].dt.strftime("%H:%M")
    rth = df[(df["tod"] > "09:30") & (df["tod"] <= w8.RTH_LAST)].copy()
    rth = rth.sort_values("time").reset_index(drop=True)
    first_stamps = rth.groupby("date")["tod"].min()
    bad = first_stamps[first_stamps != w8.RTH_FIRST]
    if strict:
        assert bad.empty, f"[{label}] sessions lacking the 09:33 bar: {list(bad.index)}"
    elif len(bad):
        print(f"[{label}] DROPPED {len(bad)} sessions whose first RTH stamp != "
              f"{w8.RTH_FIRST} (cannot anchor the 09:30 open under the frozen rule):")
        for dte, tod in bad.items():
            print(f"    {pd.Timestamp(dte).date()} (first stamp {tod})")
        rth = rth[~rth["date"].isin(bad.index)].reset_index(drop=True)
    # sessions where the 09:33 bucket is missing its 09:31 minute (open0930 is then
    # the first traded price after 09:30, not the literal 09:30-09:31 open)
    b933 = rth[rth["tod"] == w8.RTH_FIRST]
    approx = b933[b933["n_minutes"] < 3]
    if len(approx):
        print(f"[{label}] {len(approx)} sessions have a thin 09:33 bucket "
              f"(<3 minutes; open0930 = first traded minute of the bucket): "
              f"{[str(pd.Timestamp(d).date()) for d in approx['date']]}")
    n_early = int((rth.groupby("date")["tod"].max() < w8.RTH_LAST).sum())
    print(f"[{label}] RTH bars={len(rth)}, sessions={rth['date'].nunique()}, "
          f"range {rth['date'].min().date()}..{rth['date'].max().date()}, "
          f"sessions with last stamp < {w8.RTH_LAST} (early close)={n_early}")
    return rth


# ------------------------------------------------------------------------- statistics
def scope_stats(label: str, tr: pd.DataFrame, daily: pd.DataFrame) -> dict:
    """Frozen readout stats for one scope (full window or one era). Reuses w8's
    bootstrap primitives; fresh rng(SEED) per CI exactly as w8.variant_stats does."""
    n_days = len(daily)
    n_trades = len(tr)
    s: dict = {"label": label, "n_sessions": n_days, "n_trades": n_trades,
               "trades_per_day": n_trades / n_days if n_days else float("nan"),
               "zero_trade_days": int((daily["n_trades"] == 0).sum())}
    for tag, cost_col, dcol in [("c1", "net_c1_ticks", "net_c1_usd"),
                                ("c2", "net_c2_ticks", "net_c2_usd")]:
        tt = tr[cost_col] if n_trades else pd.Series(dtype=float)
        dd_ = daily[dcol]
        ci_day = w8.boot_ci_mean(dd_.to_numpy(float), np.random.default_rng(SEED))
        ci_trd = w8.boot_ci_per_trade(daily["sess"].to_numpy(),
                                      tr["sess"].to_numpy() if n_trades else np.array([]),
                                      tt.to_numpy(float),
                                      np.random.default_rng(SEED))
        top5 = dd_.nlargest(5).sum()
        total = dd_.sum()
        s[tag] = {
            "total_net_ticks": float(tt.sum()),
            "total_net_usd": float(dd_.sum()),
            "net_per_trade_ticks": float(tt.mean()) if n_trades else float("nan"),
            "net_per_trade_ci95_ticks_dayclustered": [ci_trd[0], ci_trd[1]],
            "pf_trade_level": w8.profit_factor(tt) if n_trades else float("nan"),
            "pf_daily_level": w8.profit_factor(dd_),
            "win_rate_trades": float((tt > 0).mean()) if n_trades else float("nan"),
            "mean_daily_usd": float(dd_.mean()),
            "mean_daily_ticks": float(dd_.mean() / w8.TICK_USD),
            "daily_ci95_usd_bootstrap": list(ci_day),
            "std_daily_usd": float(dd_.std()),
            "ann_sharpe_daily": float(dd_.mean() / dd_.std() * np.sqrt(252))
            if dd_.std() > 0 else float("nan"),
            "max_dd_usd": w8.max_drawdown(dd_),
            "top5_day_share_pct": float(top5 / total * 100) if total > 0 else float("nan"),
            "ci_lo_pos": bool(ci_day[0] > 0),
            "ci_hi_neg": bool(ci_day[1] < 0),
        }
    return s


def yearly_table(tr: pd.DataFrame, daily: pd.DataFrame) -> dict:
    """Same shape as w8.variant_stats' yearly_c1 block."""
    y = daily.assign(year=pd.to_datetime(daily["sess"]).dt.year)
    ty = tr.assign(year=pd.to_datetime(tr["sess"]).dt.year) if len(tr) else None
    out = {}
    for yr, grp in y.groupby("year"):
        tg = ty[ty["year"] == yr]["net_c1_ticks"] if ty is not None \
            else pd.Series(dtype=float)
        out[int(yr)] = {
            "sessions": int(len(grp)),
            "trades": int(grp["n_trades"].sum()),
            "trades_per_day": float(grp["n_trades"].mean()),
            "net_c1_ticks": float(grp["net_c1_ticks"].sum()),
            "net_c1_usd": float(grp["net_c1_usd"].sum()),
            "net_per_trade_ticks": float(tg.mean()) if len(tg) else float("nan"),
            "pf_trade_level": w8.profit_factor(tg) if len(tg) else float("nan"),
            "win_rate": float((tg > 0).mean()) if len(tg) else float("nan"),
        }
    return out


def rollgap_flags(rth: pd.DataFrame, daily: pd.DataFrame) -> pd.DataFrame:
    """Overnight gap = open0930(d) - prior RTH session close. Flag |z| >= 8 on either
    the full-window z or a trailing-120-session z (both from PRIOR days only for the
    trailing variant; full-window z is descriptive)."""
    by = rth.sort_values("time").groupby("date")
    o = by.apply(lambda d: d.iloc[0]["open"], include_groups=False)  # 09:33 bucket open
    c = by.apply(lambda d: d.iloc[-1]["close"], include_groups=False)
    gap = (o - c.shift(1)).dropna()
    z_full = (gap - gap.mean()) / gap.std()
    mu = gap.rolling(120, min_periods=40).mean().shift(1)
    sd = gap.rolling(120, min_periods=40).std().shift(1)
    z_roll = (gap - mu) / sd
    f = pd.DataFrame({"gap_pts": gap, "z_full": z_full, "z_roll": z_roll})
    f["flag_8sigma"] = (f["z_full"].abs() >= 8) | (f["z_roll"].abs() >= 8)
    f = f.reset_index().rename(columns={"date": "sess"})
    dnet = daily.set_index("sess")["net_c1_usd"]
    f["net_c1_usd"] = f["sess"].map(dnet)  # NaN if session not in included set
    return f


# ------------------------------------------------------------------------------ main
def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    print(f"W10 B-MOM history run — spec W10_bmom_history.md (frozen e4e73a8); "
          f"rule = w8_bmom (frozen, reused verbatim); window={WINDOW}, seed={SEED}, "
          f"n_boot={N_BOOT}, C1={w8.C1_TICKS}t, C2={w8.C2_TICKS}t")
    mn = pd.read_parquet(PARQ)
    mn["time"] = pd.to_datetime(mn["time"])
    print(f"[minute] {PARQ.name}: rows={len(mn)}, "
          f"range {mn['time'].min()} .. {mn['time'].max()} (END-stamped ET; verified: "
          f"session's first stamp is 18:01, no 18:00 stamps, RTH-open volume on 09:31)")

    pre_min = mn[mn["time"] < READOUT_BOUNDARY]
    post_min = mn[(mn["time"] >= READOUT_BOUNDARY) & (mn["time"] <= w8.DEV_END)]
    print(f"[split] readout minute rows (< {READOUT_BOUNDARY.date()}): {len(pre_min)}; "
          f"reconciliation minute rows ({READOUT_BOUNDARY.date()} .. "
          f"{w8.DEV_END.date()}): {len(post_min)} — never pooled")

    # ---------------- A. RECONCILIATION CONTROL (2022+; never in the readout) -------
    print("\n===== A. RECONCILIATION CONTROL: 2022-01 .. 2026-05 vs committed W8-1 =====")
    rth_post = rth_frame(to_3min(post_min), "recon", strict=True)
    bars_post = w8.build_bands(rth_post, WINDOW)
    tr_r, dl_r, dg_r = w8.run_rule(bars_post, WINDOW)
    ledger = pd.read_csv(w8.LEDGER_CSV, parse_dates=["sess"])
    ledger = ledger[ledger["sess"] <= w8.DEV_END].copy()
    s_r = w8.variant_stats("recon_2022plus_w14", tr_r, dl_r, dg_r, ledger)
    s_r.pop("_joined")

    committed = json.loads((W8ART / "w8bmom_stats.json").read_text())
    cv = committed["variants"]["w14_FROZEN"]
    ctr = pd.read_csv(W8ART / "w8bmom_w14_trades.csv",
                      parse_dates=["entry_time", "exit_time"])

    rows = []
    def cmp_row(name, mine, theirs):
        rows.append({"metric": name, "recon_run": mine, "committed_w8": theirs,
                     "diff": (mine - theirs) if isinstance(mine, (int, float)) else ""})
    cmp_row("sessions_total", s_r["n_sessions_total"], cv["n_sessions_total"])
    cmp_row("sessions_excluded", s_r["n_sessions_excluded_no_band_history"],
            cv["n_sessions_excluded_no_band_history"])
    cmp_row("sessions_included", s_r["n_sessions_included"], cv["n_sessions_included"])
    cmp_row("n_trades", s_r["n_trades"], cv["n_trades"])
    cmp_row("c1_total_net_ticks", s_r["c1"]["total_net_ticks"], cv["c1"]["total_net_ticks"])
    cmp_row("c1_total_net_usd", s_r["c1"]["total_net_usd"], cv["c1"]["total_net_usd"])
    cmp_row("c1_net_per_trade_ticks", s_r["c1"]["net_per_trade_ticks"],
            cv["c1"]["net_per_trade_ticks"])
    cmp_row("c1_pf_trade", s_r["c1"]["pf_trade_level"], cv["c1"]["pf_trade_level"])
    cmp_row("c1_mean_daily_usd", s_r["c1"]["mean_daily_usd"], cv["c1"]["mean_daily_usd"])
    cmp_row("c1_daily_ci_lo_usd", s_r["c1"]["daily_ci95_usd_bootstrap"][0],
            cv["c1"]["daily_ci95_usd_bootstrap"][0])
    cmp_row("c1_daily_ci_hi_usd", s_r["c1"]["daily_ci95_usd_bootstrap"][1],
            cv["c1"]["daily_ci95_usd_bootstrap"][1])
    cmp_row("c2_total_net_ticks", s_r["c2"]["total_net_ticks"], cv["c2"]["total_net_ticks"])
    cmp_df = pd.DataFrame(rows)
    print("\n[reconciliation] recon run (substrate 1-min -> 3-min) vs committed w8 artifacts:")
    print(cmp_df.to_string(index=False))

    mm = ctr.merge(tr_r, on=["entry_time", "exit_time", "side"], how="outer",
                   suffixes=("_w8", "_w10"), indicator=True)
    n_match = int((mm["_merge"] == "both").sum())
    n_only_w8 = int((mm["_merge"] == "left_only").sum())
    n_only_w10 = int((mm["_merge"] == "right_only").sum())
    both = mm[mm["_merge"] == "both"]
    px_diff = float(np.nanmax(
        np.abs(both["entry_px_w8"] - both["entry_px_w10"]).to_numpy().tolist()
        + np.abs(both["exit_px_w8"] - both["exit_px_w10"]).to_numpy().tolist())) \
        if len(both) else float("nan")
    print(f"[reconciliation] trade-by-trade: matched={n_match}, "
          f"w8-only={n_only_w8}, w10-only={n_only_w10}, max |px diff| on matched={px_diff}")

    tc_rel = abs(s_r["n_trades"] - cv["n_trades"]) / cv["n_trades"]
    net_rel = abs(s_r["c1"]["total_net_ticks"] - cv["c1"]["total_net_ticks"]) \
        / abs(cv["c1"]["total_net_ticks"])
    material = tc_rel > RECON_MAX_TRADECOUNT_RELDIFF or net_rel > RECON_MAX_NET_RELDIFF
    print(f"[reconciliation] trade-count rel diff={tc_rel:.6f} "
          f"(threshold {RECON_MAX_TRADECOUNT_RELDIFF}), "
          f"C1 net rel diff={net_rel:.6f} (threshold {RECON_MAX_NET_RELDIFF}) -> "
          f"{'MATERIALLY DIFFERENT — STOPPING' if material else 'PASS'}")
    recon_block = {"comparison": rows,
                   "trade_match": {"matched": n_match, "w8_only": n_only_w8,
                                   "w10_only": n_only_w10,
                                   "max_abs_px_diff_matched": px_diff},
                   "trade_count_rel_diff": tc_rel, "c1_net_rel_diff": net_rel,
                   "thresholds": {"trade_count": RECON_MAX_TRADECOUNT_RELDIFF,
                                  "c1_net": RECON_MAX_NET_RELDIFF},
                   "material_difference": bool(material)}
    cmp_df.to_csv(ART / "w10bmom_recon_vs_w8.csv", index=False)
    if material:
        (ART / "w10bmom_stats.json").write_text(json.dumps(
            {"status": "STOPPED_RECONCILIATION_FAILURE", "recon": recon_block},
            indent=2, default=str))
        return 2

    # ---------------- B. READOUT (2006-01 .. 2021-12-31 ONLY) ----------------------
    print("\n===== B. READOUT: frozen rule on 2006-01 .. 2021-12-31 (confirmation) =====")
    rng = np.random.default_rng(SEED)
    rth_pre = rth_frame(to_3min(pre_min), "readout", strict=False)
    assert rth_pre["time"].max() < READOUT_BOUNDARY  # no 2022+ row in the readout
    bars_pre = w8.build_bands(rth_pre, WINDOW)
    w8.assert_no_same_day_leakage(rth_pre, bars_pre, WINDOW, rng)
    tr, daily, diag = w8.run_rule(bars_pre, WINDOW)
    print(f"[readout] sessions total={diag['n_sessions_total']}, excluded (no band "
          f"history)={diag['n_sessions_excluded_no_band_history']} "
          f"[{diag['excluded_range']}], included={diag['n_sessions_included']} "
          f"[{diag['included_range']}]")
    print(f"[readout] early-closeout sessions (last elig bar != {w8.CLOSEOUT_TOD})="
          f"{diag['early_closeout_days']}, NaN-band decision bars after exclusion="
          f"{diag['nan_band_decision_bars_after_exclusion']}")
    if len(tr):
        print(f"[readout] exits: {tr['exit_reason'].value_counts().to_dict()}   "
              f"sides: long={(tr['side'] == 1).sum()}, short={(tr['side'] == -1).sum()}")

    # scope stats: full pre-2022 + four eras
    scopes = {"full_pre2022": scope_stats("full_pre2022", tr, daily)}
    daily_y = pd.to_datetime(daily["sess"]).dt.year
    tr_y = pd.to_datetime(tr["sess"]).dt.year if len(tr) else pd.Series(dtype=int)
    era_rows = []
    for name, y0, y1 in ERAS:
        dsel = daily[(daily_y >= y0) & (daily_y <= y1)].reset_index(drop=True)
        tsel = tr[(tr_y >= y0) & (tr_y <= y1)].reset_index(drop=True) if len(tr) \
            else tr
        scopes[name] = scope_stats(name, tsel, dsel)
    for name in ["full_pre2022"] + [e[0] for e in ERAS]:
        s = scopes[name]
        for tag in ["c1", "c2"]:
            c = s[tag]
            era_rows.append({
                "scope": name, "cost": tag.upper(), "sessions": s["n_sessions"],
                "trades": s["n_trades"], "trades_per_day": s["trades_per_day"],
                "zero_trade_days": s["zero_trade_days"],
                "total_net_ticks": c["total_net_ticks"],
                "total_net_usd": c["total_net_usd"],
                "net_per_trade_ticks": c["net_per_trade_ticks"],
                "npt_ci_lo_ticks": c["net_per_trade_ci95_ticks_dayclustered"][0],
                "npt_ci_hi_ticks": c["net_per_trade_ci95_ticks_dayclustered"][1],
                "pf_trade": c["pf_trade_level"], "pf_daily": c["pf_daily_level"],
                "win_rate": c["win_rate_trades"],
                "mean_daily_usd": c["mean_daily_usd"],
                "daily_ci_lo_usd": c["daily_ci95_usd_bootstrap"][0],
                "daily_ci_hi_usd": c["daily_ci95_usd_bootstrap"][1],
                "std_daily_usd": c["std_daily_usd"],
                "ann_sharpe": c["ann_sharpe_daily"], "max_dd_usd": c["max_dd_usd"],
                "top5_day_share_pct": c["top5_day_share_pct"],
                "ci_lo_pos": c["ci_lo_pos"], "ci_hi_neg": c["ci_hi_neg"],
            })
    era_df = pd.DataFrame(era_rows)
    era_df.to_csv(ART / "w10bmom_era_stats.csv", index=False)
    show = era_df[era_df["cost"] == "C1"][
        ["scope", "sessions", "trades", "trades_per_day", "net_per_trade_ticks",
         "npt_ci_lo_ticks", "npt_ci_hi_ticks", "pf_trade", "mean_daily_usd",
         "daily_ci_lo_usd", "daily_ci_hi_usd", "ann_sharpe", "ci_lo_pos"]]
    print("\n[era readout, C1]")
    print(show.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
    show2 = era_df[era_df["cost"] == "C2"][
        ["scope", "net_per_trade_ticks", "npt_ci_lo_ticks", "npt_ci_hi_ticks",
         "pf_trade", "mean_daily_usd", "daily_ci_lo_usd", "daily_ci_hi_usd"]]
    print("\n[era readout, C2 stress]")
    print(show2.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))

    yearly = yearly_table(tr, daily)
    ydf = pd.DataFrame(yearly).T
    ydf.index.name = "year"
    ydf.to_csv(ART / "w10bmom_yearly.csv")
    print("\n[yearly, C1]")
    print(ydf.to_string(float_format=lambda v: f"{v:,.3f}"))

    # rolling 2-year daily-mean CSV
    dsort = daily.sort_values("sess").reset_index(drop=True)
    roll = pd.DataFrame({
        "sess": dsort["sess"],
        "roll504_mean_daily_net_c1_usd":
            dsort["net_c1_usd"].rolling(ROLL_SESSIONS, min_periods=ROLL_SESSIONS).mean(),
        "roll504_mean_daily_net_c1_ticks":
            dsort["net_c1_ticks"].rolling(ROLL_SESSIONS, min_periods=ROLL_SESSIONS).mean(),
        "roll504_mean_daily_net_c2_usd":
            dsort["net_c2_usd"].rolling(ROLL_SESSIONS, min_periods=ROLL_SESSIONS).mean(),
    })
    roll.to_csv(ART / "w10bmom_rolling2y_daily_mean.csv", index=False)
    rv = roll.dropna()
    print(f"\n[rolling] 2-year ({ROLL_SESSIONS}-session) mean daily net C1: "
          f"first={rv.iloc[0]['roll504_mean_daily_net_c1_usd']:+.2f} USD "
          f"({rv.iloc[0]['sess'].date()}), last={rv.iloc[-1]['roll504_mean_daily_net_c1_usd']:+.2f} USD "
          f"({rv.iloc[-1]['sess'].date()}), min={rv['roll504_mean_daily_net_c1_usd'].min():+.2f}, "
          f"max={rv['roll504_mean_daily_net_c1_usd'].max():+.2f}")

    # roll-gap 8-sigma audit
    gaps = rollgap_flags(rth_pre, daily)
    flagged = gaps[gaps["flag_8sigma"]]
    gaps.to_csv(ART / "w10bmom_rollgap_audit.csv", index=False)
    print(f"\n[roll-gap] sessions with overnight gap |z|>=8 (full-window or "
          f"trailing-120): {len(flagged)}")
    if len(flagged):
        print(flagged.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
        keep = ~daily["sess"].isin(flagged["sess"])
        sens = scope_stats("full_pre2022_excl_8sigma_days",
                           tr[~tr["sess"].isin(flagged["sess"])].reset_index(drop=True)
                           if len(tr) else tr,
                           daily[keep].reset_index(drop=True))
        print(f"[roll-gap] SENSITIVITY (non-frozen) excl flagged days: C1 mean/day="
              f"{sens['c1']['mean_daily_usd']:+.2f} USD, CI95="
              f"[{sens['c1']['daily_ci95_usd_bootstrap'][0]:+.2f}, "
              f"{sens['c1']['daily_ci95_usd_bootstrap'][1]:+.2f}]")
    else:
        sens = None

    # frozen interpretation
    full = scopes["full_pre2022"]["c1"]
    era_pass = {e[0]: scopes[e[0]]["c1"]["ci_lo_pos"] for e in ERAS}
    if full["ci_lo_pos"]:
        verdict = "STRUCTURAL"
    elif full["ci_hi_neg"]:
        verdict = "CONTRADICTED"
    elif era_pass["2018-21"] and not any(era_pass[e] for e in
                                         ["2006-09", "2010-13", "2014-17"]):
        verdict = "REVIVED-REGIME"
    elif not any(era_pass.values()):
        verdict = "REGIME-LOCAL"
    else:
        verdict = "MIXED (outside frozen taxonomy)"
    print(f"\n===== FROZEN INTERPRETATION =====")
    print(f"full pre-2022 daily net C1: mean={full['mean_daily_usd']:+.2f} USD/day, "
          f"CI95=[{full['daily_ci95_usd_bootstrap'][0]:+.2f}, "
          f"{full['daily_ci95_usd_bootstrap'][1]:+.2f}] "
          f"-> CI_lo>0: {full['ci_lo_pos']}, CI_hi<0: {full['ci_hi_neg']}")
    for e, p in era_pass.items():
        c = scopes[e]["c1"]
        print(f"  era {e}: mean={c['mean_daily_usd']:+.2f} USD/day, "
              f"CI95=[{c['daily_ci95_usd_bootstrap'][0]:+.2f}, "
              f"{c['daily_ci95_usd_bootstrap'][1]:+.2f}] -> pass={p}")
    print(f"VERDICT: {verdict}")

    tr.to_csv(ART / "w10bmom_trades.csv", index=False)
    daily.to_csv(ART / "w10bmom_daily.csv", index=False)
    stats = {"spec": "W10_bmom_history.md (frozen e4e73a8); rule = W8-1 frozen "
                     "(w8_bmom.py, reused verbatim)",
             "seed": SEED, "n_boot": N_BOOT, "window": WINDOW,
             "costs_ticks_rt": {"C1": w8.C1_TICKS, "C2": w8.C2_TICKS},
             "bar_basis": "3-min END-stamped bars aggregated from 1-min END-stamped "
                          "substrate minutes (bucket end = ceil(t/3min)); RTH slots "
                          "09:33..16:00",
             "readout_boundary_exclusive": str(READOUT_BOUNDARY.date()),
             "reconciliation_control": recon_block,
             "readout_diag": diag,
             "readout_exits": tr["exit_reason"].value_counts().to_dict() if len(tr) else {},
             "readout_sides": {"long": int((tr["side"] == 1).sum()),
                               "short": int((tr["side"] == -1).sum())} if len(tr) else {},
             "scopes": scopes, "era_pass_c1_daily_ci": era_pass,
             "yearly_c1": yearly,
             "rollgap_flagged_days": flagged.to_dict("records"),
             "rollgap_sensitivity_excl_flagged": sens,
             "verdict": verdict}
    (ART / "w10bmom_stats.json").write_text(json.dumps(stats, indent=2, default=str))
    print(f"\n[artifacts] written to {ART}")
    return 0


if __name__ == "__main__":
    buf = io.StringIO()

    class Tee(io.TextIOBase):
        def write(self, sxt):
            buf.write(sxt)
            sys.__stdout__.write(sxt)
            return len(sxt)

    with redirect_stdout(Tee()):
        rc = main()
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "w10bmom_stdout.txt").write_text(buf.getvalue())
    sys.exit(rc)
