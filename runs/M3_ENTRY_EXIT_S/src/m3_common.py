"""M3_ENTRY_EXIT_S — member-level state machine with independently-scaled entry/exit thresholds.

member_states_asym / member_trades_asym are near-verbatim copies of
sm01_solarsim.member_states / member_trades with ONE structural change each, documented inline.
The shared library is NOT modified (program convention: experiment-local variants live in the
run's own src/, verified against the original for parity before use).
"""
import os, sys
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
import common as C1  # e10_exec, rha, dual_htf, htf_state, build_portfolio_6040


def member_states_asym(close, sigma, vol_mult, entry_mult, exit_mult,
                        stop_mult_ticks=179.0, smin_ticks=40.0, smax_ticks=1200.0,
                        start_up=False):
    """Verbatim sm01_solarsim.member_states, EXCEPT: the toggle condition (which bar counts as
    a trend birth, hence flip[t] / re-entry eligibility) uses S_entry = entry_mult*vol_mult*sigma
    (clamped), while a SEPARATE S_exit = exit_mult*vol_mult*sigma (clamped) is tracked in
    parallel, recomputed at the SAME trend-birth bars, for later use by member_trades_asym's
    exit check only. entry_mult=exit_mult=1.0 reproduces the original bit-for-bit (verified by
    the run's parity_assertion, not assumed).
    """
    n = close.size
    lo, hi = smin_ticks * sm.TICK, smax_ticks * sm.TICK
    fallback = stop_mult_ticks * sm.TICK

    def resolve(mult, t):
        s = sigma[t]
        if not np.isfinite(s) or s <= 0:
            return fallback
        return min(max(mult * vol_mult * s, lo), hi)

    is_up = np.zeros(n, dtype=bool)
    flip = np.zeros(n, dtype=np.int8)
    s_entry_eff = np.empty(n)
    s_exit_eff = np.empty(n)
    anchor_out = np.empty(n)

    up = bool(start_up)
    anchor = close[0]
    S_entry = resolve(entry_mult, 0)
    S_exit = resolve(exit_mult, 0)
    is_up[0] = up; s_entry_eff[0] = S_entry; s_exit_eff[0] = S_exit; anchor_out[0] = anchor

    for t in range(1, n):
        px = close[t]
        if up:
            if px >= anchor:
                anchor = px
            elif px < anchor - S_entry:
                up = False
                S_entry = resolve(entry_mult, t)
                S_exit = resolve(exit_mult, t)
                anchor = px
                flip[t] = -1
        else:
            if px <= anchor:
                anchor = px
            elif px > anchor + S_entry:
                up = True
                S_entry = resolve(entry_mult, t)
                S_exit = resolve(exit_mult, t)
                anchor = px
                flip[t] = 1
        is_up[t] = up; s_entry_eff[t] = S_entry; s_exit_eff[t] = S_exit; anchor_out[t] = anchor
    return is_up, flip, s_entry_eff, s_exit_eff, anchor_out


def member_trades_asym(bars, is_up, flip, s_exit_eff, anchor, bars_required=20,
                        comm_side=sm.NQ_COMM_SIDE, point_value=sm.NQ_POINT_VALUE):
    """Verbatim sm01_solarsim.member_trades, EXCEPT: the exit-check threshold `xl` uses
    `s_exit_eff[t]` (the independently-scaled exit series) instead of the entry-governed
    `s_eff[t]`. Re-entry timing (via `flip`) and anchor tracking are UNCHANGED — both still
    driven by the entry-governed state machine, per spec.yaml §1. stop_mult (SM03 disaster stop)
    intentionally omitted — unused by every other experiment in this line, dead in the vendor
    replica per sm01_solarsim's own docstring.

    Returns (fills, pos, pend_pos) — MUST return pend_pos too: downstream aggregation
    (W18R1 common.build_pend, and this file's build_pend_asym) consumes `pend_pos` (the
    forward-looking "position after next fill" including not-yet-executed orders), NOT `pos`
    (the realized, one-bar-lagged position) — caught by this run's own parity assertion, which
    crashed on a naive `pos`-only port before this fix; see spec.yaml's validation note.
    """
    n = len(bars)
    close = bars["close"].to_numpy(); open_ = bars["open"].to_numpy()
    high = bars["high"].to_numpy(); low = bars["low"].to_numpy()
    last_of_sess = bars["is_last_of_sess"].to_numpy()
    times = bars["time"].to_numpy()

    pos = np.zeros(n, dtype=np.int8)
    pend_pos = np.zeros(n, dtype=np.int8)
    fills = []
    p = 0
    pending = 0

    for t in range(n):
        if pending != 0:
            if pending == 1:
                px = sm._fill(open_[t], high[t], low[t], +1)
                p = 1
                fills.append((t, times[t], "Long", "Buy", px, p))
            elif pending == -1:
                px = sm._fill(open_[t], high[t], low[t], -1)
                p = -1
                fills.append((t, times[t], "Short", "SellShort", px, p))
            elif pending == -2:
                px = sm._fill(open_[t], high[t], low[t], -1)
                p = 0
                fills.append((t, times[t], "L-SolarExit", "Sell", px, p))
            elif pending == 2:
                px = sm._fill(open_[t], high[t], low[t], +1)
                p = 0
                fills.append((t, times[t], "S-SolarExit", "BuyToCover", px, p))
            pending = 0

        if t >= bars_required:
            xl = anchor[t] - s_exit_eff[t] if is_up[t] else anchor[t] + s_exit_eff[t]
            decided = False
            if p == 1 and close[t] <= xl:
                pending = -2; decided = True
            elif p == -1 and close[t] >= xl:
                pending = 2; decided = True
            if not decided and p == 0 and flip[t] != 0 and not last_of_sess[t]:
                pending = 1 if flip[t] > 0 else -1

        if last_of_sess[t] and p != 0:
            side = -1 if p == 1 else +1
            px = sm._fill(open_[t], high[t], low[t], side, at_close=close[t])
            fills.append((t, times[t], "Exit on session close",
                          "Sell" if p == 1 else "BuyToCover", px, 0))
            p = 0
            if pending in (-2, 2):
                pending = 0
        pos[t] = p
        if pending == 1:
            pend_pos[t] = 1
        elif pending == -1:
            pend_pos[t] = -1
        elif pending in (2, -2):
            pend_pos[t] = 0
        else:
            pend_pos[t] = p

    f = pd.DataFrame(fills, columns=["bar", "time", "name", "order_action", "price", "pos_after"])
    f["commission"] = comm_side
    return f, pos, pend_pos


def build_pend_asym(bars, sigma, entry_mult, exit_mult, vms=None):
    """Same shape as W18R1's common.build_pend but with the asymmetric state machine. Appends
    `pend` (forward-looking pending position), matching common.build_pend's own convention, NOT
    `pos` (realized) — see member_trades_asym's docstring."""
    vms = vms or list(sm.VMS)
    PEND = []
    for vm in vms:
        is_up, flip, s_entry_eff, s_exit_eff, anchor = member_states_asym(
            bars["close"].to_numpy(), sigma, float(vm), entry_mult, exit_mult)
        fills, pos, pend = member_trades_asym(bars, is_up, flip, s_exit_eff, anchor)
        PEND.append(pend)
    return np.column_stack(PEND)


def verify_parity(bars, sigma, vms=None, sample_vm=None):
    """Hard parity check: entry_mult=exit_mult=1.0 must reproduce sm01_solarsim.member_states /
    member_trades bit-for-bit, on EVERY incumbent VolMult, not just one sample."""
    vms = vms or list(sm.VMS)
    close = bars["close"].to_numpy()
    all_ok = True
    detail = []
    for vm in vms:
        is_up0, flip0, s_eff0, anchor0 = sm.member_states(close, sigma, float(vm))
        _, pos0, pend0 = sm.member_trades(bars, is_up0, flip0, s_eff0, anchor0)
        is_up1, flip1, s_entry1, s_exit1, anchor1 = member_states_asym(close, sigma, float(vm), 1.0, 1.0)
        _, pos1, pend1 = member_trades_asym(bars, is_up1, flip1, s_exit1, anchor1)
        ok = bool(np.array_equal(pos0, pos1) and np.array_equal(pend0, pend1)
                  and np.array_equal(is_up0, is_up1)
                  and np.array_equal(flip0, flip1) and np.allclose(s_eff0, s_entry1)
                  and np.allclose(s_eff0, s_exit1) and np.allclose(anchor0, anchor1))
        detail.append({"vol_mult": vm, "PASS": ok, "n_pos_mismatch": int((pos0 != pos1).sum()),
                        "n_pend_mismatch": int((pend0 != pend1).sum())})
        all_ok = all_ok and ok
    return all_ok, detail
