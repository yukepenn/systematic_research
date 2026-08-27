"""RR_W001 - THE ACTION-VALUE LEDGER.

Spec: runs/RR_W001_ACTION_VALUE_LEDGER/spec.yaml, committed at f3dd814 BEFORE this file existed.
prereg_guard check --run-class DIAGNOSTIC passed against that commit.

NO MODEL IS FITTED IN THIS WAVE. No feature is selected, no threshold tuned, no policy proposed.

The frozen policy is IMPORTED from run_we_w98.gfills, never reimplemented, so a divergence cannot
be a transcription bug in the reference. FOLLOW_MORNING is imported from run_we_w114.Win for the
same reason. The one piece of new machinery - a SESSION-SCOPED replay - is certified byte-for-byte
against the full-pass engine in Phase 0, before any counterfactual arm is read.

Usage:
    python run_rr_w001.py --certify        # Phase 0 only, blocking gate
    python run_rr_w001.py                  # full wave
"""
from __future__ import annotations

import argparse
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
from run_we_w98 import gfills, same, TICKV                                # noqa: E402
from we_fastctx import fast_build_context                                 # noqa: E402

RUN = os.path.join(ROOT, "runs", "RR_W001_ACTION_VALUE_LEDGER")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
W82OUT = os.path.join(ROOT, "runs", "WE_W82_FILLAUDIT", "out")
XMREF = os.path.join(ROOT, "research", "weekly_edge", "ninjascript", "reference",
                     "xm_reference_decisions.csv")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
HALT, TARGET = 1300.0, 1000.0
MATERIALITY = 0.10
Z80 = 1.959963985 + 0.8416212     # two-sided alpha 0.05 + 80 % power
G1_DOLLARS, G1_SHARE = 50.0, 0.10
G2_TOP, G2_MAX = 0.05, 0.80
G4_YEARS = 3
B_CAP = 8
FRACS = [0.05, 0.10, 0.20, 0.30]

_t0 = _time.time()
_fh = None


def P_(*a):
    print(*a, flush=True)
    if _fh is not None:
        print(*a, file=_fh)
        _fh.flush()


def el():
    return f"[{_time.time() - _t0:6.0f}s]"


def gfills_sess(D, dir_arr, size_at_entry, lo, hi, halt=HALT, target=TARGET, per_ctr=True):
    """run_we_w98.gfills restricted to bars [lo, hi]. CERTIFIED byte-identical in Phase 0."""
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb = D["fb"], D["lb"]
    trades = []
    p = 0; u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False
    for i in range(lo, hi + 1):
        if fb[i]:
            spnl = 0.0; stopped = False
        want = int(dir_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped:
            want = 0
        if want != p:
            if p != 0:
                pnl = p * u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=p, u=u, eti=eti, xti=i, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += (pnl / u) if per_ctr else pnl
                if spnl <= -halt or (target is not None and spnl >= target):
                    stopped = True; want = 0
            p = want
            if p != 0:
                u = int(size_at_entry[i]) if size_at_entry is not None else 1
                if u < 1:
                    p = 0; u = 0
                else:
                    epx, eti = o[i], i
        if lb[i] and p != 0:
            pnl = p * u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=p, u=u, eti=eti, xti=i, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            p = 0; u = 0
    return trades


def runs_in(dir_arr, fb, lo, hi):
    out = []
    i = lo
    while i <= hi:
        if dir_arr[i] == 0:
            i += 1
            continue
        j = i
        while j + 1 <= hi and dir_arr[j + 1] == dir_arr[i] and not fb[j + 1]:
            j += 1
        out.append((i, j))
        i = j + 1
    return out


def score_to_size(s_, n):
    sz = np.ones(n, np.int8)
    sz[s_ >= 3] = 2
    return sz


def icc_and_neff(vals, groups):
    """one-way random-effects ICC and the session-clustered effective N."""
    df = pd.DataFrame(dict(v=vals, g=groups))
    k = df.groupby("g")["v"].size()
    if len(k) < 2:
        return 0.0, float(len(vals))
    gm = df["v"].mean()
    means = df.groupby("g")["v"].mean()
    msb = float((k * (means - gm) ** 2).sum() / (len(k) - 1))
    msw_num = float(((df["v"] - df["g"].map(means)) ** 2).sum())
    dfw = len(df) - len(k)
    msw = msw_num / dfw if dfw > 0 else 0.0
    k0 = float((len(df) - (k ** 2).sum() / len(df)) / (len(k) - 1))
    icc = 0.0 if (msb + (k0 - 1) * msw) == 0 else max(0.0, (msb - msw) / (msb + (k0 - 1) * msw))
    mbar = float(k.mean())
    neff = len(df) / (1.0 + (mbar - 1.0) * icc)
    return icc, neff


def main(certify_only: bool, limit: int = 0):
    global _fh
    _fh = open(os.path.join(OUT, "certify.txt" if certify_only else "rr_w001.txt"),
               "w", encoding="utf-8")

    P_("=" * 124)
    P_("=== RR_W001 - ACTION-VALUE LEDGER.  Spec f3dd814.  NO MODEL IS FITTED IN THIS WAVE.")
    P_("=== A / B / C are EX-POST CEILINGS, never 'opportunity'. A - E is NOT money we failed to")
    P_("=== collect. OPPORTUNITY_LANGUAGE.md is binding and this is the error it exists to prevent.")
    P_("=" * 124)

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    X = fast_build_context(D)
    zz = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    vl, _ = votes(D, zz["mem"], zz["bmom"], zz["tilt"], X, zz["bmom"])
    p = vl.astype(np.int8)
    n, tarr, sid, fb, lb = D["n"], D["t"], D["sid"], D["fb"], D["lb"]
    hi_px, lo_px, o_px = D["h"], D["l"], D["o"]
    P_(f"{el()} substrate {n:,} bars / {D['n_sess']:,} sessions")

    sess_lo = {int(sid[i]): int(i) for i in np.flatnonzero(fb)}
    sess_hi = {int(sid[i]): int(i) for i in np.flatnonzero(lb)}
    NS = D["n_sess"]

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    prof = pd.read_csv(os.path.join(W82OUT, "spread_by_minute.csv")).set_index("mod")["sp_tk"]
    prof_d = {int(k): float(v) for k, v in prof.items()}
    modarr = np.array([pd.Timestamp(x).hour * 60 + pd.Timestamp(x).minute for x in tarr])
    spk = np.array([prof_d.get(int(m), 3.0) for m in modarr])

    def spread_cost(tr):
        return tr["u"] * TICKV * (spk[tr["eti"]] + spk[tr["xti"]]) / 2.0

    def net_res(tr):
        return tr["pnl"] - spread_cost(tr)

    # ---------------- baseline
    bb = fills_daily(D, p, halt=HALT, target=TARGET)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    s_, sc_ent = causal_score(X, ee, window=WIN)
    # sc_ent carries NaN for the MINHIST warm-up; the per-bar array zero-fills it and so cannot
    # distinguish 'unscored' from 'score = 0'. Keep the distinction explicitly.
    warm = {int(e): bool(np.isnan(v)) for e, v in zip(ee, sc_ent)}
    scent = {int(e): (None if np.isnan(v) else float(v)) for e, v in zip(ee, sc_ent)}
    sz = score_to_size(s_, n)
    BASE_full = gfills(D, p, size_at_entry=sz, halt=HALT, target=TARGET, per_ctr=True)
    P_(f"{el()} baseline: fills_daily {len(bb):,}, causal_score on {len(ee):,}, "
       f"gfills {len(BASE_full):,}")

    # ===================================================================== PHASE 0
    P_("")
    P_("=" * 124)
    P_("=== PHASE 0 - REPLAY CERTIFICATION.  BLOCKING.")
    P_("=" * 124)
    checks = []
    checks.append(("H-A", "gfills is deterministic (byte-identical on repeat)",
                   f"{len(BASE_full):,} trades",
                   same(BASE_full, gfills(D, p, size_at_entry=sz, halt=HALT, target=TARGET,
                                          per_ctr=True))))
    SCH1 = {s: gfills_sess(D, p, None, sess_lo[s], sess_hi[s]) for s in range(NS)}
    stitched = []
    for s in range(NS):
        stitched.extend(gfills_sess(D, p, sz, sess_lo[s], sess_hi[s]))
    st_cmp = [{k: v for k, v in x.items() if k in ("d", "u", "et", "xt", "pnl")} for x in stitched]
    nmis = (sum(1 for a_, b_ in zip(BASE_full, st_cmp)
                if a_["et"] != b_["et"] or a_["xt"] != b_["xt"] or a_["u"] != b_["u"]
                or abs(a_["pnl"] - b_["pnl"]) > 1e-9) if len(BASE_full) == len(st_cmp) else -1)
    checks.append(("H-B", "session-scoped replay == full pass, byte for byte",
                   f"{len(st_cmp):,} vs {len(BASE_full):,}, {nmis} mismatches",
                   same(BASE_full, st_cmp)))
    sched_g = [(x["et"], x["xt"], x["d"]) for x in BASE_full]
    sched_f = [(x["et"], x["xt"], x["d"]) for x in bb]
    checks.append(("H-C", "trade SCHEDULE is size-invariant (gfills == fills_daily)",
                   f"equal={sched_g == sched_f}", sched_g == sched_f))
    T1 = gfills(D, p, size_at_entry=np.ones(n, np.int8), halt=HALT, target=TARGET, per_ctr=True)
    T2 = gfills(D, p, size_at_entry=np.full(n, 2, np.int8), halt=HALT, target=TARGET, per_ctr=True)
    lin_ok = (len(T1) == len(T2)
              and all(a_["et"] == b_["et"] and a_["xt"] == b_["xt"] for a_, b_ in zip(T1, T2))
              and all(abs(b_["pnl"] - 2.0 * a_["pnl"]) < 1e-9 for a_, b_ in zip(T1, T2)))
    checks.append(("H-D", "doubling size doubles P&L and moves no schedule (re-pricing exact)",
                   f"{len(T1):,} vs {len(T2):,} trades", lin_ok))
    in_win = np.zeros(NS, bool)
    for s in range(NS):
        if A <= tarr[sess_lo[s]] < B:
            in_win[s] = True
    n_sf = sum(1 for x in stitched if in_win[int(sid[x["eti"]])])
    n_tf = sum(1 for x in stitched if A <= tarr[x["eti"]] < B)
    checks.append(("H-E", "populations: 2,401 total / 2,131 session-filter / 2,139 ts-filter",
                   f"{len(stitched):,} / {n_sf:,} / {n_tf:,}",
                   len(stitched) == 2401 and n_sf == 2131 and n_tf == 2139))
    P_(f"{'check':<7}{'assertion':<64}{'observed':>36}{'verdict':>9}")
    for cid, desc, obsv, ok in checks:
        P_(f"{cid:<7}{desc:<64}{obsv:>36}{('PASS' if ok else 'FAIL'):>9}")
    allok = all(c[3] for c in checks)
    P_("")
    P_(f"    CERTIFICATION: {'PASS' if allok else 'FAIL - STOP. Fix the simulator. Interpret nothing.'}")
    pd.DataFrame([dict(check=c[0], assertion=c[1], observed=c[2],
                       verdict="PASS" if c[3] else "FAIL") for c in checks]).to_csv(
        os.path.join(OUT, "certification.csv"), index=False)
    if not allok:
        _fh.close(); sys.exit(1)
    if certify_only:
        P_(f"\n{el()} --certify: stopping. No counterfactual arm was read.")
        _fh.close(); return

    tot_ctr = sum(x["u"] for x in stitched)
    tot_sp = sum(spread_cost(x) for x in stitched)
    P_("")
    P_(f"    cost reconciliation: modelled spread ${tot_sp / tot_ctr:.2f}/ctrRT over {tot_ctr:,} "
       f"contract-RTs (CURRENT_BASELINE records $14.44 for P1)")

    # ===================================================================== PHASE 1
    P_("")
    P_("=" * 124)
    P_("=== PHASE 1 - P1/PCT ACTION-VALUE LEDGER.  One row per genuine decision event.")
    P_("=" * 124)

    base_ent_all = [t["eti"] for s in range(NS) for t in SCH1[s]]   # size-1 schedule, global order
    sess_of_ent = [int(sid[e]) for e in base_ent_all]
    idx_by_sess = {}
    for j, s in enumerate(sess_of_ent):
        idx_by_sess.setdefault(s, []).append(j)

    base_net = np.array([net_res(x) for x in stitched])
    base_pc = np.array([net_res(x) / x["u"] for x in stitched])
    base_eti = np.array([x["eti"] for x in stitched])
    base_sess = np.array([int(sid[e]) for e in base_eti])
    sess_net = {}
    for i2, s in enumerate(base_sess):
        sess_net[s] = sess_net.get(s, 0.0) + base_net[i2]

    def mae_mfe(tr):
        a_, b_ = tr["eti"], tr["xti"]
        if b_ < a_:
            return 0.0, 0.0
        sl, sh = float(lo_px[a_:b_ + 1].min()), float(hi_px[a_:b_ + 1].max())
        d_, epx, u_ = tr["d"], o_px[a_], tr["u"]
        if d_ > 0:
            return (sl - epx) * PV * u_, (sh - epx) * PV * u_
        return (epx - sh) * PV * u_, (epx - sl) * PV * u_

    assert base_ent_all == list(base_eti), "size-1 and sized schedules disagree (H-C should have caught this)"

    # entry ordinal and the session box state the engine actually carried into each decision
    ordinal, box_before, stopped_before = {}, {}, {}
    cnt, acc = {}, {}
    for k, x in enumerate(stitched):
        s = int(sid[x["eti"]])
        cnt[s] = cnt.get(s, 0) + 1
        ordinal[k] = cnt[s]
        box_before[k] = acc.get(s, 0.0)                       # per-contract, engine-native
        stopped_before[k] = int(acc.get(s, 0.0) <= -HALT or acc.get(s, 0.0) >= TARGET)
        acc[s] = acc.get(s, 0.0) + x["pnl"] / x["u"]          # gfills: spnl += pnl/u under per_ctr

    p_work = p.copy()
    rows = []
    todo = stitched[:limit] if limit else stitched
    for k, x in enumerate(todo):
        s = int(sid[x["eti"]])
        lo_s, hi_s = sess_lo[s], sess_hi[s]
        sig = x["eti"] - 1
        run = next((r for r in runs_in(p, fb, lo_s, hi_s) if r[0] <= sig <= r[1]), None)
        if run is None:
            continue
        r0, r1 = run
        saved = p_work[r0:r1 + 1].copy()
        p_work[r0:r1 + 1] = 0

        cf_sched = gfills_sess(D, p_work, None, lo_s, hi_s)
        new_ent = list(base_ent_all)
        js = idx_by_sess.get(s, [])
        if js:
            new_ent = new_ent[:js[0]] + [t["eti"] for t in cf_sched] + new_ent[js[-1] + 1:]
        ee2 = np.array([e for e in new_ent if A <= tarr[e] < B], dtype=np.int64)
        s2_, _ = causal_score(X, ee2, window=WIN) if len(ee2) else (np.zeros(n), None)
        sz2 = score_to_size(s2_, n)
        cf_tr = gfills_sess(D, p_work, sz2, lo_s, hi_s)
        cf_tr_fz = gfills_sess(D, p_work, sz, lo_s, hi_s)

        cf_net = sum(net_res(t) for t in cf_tr)
        cf_net_fz = sum(net_res(t) for t in cf_tr_fz)
        d_av = cf_net - sess_net.get(s, 0.0)
        d_av_fz = cf_net_fz - sess_net.get(s, 0.0)

        outside = base_sess != s
        du = sz2[base_eti[outside]].astype(np.int16) - sz[base_eti[outside]].astype(np.int16)
        d_outside = float(np.sum(du * base_pc[outside]))
        size_changed = bool(np.any(du != 0))

        mae, mfe = mae_mfe(x)
        cf_mae = min((mae_mfe(t)[0] for t in cf_tr), default=0.0)
        cf_mfe = max((mae_mfe(t)[1] for t in cf_tr), default=0.0)

        rows.append(dict(
            event_id=f"P1PCT-{k:05d}", expert_id="P1PCT", family_id="SOLAR_RATCHET_ENSEMBLE",
            session_date=str(pd.Timestamp(tarr[x["eti"]]).date()), session_id=s,
            decision_ts=x["et"], info_cutoff_ts=str(tarr[sig]),
            entry_ordinal_in_session=ordinal[k], eligible=1, baseline_action="ACCEPT",
            baseline_qty=x["u"], side=x["d"], in_window_session=bool(in_win[s]),
            causal_quality_score=scent.get(int(x["eti"])),
            quality_score_is_warmup=int(warm.get(int(x["eti"]), False)),
            in_scoring_population=int(int(x["eti"]) in scent),
            size_at_entry=int(sz[x["eti"]]),
            strategy_session_pnl_before_per_ctr=float(box_before[k]),
            box_stopped_before=int(stopped_before[k]),
            baseline_trade_net=float(net_res(x)), baseline_trade_pnl_commonly=float(x["pnl"]),
            baseline_session_net=float(sess_net.get(s, 0.0)), baseline_mae=mae, baseline_mfe=mfe,
            baseline_hold_minutes=int(x["xti"] - x["eti"]),
            cf_session_net=float(cf_net), cf_trade_count_in_session=len(cf_tr),
            cf_mae=cf_mae, cf_mfe=cf_mfe,
            delta_action_value=float(-d_av),          # value OF ACTING = base - cf
            delta_action_value_frozen=float(-d_av_fz),
            delta_outside_session=float(-d_outside),
            delta_total_window=float(-(d_av + d_outside)),
            future_event_count_delta=len(cf_tr) - int((base_sess == s).sum()),
            schedule_changed=1, size_changed_downstream=int(size_changed),
            cost_model_id="COMMISSION_PLUS_MODELLED_SPREAD"))
        p_work[r0:r1 + 1] = saved
        if (k + 1) % 400 == 0:
            P_(f"{el()}   ... {k + 1:,} / {len(todo):,} decision events replayed")

    L = pd.DataFrame(rows)
    L.to_csv(os.path.join(OUT, "ledger_p1pct%s.csv" % ("_SMOKE" if limit else "")), index=False)
    P_(f"{el()} P1/PCT ledger: {len(L):,} rows written")
    np.save(os.path.join(OUT, "_base_pc.npy"), base_pc)
    L.to_pickle(os.path.join(OUT, "_L.pkl"))
    P_(f"{el()} PHASE 1 complete. Ledger persisted; analysis continues in run_rr_w001b.py")
    _fh.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--certify", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a_ = ap.parse_args()
    main(a_.certify, a_.limit)
