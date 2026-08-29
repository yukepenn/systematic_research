"""G2_F4_NDX_DELEV02_20260829 — MC-40 retest on a percent-clean basis (trial G00028).

Implements the FROZEN spec.yaml + out/spec_resolutions.txt (R1-R18, A1) exactly once.
Events on the CASH NASDAQ-100 index (FRED NASDAQ100, certified); futures P&L in POINTS
on the owned substrates (deep parquet pre-2022 / modern 2022+, each within its own
window). No parameter is searched. All gate rows are printed BY THIS PROGRAM.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time as _time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from research_sdk.seal_guard import assert_presealed, truncate_presealed  # noqa: E402

RUN = REPO / "runs" / "G2_F4_NDX_DELEV02_20260829"
OUT, RAW, CERT = RUN / "out", RUN / "raw", RUN / "certified"

DEEP_NQ = REPO / "research" / "scalping_lab" / "substrate" / "minute" / "NQ" / "nq1m_2005_202605.parquet"
MODERN_NQ = REPO / "runs" / "SM1M_SUBSTRATE" / "out" / "nq_1m_2022_2026.parquet"
SHA_DEEP = "dfd017eff0b031c2be89639fc4ad347d45053867edcdc2600002252b10b627cf"    # run_provenance.txt
SHA_MODERN = "87aa53f007aa47b9ee10d0080317a3cde8d22b55aa368267fa9a4aed7435295d"  # run_provenance.txt

WIN_START = pd.Timestamp("2006-01-01")
WIN_END = pd.Timestamp("2026-05-31")            # frozen window end
OVL_START = pd.Timestamp("2009-01-01")          # Stage-A overlap gate window (frozen)
SPLIT = pd.Timestamp("2022-01-01")              # deep < 2022-01-01 <= modern (spec substrate split)
BAND_LO, BAND_HI = -0.05, -0.025                # [-5.0%, -2.5%) frozen, on INDEX %
MA_N = 200                                      # frozen, on INDEX closes
HOLD = 3                                        # exit at futures RTH close of fu+3, frozen
VETO = -0.015                                   # gap-down veto vs INDEX level (R9), frozen
PV = 20.0                                       # $/pt NQ
COST_RT = 33.0                                  # $/RT stressed tape, frozen
RV_N = 21                                       # trailing-21d INDEX RV, frozen
N_SHIFTS = 500                                  # >= 300 specced; 500 matches G00027 structure
CORR_GATE = 0.97                                # Stage-A overlap gate, frozen
WARMUP_MIN = 221                                # R4 hard sufficiency rule
SESSION_CLOSE = pd.Timedelta(hours=17)
TOD_0931 = pd.Timedelta(hours=9, minutes=31)
TOD_1600 = pd.Timedelta(hours=16)

_LINES: list[str] = []


def emit(s: str = ""):
    print(s)
    _LINES.append(s)


def flush_to(path: Path):
    path.write_text("\n".join(_LINES) + "\n", encoding="utf-8")
    _LINES.clear()


def era_of(ts: pd.Timestamp) -> str:
    y = ts.year
    if y <= 2007: return "2006-07"
    if y <= 2009: return "2008-09"
    if y <= 2013: return "2010-13"
    if y <= 2017: return "2014-17"
    if y <= 2019: return "2018-19"
    if y <= 2021: return "2020-21"
    if y == 2022: return "2022"
    return "2023-26/05"


ERA_ORDER = ["2006-07", "2008-09", "2010-13", "2014-17", "2018-19", "2020-21", "2022", "2023-26/05"]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_store(path: Path, kind: str) -> tuple[dict, dict, int]:
    """Stream a minute store; return (open_map, close_map, n_seal_calls).

    open_map[label]  = OPEN of the bar stamped 09:31:00  (the 09:30:00 price)
    close_map[label] = CLOSE of the bar stamped 16:00:00
    Modern store: truncate_presealed FIRST, then label-cut to <= WIN_END (R6).
    Deep store: assert_presealed every row-group.
    """
    f = pq.ParquetFile(path)
    open_map: dict[pd.Timestamp, float] = {}
    close_map: dict[pd.Timestamp, float] = {}
    n_seal, prev_last = 0, None
    for g in range(f.metadata.num_row_groups):
        t = f.read_row_group(g, columns=["time", "open", "close"]).to_pandas()
        if t["time"].dtype == object:
            t["time"] = pd.to_datetime(t["time"], format="%Y-%m-%d %H:%M:%S")
        if kind == "modern":
            t, _n_dropped = truncate_presealed(t, "time", f"DELEV02 modern rg{g}")
        assert_presealed(t, "time", f"DELEV02 {kind} rg{g}")
        n_seal += 1
        if not t["time"].is_monotonic_increasing:
            raise RuntimeError(f"{kind} rg{g}: time not monotonic")
        if prev_last is not None and len(t) and t["time"].iloc[0] < prev_last:
            raise RuntimeError(f"{kind} rg{g}: row-group ordering broken")
        if len(t):
            prev_last = t["time"].iloc[-1]
        day = t["time"].dt.normalize()
        tod = t["time"] - day
        label = day.where(tod <= SESSION_CLOSE, day + pd.Timedelta(days=1))
        if kind == "modern":
            keep = label <= WIN_END
            t, day, tod, label = t[keep], day[keep], tod[keep], label[keep]
        for mask, store, px in ((tod == TOD_0931, open_map, "open"), (tod == TOD_1600, close_map, "close")):
            sub_lab = label[mask]
            sub_px = t.loc[mask, px]
            for lab, v in zip(sub_lab, sub_px):
                lab = pd.Timestamp(lab)
                if lab in store and store[lab] != float(v):
                    raise RuntimeError(f"{kind}: duplicate {px} bar with differing value at session {lab.date()}")
                store[lab] = float(v)
        del t
    return open_map, close_map, n_seal


def main():
    t0 = _time.time()

    # =========================== STAGE A — DATA CONTRACT ===========================
    emit("G2_F4_NDX_DELEV02_20260829 — STAGE A DATA CONTRACT (printed by program)  trial G00028")
    emit("=" * 100)

    # ---- A.1 fetch record (from the quarantined manifest) ----
    man = json.loads((RAW / "fetch_manifest.json").read_text(encoding="utf-8"))
    raw_path = RAW / "fredgraph_NASDAQ100.csv"
    raw_sha = sha256_file(raw_path)
    if raw_sha != man["sha256"]:
        raise RuntimeError("raw file sha256 does not match fetch manifest — DEFECT")
    emit("FETCH RECORD (raw quarantined; never inspected beyond this parse):")
    emit(f"  source : {man['source']}")
    emit(f"  url    : {man['url']}")
    emit(f"  status : {man['http_status']}   bytes: {man['bytes']:,} (cap {man['cap_bytes']:,})   attempts: {man['attempts']}")
    emit(f"  sha256 : {man['sha256']}")
    emit(f"  fetched: {man['fetched_utc']} UTC   snapshot: {man.get('snapshot_utc', 'n/a')}")
    emit("  live-FRED unreachability + fallback ladder: recorded in out/spec_resolutions.txt A1")

    # ---- A.2 parse + seal + certify ----
    df = pd.read_csv(raw_path)
    cols = list(df.columns)
    date_col = "observation_date" if "observation_date" in cols else ("DATE" if "DATE" in cols else None)
    if date_col is None or "NASDAQ100" not in cols:
        raise RuntimeError(f"unexpected CSV header {cols} — DEFECT")
    df[date_col] = pd.to_datetime(df[date_col], format="%Y-%m-%d")
    n_parsed = len(df)
    # SEAL FIRST (A1/R2): mechanical truncation before any other operation; values never shown
    df, n_sealed_dropped = truncate_presealed(df, date_col, "DELEV02 index parse")
    assert_presealed(df, date_col, "DELEV02 index certified")
    n_missing = int((df["NASDAQ100"].astype(str) == ".").sum())
    df["close"] = pd.to_numeric(df["NASDAQ100"], errors="coerce")
    n_missing_all = int(df["close"].isna().sum())
    cert = df.loc[df["close"].notna(), [date_col, "close"]].rename(columns={date_col: "date"}).reset_index(drop=True)
    if not cert["date"].is_monotonic_increasing or cert["date"].duplicated().any():
        raise RuntimeError("certified index dates not strictly increasing / not unique — DEFECT")
    if not (np.isfinite(cert["close"]).all() and (cert["close"] > 0).all()):
        raise RuntimeError("certified index closes not all finite/positive — DEFECT")
    cert.to_csv(CERT / "nasdaq100_daily.csv", index=False)
    emit("")
    emit("CERTIFICATION (certified/nasdaq100_daily.csv):")
    emit("  timestamp semantics: official NDX value at the 16:00 ET market close of the stamped calendar day")
    emit("  revision policy    : closed index history is fixed (not revised)")
    emit(f"  parsed rows={n_parsed:,}  sealed rows dropped by seal_guard.truncate_presealed={n_sealed_dropped}"
         f"  ('.'/non-numeric missing={n_missing_all}, of which '.'={n_missing})")
    emit(f"  certified rows={len(cert):,}  span {cert['date'].iloc[0].date()} -> {cert['date'].iloc[-1].date()}"
         f"  (all < 2026-08-01: {bool(cert['date'].max() < pd.Timestamp('2026-08-01'))})")

    # ---- A.3 coverage / missingness map ----
    bdays = pd.bdate_range(cert["date"].iloc[0], cert["date"].iloc[-1])
    n_bday_gaps = int(len(bdays.difference(pd.DatetimeIndex(cert["date"]))))
    emit("")
    emit("COVERAGE / MISSINGNESS MAP (counts only):")
    emit(f"  Mon-Fri weekdays in span with no certified value (holidays + vendor gaps): {n_bday_gaps:,}")
    yr = cert["date"].dt.year.value_counts().sort_index()
    items = [f"{y}:{c}" for y, c in yr.items()]
    for i in range(0, len(items), 8):
        emit("  per-year obs  " + "  ".join(items[i:i + 8]))
    n_warm = int((cert["date"] < WIN_START).sum())
    emit(f"  certified obs strictly before 2006-01-01 (warm-up): {n_warm:,}  (R4 hard requirement >= {WARMUP_MIN})")
    if n_warm < WARMUP_MIN:
        raise RuntimeError("FRED NASDAQ100 history insufficient per R4 — fallback ladder would engage; DEFECT here")
    emit(f"  'what FRED provides': full series from {cert['date'].iloc[0].date()} (spec expectation '1986 ->': "
         f"{bool(cert['date'].iloc[0] <= pd.Timestamp('1986-06-30'))})")

    # ---- A.4 futures substrates: provenance + load ----
    emit("")
    sha_d, sha_m = sha256_file(DEEP_NQ), sha256_file(MODERN_NQ)
    emit(f"substrate deep  : {DEEP_NQ.relative_to(REPO)}")
    emit(f"  sha256={sha_d}  size={DEEP_NQ.stat().st_size:,}B  match_recorded_provenance={sha_d == SHA_DEEP}")
    emit(f"substrate modern: {MODERN_NQ.relative_to(REPO)}")
    emit(f"  sha256={sha_m}  size={MODERN_NQ.stat().st_size:,}B  match_recorded_provenance={sha_m == SHA_MODERN}")
    if sha_d != SHA_DEEP or sha_m != SHA_MODERN:
        raise RuntimeError("substrate hash mismatch vs GENESIS_REPRO_INCUMBENT run_provenance — DEFECT")
    emit("data_esnq: NOT ACCESSED by this run -> ALLOWLIST_DEV_44 enforcement N/A (no tick reads). Blind pools untouched.")

    do_map, dc_map, seal_d = load_store(DEEP_NQ, "deep")
    mo_map, mc_map, seal_m = load_store(MODERN_NQ, "modern")
    emit(f"seal_guard calls: deep assert_presealed x{seal_d} row-groups; modern truncate_presealed+assert x{seal_m} row-groups")

    # ---- A.5 splice: U universe, each substrate within its own window (R6) ----
    deep_labels = sorted(l for l in dc_map if l < SPLIT)
    modern_labels = sorted(l for l in mc_map if SPLIT <= l <= WIN_END)
    common = sorted(set(dc_map) & set(mc_map))
    common = [l for l in common if SPLIT <= l <= WIN_END]
    diffs = np.array([abs(dc_map[l] - mc_map[l]) for l in common])
    emit(f"SPLICE CONTINUITY CHECK (no P&L use of deep >= 2022): common U-labels 2022-01..2026-05 n={len(common)}"
         f"  max|close diff|={diffs.max() if len(diffs) else float('nan'):.4f} pts")
    if len(common) == 0 or diffs.max() != 0.0:
        raise RuntimeError("splice continuity violated (deep vs modern closes differ) — DEFECT")

    u_labels = pd.DatetimeIndex(deep_labels + modern_labels)
    if not u_labels.is_monotonic_increasing or u_labels.duplicated().any():
        raise RuntimeError("spliced U not strictly increasing/unique — DEFECT")
    fclose = np.array([dc_map[l] if l < SPLIT else mc_map[l] for l in u_labels])
    fopen = np.array([(do_map.get(l, np.nan) if l < SPLIT else mo_map.get(l, np.nan)) for l in u_labels])
    emit(f"U (futures sessions with a 16:00 RTH close, spliced deep<2022|modern>=2022): {len(u_labels):,}"
         f"  span {u_labels[0].date()} -> {u_labels[-1].date()}  (max label <= {WIN_END.date()}: {u_labels[-1] <= WIN_END})")
    emit(f"U-sessions missing a 09:31 bar: {int(np.isnan(fopen).sum())}")

    # ---- A.6 session alignment + holiday mismatches (R7) ----
    idx_dates = pd.DatetimeIndex(cert["date"])
    idx_use = idx_dates[idx_dates <= WIN_END]
    uset, iset = set(u_labels), set(idx_use)
    win_idx = [d for d in idx_use if WIN_START <= d <= WIN_END]
    win_u = [l for l in u_labels if WIN_START <= l <= WIN_END]
    idx_no_fut = sorted(d for d in win_idx if d not in uset)
    fut_no_idx = sorted(l for l in win_u if l not in iset)
    emit("")
    emit("SESSION ALIGNMENT (index calendar day D -> futures session labeled D; RTH falls on D):")
    emit(f"  in-window index days: {len(win_idx):,}   in-window futures U-sessions: {len(win_u):,}")
    emit(f"  index days with NO futures U-session (events there = UNTRADEABLE_ALIGN): {len(idx_no_fut)}")
    emit(f"  futures U-sessions with NO index day (count in hold horizon; host no events): {len(fut_no_idx)}")

    # ---- A.7 overlap-correlation gate (R5) ----
    ovl = pd.DatetimeIndex(sorted(iset & uset))
    ovl = ovl[ovl <= WIN_END]
    idx_close_map = dict(zip(cert["date"], cert["close"]))
    fut_close_map = dict(zip(u_labels, fclose))
    prev_d, cur_d = ovl[:-1], ovl[1:]
    pair_ok = (prev_d >= OVL_START) & (cur_d <= WIN_END)
    ic_prev = np.array([idx_close_map[d] for d in prev_d[pair_ok]])
    ic_cur = np.array([idx_close_map[d] for d in cur_d[pair_ok]])
    fc_prev = np.array([fut_close_map[d] for d in prev_d[pair_ok]])
    fc_cur = np.array([fut_close_map[d] for d in cur_d[pair_ok]])
    y_idx = ic_cur / ic_prev - 1.0
    x_fut = (fc_cur - fc_prev) / ic_prev
    corr = float(np.corrcoef(y_idx, x_fut)[0, 1])
    a1_pass = corr > CORR_GATE
    emit("")
    emit("OVERLAP-CORRELATION GATE (the two series must describe the same market):")
    emit(f"  consecutive common-calendar pairs in [{OVL_START.date()}, {WIN_END.date()}]: n={pair_ok.sum():,}")
    emit(f"  corr(index daily %return, futures daily point-return / prior index close) = {corr:.6f}")
    emit("")
    emit("STAGE-A GATE (printed by program)")
    emit("GATE  SPEC                                                      OBSERVED                 PASS-FAIL")
    emit("-" * 100)
    emit(f"A1    corr(idx %ret, fut pt-ret / idx level) > {CORR_GATE} on 2009-2026/05  corr={corr:.6f} (n={pair_ok.sum():,})  "
         + ("PASS" if a1_pass else "FAIL -> DEFECT"))
    emit("")
    emit(f"STAGE-A VERDICT: {'CONTRACT SATISFIED — Stage B proceeds' if a1_pass else 'DEFECT — the two series do not describe the same market; Stage B NOT computed'}")
    flush_to(OUT / "contract.txt")

    if not a1_pass:
        _LINES.clear()
        emit("G2_F4_NDX_DELEV02_20260829 — gate output (printed by program)  trial G00028")
        emit("=" * 100)
        emit(f"STAGE-A DEFECT: overlap correlation {corr:.6f} <= {CORR_GATE}. Stage B not computed (R17).")
        emit("GATE     SPEC                                            OBSERVED             PASS-FAIL")
        emit(f"A1       overlap corr > {CORR_GATE}                            corr={corr:.6f}       FAIL")
        emit("VERDICT  Stage-A contract must hold                      DEFECT               FAIL")
        flush_to(OUT / "gate_table.txt")
        (OUT / "ledger_result_pending.json").write_text(json.dumps({
            "trial_id": "G00028", "result": "DEFECT",
            "metrics": {"overlap_corr": round(corr, 6), "overlap_pairs": int(pair_ok.sum())},
            "note": "Stage-A overlap-correlation gate failed; index and futures substrate do not describe the same market.",
        }, indent=2), encoding="utf-8")
        return

    # =========================== STAGE B — FROZEN RETEST ===========================
    _LINES.clear()
    emit("G2_F4_NDX_DELEV02_20260829 — gate output (printed by program)  trial G00028")
    emit("=" * 100)
    emit("Stage A: CONTRACT SATISFIED (out/contract.txt). Events on CASH NDX %, P&L in FUTURES POINTS.")
    emit(f"  certified index: {len(cert):,} obs {cert['date'].iloc[0].date()} -> {cert['date'].iloc[-1].date()};"
         f"  futures U: {len(u_labels):,} sessions {u_labels[0].date()} -> {u_labels[-1].date()} (spliced, <= {WIN_END.date()})")
    emit(f"  overlap gate A1: corr={corr:.6f} > {CORR_GATE} (n={pair_ok.sum():,}) PASS")

    # ---- index analysis series (<= WIN_END only; R15) ----
    s_idx = pd.Series(cert["close"].to_numpy(), index=pd.DatetimeIndex(cert["date"]))
    s_idx = s_idx[s_idx.index <= WIN_END]
    r_all = (s_idx / s_idx.shift(1) - 1.0).to_numpy()
    ma_all = s_idx.rolling(MA_N, min_periods=MA_N).mean().to_numpy()
    rv_all = pd.Series(r_all, index=s_idx.index).rolling(RV_N, min_periods=RV_N).std(ddof=1).to_numpy()
    all_dates = s_idx.index

    inwin = (all_dates >= WIN_START) & (all_dates <= WIN_END)
    off = int(np.argmax(inwin.to_numpy() if hasattr(inwin, "to_numpy") else inwin))
    N = int(inwin.sum())
    assert np.asarray(inwin)[off:off + N].all(), "index window not contiguous"
    emit(f"in-window index days [{WIN_START.date()}..{WIN_END.date()}]: N={N:,} (earlier history = warm-up only)")

    j = np.arange(N) + off
    lab_w = all_dates[j]                       # index event dates
    r_w, ma_w, cl_w, rv_w = r_all[j], ma_all[j], s_idx.to_numpy()[j], rv_all[j]

    # ---- per-index-day policy arrays (R7/R9): map to futures, completability, veto, net ----
    upos = {l: i for i, l in enumerate(u_labels)}
    nU = len(u_labels)
    fu = np.array([upos.get(d, -1) for d in lab_w])            # mapped futures U-position, -1 = no session
    aligned = fu >= 0
    entry_open = np.full(N, np.nan)
    exitc = np.full(N, np.nan)
    ev_fclose = np.full(N, np.nan)
    c1 = np.full(N, np.nan); c2 = np.full(N, np.nan); c3 = np.full(N, np.nan)
    ok_h = aligned & (fu + HOLD < nU)                          # fu+3 exists (U already cut at WIN_END)
    ih = np.where(ok_h)[0]
    entry_open[ih] = fopen[fu[ih] + 1]
    ev_fclose[ih] = fclose[fu[ih]]
    c1[ih] = entry_open[ih] - fclose[fu[ih] + 1]
    c2[ih] = entry_open[ih] - fclose[fu[ih] + 2]
    c3[ih] = entry_open[ih] - fclose[fu[ih] + 3]
    exitc[ih] = fclose[fu[ih] + 3]
    completable = ok_h & np.isfinite(entry_open)
    with np.errstate(invalid="ignore"):
        gap = (entry_open - ev_fclose) / cl_w                  # denominator = INDEX level (frozen)
        vetoed_arr = gap < VETO
    traded_ok = completable & ~vetoed_arr
    net = np.where(completable, c3 * PV - COST_RT, np.nan)

    # ---- events (R8) ----
    with np.errstate(invalid="ignore"):
        band = (r_w >= BAND_LO) & (r_w < BAND_HI)
        bear = cl_w < ma_w
    detected = np.where(band & bear)[0]
    st = np.where(~aligned[detected], "UNTRADEABLE_ALIGN",
                  np.where(~completable[detected], "UNTRADEABLE",
                           np.where(vetoed_arr[detected], "VETOED", "TRADED")))
    traded = detected[st == "TRADED"]
    eras_det = np.array([era_of(lab_w[p]) for p in detected])

    emit(""); emit("PER-ERA EVENT COUNTS (printed BEFORE any return table)")
    emit(f"{'era':<10} {'detected':>8} {'untr_align':>10} {'untradeable':>11} {'vetoed':>7} {'traded':>7}")
    for e in ERA_ORDER:
        m = eras_det == e
        emit(f"{e:<10} {int(m.sum()):>8} {int((st[m]=='UNTRADEABLE_ALIGN').sum()):>10} "
             f"{int((st[m]=='UNTRADEABLE').sum()):>11} {int((st[m]=='VETOED').sum()):>7} {int((st[m]=='TRADED').sum()):>7}")
    emit(f"{'TOTAL':<10} {len(detected):>8} {int((st=='UNTRADEABLE_ALIGN').sum()):>10} "
         f"{int((st=='UNTRADEABLE').sum()):>11} {int((st=='VETOED').sum()):>7} {len(traded):>7}")
    emit("STATED: effective N concentrates in the 2008/2020/2022 stress clusters — now VISIBLE on the cash index.")

    if len(traded) == 0:
        raise RuntimeError("zero traded events — cannot evaluate gates (would be DEFECT)")

    # ---- D1 clusters (R10) + MDE printed BEFORE return table ----
    tp = np.sort(traded)
    months = np.array([lab_w[p].strftime("%Y-%m") for p in tp])
    fut_pos = fu[tp]
    cluster_id = np.zeros(len(tp), dtype=int)
    for i in range(1, len(tp)):
        linked = (fut_pos[i] - fut_pos[i - 1] <= 2) or (months[i] == months[i - 1])
        cluster_id[i] = cluster_id[i - 1] if linked else cluster_id[i - 1] + 1
    y = net[tp]
    import statsmodels.api as sm
    res = sm.OLS(y, np.ones((len(y), 1))).fit(cov_type="cluster", cov_kwds={"groups": cluster_id})
    mean_net = float(res.params[0]); se = float(res.bse[0]); tstat = float(res.tvalues[0])
    n_clusters = int(pd.Series(cluster_id).nunique())
    mde = 2.0 * se
    emit(""); emit(f"MDE (printed BEFORE the return table): 2.0 x clustered SE = ${mde:,.2f} per event "
                   f"(SE=${se:,.2f}, n={len(tp)}, clusters={n_clusters})")

    # ---- return tables ----
    emit(""); emit("D1 RETURN TABLE — traded events, SHORT 1 NQ ct, net of $33/RT, P&L in futures POINTS x $20")
    emit(f"  mean net/event = ${mean_net:,.2f}   median = ${np.median(y):,.2f}   sd = ${np.std(y, ddof=1):,.2f}")
    emit(f"  sum net = ${y.sum():,.2f}   win rate (net>0) = {float((y > 0).mean()):.1%}   clustered t = {tstat:.3f}")
    emit("  per-era (traded): era, n, mean net, sum net")
    eras_tr = np.array([era_of(lab_w[p]) for p in tp])
    for e in ERA_ORDER:
        m = eras_tr == e
        if m.sum():
            emit(f"    {e:<10} n={int(m.sum()):>3}  mean=${y[m].mean():>10,.2f}  sum=${y[m].sum():>12,.2f}")

    # ---- D2 vol-matched control (R11) — shared rng draw FIRST ----
    rng = np.random.default_rng(0)
    rv_valid = rv_w[np.isfinite(rv_w)]
    edges = np.quantile(rv_valid, np.arange(1, 10) / 10.0)
    decile = np.where(np.isfinite(rv_w), np.searchsorted(edges, rv_w, side="right"), -1)
    assert (decile[tp] >= 0).all(), "traded event lacking RV — DEFECT"
    det_mask = np.zeros(N, dtype=bool); det_mask[detected] = True
    with np.errstate(invalid="ignore"):
        pool_mask = (r_w < 0) & (decile >= 0) & ~det_mask & traded_ok
    ctrl_idx, shortfall = [], 0
    for d in range(10):
        need = int((decile[tp] == d).sum())
        if need == 0:
            continue
        avail = np.where(pool_mask & (decile == d))[0]
        if len(avail) < need:
            shortfall += need - len(avail)
            take = avail
        else:
            take = rng.choice(avail, size=need, replace=False)
        ctrl_idx.append(np.sort(take))
    ctrl = np.concatenate(ctrl_idx) if ctrl_idx else np.array([], dtype=int)
    yc = net[ctrl]
    mean_ctrl = float(yc.mean())
    emit(""); emit("D2 VOL-MATCHED CONTROL — index down-days (r<0), no bear filter/band, matched on trailing-21d INDEX RV decile,")
    emit("  same futures policy incl. gap-down veto, count-matched per decile, ONE shared draw (seed 0, consumed before D3)")
    emit(f"  control n = {len(ctrl)} (events {len(tp)}, decile shortfall = {shortfall})")
    emit(f"  control mean net/event = ${mean_ctrl:,.2f}   median = ${np.median(yc):,.2f}   sd = ${np.std(yc, ddof=1):,.2f}")
    emit(f"  event-minus-control mean = ${mean_net - mean_ctrl:,.2f}")

    # ---- D3 circular-shift null (R12) — shared rng, drawn AFTER D2 ----
    shifts = rng.choice(np.arange(1, N), size=N_SHIFTS, replace=False)
    means, n_empty, n_traded_acc = [], 0, []
    for k in shifts:
        q = (detected + int(k)) % N
        m = traded_ok[q]
        if not m.any():
            n_empty += 1
            continue
        means.append(float(net[q[m]].mean()))
        n_traded_acc.append(int(m.sum()))
    means = np.array(means)
    p95 = float(np.percentile(means, 95))
    emit(""); emit(f"D3 CIRCULAR-SHIFT NULL — {N_SHIFTS} distinct whole-index-day shifts of the detected-event indicator")
    emit(f"  valid shifts = {len(means)} (empty: {n_empty})   pseudo-events/shift mean = {np.mean(n_traded_acc):.1f}"
         f" min = {min(n_traded_acc)}")
    emit(f"  null mean of means = ${means.mean():,.2f}   p50 = ${np.percentile(means, 50):,.2f}   p95 = ${p95:,.2f}")
    emit(f"  observed mean net = ${mean_net:,.2f}   exceeds p95: {mean_net > p95}")

    # ---- diagnostic (non-gate): MFE-path shape (R13) ----
    emit(""); emit("DIAGNOSTIC (non-gate) — MFE-path shape, traded events, gross short pts at futures U-closes fu+1/fu+2/fu+3")
    for nm, arr in (("cum@c1", c1[tp]), ("cum@c2", c2[tp]), ("cum@c3", c3[tp])):
        emit(f"  {nm}: mean={arr.mean():+8.2f} pts  median={np.median(arr):+8.2f} pts")
    inc1, inc2, inc3 = c1[tp], c2[tp] - c1[tp], c3[tp] - c2[tp]
    emit(f"  increments: entry->c1 mean={inc1.mean():+.2f}  c1->c2 mean={inc2.mean():+.2f}  c2->c3 mean={inc3.mean():+.2f} pts")
    argmx = np.argmax(np.vstack([c1[tp], c2[tp], c3[tp]]), axis=0)
    emit(f"  max close-mark at: c1 {int((argmx==0).sum())}, c2 {int((argmx==1).sum())}, c3 {int((argmx==2).sum())} "
         f"(positive-early/negative-late = spiral-then-reversal signature)")

    # ---- gate table (printed by program) ----
    d1 = (mean_net > 0.0) and (tstat >= 2.0)
    d2 = mean_net > mean_ctrl
    d3 = mean_net > p95
    survived = d1 and d2 and d3
    rows = [
        ("A1", f"Stage-A overlap corr > {CORR_GATE} (contract)",
         f"corr={corr:.6f} (n={pair_ok.sum():,})", "PASS" if a1_pass else "FAIL"),
        ("D1", "net mean/event > 0 AND event-clustered t >= 2.0",
         f"mean=${mean_net:,.2f}, t={tstat:.3f} (n={len(tp)}, clusters={n_clusters})", "PASS" if d1 else "FAIL"),
        ("D2", "event mean net > vol-matched control mean net",
         f"${mean_net:,.2f} vs ${mean_ctrl:,.2f}", "PASS" if d2 else "FAIL"),
        ("D3", f"mean net > p95 of {N_SHIFTS} circular-shift means",
         f"${mean_net:,.2f} vs p95=${p95:,.2f}", "PASS" if d3 else "FAIL"),
        ("VERDICT", "D1+D2+D3 PASS -> SURVIVED-DISCOVERY; any fail -> NULL",
         "SURVIVED-DISCOVERY" if survived else "NULL at formulation (MC-40 finally TESTED)", "PASS" if survived else "FAIL"),
    ]
    emit(""); emit("GATE TABLE (printed by program)")
    w0 = max(len(x[0]) for x in rows); w1 = max(len(x[1]) for x in rows); w2 = max(len(x[2]) for x in rows)
    emit(f"{'GATE':<{w0}}  {'SPEC':<{w1}}  {'OBSERVED':<{w2}}  PASS-FAIL")
    emit("-" * (w0 + w1 + w2 + 15))
    for g_, sp, ob, vd in rows:
        emit(f"{g_:<{w0}}  {sp:<{w1}}  {ob:<{w2}}  {vd}")

    # ---- outputs ----
    ev = pd.DataFrame({
        "event_date": [lab_w[p].date() for p in detected],
        "era": eras_det,
        "idx_ret_pct": r_w[detected] * 100.0,
        "idx_close": cl_w[detected],
        "idx_ma200": ma_w[detected],
        "idx_rv21": rv_w[detected],
        "rv_decile": decile[detected],
        "status": st,
        "fut_session": [u_labels[fu[p]].date() if fu[p] >= 0 else None for p in detected],
        "entry_label": [u_labels[fu[p] + 1].date() if fu[p] >= 0 and fu[p] + 1 < nU else None for p in detected],
        "entry_px": entry_open[detected],
        "gap_pct_of_idx": gap[detected] * 100.0,
        "exit_label": [u_labels[fu[p] + 3].date() if fu[p] >= 0 and fu[p] + 3 < nU else None for p in detected],
        "exit_px": exitc[detected],
        "gross_pts": c3[detected],
        "net_usd": net[detected],
        "cum_pts_c1": c1[detected], "cum_pts_c2": c2[detected], "cum_pts_c3": c3[detected],
    })
    cmap = dict(zip(tp, cluster_id))
    ev["cluster_id"] = [cmap.get(p, -1) for p in detected]
    ev.to_csv(OUT / "events.csv", index=False)
    pd.DataFrame({
        "control_date": [lab_w[p].date() for p in ctrl],
        "era": [era_of(lab_w[p]) for p in ctrl],
        "idx_ret_pct": r_w[ctrl] * 100.0, "idx_rv21": rv_w[ctrl], "rv_decile": decile[ctrl],
        "entry_px": entry_open[ctrl], "gap_pct_of_idx": gap[ctrl] * 100.0,
        "gross_pts": c3[ctrl], "net_usd": net[ctrl],
    }).to_csv(OUT / "controls.csv", index=False)

    wall = int(_time.time() - t0)
    emit(""); emit(f"wall_s {wall}")
    flush_to(OUT / "gate_table.txt")

    pending = {
        "trial_id": "G00028",
        "metrics": {
            "overlap_corr": round(corr, 6), "overlap_pairs": int(pair_ok.sum()),
            "n_detected": int(len(detected)), "n_untradeable_align": int((st == "UNTRADEABLE_ALIGN").sum()),
            "n_untradeable": int((st == "UNTRADEABLE").sum()),
            "n_vetoed": int((st == "VETOED").sum()), "n_traded": int(len(tp)),
            "n_clusters": n_clusters, "mean_net_usd": round(mean_net, 2), "median_net_usd": round(float(np.median(y)), 2),
            "clustered_t": round(tstat, 3), "clustered_se_usd": round(se, 2), "mde_usd": round(mde, 2),
            "sum_net_usd": round(float(y.sum()), 2), "win_rate": round(float((y > 0).mean()), 4),
            "ctrl_n": int(len(ctrl)), "ctrl_shortfall": int(shortfall), "ctrl_mean_net_usd": round(mean_ctrl, 2),
            "shift_n": int(len(means)), "shift_p95_usd": round(p95, 2), "shift_mean_usd": round(float(means.mean()), 2),
            "cum_pts_c1_mean": round(float(c1[tp].mean()), 2), "cum_pts_c2_mean": round(float(c2[tp].mean()), 2),
            "cum_pts_c3_mean": round(float(c3[tp].mean()), 2),
            "A1": bool(a1_pass), "D1": bool(d1), "D2": bool(d2), "D3": bool(d3),
            "index_source_sha256": man["sha256"], "substrate_sha256_match": True, "wall_s": wall,
        },
        "result": "PASS" if survived else "NULL",
        "note": ("MC-40 retest on percent-clean basis (G00027 was DEFECT: additive back-adjustment): events on CASH "
                 "NDX % (FRED NASDAQ100 via recorded Wayback snapshot, live host blocked), P&L in futures POINTS on "
                 "spliced deep/modern substrate; frozen band/horizon/MA/veto, $33/RT; Stage-A overlap corr "
                 f"{corr:.4f}>{CORR_GATE}; D1 event-clustered t; D2 index-RV-decile count-matched down-day control "
                 "(shared draw seed 0); D3 500 circular index-day shifts (same rng). "
                 + ("All gates passed -> SURVIVED-DISCOVERY (routes to robustness + independent implementation)."
                    if survived else "Failed gate(s) -> NULL at formulation; a FAIL is a FAIL. MC-40 finally TESTED.")),
    }
    (OUT / "ledger_result_pending.json").write_text(json.dumps(pending, indent=2), encoding="utf-8")
    print("WROTE:", OUT / "contract.txt", OUT / "gate_table.txt", OUT / "events.csv",
          OUT / "controls.csv", OUT / "ledger_result_pending.json")


if __name__ == "__main__":
    main()
