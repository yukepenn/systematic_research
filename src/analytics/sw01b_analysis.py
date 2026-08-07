"""SW01b: null-distribution analysis from sweep payloads."""
import json
import os
import sys

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
BASELINE_NET = 146440.60
BASELINE_PF = 1.132213
BASELINE_TRADES = 2915


def load_sweep(payload_file, run_dir):
    with open(payload_file, encoding="utf-8") as f:
        job = json.load(f)
    res = job["result"]
    assert res.get("mode") == "optimization", res.get("error")
    rows = []
    for it in res["results"]:
        p = {pv["name"]: pv["value"] for pv in it["parameter_values"]}
        s = it["performance_summary"]
        rows.append(dict(seed=p.get("Seed"), net=s["NetProfit"], pf=s["ProfitFactor"],
                         trades=s["TradesCount"], gp=s["GrossProfit"], gl=s["GrossLoss"],
                         sharpe=s["SharpeRatio"]))
    rows.sort(key=lambda r: r["seed"])
    os.makedirs(os.path.join(ROOT, "runs", run_dir), exist_ok=True)
    with open(os.path.join(ROOT, "runs", run_dir, "raw_result.json"), "w", encoding="utf-8") as f:
        json.dump(job, f, indent=1)
    return rows, res.get("iterations_completed")


def stats(rows, key="net"):
    v = sorted(r[key] for r in rows)
    n = len(v)
    return dict(n=n, min=round(v[0], 2), p25=round(v[n // 4], 2), median=round(v[n // 2], 2),
                p75=round(v[3 * n // 4], 2), max=round(v[-1], 2),
                mean=round(sum(v) / n, 2))


a_rows, a_iter = load_sweep(sys.argv[1], "SW01b_SWEEP_A")
b_rows, b_iter = load_sweep(sys.argv[2], "SW01b_SWEEP_B")

out = dict(
    mode0=dict(iterations=a_iter, net=stats(a_rows), pf=stats(a_rows, "pf"),
               trades=stats(a_rows, "trades"),
               n_above_baseline=sum(1 for r in a_rows if r["net"] >= BASELINE_NET),
               baseline_net=BASELINE_NET,
               empirical_p_one_sided=round((1 + sum(1 for r in a_rows if r["net"] >= BASELINE_NET)) / (len(a_rows) + 1), 4),
               null_rejected=all(r["net"] < BASELINE_NET for r in a_rows),
               seeds=a_rows),
    mode1=dict(iterations=b_iter, net=stats(b_rows), trades=stats(b_rows, "trades"),
               pf=stats(b_rows, "pf"),
               per_trade_mean=round(sum(r["net"] / r["trades"] for r in b_rows) / len(b_rows), 2),
               seeds=b_rows),
)
with open(os.path.join(ROOT, "research", "01_diagnostics", "SW01b_null_analysis.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
compact = {k: {kk: vv for kk, vv in v.items() if kk != "seeds"} for k, v in out.items()}
print(json.dumps(compact, indent=1))
