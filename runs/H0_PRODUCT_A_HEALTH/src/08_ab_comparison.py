"""H0 sec12 -- Product A vs Product B current-health comparison (feeds
PRODUCT_A_VS_B_CURRENT_HEALTH.md). Session-level correlation (full + rolling-60), losing-day
conditional probability, drawdown-episode overlap, tail-day overlap, bar-level exposure/signal-
state agreement, and candidate matched-example sessions (A-wins/B-loses, B-wins/A-loses, both-
lose-badly) with the underlying state pulled for mechanistic write-up in the .md."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")

u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"))
u0 = u0.sort_values("t_idx").reset_index(drop=True)

# ============================================================== SESSION-LEVEL DAILY SERIES, BOTH PRODUCTS
daily_A = u0.groupby("sess_date", as_index=False)["bar_pnl_A_dollars"].sum()
daily_B = u0.groupby("sess_date", as_index=False)["bar_pnl_B_nq_dollars"].sum()
daily = daily_A.merge(daily_B, on="sess_date")
daily.columns = ["sess", "net_A", "net_B"]
daily["sess"] = pd.to_datetime(daily["sess"])
daily = daily.sort_values("sess").reset_index(drop=True)
daily["year"] = daily["sess"].dt.year
is_health_map = u0.groupby("sess_date")["is_health_only_bar"].first()  # keyed by datetime.date
daily["is_health_only"] = daily["sess"].dt.date.map(is_health_map)
assert daily["is_health_only"].isna().sum() == 0, "is_health_only join failed to match some sessions"
daily["is_health_only"] = daily["is_health_only"].astype(bool)

print("=" * 90, "\nSEC12a -- SESSION-LEVEL DAILY-RETURN CORRELATION (A vs B-NQ)\n", "=" * 90, sep="")
full_corr = daily["net_A"].corr(daily["net_B"])
canon_corr = daily.loc[~daily["is_health_only"], "net_A"].corr(daily.loc[~daily["is_health_only"], "net_B"])
health_corr = daily.loc[daily["is_health_only"], "net_A"].corr(daily.loc[daily["is_health_only"], "net_B"])
print(f"full-history correlation: {full_corr:.4f}")
print(f"canonical-window correlation: {canon_corr:.4f}")
print(f"health-only-extension correlation: {health_corr:.4f}")

roll60_corr = daily["net_A"].rolling(60).corr(daily["net_B"])
print(f"\nrolling-60 correlation: current={roll60_corr.iloc[-1]:.4f}  "
      f"min={roll60_corr.min():.4f}  max={roll60_corr.max():.4f}  "
      f"mean={roll60_corr.mean():.4f}  std={roll60_corr.std():.4f}")
daily["roll60_corr"] = roll60_corr.to_numpy()
daily.to_csv(os.path.join(OUT, "sec12_daily_AB.csv"), index=False)

# ============================================================== LOSING-DAY CONDITIONAL PROBABILITY
print("\n" + "=" * 90, "\nSEC12b -- LOSING-DAY CONDITIONAL PROBABILITY\n", "=" * 90, sep="")
p_a_loses = (daily["net_A"] < 0).mean()
p_b_loses = (daily["net_B"] < 0).mean()
p_a_loses_given_b_loses = daily.loc[daily["net_B"] < 0, "net_A"].lt(0).mean()
p_b_loses_given_a_loses = daily.loc[daily["net_A"] < 0, "net_B"].lt(0).mean()
p_both_lose = ((daily["net_A"] < 0) & (daily["net_B"] < 0)).mean()
print(f"P(A loses) unconditional = {p_a_loses:.4f}")
print(f"P(B loses) unconditional = {p_b_loses:.4f}")
print(f"P(A loses | B loses) = {p_a_loses_given_b_loses:.4f}  (vs unconditional {p_a_loses:.4f}, "
      f"lift = {p_a_loses_given_b_loses / p_a_loses:.3f}x)")
print(f"P(B loses | A loses) = {p_b_loses_given_a_loses:.4f}  (vs unconditional {p_b_loses:.4f}, "
      f"lift = {p_b_loses_given_a_loses / p_b_loses:.3f}x)")
print(f"P(both lose same session) = {p_both_lose:.4f}  "
      f"(vs independence-implied {p_a_loses*p_b_loses:.4f})")

# ============================================================== DRAWDOWN-EPISODE OVERLAP
print("\n" + "=" * 90, "\nSEC12c -- DRAWDOWN-EPISODE OVERLAP\n", "=" * 90, sep="")


def dd_episodes(net, sess, top_n=5):
    cum = net.cumsum(); peak = cum.cummax(); dd = peak - cum
    uw = dd > 1e-9
    episodes = []
    start = None
    for i, u in enumerate(uw):
        if u and start is None:
            start = i
        if not u and start is not None:
            seg = dd.iloc[start:i]
            episodes.append({"start": sess.iloc[start], "end": sess.iloc[i - 1],
                              "max_dd": float(seg.max()), "start_idx": start, "end_idx": i - 1})
            start = None
    if start is not None:
        seg = dd.iloc[start:]
        episodes.append({"start": sess.iloc[start], "end": sess.iloc[len(dd) - 1],
                          "max_dd": float(seg.max()), "start_idx": start, "end_idx": len(dd) - 1})
    ep_df = pd.DataFrame(episodes).sort_values("max_dd", ascending=False)
    return ep_df.head(top_n)


ep_A = dd_episodes(daily["net_A"], daily["sess"])
ep_B = dd_episodes(daily["net_B"], daily["sess"])
print("Top-5 Product-A drawdown episodes:")
print(ep_A[["start", "end", "max_dd"]].to_string(index=False))
print("\nTop-5 Product-B(NQ) drawdown episodes:")
print(ep_B[["start", "end", "max_dd"]].to_string(index=False))


def overlap_days(a0, a1, b0, b1):
    lo = max(a0, b0); hi = min(a1, b1)
    return max(0, (hi - lo).days + 1) if hi >= lo else 0


overlap_rows = []
for _, ra in ep_A.iterrows():
    for _, rb in ep_B.iterrows():
        ov = overlap_days(ra["start"], ra["end"], rb["start"], rb["end"])
        if ov > 0:
            overlap_rows.append({"A_start": ra["start"], "A_end": ra["end"], "A_maxdd": ra["max_dd"],
                                  "B_start": rb["start"], "B_end": rb["end"], "B_maxdd": rb["max_dd"],
                                  "overlap_days": ov})
overlap_df = pd.DataFrame(overlap_rows)
print(f"\noverlapping drawdown-episode pairs among each product's top-5: {len(overlap_df)}")
if len(overlap_df):
    print(overlap_df.to_string(index=False))
ep_A.to_csv(os.path.join(OUT, "sec12_dd_episodes_A.csv"), index=False)
ep_B.to_csv(os.path.join(OUT, "sec12_dd_episodes_B.csv"), index=False)

# ============================================================== TAIL-DAY OVERLAP
print("\n" + "=" * 90, "\nSEC12d -- TAIL-DAY OVERLAP (top/bottom 20 days each)\n", "=" * 90, sep="")
top20_A = set(daily.nlargest(20, "net_A")["sess"])
top20_B = set(daily.nlargest(20, "net_B")["sess"])
bot20_A = set(daily.nsmallest(20, "net_A")["sess"])
bot20_B = set(daily.nsmallest(20, "net_B")["sess"])
print(f"top-20-day overlap (both products' best days): {len(top20_A & top20_B)} / 20")
print(f"bottom-20-day overlap (both products' worst days): {len(bot20_A & bot20_B)} / 20")
print(f"A-top20 in B-bottom20 (A's best days that were among B's worst): {len(top20_A & bot20_B)}")
print(f"B-top20 in A-bottom20 (B's best days that were among A's worst): {len(top20_B & bot20_A)}")
print(f"shared top-20 dates: {sorted(d.date() for d in (top20_A & top20_B))}")
print(f"shared bottom-20 dates: {sorted(d.date() for d in (bot20_A & bot20_B))}")

# ============================================================== BAR-LEVEL EXPOSURE/SIGNAL-STATE OVERLAP
print("\n" + "=" * 90, "\nSEC12e -- BAR-LEVEL sign(target_exposure_A) vs position_B AGREEMENT\n", "=" * 90, sep="")
sign_A = np.sign(u0["target_exposure_A"].to_numpy())
pos_B = u0["position_B"].to_numpy()
both_nonzero = (sign_A != 0) & (pos_B != 0)
n_both_nonzero = int(both_nonzero.sum())
agree = (sign_A[both_nonzero] == pos_B[both_nonzero]).mean()
disagree_active = (sign_A[both_nonzero] == -pos_B[both_nonzero]).mean()
print(f"bars where BOTH have a nonzero position: {n_both_nonzero} ({100*n_both_nonzero/len(u0):.1f}% of all bars)")
print(f"  agreement rate (same sign) among those bars: {agree:.4f}")
print(f"  active-disagreement rate (opposite sign) among those bars: {disagree_active:.4f}")
either_nonzero = (sign_A != 0) | (pos_B != 0)
both_flat = (sign_A == 0) & (pos_B == 0)
print(f"\nbars where BOTH are flat: {both_flat.sum()} ({100*both_flat.mean():.1f}% of all bars)")
a_only = (sign_A != 0) & (pos_B == 0)
b_only = (sign_A == 0) & (pos_B != 0)
print(f"bars where ONLY A has a position: {a_only.sum()} ({100*a_only.mean():.1f}%)")
print(f"bars where ONLY B has a position: {b_only.sum()} ({100*b_only.mean():.1f}%)")

overlap_summary = {
    "full_corr": float(full_corr), "canon_corr": float(canon_corr), "health_corr": float(health_corr),
    "roll60_corr_current": float(roll60_corr.iloc[-1]), "roll60_corr_min": float(roll60_corr.min()),
    "roll60_corr_max": float(roll60_corr.max()), "roll60_corr_mean": float(roll60_corr.mean()),
    "p_a_loses": float(p_a_loses), "p_b_loses": float(p_b_loses),
    "p_a_loses_given_b_loses": float(p_a_loses_given_b_loses),
    "p_b_loses_given_a_loses": float(p_b_loses_given_a_loses),
    "p_both_lose": float(p_both_lose),
    "top20_overlap": len(top20_A & top20_B), "bottom20_overlap": len(bot20_A & bot20_B),
    "n_dd_episode_overlaps": len(overlap_df),
    "n_both_nonzero_bars": n_both_nonzero, "pct_both_nonzero": float(100 * n_both_nonzero / len(u0)),
    "agreement_rate_both_nonzero": float(agree), "active_disagreement_rate_both_nonzero": float(disagree_active),
    "pct_both_flat": float(100 * both_flat.mean()), "pct_a_only": float(100 * a_only.mean()),
    "pct_b_only": float(100 * b_only.mean()),
}
json.dump(overlap_summary, open(os.path.join(OUT, "sec12_ab_overlap_summary.json"), "w"), indent=2)

# ============================================================== CANDIDATE MATCHED EXAMPLE SESSIONS
print("\n" + "=" * 90, "\nSEC12f -- CANDIDATE MATCHED-EXAMPLE SESSIONS\n", "=" * 90, sep="")
daily["diff_AB"] = daily["net_A"] - daily["net_B"]
a_wins_b_loses = daily[(daily["net_A"] > 500) & (daily["net_B"] < -300)].sort_values("diff_AB", ascending=False)
b_wins_a_loses = daily[(daily["net_B"] > 500) & (daily["net_A"] < -300)].sort_values("diff_AB")
both_lose_badly = daily[(daily["net_A"] < -500) & (daily["net_B"] < -500)].copy()
both_lose_badly["combined"] = both_lose_badly["net_A"] + both_lose_badly["net_B"]
both_lose_badly = both_lose_badly.sort_values("combined")

print(f"\nA-wins-big/B-loses candidates (n={len(a_wins_b_loses)}), top 5:")
print(a_wins_b_loses.head(5)[["sess", "net_A", "net_B"]].to_string(index=False))
print(f"\nB-wins-big/A-loses candidates (n={len(b_wins_a_loses)}), top 5:")
print(b_wins_a_loses.head(5)[["sess", "net_A", "net_B"]].to_string(index=False))
print(f"\nBoth-lose-badly candidates (n={len(both_lose_badly)}), top 5:")
print(both_lose_badly.head(5)[["sess", "net_A", "net_B"]].to_string(index=False))

# pull bar-level state context for the top candidates from each bucket
example_dates = list(a_wins_b_loses.head(3)["sess"]) + list(b_wins_a_loses.head(3)["sess"]) + \
                 list(both_lose_badly.head(3)["sess"])
example_dates = [pd.Timestamp(d).date() for d in example_dates]

state_cols = ["sess_date", "T", "HTF_tilt_state", "B", "M", "M_A_raw", "target_exposure_A", "position_B",
              "action_A", "action_B", "bar_pnl_A_dollars", "bar_pnl_B_nq_dollars"]
state_ctx = u0[u0["sess_date"].isin(example_dates)][state_cols]
sess_state_summary = state_ctx.groupby("sess_date").agg(
    T_min=("T", "min"), T_max=("T", "max"), T_mean=("T", "mean"),
    HTF_tilt_mode=("HTF_tilt_state", lambda x: x.mode().iloc[0] if len(x.mode()) else np.nan),
    B_frac_active=("B", lambda x: float((x != 0).mean())),
    B_mean=("B", "mean"),
    M_mean=("M", "mean"), M_min=("M", "min"), M_max=("M", "max"),
    max_abs_target_A=("target_exposure_A", lambda x: int(x.abs().max())),
    n_flip_A=("action_A", lambda x: int((x == "FLIP").sum())),
    n_reversal_B=("action_B", lambda x: int((x == "REVERSAL").sum())),
    net_A=("bar_pnl_A_dollars", "sum"), net_B=("bar_pnl_B_nq_dollars", "sum"),
)
print("\nstate context for candidate matched-example sessions:")
print(sess_state_summary.round(3).to_string())
sess_state_summary.to_csv(os.path.join(OUT, "sec12f_matched_example_state.csv"))
a_wins_b_loses.to_csv(os.path.join(OUT, "sec12f_a_wins_b_loses.csv"), index=False)
b_wins_a_loses.to_csv(os.path.join(OUT, "sec12f_b_wins_a_loses.csv"), index=False)
both_lose_badly.to_csv(os.path.join(OUT, "sec12f_both_lose_badly.csv"), index=False)

print("\n[H0] sec12 A-vs-B comparison complete.")
