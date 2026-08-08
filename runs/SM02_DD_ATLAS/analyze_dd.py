# SM02_DD_ATLAS — drawdown episode decomposition of the dev-window E10 daily.
# INSTRUMENTATION (zero R1 burn). Spec: runs/SM02_DD_ATLAS/spec.yaml.
# Conventions: dev = sessions <= 2026-05-31; seed 20260808; block-5 circular bootstrap.
import sys, json, datetime as dt
import numpy as np
import pandas as pd

ROOT = r"D:/OneDrive - Washington University in St. Louis/TradingResearch/systematic_research"
OUT = ROOT + "/runs/SM02_DD_ATLAS/out"
DEV_END = "2026-05-31"
SEED = 20260808
B = 10000
BLOCK = 5

import os
os.makedirs(OUT, exist_ok=True)

# ---------- load ----------
d = pd.read_csv(ROOT + "/runs/SM01_SUBSTRATE/out/e10_daily_py.csv")
d = d[d.sess <= DEV_END].reset_index(drop=True)
N = len(d)
t = pd.read_parquet(ROOT + "/runs/SM01_SUBSTRATE/out/member_trades.parquet")
t["exit_sess"] = t.exit_sess.astype(str)
t["entry_sess"] = t.entry_sess.astype(str)
v = pd.read_parquet(ROOT + "/runs/SM01_SUBSTRATE/out/vote_state_3m.parquet")
v["sess_date"] = v.sess_date.astype(str)

tdev = t[t.exit_sess <= DEV_END].copy()
vdev = v[v.sess_date <= DEV_END].copy()

# S at entry (close approximation: vm*sigma460 at entry_bar, clamped [10,300]; 44.75 fallback)
sig_at_entry = v.sigma460.values[tdev.entry_bar.values]
S_entry = np.clip(tdev.vm.values * sig_at_entry, 10.0, 300.0)
S_entry = np.where(np.isfinite(S_entry), S_entry, 44.75)
tdev["S_entry"] = S_entry
tdev["false_start"] = (tdev.net < 0) & (tdev.mfe_pts < 0.5 * tdev.S_entry)
tdev["vote_pend_abs_entry"] = np.abs(v.vote_pend.values[tdev.entry_bar.values])

# ET session bucket by entry_time minutes-of-day
mins = tdev.entry_time.dt.hour * 60 + tdev.entry_time.dt.minute
BUCKETS = ["18-02", "02-0830", "0830-0930", "0930-1130", "1130-15", "15-17"]
def bucket_of(m):
    if m >= 1080 or m < 120:  return "18-02"
    if m < 510:   return "02-0830"
    if m < 570:   return "0830-0930"
    if m < 690:   return "0930-1130"
    if m < 900:   return "1130-15"
    return "15-17"
tdev["bucket"] = mins.map(bucket_of)

# ---------- dev baselines ----------
dev_daily_mean = d.net.mean(); dev_daily_std = d.net.std(ddof=1)
dev_trade_net = tdev.net.values
dev_trade_mean = dev_trade_net.mean()
q05, q25, q75, q95 = np.percentile(dev_trade_net, [5, 25, 75, 95])
BANDS = [("lt_q05", -np.inf, q05), ("q05_q25", q05, q25), ("q25_q75", q25, q75),
         ("q75_q95", q75, q95), ("gt_q95", q95, np.inf)]
def band_stats(x):
    out = {}
    n = len(x)
    for name, lo, hi in BANDS:
        m = (x > lo) & (x <= hi) if np.isfinite(lo) else (x <= hi)
        if not np.isfinite(hi): m = x > lo
        out[name] = (m.sum() / max(n, 1), x[m].mean() if m.sum() else 0.0, x[m].sum())
    return out
dev_bands = band_stats(dev_trade_net)
dev_fs_rate = tdev.false_start.mean()
dev_flip = vdev.flips_bar.mean()
dev_vpe = tdev.vote_pend_abs_entry.mean()
dev_sigma = vdev.sigma460.mean()
dev_bucket_net = tdev.groupby("bucket").net.sum().reindex(BUCKETS).fillna(0)

# ---------- drawdown episodes ----------
cum = d.net.cumsum().values
peak = np.maximum.accumulate(cum)
dd = cum - peak
sess = d.sess.values

episodes = []
i = 0
while i < N:
    if dd[i] < 0:
        start = i                      # first underwater session (peak was start-1)
        j = i
        while j < N and dd[j] < 0:
            j += 1
        seg = dd[start:j]
        trough_rel = int(np.argmin(seg))
        trough = start + trough_rel
        recovered = j < N
        episodes.append(dict(
            peak_sess=sess[start - 1] if start > 0 else None,
            start_sess=sess[start], trough_sess=sess[trough],
            recovery_sess=sess[j] if recovered else None,
            depth=float(seg.min()),
            decline_len=trough - start + 1,
            recover_len=(j - trough) if recovered else None,
            tuw=(j - start + (1 if recovered else 0)) if recovered else (N - start),
            recovered=recovered,
            start_i=start, trough_i=trough, end_i=(j if recovered else N - 1),
        ))
        i = j
    else:
        i += 1

ep = pd.DataFrame(episodes).sort_values("depth").reset_index(drop=True)
sel = ep[(ep.depth <= -10000)].copy()
top10 = ep.head(10)
sel = pd.concat([sel, top10]).drop_duplicates(subset=["start_sess"]).sort_values("depth").reset_index(drop=True)
sel["ep_id"] = ["E%02d" % (k + 1) for k in range(len(sel))]

# ---------- bootstrap 1: block-5 circular on dev daily -> maxDD dist & episode counts ----------
rng = np.random.default_rng(SEED)
x = d.net.values
nblocks = int(np.ceil(N / BLOCK))
starts = rng.integers(0, N, size=(B, nblocks))
idx = (starts[:, :, None] + np.arange(BLOCK)[None, None, :]) % N
paths = x[idx.reshape(B, -1)[:, :N]]
cumB = np.cumsum(paths, axis=1)
peakB = np.maximum.accumulate(cumB, axis=1)
ddB = cumB - peakB
maxddB = ddB.min(axis=1)
# count episodes <= -10k per path
cnt10k = np.zeros(B, dtype=int)
for b in range(B):
    row = ddB[b]
    under = row < 0
    # episode boundaries
    edges = np.flatnonzero(np.diff(np.concatenate(([0], under.view(np.int8), [0]))))
    for s0, e0 in zip(edges[::2], edges[1::2]):
        if row[s0:e0].min() <= -10000:
            cnt10k[b] += 1
boot = dict(
    maxdd_p05=float(np.percentile(maxddB, 5)), maxdd_p25=float(np.percentile(maxddB, 25)),
    maxdd_median=float(np.median(maxddB)), maxdd_p75=float(np.percentile(maxddB, 75)),
    maxdd_p95=float(np.percentile(maxddB, 95)),
    p_maxdd_le_40208=float((maxddB <= -40207.6).mean()),
    mean_n_ep_le_10k=float(cnt10k.mean()), p05_n=float(np.percentile(cnt10k, 5)),
    p95_n=float(np.percentile(cnt10k, 95)),
)

# ---------- per-episode decomposition ----------
sess_index = {s: k for k, s in enumerate(sess)}
rows = []
rng2 = np.random.default_rng(SEED)  # fresh, same seed, for trade bootstrap
for _, e in sel.iterrows():
    w0, w1 = e.start_sess, e.trough_sess          # decline window (inclusive)
    win_sess = sess[e.start_i: e.trough_i + 1]
    dwin = d.iloc[e.start_i: e.trough_i + 1]
    tw = tdev[(tdev.exit_sess >= w0) & (tdev.exit_sess <= w1)]
    n_ep = len(tw)
    long_net = tw.loc[tw.side == 1, "net"].sum(); n_long = int((tw.side == 1).sum())
    short_net = tw.loc[tw.side == -1, "net"].sum(); n_short = int((tw.side == -1).sum())
    fs_n = int(tw.false_start.sum()); fs_rate = tw.false_start.mean() if n_ep else np.nan
    fs_net = tw.loc[tw.false_start, "net"].sum()
    vw = vdev[(vdev.sess_date >= w0) & (vdev.sess_date <= w1)]
    flip = vw.flips_bar.mean()
    vpe = tw.vote_pend_abs_entry.mean() if n_ep else np.nan
    sig_win = vw.sigma460.mean()
    # prior 20 sessions
    p_lo = max(0, e.start_i - 20)
    prior_sess = sess[p_lo: e.start_i]
    vp = vdev[vdev.sess_date.isin(prior_sess)]
    sig_prior = vp.sigma460.mean()
    sig_chg = (sig_win / sig_prior - 1) if sig_prior and np.isfinite(sig_prior) else np.nan
    # buckets
    bnet = tw.groupby("bucket").net.sum().reindex(BUCKETS).fillna(0)
    bn = tw.groupby("bucket").size().reindex(BUCKETS).fillna(0).astype(int)
    # attribution vs dev trade distribution
    ep_sum = tw.net.sum()
    expected = n_ep * dev_trade_mean
    gap = ep_sum - expected
    eb = band_stats(tw.net.values) if n_ep else {k: (0, 0, 0) for k, _, _ in BANDS}
    band_contrib = {}
    for name, _, _ in BANDS:
        f_e, m_e, _ = eb[name]; f_d, m_d, _ = dev_bands[name]
        band_contrib[name] = n_ep * (f_e * m_e - f_d * m_d)
    # trade-count-matched iid bootstrap from dev distribution
    if n_ep:
        draws = rng2.choice(dev_trade_net, size=(B, n_ep), replace=True).sum(axis=1)
        pct = float((draws <= ep_sum).mean())
        exp_p05, exp_p95 = np.percentile(draws, [5, 95])
    else:
        pct, exp_p05, exp_p95 = np.nan, np.nan, np.nan
    # daily z of decline sum
    L = e.decline_len
    decl_sum = dwin.net.sum()
    z_daily = (decl_sum - L * dev_daily_mean) / (dev_daily_std * np.sqrt(L))
    # price context: NQ close at peak session end vs trough session end
    px0 = vdev[vdev.sess_date == e.peak_sess].close.iloc[-1] if e.peak_sess else np.nan
    px1 = vw.close.iloc[-1] if len(vw) else np.nan
    px_lo = vw.close.min(); px_hi = vw.close.max()
    rows.append(dict(
        ep_id=e.ep_id, peak_sess=e.peak_sess, start_sess=w0, trough_sess=w1,
        recovery_sess=e.recovery_sess, recovered=e.recovered, depth=round(e.depth, 1),
        decline_len=L, recover_len=e.recover_len, tuw=e.tuw,
        decline_sum_daily=round(decl_sum, 1),
        worst_day=round(dwin.net.min(), 1), worst_day_sess=dwin.sess.iloc[dwin.net.values.argmin()],
        n_down_days=int((dwin.net < 0).sum()), n_days=L,
        n_trades=n_ep, n_long=n_long, n_short=n_short,
        long_net=round(long_net, 1), short_net=round(short_net, 1),
        fs_n=fs_n, fs_rate=round(fs_rate, 4) if n_ep else np.nan,
        fs_rate_ratio=round(fs_rate / dev_fs_rate, 3) if n_ep else np.nan,
        fs_net=round(fs_net, 1),
        flip_mean=round(flip, 4), flip_ratio=round(flip / dev_flip, 3),
        vpe_mean=round(vpe, 3) if n_ep else np.nan,
        vpe_ratio=round(vpe / dev_vpe, 3) if n_ep else np.nan,
        sigma_win=round(sig_win, 3), sigma_prior20=round(sig_prior, 3),
        sigma_chg=round(sig_chg, 4) if np.isfinite(sig_chg) else np.nan,
        sigma_vs_dev=round(sig_win / dev_sigma, 3),
        **{f"net_{b}": round(bnet[b], 1) for b in BUCKETS},
        **{f"n_{b}": int(bn[b]) for b in BUCKETS},
        trade_sum=round(ep_sum, 1), trade_sum_e10eq=round(ep_sum / 13, 1),
        expected_sum=round(expected, 1), gap=round(gap, 1),
        gap_e10eq=round(gap / 13, 1),
        **{f"contrib_{name}": round(band_contrib[name], 1) for name, _, _ in BANDS},
        rt_share_of_gap=round(band_contrib["gt_q95"] / gap, 3) if gap < 0 else np.nan,
        lt_share_of_gap=round(band_contrib["lt_q05"] / gap, 3) if gap < 0 else np.nan,
        boot_pct=pct, boot_p05=round(exp_p05, 1) if n_ep else np.nan,
        boot_p95=round(exp_p95, 1) if n_ep else np.nan,
        z_daily=round(z_daily, 2),
        f_lt_q05=round(eb["lt_q05"][0], 4), f_gt_q95=round(eb["gt_q95"][0], 4),
        px_peak=px0, px_trough=px1,
        px_ret_win=round(px1 / px0 - 1, 4) if np.isfinite(px0) else np.nan,
        px_range_win=round((px_hi - px_lo) / px0, 4) if np.isfinite(px0) else np.nan,
    ))

dec = pd.DataFrame(rows)

# ---------- taxonomy ----------
def classify(r):
    cls = []
    # attribution classes (what the P&L gap is)
    if r.gap < 0:
        if r.rt_share_of_gap is not np.nan and r.rt_share_of_gap >= 0.5:
            cls.append("RIGHT_TAIL_ABSENCE")
        if r.lt_share_of_gap is not np.nan and r.lt_share_of_gap >= 0.5:
            cls.append("LEFT_TAIL_EXCESS")
    if (r.fs_rate_ratio >= 1.25) and (r.fs_n >= 10) and (r.trade_sum < 0) and (r.fs_net <= 0.35 * r.trade_sum):
        cls.append("FALSE_START_CLUSTER")
    if (r.decline_len >= 25) and (r.worst_day >= -3 * dev_daily_std) and \
       (r.decline_sum_daily / r.decline_len >= -0.5 * dev_daily_std):
        cls.append("NO_PROGRESS_BLEED")
    if r.vpe_ratio == r.vpe_ratio and r.vpe_ratio <= 0.85:
        cls.append("HIGH_DISAGREEMENT")
    if r.flip_ratio >= 1.25:
        cls.append("CHOP_CLUSTER")
    if r.sigma_chg == r.sigma_chg and r.sigma_chg >= 0.30:
        cls.append("VOL_SHOCK")
    if r.sigma_chg == r.sigma_chg and r.sigma_chg <= -0.20:
        cls.append("VOL_COLLAPSE")
    ln, sn = r.long_net, r.short_net
    if min(ln, sn) < 0 and (max(ln, sn) >= 0 or max(ln, sn) >= 0.2 * min(ln, sn)):
        cls.append("SIDE_SPECIFIC_" + ("LONG" if ln < sn else "SHORT"))
    bnets = np.array([r[f"net_{b}"] for b in BUCKETS])
    negsum = bnets[bnets < 0].sum()
    if negsum < 0 and bnets.min() / negsum >= 0.60:
        cls.append("SESSION_SPECIFIC_" + BUCKETS[int(bnets.argmin())])
    if not cls or (r.boot_pct == r.boot_pct and r.boot_pct >= 0.05 and abs(r.z_daily) < 2):
        cls.append("NORMAL_VARIANCE")
    return cls

dec["classes"] = dec.apply(classify, axis=1)
def dominant(r):
    c = r.classes
    for pref in ["RIGHT_TAIL_ABSENCE", "LEFT_TAIL_EXCESS", "FALSE_START_CLUSTER", "NO_PROGRESS_BLEED"]:
        if pref in c: return pref
    for x in c:
        if not x.startswith("NORMAL"): return x
    return "NORMAL_VARIANCE"
dec["dominant_class"] = dec.apply(dominant, axis=1)
dec["classes"] = dec.classes.map(lambda c: "|".join(c))

# ---------- longest TUW ----------
ep_all = ep.copy()
ep_all["tuw_rank"] = ep_all.tuw.rank(ascending=False)
longest = ep_all.sort_values("tuw", ascending=False).head(3)

# ---------- write ----------
ep_out = sel.merge(dec[["ep_id", "dominant_class", "classes", "z_daily", "boot_pct"]], on="ep_id")
ep_out = ep_out.drop(columns=["start_i", "trough_i", "end_i"])
ep_out.to_csv(OUT + "/dd_episodes.csv", index=False)
dec.to_csv(OUT + "/dd_trade_decomp.csv", index=False)

baselines = dict(
    dev_sessions=N, dev_total=float(d.net.sum()), dev_daily_mean=float(dev_daily_mean),
    dev_daily_std=float(dev_daily_std), dev_trades=len(tdev),
    dev_trade_mean=float(dev_trade_mean), dev_trade_median=float(np.median(dev_trade_net)),
    q05=float(q05), q25=float(q25), q75=float(q75), q95=float(q95),
    dev_fs_rate=float(dev_fs_rate), dev_flip=float(dev_flip), dev_vpe=float(dev_vpe),
    dev_sigma=float(dev_sigma),
    dev_bucket_net={b: float(dev_bucket_net[b]) for b in BUCKETS},
    dev_band_freq={k: dev_bands[k][0] for k, _, _ in BANDS},
    dev_band_mean={k: dev_bands[k][1] for k, _, _ in BANDS},
    n_episodes_total=len(ep), n_episodes_le10k=int((ep.depth <= -10000).sum()),
    n_selected=len(sel), bootstrap=boot,
    longest_tuw=[dict(start=r.start_sess, trough=r.trough_sess,
                      rec=r.recovery_sess, tuw=int(r.tuw), depth=float(r.depth),
                      recovered=bool(r.recovered)) for _, r in longest.iterrows()],
)
# ---------- supporting context ----------
yr = tdev.copy(); yr["year"] = yr.exit_sess.str[:4]
side_by_year = yr.groupby(["year", "side"]).net.sum().unstack().rename(columns={1: "long", -1: "short"})
d2 = d.copy(); d2["year"] = d2.sess.str[:4]; d2["at_peak"] = dd >= 0
at_peak_by_year = d2.groupby("year").at_peak.agg(["sum", "count"])
# monthly detail inside deep-dive episodes
def monthly_detail(w0, w1):
    dwin = d[(d.sess >= w0) & (d.sess <= w1)].copy(); dwin["ym"] = dwin.sess.str[:7]
    tw = tdev[(tdev.exit_sess >= w0) & (tdev.exit_sess <= w1)].copy(); tw["ym"] = tw.exit_sess.str[:7]
    m1 = dwin.groupby("ym").net.agg(["sum", "min", "count"]).rename(
        columns={"sum": "e10_net", "min": "e10_worst_day", "count": "n_sess"})
    m2 = tw.groupby(["ym", "side"]).net.sum().unstack().rename(columns={1: "long_mem", -1: "short_mem"})
    m3 = tw.groupby("ym").agg(n_tr=("net", "size"), fs_rate=("false_start", "mean"))
    return m1.join(m2).join(m3).round(1)
deep = {}
for eid, (w0, w1) in {"E01": ("2026-02-13", "2026-05-29"), "E02": ("2024-09-04", "2024-12-05"),
                      "E04": ("2025-04-11", "2025-07-28"), "E07": ("2023-01-10", "2023-03-21")}.items():
    deep[eid] = monthly_detail(w0, w1).to_string()
worst5_e01 = d[(d.sess >= "2026-02-13") & (d.sess <= "2026-05-29")].nsmallest(5, "net")
# sep2024->sep2025 underwater complex
mask = (d.sess >= "2024-09-04") & (d.sess <= "2025-09-02")
n_complex = int(mask.sum()); n_at_peak_complex = int((dd >= 0)[mask.values].sum())
baselines["side_by_year"] = side_by_year.round(0).to_dict()
baselines["at_peak_by_year"] = at_peak_by_year.to_dict()
baselines["complex_2024_2025"] = dict(sessions=n_complex, at_peak=n_at_peak_complex)
baselines["worst5_E01"] = worst5_e01.to_dict("records")
baselines["dev_fs_net_share"] = float(tdev.loc[tdev.false_start, "net"].sum() / tdev.net.sum())
baselines["dev_fs_net"] = float(tdev.loc[tdev.false_start, "net"].sum())
baselines["dev_long_net"] = float(tdev.loc[tdev.side == 1, "net"].sum())
baselines["dev_short_net"] = float(tdev.loc[tdev.side == -1, "net"].sum())

with open(OUT + "/dd_baselines.json", "w") as f:
    json.dump(baselines, f, indent=2, default=str)
with open(OUT + "/deep_dive_monthly.txt", "w") as f:
    for k, s in deep.items():
        f.write(f"== {k} ==\n{s}\n\n")

print(json.dumps(baselines, indent=2, default=str))
print(ep_out[["ep_id", "peak_sess", "trough_sess", "recovery_sess", "depth", "decline_len",
              "tuw", "dominant_class"]].to_string())
