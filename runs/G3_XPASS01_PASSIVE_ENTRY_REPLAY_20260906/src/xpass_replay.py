"""G3_XPASS01 - Class-X EXECUTION replay: P1/PCT passive-entry policy (join-bid limit + T-sec timeout).

Spec: runs/G3_XPASS01_PASSIVE_ENTRY_REPLAY_20260906/DESIGN_FROZEN.md (frozen before results).
Class-X EXECUTION / DISCOVERY-grade. Output prices an execution policy; it is NEVER alpha evidence.

Program order (binding):
  Phase 0  registers + substrate census (file NAMES only) -> replay set, G0/G0b.
           Pool exclusion happens HERE, before any tick parquet is opened: no frozen-pool
           session's price content is ever read by this program.
  Phase 1  G0c bench parity (xinst_bench on the FREE SM1M NQ 1-min substrate) - RAISE on failure.
  Phase 2  entry population from the bench trade list; anchors.
  Pass 1   per-session tick read #1: measurability + anchor BBO snapshot (spread) ONLY.
           No policy fill is evaluated, no chase price stored.
  G1       MDE-first barrier printed (mde_barrier.txt) BEFORE any policy outcome is computed.
  Pass 2   per-session tick read #2: fills (strict/at-touch/+1-tick stress), time-to-fill, chase.
  Phase 4  G2-G6 gates, fill curves, decision rule, outputs.

Seal: every session < 2026-08-01, asserted at load. int64-ns discipline asserted everywhere.
"""
from __future__ import annotations

import csv
import os
import re
import sys
import time as _time

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(REPO, "runs", "G3_XPASS01_PASSIVE_ENTRY_REPLAY_20260906")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

WE_SRC = os.path.join(REPO, "research", "weekly_edge", "src")
XINST_SRC = os.path.join(REPO, "runs", "XINST01_WEEKLY_EDGE_PORT_20260906", "src")
for p_ in (WE_SRC, XINST_SRC):
    if p_ not in sys.path:
        sys.path.insert(0, p_)

# ------------------------------------------------------------------ constants (preregistered)
PV = 20.0                      # $/point NQ
TICK = 0.25                    # points
DV = PV * TICK                 # $/tick = 5.0
RATE_W103 = 14.436482661004954  # $/ctrRT modelled spread addend (WE_W103 convention)
T_LIST = [5, 30, 120]          # seconds, preregistered family (3)
DELTA_PRIMARY_MS = 250
DELTA_SENS_MS = [100, 1000]
NS = np.int64(1_000_000_000)
GAP_NS = np.int64(60) * NS      # >60s silence = data gap
STALE_NS = np.int64(60) * NS    # snapshot must be found within 60s
COVER_PRE_NS = np.int64(60) * NS
COVER_POST_NS = np.int64(180) * NS  # 120s max T + 60s chase margin
SEAL_DATE = "20260801"
BOOT_B = 10000
BOOT_SEED = 20260906
Z_BONF = 2.393980261354979     # z_{1 - (0.05/3)/2}
Z_POW = 0.8416212335729143     # z_{0.80}
MDE_FACTOR = Z_BONF + Z_POW    # 3.2356
Q_BONF = (0.05 / 3) / 2        # 0.0083333 per tail
KILL1_FLOOR = 2.50             # $/ctr-entry materiality floor (declared in DESIGN 5)
FILLRATE_FLOOR = 0.20
CEIL_RTH = 15.0                # $/ctr, median RTH 3 ticks (MEASURED)
CEIL_ALLH = 20.0               # $/ctr, all-hours 4 ticks (MEASURED, burned-window)

V2_DIR = os.path.join(REPO, "research", "data_microstructure_v2", "raw", "NQ")
V1_DIR = os.path.join(REPO, "research", "scalping_lab", "substrate", "raw", "NQ")
ES_DIR = os.path.join(REPO, "research", "data_esnq", "parquet", "NQ")
REG_W5 = os.path.join(REPO, "runs", "W5_PROTECTED_CONFIRMATION", "manifest_work",
                      "confirmation_pool_168_dates.txt")
REG_B1 = os.path.join(REPO, "runs", "W5_PROTECTED_CONFIRMATION", "manifest_work",
                      "batch1_export_sessions.txt")
REG_MICRO = os.path.join(REPO, "runs", "MICRO_DISCOVERY_CONFIRMATION_SPLIT", "out",
                         "MICRO_BLIND_CONFIRMATION_POOL.csv")
REG_BBO = os.path.join(REPO, "runs", "BBO_COMPLETENESS_RECENSUS_V1_20260828", "out",
                       "BBO_BLIND_POOL_MANIFEST.csv")
REG_ESNQ = os.path.join(REPO, "runs", "ESNQ_V1_20260828", "manifests", "ESNQ_BLIND_15.csv")

# committed P1/PCT targets (WE_W103_CONSOLIDATE/out/components.csv, same as XINST01 G0)
TGT = dict(weekly=1393.5736634670018, maxdd=22930.665852795442, t=4.1636115325867715,
           trades=2401.0, rate=14.436482661004954)
NQ_1M = "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet"

LOG_LINES = []
GATE_ROWS = []  # (gate, spec, observed, verdict)


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG_LINES.append(s)


def gate(name, spec, observed, verdict):
    GATE_ROWS.append((name, spec, observed, verdict))
    P(f"  GATE {name:<26} | SPEC {spec:<58} | OBSERVED {observed:<44} | {verdict}")


def hdr(title):
    P("")
    P("=" * 118)
    P(f"=== {title}")
    P("    [Class-X EXECUTION replay - DISCOVERY-grade by construction - NEVER alpha evidence]")
    P("=" * 118)


# ================================================================== Phase 0: registers / union
def phase0():
    hdr("PHASE 0 - clean tick union + mechanical pool re-intersection (file NAMES only)")
    v2 = {f[1:9] for f in os.listdir(V2_DIR) if re.fullmatch(r"s\d{8}\.parquet", f)}
    v1_files = [f for f in os.listdir(V1_DIR) if f.endswith(".parquet")]
    v1 = {re.match(r"s(\d{8})", f).group(1) for f in v1_files}
    es = {f[1:9] for f in os.listdir(ES_DIR) if re.fullmatch(r"s\d{8}\.parquet", f)}
    union = v2 | v1 | es
    P(f"  substrates: v2 {len(v2)} sessions | v1 {len(v1_files)} files / {len(v1)} sessions | "
      f"ESNQ {len(es)} sessions | UNION {len(union)} sessions "
      f"({min(union)} -> {max(union)})")
    if len(union) != 104:
        raise RuntimeError(f"union count {len(union)} != 104 (GOVERNANCE_PRECHECK premise)")

    w5 = {l.strip() for l in open(REG_W5, encoding="utf-8") if l.strip()}
    b1 = {l.strip() for l in open(REG_B1, encoding="utf-8") if l.strip()}
    micro, bbo, esb = set(), set(), set()
    with open(REG_MICRO, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            micro.add(row["session"][1:] if row["session"].startswith("s") else row["session"])
    with open(REG_BBO, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            bbo.add(row["session_date"].replace("-", ""))
    with open(REG_ESNQ, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            esb.add(row["session_date"].replace("-", ""))
    P(f"  registers: W5-168 {len(w5)} | batch1 {len(b1)} | MICRO {len(micro)} | "
      f"BBO_BLIND {len(bbo)} | ESNQ_BLIND {len(esb)}")
    for nm, s_, n_ in (("W5", w5, 168), ("MICRO", micro, 141), ("BBO", bbo, 19),
                       ("ESNQ_BLIND", esb, 15), ("batch1", b1, 8)):
        if len(s_) != n_:
            raise RuntimeError(f"register {nm} count {len(s_)} != {n_}")

    pools = w5 | micro | bbo | esb
    inter104 = sorted(union & pools)
    inter_b1 = sorted(set(inter104) & b1)
    inter_rest = sorted(set(inter104) - b1)
    P(f"  104-union \u2229 (W5\u222aMICRO\u222aBBO\u222aESNQ) = {len(inter104)} session(s): "
      f"{inter104}")
    P(f"    decomposition: {len(inter_b1)} batch-1-CONSUMED {inter_b1}")
    P(f"                 + {len(inter_rest)} W5 protected members with tick content later "
      f"materialized by MS01/ESNQ dev {inter_rest}")
    P(f"    (matches BBO_GOVERNANCE_MEMO footnote: '13 W5 members were batch-consumed or later")
    P(f"     legitimately materialized' = 8 batch-1 + 13 materialized = 21; the memo's")
    P(f"     'pool \u2229 extracted = 0' claim held only for the BBO/MICRO/ESNQ registers.)")
    per_reg = {"W5-168": sorted(union & w5), "MICRO": sorted(union & micro),
               "BBO_BLIND": sorted(union & bbo), "ESNQ_BLIND": sorted(union & esb)}
    for k, v_ in per_reg.items():
        P(f"    union \u2229 {k}: {len(v_)}")

    # the frozen G0b premise row - recorded FAILED (never redefined to pass)
    gate("G0b-i 104-union \u2229 pools", "= \u2205 (GOVERNANCE_PRECHECK premise)",
         f"{len(inter104)} sessions (all W5-168; other 3 registers = 0)",
         "FAIL (premise false; recorded)")
    # conservative mechanical remediation: EXCLUDE every pool member BEFORE any tick read
    replay = sorted(union - pools)
    P(f"  -> CONSERVATIVE EXCLUSION applied at load: the {len(inter104)} W5-pool sessions are")
    P(f"     DROPPED from the replay set before any tick file is opened. No pool member's price")
    P(f"     content is read by this program. Replay set = {len(replay)} sessions.")
    inter_final = sorted(set(replay) & pools)
    gate("G0b-ii replay-set \u2229 pools", "= \u2205 after exclusion; RAISE if nonempty",
         f"{len(inter_final)} sessions over 4 registers", "PASS" if not inter_final else "FAIL")
    if inter_final:
        raise RuntimeError("replay set still intersects a frozen pool")
    g505 = ("20260505" not in union) and ("20260505" not in replay)
    gate("G0b-iii 2026-05-05 absent", "2026-05-05 \u2209 union and \u2209 replay set",
         f"absent={g505}", "PASS" if g505 else "FAIL")
    if not g505:
        raise RuntimeError("2026-05-05 present")
    seal_ok = max(replay) < SEAL_DATE
    gate("G0 seal (session names)", f"every replay session < {SEAL_DATE}",
         f"max session {max(replay)}", "PASS" if seal_ok else "FAIL")
    if not seal_ok:
        raise RuntimeError("seal violation in replay set")

    # precedence map v2 > ESNQ > v1 (NEVER merge substrates within a session)
    sub_of = {}
    for d in replay:
        sub_of[d] = "v2" if d in v2 else ("es" if d in es else "v1")
    cnt = {s: sum(1 for x in sub_of.values() if x == s) for s in ("v2", "es", "v1")}
    P(f"  precedence v2 > ESNQ > v1: v2 {cnt['v2']} | ESNQ {cnt['es']} | v1 {cnt['v1']}")
    v1_trunc = []
    for f in v1_files:
        nrows = pq.ParquetFile(os.path.join(V1_DIR, f)).metadata.num_rows
        if nrows == 12_000_000:
            v1_trunc.append(f)
    P(f"  v1 truncated files (== 12,000,000 rows exactly): {len(v1_trunc)}")
    return dict(replay=replay, sub_of=sub_of, v1_files=v1_files, v1_trunc=set(v1_trunc),
                inter104=inter104, pools=pools, per_reg=per_reg)


# ================================================================== Phase 1: G0c bench parity
def phase1():
    hdr("PHASE 1 - G0c bench parity: xinst_bench reproduces P1/PCT (RAISE on failure)")
    import xinst_bench as XB
    from we_lab import spread_profile
    t0 = _time.time()
    D, bnd = XB.load_substrate(NQ_1M, "NQ")
    P(f"  substrate: {bnd['n_bars']:,} bars / {bnd['n_sess']:,} sessions  "
      f"{bnd['first_sess']} -> {bnd['last_sess']}   dropped>=seal {bnd['n_dropped']}")
    gate("G0 seal (1-min substrate)", "max session < 2026-08-01 at load",
         f"max {bnd['last_sess']}, dropped {bnd['n_dropped']}",
         "PASS" if bnd["seal_ok"] else "FAIL")
    if not bnd["seal_ok"]:
        raise RuntimeError("SEAL VIOLATION on NQ 1-min load")
    tr, meta = XB.build_p1pct(D, PV=20.0, comm=4.36, halt_pts=XB.NQ_HALT_PTS,
                              tgt_pts=XB.NQ_TGT_PTS, smin_pts=None, smax_pts=None,
                              stopm_pts=None, win_a="2022-07-01", win_b="2026-08-01")
    prof = spread_profile()
    net, ct, rate, ntr = XB.net_series(D, tr, PV=20.0, tick=0.25,
                                       spread_model=("nq_profile", prof),
                                       sess_in=meta["sess_in"], i_of=meta["i_of"])
    w, _wk = XB.weekly(D, net, meta["sess_in"])
    pan = XB.panel(w)
    P(f"  rebuilt: {len(tr):,} in-window trades / {meta['n_entries']:,} fills_daily entries / "
      f"size-2 share {100 * meta['size2_share']:.1f}%   [{_time.time() - t0:.0f}s]")
    P(f"  {'metric':<10}{'REBUILT':>18}{'COMMITTED':>18}{'rel diff':>12}")
    ok_all = True
    for k, obs in (("weekly", pan["weekly"]), ("maxdd", pan["maxdd"]), ("t", pan["t"]),
                   ("trades", float(ntr)), ("rate", rate)):
        rd = abs(obs - TGT[k]) / abs(TGT[k])
        P(f"  {k:<10}{obs:>18.6f}{TGT[k]:>18.6f}{100 * rd:>11.4f}%")
        ok_all &= (rd < 5e-7)  # prints as 0.0000%
    gate("G0c bench parity", "all 5 committed metrics reproduced to 0.0000%; RAISE on failure",
         "all 5 at 0.0000%" if ok_all else "MISMATCH", "PASS" if ok_all else "FAIL")
    if not ok_all:
        raise RuntimeError("G0c FAILED: bench does not reproduce P1/PCT - no timestamps emitted")
    trin = meta["trin"]
    return D, meta, trin


# ================================================================== Phase 2: entry population
def phase2(D, meta, trin, reg):
    hdr("PHASE 2 - entry population: bench-regenerated P1/PCT entry events")
    sid, i_of = D["sid"], meta["i_of"]
    sess_date = D["sess_date"]
    rows = []
    for x in trin:
        assert x["d"] == 1, "P1 is long-only; non-buy entry found"
        et = np.datetime64(x["et"], "ns")
        i = i_of(x["et"])
        sd = pd.Timestamp(sess_date[int(sid[i])]).strftime("%Y%m%d")
        action_ns = et.astype(np.int64) - np.int64(60) * NS  # entry executes at bar OPEN
        rows.append(dict(session=sd, et=str(x["et"]), action_ns=int(action_ns),
                         u=int(x["u"]), pnl=float(x["pnl"]),
                         pnl_ctr=float(x["pnl"] / x["u"]),
                         allin_ctr=float(x["pnl"] / x["u"] - RATE_W103)))
    E = pd.DataFrame(rows)
    assert E["action_ns"].dtype == np.int64
    in_union = E["session"].isin(reg["replay"] + reg["inter104"])
    in_replay = E["session"].isin(reg["replay"])
    in_pool_excl = E["session"].isin(reg["inter104"])
    P(f"  bench in-window trades: {len(E):,} "
      f"(convention: et = END-stamp of entry bar; action instant = et - 60s; anchor = action + \u03b4)")
    P(f"  in 104-union sessions: {int(in_union.sum())} | in POOL-EXCLUDED sessions "
      f"(not replayed): {int(in_pool_excl.sum())} | in replay set: {int(in_replay.sum())}")
    Er = E[in_replay].reset_index(drop=True)
    Er["substrate"] = Er["session"].map(reg["sub_of"])
    n_ctr = int(Er["u"].sum())
    P(f"  REPLAY POPULATION: {len(Er)} entry events / {n_ctr} contract-entries in "
      f"{Er['session'].nunique()} sessions")
    # SD of bench per-trade all-in P&L over ALL in-window trades (known discovery content)
    allin_all = E["pnl_ctr"] - RATE_W103
    sd_b = float(allin_all.std(ddof=1))
    P(f"  bench per-ctr all-in trade P&L SD (n={len(E):,}, G1 proxy for accounting B): "
      f"${sd_b:,.0f}  [ALL_IN approx: commission-in, ${RATE_W103:.2f}/ctrRT modelled spread; "
      f"DISCOVERY_CONSUMED]")
    return Er, sd_b


# ================================================================== tick session I/O
def load_session_streams(date, sub, v1_files):
    if sub == "v2":
        paths = [os.path.join(V2_DIR, f"s{date}.parquet")]
    elif sub == "es":
        paths = [os.path.join(ES_DIR, f"s{date}.parquet")]
    else:
        paths = [os.path.join(V1_DIR, f"s{date}.parquet")]
        rth = f"s{date}_rth.parquet"
        if rth in v1_files:
            paths.append(os.path.join(V1_DIR, rth))
    parts = [pq.read_table(p, columns=["bip", "time", "price", "volume"]).to_pandas()
             for p in paths]
    df = pd.concat(parts, ignore_index=True) if len(parts) > 1 else parts[0]
    if len(parts) > 1:  # v1 builder convention (build_grid1s): dedup base+_rth overlap
        df = df.drop_duplicates(subset=["bip", "time", "price", "volume"])
    df = df.sort_values("time", kind="mergesort")
    t = df["time"].to_numpy().astype("datetime64[ns]").view(np.int64)
    assert t.dtype == np.int64, "int64-ns discipline"
    seal_ns = np.datetime64("2026-08-01T00:00:00", "ns").astype(np.int64)
    if t[-1] >= seal_ns:
        raise RuntimeError(f"SEAL VIOLATION: session {date} has ticks >= 2026-08-01")
    bip = df["bip"].to_numpy()
    px = df["price"].to_numpy().astype(np.float64)
    Lm, Bm, Am = bip == 0, bip == 1, bip == 2
    gap_idx = np.flatnonzero(np.diff(t) > GAP_NS)  # gap between t[i] and t[i+1]
    return dict(t=t, Lt=t[Lm], Lp=px[Lm], Bt=t[Bm], Bp=px[Bm], At=t[Am], Ap=px[Am],
                gap_idx=gap_idx, n=len(t))


def covered(S, a, b):
    """True iff [a,b] lies inside one contiguous covered segment (no >60s gap, file spans)."""
    t = S["t"]
    i0 = int(np.searchsorted(t, a, "right")) - 1
    i1 = int(np.searchsorted(t, b, "left"))
    if i0 < 0 or i1 >= len(t):
        return False
    g = S["gap_idx"]
    j = int(np.searchsorted(g, i0, "left"))
    return not (j < len(g) and g[j] < i1)


def snapshot(S, tau, limit):
    """First valid (bid>0, ask>0, ask>=bid) BBO at instant >= tau (state as of <= instant).
    Returns (t_q, bid, ask, n_crossed_skipped) or (None, None, None, n_crossed)."""
    Bt, Bp, At, Ap = S["Bt"], S["Bp"], S["At"], S["Ap"]
    ib = int(np.searchsorted(Bt, tau, "right")) - 1
    ia = int(np.searchsorted(At, tau, "right")) - 1
    crossed = 0
    t_cur = tau
    while True:
        if ib >= 0 and ia >= 0:
            b, a = Bp[ib], Ap[ia]
            if b > 0 and a > 0 and a >= b - 1e-9:
                return t_cur, float(b), float(a), crossed
            crossed += 1
        nb = Bt[ib + 1] if ib + 1 < len(Bt) else None
        na = At[ia + 1] if ia + 1 < len(At) else None
        if nb is None and na is None:
            return None, None, None, crossed
        nxt = min(x for x in (nb, na) if x is not None)
        if nxt > limit:
            return None, None, None, crossed
        if nb is not None and nb == nxt:
            ib += 1
        if na is not None and na == nxt:
            ia += 1
        t_cur = int(nxt)
    # unreachable


def first_hit(tt, pp, a, b, cond):
    """first event time in (a, b] with cond(price)=True, else None."""
    i0 = int(np.searchsorted(tt, a, "right"))
    i1 = int(np.searchsorted(tt, b, "right"))
    if i1 <= i0:
        return None
    m = cond(pp[i0:i1])
    k = int(np.argmax(m)) if m.any() else -1
    return int(tt[i0 + k]) if k >= 0 else None


# ================================================================== Pass 1: measurability
def pass1(Er, reg):
    hdr("PASS 1 - measurability census + anchor BBO snapshots (NO policy outcome evaluated)")
    P("  (This pass reads quote VALIDITY and the anchor quoted spread only - the baseline-leg")
    P("   descriptor preregistered as the G1 variance proxy. No fill rule is evaluated and no")
    P("   chase price is stored in this pass.)")
    deltas = {"d250": DELTA_PRIMARY_MS, "d100": DELTA_SENS_MS[0], "d1000": DELTA_SENS_MS[1]}
    res = {k: dict(tq=[], bid=[], ask=[], valid=[], crossed=[]) for k in deltas}
    meas, reason = [], []
    t0 = _time.time()
    for sess, grp in Er.groupby("session", sort=True):
        S = load_session_streams(sess, reg["sub_of"][sess], reg["v1_files"])
        for idx, e in grp.iterrows():
            a_ns = np.int64(e["action_ns"])
            snaps = {}
            for key, ms in deltas.items():
                anchor = a_ns + np.int64(ms) * np.int64(1_000_000)
                tq, b, a, cr = snapshot(S, anchor, anchor + STALE_NS)
                snaps[key] = (anchor, tq, b, a, cr)
            anchor_p = snaps["d250"][0]
            ok_snap = snaps["d250"][1] is not None
            ok_cov = covered(S, anchor_p - COVER_PRE_NS, anchor_p + COVER_POST_NS)
            ok_chase = True
            if ok_snap and ok_cov:
                for T in T_LIST:
                    ct_ = anchor_p + np.int64(T) * NS
                    tq, b, a, _ = snapshot(S, ct_, ct_ + STALE_NS)
                    if tq is None:
                        ok_chase = False
                        break
            m = ok_snap and ok_cov and ok_chase
            meas.append((idx, m))
            reason.append((idx, "OK" if m else
                           ("NO_VALID_ANCHOR_BBO" if not ok_snap else
                            ("COVERAGE_GAP" if not ok_cov else "NO_CHASE_QUOTE"))))
            for key in deltas:
                anchor, tq, b, a, cr = snaps[key]
                res[key]["tq"].append((idx, tq))
                res[key]["bid"].append((idx, b))
                res[key]["ask"].append((idx, a))
                res[key]["valid"].append((idx, tq is not None))
                res[key]["crossed"].append((idx, cr))
        del S
    P(f"  scanned {Er['session'].nunique()} sessions  [{_time.time() - t0:.0f}s]")
    for key in deltas:
        for col in ("tq", "bid", "ask", "valid", "crossed"):
            s_ = pd.Series({i: v for i, v in res[key][col]})
            Er[f"{key}_{col}"] = s_
    Er["measurable"] = pd.Series({i: v for i, v in meas})
    Er["unmeas_reason"] = pd.Series({i: v for i, v in reason})
    Er["spread_pts"] = Er["d250_ask"] - Er["d250_bid"]
    Er["spread_usd"] = Er["spread_pts"] * PV
    return Er


# ================================================================== G1: MDE-first barrier
def g1_mde(Er, sd_b):
    hdr("G1 - MDE-FIRST BARRIER (printed BEFORE any observed policy outcome)")
    M = Er[Er["measurable"]]
    n = len(M)
    n_ctr = int(M["u"].sum())
    n_sess = M["session"].nunique()
    sd_a = float(M["spread_usd"].std(ddof=1))
    mean_sp = float(M["spread_usd"].mean())
    lines = []

    def Q(s):
        P(s)
        lines.append(s)

    Q(f"  n_measurable = {n} entry events ({n_ctr} contract-entries, {n_sess} sessions)")
    Q(f"  anchor quoted spread (baseline descriptor): mean ${mean_sp:.2f}/ctr, SD ${sd_a:.2f} "
      f"[BASIS SPREAD_ONLY, EVIDENCE MEASURED]")
    Q(f"  MDE = (z_bonf {Z_BONF:.4f} + z_80 {Z_POW:.4f}) * SD / sqrt(n), "
      f"two-sided Bonferroni alpha = 0.05/3")
    mde_a = MDE_FACTOR * sd_a / np.sqrt(max(n, 1))
    mde_b = MDE_FACTOR * sd_b / np.sqrt(max(n, 1))
    Q(f"  ACCOUNTING A (CHASE, primary): variance proxy = anchor-spread distribution ->")
    Q(f"    MDE_A = ${mde_a:.2f}/ctr-entry at 80% power  (proxy covers the filled-leg savings")
    Q(f"    dispersion only; timeout-drift variance is NOT in the proxy - the binding")
    Q(f"    adjudication for A is the G2 bootstrap CI itself)")
    Q(f"  ACCOUNTING B (CANCEL, secondary): variance proxy = bench per-ctr all-in trade P&L SD "
      f"${sd_b:,.0f} ->")
    Q(f"    MDE_B = ${mde_b:,.2f}/ctr-entry at 80% power")
    Q(f"    ceiling (fill_rate=1 x full quoted spread): ${CEIL_RTH:.0f}/ctr RTH (3 tk, MEASURED)"
      f" / ${CEIL_ALLH:.0f}/ctr all-hours (4 tk, MEASURED)")
    b_unpowered = mde_b > CEIL_ALLH
    verdict_b = ("UNPOWERED-BY-DESIGN - components-only reporting, can neither adopt nor kill"
                 if b_unpowered else "POWERED")
    Q(f"    MDE_B ${mde_b:,.2f} > ceiling ${CEIL_ALLH:.0f} ? {b_unpowered} -> "
      f"ACCOUNTING B: {verdict_b}")
    Q(f"    (MDE_B / ceiling = {mde_b / CEIL_ALLH:,.1f}x)")
    gate("G1 MDE-first barrier", "MDE printed before outcomes; if MDE_B > ceiling, B is "
         "UNPOWERED (components only)",
         f"MDE_A ${mde_a:.2f}, MDE_B ${mde_b:,.0f} vs ceil ${CEIL_ALLH:.0f} -> B {'UNPOWERED' if b_unpowered else 'POWERED'}",
         "PASS")
    with open(os.path.join(OUT, "mde_barrier.txt"), "w", encoding="utf-8") as f:
        f.write("G3_XPASS01 - G1 MDE-FIRST BARRIER (written before any policy outcome was "
                "computed)\nClass-X EXECUTION / DISCOVERY-grade - never alpha.\n\n"
                + "\n".join(lines) + "\n")
    return b_unpowered, mde_a, mde_b


# ================================================================== Pass 2: policy outcomes
def pass2(Er, reg):
    hdr("PASS 2 - policy replay: fills (strict / at-touch / +1-tick stress), chase, time-to-fill")
    deltas = {"d250": DELTA_PRIMARY_MS, "d100": DELTA_SENS_MS[0], "d1000": DELTA_SENS_MS[1]}
    Tmax_ns = np.int64(T_LIST[-1]) * NS
    cols = {}
    for key in deltas:
        cols[f"{key}_tt_strict"] = {}
        cols[f"{key}_tt_touch"] = {}
        cols[f"{key}_tt_stress"] = {}
        cols[f"{key}_tt_stress_lit"] = {}
        for T in T_LIST:
            cols[f"{key}_chase_ask_T{T}"] = {}
    t0 = _time.time()
    for sess, grp in Er.groupby("session", sort=True):
        S = load_session_streams(sess, reg["sub_of"][sess], reg["v1_files"])
        for idx, e in grp.iterrows():
            if not e["measurable"]:
                continue
            a_ns = np.int64(e["action_ns"])
            for key, ms in deltas.items():
                anchor = a_ns + np.int64(ms) * np.int64(1_000_000)
                if not e[f"{key}_valid"]:
                    continue
                B = float(e[f"{key}_bid"])
                w0, w1 = anchor, anchor + Tmax_ns
                # strict-through: trade strictly below B, or ask <= B
                h_tr = first_hit(S["Lt"], S["Lp"], w0, w1, lambda p: p < B - 1e-9)
                h_ak = first_hit(S["At"], S["Ap"], w0, w1, lambda p: p <= B + 1e-9)
                tt_s = min([x for x in (h_tr, h_ak) if x is not None], default=None)
                # at-touch (diagnostic): any trade at <= B
                h_to = first_hit(S["Lt"], S["Lp"], w0, w1, lambda p: p <= B + 1e-9)
                # +1-tick stress (G3 primary): strict-through with barrier B - 1 tick
                h_tr2 = first_hit(S["Lt"], S["Lp"], w0, w1, lambda p: p < B - TICK - 1e-9)
                h_ak2 = first_hit(S["At"], S["Ap"], w0, w1, lambda p: p <= B - TICK + 1e-9)
                tt_x = min([x for x in (h_tr2, h_ak2) if x is not None], default=None)
                # literal-reading sensitivity: print <= B - 1 tick (trade clause only)
                tt_xl = h_tr
                cols[f"{key}_tt_strict"][idx] = (None if tt_s is None else (tt_s - anchor))
                cols[f"{key}_tt_touch"][idx] = (None if h_to is None else (h_to - anchor))
                cols[f"{key}_tt_stress"][idx] = (None if tt_x is None else (tt_x - anchor))
                cols[f"{key}_tt_stress_lit"][idx] = (None if tt_xl is None else (tt_xl - anchor))
                for T in T_LIST:
                    ct_ = anchor + np.int64(T) * NS
                    tq, b_, a_, _ = snapshot(S, ct_, ct_ + STALE_NS)
                    cols[f"{key}_chase_ask_T{T}"][idx] = (a_ if tq is not None else None)
        del S
    P(f"  replayed {int(Er['measurable'].sum())} measurable entries  [{_time.time() - t0:.0f}s]")
    for c, d in cols.items():
        Er[c] = pd.Series(d, dtype="float64")
    return Er


# ================================================================== helpers: aggregation
def wmean(vals, w):
    vals = np.asarray(vals, float)
    w = np.asarray(w, float)
    return float(np.sum(vals * w) / np.sum(w))


def build_deltas(M, key="d250"):
    """per-entry policy deltas for each T and rule, accounting A and B components."""
    out = {}
    A0 = M[f"{key}_ask"].to_numpy(float)
    B0 = M[f"{key}_bid"].to_numpy(float)
    sav = (A0 - B0) * PV                       # $/ctr if filled
    for T in T_LIST:
        chase = M[f"{key}_chase_ask_T{T}"].to_numpy(float)
        for rule, ttc in (("strict", "tt_strict"), ("touch", "tt_touch"),
                          ("stress", "tt_stress"), ("stress_lit", "tt_stress_lit")):
            tt = M[f"{key}_{ttc}"].to_numpy(float)
            filled = np.isfinite(tt) & (tt <= T * 1e9)
            eff = np.where(filled, B0, chase)
            dA = (A0 - eff) * PV
            out[(rule, T)] = dict(filled=filled, dA=dA, sav=sav,
                                  cost_unf=(chase - A0) * PV)
    return out


def boot_ci(num_s, den_s, R):
    """ratio-of-sums bootstrap: num_s/den_s per session, resample matrix R [B x n_s]."""
    ns_ = num_s[R].sum(axis=1)
    ds_ = den_s[R].sum(axis=1)
    stats = ns_ / ds_
    return stats


# ================================================================== main
def main():
    t00 = _time.time()
    hdr("G3_XPASS01_PASSIVE_ENTRY_REPLAY_20260906 - ledger G00082 - run start")
    P(f"  parameters: T family {T_LIST}s, latency primary {DELTA_PRIMARY_MS}ms "
      f"(sens {DELTA_SENS_MS}ms), tick {TICK}, PV {PV}, bootstrap B={BOOT_B} seed={BOOT_SEED}")
    reg = phase0()
    D, meta, trin = phase1()
    Er, sd_b = phase2(D, meta, trin, reg)
    Er = pass1(Er, reg)

    # ---- censoring census (printed pre-G1 is fine: no policy outcome involved)
    cens = Er.groupby(["measurable", "unmeas_reason"]).agg(
        n=("u", "size"), n_ctr=("u", "sum")).reset_index()
    P("")
    P("  measurability census (reasons):")
    for _, r in cens.iterrows():
        P(f"    measurable={str(bool(r['measurable'])):<6} reason={r['unmeas_reason']:<22} "
          f"n={int(r['n']):>4}  ctr={int(r['n_ctr']):>4}")
    crossed_total = int(Er["d250_crossed"].sum())
    P(f"  crossed-BBO instants skipped while forming anchor snapshots (primary \u03b4): "
      f"{crossed_total}")

    b_unpowered, mde_a, mde_b = g1_mde(Er, sd_b)

    Er = pass2(Er, reg)
    gate("G0 seal (tick files)", "every loaded tick file max ts < 2026-08-01 (in-code RAISE)",
         "all loaded files passed the load-time assertion", "PASS")
    M = Er[Er["measurable"]].copy().reset_index(drop=True)
    n, n_ctr = len(M), int(M["u"].sum())
    w = M["u"].to_numpy(float)
    DL = build_deltas(M, "d250")

    # ---- per-entry CSV (written before G4 re-reads it independently)
    per_cols = ["session", "substrate", "et", "action_ns", "u", "pnl_ctr", "allin_ctr",
                "measurable", "unmeas_reason", "d250_bid", "d250_ask", "spread_usd",
                "d250_tt_strict", "d250_tt_touch", "d250_tt_stress", "d250_tt_stress_lit"] + \
               [f"d250_chase_ask_T{T}" for T in T_LIST]
    PE = Er[per_cols].copy()
    for T in T_LIST:
        tt = Er["d250_tt_strict"]
        PE[f"strict_fill_T{T}"] = (tt.notna()) & (tt <= T * 1e9)
    PE.to_csv(os.path.join(OUT, "per_entry.csv"), index=False)

    # ---- bootstrap machinery (one shared resample across the whole family)
    sess_codes, sess_uniq = pd.factorize(M["session"], sort=True)
    n_s = len(sess_uniq)
    rng = np.random.default_rng(BOOT_SEED)
    R = rng.integers(0, n_s, size=(BOOT_B, n_s))
    den_s = np.bincount(sess_codes, weights=w, minlength=n_s)

    def session_sums(vals):
        return np.bincount(sess_codes, weights=np.asarray(vals, float) * w, minlength=n_s)

    # ================================================== G2 primary + G3 stress + diagnostics
    hdr("G2/G3 - accounting A (CHASE, powered primary): per-ctr-entry net delta, "
        "session-level block bootstrap")
    P("  [All figures: BASIS SPREAD_ONLY (entry-side, vs baseline first-valid-ask fill), "
      "EVIDENCE MEASURED (tick replay).]")
    P("  [Bonferroni family = 3 T-variants; per-test two-sided alpha = 0.05/3; "
      "shared session resample across the family.]")
    res_rows = []
    g2_pass, g3_pass, fr_strict, upper95 = {}, {}, {}, {}
    for rule in ("strict", "stress", "touch", "stress_lit"):
        for T in T_LIST:
            d = DL[(rule, T)]
            mean_d = wmean(d["dA"], w)
            fr = wmean(d["filled"].astype(float), w)
            num_s = session_sums(d["dA"])
            stats = boot_ci(num_s, den_s, R)
            lo_b, hi_b = np.quantile(stats, [Q_BONF, 1 - Q_BONF])
            lo95, hi95 = np.quantile(stats, [0.025, 0.975])
            n_fill = int(d["filled"].sum())
            sav_f = wmean(d["sav"][d["filled"]], w[d["filled"]]) if n_fill else float("nan")
            cost_u = (wmean(d["cost_unf"][~d["filled"]], w[~d["filled"]])
                      if n_fill < n else float("nan"))
            res_rows.append(dict(rule=rule, T=T, n=n, n_ctr=n_ctr, fill_rate_ctrw=fr,
                                 mean_delta_usd=mean_d, ci_bonf_lo=lo_b, ci_bonf_hi=hi_b,
                                 ci95_lo=lo95, ci95_hi=hi95, n_filled=n_fill,
                                 mean_savings_filled=sav_f, mean_chase_cost_unfilled=cost_u))
            if rule == "strict":
                g2_pass[T] = bool(lo_b > 0)
                fr_strict[T] = fr
                upper95[T] = hi95
            if rule == "stress":
                g3_pass[T] = bool(lo_b > 0)
    RT = pd.DataFrame(res_rows)
    for rule, label in (("strict", "STRICT-THROUGH (primary)"),
                        ("stress", "+1-TICK STRESS (G3, barrier B-1tk both clauses)"),
                        ("stress_lit", "stress literal-reading sensitivity (print<B only)"),
                        ("touch", "AT-TOUCH (upper-bound diagnostic)")):
        P(f"  {label}:")
        P(f"    {'T':>4} {'fill%':>7} {'mean $/ctr':>11} {'CI-Bonf':>22} {'CI-95':>22} "
          f"{'sav|fill':>9} {'cost|unf':>9}")
        for T in T_LIST:
            r = RT[(RT["rule"] == rule) & (RT["T"] == T)].iloc[0]
            P(f"    {T:>4} {100 * r.fill_rate_ctrw:>6.1f}% {r.mean_delta_usd:>11.2f} "
              f"[{r.ci_bonf_lo:>9.2f},{r.ci_bonf_hi:>9.2f}] "
              f"[{r.ci95_lo:>9.2f},{r.ci95_hi:>9.2f}] {r.mean_savings_filled:>9.2f} "
              f"{r.mean_chase_cost_unfilled:>9.2f}")
    for T in T_LIST:
        rs = RT[(RT["rule"] == "strict") & (RT["T"] == T)].iloc[0]
        gate(f"G2 primary T={T}", "strict-through net > 0 at Bonferroni (lower CI > 0)",
             f"mean {rs['mean_delta_usd']:+.2f}, CI-Bonf lo {rs['ci_bonf_lo']:+.2f}",
             "PASS" if g2_pass[T] else "FAIL")
    for T in T_LIST:
        frag = g2_pass[T] and not g3_pass[T]
        rx = RT[(RT["rule"] == "stress") & (RT["T"] == T)].iloc[0]
        gate(f"G3 +1-tick stress T={T}", "stress net > 0 at Bonferroni; "
             "positive-only-without-stress = FILL-FRAGILE",
             f"stress CI-Bonf lo {rx['ci_bonf_lo']:+.2f}"
             + (" [FILL-FRAGILE]" if frag else ""),
             "PASS" if g3_pass[T] else "FAIL")

    # ---- latency sensitivity (point estimates, strict rule)
    P("")
    P("  latency sensitivity (strict-through mean $/ctr-entry, point estimates):")
    for key, ms in (("d100", 100), ("d250", 250), ("d1000", 1000)):
        ok = M[f"{key}_valid"].to_numpy(bool)
        DLs = build_deltas(M[ok].reset_index(drop=True), key)
        ws = M[ok]["u"].to_numpy(float)
        vals = []
        for T in T_LIST:
            dA = DLs[("strict", T)]["dA"]
            fin = np.isfinite(dA)
            vals.append(f"T={T}: {wmean(dA[fin], ws[fin]):+.2f}"
                        + ("" if fin.all() else f" (n_fin={int(fin.sum())})"))
        P(f"    delta = {ms:>5}ms (n={int(ok.sum())}): " + "  ".join(vals))

    # ================================================== accounting B (per G1 power status)
    hdr("ACCOUNTING B - CANCEL (secondary) - " +
        ("UNPOWERED-BY-DESIGN: measured COMPONENTS ONLY, no net headline, cannot adopt or kill"
         if b_unpowered else "POWERED: full reporting"))
    for T in T_LIST:
        d = DL[("strict", T)]
        f_, u_ = d["filled"], ~d["filled"]
        sav_f = wmean(d["sav"][f_], w[f_]) if f_.any() else float("nan")
        pnl_u = wmean(M["allin_ctr"].to_numpy(float)[u_], w[u_]) if u_.any() else float("nan")
        P(f"    T={T:>3}: fill {100 * wmean(f_.astype(float), w):.1f}% | "
          f"savings|fill ${sav_f:.2f}/ctr [SPREAD_ONLY, MEASURED] | "
          f"unfilled entries' incumbent all-in P&L ${pnl_u:+,.0f}/ctr "
          f"[ALL_IN approx (comm-in + ${RATE_W103:.2f} modelled), DISCOVERY_CONSUMED]")
    if b_unpowered:
        P("    (net = savings - foregone NOT quoted: MDE_B "
          f"${mde_b:,.0f} vs ceiling ${CEIL_ALLH:.0f} -> any observed net is noise at this n.)")

    # ================================================== G4 semantic double-computation
    hdr("G4 - semantic double-computation (the CAP01 rule)")
    PE2 = pd.read_csv(os.path.join(OUT, "per_entry.csv"))  # independent re-read
    PE2m = PE2[PE2["measurable"] == True]  # noqa: E712
    g4_ok_all = True
    for T in T_LIST:
        r = RT[(RT["rule"] == "strict") & (RT["T"] == T)].iloc[0]
        P(f"  T={T}: the headline ${r.mean_delta_usd:+.2f}/ctr-entry is: over N={n} measurable "
          f"bench-regenerated P1/PCT entry events ({n_ctr} contract-entries, contract-weighted) "
          f"in the {len(reg['replay'])}-session strictly-clean replay union, the mean of "
          f"(first-valid-ask-at-anchor minus effective fill) x $20/pt, where the effective fill "
          f"is the join-bid limit B when the strict-through rule fills within (anchor, "
          f"anchor+{T}s], else the first valid ask at/after anchor+{T}s (CHASE). It is an "
          f"EXECUTION cost delta vs the baseline marketable buy - not P&L, not alpha.")
        # independent identity recomputation from the CSV
        w2 = PE2m["u"].to_numpy(float)
        fill2 = PE2m[f"strict_fill_T{T}"].to_numpy(bool)
        A02 = PE2m["d250_ask"].to_numpy(float)
        B02 = PE2m["d250_bid"].to_numpy(float)
        ch2 = PE2m[f"d250_chase_ask_T{T}"].to_numpy(float)
        fr2 = np.sum(w2 * fill2) / np.sum(w2)
        sav2 = (np.sum((w2 * (A02 - B02) * PV)[fill2]) / np.sum(w2[fill2])
                if fill2.any() else 0.0)
        cost2 = (np.sum((w2 * (ch2 - A02) * PV)[~fill2]) / np.sum(w2[~fill2])
                 if (~fill2).any() else 0.0)
        ident = fr2 * sav2 - (1 - fr2) * cost2
        diff = abs(ident - r.mean_delta_usd)
        ok = diff < 1e-9 * max(1.0, abs(r.mean_delta_usd))
        g4_ok_all &= ok
        gate(f"G4 identity T={T}", "fill_rate x E[sav|fill] - (1-fill_rate) x E[cost|unf] == "
             "direct mean (independent recompute from CSV)",
             f"identity {ident:+.6f} vs direct {r.mean_delta_usd:+.6f} (|diff| {diff:.2e})",
             "PASS" if ok else "FAIL")

    # ================================================== G5 censoring & selection control
    hdr("G5 - censoring & selection control")
    um = Er[~Er["measurable"]]
    P(f"  unmeasurable entries: {len(um)} of {len(Er)} "
      f"({100 * len(um) / max(len(Er), 1):.1f}%)")
    cen_rows = []
    for msk, tag in ((Er["measurable"], "MEASURABLE"), (~Er["measurable"], "UNMEASURABLE")):
        sub = Er[msk]
        if len(sub):
            cen_rows.append(dict(subset=tag, n=len(sub), n_ctr=int(sub["u"].sum()),
                                 mean_allin_pnl_ctr=float(sub["allin_ctr"].mean()),
                                 sd_allin_pnl_ctr=float(sub["allin_ctr"].std(ddof=1))
                                 if len(sub) > 1 else float("nan")))
    for r in cen_rows:
        P(f"    {r['subset']:<13} n={r['n']:>4} ctr={r['n_ctr']:>4} "
          f"incumbent all-in P&L mean ${r['mean_allin_pnl_ctr']:+,.0f}/ctr "
          f"SD ${r['sd_allin_pnl_ctr']:,.0f}")
    by_reason = um.groupby("unmeas_reason").agg(n=("u", "size")).reset_index()
    for _, r in by_reason.iterrows():
        P(f"      reason {r['unmeas_reason']}: {int(r['n'])}")
    pd.DataFrame(cen_rows).to_csv(os.path.join(OUT, "censoring_census.csv"), index=False)
    Er.groupby(["measurable", "unmeas_reason", "substrate"]).agg(
        n=("u", "size")).reset_index().to_csv(
        os.path.join(OUT, "censoring_by_substrate.csv"), index=False)
    P("  adverse-selection diagnostic (strict rule; mechanism prior: unfilled entries skew "
      "toward winners):")
    for T in T_LIST:
        d = DL[("strict", T)]
        f_, u_ = d["filled"], ~d["filled"]
        pf = wmean(M["allin_ctr"].to_numpy(float)[f_], w[f_]) if f_.any() else float("nan")
        pu = wmean(M["allin_ctr"].to_numpy(float)[u_], w[u_]) if u_.any() else float("nan")
        P(f"    T={T:>3}: incumbent all-in P&L filled ${pf:+,.0f}/ctr (n={int(f_.sum())}) vs "
          f"unfilled ${pu:+,.0f}/ctr (n={int(u_.sum())})")
    gate("G5 censoring/selection", "census + measurable-vs-unmeasurable P&L + "
         "adverse-selection diagnostic printed, all cells",
         f"{len(um)} unmeasurable censused; diagnostics printed", "PASS")

    # ================================================== G6 evidence tags
    hdr("G6 - evidence-status tags (per session) + run class")
    sess_tab = M.groupby(["session", "substrate"]).agg(n=("u", "size"),
                                                       ctr=("u", "sum")).reset_index()
    burn0 = "20260531"
    sess_tab["evidence_tag"] = np.where(sess_tab["session"] >= burn0,
                                        "BURNED-WINDOW", "DISCOVERY-CONSUMED")
    n_burn = int((sess_tab["evidence_tag"] == "BURNED-WINDOW").sum())
    P(f"  replayed sessions with entries: {len(sess_tab)} "
      f"({n_burn} BURNED-WINDOW, {len(sess_tab) - n_burn} DISCOVERY-CONSUMED pre-burn)")
    P("  run class: Class-X EXECUTION - DISCOVERY-grade - prices an execution policy - "
      "NEVER alpha evidence.")
    P("  dollar bases used: savings/deltas = SPREAD_ONLY + MEASURED (tick replay); "
      "incumbent P&L = ALL_IN approx (commission-in + $14.44/ctrRT MODELLED spread), "
      "DISCOVERY_CONSUMED.")
    gate("G6 evidence tags", "per-session tag table + BASIS/EVIDENCE on every $ figure + "
         "run class printed", f"{len(sess_tab)} sessions tagged; bases stated", "PASS")

    # ---- fill curves
    grid = np.arange(1, 121)
    fc_rows = []
    for rule in ("strict", "touch", "stress"):
        tt = M[f"d250_tt_{rule}"].to_numpy(float)
        for g in grid:
            fr = np.sum(w * (np.isfinite(tt) & (tt <= g * 1e9))) / np.sum(w)
            fc_rows.append(dict(rule=rule, T_sec=int(g), fill_rate_ctrw=fr))
    pd.DataFrame(fc_rows).to_csv(os.path.join(OUT, "fill_curves.csv"), index=False)
    tts = M["d250_tt_strict"].to_numpy(float) / 1e9
    tts = tts[np.isfinite(tts)]
    if len(tts):
        qs = np.quantile(tts, [0.1, 0.25, 0.5, 0.75, 0.9])
        P(f"  time-to-fill (strict, within 120s, n={len(tts)}): "
          f"p10 {qs[0]:.1f}s p25 {qs[1]:.1f}s p50 {qs[2]:.1f}s p75 {qs[3]:.1f}s p90 {qs[4]:.1f}s")

    # ---- session evidence / replay tables
    RT.to_csv(os.path.join(OUT, "replay_table.csv"), index=False)
    sess_tab.to_csv(os.path.join(OUT, "session_evidence_tags.csv"), index=False)

    # ================================================== decision rule (mechanical)
    hdr("DECISION RULE (DESIGN_FROZEN 5, applied mechanically)")
    candidates = []
    for T in T_LIST:
        cand = g2_pass[T] and g3_pass[T] and (fr_strict[T] >= FILLRATE_FLOOR)
        P(f"  T={T:>3}: G2 {'PASS' if g2_pass[T] else 'FAIL'} & G3 "
          f"{'PASS' if g3_pass[T] else 'FAIL'} & fill_rate {100 * fr_strict[T]:.1f}% >= 20% "
          f"{'PASS' if fr_strict[T] >= FILLRATE_FLOOR else 'FAIL'} -> "
          f"{'CANDIDATE' if cand else 'not a candidate'}")
        if cand:
            candidates.append(T)
    kill2 = fr_strict[120] < FILLRATE_FLOOR
    P(f"  KILL-2 (mechanism): strict fill_rate(T=120) = {100 * fr_strict[120]:.1f}% < 20% ? "
      f"{kill2}")
    kill1 = all(upper95[T] < KILL1_FLOOR for T in T_LIST)
    P(f"  KILL-1 (powered kill): upper 95% CI per T = "
      + ", ".join(f"T={T}: {upper95[T]:+.2f}" for T in T_LIST)
      + f" - ALL < ${KILL1_FLOOR:.2f} ? {kill1}")
    gate("KILL-2 mechanism", "strict fill_rate(T=120) < 20% => CLOSED-BY-MECHANISM",
         f"fill_rate(120) {100 * fr_strict[120]:.1f}%", "FIRED" if kill2 else "not fired")
    gate("KILL-1 powered kill", f"all T: strict upper 95% CI < ${KILL1_FLOOR:.2f} => "
         "PASSIVE-ENTRY-AT-L1 CLOSED",
         "all upper CIs " + ", ".join(f"{upper95[T]:+.2f}" for T in T_LIST),
         "FIRED" if kill1 else "not fired")
    if candidates:
        decision = (f"CANDIDATE(T={candidates}) - queue for owner-gated NT8 implementation "
                    f"study + forward shadow; NO live change, NO sizing change, NO promotion")
        ledger = "PASS"
    elif kill2 and kill1:
        decision = ("CLOSED-BY-MECHANISM (KILL-2) and PASSIVE-ENTRY-AT-L1 CLOSED (KILL-1): "
                    "the join-bid policy cannot engage the book at P1's entry instants AND its "
                    "upper CI is below the materiality floor. Do not revisit without "
                    "depth/queue data.")
        ledger = "FAIL"
    elif kill2:
        decision = "CLOSED-BY-MECHANISM (KILL-2): fill_rate(T=120) < 20%."
        ledger = "FAIL"
    elif kill1:
        decision = ("PASSIVE-ENTRY-AT-L1 CLOSED (KILL-1): all upper 95% CIs < $2.50/ctr-entry. "
                    "Do not revisit without depth/queue data.")
        ledger = "FAIL"
    else:
        decision = "NO CANDIDATE, NO KILL - indeterminate at this n (recorded NULL)."
        ledger = "NULL"
    P("")
    P(f"  DECISION: {decision}")
    P(f"  LEDGER G00082 (family EXEC_PASSIVE_ENTRY, 3 T-variants = one family): {ledger}")

    # ================================================== final gate table
    hdr("GATE / SPEC / OBSERVED / PASS-FAIL (program-printed)")
    gt_lines = ["G3_XPASS01_PASSIVE_ENTRY_REPLAY_20260906 - ledger G00082",
                "Class-X EXECUTION replay - DISCOVERY-grade - NEVER alpha evidence",
                f"run finished {pd.Timestamp.now()}  wall {(_time.time() - t00) / 60:.1f} min",
                "",
                f"{'GATE':<28} | {'SPEC':<60} | {'OBSERVED':<46} | VERDICT",
                "-" * 155]
    for g_ in GATE_ROWS:
        gt_lines.append(f"{g_[0]:<28} | {g_[1]:<60} | {g_[2]:<46} | {g_[3]}")
        P(f"  {g_[0]:<28} | {g_[1]:<60} | {g_[2]:<46} | {g_[3]}")
    gt_lines += ["", f"DECISION: {decision}", f"LEDGER: {ledger}"]
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(gt_lines) + "\n")
    with open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG_LINES) + "\n")
    P("")
    P(f"  outputs written to {OUT}")
    P(f"  FINAL DECISION LINE: {decision}")
    P(f"  [total {(_time.time() - t00) / 60:.1f} min]")


if __name__ == "__main__":
    main()
