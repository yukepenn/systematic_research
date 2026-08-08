"""W2-1 FAST_STRUCTURAL_OPPORTUNITY_CENSUS + wide excursion surface.
Spec: specs/W2-1_fast_opportunity_census.md (frozen before readout). Seed 20260808.
LABELS + descriptive conditional distributions only — no rule P&L here."""
import glob, os
import numpy as np, pandas as pd
from numba import njit

HGRID = [5, 10, 20, 30, 45, 60, 90, 120, 180, 300]
MGRID = [8, 12, 16, 20, 24, 32]
CHAR = [(60, 20), (30, 12), (120, 24)]          # frozen characterization labels
PAIRS = [(8,4),(12,4),(16,6),(20,6),(20,8),(24,8),(32,10)]
MFEH = [5, 10, 20, 30, 45, 60, 90, 120]
CAP = 600
BLOCKS = [("0930_1030", 9*3600+1800, 10*3600+1800), ("1030_1200", 10*3600+1800, 12*3600),
          ("1200_1400", 12*3600, 14*3600), ("1400_1600", 14*3600, 16*3600)]

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
def episodes(flags, H):
    n = flags.shape[0]; cnt = 0; nxt = -1
    for t in range(n):
        if flags[t] and t >= nxt:
            cnt += 1; nxt = t + H
    return cnt

@njit(cache=True)
def barrier(ml, hi, lo, starts, d, A, B, cap):
    tgt = 0; adv = 0; nei = 0
    n = ml.shape[0]
    for s in range(starts.shape[0]):
        t0 = starts[s]; m0 = ml[t0]
        end = min(t0 + cap, n - 1)
        res = 0
        for i in range(t0+1, end+1):
            up = hi[i] - m0; dn = m0 - lo[i]
            if d == 1:
                t_hit = up >= A; a_hit = dn >= B
            else:
                t_hit = dn >= A; a_hit = up >= B
            if t_hit and a_hit: res = 2; break     # same-second ambiguity -> adverse
            if a_hit: res = 2; break
            if t_hit: res = 1; break
        if res == 1: tgt += 1
        elif res == 2: adv += 1
        else: nei += 1
    return tgt, adv, nei

@njit(cache=True)
def t2mfe(ml, hi, lo, starts, H):
    out = np.full(starts.shape[0], np.nan)
    n = ml.shape[0]
    for s in range(starts.shape[0]):
        t0 = starts[s]; e = min(t0 + H, n - 1)
        if t0 + 1 > e: continue
        best = -1e18; bi = t0+1
        for i in range(t0+1, e+1):
            if hi[i] - ml[t0] > best: best = hi[i] - ml[t0]; bi = i
        out[s] = bi - t0
    return out

SH = "research/scalping_lab/substrate/sechilo/NQ"
GR = "research/scalping_lab/substrate/grid1s/NQ"
OUTD = "research/scalping_lab/artifacts/census"
os.makedirs(OUTD, exist_ok=True)
rng = np.random.default_rng(20260808)

count_rows, feat_frames, surf_rows, mfe_samples = [], [], [], {h: {"MFE": [], "MAE": []} for h in MFEH}
t2m_samples = {60: [], 120: []}

sessions = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(SH, "s*.parquet")))
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
    f["n_ev"] = f["n_ev"].fillna(0)
    ml = f["mid_last"].values; hi = f["mid_high"].values; lo = f["mid_low"].values
    n = len(f)
    tod = (f["time"] - d).dt.total_seconds().values   # seconds relative to session END date midnight
    rth = (tod >= 9*3600+1800) & (tod < 16*3600)
    upd = (f["bid_upd"] + f["ask_upd"]).values
    upd60 = pd.Series(upd).rolling(60, min_periods=1).sum().values
    alive = upd60 > 0                                  # data-quality: quotes seen in last 60s
    dec = rth & alive
    dec_idx = np.where(dec)[0]
    if len(dec_idx) == 0: continue

    fx = {}; fn = {}
    for H in HGRID:
        fx[H], fn[H] = fwd_extrema(hi, lo, H)

    # --- deliverable 1: counts ---
    for H in HGRID:
        up_amt = fx[H] - ml; dn_amt = ml - fn[H]
        for M in MGRID:
            for dname, amt in (("up", up_amt), ("dn", dn_amt)):
                fl = np.zeros(n, np.bool_); fl[dec_idx] = amt[dec_idx] >= M
                raw = int(fl.sum())
                epi = episodes(fl, H)
                blk = {b[0]: int(fl[(tod >= b[1]) & (tod < b[2])].sum()) for b in BLOCKS}
                count_rows.append(dict(session=tag, H=H, M=M, dir=dname, raw=raw, episodes=epi,
                                       dec_secs=len(dec_idx), **blk))

    # --- features (trailing, causal) ---
    mls = pd.Series(ml); dmid = mls.diff()
    F = pd.DataFrame({"session": tag, "t": np.arange(n), "tod": tod})
    for k in (5, 10, 30, 60, 300): F[f"ret{k}"] = mls.diff(k).values
    F["rv60"] = dmid.rolling(60).std().values
    F["rv300"] = dmid.rolling(300).std().values
    tv60 = dmid.abs().rolling(60).sum().values
    F["tv60"] = tv60
    F["eff60"] = np.abs(F["ret60"]) / np.where(tv60 > 0, tv60, np.nan)
    F["range300"] = (pd.Series(hi).rolling(300).max() - pd.Series(lo).rolling(300).min()).values
    shi = np.maximum.accumulate(hi); slo = np.minimum.accumulate(lo)
    F["dist_hi"] = shi - ml; F["dist_lo"] = ml - slo
    hidx = pd.Series(np.where(hi >= shi - 1e-9, np.arange(n), np.nan)).ffill().values
    lidx = pd.Series(np.where(lo <= slo + 1e-9, np.arange(n), np.nan)).ffill().values
    F["secs_since_hi"] = np.arange(n) - hidx; F["secs_since_lo"] = np.arange(n) - lidx
    for k in (10, 60):
        F[f"trades{k}"] = pd.Series(f["trades"].values).rolling(k).sum().values
        F[f"vol{k}"] = pd.Series(f["vol"].values).rolling(k).sum().values
        F[f"upd{k}"] = pd.Series(upd).rolling(k).sum().values
        F[f"sflow{k}"] = pd.Series(f["sflow"].values).rolling(k).sum().values
    F["act_accel"] = F["trades10"] / np.where(F["trades60"] > 0, F["trades60"] / 6.0, np.nan)
    F["nsflow60"] = F["sflow60"] / np.where(F["vol60"] > 0, F["vol60"], np.nan)
    F["spread"] = f["spread_t"].values
    F["spread60"] = pd.Series(f["spread_t"].values).rolling(60).mean().values
    for (H, M) in CHAR:
        F[f"fwdup_{H}"] = fx[H] - ml
        F[f"fwddn_{H}"] = ml - fn[H]
    F["dec"] = dec
    feat_frames.append(F[F["dec"] & (F["t"] >= 300)].astype({c: np.float32 for c in F.columns
                       if c not in ("session", "dec")}, errors="ignore"))

    # --- excursion surface + MFE/MAE (every-30s clock) ---
    st30 = dec_idx[::30].astype(np.int64)
    for (A, B) in PAIRS:
        for dname, dv in (("long", 1), ("short", -1)):
            tgt, adv, nei = barrier(ml, hi, lo, st30, dv, float(A), float(B), CAP)
            surf_rows.append(dict(session=tag, A=A, B=B, dir=dname, tgt=tgt, adv=adv, nei=nei))
    for H in MFEH:
        mfe_samples[H]["MFE"].append((fx[H] - ml)[st30])
        mfe_samples[H]["MAE"].append((ml - fn[H])[st30])
    for H in (60, 120):
        t2m_samples[H].append(t2mfe(ml, hi, lo, st30, H))
    print(tag, "done", flush=True)

C = pd.DataFrame(count_rows); C.to_csv(os.path.join(OUTD, "census_counts.csv"), index=False)
S = pd.DataFrame(surf_rows); S.to_csv(os.path.join(OUTD, "excursion_surface_by_session.csv"), index=False)
FA = pd.concat(feat_frames, ignore_index=True)

# ---------- pooled outputs ----------
print("\n=== OPPORTUNITY MAP (episodes/day, mean across sessions) ===")
em = C.groupby(["H", "M", "dir"]).apply(lambda g: g["episodes"].sum() / g["session"].nunique()).unstack("dir")
piv = em.unstack("M")
print(piv.round(1).to_string())

print("\n=== flag rate P(label) pooled (raw flagged secs / decision secs) ===")
pr = C.groupby(["H", "M"]).apply(lambda g: g["raw"].sum() / g["dec_secs"].sum()).unstack("M")
print((100*pr).round(2).to_string())

print("\n=== block mix for primary label (H=60,M=20), episodes summed ===")
c1 = C[(C.H == 60) & (C.M == 20)]
print(c1.groupby("dir")[[b[0] for b in BLOCKS]].sum().to_string())

# excursion surface pooled + break-evens
print("\n=== EXCURSION SURFACE (pooled, every-30s RTH clock, cap 600s) ===")
rows_out = []
brng = np.random.default_rng(20260808)
for (A, B) in PAIRS:
    for dname in ("long", "short"):
        g = S[(S.A == A) & (S.B == B) & (S.dir == dname)]
        T, V, N = g.tgt.sum(), g.adv.sum(), g.nei.sum()
        dec_n = T + V
        p = T / dec_n if dec_n else np.nan
        ps = (g.tgt / (g.tgt + g.adv).replace(0, np.nan)).dropna().values
        b = [np.mean(brng.choice(ps, len(ps), replace=True)) for _ in range(1000)]
        be1 = (B + 2.872) / (A + B); be2 = (B + 4.872) / (A + B)
        rows_out.append(dict(A=A, B=B, dir=dname, p_target=round(p, 4),
                             ci_lo=round(np.percentile(b, 2.5), 4), ci_hi=round(np.percentile(b, 97.5), 4),
                             p_neither=round(N / (T + V + N), 4), n=int(T + V + N),
                             be_c1=round(be1, 4), be_c2=round(be2, 4), gap_c1=round(be1 - p, 4)))
SO = pd.DataFrame(rows_out); SO.to_csv(os.path.join(OUTD, "excursion_surface.csv"), index=False)
print(SO.to_string(index=False))

print("\n=== MFE/MAE quantiles (ticks, long side, pooled 30s clock) ===")
mm = []
for H in MFEH:
    a = np.concatenate(mfe_samples[H]["MFE"]); e = np.concatenate(mfe_samples[H]["MAE"])
    a = a[~np.isnan(a)]; e = e[~np.isnan(e)]
    mm.append(dict(H=H, MFE_p50=np.percentile(a, 50), MFE_p75=np.percentile(a, 75),
                   MFE_p90=np.percentile(a, 90), MFE_p95=np.percentile(a, 95), MFE_p99=np.percentile(a, 99),
                   MAE_p50=np.percentile(e, 50), MAE_p90=np.percentile(e, 90), MAE_p99=np.percentile(e, 99)))
MM = pd.DataFrame(mm).round(2); MM.to_csv(os.path.join(OUTD, "census_mfemae.csv"), index=False)
print(MM.to_string(index=False))
for H in (60, 120):
    v = np.concatenate(t2m_samples[H]); v = v[~np.isnan(v)]
    print(f"time-to-MFE H={H}: p50={np.percentile(v,50):.0f}s p90={np.percentile(v,90):.0f}s")

# ---------- pre-state characterization (3 frozen labels) ----------
FEATS = [c for c in FA.columns if c not in ("session", "t", "tod", "dec")
         and not c.startswith("fwdup") and not c.startswith("fwddn")]
FA["block"] = pd.cut(FA["tod"], bins=[b[1] for b in BLOCKS] + [16*3600],
                     labels=[b[0] for b in BLOCKS], right=False)
FA["rvq"] = pd.qcut(FA["rv60"], 5, labels=False)
frows, udrows = [], []
for (H, M) in CHAR:
    fup = FA[f"fwdup_{H}"].values; fdn = FA[f"fwddn_{H}"].values
    lim = min(8.0, M / 2.0)
    is_up = fup >= M; is_dn = fdn >= M
    ctrl_ok = (fup < lim) & (fdn < lim)
    # episode collapse per session on the pooled frame
    def epi_mask(mask):
        out = np.zeros(len(FA), np.bool_)
        for sess, gidx in FA.groupby("session").groups.items():
            gi = np.asarray(gidx)
            tvals = FA["t"].values[gi]; m = mask[gi]
            nxt = -1e18
            for j in np.where(m)[0]:
                if tvals[j] >= nxt:
                    out[gi[j]] = True; nxt = tvals[j] + H
        return out
    eup = epi_mask(is_up); edn = epi_mask(is_dn)
    # controls: same block + same rv quintile + ctrl_ok, 4 per episode
    ctrl_pool = FA[ctrl_ok & FA["rvq"].notna()]
    def draw_controls(emask):
        keys = FA.loc[emask, ["block", "rvq"]]
        picks = []
        for (bl, q), cnt in keys.value_counts().items():
            pool = ctrl_pool[(ctrl_pool["block"] == bl) & (ctrl_pool["rvq"] == q)]
            if len(pool) == 0: continue
            picks.append(pool.sample(n=min(4 * cnt, len(pool)), random_state=20260808))
        return pd.concat(picks) if picks else ctrl_pool.iloc[:0]
    cup = draw_controls(eup); cdn = draw_controls(edn)
    def med_ci(ev_df, ct_df, feat):
        ev = ev_df.groupby("session")[feat].apply(lambda x: x.dropna().values)
        ct = ct_df.groupby("session")[feat].apply(lambda x: x.dropna().values)
        de = np.concatenate(ev.values) if len(ev) else np.array([])
        dc = np.concatenate(ct.values) if len(ct) else np.array([])
        if len(de) < 20 or len(dc) < 20: return None
        md = np.median(de) - np.median(dc)
        iqr = np.subtract(*np.percentile(np.concatenate([de, dc]), [75, 25]))
        boots = []
        sess_e = list(ev.index); sess_c = list(ct.index)
        for _ in range(500):
            se = brng.choice(len(sess_e), len(sess_e), replace=True)
            sc = brng.choice(len(sess_c), len(sess_c), replace=True)
            be = np.concatenate([ev.iloc[i] for i in se]); bc = np.concatenate([ct.iloc[i] for i in sc])
            if len(be) and len(bc): boots.append(np.median(be) - np.median(bc))
        return dict(med_evt=np.median(de), med_ctrl=np.median(dc), med_diff=md,
                    effect=md / iqr if iqr > 0 else np.nan, n_evt=len(de), n_ctrl=len(dc),
                    ci_lo=np.percentile(boots, 2.5), ci_hi=np.percentile(boots, 97.5))
    for feat in FEATS:
        r = med_ci(FA[eup], cup, feat)
        if r: frows.append(dict(label=f"H{H}M{M}", cmp="up_vs_ctrl", feature=feat, **r))
        r = med_ci(FA[edn], cdn, feat)
        if r: frows.append(dict(label=f"H{H}M{M}", cmp="dn_vs_ctrl", feature=feat, **r))
        r = med_ci(FA[eup], FA[edn], feat)
        if r: udrows.append(dict(label=f"H{H}M{M}", feature=feat, **r))
    print(f"char label H{H}M{M}: up_epi={int(eup.sum())} dn_epi={int(edn.sum())} "
          f"ctrl_up={len(cup)} ctrl_dn={len(cdn)}", flush=True)

FR = pd.DataFrame(frows).round(4); FR.to_csv(os.path.join(OUTD, "census_features.csv"), index=False)
UD = pd.DataFrame(udrows).round(4); UD.to_csv(os.path.join(OUTD, "census_updown.csv"), index=False)
print("\n=== TOP effects |median diff / IQR| (primary H60M20, vs matched controls) ===")
pr = FR[(FR.label == "H60M20") & FR.effect.notna()].copy()
pr["a"] = pr.effect.abs()
print(pr.sort_values("a", ascending=False).head(30)[
    ["cmp", "feature", "med_evt", "med_ctrl", "effect", "ci_lo", "ci_hi", "n_evt"]].to_string(index=False))
print("\n=== UP vs DOWN directional separation (H60M20) ===")
du = UD[UD.label == "H60M20"].copy(); du["a"] = du.effect.abs()
print(du.sort_values("a", ascending=False).head(15)[
    ["feature", "med_evt", "med_ctrl", "effect", "ci_lo", "ci_hi"]].to_string(index=False))
print("\nCENSUS DONE")
