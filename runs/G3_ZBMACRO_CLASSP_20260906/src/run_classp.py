# -*- coding: utf-8 -*-
"""
G3_ZBMACRO_CLASSP_20260906 -- ledger G00078, family GENESIS3_DECISION.
EXPLORATORY Class-P pre-read for ZBMACRO01 (post-G00072 ENGINE CANDIDATE).

EVERY TABLE: EVIDENCE STATUS = DISCOVERY_CONSUMED + EXPLORATORY (a pre-read; licenses ONLY
the next research stage -- engine construction -- never deploy, never a baseline touch).

EXECUTABLE PREREGISTRATION -- ambiguity resolutions FIXED here, before results exist:

  * JOINT CALENDAR: identical to the G00072 falsifier's G9 construction -- ZB substrate
    sessions (runs/SM1M_ZB_SUBSTRATE parquet, 18:00-ET session dating) inside the P1 series'
    span; BOTH series zero-filled on no-trade days. Expected reproduction (from the G00072
    REPORT): 2022-12-27..2026-05-29, 878 sessions, 39/40 ZB trades in overlap, and the
    quoted rho_d -0.006 / rho_w +0.100 must reproduce at 3 decimals (identity clause in C0).
  * ZB leg: out/trades.csv of G00072 AS-IS (sha printed), PRIMARY cost arm
    (profit_net_primary_usd, per contract), exit-day == session_date (intraday object).
  * P1 leg: runs/WE_W56_BREADTH/out/p1_daily.csv AS-IS (sha printed). DISCLOSED: every
    Python-chain P1 figure is ~2.0% optimistic (GENESIS III double-lagged-ATR finding).
  * SCALE BASES (both always printed, labeled):
      LIVE_SCALE     = P1 x 0.30 NQ-equivalent (deployed MnqPerNq=3)  vs  ZB x k
      RESEARCH_FULL  = P1 x 1.00 NQ                                   vs  ZB x k
    for k in {1, 2, 4} ZB contracts.
  * WEEKLY GRID: calendar-week (to_period('W')) sums over the joint calendar; weekly-vol
    annualized Sharpe = mean/sd(ddof=1) * sqrt(52).
  * "losing-P1-week" = weeks with P1 weekly PnL < 0 strictly (scale-invariant set).
    Conditional ZBMACRO mean = mean of ZB weekly $ over ALL losing-P1 weeks (ZB-inactive
    weeks count as 0 -- the no-harm read); the active-only subset is ALSO printed (honesty).
  * "P1 bottom-decile days" = worst ceil(N*0.10) days of the zero-filled P1 daily series on
    the joint calendar (membership scale-invariant); table lists every such day with an
    active ZB trade.
  * TAILS: maxDD and CDaR5 on the zero-filled DAILY $ series over the joint calendar via
    research_sdk.eval_battery.max_drawdown / cdar(alpha=0.95) (CDaR5 == mean of the worst 5%
    of the drawdown path == the falsifier's "CDaR95" label; same function, stated once).
    Ratios = book / P1-alone, same basis, same calendar.
    eval_battery GUARD honored: maxDD/CDaR appear ONLY as dollar path descriptives and as
    book-vs-P1 tail RATIOS (the preregistered dollar tail check). NO fixed-DD- or
    CDaR-normalized income figure is quoted anywhere in this run, and NO trade is removed
    from any series (a leg is ADDED, never thinned), so no thinning placebo is owed.
  * ANNUAL ECONOMICS: full 40-trade ledger over the substrate session span
    (yrs = (last-first).days/365.25); the 39-trade joint-window figure also printed.
  * PROBABILITY STATEMENTS: NONE are quoted anywhere in this run -- the CAP01 two-way
    clause is satisfied on its "or none quoted" arm, printed explicitly.
  * MARGIN/CAPITAL NOTE: broker ZB day-margin figure is ASSUMED (flagged; NOT verified
    against any broker surface -- no NT8/CrossTrade call is made by this run).

DECISION RULE (mechanical, spec verbatim; evaluated at k=2 on LIVE_SCALE):
  (a) marginal weekly-vol Sharpe (book - P1-alone) > 0
  (b) maxDD ratio <= 1.02 AND CDaR5 ratio <= 1.02
  (c) losing-P1-week conditional ZBMACRO mean > -50.0 $/wk
  all three -> STACK-MEMBER (ledger PASS -> next stage: engine construction, frozen rule
  restated, eval_battery full pass, adversarial skeptic, THEN fast-track consideration).
  else -> PARK with the failed clause(s) as the reason (ledger NULL).
  C0 identity/seal failure -> DEFECT, stop.

Data seals: assert every input's max session/date < 2026-08-01 (and substrate <= 2026-07-31).
Daily per-contract math in POINTS->$ at fixed $1000/pt (DELEV01: never % on back-adjusted).
Bars END-stamped, ET sessions -- inherited from the certified substrate; no price series is
(re)built here, so no roll construction is invoked.
"""
import hashlib
import os
import sys

import numpy as np
import pandas as pd

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(RUN_DIR))
sys.path.insert(0, REPO)

from research_sdk.eval_battery import max_drawdown, cdar  # noqa: E402

TRADES_CSV = os.path.join(REPO, "runs", "G3_ZBMACRO_FALSIFIER_20260906", "out", "trades.csv")
P1_DAILY_CSV = os.path.join(REPO, "runs", "WE_W56_BREADTH", "out", "p1_daily.csv")
ZB_PARQUET = os.path.join(REPO, "runs", "SM1M_ZB_SUBSTRATE", "out", "zb_1m_2023_2026.parquet")
OUT = os.path.join(RUN_DIR, "out")
os.makedirs(OUT, exist_ok=True)

SEAL_HARD = pd.Timestamp("2026-08-01")          # never read >= this
SEAL_SUBSTRATE = pd.Timestamp("2026-07-31").date()
LIVE_P1_MULT = 0.30                              # deployed MnqPerNq=3 -> 0.30 NQ-equivalent
KS = [1, 2, 4]
ANN = np.sqrt(52.0)
EVSTAT = "DISCOVERY_CONSUMED + EXPLORATORY"
# C0 reproduction targets, from the G00072 REPORT (identity clause):
EXP_CAL = ("2022-12-27", "2026-05-29", 878, 39)
EXP_RHO_D, EXP_RHO_W = -0.006, 0.100

LINES = []
def say(s=""):
    print(s)
    LINES.append(s)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def sharpe_w(w):
    sd = float(np.std(w, ddof=1))
    return float(np.mean(w)) / sd * ANN if sd > 0 else np.nan

# ==================================================================== load + seal + identity
say("=" * 104)
say("G3_ZBMACRO_CLASSP_20260906  (ledger G00078, family GENESIS3_DECISION)")
say("EXPLORATORY Class-P pre-read for ZBMACRO01 -- is it a rational STACK MEMBER next to P1?")
say(f"EVIDENCE STATUS (every table in this run): {EVSTAT}")
say("  -> a pre-read; licenses ONLY the next research stage (engine construction); NEVER deploy.")
say("=" * 104)

tr = pd.read_csv(TRADES_CSV, parse_dates=["session_date"])
p1 = pd.read_csv(P1_DAILY_CSV, index_col=0, parse_dates=True)["p1_usd"]
say(f"input ZB ledger : {os.path.relpath(TRADES_CSV, REPO)}")
say(f"                  sha256 {sha256(TRADES_CSV)}")
say(f"                  n={len(tr)} trades {tr.session_date.min().date()}..{tr.session_date.max().date()}, "
    f"PRIMARY cost arm (comm $4.36 + 1tk/side; BASIS=MODELED ALL_IN), $ per 1 ZB contract")
say(f"input P1 daily  : {os.path.relpath(P1_DAILY_CSV, REPO)}")
say(f"                  sha256 {sha256(P1_DAILY_CSV)}")
say(f"                  n={len(p1)} days {p1.index.min().date()}..{p1.index.max().date()}, $ per 1.00 NQ")
say("                  DISCLOSED: Python-chain P1 figures are ~2.0% optimistic (double-lagged ATR,")
say("                  we_fastctx.py:81 -- GENESIS III finding); not corrected here, stated.")

assert tr.session_date.max() < SEAL_HARD, "SEAL VIOLATION: ZB ledger"
assert p1.index.max() < SEAL_HARD, "SEAL VIOLATION: P1 daily"
assert len(tr) == 40 and not tr.session_date.duplicated().any()

zbp = pd.read_parquet(ZB_PARQUET, columns=["time"])
t = pd.to_datetime(zbp["time"])
sess_date = (t.dt.normalize() + pd.to_timedelta((t.dt.hour >= 18).astype(int), unit="D")).dt.date
sessions = np.array(sorted(set(sess_date.to_numpy())))
assert sessions.max() <= SEAL_SUBSTRATE, "SEAL VIOLATION: substrate"
say(f"joint calendar  : ZB substrate sessions inside the P1 span (falsifier-G9-identical), zero-filled")

cal = pd.DatetimeIndex([pd.Timestamp(str(d)) for d in sessions])
cal = cal[(cal >= p1.index.min()) & (cal <= p1.index.max())]
zb1 = tr.set_index("session_date")["profit_net_primary_usd"]          # k=1, $/ct
p1_al = p1.reindex(cal).fillna(0.0)
zb_al = zb1.reindex(cal).fillna(0.0)
n_overlap = int((zb_al != 0).sum())
rho_d = float(np.corrcoef(p1_al, zb_al)[0, 1])
p1_wk_full = p1_al.groupby(p1_al.index.to_period("W")).sum()
zb_wk1 = zb_al.groupby(zb_al.index.to_period("W")).sum()
rho_w = float(np.corrcoef(p1_wk_full, zb_wk1)[0, 1])

c0_cal_ok = (str(cal.min().date()), str(cal.max().date()), len(cal), n_overlap) == EXP_CAL
c0_rho_ok = (round(rho_d, 3) == EXP_RHO_D) and (round(rho_w, 3) == EXP_RHO_W)
c0_pass = bool(c0_cal_ok and c0_rho_ok)
say(f"                  {cal.min().date()}..{cal.max().date()}, {len(cal)} sessions, "
    f"{n_overlap}/40 ZB trades in overlap (2026-06-05 sits outside the P1 span -- excluded, disclosed)")
say(f"                  identity: rho_d {rho_d:+.4f} rho_w {rho_w:+.4f} "
    f"(G00072 quoted {EXP_RHO_D:+.3f}/{EXP_RHO_W:+.3f}) -> {'MATCH' if c0_rho_ok else 'MISMATCH'}")
if not c0_pass:
    say("C0 FAILED -- DEFECT, stop.")

# ==================================================================== joint series artifact
js = pd.DataFrame({
    "date": cal.date,
    "p1_research_full_usd": p1_al.to_numpy(),
    "p1_live_scale_030_usd": (p1_al * LIVE_P1_MULT).to_numpy(),
    "zbmacro_k1_usd": zb_al.to_numpy(),
    "zb_active": (zb_al != 0.0).to_numpy().astype(int),
})
js["evidence_status"] = EVSTAT
js.to_csv(os.path.join(OUT, "joint_series.csv"), index=False)

# ==================================================================== per-basis / per-k table
say("")
say("=" * 104)
say(f"[T1] STACK TABLE -- all cells, both scale bases, k in {KS}   ({EVSTAT})")
say("     weekly grid: %d calendar weeks; Sharpe = mean/sd * sqrt(52); tails on DAILY $ series"
    % len(p1_wk_full))
say("     maxDD/CDaR5: dollar path descriptives + book/P1 RATIOS only; no DD-normalized income;")
say("     no trade removed anywhere -> no thinning placebo owed (eval_battery guard honored).")
rows = []
for basis, mult in (("LIVE_SCALE", LIVE_P1_MULT), ("RESEARCH_FULL", 1.0)):
    p1d = p1_al * mult
    p1w = p1_wk_full * mult
    s_p1 = sharpe_w(p1w)
    mdd_p1, cdar_p1 = max_drawdown(p1d), cdar(p1d, 0.95)
    lose = p1w < 0.0
    n_lose = int(lose.sum())
    for k in KS:
        zbd = zb_al * k
        zbw = zb_wk1 * k
        book_d = p1d + zbd
        book_w = p1w + zbw
        s_book = sharpe_w(book_w)
        marg = s_book - s_p1
        cond_all = float(zbw[lose].mean())
        act = lose & (zbw != 0.0)
        cond_act = float(zbw[act].mean()) if act.sum() else np.nan
        mdd_b, cdar_b = max_drawdown(book_d), cdar(book_d, 0.95)
        r_mdd, r_cdar = mdd_b / mdd_p1, cdar_b / cdar_p1
        rows.append(dict(
            basis=basis, p1_mult=mult, k_zb=k,
            sharpe_wk_p1_alone=round(s_p1, 4), sharpe_wk_book=round(s_book, 4),
            marginal_sharpe_wk=round(marg, 4),
            n_losing_p1_weeks=n_lose,
            zb_mean_on_losing_p1_weeks_usd=round(cond_all, 2),
            zb_mean_on_losing_p1_weeks_active_only_usd=(round(cond_act, 2) if act.sum() else np.nan),
            n_losing_p1_weeks_zb_active=int(act.sum()),
            worst_day_p1_alone_usd=round(float(p1d.min()), 2),
            worst_day_book_usd=round(float(book_d.min()), 2),
            worst_week_p1_alone_usd=round(float(p1w.min()), 2),
            worst_week_book_usd=round(float(book_w.min()), 2),
            maxdd_p1_alone_usd=round(mdd_p1, 2), maxdd_book_usd=round(mdd_b, 2),
            maxdd_ratio=round(r_mdd, 4),
            cdar5_p1_alone_usd=round(cdar_p1, 2), cdar5_book_usd=round(cdar_b, 2),
            cdar5_ratio=round(r_cdar, 4),
            zb_annual_usd_at_k=round(float(zb_al.sum()) * k
                                     / ((cal.max() - cal.min()).days / 365.25), 0),
            evidence_status=EVSTAT))
tab = pd.DataFrame(rows)
tab.to_csv(os.path.join(OUT, "classp_table.csv"), index=False)
hdr = (f"     {'basis':<15}{'k':>2}{'S_p1':>8}{'S_book':>8}{'dS':>8}{'condL$':>9}"
       f"{'wday_p1':>10}{'wday_bk':>10}{'wwk_p1':>10}{'wwk_bk':>10}{'rMDD':>8}{'rCDaR5':>8}")
say("")
say(hdr)
for _, r in tab.iterrows():
    say(f"     {r.basis:<15}{int(r.k_zb):>2}{r.sharpe_wk_p1_alone:>8.3f}{r.sharpe_wk_book:>8.3f}"
        f"{r.marginal_sharpe_wk:>+8.3f}{r.zb_mean_on_losing_p1_weeks_usd:>+9.1f}"
        f"{r.worst_day_p1_alone_usd:>10.0f}{r.worst_day_book_usd:>10.0f}"
        f"{r.worst_week_p1_alone_usd:>10.0f}{r.worst_week_book_usd:>10.0f}"
        f"{r.maxdd_ratio:>8.4f}{r.cdar5_ratio:>8.4f}")
say(f"     losing-P1 weeks: n={int(tab.n_losing_p1_weeks.iloc[0])} of {len(p1_wk_full)} "
    f"(set is scale-invariant); condL$ = ZB weekly mean over ALL those weeks (zeros kept);")
act_n = int(tab.n_losing_p1_weeks_zb_active.iloc[0])
say(f"     active-only subset: {act_n} losing-P1 weeks had a ZB trade; "
    f"active-only mean at k=1 = {tab.zb_mean_on_losing_p1_weeks_active_only_usd.iloc[0]:+.1f} $/wk")

# ==================================================================== bottom-decile day table
n_dec = int(np.ceil(len(cal) * 0.10))
order = p1_al.sort_values().index[:n_dec]
dec_thresh = float(p1_al.loc[order].max())
dec_active = [d for d in order if zb_al.loc[d] != 0.0]
say("")
say(f"[T2] P1 BOTTOM-DECILE DAYS (worst {n_dec} of {len(cal)} joint-calendar days; "
    f"threshold {dec_thresh:+.0f} $ full-scale)   ({EVSTAT})")
say(f"     ZB active on {len(dec_active)} of {n_dec} "
    f"(chance expectation ~{n_overlap * n_dec / len(cal):.1f}); those days (k=1 $/ct):")
say(f"     {'date':<12}{'P1 full $':>12}{'ZB k=1 $':>12}")
for d in sorted(dec_active):
    say(f"     {str(pd.Timestamp(d).date()):<12}{p1_al.loc[d]:>12.0f}{zb_al.loc[d]:>12.1f}")
if dec_active:
    sub = zb_al.loc[sorted(dec_active)]
    say(f"     sum {float(sub.sum()):+.1f} $, mean {float(sub.mean()):+.1f} $/ct on those days "
        f"(x k for the stack; sign is what matters at this n)")
else:
    say("     (none -- ZB never traded on a P1 bottom-decile day)")

# ==================================================================== economics + concentration
yrs_full = (tr.session_date.max() - tr.session_date.min()).days / 365.25
yrs_sub = (pd.Timestamp(str(sessions.max())) - pd.Timestamp(str(sessions.min()))).days / 365.25
tot40 = float(tr.profit_net_primary_usd.sum())
tot39 = float(zb_al.sum())
top3 = tr.profit_net_primary_usd.nlargest(3)
say("")
say(f"[T3] ANNUAL ECONOMICS + CONCENTRATION HONESTY   ({EVSTAT})")
say(f"     full ledger (40 tr): net ${tot40:,.0f} over {yrs_sub:.2f} yr substrate span = "
    f"${tot40 / yrs_sub:,.0f}/yr/ct on {40 / yrs_sub:.1f} trades/yr  -> x k: "
    + ", ".join(f"k={k}: ${tot40 / yrs_sub * k:,.0f}/yr" for k in KS))
say(f"     joint window (39 tr): net ${tot39:,.0f} over "
    f"{(cal.max() - cal.min()).days / 365.25:.2f} yr = "
    f"${tot39 / ((cal.max() - cal.min()).days / 365.25):,.0f}/yr/ct")
say(f"     EFFECTIVE N IS SMALL: ~11 trades/yr; one trade sits in the BURNED 2026-06..07 window")
say(f"     top-3 trade share of total net PnL: ${float(top3.sum()):,.0f} / ${tot40:,.0f} = "
    f"{float(top3.sum()) / tot40 * 100:.0f}%  (dates: "
    + ", ".join(str(tr.session_date.iloc[i].date()) for i in top3.index) + ")")
say(f"     -> the edge is TAIL-CARRIED (G00072 drop-k: +$91/ct at k=2, +$18 at k=5); a Class-P")
say(f"        stack read at ~11 tr/yr rests on very few observations. Stated, not hidden.")
say("")
say(f"[T4] ZB DAY-MARGIN / CAPITAL NOTE -- broker figure ASSUMED, NOT verified (flagged)")
say(f"     object is intraday-only (08:45->15:00 ET), so DAY margin binds. ASSUMED ~$2,000/ct")
say(f"     (typical retail futures day margin for ZB; CME maintenance ~$4,000-4,500/ct would")
say(f"     bind only if held past the session -- it never is). Against the ~$10.2k live account")
say(f"     (MX01-era figure, not re-read here): k=1 ~20%, k=2 ~39%, k=4 ~78% of equity tied up")
say(f"     during the 6h15m window on ~11 days/yr. k=4 is capital-implausible at current size.")
say(f"     NO probability-style statement is quoted anywhere in this run -- the CAP01 two-way")
say(f"     clause is satisfied on its 'or none quoted' arm.")

# ==================================================================== gates + decision
k2 = tab[(tab.basis == "LIVE_SCALE") & (tab.k_zb == 2)].iloc[0]
a_pass = bool(k2.marginal_sharpe_wk > 0.0)
b_pass = bool(k2.maxdd_ratio <= 1.02 and k2.cdar5_ratio <= 1.02)
c_pass = bool(k2.zb_mean_on_losing_p1_weeks_usd > -50.0)
all_cells = bool(len(tab) == 6)

gates = [
    ("C0_seal_identity",
     "seals hold; joint calendar reproduces G00072-G9 (878 sess, 39/40, rho -0.006/+0.100 @3dp)",
     f"{cal.min().date()}..{cal.max().date()}, {len(cal)} sess, {n_overlap}/40, "
     f"rho_d {rho_d:+.4f} rho_w {rho_w:+.4f}", c0_pass),
    ("CP_a_marginal_sharpe",
     "k=2 LIVE_SCALE: marginal weekly-vol Sharpe (book - P1-alone) > 0",
     f"S_book {k2.sharpe_wk_book:.4f} - S_p1 {k2.sharpe_wk_p1_alone:.4f} = "
     f"{k2.marginal_sharpe_wk:+.4f}", a_pass),
    ("CP_b_tail_ratios",
     "k=2 LIVE_SCALE: maxDD ratio <= 1.02 AND CDaR5 ratio <= 1.02",
     f"maxDD {k2.maxdd_ratio:.4f} (${k2.maxdd_p1_alone_usd:,.0f}->${k2.maxdd_book_usd:,.0f}); "
     f"CDaR5 {k2.cdar5_ratio:.4f} (${k2.cdar5_p1_alone_usd:,.0f}->${k2.cdar5_book_usd:,.0f})",
     b_pass),
    ("CP_c_no_harm",
     "k=2 LIVE_SCALE: losing-P1-week conditional ZB mean > -50 $/wk",
     f"{k2.zb_mean_on_losing_p1_weeks_usd:+.2f} $/wk over {int(k2.n_losing_p1_weeks)} losing weeks",
     c_pass),
    ("R_all_cells",
     "all 6 basis x k cells + decile table + concentration + margin note printed",
     f"{len(tab)}/6 cells; T2 {len(dec_active)} rows; T3/T4 printed", all_cells),
    ("R_probability_clause",
     "any probability-style statement computed 2 ways, OR none quoted",
     "none quoted (stated in T4)", True),
]
say("")
say("=" * 104)
say(f"GATE TABLE (program-printed; {EVSTAT})")
say(f"{'GATE':<24}{'SPEC':<66}{'PASS/FAIL':>10}")
say("-" * 104)
for g, spec, obs, ok in gates:
    say(f"{g:<24}{spec:<66}{'PASS' if ok else 'FAIL':>10}")
    say(f"{'':<24}OBSERVED: {obs}")
say("-" * 104)

if not c0_pass:
    verdict, ledger = "DEFECT (C0 identity/seal failed -- results not interpretable)", "DEFECT"
else:
    stack = a_pass and b_pass and c_pass
    if stack:
        verdict = ("STACK-MEMBER -- next stage licensed: ZBMACRO01 engine construction "
                   "(frozen rule restated, eval_battery full pass, adversarial skeptic, "
                   "THEN fast-track consideration). NOT a deploy decision.")
        ledger = "PASS"
    else:
        fails = [n for n, ok in (("a_marginal_sharpe", a_pass), ("b_tail_ratios", b_pass),
                                 ("c_no_harm", c_pass)) if not ok]
        verdict = "PARK -- failed clause(s) at k=2 LIVE_SCALE: " + ", ".join(fails)
        ledger = "NULL"
say(f"DECISION (mechanical): {verdict}")
say(f"LEDGER G00078 RESULT: {ledger}")
say("=" * 104)

with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(LINES) + "\n")
with open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(LINES) + "\n")
print("\nwrote out/joint_series.csv, out/classp_table.csv, out/gate_table.txt, out/run_log.txt")
