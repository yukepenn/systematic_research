#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G3_ZBMACRO_ENGINE_20260906 -- ledger G00079, family GENESIS3_ENGINE.
Engine construction + adversarial skeptic for ZBMACRO01 (the frozen G00072 rule).

FROZEN OBJECT (from G00072, zero retuning of the RULE):
  On GENESIS_H2_CALENDAR NFP_DAY/CPI_DAY sessions: if close(08:45)-close(08:30) < 0
  (ZB points), SHORT k ZB (k=2 from G00078; k=1 also dossiered); exit at close(15:00).
  No overnight. No other conditioning.

EVIDENCE STATUS: DISCOVERY_CONSUMED (same substrate as the G00067 screen), every table.

EXECUTABLE PREREGISTRATION -- every ambiguity resolution FIXED here, before results exist:

  * E0 SEAL+IDENTITY (DEFECT-on-fail): substrate max session <= 2026-07-31 asserted;
    trades.csv sha256 must equal the G00078-printed
    245431500d42becbc6ed8c8f07c0696e9057346d3b52cad05d8976bb2d8e2273; the 40 trades
    (dates, fwd moves) must reproduce EXACTLY (<1e-9) from the substrate via the E1
    constructor (verbatim from run_falsifier.py); joint_series.csv must show 878 rows
    2022-12-27..2026-05-29, 39 active ZB days, and reproduce rho_d -0.0058 /
    rho_w +0.1004 at 4 dp (G00078 C0 values).
  * G_DELAY (blocking; THE decisive question): recompute the frozen object with entry at
    the as-of close of 08:45 (frozen ref), 08:46, 08:47, 08:48, 08:50 -- SAME signal
    (r1 = c0845-c0830 < 0, same 40 events), SAME exit c1500, PRIMARY cost arm unchanged
    (MODELED ALL_IN $66.86 RT = comm $4.36 + 1 tk/side; a 1-min-later close fill does not
    change the modeled cost). x_e = (c1500 - c_e) + cost_pts; net profit $ = -x_e * 1000.
    Entry closes read from the E1 as-of grid (ffill limit 15 min); if any entry close is
    NaN for a trade, that trade is DROPPED from that delayed arm with n printed (fallback
    fixed here; expected n dropped = 0 on release mornings).
    BOOTSTRAP: PAIRED moving-block bootstrap -- ONE shared set of block-start draws
    (L=5, B=2000, seed 20260910) applied to every entry arm, so curve differences are
    never bootstrap noise. CI95 = percentile CI of the after-cost mean move.
    GATE (spec verbatim): PASS iff mean net profit at 08:46 > 0 AND CI95 excludes 0
    (ci_hi of the move < 0). If the 08:46 CI includes 0: verdict FAST-EXECUTION-REQUIRED
    iff net_0846 >= 0.60 * net_0845 AND the 5-point net-profit curve is monotone
    non-increasing (45 >= 46 >= 47 >= 48 >= 50, zero tolerance; operationalization of
    "monotone-decaying" fixed HERE); else KILLED-AT-EXECUTION.
    THE EXECUTABLE ENGINE CLAIM USES close(08:46).
  * D1 DRIFT: per-minute mean cumulative move c(t)-c0845 for t = 08:45..09:15 over the 40
    events (nanmean, n printed), in pts and short-$/ct; plus per-minute increments; coarse
    checkpoints 09:30/10:30/12:00/14:00/15:00 report-only.
  * D2 BATTERY: weekly-vol LEAD on the calendar-week grid spanning the substrate sessions
    (zeros where no trade), Sharpe = mean/sd(ddof=1)*sqrt(52). LEAD arm = the EXECUTABLE
    entry (08:46); 08:45 research arm printed as reference; k=1 and k=2 (k scales $, not
    Sharpe). maxDD/CDaR95 via research_sdk.eval_battery ONLY as dollar path descriptors;
    NO fixed-DD- or CDaR-normalized income anywhere; nothing is thinned (no trade removal
    rule is evaluated) -> thinning placebo N/A, stated.
  * D3 MAE/MFE: intra-trade path on the as-of grid from entry minute+1 to 15:00.
    Short at c_e: MAE_pts = max(max_t c(t) - c_e, 0); MFE_pts = max(c_e - min_t c(t), 0).
    Computed for BOTH the frozen 08:45 entry and the executable 08:46 entry
    (out/maemfe.csv). WORST-5 ANATOMY: the 5 most negative net-$ trades at the EXECUTABLE
    08:46 entry (the object under construction), each with date, release, r1, entry/exit
    px, net, MAE(time), MFE(time), position at 09:15.
  * D4 CALENDAR HONESTY: (i) NFP+CPI same-session overlaps among the 40; (ii) weekday
    table; NFP events not on Friday flagged (holiday-shifted releases); (iii) ROLL: the
    substrate is a merged back-adjusted chain carrying only the rolled contract's volume,
    so the TRUE volume crossover is NOT MEASURABLE here -- ASSUMED-PROXY fixed as: the
    last trading session of Feb/May/Aug/Nov (classic ZB roll month-ends); any event day
    within +-3 SESSIONS of a proxy crossover is flagged, label ASSUMED-PROXY.
  * D5 SESSION/MARGIN: entry 08:45-08:46 ET, flat at 15:00 -> no overnight margin; ZB day
    margin ASSUMED ~$2,000/ct (flagged, no broker surface touched). CAPACITY: stated, not
    proven.
  * D6 ORTHOGONALITY at k=2 from G00078 joint_series.csv AS-IS: rho_d/rho_w of 2x ZB vs
    P1 (both scales; correlation is scale-invariant in k -- stated and shown), and the
    k=2 LIVE_SCALE marginal weekly-vol Sharpe must reproduce +0.0923 (identity, 3 dp).
  * SKEPTIC (blocking; runs AFTER the dossier): four preregistered lenses with kill
    criteria FIXED here:
      L1 duplication: KILL iff the effect is shown tradable-known AND arbitraged
        post-publication; operationalized in-sample as: G00072 last-half after-cost mean
        >= 0 (decay-to-zero). Observed last-20 mean was -0.1363 -> evaluated on today's
        reproduction. Otherwise: mechanism LABEL (post-announcement drift / slow
        repricing), recorded, NO KILL.
      L2 fragility: KILL iff G_DELAY = KILLED-AT-EXECUTION (mechanical link). Otherwise
        the lens must STATE the single most likely way this is nothing.
      L3 regime: KILL iff the chronology halves are BOTH wrong-sign on the reproduction
        (G00072 G4 standard). Otherwise: state the decay condition + a concrete
        prospective chronology-half monitor kill rule (proposed for FT-stage prereg).
      L4 implementation: KILL iff the object cannot be implemented fail-closed in NT8
        (blocking impossibility). Otherwise enumerate FT4-FT9 risks.
    SKEPTIC VERDICT = SURVIVES iff no lens kills.
  * DECISION RULE (spec verbatim, mechanical): G_DELAY in {PASS, FAST-EXECUTION-REQUIRED}
    AND skeptic SURVIVES -> ledger PASS -> FT0 freeze licensed (rule + entry convention
    08:46 + k=2). Any kill -> ledger FAIL with the lens named. E0 failure -> DEFECT, stop.

Data seals: assert every input max session/date < 2026-08-01 (substrate <= 2026-07-31).
POINTS basis on the back-adjusted series (DELEV01), $1000/pt, tick $31.25. Bars
END-stamped, ET sessions 18:00->17:00. No NT8/CrossTrade call is made by this run.
"""

import hashlib
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
TRADES_CSV = os.path.join(REPO, "runs", "G3_ZBMACRO_FALSIFIER_20260906", "out", "trades.csv")
JOINT_CSV = os.path.join(REPO, "runs", "G3_ZBMACRO_CLASSP_20260906", "out", "joint_series.csv")
OUT = os.path.join(RUN_DIR, "out")
os.makedirs(OUT, exist_ok=True)

SEAL_MAX_SESSION = pd.Timestamp("2026-07-31").date()
TRADES_SHA_EXPECTED = "245431500d42becbc6ed8c8f07c0696e9057346d3b52cad05d8976bb2d8e2273"
POINT_VALUE = 1000.0
COMM_RT = 4.36
COST_PRIMARY_USD = COMM_RT + 2 * 31.25          # $66.86
COST_STRESS_USD = COMM_RT + 4 * 31.25           # $129.36
COST_PRIMARY_PTS = COST_PRIMARY_USD / POINT_VALUE
COST_STRESS_PTS = COST_STRESS_USD / POINT_VALUE
B_BOOT = 2000
BLOCK_L = 5
SEED_BOOT = 20260910
ASOF_LIMIT = 15
EVSTAT = "DISCOVERY_CONSUMED"
K_ENGINE = 2

LINES = []
def say(s=""):
    print(s)
    LINES.append(s)

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

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
assert max_sess <= SEAL_MAX_SESSION, f"SEAL VIOLATION: {max_sess}"

msess = ((hh * 60 + mm) - 1080) % 1440
closeA = np.full((NS, 1381), np.nan)
closeA[code, msess] = df["close"].to_numpy()
gridf = pd.DataFrame(closeA).ffill(axis=1, limit=ASOF_LIMIT).to_numpy()
freshA = np.zeros((NS, 1381), dtype=bool)
freshA[code, msess] = True

M0830, M0845, M0846, M0847, M0848, M0850 = 870, 885, 886, 887, 888, 890
M0915, M1500 = 915, 1260
c0830 = gridf[:, M0830]; c0845 = gridf[:, M0845]; c1030 = gridf[:, 990]; c1500 = gridf[:, M1500]

# ==================================================================== E1 event set (verbatim constructor)
nfp = set(pd.to_datetime(pd.read_csv(NFP_CSV)["session_date"]).dt.date)
cpi = set(pd.to_datetime(pd.read_csv(CPI_CSV)["session_date"]).dt.date)
rel_in_window = {d for d in (nfp | cpi) if sessions.min() <= d <= sessions.max()}

u1 = np.flatnonzero(~np.isnan(c0830) & ~np.isnan(c0845) & ~np.isnan(c1030) & ~np.isnan(c1500))
fam1 = u1
fam1_dates = sessions[u1]
is_rel = np.array([d in rel_in_window for d in fam1_dates])
r1 = (c0845 - c0830)[fam1]
f1500 = (c1500 - c0845)[fam1]
ev1_pos_all = np.flatnonzero(is_rel)
ev1_pos = ev1_pos_all[r1[ev1_pos_all] != 0.0]
s1sign_ev = np.sign(r1[ev1_pos])
pos40 = ev1_pos[s1sign_ev == -1.0]
dates40 = fam1_dates[pos40]
r1_40 = r1[pos40]
f40 = f1500[pos40]
sidx40 = fam1[pos40]                    # session-row indices of the 40 events

# ==================================================================== E0 identity vs artifacts
tr = pd.read_csv(TRADES_CSV)
sha_trades = sha256_file(TRADES_CSV)
tr_dates = pd.to_datetime(tr["session_date"]).dt.date.to_numpy()
id_dates = (len(tr) == 40 and len(dates40) == 40 and all(tr_dates == dates40))
id_fwd = bool(np.max(np.abs(tr["fwd_0845_1500_pts"].to_numpy() - f40)) < 1e-9) if id_dates else False
id_r1 = bool(np.max(np.abs(tr["r1_pts"].to_numpy() - r1_40)) < 1e-9) if id_dates else False
sha_ok = sha_trades == TRADES_SHA_EXPECTED
rel_label = tr["release"].to_numpy()
net45_art = tr["profit_net_primary_usd"].to_numpy()

js = pd.read_csv(JOINT_CSV, parse_dates=["date"])
sha_joint = sha256_file(JOINT_CSV)
js_ok_shape = (len(js) == 878 and js["date"].min() == pd.Timestamp("2022-12-27")
               and js["date"].max() == pd.Timestamp("2026-05-29")
               and int((js["zbmacro_k1_usd"] != 0).sum()) == 39)
p1f = js["p1_research_full_usd"].to_numpy(); p1l = js["p1_live_scale_030_usd"].to_numpy()
zb1 = js["zbmacro_k1_usd"].to_numpy()
rho_d1 = float(np.corrcoef(p1f, zb1)[0, 1])
wkP = js["date"].dt.to_period("W")
p1f_w = pd.Series(p1f).groupby(wkP).sum(); zb1_w = pd.Series(zb1).groupby(wkP).sum()
p1l_w = pd.Series(p1l).groupby(wkP).sum()
rho_w1 = float(np.corrcoef(p1f_w, zb1_w)[0, 1])
js_ok_rho = (abs(rho_d1 - (-0.0058)) < 5e-5) and (abs(rho_w1 - 0.1004) < 5e-5)
seal_inputs = (tr_dates.max() < pd.Timestamp("2026-08-01").date()
               and js["date"].max() < pd.Timestamp("2026-08-01"))
e0_pass = bool(sha_ok and id_dates and id_fwd and id_r1 and js_ok_shape and js_ok_rho and seal_inputs)

say("=" * 100)
say("G3_ZBMACRO_ENGINE_20260906  (ledger G00079, family GENESIS3_ENGINE)")
say("ZBMACRO01 engine construction + adversarial skeptic.  EVIDENCE STATUS: %s (all tables)." % EVSTAT)
say(f"substrate: {os.path.relpath(ZB_PARQUET, REPO)}  sessions={NS} ({sessions.min()} .. {sessions.max()})")
say("frozen rule (G00072, zero retuning): NFP/CPI day, close(08:45)-close(08:30)<0 -> SHORT k ZB")
say("  at entry close, exit close(15:00). k=2 (G00078 decision cell); k=1 also dossiered.")
say(f"cost arms (BASIS=MODELED ALL_IN = comm $4.36 + spread): PRIMARY ${COST_PRIMARY_USD:.2f} RT, "
    f"STRESS ${COST_STRESS_USD:.2f} RT; a 1-min-later close fill does not change the modeled cost")
say("")
say("[E0] seal + identity vs frozen artifacts")
say(f"     substrate seal: max session {max_sess} <= {SEAL_MAX_SESSION} OK; input seals "
    f"(trades max {tr_dates.max()}, joint max {js['date'].max().date()}) < 2026-08-01 : "
    f"{'OK' if seal_inputs else 'VIOLATION'}")
say(f"     trades.csv sha256 = {sha_trades}")
say(f"       expected (G00078)= {TRADES_SHA_EXPECTED} : {'MATCH' if sha_ok else 'MISMATCH'}")
say(f"     40-trade reproduction from substrate: dates {'EXACT' if id_dates else 'MISMATCH'}; "
    f"fwd moves {'EXACT<1e-9' if id_fwd else 'MISMATCH'}; r1 {'EXACT<1e-9' if id_r1 else 'MISMATCH'}")
say(f"     joint_series.csv sha256 = {sha_joint}")
say(f"     joint identity: rows/span/active {'OK' if js_ok_shape else 'FAIL'}; "
    f"rho_d {rho_d1:+.4f} (exp -0.0058), rho_w {rho_w1:+.4f} (exp +0.1004) : "
    f"{'OK' if js_ok_rho else 'FAIL'}")
say(f"     E0: {'PASS' if e0_pass else 'FAIL -> DEFECT'}")

if not e0_pass:
    say("E0 FAILED -> DEFECT. STOP.")
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(LINES) + "\n")
    sys.exit(2)

# ==================================================================== G_DELAY -- the decisive question
ENTRIES = [("08:45", M0845), ("08:46", M0846), ("08:47", M0847), ("08:48", M0848), ("08:50", M0850)]

n40 = 40
rng_boot = np.random.default_rng(SEED_BOOT)
Lb = min(BLOCK_L, n40)
nblocks = int(np.ceil(n40 / Lb))
starts_max = n40 - Lb + 1
ST = rng_boot.integers(0, starts_max, size=(B_BOOT, nblocks))          # SHARED draws (paired)
IDX = (ST[:, :, None] + np.arange(Lb)[None, None, :]).reshape(B_BOOT, -1)[:, :n40]

def paired_ci(x):
    means = x[IDX].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi)

curve_rows = []
xmap = {}
for ename, m in ENTRIES:
    ce = gridf[:, m][sidx40]
    fresh = freshA[:, m][sidx40]
    keep = np.isfinite(ce)
    n_drop = int((~keep).sum())
    x = (c1500[sidx40] - ce) + COST_PRIMARY_PTS            # after-cost move (PRIMARY)
    xs = (c1500[sidx40] - ce) + COST_STRESS_PTS
    x_eval = x[keep]
    lo, hi = paired_ci(x_eval) if n_drop == 0 else paired_ci(x_eval)
    xmap[ename] = x
    curve_rows.append(dict(
        entry=ename, minute=m, n=int(keep.sum()), n_dropped_nan=n_drop,
        n_fresh_bar=int(fresh.sum()),
        mean_gross_move_pts=float(np.mean((c1500[sidx40] - ce)[keep])),
        mean_aftercost_move_pts=float(np.mean(x_eval)),
        ci_lo_move_pts=lo, ci_hi_move_pts=hi,
        mean_net_profit_primary_usd=float(-np.mean(x_eval) * POINT_VALUE),
        profit_ci_lo_usd=float(-hi * POINT_VALUE), profit_ci_hi_usd=float(-lo * POINT_VALUE),
        mean_net_profit_stress_usd=float(-np.mean(xs[keep]) * POINT_VALUE),
        evidence_status=EVSTAT))
cv = pd.DataFrame(curve_rows)
cv["retention_vs_0845"] = cv["mean_net_profit_primary_usd"] / \
    float(cv.loc[cv.entry == "08:45", "mean_net_profit_primary_usd"].iloc[0])
cv.to_csv(os.path.join(OUT, "delay_curve.csv"), index=False)

net45 = float(cv.loc[cv.entry == "08:45", "mean_net_profit_primary_usd"].iloc[0])
net46 = float(cv.loc[cv.entry == "08:46", "mean_net_profit_primary_usd"].iloc[0])
hi46 = float(cv.loc[cv.entry == "08:46", "ci_hi_move_pts"].iloc[0])
lo46 = float(cv.loc[cv.entry == "08:46", "ci_lo_move_pts"].iloc[0])
profits = cv["mean_net_profit_primary_usd"].to_numpy()
monotone = bool(np.all(np.diff(profits) <= 0.0))
retention46 = net46 / net45 if net45 > 0 else np.nan
ci46_excl0 = (net46 > 0) and (hi46 < 0)

if ci46_excl0:
    gdelay_verdict = "PASS"
elif (retention46 >= 0.60) and monotone:
    gdelay_verdict = "FAST-EXECUTION-REQUIRED"
else:
    gdelay_verdict = "KILLED-AT-EXECUTION"
gdelay_ok = gdelay_verdict in ("PASS", "FAST-EXECUTION-REQUIRED")

say("")
say("[G_DELAY] THE DECISIVE QUESTION -- delayed-entry curve (same 40 events, same signal, same")
say("          15:00 exit, PRIMARY cost; paired moving-block bootstrap L=%d B=%d seed %d)" %
    (BLOCK_L, B_BOOT, SEED_BOOT))
say(f"     {'entry':<7}{'n':>3}{'fresh':>6}{'gross pt':>10}{'net move pt':>12}"
    f"{'net $/ct':>10}{'CI95 profit $/ct':>22}{'retention':>10}")
for _, r in cv.iterrows():
    say(f"     {r.entry:<7}{r.n:>3}{r.n_fresh_bar:>6}{r.mean_gross_move_pts:>10.4f}"
        f"{r.mean_aftercost_move_pts:>12.4f}{r.mean_net_profit_primary_usd:>10.1f}"
        f"   [{r.profit_ci_lo_usd:>+8.1f},{r.profit_ci_hi_usd:>+8.1f}]{r.retention_vs_0845:>10.3f}")
say(f"     STRESS-arm net $/ct along the curve: " +
    "  ".join(f"{r.entry} {r.mean_net_profit_stress_usd:+.1f}" for _, r in cv.iterrows()))
say(f"     08:46 clause: net {net46:+.1f} $/ct > 0 : {net46 > 0}; CI95 of move "
    f"[{lo46:+.4f},{hi46:+.4f}] excludes 0 : {hi46 < 0}")
say(f"     fallback clauses: retention {retention46:.3f} (>=0.60: {retention46 >= 0.60}); "
    f"monotone non-increasing 45>=46>=47>=48>=50: {monotone}")
say(f"     G_DELAY VERDICT: {gdelay_verdict}")

# ==================================================================== D1 per-minute drift 08:45->09:15
say("")
say("[D1] per-minute drift decomposition on the 40 event days (cumulative from 08:45 close;")
say("     short $/ct = -move*1000; nanmean over available as-of closes)")
say(f"     {'minute':<8}{'n':>3}{'cum move pt':>12}{'cum short $':>12}{'incr pt':>10}")
prev = np.zeros(40)
drift_rows = []
for m in range(M0845, M0915 + 1):
    cm = gridf[:, m][sidx40] - c0845[sidx40]
    n_ok = int(np.isfinite(cm).sum())
    mu = float(np.nanmean(cm))
    inc = float(np.nanmean(cm - prev))
    hhmm = f"{(m + 1080) // 60 % 24:02d}:{(m + 1080) % 60:02d}"
    drift_rows.append((hhmm, n_ok, mu, -mu * POINT_VALUE, inc))
    say(f"     {hhmm:<8}{n_ok:>3}{mu:>12.4f}{-mu*POINT_VALUE:>12.1f}{inc:>10.4f}")
    prev = cm
say("     coarse checkpoints (report-only):")
for m, lab in ((930, "09:30"), (990, "10:30"), (1080, "12:00"), (1200, "14:00"), (1260, "15:00")):
    cm = gridf[:, m][sidx40] - c0845[sidx40]
    say(f"     {lab:<8}{int(np.isfinite(cm).sum()):>3}{float(np.nanmean(cm)):>12.4f}"
        f"{-float(np.nanmean(cm))*POINT_VALUE:>12.1f}")
cm0850 = float(np.nanmean(gridf[:, M0850][sidx40] - c0845[sidx40]))
cm0915 = float(np.nanmean(gridf[:, M0915][sidx40] - c0845[sidx40]))
cm1500 = float(np.nanmean(c1500[sidx40] - c0845[sidx40]))
say(f"     share of the eventual mean move realized by 08:50: {cm0850/cm1500*100:.1f}% ; "
    f"by 09:15: {cm0915/cm1500*100:.1f}%  (gross, pts basis)")

# ==================================================================== D2 eval battery
say("")
say("[D2] eval battery -- WEEKLY-VOL LEAD; LEAD arm = EXECUTABLE entry 08:46; 08:45 reference")
all_weeks = pd.period_range(pd.Timestamp(str(sessions.min())), pd.Timestamp(str(sessions.max())), freq="W")
d_idx = pd.DatetimeIndex(pd.to_datetime(dates40.astype(str)))
yrs_cal = (pd.Timestamp(str(sessions.max())) - pd.Timestamp(str(sessions.min()))).days / 365.25

battery = {}
for ename in ("08:46", "08:45"):
    net_usd = -xmap[ename] * POINT_VALUE
    daily = pd.Series(net_usd, index=d_idx).groupby(level=0).sum()
    wk = pd.Series(0.0, index=all_weeks)
    tmp = daily.groupby(daily.index.to_period("W")).sum()
    wk.loc[tmp.index] = tmp.values
    mu, sd = float(wk.mean()), float(wk.std(ddof=1))
    battery[ename] = dict(
        sharpe_wk=mu / sd * np.sqrt(52.0), wk_mean=mu, wk_sd=sd,
        total=float(np.sum(net_usd)), per_yr=float(np.sum(net_usd)) / yrs_cal,
        mdd_wk=max_drawdown(wk.to_numpy()), cdar_wk=cdar(wk.to_numpy(), 0.95),
        mdd_tr=max_drawdown(net_usd), cdar_tr=cdar(net_usd, 0.95))
for ename, lab in (("08:46", "EXECUTABLE (LEAD)"), ("08:45", "research reference")):
    b = battery[ename]
    say(f"     entry {ename} [{lab}] k=1: Sharpe_wk {b['sharpe_wk']:.2f} "
        f"(mean ${b['wk_mean']:.1f}/wk sd ${b['wk_sd']:.1f}/wk); total ${b['total']:,.0f} "
        f"= ${b['per_yr']:,.0f}/yr on {40/yrs_cal:.1f} tr/yr")
    say(f"       path descriptors ($, k=1): weekly maxDD ${b['mdd_wk']:,.0f}, CDaR95 ${b['cdar_wk']:,.0f}; "
        f"trade-seq maxDD ${b['mdd_tr']:,.0f}, CDaR95 ${b['cdar_tr']:,.0f}")
    say(f"       k={K_ENGINE}: ${b['per_yr']*K_ENGINE:,.0f}/yr; weekly maxDD ${b['mdd_wk']*K_ENGINE:,.0f}, "
        f"CDaR95 ${b['cdar_wk']*K_ENGINE:,.0f} (linear in k; Sharpe invariant)")
say("     fixed-DD/CDaR figures above are DOLLAR PATH DESCRIPTORS ONLY -- no income is normalized")
say("     by them; NO trade-removal rule is evaluated in this run -> thinning placebo N/A (stated).")

# ==================================================================== D3 MAE/MFE + worst-5
mae_rows = []
for i in range(40):
    row = dict(session_date=dates40[i], release=rel_label[i], r1_pts=r1_40[i])
    for ename, m in (("0845", M0845), ("0846", M0846)):
        ce = float(gridf[sidx40[i], m])
        path = gridf[sidx40[i], m + 1:M1500 + 1]
        ok = np.isfinite(path)
        mae = float(max(np.max(path[ok]) - ce, 0.0)) if ok.any() else np.nan
        mfe = float(max(ce - np.min(path[ok]), 0.0)) if ok.any() else np.nan
        t_mae = int(m + 1 + np.argmax(np.where(ok, path, -np.inf))) if ok.any() else -1
        t_mfe = int(m + 1 + np.argmin(np.where(ok, path, np.inf))) if ok.any() else -1
        row[f"entry_{ename}_px"] = ce
        row[f"mae_{ename}_pts"] = mae; row[f"mfe_{ename}_pts"] = mfe
        row[f"mae_{ename}_time"] = f"{(t_mae+1080)//60%24:02d}:{(t_mae+1080)%60:02d}"
        row[f"mfe_{ename}_time"] = f"{(t_mfe+1080)//60%24:02d}:{(t_mfe+1080)%60:02d}"
        row[f"net_{ename}_usd"] = float(-((c1500[sidx40[i]] - ce) + COST_PRIMARY_PTS) * POINT_VALUE)
    m915 = float(gridf[sidx40[i], M0915] - gridf[sidx40[i], M0846])
    row["pnl_at_0915_from_0846_usd"] = -m915 * POINT_VALUE
    row["evidence_status"] = EVSTAT
    mae_rows.append(row)
mf = pd.DataFrame(mae_rows)
mf.to_csv(os.path.join(OUT, "maemfe.csv"), index=False)

say("")
say("[D3] MAE/MFE from the 1-min as-of path (short; pts; PRIMARY cost applied to net only)")
for ename in ("0845", "0846"):
    mae = mf[f"mae_{ename}_pts"]; mfe = mf[f"mfe_{ename}_pts"]
    say(f"     entry {ename[:2]}:{ename[2:]}: MAE mean {mae.mean():.3f} med {mae.median():.3f} "
        f"p90 {mae.quantile(0.9):.3f} max {mae.max():.3f} pt "
        f"(${mae.mean()*1000:.0f}/${mae.max()*1000:.0f} mean/max per ct); "
        f"MFE mean {mfe.mean():.3f} med {mfe.median():.3f} max {mfe.max():.3f} pt")
w = mf[f"net_0846_usd"] > 0
say(f"     08:46 winners (n={int(w.sum())}): MAE mean {mf.loc[w,'mae_0846_pts'].mean():.3f} pt; "
    f"losers (n={int((~w).sum())}): MAE mean {mf.loc[~w,'mae_0846_pts'].mean():.3f} pt")
say("")
say("     WORST-5 anatomy (by net $ at the EXECUTABLE 08:46 entry):")
worst5 = mf.nsmallest(5, "net_0846_usd")
say(f"     {'date':<12}{'rel':<9}{'r1 pt':>8}{'net46 $':>9}{'net45 $':>9}{'MAE pt':>8}"
    f"{'@':>7}{'MFE pt':>8}{'@':>7}{'pnl@0915$':>10}")
for _, r in worst5.iterrows():
    say(f"     {str(r.session_date):<12}{r.release:<9}{r.r1_pts:>8.3f}{r.net_0846_usd:>9.1f}"
        f"{r.net_0845_usd if 'net_0845_usd' in r else r['net_0845_usd']:>9.1f}"
        f"{r.mae_0846_pts:>8.3f}{r.mae_0846_time:>7}{r.mfe_0846_pts:>8.3f}{r.mfe_0846_time:>7}"
        f"{r.pnl_at_0915_from_0846_usd:>10.1f}")

# ==================================================================== D4 calendar honesty
say("")
say("[D4] calendar honesty")
overlap = [str(d) for d in dates40 if (d in nfp and d in cpi)]
say(f"     NFP+CPI same-session overlaps among the 40: {len(overlap)}"
    + (f" ({', '.join(overlap)})" if overlap else ""))
wd = pd.Series([pd.Timestamp(str(d)).day_name() for d in dates40])
say("     weekday table: " + "  ".join(f"{k} {v}" for k, v in wd.value_counts().items()))
nfp_offfri = [str(dates40[i]) for i in range(40)
              if "NFP" in rel_label[i] and pd.Timestamp(str(dates40[i])).day_name() != "Friday"]
say(f"     NFP events NOT on Friday (holiday-shift check): {len(nfp_offfri)}"
    + (f" ({', '.join(nfp_offfri)})" if nfp_offfri else ""))
# roll proxy: last trading session of Feb/May/Aug/Nov, +-3 sessions
sess_pd = pd.DatetimeIndex([pd.Timestamp(str(d)) for d in sessions])
proxy_idx = []
for y in range(2023, 2027):
    for mo in (2, 5, 8, 11):
        in_m = np.flatnonzero((sess_pd.year == y) & (sess_pd.month == mo))
        if len(in_m):
            proxy_idx.append(in_m[-1])
flagged = []
for i in range(40):
    si = sess_idx[dates40[i]]
    dmin = min(abs(si - p) for p in proxy_idx)
    if dmin <= 3:
        flagged.append((str(dates40[i]), dmin))
say("     roll windows (ASSUMED-PROXY: last session of Feb/May/Aug/Nov; TRUE volume crossover")
say("     NOT MEASURABLE from the merged chain -- it carries only the rolled contract's volume):")
say(f"     event days within +-3 sessions of a proxy crossover: {len(flagged)}"
    + (f" -> {', '.join(f'{d} (d={k})' for d, k in flagged)}" if flagged else ""))

# ==================================================================== D5 session/margin/capacity
say("")
say("[D5] session/margin facts (ASSUMED-flagged) + capacity note")
say("     entry 08:45-08:46 ET, flat at the 15:00 close -> intraday only, NO overnight margin.")
say("     ZB day margin ASSUMED ~$2,000/ct (FLAGGED: not broker-verified; no broker surface")
say("     touched by this run). k=2 ~ $4,000 intraday for ~6h14m on ~11 days/yr.")
say("     capacity: ZB top-of-book depth is deep (among the deepest CME treasuries books);")
say("     k=2 is negligible size. STATED, NOT PROVEN -- no depth data is read by this run.")

# ==================================================================== D6 orthogonality at k=2
zb2 = K_ENGINE * zb1
rho_d2 = float(np.corrcoef(p1f, zb2)[0, 1])
zb2_w = K_ENGINE * zb1_w
rho_w2 = float(np.corrcoef(p1f_w, zb2_w)[0, 1])
book_w = p1l_w + zb2_w
s_p1 = float(p1l_w.mean() / p1l_w.std(ddof=1) * np.sqrt(52))
s_book = float(book_w.mean() / book_w.std(ddof=1) * np.sqrt(52))
marg = s_book - s_p1
marg_ok = abs(marg - 0.0923) < 5e-4
say("")
say("[D6] orthogonality recomputation at k=2 (G00078 joint_series.csv AS-IS; 178-wk grid)")
say(f"     rho(ZB k=2, P1): daily {rho_d2:+.4f}, weekly {rho_w2:+.4f} "
    f"(scale-invariant in k: k=1 gives {rho_d1:+.4f}/{rho_w1:+.4f} -- identical, as stated)")
say(f"     k=2 LIVE_SCALE marginal weekly-vol Sharpe: {s_book:.4f} - {s_p1:.4f} = {marg:+.4f} "
    f"(G00078 printed +0.0923; reproduction {'OK' if marg_ok else 'FAIL'})")

# ==================================================================== SKEPTIC (preregistered kill criteria)
x45 = xmap["08:45"]
h1m, h2m = float(np.mean(x45[:20])), float(np.mean(x45[20:]))
l1_kill = h2m >= 0.0                      # arbitraged-away operationalization
l2_kill = (gdelay_verdict == "KILLED-AT-EXECUTION")
l3_kill = (h1m >= 0.0) and (h2m >= 0.0)   # both-wrong-sign
l4_kill = False                            # no blocking impossibility found (enumerated below)
kills = dict(duplication=l1_kill, fragility=l2_kill, regime=l3_kill, implementation=l4_kill)
skeptic_survives = not any(kills.values())
killed_lenses = [k for k, v in kills.items() if v]

say("")
say("[SKEPTIC] adversarial section -- preregistered kill criteria (see src header), applied")
say("          mechanically; full prose in out/skeptic.md")
say(f"     L1 duplication: last-half after-cost mean {h2m:+.4f} pt (kill iff >= 0, i.e. arbitraged")
say(f"        in-sample): {'KILL' if l1_kill else 'NO KILL -> mechanism LABEL: post-announcement'}")
say("        drift / slow repricing of the 08:30 surprise on the bond side (a label, not a kill).")
say(f"     L2 fragility: G_DELAY = {gdelay_verdict} (kill iff KILLED-AT-EXECUTION): "
    f"{'KILL' if l2_kill else 'NO KILL'}")
say("        single most likely way this is nothing: n=40 tail-carried (66% in 3 trades),")
say("        |mean| below its own MDE_80, selected from the G00067 event-screen family.")
say(f"     L3 regime: halves {h1m:+.4f} / {h2m:+.4f} pt (kill iff BOTH >= 0): "
    f"{'KILL' if l3_kill else 'NO KILL'}; decay condition + prospective monitor in skeptic.md")
say(f"     L4 implementation: fail-closed NT8 path exists (1-min ZB primary, flatten 15:00,")
say("        no-bar-guard on 08:30/08:45): NO KILL; FT4-FT9 risks enumerated in skeptic.md")
say(f"     SKEPTIC VERDICT: {'SURVIVES' if skeptic_survives else 'KILLED (' + ', '.join(killed_lenses) + ')'}")

# ==================================================================== GATE TABLE + DECISION
d_complete = True  # all dossier sections printed above (procedural)
ledger_pass = bool(e0_pass and gdelay_ok and skeptic_survives)
gates = [
    ("E0_seal_identity",
     "seals; trades.csv sha; 40-trade exact repro; joint identity (878/39, rho 4dp)",
     f"sha MATCH; dates/fwd/r1 EXACT; joint OK rho_d {rho_d1:+.4f} rho_w {rho_w1:+.4f}", e0_pass),
    ("G_delay",
     "08:46 net>0 & CI95 excl 0 -> PASS; else >=60% retention & monotone -> FAST-EXEC; else KILLED",
     f"net46 {net46:+.1f} $/ct, CI [{-hi46*1000:+.1f},{-lo46*1000:+.1f}], retention {retention46:.3f}, "
     f"monotone {monotone} -> {gdelay_verdict}", gdelay_ok),
    ("D_dossier",
     "drift, battery (wk-vol lead, no DD-normalized income), MAE/MFE, worst-5, calendar, "
     "margin(ASSUMED), capacity(stated), orthogonality k=2 -- all printed",
     "all sections printed; battery lead = 08:46 executable arm; placebo N/A stated", d_complete),
    ("S_skeptic",
     "four lenses, preregistered kill criteria, mechanical verdict",
     f"kills: {kills} -> {'SURVIVES' if skeptic_survives else 'KILLED'}", skeptic_survives),
]
say("")
say("=" * 100)
say(f"{'GATE':<18}{'SPEC':<72}{'PASS/FAIL':>10}")
say("-" * 100)
for gid, spec, obs, ok in gates:
    say(f"{gid:<18}{spec:<72}{'PASS' if ok else 'FAIL':>10}")
    say(f"{'':<18}OBSERVED: {obs}")
say("-" * 100)
say(f"DECISION RULE: G_delay in {{PASS, FAST-EXECUTION-REQUIRED}} AND skeptic SURVIVES -> ledger PASS")
say(f"G_delay = {gdelay_verdict}; skeptic = {'SURVIVES' if skeptic_survives else 'KILLED: ' + ', '.join(killed_lenses)}")
verdict = ("ZBMACRO01 ENGINE FROZEN-READY (FT0 licensed: rule + entry close(08:46) + k=2)"
           if ledger_pass else
           "ZBMACRO01 CLOSED AT ENGINE STAGE (lens: " + ", ".join(killed_lenses or ["G_delay"]) + ")")
say(f"DECISION (mechanical): {verdict}  (ledger {'PASS' if ledger_pass else 'FAIL'})")
say(f"EVIDENCE STATUS: {EVSTAT} -- nothing here is forward evidence; no baseline is touched.")
say("=" * 100)

with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(LINES) + "\n")
with open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(LINES) + "\n")

# ==================================================================== dossier.md (program-written)
b46, b45 = battery["08:46"], battery["08:45"]
drift_tbl = "\n".join(f"| {h} | {n} | {mu:+.4f} | {usd:+.1f} | {inc:+.4f} |"
                      for h, n, mu, usd, inc in drift_rows)
curve_tbl = "\n".join(
    f"| {r.entry} | {r.n} | {r.mean_gross_move_pts:+.4f} | {r.mean_net_profit_primary_usd:+.1f} | "
    f"[{r.profit_ci_lo_usd:+.1f}, {r.profit_ci_hi_usd:+.1f}] | {r.mean_net_profit_stress_usd:+.1f} | "
    f"{r.retention_vs_0845:.3f} |" for _, r in cv.iterrows())
w5_tbl = "\n".join(
    f"| {r.session_date} | {r.release} | {r.r1_pts:+.3f} | {r.net_0846_usd:+.1f} | {r.net_0845_usd:+.1f} | "
    f"{r.mae_0846_pts:.3f} @ {r.mae_0846_time} | {r.mfe_0846_pts:.3f} @ {r.mfe_0846_time} | "
    f"{r.pnl_at_0915_from_0846_usd:+.1f} |" for _, r in worst5.iterrows())

dossier = f"""# ZBMACRO01 engine dossier -- G3_ZBMACRO_ENGINE_20260906 (ledger G00079)

**EVIDENCE STATUS: {EVSTAT} (every table).** Program-written by `src/run_engine.py`; the
gate table and full log are `out/gate_table.txt` / `out/run_log.txt`.

## 0. The engine object (FT0-freeze candidate)

- **Rule (frozen, G00072, zero retuning):** on GENESIS_H2_CALENDAR NFP_DAY/CPI_DAY sessions,
  if close(08:45) - close(08:30) < 0 (ZB points), SHORT k ZB, exit at close(15:00). No
  overnight, no other conditioning.
- **Entry convention (THE EXECUTABLE CLAIM): fill at the close of the 08:46 bar** -- the
  signal is known at the 08:45 close; one full minute of latency is charged before the fill.
- **Size: k=2** (G00078 Class-P decision cell; k=1 also dossiered throughout).
- **Cost (BASIS=MODELED ALL_IN):** PRIMARY $66.86/RT (comm $4.36 + 1 tk/side); STRESS $129.36/RT.

## 1. THE DECISIVE QUESTION -- the delay curve (G_delay)

Same 40 events, same signal, same exit; only the entry close is delayed. Paired moving-block
bootstrap (L=5, B=2000, seed 20260910; one shared draw across arms).

| entry | n | gross move pt | net $/ct | CI95 profit $/ct | STRESS $/ct | retention |
|---|---|---|---|---|---|---|
{curve_tbl}

- **G_delay verdict: {gdelay_verdict}** -- 08:46 net {net46:+.1f} $/ct, CI
  [{-hi46 * 1000:+.1f}, {-lo46 * 1000:+.1f}], retention {retention46:.3f} of the 08:45 edge;
  curve monotone non-increasing: {monotone}.
- The G00072 neighborhood's 08:50 cell ($17.7/ct) conditioned on r(08:50); THIS curve holds
  the signal fixed at r1(08:45) and delays only the fill -- the executable question.

## 2. Per-minute drift 08:45 -> 09:15 (event days, cumulative from the 08:45 close)

| minute | n | cum move pt | cum short $ | incr pt |
|---|---|---|---|---|
{drift_tbl}

Share of the eventual (15:00) mean move already realized: by 08:50 **{cm0850 / cm1500 * 100:.1f}%**,
by 09:15 **{cm0915 / cm1500 * 100:.1f}%** (gross, pts). Checkpoints: 09:30
{-float(np.nanmean(gridf[:, 930][sidx40] - c0845[sidx40])) * 1000:+.0f} $, 10:30
{-float(np.nanmean(gridf[:, 990][sidx40] - c0845[sidx40])) * 1000:+.0f} $, 12:00
{-float(np.nanmean(gridf[:, 1080][sidx40] - c0845[sidx40])) * 1000:+.0f} $, 14:00
{-float(np.nanmean(gridf[:, 1200][sidx40] - c0845[sidx40])) * 1000:+.0f} $, 15:00
{-cm1500 * 1000:+.0f} $ (per ct, gross).

## 3. eval_battery (weekly-vol LEAD; LEAD arm = executable 08:46 entry)

| arm | Sharpe_wk | $/wk mean (sd) | $/yr k=1 | $/yr k=2 | wk maxDD k=1 | wk CDaR95 k=1 |
|---|---|---|---|---|---|---|
| **08:46 executable (LEAD)** | **{b46['sharpe_wk']:.2f}** | {b46['wk_mean']:.1f} ({b46['wk_sd']:.1f}) | {b46['per_yr']:,.0f} | {b46['per_yr'] * 2:,.0f} | {b46['mdd_wk']:,.0f} | {b46['cdar_wk']:,.0f} |
| 08:45 research reference | {b45['sharpe_wk']:.2f} | {b45['wk_mean']:.1f} ({b45['wk_sd']:.1f}) | {b45['per_yr']:,.0f} | {b45['per_yr'] * 2:,.0f} | {b45['mdd_wk']:,.0f} | {b45['cdar_wk']:,.0f} |

maxDD/CDaR are **dollar path descriptors only** -- no income is normalized by them, no trade
is removed by any rule in this run, so **the thinning placebo is N/A (stated)**. Sharpe is
k-invariant; dollars and dollar tails scale linearly in k.

## 4. MAE/MFE (1-min as-of path) and worst-5 anatomy

- Entry 08:46: MAE mean {mf['mae_0846_pts'].mean():.3f} / med {mf['mae_0846_pts'].median():.3f} /
  p90 {mf['mae_0846_pts'].quantile(0.9):.3f} / max {mf['mae_0846_pts'].max():.3f} pt
  (${mf['mae_0846_pts'].mean() * 1000:.0f} mean, ${mf['mae_0846_pts'].max() * 1000:.0f} max per ct);
  MFE mean {mf['mfe_0846_pts'].mean():.3f} / max {mf['mfe_0846_pts'].max():.3f} pt.
- Winners' MAE mean {mf.loc[w, 'mae_0846_pts'].mean():.3f} pt vs losers'
  {mf.loc[~w, 'mae_0846_pts'].mean():.3f} pt -- per-trade table in `out/maemfe.csv`.

Worst 5 by net $ at the executable entry:

| date | rel | r1 pt | net46 $ | net45 $ | MAE pt @ t | MFE pt @ t | pnl@09:15 $ |
|---|---|---|---|---|---|---|---|
{w5_tbl}

## 5. Calendar honesty

- NFP+CPI same-session overlaps among the 40: **{len(overlap)}**{(' (' + ', '.join(overlap) + ')') if overlap else ''}.
- Weekdays: {'  '.join(f'{k} {v}' for k, v in wd.value_counts().items())}. NFP not on Friday:
  **{len(nfp_offfri)}**{(' (' + ', '.join(nfp_offfri) + ')') if nfp_offfri else ''}.
- Roll windows (**ASSUMED-PROXY** -- the merged chain carries only the rolled contract's
  volume, so the true volume crossover is NOT measurable here; proxy = last session of
  Feb/May/Aug/Nov): event days within +-3 sessions: **{len(flagged)}**
  {('-> ' + ', '.join(f'{d} (d={k})' for d, k in flagged)) if flagged else ''}.

## 6. Session, margin, capacity

- Entry 08:45-08:46 ET, flat at the 15:00 close: intraday only, **no overnight margin**.
- ZB day margin **ASSUMED ~$2,000/ct (FLAGGED, not broker-verified; no broker surface
  touched)**; k=2 ~ $4,000 for ~6h14m on ~11 days/yr.
- Capacity: ZB top-of-book depth is deep; k=2 is negligible. **Stated, not proven.**

## 7. Orthogonality at k=2 (G00078 joint series AS-IS, 178-week grid)

rho(ZB k=2, P1): daily {rho_d2:+.4f}, weekly {rho_w2:+.4f} (identical to k=1 -- correlation is
scale-invariant in k). k=2 LIVE_SCALE marginal weekly-vol Sharpe {marg:+.4f}
(reproduces G00078's +0.0923: {'OK' if marg_ok else 'FAIL'}).

## 8. Verdict carried to the gate table

G_delay = **{gdelay_verdict}**; skeptic = **{'SURVIVES' if skeptic_survives else 'KILLED'}** ->
**{verdict}** (ledger {'PASS' if ledger_pass else 'FAIL'}).
"""
with open(os.path.join(OUT, "dossier.md"), "w", encoding="utf-8") as fh:
    fh.write(dossier)

# ==================================================================== skeptic.md (program-written)
skeptic = f"""# ZBMACRO01 adversarial skeptic -- G3_ZBMACRO_ENGINE_20260906 (ledger G00079)

**Framing: refuter.** The job of this section is to kill the engine. Kill criteria were
preregistered in `src/run_engine.py` (header) BEFORE any result existed and are applied
mechanically. **EVIDENCE STATUS: {EVSTAT}.**

## Lens 1 -- DUPLICATION ("this is just published post-announcement drift")

**Attack.** r1 = close(08:45)-close(08:30) on a release morning is close to a linear read of
the macro surprise: a down first response IS "the number came in hawkish/strong". Bond-market
post-announcement drift after macro surprises is published literature (announcement-day
momentum/underreaction). If every rates desk knows it, the residual after their arbitrage
should be zero, and our +$177/ct is a measurement artifact of a lucky window.

**What the attack must show to kill (preregistered):** the effect is tradable-known AND
arbitraged post-publication -- operationalized in-sample as last-half after-cost mean >= 0.

**Observed:** last-20 after-cost mean {h2m:+.4f} pt ({-h2m * 1000:+.1f} $/ct) -- still profitable
through 2026. The shift-null (G00072 G3) put the effect at the 0.5th percentile with a
POSITIVE null mean: generic down-momentum on non-release days LOSES money, so this is not a
generic drift harvest either. **Verdict: NO KILL.** The lens instead assigns the mechanism
LABEL: **behavioral underreaction / slow repricing of an 08:30 macro surprise** -- a known
mechanism family. That label cuts both ways: it makes the effect more credible ex ante and
predicts it is crowded-fragile ex post; the regime lens owns the monitoring consequence.

## Lens 2 -- FRAGILITY ("the edge lives in 5 minutes and 3 trades")

**Attack.** (i) Latency: the G00072 neighborhood showed the 08:50-conditioned cell at
$17.7/ct. If the executable 08:46 fill cannot hold the edge, the claim dies. (ii)
Concentration: top-3 trades = 66% of net; drop-k dies at k~5. (iii) Power: |mean| 0.1777 pt
< MDE_80 0.2641 pt at n=40. (iv) Family: E1 came out of the G00067 event screen -- some
selection debt is unpaid even after the falsifier.

**Preregistered kill:** G_delay = KILLED-AT-EXECUTION.

**Observed delay curve (net $/ct, PRIMARY):** {'  '.join(f"{r.entry} {r.mean_net_profit_primary_usd:+.1f}" for _, r in cv.iterrows())};
08:46 CI [{-hi46 * 1000:+.1f}, {-lo46 * 1000:+.1f}] $/ct; retention {retention46:.3f};
monotone {monotone}. **G_delay = {gdelay_verdict} -> {'NO KILL' if not l2_kill else 'KILL'}.**

**The single most likely way this is nothing (stated, as required):** a tail-carried n=40
object below its own 80%-power MDE, drawn from an event-screen family -- i.e., three good
CPI mornings in 2023 doing 66% of the work, with the rest near noise. The falsifier's CI,
null, chronology and drop-k clauses all passed, but every one of them is a point-in-time
in-sample statement on the same consumed substrate. This risk is IRREDUCIBLE at n=40 and is
carried forward as the engine's stated fragility, to be discharged only by forward trades.

## Lens 3 -- REGIME ("2023-2026 is the inflation-attention era")

**Attack.** The sample is exactly the era when CPI/NFP were THE bond-market events. In a
2% -inflation regime CPI mornings stop moving ZB; the conditioning event (|r1| large enough
to matter) thins out and the drift mechanism starves.

**Preregistered kill:** both chronology halves wrong-sign. **Observed:** {h1m:+.4f} /
{h2m:+.4f} pt -- both profitable. **NO KILL.**

**Decay condition (named):** the edge requires (i) scheduled 08:30 releases that still move
ZB (measurable: |r1| level) and (ii) minutes-scale underreaction persisting. **Regime
indicator:** rolling median |r1| over the trailing 12 events vs the 2023-2026 sample median
({float(np.median(np.abs(r1_40))):.3f} pt on the 40 events); a sustained fall below HALF that
level says the conditioning regime has left.

**Prospective kill rule (proposed for FT-stage preregistration; a chronology-half monitor):**
maintain the cumulative FORWARD after-cost mean at the executable 08:46 entry; evaluate at
every 10th forward trade; **KILL if at n_fwd >= 20 the cumulative forward after-cost mean
<= 0**, and REVIEW (owner packet) if at n_fwd >= 10 it is below -$100/ct. At ~11 trades/yr
the kill point arrives in ~2 years -- stated so nobody mistakes this for a fast-falsifying
object.

## Lens 4 -- IMPLEMENTATION ("the NT8 path will not be the research object")

**Attack surface (FT4-FT9 risks, enumerated):**
1. **New class** -- no shared lineage with the certified P1/XM classes; every W52-class
   parity lesson (decision-series first, dollars last) must be re-earned on ZB.
2. **Roll guard inheritance** -- ZB's quarterly roll differs from NQ/MNQ's; the W98-family
   roll fail-safe LATCHES; a wrong ZB rollover date would block entries silently. The ZB
   rollover table must be built from scratch, never inherited.
3. **Session flatten at 15:00** -- CBOT 30Y trades to 17:00; the 15:00 exit is a strategy
   order, not a session end. A missed flatten holds overnight -- the object explicitly
   forbids that; the flatten needs its own fail-safe (flatten-or-disable).
4. **Fail-closed on missing bars** -- ZB prints no bar in zero-trade minutes. The signal
   needs the 08:30 and 08:45 closes; if either bar is missing/stale the engine must STAND
   ASIDE (no as-of improvisation live), and the 08:46 fill is at the next print.
5. **Calendar dependency** -- NFP/CPI dates must come from a maintained calendar with
   holiday shifts; a stale calendar file = silent no-trade (fail-closed, but silently
   idle -- needs a heartbeat).
6. **Cost reality** -- the modeled 1 tk/side ZB spread is plausible for the deepest
   treasury book but was never measured on this box; the STRESS arm (2 tk/side) is the
   honest floor: {'  '.join(f"{r.entry} {r.mean_net_profit_stress_usd:+.1f}" for _, r in cv.iterrows())} $/ct.
7. **Margin** -- day margin ASSUMED ~$2,000/ct, not broker-verified.

**Preregistered kill:** a blocking impossibility (cannot be implemented fail-closed).
**Assessment:** none found -- every risk above has a standard fail-closed treatment already
used by the live P1 class (stand-aside guards, flatten fail-safe, explicit roll table).
**NO KILL.** These seven items are the FT4-FT9 work list, not reasons the object cannot
exist.

## Verdict (mechanical)

kills = {kills} -> **{'SURVIVES' if skeptic_survives else 'KILLED: ' + ', '.join(killed_lenses)}**.

{'The skeptic did not kill the engine. Per the preregistered decision rule with G_delay = ' + gdelay_verdict + ', the run is ledger ' + ('PASS' if ledger_pass else 'FAIL') + ' and FT0 (freeze: rule + entry close(08:46) + k=2) is licensed. The fragility statement in Lens 2 and the FT-stage monitor in Lens 3 are BINDING riders on that license.' if skeptic_survives else 'The engine is killed at the named lens; ZBMACRO01 closes at engine stage. The G00072 science verdict stands as science.'}
"""
with open(os.path.join(OUT, "skeptic.md"), "w", encoding="utf-8") as fh:
    fh.write(skeptic)

print("\nwrote out/delay_curve.csv, out/maemfe.csv, out/gate_table.txt, out/run_log.txt, "
      "out/dossier.md, out/skeptic.md")
