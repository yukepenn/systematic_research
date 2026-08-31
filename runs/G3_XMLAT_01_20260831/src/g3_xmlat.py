"""G3_XMLAT_01_20260831 - XM_CONFLICT LATENCY FORENSICS.

Executes runs/G3_XMLAT_01_20260831/spec.yaml, gate for gate. Every number in the report is
printed by THIS program; nothing is assembled by hand.

PROHIBITIONS HONOURED (spec section 4, and the task instruction):
  * no order / deploy / enable / disable / backtest / CrossTrade call of any kind is made
  * no file in research/weekly_edge/src/ and no .cs file is written
  * no session at or after 2026-08-01 is read (asserted at load, and again per store)
  * the best-performing delay is NOT adopted; X2 is a diagnostic surface

RUN ORDER: X0 first. If X0 fails the premise is withdrawn, X1-X5 are VOID and are not printed.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import xm_core as XC                                                     # noqa: E402
import tick_lab as TL                                                    # noqa: E402
from xm_core import PV, ENTRY_FILLS, EXIT_FILLS                          # noqa: E402

RUN = os.path.dirname(HERE)
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

# =============================================================================================
# PRE-DECLARED CONSTANTS. Every one is a fact about the PRIOR work, fixed before this run
# computed anything, with its provenance beside it.
# =============================================================================================
PRIOR = dict(
    entry_wk=-74.18, entry_se=28.24, entry_t=-2.63,
    exit_wk=-11.43, exit_se=13.54, exit_t=-0.84,
    both_wk=-85.61, both_se=31.49, both_t=-2.72,
    per_trade=-45.66, total=-15800.0, trades=346, weeks=213)
# provenance: runs/XM_EXEC_COST_AUDIT_V1_20260831/out/addendum2.txt Y9 (lines 22-26) and Y10,
# produced by that run's src/xm_exec_addendum2.py with A=2022-07-01, B=2026-08-01.

# THE POPULATION THE PRIOR FIGURE WAS ACTUALLY MEASURED ON. Declared here, before X0 runs,
# because the G3 spec's section 0 misstates it as "378 trades over ~243 weeks" - 378 is the
# NT8 backtest's own longer window (2022-01-03..2026-08-30), not the measurement's population.
SOURCE_WINDOW = ("2022-07-01", "2026-08-01")     # 346 trades / 213 ISO weeks
SPEC_WINDOW = ("2022-01-03", "2026-08-01")       # the task's hard-rule study window

# X0 is gated on the SOURCE window, because "reproduce the premise" means reproduce the
# measurement that was made. The SPEC window is printed beside it and is the population for
# X1-X5, as the task's hard rules require.
X0_GATE_WINDOW = "SOURCE"
X0_TOL = 0.15

# XM's currently quoted contribution, for the verdict rule. All three are printed; the primary
# is the deployed-object standalone figure, because that is the object this run rebuilds.
XM_QUOTED_STANDALONE = 936.32   # XM_EXEC_COST_AUDIT_V1_20260831/out/gate_table.txt:21
XM_QUOTED_VECTORISED = 915.51   # research/genesis2/MASTER_SCOREBOARD.md:14 (348-trade variant)
XM_QUOTED_MARGINAL = 763.0      # research/weekly_edge/CURRENT_BASELINE.md, FULL-window causal

COST_STRESS = [4.36, 16.86, 24.00, 30.00]        # spec X4
MODELLED_SPREAD_RT = 12.50                       # CLAUDE.md section 6; CURRENT_BASELINE.md:32
BOOT_B = 20000
BOOT_MEAN_BLOCK = 4.0
BOOT_SEED = 20260831
RETAIL_LATENCY_S = 0.250                         # spec X5 component E
BEYOND_LATENCY_S = 1.0                           # spec X5 component A
UNDERPOWER_N = 20                                # spec X3 MANDATORY_REPORTING

GATES = []
RESULT = {}


# =============================================================================================
class Tee:
    def __init__(self, path):
        self.f = open(path, "w", encoding="utf-8")
        self.stdout = sys.stdout

    def write(self, s):
        self.stdout.write(s)
        self.f.write(s)

    def flush(self):
        self.stdout.flush()
        self.f.flush()


def hr(c="=", n=110):
    print(c * n)


def head(title):
    print()
    hr()
    print(title)
    hr()


def gate(name, spec_txt, obs_txt, passed):
    GATES.append(dict(gate=name, spec=spec_txt, observed=obs_txt,
                      verdict="PASS" if passed else "FAIL"))
    return passed


# =============================================================================================
def stationary_bootstrap(x, mean_block=BOOT_MEAN_BLOCK, B=BOOT_B, seed=BOOT_SEED):
    """Politis-Romano stationary bootstrap of the MEAN. THIS is the test; t is a diagnostic."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 3:
        return dict(p=np.nan, lo=np.nan, hi=np.nan, B=B, n=n, mean_block=mean_block)
    rng = np.random.default_rng(seed)
    p_new = 1.0 / mean_block
    starts = rng.integers(0, n, size=(B, n))
    newb = rng.random((B, n)) < p_new
    idx = np.empty((B, n), dtype=np.int64)
    idx[:, 0] = starts[:, 0]
    for t in range(1, n):
        idx[:, t] = np.where(newb[:, t], starts[:, t], (idx[:, t - 1] + 1) % n)
    means = x[idx].mean(axis=1)
    xb = x.mean()
    p = float((np.abs(means - xb) >= abs(xb)).mean())
    return dict(p=p, lo=float(np.percentile(means, 2.5)), hi=float(np.percentile(means, 97.5)),
                B=B, n=n, mean_block=mean_block, boot_sd=float(means.std(ddof=1)))


def tstat(x):
    x = np.asarray(x, dtype=float)
    if len(x) < 2 or x.std(ddof=1) == 0:
        return np.nan, np.nan
    se = x.std(ddof=1) / np.sqrt(len(x))
    return float(x.mean() / se), float(se)


def weekly_series(D, sessions, pnl, weeks_order):
    wmap = {w: i for i, w in enumerate(weeks_order)}
    sd = pd.to_datetime(D["sess_date"])
    out = np.zeros(len(weeks_order))
    for s, p in zip(sessions, pnl):
        iso = sd[int(s)].isocalendar()
        out[wmap[f"{iso[0]}-W{iso[1]:02d}"]] += p
    return out


# =============================================================================================
def common_armed_set(DEC, entry_keys, exit_keys):
    """THE SURVIVORSHIP RULE (spec trap 4): ONE armed set, used at EVERY delay."""
    sess = np.flatnonzero(DEC["desired"] != 0)
    ok = np.ones(len(sess), bool)
    for k in entry_keys:
        ok &= np.isfinite(DEC["E_" + k][sess])
    for k in exit_keys:
        ok &= np.isfinite(DEC["X_" + k][sess])
    return sess[ok], sess[~ok]


# =============================================================================================
def gate_X0(D):
    head("GATE X0 - REPRODUCE THE PREMISE  (if this fails, X1-X5 are VOID and are not printed)")
    print("  The prior claim, verbatim from runs/XM_EXEC_COST_AUDIT_V1_20260831/out/addendum2.txt")
    print("  section Y9:  entry +1 min  -$74.18/wk (SE $28.24, t -2.63, total -$15,800)")
    print("               exit  +1 min  -$11.43/wk (SE $13.54, t -0.84, total  -$2,435)")
    print("               both  +1 min  -$85.61/wk (SE $31.49, t -2.72)")
    print("               per trade     -$45.66    on 346 trades / 213 ISO weeks")
    print()
    print("  ⚠ POPULATION CORRECTION, stated BEFORE the reproduction: this run's own spec.yaml")
    print("    section 0 attributes the figure to '378 trades x $45.66' and section 3 to")
    print("    'n=378 trades over ~243 weeks'. That is wrong. 378 is the NT8 backtest's trade")
    print("    count over ITS longer window (2022-01-03..2026-08-30, commission-only). The")
    print("    measurement was made on 346 trades / 213 ISO weeks over 2022-07-01..2026-08-01.")
    print("    $74.18 x 213 = $15,800 and $15,800 / 346 = $45.66 - the arithmetic closes only")
    print("    on the 346/213 population. X0 is therefore GATED ON THAT POPULATION, and the")
    print("    task's wider 2022-01-03 study window is printed beside it and used for X1-X5.")
    print()
    print("  NOTE the delay delta is COST-INVARIANT: only the entry price moves, so the charged")
    print("  round-turn cost cancels in the difference. No cost-model choice can move X0.")
    print()

    cost = XC.cost_per_rt()
    out = {}
    for wname, (lo, hi) in (("SOURCE", SOURCE_WINDOW), ("SPEC", SPEC_WINDOW)):
        DEC = XC.build_decisions(D, lo, hi)
        weeks, _ = XC.week_index(D, DEC["win"])
        # ONE population, shared by every arm (survivorship rule)
        sess, drop = common_armed_set(DEC, ["open_0946", "open_0947"],
                                      ["open_1546", "open_1547"])
        d = DEC["desired"][sess].astype(float)
        e0, e1 = DEC["E_open_0946"][sess], DEC["E_open_0947"][sess]
        x0, x1 = DEC["X_open_1546"][sess], DEC["X_open_1547"][sess]
        P = dict(base=d * (x0 - e0) * PV - cost,
                 ent1=d * (x0 - e1) * PV - cost,
                 ext1=d * (x1 - e0) * PV - cost,
                 both=d * (x1 - e1) * PV - cost)
        base = P["base"]
        W = {k: weekly_series(D, sess, v, weeks) for k, v in P.items()}
        r = dict(window=f"{lo}..{hi}", weeks=len(weeks), trades=int(len(sess)),
                 dropped=int(len(drop)),
                 base_wk=float(W["base"].mean()), base_total=float(base.sum()),
                 base_per_trade=float(base.mean()))
        for k, lab in (("ent1", "entry"), ("ext1", "exit"), ("both", "both")):
            dw = W[k] - W["base"]
            t_, se_ = tstat(dw)
            bs = stationary_bootstrap(dw)
            r[lab] = dict(wk=float(dw.mean()), se=se_, t=t_, total=float(dw.sum()),
                          per_trade=float((P[k] - base).mean()),
                          boot_p=bs["p"], boot_lo=bs["lo"], boot_hi=bs["hi"])
        out[wname] = r

    for wname in ("SOURCE", "SPEC"):
        r = out[wname]
        print(f"  {wname:<7s} window {r['window']}   {r['trades']} trades / {r['weeks']} ISO "
              f"weeks   (dropped for a missing +1-min bar: {r['dropped']})")
        print(f"          incumbent net  ${r['base_wk']:>8.2f}/wk   "
              f"${r['base_per_trade']:>8.2f}/trade   total ${r['base_total']:>12,.2f}")
        for lab in ("entry", "exit", "both"):
            v = r[lab]
            print(f"          {lab:<5s} +1 min  ${v['wk']:>8.2f}/wk  (SE ${v['se']:>6.2f}, "
                  f"t {v['t']:>6.2f}, boot p {v['boot_p']:.4f}, 95% CI "
                  f"[${v['boot_lo']:>7.2f}, ${v['boot_hi']:>7.2f}])  "
                  f"total ${v['total']:>10,.0f}  ${v['per_trade']:>7.2f}/trade")
        print()

    g = out[X0_GATE_WINDOW]
    ent = g["entry"]["wk"]
    ext = g["exit"]["wk"]
    rel = abs(ent - PRIOR["entry_wk"]) / abs(PRIOR["entry_wk"])
    ok_entry = rel <= X0_TOL
    # the exit non-effect: same sign, same rough magnitude (within a factor of 3), not significant
    ok_exit = (np.sign(ext) == np.sign(PRIOR["exit_wk"])
               and (abs(ext) / abs(PRIOR["exit_wk"]) <= 3.0)
               and (abs(ext) / abs(PRIOR["exit_wk"]) >= 1 / 3.0)
               and abs(g["exit"]["t"]) < 2.0)
    print(f"  entry-delay reproduction : observed ${ent:.2f}/wk vs claimed "
          f"${PRIOR['entry_wk']:.2f}/wk -> {100*rel:.2f} % deviation "
          f"(tolerance {100*X0_TOL:.0f} %)")
    print(f"  exit-side non-effect     : observed ${ext:.2f}/wk (t {g['exit']['t']:.2f}) vs "
          f"claimed ${PRIOR['exit_wk']:.2f}/wk (t {PRIOR['exit_t']:.2f}) -> sign "
          f"{'MATCHES' if np.sign(ext)==np.sign(PRIOR['exit_wk']) else 'DIFFERS'}, "
          f"magnitude ratio {abs(ext)/abs(PRIOR['exit_wk']):.2f}x, "
          f"{'not significant' if abs(g['exit']['t'])<2 else 'SIGNIFICANT'}")
    passed = gate("X0", f"entry-delay within +/-{100*X0_TOL:.0f} % of ${PRIOR['entry_wk']:.2f}/wk "
                        f"AND exit non-effect reproduces in sign and rough magnitude",
                  f"entry ${ent:.2f}/wk ({100*rel:.1f} % dev); exit ${ext:.2f}/wk (t "
                  f"{g['exit']['t']:.2f})", ok_entry and ok_exit)
    print(f"\n  ==> X0 {'PASS' if passed else 'FAIL'}")
    RESULT["X0"] = out
    return passed, out


# =============================================================================================
def gate_X1(D):
    head("GATE X1 - TWO-SIDED CAUSALITY")
    lo, hi = SPEC_WINDOW
    DEC = XC.build_decisions(D, lo, hi)
    win = DEC["win"]
    nwin = int(win.sum())

    print("  X1-NEGATIVE  every NQ/ES/RTY/YM price from the bar stamped 09:46 ONWARD is replaced")
    print("               by volatility-matched white noise, on EVERY session. The decision")
    print("               series must be BIT-IDENTICAL. Finiteness structure is preserved, so a")
    print("               `take` mask cannot move for a reason other than a genuine leak.")
    Dc, n_corr = XC.corrupt_after_decision(D)
    DECc = XC.build_decisions(Dc, lo, hi)
    ident = {}
    for key, lab in (("drive", "nq_drive"), ("conflict", "conflict_flag"),
                     ("desired", "desired_direction")):
        a, b = DEC[key][win], DECc[key][win]
        ident[lab] = float((a == b).mean() * 100.0)
    a, b = DEC["comp"][win], DECc["comp"][win]
    same = ((a == b) | (~np.isfinite(a) & ~np.isfinite(b)))
    ident["broad_composite"] = float(same.mean() * 100.0)
    fin = np.isfinite(a) & np.isfinite(b)
    maxd = float(np.abs(a[fin] - b[fin]).max()) if fin.any() else 0.0
    for k, v in ident.items():
        print(f"      {k:<20s} identical on {v:8.4f} % of {nwin:,} in-window sessions")
    print(f"      broad_composite max |diff| over sessions where both are finite: {maxd:.3e}")
    # the corruption must actually have bitten somewhere, or the probe is a no-op
    ep = DEC["E_open_0946"][win]
    epc = DECc["E_open_0946"][win]
    fine = np.isfinite(ep) & np.isfinite(epc)
    moved = float((ep[fine] != epc[fine]).mean() * 100.0)
    print(f"      SANITY: the post-cutoff ENTRY price open(09:46) changed on {moved:.2f} % of "
          f"sessions - the corruption is real, not a no-op")
    neg_ok = all(v == 100.0 for v in ident.values()) and moved > 99.0

    print()
    print("  X1-POSITIVE  the ES/RTY/YM close at the 09:45 bar is perturbed by +/-0.5 sigma of")
    print("               that market's own 60-session sigma, ONE MARKET AT A TIME, one session")
    print("               at a time (the sigma HISTORY is left untouched, so the probe measures")
    print("               the action's sensitivity and not a propagating cascade).")
    idx = np.flatnonzero(win)
    comp, drive, cnt = DEC["comp"], DEC["drive"], DEC["cnt_of"]
    des = DEC["desired"]
    take_ok = np.isfinite(DEC["E_open_0946"]) & np.isfinite(DEC["X_close_1545"]) \
        & np.isfinite(DEC["X_open_1546"])
    computable = idx[np.isfinite(comp[idx]) & (cnt[idx] > 0)]
    armed = idx[des[idx] != 0]
    per_market = {}
    flip_any = np.zeros(len(computable), bool)
    for k in XC.XM_PATHS:
        fk = np.zeros(len(computable), bool)
        for sgn in (+1.0, -1.0):
            for j, s in enumerate(computable):
                sg = DEC["sg_of"][k][s]
                if not np.isfinite(sg):
                    continue                       # this market did not contribute today
                r_old = DEC["r_of"][k][s]
                px = D["XD"][k][DEC["idc"][s]] * np.exp(sgn * 0.5 * sg)
                r_new = np.log(px / D["XD"][k][DEC["ia"][s]])
                comp2 = comp[s] + (r_new - r_old) / sg / cnt[s]
                xs = np.sign(comp2)
                d2 = int(drive[s]) if (xs != 0 and drive[s] != 0 and xs != drive[s]) else 0
                if not take_ok[s]:
                    d2 = 0
                if d2 != des[s]:
                    fk[j] = True
        per_market[k] = float(fk.mean() * 100.0)
        flip_any |= fk
    frac_any = float(flip_any.mean() * 100.0)
    frac_all_win = float(flip_any.sum() / nwin * 100.0)
    frac_armed = float(flip_any[np.isin(computable, armed)].mean() * 100.0) \
        if len(armed) else np.nan
    for k, v in per_market.items():
        print(f"      {k:<4s} alone flips desired_direction on {v:6.2f} % of "
              f"{len(computable):,} sessions with a computable composite")
    print(f"      ANY single-market perturbation flips it on {frac_any:.2f} % "
          f"({int(flip_any.sum())} / {len(computable):,})")
    print(f"        same count against ALL {nwin:,} in-window sessions: {frac_all_win:.2f} %")
    print(f"        restricted to the {len(armed)} ARMED sessions:      {frac_armed:.2f} %")
    pos_ok = frac_any >= 5.0

    gate("X1-NEG", "decision series BIT-IDENTICAL on 100 % of sessions under post-09:45:00 "
                   "corruption",
         "; ".join(f"{k} {v:.4f} %" for k, v in ident.items()) +
         f"; entry price moved on {moved:.1f} % (probe is live)", neg_ok)
    gate("X1-POS", ">= 5 % of sessions flip desired_direction under at least one single-market "
                   "+/-0.5 sigma perturbation",
         f"{frac_any:.2f} % of {len(computable):,} computable sessions "
         f"(ES {per_market['ES']:.2f} %, RTY {per_market['RTY']:.2f} %, "
         f"YM {per_market['YM']:.2f} %)", pos_ok)
    print(f"\n  ==> X1-NEGATIVE {'PASS' if neg_ok else 'FAIL'}   "
          f"X1-POSITIVE {'PASS' if pos_ok else 'FAIL'}")
    RESULT["X1"] = dict(negative=ident, negative_entry_price_moved_pct=moved,
                        positive_per_market=per_market, positive_any_pct=frac_any,
                        positive_n=int(len(computable)), positive_armed_pct=frac_armed,
                        corrupted_bars=int(n_corr))
    return neg_ok and pos_ok, DEC


# =============================================================================================
def gate_X2(D, DEC):
    head("GATE X2 - THE 1-MINUTE EXECUTION DECAY CURVE  (DIAGNOSTIC. No delay is adopted.)")
    cost = XC.cost_per_rt()
    weeks, _ = XC.week_index(D, DEC["win"])
    ekeys = [k for k, _, _, _ in ENTRY_FILLS]
    sess, drop = common_armed_set(DEC, ekeys, ["open_1546"])
    print(f"  ONE armed set, fixed at every delay (spec trap 4): {len(sess)} trades over "
          f"{len(weeks)} ISO weeks.")
    print(f"  Dropped because at least one fill bar in the ladder does not exist: {len(drop)} "
          f"session(s).")
    if len(drop):
        sd = pd.to_datetime(D["sess_date"])
        print("    " + ", ".join(sd[int(s)].strftime("%Y-%m-%d") for s in drop))
    print(f"  Charged cost is HELD CONSTANT at ${cost:.2f}/ctrRT at every delay, so the curve is")
    print(f"  the price effect alone. (The delta is cost-invariant in any case.)")
    c46 = DEC["E_close_0946"][np.flatnonzero(DEC["desired"] != 0)]
    o47 = DEC["E_open_0947"][np.flatnonzero(DEC["desired"] != 0)]
    fin = np.isfinite(c46) & np.isfinite(o47)
    print(f"  The '+59 s' point is close(09:46) and the '+60 s' point is open(09:47). In this")
    print(f"  substrate they are DISTINCT prices on {100*(c46[fin]!=o47[fin]).mean():.1f} % of the "
          f"armed sessions, so the two rows are")
    print(f"  genuinely two measurements and not one printed twice.")
    print()
    d = DEC["desired"][sess].astype(float)
    xp = DEC["X_open_1546"][sess]
    sd = pd.to_datetime(D["sess_date"])
    years = np.array([sd[int(s)].year for s in sess])

    pnl = {}
    for lab, _, _, _ in ENTRY_FILLS:
        pnl[lab] = d * (xp - DEC["E_" + lab][sess]) * PV - cost
    # worst / best case within the 09:46 minute, signed by direction
    worst = np.where(d > 0, DEC["E_high_0946"][sess], DEC["E_low_0946"][sess])
    best = np.where(d > 0, DEC["E_low_0946"][sess], DEC["E_high_0946"][sess])
    pnl["WORST_in_0946"] = d * (xp - worst) * PV - cost
    pnl["BEST_in_0946"] = d * (xp - best) * PV - cost
    del pnl["high_0946"], pnl["low_0946"]

    base = pnl["open_0946"]
    Wb = weekly_series(D, sess, base, weeks)
    delay_of = {lab: dl for lab, _, _, dl in ENTRY_FILLS}
    delay_of["WORST_in_0946"] = np.nan
    delay_of["BEST_in_0946"] = np.nan

    order = ["open_0946", "close_0946", "open_0947", "open_0948", "open_0950",
             "WORST_in_0946", "BEST_in_0946"]
    rows = []
    print(f"  {'fill':<16s}{'delay':>7s}{'net/wk':>10s}{'$/trade':>10s}{'wkSD':>9s}"
          f"{'d$/wk':>9s}{'t(diff)':>9s}{'bootP':>8s}{'95% CI on d$/wk':>24s}")
    hr("-")
    for lab in order:
        Wv = weekly_series(D, sess, pnl[lab], weeks)
        dw = Wv - Wb
        t_, se_ = tstat(dw)
        bs = stationary_bootstrap(dw) if lab != "open_0946" else dict(p=np.nan, lo=0.0, hi=0.0)
        dl = delay_of[lab]
        rows.append(dict(fill=lab, delay_s=dl, net_wk=float(Wv.mean()),
                         per_trade=float(pnl[lab].mean()), wk_sd=float(Wv.std(ddof=1)),
                         d_wk=float(dw.mean()), d_per_trade=float((pnl[lab] - base).mean()),
                         t_diff=t_, se_diff=se_, boot_p=bs["p"], ci_lo=bs["lo"], ci_hi=bs["hi"],
                         n=len(sess)))
        is_inc = lab == "open_0946"
        ci = "" if is_inc else "[{:>8.2f},{:>8.2f}]".format(bs["lo"], bs["hi"])
        c_dl = "" if not np.isfinite(dl) else "{:>6.0f}s".format(dl)
        c_t = "" if is_inc else "{:>9.2f}".format(t_)
        c_p = "" if is_inc else "{:>8.4f}".format(bs["p"])
        print(f"  {lab:<16s}{c_dl:>7s}"
              f"{Wv.mean():>10.2f}{pnl[lab].mean():>10.2f}{Wv.std(ddof=1):>9.2f}"
              f"{dw.mean():>9.2f}{c_t:>9s}{c_p:>8s}{ci:>24s}")

    # ---- LONG / SHORT split
    print()
    print("  BY SIDE (net/week is on the SAME balanced weekly panel; the side's trades only)")
    print(f"  {'fill':<16s}{'LONG n':>8s}{'LONG $/tr':>11s}{'LONG d$/wk':>12s}"
          f"{'SHORT n':>9s}{'SHORT $/tr':>12s}{'SHORT d$/wk':>13s}")
    hr("-")
    side_rows = []
    for lab in order:
        rec = dict(fill=lab)
        cells = []
        for nm, m in (("LONG", d > 0), ("SHORT", d < 0)):
            Wv = weekly_series(D, sess[m], pnl[lab][m], weeks)
            Wb2 = weekly_series(D, sess[m], base[m], weeks)
            rec[nm + "_n"] = int(m.sum())
            rec[nm + "_per_trade"] = float(pnl[lab][m].mean())
            rec[nm + "_d_wk"] = float((Wv - Wb2).mean())
            cells.append((int(m.sum()), pnl[lab][m].mean(), (Wv - Wb2).mean()))
        side_rows.append(rec)
        print(f"  {lab:<16s}{cells[0][0]:>8d}{cells[0][1]:>11.2f}{cells[0][2]:>12.2f}"
              f"{cells[1][0]:>9d}{cells[1][1]:>12.2f}{cells[1][2]:>13.2f}")

    # ---- calendar-year split
    print()
    print("  BY CALENDAR YEAR - d$/trade vs the incumbent fill (negative = the delay costs)")
    ys = sorted(set(years.tolist()))
    print(f"  {'fill':<16s}" + "".join(f"{y:>12d}" for y in ys))
    hr("-")
    year_rows = []
    for lab in order:
        rec = dict(fill=lab)
        line = f"  {lab:<16s}"
        for y in ys:
            m = years == y
            v = float((pnl[lab][m] - base[m]).mean()) if m.any() else np.nan
            rec[str(y)] = v
            line += f"{v:>12.2f}"
        year_rows.append(rec)
        print(line)
    print(f"  {'n trades':<16s}" + "".join(f"{int((years==y).sum()):>12d}" for y in ys))

    # ---- slope and break-even latency
    print()
    fit_labs = ["open_0946", "close_0946", "open_0947", "open_0948", "open_0950"]
    xs = np.array([delay_of[l] for l in fit_labs], dtype=float)
    ys_ = np.array([float(pnl[l].mean()) for l in fit_labs])
    A_ = np.vstack([xs, np.ones_like(xs)]).T
    slope, icpt = np.linalg.lstsq(A_, ys_, rcond=None)[0]
    first_min = (float(pnl["open_0947"].mean()) - float(base.mean())) / 60.0
    inc_pt = float(base.mean())
    be_fit = inc_pt / abs(slope) if slope < 0 else np.inf
    be_1min = inc_pt / abs(first_min) if first_min < 0 else np.inf
    print(f"  DECAY SLOPE (OLS on $/trade over the 0..240 s ladder)  "
          f"{slope:+.4f} $/trade/second   (intercept ${icpt:.2f})")
    print(f"  FIRST-MINUTE slope (0 -> 60 s only)                    "
          f"{first_min:+.4f} $/trade/second")
    print(f"  incumbent after-cost edge                              ${inc_pt:.2f}/trade")
    print(f"  BREAK-EVEN LATENCY, linear fit over 0-240 s            "
          f"{be_fit:,.0f} s  ({be_fit/60:,.1f} min)")
    print(f"  BREAK-EVEN LATENCY, first-minute slope                 "
          f"{be_1min:,.0f} s  ({be_1min/60:,.1f} min)")
    print("  ⚠ Both extrapolate a slope fitted inside four minutes to a horizon of hours. The")
    print("    ladder itself is NOT monotone (see the table), so the linear slope is a summary")
    print("    of a noisy surface, not a law. The sub-second break-even in X3 is the one that")
    print("    bears on deployment.")

    pd.DataFrame(rows).to_csv(os.path.join(OUT, "decay_1min.csv"), index=False)
    pd.DataFrame(side_rows).to_csv(os.path.join(OUT, "decay_1min_by_side.csv"), index=False)
    pd.DataFrame(year_rows).to_csv(os.path.join(OUT, "decay_1min_by_year.csv"), index=False)
    print(f"\n  wrote out/decay_1min.csv, out/decay_1min_by_side.csv, out/decay_1min_by_year.csv")

    # ---- the exit-side ladder, for the record
    print()
    print("  EXIT-SIDE LADDER (entry held at open(09:46)) - d$/wk vs the incumbent exit")
    xkeys = [k for k, _, _, _ in EXIT_FILLS]
    sess2, drop2 = common_armed_set(DEC, ["open_0946"], xkeys)
    d2 = DEC["desired"][sess2].astype(float)
    e2 = DEC["E_open_0946"][sess2]
    b2 = d2 * (DEC["X_open_1546"][sess2] - e2) * PV - cost
    Wb2 = weekly_series(D, sess2, b2, weeks)
    print(f"    common exit set {len(sess2)} trades (dropped {len(drop2)})")
    exit_rows = []
    for lab, _, _, dl in EXIT_FILLS:
        p2 = d2 * (DEC["X_" + lab][sess2] - e2) * PV - cost
        dw = weekly_series(D, sess2, p2, weeks) - Wb2
        t_, _ = tstat(dw)
        exit_rows.append(dict(fill=lab, delay_s=dl, net_wk=float((Wb2 + dw).mean()),
                              d_wk=float(dw.mean()), t_diff=t_,
                              per_trade=float(p2.mean()), n=len(sess2)))
        print(f"    {lab:<14s} delay {dl:>5.0f}s   net ${(Wb2+dw).mean():>8.2f}/wk   "
              f"d ${dw.mean():>8.2f}/wk   t {t_:>6.2f}   ${p2.mean():>8.2f}/trade")
    pd.DataFrame(exit_rows).to_csv(os.path.join(OUT, "decay_1min_exit.csv"), index=False)

    RESULT["X2"] = dict(rows=rows, by_side=side_rows, by_year=year_rows, exit=exit_rows,
                        slope_per_sec=float(slope), first_minute_slope=float(first_min),
                        incumbent_per_trade=inc_pt, breakeven_s_fit=float(be_fit),
                        breakeven_s_first_minute=float(be_1min),
                        n_trades=int(len(sess)), n_weeks=len(weeks),
                        dropped=int(len(drop)), cost_per_rt=cost)
    gate("X2", "print the whole predefined fill surface on ONE fixed armed set; derive slope and "
               "break-even latency; adopt nothing",
         f"7 fills x {len(sess)} trades on one armed set; slope {slope:+.4f} $/trade/s; "
         f"break-even {be_fit/60:,.1f} min (linear fit); NO delay adopted", True)
    return rows


# =============================================================================================
def gate_X3(D, DEC):
    head("GATE X3 - SUB-SECOND DECAY  (the only tick+BBO sessions this repository owns)")
    sess_tk, log = TL.index_tick_sessions(verbose=True)
    dates = sorted(sess_tk)

    sd = pd.to_datetime(D["sess_date"])
    dir_by_date, sess_by_date = {}, {}
    for s in np.flatnonzero(DEC["desired"] != 0):
        dir_by_date[sd[int(s)].normalize()] = int(DEC["desired"][s])
        sess_by_date[sd[int(s)].normalize()] = int(s)
    cond_dates = [d for d in dates if d in dir_by_date]

    # ---- the extraction-ceiling arithmetic the owner asked for
    cen = pd.read_csv(os.path.join(XC.ROOT, "research", "data", "NT8_CAPABILITY_CENSUS.csv"))
    ct = cen[(cen.kind == "tick") & (cen.root == "NQ") & (cen.payload_class == "PAYLOAD")].copy()
    ct["d"] = pd.to_datetime(ct.date.astype("Int64").astype(str), format="%Y%m%d")
    grp = ct.groupby("d")["series"].apply(set)
    full = grp[grp.apply(lambda s: {"Last", "Bid", "Ask"} <= s)]
    preseal = set(full.index[full.index < pd.Timestamp("2026-08-01")])
    owned_cond = preseal & set(dir_by_date)
    extra = owned_cond - set(dates)
    print()
    print("  ---- OWNED vs EXTRACTED (research/data/NT8_CAPABILITY_CENSUS.csv) ----------------")
    print(f"    NQ tick sessions with Last AND Bid AND Ask payload : {len(full)} total, "
          f"{len(preseal)} PRE-SEAL")
    print(f"    ALREADY EXTRACTED to parquet, deduplicated by date  : {len(dates)}")
    print(f"    extracted AND carrying an XM decision (X3-A n)      : {len(cond_dates)}")
    print(f"    OWNED (pre-seal BBO) AND carrying an XM decision    : {len(owned_cond)}"
          f"   <- the ceiling if the .ncd store were extracted")
    print(f"    ADDITIONAL XM-decision sessions extraction would add: {len(extra)}")
    print(f"    extracted dates absent from the .ncd BBO census     : "
          f"{sorted(x.strftime('%Y-%m-%d') for x in (set(dates) - preseal))}")
    print("    (extraction is a NinjaScript export job at $0. It is NOT attempted in this run:")
    print("     CrossTrade calls are forbidden here. This is a scoping number, not a request.)")

    # ---- measure every owned session, at the ENTRY instant and at the EXIT instant
    t0 = time.time()
    rows_e, rows_x = [], []
    for d in dates:
        df = TL.read_window(sess_tk[d]["paths"], d, "09:40:00", "09:47:30")
        m = TL.measure_session(df, d, "09:45:00.000")
        m["store"] = sess_tk[d]["store"]
        m["has_xm"] = d in dir_by_date
        m["xm_dir"] = dir_by_date.get(d, 0)
        rows_e.append(m)
        dfx = TL.read_window(sess_tk[d]["paths"], d, "15:40:00", "15:47:30")
        mx = TL.measure_session(dfx, d, "15:45:00.000")
        mx["store"] = sess_tk[d]["store"]
        mx["has_xm"] = d in dir_by_date
        rows_x.append(mx)
    E = pd.DataFrame(rows_e)
    X = pd.DataFrame(rows_x)
    print(f"\n    measured {len(E)} sessions at 09:45:00.000 and 15:45:00.000 "
          f"[{time.time()-t0:.0f}s]")

    # ------------------------------------------------------------------ B: unconditional
    print()
    print("  X3-B  UNCONDITIONAL microstructure at the decision instant. Every owned session,")
    print("        direction-free. THIS is the load-bearing quantity if A is thin.")
    hb = E[E.has_bbo]
    print(f"    sessions with a reconstructable BBO at 09:45:00.000 : {len(hb)} / {len(E)}")
    print(f"      quoted spread at the instant   median {hb.spread_ticks.median():.2f} tk  "
          f"mean {hb.spread_ticks.mean():.2f} tk  p90 {hb.spread_ticks.quantile(.9):.2f} tk")
    print(f"      1-second median spread         median "
          f"{hb.spread_ticks_med1s.median():.2f} tk  mean "
          f"{hb.spread_ticks_med1s.mean():.2f} tk  p90 "
          f"{hb.spread_ticks_med1s.quantile(.9):.2f} tk")
    print(f"      crossed fraction of the 1 s reconstruction: median "
          f"{hb.spread_crossed_frac1s.median():.3f}  - an artefact of forward-filling TWO")
    print(f"        independent 4 ms event streams against each other, NOT a crossed market.")
    print(f"      last bid update age at the instant: median {hb.bid_age_s.median()*1000:.0f} ms, "
          f"max {hb.bid_age_s.max()*1000:.0f} ms")
    hbx = X[X.has_bbo]
    print(f"    EXIT instant 15:45:00.000, {len(hbx)} sessions: spread median "
          f"{hbx.spread_ticks.median():.2f} tk (1 s median "
          f"{hbx.spread_ticks_med1s.median():.2f} tk)")
    print(f"      For comparison the COMMITTED W82 profile charges 3.0 tk at minute 586 (09:46) "
          f"and 2.0 tk at 946 (15:46).")
    print()
    print("    THE LAST-PRICE ladder and the MID ladder are BOTH printed. At 50-250 ms the")
    print("    change in the LAST price is dominated by BID-ASK BOUNCE, not by drift: the")
    print("    median |dP_last| at +50 ms below is almost exactly the median quoted spread. The")
    print("    MID column strips the bounce out and is the honest measure of how far the market")
    print("    actually moved. Confusing the two would triple the apparent latency cost.")
    print()
    print(f"    {'delay':<8s}{'n':>5s}{'mean|dLAST| tk':>16s}{'med|dLAST| tk':>15s}"
          f"{'mean|dMID| tk':>15s}{'med|dMID| tk':>14s}{'p(last moved)':>15s}"
          f"{'p90|dLAST| tk':>15s}")
    hr("-")
    unc = []
    p0 = E["px+0ms"].to_numpy()
    m0 = E["mid+0ms"].to_numpy()
    for lab in TL.DELAY_LBL[1:]:
        pd_ = E["px" + lab].to_numpy()
        md_ = E["mid" + lab].to_numpy()
        m = np.isfinite(p0) & np.isfinite(pd_)
        mm = np.isfinite(m0) & np.isfinite(md_)
        ad = np.abs(pd_[m] - p0[m])
        amd = np.abs(md_[mm] - m0[mm])
        unc.append(dict(delay=lab, n=int(m.sum()), mean_abs_tk=float(ad.mean() / XC.TICK),
                        med_abs_tk=float(np.median(ad) / XC.TICK),
                        mean_abs_usd=float(ad.mean() * PV),
                        n_mid=int(mm.sum()),
                        mean_abs_mid_tk=float(amd.mean() / XC.TICK) if mm.any() else np.nan,
                        med_abs_mid_tk=float(np.median(amd) / XC.TICK) if mm.any() else np.nan,
                        mean_abs_mid_usd=float(amd.mean() * PV) if mm.any() else np.nan,
                        p_moved=float((ad > 0).mean()),
                        p90_abs_tk=float(np.percentile(ad, 90) / XC.TICK)))
        r = unc[-1]
        print(f"    {lab:<8s}{r['n']:>5d}{r['mean_abs_tk']:>16.2f}{r['med_abs_tk']:>15.2f}"
              f"{r['mean_abs_mid_tk']:>15.2f}{r['med_abs_mid_tk']:>14.2f}"
              f"{r['p_moved']:>15.3f}{r['p90_abs_tk']:>15.2f}")

    # ------------------------------------------------------------------ A: conditional
    print()
    print("  X3-A  CONDITIONAL realised slippage, signed by the XM desired_direction.")
    print("        slippage = -dir * (P(delay) - P(+0ms)) * $20 ; NEGATIVE means the delay COST")
    print("        money. P(+0ms) is the incumbent's modelled fill: the first print at or after")
    print("        09:45:00.000.")
    C = E[E.has_xm].reset_index(drop=True)
    nA = len(C)
    print(f"        n = {nA}   ⚠ EVERY number below carries this n.")
    cond = []
    dirv = C.xm_dir.to_numpy().astype(float)
    c0 = C["px+0ms"].to_numpy()
    cm0 = C["mid+0ms"].to_numpy()
    print()
    print(f"    {'delay':<8s}{'n':>4s}{'mean slip $':>13s}{'95% CI $':>22s}{'median $':>10s}"
          f"{'mean tk':>9s}{'p(adv)':>8s}{'nMID':>6s}{'MID slip $':>12s}{'MID 95% CI':>22s}")
    hr("-")
    for lab in TL.DELAY_LBL[1:]:
        cd = C["px" + lab].to_numpy()
        cmd = C["mid" + lab].to_numpy()
        m = np.isfinite(c0) & np.isfinite(cd)
        mm = np.isfinite(cm0) & np.isfinite(cmd)
        slip = -dirv[m] * (cd[m] - c0[m]) * PV
        mslip = -dirv[mm] * (cmd[mm] - cm0[mm]) * PV
        n_, nm_ = int(m.sum()), int(mm.sum())
        mu = float(slip.mean())
        se = float(slip.std(ddof=1) / np.sqrt(n_)) if n_ > 1 else np.nan
        rng = np.random.default_rng(BOOT_SEED)
        bm = slip[rng.integers(0, n_, size=(BOOT_B, n_))].mean(axis=1)
        lo, hi = float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))
        if nm_ > 1:
            bmm = mslip[rng.integers(0, nm_, size=(BOOT_B, nm_))].mean(axis=1)
            mlo, mhi = float(np.percentile(bmm, 2.5)), float(np.percentile(bmm, 97.5))
            mmu = float(mslip.mean())
        else:
            mlo = mhi = mmu = np.nan
        cond.append(dict(delay=lab, n=n_, mean_usd=mu, se_usd=se, ci_lo=lo, ci_hi=hi,
                         median_usd=float(np.median(slip)),
                         mean_ticks=float(mu / (PV * XC.TICK)),
                         p_adverse=float((slip < 0).mean()),
                         p_moved=float((slip != 0).mean()),
                         n_mid=nm_, mid_mean_usd=mmu, mid_ci_lo=mlo, mid_ci_hi=mhi))
        r = cond[-1]
        print(f"    {lab:<8s}{n_:>4d}{mu:>13.2f}{f'[{lo:>8.2f},{hi:>8.2f}]':>22s}"
              f"{r['median_usd']:>10.2f}{r['mean_ticks']:>9.2f}{r['p_adverse']:>8.3f}"
              f"{nm_:>6d}{mmu:>12.2f}{f'[{mlo:>8.2f},{mhi:>8.2f}]':>22s}")
    print()
    print("    The MID columns are the same measurement on the bid-ask midpoint. A marketable")
    print("    order does pay the spread, but it pays it at +0 ms too - so the INCREMENTAL cost")
    print("    of latency is the MID move, and the LAST-price column mixes that with bounce.")

    # ------------------------------------------------------- C: is the tick sample typical?
    print()
    print("  X3-C  REPRESENTATIVENESS. The tick sample is not a random draw from history, so")
    print("        before anything measured on it is extrapolated to all trades, the SAME")
    print("        quantity is computed two ways on the SAME 1-minute bars: the +60 s entry")
    print("        delay, on the tick subsample and on the full trade population.")
    all_sess = np.flatnonzero(DEC["desired"] != 0)
    sub = np.array([sess_by_date[d] for d in cond_dates if d in sess_by_date])
    d_all = DEC["desired"][all_sess].astype(float)
    d_sub = DEC["desired"][sub].astype(float)
    dd_all = d_all * (DEC["E_open_0946"][all_sess] - DEC["E_open_0947"][all_sess]) * PV
    dd_sub = d_sub * (DEC["E_open_0946"][sub] - DEC["E_open_0947"][sub]) * PV
    tick60 = [c for c in cond if c["delay"] == "+60s"][0]
    print(f"    +60 s entry delay, 1-minute bars, FULL population   n={len(all_sess):>4d}   "
          f"${dd_all.mean():>9.2f}/trade")
    print(f"    +60 s entry delay, 1-minute bars, TICK subsample    n={len(sub):>4d}   "
          f"${dd_sub.mean():>9.2f}/trade")
    print(f"    +60 s entry delay, TICK measurement, same sessions  n={tick60['n']:>4d}   "
          f"${tick60['mean_usd']:>9.2f}/trade")
    ratio = dd_sub.mean() / dd_all.mean() if dd_all.mean() != 0 else np.nan
    print(f"    -> the tick subsample is {ratio:.2f}x as latency-sensitive as the full")
    print(f"       population on the IDENTICAL 1-minute measurement. Any sub-second number")
    print(f"       extrapolated from these {len(sub)} sessions to all {len(all_sess)} trades")
    print(f"       inherits that factor. X5 states it and widens its band accordingly.")
    agree = (abs(dd_sub.mean() - tick60["mean_usd"])
             / max(abs(dd_sub.mean()), abs(tick60["mean_usd"]), 1e-9))
    print(f"    -> CROSS-SOURCE CHECK: rows 2 and 3 are the same quantity computed from TWO")
    print(f"       INDEPENDENTLY BUILT STORES - the 1-minute bar substrate and the tick parquet")
    print(f"       - and they agree to {100*(1-agree):.2f} %. The tick pipeline in this run is")
    print(f"       therefore reading the same market the rest of the campaign reads.")
    cost_ = XC.cost_per_rt()
    pt_all = float((d_all * (DEC["X_open_1546"][all_sess] - DEC["E_open_0946"][all_sess]) * PV
                    - cost_).mean())
    pt_sub = float((d_sub * (DEC["X_open_1546"][sub] - DEC["E_open_0946"][sub]) * PV
                    - cost_).mean())
    print(f"    after-cost edge per trade: full population ${pt_all:.2f}, tick subsample "
          f"${pt_sub:.2f}")
    RESULT.setdefault("X3C", {}).update(
        full_pop_60s=float(dd_all.mean()), subsample_60s=float(dd_sub.mean()),
        tick_60s=float(tick60["mean_usd"]), ratio=float(ratio), n_sub=int(len(sub)),
        n_full=int(len(all_sess)), per_trade_full=pt_all, per_trade_sub=pt_sub)

    pd.DataFrame(cond).to_csv(os.path.join(OUT, "decay_subsecond.csv"), index=False)
    pd.DataFrame(unc).to_csv(os.path.join(OUT, "decay_subsecond_unconditional.csv"), index=False)
    E.to_csv(os.path.join(OUT, "tick_sessions_0945.csv"), index=False)
    X.to_csv(os.path.join(OUT, "tick_sessions_1545.csv"), index=False)
    print(f"\n  wrote out/decay_subsecond.csv, out/decay_subsecond_unconditional.csv, "
          f"out/tick_sessions_0945.csv, out/tick_sessions_1545.csv")

    underpowered = nA < UNDERPOWER_N
    print()
    if underpowered:
        print(f"  ⚠⚠ THE CONDITIONAL SUB-SECOND CURVE IS UNDERPOWERED AT n = {nA}, AND THE")
        print(f"     UNCONDITIONAL BOUND (X3-B) IS THE LOAD-BEARING QUANTITY.")
        print(f"     The reason is NOT that the data is missing. It is underpowered at n = {nA}")
        print(f"     BECAUSE ONLY {len(dates)} OF THE {len(preseal)} PRE-SEAL NQ BBO SESSIONS")
        print(f"     THIS REPOSITORY ALREADY OWNS HAVE BEEN EXTRACTED TO PARQUET. The remedy is")
        print(f"     an extraction job at $0, not a data purchase: extracting the rest would")
        print(f"     raise n from {nA} to {len(owned_cond)}.")
    else:
        print(f"  n = {nA} >= {UNDERPOWER_N}: the conditional curve is NOT underpowered by the")
        print(f"     spec's own threshold. It is still THIN and the selection caveat below binds.")
        print(f"     Extracting the rest of the .ncd store we already own would raise n from")
        print(f"     {nA} to {len(owned_cond)} at $0 - a {100*(len(owned_cond)/max(nA,1)-1):.0f} %")
        print(f"     increase, i.e. a {np.sqrt(len(owned_cond)/max(nA,1)):.2f}x narrowing of the CI.")
    print(f"  ⚠ SELECTION: these {len(dates)} sessions are NOT a random sample of history. They")
    print(f"    are what was exported, they all fall in {dates[0].date()}..{dates[-1].date()},")
    print(f"    and s20260525 is quarantined. Every sub-second number inherits that selection.")
    print(f"  ⚠ A shallow price decay does NOT prove the fill is achievable. Queue position,")
    print(f"    rejection and partial fills are separate risks measured by no price series here.")

    gate("X3-A", f"conditional sub-second slippage curve with the exact n beside every number; "
                 f"state UNDERPOWERED if n < {UNDERPOWER_N}",
         f"n = {nA} ({'UNDERPOWERED' if underpowered else 'not underpowered'}); "
         f"mean slip at 250 ms "
         f"${[c for c in cond if c['delay']=='+250ms'][0]['mean_usd']:.2f}/contract", True)
    gate("X3-B", "unconditional BBO + |price change| bound on EVERY owned tick session",
         f"{len(E)} sessions, {len(hb)} with BBO; median quoted spread "
         f"{hb.spread_ticks.median():.2f} tk; mean |dP| at 250 ms "
         f"{[u for u in unc if u['delay']=='+250ms'][0]['mean_abs_tk']:.2f} tk", True)

    RESULT["X3"] = dict(conditional=cond, unconditional=unc, n_conditional=nA,
                        n_sessions=len(E), n_with_bbo=int(len(hb)),
                        underpowered=bool(underpowered),
                        spread_med_tk_entry=float(hb.spread_ticks.median()),
                        spread_med1s_tk_entry=float(hb.spread_ticks_med1s.median()),
                        spread_med_tk_exit=float(hbx.spread_ticks.median()),
                        spread_med1s_tk_exit=float(hbx.spread_ticks_med1s.median()),
                        owned_preseal_bbo=len(preseal), extracted=len(dates),
                        owned_and_xm=len(owned_cond), extraction_would_add=len(extra),
                        first_date=str(dates[0].date()), last_date=str(dates[-1].date()),
                        exclusions=dict(
                            quarantined=[t for t, _ in log["qa_quarantined"]],
                            truncated=[t for t, r in log["sl_excluded"]
                                       if r.startswith("TRUNCATED")]))
    return cond, unc, E, X, sess_tk, dir_by_date, cond_dates


# =============================================================================================
def gate_X4(D, DEC, sess_tk, dir_by_date, cond_dates):
    head("GATE X4 - SIGNAL vs EXECUTION SEPARATION")
    weeks, _ = XC.week_index(D, DEC["win"])
    sess, drop = common_armed_set(DEC, ["open_0946"], ["open_1546"])
    d = DEC["desired"][sess].astype(float)
    e = DEC["E_open_0946"][sess]
    x = DEC["X_open_1546"][sess]
    gross = d * (x - e) * PV
    print("  COST STRESS - the ACTION PATH IS HELD FIXED. Identical entries, identical exits,")
    print("  identical sizes. Only the charged round-turn cost varies.")
    print()
    print(f"    {'cost/ctrRT':>12s}{'trades':>9s}{'L':>5s}{'S':>5s}{'net/wk':>11s}"
          f"{'$/trade':>10s}{'total':>14s}{'action path':>16s}")
    hr("-")
    ref_sig = (tuple(sess.tolist()), tuple(d.tolist()), float(np.nansum(e)), float(np.nansum(x)))
    stress = []
    bug = False
    for c in COST_STRESS:
        pnl = gross - c
        W = weekly_series(D, sess, pnl, weeks)
        sig = (tuple(sess.tolist()), tuple(d.tolist()), float(np.nansum(e)), float(np.nansum(x)))
        same = sig == ref_sig
        bug |= not same
        stress.append(dict(cost=c, trades=int(len(sess)), net_wk=float(W.mean()),
                           per_trade=float(pnl.mean()), total=float(pnl.sum()),
                           action_path_identical=bool(same)))
        print(f"    ${c:>11.2f}{len(sess):>9d}{int((d>0).sum()):>5d}{int((d<0).sum()):>5d}"
              f"{W.mean():>11.2f}{pnl.mean():>10.2f}{pnl.sum():>14,.2f}"
              f"{'IDENTICAL' if same else 'CHANGED (BUG)':>16s}")
    print()
    if bug:
        print("    *** BUG: a cost stress changed which trades occur. Reported as a defect. ***")
    else:
        print("    No cost stress changes which trades occur. That is the required invariant:")
        print("    XM has no cost-aware filter, no stop and no sizing rule, so cost enters as a")
        print("    pure constant per round turn. Cost is a SUBTRACTION, never a SIGNAL.")

    # ---------------------------------------------------------------- policy variants
    print()
    print("  POLICY VARIANTS - evaluated only because X1 passed. These are quote-driven and can")
    print("  therefore only be measured on the owned tick sessions that also carry an XM")
    print(f"  decision: n = {len(cond_dates)}. Any variant that changes WHICH trades occur is a")
    print("  POLICY CHANGE and inherits the full challenger burden. It is NOT folded into a")
    print("  cost table and NOTHING here is proposed for adoption.")
    print()
    rows = []
    for dte in cond_dates:
        direction = dir_by_date[dte]
        df = TL.read_window(sess_tk[dte]["paths"], dte, "09:40:00", "09:47:30")
        r = TL.policy_fills(df, dte, direction)
        r["date"] = dte.strftime("%Y-%m-%d")
        r["dir"] = direction
        rows.append(r)
    P = pd.DataFrame(rows)
    P.to_csv(os.path.join(OUT, "policy_variants.csv"), index=False)
    v0 = P["V0_first_print"].to_numpy()
    dv = P["dir"].to_numpy().astype(float)
    # DENOMINATOR DISCIPLINE: a variant that cannot be evaluated because the session carries no
    # BBO in the window is a DATA GAP, not a policy declining to trade. The two are separated.
    quotable = np.isfinite(P["bid_at_cut"].to_numpy()) & np.isfinite(P["ask_at_cut"].to_numpy())
    nq_ = int(quotable.sum())
    print(f"    of the {len(P)} conditional sessions, {nq_} carry a reconstructable BBO at")
    print(f"    09:45:00.000. The other {len(P)-nq_} are a DATA GAP, not a policy refusal, and")
    print(f"    are excluded from the fill-rate denominator.")
    print()
    print(f"    {'variant':<24s}{'filled':>8s}{'of':>5s}{'fill %':>9s}{'mean vs V0 $':>15s}"
          f"{'median $':>11s}{'trades change?':>20s}")
    hr("-")
    pol = []
    for key, nm in (("V1_marketable", "immediate marketable"),
                    ("V2_marketable_limit", "marketable limit +/-1tk"),
                    ("V3_touch_60s", "limit at touch, 60s")):
        v = P[key].to_numpy()
        m = np.isfinite(v) & np.isfinite(v0)
        slip = -dv[m] * (v[m] - v0[m]) * PV
        nf = int((np.isfinite(v) & quotable).sum())
        changes = nf < nq_
        pol.append(dict(variant=key, name=nm, filled=nf, n_quotable=nq_, n=len(P),
                        fill_pct=100.0 * nf / max(nq_, 1),
                        mean_vs_v0=float(slip.mean()) if m.any() else np.nan,
                        median_vs_v0=float(np.median(slip)) if m.any() else np.nan,
                        changes_which_trades=bool(changes)))
        print(f"    {nm:<24s}{nf:>8d}{nq_:>5d}{100.0*nf/max(nq_,1):>9.1f}"
              f"{(slip.mean() if m.any() else np.nan):>15.2f}"
              f"{(np.median(slip) if m.any() else np.nan):>11.2f}"
              f"{('YES - POLICY CHANGE' if changes else 'no'):>20s}")
    v1 = [p for p in pol if p["variant"] == "V1_marketable"][0]
    weeks_, _ = XC.week_index(D, DEC["win"])
    sess_, _ = common_armed_set(DEC, ["open_0946"], ["open_1546"])
    tpw_ = len(sess_) / len(weeks_)
    charged_entry_leg = XC.TICKV * 3.0 / 2.0
    print()
    print(f"    ⚠ THE ONE EXECUTION COST THE INCUMBENT REALLY DOES UNDER-BOOK, and it is not")
    print(f"      latency. V0 is a PRINT; a real market order fills at the FAR SIDE of the")
    print(f"      quote. V1 - V0 = ${v1['mean_vs_v0']:.2f}/contract (median "
          f"${v1['median_vs_v0']:.2f}) on {v1['filled']} sessions.")
    print(f"      The research cost model already charges ${charged_entry_leg:.2f} for the entry")
    print(f"      leg (half of the 3.0-tick modelled spread), so the UNBOOKED residue is")
    print(f"      ${abs(v1['mean_vs_v0']) - charged_entry_leg:+.2f}/contract = "
          f"${(abs(v1['mean_vs_v0']) - charged_entry_leg) * tpw_:+.2f}/week at {tpw_:.2f} "
          f"trades/wk.")
    print(f"      That is a SPREAD/CROSSING error, belongs in X5 component C, and is an order of")
    print(f"      magnitude smaller than the ${abs(PRIOR['entry_wk']):.2f}/wk the one-minute")
    print(f"      headline suggests is at stake.")
    print()
    print("    V0 is the incumbent's modelled fill (first print at or after 09:45:00.000).")
    print("    V1 pays the far side of the quote at arrival - that is the honest price of the")
    print("    incumbent's own market order, and it is a COST, not an improvement.")
    print("    V3's fill rule is 'a print traded through the level' - NO QUEUE MODEL, so its")
    print("    fill rate is an UPPER BOUND and its economics are optimistic by construction.")
    print("    NOTHING here is proposed for adoption. A variant that declines trades changes the")
    print("    OBJECT and would have to clear the full challenger burden on its own population.")

    gate("X4-COST", "cost stress must not change which trades occur",
         f"4 stresses ($4.36..$30.00), action path "
         f"{'CHANGED - BUG' if bug else 'IDENTICAL in all four'}", not bug)
    gate("X4-POLICY", "policy variants evaluated separately; any that changes WHICH trades occur "
                      "is labelled a POLICY CHANGE, not an execution improvement",
         "; ".join(f"{p['name']} filled {p['filled']}/{p['n']}"
                   f"{' POLICY CHANGE' if p['changes_which_trades'] else ''}" for p in pol), True)
    RESULT["X4"] = dict(cost_stress=stress, action_path_bug=bool(bug), policy=pol,
                        policy_n=len(P))
    return stress, pol


# =============================================================================================
def gate_X5(D, DEC, x2rows, cond, unc):
    head("GATE X5 - THE FIVE-WAY DECOMPOSITION IN $/WEEK  (an ESTIMATE with bands, not a test)")
    inc = [r for r in x2rows if r["fill"] == "open_0946"][0]
    ntr, nwk = inc["n"], RESULT["X2"]["n_weeks"]
    tpw = ntr / nwk
    base_wk = inc["net_wk"]
    weeks, _ = XC.week_index(D, DEC["win"])
    sess, _ = common_armed_set(DEC, [k for k, _, _, _ in ENTRY_FILLS], ["open_1546"])
    d = DEC["desired"][sess].astype(float)
    pnl = d * (DEC["X_open_1546"][sess] - DEC["E_open_0946"][sess]) * PV - XC.cost_per_rt()
    Wb = weekly_series(D, sess, pnl, weeks)
    bs_base = stationary_bootstrap(Wb)
    print(f"  Incumbent (zero-latency modelled fill): ${base_wk:.2f}/wk over {nwk} ISO weeks, "
          f"{ntr} trades = {tpw:.2f} trades/wk")
    print(f"    block-bootstrap 95 % CI on the weekly mean: "
          f"[${bs_base['lo']:.2f}, ${bs_base['hi']:.2f}]")
    print()

    def at(delay_lbl):
        r = [c for c in cond if c["delay"] == delay_lbl][0]
        return r

    s250 = at("+250ms")
    s1s = at("+1s")
    k = RESULT.get("X3C", {}).get("ratio", np.nan)
    print(f"  METHOD. The sub-second slippage measured in X3-A on n = {s250['n']} sessions is")
    print(f"  applied to ALL {ntr} trades at {tpw:.2f} trades/week. That is an EXTRAPOLATION")
    print(f"  from a {RESULT['X3']['first_date']}..{RESULT['X3']['last_date']} tick sample to a")
    print(f"  2022-2026 trade population, and it is the single largest source of uncertainty.")
    print(f"  X3-C measured the size of that risk directly: on the IDENTICAL 1-minute +60 s")
    print(f"  measurement the tick subsample is {k:.2f}x as latency-sensitive as the full")
    print(f"  population. The BANDS below are therefore the UNION of (i) the block/percentile")
    print(f"  bootstrap CI of the slippage mean and (ii) that same CI divided by {k:.2f}. The")
    print(f"  POINT ESTIMATE is the UNADJUSTED (more pessimistic) value.")
    print()

    def band(mean_usd, lo, hi):
        mu, l, h = mean_usd * tpw, lo * tpw, hi * tpw
        if np.isfinite(k) and k > 0:
            l, h = min(l, l / k), max(h, h / k)
        return mu, l, h

    d1_mu, d1_lo, d1_hi = band(s1s["mean_usd"], s1s["ci_lo"], s1s["ci_hi"])
    d2_mu, d2_lo, d2_hi = band(s250["mean_usd"], s250["ci_lo"], s250["ci_hi"])
    A_mu, A_lo, A_hi = base_wk + d1_mu, base_wk + d1_lo, base_wk + d1_hi
    B_mu, B_lo, B_hi = -d1_mu, -d1_hi, -d1_lo
    Dc_mu, Dc_lo, Dc_hi = -d2_mu, -d2_hi, -d2_lo
    E_mu, E_lo, E_hi = base_wk + d2_mu, base_wk + d2_lo, base_wk + d2_hi

    # ---- C: modelled vs measured spread
    sp_e = RESULT["X3"]["spread_med_tk_entry"]
    sp_e1 = RESULT["X3"]["spread_med1s_tk_entry"]
    sp_x = RESULT["X3"]["spread_med_tk_exit"]
    sp_x1 = RESULT["X3"]["spread_med1s_tk_exit"]
    meas_rt = XC.TICKV * (sp_e + sp_x) / 2.0
    meas_rt1 = XC.TICKV * (sp_e1 + sp_x1) / 2.0
    C_mu = -(meas_rt - MODELLED_SPREAD_RT) * tpw
    C_lo = -(max(meas_rt, meas_rt1) - MODELLED_SPREAD_RT) * tpw
    C_hi = -(min(meas_rt, meas_rt1) - MODELLED_SPREAD_RT) * tpw
    print(f"  C uses the SAME charging convention as the research cost model, which charges")
    print(f"  $5.00 x (spread_entry + spread_exit)/2 = one HALF spread per leg.")
    print(f"    modelled: 3.00 tk at 09:46 and 2.00 tk at 15:46 -> ${MODELLED_SPREAD_RT:.2f}/ctrRT")
    print(f"    MEASURED: {sp_e:.2f} tk at 09:45:00 and {sp_x:.2f} tk at 15:45:00 -> "
          f"${meas_rt:.2f}/ctrRT   (1 s-median estimator: {sp_e1:.2f}/{sp_x1:.2f} tk -> "
          f"${meas_rt1:.2f})")
    print()

    comps = [
        ("A  signal alpha", "edge surviving a fill delayed past any plausible retail latency "
         f"({BEYOND_LATENCY_S:.0f} s)", A_mu, A_lo, A_hi,
         f"X2 incumbent + X3-A slip at +1s (n={s1s['n']})"),
        ("B  impossible-backtest execution", "value that exists ONLY at the zero-latency fill",
         B_mu, B_lo, B_hi, f"-(X3-A slip at +1s) x {tpw:.2f} trades/wk"),
        ("C  spread and slippage", "measured BBO at the decision instant vs the modelled "
         f"${MODELLED_SPREAD_RT:.2f}/ctrRT", C_mu, C_lo, C_hi,
         f"({MODELLED_SPREAD_RT:.2f} - {meas_rt:.2f}) x {tpw:.2f}/wk, band = the two estimators"),
        ("D  latency decay", f"the sub-second portion of B, at {RETAIL_LATENCY_S*1000:.0f} ms",
         Dc_mu, Dc_lo, Dc_hi, f"-(X3-A slip at +250ms) x {tpw:.2f} trades/wk"),
        ("E  capturable tomorrow", f"A + whatever of B survives a "
         f"{RETAIL_LATENCY_S*1000:.0f} ms fill", E_mu, E_lo, E_hi,
         "X2 incumbent + X3-A slip at +250ms"),
    ]
    print(f"  {'component':<36s}{'$/wk':>10s}{'95 % band':>24s}   method")
    hr("-")
    for nm, desc, mu, lo, hi, meth in comps:
        print(f"  {nm:<36s}{mu:>10.2f}{f'[{lo:>8.2f}, {hi:>8.2f}]':>24s}   {meth}")
        print(f"    {desc}")
    E_plus_C = E_mu + C_mu
    print()
    print(f"  E with the measured-spread correction C also applied: "
          f"${E_plus_C:.2f}/wk  (band ${E_lo + C_lo:.2f} .. ${E_hi + C_hi:.2f})")
    print()
    print("  SENSITIVITY on the representativeness adjustment (X3-C) and on the bounce/drift")
    print("  split (X3-A MID columns) - three readings of the SAME components:")
    mid250 = s250.get("mid_mean_usd", np.nan)
    mid1s = s1s.get("mid_mean_usd", np.nan)
    print(f"    {'reading':<46s}{'D $/wk':>11s}{'E $/wk':>11s}")
    hr("-")
    print(f"    {'raw LAST-price slippage (the point estimate)':<46s}"
          f"{Dc_mu:>11.2f}{E_mu:>11.2f}")
    if np.isfinite(k) and k > 0:
        print(f"    {'LAST-price, representativeness-adjusted /'+f'{k:.2f}':<46s}"
              f"{Dc_mu/k:>11.2f}{base_wk + d2_mu/k:>11.2f}")
    print(f"    {'MID-based (bounce removed) at 250 ms':<46s}"
          f"{-mid250*tpw:>11.2f}{base_wk + mid250*tpw:>11.2f}")
    print(f"    -> across every reading E stays in "
          f"${min(E_mu, base_wk + (d2_mu/k if np.isfinite(k) and k>0 else d2_mu), base_wk + mid250*tpw):.0f}"
          f" .. ${max(E_mu, base_wk + (d2_mu/k if np.isfinite(k) and k>0 else d2_mu), base_wk + mid250*tpw):.0f}/wk")
    print("    NOTE the 95 % bands above are NOT widened by the representativeness adjustment:")
    print("    the adjustment SHRINKS the slippage toward zero, and every slippage CI already")
    print("    straddles zero, so the union of the two intervals IS the raw interval.")
    print()
    # -------- population-matched restatement, for the verdict rule ---------------------------
    print("  POPULATION-MATCHED RESTATEMENT. E above is on this run's 2022-01-03 study window,")
    print("  whose own incumbent is ${:.2f}/wk. XM's QUOTED contribution (${:.2f}/wk) was".format(
        base_wk, XM_QUOTED_STANDALONE))
    print("  measured on the 2022-07-01 window. Comparing the two directly would mix")
    print("  populations, so the same arithmetic is repeated on the quoted population:")
    DECs = XC.build_decisions(D, *SOURCE_WINDOW)
    ws, _ = XC.week_index(D, DECs["win"])
    ss, _ = common_armed_set(DECs, ["open_0946"], ["open_1546"])
    tpw_s = len(ss) / len(ws)
    E_src = XM_QUOTED_STANDALONE + s250["mean_usd"] * tpw_s
    A_src = XM_QUOTED_STANDALONE + s1s["mean_usd"] * tpw_s
    ret_spec = 100.0 * E_mu / base_wk
    ret_src = 100.0 * E_src / XM_QUOTED_STANDALONE
    print(f"    SOURCE window: {len(ss)} trades / {len(ws)} weeks = {tpw_s:.2f} trades/wk, "
          f"incumbent ${XM_QUOTED_STANDALONE:.2f}/wk")
    print(f"      A (1 s fill)   ${A_src:>8.2f}/wk      E (250 ms fill) ${E_src:>8.2f}/wk")
    print(f"    RETENTION of XM's modelled edge at a 250 ms fill: "
          f"{ret_spec:.1f} % (spec window)  /  {ret_src:.1f} % (quoted window)")
    RESULT.setdefault("X5_matched", {}).update(
        E_source_window=float(E_src), A_source_window=float(A_src),
        retention_pct_spec=float(ret_spec), retention_pct_source=float(ret_src),
        trades_per_week_source=float(tpw_s))
    print()
    print("  EVIDENCE CLASS of each component:")
    print("    A, B, D, E  DIRECTLY_BURNED on the 1-min side (the XM object is in-sample over the")
    print("                whole window) x FORWARD-ish on the tick side (the tick sample is a")
    print(f"                {RESULT['X3']['first_date']}..{RESULT['X3']['last_date']} slice that")
    print("                was never used to fit XM). The PRODUCT is a mixture and is quoted as")
    print("                an estimate, never as an out-of-sample result.")
    print("    C           LEGACY_DIAGNOSTIC vs measurement: the modelled profile is W82's")
    print("                committed per-minute spread; the measurement is this run's.")

    RESULT["X5"] = dict(trades_per_week=tpw, incumbent_wk=base_wk,
                        incumbent_ci=[bs_base["lo"], bs_base["hi"]],
                        A=[A_mu, A_lo, A_hi], B=[B_mu, B_lo, B_hi], C=[C_mu, C_lo, C_hi],
                        D=[Dc_mu, Dc_lo, Dc_hi], E=[E_mu, E_lo, E_hi],
                        E_with_C=[E_plus_C, E_lo + C_lo, E_hi + C_hi],
                        measured_spread_rt=meas_rt, measured_spread_rt_1s=meas_rt1,
                        modelled_spread_rt=MODELLED_SPREAD_RT)
    gate("X5", "five-way split in $/week, each component with a stated method and an uncertainty "
               "band", f"A ${A_mu:.0f} B ${B_mu:.0f} C ${C_mu:.0f} D ${Dc_mu:.0f} E ${E_mu:.0f} "
                       f"per week, all banded", True)
    return dict(A=(A_mu, A_lo, A_hi), B=(B_mu, B_lo, B_hi), C=(C_mu, C_lo, C_hi),
                D=(Dc_mu, Dc_lo, Dc_hi), E=(E_mu, E_lo, E_hi), E_with_C=E_plus_C)


# =============================================================================================
def breakeven_block(cond, x2rows):
    """The single number the execution budget needs: at what delay does the edge reach zero?"""
    head("BREAK-EVEN LATENCY, CONSOLIDATED  (spec X2 'derived'; needs both instruments)")
    x3c = RESULT["X3C"]
    inc = [r for r in x2rows if r["fill"] == "open_0946"][0]
    print("  Three functional forms, on both populations. They are printed together because no")
    print("  one of them is right: the measured surface is noisy and non-monotone, and every")
    print("  break-even extrapolates a slope fitted inside four minutes to a horizon of hours.")
    print()
    rows = []
    for pop, edge, pts in (
        (f"tick subsample (n={x3c['n_sub']})", x3c["per_trade_sub"],
         [(0.25, -[c for c in cond if c["delay"] == "+250ms"][0]["mean_usd"]),
          (1.0, -[c for c in cond if c["delay"] == "+1s"][0]["mean_usd"]),
          (60.0, -x3c["tick_60s"])]),
        (f"all trades (n={x3c['n_full']})", inc["per_trade"],
         [(0.25, -[c for c in cond if c["delay"] == "+250ms"][0]["mean_usd"] / x3c["ratio"]),
          (1.0, -[c for c in cond if c["delay"] == "+1s"][0]["mean_usd"] / x3c["ratio"]),
          (60.0, -[r for r in x2rows if r["fill"] == "open_0947"][0]["d_per_trade"]),
          (120.0, -[r for r in x2rows if r["fill"] == "open_0948"][0]["d_per_trade"]),
          (240.0, -[r for r in x2rows if r["fill"] == "open_0950"][0]["d_per_trade"])])):
        t_ = np.array([p[0] for p in pts])
        c_ = np.array([p[1] for p in pts])
        lin = float(np.linalg.lstsq(t_.reshape(-1, 1), c_, rcond=None)[0][0])
        sq = float(np.linalg.lstsq(np.sqrt(t_).reshape(-1, 1), c_, rcond=None)[0][0])
        loc = c_[1] / t_[1]                          # local slope at 1 s
        be_lin = edge / lin if lin > 0 else np.inf
        be_sq = (edge / sq) ** 2 if sq > 0 else np.inf
        be_loc = edge / loc if loc > 0 else np.inf
        rows.append(dict(population=pop, edge_per_trade=edge, linear_be_s=be_lin,
                         sqrt_be_s=be_sq, local1s_be_s=be_loc))
        print(f"  {pop:<28s} after-cost edge ${edge:>7.2f}/trade")
        print(f"      LINEAR   cost = {lin:.4f}$/s        -> break-even "
              f"{be_lin:>10,.0f} s  ({be_lin/60:>7.1f} min)")
        print(f"      SQRT-LAW cost = {sq:.4f}$/sqrt(s)  -> break-even "
              f"{be_sq:>10,.0f} s  ({be_sq/60:>7.1f} min)   <- the diffusive form, best motivated")
        print(f"      LOCAL@1s cost = {loc:.4f}$/s        -> break-even "
              f"{be_loc:>10,.0f} s  ({be_loc/60:>7.1f} min)   <- steepest, most pessimistic")
    allbe = [r[k] for r in rows for k in ("linear_be_s", "sqrt_be_s", "local1s_be_s")]
    lo_, hi_ = min(allbe), max(allbe)
    print()
    print(f"  THE OPERATIONAL READING: across all six estimates the break-even latency spans")
    print(f"  {lo_:,.0f} s to {hi_:,.0f} s. The TIGHTEST ({lo_:,.0f} s) is the LOCAL@1s form on")
    print(f"  the tick subsample - the most pessimistic construction available, because it takes")
    print(f"  the steepest measured local slope, on the most latency-sensitive {rows[0]['population']}")
    print(f"  we own, and extrapolates it LINEARLY when the measured surface is clearly")
    print(f"  sub-linear (sqrt-like) in time. Even that number is {lo_/RETAIL_LATENCY_S:,.0f}x a "
          f"{RETAIL_LATENCY_S*1000:.0f} ms fill:")
    print(f"  a 250 ms order path spends {100*RETAIL_LATENCY_S/lo_:.1f} % of the pessimistic "
          f"budget and {100*RETAIL_LATENCY_S/hi_:.4f} % of the")
    print(f"  optimistic one. THE BUDGET IS NOT THE BINDING CONSTRAINT ON THIS STRATEGY.")
    RESULT["BREAKEVEN_SPAN"] = [float(lo_), float(hi_)]
    RESULT["BREAKEVEN"] = rows
    return rows


def verdict(x5, cond, x2rows):
    head("THE VERDICT RULE - written in spec.yaml section 2 BEFORE any number existed")
    E_mu, E_lo, E_hi = x5["E"]
    print(f"  downgrade_rule : E < 50 % of XM's currently quoted contribution -> DOWNGRADE")
    print(f"  retain_rule    : decay shallow inside 1 s and steep only across minutes -> the")
    print(f"                   -$74.18/wk figure is a RED HERRING for deployment")
    print(f"  neither_rule   : X3 underpowered AND the unconditional bound inconclusive ->")
    print(f"                   UNRESOLVED WITH A NAMED NEXT MEASUREMENT")
    print()
    E_src = RESULT["X5_matched"]["E_source_window"]
    print(f"  The rule is applied POPULATION-MATCHED: E on the quoted population is "
          f"${E_src:.2f}/wk.")
    print(f"  (E on this run's wider 2022-01-03 study window is ${E_mu:.2f}/wk against that")
    print(f"  window's own incumbent of ${RESULT['X5']['incumbent_wk']:.2f}/wk; both are printed")
    print(f"  so the reader can see the rule does not turn on the choice.)")
    print()
    for nm, q in (("standalone, deployed 346-trade object", XM_QUOTED_STANDALONE),
                  ("standalone, vectorised 348-trade variant", XM_QUOTED_VECTORISED),
                  ("marginal contribution to the P1+XM book", XM_QUOTED_MARGINAL)):
        print(f"    E ${E_src:.2f}/wk vs 50 % of ${q:.2f} = ${0.5*q:.2f}  "
              f"-> {'BELOW (downgrade)' if E_src < 0.5*q else 'ABOVE (no downgrade)'}   [{nm}]")
    downgrade = E_src < 0.5 * XM_QUOTED_STANDALONE

    s1 = [c for c in cond if c["delay"] == "+1s"][0]
    s250 = [c for c in cond if c["delay"] == "+250ms"][0]
    m60 = [r for r in x2rows if r["fill"] == "open_0947"][0]
    inc = [r for r in x2rows if r["fill"] == "open_0946"][0]
    x3c = RESULT["X3C"]
    k = x3c["ratio"]
    print()
    print(f"  SHAPE OF THE CURVE - stated POPULATION-MATCHED, because the sub-second curve lives")
    print(f"  on {x3c['n_sub']} tick sessions and the 1-minute curve on all {x3c['n_full']}, and "
          f"those two sets are")
    print(f"  not equally latency-sensitive ({k:.2f}x, X3-C).")
    print()
    print(f"    ON THE {x3c['n_sub']} TICK SESSIONS (one population, one instrument):")
    print(f"      +250 ms ${s250['mean_usd']:+8.2f}/trade   +1 s ${s1['mean_usd']:+8.2f}/trade   "
          f"+60 s ${x3c['tick_60s']:+8.2f}/trade")
    print(f"      the first second costs {100*abs(s1['mean_usd'])/abs(x3c['tick_60s']):.0f} % of "
          f"what the first MINUTE costs; the first 250 ms costs "
          f"{100*abs(s250['mean_usd'])/abs(x3c['tick_60s']):.0f} %.")
    print(f"      against that subsample's own ${x3c['per_trade_sub']:.2f}/trade after-cost edge: "
          f"{100*abs(s250['mean_usd'])/abs(x3c['per_trade_sub']):.1f} % at 250 ms, "
          f"{100*abs(s1['mean_usd'])/abs(x3c['per_trade_sub']):.1f} % at 1 s, "
          f"{100*abs(x3c['tick_60s'])/abs(x3c['per_trade_sub']):.1f} % at 60 s")
    print(f"    ON ALL {x3c['n_full']} TRADES (1-minute instrument, plus the /"
          f"{k:.2f} adjusted sub-second):")
    print(f"      +250 ms ${s250['mean_usd']/k:+8.2f}   +1 s ${s1['mean_usd']/k:+8.2f}   "
          f"+60 s ${m60['d_per_trade']:+8.2f}/trade "
          f"(d ${m60['d_wk']:+.2f}/wk, t {m60['t_diff']:.2f}, boot p {m60['boot_p']:.4f})")
    print(f"      against the ${inc['per_trade']:.2f}/trade after-cost edge: "
          f"{100*abs(s250['mean_usd']/k)/abs(inc['per_trade']):.1f} % at 250 ms, "
          f"{100*abs(s1['mean_usd']/k)/abs(inc['per_trade']):.1f} % at 1 s, "
          f"{100*abs(m60['d_per_trade'])/abs(inc['per_trade']):.1f} % at 60 s")
    print(f"    MID-based (bounce removed), same n: ${s250.get('mid_mean_usd', np.nan):+.2f} at "
          f"250 ms, ${s1.get('mid_mean_usd', np.nan):+.2f} at 1 s")
    shallow_1s = abs(s1["mean_usd"]) < 0.15 * abs(x3c["per_trade_sub"])
    steep_min = abs(x3c["tick_60s"]) > 2.0 * abs(s1["mean_usd"])
    ci_spans_zero = (s250["ci_lo"] < 0 < s250["ci_hi"])
    underpowered = RESULT["X3"]["underpowered"]
    print()
    print(f"  RULE EVALUATION, mechanical")
    print(f"    E ${E_src:.2f}/wk >= 50 % of the quoted ${XM_QUOTED_STANDALONE:.2f}/wk    "
          f"-> downgrade_rule {'FIRES' if downgrade else 'DOES NOT FIRE'}")
    print(f"    slippage inside 1 s is "
          f"{100*abs(s1['mean_usd'])/abs(x3c['per_trade_sub']):.1f} % of the per-trade edge on "
          f"the SAME sessions (< 15 %) -> 'shallow inside 1 s' "
          f"{'TRUE' if shallow_1s else 'FALSE'}")
    print(f"    the 1-minute cost ${abs(x3c['tick_60s']):.2f}/trade is "
          f"{abs(x3c['tick_60s'])/abs(s1['mean_usd']):.1f}x the 1-second cost "
          f"${abs(s1['mean_usd']):.2f} on the SAME sessions -> 'steeper across minutes' "
          f"{'TRUE' if steep_min else 'FALSE'}")
    print(f"    X3-A underpowered (n < {UNDERPOWER_N})                                    "
          f"-> {'TRUE' if underpowered else 'FALSE'}")
    print()
    if downgrade:
        print("  ==> VERDICT: XM IS DOWNGRADED. E is under half the quoted contribution; the")
        print("      book's second leg would be resting on an execution assumption.")
    elif shallow_1s and steep_min and not underpowered:
        print("  ==> VERDICT: retain_rule FIRES. XM's edge is ROBUST TO REALISTIC LATENCY. The")
        print("      decay is shallow inside one second and only becomes material across")
        print("      minutes, so the -$74.18/wk one-minute figure is A RED HERRING FOR")
        print("      DEPLOYMENT PURPOSES. It is a true statement about a one-MINUTE delay and a")
        print("      misleading one about a retail order, which is late by milliseconds.")
    elif underpowered:
        print("  ==> VERDICT: UNRESOLVED WITH A NAMED NEXT MEASUREMENT.")
    else:
        print("  ==> VERDICT: neither rule fires cleanly; see the report.")
    RESULT["VERDICT"] = dict(downgrade=bool(downgrade), shallow_inside_1s=bool(shallow_1s),
                             steep_across_minutes=bool(steep_min),
                             subsecond_ci_spans_zero=bool(ci_spans_zero),
                             underpowered=bool(underpowered),
                             E=E_mu, E_band=[E_lo, E_hi],
                             quoted=XM_QUOTED_STANDALONE)
    return downgrade, shallow_1s, steep_min


# =============================================================================================
def print_gate_table():
    head("GATE TABLE  (printed by the program - GATE / SPEC / OBSERVED / PASS-FAIL)")
    w1, w2, w3 = 10, 62, 74
    print(f"  {'GATE':<{w1}}{'SPEC':<{w2}}{'OBSERVED':<{w3}}VERDICT")
    hr("-")
    for g in GATES:
        sp = [g["spec"][i:i + w2 - 2] for i in range(0, len(g["spec"]), w2 - 2)]
        ob = [g["observed"][i:i + w3 - 2] for i in range(0, len(g["observed"]), w3 - 2)]
        n = max(len(sp), len(ob))
        for i in range(n):
            print(f"  {(g['gate'] if i == 0 else ''):<{w1}}"
                  f"{(sp[i] if i < len(sp) else ''):<{w2}}"
                  f"{(ob[i] if i < len(ob) else ''):<{w3}}"
                  f"{(g['verdict'] if i == 0 else '')}")
        hr("-")


# =============================================================================================
def main():
    t0 = time.time()
    tee = Tee(os.path.join(OUT, "console.txt"))
    sys.stdout = tee
    try:
        hr()
        print("G3_XMLAT_01_20260831 - XM_CONFLICT LATENCY FORENSICS")
        print("run per runs/G3_XMLAT_01_20260831/spec.yaml, preregistered and committed "
              "before any result existed")
        print(f"executed {pd.Timestamp.now():%Y-%m-%d %H:%M:%S}   live_enabled: NO   spend: 0   "
              "orders_placed: NO")
        hr()
        print("SEAL: the substrate is loaded with b = '2026-07-31 17:00' and the load asserts no")
        print("      bar at or after 2026-08-01 exists. The tick index refuses any session dated")
        print("      2026-08-01 or later. NOTHING VIRGIN IS READ.")
        print("EXCLUDED BY SEAL: the 9 NQ full-BBO tick sessions dated 2026-08-01..2026-08-11 in")
        print("      NT8_CAPABILITY_CENSUS.csv (196 total - 187 pre-seal), and every 1-minute bar")
        print("      after 2026-07-31 17:00 ET.")
        print("NO CrossTrade / NinjaTrader tool call is made anywhere in this program.")

        head("SUBSTRATE AND THE FROZEN DECISION LEDGER")
        D = XC.load_substrate()
        print()
        print("  The frozen decision set used wherever possible is")
        print("    research/weekly_edge/ninjascript/reference/xm_reference_decisions.csv")
        print("  It covers 2022-07-04..2026-07-31 only and carries no delayed-fill prices, so the")
        print("  run REBUILDS the decision set from export_xm_reference.py semantics and asserts")
        print("  the rebuild against the frozen ledger before any gate runs. Both are used: the")
        print("  ledger as the authority, the rebuild as the instrument.")
        print()
        DECf = XC.build_decisions(D, *SOURCE_WINDOW)
        ver = XC.verify_against_frozen(DECf, D)
        ok_ver = (ver["dd_agree"] == 100.0 and ver["cf_agree"] == 100.0
                  and ver["drive_agree"] == 100.0 and ver["comp_maxabsdiff"] < 1e-12
                  and ver["entry_px_maxabsdiff"] == 0.0 and ver["exit_px_maxabsdiff"] == 0.0
                  and ver["ref_trades"] == ver["mine_trades_on_ref_window"])
        gate("REBUILD", "rebuild must reproduce the frozen decision ledger exactly before any "
                        "gate is evaluated",
             f"desired_direction {ver['dd_agree']:.4f} %, conflict {ver['cf_agree']:.4f} %, "
             f"drive {ver['drive_agree']:.4f} %, composite max |diff| "
             f"{ver['comp_maxabsdiff']:.1e}, fill prices exact, trades "
             f"{ver['mine_trades_on_ref_window']}/{ver['ref_trades']}", ok_ver)
        RESULT["REBUILD"] = ver
        if not ok_ver:
            print("\n  *** THE REBUILD DOES NOT REPRODUCE THE FROZEN LEDGER. Everything downstream")
            print("      would be a different object. Stopping. ***")
            print_gate_table()
            return

        x0_pass, x0 = gate_X0(D)
        if not x0_pass:
            print()
            hr()
            print("X0 FAILED. THE PREMISE IS WITHDRAWN.")
            print("Per spec.yaml X0.if_fail, gates X1-X5 are VOID and are NOT printed.")
            hr()
            print_gate_table()
            RESULT["X1_X5"] = "VOID - X0 failed"
            return

        x1_pass, DEC = gate_X1(D)
        x2rows = gate_X2(D, DEC)
        cond, unc, E, X, sess_tk, dir_by_date, cond_dates = gate_X3(D, DEC)
        if x1_pass:
            gate_X4(D, DEC, sess_tk, dir_by_date, cond_dates)
        else:
            print("\n  X1 did not pass: the policy variants of X4 are NOT evaluated (spec X4).")
        x5 = gate_X5(D, DEC, x2rows, cond, unc)
        breakeven_block(cond, x2rows)
        verdict(x5, cond, x2rows)

        head("THE TRAP NAMED IN SPEC SECTION 3, RESTATED AFTER THE MEASUREMENT")
        print("  '$15,800 earned in the minute 09:45 -> 09:46' and '-$74.18/wk per minute of")
        print("  entry delay' ARE THE SAME MEASUREMENT SEEN TWICE. $74.18 x 213 weeks = $15,800")
        print("  and $15,800 / 346 trades = $45.66/trade. They are one number expressed three")
        print("  ways - per week, in total, and per trade - and this report never cites them as")
        print("  two corroborating findings.")

        print_gate_table()
        with open(os.path.join(OUT, "gates.json"), "w", encoding="utf-8") as f:
            json.dump(dict(run_id="G3_XMLAT_01_20260831",
                           executed=str(pd.Timestamp.now()),
                           live_enabled=False, spend=0, orders_placed=False,
                           gates=GATES, results=RESULT), f, indent=2, default=str)
        print(f"\nwrote out/gates.json, out/console.txt   [{time.time()-t0:.0f}s total]")
    finally:
        sys.stdout = tee.stdout
        tee.f.close()


if __name__ == "__main__":
    main()
