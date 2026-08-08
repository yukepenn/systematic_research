"""W4-E CLEAN_MOVE labels + path ordering. Spec: specs/W4_alpha_wave1.md section W4-E
(frozen before readout). LABELS ONLY — no trade rule, no P&L. Seed 20260808.

CLEAN(H=60s) at second t (RTH & quote-alive): path over (t, t+60]. UP with magnitude
M in {16,20,24,32} and MAE bound K in {6,8}: +M reached BEFORE mid ever drops K below
mid_last(t); per-second hi/lo scan; conservative: both crossed same second -> MAE-violated
(not clean). DOWN symmetric. Plain = MFE >= M within 60s (census logic equivalent).
Path ordering on every-30s RTH clock: tt(+8) vs tt(-4), pre-target drawdown for +20
reachers (touch-second included, conservative), time-underwater fraction over 60s.
Directional pre-state on (20,6): UP-clean vs DOWN-clean, and clean vs dirty per dir."""
import glob, os
import numpy as np, pandas as pd
from numba import njit

H = 60
MS = [16, 20, 24, 32]
KS = [6, 8]
TGT_THR = np.array([8.0, 16.0, 20.0, 24.0, 32.0])   # index 0 is the path-order +8
ADV_THR = np.array([4.0, 6.0, 8.0])                  # index 0 is the path-order -4
JM = {16: 1, 20: 2, 24: 3, 32: 4}
JK = {6: 1, 8: 2}
PTM = 20.0                                           # pre-target drawdown magnitude
BLOCKS = [("0930_1030", 9*3600+1800, 10*3600+1800), ("1030_1200", 10*3600+1800, 12*3600),
          ("1200_1400", 12*3600, 14*3600), ("1400_1600", 14*3600, 16*3600)]
SEED = 20260808

@njit(cache=True)
def crosses(ml, hi, lo, H, tgt_thr, adv_thr, dirsign):
    """First-cross times (seconds after t, path (t, t+H]) for favorable thresholds
    (tgt_thr) and adverse thresholds (adv_thr). -1 = not crossed within horizon."""
    n = ml.shape[0]
    nt = tgt_thr.shape[0]; na = adv_thr.shape[0]
    tt_t = np.full((n, nt), -1, np.int32)
    tt_a = np.full((n, na), -1, np.int32)
    for t in range(n):
        m0 = ml[t]
        end = min(t + H, n - 1)
        found = 0
        for i in range(t + 1, end + 1):
            if dirsign == 1:
                fav = hi[i] - m0; adv = m0 - lo[i]
            else:
                fav = m0 - lo[i]; adv = hi[i] - m0
            for j in range(nt):
                if tt_t[t, j] < 0 and fav >= tgt_thr[j]:
                    tt_t[t, j] = i - t; found += 1
            for j in range(na):
                if tt_a[t, j] < 0 and adv >= adv_thr[j]:
                    tt_a[t, j] = i - t; found += 1
            if found == nt + na:
                break
    return tt_t, tt_a

@njit(cache=True)
def epi_starts(flags, H):
    """Episode collapse with refractory H seconds; returns start indices."""
    n = flags.shape[0]
    out = np.empty(n, np.int64)
    m = 0; nxt = -1
    for t in range(n):
        if flags[t] and t >= nxt:
            out[m] = t; m += 1; nxt = t + H
    return out[:m]

@njit(cache=True)
def fwd_extrema(hi, lo, H):
    n = hi.shape[0]
    fmax = np.full(n, np.nan); fmin = np.full(n, np.nan)
    for t in range(n):
        e = min(t + H, n - 1)
        if t + 1 > e: continue
        mx = hi[t+1]; mn = lo[t+1]
        for i in range(t+2, e+1):
            if hi[i] > mx: mx = hi[i]
            if lo[i] < mn: mn = lo[i]
        fmax[t] = mx; fmin[t] = mn
    return fmax, fmin

@njit(cache=True)
def path_stats(ml, hi, lo, starts, H, dirsign, M):
    """Per start: reach flag for +M within (t,t+H], pre-target drawdown (max adverse
    up to AND INCLUDING the touch second — conservative), underwater fraction of the
    full window (mid_last beyond entry on the adverse side)."""
    ns = starts.shape[0]
    n = ml.shape[0]
    reach = np.zeros(ns, np.uint8)
    dd = np.full(ns, np.nan)
    uw = np.full(ns, np.nan)
    for s in range(ns):
        t0 = starts[s]; m0 = ml[t0]
        end = min(t0 + H, n - 1)
        if end <= t0: continue
        cnt = 0; tot = 0
        maxadv = 0.0; touched = False; ddv = 0.0
        for i in range(t0 + 1, end + 1):
            if dirsign == 1:
                fav = hi[i] - m0; adv = m0 - lo[i]; under = ml[i] < m0
            else:
                fav = m0 - lo[i]; adv = hi[i] - m0; under = ml[i] > m0
            tot += 1
            if under: cnt += 1
            if not touched:
                if adv > maxadv: maxadv = adv
                if fav >= M:
                    touched = True; ddv = maxadv
        uw[s] = cnt / tot
        if touched:
            reach[s] = 1; dd[s] = ddv
    return reach, dd, uw

SH = "research/scalping_lab/substrate/sechilo/NQ"
GR = "research/scalping_lab/substrate/grid1s/NQ"
OUTD = "research/scalping_lab/artifacts/w4_cleanmove"
os.makedirs(OUTD, exist_ok=True)

FEATS = ["ret5", "ret10", "ret30", "ret60", "rv60", "eff60", "sflow10", "sflow60",
         "spread_t", "spread60", "trades10", "dist_hi", "dist_lo"]

count_rows, po_rows, feat_frames = [], [], []
po_samples = {d: {"tt8": [], "tt4": [], "dd": [], "uw": []} for d in ("up", "dn")}
mismatch_total = 0

sessions = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(SH, "s*.parquet")))
print(f"sessions: {len(sessions)}", flush=True)
for tag in sessions:
    d = pd.to_datetime(tag[1:], format="%Y%m%d")
    g = pd.read_parquet(os.path.join(GR, tag + ".parquet"))
    s = pd.read_parquet(os.path.join(SH, tag + ".parquet"))
    g["time"] = pd.to_datetime(g["time"]); s["time"] = pd.to_datetime(s["time"])
    f = g.merge(s, on="time", how="left")
    f["mid_last"] = f["mid_last"].ffill()
    f = f[f["mid_last"].notna()].reset_index(drop=True)
    f["mid_high"] = f["mid_high"].fillna(f["mid_last"])
    f["mid_low"] = f["mid_low"].fillna(f["mid_last"])
    ml = f["mid_last"].values; hi = f["mid_high"].values; lo = f["mid_low"].values
    n = len(f)
    tod = (f["time"] - d).dt.total_seconds().values
    rth = (tod >= 9*3600+1800) & (tod < 16*3600)
    upd = (f["bid_upd"] + f["ask_upd"]).values
    upd60 = pd.Series(upd).rolling(60, min_periods=1).sum().values
    dec = rth & (upd60 > 0)
    dec_idx = np.where(dec)[0]
    if len(dec_idx) == 0: continue

    tt = {}
    for dname, dv in (("up", 1), ("dn", -1)):
        tt[dname] = crosses(ml, hi, lo, H, TGT_THR, ADV_THR, dv)

    # internal consistency check: tt-based plain(M=20) == census fwd_extrema logic
    fx, fn = fwd_extrema(hi, lo, H)
    for dname, amt in (("up", fx - ml), ("dn", ml - fn)):
        pl_tt = tt[dname][0][:, JM[20]] > 0
        pl_fx = np.where(np.isnan(amt), False, amt >= 20)
        mismatch_total += int((pl_tt[dec_idx] != pl_fx[dec_idx]).sum())

    # ---- deliverable 1: CLEAN frequency map ----
    for dname in ("up", "dn"):
        tt_t, tt_a = tt[dname]
        for M in MS:
            tm = tt_t[:, JM[M]]
            plain = np.zeros(n, np.bool_); plain[dec_idx] = tm[dec_idx] > 0
            pe = epi_starts(plain, H)
            for K in KS:
                ta = tt_a[:, JK[K]]
                cl = np.zeros(n, np.bool_)
                cl[dec_idx] = (tm[dec_idx] > 0) & ((ta[dec_idx] < 0) | (tm[dec_idx] < ta[dec_idx]))
                ce = epi_starts(cl, H)
                dirty = plain & ~cl
                de = epi_starts(dirty, H)
                blk = {f"blk_{b[0]}": int(((tod[ce] >= b[1]) & (tod[ce] < b[2])).sum())
                       for b in BLOCKS}
                count_rows.append(dict(session=tag, dir=dname, M=M, K=K,
                                       dec_secs=len(dec_idx),
                                       clean_raw=int(cl.sum()), clean_epi=len(ce),
                                       plain_raw=int(plain.sum()), plain_epi=len(pe),
                                       dirty_raw=int(dirty.sum()), dirty_epi=len(de), **blk))

    # ---- deliverable 2: path ordering, every-30s RTH clock ----
    st30 = dec_idx[::30].astype(np.int64)
    for dname, dv in (("up", 1), ("dn", -1)):
        tt_t, tt_a = tt[dname]
        tt8 = tt_t[st30, 0]; tt4 = tt_a[st30, 0]
        p8first = (tt8 > 0) & ((tt4 < 0) | (tt8 < tt4))
        m4first = (tt4 > 0) & ((tt8 < 0) | (tt4 < tt8))
        tie = (tt8 > 0) & (tt4 > 0) & (tt8 == tt4)
        neither = (tt8 < 0) & (tt4 < 0)
        reach, ddv, uwv = path_stats(ml, hi, lo, st30, H, dv, PTM)
        po_rows.append(dict(session=tag, dir=dname, n30=len(st30),
                            n_p8first=int(p8first.sum()), n_m4first=int(m4first.sum()),
                            n_tie=int(tie.sum()), n_neither=int(neither.sum()),
                            n_reach20=int(reach.sum()),
                            n_dd_le6=int((ddv[reach == 1] < 6).sum()),
                            n_dd_le8=int((ddv[reach == 1] < 8).sum()),
                            uw_sum=float(np.nansum(uwv)), uw_n=int((~np.isnan(uwv)).sum())))
        po_samples[dname]["tt8"].append(tt8[tt8 > 0])
        po_samples[dname]["tt4"].append(tt4[tt4 > 0])
        po_samples[dname]["dd"].append(ddv[reach == 1])
        po_samples[dname]["uw"].append(uwv[~np.isnan(uwv)])

    # ---- deliverable 3: features at (20,6) clean/dirty episode starts ----
    mls = pd.Series(ml); dmid = mls.diff()
    tv60 = dmid.abs().rolling(60).sum().values
    ret60 = mls.diff(60).values
    F = pd.DataFrame({
        "ret5": mls.diff(5).values, "ret10": mls.diff(10).values,
        "ret30": mls.diff(30).values, "ret60": ret60,
        "rv60": dmid.rolling(60).std().values,
        "eff60": np.abs(ret60) / np.where(tv60 > 0, tv60, np.nan),
        "sflow10": pd.Series(f["sflow"].values).rolling(10).sum().values,
        "sflow60": pd.Series(f["sflow"].values).rolling(60).sum().values,
        "spread_t": f["spread_t"].values,
        "spread60": pd.Series(f["spread_t"].values).rolling(60).mean().values,
        "trades10": pd.Series(f["trades"].values).rolling(10).sum().values,
        "dist_hi": np.maximum.accumulate(hi) - ml,
        "dist_lo": ml - np.minimum.accumulate(lo)})
    for dname in ("up", "dn"):
        tt_t, tt_a = tt[dname]
        tm = tt_t[:, JM[20]]; ta = tt_a[:, JK[6]]
        cl = np.zeros(n, np.bool_)
        cl[dec_idx] = (tm[dec_idx] > 0) & ((ta[dec_idx] < 0) | (tm[dec_idx] < ta[dec_idx]))
        plain = np.zeros(n, np.bool_); plain[dec_idx] = tm[dec_idx] > 0
        dirty = plain & ~cl
        for gname, mask in ((f"{dname}_clean", cl), (f"{dname}_dirty", dirty)):
            st = epi_starts(mask, H)
            if len(st) == 0: continue
            sub = F.iloc[st].copy()
            sub["session"] = tag; sub["group"] = gname
            feat_frames.append(sub)
    print(tag, "done", flush=True)

C = pd.DataFrame(count_rows); C.to_csv(os.path.join(OUTD, "w4e_clean_by_session.csv"), index=False)
PO = pd.DataFrame(po_rows); PO.to_csv(os.path.join(OUTD, "w4e_pathorder_by_session.csv"), index=False)
FE = pd.concat(feat_frames, ignore_index=True)
FE.to_csv(os.path.join(OUTD, "w4e_feature_rows.csv"), index=False)
nsess = C["session"].nunique()
print(f"\nplain-label consistency check vs census fwd_extrema (M=20, both dirs, dec secs): "
      f"mismatches = {mismatch_total}")

# ---------- pooled: CLEAN frequency map ----------
print(f"\n=== W4-E CLEAN(H=60s) FREQUENCY MAP (pooled over {nsess} sessions) ===")
print(f"{'dir':>4} {'M':>3} {'K':>2} | {'clean_raw':>9} {'clean_epi':>9} {'epi/day':>7} "
      f"{'udays':>5} | {'plain_raw':>9} {'plain_epi':>9} | {'cfrac_raw':>9} {'cfrac_epi':>9} "
      f"| {'b0930':>5} {'b1030':>5} {'b1200':>5} {'b1400':>5}")
fm_rows = []
for dname in ("up", "dn"):
    for M in MS:
        for K in KS:
            gph = C[(C.dir == dname) & (C.M == M) & (C.K == K)]
            cr = gph.clean_raw.sum(); ce = gph.clean_epi.sum()
            pr = gph.plain_raw.sum(); pe = gph.plain_epi.sum()
            ud = int((gph.clean_epi > 0).sum())
            fr = cr / pr if pr else np.nan
            fe = ce / pe if pe else np.nan
            b = [gph[f"blk_{x[0]}"].sum() for x in BLOCKS]
            print(f"{dname:>4} {M:>3} {K:>2} | {cr:>9} {ce:>9} {ce/nsess:>7.2f} {ud:>5} | "
                  f"{pr:>9} {pe:>9} | {fr:>9.4f} {fe:>9.4f} | "
                  f"{b[0]:>5} {b[1]:>5} {b[2]:>5} {b[3]:>5}")
            fm_rows.append(dict(dir=dname, M=M, K=K, clean_raw=int(cr), clean_epi=int(ce),
                                epi_per_day=round(ce/nsess, 3), unique_days=ud,
                                plain_raw=int(pr), plain_epi=int(pe),
                                cleanfrac_raw=round(fr, 4), cleanfrac_epi=round(fe, 4),
                                blk_0930_1030=int(b[0]), blk_1030_1200=int(b[1]),
                                blk_1200_1400=int(b[2]), blk_1400_1600=int(b[3])))
pd.DataFrame(fm_rows).to_csv(os.path.join(OUTD, "w4e_freqmap.csv"), index=False)
print("(clean_raw/plain_raw = flagged decision seconds; episodes = refractory 60s; "
      "epi/day over all sessions; block mix = clean EPISODE starts per time block; "
      "cfrac = clean/plain)")

# ---------- pooled: path ordering ----------
brng = np.random.default_rng(SEED)
print("\n=== W4-E PATH ORDERING, every-30s RTH clock, horizon 60s ===")
po_sum = []
for dname in ("up", "dn"):
    gph = PO[PO.dir == dname]
    n30 = gph.n30.sum()
    p8 = gph.n_p8first.sum(); m4 = gph.n_m4first.sum()
    tie = gph.n_tie.sum(); nei = gph.n_neither.sum()
    # day-clustered CI on P(+8 first): resample sessions, 1000 reps
    a = gph.n_p8first.values.astype(float); b = gph.n30.values.astype(float)
    idx = np.arange(len(gph))
    boots = []
    for _ in range(1000):
        r = brng.choice(idx, len(idx), replace=True)
        boots.append(a[r].sum() / b[r].sum())
    tt8 = np.concatenate(po_samples[dname]["tt8"])
    tt4 = np.concatenate(po_samples[dname]["tt4"])
    dd = np.concatenate(po_samples[dname]["dd"])
    uwv = np.concatenate(po_samples[dname]["uw"])
    nr = gph.n_reach20.sum()
    lbl = "long(+8/-4)" if dname == "up" else "short(-8/+4)"
    print(f"\n[{lbl}] n_starts={n30}")
    print(f"  P(fav 8t first)={p8/n30:.4f} [CI {np.percentile(boots,2.5):.4f},"
          f" {np.percentile(boots,97.5):.4f}]  P(adv 4t first)={m4/n30:.4f}  "
          f"P(same-sec tie->adverse)={tie/n30:.4f}  P(neither in 60s)={nei/n30:.4f}")
    print(f"  tt(fav8) given reached (n={len(tt8)}): p25={np.percentile(tt8,25):.0f}s "
          f"p50={np.percentile(tt8,50):.0f}s p75={np.percentile(tt8,75):.0f}s "
          f"p90={np.percentile(tt8,90):.0f}s")
    print(f"  tt(adv4) given reached (n={len(tt4)}): p25={np.percentile(tt4,25):.0f}s "
          f"p50={np.percentile(tt4,50):.0f}s p75={np.percentile(tt4,75):.0f}s "
          f"p90={np.percentile(tt4,90):.0f}s")
    print(f"  reach +20t within 60s: n={nr} ({nr/n30:.4f} of starts); pre-target drawdown "
          f"(ticks, touch-sec incl): p25={np.percentile(dd,25):.2f} p50={np.percentile(dd,50):.2f} "
          f"p75={np.percentile(dd,75):.2f} p90={np.percentile(dd,90):.2f} p95={np.percentile(dd,95):.2f}")
    print(f"  P(dd<6 | reach20)={gph.n_dd_le6.sum()/nr:.4f}  P(dd<8 | reach20)={gph.n_dd_le8.sum()/nr:.4f}")
    print(f"  time-underwater fraction over 60s: mean={uwv.mean():.4f} "
          f"p25={np.percentile(uwv,25):.4f} p50={np.percentile(uwv,50):.4f} "
          f"p75={np.percentile(uwv,75):.4f} p90={np.percentile(uwv,90):.4f}")
    po_sum.append(dict(dir=dname, n30=int(n30), p_fav8_first=round(p8/n30, 4),
                       ci_lo=round(np.percentile(boots, 2.5), 4),
                       ci_hi=round(np.percentile(boots, 97.5), 4),
                       p_adv4_first=round(m4/n30, 4), p_tie=round(tie/n30, 4),
                       p_neither=round(nei/n30, 4),
                       tt8_p50=float(np.percentile(tt8, 50)), tt4_p50=float(np.percentile(tt4, 50)),
                       n_reach20=int(nr), dd_p50=round(float(np.percentile(dd, 50)), 2),
                       dd_p90=round(float(np.percentile(dd, 90)), 2),
                       p_dd_lt6=round(gph.n_dd_le6.sum()/nr, 4),
                       p_dd_lt8=round(gph.n_dd_le8.sum()/nr, 4),
                       uw_mean=round(float(uwv.mean()), 4),
                       uw_p50=round(float(np.percentile(uwv, 50)), 4)))
pd.DataFrame(po_sum).to_csv(os.path.join(OUTD, "w4e_pathorder_summary.csv"), index=False)

# ---------- pooled: feature contrasts on (20,6) episodes ----------
def med_ci(A, Bd, feat, reps=500):
    ev = A.groupby("session")[feat].apply(lambda x: x.dropna().values)
    ct = Bd.groupby("session")[feat].apply(lambda x: x.dropna().values)
    de = np.concatenate(ev.values) if len(ev) else np.array([])
    dc = np.concatenate(ct.values) if len(ct) else np.array([])
    if len(de) < 20 or len(dc) < 20: return None
    md = np.median(de) - np.median(dc)
    iqr = np.subtract(*np.percentile(np.concatenate([de, dc]), [75, 25]))
    boots = []
    for _ in range(reps):
        se = brng.choice(len(ev), len(ev), replace=True)
        sc = brng.choice(len(ct), len(ct), replace=True)
        be = np.concatenate([ev.iloc[i] for i in se]); bc = np.concatenate([ct.iloc[i] for i in sc])
        if len(be) and len(bc): boots.append(np.median(be) - np.median(bc))
    return dict(med_A=round(float(np.median(de)), 4), med_B=round(float(np.median(dc)), 4),
                med_diff=round(float(md), 4),
                effect=round(float(md / iqr), 4) if iqr > 0 else np.nan,
                ci_lo=round(float(np.percentile(boots, 2.5)), 4),
                ci_hi=round(float(np.percentile(boots, 97.5)), 4),
                n_A=len(de), n_B=len(dc))

grp = {g: FE[FE.group == g] for g in ("up_clean", "dn_clean", "up_dirty", "dn_dirty")}
print("\n=== W4-E PRE-STATE (M=20,K=6) episode counts by group ===")
for g, df in grp.items():
    print(f"  {g}: n={len(df)} sessions={df['session'].nunique()}")

frows = []
CONTRASTS = [("up_clean", "dn_clean", "upclean_vs_dnclean"),
             ("up_clean", "up_dirty", "upclean_vs_updirty"),
             ("dn_clean", "dn_dirty", "dnclean_vs_dndirty")]
for ga, gb, cname in CONTRASTS:
    print(f"\n=== {cname}: median diff / pooled IQR, day-clustered 95% CI (500 reps) ===")
    print(f"{'feature':>10} | {'med_A':>9} {'med_B':>9} {'med_diff':>9} {'effect':>8} "
          f"{'ci_lo':>9} {'ci_hi':>9} | {'n_A':>5} {'n_B':>5} {'sig':>3}")
    for feat in FEATS:
        r = med_ci(grp[ga], grp[gb], feat)
        if r is None: continue
        sig = "*" if (r["ci_lo"] > 0 or r["ci_hi"] < 0) else ""
        print(f"{feat:>10} | {r['med_A']:>9} {r['med_B']:>9} {r['med_diff']:>+9} "
              f"{r['effect']:>+8} {r['ci_lo']:>+9} {r['ci_hi']:>+9} | {r['n_A']:>5} {r['n_B']:>5} {sig:>3}")
        frows.append(dict(contrast=cname, feature=feat, **r))
FR = pd.DataFrame(frows); FR.to_csv(os.path.join(OUTD, "w4e_features.csv"), index=False)
print("\n(A = first group, B = second group; sig * = day-clustered 95% CI excludes 0)")
print("\nW4E DONE")
