"""W7-2 FSS-9: sweep -> reclaim trade rules at dynamic/prior levels (new level class).
Frozen spec: specs/W7_rt2_discharge.md section "W7-2" (committed 1d76c14 before readout).
Seed 20260808. FSS-5 grammar (w4c_fss5.py) extended to array-valued levels.

Levels per session (all converted to TICKS, actual contract space):
  VWAP = running RTH-anchored VWAP from grid1s (cum(last*vol)/cum(vol) from 09:30),
         usable as a level only from 09:45. MOVING level: sweep/reclaim/re-arm are
         evaluated against the CURRENT VWAP value at each second (L[t], not a frozen
         snapshot). Two-sided (long low-side reclaim AND short high-side reclaim).
  PDH / PDL = prior trading day's RTH high / low from runs/AUDIT03_BARS 3-min CSV
         (back-adjusted space), converted to actual space via the per-session offset.
         PDH short-side primary; PDL long-side primary (one-sided).
  PC   = prior day's RTH close (close of last CSV bar end-stamped in (09:30,16:00]
         on the prior date), offset-converted. Two-sided.
Back-adjustment offset (frozen rule): offset_s = (CSV 09:30-stamped bar close on the
session date, in ticks) - (sechilo mid_last at 09:30:00 same date, ticks). Actual-space
level = CSV-space level - offset_s. The CSV close is a LAST price while sechilo is a
bid/ask MID (~1-tick Last-vs-mid error); offset constant within a session (no roll
inside a session).
OFFSET AMBIGUITY (measured, documented): the end-stamped CSV 09:30 bar closes with the
last trade BEFORE 09:30:00.000, while the sechilo second STAMPED 09:30:00 ends at
09:30:00.999 — inside the first RTH second. Audit (this artifact dir): CSV 09:30 close
vs grid1s last at second 09:29:59 is constant within contract era to std <= 0.7t
(exact pairing); vs the 09:30:00 second it carries the open-second jump, std 12-41t
per era. The frozen rule's stated ~1t error property therefore identifies the
PRE-open boundary pairing ("mid prevailing at the instant 09:30:00" = mid_last of
second 09:29:59, ffilled) as the intended reading. BOTH are run: ovar='pre0930'
(boundary-synchronized, primary) and ovar='lit0930' (literal 09:30:00-second,
sensitivity). VWAP needs no offset (ovar='none'). Verdict is rendered under both.

Rule (RECLAIM primary, FSS-5 grammar frozen): low-side approach at level L: sweep =
mid_low[t] <= L[t] - pierce (primary pierce=2t), reclaim = mid_last[i] >= L[i] + 1t
within W=60s of the FIRST sweep second -> MARKET entry at the reclaim second. High-side
approach symmetric (sweep mid_high >= L + pierce, reclaim mid_last <= L - 1t -> SHORT).
CONTINUATION mirror (frozen diagnostic, both reported): failure to reclaim within 60s
-> enter in the sweep direction at t0+60. One trade per level-sweep episode (re-arm at
|mid - L| >= 8t, current L); brackets (24,8),(32,10); cap 300s; cooldown 60s; sequential
per (level, side). Neighbors (reported, never selected on): pierce {1t,4t}. W fixed 60s.
Barriers on per-second mid_high/mid_low; same-second both-crossed -> ADVERSE.
Decisions (sweep detection + entries) only on RTH & quote-alive seconds.
Costs C1=2.872t, C2=4.872t RT. Day-clustered 95% CI: session bootstrap, 1000 reps.
Lift = P(target|rule) - unconditional census baseline (artifacts/census/
excursion_surface.csv, same bracket & trade direction; census cap 600s vs rule cap
300s — documented, not re-run). Pass: net C1 > 0 AND CI_lo > -0.5t. Family verdict by
plateau (reclaim side only; continuation is diagnostic).
Discovery substrate only; the 3-min CSV is read strictly below 2026-06-01.
"""
import glob, os
import numpy as np, pandas as pd
from numba import njit

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
SH = os.path.join(ROOT, "research", "scalping_lab", "substrate", "sechilo", "NQ")
GR = os.path.join(ROOT, "research", "scalping_lab", "substrate", "grid1s", "NQ")
CSV = os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv")
CENSUS = os.path.join(ROOT, "research", "scalping_lab", "artifacts", "census",
                      "excursion_surface.csv")
OUTD = os.path.join(ROOT, "research", "scalping_lab", "artifacts", "w7_fss9")
os.makedirs(OUTD, exist_ok=True)

PIERCES = [1.0, 2.0, 4.0]          # 2 = primary; 1/4 = frozen neighbors
W = 60                             # frozen (no window neighbors in W7-2)
BRK = [(24, 8), (32, 10)]          # frozen brackets
CAP = 300
COOL = 60
REARM = 8.0
C1, C2 = 2.872, 4.872
RTH0, VWAP_OK, RTH1 = 9*3600+1800, 9*3600+2700, 16*3600   # 09:30 / 09:45 / 16:00
DEV_CUTOFF = pd.Timestamp("2026-06-01")   # never read CSV rows >= this


@njit(cache=True)
def simulate_level(ml, hi, lo, dec, avail, Lv, lvl_side, mode, pierce, W, A, B,
                   cap, cool, rearm):
    """Sequential per-(level,side) state machine; Lv is the level VALUE PER SECOND
    (constant array for static levels, running VWAP for the moving level).
    lvl_side: +1 = low-side approach (sweep down / reclaim long), -1 = high-side.
    mode: 0 = RECLAIM trade, 1 = CONTINUATION trade (failure-to-reclaim mirror).
    Returns entry_idx, outcome (1 tgt / 2 adv / 3 cap), gross ticks, n_sweep episodes."""
    n = ml.shape[0]
    e_idx = np.empty(n, np.int64); e_out = np.empty(n, np.int8)
    e_gross = np.empty(n, np.float64)
    m = 0; n_sweep = 0
    t = 0; armed = True; next_ok = 0
    while t < n:
        if not armed:
            d = ml[t] - Lv[t]
            if d < 0.0: d = -d
            if d >= rearm:            # NaN-safe: comparison with NaN is False
                armed = True          # fall through: same second may sweep again
            else:
                t += 1
                continue
        swept = False
        if dec[t] and avail[t] and t >= next_ok:
            if lvl_side == 1:
                swept = lo[t] <= Lv[t] - pierce
            else:
                swept = hi[t] >= Lv[t] + pierce
        if not swept:
            t += 1
            continue
        n_sweep += 1
        t0 = t
        wend = t0 + W
        if wend > n - 1: wend = n - 1
        rec_i = -1
        for i in range(t0, wend + 1):          # reclaim vs CURRENT level value
            if lvl_side == 1:
                if ml[i] >= Lv[i] + 1.0: rec_i = i; break
            else:
                if ml[i] <= Lv[i] - 1.0: rec_i = i; break
        te = -1; ddir = 0
        if mode == 0:                                  # RECLAIM side
            if rec_i >= 0 and dec[rec_i]:
                te = rec_i; ddir = 1 if lvl_side == 1 else -1
            resume = (rec_i + 1) if rec_i >= 0 else (wend + 1)
        else:                                          # CONTINUATION mirror
            if rec_i < 0:
                cand = t0 + W
                if cand <= n - 1 and dec[cand]:
                    te = cand; ddir = -1 if lvl_side == 1 else 1
                resume = wend + 1
            else:
                resume = rec_i + 1
        if te >= 0:
            entry = ml[te]
            res = 0; i = te + 1
            end = te + cap
            if end > n - 1: end = n - 1
            while i <= end:
                up = hi[i] - entry; dn = entry - lo[i]
                if ddir == 1:
                    t_hit = up >= A; a_hit = dn >= B
                else:
                    t_hit = dn >= A; a_hit = up >= B
                if a_hit:                  # adverse first: same-second both -> ADVERSE
                    res = 2; break
                if t_hit:
                    res = 1; break
                i += 1
            if res == 1: g = float(A)
            elif res == 2: g = -float(B)
            else:
                res = 3; g = (ml[end] - entry) * ddir; i = end
            e_idx[m] = te; e_out[m] = res; e_gross[m] = g; m += 1
            next_ok = i + cool
            resume = i + 1
        armed = False                      # disarm until |mid - L| >= re-arm 8t
        t = resume
    return e_idx[:m], e_out[:m], e_gross[:m], n_sweep


# ---------- prior-day levels from the 3-min CSV (back-adjusted space) ----------
bars = pd.read_csv(CSV, parse_dates=["time"])
bars = bars[bars["time"] < DEV_CUTOFF].copy()          # dev-window guard, frozen
todb = (bars["time"].dt.hour * 3600 + bars["time"].dt.minute * 60
        + bars["time"].dt.second)
bars["date"] = bars["time"].dt.normalize()
rth_b = bars[(todb > RTH0) & (todb <= RTH1)]           # end-stamped: 09:33..16:00
rth_b = rth_b.sort_values("time")
day = rth_b.groupby("date").agg(pdh_csv=("high", "max"), pdl_csv=("low", "min"),
                                pclose_csv=("close", "last"),
                                last_bar=("time", "last"), n_bars=("time", "size"))
open0930 = bars[todb == RTH0].set_index("date")["close"]   # 09:30-stamped bar close
rth_dates = day.index.to_numpy()

# ---------- unconditional census baselines (same bracket & trade direction) ----------
cen = pd.read_csv(CENSUS)
BASE = {(r.dir, int(r.A), int(r.B)): float(r.p_target) for r in cen.itertuples()}

# ---------- per-session simulation ----------
rows, lvl_rows = [], []
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
    ml = f["mid_last"].values; hi = f["mid_high"].values; lo = f["mid_low"].values
    tod = (f["time"] - d).dt.total_seconds().values
    upd60 = pd.Series((f["bid_upd"] + f["ask_upd"]).values).rolling(60, min_periods=1).sum().values
    dec = ((tod >= RTH0) & (tod < RTH1) & (upd60 > 0)).astype(np.bool_)
    n = len(f)

    # --- running RTH-VWAP from grid1s (price -> ticks), moving level ---
    last_p = f["last"].values.astype(np.float64)
    vol = f["vol"].values.astype(np.float64)
    in_rth = tod >= RTH0
    pv = np.where(in_rth & np.isfinite(last_p), last_p * vol, 0.0)
    vv = np.where(in_rth & np.isfinite(last_p), vol, 0.0)
    cs_pv = np.cumsum(pv); cs_vv = np.cumsum(vv)
    vwap_t = np.where(cs_vv > 0, cs_pv / np.where(cs_vv > 0, cs_vv, 1.0), np.nan) / 0.25
    avail_vwap = ((tod >= VWAP_OK) & np.isfinite(vwap_t)).astype(np.bool_)
    avail_rth = (tod >= RTH0).astype(np.bool_)

    # --- prior-day levels: offset-convert CSV space -> actual ticks (2 variants) ---
    i0930 = np.searchsorted(tod, RTH0)
    have_0930 = i0930 < n and tod[i0930] == RTH0
    i0929 = np.searchsorted(tod, RTH0 - 1)
    have_0929 = i0929 < n and tod[i0929] == RTH0 - 1
    prior_ok = False
    offs = {"lit0930": np.nan, "pre0930": np.nan}
    lvls_t = {}
    pd_date = None
    if have_0930 and have_0929 and d in open0930.index:
        mask = rth_dates < np.datetime64(d)
        if mask.any():
            pd_date = pd.Timestamp(rth_dates[mask][-1])
            csv0930_t = float(open0930.loc[d]) / 0.25
            offs["lit0930"] = csv0930_t - float(ml[i0930])   # 09:30:00 second (literal)
            offs["pre0930"] = csv0930_t - float(ml[i0929])   # mid at instant 09:30:00
            r = day.loc[pd_date]
            for ov, off_s in offs.items():
                lvls_t[ov] = dict(PDH=float(r.pdh_csv) / 0.25 - off_s,
                                  PDL=float(r.pdl_csv) / 0.25 - off_s,
                                  PC=float(r.pclose_csv) / 0.25 - off_s)
            prior_ok = True

    lvl_rows.append(dict(
        session=tag, n_sec=n, dec_secs=int(dec.sum()),
        vwap_secs=int(avail_vwap.sum()),
        vwap_0945_t=float(vwap_t[np.searchsorted(tod, VWAP_OK)]) if avail_vwap.any() else np.nan,
        vwap_close_t=float(vwap_t[-1]) if np.isfinite(vwap_t[-1]) else np.nan,
        mid_0930_t=float(ml[i0930]) if have_0930 else np.nan,
        mid_0929_t=float(ml[i0929]) if have_0929 else np.nan,
        csv_0930_close=float(open0930.loc[d]) if d in open0930.index else np.nan,
        offset_lit_t=offs["lit0930"], offset_pre_t=offs["pre0930"],
        prior_date=str(pd_date.date()) if pd_date is not None else "",
        prior_last_bar=str(day.loc[pd_date].last_bar) if prior_ok else "",
        **{f"{k}_{ov}_t": lvls_t[ov][k] for ov in lvls_t for k in ("PDH", "PDL", "PC")},
        PDH_dist_pre_t=(lvls_t["pre0930"]["PDH"] - ml[i0930]) if prior_ok else np.nan,
        PDL_dist_pre_t=(ml[i0930] - lvls_t["pre0930"]["PDL"]) if prior_ok else np.nan))

    # --- level set: (name, side, Lv array, avail, offset-variant) ---
    const = lambda v: np.full(n, v, np.float64)
    levels = [("VWAP", 1, vwap_t, avail_vwap, "none"),
              ("VWAP", -1, vwap_t, avail_vwap, "none")]
    if prior_ok:
        for ov in ("pre0930", "lit0930"):
            levels += [("PDH", -1, const(lvls_t[ov]["PDH"]), avail_rth, ov),
                       ("PDL", 1, const(lvls_t[ov]["PDL"]), avail_rth, ov),
                       ("PC", 1, const(lvls_t[ov]["PC"]), avail_rth, ov),
                       ("PC", -1, const(lvls_t[ov]["PC"]), avail_rth, ov)]
    for lname, side, Lv, avail, ovar in levels:
        sidename = "low" if side == 1 else "high"
        for mode, mname in ((0, "reclaim"), (1, "cont")):
            ddirname = ("long" if side == 1 else "short") if mode == 0 else \
                       ("short" if side == 1 else "long")
            for pierce in PIERCES:
                for (A, B) in BRK:
                    ei, eo, eg, nsw = simulate_level(
                        ml, hi, lo, dec, avail, Lv, side, mode, pierce, W,
                        float(A), float(B), CAP, COOL, REARM)
                    rows.append(dict(session=tag, level=lname, side=sidename,
                                     ovar=ovar, mode=mname, dir=ddirname, pierce=pierce,
                                     A=A, B=B, n_sweep=nsw, n=len(ei),
                                     n_tgt=int((eo == 1).sum()),
                                     n_adv=int((eo == 2).sum()),
                                     n_cap=int((eo == 3).sum()),
                                     gross_sum=float(eg.sum())))
    print(tag, "done", flush=True)

R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUTD, "w7fss9_results.csv"), index=False)
LV = pd.DataFrame(lvl_rows)
LV.to_csv(os.path.join(OUTD, "w7fss9_levels.csv"), index=False)
NDAYS = len(sessions)
print(f"\nsessions={NDAYS}  per-session rows={len(R)}")
print("offset audit (ticks): pre0930 = CSV 09:30 close - mid at instant 09:30:00 "
      "(second 09:29:59); lit0930 = vs the 09:30:00-stamped second (open-second jump):")
LVa = LV[LV.dec_secs > 0].copy()      # exclude quote-dead s20250902 (garbage mid)
LVa["era"] = (LVa["offset_pre_t"].diff().abs() > 500).cumsum()
for e, gp in LVa.groupby("era"):
    print(f"  era{e} ({gp.session.iloc[0]}..{gp.session.iloc[-1]}): "
          f"pre0930 med={gp.offset_pre_t.median():.1f} std={gp.offset_pre_t.std():.2f} | "
          f"lit0930 med={gp.offset_lit_t.median():.1f} std={gp.offset_lit_t.std():.2f}")

brng = np.random.default_rng(20260808)
pooled = []
def pool(gsub):
    """Pooled stats + day-clustered bootstrap CI (sessions with >=1 trade), on
    per-trade net; also session-bootstrap CI on P(target)."""
    g = gsub[gsub.n > 0]
    n = int(g.n.sum())
    out = dict(n_sweep=int(gsub.n_sweep.sum()), n=n, days=int((g.n > 0).sum()))
    if n == 0:
        return out
    dec_n = int((g.n_tgt + g.n_adv).sum())
    out["p_tgt"] = g.n_tgt.sum() / dec_n if dec_n else np.nan
    out["n_cap"] = int(g.n_cap.sum())
    gross = g.gross_sum.sum() / n
    out["net1"] = gross - C1; out["net2"] = gross - C2
    per = (g.gross_sum / g.n).values; w = g.n.values
    tgt = g.n_tgt.values; dcd = (g.n_tgt + g.n_adv).values
    idx = np.arange(len(per))
    boots = np.empty(1000); pboots = np.full(1000, np.nan)
    for r in range(1000):
        b = brng.choice(idx, len(idx), replace=True)
        boots[r] = np.average(per[b], weights=w[b])
        if dcd[b].sum() > 0:
            pboots[r] = tgt[b].sum() / dcd[b].sum()
    out["ci1_lo"] = np.percentile(boots, 2.5) - C1
    out["ci1_hi"] = np.percentile(boots, 97.5) - C1
    out["ci2_lo"] = out["ci1_lo"] - 2.0; out["ci2_hi"] = out["ci1_hi"] - 2.0
    pb = pboots[np.isfinite(pboots)]
    if len(pb):
        out["p_ci_lo"] = np.percentile(pb, 2.5); out["p_ci_hi"] = np.percentile(pb, 97.5)
    return out

LEVELSIDES = [("VWAP", "low", "none"), ("VWAP", "high", "none"),
              ("PDH", "high", "pre0930"), ("PDL", "low", "pre0930"),
              ("PC", "low", "pre0930"), ("PC", "high", "pre0930"),
              ("PDH", "high", "lit0930"), ("PDL", "low", "lit0930"),
              ("PC", "low", "lit0930"), ("PC", "high", "lit0930")]
for mname in ("reclaim", "cont"):
    hdr = "RECLAIM (primary side)" if mname == "reclaim" else "CONTINUATION mirror (diagnostic)"
    print(f"\n=== W7-2 FSS-9 {hdr} — pooled by config ===")
    print(f"{'level':>5} {'side':>4} {'ovar':>7} {'dir':>5} {'prc':>3} {'A':>3} {'B':>3} | "
          f"{'sweeps':>6} {'epi':>5} {'epi/d':>6} {'days':>4} {'P(tgt)':>7} {'base':>6} "
          f"{'lift':>7} {'BE_C1':>6} | {'netC1':>7} {'CI_lo':>7} {'CI_hi':>7} | "
          f"{'netC2':>7} | {'pass':>4}")
    for lname, sname, ovar in LEVELSIDES:
        for pierce in PIERCES:
            for (A, B) in BRK:
                gsub = R[(R["level"] == lname) & (R["side"] == sname)
                         & (R["ovar"] == ovar) & (R["mode"] == mname)
                         & (R["pierce"] == pierce) & (R["A"] == A) & (R["B"] == B)]
                if not len(gsub): continue
                o = pool(gsub)
                ddir = gsub.dir.iloc[0]
                base = BASE[(ddir, A, B)]
                star = " *" if pierce == 2.0 else ""
                if o["n"] == 0:
                    print(f"{lname:>5} {sname:>4} {ovar:>7} {ddir:>5} {int(pierce):>3} "
                          f"{A:>3} {B:>3} | {o['n_sweep']:>6} {0:>5}  (no trades){star}")
                    pooled.append(dict(level=lname, side=sname, ovar=ovar, mode=mname,
                                       dir=ddir, pierce=pierce, A=A, B=B, base=base, **o))
                    continue
                be1 = (B + C1) / (A + B)
                lift = o["p_tgt"] - base if np.isfinite(o.get("p_tgt", np.nan)) else np.nan
                ok = (o["net1"] > 0) and (o["ci1_lo"] > -0.5)
                print(f"{lname:>5} {sname:>4} {ovar:>7} {ddir:>5} {int(pierce):>3} {A:>3} "
                      f"{B:>3} | {o['n_sweep']:>6} {o['n']:>5} {o['n']/NDAYS:>6.2f} "
                      f"{o['days']:>4} {o['p_tgt']:>7.4f} {base:>6.4f} {lift:>+7.4f} "
                      f"{be1:>6.4f} | {o['net1']:>+7.3f} {o['ci1_lo']:>+7.3f} "
                      f"{o['ci1_hi']:>+7.3f} | {o['net2']:>+7.3f} | "
                      f"{'PASS' if ok else 'fail':>4}{star}")
                pooled.append(dict(level=lname, side=sname, ovar=ovar, mode=mname,
                                   dir=ddir, pierce=pierce, A=A, B=B, base=base,
                                   lift=lift, be_c1=be1, passes=bool(ok), **o))
print("\n(* = primary pierce=2t; pierce 1t/4t are frozen neighbors; W=60s fixed."
      "\n ovar: pre0930 = boundary-synchronized offset (primary), lit0930 = literal"
      "\n 09:30:00-second offset (sensitivity), none = no offset needed (VWAP)."
      "\n base = unconditional census P(target), same bracket & direction, 30s clock"
      "\n (census cap 600s vs rule cap 300s — documented). pass: net C1 > 0 AND"
      f"\n CI_lo > -0.5t; epi/d over all {NDAYS} sessions)")

P = pd.DataFrame(pooled)
P.to_csv(os.path.join(OUTD, "w7fss9_pooled.csv"), index=False)

print("\n=== primary configs (pierce=2, W=60; ovar=pre0930 for prior levels) ===")
pr = P[(P["pierce"] == 2.0) & (P["ovar"].isin(["none", "pre0930"]))]
for _, r in pr.iterrows():
    if r["n"] == 0 or not np.isfinite(r.get("net1", np.nan)):
        print(f"  {r['mode']:>7} {r['level']:>5}/{r['side']:<4} {r['dir']:>5} "
              f"+{r['A']}/-{r['B']}: no trades")
    else:
        print(f"  {r['mode']:>7} {r['level']:>5}/{r['side']:<4} {r['dir']:>5} "
              f"+{int(r['A'])}/-{int(r['B'])}: n={int(r['n'])} epi/d={r['n']/NDAYS:.2f} "
              f"days={int(r['days'])} P(tgt)={r['p_tgt']:.4f} lift={r['lift']:+.4f} "
              f"netC1={r['net1']:+.3f} [{r['ci1_lo']:+.3f},{r['ci1_hi']:+.3f}] "
              f"netC2={r['net2']:+.3f} {'PASS' if r['passes'] else 'fail'}")

# ---------- plateau verdict (reclaim only; continuation is diagnostic) ----------
print("\n=== plateau check per (level, side, ovar) — RECLAIM ===")
verdicts = []
for lname, sname, ovar in LEVELSIDES:
    sub = P[(P["level"] == lname) & (P["side"] == sname) & (P["ovar"] == ovar)
            & (P["mode"] == "reclaim")]
    prim = sub[sub["pierce"] == 2.0]
    nbr = sub[sub["pierce"] != 2.0]
    n_prim = int(prim["passes"].fillna(False).sum()) if "passes" in prim else 0
    n_nbr = int(nbr["passes"].fillna(False).sum()) if "passes" in nbr else 0
    plateau = (n_prim == 2) and (n_nbr >= 2)
    verdicts.append(dict(level=lname, side=sname, ovar=ovar, prim_pass=n_prim,
                         prim_tot=len(prim), nbr_pass=n_nbr, nbr_tot=len(nbr),
                         plateau=plateau))
    print(f"  {lname:>5}/{sname:<4} {ovar:>7}: primary pass {n_prim}/{len(prim)}, "
          f"neighbor pass {n_nbr}/{len(nbr)} -> "
          f"{'PLATEAU SURVIVOR' if plateau else 'no plateau'}")
VD = pd.DataFrame(verdicts)
VD.to_csv(os.path.join(OUTD, "w7fss9_verdict.csv"), index=False)
npass_rec = int(P[(P['mode'] == 'reclaim')]["passes"].fillna(False).sum())
npass_cont = int(P[(P['mode'] == 'cont')]["passes"].fillna(False).sum())
n_rec = len(P[P['mode'] == 'reclaim']); n_cont = len(P[P['mode'] == 'cont'])
print(f"\npassing configs: reclaim={npass_rec}/{n_rec} cont={npass_cont}/{n_cont} "
      f"(cont diagnostic-only, never a family pass)")
fam_pre = bool(VD[VD.ovar.isin(["none", "pre0930"])]["plateau"].any())
fam_lit = bool(VD[VD.ovar.isin(["none", "lit0930"])]["plateau"].any())
print(f"FAMILY VERDICT (plateau rule, both primary brackets pass AND >=2/4 pierce "
      f"neighbors pass, reclaim side):")
print(f"  under pre0930 offset (primary reading):    "
      f"{'SURVIVOR' if fam_pre else 'FAIL'}")
print(f"  under lit0930 offset (sensitivity reading): "
      f"{'SURVIVOR' if fam_lit else 'FAIL'}")
print("\nW7-2 DONE")
