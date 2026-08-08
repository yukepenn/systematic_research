# W8-4 ROLE-B feasibility: entry-time micro-state vs Solar (E10 master v2) per-trade P&L
# MEASUREMENT only. Frozen spec: research/scalping_lab/specs/W8_programs_final.md (cf7041f).
# Seed 20260808, 1000 bootstrap reps, day-clustered CIs. Dev guard: no data >= 2026-06-01.
import os, sys, glob
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
FILLS = os.path.join(ROOT, "runs", "E10MASTER_V2", "out", "e10m_v2_fills.csv")
DAILY = os.path.join(ROOT, "runs", "E10MASTER_V2", "out", "daily_v1_v2.csv")
SH = os.path.join(ROOT, "research", "scalping_lab", "substrate", "sechilo", "NQ")
GR = os.path.join(ROOT, "research", "scalping_lab", "substrate", "grid1s", "NQ")
OUTD = os.path.join(ROOT, "research", "scalping_lab", "artifacts", "w8_roleb")
os.makedirs(OUTD, exist_ok=True)
SEED, NBOOT = 20260808, 1000
DEV_CUT = pd.Timestamp("2026-06-01")   # hard guard: never use data at/after this
TICK_PT = 0.25                          # 1 NQ tick = 0.25 pts
NQ_TICK_USD = 5.0                       # 1 NQ tick on 1-NQ-equivalent (10 MNQ) = $5

log_f = open(os.path.join(OUTD, "stdout.txt"), "w", encoding="utf-8")
def P(*a):
    s = " ".join(str(x) for x in a)
    print(s); log_f.write(s + "\n"); log_f.flush()

# ---------------- 1. fills -> flat-to-flat round trips (position tracking, signed qty) ----
f = pd.read_csv(FILLS, skiprows=1)
f["time"] = pd.to_datetime(f["time"])
n_dropped_dev = int((f["time"] >= DEV_CUT).sum())
f = f[f["time"] < DEV_CUT].reset_index(drop=True)
sd = {"Buy": 1, "BuyToCover": 1, "Sell": -1, "SellShort": -1}
f["sq"] = f["qty"] * f["order_action"].map(sd)
f["pos"] = f["sq"].cumsum()
# session tag = END date (18:00 ET open -> next-day 17:00 ET close)
f["sess"] = pd.to_datetime(np.where(f["time"].dt.hour >= 18,
                                    (f["time"] + pd.Timedelta(days=1)).dt.date,
                                    f["time"].dt.date))
f = f[f["sess"] < DEV_CUT].reset_index(drop=True)   # drop the truncated 2026-06-01 session
prev = f["pos"].shift(1).fillna(0).astype(int)
assert not (((np.sign(prev) != 0) & (np.sign(f["pos"]) != 0) &
             (np.sign(prev) != np.sign(f["pos"])))).any(), "reversal fills present"
f["epi_id"] = ((prev == 0) & (f["pos"] != 0)).cumsum()
P(f"[FACT] fills loaded: {len(f)} (dropped {n_dropped_dev} fills at/after {DEV_CUT.date()} guard)")

# cash-flow P&L per episode: sell = +price*qty, buy = -price*qty ; MNQ $2/pt
f["cash_pts"] = -np.sign(f["sq"]) * f["price"] * f["qty"]     # MNQ-contract-points
g = f.groupby("epi_id")
tr = pd.DataFrame({
    "sess": g["sess"].first(), "entry_time": g["time"].first(), "exit_time": g["time"].last(),
    "side": g["sq"].first().apply(np.sign).astype(int), "n_fills": g.size(),
    "max_pos_mnq": g["pos"].apply(lambda s: s.abs().max()),
    "end_pos": g["pos"].last(), "cash_pts": g["cash_pts"].sum(), "comm_usd": g["commission"].sum(),
})
assert (tr["sess"] == g["sess"].last()).all(), "episode spans session boundary"
open_epis = tr[tr["end_pos"] != 0]
P(f"[FACT] flat-to-flat episodes: {len(tr)}; open (unclosed) at data end: {len(open_epis)} -> excluded")
tr = tr[tr["end_pos"] == 0].copy()
tr["pnl_usd"] = 2.0 * tr["cash_pts"] - tr["comm_usd"]
tr["pnl_t"] = tr["pnl_usd"] / NQ_TICK_USD          # NQ ticks per 1-NQ-equivalent (qty/10)
tr["win"] = (tr["pnl_t"] > 0).astype(int)
tr["dur_min"] = (tr["exit_time"] - tr["entry_time"]).dt.total_seconds() / 60

# ---------------- 2. VERIFY vs daily_v1_v2.csv net_v2 -------------------------------------
daily = pd.read_csv(DAILY)
daily["sess"] = pd.to_datetime(daily["sess"])
daily = daily[daily["sess"] <= pd.Timestamp("2026-05-31")]
recon = tr.groupby("sess")["pnl_usd"].sum().rename("recon_usd")
cmp_all = daily.set_index("sess")[["net_v2"]].join(recon, how="outer").fillna(0.0)
cmp_all["diff"] = cmp_all["recon_usd"] - cmp_all["net_v2"]
P(f"[FACT] all-session verification vs net_v2 ({len(cmp_all)} sessions <= 2026-05-31):")
P(f"  sum recon ${cmp_all['recon_usd'].sum():,.2f} vs sum net_v2 ${cmp_all['net_v2'].sum():,.2f}"
  f" | max |diff| ${cmp_all['diff'].abs().max():.4f} | sessions |diff|>$1: {(cmp_all['diff'].abs()>1).sum()}")
P("[FACT] episodes spanning a session boundary: 0 (asserted) -> no position-carry mismatch to quantify")

sessions37 = sorted(os.path.basename(p)[1:-8] for p in glob.glob(os.path.join(SH, "s*.parquet")))
sess37 = pd.to_datetime(pd.Series(sessions37), format="%Y%m%d")
assert (sess37 < DEV_CUT).all()
P(f"[FACT] substrate sessions: {len(sess37)} ({sess37.min().date()} .. {sess37.max().date()})")
cmp37 = cmp_all.loc[cmp_all.index.isin(sess37)].copy()
P("[FACT] per-session comparison on the 37 substrate dates (recon vs net_v2, $):")
P(cmp37.round(2).to_string())
cmp37.to_csv(os.path.join(OUTD, "verify_sessions37.csv"))
cmp_all.to_csv(os.path.join(OUTD, "verify_sessions_all.csv"))

tr37 = tr[tr["sess"].isin(sess37)].copy().reset_index(drop=True)
P(f"[FACT] trades on the 37 substrate sessions: {len(tr37)} "
  f"(mean {len(tr37)/len(sess37):.2f}/session) | mean pnl {tr37['pnl_t'].mean():+.2f}t | "
  f"win rate {tr37['win'].mean():.3f} | median dur {tr37['dur_min'].median():.0f} min")

# ---------------- 3. entry-minute micro features (grid1s + sechilo) -----------------------
# Sampled at the entry minute's :00 second; rolling windows use the 60 STRICTLY PRIOR
# seconds (rows t-60..t-1), so nothing from the entry-stamp second leaks in.
feat_rows = []
for tag, d in zip(sessions37, sess37):
    gsub = pd.read_parquet(os.path.join(GR, "s" + tag + ".parquet"))
    ssub = pd.read_parquet(os.path.join(SH, "s" + tag + ".parquet"))
    gsub["time"] = pd.to_datetime(gsub["time"]); ssub["time"] = pd.to_datetime(ssub["time"])
    m = gsub.merge(ssub, on="time", how="left")
    m["mid_last"] = m["mid_last"].ffill()
    m = m[m["mid_last"].notna()].reset_index(drop=True)
    m["mid_high"] = m["mid_high"].fillna(m["mid_last"])
    m["mid_low"] = m["mid_low"].fillna(m["mid_last"])
    ml = m["mid_last"]                                     # NQ ticks (price*4)
    dmid = ml.diff()
    F = pd.DataFrame({"time": m["time"]})
    F["spread60"] = m["spread_t"].rolling(60).mean()       # ticks
    F["sflow60"] = m["sflow"].rolling(60).sum()            # signed contracts
    F["upd60"] = (m["bid_upd"] + m["ask_upd"]).rolling(60).sum()
    F["rv60"] = dmid.rolling(60).std()                     # ticks (1s diffs)
    tv60 = dmid.abs().rolling(60).sum()
    F["eff60"] = ml.diff(60).abs() / tv60.where(tv60 > 0)
    shi = m["mid_high"].cummax(); slo = m["mid_low"].cummin()
    F["dist_hi"] = shi - ml                                # ticks below running session high
    F["dist_lo"] = ml - slo                                # ticks above running session low
    ent = tr37[tr37["sess"] == d]
    if len(ent) == 0: continue
    times = F["time"].values
    for _, r in ent.iterrows():
        et = np.datetime64(r["entry_time"])
        j = int(np.searchsorted(times, et))
        exact = j < len(times) and times[j] == et
        row = {"epi_id": r.name, "sess": d, "entry_time": r["entry_time"], "exact_grid": exact}
        k = j - 1                                          # strictly prior second
        if exact and k >= 60:
            for c in ["spread60", "sflow60", "upd60", "rv60", "eff60", "dist_hi", "dist_lo"]:
                row[c] = float(F[c].iloc[k])
        else:
            for c in ["spread60", "sflow60", "upd60", "rv60", "eff60", "dist_hi", "dist_lo"]:
                row[c] = np.nan
        so = (d - pd.Timedelta(days=1)) + pd.Timedelta(hours=18)   # session open 18:00 ET
        row["mins_open"] = (r["entry_time"] - so).total_seconds() / 60
        feat_rows.append(row)
FE = pd.DataFrame(feat_rows).set_index("epi_id")
tf = tr37.join(FE.drop(columns=["sess", "entry_time"]), how="left")
tf["sflow60_signed"] = tf["side"] * tf["sflow60"]          # SUPPLEMENTARY (not in frozen list)
FEATS = ["spread60", "sflow60", "upd60", "rv60", "eff60", "dist_hi", "dist_lo", "mins_open"]
n_nan = int(tf[FEATS].isna().any(axis=1).sum())
P(f"[FACT] entries matched to grid :00 second exactly: {int(tf['exact_grid'].sum())}/{len(tf)}; "
  f"trades with any missing feature (first-60s entries / off-grid): {n_nan} -> dropped from feature analyses")
tf.to_csv(os.path.join(OUTD, "trades_features.csv"))
tv = tf.dropna(subset=FEATS).copy()
P(f"[FACT] feature sample: {len(tv)} trades, {tv['sess'].nunique()} sessions | "
  f"mean pnl {tv['pnl_t'].mean():+.2f}t | win rate {tv['win'].mean():.3f}")

# ---------------- 4. day-clustered bootstrap helpers --------------------------------------
rng = np.random.default_rng(SEED)
sess_list = np.array(sorted(tv["sess"].unique()))
sess_groups = {s: tv.index[tv["sess"] == s].values for s in sess_list}

def cluster_boot(stat_fn, nboot=NBOOT):
    """stat_fn(df) -> scalar or vector; resample sessions with replacement."""
    out = []
    for _ in range(nboot):
        pick = rng.choice(sess_list, size=len(sess_list), replace=True)
        idx = np.concatenate([sess_groups[s] for s in pick])
        out.append(stat_fn(tv.loc[idx]))
    a = np.array(out, dtype=float)
    return np.nanpercentile(a, 2.5, axis=0), np.nanpercentile(a, 97.5, axis=0)

# ---------------- 5. quintile tables ------------------------------------------------------
qrows = []
P("\n[IN-SAMPLE CHARACTERIZATION] feature quintile -> mean trade pnl (t/1NQ-equiv), win rate")
P("(quintile edges fixed on the pooled 37-session sample; CIs = day-clustered bootstrap, "
  f"{NBOOT} reps, seed {SEED})")
for feat in FEATS + ["sflow60_signed"]:
    tag = "SUPPLEMENTARY " if feat == "sflow60_signed" else ""
    tv["q"] = pd.qcut(tv[feat], 5, labels=False, duplicates="drop")
    binmap = tv["q"].to_dict()
    def bin_means(df, _bm=binmap):
        qs = df.index.map(_bm)
        return np.array([df.loc[qs == b, "pnl_t"].mean() for b in range(5)])
    lo, hi = cluster_boot(bin_means)
    edges = pd.qcut(tv[feat], 5, duplicates="drop").cat.categories
    for b in range(int(tv["q"].max()) + 1):
        sub = tv[tv["q"] == b]
        qrows.append(dict(feature=feat, q=b + 1, lo_edge=edges[b].left, hi_edge=edges[b].right,
                          n=len(sub), mean_pnl_t=sub["pnl_t"].mean(), ci_lo=lo[b], ci_hi=hi[b],
                          win_rate=sub["win"].mean(), mean_maxpos_nq=sub["max_pos_mnq"].mean() / 10))
    def spread_fn(df, _bm=binmap):
        qs = df.index.map(_bm)
        return df.loc[qs == 4, "pnl_t"].mean() - df.loc[qs == 0, "pnl_t"].mean()
    slo, shi = cluster_boot(spread_fn)
    sp = tv[tv["q"] == 4]["pnl_t"].mean() - tv[tv["q"] == 0]["pnl_t"].mean()
    def rho_fn(df, _f=feat):
        return df[_f].rank().corr(df["pnl_t"].rank())
    rlo, rhi = cluster_boot(rho_fn)
    rho = tv[feat].rank().corr(tv["pnl_t"].rank())
    qrows.append(dict(feature=feat, q="Q5-Q1", lo_edge=np.nan, hi_edge=np.nan, n=len(tv),
                      mean_pnl_t=sp, ci_lo=float(slo), ci_hi=float(shi),
                      win_rate=np.nan, mean_maxpos_nq=np.nan))
    P(f"  {tag}{feat:15s} Q5-Q1 {sp:+8.1f}t  CI[{float(slo):+8.1f},{float(shi):+8.1f}] | "
      f"spearman {rho:+.3f} CI[{float(rlo):+.3f},{float(rhi):+.3f}]"
      f"{'  <- CI excludes 0' if (float(slo) > 0 or float(shi) < 0) else ''}")
    qrows.append(dict(feature=feat, q="spearman", lo_edge=np.nan, hi_edge=np.nan, n=len(tv),
                      mean_pnl_t=rho, ci_lo=float(rlo), ci_hi=float(rhi),
                      win_rate=np.nan, mean_maxpos_nq=np.nan))
QT = pd.DataFrame(qrows)
QT.to_csv(os.path.join(OUTD, "quintiles.csv"), index=False)
P("\n[IN-SAMPLE CHARACTERIZATION] full quintile table:")
with pd.option_context("display.width", 200):
    P(QT.round(3).to_string(index=False))

# ---------------- 6. leakage-guarded L2 logistic, chronological session folds -------------
P("\n[IN-SAMPLE CHARACTERIZATION] L2 logistic win/loss, chronological session folds "
  "(expanding train, scaler fit on train only, C=1.0 fixed - no tuning)")
blocks = np.array_split(np.arange(len(sess_list)), 5)
oof = []
fold_rows = []
for k in range(1, 5):
    train_s = sess_list[np.concatenate(blocks[:k])]
    test_s = sess_list[blocks[k]]
    trn = tv[tv["sess"].isin(train_s)]; tst = tv[tv["sess"].isin(test_s)]
    sc = StandardScaler().fit(trn[FEATS])
    clf = LogisticRegression(penalty="l2", C=1.0, solver="lbfgs", max_iter=2000)
    clf.fit(sc.transform(trn[FEATS]), trn["win"])
    p = clf.predict_proba(sc.transform(tst[FEATS]))[:, 1]
    auc_k = roc_auc_score(tst["win"], p) if tst["win"].nunique() == 2 else np.nan
    fold_rows.append(dict(fold=k + 1, n_train=len(trn), n_test=len(tst),
                          test_sessions=f"{pd.Timestamp(test_s[0]).date()}..{pd.Timestamp(test_s[-1]).date()}",
                          auc=auc_k, test_win_rate=tst["win"].mean()))
    oof.append(pd.DataFrame({"idx": tst.index, "sess": tst["sess"].values,
                             "p_win": p, "win": tst["win"].values, "pnl_t": tst["pnl_t"].values}))
    P(f"  fold {k+1}: train n={len(trn)} test n={len(tst)} ({fold_rows[-1]['test_sessions']}) "
      f"AUC={auc_k:.3f}")
OOF = pd.concat(oof, ignore_index=True)
OOF.to_csv(os.path.join(OUTD, "oof_predictions.csv"), index=False)
pd.DataFrame(fold_rows).to_csv(os.path.join(OUTD, "logistic_folds.csv"), index=False)
auc_pool = roc_auc_score(OOF["win"], OOF["p_win"])
osess = np.array(sorted(OOF["sess"].unique()))
ogrp = {s: OOF.index[OOF["sess"] == s].values for s in osess}
aucs = []
for _ in range(NBOOT):
    pick = rng.choice(osess, size=len(osess), replace=True)
    idx = np.concatenate([ogrp[s] for s in pick])
    sub = OOF.loc[idx]
    aucs.append(roc_auc_score(sub["win"], sub["p_win"]) if sub["win"].nunique() == 2 else np.nan)
alo, ahi = np.nanpercentile(aucs, [2.5, 97.5])
base_wr = OOF["win"].mean()
def lift(frac):
    k = max(1, int(round(len(OOF) * frac)))
    top = OOF.nlargest(k, "p_win")
    return top["win"].mean() - base_wr, top["win"].mean(), k
l10, w10, k10 = lift(0.10); l20, w20, k20 = lift(0.20)
lifts10, lifts20 = [], []
for _ in range(NBOOT):
    pick = rng.choice(osess, size=len(osess), replace=True)
    idx = np.concatenate([ogrp[s] for s in pick])
    sub = OOF.loc[idx]
    for frac, acc in ((0.10, lifts10), (0.20, lifts20)):
        kk = max(1, int(round(len(sub) * frac)))
        acc.append(sub.nlargest(kk, "p_win")["win"].mean() - sub["win"].mean())
l10lo, l10hi = np.nanpercentile(lifts10, [2.5, 97.5]); l20lo, l20hi = np.nanpercentile(lifts20, [2.5, 97.5])
P(f"  pooled out-of-fold: n={len(OOF)} base win rate {base_wr:.3f}")
P(f"  AUC (pooled OOF) = {auc_pool:.3f}  day-clustered CI [{alo:.3f},{ahi:.3f}]")
P(f"  top-decile (n={k10}) win rate {w10:.3f}, lift {l10:+.3f}  CI [{l10lo:+.3f},{l10hi:+.3f}]")
P(f"  top-quintile (n={k20}) win rate {w20:.3f}, lift {l20:+.3f}  CI [{l20lo:+.3f},{l20hi:+.3f}]  (supplementary)")

# in-sample coefficients (full sample, for the report only)
sc = StandardScaler().fit(tv[FEATS])
clf = LogisticRegression(penalty="l2", C=1.0, solver="lbfgs", max_iter=2000)
clf.fit(sc.transform(tv[FEATS]), tv["win"])
coefs = pd.Series(clf.coef_[0], index=FEATS).sort_values(key=np.abs, ascending=False)
P("\n[IN-SAMPLE CHARACTERIZATION] full-sample standardized logistic coefficients (descriptive only):")
P(coefs.round(3).to_string())
coefs.to_csv(os.path.join(OUTD, "logistic_coefs_insample.csv"))

tr.to_csv(os.path.join(OUTD, "trades_all_sessions.csv"), index=False)
P("\n[FACT] artifacts written to research/scalping_lab/artifacts/w8_roleb/")
log_f.close()
