"""R1 -- constructs the 12-candidate giveback-conditioned early-exit overlay grid on top of the
Product-B shared decision core, prices each candidate decision sequence on BOTH NQ and MNQ
execution economics (directive sec2/sec32 shared-core discipline), and computes the full
primary/tail/chronology battery vs the BEST_ONE_NQ/MNQ incumbent controls. Bounded, preregistered
grid only (spec.yaml) -- no post-hoc parameter selection.

Design: decision generation (pos_seq, with the overlay) is kept STRUCTURALLY IDENTICAL to
r2_battery.py's verified one_contract_decisions() (same control flow, same last-bar force-flat
cancellation semantics) with only the overlay override injected into the target computation.
Actual dollar pricing of the resulting pos_seq reuses r2_battery.py's onelot_exec() logic
verbatim (not reimplemented inline), so every reported dollar figure is priced by
already-trusted code; the overlay's own internal MFE/giveback tracker uses a close-to-close
mark-to-market proxy (not exact fill prices) purely as its firing heuristic -- disclosed, not
used for any reported P&L number."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
from sm01_solarsim import load_bars_3m, _fill
from sm_bmom import rth_3m, BAND_DAYS
from smv2_common import dd_battery
import common as C1

RUN = os.path.join(ROOT, "runs", "R1_ADAPTIVE_EXIT")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

PV_MNQ, COMM_MNQ = 2.0, 0.65
PV_NQ, COMM_NQ = 20.0, 2.18
ENTRY_LEVEL, EXIT_LEVEL = 3.0, 1.0

print("building shared substrate (verbatim r2_battery.py formulas) ...", flush=True)
bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"])
dev = (sess <= pd.Timestamp("2026-05-31")).to_numpy()
bars = bars[dev].reset_index(drop=True)
n = len(bars)
close = bars["close"].to_numpy(); open_ = bars["open"].to_numpy()
high = bars["high"].to_numpy(); low = bars["low"].to_numpy()
sig460 = sm.sigma_series(close)
PEND = C1.build_pend(bars, sig460)
T = sm.e10_target(PEND).astype(int)

sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
tilt_by_date = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
tilt_state = np.array([tilt_by_date.get(d, np.nan) for d in bars["sess_date"]])
tilt_state = np.where(np.isnan(tilt_state), 0.0, tilt_state)


def bmom_pos_series(bars3):
    r = rth_3m(bars3)
    pos_arr = np.zeros(len(bars3)); hist = {}; day_count = 0
    for d_, g in r.groupby("date", sort=True):
        g = g.sort_values("hm")
        if g["hm"].iloc[0] != 933:
            continue
        open0930 = g["open"].iloc[0]
        close_ = g["close"].to_numpy(); vol = g["volume"].to_numpy(); hm = g["hm"].to_numpy()
        vwap = np.cumsum(close_ * vol) / np.maximum(np.cumsum(vol), 1e-9)
        gidx = g.index.to_numpy(); pos = 0
        flat_hm = int(hm[hm <= 1557].max()) if (hm <= 1557).any() else None
        if day_count >= BAND_DAYS:
            for i in range(len(g)):
                h = int(hm[i])
                if flat_hm is not None and h == flat_hm:
                    pos = 0; pos_arr[gidx[i]] = pos; break
                if h > 1554:
                    pos_arr[gidx[i]] = pos; continue
                past = hist.get(h)
                if past is not None and len(past) >= 1:
                    m_tod = float(np.mean(past[-BAND_DAYS:]))
                    up, lo = open0930 + m_tod, open0930 - m_tod
                    if close_[i] > max(up, vwap[i]):
                        pos = 1
                    elif close_[i] < min(lo, vwap[i]):
                        pos = -1
                pos_arr[gidx[i]] = pos
        for i in range(len(g)):
            hist.setdefault(int(hm[i]), []).append(abs(close_[i] - open0930))
        day_count += 1
    return pos_arr


B = bmom_pos_series(bars)

sess_close_ts = bars.groupby("sess_date")["time"].transform("max")
entry_block_dl = sess_close_ts - pd.Timedelta(minutes=30)
forced_flat_dl = sess_close_ts - pd.Timedelta(minutes=21)
bar_time = bars["time"]
entry_blocked_c4 = (bar_time >= entry_block_dl).to_numpy()
forced_flat_c4 = (bar_time >= forced_flat_dl).to_numpy()
last = bars["is_last_of_sess"].to_numpy()


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


WSOLAR, WBMOM, TILTRESCALE, TILTMULT = 0.7086, 2.83, 0.9026, 1.25
m_arr = np.where((T != 0) & (tilt_state != 0) & (np.sign(T) == tilt_state), TILTMULT, 1.0)
Tp = np.clip(rha(T * m_arr * TILTRESCALE), -13, 13)
M = WSOLAR * Tp + WBMOM * np.asarray(B)


# ================================================================== decision layer (+ overlay)
def build_candidate_pos_seq(giveback_thresh=None, mfe_floor=0.0, decay_confirm=None):
    """Structurally identical control flow to r2_battery.py's one_contract_decisions() (physical
    lagged position p, pend takes effect next bar, session-close force-flat CANCELS a same-bar
    fresh entry rather than filling it -- same semantics, verified against the original). The
    ONLY addition: an online, close-to-close MTM giveback/decay tracker per open block that can
    force tgt=0 (early flatten) before the incumbent's own M-based logic decides. giveback_thresh
    =None reproduces the incumbent exactly (pure passthrough, used as this script's own control)."""
    p = 0; pend = 0
    pos_seq = np.zeros(n, dtype=int)
    block_pnl = 0.0; block_mfe = 0.0; block_peak_absT = 0.0; block_ref_close = None
    n_overlay_exits = 0
    for t in range(n):
        if pend != p:
            p = pend
            block_pnl = 0.0; block_mfe = 0.0; block_peak_absT = 0.0; block_ref_close = close[t]
        if last[t] and p != 0:
            p = 0; pend = 0
            pos_seq[t] = p
            continue
        pos_seq[t] = p
        if p != 0:
            block_pnl += p * (close[t] - block_ref_close) * PV_NQ  # NQ-point proxy; instrument-
            block_ref_close = close[t]                              # agnostic in relative terms
            block_mfe = max(block_mfe, block_pnl, 0.0)
            block_peak_absT = max(block_peak_absT, abs(T[t]))

        overlay_fire = False
        if giveback_thresh is not None and p != 0 and block_mfe >= mfe_floor and block_mfe > 0:
            gb_ratio = (block_mfe - block_pnl) / block_mfe
            if gb_ratio >= giveback_thresh:
                if decay_confirm is None:
                    overlay_fire = True
                else:
                    decay_frac = 1.0 - (abs(T[t]) / block_peak_absT) if block_peak_absT > 0 else 0.0
                    overlay_fire = decay_frac >= decay_confirm

        if forced_flat_c4[t] or overlay_fire:
            tgt = 0
            if overlay_fire and not forced_flat_c4[t]:
                n_overlay_exits += 1
        elif p == 0:
            tgt = 0 if entry_blocked_c4[t] else (1 if M[t] >= ENTRY_LEVEL else (-1 if M[t] <= -ENTRY_LEVEL else 0))
        elif p > 0:
            if M[t] <= -ENTRY_LEVEL and not entry_blocked_c4[t]:
                tgt = -1
            elif M[t] <= EXIT_LEVEL:
                tgt = 0
            else:
                tgt = p
        else:
            if M[t] >= ENTRY_LEVEL and not entry_blocked_c4[t]:
                tgt = 1
            elif M[t] >= -EXIT_LEVEL:
                tgt = 0
            else:
                tgt = p
        pend = tgt
    return pos_seq, n_overlay_exits


# ================================================================== pricing (verbatim r2_battery.onelot_exec)
def onelot_exec(pos_seq, comm, pv, o, h, l, c):
    cash = 0.0; p = 0; prev_eq = 0.0
    contracts_by_sess = {}
    bar_pos = np.zeros(n, dtype=int); bar_pnl = np.zeros(n)
    for t in range(n):
        tgt = int(pos_seq[t])
        if tgt != p:
            d = tgt - p
            side = 1 if d > 0 else -1
            if last[t]:
                px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            else:
                px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * pv
            cash -= abs(d) * comm
            contracts_by_sess[bars["sess_date"].iloc[t]] = contracts_by_sess.get(bars["sess_date"].iloc[t], 0) + abs(d)
            p = tgt
        eq = cash + p * c[t] * pv
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
    dd = pd.DataFrame({"sess": bars["sess_date"], "pnl": bar_pnl}).groupby("sess")["pnl"].sum().reset_index()
    dd.columns = ["sess", "net"]
    return dd, bar_pos, bar_pnl


def battery_row(tag, daily):
    b = dd_battery(pd.to_datetime(daily["sess"]), daily["net"].to_numpy(), label=tag)
    return {"tag": tag, "n_days": b["n_days"], "net": b["net"], "sharpe": b["sharpe"],
            "sortino": b["sortino"], "calmar": b["calmar"], "maxDD_eod": b["maxDD_eod"],
            "CDaR95": b["CDaR5"], "worst_day": float(daily["net"].min()),
            "worst_month": b["worst_month"], "pos_day_pct": b["pos_day_pct"]}


print("loading genuine MNQU6 prices (verbatim r2_battery.py convention, NOT NQ-scaled) ...", flush=True)
mnq_raw = pd.read_csv(os.path.join(ROOT, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "mnq_3m_raw.csv"), comment="#")
mnq_raw["time"] = pd.to_datetime(mnq_raw["time"])
mnq_idx = mnq_raw.set_index("time")
aligned = mnq_idx.reindex(bars["time"]).ffill()
n_missing = int(aligned["close"].isna().sum())
print(f"  MNQ genuine bars aligned to NQ grid: {n_missing} missing ({100*n_missing/n:.4f}%), ffilled", flush=True)
o_mnq = aligned["open"].to_numpy(); h_mnq = aligned["high"].to_numpy()
l_mnq = aligned["low"].to_numpy(); c_mnq = aligned["close"].to_numpy()

print("running CONTROL (no overlay, pure passthrough) on NQ + MNQ economics ...", flush=True)
pos_ctrl, _ = build_candidate_pos_seq(None, 0.0, None)
daily_ctrl_nq, barpos_ctrl_nq, bpnl_ctrl_nq = onelot_exec(pos_ctrl, COMM_NQ, PV_NQ, open_, high, low, close)
daily_ctrl_mnq, barpos_ctrl_mnq, bpnl_ctrl_mnq = onelot_exec(pos_ctrl, COMM_MNQ, PV_MNQ, o_mnq, h_mnq, l_mnq, c_mnq)
ctrl_row_nq = battery_row("CONTROL_NQ", daily_ctrl_nq)
ctrl_row_mnq = battery_row("CONTROL_MNQ", daily_ctrl_mnq)
print(f"  control NQ net={ctrl_row_nq['net']:.2f}  control MNQ net={ctrl_row_mnq['net']:.2f}", flush=True)
assert abs(ctrl_row_nq["net"] - 301915.92) < 1.0, "CONTROL does not reproduce the certified incumbent NQ net -- construction bug"
assert abs(ctrl_row_mnq["net"] - 28587.10) < 1.0, "CONTROL does not reproduce the certified incumbent MNQ net -- construction bug"
print("  control reproduces certified incumbent NQ+MNQ nets exactly -- construction verified.", flush=True)

GRID = []
for design in ["GIVEBACK_ONLY", "GIVEBACK_PLUS_DECAY_CONFIRM"]:
    for gb in [0.50, 0.65, 0.80]:
        for floor in [300.0, 600.0]:
            GRID.append({"design": design, "giveback_thresh": gb, "mfe_floor": floor,
                         "decay_confirm": 0.30 if design == "GIVEBACK_PLUS_DECAY_CONFIRM" else None})
print(f"{len(GRID)} candidates in grid", flush=True)

results = []
np.save(os.path.join(OUT, "pos_control.npy"), pos_ctrl)
daily_ctrl_nq.to_csv(os.path.join(OUT, "daily_CONTROL_NQ.csv"), index=False)
daily_ctrl_mnq.to_csv(os.path.join(OUT, "daily_CONTROL_MNQ.csv"), index=False)

for i, cfg in enumerate(GRID):
    tag = f"C{i+1:02d}_{cfg['design']}_gb{cfg['giveback_thresh']}_floor{int(cfg['mfe_floor'])}"
    pos_seq, n_ov = build_candidate_pos_seq(cfg["giveback_thresh"], cfg["mfe_floor"], cfg["decay_confirm"])
    daily_nq, barpos_nq, bpnl_nq = onelot_exec(pos_seq, COMM_NQ, PV_NQ, open_, high, low, close)
    daily_mnq, barpos_mnq, bpnl_mnq = onelot_exec(pos_seq, COMM_MNQ, PV_MNQ, o_mnq, h_mnq, l_mnq, c_mnq)
    row_nq = battery_row(tag + "_NQ", daily_nq)
    row_mnq = battery_row(tag + "_MNQ", daily_mnq)
    row_nq.update({**cfg, "n_overlay_exits": n_ov, "instrument": "NQ"})
    row_mnq.update({**cfg, "n_overlay_exits": n_ov, "instrument": "MNQ"})
    results.append(row_nq); results.append(row_mnq)
    np.save(os.path.join(OUT, f"pos_{tag}.npy"), pos_seq)
    np.save(os.path.join(OUT, f"barpnl_{tag}_NQ.npy"), bpnl_nq)
    daily_nq.to_csv(os.path.join(OUT, f"daily_{tag}_NQ.csv"), index=False)
    daily_mnq.to_csv(os.path.join(OUT, f"daily_{tag}_MNQ.csv"), index=False)
    print(f"  [{tag}] NQ net={row_nq['net']:.2f} sharpe={row_nq['sharpe']:.3f} maxDD={row_nq['maxDD_eod']:.2f} CDaR95={row_nq['CDaR95']:.2f}  "
          f"MNQ net={row_mnq['net']:.2f} sharpe={row_mnq['sharpe']:.3f}  n_overlay_exits={n_ov}", flush=True)

leaderboard = pd.DataFrame(results)
leaderboard.to_csv(os.path.join(OUT, "leaderboard.csv"), index=False)
json.dump({"control_NQ": ctrl_row_nq, "control_MNQ": ctrl_row_mnq},
          open(os.path.join(OUT, "control_battery.json"), "w"), indent=2)
print("\nsaved leaderboard.csv, control_battery.json", flush=True)
