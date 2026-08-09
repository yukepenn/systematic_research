"""ENGINE3_SLATE5_CROSSMARKET -- 3 bounded candidates, implements frozen spec.yaml exactly.
Reuses runs/SMV2AB_ENGINE3_S4/out/merged_3m_dev.parquet verbatim (no substrate rebuild) and
duplicates (not imports, to avoid re-running slate 4's whole script as an import side effect)
its small set of already-verified shared helper functions.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from sm01_solarsim import _fill
from smv2_common import boot_ci_mean

RUN = os.path.join(ROOT, "runs", "ENGINE3_SLATE5_CROSSMARKET")
OUT = os.path.join(RUN, "out")
PV, COMM_RT = 20.0, 4.36
DEV_END = pd.Timestamp("2026-05-31")
NW_LAG = 5
SPLIT = pd.Timestamp("2024-12-31")
BOOT_BLOCK, BOOT_B, BOOT_SEED = 5, 10000, 20260809
BURNIN_SESSIONS = 20

M = pd.read_parquet(os.path.join(ROOT, "runs", "SMV2AB_ENGINE3_S4", "out", "merged_3m_dev.parquet"))
M = M.sort_values("time").reset_index(drop=True)
M["sd"] = pd.to_datetime(M["sd"])
SESSION_ORDER = np.sort(M["sess_id"].unique())
SESS_RANK = pd.Series(np.arange(len(SESSION_ORDER)), index=SESSION_ORDER)
M["sess_rank"] = M["sess_id"].map(SESS_RANK).to_numpy()
sess_rank_arr = M["sess_rank"].to_numpy()
print(f"loaded merged table: {len(M)} bars, {len(SESSION_ORDER)} sessions", flush=True)


# ============================================================================ shared helpers (verbatim ports)
def trailing_session_stats(df, col, n_sessions=BURNIN_SESSIONS):
    x = df[col]; valid = x.notna()
    s = pd.DataFrame({"sess_id": df["sess_id"], "x": x.where(valid, 0.0), "v": valid.astype(float)})
    agg = s.groupby("sess_id").agg(sumx=("x", "sum"), sumx2=("x", lambda z: float((z ** 2).sum())), n=("v", "sum"))
    agg = agg.reindex(SESSION_ORDER).fillna(0.0)
    tr_sumx = agg["sumx"].rolling(n_sessions).sum().shift(1)
    tr_sumx2 = agg["sumx2"].rolling(n_sessions).sum().shift(1)
    tr_n = agg["n"].rolling(n_sessions).sum().shift(1)
    mean_tr = tr_sumx / tr_n
    var_tr = (tr_sumx2 / tr_n - mean_tr ** 2).clip(lower=0.0)
    std_tr = np.sqrt(var_tr).where(tr_n >= 2)
    return mean_tr.reindex(df["sess_id"]).to_numpy(), std_tr.reindex(df["sess_id"]).to_numpy()


def zscore(df, col, n_sessions=BURNIN_SESSIONS):
    mean_map, std_map = trailing_session_stats(df, col, n_sessions)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (df[col].to_numpy() - mean_map) / std_map


def nw_stats(x, sess_dates, lag=NW_LAG):
    x = np.asarray(x, dtype=float); n = len(x)
    out = {"n": n, "mean": np.nan, "total": np.nan, "t_nw": np.nan, "n_sessions": 0}
    if n == 0:
        return out
    xbar = x.mean(); out["mean"] = xbar; out["total"] = x.sum()
    if n < 3:
        return out
    dfz = pd.DataFrame({"x": x - xbar, "s": pd.to_datetime(list(sess_dates))})
    z = dfz.groupby("s", sort=True)["x"].sum().to_numpy()
    out["n_sessions"] = len(z)
    Snw = float((z ** 2).sum())
    L = min(lag, len(z) - 1)
    for l in range(1, L + 1):
        w = 1.0 - l / (lag + 1.0)
        Snw += 2.0 * w * float((z[l:] * z[:-l]).sum())
    if Snw > 0:
        out["t_nw"] = xbar / (np.sqrt(Snw) / n)
    return out


def split_stats(sd, net):
    sd = pd.to_datetime(pd.Series(sd)).reset_index(drop=True)
    net = pd.Series(net).reset_index(drop=True)
    h1 = net[sd.values <= SPLIT]; h2 = net[sd.values > SPLIT]
    return nw_stats(h1, sd[sd.values <= SPLIT]), nw_stats(h2, sd[sd.values > SPLIT])


def boot_p(net):
    if len(net) < 5:
        return np.nan
    _, _, p = boot_ci_mean(np.asarray(net, dtype=float), block=BOOT_BLOCK, n_boot=BOOT_B, seed=BOOT_SEED)
    return p


def sgn(v):
    return int(np.sign(v)) if np.isfinite(v) else 0


nq_o = M["nq_open"].to_numpy(); nq_h = M["nq_high"].to_numpy()
nq_l = M["nq_low"].to_numpy(); nq_c = M["nq_close"].to_numpy()
sd_arr = M["sd"].to_numpy()


def fill_open(i, side):
    return _fill(nq_o[i], nq_h[i], nq_l[i], side)


def fill_close(i, side):
    return _fill(nq_o[i], nq_h[i], nq_l[i], side, at_close=nq_c[i])


GATES = []
VERDICTS = {}

# ============================================================================ CANDIDATE 1: Europe -> US lead
print("=" * 90); print("CANDIDATE 1: Europe (YM) -> US (NQ) session lead"); print("=" * 90)

M["bar_hm"] = pd.to_datetime(M["time"]).dt.hour * 100 + pd.to_datetime(M["time"]).dt.minute
M["r_ym_from_open"] = np.log(M["ym_close"] / M.groupby("sess_id")["ym_open"].transform("first"))
M["r_nq_from_open"] = np.log(M["nq_close"] / M.groupby("sess_id")["nq_open"].transform("first"))
decision_mask = (M["bar_hm"] >= 754) & (M["bar_hm"] <= 800)  # last bar at/near 08:00 ET
dec = M[decision_mask].sort_values(["sess_id", "time"]).groupby("sess_id").last().reset_index()
dec_full = dec.merge(M[["sess_id"]].drop_duplicates(), on="sess_id", how="right").sort_values("sess_id")
dec_full["sess_rank"] = dec_full["sess_id"].map(SESS_RANK)
z_ym = zscore(dec_full, "r_ym_from_open")
z_nq = zscore(dec_full, "r_nq_from_open")
burnin_ok1 = dec_full["sess_rank"].to_numpy() >= BURNIN_SESSIONS
r_ym = dec_full["r_ym_from_open"].to_numpy()

c1_rows = []
c1_events_center = None
for YMZ in (1.0, 1.25, 1.5):
    mask = burnin_ok1 & np.isfinite(z_ym) & np.isfinite(z_nq) & (np.abs(z_ym) > YMZ) & (np.abs(z_nq) < 0.5) & (r_ym != 0)
    idx = dec_full.index[mask].to_numpy()
    sess_ids = dec_full.loc[idx, "sess_id"].to_numpy()
    directions = np.sign(r_ym[idx])
    entry_gidx, exit_gidx, nets, sds = [], [], [], []
    for sid, d in zip(sess_ids, directions):
        sess_bars = M[M["sess_id"] == sid]
        entry_row = sess_bars[decision_mask.reindex(sess_bars.index, fill_value=False)]
        if len(entry_row) == 0:
            continue
        e_gidx = entry_row.index[-1]
        last_gidx = sess_bars.index[-1]
        ep = fill_open(e_gidx, d)
        xp = fill_close(last_gidx, -d)
        net = d * (xp - ep) * PV - COMM_RT
        entry_gidx.append(e_gidx); exit_gidx.append(last_gidx); nets.append(net); sds.append(sd_arr[e_gidx])
    ev = pd.DataFrame({"entry_gidx": entry_gidx, "exit_gidx": exit_gidx, "net": nets, "sd": sds, "dir": directions[:len(nets)]})
    st = nw_stats(ev["net"], ev["sd"]) if len(ev) else nw_stats([], [])
    st.update({"YMZ": YMZ, "p_boot": boot_p(ev["net"].to_numpy()) if len(ev) else np.nan})
    if len(ev):
        h1, h2 = split_stats(ev["sd"], ev["net"])
        st["wf_2022_24_mean"] = h1["mean"]; st["wf_2025_26_mean"] = h2["mean"]
    c1_rows.append(st)
    if YMZ == 1.25:
        c1_events_center = ev.copy()
    print(f"c1 YMZ={YMZ}  N={st['n']:4d}  mean={st['mean']:.2f}  t_nw={st['t_nw']:.2f}", flush=True)

c1_events_center.to_csv(os.path.join(OUT, "c1_events.csv"), index=False)
c1_summary = pd.DataFrame(c1_rows)
c1_summary.to_csv(os.path.join(OUT, "c1_summary.csv"), index=False)
g1c = c1_summary[c1_summary["YMZ"] == 1.25].iloc[0]
plateau1 = set(sgn(v) for v in c1_summary["mean"])
GATES += [
    {"candidate": "c1_europe_lead", "gate": "N>=40", "value": g1c["n"], "pass": bool(g1c["n"] >= 40)},
    {"candidate": "c1_europe_lead", "gate": "t_nw>=2", "value": g1c["t_nw"], "pass": bool(np.isfinite(g1c["t_nw"]) and g1c["t_nw"] >= 2)},
    {"candidate": "c1_europe_lead", "gate": "WF_same_sign",
     "value": f"{g1c.get('wf_2022_24_mean', np.nan):.2f}|{g1c.get('wf_2025_26_mean', np.nan):.2f}",
     "pass": bool(len(c1_events_center) and sgn(g1c["wf_2022_24_mean"]) == sgn(g1c["wf_2025_26_mean"]) != 0)},
    {"candidate": "c1_europe_lead", "gate": "plateau_YMZ_1.0_1.25_1.5_same_sign", "value": str(sorted(plateau1)), "pass": bool(len(plateau1) == 1)},
]
VERDICTS["c1_europe_lead"] = "PASS" if all(g["pass"] for g in GATES if g["candidate"] == "c1_europe_lead") else "FAIL"
print(f"C1 VERDICT: {VERDICTS['c1_europe_lead']}\n", flush=True)

# ============================================================================ CANDIDATE 2: NDX-100 rebalance
print("=" * 90); print("CANDIDATE 2: NDX-100 annual special-rebalance (3rd-Friday December, T-1..T+1)"); print("=" * 90)

sess_first = M.groupby("sess_id").first(); sess_last = M.groupby("sess_id").last()
SESS = pd.DataFrame({"sess_id": SESSION_ORDER, "sd": sess_first.loc[SESSION_ORDER, "sd"].to_numpy(),
                      "nq_o": sess_first.loc[SESSION_ORDER, "nq_open"].to_numpy(),
                      "nq_c": sess_last.loc[SESSION_ORDER, "nq_close"].to_numpy()}).reset_index(drop=True)
SESS["rank"] = np.arange(len(SESS))
SD_TO_RANK = dict(zip(pd.to_datetime(SESS["sd"]), SESS["rank"]))
SD_SET = set(pd.to_datetime(SESS["sd"]))

dec_fridays = [pd.Timestamp(t.date()) for t in pd.date_range("2022-01-01", DEV_END, freq="WOM-3FRI") if t.month == 12]
c2_rows = []
for T in dec_fridays:
    if T not in SD_SET:
        continue
    T_rank = SD_TO_RANK[T]
    if T_rank < 5 or T_rank + 1 >= len(SESS):
        continue
    pre_ret = np.log(SESS.loc[T_rank - 1, "nq_c"] / SESS.loc[T_rank - 5, "nq_c"])
    direction = int(np.sign(pre_ret))
    if direction == 0:
        continue
    entry_rank = T_rank - 1
    exit_rank = T_rank + 1
    ep = _fill(SESS.loc[entry_rank, "nq_o"], SESS.loc[entry_rank, "nq_o"], SESS.loc[entry_rank, "nq_o"], direction)
    xp = _fill(SESS.loc[exit_rank, "nq_c"], SESS.loc[exit_rank, "nq_c"], SESS.loc[exit_rank, "nq_c"], -direction)
    net = direction * (xp - ep) * PV - COMM_RT
    c2_rows.append({"T": T, "entry_sd": SESS.loc[entry_rank, "sd"], "exit_sd": SESS.loc[exit_rank, "sd"],
                     "pre_ret_5sess": pre_ret, "dir": direction, "net": net})

c2 = pd.DataFrame(c2_rows)
c2.to_csv(os.path.join(OUT, "c2_events.csv"), index=False)
st2 = nw_stats(c2["net"], c2["entry_sd"]) if len(c2) else nw_stats([], [])
print(f"c2: {len(dec_fridays)} December-3rd-Friday candidates in dev window; {len(c2)} tradeable events", flush=True)
print(f"c2 N={st2['n']}  mean={st2['mean']}  t_nw={st2['t_nw']}", flush=True)
GATES += [
    {"candidate": "c2_ndx_rebalance", "gate": "N>=12 (pre-registered EXPECTED FAIL, N<=4 by construction)",
     "value": st2["n"], "pass": bool(st2["n"] >= 12)},
]
VERDICTS["c2_ndx_rebalance"] = "FAIL (power floor, as pre-registered)" if st2["n"] < 12 else ("PASS" if st2.get("t_nw", 0) >= 2 else "FAIL")
print(f"C2 VERDICT: {VERDICTS['c2_ndx_rebalance']}\n", flush=True)

# ============================================================================ CANDIDATE 3: weekend lag + any-gap control
print("=" * 90); print("CANDIDATE 3: weekend info-diffusion lag, with mandatory any-gap head-to-head control"); print("=" * 90)

SESS["r_es"] = np.log(sess_last.loc[SESSION_ORDER, "es_close"].to_numpy() / sess_first.loc[SESSION_ORDER, "es_open"].to_numpy())
SESS["r_nq_full"] = np.log(sess_last.loc[SESSION_ORDER, "nq_close"].to_numpy() / sess_first.loc[SESSION_ORDER, "nq_open"].to_numpy())
SESS["r_ym"] = np.log(sess_last.loc[SESSION_ORDER, "ym_close"].to_numpy() / sess_first.loc[SESSION_ORDER, "ym_open"].to_numpy())
SESS["dow"] = pd.to_datetime(SESS["sd"]).dt.dayofweek  # Mon=0 .. Fri=4


def consensus_events(rank_pairs, tag):
    rows = []
    for prev_rank, cur_rank in rank_pairs:
        r_es, r_nq, r_ym = SESS.loc[prev_rank, ["r_es", "r_nq_full", "r_ym"]]
        s = {np.sign(r_es), np.sign(r_nq), np.sign(r_ym)}
        if len(s) != 1 or 0.0 in s:
            continue
        direction = int(list(s)[0])
        ep = fill_open(M[M["sess_id"] == SESS.loc[cur_rank, "sess_id"]].index[0], direction)
        cur_bars = M[M["sess_id"] == SESS.loc[cur_rank, "sess_id"]]
        xp = fill_close(cur_bars.index[-1], -direction)
        net = direction * (xp - ep) * PV - COMM_RT
        rows.append({"prev_sd": SESS.loc[prev_rank, "sd"], "entry_sd": SESS.loc[cur_rank, "sd"],
                      "dir": direction, "net": net, "kind": tag})
    return pd.DataFrame(rows)


weekend_pairs = [(r, r + 1) for r in SESS["rank"][:-1] if SESS.loc[r, "dow"] == 4 and SESS.loc[r + 1, "dow"] == 0]
anygap_pairs = [(r, r + 1) for r in SESS["rank"][:-1] if not (SESS.loc[r, "dow"] == 4 and SESS.loc[r + 1, "dow"] == 0)]

c3_weekend = consensus_events(weekend_pairs, "weekend")
c3_control = consensus_events(anygap_pairs, "any_gap_control")
c3_weekend.to_csv(os.path.join(OUT, "c3_weekend_events.csv"), index=False)
c3_control.to_csv(os.path.join(OUT, "c3_control_events.csv"), index=False)

st3w = nw_stats(c3_weekend["net"], c3_weekend["entry_sd"]) if len(c3_weekend) else nw_stats([], [])
st3c = nw_stats(c3_control["net"], c3_control["entry_sd"]) if len(c3_control) else nw_stats([], [])
print(f"c3 weekend: N={st3w['n']}  mean={st3w['mean']:.2f}  t_nw={st3w['t_nw']:.2f}", flush=True)
print(f"c3 any-gap control: N={st3c['n']}  mean={st3c['mean']:.2f}  t_nw={st3c['t_nw']:.2f}", flush=True)
head_to_head_pass = bool(np.isfinite(st3w["mean"]) and np.isfinite(st3c["mean"]) and st3w["mean"] > st3c["mean"])
h1w, h2w = split_stats(c3_weekend["sd" if "sd" in c3_weekend.columns else "entry_sd"], c3_weekend["net"]) if len(c3_weekend) else (nw_stats([], []), nw_stats([], []))
GATES += [
    {"candidate": "c3_weekend_lag", "gate": "N>=40", "value": st3w["n"], "pass": bool(st3w["n"] >= 40)},
    {"candidate": "c3_weekend_lag", "gate": "t_nw>=2", "value": st3w["t_nw"], "pass": bool(np.isfinite(st3w["t_nw"]) and st3w["t_nw"] >= 2)},
    {"candidate": "c3_weekend_lag", "gate": "WF_same_sign",
     "value": f"{h1w['mean']:.2f}|{h2w['mean']:.2f}", "pass": bool(sgn(h1w["mean"]) == sgn(h2w["mean"]) != 0)},
    {"candidate": "c3_weekend_lag", "gate": "weekend_mean_beats_anygap_control (MANDATORY per ledger)",
     "value": f"{st3w['mean']:.2f} vs {st3c['mean']:.2f}", "pass": head_to_head_pass},
]
VERDICTS["c3_weekend_lag"] = "PASS" if all(g["pass"] for g in GATES if g["candidate"] == "c3_weekend_lag") else "FAIL"
print(f"C3 VERDICT: {VERDICTS['c3_weekend_lag']}\n", flush=True)

gates_df = pd.DataFrame(GATES)
gates_df.to_csv(os.path.join(OUT, "gates.csv"), index=False)
json.dump(VERDICTS, open(os.path.join(OUT, "verdicts.json"), "w"), indent=2)
print("\nFINAL VERDICTS:", VERDICTS, flush=True)
