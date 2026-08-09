"""R2 construction (bounded, small grid, per diagnose.py's positive finding): require M to stay
beyond ENTRY_LEVEL for CONFIRM_BARS additional bars before committing a NEW entry from flat.
Diagnostic found 77/1978 (3.9%) entries where M reverts by t0+1 cost -$1,160.75 avg vs +$213.28
avg for persistent ones (aggregate -$89,378 for the non-persistent group), with ZERO of the
top-20 winners affected -- unlike R1, this looks right-tail-safe. Reuses the exact substrate/
onelot_exec pattern from R1_ADAPTIVE_EXIT/src/construct.py (imported, not reimplemented)."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "runs", "R1_ADAPTIVE_EXIT", "src"))
import construct as R1  # reuses substrate: bars, T, M, B, tilt_state, entry_blocked_c4, forced_flat_c4, onelot_exec

OUT = os.path.join(ROOT, "runs", "R2_ENTRY_TIMING", "out")
os.makedirs(OUT, exist_ok=True)
n = R1.n; last = R1.last; M = R1.M
ENTRY_LEVEL, EXIT_LEVEL = R1.ENTRY_LEVEL, R1.EXIT_LEVEL
entry_blocked_c4 = R1.entry_blocked_c4; forced_flat_c4 = R1.forced_flat_c4


def build_pos_seq_confirm(confirm_bars):
    """Verbatim one_contract_decisions() control flow. ONLY change: a NEW commitment from flat
    (p==0 -> tgt!=0) is not immediately pend-ed; it must first survive `confirm_bars` additional
    bars where M stays beyond +-ENTRY_LEVEL on the SAME side, checked one bar at a time (if M
    drops back at any point during the confirmation window, the candidate entry is cancelled and
    flat evaluation resumes fresh next bar -- not a fixed-delay entry, a conditional one).
    Reversals (already in a position, flipping side) and exits are UNCHANGED -- confirmation
    applies only to a NEW commitment from flat, matching directive sec12's framing exactly."""
    p = 0; pend = 0
    pos_seq = np.zeros(n, dtype=int)
    armed_side = 0; armed_bars = 0
    n_confirmed = 0; n_cancelled = 0
    for t in range(n):
        if pend != p:
            p = pend
        if last[t] and p != 0:
            p = 0; pend = 0
            pos_seq[t] = p
            armed_side = 0; armed_bars = 0
            continue
        pos_seq[t] = p

        if forced_flat_c4[t]:
            tgt = 0
            armed_side = 0; armed_bars = 0
        elif p == 0:
            if entry_blocked_c4[t]:
                tgt = 0
                armed_side = 0; armed_bars = 0
            else:
                raw = 1 if M[t] >= ENTRY_LEVEL else (-1 if M[t] <= -ENTRY_LEVEL else 0)
                if raw == 0:
                    tgt = 0; armed_side = 0; armed_bars = 0
                elif armed_side == raw:
                    armed_bars += 1
                    if armed_bars >= confirm_bars:
                        tgt = raw; n_confirmed += 1; armed_side = 0; armed_bars = 0
                    else:
                        tgt = 0
                else:
                    if armed_side != 0:
                        n_cancelled += 1
                    armed_side = raw; armed_bars = 0
                    tgt = raw if confirm_bars == 0 else 0
        elif p > 0:
            if M[t] <= -ENTRY_LEVEL and not entry_blocked_c4[t]:
                tgt = -1
            elif M[t] <= EXIT_LEVEL:
                tgt = 0
            else:
                tgt = p
        else:
            if M[t] >= ENTRY_LEVEL and not entry_blocked_c4[t]:
                tgt = 1
            elif M[t] >= -EXIT_LEVEL:
                tgt = 0
            else:
                tgt = p
        pend = tgt
    return pos_seq, n_confirmed, n_cancelled


print("running R2 confirmation-delay grid ...", flush=True)
results = []
for confirm_bars in [1, 2]:
    pos_seq, n_conf, n_cancel = build_pos_seq_confirm(confirm_bars)
    daily_nq, _, _ = R1.onelot_exec(pos_seq, R1.COMM_NQ, R1.PV_NQ, R1.open_, R1.high, R1.low, R1.close)
    daily_mnq, _, _ = R1.onelot_exec(pos_seq, R1.COMM_MNQ, R1.PV_MNQ, R1.o_mnq, R1.h_mnq, R1.l_mnq, R1.c_mnq)
    row_nq = R1.battery_row(f"R2_CONFIRM{confirm_bars}_NQ", daily_nq)
    row_mnq = R1.battery_row(f"R2_CONFIRM{confirm_bars}_MNQ", daily_mnq)
    row_nq.update({"confirm_bars": confirm_bars, "n_confirmed": n_conf, "n_cancelled": n_cancel, "instrument": "NQ"})
    row_mnq.update({"confirm_bars": confirm_bars, "n_confirmed": n_conf, "n_cancelled": n_cancel, "instrument": "MNQ"})
    results.append(row_nq); results.append(row_mnq)
    np.save(os.path.join(OUT, f"pos_CONFIRM{confirm_bars}.npy"), pos_seq)
    daily_nq.to_csv(os.path.join(OUT, f"daily_CONFIRM{confirm_bars}_NQ.csv"), index=False)
    daily_mnq.to_csv(os.path.join(OUT, f"daily_CONFIRM{confirm_bars}_MNQ.csv"), index=False)
    print(f"  [confirm={confirm_bars}] NQ net={row_nq['net']:.2f} sharpe={row_nq['sharpe']:.3f} "
          f"CDaR95={row_nq['CDaR95']:.2f}  MNQ net={row_mnq['net']:.2f} sharpe={row_mnq['sharpe']:.3f} "
          f"n_confirmed={n_conf} n_cancelled={n_cancel}", flush=True)

pd.DataFrame(results).to_csv(os.path.join(OUT, "leaderboard.csv"), index=False)
print("\nCONTROL for reference: NQ net=301915.92 sharpe=1.1131  MNQ net=28587.10 sharpe=1.0534", flush=True)
print("saved leaderboard.csv", flush=True)
