# G3_COMPCASCADE_20260906 (G00093, family GENESIS3_EVENT)
# Compression-primed stop cascades: range break AFTER multi-day compression, 5 markets daily.
# Spec: runs/G3_COMPCASCADE_20260906/spec.yaml (committed before results).
#
# MECHANICAL OPERATIONALIZATIONS (fixed HERE, before any outcome is computed):
#  O1. Level series = additively-adjusted CLOSE series per market (NQ spine is close-only, so
#      close-based ranges/breaks are the only construction implementable identically across all
#      five markets; applied uniformly to signal AND control).
#  O2. "ON a compression day" vs mechanism "a range break AFTER a multi-day compression":
#      PRIMARY (gating) = compression state at the PRIOR close, comp[t-1] (the priming must
#      pre-exist the break; a big break day inflates its own 5-day range and would mechanically
#      disqualify the strongest breaks). SPEC-LITERAL comp[t] variant printed as annex cells.
#      Conflict disclosed in REPORT anomalies.
#  O3. comp[t] = range5[t] <= 20th pctile of trailing-60 range5 values (window inclusive of t).
#      range5[t] = max(C[t-4..t]) - min(C[t-4..t]).
#  O4. Break at t: C[t] > max(C[t-5..t-1]) (up) or C[t] < min(C[t-5..t-1]) (down).
#  O5. Trend: drift20[t] = C[t-1] - C[t-21] (ends at t-1, causal). WITH iff sign match & drift!=0.
#  O6. Validity: t>=64 (warmup), no EXCLUDED session in positions [t-5, t+k], fwd_k defined.
#      Excluded = clean_daily==0 (gap-spanning) OR HOLE day (certified ret_points != raw close
#      diff on a same-contract clean day => the daily store is missing sessions there).
#      Same rule for events, controls, and null landing sites.
#  O7. Pooling unit for gating = $/event/contract at the CONSERVATIVE cost rung (family
#      precedent G3_AUCTCYCLE [GATING] on CONS). Cost rungs: opt = 1 tick RT + $4.36 comm,
#      cons = 2 ticks RT + $4.36 comm. z-standardized pooled annex printed (non-gating).
#  O8. Null = shared-draw circular shift: ONE uniform u per iteration, per-market offset
#      floor(u*L_m); signed event structure held fixed, return series circularly reindexed;
#      2,000 iterations; p one-sided (mean>0) with +1 smoothing.
#  O9. Event-block CI: pooled events sorted by date, chained into blocks when the gap to the
#      previous pooled event is <= 5 calendar days; 10,000 block-bootstrap resamples, pct CI95.
#      Delta CI: event blocks and control blocks resampled independently.
#  O10. Eras (family convention, G3_AUCTCYCLE): era1 <= 2015-12-31 (NQ 2006-08 included),
#      era2 2016-2021, era3 2022 -> 2026-07. G5 FAIL iff era3 pooled after-cost(cons) mean < 0.
#  O11. k in {1,2,3}; k=2 PRIMARY, fixed in spec; single preregistered gating cell => no
#      multiplicity correction on the gate (other cells are report-only).
#  O12. CL daily: no certified daily exists; built here from SM1M_CL_SUBSTRATE 1m parquet
#      (session close-to-close, 18:00->17:00 ET label rule, POINTS on merge-back-adjusted
#      continuous). Validated against the substrate MANIFEST session census (1,182 sessions,
#      2022-01-03 -> 2026-07-31). CL holdout freeze RETIRED 2026-09-06 (owner directive) --
#      full pre-seal history is discovery-consumable.
import hashlib, json, sys, io, os
import numpy as np
import pandas as pd

RUN = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\G3_COMPCASCADE_20260906"
REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

SEAL = pd.Timestamp("2026-08-01")
COMM = 4.36
NSHIFT = 2000
NBOOT = 10000
RNG = np.random.default_rng(93)

MKT = {
    "ES": dict(tick=0.25, pv=50.0),
    "NQ": dict(tick=0.25, pv=20.0),
    "CL": dict(tick=0.01, pv=1000.0),
    "ZB": dict(tick=0.03125, pv=1000.0),
    "GC": dict(tick=0.10, pv=100.0),
}
for m, d in MKT.items():
    tv = d["tick"] * d["pv"]
    d["cost_opt"] = 1 * tv + COMM
    d["cost_cons"] = 2 * tv + COMM

EXPECTED_SHA = {
    "ES": "249921cb6d790b8478910fabbc480e0ac82a3d20a206b38fedb34fa1b2054f91",
    "ZB": "9446e7f19ee17754d5afd31c65790e5fe24ae76f23ebf128101c7c0bdf786c56",
    "GC": "93ec562d3ebb3ce7021855945545b3bb60365e8b090c6d62de2a675f39ed98a1",
    "CL1M": "e587486c23f5b61184b6a49aaeebc77f1a3e74e0731d8d0f4192087587adc137",
    # NQ daily spine: G3_EVENT_GC inputs_manifest.json nq_spine.parquet_sha256
    "NQ": "15d247470379e8818aaf4a3dd3cfea7edcde7387e05b9a36e71adccb40471e9f",
}

PATHS = {
    "ES": os.path.join(REPO, r"runs\G3_AUCTCYCLE_20260906\out\es_daily.parquet"),
    "ZB": os.path.join(REPO, r"runs\G3_AUCTCYCLE_20260906\out\zb_daily.parquet"),
    "GC": os.path.join(REPO, r"runs\DAILY_GC_EXTRACT_AUTOPSY_20260906\out\gc_daily.parquet"),
    "NQ": os.path.join(REPO, r"runs\G3_EVENT_GC_20260906\out\nq_daily_spine.parquet"),
    "CL1M": os.path.join(REPO, r"runs\SM1M_CL_SUBSTRATE\out\cl_1m_2022_2026.parquet"),
}

LOG = io.StringIO()
def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

# ----------------------------------------------------------------------------------------
P("=" * 118)
P("=== G3_COMPCASCADE_20260906 -- compression-primed stop cascades, 5-market daily breakout (G00093, family GENESIS3_EVENT)")
P("=" * 118)
P("DEDUP NOTE (spec): NQ allowed here -- daily breakout is not a P1 object, and NQ's prior Donchian-family")
P("closures were intraday/ensemble scopes; this is the compression->expansion row's first strategy-object entry.")
P("CL: no certified daily exists; built in-run from SM1M_CL_SUBSTRATE 1m (session close-to-close, POINTS);")
P("CL holdout freeze RETIRED 2026-09-06 (owner directive) -> full pre-seal history discovery-consumable.")
P("")

# ---- load + sha ------------------------------------------------------------------------
shas = {}
for key, p in PATHS.items():
    shas[key] = sha256(p)
    exp = EXPECTED_SHA.get(key)
    tag = ("MATCH" if shas[key] == exp else "*** MISMATCH ***") if exp else "recorded-for-the-record (no prior sha)"
    P(f"INPUT {key:4s} sha256 {shas[key]}  [{tag}]")
    if exp and shas[key] != exp:
        raise SystemExit(f"SHA MISMATCH for {key}")
P("")

frames = {}
es = pd.read_parquet(PATHS["ES"]); zb = pd.read_parquet(PATHS["ZB"]); gc = pd.read_parquet(PATHS["GC"])
nq = pd.read_parquet(PATHS["NQ"])

# ---- CL daily build --------------------------------------------------------------------
cl1 = pd.read_parquet(PATHS["CL1M"])
t = pd.to_datetime(cl1["time"])
frac = t.dt.hour * 60 + t.dt.minute
in_break = ((frac > 17 * 60) & (frac <= 18 * 60)).sum()
assert in_break == 0, "CL 1m stamps found in (17:00,18:00] ET"
sess = t.dt.normalize() + pd.to_timedelta((frac > 17 * 60).astype(int), unit="D")
cl1 = cl1.assign(session=sess)
g = cl1.groupby("session", sort=True)
cl = pd.DataFrame({
    "date": np.array(sorted(cl1["session"].unique())),
})
agg = g.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
            close=("close", "last"), volume=("volume", "sum"), n_bars=("close", "size"))
agg = agg.sort_index()
cl = agg.reset_index().rename(columns={"session": "date"})
assert len(cl) == 1182, f"CL session count {len(cl)} != MANIFEST 1,182"
assert str(cl['date'].min())[:10] == "2022-01-03" and str(cl['date'].max())[:10] == "2026-07-31", "CL session span mismatch vs MANIFEST"
# closes on 0.01 grid (certified loss-free grid)
grid = (cl["close"] / 0.01).round() * 0.01
assert float(np.max(np.abs(grid - cl["close"]))) < 5e-3, "CL close off 0.01 grid"
gapd = cl["date"].diff().dt.days
cl["cal_gap_days"] = gapd
cl["clean_daily"] = ((gapd.isna()) | (gapd <= 5)).astype(int)
cl["ret_points"] = cl["close"].diff()
cl_path = os.path.join(OUT, "cl_daily.parquet")
cl.to_parquet(cl_path, index=False)
P(f"CL daily BUILT: {len(cl)} sessions {str(cl['date'].min())[:10]} -> {str(cl['date'].max())[:10]}, "
  f"clean_daily==0: {(cl['clean_daily']==0).sum()}; session census == MANIFEST (1,182 / 2022-01-03 -> 2026-07-31) PASS")
P(f"CL daily parquet sha256 {sha256(cl_path)}  (out/cl_daily.parquet)")
P("")

# ---- adjusted level series per market --------------------------------------------------
# Level series A: cumulated CERTIFIED economic returns (ret_points, identity-gated 0.0 vs
# roll.economic_returns in the source manifests) anchored at the first close, so diff(A) ==
# ret_points identically. The adjustment K may step ONLY on roll days or gap-spanning
# (clean_daily==0) days -- on a gap day the certified ret_points is the held-contract
# close-to-close economic return across the data hole (which may contain an unflagged roll),
# authoritative over the raw close diff. Asserted below.
def build_adj(df, close_col="close", ret_col="ret_points", rolled_col="rolled"):
    c = df[close_col].to_numpy(float)
    r = df[ret_col].to_numpy(float)
    rolled = np.asarray(df[rolled_col].to_numpy(), float)
    clean = np.asarray(df["clean_daily"].to_numpy(), float)
    held = df["held_contract"].astype(str).to_numpy()
    contract_change = np.r_[[False], held[1:] != held[:-1]]
    K = np.zeros(len(c))
    for i in range(1, len(c)):
        step = 0.0
        if np.isfinite(r[i]):
            step = r[i] - (c[i] - c[i - 1])
        K[i] = K[i - 1] + step
    A = c + K
    dK = np.abs(np.diff(K))
    stepped = np.r_[[False], dK > 1e-9]
    is_roll = stepped & ((np.r_[[0.], rolled[1:]] == 1) | contract_change)
    # HOLE day: K stepped on a same-contract, clean-flagged day => the daily store is missing
    # sessions there (certified ret_points is the true 1-day economic return; the parquet's
    # close diff spans the hole). The LEVEL series absorbs the hole; such days are EXCLUDED
    # from event formation/hold windows below (O6), like clean_daily==0 days.
    is_gap = stepped & ~is_roll & np.r_[[False], clean[1:] == 0]
    is_hole = stepped & ~is_roll & ~is_gap
    return A, K, is_roll, is_gap, is_hole

data = {}
for name, df in [("ES", es), ("ZB", zb), ("GC", gc)]:
    A, K, is_roll, is_gap, is_hole = build_adj(df)
    d = np.abs(np.diff(A) - df["ret_points"].to_numpy(float)[1:])
    d = d[np.isfinite(d)]
    assert float(np.max(d)) < 1e-9, f"{name}: diff(A) != ret_points"
    excl = (df["clean_daily"].to_numpy(int) == 0) | is_hole
    data[name] = dict(dates=pd.to_datetime(df["date"]).reset_index(drop=True), A=A,
                      clean=(~excl).astype(int), identity=0.0)
    P(f"{name}: {len(df)} rows {str(df['date'].min())[:10]} -> {str(df['date'].max())[:10]}; "
      f"diff(A)==certified ret_points maxerr {float(np.max(d)):.1e}; K steps: {int(is_roll.sum())} roll/contract-change + "
      f"{int(is_gap.sum())} gap-day(clean==0) + {int(is_hole.sum())} HOLE(same-contract clean day; excluded from windows); "
      f"window-excluded days total {int(excl.sum())}")

# GC cross-check vs certified close_padj: on days where our adjustment K did NOT step and no
# roll is flagged, the offset (A - close_padj) must not move -- i.e. the two constructions agree
# everywhere except the (roll/gap/hole) step days each handles by design.
gpad = gc["close_padj"].to_numpy(float)
diffc = data["GC"]["A"] - gpad
step = np.abs(np.diff(diffc))
dK_gc = np.abs(np.diff(data["GC"]["A"] - gc["close"].to_numpy(float)))
mask_quiet = (dK_gc < 1e-9) & (np.asarray(gc["rolled"].to_numpy(), float)[1:] == 0)
stray_pad = float(np.max(step[mask_quiet]))
assert stray_pad < 1e-6, f"GC A vs close_padj moves on a quiet day ({stray_pad})"
P(f"GC cross-check: in-run level series vs certified close_padj -- offset moves only where an adjustment "
  f"(roll/gap/hole) is by-design; max move on quiet days {stray_pad:.2e} PASS")

# NQ spine
nqc = nq["close_adj"].to_numpy(float)
rr = nq["ret_pts"].to_numpy(float)
dd = np.abs(np.diff(nqc) - rr[1:]); dd = dd[np.isfinite(rr[1:])]
P(f"NQ spine: {len(nq)} sessions {str(nq['date'].min())[:10]} -> {str(nq['date'].max())[:10]}; "
  f"diff(close_adj) vs ret_pts maxerr {float(np.max(dd)):.1e} (finite rets only); clean_daily==0: {(nq['clean_daily']==0).sum()}")
assert float(np.max(dd)) < 1e-6
data["NQ"] = dict(dates=pd.to_datetime(nq["date"]).reset_index(drop=True), A=nqc,
                  clean=nq["clean_daily"].to_numpy(int), identity=0.0)
data["CL"] = dict(dates=pd.to_datetime(cl["date"]).reset_index(drop=True), A=cl["close"].to_numpy(float),
                  clean=cl["clean_daily"].to_numpy(int), identity=0.0)

# seals + tick asserts on RAW (unadjusted) closes where available
P("")
for name, df, colc, tick in [("ES", es, "close", 0.25), ("ZB", zb, "close", 0.03125),
                             ("GC", gc, "close", 0.10), ("CL", cl, "close", 0.01)]:
    mx = pd.to_datetime(df["date"]).max()
    assert mx < SEAL, f"{name} seal breach {mx}"
    half = tick / 2  # daily SETTLEMENT can print on the half-tick grid (ZB settles in 1/64ths)
    offgrid = float(np.max(np.abs((df[colc] / half).round() * half - df[colc])))
    P(f"SEAL {name}: max session {str(mx)[:10]} < 2026-08-01 PASS | grid assert: closes on half-tick settlement grid "
      f"({half}); max residual {offgrid:.2e} {'PASS' if offgrid < 1e-9 else 'FAIL'}  (cost tick {tick} = certified manifest tick_size)")
    assert offgrid < 1e-9
mxn = pd.to_datetime(nq["date"]).max()
assert mxn < SEAL
P(f"SEAL NQ: max session {str(mxn)[:10]} < 2026-08-01 PASS | tick assert: n/a on back-adjusted spine (tick 0.25 from contract spec; noted)")
P("")

# ---- event construction ----------------------------------------------------------------
K_HOLDS = [1, 2, 3]
WARMUP = 64

def features(A):
    s = pd.Series(A)
    range5 = s.rolling(5).max() - s.rolling(5).min()
    q20 = range5.rolling(60).quantile(0.2)
    comp = (range5 <= q20) & range5.notna() & q20.notna()
    comp_def = range5.notna() & q20.notna()
    hi5p = s.rolling(5).max().shift(1)
    lo5p = s.rolling(5).min().shift(1)
    up = (s > hi5p) & hi5p.notna()
    dn = (s < lo5p) & lo5p.notna()
    drift20 = s.shift(1) - s.shift(21)
    return range5, comp, comp_def, up, dn, drift20

events = []       # primary: comp[t-1]
events_lit = []   # spec-literal annex: comp[t]
controls = []     # break, comp[t-1] defined & False
null_sites = {}   # per market: valid landing masks + fwd arrays
excl_counts = {}

for name, d in data.items():
    A, dates, clean = d["A"], d["dates"], d["clean"]
    L = len(A)
    range5, comp, comp_def, up, dn, drift20 = features(A)
    comp_np, compdef_np = comp.to_numpy(), comp_def.to_numpy()
    up_np, dn_np, drift_np = up.to_numpy(), dn.to_numpy(), drift20.to_numpy()
    fwd = {k: np.r_[A[k:] - A[:-k], [np.nan] * k] for k in K_HOLDS}
    # validity per O6, per k
    clean_ok = {}
    for k in K_HOLDS:
        ok = np.ones(L, bool)
        for t_ in range(L):
            if t_ < WARMUP or not np.isfinite(fwd[k][t_]):
                ok[t_] = False; continue
            lo_, hi_ = t_ - 5, min(t_ + k, L - 1)
            if (clean[lo_:hi_ + 1] == 0).any():
                ok[t_] = False
        clean_ok[k] = ok
    null_sites[name] = dict(fwd=fwd, ok=clean_ok, L=L)
    n_excl = {k: 0 for k in K_HOLDS}
    for t_ in range(WARMUP, L):
        if not (up_np[t_] or dn_np[t_]):
            continue
        direc = 1 if up_np[t_] else -1
        drift = drift_np[t_]
        split = "WITH" if (np.isfinite(drift) and np.sign(drift) == direc and drift != 0) else "AGAINST"
        prior_comp_def = compdef_np[t_ - 1]
        prior_comp = bool(comp_np[t_ - 1]) if prior_comp_def else None
        lit_comp = bool(comp_np[t_]) if compdef_np[t_] else None
        rets = {}
        okall = {}
        for k in K_HOLDS:
            if clean_ok[k][t_]:
                rets[k] = direc * fwd[k][t_]
                okall[k] = True
            else:
                rets[k] = np.nan
                okall[k] = False
                n_excl[k] += 1
        row = dict(market=name, t=t_, date=dates.iloc[t_], dir=direc, split=split, **{f"pts_k{k}": rets[k] for k in K_HOLDS})
        if prior_comp is True:
            events.append(row)
        elif prior_comp is False:
            controls.append(row)
        if lit_comp is True:
            events_lit.append(row.copy())
    excl_counts[name] = n_excl
    ne = sum(1 for r in events if r["market"] == name)
    nc = sum(1 for r in controls if r["market"] == name)
    P(f"{name}: breaks with prior-compression (PRIMARY events) {ne} | no-compression breaks (CONTROL) {nc} | "
      f"spec-literal comp[t] events {sum(1 for r in events_lit if r['market']==name)} | window-invalid at k=2 among breaks: {n_excl[2]}")

ev = pd.DataFrame(events)
ct = pd.DataFrame(controls)
evl = pd.DataFrame(events_lit)
P("")

def usd(df_, k, rung):
    out = np.empty(len(df_))
    for i, (m, p_) in enumerate(zip(df_["market"], df_[f"pts_k{k}"])):
        out[i] = p_ * MKT[m]["pv"] - (MKT[m][f"cost_{rung}"] if np.isfinite(p_) else np.nan)
    return out

for k in K_HOLDS:
    for df_ in (ev, ct, evl):
        if len(df_):
            df_[f"usd_gross_k{k}"] = [p_ * MKT[m]["pv"] for m, p_ in zip(df_["market"], df_[f"pts_k{k}"])]
            df_[f"usd_opt_k{k}"] = usd(df_, k, "opt")
            df_[f"usd_cons_k{k}"] = usd(df_, k, "cons")

era_of = lambda d: "era1_<=2015" if d.year <= 2015 else ("era2_2016-21" if d.year <= 2021 else "era3_2022-26")
for df_ in (ev, ct, evl):
    if len(df_):
        df_["era"] = df_["date"].map(era_of)

# ---- G1 MDE FIRST (printed before any observed event mean) ------------------------------
P("G1 MDE (PRINTED BEFORE ANY OBSERVED EVENT MEAN)  -- sigma from UNCONDITIONAL k=2 forward $ moves, N = valid event count")
sig = {}
nev = {}
for name, d in data.items():
    f2 = null_sites[name]["fwd"][2]
    ok2 = null_sites[name]["ok"][2]
    sig[name] = float(np.nanstd(f2[ok2], ddof=1)) * MKT[name]["pv"]
    nev[name] = int(ev[(ev.market == name) & np.isfinite(ev.pts_k2)].shape[0]) if len(ev) else 0
    mde = 2.486 * sig[name] / np.sqrt(max(nev[name], 1))
    P(f"    {name}: uncond 2d $sd {sig[name]:>10,.0f}  n_event(k2) {nev[name]:>4d}  MDE80(one-sided 5%) ${mde:>8,.0f}/event")
N2 = sum(nev.values())
sig_pool = np.sqrt(sum(nev[m] * sig[m] ** 2 for m in data) / max(N2, 1))
MDE_POOL = 2.486 * sig_pool / np.sqrt(max(N2, 1))
P(f"    POOLED: sigma_pool ${sig_pool:,.0f} (composition-weighted), N {N2}, MDE80 ${MDE_POOL:,.0f}/event")
P("")

# ---- blocks -----------------------------------------------------------------------------
def make_blocks(df_, k):
    d2 = df_[np.isfinite(df_[f"pts_k{k}"])].sort_values("date").reset_index(drop=True)
    blocks, cur = [], [0]
    for i in range(1, len(d2)):
        if (d2.date.iloc[i] - d2.date.iloc[i - 1]).days <= 5:
            cur.append(i)
        else:
            blocks.append(cur); cur = [i]
    if cur: blocks.append(cur)
    return d2, blocks

def block_boot_mean(vals, blocks, nboot, rng):
    means = np.empty(nboot)
    B = len(blocks)
    bl = [np.asarray(b) for b in blocks]
    for i in range(nboot):
        idx = rng.integers(0, B, B)
        sel = np.concatenate([bl[j] for j in idx])
        means[i] = np.nanmean(vals[sel])
    return means

# ---- PRIMARY pooled cell k=2 ------------------------------------------------------------
ev2, evb = make_blocks(ev, 2)
ct2, ctb = make_blocks(ct, 2)
obs_gross = float(np.nanmean(ev2["usd_gross_k2"]))
obs_opt = float(np.nanmean(ev2["usd_opt_k2"]))
obs_cons = float(np.nanmean(ev2["usd_cons_k2"]))
ctrl_gross = float(np.nanmean(ct2["usd_gross_k2"]))
ctrl_cons = float(np.nanmean(ct2["usd_cons_k2"]))

P(f"PRIMARY (k=2, pooled 5 markets, $/event/contract):  n_event {len(ev2)}  n_control {len(ct2)}")
P(f"    gross mean       ${obs_gross:+,.2f}/event")
P(f"    after-cost OPT   ${obs_opt:+,.2f}/event      after-cost CONS ${obs_cons:+,.2f}/event   [GATING]")

boots = block_boot_mean(ev2["usd_cons_k2"].to_numpy(), evb, NBOOT, RNG)
ci_lo, ci_hi = np.percentile(boots, [2.5, 97.5])
P(f"    event-block bootstrap 95% CI (cons): [${ci_lo:+,.2f}, ${ci_hi:+,.2f}]   ({len(evb)} blocks, {NBOOT} draws)")

# shared-draw circular-shift null
null_means = np.empty(NSHIFT)
ev_by_m = {m: ev2[ev2.market == m] for m in data}
for it in range(NSHIFT):
    u = RNG.random()
    tot, cnt = 0.0, 0
    for m in data:
        sub = ev_by_m[m]
        if not len(sub):
            continue
        L = null_sites[m]["L"]
        o = int(np.floor(u * L))
        f2 = null_sites[m]["fwd"][2]; ok2 = null_sites[m]["ok"][2]
        pos = (sub["t"].to_numpy() + o) % L
        good = ok2[pos]
        vals = sub["dir"].to_numpy()[good] * f2[pos[good]] * MKT[m]["pv"] - MKT[m]["cost_cons"]
        tot += vals.sum(); cnt += len(vals)
    null_means[it] = tot / max(cnt, 1)
p_1s = (1 + np.sum(null_means >= obs_cons)) / (1 + NSHIFT)
p_2s = (1 + np.sum(np.abs(null_means - null_means.mean()) >= abs(obs_cons - null_means.mean()))) / (1 + NSHIFT)
P(f"    shared-draw circular-shift null ({NSHIFT} draws, ONE uniform per draw across all 5 markets):")
P(f"        null mean ${null_means.mean():+,.2f}, sd ${null_means.std(ddof=1):,.2f}; p one-sided(cons mean > null) = {p_1s:.4f} [GATING], two-sided = {p_2s:.4f}")
P(f"    P-MEANING IN WORDS: p = share of 2,000 random circular placements of the SAME signed event structure")
P(f"        (dependence preserved by one shared draw) whose pooled after-cost(cons) mean >= the observed ${obs_cons:+,.2f}.")
P(f"        Second, independent computation of the same event: the event-block bootstrap CI above (does 0 sit inside?).")

# z-standardized annex (non-gating)
zvals = []
for m in data:
    sub = ev_by_m[m]
    if not len(sub):
        continue
    A = data[m]["A"]
    s = pd.Series(A).diff()
    sd60 = s.rolling(60).std().shift(1).to_numpy()  # causal daily-ret sd
    z = sub[f"pts_k2"].to_numpy() / (sd60[sub["t"].to_numpy()] * np.sqrt(2))
    zvals.append(z)
zpool = np.concatenate(zvals)
P(f"    ANNEX (non-gating) z-pooled k=2 gross: mean z {np.nanmean(zpool):+.4f} (points / causal trailing-60 daily sd x sqrt2; n {np.sum(np.isfinite(zpool))})")
P("")

# ---- G3 control -------------------------------------------------------------------------
delta = obs_cons - ctrl_cons
d_boots = np.empty(NBOOT)
ctb_arr = [np.asarray(b) for b in ctb]
ct_vals = ct2["usd_cons_k2"].to_numpy()
for i in range(NBOOT):
    idx_e = RNG.integers(0, len(evb), len(evb))
    sel_e = np.concatenate([np.asarray(evb[j]) for j in idx_e])
    idx_c = RNG.integers(0, len(ctb_arr), len(ctb_arr))
    sel_c = np.concatenate([ctb_arr[j] for j in idx_c])
    d_boots[i] = np.nanmean(ev2["usd_cons_k2"].to_numpy()[sel_e]) - np.nanmean(ct_vals[sel_c])
d_lo, d_hi = np.percentile(d_boots, [2.5, 97.5])
P(f"MANDATORY CONTROL (same breach, NO prior compression, same k=2, same costs, same validity rule):")
P(f"    control mean (cons) ${ctrl_cons:+,.2f}/event over n {len(ct2)} ({len(ctb)} blocks); gross ${ctrl_gross:+,.2f}")
P(f"    DELTA (event - control, cons) = ${delta:+,.2f};  independent-block bootstrap 95% CI [${d_lo:+,.2f}, ${d_hi:+,.2f}]")
# composition-matched annex
comp_delta = 0.0
rows_cd = []
for m in data:
    e_m = ev2[ev2.market == m]["usd_cons_k2"]; c_m = ct2[ct2.market == m]["usd_cons_k2"]
    dm = (np.nanmean(e_m) - np.nanmean(c_m)) if len(e_m) and len(c_m) else np.nan
    w = len(e_m) / len(ev2)
    if np.isfinite(dm):
        comp_delta += w * dm
    rows_cd.append(dict(market=m, n_event=len(e_m), n_control=len(c_m),
                        event_mean_cons=float(np.nanmean(e_m)) if len(e_m) else np.nan,
                        control_mean_cons=float(np.nanmean(c_m)) if len(c_m) else np.nan,
                        delta=dm, event_weight=w))
P(f"    ANNEX composition-matched delta (event-weighted per-market deltas): ${comp_delta:+,.2f}")
P("")

# ---- G4 asymmetry -----------------------------------------------------------------------
w2 = ev2[ev2.split == "WITH"]; a2 = ev2[ev2.split == "AGAINST"]
wm = float(np.nanmean(w2["usd_cons_k2"])) if len(w2) else np.nan
am = float(np.nanmean(a2["usd_cons_k2"])) if len(a2) else np.nan
diffs = np.empty(NBOOT)
wmask = (ev2.split == "WITH").to_numpy()
vals2 = ev2["usd_cons_k2"].to_numpy()
for i in range(NBOOT):
    idx = RNG.integers(0, len(evb), len(evb))
    sel = np.concatenate([np.asarray(evb[j]) for j in idx])
    ws = vals2[sel][wmask[sel]]; as_ = vals2[sel][~wmask[sel]]
    diffs[i] = (np.nanmean(ws) if len(ws) else np.nan) - (np.nanmean(as_) if len(as_) else np.nan)
diffs = diffs[np.isfinite(diffs)]
a_lo, a_hi = np.percentile(diffs, [2.5, 97.5])
asym_claim = "CLAIMED" if (a_lo > 0 or a_hi < 0) else "NOT CLAIMED (unpowered/indistinct -- reported only)"
# each split's own CI
def split_ci(mask):
    arr = np.empty(NBOOT)
    for i in range(NBOOT):
        idx = RNG.integers(0, len(evb), len(evb))
        sel = np.concatenate([np.asarray(evb[j]) for j in idx])
        v = vals2[sel][mask[sel]]
        arr[i] = np.nanmean(v) if len(v) else np.nan
    arr = arr[np.isfinite(arr)]
    return np.percentile(arr, [2.5, 97.5])
w_lo, w_hi = split_ci(wmask); ag_lo, ag_hi = split_ci(~wmask)
P(f"ASYMMETRY (k=2 cons): WITH-trend n {len(w2)} mean ${wm:+,.2f} CI [{w_lo:+,.2f},{w_hi:+,.2f}] | "
  f"AGAINST n {len(a2)} mean ${am:+,.2f} CI [{ag_lo:+,.2f},{ag_hi:+,.2f}]")
P(f"    WITH-minus-AGAINST = ${wm-am:+,.2f}, block-bootstrap 95% CI [${a_lo:+,.2f}, ${a_hi:+,.2f}]  -> {asym_claim}")
P("")

# ---- G5 eras ----------------------------------------------------------------------------
P("ERA TABLE (k=2 after-cost CONS, pooled; sign gates G5; CL contributes only to era3 by span):")
era_rows = []
for e in ["era1_<=2015", "era2_2016-21", "era3_2022-26"]:
    sub = ev2[ev2.era == e]
    m_ = float(np.nanmean(sub["usd_cons_k2"])) if len(sub) else np.nan
    g_ = float(np.nanmean(sub["usd_gross_k2"])) if len(sub) else np.nan
    csub = ct2[ct2.era == e]
    cm_ = float(np.nanmean(csub["usd_cons_k2"])) if len(csub) else np.nan
    sign = "+" if m_ > 0 else "-"
    era_rows.append((e, len(sub), g_, m_, cm_, sign))
    P(f"    {e:14s} n {len(sub):4d}  gross ${g_:+9,.2f}  aftercost ${m_:+9,.2f}  ctrl ${cm_:+9,.2f}  sign {sign}")
signs = "".join(r[5] for r in era_rows)
era3_mean = era_rows[2][3]
era_class = ("STRUCTURAL (all +)" if signs == "+++" else
             ("SIGN-FLIP / modern-negative" if era3_mean < 0 else "MIXED, modern-positive"))
P(f"    ERA CLASSIFICATION: {signs} -> {era_class}")
P("")

# ---- cells (all k, per market, splits, spec-literal annex) ------------------------------
cells = []
def add_cell(tag, df_, k, market="POOLED", split="ALL"):
    v = df_[f"usd_cons_k{k}"]; g_ = df_[f"usd_gross_k{k}"]; p_ = df_[f"pts_k{k}"]
    n = int(np.isfinite(p_).sum())
    cells.append(dict(cell=tag, market=market, k=k, split=split, n=n,
                      mean_pts=float(np.nanmean(p_)) if n else np.nan,
                      mean_usd_gross=float(np.nanmean(g_)) if n else np.nan,
                      mean_usd_opt=float(np.nanmean(df_[f"usd_opt_k{k}"])) if n else np.nan,
                      mean_usd_cons=float(np.nanmean(v)) if n else np.nan))
for k in K_HOLDS:
    add_cell(f"EVENT_pooled_k{k}", ev, k)
    add_cell(f"CONTROL_pooled_k{k}", ct, k)
    add_cell(f"EVENT_lit_pooled_k{k}", evl, k, market="POOLED", split="SPEC-LITERAL comp[t]")
    for m in data:
        add_cell(f"EVENT_{m}_k{k}", ev[ev.market == m], k, market=m)
        add_cell(f"CONTROL_{m}_k{k}", ct[ct.market == m], k, market=m)
    for sp in ["WITH", "AGAINST"]:
        add_cell(f"EVENT_pooled_{sp}_k{k}", ev[ev.split == sp], k, split=sp)
cells_df = pd.DataFrame(cells)
cells_df.to_csv(os.path.join(OUT, "cells.csv"), index=False)

P("PER-MARKET k=2 (events, after-cost cons $/event):")
for m in data:
    sub = ev2[ev2.market == m]
    if len(sub):
        P(f"    {m}: n {len(sub):4d}  gross ${float(np.nanmean(sub['usd_gross_k2'])):+9,.2f}  cons ${float(np.nanmean(sub['usd_cons_k2'])):+9,.2f}  "
          f"(ctrl cons ${float(np.nanmean(ct2[ct2.market==m]['usd_cons_k2'])):+9,.2f}, n_ctrl {len(ct2[ct2.market==m])})")
P("")
P(f"SPEC-LITERAL comp[t] annex (k=2 pooled, cons): n {int(np.isfinite(evl['pts_k2']).sum()) if len(evl) else 0}  "
  f"mean ${float(np.nanmean(evl['usd_cons_k2'])) if len(evl) else float('nan'):+,.2f}   (non-gating; O2 disclosed)")
P("")

pd.DataFrame(rows_cd + [dict(market="POOLED_RAW", n_event=len(ev2), n_control=len(ct2),
                             event_mean_cons=obs_cons, control_mean_cons=ctrl_cons, delta=delta,
                             event_weight=1.0),
                        dict(market="POOLED_COMPOSITION_MATCHED", n_event=len(ev2), n_control=len(ct2),
                             event_mean_cons=obs_cons, control_mean_cons=obs_cons - comp_delta,
                             delta=comp_delta, event_weight=1.0)]).to_csv(
    os.path.join(OUT, "control_delta.csv"), index=False)

# ---- costs print ------------------------------------------------------------------------
P("COSTS/ct RT (MODELED ALL_IN rungs = {1,2}-tick RT spread band + $4.36 commission; basis MODELED, EVIDENCE: family convention COST_MODEL.md):")
for m, d in MKT.items():
    P(f"    {m}: tick {d['tick']} x ${d['pv']:,.0f}/pt -> opt ${d['cost_opt']:,.2f} | cons ${d['cost_cons']:,.2f}")
P("")

# ---- gates ------------------------------------------------------------------------------
g1 = "PASS"  # printed above, before observed means
g2_pass = (obs_cons > 0) and (ci_lo > 0) and (p_1s < 0.05)
g3_pass = (delta > 0) and (d_lo > 0)
g4 = "PASS"  # printed with own CIs; claim discipline applied mechanically
g5_pass = era3_mean >= 0
g6 = "PASS"

gate_rows = [
    ("G1_MDE_FIRST", "MDE printed per market + pooled BEFORE observed means",
     f"per-market + pooled MDE80 ${MDE_POOL:,.0f}/event at N={N2}", g1),
    ("G2_EDGE", "pooled k=2 after-cost(cons) mean > 0 AND event-block CI excl 0 AND shared-draw p < .05",
     f"mean ${obs_cons:+,.2f}, CI [{ci_lo:+,.2f},{ci_hi:+,.2f}], p_1s {p_1s:.4f}",
     "PASS" if g2_pass else "*** FAIL ***"),
    ("G3_VS_CONTROL", "beats unconditional-break control; delta CI excludes 0 (same drift in control = FAIL)",
     f"delta ${delta:+,.2f}, CI [{d_lo:+,.2f},{d_hi:+,.2f}]; comp-matched ${comp_delta:+,.2f}",
     "PASS" if g3_pass else "*** FAIL ***"),
    ("G4_ASYMMETRY", "WITH vs AGAINST printed, each with own CI; claim only if diff CI excl 0",
     f"WITH ${wm:+,.2f} vs AGAINST ${am:+,.2f}; diff CI [{a_lo:+,.2f},{a_hi:+,.2f}] -> {asym_claim}", g4),
    ("G5_ERA", "3-era signs on pooled cell; modern(era3 2022-26)-negative = FAIL",
     f"{signs} -> {era_class}; era3 mean ${era3_mean:+,.2f}",
     "PASS" if g5_pass else "*** FAIL ***"),
    ("G6_COST", "{1,2}-tick RT band + $4.36 comm; ticks asserted from data; cons rung gates",
     "all 5 rungs printed; ticks asserted on raw closes (NQ spine: contract-spec, noted)", g6),
]
P("GATE TABLE  (printed by program)")
P(f"{'GATE':16s}{'SPEC':94s}{'OBSERVED':92s}PASS-FAIL")
for g_, s_, o_, r_ in gate_rows:
    P(f"{g_:16s}{s_:94s}{o_:92s}{r_}")
P("")

candidate = g2_pass and g3_pass and g5_pass
if candidate:
    verdict = "G2+G3+G5 PASS -> COMPCASCADE01 candidate"
else:
    verdict = (f"G2={'PASS' if g2_pass else 'FAIL'} G3={'PASS' if g3_pass else 'FAIL'} "
               f"G5={'PASS' if g5_pass else 'FAIL'} -> CLOSED AT SCOPE (S28 block)")
P(f"DECISION RULE (spec, mechanical): {verdict}")
yrs = (max(d["dates"].iloc[-1] for d in data.values()) - min(d["dates"].iloc[0] for d in data.values())).days / 365.25
P(f"events/yr (pooled, union span ~{yrs:.1f}y) = {len(ev2)/yrs:.1f}; after-cost economics at cons rung = ${obs_cons*len(ev2)/yrs:+,.0f}/yr across the 5-market union")
P("")
P("PREREG CONSTANTS ECHO: " + json.dumps({
    "range_win": 5, "quantile_win": 60, "bottom_q": 0.2, "break_lookback": 5, "drift_win": 20,
    "k_holds": K_HOLDS, "k_primary": 2, "warmup": WARMUP, "clean_gap_days_max": 5,
    "block_chain_gap_days": 5, "n_shift": NSHIFT, "n_boot": NBOOT, "commission": COMM,
    "cost_rungs_ticks_RT": [1, 2], "gating_rung": "cons",
    "eras": ["<=2015", "2016-21", "2022-26"], "compression_timing_primary": "comp[t-1] (O2)",
    "seed": 93}))
P("=" * 118)

with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
    f.write(LOG.getvalue())
print("WROTE out/gate_table.txt, out/cells.csv, out/control_delta.csv, out/cl_daily.parquet")
