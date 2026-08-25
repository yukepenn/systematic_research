"""R12: A3/A4/A5 retune as a natural experiment (directive v4.0 section 11).

Which Solar event families actually move when 5/10/10 -> 3/6/9 (A2 179 -> 180)?
Measured in EVENT SPACE ONLY. No P&L is computed anywhere in this file, by design:
the point is to identify the causal candidates for the layer the trader has and our
T1 skeleton does not, without letting profit pick the answer.
"""
import csv
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solarwave import SolarWaveParams, solar_wave_full  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R12_PARAM_INTERVENTION", "out")
os.makedirs(OUT, exist_ok=True)

OLD = dict(offset_multiplier_trend=90.0, offset_multiplier_stop=179.0,
           slowdown_scan=5, weak_weak_split=10, pullback_split=10)
NEW = dict(offset_multiplier_trend=90.0, offset_multiplier_stop=180.0,
           slowdown_scan=3, weak_weak_split=6, pullback_split=9)
# isolate which single field carries each effect
ONLY_A2 = dict(OLD, offset_multiplier_stop=180.0)
ONLY_A3 = dict(OLD, slowdown_scan=3)
ONLY_A4 = dict(OLD, weak_weak_split=6)
ONLY_A5 = dict(OLD, pullback_split=9)
SETS = {"OLD_5_10_10": OLD, "NEW_3_6_9": NEW, "only_A2_180": ONLY_A2,
        "only_A3_3": ONLY_A3, "only_A4_6": ONLY_A4, "only_A5_9": ONLY_A5}


def families(seg, prm, early):
    r = solar_wave_full(seg["open"].values, seg["high"].values, seg["low"].values,
                        seg["close"].values, SolarWaveParams(pullback_early=early, **prm))
    st = r.signal_trade.astype(int)
    return dict(
        T1=set(np.flatnonzero(np.abs(st) == 1).tolist()),
        T2=set(np.flatnonzero(np.abs(st) == 2).tolist()),
        T3=set(np.flatnonzero(np.abs(st) == 3).tolist()),
        T1L=set(np.flatnonzero(st == 1).tolist()),
        T1S=set(np.flatnonzero(st == -1).tolist()),
        T2L=set(np.flatnonzero(st == 2).tolist()),
        T2S=set(np.flatnonzero(st == -2).tolist()),
        T3L=set(np.flatnonzero(st == 3).tolist()),
        T3S=set(np.flatnonzero(st == -3).tolist()),
        _weak=r.signal_trend, _wave=r.signal_wave, _tv=r.trend_vector,
        _c=seg["close"].values)


def jac(a, b):
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def main():
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2025-06-15") & (df["time"] <= "2026-01-24 17:00")].reset_index(drop=True)
    print(f"bars: {len(seg):,}  {seg['time'].iloc[0]} .. {seg['time'].iloc[-1]}")

    rows = []
    for early in (True, False):
        F = {k: families(seg, v, early) for k, v in SETS.items()}
        base = F["OLD_5_10_10"]
        print(f"\n================ PullbackEarly = {early} ================")
        print(f"{'param set':<14} {'T1':>6} {'T2':>6} {'T3':>6} | "
              f"{'J(T1)':>7} {'J(T2)':>7} {'J(T3)':>7} | {'weak%':>6} {'waves':>6} {'TVx':>6}")
        for k, f in F.items():
            weak_pct = 100.0 * float(np.mean(np.abs(f["_weak"]) == 1))
            waves = int(np.sum(np.abs(np.diff(f["_wave"])) > 0))
            tvx = int(np.sum(np.sign(f["_c"][1:] - f["_tv"][1:]) !=
                             np.sign(f["_c"][:-1] - f["_tv"][:-1])))
            print(f"{k:<14} {len(f['T1']):>6} {len(f['T2']):>6} {len(f['T3']):>6} | "
                  f"{jac(base['T1'], f['T1']):>7.4f} {jac(base['T2'], f['T2']):>7.4f} "
                  f"{jac(base['T3'], f['T3']):>7.4f} | {weak_pct:>6.2f} {waves:>6} {tvx:>6}")
            rows.append(dict(pullback_early=early, param_set=k,
                             n_T1=len(f["T1"]), n_T2=len(f["T2"]), n_T3=len(f["T3"]),
                             n_T1_long=len(f["T1L"]), n_T1_short=len(f["T1S"]),
                             n_T2_long=len(f["T2L"]), n_T2_short=len(f["T2S"]),
                             n_T3_long=len(f["T3L"]), n_T3_short=len(f["T3S"]),
                             jac_T1=round(jac(base["T1"], f["T1"]), 6),
                             jac_T2=round(jac(base["T2"], f["T2"]), 6),
                             jac_T3=round(jac(base["T3"], f["T3"]), 6),
                             weak_duty_pct=round(weak_pct, 3),
                             wave_transitions=waves, tv_crosses=tvx))
        # per-family deltas OLD -> NEW, with side asymmetry
        n = F["NEW_3_6_9"]
        print(f"\n  OLD -> NEW deltas (counts, and long/short split):")
        for fam in ("T1", "T2", "T3"):
            do = len(base[fam]); dn = len(n[fam])
            pl = (100.0 * (dn - do) / do) if do else float("nan")
            lo_, ln_ = len(base[fam + "L"]), len(n[fam + "L"])
            so_, sn_ = len(base[fam + "S"]), len(n[fam + "S"])
            print(f"    {fam}: {do:>6} -> {dn:>6}  ({pl:+7.2f}%)   "
                  f"long {lo_}->{ln_} ({100*(ln_-lo_)/max(lo_,1):+.1f}%)  "
                  f"short {so_}->{sn_} ({100*(sn_-so_)/max(so_,1):+.1f}%)")
        # how many NEW events are at bars where OLD had NOTHING
        allo = base["T1"] | base["T2"] | base["T3"]
        for fam in ("T1", "T2", "T3"):
            fresh = len(n[fam] - allo)
            print(f"    {fam}: {fresh} NEW-only event bars carry no OLD event at all")

    with open(os.path.join(OUT, "event_family_deltas.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"\nwrote {os.path.join(OUT, 'event_family_deltas.csv')}")

    # ---- prereg verdicts -----------------------------------------------------
    d = pd.DataFrame(rows)
    print("\n=== PREREGISTERED PREDICTION VERDICTS ===")
    for early in (True, False):
        b = d[(d.pullback_early == early) & (d.param_set == "OLD_5_10_10")].iloc[0]
        nn = d[(d.pullback_early == early) & (d.param_set == "NEW_3_6_9")].iloc[0]
        p1 = nn.jac_T1 > 0.97
        p2 = nn.n_T3 > b.n_T3
        p3 = nn.n_T2 > b.n_T2
        p4 = nn.weak_duty_pct > b.weak_duty_pct
        print(f"  early={early}: P1 T1-invariant(J>0.97) {nn.jac_T1:.4f} "
              f"{'PASS' if p1 else 'FAIL'} | P2 T3 up {b.n_T3}->{nn.n_T3} "
              f"{'PASS' if p2 else 'FAIL'} | P3 T2 up {b.n_T2}->{nn.n_T2} "
              f"{'PASS' if p3 else 'FAIL'} | P4 weak up {b.weak_duty_pct:.2f}->"
              f"{nn.weak_duty_pct:.2f} {'PASS' if p4 else 'FAIL'}")


if __name__ == "__main__":
    main()
