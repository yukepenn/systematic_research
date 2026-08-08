"""SM02B_TRADE_ANATOMY — trade-path anatomy on the SM01 substrate.

INSTRUMENTATION (no selection). Dev window: entry_sess <= 2026-05-31.
All decision-critical conditionals carry day-clustered circular block bootstrap
CIs (cluster = entry session, block=5, B=2000, seed 20260808).

S_entry is EXACT: recomputed via sm01_solarsim.member_states per member and read
as s_eff[entry_bar-1] (the flip/trend-birth bar; entry fills at flip+1 open).

Run from repo root:  python runs/SM02B_TRADE_ANATOMY/anatomy_build.py
"""
import sys, os, json, time
sys.path.insert(0, "src/analytics")
import numpy as np
import pandas as pd
import sm01_solarsim as sm

t_start = time.time()
RUN = "runs/SM02B_TRADE_ANATOMY"
OUT = f"{RUN}/out"
TBL = f"{OUT}/anatomy_tables"
os.makedirs(TBL, exist_ok=True)

SEED, B_BOOT, BLOCK = 20260808, 2000, 5
DEV_END = pd.Timestamp("2026-05-31")
PV = 20.0                          # NQ $/point
B_LIST = [5, 10, 20, 40, 80, 160]  # decision bars (3-min bars after entry)
Q_GRID = [0.25, 0.50]              # t3a stop grid MFE-progress thresholds
Q_PROG = [0.25, 0.50, 1.00]        # t2 progress curves
M_GRID = [0.0, 0.25, 0.50, 1.00]   # t3a current-MAE thresholds
M_CROSS = [0.25, 0.50, 1.00, 1.50, 2.00, 3.00]  # first-crossing analysis
CAT_S = [1.0, 1.5, 2.0, 3.0]       # catastrophe: final loss / interim MAE in S units
CAT_D = [2000.0, 4000.0, 8000.0]   # catastrophe: final loss in $
BANDS = {"fast": {6, 8, 10, 12}, "mid": {14, 16, 18, 20, 22},
         "slow": {24, 26, 28, 30}}

# ---------------------------------------------------------------- load + S_entry
bars = sm.load_bars_3m()
close = bars.close.to_numpy(); high = bars.high.to_numpy(); low = bars.low.to_numpy()
sig = sm.sigma_series(close)
tr = pd.read_parquet("runs/SM01_SUBSTRATE/out/member_trades.parquet")
vote = pd.read_parquet("runs/SM01_SUBSTRATE/out/vote_state_3m.parquet")
assert (vote["time"].to_numpy() == bars["time"].to_numpy()).all(), "bars/vote misaligned"
assert np.allclose(vote["sigma460"].to_numpy(), sig, equal_nan=True), "sigma mismatch"
assert (bars["time"].to_numpy()[tr.entry_bar.to_numpy()] == tr.entry_time.to_numpy()).all()

n_tr = len(tr)
eb = tr.entry_bar.to_numpy(); xb = tr.exit_bar.to_numpy()
side = tr.side.to_numpy(); epx = tr.entry_px.to_numpy(); xpx = tr.exit_px.to_numpy()
held = tr.bars_held.to_numpy(); net = tr.net.to_numpy(); vm = tr.vm.to_numpy()

S_exact = np.full(n_tr, np.nan)
flip_ok = np.zeros(n_tr, bool)
for v in sm.VMS:
    is_up, flip, s_eff, anchor = sm.member_states(close, sig, float(v))
    m = vm == v
    S_exact[m] = s_eff[eb[m] - 1]
    flip_ok[m] = flip[eb[m] - 1] != 0
    print(f"member_states vm{v} done  t={time.time()-t_start:.0f}s", flush=True)
assert flip_ok.all(), "some entry not preceded by flip at entry_bar-1"

# approximation checks (task asks to validate the formula)
sig_bm1 = sig[eb - 1]; sig_b = sig[eb]
FALLBACK = 179 * 0.25
apx_bm1 = np.where(np.isfinite(sig_bm1) & (sig_bm1 > 0),
                   np.clip(vm * sig_bm1, 10.0, 300.0), FALLBACK)
apx_b = np.where(np.isfinite(sig_b) & (sig_b > 0),
                 np.clip(vm * sig_b, 10.0, 300.0), FALLBACK)
s_val_df = pd.DataFrame({
    "metric": ["max_abs_diff_exact_vs_clamp(vm*sigma[eb-1])",
               "n_diff_gt_1e-9_exact_vs_eb-1",
               "max_abs_diff_exact_vs_clamp(vm*sigma[eb])",
               "median_rel_diff_eb_vs_eb-1",
               "n_sigma_fallback", "n_trades",
               "n_S_at_lower_clamp_10", "n_S_at_upper_clamp_300"],
    "value": [float(np.max(np.abs(S_exact - apx_bm1))),
              int((np.abs(S_exact - apx_bm1) > 1e-9).sum()),
              float(np.max(np.abs(S_exact - apx_b))),
              float(np.median(np.abs(apx_b - apx_bm1) / S_exact)),
              int((~(np.isfinite(sig_bm1) & (sig_bm1 > 0))).sum()), n_tr,
              int((S_exact <= 10.0 + 1e-12).sum()),
              int((S_exact >= 300.0 - 1e-12).sum())]})
S = S_exact

# ---------------------------------------------------------------- path loop
nB = len(B_LIST); Barr = np.array(B_LIST)
nMc = len(M_CROSS); Mc = np.array(M_CROSS)
mfe_b = np.full((n_tr, nB), np.nan); mae_b = np.full((n_tr, nB), np.nan)
rem_b = np.full((n_tr, nB), np.nan); open_b = np.zeros((n_tr, nB), bool)
crossk = np.full((n_tr, nMc), -1, np.int32)          # first bar running MAE >= m*S
rem_cross = np.full((n_tr, nMc), np.nan)             # remaining $ from cross-bar close
kfe = np.full((n_tr, 2), -1, np.int32)               # first bar MFE >= {0.5,1.0}*S
recon_mfe = np.empty(n_tr); recon_mae = np.empty(n_tr)
fe_thr_mult = np.array([0.5, 1.0])

for i in range(n_tr):
    a, z = eb[i], xb[i]
    if side[i] == 1:
        fe = high[a:z + 1] - epx[i]; ae = epx[i] - low[a:z + 1]
    else:
        fe = epx[i] - low[a:z + 1]; ae = high[a:z + 1] - epx[i]
    rf = np.maximum.accumulate(fe); ra = np.maximum.accumulate(ae)
    recon_mfe[i] = rf[-1]; recon_mae[i] = ra[-1]
    h = held[i]
    ob = Barr < h                                    # still open AFTER bar b close
    if ob.any():
        bb = Barr[ob]
        open_b[i, ob] = True
        mfe_b[i, ob] = rf[bb]; mae_b[i, ob] = ra[bb]
        rem_b[i, ob] = side[i] * (xpx[i] - close[a + bb]) * PV
    kc = np.searchsorted(ra, Mc * S[i])
    hit = kc <= h
    crossk[i, hit] = kc[hit]
    for j in np.where(hit)[0]:
        k = kc[j]
        rem_cross[i, j] = 0.0 if k == h else side[i] * (xpx[i] - close[a + k]) * PV
    kf = np.searchsorted(rf, fe_thr_mult * S[i])
    for j in range(2):
        if kf[j] <= h:
            kfe[i, j] = kf[j]

assert float(np.max(np.abs(recon_mfe - tr.mfe_pts.to_numpy()))) < 1e-9
assert float(np.max(np.abs(recon_mae - tr.mae_pts.to_numpy()))) < 1e-9
print(f"path loop done t={time.time()-t_start:.0f}s", flush=True)

# ---------------------------------------------------------------- dev subset
entry_sess = pd.to_datetime(tr.entry_sess)
dev = (entry_sess <= DEV_END).to_numpy()
didx = np.where(dev)[0]
D = {k: v[didx] for k, v in dict(
    eb=eb, net=net, vm=vm, S=S, held=held, side=side).items()}
mfe_b, mae_b, rem_b, open_b = mfe_b[didx], mae_b[didx], rem_b[didx], open_b[didx]
crossk, rem_cross, kfe = crossk[didx], rem_cross[didx], kfe[didx]
mfeS = tr.mfe_pts.to_numpy()[didx] / D["S"]
maeS = tr.mae_pts.to_numpy()[didx] / D["S"]
mfe_pts = tr.mfe_pts.to_numpy()[didx]; mae_pts = tr.mae_pts.to_numpy()[didx]
b2mfe = tr.bars_to_mfe.to_numpy()[didx]; b2mae = tr.bars_to_mae.to_numpy()[didx]
exit_sc = (tr.exit_reason == "Exit on session close").to_numpy()[didx]
nd = len(didx)
NET, Sd = D["net"], D["S"]
win = NET > 0

sess_d = entry_sess.to_numpy()[didx]
dev_sessions = np.sort(pd.unique(sess_d))
sidx = np.searchsorted(dev_sessions, sess_d)
nsess = len(dev_sessions)
print(f"dev trades {nd}, sessions {nsess}", flush=True)

groups = {"pooled": np.ones(nd, bool)}
for gname, vs in BANDS.items():
    groups[gname] = np.isin(D["vm"], list(vs))

# top-1% (pooled dev, by net)
thr99 = np.quantile(NET, 0.99)
top1 = NET >= thr99
n_top1 = int(top1.sum())

# ---------------------------------------------------------------- bootstrap engine
rng = np.random.default_rng(SEED)
nblocks = int(np.ceil(nsess / BLOCK))
starts = rng.integers(0, nsess, (B_BOOT, nblocks))
idx = (starts[:, :, None] + np.arange(BLOCK)[None, None, :]).reshape(B_BOOT, -1)[:, :nsess] % nsess
W = np.zeros((B_BOOT, nsess))
for r in range(B_BOOT):
    W[r] = np.bincount(idx[r], minlength=nsess)
print(f"W built t={time.time()-t_start:.0f}s", flush=True)

def boot_ratio(num, den):
    """num, den: length-nd arrays (zeros outside cell). Returns point, lo, hi of
    sum(num)/sum(den) under day-clustered block bootstrap."""
    sn = np.bincount(sidx, weights=num, minlength=nsess)
    sd = np.bincount(sidx, weights=den, minlength=nsess)
    tot_n, tot_d = sn.sum(), sd.sum()
    pt = tot_n / tot_d if tot_d != 0 else np.nan
    bn = W @ sn; bd = W @ sd
    with np.errstate(invalid="ignore", divide="ignore"):
        rr = np.where(bd != 0, bn / bd, np.nan)
    if np.isfinite(rr).sum() < 50:
        return pt, np.nan, np.nan
    lo, hi = np.nanpercentile(rr, [2.5, 97.5])
    return pt, lo, hi

def q_of(x, qs):
    return [float(np.quantile(x, q)) if len(x) else np.nan for q in qs]

# ---------------------------------------------------------------- T1 distributions
rows = []
for g, gm in groups.items():
    for lab, om in [("win", win), ("loss", ~win)]:
        m = gm & om
        x_mfeS, x_maeS = mfeS[m], maeS[m]
        rows.append(dict(
            group=g, outcome=lab, n=int(m.sum()), frac=float(m.mean() / gm.mean()),
            mean_net=float(NET[m].mean()), med_net=float(np.median(NET[m])),
            **{f"mfeS_q{int(q*100)}": v for q, v in zip([.25, .5, .75, .9],
               q_of(x_mfeS, [.25, .5, .75, .9]))},
            **{f"maeS_q{int(q*100)}": v for q, v in zip([.25, .5, .75, .9],
               q_of(x_maeS, [.25, .5, .75, .9]))},
            med_mfe_pts=float(np.median(mfe_pts[m])), med_mae_pts=float(np.median(mae_pts[m])),
            med_bars_held=float(np.median(D["held"][m])),
            med_bars_to_mfe=float(np.median(b2mfe[m])),
            med_bars_to_mae=float(np.median(b2mae[m])),
            frac_sess_close_exit=float(exit_sc[m].mean())))
pd.DataFrame(rows).to_csv(f"{TBL}/t1_mfe_mae_dist.csv", index=False)

# ---------------------------------------------------------------- T2 progress curves
rows = []
for g, gm in groups.items():
    for bi, b in enumerate(B_LIST):
        ob = gm & open_b[:, bi]
        for q in Q_PROG:
            for lab, cm in [("no_progress", ob & (mfe_b[:, bi] < q * Sd)),
                            ("progress", ob & (mfe_b[:, bi] >= q * Sd))]:
                n = int(cm.sum())
                p_pt, p_lo, p_hi = boot_ratio((win & cm).astype(float), cm.astype(float))
                remv = np.where(cm, np.nan_to_num(rem_b[:, bi]), 0.0)
                r_pt, r_lo, r_hi = boot_ratio(remv, cm.astype(float))
                rows.append(dict(group=g, b=b, q=q, cond=lab, n=n,
                                 frac_of_open=float(n / ob.sum()) if ob.sum() else np.nan,
                                 p_win=p_pt, p_win_lo=p_lo, p_win_hi=p_hi,
                                 e_rem=r_pt, e_rem_lo=r_lo, e_rem_hi=r_hi,
                                 sum_rem=float(remv.sum()),
                                 mean_final_net=float(NET[cm].mean()) if n else np.nan))
pd.DataFrame(rows).to_csv(f"{TBL}/t2_progress_curves.csv", index=False)
print(f"t2 done t={time.time()-t_start:.0f}s", flush=True)

# ---------------------------------------------------------------- T3a stop grid
rows = []
for g, gm in groups.items():
    for bi, b in enumerate(B_LIST):
        ob = gm & open_b[:, bi]
        for q in Q_GRID:
            noprog = ob & (mfe_b[:, bi] < q * Sd)
            for m_ in M_GRID:
                cm = noprog & (mae_b[:, bi] >= m_ * Sd)
                n = int(cm.sum())
                p_pt, p_lo, p_hi = boot_ratio((win & cm).astype(float), cm.astype(float))
                remv = np.where(cm, np.nan_to_num(rem_b[:, bi]), 0.0)
                r_pt, r_lo, r_hi = boot_ratio(remv, cm.astype(float))
                t1_hit = int((cm & top1).sum()) if g == "pooled" else int((cm & top1).sum())
                rows.append(dict(
                    group=g, b=b, q=q, m=m_, n=n,
                    p_win=p_pt, p_win_lo=p_lo, p_win_hi=p_hi,
                    e_rem=r_pt, e_rem_lo=r_lo, e_rem_hi=r_hi,
                    sum_rem=float(remv.sum()),
                    clearly_neg=bool(n >= 30 and np.isfinite(r_hi) and r_hi < 0),
                    top1_n_hit=t1_hit,
                    top1_frac_hit=float(t1_hit / n_top1),
                    mean_final_net=float(NET[cm].mean()) if n else np.nan))
pd.DataFrame(rows).to_csv(f"{TBL}/t3a_stop_grid.csv", index=False)
print(f"t3a done t={time.time()-t_start:.0f}s", flush=True)

# ---------------------------------------------------------------- T3b MAE first crossing
rows = []
for g, gm in groups.items():
    for j, m_ in enumerate(M_CROSS):
        cm = gm & (crossk[:, j] >= 0)
        n = int(cm.sum())
        p_pt, p_lo, p_hi = boot_ratio((win & cm).astype(float), cm.astype(float))
        remv = np.where(cm, np.nan_to_num(rem_cross[:, j]), 0.0)
        r_pt, r_lo, r_hi = boot_ratio(remv, cm.astype(float))
        rows.append(dict(
            group=g, m=m_, n_crossed=n,
            frac_of_trades=float(n / gm.sum()),
            p_recover_net_pos=p_pt, p_rec_lo=p_lo, p_rec_hi=p_hi,
            e_rem_from_cross=r_pt, e_rem_lo=r_lo, e_rem_hi=r_hi,
            sum_rem_from_cross=float(remv.sum()),
            stop_delta_if_cut_at_cross_close=float(-remv.sum()),
            mean_final_net=float(NET[cm].mean()) if n else np.nan,
            med_cross_bar=float(np.median(crossk[cm, j])) if n else np.nan,
            top1_n_crossed=int((cm & top1).sum())))
pd.DataFrame(rows).to_csv(f"{TBL}/t3b_mae_crossing.csv", index=False)

# ---------------------------------------------------------------- T3c catastrophe
loss_total = NET[~win].sum()
rows = []
for g, gm in groups.items():
    gnet = NET[gm].sum()
    gloss = NET[gm & ~win].sum()
    for thr in CAT_S:
        m1 = gm & (-NET >= thr * Sd * PV)          # final $ loss >= thr*S*PV (points-loss in S units)
        m1b = gm & ((-(tr.points.to_numpy()[didx])) >= thr * Sd)  # final points-loss >= thr*S
        m2 = gm & (maeS >= thr)                     # interim MAE >= thr*S
        rows.append(dict(
            group=g, thr_type="S_mult", thr=thr,
            n_final_loss=int(m1b.sum()), net_final_loss=float(NET[m1b].sum()),
            final_loss_share_of_group_gross_loss=float(NET[m1b].sum() / gloss) if gloss else np.nan,
            excess_loss_beyond_thr=float(np.sum(-NET[m1b] - thr * Sd[m1b] * PV)),
            n_mae_ge=int(m2.sum()), net_of_mae_ge=float(NET[m2].sum()),
            p_recover=float(win[m2].mean()) if m2.sum() else np.nan,
            n_recover=int((m2 & win).sum()),
            group_net=float(gnet)))
    for thr in CAT_D:
        m1 = gm & (-NET >= thr)
        m2 = gm & (mae_pts * PV >= thr)
        rows.append(dict(
            group=g, thr_type="dollar", thr=thr,
            n_final_loss=int(m1.sum()), net_final_loss=float(NET[m1].sum()),
            final_loss_share_of_group_gross_loss=float(NET[m1].sum() / gloss) if gloss else np.nan,
            excess_loss_beyond_thr=float(np.sum(-NET[m1] - thr)),
            n_mae_ge=int(m2.sum()), net_of_mae_ge=float(NET[m2].sum()),
            p_recover=float(win[m2].mean()) if m2.sum() else np.nan,
            n_recover=int((m2 & win).sum()),
            group_net=float(gnet)))
pd.DataFrame(rows).to_csv(f"{TBL}/t3c_catastrophe.csv", index=False)
print(f"t3 done t={time.time()-t_start:.0f}s", flush=True)

# ---------------------------------------------------------------- T4 entry-state
vp = np.abs(vote["vote_pend"].to_numpy()[eb - 1])[didx]
vp_edges = [(0, 3), (4, 6), (7, 9), (10, 13)]
fc = np.cumsum(vote["flips_bar"].to_numpy())
f20_all = fc[eb - 1] - np.where(eb - 21 >= 0, fc[np.maximum(eb - 21, 0)], 0.0)
f20 = f20_all[didx]
f20_edges = [(1, 1), (2, 2), (3, 4), (5, 30)]
bar_dev = (pd.to_datetime(bars["sess_date"]) <= DEV_END).to_numpy()
svals = np.sort(sig[bar_dev & np.isfinite(sig)])
sig_pct = np.searchsorted(svals, sig[eb - 1][didx]) / len(svals)
sp_edges = [(0.0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.01)]

def entry_state_table(vals, edges, fname, label):
    rows = []
    for g, gm in groups.items():
        gnet = NET[gm].sum()
        gt1 = int((gm & top1).sum())
        for lo_, hi_ in edges:
            if label == "sigma_pct":
                bm = gm & (vals >= lo_) & (vals < hi_)
                bname = f"[{lo_:.1f},{min(hi_,1.0):.1f})"
            else:
                bm = gm & (vals >= lo_) & (vals <= hi_)
                bname = f"{lo_}-{hi_}" if lo_ != hi_ else f"{lo_}"
            n = int(bm.sum())
            p_pt, p_lo, p_hi = boot_ratio((win & bm).astype(float), bm.astype(float))
            e_pt, e_lo, e_hi = boot_ratio(np.where(bm, NET, 0.0), bm.astype(float))
            t1n = int((bm & top1).sum())
            rows.append(dict(group=g, bucket=bname, n=n,
                             frac=float(n / gm.sum()),
                             win_rate=p_pt, win_lo=p_lo, win_hi=p_hi,
                             mean_net=e_pt, mean_net_lo=e_lo, mean_net_hi=e_hi,
                             net_sum=float(NET[bm].sum()),
                             net_share_of_group=float(NET[bm].sum() / gnet) if gnet else np.nan,
                             top1_n=t1n,
                             top1_share=float(t1n / gt1) if gt1 else np.nan))
    pd.DataFrame(rows).to_csv(f"{TBL}/{fname}", index=False)

entry_state_table(vp, vp_edges, "t4a_vote_pend.csv", "vote_pend")
entry_state_table(f20, f20_edges, "t4b_flips20.csv", "flips20")
entry_state_table(sig_pct, sp_edges, "t4c_sigma_pct.csv", "sigma_pct")
print(f"t4 done t={time.time()-t_start:.0f}s", flush=True)

# ---------------------------------------------------------------- T5a loss clustering (trades, same member)
order = np.lexsort((D["eb"], D["vm"]))
streak = np.zeros(nd, int)
prev_vm, prev_loss, run = None, False, 0
for pos_ in order:
    if D["vm"][pos_] != prev_vm:
        run = 0
    streak[pos_] = run
    prev_vm = D["vm"][pos_]
    run = run + 1 if NET[pos_] < 0 else 0
rows = []
for g, gm in groups.items():
    base_p = float((~win)[gm].mean())
    for cond_lab, cm in ([("base", gm)] +
                         [(f"streak>={k}", gm & (streak >= k)) for k in (1, 2, 3)] +
                         [(f"streak=={k}", gm & (streak == k)) for k in (0, 1, 2, 3)]):
        n = int(cm.sum())
        p_pt, p_lo, p_hi = boot_ratio(((~win) & cm).astype(float), cm.astype(float))
        e_pt, e_lo, e_hi = boot_ratio(np.where(cm, NET, 0.0), cm.astype(float))
        rows.append(dict(group=g, cond=cond_lab, n=n,
                         p_loss=p_pt, p_loss_lo=p_lo, p_loss_hi=p_hi,
                         base_p_loss=base_p,
                         mean_net=e_pt, mean_net_lo=e_lo, mean_net_hi=e_hi))
pd.DataFrame(rows).to_csv(f"{TBL}/t5a_loss_clustering_trades.csv", index=False)

# ---------------------------------------------------------------- T5b loss clustering (E10 days)
e10 = pd.read_csv("runs/SM01_SUBSTRATE/out/e10_daily_py.csv")
e10["sess"] = pd.to_datetime(e10["sess"])
e10 = e10[e10["sess"] <= DEV_END].reset_index(drop=True)
x = e10["net"].to_numpy()
nD = len(x)
nbD = int(np.ceil(nD / BLOCK))
startsD = rng.integers(0, nD, (B_BOOT, nbD))   # rng continues after W draws (deterministic)

def day_cond_boot(cond, num, max_off):
    """Within-block bootstrap of ratio sum(num)/sum(cond) over circular index arrays.
    cond/num indexed by 'anchor' day i; offsets 0..max_off-1 valid within a block."""
    pt = num.sum() / cond.sum() if cond.sum() else np.nan
    off = np.arange(max_off)
    gidx = (startsD[:, :, None] + off[None, None, :]).reshape(B_BOOT, -1) % nD
    bn = num[gidx].sum(axis=1); bd = cond[gidx].sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        rr = np.where(bd > 0, bn / bd, np.nan)
    lo, hi = np.nanpercentile(rr, [2.5, 97.5])
    return pt, lo, hi

neg = (x < 0).astype(float)
nxt = np.roll(x, -1); nxt_neg = np.roll(neg, -1)
rows = []
# base
rows.append(dict(cond="base P(day<0)", n=nD, p=float(neg.mean()),
                 p_lo=np.nan, p_hi=np.nan, e_next=float(x.mean()),
                 e_lo=np.nan, e_hi=np.nan))
specs = [
    ("P(day<0 | prior<0)", neg, nxt_neg * neg, nxt * neg, 4),
    ("P(day<0 | prior>=0)", 1 - neg, nxt_neg * (1 - neg), nxt * (1 - neg), 4),
    ("P(day<0 | 2 prior<0)", neg * nxt_neg,
     neg * nxt_neg * np.roll(neg, -2), neg * nxt_neg * np.roll(x, -2), 3),
    ("P(day<0 | 3 prior<0)", neg * nxt_neg * np.roll(neg, -2),
     neg * nxt_neg * np.roll(neg, -2) * np.roll(neg, -3),
     neg * nxt_neg * np.roll(neg, -2) * np.roll(x, -3), 2),
]
for lab, cond, joint, val, moff in specs:
    # drop wrap pairs for the point estimate
    valid = np.ones(nD); valid[nD - (5 - moff) - moff + 1:] = 0  # conservative tail trim
    p_pt = joint[:nD - moff].sum() / cond[:nD - moff].sum() if cond[:nD - moff].sum() else np.nan
    e_pt = val[:nD - moff].sum() / cond[:nD - moff].sum() if cond[:nD - moff].sum() else np.nan
    p_pt2, p_lo, p_hi = day_cond_boot(cond, joint, moff)
    e_pt2, e_lo, e_hi = day_cond_boot(cond, val, moff)
    rows.append(dict(cond=lab, n=int(cond[:nD - moff].sum()), p=p_pt,
                     p_lo=p_lo, p_hi=p_hi, e_next=e_pt, e_lo=e_lo, e_hi=e_hi))
pd.DataFrame(rows).to_csv(f"{TBL}/t5b_loss_clustering_e10.csv", index=False)
print(f"t5 done t={time.time()-t_start:.0f}s", flush=True)

# ---------------------------------------------------------------- T6 right tail
qs = [.10, .25, .50, .75, .90, .95, .98, .99, 1.00]
rows = []
for g, gm in groups.items():
    tm = gm & top1
    n = int(tm.sum())
    if n == 0:
        continue
    maeS_t = maeS[tm]
    k05 = kfe[tm, 0].astype(float); k10 = kfe[tm, 1].astype(float)
    k05[k05 < 0] = np.nan; k10[k10 < 0] = np.nan
    rows.append(dict(
        group=g, n_top1=n, thr_net=float(thr99),
        sum_net=float(NET[tm].sum()),
        share_of_group_net=float(NET[tm].sum() / NET[gm].sum()),
        **{f"maeS_q{int(q*100)}": v for q, v in zip(qs, q_of(maeS_t, qs))},
        m_star_q98_maeS=float(np.quantile(maeS_t, 0.98)),
        **{f"bars_to_halfS_q{int(q*100)}": v for q, v in
           zip([.5, .75, .9, .95, .98, 1.0], q_of(k05[~np.isnan(k05)], [.5, .75, .9, .95, .98, 1.0]))},
        **{f"bars_to_1S_q{int(q*100)}": v for q, v in
           zip([.5, .75, .9, .95, .98, 1.0], q_of(k10[~np.isnan(k10)], [.5, .75, .9, .95, .98, 1.0]))},
        n_never_halfS=int(np.isnan(k05).sum()), n_never_1S=int(np.isnan(k10).sum()),
        med_bars_held=float(np.median(D["held"][tm])),
        med_net=float(np.median(NET[tm]))))
pd.DataFrame(rows).to_csv(f"{TBL}/t6a_right_tail_summary.csv", index=False)

# stop-rule incidence on top-1% trades: rule = "at bar b, if still open and MFE < q*S -> stop"
rows = []
for bi, b in enumerate(B_LIST):
    for q in Q_PROG:
        hit = top1 & open_b[:, bi] & (mfe_b[:, bi] < q * Sd)
        for m_ in [0.0] + M_CROSS[:4]:
            hm = hit & (mae_b[:, bi] >= m_ * Sd) if m_ > 0 else hit
            rows.append(dict(b=b, q=q, m=m_, n_top1_stopped=int(hm.sum()),
                             frac_top1_stopped=float(hm.sum() / n_top1),
                             net_top1_stopped=float(NET[hm].sum()),
                             safe_le_2pct=bool(hm.sum() / n_top1 <= 0.02)))
pd.DataFrame(rows).to_csv(f"{TBL}/t6b_right_tail_stopgrid.csv", index=False)

# top-1% path profile at decision bars
rows = []
for bi, b in enumerate(B_LIST):
    tm = top1 & open_b[:, bi]
    n = int(tm.sum())
    rows.append(dict(
        b=b, n_open=n, frac_open=float(n / n_top1),
        mfeS_q25=float(np.quantile(mfe_b[tm, bi] / Sd[tm], .25)) if n else np.nan,
        mfeS_q50=float(np.quantile(mfe_b[tm, bi] / Sd[tm], .50)) if n else np.nan,
        mfeS_q75=float(np.quantile(mfe_b[tm, bi] / Sd[tm], .75)) if n else np.nan,
        maeS_q50=float(np.quantile(mae_b[tm, bi] / Sd[tm], .50)) if n else np.nan,
        maeS_q90=float(np.quantile(mae_b[tm, bi] / Sd[tm], .90)) if n else np.nan,
        maeS_q98=float(np.quantile(mae_b[tm, bi] / Sd[tm], .98)) if n else np.nan))
pd.DataFrame(rows).to_csv(f"{TBL}/t6c_right_tail_path.csv", index=False)

s_val_df.to_csv(f"{TBL}/t0_s_validation.csv", index=False)

# ---------------------------------------------------------------- headline json
head = dict(
    n_trades_total=n_tr, n_trades_dev=nd, n_sessions_dev=nsess,
    dev_net=float(NET.sum()), dev_gross_loss=float(loss_total),
    win_rate=float(win.mean()), thr99_net=float(thr99), n_top1=n_top1,
    top1_net=float(NET[top1].sum()), top1_share=float(NET[top1].sum() / NET.sum()),
    e10_dev_days=nD, e10_dev_net=float(x.sum()),
    s_entry_exact_max_diff_vs_formula=float(s_val_df["value"][0]),
    runtime_s=round(time.time() - t_start, 1))
with open(f"{OUT}/headline.json", "w") as f:
    json.dump(head, f, indent=1)
print(json.dumps(head, indent=1), flush=True)
print("DONE", flush=True)
