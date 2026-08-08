"""SMV2AD sub_417 -- old-regime screen (DIAGNOSTIC, non-adoption). Per spec: run for
EVERY arm across sub_415/416 that qualifies as a CANDIDATE (ceiling or extension).

sub_415 produced ZERO CEILING-CANDIDATEs (see out/sub415_verdict.json) and sub_416
produced ZERO EXTENSION-CANDIDATEs (see out/sub416_verdict.json) -- every arm in both
sub-tests failed the standalone Sharpe-AND-CDaR_0.95 verdict rule on dev. There is
therefore NOTHING TO SCREEN this wave: the screen is explicitly conditional on the
wave producing >=1 CANDIDATE, and none did. This is disclosed here (not silently
skipped) with the exact reason, and out/old_regime_screen.csv is still written (one
NONE_QUALIFIED row) so the required output artifact exists.

If a future wave revisits this lead with a genuinely new mechanism and produces a
CANDIDATE, this script's rebuild machinery (SM06 hist substrate, SMV2H2-gate-B
executor convention: close-only, decisions at 3m close, fills at next 3m bar close
+-1 tick uncapped, session-close flatten at last-bar close +-1 tick, ops windows
16:30-18:03, NQ costs $2.18/side, PV $20 -- verbatim runs/SMV2T_NOFAST_R2/gate_C.py)
is retained below as CANDIDATE_SCREEN(), parameterized by (vms, smax_ticks), ready
to run against whichever arm(s) qualify.
"""
import sys, os, json, time
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, OUT
import sm01_solarsim as sm

TICK = 0.25; COMM = 2.18; PV = 20.0


def run_policy_hist(df, desired, comm, pv):
    """Verbatim runs/SMV2T_NOFAST_R2/gate_C.py run_policy_hist (SMV2H2 gate-B
    executor convention on the close-only hist substrate)."""
    n = len(df)
    c = df["close"].to_numpy(); last = df["is_last_of_sess"].to_numpy()
    tm = pd.to_datetime(df["time"])
    hm = tm.dt.hour.to_numpy() * 100 + tm.dt.minute.to_numpy()
    sd = df["sess_date"].to_numpy()
    cash = 0.0; p = 0; pend_ = 0; daily = {}; prev = 0.0
    fills = 0; entries = 0
    for t in range(n):
        if pend_ != p:
            d = pend_ - p; side = 1 if d > 0 else -1
            px = c[t] + side * TICK
            cash -= d * px * pv; cash -= abs(d) * comm
            if pend_ != 0:
                entries += 1
            p = pend_; fills += 1
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = c[t] + side * TICK
            cash += p * px * pv; cash -= abs(p) * comm
            fills += 1; p = 0; pend_ = 0
        else:
            want = int(desired[t])
            if hm[t] == 1639:
                pend_ = 0
            elif 1630 <= hm[t] < 1803:
                pend_ = p if hm[t] < 1639 else 0
            else:
                pend_ = want
        if last[t]:
            eqv = cash + p * c[t] * pv
            daily[sd[t]] = eqv - prev; prev = eqv
    dl = pd.Series(daily); dl.index = pd.to_datetime(dl.index)
    return dl, fills, entries


def battery(dl):
    net = dl.values; eqd = np.cumsum(net); pk = np.maximum.accumulate(eqd); dd = pk - eqd
    k = max(1, int(0.05 * len(net)))
    sd_ = net.std(ddof=1)
    return {"n_days": len(net), "net": net.sum(),
            "sharpe": net.mean() / sd_ * np.sqrt(252) if sd_ > 0 else np.nan,
            "maxDD_eod": dd.max(), "CDaR5": np.sort(dd)[::-1][:k].mean()}


def CANDIDATE_SCREEN(vms, smax_ticks, label, hist_bars, sig_hist, dl_control_hist):
    pend = []
    for vm in vms:
        is_up, flip, s_eff, anchor = sm.member_states(
            hist_bars["close"].to_numpy(), sig_hist, float(vm),
            smin_ticks=40.0, smax_ticks=smax_ticks)
        _, _, p = sm.member_trades(hist_bars, is_up, flip, s_eff, anchor)
        pend.append(p)
    pend = np.column_stack(pend)
    tgt = sm.e10_target(pend)
    dl, f, e = run_policy_hist(hist_bars, tgt, COMM, PV)
    b = battery(dl)
    b_ctrl = battery(dl_control_hist)
    c1 = b["net"] >= b_ctrl["net"] - 10000.0
    c2 = b["maxDD_eod"] <= 1.25 * b_ctrl["maxDD_eod"]
    return {
        "arm": label, "smax_ticks": smax_ticks, "n_members": len(vms),
        "net_hist": b["net"], "net_incumbent_hist": b_ctrl["net"],
        "net_gap": b["net"] - b_ctrl["net"],
        "sharpe_hist": b["sharpe"], "sharpe_incumbent_hist": b_ctrl["sharpe"],
        "maxDD_hist": b["maxDD_eod"], "maxDD_incumbent_hist": b_ctrl["maxDD_eod"],
        "maxDD_ratio": b["maxDD_eod"] / b_ctrl["maxDD_eod"],
        "CDaR5_hist": b["CDaR5"], "CDaR5_incumbent_hist": b_ctrl["CDaR5"],
        "pass_c1_net_ge_incumbent_minus_10k": bool(c1),
        "pass_c2_maxDD_le_1.25x_incumbent": bool(c2),
        "screen_pass": bool(c1 and c2),
    }


sub415_v = json.load(open(os.path.join(OUT, "sub415_verdict.json")))
sub416_v = json.load(open(os.path.join(OUT, "sub416_verdict.json")))
ceiling_candidates = sub415_v["candidates_smax_ticks"]
ext_candidates = sub416_v["candidates"]

if not ceiling_candidates and not ext_candidates:
    row = {
        "status": "NONE_QUALIFIED",
        "reason": ("sub_415: 0/3 non-control arms qualified as CEILING-CANDIDATE "
                   "(every raised-ceiling arm improved Sharpe but WORSENED CDaR_0.95 "
                   "vs the 1200t control -- see out/ceiling_sweep.csv). "
                   "sub_416: 0/2 arms qualified as EXTENSION-CANDIDATE (both arm_ADD "
                   "and arm_REPLACE underperformed the 1200t/13-member control on "
                   "standalone Sharpe -- see out/extended_cohort.csv). "
                   "Old-regime screen is conditional on >=1 CANDIDATE; none exists "
                   "this wave, so nothing is rebuilt on the SM06 hist substrate."),
        "sub415_candidates": str(ceiling_candidates),
        "sub416_candidates": str(ext_candidates),
    }
    pd.DataFrame([row]).to_csv(os.path.join(OUT, "old_regime_screen.csv"), index=False)
    print(json.dumps(row, indent=2))
    print("sub_417: NONE_QUALIFIED -- no candidates to screen. Screen machinery "
          "retained in this script (CANDIDATE_SCREEN()) for a future wave.", flush=True)
else:
    # (retained path -- not exercised this wave; would rebuild each candidate on
    #  the SM06 hist substrate per gate_C.py convention)
    t0 = time.time()
    h = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                                      "nq1m_2005_202605.parquet"))
    h["time"] = pd.to_datetime(h["time"])
    h = h[h["time"] < "2022-01-01"].reset_index(drop=True)
    hist_bars = sm.resample_3m(h)
    sig_hist = sm.sigma_series(hist_bars["close"].to_numpy())
    from common import INCUMBENT_VMS
    pend_ctrl = []
    for vm in INCUMBENT_VMS:
        is_up, flip, s_eff, anchor = sm.member_states(
            hist_bars["close"].to_numpy(), sig_hist, float(vm), smin_ticks=40.0, smax_ticks=1200.0)
        _, _, p = sm.member_trades(hist_bars, is_up, flip, s_eff, anchor)
        pend_ctrl.append(p)
    pend_ctrl = np.column_stack(pend_ctrl)
    tgt_ctrl = sm.e10_target(pend_ctrl)
    dl_control_hist, _, _ = run_policy_hist(hist_bars, tgt_ctrl, COMM, PV)

    rows = []
    NEW_SLOW = [34, 38, 42, 46, 50]; FAST5 = [6, 8, 10, 12, 14]
    for smax in ceiling_candidates:
        rows.append(CANDIDATE_SCREEN(INCUMBENT_VMS, smax, f"sub415_smax_{int(smax)}t",
                                      hist_bars, sig_hist, dl_control_hist))
    smax_use = sub416_v["smax_ticks_used"]
    for arm in ext_candidates:
        vms = (INCUMBENT_VMS + NEW_SLOW) if arm == "arm_ADD" else \
              ([v for v in INCUMBENT_VMS if v not in FAST5] + NEW_SLOW)
        rows.append(CANDIDATE_SCREEN(vms, smax_use, f"sub416_{arm}",
                                      hist_bars, sig_hist, dl_control_hist))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "old_regime_screen.csv"), index=False)
    print(pd.DataFrame(rows).to_string(index=False), flush=True)
    print("done sub_417", round(time.time() - t0, 1), "s", flush=True)
