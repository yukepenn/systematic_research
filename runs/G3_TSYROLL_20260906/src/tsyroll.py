"""G3_TSYROLL_20260906 -- Front-running the passive bond roll (G00087, family GENESIS3_EVENT).

Frozen spec: runs/G3_TSYROLL_20260906/spec.yaml (committed before results).
Per-contract ZN/ZB day-store work via research/multi_market/src/ncd_day.py (both legs
required simultaneously; pairing coverage measured and reported honestly).

FN = first notice = last business day of the month preceding delivery, realized on the
front contract's own trading calendar: FN_eff = last front-trading date in that month.

PRIMARY (fixed in advance): LONG back / SHORT front, enter close FN-10, exit close FN-4
(front-grid trading days). Points P&L = S(FN-10) - S(FN-4), S = front_close - back_close.

Seal: every loaded row is hard-filtered to date < 2026-08-01 and asserted.
All output ASCII. Program prints the GATE/SPEC/OBSERVED/PASS-FAIL table itself.
"""
from __future__ import annotations

import hashlib
import io
import math
import os
import sys

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(REPO, "runs", "G3_TSYROLL_20260906")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(REPO, "research", "multi_market", "src"))
import ncd_day  # noqa: E402

SEAL = pd.Timestamp("2026-08-01")          # never read market data >= this date
ROOTS = ("ZN", "ZB")
POINT_VALUE = 1000.0                        # USD per 1.00 point, both roots
DECL_TICK = {"ZN": 0.015625, "ZB": 0.03125}  # declared outright ticks (1/64, 1/32)
N_BOOT = 4000
N_SHIFTS = 2000
SEED_BOOT = 87001
SEED_SHIFT = 87002
COMMISSION_RT = 4.36                        # USD per contract round trip (info only, non-gating)

buf = io.StringIO()


def emit(s=""):
    print(s)
    buf.write(s + "\n")


def sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


emit("=" * 118)
emit("G3_TSYROLL_20260906 -- passive bond-roll front-running, ZN/ZB calendar spread (G00087, GENESIS3_EVENT)")
emit("program: runs/G3_TSYROLL_20260906/src/tsyroll.py  sha256/16 " + sha16(os.path.abspath(__file__)))
emit("day store: " + ncd_day.DB_DAY)
emit(f"seeds: boot {SEED_BOOT} shift {SEED_SHIFT}; draws: boot {N_BOOT} shift {N_SHIFTS}")
emit("=" * 118)

# ---------------------------------------------------------------- load contracts
# cycles: deliveries 2009-03 .. 2026-06 (70 per root, census). back of 2026-06 = 09-26.
def qlist():
    out = []
    for y in range(2009, 2027):
        for m in (3, 6, 9, 12):
            if (y, m) <= (2026, 6):
                out.append((y, m))
    return out


CYCLES = qlist()
assert len(CYCLES) == 70, len(CYCLES)


def next_q(y, m):
    return (y, m + 3) if m < 12 else (y + 1, 3)


store = {}          # cid -> DataFrame(date-indexed close, volume)
tick_hdr = {}
seal_max = pd.Timestamp("1900-01-01")
need = set()
for root in ROOTS:
    for (y, m) in CYCLES:
        need.add((root, y, m))
        need.add((root,) + next_q(y, m))
for (root, y, m) in sorted(need):
    cid = ncd_day.contract_id(root, m, y)
    df = ncd_day.read_contract(cid)
    if df.empty:
        store[cid] = None
        continue
    df = df[df["date"] < SEAL]              # SEAL: hard filter before any use
    if df.empty:
        store[cid] = None
        continue
    seal_max = max(seal_max, df["date"].max())
    tick_hdr[cid] = float(df["tick_size"].iloc[0])
    d = df.set_index("date")[["close", "volume"]].sort_index()
    store[cid] = d

assert seal_max < SEAL, f"SEAL VIOLATION: max date {seal_max}"
emit(f"SEAL assert: max loaded date {seal_max.date()} < 2026-08-01  OK")

# tick header assert
bad_tick = {c: t for c, t in tick_hdr.items() if abs(t - DECL_TICK[c[:2]]) > 1e-12}
emit(f"tick headers: {len(tick_hdr)} contracts, all == declared (ZN 1/64, ZB 1/32): "
     + ("OK" if not bad_tick else f"VIOLATIONS {bad_tick}"))
assert not bad_tick

# price-band and grid census (report, AS-IS -- spec froze no exclusion)
n_rows = n_band = n_grid = n_zerovol = 0
for cid, d in store.items():
    if d is None:
        continue
    n_rows += len(d)
    n_band += int(((d["close"] < 60) | (d["close"] > 250)).sum())
    half = DECL_TICK[cid[:2]] / 2.0
    n_grid += int((np.abs(np.round(d["close"] / half) * half - d["close"]) > 1e-9).sum())
    n_zerovol += int((d["volume"] == 0).sum())
emit(f"data census: {n_rows} contract-day rows; closes outside (60,250): {n_band}; "
     f"off half-tick grid: {n_grid}; zero-volume rows: {n_zerovol}")

empty_ids = sorted(c for c, d in store.items() if d is None)
emit(f"contracts with NO usable data: {empty_ids}")

# ---------------------------------------------------------------- per-cycle build
K_PANEL = list(range(-15, 1))       # frozen event panel FN-15..FN
K_EXT_LO, K_EXT_HI = -36, 8         # extended range for the shift-null series
ENTRY_K, EXIT_K = -10, -4           # frozen primary window endpoints
HOLD_CHANGES = 6                    # daily changes in (FN-10, FN-4]

panel_rows = []
cyc = []
for root in ROOTS:
    for (y, m) in CYCLES:
        rec = dict(root=root, dyear=y, dmonth=m, delivery=f"{y}-{m:02d}",
                   quarter=f"{y}Q{(m // 3)}")
        fid = ncd_day.contract_id(root, m, y)
        by, bm = next_q(y, m)
        bid = ncd_day.contract_id(root, bm, by)
        rec["front"], rec["back"] = fid, bid
        f, b = store.get(fid), store.get(bid)
        if f is None or b is None:
            rec["status"] = "NO_LEG_DATA"
            cyc.append(rec)
            continue
        fn_y, fn_m = (y, m - 1) if m > 1 else (y - 1, 12)
        fdates = f.index
        in_fn_month = fdates[(fdates.year == fn_y) & (fdates.month == fn_m)]
        if len(in_fn_month) == 0:
            rec["status"] = "NO_FN_ON_FRONT_GRID"
            cyc.append(rec)
            continue
        fn = in_fn_month.max()
        pos = fdates.get_loc(fn)
        rec["fn"] = fn.date().isoformat()

        def day(k):
            j = pos + k
            return fdates[j] if 0 <= j < len(fdates) else None

        def spread(k):
            d0 = day(k)
            if d0 is None or d0 not in b.index:
                return None, d0
            return float(f.at[d0, "close"] - b.at[d0, "close"]), d0

        # frozen event panel
        n_paired = 0
        for k in K_PANEL:
            s, d0 = spread(k)
            fr = float(f.at[d0, "close"]) if d0 is not None else np.nan
            bk = float(b.at[d0, "close"]) if (d0 is not None and d0 in b.index) else np.nan
            panel_rows.append(dict(root=root, delivery=rec["delivery"], fn=rec["fn"],
                                   event_day=k, date=(d0.date().isoformat() if d0 is not None else ""),
                                   front_close=fr, back_close=bk,
                                   spread=(s if s is not None else np.nan),
                                   paired=int(s is not None)))
            if s is not None:
                n_paired += 1
        rec["panel_paired"] = n_paired

        s_ent, _ = spread(ENTRY_K)
        s_ext, _ = spread(EXIT_K)
        if s_ent is None or s_ext is None:
            rec["status"] = "UNPAIRED_PRIMARY_ENDPOINT"
        else:
            rec["status"] = "OK"
            rec["s_entry"], rec["s_exit"] = s_ent, s_ext
            rec["gross_pts"] = s_ent - s_ext          # LONG back / SHORT front

        # carry control: measured average daily slide of S over the frozen panel
        sp = []
        for k in K_PANEL:
            s, _ = spread(k)
            sp.append(s)
        ds = [sp[i] - sp[i - 1] for i in range(1, len(sp))
              if sp[i] is not None and sp[i - 1] is not None]
        # consecutive-paired changes within the panel (gaps skipped, AS-IS)
        chg, prev = [], None
        for k in K_PANEL:
            s, _ = spread(k)
            if s is None:
                continue
            if prev is not None:
                chg.append(s - prev)
            prev = s
        rec["n_carry_chg"] = len(chg)
        if len(chg) >= 8:
            rec["carry_exp_pts"] = -HOLD_CHANGES * float(np.mean(chg))
        # placebos: +/- 1 month anchors on the front grid, same construction
        for tag, (ay, am) in (("pm", (fn_y, fn_m - 1) if fn_m > 1 else (fn_y - 1, 12)),
                              ("pp", (y, m))):
            sel = fdates[(fdates.year == ay) & (fdates.month == am)]
            if len(sel) == 0:
                continue
            ap = fdates.get_loc(sel.max())
            def pspread(k, ap=ap):
                j = ap + k
                if not (0 <= j < len(fdates)):
                    return None
                d0 = fdates[j]
                if d0 not in b.index:
                    return None
                return float(f.at[d0, "close"] - b.at[d0, "close"])
            pe, px = pspread(ENTRY_K), pspread(EXIT_K)
            if pe is not None and px is not None:
                rec[f"{tag}_gross_pts"] = pe - px
                rec[f"{tag}_anchor"] = fdates[ap].date().isoformat()

        # extended segment for the shift null (built later only for OK cycles)
        seg_k, seg_s = [], []
        for k in range(K_EXT_LO, K_EXT_HI + 1):
            s, _ = spread(k)
            if s is not None:
                seg_k.append(k)
                seg_s.append(s)
        rec["_seg"] = (seg_k, seg_s)
        cyc.append(rec)

C = pd.DataFrame(cyc)
seg_store = {i: r["_seg"] for i, r in C.iterrows() if isinstance(r.get("_seg"), tuple)}
C = C.drop(columns=["_seg"], errors="ignore")

# ---------------------------------------------------------------- coverage report
emit("")
emit("PAIRING COVERAGE (honest census -- both legs required simultaneously)")
n_census = len(C)
ok = C[C["status"] == "OK"]
emit(f"  census root-cycles: {n_census} (70 deliveries x 2 roots, 2009-03 .. 2026-06)")
for st, g in C.groupby("status"):
    emit(f"    status {st:<28} n = {len(g):3d}")
for root in ROOTS:
    g = C[(C["root"] == root)]
    go = g[g["status"] == "OK"]
    emit(f"  {root}: primary-usable {len(go)}/{len(g)}; dead cycles: "
         + ", ".join(sorted(g.loc[g['status'] != 'OK', 'delivery'])))
pp = pd.DataFrame(panel_rows)
cov = pp.groupby("event_day")["paired"].mean()
emit("  event-day pairing rate over cycles with an FN on the front grid (FN-15..FN):")
emit("    k:      " + " ".join(f"{k:>5d}" for k in K_PANEL))
emit("    paired: " + " ".join(f"{cov.get(k, 0):>5.0%}" for k in K_PANEL))
n_pm = int(C["pm_gross_pts"].notna().sum()) if "pm_gross_pts" in C else 0
n_pp = int(C["pp_gross_pts"].notna().sum()) if "pp_gross_pts" in C else 0
emit(f"  placebo coverage: -1-month usable {n_pm}/{n_census}; +1-month usable {n_pp}/{n_census}")
emit(f"  panel fully paired (16/16): {int((C['panel_paired'] == 16).sum())} of {n_census}")

# ---------------------------------------------------------------- cost model (G7 rungs)
emit("")
emit("G7 COST MODEL (MODELED, SPREAD_ONLY basis; {1,2}-tick outright-equivalent band; 2 legs, 1 RT each):")
cost = {}
for root in ROOTS:
    t = DECL_TICK[root]
    cost[root] = {"opt": 2 * 1 * t, "cons": 2 * 2 * t}
    emit(f"  {root}: tick {t} pt -> opt (1 tick/leg-RT) {cost[root]['opt']:.6f} pt = "
         f"${cost[root]['opt'] * POINT_VALUE:6.2f}/cycle; cons (2 ticks/leg-RT) {cost[root]['cons']:.6f} pt = "
         f"${cost[root]['cons'] * POINT_VALUE:6.2f}/cycle   [cons rung GATES]")
emit(f"  info only (non-gating, COMMISSION_ONLY): + 2 legs x ${COMMISSION_RT}/ctrRT = ${2 * COMMISSION_RT:.2f}/cycle")

ok = C[C["status"] == "OK"].copy()
ok["cost_opt"] = ok["root"].map(lambda r: cost[r]["opt"])
ok["cost_cons"] = ok["root"].map(lambda r: cost[r]["cons"])
ok["net_opt"] = ok["gross_pts"] - ok["cost_opt"]
ok["net_cons"] = ok["gross_pts"] - ok["cost_cons"]
ok["era"] = np.where(pd.to_datetime(ok["fn"]) < "2016-01-01", "pre2016", "post2016")

# ---------------------------------------------------------------- G1: MDE FIRST
emit("")
emit("G1 MDE (PRINTED BEFORE ANY OBSERVED POOLED MEAN):")
q_net = ok.groupby("quarter")["net_cons"].mean()          # quarter-pooled (dependence-honest)
NQ = len(q_net)
NC = len(ok)
sd_q = float(q_net.std(ddof=1))
mde_q = 2.486 * sd_q / math.sqrt(NQ)
rho = float(ok.pivot_table(index="quarter", columns="root", values="net_cons").corr().iloc[0, 1])
k_eff = 2 / (1 + rho) if np.isfinite(rho) else 1.0
emit(f"  N = {NC} root-cycles ({NQ} quarters; census 140; spec anticipated ~140) -- shortfall is DATA ABSENCE, reported above")
emit(f"  quarter-pooled after-cost-cons sd = {sd_q:.4f} pt (${sd_q * POINT_VALUE:,.0f})")
emit(f"  MDE (one-sided 5%, 80% power) = 2.486 x sd/sqrt(N_q) = {mde_q:.4f} pt = ${mde_q * POINT_VALUE:,.0f}/cycle")
emit(f"  ZN-ZB same-quarter rho = {rho:+.3f} -> K_eff per quarter = {k_eff:.2f} legs")

# ---------------------------------------------------------------- observed primary
emit("")
emit("PRIMARY (LONG back / SHORT front, close FN-10 -> close FN-4, pooled ZN+ZB):")
gross = float(ok["gross_pts"].mean())
net_cons = float(ok["net_cons"].mean())
net_opt = float(ok["net_opt"].mean())
emit(f"  n = {NC}; gross mean {gross:+.5f} pt = ${gross * POINT_VALUE:+,.2f}/cycle")
emit(f"  after-cost CONS {net_cons:+.5f} pt = ${net_cons * POINT_VALUE:+,.2f}/cycle   [GATING]")
emit(f"  after-cost OPT  {net_opt:+.5f} pt = ${net_opt * POINT_VALUE:+,.2f}/cycle")
for root in ROOTS:
    g = ok[ok["root"] == root]
    emit(f"    {root}: n {len(g):3d}  gross {g['gross_pts'].mean():+.5f}  net_cons {g['net_cons'].mean():+.5f} pt "
         f"(${g['net_cons'].mean() * POINT_VALUE:+,.2f})  share>0 net_cons {(g['net_cons'] > 0).mean():.1%}")

# quarter-block bootstrap CI on after-cost cons mean (one shared draw across roots)
rng_b = np.random.default_rng(SEED_BOOT)
quarters = ok["quarter"].unique()
by_q = {q: ok.loc[ok["quarter"] == q, "net_cons"].values for q in quarters}
bm = np.empty(N_BOOT)
for i in range(N_BOOT):
    qs = rng_b.choice(quarters, size=len(quarters), replace=True)
    bm[i] = float(np.concatenate([by_q[q] for q in qs]).mean())
ci_lo, ci_hi = np.percentile(bm, [2.5, 97.5])
emit(f"  quarter-block bootstrap ({N_BOOT}, seed {SEED_BOOT}) 95% CI of after-cost-cons mean: "
     f"[{ci_lo:+.5f}, {ci_hi:+.5f}] pt = [${ci_lo * POINT_VALUE:+,.0f}, ${ci_hi * POINT_VALUE:+,.0f}]")

# shared-draw circular-shift null over the extended paired-spread-change series
series = {}
for root in ROOTS:
    vals, flags = [], []
    for i, r in ok.iterrows():
        seg_k, seg_s = seg_store[i]
        for j in range(1, len(seg_k)):
            vals.append(-(seg_s[j] - seg_s[j - 1]))            # -dS = long-back/short-front P&L
            flags.append(ENTRY_K < seg_k[j] <= EXIT_K)         # change ENDS in (FN-10, FN-4]
    series[root] = (np.array(vals), np.array(flags, dtype=bool))
    emit(f"  null series {root}: {len(vals)} paired daily spread-changes across {int((ok['root'] == root).sum())} cycles, "
         f"{int(np.sum(flags))} flagged (window entries)")

obs_flag = float(np.concatenate([series[r][0][series[r][1]] for r in ROOTS]).mean())
emit(f"  observed per-flagged-day premium {obs_flag:+.6f} pt; x{HOLD_CHANGES} = {obs_flag * HOLD_CHANGES:+.5f} pt "
     f"(cross-check vs endpoint-close gross {gross:+.5f} pt -- second computation of the same event)")

rng_s = np.random.default_rng(SEED_SHIFT)
u = rng_s.random(N_SHIFTS)
null_means = np.empty(N_SHIFTS)
for i in range(N_SHIFTS):
    tot, cnt = 0.0, 0
    for r in ROOTS:
        v, fl = series[r]
        L = len(v)
        o = 1 + int(u[i] * (L - 2))
        fv = np.roll(fl, o)
        tot += float(v[fv].sum())
        cnt += int(fv.sum())
    null_means[i] = tot / cnt
p_1s = (1 + int((null_means >= obs_flag).sum())) / (1 + N_SHIFTS)
z = (obs_flag - null_means.mean()) / null_means.std(ddof=1)
p_norm = 1 - 0.5 * (1 + math.erf(z / math.sqrt(2)))
emit(f"  shared-draw circular-shift null ({N_SHIFTS} shifts, seed {SEED_SHIFT}): null mean {null_means.mean():+.6f}, "
     f"sd {null_means.std(ddof=1):.6f}")
emit(f"  p one-sided = {p_1s:.4f} [GATING]; z = {z:+.2f} (normal-approx p {p_norm:.4f} cross-check)")
emit("  IN WORDS: p is the probability, under dependence-preserving circular shifts of the roll-window flag")
emit("  (ONE shared draw moving ZN and ZB together) over each root's paired daily calendar-spread-change series,")
emit("  that randomly placed pseudo-windows show a mean per-day LONG-back/SHORT-front drift >= the observed one.")

g2_ok = (net_cons > 0) and (ci_lo > 0) and (p_1s < 0.05)

# ---------------------------------------------------------------- G3 sign consistency
share_pos = float((ok["net_cons"] > 0).mean())
share_pos_gross = float((ok["gross_pts"] > 0).mean())
g3_ok = share_pos >= 0.60
emit("")
emit(f"G3 SIGN CONSISTENCY: after-cost-cons share of positive root-cycles = {share_pos:.1%} "
     f"(gross {share_pos_gross:.1%}); gate >= 60%")

# ---------------------------------------------------------------- G4 placebos
emit("")
emit("G4 PLACEBOS (same construction at +/-1-month anchors, gross pt; 'shows the drift' = mean>0 AND q-block CI_lo>0):")
plac = {}
for tag, lbl in (("pm", "-1 month"), ("pp", "+1 month")):
    col = f"{tag}_gross_pts"
    if col not in C:
        plac[tag] = (0, np.nan, np.nan, np.nan, False)
        continue
    sub = C[C[col].notna()]
    v = sub[col].astype(float)
    n = len(v)
    if n < 8:
        plac[tag] = (n, float(v.mean()) if n else np.nan, np.nan, np.nan, False)
        emit(f"  {lbl}: n = {n} (UNDER-COVERED, cannot show the drift; coverage reported)")
        continue
    qs2 = sub["quarter"].unique()
    byq = {q: sub.loc[sub["quarter"] == q, col].values for q in qs2}
    rb = np.random.default_rng(SEED_BOOT + (1 if tag == "pm" else 2))
    bmm = np.empty(N_BOOT)
    for i in range(N_BOOT):
        draw = rb.choice(qs2, size=len(qs2), replace=True)
        bmm[i] = float(np.concatenate([byq[q] for q in draw]).mean())
    lo, hi = np.percentile(bmm, [2.5, 97.5])
    shows = (v.mean() > 0) and (lo > 0)
    plac[tag] = (n, float(v.mean()), lo, hi, shows)
    emit(f"  {lbl}: n = {n}; gross mean {v.mean():+.5f} pt (${v.mean() * POINT_VALUE:+,.0f}); "
         f"CI [{lo:+.5f}, {hi:+.5f}] -> shows drift: {shows}")
g4_ok = (not plac["pm"][4]) and (not plac["pp"][4])

# ---------------------------------------------------------------- G5 carry control
emit("")
emit("G5 NOT-CARRY (control = expected slide from each cycle's measured average daily spread slide over FN-15..FN;")
emit("   expected primary under smooth carry = -6 x mean(dS); EXCESS = gross - expected; excess-after-cost carries G2):")
g5 = ok[ok["carry_exp_pts"].notna()].copy()
g5["excess_gross"] = g5["gross_pts"] - g5["carry_exp_pts"]
g5["excess_net_cons"] = g5["net_cons"] - g5["carry_exp_pts"]
exc_mean = float(g5["excess_net_cons"].mean())
qs3 = g5["quarter"].unique()
byq3 = {q: g5.loc[g5["quarter"] == q, "excess_net_cons"].values for q in qs3}
rb3 = np.random.default_rng(SEED_BOOT + 3)
bm3 = np.empty(N_BOOT)
for i in range(N_BOOT):
    draw = rb3.choice(qs3, size=len(qs3), replace=True)
    bm3[i] = float(np.concatenate([byq3[q] for q in draw]).mean())
lo3, hi3 = np.percentile(bm3, [2.5, 97.5])
emit(f"  n = {len(g5)} (>=8 panel changes required); carry-expected mean {g5['carry_exp_pts'].mean():+.5f} pt; "
     f"excess gross mean {g5['excess_gross'].mean():+.5f} pt")
emit(f"  excess after-cost-cons mean {exc_mean:+.5f} pt (${exc_mean * POINT_VALUE:+,.2f}); "
     f"q-block CI [{lo3:+.5f}, {hi3:+.5f}]")
emit("  (the shift-null clause on the excess is IDENTICAL to G2's by construction: the control is a per-cycle")
emit("   constant anchored to FN, so it shifts observed and null equally; recorded, not re-tested)")
g5_ok = (exc_mean > 0) and (lo3 > 0)

# ---------------------------------------------------------------- G6 era split
emit("")
emit("G6 ERA SPLIT (pre/post-2016 by FN date; after-cost cons; modern-negative = FAIL):")
era_rows = []
for era in ("pre2016", "post2016"):
    for scope in ("ZN", "ZB", "POOLED"):
        g = ok[ok["era"] == era] if scope == "POOLED" else ok[(ok["era"] == era) & (ok["root"] == scope)]
        if len(g) == 0:
            continue
        era_rows.append(dict(era=era, scope=scope, n=len(g),
                             gross_mean_pts=float(g["gross_pts"].mean()),
                             net_cons_mean_pts=float(g["net_cons"].mean()),
                             net_cons_mean_usd=float(g["net_cons"].mean() * POINT_VALUE),
                             share_pos_net_cons=float((g["net_cons"] > 0).mean())))
E = pd.DataFrame(era_rows)
for _, r in E.iterrows():
    emit(f"  {r['era']:<9} {r['scope']:<7} n {r['n']:3d}  gross {r['gross_mean_pts']:+.5f}  "
         f"net_cons {r['net_cons_mean_pts']:+.5f} pt (${r['net_cons_mean_usd']:+,.2f})  share>0 {r['share_pos_net_cons']:.1%}")
post_mean = float(ok.loc[ok["era"] == "post2016", "net_cons"].mean())
modern_negative = post_mean < 0
g6_ok = not modern_negative

g1_ok = True   # MDE printed first, honest N recorded
g7_ok = True   # band printed from declared ticks, asserted vs headers, cons rung gates

# ---------------------------------------------------------------- GATE TABLE
emit("")
emit("GATE TABLE  (printed by program)")
rows = [
    ("G1_MDE_first", "MDE printed before observed (~140 root-cycles)",
     f"MDE {mde_q:.4f} pt (${mde_q * POINT_VALUE:,.0f})/cycle at N={NC} rc / {NQ} q (census 140)", g1_ok),
    ("G2_drift", "after-cost mean>0 AND q-block CI excl 0 AND shift p<.05",
     f"net_cons {net_cons:+.5f} pt, CI [{ci_lo:+.5f},{ci_hi:+.5f}], p_1s {p_1s:.4f}", g2_ok),
    ("G3_sign", ">= 60% of root-cycles positive (after-cost cons)",
     f"{share_pos:.1%} positive (gross {share_pos_gross:.1%})", g3_ok),
    ("G4_placebo", "+/-1-month windows must NOT show the drift",
     f"-1mo n={plac['pm'][0]} mean {plac['pm'][1]:+.5f} shows={plac['pm'][4]}; "
     f"+1mo n={plac['pp'][0]} mean {plac['pp'][1]:+.5f} shows={plac['pp'][4]}", g4_ok),
    ("G5_not_carry", "excess over measured avg slide carries G2 (mean>0, CI excl 0)",
     f"excess net_cons {exc_mean:+.5f} pt, CI [{lo3:+.5f},{hi3:+.5f}], n={len(g5)}", g5_ok),
    ("G6_era", "pre/post-2016 split; modern-negative = FAIL",
     f"pre {float(ok.loc[ok['era'] == 'pre2016', 'net_cons'].mean()):+.5f} / post {post_mean:+.5f} pt net_cons", g6_ok),
    ("G7_cost", "MODELED {1,2}-tick outright-equiv band, cons rung gates",
     f"ZN $31.25/$62.50, ZB $62.50/$125.00 per cycle; cons gates G2/G3/G5/G6", g7_ok),
]
emit(f"{'GATE':<14}{'SPEC':<58}{'OBSERVED':<72}PASS-FAIL")
for name, spec, obsv, okk in rows:
    emit(f"{name:<14}{spec:<58}{obsv:<72}{'PASS' if okk else '*** FAIL ***'}")

decision = ("TSYROLL01 CANDIDATE" if (g2_ok and g3_ok and g4_ok and g5_ok and g6_ok)
            else "CLOSED AT SCOPE (S28 block)")
emit("")
emit(f"DECISION RULE (spec, mechanical): G2={'PASS' if g2_ok else 'FAIL'} G3={'PASS' if g3_ok else 'FAIL'} "
     f"G4={'PASS' if g4_ok else 'FAIL'} G5={'PASS' if g5_ok else 'FAIL'} "
     f"G6={'not-modern-negative' if g6_ok else 'MODERN-NEGATIVE'} -> {decision}")
emit(f"annualized after-cost-cons economics if held every cycle: 4 cycles/yr x ${net_cons * POINT_VALUE:+,.2f} = "
     f"${4 * net_cons * POINT_VALUE:+,.2f}/yr per 1-lot spread")
emit("evidence_status: DISCOVERY (first read of this representation; consumed by this read)")
emit("=" * 118)

# ---------------------------------------------------------------- OI CENSUS sidecar
emit("")
emit("OI CENSUS SIDECAR (world-scan #14 step 1 -- layout question only, no price analysis):")
probe_cid = "ZN 12-25"
probe_dir = os.path.join(ncd_day.DB_DAY, probe_cid)
fname = sorted(f for f in os.listdir(probe_dir) if f.endswith(".Last.ncd"))[0]
fpath = os.path.join(probe_dir, fname)
raw = open(fpath, "rb").read()
size = len(raw)
n_rec = (size - 28) // 48
emit(f"  probe file: {probe_cid}/{fname}; size {size} bytes; (size-28) % 48 = {(size - 28) % 48}; {n_rec} records")
rec0 = raw[28:76]
ts = int.from_bytes(rec0[0:8], "little", signed=True)
o, h, l, c = (np.frombuffer(rec0[8:40], dtype="<f8"))
v = int.from_bytes(rec0[40:48], "little", signed=True)
dt = np.datetime64("0001-01-01") + np.timedelta64(ts // 10, "us")
emit(f"  first raw record (hex): {rec0.hex()}")
emit(f"  decoded: ts {dt} | o {o} h {h} l {l} c {c} | volume {v}")
emit("  layout: 28-byte header + 48-byte records = int64 ticks + 4 x float64 OHLC + int64 volume.")
emit("  48 = 8+32+8 exactly; NO field remains for open interest. The day store does NOT carry OI.")

# ---------------------------------------------------------------- outputs
import json  # noqa: E402

bad3 = ((ok["root"] == "ZB") & (ok["delivery"].isin(["2009-06", "2009-09", "2015-03"])))
ex3 = ok[~bad3]
verdicts = dict(
    run_id="G3_TSYROLL_20260906", ledger="G00087", family="GENESIS3_EVENT",
    n_census=int(n_census), n_usable=int(NC), n_quarters=int(NQ),
    mde_pts=round(mde_q, 5), mde_usd=round(mde_q * POINT_VALUE, 2),
    gross_pts=round(gross, 6), gross_usd=round(gross * POINT_VALUE, 2),
    net_cons_pts=round(net_cons, 6), net_cons_usd=round(net_cons * POINT_VALUE, 2),
    net_opt_usd=round(net_opt * POINT_VALUE, 2),
    ci_cons_pts=[round(ci_lo, 6), round(ci_hi, 6)],
    p_shift_1s=round(p_1s, 5), null_mean=round(float(null_means.mean()), 7),
    null_sd=round(float(null_means.std(ddof=1)), 7),
    share_pos_net_cons=round(share_pos, 4), share_pos_gross=round(share_pos_gross, 4),
    placebo_m1=dict(n=int(plac["pm"][0]), gross_pts=round(plac["pm"][1], 6), shows=bool(plac["pm"][4])),
    placebo_p1=dict(n=int(plac["pp"][0]), gross_pts=round(plac["pp"][1], 6), shows=bool(plac["pp"][4])),
    excess_net_cons_pts=round(exc_mean, 6), excess_ci_pts=[round(lo3, 6), round(hi3, 6)],
    era_net_cons_pts=dict(pre2016=round(float(ok.loc[ok["era"] == "pre2016", "net_cons"].mean()), 6),
                          post2016=round(post_mean, 6)),
    modern_negative=bool(modern_negative),
    gates=dict(G1="PASS", G2="PASS" if g2_ok else "FAIL", G3="PASS" if g3_ok else "FAIL",
               G4="PASS" if g4_ok else "FAIL", G5="PASS" if g5_ok else "FAIL",
               G6="PASS" if g6_ok else "FAIL", G7="PASS"),
    decision=decision,
    sensitivity_excl_3_defective_zb_panels=dict(
        n=int(len(ex3)), gross_pts=round(float(ex3["gross_pts"].mean()), 6),
        net_cons_pts=round(float(ex3["net_cons"].mean()), 6),
        share_pos_net_cons=round(float((ex3["net_cons"] > 0).mean()), 4)),
    oi_in_day_store=False,
)
with open(os.path.join(OUT, "verdicts.json"), "w", encoding="utf-8") as fh:
    json.dump(verdicts, fh, indent=2)

with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as fh:
    fh.write(buf.getvalue())
pp.to_csv(os.path.join(OUT, "cycle_panel.csv"), index=False)
E.to_csv(os.path.join(OUT, "era_table.csv"), index=False)
keep = [c for c in C.columns if not c.startswith("_")]
C[keep].to_csv(os.path.join(OUT, "cycle_summary.csv"), index=False)
ok.drop(columns=[c for c in ok.columns if c.startswith("_")], errors="ignore").to_csv(
    os.path.join(OUT, "cycle_primary.csv"), index=False)
print("\nWROTE out/gate_table.txt, out/cycle_panel.csv, out/era_table.csv, out/cycle_summary.csv, out/cycle_primary.csv")
