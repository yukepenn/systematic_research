"""W19D7 step 1 — the MARKET-VARIABLE panel, the changepoint estimate, and the analog search.

D5 RULE, and it binds hardest here: no variable below touches any strategy's P&L, position,
target, trade list or fill. They are functions of the NQ price series alone. The one
semi-strategy quantity (clamp binding rate) is computed in structure.py, labelled there, and is
EXCLUDED from the changepoint panel and from the analog search per the frozen spec.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import sm01_solarsim as sm

RUN = os.path.join(ROOT, "runs", "W19D7_REGIME_2026")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
DEV_END = pd.Timestamp("2026-05-29").date()
SEED, BLOCK, NBOOT = 20260809, 5, 10000
EDGE = 0.10          # frozen: exclude the outer 10% of candidate changepoint locations
DC_K = 3.0           # frozen: directional-change threshold in per-bar sigma units
WIN = 106            # the window under investigation, in sessions

bars = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
bars = bars[bars["sess_date"] <= DEV_END].reset_index(drop=True)
print(f"dev bars {len(bars)}  sessions {bars['sess_date'].nunique()}", flush=True)

t = pd.to_datetime(bars["time"])
bars["slot"] = ((t.dt.hour * 60 + t.dt.minute) // 3).astype(int)
c = bars["close"].to_numpy()
bars["logret"] = np.concatenate([[0.0], np.diff(np.log(c))])
bars["dclose"] = np.concatenate([[0.0], np.diff(c)])
prev_close = np.concatenate([[c[0]], c[:-1]])
h, l = bars["high"].to_numpy(), bars["low"].to_numpy()
bars["tr"] = np.maximum(h - l, np.maximum(np.abs(h - prev_close), np.abs(l - prev_close)))
# a session's first bar has no within-session predecessor: its diff spans the roll gap
first = bars["first_bar_of_session"].to_numpy().astype(bool)
bars.loc[first, ["logret", "dclose"]] = 0.0


def excursion_len(px, k=DC_K):
    """Mean bars between successive PRICE directional changes, threshold = k x that session's
    own per-bar sigma. Pure price statistic: no VolMult, no clamp, no ensemble, no P&L, and
    deliberately NOT the Solar flip."""
    if len(px) < 20:
        return np.nan
    d = np.diff(px)
    sd = d.std(ddof=1)
    if not np.isfinite(sd) or sd <= 0:
        return np.nan
    thr = k * sd
    up = True
    anchor = px[0]
    last = 0
    gaps = []
    for i in range(1, len(px)):
        if up:
            if px[i] >= anchor:
                anchor = px[i]
            elif px[i] < anchor - thr:
                up = False; anchor = px[i]; gaps.append(i - last); last = i
        else:
            if px[i] <= anchor:
                anchor = px[i]
            elif px[i] > anchor + thr:
                up = True; anchor = px[i]; gaps.append(i - last); last = i
    return float(np.mean(gaps)) if gaps else float(len(px))


# ------------------------------------------------------------ reference profile (2022-2025)
ref = bars[pd.to_datetime(bars["sess_date"]) < pd.Timestamp("2026-01-01")]
ref_prof = ref.groupby("slot")["dclose"].apply(lambda s: s.abs().mean())
COARSE = 20  # slots -> 20 coarse bins for the peak/trough statistic (1 obs/slot is too thin)
bars["cbin"] = (bars["slot"] * COARSE // 480).astype(int)

rows = []
for sd_, g in bars.groupby("sess_date", sort=True):
    lr = g["logret"].to_numpy()[1:] if len(g) > 1 else np.array([0.0])
    rv = float(np.sqrt(np.sum(lr ** 2)))
    ac = float(pd.Series(lr).autocorr(lag=1)) if len(lr) > 20 else np.nan
    md = float(g["dclose"].abs().mean())
    prof = g.groupby("slot")["dclose"].apply(lambda s: s.abs().mean())
    common = prof.index.intersection(ref_prof.index)
    sp = (float(prof[common].rank().corr(ref_prof[common].rank()))
          if len(common) > 50 else np.nan)
    cb = g.groupby("cbin")["dclose"].apply(lambda s: s.abs().mean())
    pk = float(cb.max() / cb.min()) if len(cb) > 5 and cb.min() > 0 else np.nan
    rows.append({
        "sess": sd_, "n_bars": len(g),
        "v1_realised_vol": rv * np.sqrt(252.0),
        "v3_range_to_close": float(g["tr"].mean() / md) if md > 0 else np.nan,
        "v4_autocorr_lag1": ac,
        "v5_excursion_len": excursion_len(g["close"].to_numpy()),
        "v6_profile_spearman": sp,
        "v6b_profile_peak_trough": pk,
    })
P = pd.DataFrame(rows).sort_values("sess").reset_index(drop=True)
P["v2_vol_of_vol"] = P["v1_realised_vol"].rolling(20).std()
P["year"] = pd.to_datetime(P["sess"]).dt.year
VARS = ["v1_realised_vol", "v2_vol_of_vol", "v3_range_to_close", "v4_autocorr_lag1",
        "v5_excursion_len", "v6_profile_spearman", "v6b_profile_peak_trough"]
P.to_csv(os.path.join(OUT, "panel.csv"), index=False)
print(P[VARS].describe().round(4).to_string(), flush=True)


# ------------------------------------------------------------------ CUSUM changepoint
def cusum_stat(x):
    """Normalised CUSUM for a single mean shift. Returns (max_stat, argmax_index)."""
    n = len(x)
    lo, hi = int(EDGE * n), int((1 - EDGE) * n)
    cs = np.cumsum(x - x.mean())
    tau = np.arange(1, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        norm = np.sqrt(n / (tau * (n - tau)))
    stat = np.abs(cs[:-1]) * norm
    sd = x.std(ddof=1)
    stat = stat / sd if sd > 0 else stat * np.nan
    mask = np.zeros_like(stat, dtype=bool)
    mask[lo:hi] = True
    stat = np.where(mask, stat, -np.inf)
    k = int(np.nanargmax(stat))
    return float(stat[k]), k


def block_resample(x, rng, block=BLOCK):
    n = len(x); nb = int(np.ceil(n / block))
    st = rng.integers(0, n, size=nb)
    idx = ((st[:, None] + np.arange(block)[None, :]) % n).reshape(-1)[:n]
    return x[idx]


def changepoint(x, name, rng):
    x = np.asarray(x, dtype=float)
    ok = np.isfinite(x)
    x = x[ok]
    n = len(x)
    if n < 200:
        return {"variable": name, "n": n, "detected": False, "note": "too few finite points"}
    stat, k = cusum_stat(x)
    # null: no change. block-resample the mean-removed series and recompute the statistic.
    z = x - x.mean()
    null = np.array([cusum_stat(block_resample(z, rng))[0] for _ in range(1000)])
    p = float((null >= stat).mean())
    crit = float(np.quantile(null, 0.95))
    # location CI: parametric-in-the-shift bootstrap of the FITTED model
    mu1, mu2 = x[:k + 1].mean(), x[k + 1:].mean()
    fit = np.concatenate([np.full(k + 1, mu1), np.full(n - k - 1, mu2)])
    resid = x - fit
    locs = []
    for _ in range(400):
        locs.append(cusum_stat(fit + block_resample(resid, rng))[1])
    return {"variable": name, "n": n, "max_cusum": stat, "crit95_null": crit, "p_value": p,
            "detected": bool(stat > crit),
            "changepoint_index": k, "changepoint_date": str(P["sess"].iloc[k]),
            "loc_ci05": str(P["sess"].iloc[int(np.quantile(locs, 0.05))]),
            "loc_ci95": str(P["sess"].iloc[int(np.quantile(locs, 0.95))]),
            "mean_before": float(mu1), "mean_after": float(mu2),
            "shift_in_sd": float((mu2 - mu1) / x.std(ddof=1))}


rng = np.random.default_rng(SEED)
cps = [changepoint(P[v].to_numpy(), v, rng) for v in VARS]

# PC1 of the standardized panel (rows with all variables finite)
Z = P[VARS].copy()
Z = (Z - Z.mean()) / Z.std(ddof=1)
Zf = Z.dropna()
U, S, Vt = np.linalg.svd(Zf.to_numpy() - Zf.to_numpy().mean(0), full_matrices=False)
pc1 = (Zf.to_numpy() - Zf.to_numpy().mean(0)) @ Vt[0]
pc1_full = pd.Series(np.nan, index=P.index)
pc1_full.loc[Zf.index] = pc1
P["pc1"] = pc1_full
cp_pc1 = changepoint(pc1, "PC1", rng)
cp_pc1["loadings"] = dict(zip(VARS, np.round(Vt[0], 4).tolist()))
cp_pc1["explained_var_frac"] = float(S[0] ** 2 / (S ** 2).sum())
cps.append(cp_pc1)

CP = pd.DataFrame([{k: v for k, v in c.items() if k != "loadings"} for c in cps])
CP.to_csv(os.path.join(OUT, "changepoints.csv"), index=False)
json.dump(cps, open(os.path.join(OUT, "changepoint_bootstrap.json"), "w"),
          indent=2, default=str)
print("\n=== CHANGEPOINTS ===")
print(CP.to_string(index=False), flush=True)
n_det = int(CP["detected"].sum())
print(f"\ndetected: {n_det} of {len(CP)}  "
      f"(spec: if fewer than half detect, the data cannot locate a boundary)", flush=True)

# ------------------------------------------------------------------ by-period table
def period_table(boundary_date):
    P["period"] = np.where(pd.to_datetime(P["sess"]) < pd.Timestamp(boundary_date),
                           "BEFORE", "AFTER")
    r = []
    for v in VARS:
        g = P.groupby("period")[v]
        b, a = g.get_group("BEFORE").dropna(), g.get_group("AFTER").dropna()
        pooled_sd = P[v].std(ddof=1)
        r.append({"variable": v, "n_before": len(b), "n_after": len(a),
                  "mean_before": b.mean(), "mean_after": a.mean(),
                  "shift_in_pooled_sd": (a.mean() - b.mean()) / pooled_sd,
                  "welch_t": (a.mean() - b.mean()) /
                             np.sqrt(b.var(ddof=1) / len(b) + a.var(ddof=1) / len(a))})
    return pd.DataFrame(r)


# yearly table too — the honest descriptive view that needs no boundary at all
yr = P.groupby("year")[VARS].mean().round(4)
yr.to_csv(os.path.join(OUT, "variables_by_year.csv"))
print("\n=== BY YEAR (no boundary assumed) ===")
print(yr.to_string(), flush=True)

BOUNDARY = cp_pc1["changepoint_date"] if cp_pc1["detected"] else "2026-01-02"
BOUNDARY_IS_CONVENTION = not cp_pc1["detected"]
pt = period_table(BOUNDARY)
pt.to_csv(os.path.join(OUT, "variables_by_period.csv"), index=False)
print(f"\n=== BY PERIOD (boundary {BOUNDARY}"
      f"{' — CONVENTION, not a finding' if BOUNDARY_IS_CONVENTION else ' — ESTIMATED'}) ===")
print(pt.round(4).to_string(index=False), flush=True)

# ------------------------------------------------------------------ analog search
AVARS = [v for v in VARS]           # v7 excluded by construction (it is not in VARS)
Zs = P[AVARS].copy()
Zs = ((Zs - Zs.mean()) / Zs.std(ddof=1)).ffill().bfill()
M = Zs.to_numpy()
n = len(M)
centres = []
for s in range(0, n - WIN + 1):
    centres.append(M[s:s + WIN].mean(0))
C = np.array(centres)
target = n - WIN                      # the final 106-session window
D = np.sqrt(((C - C[target]) ** 2).sum(1))
# exclude windows overlapping the target
starts = np.arange(len(C))
non_overlap = starts + WIN <= target
cand = np.where(non_overlap)[0]
order = cand[np.argsort(D[cand])]
analogs = pd.DataFrame([{
    "rank": i + 1, "start": str(P["sess"].iloc[s]), "end": str(P["sess"].iloc[s + WIN - 1]),
    "distance": float(D[s])} for i, s in enumerate(order[:5])])

# novelty: nearest-neighbour distance of every window vs every non-overlapping other
nn = []
for i in range(len(C)):
    other = np.where((starts + WIN <= i) | (starts >= i + WIN))[0]
    if len(other) == 0:
        continue
    d = np.sqrt(((C[other] - C[i]) ** 2).sum(1))
    nn.append(d.min())
nn = np.array(nn)
target_nn = float(D[cand].min())
pct = float((nn < target_nn).mean())
novel = bool(pct > 0.95)
analogs.to_csv(os.path.join(OUT, "analogs.csv"), index=False)
nov = {"target_window": f"{P['sess'].iloc[target]}..{P['sess'].iloc[n-1]}",
       "nearest_neighbour_distance": target_nn,
       "percentile_among_all_windows": pct, "NOVEL": novel,
       "nearest_analog": analogs.iloc[0].to_dict() if len(analogs) else None}
json.dump(nov, open(os.path.join(OUT, "novelty.json"), "w"), indent=2, default=str)
print("\n=== ANALOGS ===")
print(analogs.to_string(index=False))
print(json.dumps(nov, indent=2, default=str), flush=True)

json.dump({"boundary": BOUNDARY, "boundary_is_convention": BOUNDARY_IS_CONVENTION,
           "n_variables_detecting": n_det, "n_variables": len(CP)},
          open(os.path.join(OUT, "boundary.json"), "w"), indent=2)
print("\npanel done", flush=True)
