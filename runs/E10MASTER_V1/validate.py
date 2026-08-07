"""E10MASTER_V1 validation driver — gates V1/V2/V3 per runs/E10MASTER_V1/spec.yaml.

V1: strategy per-bar target sequence == Python simulator target sequence
    (audit04_executable.member_positions on the 13 AUDIT02_V3_SWEEP_B ledgers,
    ffilled onto the strategy's exported primary-bar closes). Every diff itemized.
V2: engine daily P&L (session basis, from the strategy fill ledger) vs
    research/audit/e_variant_daily_vectors.csv E10_round_session:
    corr >= 0.995 AND full-window net within +/-5%.
V3: observed MNQ commission == $0.65/side on every fill.

Run from repo root:  python runs/E10MASTER_V1/validate.py
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from audit04_executable import member_positions          # noqa: E402
from audit03_mtm_run import load_bars                    # noqa: E402
from audit_mtm import session_date                       # noqa: E402

RUN = os.path.join(ROOT, "runs", "E10MASTER_V1")
OUT = os.path.join(RUN, "out")
LEDGER_DIR = os.path.join(ROOT, "runs", "AUDIT02_V3_SWEEP_B", "ledgers")
BARS_CSV = os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv")
VEC_CSV = os.path.join(ROOT, "research", "audit", "e_variant_daily_vectors.csv")
FAM = os.path.join(ROOT, "research", "04_complementary_family")

VOLMULTS = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]


def load_master_bars():
    b = pd.read_csv(os.path.join(OUT, "e10m_v1_bars.csv"), comment="#",
                    parse_dates=["time"])
    return b


def load_master_fills():
    f = pd.read_csv(os.path.join(OUT, "e10m_v1_fills.csv"), comment="#",
                    parse_dates=["time"])
    buy = {"Buy", "BuyToCover"}
    sell = {"Sell", "SellShort"}
    side = np.where(f.order_action.isin(buy), 1,
                    np.where(f.order_action.isin(sell), -1, 0))
    assert (side != 0).all(), "unknown order_action"
    f["delta"] = side * f.qty
    return f


def gate_v1():
    bars = load_bars()   # includes the missing final 17:00 boundary bar
    paths = [os.path.join(LEDGER_DIR,
             "b2v3__tf3_sm179_am0_th1_vp460_vm%d_xm0_sc_slip1.csv" % v)
             for v in VOLMULTS]
    pos, rawpx, spread = member_positions(paths, bars)
    mean_pos = pos.mean(axis=1)
    tgt = (mean_pos * 10).round()

    mb = load_master_bars()
    # simulator target ffilled onto the strategy's exported bar closes
    sim = tgt.reindex(mb.time, method="ffill").fillna(0.0).astype(int).values
    eng = mb.tgt_close.values
    diff_mask = sim != eng
    diffs = mb.loc[diff_mask, ["time", "bar", "sess_end", "sum", "tgt_close"]].copy()
    diffs["sim_tgt"] = sim[diff_mask]
    n = len(mb)
    nd = int(diff_mask.sum())
    # member-level comparison at bar closes (positions, not just target)
    posb = pos.reindex(mb.time, method="ffill").fillna(0.0).astype(int)
    memcols = ["p%d" % v for v in VOLMULTS]
    mem_eng = mb[memcols].values
    mem_diff = (posb.values != mem_eng).any(axis=1)
    md = int(mem_diff.sum())
    return dict(bars=n, target_diffs=nd, member_diff_bars=md,
                match_pct=100.0 * (n - nd) / n, raw_spread=spread,
                diffs=diffs, mb=mb, pos=pos, posb=posb, mem_diff=mem_diff)


def gate_v2():
    f = load_master_fills()
    assert (f.instrument == "MNQU6").all(), "non-MNQ fill present"
    f["sess"] = [session_date(t) for t in f.time]
    # flat at every session close?
    endpos = f.groupby("sess").delta.sum().cumsum()
    not_flat = endpos[endpos != 0]
    # session cash P&L (MNQ $2/point), slippage embedded in fill prices
    f["cash"] = -f.delta * f.price * 2.0 - f.commission
    eng = f.groupby("sess").cash.sum()
    eng.index = pd.to_datetime(eng.index)

    vec = pd.read_csv(VEC_CSV, parse_dates=["day"]).set_index("day")
    ref = vec["E10_round_session"].dropna()

    both = pd.DataFrame({"eng": eng, "ref": ref}).fillna(0.0)
    corr = both.eng.corr(both.ref)
    net_e, net_r = both.eng.sum(), both.ref.sum()
    daily = both.copy()
    daily["diff"] = daily.eng - daily.ref
    return dict(corr=corr, net_engine=net_e, net_ref=net_r,
                net_ratio=net_e / net_r, sessions_engine=int((eng != 0).sum()),
                sessions_ref=len(ref), not_flat=not_flat, daily=daily, fills=f)


def gate_v3(f):
    per_side = (f.commission / f.qty).round(6)
    bad = f[per_side != 0.65]
    return dict(all_065=len(bad) == 0, n_bad=len(bad),
                total_commission=f.commission.sum(),
                contracts_traded=int(f.qty.sum()))


def dd(series):
    eq = series.cumsum()
    return (eq - eq.cummax()).min()


def main():
    v1 = gate_v1()
    print("V1 bars=%d target_diffs=%d member_diff_bars=%d match=%.5f%% spread=%.3f"
          % (v1["bars"], v1["target_diffs"], v1["member_diff_bars"],
             v1["match_pct"], v1["raw_spread"]))
    if v1["target_diffs"]:
        print(v1["diffs"].head(40).to_string())

    v2 = gate_v2()
    print("V2 corr=%.6f net_engine=%.2f net_ref=%.2f ratio=%.4f"
          % (v2["corr"], v2["net_engine"], v2["net_ref"], v2["net_ratio"]))
    if len(v2["not_flat"]):
        print("NOT FLAT sessions:", v2["not_flat"])

    v3 = gate_v3(v2["fills"])
    print("V3 all_0.65=%s bad=%d total_comm=%.2f contracts=%d"
          % (v3["all_065"], v3["n_bad"], v3["total_commission"],
             v3["contracts_traded"]))

    d = v2["daily"]
    sd = d.eng.std(ddof=1)
    sharpe = d.eng.mean() / sd * np.sqrt(252) if sd else 0.0
    print("engine daily: n=%d net=%.2f sharpe=%.4f maxDD(session)=%.2f worst=%.2f"
          % (len(d), d.eng.sum(), sharpe, dd(d.eng), d.eng.min()))
    print("ref    daily: maxDD(session)=%.2f" % dd(d.ref))

    # parity CSVs
    os.makedirs(FAM, exist_ok=True)
    v1["diffs"].to_csv(os.path.join(FAM, "e10master_target_parity_diffs.csv"),
                       index=False)
    d.to_csv(os.path.join(FAM, "e10master_daily_parity.csv"))
    print("wrote parity CSVs")
    return v1, v2, v3


if __name__ == "__main__":
    main()
