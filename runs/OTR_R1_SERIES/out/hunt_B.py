# hunt_B.py — FAMILY B: session/calendar mechanics hunt for the hidden entry gate
# Creates features per labeled flip (true-system context derived from labels),
# mines separators, and simulates candidate gates. New file; touches nothing existing.
import sys, os, json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, r"research\original_trader_reconstruction\solar_family\src"))
from otr_engine import load_ledger, run_wrapper, WrapperPolicy

OUT = os.path.join(ROOT, r"runs\OTR_R1_SERIES\out")
LEDGER = os.path.join(ROOT, r"research\03_reverse_engineering\ledgers\t2_canonical_1m.csv")
LABELS = os.path.join(OUT, "r12f_flip_features.csv")


def build():
    bars = load_ledger(LEDGER)
    t = bars["time"]
    tidx = {str(x): i for i, x in enumerate(t)}
    lab = pd.read_csv(LABELS)

    pol = WrapperPolicy(comm_side=2.09, entry_types=(1,), reverse_on_flip=True)
    res = run_wrapper(bars, pol)
    tr = pd.DataFrame(res["trades"])
    tr["entry_dt"] = pd.to_datetime(tr["entry_time"])
    jan = tr[tr["entry_dt"] < "2023-01-21"].reset_index(drop=True)
    assert len(jan) == len(lab)
    lab = lab.sort_values("entry_time").reset_index(drop=True)
    jan = jan.sort_values("entry_time").reset_index(drop=True)
    assert (lab["entry_time"].values == jan["entry_time"].values).all()
    lab["exit_time"] = jan["exit_time"].values
    lab["entry_i"] = [tidx[x] for x in lab["entry_time"]]
    lab["exit_i"] = [tidx[x] for x in lab["exit_time"]]

    # true-system position context: taken trades occupy [entry_i, exit_i)
    taken = lab[lab.label == "TAKE"]
    lab["true_ctx"] = "flat"
    lab["pos_before"] = 0
    for k, r in lab.iterrows():
        s = r["entry_i"] - 1  # signal bar
        for _, q in taken.iterrows():
            if q["entry_i"] <= s < q["exit_i"]:
                lab.loc[k, "true_ctx"] = "reversal"
                lab.loc[k, "pos_before"] = 1 if q["dir"] == "L" else -1
                break
    return bars, lab, jan


def features(bars, lab):
    t = bars["time"]; c = bars["close"]; o = bars["open"]
    h = bars["high"]; l = bars["low"]; v = bars["volume"]
    sid = bars["session_id"]; fb = bars["first_bar"]; lastb = bars["last_bar"]
    sw = bars["signal_wave"]; strend = bars["signal_trend"]; st = bars["signal_trade"]
    sopen = np.where(fb)[0]
    slast = np.where(lastb)[0]

    dt = pd.to_datetime(t)
    dow = dt.dayofweek.values  # Mon=0
    rows = []
    for k, r in lab.iterrows():
        i = r["entry_i"]; s = i - 1
        so = sopen[sid[s]]; sl = slast[sid[s]]
        prev_sl = so - 1 if so > 0 else so
        d = 1 if r["dir"] == "L" else -1
        sess_len = (t[sl] - t[so]).astype("timedelta64[m]").astype(int)
        prev_sess_len = None
        if sid[s] > 0:
            pso = sopen[sid[s] - 1]
            prev_sess_len = (t[prev_sl] - t[pso]).astype("timedelta64[m]").astype(int)
        gap_days = (t[so].astype("datetime64[D]") - t[prev_sl].astype("datetime64[D]")).astype(int) if so > 0 else 0
        mod = (t[s] - t[s].astype("datetime64[D]")).astype("timedelta64[m]").astype(int)
        rows.append(dict(
            entry_time=r["entry_time"], label=r["label"], cert=r["certainty"], dir=r["dir"],
            true_ctx=r["true_ctx"], pos_before=r["pos_before"],
            sig_mod=int(mod), mins_since_open=int((t[s]-t[so]).astype("timedelta64[m]").astype(int)),
            mins_to_close=int((t[sl]-t[s]).astype("timedelta64[m]").astype(int)),
            dow_sig=int(dow[s]), dow_open=int(dow[so]),
            sess_len=int(sess_len), prev_sess_len=int(prev_sess_len) if prev_sess_len is not None else -1,
            reopen_gap_days=int(gap_days),
            prev_sess_early_close=int(prev_sess_len is not None and prev_sess_len < 1370),
            old_wave=int(sw[s-1]), old_trend=int(strend[s-1]),
            new_leg_dir=d,
            c_sig=float(c[s]), sess_open_px=float(o[so]), prev_close_px=float(c[prev_sl]),
            c_vs_sopen=float(c[s]-o[so]), c_vs_pclose=float(c[s]-c[prev_sl]),
            sess_hi_sofar=float(h[so:s+1].max()), sess_lo_sofar=float(l[so:s+1].min()),
            vol_sig=float(v[s]),
        ))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    bars, lab, jan = build()
    F = features(bars, lab)
    F.to_csv(os.path.join(OUT, "hunt_B_labelfeatures.csv"), index=False)
    pd.set_option("display.width", 300)
    print(F[F.label == "SKIP"].to_string())
