"""W5-B2 — Intraday-momentum correlation pre-gate (Program B; frozen spec W5_programs_wave.md §B2).

NO new alpha claims — correlation structure only. H-A1's kill of the standalone
Gao-style effect stands; this measures whether the family could diversify Solar.

Frozen definitions
------------------
- Data: runs/AUDIT03_BARS/nq_3m_2022_2026.csv (3-min bars, close-stamped, exchange ET).
  CONTAMINATION RULE: dev window ends 2026-05-31; rows with timestamp >= 2026-06-01 are
  dropped at load and never used (sealed holdout).
- Gao-style daily P&L: signal = sign(rest-of-day return 09:30 -> 15:30);
  position = signal held from 15:30 bar close to 16:45 bar close, 1 NQ;
  friction = C1 = 2.872 ticks/trade = $14.36 (tick = 0.25 pt = $5; 1 pt = $20).
  Reference prices ("first bar with time >= T, its close" — same convention frozen in B1):
    p0930 = close of first bar with tod in [09:30, 09:45]
    p1530 = close of first bar with tod in [15:30, 15:45]
    p1645 = close of first bar with tod in [16:45, 17:00]
  Days missing any reference bar (early closes, holidays) are skipped.
  signal == 0 -> no trade, no friction, P&L 0 (day still included in correlations).
- Solar ledger: runs/E10MASTER_V2/out/daily_v1_v2.csv, column net_v1 — the v1 frozen
  research champion ledger (per E10MASTER_V2/results.md, v1 remains the research
  champion for analytics continuity). Truncated to <= 2026-05-31.
- Deliverables: full Pearson rho, losing-day rho (subset where Solar net_v1 < 0),
  monthly-aggregated rho (calendar-month sums). Frozen rule:
    rho >= 0.5 -> family REJECTED as diversifier (build nothing);
    rho <  0.3 -> a build spec MAY be written next wave.
- Seed 20260808 (used only for the supplementary circular block bootstrap CI on rho).

Outputs -> research/scalping_lab/artifacts/w5_b2/
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
ART = ROOT / "research" / "scalping_lab" / "artifacts" / "w5_b2"

DEV_END = pd.Timestamp("2026-05-31 23:59:59")  # contamination boundary (inclusive)
POINT_USD = 20.0          # NQ $ per point
TICK_USD = 5.0            # NQ $ per tick (0.25 pt)
C1_TICKS = 2.872          # frozen friction per trade (round trip), ticks
C1_USD = C1_TICKS * TICK_USD  # = $14.36
SEED = 20260808
BOOT_PATHS = 2000
BOOT_BLOCK = 10           # days, matches the wave's block convention


def load_bars() -> pd.DataFrame:
    df = pd.read_csv(BARS_CSV, parse_dates=["time"])
    n_total = len(df)
    df = df[df["time"] <= DEV_END].copy()  # contamination truncation, applied at load
    print(f"[load] bars rows total={n_total}, kept (<= {DEV_END.date()})={len(df)}, "
          f"dropped sealed-holdout rows={n_total - len(df)}")
    print(f"[load] bar time range kept: {df['time'].min()} .. {df['time'].max()}")
    return df


def ref_price(day: pd.DataFrame, lo: str, hi: str) -> float | None:
    """Close of first bar with time-of-day in [lo, hi]; None if absent."""
    sel = day[(day["tod"] >= lo) & (day["tod"] <= hi)]
    if sel.empty:
        return None
    return float(sel.iloc[0]["close"])


def build_momentum_pnl(bars: pd.DataFrame) -> pd.DataFrame:
    b = bars.copy()
    b["date"] = b["time"].dt.date
    b["tod"] = b["time"].dt.strftime("%H:%M")
    b = b.sort_values("time")

    rows, skipped = [], {"no_0930": 0, "no_1530": 0, "no_1645": 0}
    for date, day in b.groupby("date", sort=True):
        p0930 = ref_price(day, "09:30", "09:45")
        p1530 = ref_price(day, "15:30", "15:45")
        p1645 = ref_price(day, "16:45", "17:00")
        if p0930 is None:
            skipped["no_0930"] += 1
            continue
        if p1530 is None:
            skipped["no_1530"] += 1
            continue
        if p1645 is None:
            skipped["no_1645"] += 1
            continue
        rod_ret = p1530 - p0930                      # rest-of-day return, points
        sig = int(np.sign(rod_ret))
        hold_pts = p1645 - p1530                     # 15:30 -> 16:45, points
        gross = sig * hold_pts * POINT_USD
        pnl = gross - (C1_USD if sig != 0 else 0.0)
        rows.append({"date": pd.Timestamp(date), "p0930": p0930, "p1530": p1530,
                     "p1645": p1645, "rod_ret_pts": rod_ret, "signal": sig,
                     "hold_pts": hold_pts, "gross_usd": gross, "momo_pnl_usd": pnl})
    out = pd.DataFrame(rows)
    print(f"[momo] tradable days={len(out)}; skipped days: {skipped} "
          f"(early closes / holidays lacking a reference bar)")
    print(f"[momo] zero-signal days (no trade, $0): {(out['signal'] == 0).sum()}")
    return out


def block_bootstrap_rho(x: np.ndarray, y: np.ndarray, rng: np.random.Generator,
                        n_paths: int = BOOT_PATHS, block: int = BOOT_BLOCK) -> tuple[float, float]:
    """Circular block bootstrap (fixed block length) 95% CI for Pearson rho.

    Supplementary context only — the frozen gate is on the point estimate.
    """
    n = len(x)
    n_blocks = int(np.ceil(n / block))
    rhos = np.empty(n_paths)
    for i in range(n_paths):
        starts = rng.integers(0, n, size=n_blocks)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel() % n
        idx = idx[:n]
        xb, yb = x[idx], y[idx]
        if xb.std() == 0 or yb.std() == 0:
            rhos[i] = np.nan
            continue
        rhos[i] = np.corrcoef(xb, yb)[0, 1]
    lo, hi = np.nanpercentile(rhos, [2.5, 97.5])
    return float(lo), float(hi)


def pearson(x: pd.Series, y: pd.Series) -> float:
    return float(np.corrcoef(x.to_numpy(float), y.to_numpy(float))[0, 1])


def spearman(x: pd.Series, y: pd.Series) -> float:
    return float(np.corrcoef(x.rank().to_numpy(float), y.rank().to_numpy(float))[0, 1])


def main() -> dict:
    ART.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    bars = load_bars()
    momo = build_momentum_pnl(bars)

    ledger = pd.read_csv(LEDGER_CSV, parse_dates=["sess"])
    n_led = len(ledger)
    ledger = ledger[ledger["sess"] <= DEV_END].copy()
    print(f"[ledger] {LEDGER_CSV.name}: rows={n_led}, kept <= {DEV_END.date()}: {len(ledger)}; "
          f"using column net_v1 (v1 frozen research champion) for the gate")

    joined = momo.merge(ledger.rename(columns={"sess": "date"}), on="date", how="inner")
    joined = joined.sort_values("date").reset_index(drop=True)
    print(f"[join] overlapping dates: {len(joined)} "
          f"({joined['date'].min().date()} .. {joined['date'].max().date()})")

    # ---- frozen deliverables (Pearson, vs net_v1) ----
    rho_full = pearson(joined["momo_pnl_usd"], joined["net_v1"])
    losing = joined[joined["net_v1"] < 0]
    rho_losing = pearson(losing["momo_pnl_usd"], losing["net_v1"])
    monthly = (joined.assign(month=joined["date"].dt.to_period("M").astype(str))
               .groupby("month")[["momo_pnl_usd", "net_v1", "net_v2"]].sum().reset_index())
    rho_monthly = pearson(monthly["momo_pnl_usd"], monthly["net_v1"])

    print("\n===== FROZEN DELIVERABLES (Pearson rho, momentum P&L vs Solar net_v1) =====")
    print(f"rho_full      = {rho_full:+.6f}   (N={len(joined)} days)")
    print(f"rho_losing    = {rho_losing:+.6f}   (N={len(losing)} Solar-losing days, net_v1<0)")
    print(f"rho_monthly   = {rho_monthly:+.6f}   (N={len(monthly)} months)")

    gate = ("REJECTED_AS_DIVERSIFIER (rho >= 0.5)" if rho_full >= 0.5
            else "BUILD_SPEC_PERMITTED_NEXT_WAVE (rho < 0.3)" if rho_full < 0.3
            else "INDETERMINATE_ZONE (0.3 <= rho < 0.5: neither rejected nor build-permitted)")
    print(f"FROZEN GATE (on rho_full): {gate}")

    # ---- supplementary robustness (context only, not gate inputs) ----
    ci_lo, ci_hi = block_bootstrap_rho(joined["momo_pnl_usd"].to_numpy(float),
                                       joined["net_v1"].to_numpy(float), rng)
    rho_sp = spearman(joined["momo_pnl_usd"], joined["net_v1"])
    rho_full_v2 = pearson(joined["momo_pnl_usd"], joined["net_v2"])
    losing_v2 = joined[joined["net_v2"] < 0]
    rho_losing_v2 = pearson(losing_v2["momo_pnl_usd"], losing_v2["net_v2"])
    print("\n----- supplementary (context only) -----")
    print(f"rho_full 95% CI (circular block bootstrap, block={BOOT_BLOCK}d, "
          f"{BOOT_PATHS} paths, seed {SEED}): [{ci_lo:+.6f}, {ci_hi:+.6f}]")
    print(f"spearman_full (vs net_v1)         = {rho_sp:+.6f}")
    print(f"rho_full vs net_v2 (ops ledger)   = {rho_full_v2:+.6f}")
    print(f"rho_losing vs net_v2 (net_v2<0, N={len(losing_v2)}) = {rho_losing_v2:+.6f}")

    # ---- simple stats of the momentum P&L itself (CONTEXT ONLY per spec) ----
    pnl = joined["momo_pnl_usd"]
    traded = joined[joined["signal"] != 0]
    ann_sharpe = float(pnl.mean() / pnl.std() * np.sqrt(252)) if pnl.std() > 0 else float("nan")
    print("\n----- momentum P&L simple stats (context only; H-A1 standalone kill stands) -----")
    print(f"days={len(pnl)}, traded_days={len(traded)}, total=${pnl.sum():,.2f}, "
          f"mean/day=${pnl.mean():,.2f} ({pnl.mean() / TICK_USD:+.3f} ticks), "
          f"std/day=${pnl.std():,.2f}")
    print(f"hit_rate(traded days, pnl>0)={float((traded['momo_pnl_usd'] > 0).mean()):.4f}, "
          f"ann_Sharpe={ann_sharpe:.3f}")
    yearly = (joined.assign(year=joined["date"].dt.year)
              .groupby("year")["momo_pnl_usd"].agg(["count", "sum", "mean"]))
    print("per-year momentum P&L ($):")
    print(yearly.to_string(float_format=lambda v: f"{v:,.2f}"))

    # ---- artifacts ----
    momo.to_csv(ART / "w5b2_momo_daily.csv", index=False)
    joined[["date", "momo_pnl_usd", "net_v1", "net_v2", "signal", "rod_ret_pts",
            "hold_pts"]].to_csv(ART / "w5b2_joined_daily.csv", index=False)
    monthly.to_csv(ART / "w5b2_monthly.csv", index=False)
    stats = {
        "spec": "W5_programs_wave.md §B2 (frozen)",
        "seed": SEED,
        "dev_window_end": str(DEV_END.date()),
        "solar_ledger": "runs/E10MASTER_V2/out/daily_v1_v2.csv column net_v1 (v1 frozen research champion)",
        "friction_per_trade_usd": C1_USD,
        "n_overlap_days": int(len(joined)),
        "n_losing_days_v1": int(len(losing)),
        "n_months": int(len(monthly)),
        "rho_full": rho_full,
        "rho_losing": rho_losing,
        "rho_monthly": rho_monthly,
        "frozen_gate_verdict": gate,
        "supplementary": {
            "rho_full_ci95_block_bootstrap": [ci_lo, ci_hi],
            "spearman_full": rho_sp,
            "rho_full_vs_net_v2": rho_full_v2,
            "rho_losing_vs_net_v2": rho_losing_v2,
            "n_losing_days_v2": int(len(losing_v2)),
        },
        "momentum_context_stats": {
            "days": int(len(pnl)),
            "traded_days": int(len(traded)),
            "total_usd": float(pnl.sum()),
            "mean_per_day_usd": float(pnl.mean()),
            "mean_per_day_ticks": float(pnl.mean() / TICK_USD),
            "std_per_day_usd": float(pnl.std()),
            "hit_rate_traded": float((traded["momo_pnl_usd"] > 0).mean()),
            "ann_sharpe": ann_sharpe,
            "per_year": {str(y): {"count": int(r["count"]), "sum": float(r["sum"]),
                                  "mean": float(r["mean"])} for y, r in yearly.iterrows()},
        },
    }
    with open(ART / "w5b2_stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    print(f"\n[artifacts] written to {ART}")
    return stats


if __name__ == "__main__":
    buf = io.StringIO()

    class Tee(io.TextIOBase):
        def write(self, s):
            buf.write(s)
            sys.__stdout__.write(s)
            return len(s)

    with redirect_stdout(Tee()):
        main()
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "w5b2_stdout.txt").write_text(buf.getvalue())
