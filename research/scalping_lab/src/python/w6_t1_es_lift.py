"""W6 T1 — ES-state conditioning lift on the NQ excursion surface (descriptive).
Spec: specs/W6_fss10_redteam.md (frozen, committed 58a97a3). Seed 20260808.
30s RTH quote-alive clock (census convention), brackets (24,8)/(32,10), both
candidate directions, cap 600s, conservative same-second-both-crossed->adverse
barrier on NQ per-second hi/lo (barrier() verbatim from opportunity_census.py).
JOIN (frozen): ES sechilo merged onto NQ per-second frame on time; ffill
es_mid_last with staleness limit 5s (older -> ES features NaN, excluded);
ES hi/lo not ffilled (not used here). Z-NORM (frozen): z_ret60 = ret60 /
rolling-600s std of 1s dmid, per instrument, trailing, min 300s history.
Baseline: artifacts/census/excursion_surface.csv (match bracket+dir);
day-clustered CIs via 1000-rep session bootstrap, paired with the census
per-session counts (excursion_surface_by_session.csv) for the lift CI."""
import glob, os
import numpy as np, pandas as pd
from numba import njit

BRK = [(24, 8), (32, 10)]
CAP = 600
STALE = 5.0
ZSTRONG = 0.5
ZDIV = 1.0
SEED = 20260808
NBOOT = 1000
# C1 gap constants (pp) = 100*gap_c1 from census excursion_surface.csv
GAP_PP = {(24, 8, "long"): 8.73, (24, 8, "short"): 9.09,
          (32, 10, "long"): 7.03, (32, 10, "short"): 7.37}
CELLS = ["CONFIRM", "NONCONF", "NQ_LED", "ES_LED"]

@njit(cache=True)
def barrier(ml, hi, lo, starts, d, A, B, cap):
    # verbatim from opportunity_census.py — conservative: same-second both -> adverse
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

SH = "research/scalping_lab/substrate/sechilo/NQ"
ESH = "research/scalping_lab/substrate/sechilo/ES"
GR = "research/scalping_lab/substrate/grid1s/NQ"
CEND = "research/scalping_lab/artifacts/census"
OUTD = "research/scalping_lab/artifacts/w6_fss10"
os.makedirs(OUTD, exist_ok=True)

nq_tags = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(SH, "s*.parquet")))
es_tags = {os.path.basename(p)[3:-8] for p in glob.glob(os.path.join(ESH, "es_s*.parquet"))}

rows, occ_rows, repro_rows = [], [], []
for tag in nq_tags:
    if tag not in es_tags:
        print(tag, "SKIP: no ES file", flush=True); continue
    d = pd.to_datetime(tag[1:], format="%Y%m%d")
    g = pd.read_parquet(os.path.join(GR, tag + ".parquet"))
    s = pd.read_parquet(os.path.join(SH, tag + ".parquet"))
    g["time"] = pd.to_datetime(g["time"]); s["time"] = pd.to_datetime(s["time"])
    f = g.merge(s, on="time", how="left")
    f["mid_last"] = f["mid_last"].ffill()
    f = f[f["mid_last"].notna()].reset_index(drop=True)
    f["mid_high"] = f["mid_high"].fillna(f["mid_last"])
    f["mid_low"] = f["mid_low"].fillna(f["mid_last"])
    n0 = len(f)
    es = pd.read_parquet(os.path.join(ESH, "es_" + tag + ".parquet"))
    es["time"] = pd.to_datetime(es["time"])
    f = f.merge(es[["time", "mid_last"]].rename(columns={"mid_last": "es_mid_raw"}),
                on="time", how="left")
    assert len(f) == n0, "ES merge changed NQ frame length"
    # --- frozen ES join: ffill with 5s staleness guard ---
    es_seen = f["es_mid_raw"].notna()
    last_es_t = f["time"].where(es_seen).ffill()
    stale = (f["time"] - last_es_t).dt.total_seconds()
    es_mid = f["es_mid_raw"].ffill()
    es_mid[~(stale <= STALE)] = np.nan          # NaN staleness (never seen) -> excluded
    # --- frozen z-norm, per instrument, trailing, min 300s ---
    mls = f["mid_last"]
    nq_rv = mls.diff().rolling(600, min_periods=300).std()
    nq_z = (mls.diff(60) / nq_rv.where(nq_rv > 0)).values
    es_ret60_s = es_mid.diff(60)
    es_rv = es_mid.diff().rolling(600, min_periods=300).std()
    es_z = (es_ret60_s / es_rv.where(es_rv > 0)).values
    es_ret60 = es_ret60_s.values

    ml = f["mid_last"].values; hi = f["mid_high"].values; lo = f["mid_low"].values
    tod = (f["time"] - d).dt.total_seconds().values
    upd60 = pd.Series((f["bid_upd"] + f["ask_upd"]).values).rolling(60, min_periods=1).sum().values
    dec = (tod >= 9*3600+1800) & (tod < 16*3600) & (upd60 > 0)
    dec_idx = np.where(dec)[0]
    if len(dec_idx) == 0:
        print(tag, "SKIP: quote-dead (0 decision secs)", flush=True); continue
    st30 = dec_idx[::30].astype(np.int64)

    nqz = nq_z[st30]; esz = es_z[st30]; esr = es_ret60[st30]
    valid = ~np.isnan(nqz) & ~np.isnan(esz)
    es_up = valid & (esr > 0); es_dn = valid & (esr < 0)
    strong = valid & (np.abs(esz) >= ZSTRONG)
    nq_led = valid & ((nqz - esz) >= ZDIV)
    es_led = valid & ((esz - nqz) >= ZDIV)
    cellmasks = {
        ("CONFIRM", "long"):  es_up & strong,   # sign(es_ret60)=+1 = candidate dir
        ("CONFIRM", "short"): es_dn & strong,
        ("NONCONF", "long"):  es_dn & strong,   # sign(es_ret60)=-candidate dir
        ("NONCONF", "short"): es_up & strong,
        ("NQ_LED", "long"):   nq_led,           # tested candidate = long AND short
        ("NQ_LED", "short"):  nq_led,
        ("ES_LED", "long"):   es_led & es_up,   # candidate = ES direction
        ("ES_LED", "short"):  es_led & es_dn,
    }
    # reproduction control: unconditional surface on full st30 must match census
    for (A, B) in BRK:
        for dname, dv in (("long", 1), ("short", -1)):
            tg, av, ne = barrier(ml, hi, lo, st30, dv, float(A), float(B), CAP)
            repro_rows.append(dict(session=tag, A=A, B=B, dir=dname, tgt=tg, adv=av, nei=ne))
    for (cell, dname), m in cellmasks.items():
        dv = 1 if dname == "long" else -1
        stc = st30[m]
        for (A, B) in BRK:
            tg, av, ne = barrier(ml, hi, lo, stc, dv, float(A), float(B), CAP)
            rows.append(dict(session=tag, cell=cell, dir=dname, A=A, B=B,
                             tgt=tg, adv=av, nei=ne, n=len(stc)))
    occ_rows.append(dict(session=tag, n_st30=len(st30), n_valid=int(valid.sum()),
                         **{f"{c}_{dn}": int(cellmasks[(c, dn)].sum())
                            for c in CELLS for dn in ("long", "short")}))
    print(tag, f"done st30={len(st30)} valid={int(valid.sum())}", flush=True)

R = pd.DataFrame(rows); R.to_csv(os.path.join(OUTD, "t1_by_session.csv"), index=False)
OC = pd.DataFrame(occ_rows); OC.to_csv(os.path.join(OUTD, "t1_occupancy.csv"), index=False)
RP = pd.DataFrame(repro_rows)

# ---------- reproduction control vs census ----------
CS = pd.read_csv(os.path.join(CEND, "excursion_surface_by_session.csv"))
mrg = RP.merge(CS, on=["session", "A", "B", "dir"], suffixes=("_w6", "_cen"))
dev = (mrg[["tgt_w6", "adv_w6", "nei_w6"]].values - mrg[["tgt_cen", "adv_cen", "nei_cen"]].values)
print(f"\nREPRO CONTROL: rows={len(mrg)} (expect {len(RP)}), "
      f"max |dev| vs census per-session counts = {np.abs(dev).max()}")

# ---------- pooled lift table with paired session bootstrap ----------
SURF = pd.read_csv(os.path.join(CEND, "excursion_surface.csv"))
sessions = sorted(R.session.unique()); S = len(sessions)
print(f"analysis sessions = {S}")
rng = np.random.default_rng(SEED)
bidx = rng.integers(0, S, size=(NBOOT, S))      # shared (paired) day-cluster resample

def sess_arr(df, col):
    return df.set_index("session")[col].reindex(sessions).fillna(0).values.astype(float)

base_arr = {}
for (A, B) in BRK:
    for dname in ("long", "short"):
        gb = CS[(CS.A == A) & (CS.B == B) & (CS.dir == dname)]
        base_arr[(A, B, dname)] = (sess_arr(gb, "tgt"), sess_arr(gb, "tgt") + sess_arr(gb, "adv"))

n_st30_tot = OC["n_st30"].sum(); n_valid_tot = OC["n_valid"].sum()
out = []
for cell in CELLS:
    for dname in ("long", "short"):
        for (A, B) in BRK:
            gc = R[(R.cell == cell) & (R.dir == dname) & (R.A == A) & (R.B == B)]
            tgt_s = sess_arr(gc, "tgt"); dec_s = sess_arr(gc, "tgt") + sess_arr(gc, "adv")
            n_all = int(gc.n.sum()); n_dec = int(dec_s.sum())
            n_sess = int((sess_arr(gc, "n") > 0).sum())
            p = tgt_s.sum() / n_dec if n_dec else np.nan
            bt, bd = base_arr[(A, B, dname)]
            srow = SURF[(SURF.A == A) & (SURF.B == B) & (SURF.dir == dname)].iloc[0]
            p_base_csv = float(srow.p_target)
            lift_pp = 100 * (p - p_base_csv)
            # paired day-clustered bootstrap
            ct = tgt_s[bidx].sum(1); cd = dec_s[bidx].sum(1)
            btg = bt[bidx].sum(1); bde = bd[bidx].sum(1)
            with np.errstate(invalid="ignore", divide="ignore"):
                pb = np.where(cd > 0, ct / cd, np.nan)
                lb = 100 * (pb - btg / bde)
            occ_pp = 100 * gc.n.sum() / n_st30_tot
            gap = GAP_PP[(A, B, dname)]
            out.append(dict(cell=cell, dir=dname, A=A, B=B, n_starts=n_all, n_dec=n_dec,
                            sessions=n_sess, occ_pct=round(occ_pp, 2),
                            p_target=round(p, 4),
                            p_ci_lo=round(np.nanpercentile(pb, 2.5), 4),
                            p_ci_hi=round(np.nanpercentile(pb, 97.5), 4),
                            p_base=p_base_csv, lift_pp=round(lift_pp, 2),
                            lift_ci_lo=round(np.nanpercentile(lb, 2.5), 2),
                            lift_ci_hi=round(np.nanpercentile(lb, 97.5), 2),
                            gap_pp=gap, lift_minus_gap=round(lift_pp - gap, 2),
                            p_neither=round(1 - n_dec / n_all, 4) if n_all else np.nan,
                            n_boot_ok=int(np.isfinite(lb).sum()),
                            ge_gap_ci=bool((lift_pp >= gap) and (np.nanpercentile(lb, 2.5) > 0)),
                            ge_5pp=bool(lift_pp >= 5.0)))
L = pd.DataFrame(out); L.to_csv(os.path.join(OUTD, "t1_lift_table.csv"), index=False)

print(f"\nES-feature validity on 30s clock: {n_valid_tot}/{n_st30_tot} "
      f"({100*n_valid_tot/n_st30_tot:.2f}%)")
print("\n=== T1 LIFT TABLE (30s RTH clock, cap 600s, conservative barrier) ===")
print(L.to_string(index=False))
print("\n=== per-session ES validity (lowest 5) ===")
oc = OC.assign(vr=lambda x: 100 * x.n_valid / x.n_st30).sort_values("vr")
print(oc[["session", "n_st30", "n_valid", "vr"]].head(5).to_string(index=False))
print("\n=== occupancy (fraction of 30s clock seconds in each cell) ===")
for c in CELLS:
    for dn in ("long", "short"):
        k = OC[f"{c}_{dn}"].sum()
        print(f"  {c:>8}/{dn:<5} {k:>6}  {100*k/n_st30_tot:6.2f}%")
hit_gap = L[L.ge_gap_ci]; hit5 = L[L.ge_5pp]
print(f"\nVERDICT: cells with lift >= gap AND lift CI_lo > 0: {len(hit_gap)}")
if len(hit_gap): print(hit_gap.to_string(index=False))
print(f"VERDICT: cells with lift >= 5pp: {len(hit5)}")
if len(hit5): print(hit5[["cell", "dir", "A", "B", "lift_pp", "lift_ci_lo", "lift_ci_hi"]].to_string(index=False))
print("\nT1 DONE")
