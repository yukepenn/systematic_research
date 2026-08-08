"""SM01 substrate builder — runs after parity gates verified interactively.
Produces: member_trades.parquet (13 members, path anatomy), vote_state_3m.parquet,
e10_daily_py.csv, parity_report.md. Run from repo root."""
import sys, time, json
sys.path.insert(0, "src/analytics")
import numpy as np, pandas as pd
import sm01_solarsim as sm

OUT = "runs/SM01_SUBSTRATE/out"
import os; os.makedirs(OUT, exist_ok=True)

t0 = time.time()
bars = sm.load_bars_3m()
n = len(bars)
close = bars.close.to_numpy(); high = bars.high.to_numpy(); low = bars.low.to_numpy()
sig = sm.sigma_series(close)

POS, PEND, FLIPS, SEFF = [], [], [], []
trades_all = []
fills_counts = {}
for vm in sm.VMS:
    is_up, flip, s_eff, anchor = sm.member_states(close, sig, float(vm))
    fills, pos, pend = sm.member_trades(bars, is_up, flip, s_eff, anchor)
    POS.append(pos); PEND.append(pend); FLIPS.append(flip); SEFF.append(s_eff)
    tr = sm.fills_to_trades(fills)
    tr["vm"] = vm
    # path anatomy from 3m bars within [entry_bar, exit_bar]
    mfe = np.empty(len(tr)); mae = np.empty(len(tr))
    t_mfe = np.empty(len(tr), dtype=int); t_mae = np.empty(len(tr), dtype=int)
    for i, r in enumerate(tr.itertuples()):
        hi = high[r.entry_bar : r.exit_bar + 1]; lo = low[r.entry_bar : r.exit_bar + 1]
        if r.side == 1:
            fe = hi - r.entry_px; ae = r.entry_px - lo
        else:
            fe = r.entry_px - lo; ae = hi - r.entry_px
        mfe[i] = fe.max(); mae[i] = ae.max()
        t_mfe[i] = int(fe.argmax()); t_mae[i] = int(ae.argmax())
    tr["mfe_pts"] = mfe; tr["mae_pts"] = mae
    tr["bars_to_mfe"] = t_mfe; tr["bars_to_mae"] = t_mae
    tr["bars_held"] = tr.exit_bar - tr.entry_bar
    trades_all.append(tr)
    fills_counts[vm] = len(fills)
    print(f"vm{vm}: {len(tr)} trades", flush=True)

pos = np.column_stack(POS); pend = np.column_stack(PEND)
flips = np.column_stack(FLIPS); seff = np.column_stack(SEFF)

trades = pd.concat(trades_all, ignore_index=True)
trades["entry_sess"] = bars.sess_date.to_numpy()[trades.entry_bar]
trades["exit_sess"] = bars.sess_date.to_numpy()[trades.exit_bar]
trades.to_parquet(f"{OUT}/member_trades.parquet", index=False)

vote = pd.DataFrame({
    "time": bars.time, "sess_date": bars.sess_date,
    "close": bars.close, "sess_id": bars.sess_id,
    "is_last_of_sess": bars.is_last_of_sess,
    "sigma460": sig,
    "vote_pos": pos.sum(axis=1),          # current physical vote sum (-13..13)
    "vote_pend": pend.sum(axis=1),        # pending vote sum (drives E10 target)
    "n_long": (pend == 1).sum(axis=1),
    "n_short": (pend == -1).sum(axis=1),
    "n_flat": (pend == 0).sum(axis=1),
    "flips_bar": (flips != 0).sum(axis=1),  # members flipping on this bar
})
for i, vm in enumerate(sm.VMS):
    vote[f"p{vm}"] = pend[:, i]
vote.to_parquet(f"{OUT}/vote_state_3m.parquet", index=False)

tgt = sm.e10_target(pend)
daily = sm.e10_sim(bars, tgt)
daily.to_csv(f"{OUT}/e10_daily_py.csv", index=False)

meta = {
    "built": time.strftime("%Y-%m-%d %H:%M:%S"),
    "bars": int(n), "sessions": int(bars.sess_id.nunique()),
    "fills_per_member": {str(k): int(v) for k, v in fills_counts.items()},
    "trades_total": int(len(trades)),
    "e10_daily_total": float(daily.net.sum()),
    "runtime_s": round(time.time() - t0, 1),
}
with open(f"{OUT}/build_meta.json", "w") as f:
    json.dump(meta, f, indent=2)
print(json.dumps(meta, indent=2))
