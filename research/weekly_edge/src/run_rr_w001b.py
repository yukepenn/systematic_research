"""RR_W001 phase 2-5 - oracles, portfolio-relative value, and the preregistered gate table.

Spec: runs/RR_W001_ACTION_VALUE_LEDGER/spec.yaml (f3dd814). Reads the ledger built by
run_rr_w001.py. NO MODEL IS FITTED. Every gate clause below is a coded assertion.

A / B / C are EX-POST CEILINGS. OPPORTUNITY_LANGUAGE.md is binding: they are never called
opportunity, and A - E is not money we failed to collect.
"""
from __future__ import annotations

import itertools
import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                   # noqa: E402
from run_we_w01 import ROOT, COMM_RT, PV                                  # noqa: E402
from run_we_w17 import load_deep                                          # noqa: E402
from run_we_w26 import fills_daily                                        # noqa: E402
from run_we_w37 import causal_score                                       # noqa: E402
from run_we_w39 import WIN                                                # noqa: E402
from run_we_w97 import votes                                              # noqa: E402
from run_we_w98 import gfills, TICKV                                      # noqa: E402
from we_fastctx import fast_build_context                                 # noqa: E402
from run_rr_w001 import gfills_sess, runs_in, score_to_size, icc_and_neff  # noqa: E402

RUN = os.path.join(ROOT, "runs", "RR_W001_ACTION_VALUE_LEDGER")
OUT = os.path.join(RUN, "out")
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
W82OUT = os.path.join(ROOT, "runs", "WE_W82_FILLAUDIT", "out")
W110W = os.path.join(ROOT, "runs", "WE_W110_XMDIVERSE", "out", "weekly.csv")
XMREF = os.path.join(ROOT, "research", "weekly_edge", "ninjascript", "reference",
                     "xm_reference_decisions.csv")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
HALT, TARGET = 1300.0, 1000.0
MATERIALITY = 0.10
Z80 = 1.959963985 + 0.8416212
G1_DOLLARS, G1_SHARE = 50.0, 0.10
G2_TOP, G2_MAX = 0.05, 0.80
G4_MIN_POS_BUCKETS = 3
B_CAP = 8
FRACS = [0.05, 0.10, 0.20, 0.30]
DDT = 20245.0

_t0 = _time.time()
_fh = open(os.path.join(OUT, "rr_w001b.txt"), "w", encoding="utf-8")


def P_(*a):
    print(*a, flush=True)
    print(*a, file=_fh)
    _fh.flush()


def el():
    return f"[{_time.time() - _t0:6.0f}s]"


def main():
    P_("=" * 124)
    P_("=== RR_W001 PHASES 2-5 - oracles, portfolio value, gates.  NO MODEL IS FITTED.")
    P_("=== A / B / C are EX-POST CEILINGS, never 'opportunity' (OPPORTUNITY_LANGUAGE.md, binding).")
    P_("=" * 124)

    # ---------------------------------------------------------------- substrate + baseline
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    X = fast_build_context(D)
    zz = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    vl, _ = votes(D, zz["mem"], zz["bmom"], zz["tilt"], X, zz["bmom"])
    p = vl.astype(np.int8)
    n, tarr, sid, fb, lb = D["n"], D["t"], D["sid"], D["fb"], D["lb"]
    NS = D["n_sess"]
    sess_lo = {int(sid[i]): int(i) for i in np.flatnonzero(fb)}
    sess_hi = {int(sid[i]): int(i) for i in np.flatnonzero(lb)}
    prof = pd.read_csv(os.path.join(W82OUT, "spread_by_minute.csv")).set_index("mod")["sp_tk"]
    prof_d = {int(k): float(v) for k, v in prof.items()}
    modarr = np.array([pd.Timestamp(x).hour * 60 + pd.Timestamp(x).minute for x in tarr])
    spk = np.array([prof_d.get(int(m), 3.0) for m in modarr])

    def net_res(tr):
        return tr["pnl"] - tr["u"] * TICKV * (spk[tr["eti"]] + spk[tr["xti"]]) / 2.0

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    SCH1 = {s: gfills_sess(D, p, None, sess_lo[s], sess_hi[s]) for s in range(NS)}
    base_ent_all = [t["eti"] for s in range(NS) for t in SCH1[s]]
    bb = fills_daily(D, p, halt=HALT, target=TARGET)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    s_, _ = causal_score(X, ee, window=WIN)
    sz = score_to_size(s_, n)
    BASE = []
    for s in range(NS):
        BASE.extend(gfills_sess(D, p, sz, sess_lo[s], sess_hi[s]))
    in_win = np.zeros(NS, bool)
    for s in range(NS):
        if A <= tarr[sess_lo[s]] < B:
            in_win[s] = True
    P_(f"{el()} substrate rebuilt; baseline {len(BASE):,} trades")

    # ---------------------------------------------------------------- the ledger
    L = pd.read_csv(os.path.join(OUT, "ledger_p1pct.csv"))
    LW = L[L["in_window_session"]].reset_index(drop=True)
    P_(f"{el()} ledger {len(L):,} rows, in-window {len(LW):,}")
    assert len(LW) == 2131, f"expected 2,131 in-window decisions, got {len(LW)}"

    dav = LW["delta_action_value"].to_numpy()
    own = LW["baseline_trade_net"].to_numpy()
    sess = LW["session_id"].to_numpy()
    realized_net = float(own.sum())
    BAR = MATERIALITY * realized_net / len(LW)

    P_("")
    P_("=" * 124)
    P_("=== 1. THE MATERIALITY BAR - derived from the object's own economics, per spec")
    P_("=" * 124)
    P_(f"    P1/PCT realized net over the window, research cost model   ${realized_net:>14,.0f}")
    P_(f"    in-window decision events                                  {len(LW):>15,}")
    P_(f"    BAR = 0.10 * net / events                                  ${BAR:>14,.2f} per decision")
    P_(f"    (= 10 % of the object's own realized net. A router must move at least this much")
    P_(f"     per decision to be worth its research and engineering cost.)")

    # ---------------------------------------------------------------- A: distribution
    P_("")
    P_("=" * 124)
    P_("=== 2. LOCAL_MARGINAL_ACTION_ORACLE (level A) - the distribution of the value OF ACTING")
    P_("=" * 124)
    P_(f"    n = {len(dav):,}   mean ${dav.mean():,.2f}   sd ${dav.std(ddof=1):,.2f}   "
       f"median ${np.median(dav):,.2f}")
    P_(f"    share positive {100 * (dav > 0).mean():.2f} %   share negative "
       f"{100 * (dav < 0).mean():.2f} %   share exactly zero {100 * (dav == 0).mean():.2f} %")
    qs = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    P_("    quantiles  " + "  ".join(f"p{q}:${np.percentile(dav, q):,.0f}" for q in qs))
    P_(f"    total absolute action value  ${np.abs(dav).sum():,.0f}")
    P_(f"    sum of action values         ${dav.sum():,.0f}   (vs realized net ${realized_net:,.0f})")
    P_("")
    P_("    BOTH ARMS, as the spec requires (neither is chosen after the result):")
    fz = LW["delta_action_value_frozen"].to_numpy()
    tw = LW["delta_total_window"].to_numpy()
    P_(f"{'arm':<34}{'mean':>12}{'sd':>12}{'sum':>14}{'% positive':>12}")
    for lab, v in (("SELF-CONSISTENT (primary)", dav), ("FROZEN-SCORE (sensitivity)", fz),
                   ("FULL-HORIZON (both channels)", tw)):
        P_(f"{lab:<34}${v.mean():>11,.2f}${v.std(ddof=1):>11,.2f}${v.sum():>13,.0f}"
           f"{100 * (v > 0).mean():>11.2f}%")
    P_(f"    the two arms differ on {int((np.abs(dav - fz) > 1e-9).sum()):,} of {len(dav):,} events; "
       f"max |difference| ${np.abs(dav - fz).max():,.0f}")
    P_("")
    P_("    EVIDENCE STATUS (spec secondary_measurements, CLAUDE.md section 4):")
    bd = pd.to_datetime(LW["session_date"])
    burn = (bd >= "2026-05-31") & (bd <= "2026-07-31")
    P_(f"      whole window 2022-07-01 -> 2026-08-01 : DISCOVERY_CONSUMED (123 waves)")
    P_(f"      2026-05-31 -> 2026-07-31              : DIRECTLY_BURNED - {int(burn.sum()):,} events "
       f"({100 * burn.mean():.2f} %), own net ${LW.loc[burn.to_numpy(), 'baseline_trade_net'].sum():,.0f}, "
       f"action-value sum ${dav[burn.to_numpy()].sum():,.0f}")
    P_(f"      >= 2026-08-01                          : VIRGIN / SEALED - NOT TOUCHED")

    # ---------------------------------------------------------------- G1
    P_("")
    P_("=" * 124)
    P_("=== 3. G1 - WAS THE COUNTERFACTUAL MACHINERY NECESSARY?")
    P_("=" * 124)
    diff = np.abs(dav - own)
    share_diff = float((diff > G1_DOLLARS).mean())
    P_(f"    |delta_action_value - the trade's OWN net| > ${G1_DOLLARS:.0f} on "
       f"{int((diff > G1_DOLLARS).sum()):,} of {len(diff):,} events = {100 * share_diff:.2f} %")
    P_(f"    mean |difference| ${diff.mean():,.2f}   median ${np.median(diff):,.2f}   "
       f"max ${diff.max():,.0f}")
    P_(f"    rank correlation(action value, own net) = "
       f"{pd.Series(dav).corr(pd.Series(own), method='spearman'):.4f}")
    P_(f"    events where the SIGN differs: {int((np.sign(dav) != np.sign(own)).sum()):,} "
       f"({100 * (np.sign(dav) != np.sign(own)).mean():.2f} %)")
    P_(f"    schedule changed by more than the toggled trade "
       f"(future_event_count_delta != -1): {int((LW['future_event_count_delta'] != -1).sum()):,}")
    P_(f"    size changed downstream in another session: "
       f"{int(LW['size_changed_downstream'].sum()):,}")

    # ---------------------------------------------------------------- G2
    P_("")
    P_("=" * 124)
    P_("=== 4. G2 - CONCENTRATION")
    P_("=" * 124)
    o_ = np.sort(np.abs(dav))[::-1]
    tot = o_.sum()
    P_(f"{'top share of events':<26}{'share of total |action value|':>34}")
    conc = {}
    for f in (0.01, G2_TOP, 0.10, 0.25):
        k = max(1, int(round(f * len(o_))))
        conc[f] = float(o_[:k].sum() / tot)
        P_(f"{100 * f:>6.0f} %{'':<19}{100 * conc[f]:>33.2f} %")

    # ---------------------------------------------------------------- G3
    P_("")
    P_("=" * 124)
    P_("=== 5. G3 - POWER.  Session-clustered MDE for a Q5-Q1 contrast an external model would sort")
    P_("=" * 124)
    icc, neff = icc_and_neff(dav, sess)
    sd = float(dav.std(ddof=1))
    mde = Z80 * sd * np.sqrt(2.0 / (neff / 5.0))
    P_(f"    sd(delta_action_value)                    ${sd:>12,.2f}")
    P_(f"    sessions (clusters)                        {len(np.unique(sess)):>12,}")
    P_(f"    mean cluster size                          {len(dav) / len(np.unique(sess)):>12.3f}")
    P_(f"    intra-session ICC                          {icc:>12.4f}")
    P_(f"    effective N after clustering               {neff:>12,.0f}  (raw {len(dav):,})")
    P_(f"    MDE for the Q5-Q1 CONTRAST at 80 % power  ${mde:>12,.2f}")
    P_(f"    materiality bar                           ${BAR:>12,.2f} per decision")
    P_("")
    P_("    >> UNITS DEFECT IN THE SPEC, found and fixed BEFORE this ledger was read.")
    P_("    The spec compares an MDE for a Q5-Q1 CONTRAST against a PER-DECISION materiality bar.")
    P_("    Those are not the same unit: a router that abstains on the bottom quintile does not")
    P_("    earn the contrast, it earns roughly 0.2 x (the amount by which Q1 sits below the mean).")
    P_("    Under a symmetric contrast that is 0.1 x MDE_contrast per decision. Both readings are")
    P_("    printed. The LITERAL spec reading is the binding gate; the corrected reading is")
    P_("    reported beside it because the gate's stated RATIONALE - 'if the smallest contrast we")
    P_("    could detect is larger than the improvement we would need to earn, the question is")
    P_("    UNDERPOWERED' - is a statement about policy value, not about a raw contrast.")
    mde_policy = 0.10 * mde
    P_(f"    G3  LITERAL  : MDE_contrast ${mde:,.2f}  vs bar ${BAR:,.2f}"
       f"   -> {'PASS' if mde <= BAR else 'FAIL'}")
    P_(f"    G3' CORRECTED: smallest DETECTABLE per-decision policy gain ${mde_policy:,.2f}"
       f"  vs bar ${BAR:,.2f}   -> {'PASS' if mde_policy <= BAR else 'FAIL'}")

    # ---------------------------------------------------------------- joint abstention curve
    P_("")
    P_("=" * 124)
    P_("=== 6. THE JOINT ABSTENTION CURVE - replayed, not summed.  Marginal values are NOT")
    P_("===    additive within a session, so the f-curve is computed by JOINT replay.")
    P_("=" * 124)

    # key on the ORIGINAL event index parsed from event_id, not on the DataFrame row position -
    # any event whose run could not be located was skipped when the ledger was built, so the two
    # are not the same thing.
    run_of = {}
    for _, row in L.iterrows():
        kk = int(str(row["event_id"]).split("-")[1])
        eti = i_of(row["decision_ts"])
        s = int(sid[eti])
        r = next((r for r in runs_in(p, fb, sess_lo[s], sess_hi[s]) if r[0] <= eti - 1 <= r[1]),
                 None)
        run_of[kk] = (s, r)

    base_net_arr = np.array([net_res(t) for t in BASE])
    base_eti_arr = np.array([t["eti"] for t in BASE])
    base_in = np.array([in_win[int(sid[e])] for e in base_eti_arr])
    base_total = float(base_net_arr[base_in].sum())
    # top-q % of baseline in-window events BY NET. At q = 1/5/10 every such event is a winner,
    # but the cut is over all events, which is what "top decile contribution" means here.
    win_thresh = {q: np.percentile(base_net_arr[base_in], 100 - q) for q in (1, 5, 10)}

    def joint(keys):
        p2 = p.copy()
        for k in keys:
            s, r = run_of[k]
            if r is not None:
                p2[r[0]:r[1] + 1] = 0
        new_ent = []
        for s in range(NS):
            new_ent.extend(t["eti"] for t in gfills_sess(D, p2, None, sess_lo[s], sess_hi[s]))
        ee2 = np.array([e for e in new_ent if A <= tarr[e] < B], dtype=np.int64)
        s2_, _ = causal_score(X, ee2, window=WIN)
        sz2 = score_to_size(s2_, n)
        TR = gfills(D, p2, size_at_entry=sz2, halt=HALT, target=TARGET, per_ctr=True)
        TR = [dict(t, eti=i_of(t["et"]), xti=i_of(t["xt"])) for t in TR]
        TR = [t for t in TR if in_win[int(sid[t["eti"]])]]
        return TR

    ordr = np.argsort(dav)          # most-negative action value first
    lw_idx = LW.index.to_numpy()
    Lidx_of_LW = {i: int(LW.loc[i, "event_id"].split("-")[1]) for i in LW.index}
    base_eti_set = set(int(e) for e in base_eti_arr[base_in])
    base_net_of = {int(e): float(v) for e, v in zip(base_eti_arr[base_in], base_net_arr[base_in])}
    curve = []

    def run_curve(order, label):
        P_("")
        P_(f"    RANKING: {label}")
        P_(f"{'f':>6}{'dropped':>9}{'net':>12}{'uplift':>12}{'uplift %':>10}{'trades':>8}"
           f"{'maxDD':>10}{'AVOIDED':>12}{'CREATED':>12}{'REPRICED':>11}{'created %':>11}"
           f"{'top10 kept':>12}{'top10 $':>10}")
        rows = []
        for f in FRACS:
            k = int(round(f * len(dav)))
            keys = [Lidx_of_LW[lw_idx[j]] for j in order[:k]]
            TR = joint(keys)
            net = float(sum(net_res(t) for t in TR))
            cf_net_of = {int(t["eti"]): net_res(t) for t in TR}
            cf_set = set(cf_net_of)
            kept = base_eti_set & cf_set
            removed = base_eti_set - cf_set
            created = cf_set - base_eti_set
            avoided = -float(sum(base_net_of[e] for e in removed))
            createdv = float(sum(cf_net_of[e] for e in created))
            repriced = float(sum(cf_net_of[e] - base_net_of[e] for e in kept))
            up = net - base_total
            # RIGHT-TAIL RETENTION, corrected. The earlier metric credited whatever trade now
            # starts at a baseline winner's entry bar AT ITS NEW SIZE, so it could exceed 100 %
            # and was not a retention rate. Report the COUNT that survives as the same trade and
            # the dollars those survivors carry at their NEW size, both explicitly.
            m = base_in & (base_net_arr >= win_thresh[10])
            tops = [int(e) for e in base_eti_arr[m]]
            keptn = sum(1 for e in tops if e in kept)
            dollars = float(sum(cf_net_of[e] for e in tops if e in kept))
            denom = float(sum(base_net_of[e] for e in tops))
            eq = np.cumsum([net_res(t) for t in TR])
            dd = float((np.maximum.accumulate(eq) - eq).max()) if len(eq) else 0.0
            rows.append(dict(ranking=label, f=f, k=k, net=net, uplift=up, trades=len(TR),
                             maxdd=dd, avoided=avoided, created=createdv, repriced=repriced,
                             n_created=len(created), n_removed=len(removed),
                             created_share=createdv / max(up, 1e-9),
                             top10_kept=keptn, top10_n=len(tops),
                             top10_dollar=dollars / denom if denom else np.nan))
            P_(f"{f:>6.2f}{k:>9,}{net:>12,.0f}{up:>12,.0f}{100 * up / abs(base_total):>9.1f}%"
               f"{len(TR):>8,}{dd:>10,.0f}{avoided:>12,.0f}{createdv:>12,.0f}{repriced:>11,.0f}"
               f"{100 * createdv / max(up, 1e-9):>10.1f}%{keptn:>7,}/{len(tops):<4,}"
               f"{100 * dollars / denom:>9.1f}%")
        return rows

    curve += run_curve(ordr, "by CAUSAL action value (the object this wave built)")
    curve += run_curve(np.argsort(own), "by the trade's OWN net (what W122's simpler ledger already had)")
    eqb = np.cumsum(base_net_arr[base_in])
    ddb = float((np.maximum.accumulate(eqb) - eqb).max())
    P_("")
    P_(f"    BASELINE: net ${base_total:,.0f}   trades {int(base_in.sum()):,}   maxDD ${ddb:,.0f}")
    P_("")
    P_("    ⚠ THE CURVE IS NOT PURE ABSTENTION. 'CREATED' is the P&L of trades the frozen policy")
    P_("    takes because the session box no longer LATCHES once a bad early decision is removed.")
    P_("    Those entries are not decision events in the ledger at all - they are the r0+1 bars of")
    P_("    latched-out runs. A large share of the headline uplift is REGENERATION, not avoidance,")
    P_("    and that is a statement about the BOX POLICY rather than about action-value routing.")
    P_("")
    P_("    ⚠ THE OWN-NET RANKING IS THE CONTROL THAT MATTERS. It uses only the trade's own P&L -")
    P_("    the label W122's ledger already carried - and needs none of this wave's machinery.")
    P_("    Whatever the causal ranking earns ABOVE it is the true incremental value of the")
    P_("    counterfactual replay for the purpose of choosing which actions to drop.")
    pd.DataFrame(curve).to_csv(os.path.join(OUT, "abstention_curve.csv"), index=False)

    # ---------------------------------------------------------------- G4
    P_("")
    P_("=" * 124)
    P_("=== 7. G4 - STABILITY of the f = 20 % abstention value, by calendar bucket")
    P_("=" * 124)
    yr = pd.to_datetime(LW["session_date"]).dt.year.to_numpy()
    P_(f"{'bucket':<12}{'events':>9}{'mean action value':>20}{'f=20% abstention value':>26}{'sign':>8}")
    ybuckets = []
    for y in sorted(set(yr)):
        m = yr == y
        dv = dav[m]
        kk = int(round(0.20 * len(dv)))
        val = float(-np.sort(dv)[:kk].sum()) if kk else 0.0
        ybuckets.append((y, len(dv), float(dv.mean()), val))
        P_(f"{y:<12}{len(dv):>9,}{dv.mean():>19,.2f}{val:>26,.0f}{'+' if val > 0 else '-':>8}")
    npos = sum(1 for _, _, _, v in ybuckets if v > 0)
    P_("")
    P_(f"    positive buckets: {npos} of {len(ybuckets)}")
    P_(f"    NOTE the spec wrote 'at least 3 of the 4 calendar years 2022(H2)-2026(H1)'. There are")
    P_(f"    {len(ybuckets)} buckets, not 4 - 2022 and 2026 are half years. The binding threshold is")
    P_(f"    the number 3, which is unchanged; only the arithmetic slip in the label is corrected.")
    P_(f"    Within-bucket f=20% values are ex-post SUMS OF MARGINALS, not joint replays - stated.")

    # ---------------------------------------------------------------- B oracle
    P_("")
    P_("=" * 124)
    P_("=== 8. SESSION_POLICY_ORACLE (level B) - best subset of a session's decisions, ex post")
    P_("=== FROZEN-SIZE arm: the baseline size array is reused, so a run that the box had latched")
    P_("=== out and that this oracle re-enables carries size 1. Stated, not hidden.")
    P_("=" * 124)
    b_gain = 0.0
    b_sess = 0
    skipped = 0
    skipped_tr = 0
    base_sess_net = {}
    for t in BASE:
        s = int(sid[t["eti"]])
        base_sess_net[s] = base_sess_net.get(s, 0.0) + net_res(t)
    for s in range(NS):
        if not in_win[s]:
            continue
        rs = runs_in(p, fb, sess_lo[s], sess_hi[s])
        if len(rs) == 0:
            continue
        if len(rs) > B_CAP:
            skipped += 1
            skipped_tr += sum(1 for t in BASE if int(sid[t["eti"]]) == s)
            continue
        best = base_sess_net.get(s, 0.0)
        p2 = p.copy()
        for mask in itertools.product([0, 1], repeat=len(rs)):
            if not any(mask):
                continue
            for bit, (r0, r1) in zip(mask, rs):
                if bit:
                    p2[r0:r1 + 1] = 0
            v = sum(net_res(t) for t in gfills_sess(D, p2, sz, sess_lo[s], sess_hi[s]))
            best = max(best, v)
            for bit, (r0, r1) in zip(mask, rs):
                if bit:
                    p2[r0:r1 + 1] = p[r0:r1 + 1]
        b_gain += best - base_sess_net.get(s, 0.0)
        b_sess += 1
    P_(f"    sessions enumerated              {b_sess:>10,}")
    P_(f"    sessions SKIPPED (> {B_CAP} runs)      {skipped:>10,}   holding {skipped_tr:,} baseline trades")
    enum_base = sum(v for s, v in base_sess_net.items()
                    if in_win[s] and 0 < len(runs_in(p, fb, sess_lo[s], sess_hi[s])) <= B_CAP)
    P_(f"    B - baseline, summed over ENUMERATED sessions   ${b_gain:>12,.0f}")
    P_(f"    baseline net over the ENUMERATED sessions only  ${enum_base:>12,.0f}")
    P_(f"    baseline net over ALL in-window sessions        ${base_total:>12,.0f}")
    P_(f"    LIKE-FOR-LIKE multiple (enumerated only)         {(enum_base + b_gain) / enum_base:>12.3f}x")
    P_(f"    (an earlier version divided the enumerated GAIN by the ALL-SESSION net and printed")
    P_(f"     3.624x. That mixed populations; the like-for-like figure above is the correct one.)")

    # ---------------------------------------------------------------- XM + FM + C
    P_("")
    P_("=" * 124)
    P_("=== 9. XM_CONFLICT and FOLLOW_MORNING ledgers, and CONSTRAINED_PORTFOLIO_ORACLE (level C)")
    P_("=" * 124)
    XM = pd.read_csv(XMREF)
    XM["session_date"] = pd.to_datetime(XM["session_date"])
    XM = XM[(XM["session_date"] >= "2022-07-01") & (XM["session_date"] < "2026-08-01")]
    xt = XM[(XM["desired_direction"] != 0) & (XM["disqualified"] == 0)].copy()
    # CORRECTED after adversarial audit. An earlier version of this file asserted the reference
    # pnl columns were COMMISSION-ONLY and subtracted $12.50, which DOUBLE-CHARGED the spread.
    # export_xm_reference.py:117 computes cst_c = COMM_RT + TICKV*(prof[ENTM]+prof[EXITM])/2
    # = 4.36 + 12.50 = 16.86 and subtracts it at line 121. Verified numerically: gross minus
    # pnl_research is CONSTANT $16.8600 on all 346 taken rows. The ~$0.95 gap between the two pnl
    # columns is the 15:45-close vs 15:46-open EXIT CONVENTION (cst_c vs cst_n), not a missing
    # spread. pnl_research is therefore already the research cost model and is used as-is.
    xm_sp = TICKV * (prof_d[9 * 60 + 46] + prof_d[15 * 60 + 45]) / 2.0
    P_(f"    XM modelled spread at its own fill minutes ${xm_sp:.2f}/ctrRT is ALREADY inside")
    P_(f"    pnl_research (export_xm_reference.py:117, cst = $4.36 + $12.50 = $16.86, verified as a")
    P_(f"    constant $16.8600 gross-minus-net on all 346 rows). No further charge is applied.")
    xt["net_research"] = xt["pnl_research"]
    xt["delta_action_value"] = xt["net_research"]
    P_(f"    XM taken decisions {len(xt):,}   net ${xt['net_research'].sum():,.0f}   "
       f"mean ${xt['net_research'].mean():,.2f}   share positive "
       f"{100 * (xt['net_research'] > 0).mean():.2f} %")
    P_(f"    XM action value == trade P&L EXACTLY (one shot, no box, no latch, size 1) - the")
    P_(f"    counterfactual is trivial and this is a structural fact, not a measurement.")
    xt[["session_date", "desired_direction", "nq_drive", "broad_composite",
        "pnl_research", "net_research", "delta_action_value"]].to_csv(
        os.path.join(OUT, "ledger_xm.csv"), index=False)

    try:
        from run_we_w114 import Win, DEC, EXIT
        Wfm = Win("2022-07-01", "2026-07-31 17:00", True, "MODERN")
        Rfm = Wfm.run(DEC, EXIT, Wfm.morn_dir())
        fm_pnl = Rfm["pnl"][Rfm["take"]]
        fm_dates = pd.to_datetime(Wfm.D["sess_date"])[Rfm["take"]]
        P_(f"    FM taken decisions {len(fm_pnl):,}   net ${fm_pnl.sum():,.0f}   "
           f"mean ${fm_pnl.mean():,.2f}   share positive {100 * (fm_pnl > 0).mean():.2f} %")
        pd.DataFrame(dict(session_date=fm_dates, delta_action_value=fm_pnl)).to_csv(
            os.path.join(OUT, "ledger_fm.csv"), index=False)
        fm_ok = True
    except Exception as e:                                          # noqa: BLE001
        P_(f"    FOLLOW_MORNING could not be reconstructed: {e}")
        fm_pnl = np.array([]); fm_ok = False

    c_extra = float(np.maximum(xt["net_research"].to_numpy(), 0).sum() - xt["net_research"].sum())
    if fm_ok:
        c_extra += float(np.maximum(fm_pnl, 0).sum() - fm_pnl.sum())
    P_("")
    P_(f"    LEVEL C decomposes additively: the three experts hold independent positions with no")
    P_(f"    shared state, so the best portfolio subset per session is the per-expert best.")
    P_(f"    C - (B + XM + FM as run) = ${c_extra:,.0f}   (the value of ex-post abstention on the")
    P_(f"    two one-shot experts). Stated as a CEILING.")

    # ---------------------------------------------------------------- portfolio-relative
    P_("")
    P_("=" * 124)
    P_("=== 10. PORTFOLIO-RELATIVE MARGINAL VALUE (directive section 14)")
    P_("=" * 124)
    wk_p1 = pd.Series(own, index=pd.to_datetime(LW["session_date"])).resample("W").sum()
    xw = pd.Series(xt["net_research"].to_numpy(),
                   index=pd.to_datetime(xt["session_date"])).resample("W").sum()
    both = pd.concat([wk_p1.rename("p1"), xw.rename("xm")], axis=1).fillna(0.0)
    sd1, sd2 = both["p1"].std(ddof=1), both["xm"].std(ddof=1)
    w1 = (1 / sd1) / ((1 / sd1) + (1 / sd2))
    P_(f"    inverse-vol weights on WEEKLY sums: w(P1/PCT) = {w1:.6f}  w(XM) = {1 - w1:.6f}")
    P_(f"    (same construction as WE_W110_XMDIVERSE/out/weekly.csv; weights inherited, not")
    P_(f"     re-derived on a different window - W119 constraint)")
    P_(f"    weekly rho(P1, XM) = {both['p1'].corr(both['xm']):.4f}")
    P_(f"    A P1 action's book-marginal value is w1 x its action value; an XM action's is")
    P_(f"    (1-w1) x its own. The ORDERING of P1 events is therefore unchanged by the weighting,")
    P_(f"    so no separate book ranking is produced - stating this rather than printing a")
    P_(f"    rescaled copy of the same column.")

    # ---------------------------------------------------------------- GATES
    P_("")
    P_("=" * 124)
    P_("=== 11. THE PREREGISTERED GATE TABLE.  Every clause is a coded assertion.")
    P_("=" * 124)
    # --- audit-driven diagnostics printed WITH the gate table, not instead of it ---
    k5 = max(1, int(round(G2_TOP * len(dav))))
    absord = np.argsort(np.abs(dav))[::-1]        # ONE ranking, by |action value|
    top_idx, rest_idx = absord[:k5], absord[k5:]
    top_sum = float(dav[top_idx].sum())
    rest_sum = float(dav[rest_idx].sum())
    top5_sum_share = top_sum / dav.sum()
    biggest = float(dav[absord[0]])

    g = [
        ("G1", f"share with |dAV - own net| > ${G1_DOLLARS:.0f} exceeds {100*G1_SHARE:.0f} %",
         f"{100 * share_diff:.2f} %", share_diff > G1_SHARE),
        ("G2", f"top {100*G2_TOP:.0f} % of events hold < {100*G2_MAX:.0f} % of |action value|",
         f"{100 * conc[G2_TOP]:.2f} %", conc[G2_TOP] < G2_MAX),
        ("G3", "session-clustered Q5-Q1 MDE <= materiality bar (LITERAL spec reading)",
         f"${mde:,.2f} vs ${BAR:,.2f}", mde <= BAR),
        ("G3'", "smallest DETECTABLE per-decision policy gain <= bar (units-corrected)",
         f"${0.10 * mde:,.2f} vs ${BAR:,.2f}", 0.10 * mde <= BAR),
        ("G4", f"f=20 % abstention value positive in >= {G4_MIN_POS_BUCKETS} calendar buckets",
         f"{npos} of {len(ybuckets)}", npos >= G4_MIN_POS_BUCKETS),
    ]
    P_(f"{'gate':<6}{'spec':<62}{'observed':>28}{'verdict':>10}")
    for gg, spec, obsv, ok in g:
        P_(f"{gg:<6}{spec:<62}{obsv:>28}{('PASS' if ok else 'FAIL'):>10}")
    pd.DataFrame([dict(gate=x[0], spec=x[1], observed=x[2], verdict="PASS" if x[3] else "FAIL")
                  for x in g]).to_csv(os.path.join(OUT, "gates.csv"), index=False)
    P_("")
    allp = all(x[3] for x in g)
    P_(f"    ALL GATES: {'PASS' if allp else 'NOT ALL PASS'}")
    P_("")
    P_("=" * 124)
    P_("=== 11b. GATE INTEGRITY - what an adversarial audit found wrong with these gates.")
    P_("=== Recorded here rather than by quietly restating the gates. No coded clause was changed.")
    P_("=" * 124)
    P_("    G4 IS VOID. It cannot fail. Its statistic is minus the sum of the most-negative 20 % of")
    P_(f"    action values, and {100 * (dav < 0).mean():.2f} % of all action values are negative, so every")
    P_("    bucket's bottom quintile is entirely negative and the statistic is positive by")
    P_("    arithmetic. Largest element of each bucket's bottom quintile:")
    yy = pd.to_datetime(LW["session_date"]).dt.year.to_numpy()
    for y in sorted(set(yy)):
        dv = dav[yy == y]
        kk = max(1, int(round(0.2 * len(dv))))
        P_(f"        {y}: ${np.sort(dv)[:kk].max():>12,.2f}   (all negative: {np.sort(dv)[:kk].max() < 0})")
    P_("    '5 of 5' therefore carries ZERO evidential content. This is exactly the un-failable-gate")
    P_("    error the spec's own why_the_raw_oracle_is_NOT_the_gate section forbids. G4 is recorded")
    P_("    VOID, not PASS. Stability is NOT established by this wave.")
    P_("")
    P_("    G2 PASSES ITS CODED CLAUSE AND FAILS ITS OWN RATIONALE. The clause measures the top 5 %")
    P_("    share of TOTAL ABSOLUTE action value (39.28 %). The rationale asks whether 'essentially")
    P_("    all of it sits in ~100 events' - which is a question about the SUM a router would earn:")
    P_(f"        top {k5} events by |action value| contribute ${top_sum:,.0f} "
       f"= {100 * top5_sum_share:.1f} % of the ${dav.sum():,.0f} SUM")
    P_(f"        the remaining {len(rest_idx):,} events sum to ${rest_sum:,.0f} "
       f"(mean ${rest_sum / len(rest_idx):,.2f} per decision)")
    P_(f"        single largest |action value| event = ${biggest:,.0f} = "
       f"{100 * biggest / dav.sum():.2f} % of the total sum")
    P_("    By the economically relevant measure the concentration condition IS met. G2 is recorded")
    P_("    PASS-ON-CLAUSE / FAIL-ON-RATIONALE and must not be quoted as a clean pass.")
    P_("")
    P_("    G3 IS TOO GENEROUS BY sqrt(2). The 0.1x conversion is valid only if Q1 and Q5 are")
    P_("    constrained symmetric about the mean, which borrows precision from Q5 that a router")
    P_("    abstaining on Q1 does not have. Assumption-free: MDE_gain = 0.2 * Z80 * sd / sqrt(neff/5).")
    mde_free = 0.2 * Z80 * sd / np.sqrt(neff / 5.0)
    P_(f"        symmetric (as coded)   ${0.1 * mde:>10,.2f}")
    P_(f"        assumption-free        ${mde_free:>10,.2f}   = sqrt(2) x the above")
    P_(f"        materiality bar        ${BAR:>10,.2f}")
    P_(f"    G3 fails under BOTH ({mde_free / BAR:.1f}x the bar assumption-free). The failure is robust.")
    P_(f"{el()} done")
    _fh.close()


if __name__ == "__main__":
    main()
