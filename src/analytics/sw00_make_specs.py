"""Generate preregistered immutable spec.yaml files for SW00_R01..R13."""
import hashlib
import json
import os
from datetime import datetime, timezone

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
STRAT = r"C:\Users\Yuke Zhang\Documents\NinjaTrader 8\bin\Custom\Strategies\SolarWaveRKReplicaV0.cs"

src = open(STRAT, "rb").read()
src_hash = hashlib.sha256(src).hexdigest()
src_mtime = datetime.fromtimestamp(os.path.getmtime(STRAT), tz=timezone.utc).isoformat()

PARAMS = {"EntrySignalType": 1, "EnableLong": True, "EnableShort": True,
          "TrendMultiplier": 90, "StopMultiplier": 179, "SlowdownScan": 5,
          "WeakWeakSplit": 10, "PullbackEarly": True, "PullbackSplit": 10,
          "UseTimeFilter": False, "StartTime": 93000, "EndTime": 160000}
params_hash = hashlib.sha256(json.dumps(PARAMS, sort_keys=True).encode()).hexdigest()

CANON_FROM, CANON_TO = "2023-01-01T06:00:00Z", "2025-02-02T22:59:59Z"

RUNS = {
    "SW00_R01": dict(purpose="determinism_1_and_baseline", slip=0, fro=CANON_FROM, to=CANON_TO),
    "SW00_R02": dict(purpose="determinism_2", slip=0, fro=CANON_FROM, to=CANON_TO),
    "SW00_R03": dict(purpose="determinism_3", slip=0, fro=CANON_FROM, to=CANON_TO),
    "SW00_R04": dict(purpose="determinism_4", slip=0, fro=CANON_FROM, to=CANON_TO),
    "SW00_R05": dict(purpose="determinism_5", slip=0, fro=CANON_FROM, to=CANON_TO),
    "SW00_R06": dict(purpose="cost_stress_slip1", slip=1, fro=CANON_FROM, to=CANON_TO),
    "SW00_R07": dict(purpose="cost_stress_slip2", slip=2, fro=CANON_FROM, to=CANON_TO),
    "SW00_R08": dict(purpose="cost_stress_slip3", slip=3, fro=CANON_FROM, to=CANON_TO),
    "SW00_R09": dict(purpose="fill_high_probe_quarantined", slip=0, fill="High",
                     fro=CANON_FROM, to="2023-01-28T00:00:00Z", timeout_ms=180000),
    "SW00_R10": dict(purpose="optimization_machinery_zero_info_sweep", slip=0,
                     fro=CANON_FROM, to=CANON_TO,
                     optimization={"optimizer": "DefaultOptimizer", "fitness": "MaxNetProfit",
                                    "keep_best_results": 2,
                                    "parameters_sweep": [{"name": "StartTime", "min": 93000, "max": 93001, "step": 1, "type": "int"}]}),
    "SW00_R11": dict(purpose="timing_scaling_3mo_quarantined", slip=0,
                     fro=CANON_FROM, to="2023-04-01T00:00:00Z"),
    "SW00_R12": dict(purpose="parallel_submission_a", slip=0, fro=CANON_FROM, to=CANON_TO),
    "SW00_R13": dict(purpose="parallel_submission_b", slip=0, fro=CANON_FROM, to=CANON_TO),
}

TPL = """# IMMUTABLE preregistered run spec — written before results were read.
run_id: {rid}
experiment_id: SW00_BASELINE_PARITY_COST
hypothesis: H-001 (research/registry/hypotheses.md)
mechanism: additive per-execution friction vs baseline edge; pipeline determinism
purpose: {purpose}
tested_config_seq: 1        # same search-space config as canonical anchor; no new DoF
parent_run: parity_B (research/solar_wave_parity/type1_2023_2025/raw_result_boundary_corrected.json)
strategy_class: SolarWaveRKReplicaV0
strategy_source_sha256: {src_hash}
strategy_source_mtime: {src_mtime}
git_commit: (preregistration commit; filled by git history)
ninjatrader_version: 8.1.8.1
crosstrade_version: v1.13.9
engine_fingerprint: sha256:b4255f1b0dd7fba1
vendor_indicator: RenkoKings_SolarWaveRK (version not exposed; assembly untouched)
instrument: "NQ 09-26"       # resolves NQU6, NT-configured back-adjusted merge
bars: {{period_type: Minute, value: 1, market_data_type: Last}}
from_utc: "{fro}"
to_utc: "{to}"
timezone_note: payload timestamps are exchange-session time (ET); sessions 18:00->17:00
trading_hours: instrument default (CME index futures ETH)
parameters_hash: {params_hash}
parameters: {params}
commission_template: "NinjaTrader Brokerage Lifetime"
slippage_ticks_per_execution: {slip}
fill_resolution: {fill}
entries_per_direction: 1 (AllEntries, from SetDefaults)
session_close: exit-on-session-close true, 30s (from SetDefaults)
time_in_force: GTC
quantity: 1 (DefaultQuantity, hardcoded)
account: isolated Backtest ($100k, USD)
{extra}acceptance_criteria: research/00_truth/SW00_spec.md (gates 1-6)
rejection_criteria: research/00_truth/SW00_spec.md (rejection section)
"""

for rid, cfg in RUNS.items():
    d = os.path.join(ROOT, "runs", rid)
    os.makedirs(d, exist_ok=True)
    extra = ""
    if "optimization" in cfg:
        extra += "optimization: " + json.dumps(cfg["optimization"]) + "\n"
    if "timeout_ms" in cfg:
        extra += f"timeout_ms: {cfg['timeout_ms']}\n"
    spec = TPL.format(rid=rid, purpose=cfg["purpose"], src_hash=src_hash, src_mtime=src_mtime,
                      fro=cfg["fro"], to=cfg["to"], params_hash=params_hash,
                      params=json.dumps(PARAMS), slip=cfg["slip"],
                      fill=cfg.get("fill", "Standard"), extra=extra)
    p = os.path.join(d, "spec.yaml")
    if os.path.exists(p):
        raise SystemExit(f"REFUSING to overwrite existing {p}")
    with open(p, "w", encoding="utf-8") as f:
        f.write(spec)
    print("wrote", rid)
print("strategy_source_sha256:", src_hash, "mtime:", src_mtime)
