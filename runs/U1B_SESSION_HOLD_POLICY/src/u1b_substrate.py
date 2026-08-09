"""U1B shared substrate -- session-conditioned HOLD policy, graded (never binary) ETH delta while
holding. Imports runs/SA0_SYSTEM_STRUCTURE/current_health/src/health_substrate.py (HS), the
byte-verified extension of substrate.py through 2026-07-31, for T/Tp/tilt_state/B/M/
entry_blocked_c4/forced_flat_c4/hm/last/bars and its own build_pos_seq/onelot_exec control-flow
pattern -- substrate.py's own module-level functions are closed over its own canonical-only
(n~519,703) arrays and cannot process the longer array this family's own June-July-2026
reporting requirement needs, the exact reason 01_build_state_table.py used HS instead of
substrate.py directly. HS's own correctness gate (canonical-window slice reproduces the
certified NQ net exactly) is the proof that using HS introduces no change to already-certified
canonical-window history.

Leg 1 (Product B): build_pos_seq_eth_exit -- HS.build_pos_seq's exact control flow with ONE
change: while holding (p!=0) at an ETH bar (is_rth[t]==False), the exit-level threshold used in
the two holding branches is exit_level_eth instead of the incumbent's EXIT_LEVEL=1.0. Reverts to
EXIT_LEVEL=1.0 the instant is_rth[t] is True. Entry logic completely unmodified.

Leg 2 (Product A): product_a_exec_eth_scale -- pa0_substrate.product_a_exec's exact control flow
(re-parametrized per 01_build_state_table.py's own working pattern), with ONE change: at a bar
where p!=0 (carried from the prior bar) AND is_rth[t]==False, the pre-round/pre-clamp raw score
KSOLAR*Tpp+KBMOM*B is multiplied by `multiplier` BEFORE rha()/clip. A bar with p==0 always uses
multiplier=1.0 -- unmodified entry logic. Reverts to multiplier=1.0 the instant is_rth is True.

Both legs default multiplier=1.0 / exit_level_eth=1.0 to reproduce the incumbent exactly -- the
correctness gate at the bottom asserts this against the certified nets."""
import os, sys
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SA0_SYSTEM_STRUCTURE", "current_health", "src"))
from sm01_solarsim import _fill
import health_substrate as HS  # extended (through 2026-07-31) Product-B substrate, self-verified on import

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

n = HS.n
bars = HS.bars
close, open_, high, low = HS.close, HS.open_, HS.high, HS.low
last = HS.last
M, T, tilt_state, B = HS.M, HS.T, HS.tilt_state, HS.B
entry_blocked_c4, forced_flat_c4 = HS.entry_blocked_c4, HS.forced_flat_c4
hm = HS.hm
sd = bars["sess_date"].to_numpy()
year_arr = HS.year_arr
CANONICAL_END = HS.CANONICAL_END
sess_dt = pd.to_datetime(bars["sess_date"])
canon_mask = (sess_dt <= CANONICAL_END).to_numpy()
health_mask = ~canon_mask  # is_health_only_bar, the new June-July-2026 sessions

# ---------------------------------------------------------------- is_rth, mirrored exactly onto
# HS's own hm array using U0's own documented formula (UNIFIED_STATE_MAP.md: 933<=hm<=1600)
is_rth = (hm >= 933) & (hm <= 1600)
print(f"[u1b_substrate] is_rth bars: {int(is_rth.sum())} / {n}  "
      f"(canonical-window: {int(is_rth[canon_mask].sum())} / {int(canon_mask.sum())})", flush=True)


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


# ================================================================== Leg 1 -- Product B
def build_pos_seq_eth_exit(exit_level_eth, entry_level=HS.ENTRY_LEVEL, exit_level_rth=HS.EXIT_LEVEL,
                            M_arr=None, is_rth_arr=None, entry_blocked=None, forced_flat=None):
    """HS.build_pos_seq's exact control flow, with ONE change: while holding (p!=0) at a bar
    where is_rth_arr[t]==False, the exit-level threshold used in the p>0/p<0 holding branches is
    exit_level_eth instead of exit_level_rth. exit_level_eth=exit_level_rth (default call)
    reproduces HS.build_pos_seq(HS.M) bar-for-bar exactly -- asserted below."""
    M_arr = M if M_arr is None else M_arr
    is_rth_arr = is_rth if is_rth_arr is None else is_rth_arr
    entry_blocked = entry_blocked_c4 if entry_blocked is None else entry_blocked
    forced_flat = forced_flat_c4 if forced_flat is None else forced_flat
    p = 0; pend = 0
    pos_seq = np.zeros(n, dtype=int)
    for t in range(n):
        if pend != p:
            p = pend
        if last[t] and p != 0:
            p = 0; pend = 0
            pos_seq[t] = p
            continue
        pos_seq[t] = p
        cur_exit = exit_level_rth if is_rth_arr[t] else exit_level_eth
        if forced_flat[t]:
            tgt = 0
        elif p == 0:
            tgt = 0 if entry_blocked[t] else (1 if M_arr[t] >= entry_level else (-1 if M_arr[t] <= -entry_level else 0))
        elif p > 0:
            if M_arr[t] <= -entry_level and not entry_blocked[t]:
                tgt = -1
            elif M_arr[t] <= cur_exit:
                tgt = 0
            else:
                tgt = p
        else:
            if M_arr[t] >= entry_level and not entry_blocked[t]:
                tgt = 1
            elif M_arr[t] >= -cur_exit:
                tgt = 0
            else:
                tgt = p
        pend = tgt
    return pos_seq


# ---------------------------------------------------------------- genuine/proxy MNQ prices (extended window)
print("[u1b_substrate] loading genuine MNQU6 prices (proxy on the 45 new June-July-2026 sessions) ...", flush=True)
mnq_raw = pd.read_csv(os.path.join(ROOT, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "mnq_3m_raw.csv"), comment="#")
mnq_raw["time"] = pd.to_datetime(mnq_raw["time"])
mnq_idx = mnq_raw.set_index("time")
aligned_raw = mnq_idx.reindex(bars["time"])  # NOT ffilled -- NaN marks genuinely-missing MNQ bars
is_mnq_genuine = aligned_raw["close"].notna().to_numpy()
o_mnq = np.where(is_mnq_genuine, aligned_raw["open"].to_numpy(), open_)
h_mnq = np.where(is_mnq_genuine, aligned_raw["high"].to_numpy(), high)
l_mnq = np.where(is_mnq_genuine, aligned_raw["low"].to_numpy(), low)
c_mnq = np.where(is_mnq_genuine, aligned_raw["close"].to_numpy(), close)
print(f"[u1b_substrate] MNQ genuine bars: {int(is_mnq_genuine.sum())} / {n}  "
      f"(proxy bars: {int((~is_mnq_genuine).sum())})", flush=True)

# ================================================================== Leg 2 -- Product A
KSOLAR, KBMOM, TILTRESCALE, TILTMULT, SHORTHALF = 0.728654, 2.934159, 0.9026, 1.25, 0.5  # verbatim from pa0_substrate.py
PV_MNQ_A, COMM_MNQ_A = 2.0, 0.65  # verbatim from pa0_substrate.py (Product A prices on NQ's own OHLC)


def product_a_exec_eth_scale(multiplier, T_leg=None, tilt_state_=None, B_=None,
                              entry_blocked_=None, forced_flat_=None, is_rth_=None,
                              o=None, h=None, l=None, c=None, last_=None, sd_=None, n_=None):
    """pa0_substrate.product_a_exec's exact control flow (re-parametrized per
    01_build_state_table.py's own working pattern for product_a_exec_generalized), with ONE
    change: at a bar where p!=0 (carried from the prior bar) AND is_rth_[t]==False, the
    pre-round/pre-clamp raw score KSOLAR*Tpp+KBMOM*B is multiplied by `multiplier` BEFORE
    rha()/clip. A bar with p==0 always uses multiplier=1.0 (unmodified entry logic).
    multiplier=1.0 (default call) reproduces the certified control byte-for-byte -- asserted
    below."""
    T_leg = T if T_leg is None else T_leg
    tilt_state_ = tilt_state if tilt_state_ is None else tilt_state_
    B_ = B if B_ is None else B_
    entry_blocked_ = entry_blocked_c4 if entry_blocked_ is None else entry_blocked_
    forced_flat_ = forced_flat_c4 if forced_flat_ is None else forced_flat_
    is_rth_ = is_rth if is_rth_ is None else is_rth_
    o = open_ if o is None else o
    h = high if h is None else h
    l = low if l is None else l
    c = close if c is None else c
    last_ = last if last_ is None else last_
    sd_ = sd if sd_ is None else sd_
    n_ = n if n_ is None else n_

    m_arr = np.where((T_leg != 0) & (tilt_state_ != 0) & (np.sign(T_leg) == tilt_state_), TILTMULT, 1.0)
    s_arr = np.where((T_leg < 0) & (tilt_state_ > 0), SHORTHALF, 1.0)
    Tpp = np.clip(rha(T_leg * m_arr * s_arr * TILTRESCALE), -13, 13)
    raw_score = KSOLAR * Tpp + KBMOM * np.asarray(B_)  # pre-round/pre-clamp -- multiplier applied per-bar below

    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    contracts_by_sess = {}
    bar_pos = np.zeros(n_, dtype=int)
    bar_pnl = np.zeros(n_)
    for t in range(n_):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * PV_MNQ_A
            cash -= abs(d) * COMM_MNQ_A
            contracts_by_sess[sd_[t]] = contracts_by_sess.get(sd_[t], 0) + abs(d)
            p = pend
        if last_[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * PV_MNQ_A
            cash -= abs(p) * COMM_MNQ_A
            contracts_by_sess[sd_[t]] = contracts_by_sess.get(sd_[t], 0) + abs(p)
            p = 0; pend = 0
        else:
            mult = multiplier if (p != 0 and not is_rth_[t]) else 1.0
            tgt_raw = int(np.clip(rha(raw_score[t] * mult), -13, 13))
            if forced_flat_[t]:
                tgt = 0
            elif entry_blocked_[t]:
                if tgt_raw == 0 or p == 0:
                    tgt = 0
                elif np.sign(tgt_raw) != np.sign(p):
                    tgt = 0
                else:
                    tgt = p if abs(tgt_raw) > abs(p) else tgt_raw
            else:
                tgt = tgt_raw
            pend = tgt
        eq = cash + p * c[t] * PV_MNQ_A
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
        if last_[t]:
            contracts_by_sess.setdefault(sd_[t], 0)
    dd = pd.DataFrame({"sess": pd.Series(sd_), "pnl": bar_pnl}).groupby("sess")["pnl"].sum().reset_index()
    dd.columns = ["sess", "net"]
    dd["contracts"] = dd["sess"].map(contracts_by_sess)
    return dd, bar_pos, bar_pnl


def battery_row(tag, daily):
    return HS.battery_row(tag, daily)


def trade_volume(bar_pos):
    """Total |position delta| across every transition (contracts traded) -- used for the
    turnover/cost check. bar_pos is prepended with an implicit 0 starting position."""
    return int(np.abs(np.diff(np.r_[0, bar_pos])).sum())


# ================================================================== correctness gates
print("[u1b_substrate] running correctness gates ...", flush=True)

pos_dummy = build_pos_seq_eth_exit(1.0)
assert np.array_equal(pos_dummy, HS.pos_full), "Leg1 eth-exit function does not reduce to HS.build_pos_seq(HS.M) at exit_level_eth=1.0"
_, _, bpnl_dummy_nq = HS.onelot_exec(pos_dummy, HS.COMM_NQ, HS.PV_NQ, open_, high, low, close)
ctrl_net_nq_canon = float(bpnl_dummy_nq[canon_mask].sum())
assert abs(ctrl_net_nq_canon - 301915.92) < 1.0, f"Leg1 baseline NQ canonical net mismatch: {ctrl_net_nq_canon}"

_, _, bpnl_dummy_mnq = HS.onelot_exec(pos_dummy, HS.COMM_MNQ, HS.PV_MNQ, o_mnq, h_mnq, l_mnq, c_mnq)
ctrl_net_mnq_canon = float(bpnl_dummy_mnq[canon_mask].sum())
assert abs(ctrl_net_mnq_canon - 28587.10) < 1.0, f"Leg1 baseline MNQ canonical net mismatch: {ctrl_net_mnq_canon}"
print(f"[u1b_substrate] Leg1 baseline VERIFIED: NQ canonical net={ctrl_net_nq_canon:.2f}  "
      f"MNQ canonical net={ctrl_net_mnq_canon:.2f}", flush=True)

daily_a_dummy, barpos_a_dummy, bpnl_a_dummy = product_a_exec_eth_scale(1.0)
ctrl_net_a_canon = float(bpnl_a_dummy[canon_mask].sum())
assert abs(ctrl_net_a_canon - 177924.40) < 1.0, f"Leg2 baseline A canonical net mismatch: {ctrl_net_a_canon}"
print(f"[u1b_substrate] Leg2 baseline VERIFIED: A canonical net={ctrl_net_a_canon:.2f}", flush=True)

print(f"[u1b_substrate] extended (through 2026-07-31) baseline nets: "
      f"B-NQ={bpnl_dummy_nq.sum():.2f}  B-MNQ={bpnl_dummy_mnq.sum():.2f}  A={bpnl_a_dummy.sum():.2f}", flush=True)

# baseline daily frames + bar_pnl kept around for the two leg scripts (avoid recomputation)
CTRL_POS_B = pos_dummy
CTRL_BPNL_B_NQ = bpnl_dummy_nq
CTRL_BPNL_B_MNQ = bpnl_dummy_mnq
CTRL_POS_A = barpos_a_dummy
CTRL_BPNL_A = bpnl_a_dummy

if __name__ == "__main__":
    print("u1b_substrate self-test OK")
