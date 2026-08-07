"""Discovery Wave 1: rank sweep results, analytic slip-1 overlay, plateau analysis."""
import json
import os
import sys

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
SLIP1_PER_TRADE = 9.53  # empirical bar-capped $/RT/tick from SW00


def load_rows(payload_file, param_names):
    with open(payload_file, encoding="utf-8") as f:
        job = json.load(f)
    res = job["result"]
    rows = []
    for it in res["results"]:
        p = {pv["name"]: pv["value"] for pv in it["parameter_values"]}
        s = it["performance_summary"]
        r = {k: p.get(k) for k in param_names}
        n = s["TradesCount"]
        r.update(net0=round(s["NetProfit"], 0), pf=round(s["ProfitFactor"], 4),
                 trades=n, sharpe=round(s["SharpeRatio"], 3),
                 avg0=round(s["NetProfit"] / n, 2) if n else None,
                 net1=round(s["NetProfit"] - n * SLIP1_PER_TRADE, 0),
                 avg1=round(s["NetProfit"] / n - SLIP1_PER_TRADE, 2) if n else None)
        rows.append(r)
    return rows, job


def grid_neighbors(rows, keys):
    vals = {k: sorted({r[k] for r in rows}) for k in keys}
    idx = {tuple(r[k] for k in keys): r for r in rows}
    for r in rows:
        nb = []
        for k in keys:
            v = vals[k]
            i = v.index(r[k])
            for j in (i - 1, i + 1):
                if 0 <= j < len(v):
                    key = tuple(v[j] if kk == k else r[kk] for kk in keys)
                    if key in idx:
                        nb.append(idx[key])
        r["n_nb"] = len(nb)
        r["nb_pos_pct"] = round(100 * sum(1 for x in nb if x["net1"] > 0) / len(nb), 0) if nb else None
        med = sorted(x["net1"] for x in nb)
        r["nb_med_net1"] = med[len(med) // 2] if med else None
    return rows


if __name__ == "__main__":
    payload, run_dir, names = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
    rows, job = load_rows(payload, names)
    os.makedirs(os.path.join(ROOT, "runs", run_dir), exist_ok=True)
    with open(os.path.join(ROOT, "runs", run_dir, "raw_result.json"), "w", encoding="utf-8") as f:
        json.dump(job, f, indent=1)
    if len(names) >= 2:
        rows = grid_neighbors(rows, names)
    rows.sort(key=lambda r: -(r["net1"] if r["net1"] is not None else -1e9))
    with open(os.path.join(ROOT, "runs", run_dir, "ranked.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1)
    for r in rows:
        print(json.dumps(r))
