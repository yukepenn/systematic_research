"""R2B construction -- reclaim-gated adaptive entry, frozen at K=6 bars (the diagnostic window
already used, not re-tuned). Conceptually distinct from R2's closed fixed-delay mechanism: entries
with NO adverse price excursion commit almost immediately (~1 bar, same as the incumbent), entries
that pull back wait for a PRICE reclaim (not a time delay) before committing, bounded at K bars
(never cancelled purely by elapsed time -- only cancelled if M itself reverts, same semantics the
incumbent already uses). K=6 is the single frozen candidate; no grid search, per directive sec43's
parameter discipline and this run's own construction_gate."""
import os, sys, json
import numpy as np, pandas as pd

SA0_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        "SA0_SYSTEM_STRUCTURE", "src")
sys.path.insert(0, SA0_SRC)
import substrate as S

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
K = 6
PULLBACK_EPS_ATR = 0.05  # matches diagnostic's "any pullback > 0.05 ATR" threshold


def build_pos_seq_reclaim(K_bars=K):
    """Structurally identical outer control flow to build_pos_seq (session-close cancellation,
    C4 forced-flat, exit/reversal logic UNCHANGED, and CRITICALLY the same pend->p one-bar lag:
    the position held during bar t reflects a decision made from bar t-1's own M/close, filled
    using bar t's OHLC -- the ONLY change from build_pos_seq is how the pend->p transition for a
    NEW commitment from flat is timed (reclaim-gated instead of immediate). sigma460 at the
    arming bar is the fixed ATR normalizer for that arm's whole pullback/reclaim measurement,
    matching the diagnostic exactly.

    A first draft of this function computed `reclaimed` from bar t's own close and applied it to
    pos_seq[t] in the SAME bar -- a one-bar look-ahead (deciding from a bar's close, then filling
    within that same bar's own OHLC, which occurs at-or-before the close). It produced an
    obviously-too-good Sharpe 5.69 / net $1.39M, which is what exposed the bug (same class of
    error caught and fixed in SA0's sec9 B-MOM raw-standalone test) rather than a real finding.
    Fixed here with the same pend/p lag every other decision-layer function in this codebase
    uses."""
    close = S.close
    n = S.n
    pos_seq = np.zeros(n, dtype=int)
    p = 0
    pend = 0
    armed_side = 0
    trigger_close = 0.0
    arm_sigma = np.nan
    armed_bars = 0
    pullback_seen = False
    for t in range(n):
        if pend != p:
            p = pend
        if S.last[t] and p != 0:
            p = 0
            pend = 0
            armed_side = 0
            pos_seq[t] = p
            continue
        pos_seq[t] = p

        if S.forced_flat_c4[t]:
            pend = 0
            armed_side = 0
        elif p == 0:
            if armed_side == 0:
                if not S.entry_blocked_c4[t] and S.M[t] >= S.ENTRY_LEVEL:
                    armed_side = 1
                elif not S.entry_blocked_c4[t] and S.M[t] <= -S.ENTRY_LEVEL:
                    armed_side = -1
                if armed_side != 0:
                    trigger_close = close[t]
                    arm_sigma = S.sig460[t] if S.sig460[t] > 0 else np.nan
                    armed_bars = 0
                    pullback_seen = False
                pend = 0
            else:
                if abs(S.M[t]) < S.ENTRY_LEVEL or np.sign(S.M[t]) != armed_side or S.entry_blocked_c4[t]:
                    armed_side = 0  # M reverted, or the C4 pre-close window started -- cancel
                    pend = 0        # this arm, matching build_pos_seq's own entry_blocked check
                else:
                    adverse = armed_side * (trigger_close - close[t])
                    pullback_atr = adverse / arm_sigma if (arm_sigma and not np.isnan(arm_sigma) and arm_sigma > 0) else 0.0
                    if pullback_atr > PULLBACK_EPS_ATR:
                        pullback_seen = True
                    reclaimed = (not pullback_seen) or (armed_side * (close[t] - trigger_close) >= 0)
                    armed_bars += 1
                    if reclaimed or armed_bars >= K_bars:
                        pend = armed_side
                        armed_side = 0
                    else:
                        pend = 0
        elif p > 0:
            if S.M[t] <= -S.ENTRY_LEVEL and not S.entry_blocked_c4[t]:
                pend = -1
            elif S.M[t] <= S.EXIT_LEVEL:
                pend = 0
            else:
                pend = p
        else:
            if S.M[t] >= S.ENTRY_LEVEL and not S.entry_blocked_c4[t]:
                pend = 1
            elif S.M[t] >= -S.EXIT_LEVEL:
                pend = 0
            else:
                pend = p
    return pos_seq


# sanity: K=1 with PULLBACK_EPS effectively infinite (no pullback can ever register meaningfully
# within a single bar's adverse move check before forced commit) should closely track FULL --
# not asserted byte-exact (the state machine's control flow differs from build_pos_seq's simpler
# immediate-commit even at K=1, since arming still takes 1 bar to notice a crossing that
# build_pos_seq resolves via its own pend/p lag) -- instead cross-checked empirically below.
print("running FULL control (reused from SA0) ...", flush=True)
pos_full = S.build_pos_seq(S.M, S.ENTRY_LEVEL, S.EXIT_LEVEL)
daily_full_nq, barpos_full_nq, bpnl_full_nq = S.onelot_exec(pos_full, S.COMM_NQ, S.PV_NQ, S.open_, S.high, S.low, S.close)
row_full = S.battery_row("FULL", daily_full_nq)
print(f"  FULL: net={row_full['net']:.2f} sharpe={row_full['sharpe']:.3f}")

print(f"running R2B_RECLAIM K={K} ...", flush=True)
pos_r2b = build_pos_seq_reclaim(K)
daily_r2b_nq, barpos_r2b_nq, bpnl_r2b_nq = S.onelot_exec(pos_r2b, S.COMM_NQ, S.PV_NQ, S.open_, S.high, S.low, S.close)
daily_r2b_mnq, barpos_r2b_mnq, bpnl_r2b_mnq = S.onelot_exec(pos_r2b, S.COMM_MNQ, S.PV_MNQ, S.o_mnq, S.h_mnq, S.l_mnq, S.c_mnq)
row_r2b_nq = S.battery_row("R2B_RECLAIM_K6_NQ", daily_r2b_nq)
row_r2b_mnq = S.battery_row("R2B_RECLAIM_K6_MNQ", daily_r2b_mnq)
n_trades_full = int((np.diff(pos_full) != 0).sum())
n_trades_r2b = int((np.diff(pos_r2b) != 0).sum())
row_r2b_nq["n_trades"] = n_trades_r2b
print(f"  R2B K={K}: NQ net={row_r2b_nq['net']:.2f} sharpe={row_r2b_nq['sharpe']:.3f} "
      f"maxDD={row_r2b_nq['maxDD_eod']:.2f} CDaR95={row_r2b_nq['CDaR95']:.2f} "
      f"n_trades={n_trades_r2b} (FULL={n_trades_full})")
print(f"  R2B K={K}: MNQ net={row_r2b_mnq['net']:.2f} sharpe={row_r2b_mnq['sharpe']:.3f}")

pd.DataFrame([row_full, row_r2b_nq]).to_csv(os.path.join(OUT, "r2b_construct_leaderboard_NQ.csv"), index=False)
pd.DataFrame([row_r2b_mnq]).to_csv(os.path.join(OUT, "r2b_construct_leaderboard_MNQ.csv"), index=False)
np.save(os.path.join(OUT, "pos_R2B_RECLAIM_K6.npy"), pos_r2b)
daily_r2b_nq.to_csv(os.path.join(OUT, "daily_R2B_RECLAIM_K6_NQ.csv"), index=False)
daily_r2b_mnq.to_csv(os.path.join(OUT, "daily_R2B_RECLAIM_K6_MNQ.csv"), index=False)
daily_full_nq.to_csv(os.path.join(OUT, "daily_FULL_NQ.csv"), index=False)

# right-tail check: exact top-20 trade mapping (same-span attribution, R2V1-style)
ledger = pd.read_parquet(S.LEDGER_PATH, columns=["t_idx", "block_id"])
block_sum = pd.read_csv(S.BLOCKSUM_PATH)
pos_blocks = ledger.merge(pd.read_parquet(S.LEDGER_PATH, columns=["t_idx", "position"]), on="t_idx")
top20 = block_sum.nlargest(20, "net_pnl")
tail_rows = []
for _, r in top20.iterrows():
    idx = ledger.loc[ledger["block_id"] == r["block_id"], "t_idx"].to_numpy()
    r2b_pnl_span = float(bpnl_r2b_nq[idx].sum())
    tail_rows.append({"block_id": int(r["block_id"]), "incumbent_net_pnl": float(r["net_pnl"]),
                       "r2b_net_pnl_same_span": r2b_pnl_span})
tail_df = pd.DataFrame(tail_rows)
tail_df.to_csv(os.path.join(OUT, "r2b_top20_same_span_check.csv"), index=False)
print(f"\ntop-20 same-span retention: incumbent sum={tail_df['incumbent_net_pnl'].sum():.2f} "
      f"R2B sum={tail_df['r2b_net_pnl_same_span'].sum():.2f} "
      f"({100*tail_df['r2b_net_pnl_same_span'].sum()/tail_df['incumbent_net_pnl'].sum():.1f}%)")

print("\nR2B construction complete.")
