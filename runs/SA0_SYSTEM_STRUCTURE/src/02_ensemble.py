"""SA0 sec7 -- Solar13 ensemble science. Diagnostic only (directive sec7 explicitly forbids
re-optimizing 13 individual weights). Reuses the repo's own participation_ratio convention
(runs/W19D7_REGIME_2026/src/structure.py) for methodological consistency."""
import os, sys, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import substrate as S

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
PEND = S.PEND  # (n, 13), VMS = 6..30 step 2
VMS = S.VMS
n = S.n


def participation_ratio(X):
    X = X[:, np.std(X, axis=0) > 0]
    if X.shape[1] < 2:
        return 1.0
    R = np.corrcoef(X, rowvar=False)
    R = np.nan_to_num(R, nan=0.0)
    ev = np.linalg.eigvalsh(R)
    ev = np.clip(ev, 0, None)
    return float(ev.sum() ** 2 / (ev ** 2).sum())


print("=" * 90, "\nPAIRWISE MEMBER AGREEMENT / DIVERSITY\n", "=" * 90, sep="")
sgn = np.sign(PEND)
corr = np.corrcoef(PEND, rowvar=False)
agree = np.zeros((13, 13))
for i in range(13):
    for j in range(13):
        agree[i, j] = float((sgn[:, i] == sgn[:, j]).mean())
corr_df = pd.DataFrame(corr, index=VMS, columns=VMS)
agree_df = pd.DataFrame(agree, index=VMS, columns=VMS)
corr_df.to_csv(os.path.join(OUT, "sec7_member_correlation_matrix.csv"))
agree_df.to_csv(os.path.join(OUT, "sec7_member_sign_agreement_matrix.csv"))

offdiag_corr = corr[np.triu_indices(13, k=1)]
offdiag_agree = agree[np.triu_indices(13, k=1)]
pr_full = participation_ratio(PEND)
print(f"mean pairwise correlation (off-diag) = {offdiag_corr.mean():.4f}  "
      f"[min {offdiag_corr.min():.4f}, max {offdiag_corr.max():.4f}]")
print(f"mean pairwise sign agreement (off-diag) = {offdiag_agree.mean():.4f}")
print(f"participation ratio (full history) = {pr_full:.3f} of 13 (1=collapsed, 13=fully diverse)")

# adjacent-VM pairs (e.g. VM6 vs VM8) vs far pairs (VM6 vs VM30) -- redundancy is structural if
# adjacent members are much more correlated than far members
adj_corr = [corr[i, i + 1] for i in range(12)]
far_corr = corr[0, 12]
print(f"adjacent-VM pairwise correlation: mean={np.mean(adj_corr):.4f} "
      f"(range {min(adj_corr):.4f}-{max(adj_corr):.4f})  vs VM6-vs-VM30 (farthest) = {far_corr:.4f}")

print("\n" + "=" * 90, "\nVOTE DISPERSION AROUND ENTRIES / EXITS / GIANT WINNERS / LOSERS\n", "=" * 90, sep="")
ledger = pd.read_parquet(S.LEDGER_PATH)
block_sum = pd.read_csv(S.BLOCKSUM_PATH)

# entry-bar vote dispersion: first bar of each nonzero block
entry_rows = ledger[(ledger["age_bars"] == 1) & (ledger["position"] != 0)]
print(f"n entries with vote_dispersion recorded: {len(entry_rows)}")
print(f"mean |vote_dispersion| at entry = {entry_rows['vote_dispersion'].abs().mean():.3f} of 13  "
      f"(all-bar mean: {ledger['vote_dispersion'].abs().mean():.3f})")

merged = block_sum.merge(
    entry_rows[["block_id", "vote_dispersion", "n_bullish", "n_bearish"]], on="block_id", how="left")
top20 = merged.nlargest(20, "net_pnl")
bot20 = merged.nsmallest(20, "net_pnl")
disp_summary = {
    "all_blocks_mean_abs_dispersion_at_entry": float(merged["vote_dispersion"].abs().mean()),
    "top20_winners_mean_abs_dispersion_at_entry": float(top20["vote_dispersion"].abs().mean()),
    "bottom20_losers_mean_abs_dispersion_at_entry": float(bot20["vote_dispersion"].abs().mean()),
    "top20_winners_mean_dispersion_signed_matches_side_pct": float(
        (np.sign(top20["vote_dispersion"]) == np.sign(top20["side"])).mean() * 100),
    "bottom20_losers_mean_dispersion_signed_matches_side_pct": float(
        (np.sign(bot20["vote_dispersion"]) == np.sign(bot20["side"])).mean() * 100),
}
print(json.dumps(disp_summary, indent=2))
json.dump(disp_summary, open(os.path.join(OUT, "sec7_vote_dispersion_summary.json"), "w"), indent=2)
merged.to_csv(os.path.join(OUT, "sec7_block_entry_dispersion.csv"), index=False)

print("\n" + "=" * 90, "\nLEAVE-ONE-MEMBER-OUT CONTRIBUTION (explanatory, NOT 13 new weights)\n", "=" * 90, sep="")
loo_rows = []
for i, vm in enumerate(VMS):
    keep = [j for j in range(13) if j != i]
    T_loo = S.rha(PEND[:, keep].mean(axis=1) * 10)
    T_loo = np.clip(T_loo, -10, 10).astype(int)
    m_arr = np.where((T_loo != 0) & (S.tilt_state != 0) & (np.sign(T_loo) == S.tilt_state), S.TILTMULT, 1.0)
    Tp_loo = np.clip(S.rha(T_loo * m_arr * S.TILTRESCALE), -13, 13)
    M_loo = S.WSOLAR * Tp_loo + S.WBMOM * np.asarray(S.B)
    pos_loo = S.build_pos_seq(M_loo, S.ENTRY_LEVEL, S.EXIT_LEVEL)
    daily, _, _ = S.onelot_exec(pos_loo, S.COMM_NQ, S.PV_NQ, S.open_, S.high, S.low, S.close)
    row = S.battery_row(f"LOO_VM{vm}", daily)
    row["vm_removed"] = vm
    row["net_delta_vs_FULL"] = row["net"] - 301915.92
    loo_rows.append(row)
    print(f"  remove VM{vm}: net={row['net']:.2f} (delta {row['net_delta_vs_FULL']:+.2f}) "
          f"sharpe={row['sharpe']:.3f}", flush=True)
pd.DataFrame(loo_rows).to_csv(os.path.join(OUT, "sec7_leave_one_member_out.csv"), index=False)

print("\n" + "=" * 90, "\nFAST / MIDDLE / SLOW TERCILE SUB-ENSEMBLES\n", "=" * 90, sep="")
FAST = [0, 1, 2, 3]      # VM 6,8,10,12
MID = [4, 5, 6, 7, 8]    # VM 14,16,18,20,22
SLOW = [9, 10, 11, 12]   # VM 24,26,28,30
tercile_rows = []
for label, idxs in [("FAST", FAST), ("MID", MID), ("SLOW", SLOW)]:
    T_sub = S.rha(PEND[:, idxs].mean(axis=1) * 10)
    T_sub = np.clip(T_sub, -10, 10).astype(int)
    m_arr = np.where((T_sub != 0) & (S.tilt_state != 0) & (np.sign(T_sub) == S.tilt_state), S.TILTMULT, 1.0)
    Tp_sub = np.clip(S.rha(T_sub * m_arr * S.TILTRESCALE), -13, 13)
    M_sub = S.WSOLAR * Tp_sub + S.WBMOM * np.asarray(S.B)
    pos_sub = S.build_pos_seq(M_sub, S.ENTRY_LEVEL, S.EXIT_LEVEL)
    daily, barpos, bpnl = S.onelot_exec(pos_sub, S.COMM_NQ, S.PV_NQ, S.open_, S.high, S.low, S.close)
    row = S.battery_row(f"TERCILE_{label}", daily)
    row["n_members"] = len(idxs)
    row["n_trades"] = int((np.diff(pos_sub) != 0).sum())
    tercile_rows.append(row)
    print(f"  {label} ({len(idxs)} members): net={row['net']:.2f} sharpe={row['sharpe']:.3f} "
          f"n_trades={row['n_trades']}", flush=True)
pd.DataFrame(tercile_rows).to_csv(os.path.join(OUT, "sec7_tercile_subensembles.csv"), index=False)

print("\nSA0 sec7 complete.")
