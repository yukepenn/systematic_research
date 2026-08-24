"""FAMILY C hunt: solar-internal-state gates on flip entries.

Builds an instrumented Solar Wave state trace (weak automaton, wave counter,
T2 latch in BOTH PullbackEarly modes, leg/anchor history), runs the base policy
(comm 2.09, T1, reverse_on_flip) on the Jan-2023 slice, joins each flip entry
with the ground-truth TAKE/SKIP labels from r12f_flip_features.csv, and scans
candidate solar-state gates for separation.

Creates only new files suffixed _C. Does not modify anything existing.
"""
from __future__ import annotations

import sys, os, json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, r"research\original_trader_reconstruction\solar_family\src"))
sys.path.insert(0, os.path.join(ROOT, r"src\analytics"))

from otr_engine import load_ledger, run_wrapper, WrapperPolicy  # noqa: E402
from solarwave import SolarWaveParams, solar_wave  # noqa: E402

LEDGER = os.path.join(ROOT, r"research\03_reverse_engineering\ledgers\t2_canonical_1m.csv")
FEAT = os.path.join(ROOT, r"runs\OTR_R1_SERIES\out\r12f_flip_features.csv")
OUT = os.path.join(ROOT, r"runs\OTR_R1_SERIES\out")

S_PTS = 179 * 0.25
V_PTS = 90 * 0.25


def instrumented_state(o, h, l, c, p: SolarWaveParams):
    """Re-run the exact solar_wave recurrence, exposing internal state per bar.

    Returns dict of arrays (all length n, value = state at END of bar t):
      is_up, anchor, event (0 none,1 extreme,2 flip), weak, bse, wave,
      armed_early, armed_late, fire_early, fire_late, leg_id
    """
    n = len(c)
    is_up_a = np.zeros(n, bool); anchor_a = np.empty(n)
    event_a = np.zeros(n, np.int8); weak_a = np.zeros(n, bool)
    bse_a = np.zeros(n, np.int64); wave_a = np.zeros(n, np.int64)
    leg_a = np.zeros(n, np.int64)

    is_up = False; anchor = c[0]; weak = False; bse = 0
    next_weak = -(1 << 60); wave = 1; leg = 0
    S = p.offset_multiplier_stop * p.tick_size
    t3_a = np.zeros(n, bool); flip_a = np.zeros(n, bool)
    for t in range(n):
        px = c[t]; event = 0
        if t > 0:
            if is_up:
                if px >= anchor:
                    if px > anchor: event = 1
                    anchor = px
                elif px < anchor - S:
                    is_up, anchor, event = False, px, 2
            else:
                if px <= anchor:
                    if px < anchor: event = 1
                    anchor = px
                elif px > anchor + S:
                    is_up, anchor, event = True, px, 2
        if event == 2:
            weak = False; bse = 0; wave = 1; leg += 1
            flip_a[t] = True
            next_weak = t + p.weak_weak_split
        elif event == 1:
            bse = 0
            if weak:
                wave += 1; weak = False; t3_a[t] = True
                next_weak = t + p.weak_weak_split
        elif t > 0:
            bse += 1
            if (not weak) and bse >= p.slowdown_scan and t >= next_weak:
                weak = True; next_weak = t + p.weak_weak_split
        is_up_a[t] = is_up; anchor_a[t] = anchor; event_a[t] = event
        weak_a[t] = weak; bse_a[t] = bse; wave_a[t] = wave; leg_a[t] = leg

    tv = np.where(is_up_a, anchor_a - 90 * 0.25, anchor_a + 90 * 0.25)

    # T2 latch, both modes (exact copy of solar_wave_full logic)
    def latch(early: bool):
        armed_a = np.zeros(n, bool); fire_a = np.zeros(n, bool)
        armed = True; next_pb = -(1 << 60)
        for t in range(n):
            if flip_a[t]:
                armed = True; next_pb = -(1 << 60)
                armed_a[t] = armed
                continue
            up = bool(is_up_a[t])
            if early:
                ext = l[t] if up else h[t]
                beyond = ext < tv[t] if up else ext > tv[t]
                inside = ext > tv[t] if up else ext < tv[t]
                if beyond and armed and t > next_pb and t > 0:
                    fire_a[t] = True; next_pb = t + p.pullback_split
                if beyond: armed = False
                elif inside: armed = True
            else:
                open_beyond = o[t] < tv[t] if up else o[t] > tv[t]
                close_beyond = c[t] < tv[t] if up else c[t] > tv[t]
                close_inside = c[t] > tv[t] if up else c[t] < tv[t]
                if (not armed or open_beyond) and close_inside and t > next_pb and t > 0:
                    fire_a[t] = True; next_pb = t + p.pullback_split
                if close_beyond: armed = False
                elif close_inside: armed = True
            if t3_a[t]:
                armed = True
            armed_a[t] = armed
        return armed_a, fire_a

    armed_e, fire_e = latch(True)
    armed_l, fire_l = latch(False)
    return dict(is_up=is_up_a, anchor=anchor_a, event=event_a, weak=weak_a,
                bse=bse_a, wave=wave_a, leg=leg_a, tv=tv, flip=flip_a, t3=t3_a,
                armed_early=armed_e, fire_early=fire_e,
                armed_late=armed_l, fire_late=fire_l)


def build():
    bars = load_ledger(LEDGER)
    n = bars["n"]
    o, h, l, c = bars["open"], bars["high"], bars["low"], bars["close"]
    p = SolarWaveParams()
    st_led = bars["signal_trade"]

    S = instrumented_state(o, h, l, c, p)

    # parity check vs ledger (EARLY mode)
    sign = np.where(S["is_up"], 1, -1)
    st_re = np.zeros(n, np.int64)
    st_re[S["t3"]] = 3 * sign[S["t3"]]
    st_re[S["fire_early"]] = 2 * sign[S["fire_early"]]
    st_re[S["flip"]] = 1 * sign[S["flip"]]
    agree = float(np.mean(st_re == st_led))
    print(f"EARLY-mode signal_trade parity vs ledger: {agree*100:.4f}%  "
          f"(mismatches: {int(np.sum(st_re != st_led))})")

    # leg table: per leg id -> dir, start index, end index, final anchor, stats
    leg = S["leg"]
    nlegs = leg[-1] + 1
    leg_start = np.zeros(nlegs, np.int64)
    leg_end = np.zeros(nlegs, np.int64)
    for lid in range(nlegs):
        idx = np.flatnonzero(leg == lid)
        leg_start[lid] = idx[0]; leg_end[lid] = idx[-1]
    leg_dir = np.where(S["is_up"][leg_start], 1, -1)
    leg_final_anchor = S["anchor"][leg_end]
    leg_max_wave = np.array([S["wave"][leg_start[i]:leg_end[i]+1].max() for i in range(nlegs)])
    leg_n_t3 = np.array([int(S["t3"][leg_start[i]:leg_end[i]+1].sum()) for i in range(nlegs)])
    leg_n_t2e = np.array([int(S["fire_early"][leg_start[i]:leg_end[i]+1].sum()) for i in range(nlegs)])
    leg_n_t2l = np.array([int(S["fire_late"][leg_start[i]:leg_end[i]+1].sum()) for i in range(nlegs)])
    leg_len = leg_end - leg_start + 1
    # index of the extreme bar (last time anchor changed) within leg
    leg_ext_bar = np.array([leg_end[i] - S["bse"][leg_end[i]] for i in range(nlegs)])

    legs = dict(start=leg_start, end=leg_end, dir=leg_dir, fa=leg_final_anchor,
                max_wave=leg_max_wave, n_t3=leg_n_t3, n_t2e=leg_n_t2e,
                n_t2l=leg_n_t2l, length=leg_len, ext_bar=leg_ext_bar)
    return bars, S, legs


def jan_slice(bars):
    cutoff = np.datetime64("2023-01-21T00:00:00")
    m = bars["time"] < cutoff
    nn = int(m.sum())
    sl = {}
    for k, v in bars.items():
        if isinstance(v, np.ndarray):
            sl[k] = v[:nn]
    sl["n"] = nn
    sl["last_bar"] = sl["last_bar"].copy()
    sl["last_bar"][-1] = True
    return sl


def base_trades(bars_sl):
    pol = WrapperPolicy(name="base", comm_side=2.09, entry_types=(1,), reverse_on_flip=True)
    res = run_wrapper(bars_sl, pol)
    return res["trades"]


def features_for_trades(trades, bars, S, legs):
    """For each base trade, features of the flip signal bar j = entry_i - 1."""
    rows = []
    time_arr = bars["time"]
    c = bars["close"]; o = bars["open"]; h = bars["high"]; l = bars["low"]
    st = bars["signal_trade"]
    for t in trades:
        j = t["entry_i"] - 1
        sig = st[j]
        d = 1 if t["dir"] > 0 else -1
        k = S["leg"][j]           # new leg id (flip bar starts leg k)
        row = dict(entry_time=t["entry_time"], dir=("L" if d > 0 else "S"),
                   pnl=t["pnl"], sig_at_j=int(sig), leg_id=int(k))
        # old leg = k-1 (dir -d); same-dir legs: k-2; prev opposite: k-3
        def A(i):
            return legs["fa"][i] if i >= 0 else np.nan
        a1, a2, a3, a4 = A(k-1), A(k-2), A(k-3), A(k-4)
        cj = c[j]
        row.update(
            close_j=cj, a1=a1, a2=a2, a3=a3, a4=a4,
            g1_hl=d*(a1-a3),          # higher-low (L) / lower-high (S), in pts
            g2_peak=d*(cj-a2),        # flip close vs last same-dir extreme
            g3_hh=d*(a2-a4),          # last same-dir extreme vs one before
            g5_range=d*(cj-a3),
            old_len=int(legs["length"][k-1]) if k >= 1 else -1,
            old_max_wave=int(legs["max_wave"][k-1]) if k >= 1 else 0,
            old_n_t3=int(legs["n_t3"][k-1]) if k >= 1 else 0,
            old_n_t2e=int(legs["n_t2e"][k-1]) if k >= 1 else 0,
            old_n_t2l=int(legs["n_t2l"][k-1]) if k >= 1 else 0,
            weak_prev=bool(S["weak"][j-1]),
            bse_prev=int(S["bse"][j-1]),
            armed_e_prev=bool(S["armed_early"][j-1]),
            armed_l_prev=bool(S["armed_late"][j-1]),
            overshoot=abs(cj - S["anchor"][j-1]) - S_PTS,
            bar_range=h[j]-l[j], bar_body=abs(c[j]-o[j]),
            bars_since_old_ext=int(j - legs["ext_bar"][k-1]) if k >= 1 else -1,
        )
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    bars, S, legs = build()
    sl = jan_slice(bars)
    trades = base_trades(sl)
    print(f"Jan-slice base trades: {len(trades)}")

    df = features_for_trades(trades, bars, S, legs)
    lab = pd.read_csv(FEAT)[["entry_time", "label", "certainty", "dir"]]
    m = df.merge(lab, on="entry_time", how="left", suffixes=("", "_lab"))
    unmatched = m["label"].isna().sum()
    print(f"label join: {len(m)} trades, {unmatched} unmatched")
    m.to_csv(os.path.join(OUT, "hunt_C_flip_features.csv"), index=False)

    # quick separation scan on HARD labels
    hard = m[m.certainty == "HARD"]
    skips = hard[hard.label == "SKIP"]
    takes = hard[hard.label == "TAKE"]
    print(f"\nHARD: {len(takes)} TAKE, {len(skips)} SKIP")
    num_cols = ["g1_hl", "g2_peak", "g3_hh", "g5_range", "old_len", "old_max_wave",
                "old_n_t3", "old_n_t2e", "old_n_t2l", "bse_prev", "overshoot",
                "bar_range", "bar_body", "bars_since_old_ext"]
    for cname in num_cols:
        s, t = skips[cname], takes[cname]
        print(f"{cname:>18}: SKIP [{s.min():9.2f},{s.max():9.2f}] med {s.median():8.2f} | "
              f"TAKE [{t.min():9.2f},{t.max():9.2f}] med {t.median():8.2f}", end="")
        # perfect threshold separation?
        if s.max() < t.min() or t.max() < s.min():
            print("  <-- PERFECT SEPARATION", end="")
        print()
    for cname in ["weak_prev", "armed_e_prev", "armed_l_prev"]:
        print(f"{cname:>18}: SKIP {skips[cname].mean():.2f} true-frac | TAKE {takes[cname].mean():.2f}")

    print("\nSKIP rows (HARD):")
    cols = ["entry_time", "dir", "g1_hl", "g2_peak", "g3_hh", "weak_prev", "bse_prev",
            "armed_l_prev", "old_len", "old_n_t2l", "overshoot", "bars_since_old_ext"]
    print(hard[hard.label == "SKIP"][cols].to_string(index=False))
    print("\nSOFT SKIP rows:")
    soft = m[(m.certainty == "SOFT") & (m.label == "SKIP")]
    print(soft[cols].to_string(index=False))


if __name__ == "__main__":
    main()
