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
    """For each base trade, wide feature set at the flip signal bar j = entry_i - 1."""
    rows = []
    time_arr = bars["time"]
    c = bars["close"]; o = bars["open"]; h = bars["high"],
    h = bars["high"]; l = bars["low"]
    st = bars["signal_trade"]
    sess = bars["session_id"]
    first_bar = bars["first_bar"]
    n = bars["n"]
    # session start index per bar
    sess_start = np.zeros(n, np.int64)
    cur = 0
    for i in range(n):
        if first_bar[i]:
            cur = i
        sess_start[i] = cur
    fl_idx = np.flatnonzero(S["flip"])
    t2l_idx = np.flatnonzero(S["fire_late"])
    t2e_idx = np.flatnonzero(S["fire_early"])
    t3_idx = np.flatnonzero(S["t3"])
    mod = ((time_arr - time_arr.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)

    leg_start_close = c[legs["start"]]     # anchor at leg birth = flip close
    # per-leg overshoot at its birth
    leg_overshoot = np.full(len(legs["start"]), np.nan)
    for i in range(1, len(legs["start"])):
        jj = legs["start"][i]
        leg_overshoot[i] = abs(c[jj] - S["anchor"][jj-1]) - S_PTS

    for t in trades:
        j = t["entry_i"] - 1
        d = 1 if t["dir"] > 0 else -1
        k = S["leg"][j]
        def A(i): return legs["fa"][i] if i >= 0 else np.nan
        def SC(i): return leg_start_close[i] if i >= 0 else np.nan
        def LEN(i): return int(legs["length"][i]) if i >= 0 else -1
        a1, a2, a3, a4 = A(k-1), A(k-2), A(k-3), A(k-4)
        s1, s2 = SC(k-1), SC(k-2)
        cj = c[j]
        amp1 = abs(a1 - s1) if k >= 1 else np.nan
        amp2 = abs(a2 - s2) if k >= 2 else np.nan
        width = d * (a2 - a1) if k >= 2 else np.nan   # last same-dir extreme minus last opp extreme
        old_len = LEN(k-1)
        bse_prev = int(S["bse"][j-1])
        ext_bar_old = int(legs["ext_bar"][k-1]) if k >= 1 else -1
        # events since old leg extreme
        t2l_since_ext = int(((t2l_idx > ext_bar_old) & (t2l_idx < j)).sum()) if k >= 1 else 0
        t2e_since_ext = int(((t2e_idx > ext_bar_old) & (t2e_idx < j)).sum()) if k >= 1 else 0
        last_t2l = t2l_idx[t2l_idx < j]
        last_t2e = t2e_idx[t2e_idx < j]
        last_t3 = t3_idx[t3_idx < j]
        row = dict(
            entry_time=t["entry_time"], dir=("L" if d > 0 else "S"), d=d,
            pnl=t["pnl"], leg_id=int(k),
            mod=int(mod[j]), bars_in_sess=int(j - sess_start[j]),
            close_j=cj,
            g1_hl=d*(a1-a3), g2_peak=d*(cj-a2), g3_hh=d*(a2-a4), g5_range=d*(cj-a3),
            prog1=d*(cj-s1), prog2=d*(cj-s2),
            amp1=amp1, amp2=amp2, width=width,
            retr=(amp1/amp2 if (k >= 2 and amp2 > 0) else np.nan),
            old_len=old_len, len2=LEN(k-2), len3=LEN(k-3),
            old_max_wave=int(legs["max_wave"][k-1]) if k >= 1 else 0,
            wave2=int(legs["max_wave"][k-2]) if k >= 2 else 0,
            old_n_t3=int(legs["n_t3"][k-1]) if k >= 1 else 0,
            old_n_t2e=int(legs["n_t2e"][k-1]) if k >= 1 else 0,
            old_n_t2l=int(legs["n_t2l"][k-1]) if k >= 1 else 0,
            weak_prev=bool(S["weak"][j-1]),
            weak_prev2=bool(S["weak"][j-2]),
            bse_prev=bse_prev,
            ext_frac=(bse_prev/old_len if old_len > 0 else np.nan),
            armed_e_prev=bool(S["armed_early"][j-1]),
            armed_l_prev=bool(S["armed_late"][j-1]),
            overshoot=abs(cj - S["anchor"][j-1]) - S_PTS,
            overshoot_prev=leg_overshoot[k-1] if k >= 1 else np.nan,
            bar_range=h[j]-l[j], bar_body=abs(c[j]-o[j]),
            gap_j=abs(o[j]-c[j-1]),
            t2l_since_ext=t2l_since_ext, t2e_since_ext=t2e_since_ext,
            bars_since_t2l=int(j - last_t2l[-1]) if len(last_t2l) else 10**6,
            bars_since_t2e=int(j - last_t2e[-1]) if len(last_t2e) else 10**6,
            bars_since_t3=int(j - last_t3[-1]) if len(last_t3) else 10**6,
            flips_60=int(((fl_idx >= j-60) & (fl_idx < j)).sum()),
            flips_120=int(((fl_idx >= j-120) & (fl_idx < j)).sum()),
            flips_240=int(((fl_idx >= j-240) & (fl_idx < j)).sum()),
            old_cross_sess=bool(sess[legs["start"][k-1]] != sess[j]) if k >= 1 else False,
        )
        rows.append(row)
    return pd.DataFrame(rows)


def search_rules(m):
    """Exhaustive scan: find skip-predicates (1 or 2 conjuncts) that capture all
    HARD SKIPs and zero HARD TAKEs. Predicates may be dir-conditioned."""
    hard = m[m.certainty == "HARD"].copy()
    y = (hard.label == "SKIP").to_numpy()
    feat_cols = [c for c in m.columns if c not in
                 ("entry_time", "dir", "label", "certainty", "dir_lab", "pnl",
                  "close_j", "leg_id")]
    X = {}
    for cname in feat_cols:
        v = hard[cname]
        if v.dtype == bool:
            X[cname + "==T"] = v.to_numpy()
            X[cname + "==F"] = (~v).to_numpy()
        else:
            vals = np.unique(v[np.isfinite(v.astype(float))])
            if len(vals) < 2:
                continue
            # candidate thresholds = midpoints
            mids = (vals[:-1] + vals[1:]) / 2
            if len(mids) > 60:
                mids = np.quantile(mids, np.linspace(0, 1, 60))
            arr = v.astype(float).to_numpy()
            for thr in mids:
                X[f"{cname}<={thr:.3f}"] = arr <= thr
                X[f"{cname}>={thr:.3f}"] = arr >= thr
    # also dir-conditioned atoms
    dl = (hard["d"] == 1).to_numpy()
    keys = list(X.keys())
    for kk in keys:
        X["[L]&" + kk] = dl & X[kk]
        X["[S]&" + kk] = (~dl) & X[kk]

    names = list(X.keys())
    mat = np.array([X[nm] for nm in names])
    nskip = int(y.sum())
    # singles
    hits = []
    for i1, nm in enumerate(names):
        p = mat[i1]
        if (p & y).sum() == nskip and (p & ~y).sum() == 0:
            hits.append(("SINGLE", nm))
    # pairs (OR of two atoms): each atom must not hit any TAKE
    clean = [i for i in range(len(names)) if (mat[i] & ~y).sum() == 0 and (mat[i] & y).sum() > 0]
    for ii, i1 in enumerate(clean):
        for i2 in clean[ii+1:]:
            p = mat[i1] | mat[i2]
            if (p & y).sum() == nskip:
                hits.append(("OR", names[i1], names[i2]))
    # pairs (AND): conjunction covers all skips, no takes
    covers = [i for i in range(len(names)) if (mat[i] & y).sum() == nskip]
    for ii, i1 in enumerate(covers):
        for i2 in covers[ii+1:]:
            p = mat[i1] & mat[i2]
            if (p & y).sum() == nskip and (p & ~y).sum() == 0:
                hits.append(("AND", names[i1], names[i2]))
    return hits


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

    hits = search_rules(m)
    print(f"\nperfect-HARD rules found: {len(hits)}")
    for hh in hits[:200]:
        print("   ", hh)
    with open(os.path.join(OUT, "hunt_C_rulehits.json"), "w") as f:
        json.dump(hits, f, indent=1)


if __name__ == "__main__":
    main()
