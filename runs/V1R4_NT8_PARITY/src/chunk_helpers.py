"""Reusable helpers for the chunked full-history certification harness."""
import json, os
import pandas as pd, numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
CHUNK_OUT = os.path.join(ROOT, "runs", "V1R4_NT8_PARITY", "out", "chunks")
os.makedirs(CHUNK_OUT, exist_ok=True)


def save_and_summarize(job_result_txt_path, save_name, eval_start, eval_end):
    """job_result_txt_path: path to the GetMcpJob overflow .txt file (raw JSON: {status, result:{...}})."""
    d = json.load(open(job_result_txt_path, encoding="utf-8"))
    r = d["result"]
    trades = r["trades"]
    df = pd.DataFrame(trades)
    df["entry_t"] = pd.to_datetime([t["entry"]["time"] for t in trades])
    es, ee = pd.Timestamp(eval_start), pd.Timestamp(eval_end)
    ev = df[(df["entry_t"] >= es) & (df["entry_t"] <= ee)]
    out = {
        "from": r["from"], "to": r["to"], "eval_start": str(es), "eval_end": str(ee),
        "n_bars_loaded": next((int(t.split("loaded ")[1].split(" bars")[0]) for t in r["trace"] if "loaded" in t and "bars" in t), None),
        "n_trades_full_job": len(trades), "n_trades_eval": len(ev),
        "net_eval": float(ev["ProfitCurrency"].sum()) if len(ev) else 0.0,
        "net_full_job": r["performance"]["all"]["NetProfit"],
    }
    json.dump(out, open(os.path.join(CHUNK_OUT, f"{save_name}_summary.json"), "w"), indent=1)
    # also persist the raw trades (compact) for later leg-level drill-down if needed
    compact = [{"entry_t": str(t["entry"]["time"]), "exit_t": str(t["exit"]["time"]),
                "entry_px": t["entry"]["price"], "exit_px": t["exit"]["price"],
                "side": t["entry"]["order_action"], "pnl": t["ProfitCurrency"], "comm": t["Commission"]}
               for t in trades]
    json.dump(compact, open(os.path.join(CHUNK_OUT, f"{save_name}_trades.json"), "w"))
    print(f"{save_name}: eval[{eval_start}..{eval_end}] n_trades_eval={len(ev)} net_eval={out['net_eval']:.2f}")
    return out


def python_eval_net(barpnl_path, bars_time_series, eval_start, eval_end):
    pnl = np.load(barpnl_path)
    m = (bars_time_series >= pd.Timestamp(eval_start)) & (bars_time_series <= pd.Timestamp(eval_end))
    return float(pnl[m].sum()), int(m.sum())
