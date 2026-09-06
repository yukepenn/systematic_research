#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G3_ZBMACRO_FALSIFIER_20260906 -- ledger G00072, family GENESIS3_EVENT.
Graduation falsifier for the G3_EVENT_ZB_20260906 (G00067) E1 LEAD.

FROZEN OBJECT (zero free parameters, from spec.yaml):
  On sessions flagged NFP_DAY or CPI_DAY in GENESIS_H2_CALENDAR_20260828 (the exact E1
  calendar), IF close(08:45) - close(08:30) < 0 (points), SHORT 1 ZB at the 08:45 bar close,
  EXIT at the 15:00 bar close. No entry on UP or zero first response. No other conditioning.

CONVENTION (stated once, used everywhere): the per-trade statistic is the AFTER-COST FORWARD
MOVE  x = (c1500 - c0845) + cost_pts.  For the SHORT, x < 0 means the trade is PROFITABLE
after cost (profit_$ = -x * 1000). Gate clauses "after-cost mean < 0" use this convention,
exactly as the spec words them ("< 0 for the short (i.e. profit > 0)").

COST (BASIS-tagged, from spec.yaml):
  PRIMARY = MODELED ALL_IN: $4.36 RT commission + 1 tick/side spread ($62.50 RT) = $66.86 RT
            = 0.06686 pt.
  STRESS  = MODELED ALL_IN: $4.36 RT commission + 2 ticks/side spread ($125.00 RT) = $129.36 RT
            = 0.12936 pt.
  Spread figures alone are never called all-in; the ALL_IN here includes commission.

EVIDENCE STATUS: DISCOVERY_CONSUMED (same substrate as the G00067 screen). Stated in every
output table.

FIXED-BEFORE-RESULTS OPERATIONALIZATIONS (ambiguity resolutions; none touched after results):
  * Event set: the EXACT E1 constructor (run_event_zb.py lines reproduced verbatim): eligible
    universe u1 = sessions with finite as-of closes at 08:30/08:45/10:30/15:00 (15-min
    staleness); releases = (NFP u CPI) in-window; r1 = c0845-c0830; r1==0 dropped; DOWN events
    = r1 < 0. Expected n = 40.
  * G0 identity: runs/G3_EVENT_ZB_20260906/out/event_tables.csv carries no per-event dates, so
    identity is asserted by exact match (n exact, mean within 1e-9) of NINE E1 cell statistics
    that jointly constrain the set: 0845_1500 sign-/sign+, terc{1,2,3}_aligned,
    sign-_terc{1,2,3}, and 0845_1030 sign-. Any mismatch = DEFECT, stop.
  * G1 MDE: session-block bootstrap SE of the after-cost mean (moving blocks L=5, B=2000,
    seed 20260907) -> MDE_sig = 1.96*SE (5% two-sided), MDE_80 = 2.80*SE (80% power).
    Printed BEFORE the observed mean in the output stream.
  * G2 CI: same moving-block bootstrap (L=5, B=2000) percentile CI95 on the chronological
    after-cost trade series; PASS iff mean < 0 AND ci_hi < 0. PRIMARY cost arm.
  * G3 null 1 (headline): circular shift of the release-day FLAG along the chronologically
    ordered eligible-session sequence (fam1). 2000 shifts; ONE shared U(0,1) draw, seed
    20260906; offset_k = 1 + floor(u_k*(L-1)) (never 0). At each shift the rule is re-run on
    the receiving sessions (their own r1 sign decides the short), statistic = after-cost TOTAL
    (PRIMARY). percentile = 100*(1+#{null_total <= obs_total})/(N+1); PASS iff <= 5.0.
  * G3 null 2 (second computation of the same event): permutation of the observed first-
    response SIGNS across the 78 nonzero-r1 release events (preserves the 40/38 split), 2000
    permutations, seed 20260908; same after-cost total statistic and percentile definition.
    Agreement clause: |pct1 - pct2| <= 5.0 percentile points, else INVALID-RUN.
  * G4: chronological event order; halves = trades[0:20] vs trades[20:40]. FAIL iff BOTH
    halves have after-cost mean >= 0. One-half-wrong-sign = REGIME note (recorded), PASS if
    the overall G2 CI holds.
  * G5 drop-k: "worst trades" = the k trades whose REMOVAL hurts the short most = the k most
    NEGATIVE forward moves (its largest winners) -- exactly the diagnostic's own -$158
    construction. Curve k=0..5; PASS iff after-cost mean (PRIMARY) < 0 at k=2.
  * G6 neighborhood (report-only, headline stays the frozen object): entry e in {08:40,08:45,
    08:50} x exit x in {14:00,15:00} x conditioning in {all-down, below-median-down,
    terc1-aligned}. r_e = c(e)-c(08:30). Per entry, the conditioning population = release
    events in fam1 with finite c(e) and r_e != 0; terciles = |r_e| quantiles (1/3, 2/3) over
    that population (pooled signs, exactly parallel to the E1 tercile construction);
    below-median-down = r_e < 0 AND |r_e| < median(|r_e|) over the same population.
    all-down / below-median-down trade SHORT; terc1-aligned trades in the direction of
    sign(r_e). Cell metric = mean after-cost PROFIT (PRIMARY), profit_pts = dir*(c(x)-c(e))
    - cost_pts (positive = good; the sign flip vs the move convention is stated in the CSV).
    Plateau statement criterion (frozen): frozen cell net>0 AND >=4 of the 6 all-down cells
    net>0 AND at least one adjacent-entry all-down cell at exit 15:00 net>0.
  * G7: NFP-only / CPI-only after-cost means (PRIMARY). Both negative strengthens; one-side
    flat = CLASSIFICATION (release-local), not veto. Report-only.
  * G8: STRESS-arm after-cost mean < 0. Blocking.
  * G9 (report-only): weekly grid = all calendar weeks spanning the substrate; ZB net PnL
    (PRIMARY, $) summed per week, zeros elsewhere. LEAD metric = weekly-vol annualized Sharpe.
    maxDD / CDaR95 via research_sdk.eval_battery.max_drawdown/cdar printed as PATH
    DESCRIPTIVES ONLY; NO fixed-DD- or CDaR-normalized income figure is quoted anywhere in
    this run, so no thinning placebo is owed (the eval_battery guard is honored by not
    reading those bases at all). UP-response mirror: long at 08:45 close on r1>0, exit 15:00.
    rho-to-P1: P1 daily PnL taken from runs/WE_W56_BREADTH/out/p1_daily.csv (the preregistered
    alternative to re-running G3_ESMR_PORTFOLIO's substrate rebuild; SOURCE STATED); common
    calendar = ZB substrate sessions inside the P1 series' span; both series zero-filled on
    no-trade days; Pearson rho on daily and calendar-week sums.

DECISION RULE (mechanical): G2+G3+G4+G5+G8 all PASS -> "ZBMACRO01 ENGINE CANDIDATE"
(ledger PASS). Any of them FAIL -> "E1 LEAD CLOSED AT SCOPE" (ledger FAIL).
G0 mismatch -> DEFECT, stop. G3 agreement clause violated -> INVALID-RUN.

Data seals: assert max session <= 2026-07-31. POINTS basis only (DELEV01). Bars END-stamped;
ET sessions 18:00->17:00.
"""

import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN_DIR = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RUN_DIR, os.pardir, os.pardir))
sys.path.insert(0, REPO)

from research_sdk.eval_battery import max_drawdown, cdar  # noqa: E402

ZB_PARQUET = os.path.join(REPO, "runs", "SM1M_ZB_SUBSTRATE", "out", "zb_1m_2023_2026.parquet")
NFP_CSV = os.path.join(REPO, "runs", "GENESIS_H2_CALENDAR_20260828", "out",
                       "calendar_artifacts", "daytype_sessions_NFP_DAY.csv")
CPI_CSV = os.path.join(REPO, "runs", "GENESIS_H2_CALENDAR_20260828", "out",
                       "calendar_artifacts", "daytype_sessions_CPI_DAY.csv")
E1_TABLES = os.path.join(REPO, "runs", "G3_EVENT_ZB_20260906", "out", "event_tables.csv")
P1_DAILY_CSV = os.path.join(REPO, "runs", "WE_W56_BREADTH", "out", "p1_daily.csv")
OUT = os.path.join(RUN_DIR, "out")
os.makedirs(OUT, exist_ok=True)

SEAL_MAX_SESSION = pd.Timestamp("2026-07-31").date()
POINT_VALUE = 1000.0
TICK = 1.0 / 32.0
COMM_RT = 4.36
COST_PRIMARY_USD = COMM_RT + 2 * 31.25          # $66.86  (1 tick/side spread)
COST_STRESS_USD = COMM_RT + 4 * 31.25           # $129.36 (2 ticks/side spread)
COST_PRIMARY_PTS = COST_PRIMARY_USD / POINT_VALUE
COST_STRESS_PTS = COST_STRESS_USD / POINT_VALUE
N_SHIFTS = 2000
SEED = 20260906
B_BOOT = 2000
BLOCK_L = 5
ASOF_LIMIT = 15
EVSTAT = "DISCOVERY_CONSUMED"

rng_shift = np.random.default_rng(SEED)
U_SHARED = rng_shift.random(N_SHIFTS)
rng_boot = np.random.default_rng(SEED + 1)
rng_perm = np.random.default_rng(SEED + 2)

LINES = []
def say(s=""):
    print(s)
    LINES.append(s)

def block_boot_means(y, B=B_BOOT, L=BLOCK_L, rng=None):
    y = np.asarray(y, dtype=float)
    y = y[np.isfinite(y)]
    n = len(y)
    L = min(L, n)
    nblocks = int(np.ceil(n / L))
    starts_max = n - L + 1
    means = np.empty(B)
    for b in range(B):
        st = rng.integers(0, starts_max, size=nblocks)
        idx = (st[:, None] + np.arange(L)[None, :]).ravel()[:n]
        means[b] = y[idx].mean()
    return means

def pct_leq(obs, null):
    null = np.asarray(null, dtype=float)
    null = null[np.isfinite(null)]
    return 100.0 * (1 + np.sum(null <= obs)) / (len(null) + 1)

# ==================================================================== load + seal (E1-identical)
df = pd.read_parquet(ZB_PARQUET)
t = pd.to_datetime(df["time"])
hh = t.dt.hour.to_numpy(); mm = t.dt.minute.to_numpy()
sess_ts = t.dt.normalize() + pd.to_timedelta((hh >= 18).astype(int), unit="D")
sess_date = sess_ts.dt.date.to_numpy()

sessions = np.array(sorted(set(sess_date)))
NS = len(sessions)
sess_idx = {d: i for i, d in enumerate(sessions)}
code = np.fromiter((sess_idx[d] for d in sess_date), dtype=np.int64, count=len(df))

max_sess = sessions.max()
seal_ok = max_sess <= SEAL_MAX_SESSION
assert seal_ok, f"SEAL VIOLATION: max session {max_sess} > {SEAL_MAX_SESSION}"

frac = np.abs(df["close"].to_numpy() * 32 - np.round(df["close"].to_numpy() * 32))
grid_share = float(np.mean(frac < 1e-6))

msess = ((hh * 60 + mm) - 1080) % 1440
assert msess.min() >= 1 and msess.max() <= 1380

closeA = np.full((NS, 1381), np.nan)
closeA[code, msess] = df["close"].to_numpy()
gridf = pd.DataFrame(closeA).ffill(axis=1, limit=ASOF_LIMIT).to_numpy()

M0830, M0840, M0845, M0850, M1030, M1400, M1500 = 870, 880, 885, 890, 990, 1200, 1260
c0830 = gridf[:, M0830]; c0845 = gridf[:, M0845]; c1030 = gridf[:, M1030]; c1500 = gridf[:, M1500]

# ==================================================================== E1 calendar (identical)
nfp = set(pd.to_datetime(pd.read_csv(NFP_CSV)["session_date"]).dt.date)
cpi = set(pd.to_datetime(pd.read_csv(CPI_CSV)["session_date"]).dt.date)
rel_all = nfp | cpi
rel_in_window = {d for d in rel_all if sessions.min() <= d <= sessions.max()}

# ==================================================================== E1 event set (identical)
u1 = np.flatnonzero(~np.isnan(c0830) & ~np.isnan(c0845) & ~np.isnan(c1030) & ~np.isnan(c1500))
fam1 = u1
fam1_dates = sessions[u1]
is_rel = np.array([d in rel_in_window for d in fam1_dates])
r1 = (c0845 - c0830)[fam1]
f1030 = (c1030 - c0845)[fam1]
f1500 = (c1500 - c0845)[fam1]

ev1_pos_all = np.flatnonzero(is_rel)
n_rel_zero = int(np.sum(r1[ev1_pos_all] == 0.0))
ev1_pos = ev1_pos_all[r1[ev1_pos_all] != 0.0]
s1sign_ev = np.sign(r1[ev1_pos])
absr = np.abs(r1[ev1_pos])
q33, q66 = np.quantile(absr, [1 / 3, 2 / 3])
terc_ev = np.where(absr <= q33, 1, np.where(absr <= q66, 2, 3))

# ==================================================================== G0 identity vs artifact
e1tab = pd.read_csv(E1_TABLES).set_index("cell")

def cell_stat(sel_mask, align, Y):
    y = align * Y[ev1_pos[sel_mask]]
    return int(sel_mask.sum()), (float(np.mean(y)) if sel_mask.sum() else np.nan)

repro = {}
repro["E1_0845_1500_sign-"] = cell_stat(s1sign_ev == -1.0, 1.0, f1500)
repro["E1_0845_1500_sign+"] = cell_stat(s1sign_ev == 1.0, 1.0, f1500)
repro["E1_0845_1030_sign-"] = cell_stat(s1sign_ev == -1.0, 1.0, f1030)
for tc in (1, 2, 3):
    m = terc_ev == tc
    y = s1sign_ev[m] * f1500[ev1_pos[m]]
    repro[f"E1_0845_1500_terc{tc}_aligned"] = (int(m.sum()), float(np.mean(y)))
    m2 = (s1sign_ev == -1.0) & (terc_ev == tc)
    repro[f"E1_0845_1500_sign-_terc{tc}"] = cell_stat(m2, 1.0, f1500)

id_checks = []
for cid, (n_r, mu_r) in repro.items():
    row = e1tab.loc[cid]
    ok = (int(row["n_events"]) == n_r) and (abs(float(row["obs_mean_pts"]) - mu_r) < 1e-9)
    id_checks.append((cid, int(row["n_events"]), n_r, float(row["obs_mean_pts"]), mu_r, ok))
g0_identity = all(c[-1] for c in id_checks)
n_down = repro["E1_0845_1500_sign-"][0]
g0_pass = seal_ok and g0_identity and (n_down == 40) and grid_share > 0.999

say("=" * 100)
say("G3_ZBMACRO_FALSIFIER_20260906  (ledger G00072, family GENESIS3_EVENT)")
say("Graduation falsifier for the G00067 E1 LEAD -- frozen object: NFP/CPI down first response")
say("=> SHORT ZB 08:45 close -> 15:00 close.  EVIDENCE STATUS: %s (all tables)." % EVSTAT)
say(f"substrate: {os.path.relpath(ZB_PARQUET, REPO)}  sessions={NS} "
    f"({sessions.min()} .. {sessions.max()})  POINTS basis, $1000/pt, tick $31.25")
say(f"calendar: NFP_DAY+CPI_DAY (GENESIS_H2_CALENDAR_20260828); in-window releases={len(rel_in_window)}; "
    f"eligible universe={len(fam1)}; nonzero-r1 release events={len(ev1_pos)} (r1==0 dropped: {n_rel_zero})")
say(f"cost arms (BASIS=MODELED ALL_IN = comm $4.36 + spread): PRIMARY 1tk/side = ${COST_PRIMARY_USD:.2f} RT "
    f"({COST_PRIMARY_PTS:.5f} pt); STRESS 2tk/side = ${COST_STRESS_USD:.2f} RT ({COST_STRESS_PTS:.5f} pt)")
say("convention: x = (c1500-c0845) + cost_pts; x<0 = profitable short; profit_$ = -x*1000")
say("")
say("[G0] seal + event-set identity vs runs/G3_EVENT_ZB_20260906/out/event_tables.csv")
say(f"     seal: max session = {max_sess} <= {SEAL_MAX_SESSION} : {'OK' if seal_ok else 'VIOLATION'}; "
    f"1/32-grid share = {grid_share:.6f}")
say("     artifact carries no per-event dates; identity asserted on 9 jointly-constraining cells:")
say(f"     {'cell':<28}{'n_art':>6}{'n_rep':>6}{'obs_art':>12}{'obs_rep':>12}{'match':>7}")
for cid, na, nr, oa, orep, ok in id_checks:
    say(f"     {cid:<28}{na:>6}{nr:>6}{oa:>12.6f}{orep:>12.6f}{'OK' if ok else 'MISMATCH':>7}")
say(f"     identity: {'EXACT (9/9)' if g0_identity else 'MISMATCH -> DEFECT'}; n_down={n_down} (expected 40)")

if not g0_pass:
    say("")
    say("G0 FAILED -> DEFECT. STOP (no gates evaluated).")
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(LINES) + "\n")
    sys.exit(2)

# ==================================================================== the 40 frozen trades
pos40 = ev1_pos[s1sign_ev == -1.0]                       # chronological (fam1 ascending)
dates40 = fam1_dates[pos40]
r1_40 = r1[pos40]
f40 = f1500[pos40]                                       # gross forward move, pts
terc40 = terc_ev[s1sign_ev == -1.0]
x_primary = f40 + COST_PRIMARY_PTS                       # after-cost move, PRIMARY
x_stress = f40 + COST_STRESS_PTS
rel_label = np.array([("NFP+CPI" if (d in nfp and d in cpi) else ("NFP" if d in nfp else "CPI"))
                      for d in dates40])

trades = pd.DataFrame(dict(
    session_date=dates40, release=rel_label, r1_pts=r1_40, tercile_absr1=terc40,
    fwd_0845_1500_pts=f40,
    move_aftercost_primary_pts=x_primary, move_aftercost_stress_pts=x_stress,
    profit_gross_usd=-f40 * POINT_VALUE,
    profit_net_primary_usd=-x_primary * POINT_VALUE,
    profit_net_stress_usd=-x_stress * POINT_VALUE,
    evidence_status=EVSTAT))
trades.to_csv(os.path.join(OUT, "trades.csv"), index=False)

# ==================================================================== G1 MDE (printed BEFORE observed)
boot_means = block_boot_means(x_primary, rng=rng_boot)
se_boot = float(np.std(boot_means, ddof=1))
mde_sig = 1.96 * se_boot
mde_80 = 2.80 * se_boot
sd_trade = float(np.std(x_primary, ddof=1))
say("")
say("[G1] MDE FIRST (session-block bootstrap SE; L=%d, B=%d) -- printed before any observed mean" %
    (BLOCK_L, B_BOOT))
say(f"     n=40 trades; trade-level SD = {sd_trade:.4f} pt; block-bootstrap SE of mean = {se_boot:.4f} pt")
say(f"     MDE (5% two-sided significance) = {mde_sig:.4f} pt = ${mde_sig*POINT_VALUE:.0f}/ct")
say(f"     MDE (80% power at 5% two-sided) = {mde_80:.4f} pt = ${mde_80*POINT_VALUE:.0f}/ct")
say("     honest statement: the falsifier operates near its own power edge (E1 REPORT said so).")

# ==================================================================== G2 after-cost edge (PRIMARY)
mean_primary = float(np.mean(x_primary))
ci_lo, ci_hi = np.percentile(boot_means, [2.5, 97.5])
g2_pass = (mean_primary < 0) and (ci_hi < 0)
say("")
say("[G2] PRIMARY after-cost edge (observed, now printed after the MDE)")
say(f"     mean after-cost move = {mean_primary:+.4f} pt = {-mean_primary*POINT_VALUE:+.1f} $/ct profit; "
    f"gross mean = {float(np.mean(f40)):+.4f} pt")
say(f"     block-bootstrap CI95 of the after-cost mean: [{ci_lo:+.4f}, {ci_hi:+.4f}] pt "
    f"(profit CI: [{-ci_hi*POINT_VALUE:+.1f}, {-ci_lo*POINT_VALUE:+.1f}] $/ct)")
say(f"     vs MDE: |mean| = {abs(mean_primary):.4f} pt vs MDE_80 {mde_80:.4f} pt "
    f"({'above' if abs(mean_primary) >= mde_80 else 'BELOW'} the 80%-power bar; informational)")

# ==================================================================== G3 null + second computation
L1 = len(fam1)
offs = (1 + np.floor(U_SHARED * (L1 - 1))).astype(np.int64)
cost = COST_PRIMARY_PTS
obs_total = float(np.sum(x_primary))

# machinery self-check at offset 0
prel0 = ev1_pos_all
rr0 = r1[prel0]
sel0 = rr0 < 0
t_check = float(np.sum(f1500[prel0[sel0]] + cost))
assert abs(t_check - obs_total) < 1e-9, "shift-null machinery does not reproduce the observed trades at k=0"

null1 = np.empty(N_SHIFTS)
for k in range(N_SHIFTS):
    prel = (ev1_pos_all + offs[k]) % L1
    rr = r1[prel]
    sel = rr < 0.0
    null1[k] = float(np.sum(f1500[prel[sel]] + cost)) if sel.any() else 0.0
pct1 = pct_leq(obs_total, null1)

sgn78 = s1sign_ev.copy()
f78 = f1500[ev1_pos]
null2 = np.empty(N_SHIFTS)
for k in range(N_SHIFTS):
    sp = rng_perm.permutation(sgn78)
    sel = sp < 0
    null2[k] = float(np.sum(f78[sel])) + int(sel.sum()) * cost
pct2 = pct_leq(obs_total, null2)

agree = abs(pct1 - pct2) <= 5.0
g3_pass = (pct1 <= 5.0) and agree
say("")
say("[G3] circular-shift null + sign-permutation second computation (after-cost TOTAL, PRIMARY)")
say(f"     observed after-cost total = {obs_total:+.4f} pt = {-obs_total*POINT_VALUE:+.0f} $/ct")
say(f"     null 1 (shift release flag along {L1} eligible sessions, {N_SHIFTS} shifts, shared draw "
    f"seed {SEED}): percentile of obs = {pct1:.2f} (null mean {np.mean(null1):+.3f}, "
    f"5th pct {np.percentile(null1,5):+.3f} pt)")
say(f"     null 2 (permute the 78 first-response signs, {N_SHIFTS} perms, seed {SEED+2}): "
    f"percentile of obs = {pct2:.2f} (null mean {np.mean(null2):+.3f}, "
    f"5th pct {np.percentile(null2,5):+.3f} pt)")
say(f"     agreement clause: |{pct1:.2f} - {pct2:.2f}| = {abs(pct1-pct2):.2f} <= 5.0 : "
    f"{'OK' if agree else 'VIOLATED -> INVALID-RUN'}")

# ==================================================================== G4 chronology halves
h1 = x_primary[:20]; h2 = x_primary[20:]
m1, m2 = float(np.mean(h1)), float(np.mean(h2))
both_neg = (m1 < 0) and (m2 < 0)
both_wrong = (m1 >= 0) and (m2 >= 0)
g4_regime_note = (not both_neg) and (not both_wrong)
g4_pass = (not both_wrong) and (both_neg or g2_pass)
say("")
say("[G4] chronology halves (first 20 vs last 20 events, after-cost PRIMARY)")
say(f"     first-20  ({dates40[0]} .. {dates40[19]}):  mean = {m1:+.4f} pt = {-m1*POINT_VALUE:+.1f} $/ct")
say(f"     last-20   ({dates40[20]} .. {dates40[39]}): mean = {m2:+.4f} pt = {-m2*POINT_VALUE:+.1f} $/ct")
say(f"     both halves negative: {'YES' if both_neg else 'NO'}"
    + ("" if not g4_regime_note else "  -> REGIME note: one half flat/wrong-sign, overall CI holds"))

# ==================================================================== G5 drop-k tail honesty
order = np.argsort(x_primary)          # ascending: most negative (largest short winners) first
rows = []
for k in range(6):
    kept = x_primary[order[k:]]
    rows.append(dict(k_dropped=k, n_kept=len(kept),
                     mean_aftercost_primary_pts=float(np.mean(kept)),
                     mean_profit_net_primary_usd=float(-np.mean(kept) * POINT_VALUE),
                     dropped_trade_move_pts=(float(x_primary[order[k - 1]]) if k else np.nan),
                     evidence_status=EVSTAT))
dropk = pd.DataFrame(rows)
dropk.to_csv(os.path.join(OUT, "dropk.csv"), index=False)
mean_k2 = float(dropk.loc[dropk.k_dropped == 2, "mean_aftercost_primary_pts"].iloc[0])
g5_pass = mean_k2 < 0
say("")
say("[G5] drop-k tail honesty (drop the k most-negative moves = the short's largest winners)")
for _, r in dropk.iterrows():
    say(f"     k={int(r.k_dropped)}: n={int(r.n_kept)}  after-cost mean = "
        f"{r.mean_aftercost_primary_pts:+.4f} pt = {-r.mean_aftercost_primary_pts*POINT_VALUE:+.1f} $/ct")
say(f"     clause: mean at k=2 = {mean_k2:+.4f} pt must be < 0")

# ==================================================================== G6 neighborhood (report-only)
ENTRIES = [(M0840, "08:40"), (M0845, "08:45"), (M0850, "08:50")]
EXITS = [(M1400, "14:00"), (M1500, "15:00")]
CONDS = ["all_down", "below_median_down", "terc1_aligned"]
nb_rows = []
for me, ename in ENTRIES:
    ce = gridf[:, me][fam1]
    r_e = ce - c0830[fam1]
    elig = np.flatnonzero(is_rel & np.isfinite(ce) & (r_e != 0.0))
    ab = np.abs(r_e[elig])
    med = float(np.median(ab))
    qa = float(np.quantile(ab, 1 / 3))
    for mx, xname in EXITS:
        cx = gridf[:, mx][fam1]
        f_ex = cx - ce
        for cond in CONDS:
            if cond == "all_down":
                m = elig[(r_e[elig] < 0)]
                dirs = -np.ones(len(m))
            elif cond == "below_median_down":
                m = elig[(r_e[elig] < 0) & (np.abs(r_e[elig]) < med)]
                dirs = -np.ones(len(m))
            else:
                m = elig[np.abs(r_e[elig]) <= qa]
                dirs = np.sign(r_e[m])
            ok = np.isfinite(f_ex[m])
            m = m[ok]; d = dirs[ok]
            prof = d * f_ex[m] - COST_PRIMARY_PTS
            n = len(m)
            nb_rows.append(dict(
                entry=ename, exit=xname, conditioning=cond, n=n,
                mean_gross_profit_pts=(float(np.mean(d * f_ex[m])) if n else np.nan),
                mean_net_profit_primary_pts=(float(np.mean(prof)) if n else np.nan),
                mean_net_profit_primary_usd=(float(np.mean(prof)) * POINT_VALUE if n else np.nan),
                naive_se_pts=(float(np.std(prof, ddof=1) / np.sqrt(n)) if n > 1 else np.nan),
                is_frozen_object=(ename == "08:45" and xname == "15:00" and cond == "all_down"),
                evidence_status=EVSTAT,
                note="profit convention: positive=good; dir=short for *down cells, sign(r_e) for aligned"))
nb = pd.DataFrame(nb_rows)
nb.to_csv(os.path.join(OUT, "neighborhood.csv"), index=False)

froz = nb[nb.is_frozen_object].iloc[0]
alldown = nb[nb.conditioning == "all_down"]
n_pos_alldown = int((alldown.mean_net_profit_primary_usd > 0).sum())
n_pos_all = int((nb.mean_net_profit_primary_usd > 0).sum())
adj = nb[(nb.conditioning == "all_down") & (nb.exit == "15:00") & (nb.entry != "08:45")]
adj_pos = int((adj.mean_net_profit_primary_usd > 0).sum())
plateau = (froz.mean_net_profit_primary_usd > 0) and (n_pos_alldown >= 4) and (adj_pos >= 1)
say("")
say("[G6] preregistered 3x2x3 neighborhood -- ALL 18 cells (net PRIMARY profit; headline stays "
    "the frozen object)")
say(f"     {'entry':<7}{'exit':<7}{'conditioning':<20}{'n':>4}{'gross pt':>10}{'net pt':>10}"
    f"{'net $':>9}{'frozen':>8}")
for _, r in nb.iterrows():
    say(f"     {r.entry:<7}{r.exit:<7}{r.conditioning:<20}{r.n:>4}"
        f"{r.mean_gross_profit_pts:>10.4f}{r.mean_net_profit_primary_pts:>10.4f}"
        f"{r.mean_net_profit_primary_usd:>9.1f}{'  <<' if r.is_frozen_object else '':>8}")
say(f"     plateau: net>0 in {n_pos_all}/18 cells overall; {n_pos_alldown}/6 all-down cells; "
    f"adjacent-entry (08:40/08:50, exit 15:00, all-down) positive: {adj_pos}/2")
say(f"     plateau statement: {'PLATEAU -- the frozen object is not an isolated cell' if plateau else 'ISOLATED-CELL WARNING'}")

# ==================================================================== G7 release split (report-only)
sp_rows = []
for lab in ("NFP", "CPI"):
    m = np.array([lab in rl for rl in rel_label])
    xm = x_primary[m]
    sp_rows.append((lab, int(m.sum()), float(np.mean(xm))))
say("")
say("[G7] release split (after-cost PRIMARY)")
for lab, n, mu in sp_rows:
    say(f"     {lab}-only: n={n}  mean = {mu:+.4f} pt = {-mu*POINT_VALUE:+.1f} $/ct")
both_neg_split = all(mu < 0 for _, _, mu in sp_rows)
say(f"     both negative: {'YES -- strengthens (not release-local)' if both_neg_split else 'NO -> CLASSIFICATION: release-local, not a veto'}")

# ==================================================================== G8 cost stress
mean_stress = float(np.mean(x_stress))
g8_pass = mean_stress < 0
say("")
say("[G8] cost stress (2 ticks/side, ALL_IN $%.2f RT)" % COST_STRESS_USD)
say(f"     mean after-cost move = {mean_stress:+.4f} pt = {-mean_stress*POINT_VALUE:+.1f} $/ct profit")

# ==================================================================== G9 battery (report-only)
net_usd = trades["profit_net_primary_usd"].to_numpy()
d_idx = pd.DatetimeIndex(pd.to_datetime(dates40.astype(str)))
zb_daily = pd.Series(net_usd, index=d_idx).groupby(level=0).sum()

all_weeks = pd.period_range(pd.Timestamp(str(sessions.min())), pd.Timestamp(str(sessions.max())), freq="W")
zb_wk = pd.Series(0.0, index=all_weeks)
tmp = zb_daily.groupby(zb_daily.index.to_period("W")).sum()
zb_wk.loc[tmp.index] = tmp.values
wk_mean = float(zb_wk.mean()); wk_sd = float(zb_wk.std(ddof=1))
sharpe_wk = wk_mean / wk_sd * np.sqrt(52.0) if wk_sd > 0 else np.nan
yrs = len(zb_wk) / 52.0
mdd_wk = max_drawdown(zb_wk.to_numpy()); cdar_wk = cdar(zb_wk.to_numpy(), alpha=0.95)
mdd_tr = max_drawdown(net_usd); cdar_tr = cdar(net_usd, alpha=0.95)

# UP mirror
posUP = ev1_pos[s1sign_ev == 1.0]
fUP = f1500[posUP]
xUP = fUP - COST_PRIMARY_PTS          # long profit convention: profit = f - cost
bmUP = block_boot_means(xUP, rng=np.random.default_rng(SEED + 3))
ciUP = np.percentile(bmUP, [2.5, 97.5])

# rho to P1 (source: WE_W56_BREADTH p1_daily.csv -- STATED)
p1 = pd.read_csv(P1_DAILY_CSV, index_col=0, parse_dates=True)["p1_usd"]
cal = pd.DatetimeIndex([pd.Timestamp(str(d)) for d in sessions])
cal = cal[(cal >= p1.index.min()) & (cal <= p1.index.max())]
p1_al = p1.reindex(cal).fillna(0.0)
zb_al = zb_daily.reindex(cal).fillna(0.0)
n_tr_overlap = int((zb_al != 0).sum())
rho_d = float(np.corrcoef(p1_al.to_numpy(), zb_al.to_numpy())[0, 1])
p1_w = p1_al.groupby(p1_al.index.to_period("W")).sum()
zb_w2 = zb_al.groupby(zb_al.index.to_period("W")).sum()
rho_w = float(np.corrcoef(p1_w.to_numpy(), zb_w2.to_numpy())[0, 1])

say("")
say("[G9] eval battery -- WEEKLY-VOL LEAD (net PRIMARY $ per contract; %s)" % EVSTAT)
say(f"     weekly grid: {len(zb_wk)} calendar weeks ({yrs:.2f} yr), zeros where no trade")
say(f"     LEAD  weekly-vol annualized Sharpe = {sharpe_wk:.2f}  (mean ${wk_mean:.1f}/wk, sd ${wk_sd:.1f}/wk)")
say(f"     native: total net ${float(np.sum(net_usd)):,.0f} over {yrs:.2f} yr = "
    f"${float(np.sum(net_usd))/yrs:,.0f}/yr on {len(net_usd)/yrs:.1f} trades/yr "
    f"(${float(np.mean(net_usd)):.1f}/trade)")
say(f"     path descriptives ONLY (research_sdk.eval_battery max_drawdown/cdar): weekly maxDD "
    f"${mdd_wk:,.0f}, CDaR95 ${cdar_wk:,.0f}; trade-sequence maxDD ${mdd_tr:,.0f}, CDaR95 ${cdar_tr:,.0f}")
say("     NO fixed-DD- or CDaR-normalized income figure is quoted in this run; the eval_battery")
say("     thinning-placebo guard is honored by never reading those bases as a denominator.")
say("")
say("     UP-response mirror (long at 08:45 on r1>0, exit 15:00; asymmetry honesty):")
say(f"       DOWN-short (frozen): n=40  net {-mean_primary*POINT_VALUE:+.1f} $/ct "
    f"(profit CI [{-ci_hi*POINT_VALUE:+.1f},{-ci_lo*POINT_VALUE:+.1f}])")
say(f"       UP-long   (mirror): n={len(xUP)}  net {float(np.mean(xUP))*POINT_VALUE:+.1f} $/ct "
    f"(profit CI [{ciUP[0]*POINT_VALUE:+.1f},{ciUP[1]*POINT_VALUE:+.1f}])")
say("")
say("     rho to P1 (SOURCE: runs/WE_W56_BREADTH/out/p1_daily.csv, zero-filled common calendar "
    f"{cal.min().date()}..{cal.max().date()}, {len(cal)} sessions; {n_tr_overlap}/40 ZB trades in overlap):")
say(f"       daily rho = {rho_d:+.4f}   weekly rho = {rho_w:+.4f}   (orthogonality preview)")

# ==================================================================== GATE TABLE
g1_pass = True   # procedural: MDE printed before observed (see output order above)
g6_pass = len(nb) == 18
g7_pass = True
g9_pass = True

gates = [
    ("G0_seal_identity",
     "seal <=2026-07-31; reproduce E1 n=40 event set exactly (identity vs artifact)",
     f"max sess {max_sess}; 9/9 cell stats exact; n_down={n_down}", g0_pass),
    ("G1_MDE_first",
     "MDE (block-bootstrap SE) printed BEFORE observed",
     f"MDE_sig {mde_sig:.4f} pt, MDE_80 {mde_80:.4f} pt, printed first (procedural)", g1_pass),
    ("G2_aftercost_edge",
     "PRIMARY after-cost mean < 0 AND block-bootstrap CI95 excludes 0",
     f"mean {mean_primary:+.4f} pt, CI95 [{ci_lo:+.4f},{ci_hi:+.4f}]", g2_pass),
    ("G3_null",
     "shift-null pct <= 5.0 AND |pct1-pct2| <= 5.0 (sign-permutation 2nd computation)",
     f"pct1 {pct1:.2f}, pct2 {pct2:.2f}, |diff| {abs(pct1-pct2):.2f}", g3_pass),
    ("G4_chronology",
     "after-cost mean < 0 in BOTH halves; both-wrong-sign = FAIL; one-flat = REGIME note",
     f"first20 {m1:+.4f}, last20 {m2:+.4f}"
     + (" (REGIME note)" if g4_regime_note else ""), g4_pass),
    ("G5_tail_honesty",
     "drop-k curve printed; after-cost mean < 0 at k=2",
     f"k=2 mean {mean_k2:+.4f} pt (curve in dropk.csv)", g5_pass),
    ("G6_neighborhood",
     "3x2x3 grid, ALL cells reported; headline stays frozen object; plateau statement",
     f"18/18 cells; net>0 in {n_pos_all}/18; all-down {n_pos_alldown}/6; "
     f"{'PLATEAU' if plateau else 'ISOLATED'}", g6_pass),
    ("G7_release_split",
     "NFP-only and CPI-only after-cost means printed; one-side-flat = classification",
     "; ".join(f"{lab} n={n} {mu:+.4f}" for lab, n, mu in sp_rows)
     + ("; both negative" if both_neg_split else "; NOT both negative"), g7_pass),
    ("G8_cost_stress",
     "after-cost mean < 0 at 2-tick STRESS arm",
     f"mean {mean_stress:+.4f} pt = {-mean_stress*POINT_VALUE:+.1f} $/ct", g8_pass),
    ("G9_battery",
     "weekly-vol lead; no unguarded fixed-DD figure; UP mirror; rho-to-P1",
     f"Sharpe_wk {sharpe_wk:.2f}; no DD-normalized income quoted; UP-long net "
     f"{float(np.mean(xUP))*POINT_VALUE:+.1f} $/ct; rho_d {rho_d:+.3f} rho_w {rho_w:+.3f}", g9_pass),
]

say("")
say("=" * 100)
say(f"{'GATE':<20}{'SPEC':<70}{'PASS/FAIL':>10}")
say("-" * 100)
for gid, spec, obs, ok in gates:
    say(f"{gid:<20}{spec:<70}{'PASS' if ok else 'FAIL':>10}")
    say(f"{'':<20}OBSERVED: {obs}")
say("-" * 100)
blocking = dict(G2=g2_pass, G3=g3_pass, G4=g4_pass, G5=g5_pass, G8=g8_pass)
all_block = all(blocking.values())
verdict = "ZBMACRO01 ENGINE CANDIDATE" if all_block else "E1 LEAD CLOSED AT SCOPE"
say(f"blocking set G2+G3+G4+G5+G8: " +
    "  ".join(f"{k}:{'PASS' if v else 'FAIL'}" for k, v in blocking.items()))
say(f"DECISION (mechanical): {verdict}  (ledger {'PASS' if all_block else 'FAIL'})")
if not agree:
    say("NOTE: G3 agreement clause VIOLATED -> INVALID-RUN per prereg.")
say(f"EVIDENCE STATUS: {EVSTAT} (same substrate as the G00067 screen).")
say("=" * 100)

with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(LINES) + "\n")
with open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(LINES) + "\n")
print("\nwrote out/trades.csv, out/dropk.csv, out/neighborhood.csv, out/gate_table.txt, out/run_log.txt")
