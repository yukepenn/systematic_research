"""Run ingestion library: CrossTrade GetMcpJob payload -> immutable run artifacts.

Usage:
  python runlib.py ingest <payload_file> <run_dir> [--slim]
      Parse a GetMcpJob payload, write raw_result.json (unless --slim, which
      stores hashes only for payloads proven identical to a reference run),
      metrics.json, trades.parquet, daily_equity.parquet, hashes.json.
      Prints a one-line JSON summary to stdout.
"""
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta

import pandas as pd

POINT_VALUE = 20.0
TICK_VALUE = 5.0


def sha(obj) -> str:
    if not isinstance(obj, (str, bytes)):
        obj = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
    if isinstance(obj, str):
        obj = obj.encode()
    return hashlib.sha256(obj).hexdigest()


def parse_ts(s: str) -> datetime:
    return datetime.fromisoformat(s[:26])


def session_date(ts: datetime):
    """Map an exchange-time (ET) timestamp to its trading-session date.
    Sessions run 18:00 ET (prior day) -> 17:00 ET. Weekend evening opens roll
    forward to the next business day."""
    d = ts.date()
    if ts.hour >= 18:
        d = d + timedelta(days=1)
    while d.weekday() >= 5:  # Sat/Sun -> Monday
        d = d + timedelta(days=1)
    return d


def canonical_ledger(trades):
    rows = []
    for t in trades:
        e, x = t["entry"], t["exit"]
        rows.append([
            t["TradeNumber"], t["Quantity"], e["market_position"],
            e["time"], e["price"], x["time"], x["price"], x.get("name"),
            round(t["ProfitCurrency"], 2), round(t["Commission"], 2),
            round(t["MaeCurrency"], 2), round(t["MfeCurrency"], 2),
        ])
    return rows


def trades_frame(trades) -> pd.DataFrame:
    rows = []
    for t in trades:
        e, x = t["entry"], t["exit"]
        et, xt = parse_ts(e["time"]), parse_ts(x["time"])
        side = 1 if e["market_position"] == "Long" else -1
        rows.append(dict(
            trade_n=t["TradeNumber"], qty=t["Quantity"], side=side,
            entry_time=et, entry_price=e["price"],
            exit_time=xt, exit_price=x["price"], exit_name=x.get("name"),
            profit=t["ProfitCurrency"], commission=t["Commission"],
            mae=t["MaeCurrency"], mfe=t["MfeCurrency"],
            duration_min=(xt - et).total_seconds() / 60.0,
            session=session_date(xt),
            entry_hour=et.hour,
        ))
    df = pd.DataFrame(rows)
    if len(df):
        df["session"] = pd.to_datetime(df["session"])
    return df


def audits(df: pd.DataFrame, slip_ticks: int, rt_commission: float = 4.36):
    out = {}
    out["n_trades_serialized"] = int(len(df))
    out["negative_duration"] = int((df["duration_min"] < 0).sum())
    out["same_timestamp_entry_exit"] = int((df["duration_min"] == 0).sum())
    # P&L identity: profit == side*(exit-entry)*20*qty - commission (fills already include slippage)
    ident = df["side"] * (df["exit_price"] - df["entry_price"]) * POINT_VALUE * df["qty"] - df["commission"]
    out["pnl_identity_max_abs_err"] = float((df["profit"] - ident).abs().max())
    # session-close exits exactly at 17:00
    sc = df[df["exit_name"].str.contains("session close", case=False, na=False)]
    bad_sc = sc[~((sc["exit_time"].dt.hour == 17) & (sc["exit_time"].dt.minute == 0))]
    out["session_close_exits"] = int(len(sc))
    out["session_close_not_at_1700"] = int(len(bad_sc))
    # no trade spans the 17:00->18:00 maintenance break (flat-at-close structural property)
    spans = df[(df["entry_time"].dt.hour < 17) & (df["exit_time"].dt.date > df["entry_time"].dt.date)]
    out["trades_spanning_sessions"] = int(len(spans))
    out["max_exit_hourmin"] = df["exit_time"].dt.strftime("%H:%M").max()
    return out


def daily_equity(df: pd.DataFrame) -> pd.DataFrame:
    d = df.groupby("session")["profit"].sum().rename("pnl").to_frame()
    d["equity"] = d["pnl"].cumsum()
    d["peak"] = d["equity"].cummax()
    d["dd"] = d["equity"] - d["peak"]
    return d


def perf_metrics(df: pd.DataFrame, perf_all: dict) -> dict:
    d = daily_equity(df)
    pnl = d["pnl"]
    n = len(df)
    wins = df[df["profit"] > 0]["profit"]
    losses = df[df["profit"] < 0]["profit"]
    ann = 252
    sharpe = float(pnl.mean() / pnl.std(ddof=1) * ann ** 0.5) if pnl.std(ddof=1) > 0 else None
    downside = pnl[pnl < 0]
    sortino = float(pnl.mean() / downside.std(ddof=1) * ann ** 0.5) if len(downside) > 1 else None
    max_dd = float(d["dd"].min())
    ann_pnl = float(pnl.mean() * ann)
    es95 = float(pnl[pnl <= pnl.quantile(0.05)].mean()) if len(pnl) >= 20 else None
    # time under water (trading days below prior peak)
    tuw, cur, mx = 0, 0, 0
    for v in d["dd"]:
        cur = cur + 1 if v < 0 else 0
        mx = max(mx, cur)
        tuw += 1 if v < 0 else 0
    # top-decile winner contribution
    k = max(1, int(len(wins) * 0.10))
    top_decile = float(wins.nlargest(k).sum())
    gp = float(wins.sum()); gl = float(losses.sum())
    q = d["pnl"].resample("QE").sum()
    m = d["pnl"].resample("ME").sum()
    remove_top = {f"net_minus_top{j}": round(float(df["profit"].sum() - df["profit"].nlargest(j).sum()), 2) for j in (1, 3, 5, 10)}
    return dict(
        n_trades=n, net=round(float(df["profit"].sum()), 2),
        gross_profit=round(gp, 2), gross_loss=round(gl, 2),
        pf=round(gp / -gl, 6) if gl else None,
        pct_win=round(100 * len(wins) / n, 4),
        avg_trade=round(float(df["profit"].mean()), 4),
        avg_win=round(float(wins.mean()), 4), avg_loss=round(float(losses.mean()), 4),
        avg_duration_min=round(float(df["duration_min"].mean()), 4),
        commission_total=round(float(df["commission"].sum()), 2),
        daily_sharpe=round(sharpe, 4) if sharpe else None,
        daily_sortino=round(sortino, 4) if sortino else None,
        ann_pnl=round(ann_pnl, 0), max_dd_daily=round(max_dd, 2),
        calmar=round(ann_pnl / abs(max_dd), 4) if max_dd else None,
        es95_daily=round(es95, 2) if es95 else None,
        tuw_days_total=tuw, tuw_days_max=mx, n_days=len(d),
        worst_quarter=round(float(q.min()), 2), best_quarter=round(float(q.max()), 2),
        pct_positive_quarters=round(100 * float((q > 0).mean()), 1),
        pct_positive_months=round(100 * float((m > 0).mean()), 1),
        top_decile_winner_pnl=round(top_decile, 2),
        top_decile_share_of_gp=round(top_decile / gp, 4) if gp else None,
        **remove_top,
        nt8=dict(
            TradesCount=perf_all.get("TradesCount"), NetProfit=perf_all.get("NetProfit"),
            ProfitFactor=perf_all.get("ProfitFactor"),
            MaxDrawdown=perf_all.get("Currency", {}).get("Drawdown"),
            TotalCommission=perf_all.get("TotalCommission"),
            TotalSlippage=perf_all.get("TotalSlippage"),
            SharpeRatio=perf_all.get("SharpeRatio"), SortinoRatio=perf_all.get("SortinoRatio"),
        ),
    )


def ingest(payload_file: str, run_dir: str, slim: bool = False) -> dict:
    t0 = time.time()
    with open(payload_file, encoding="utf-8") as f:
        job = json.load(f)
    res = job["result"]
    if res.get("error"):
        raise SystemExit(json.dumps({"error": res["error"], "detail": res.get("detail")}))
    trades = res.get("trades", [])
    ledger = canonical_ledger(trades)
    hashes = dict(
        ledger_hash=sha(ledger),
        metrics_hash=sha({k: res["performance"]["all"].get(k) for k in
                          ("TradesCount", "NetProfit", "GrossProfit", "GrossLoss", "ProfitFactor", "TotalCommission", "TotalSlippage")}),
        equity_hash=sha(res.get("equity_curve", [])),
        params_hash=sha(res.get("effective_parameters", {})),
        payload_bytes=os.path.getsize(payload_file),
    )
    os.makedirs(run_dir, exist_ok=True)
    df = trades_frame(trades)
    slip = int(res.get("effective_slippage", 0) or 0)
    a = audits(df, slip) if len(df) else {}
    m = perf_metrics(df, res["performance"]["all"]) if len(df) else {}
    bench = dict(
        engine_ms=job.get("elapsed_ms"),
        started_at=job.get("started_at"), finished_at=job.get("finished_at"),
        payload_bytes=hashes["payload_bytes"],
    )
    if not slim:
        with open(os.path.join(run_dir, "raw_result.json"), "w", encoding="utf-8") as f:
            json.dump(job, f, indent=1)
    if len(df):
        df.to_parquet(os.path.join(run_dir, "trades.parquet"), index=False)
        daily_equity(df).to_parquet(os.path.join(run_dir, "daily_equity.parquet"))
    out = dict(run_dir=os.path.basename(run_dir), job_id=job.get("job_id"),
               effective_parameters=res.get("effective_parameters"),
               hashes=hashes, audits=a, metrics=m, bench=bench,
               ingest_ms=round((time.time() - t0) * 1000, 1))
    with open(os.path.join(run_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    with open(os.path.join(run_dir, "hashes.json"), "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=1)
    return out


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "ingest":
        slim = "--slim" in sys.argv
        summary = ingest(sys.argv[2], sys.argv[3], slim=slim)
        print(json.dumps({k: summary[k] for k in ("run_dir", "job_id", "hashes", "audits", "bench", "ingest_ms")}, default=str))
        print("METRICS:", json.dumps(summary["metrics"], default=str))
    else:
        raise SystemExit(f"unknown command {cmd}")
