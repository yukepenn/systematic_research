"""GENESIS_FREEDATA_CBOE_20260828 — certification step.

Reads raw/ quarantine (parse only — no raw values printed), mechanically truncates
every table to < 2026-08-01 via research_sdk.seal_guard.truncate_presealed, asserts
the seal with assert_presealed on EVERY certified frame, writes certified/ parquet,
computes the contract stats (coverage, missingness, identity, sanity correlation),
and PRINTS the gate table to out/gate_table.txt (never hand-assembled).

Gates were decided before results (this file is the falsifier program):
  G0 core downloads complete       : 8/8 indices, cfevoloi, >=150 VX monthly files, 18/18 COT zips
  G1 seal assertion                : assert_presealed passes on EVERY certified frame (0 SealError)
  G2 VIX coverage                  : first date <= 1990-01-31 AND last certified date == 2026-07-31
  G3 VXN coverage                  : first date <= 2010-01-01 AND last certified date == 2026-07-31
  G4 VX settlements                : >=150 contracts certified, 0 identity mismatches,
                                     max trade date == 2026-07-31, min trade date <= 2005-06-30
  G5 CFE vol+OI                    : min date <= 2004-12-31 AND max date in [2026-07-29 .. 2026-07-31]
  G6 COT TFF                       : VIX futures rows >= 500 reports, max report date == 2026-07-28,
                                     >=99% of report dates are Tuesdays
  G7 sanity corr(VIX,VXN) levels   : >= 0.80 on overlapping certified dates (sanity only, NOT alpha)
  G8 caps                          : total raw bytes <= 100MB, max file <= 30MB
PASS iff all G0-G8 pass.
"""
from __future__ import annotations

import io
import json
import re
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research")
RUN = REPO / "runs" / "GENESIS_FREEDATA_CBOE_20260828"
RAW, CERT, OUT = RUN / "raw", RUN / "certified", RUN / "out"
sys.path.insert(0, str(REPO))
from research_sdk.seal_guard import SealError, assert_presealed, truncate_presealed  # noqa: E402

LINES: list[str] = []


def log(s: str = "") -> None:
    print(s, flush=True)
    LINES.append(s)


stats: dict = {"indices": {}, "vx": {}, "cfevoloi": {}, "cot": {}, "sanity": {}, "caps": {}, "seal": {}}
seal_assert_count = 0
seal_errors = 0
total_dropped_postseal = 0


def certify_frame(df: pd.DataFrame, col: str, ctx: str) -> pd.DataFrame:
    """Mechanical truncation + assertion; counts recorded; sealed values never shown."""
    global seal_assert_count, seal_errors, total_dropped_postseal
    kept, n_dropped = truncate_presealed(df, col, ctx)
    total_dropped_postseal += n_dropped
    try:
        assert_presealed(kept, col, ctx)
        seal_assert_count += 1
        LINES.append(f"seal_guard.assert_presealed PASS [{ctx}] rows={len(kept)} dropped_postseal={n_dropped}")
    except SealError as e:  # pragma: no cover — would be a defect
        seal_errors += 1
        LINES.append(f"seal_guard.assert_presealed RAISED [{ctx}]: {e}")
        raise
    return kept


def parse_dates(s: pd.Series, ctx: str) -> pd.Series:
    s = s.astype(str).str.strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
        try:
            return pd.to_datetime(s, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.to_datetime(s)  # last resort: let pandas infer (raises on failure)


def to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(",", "", regex=False).str.strip(), errors="coerce")


def weekday_gap(dates: pd.Series) -> int:
    """Count weekdays in span not present (holidays + any true gaps)."""
    if len(dates) == 0:
        return 0
    bd = pd.bdate_range(dates.min(), dates.max())
    return int(len(bd.difference(pd.DatetimeIndex(dates))))


# ------------------------------------------------------------------ 0. selftest
log("=" * 100)
log("GENESIS_FREEDATA_CBOE_20260828 — certification program output (printed, not hand-assembled)")
log("=" * 100)
st = subprocess.run([sys.executable, str(REPO / "research_sdk" / "seal_guard.py")],
                    capture_output=True, text=True, cwd=str(REPO))
log("[seal_guard selftest] " + (st.stdout.strip().splitlines()[-1] if st.stdout.strip() else f"NO OUTPUT rc={st.returncode}"))
selftest_pass = "PASS" in st.stdout

# ------------------------------------------------------------------ 1. manifest / caps
man = json.loads((RAW / "_MANIFEST.json").read_text(encoding="utf-8"))
files = man["files"]
dl = [f for f in files if f.get("sha256")]
stats["caps"] = {"total_bytes": man["total_bytes"], "n_files": len(dl),
                 "max_file_bytes": max(f["bytes"] for f in dl),
                 "n_unreachable": man["n_unreachable"]}
n_idx_dl = sum(1 for f in dl if f["dest"].startswith("raw/indices/"))
n_vx_dl = sum(1 for f in dl if f["dest"].startswith("raw/vx_"))
n_cot_dl = sum(1 for f in dl if f["dest"].startswith("raw/cot/"))
has_voloi = any(f["dest"].endswith("cfevoloi.csv") for f in dl)

# ------------------------------------------------------------------ 2. indices
log("")
log("-- indices --")
INDEX_SYMS = ["VIX", "VIX3M", "VIX9D", "VXN", "VVIX", "SKEW", "OVX", "GVZ"]
long_rows = []
for sym in INDEX_SYMS:
    p = RAW / "indices" / f"{sym}_History.csv"
    txt = p.read_text(encoding="utf-8", errors="replace")
    hdr_i = next(i for i, l in enumerate(txt.splitlines()) if l.upper().startswith("DATE"))
    df = pd.read_csv(io.StringIO(txt), skiprows=hdr_i)
    df.columns = [c.strip().upper() for c in df.columns]
    df["date"] = parse_dates(df["DATE"], sym)
    valcols = [c for c in df.columns if c not in ("DATE", "date")]
    for c in valcols:
        df[c] = to_num(df[c])
    close_col = "CLOSE" if "CLOSE" in df.columns else valcols[-1]
    keep = df[["date"] + valcols].rename(columns={c: c.lower() for c in valcols})
    keep = certify_frame(keep, "date", f"index {sym}")
    keep = keep.sort_values("date").reset_index(drop=True)
    ndup = int(keep.duplicated("date").sum())
    keep.to_parquet(CERT / f"idx_{sym}_daily.parquet", index=False)
    stats["indices"][sym] = {
        "columns": list(keep.columns), "n_rows": len(keep), "dup_dates": ndup,
        "first": str(keep["date"].min().date()), "last": str(keep["date"].max().date()),
        "weekday_gaps_in_span": weekday_gap(keep["date"]),
        "n_null_close": int(keep[close_col.lower()].isna().sum()),
    }
    lr = keep[["date", close_col.lower()]].rename(columns={close_col.lower(): "close"})
    lr.insert(0, "symbol", sym)
    long_rows.append(lr)
    log(f"  {sym:6s} rows={len(keep):6d} span={stats['indices'][sym]['first']}..{stats['indices'][sym]['last']} "
        f"dup={ndup} wkday_gaps={stats['indices'][sym]['weekday_gaps_in_span']} cols={stats['indices'][sym]['columns']}")
idx_long = pd.concat(long_rows, ignore_index=True)
assert_presealed(idx_long, "date", "indices combined long")
seal_assert_count += 1
LINES.append(f"seal_guard.assert_presealed PASS [indices combined long] rows={len(idx_long)}")
idx_long.to_parquet(CERT / "indices_close_long.parquet", index=False)

# ------------------------------------------------------------------ 3. VX per-contract
log("")
log("-- VX per-contract settlements --")
MONTH_NUM = {"F": 1, "G": 2, "H": 3, "J": 4, "K": 5, "M": 6, "N": 7, "Q": 8, "U": 9, "V": 10, "X": 11, "Z": 12}
MON3 = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}
vx_frames = []
identity_mismatch = 0
n_contracts_cert = 0
n_contracts_empty = 0
weekly_grabbed = 0
ragged = {"lines": 0, "nonempty_extra": 0, "files": 0}
for p in sorted((RAW / "vx_modern").glob("VX_*.csv")) + sorted((RAW / "vx_archive").glob("CFE_*_VX.csv")):
    if p.parent.name == "vx_modern":
        era = "modern_2013plus"
        exp = pd.Timestamp(p.stem.split("_")[1])
        cmonth, cyear = exp.month, exp.year
    else:
        era = "archive_2004_2012"
        code = p.stem.split("_")[1]  # e.g. F05
        exp = pd.NaT
        cmonth, cyear = MONTH_NUM[code[0]], 2000 + int(code[1:])
    file_ragged = {"n": 0}

    def _bad(line, _fr=file_ragged):  # ragged row: truncate/pad to 11 header fields, count it
        _fr["n"] += 1
        ragged["lines"] += 1
        if any(str(x).strip() for x in line[11:]):
            ragged["nonempty_extra"] += 1
        return (list(line) + [""] * 11)[:11]

    df = pd.read_csv(p, engine="python", on_bad_lines=_bad)
    if file_ragged["n"]:
        ragged["files"] += 1
    df.columns = [c.strip() for c in df.columns]
    df = df[df["Trade Date"].astype(str).str.strip().str.len() > 0]
    df = df[~df["Trade Date"].astype(str).str.contains("[A-Za-z]", regex=True, na=True)]
    if len(df) == 0:
        n_contracts_empty += 1
        continue
    lab = df["Futures"].astype(str).str.strip()
    labset = set(lab.unique())
    m = re.match(r"^([A-Z]{1,2}\d{0,2}) \((\w{3}) (\d{2,4})\)$", sorted(labset)[0])
    lab_ok = False
    if m and len(labset) == 1:
        lm, ly = MON3.get(m.group(2), -1), int(m.group(3))
        ly = ly + 2000 if ly < 100 else ly
        lab_ok = (lm == cmonth and ly == cyear and m.group(1) in MONTH_NUM)  # pure month code = monthly
        if m.group(1) not in MONTH_NUM:
            weekly_grabbed += 1
    if not lab_ok:
        identity_mismatch += 1
        log(f"  IDENTITY MISMATCH: {p.name} label(s) {sorted(labset)[:3]} vs expected month {cyear}-{cmonth:02d}")
    out = pd.DataFrame({
        "trade_date": parse_dates(df["Trade Date"], p.name),
        "contract_label": lab,
        "contract_year": cyear, "contract_month": cmonth,
        "expiry_date_file": exp, "era": era,
        "open": to_num(df["Open"]), "high": to_num(df["High"]), "low": to_num(df["Low"]),
        "close": to_num(df["Close"]), "settle": to_num(df["Settle"]), "change": to_num(df["Change"]),
        "total_volume": to_num(df["Total Volume"]), "efp": to_num(df["EFP"]),
        "open_interest": to_num(df["Open Interest"]), "source_file": p.name,
    })
    kept, nd = truncate_presealed(out, "trade_date", f"VX {p.name}")
    total_dropped_postseal += nd
    if len(kept) == 0:
        n_contracts_empty += 1
        continue
    vx_frames.append(kept)
    n_contracts_cert += 1
vx = pd.concat(vx_frames, ignore_index=True).sort_values(["trade_date", "contract_year", "contract_month"]).reset_index(drop=True)
vx["legacy_scale_flag"] = np.where(
    (vx["era"] == "archive_2004_2012") & (vx["trade_date"] < pd.Timestamp("2007-03-26")),
    "LEGACY_10X_SUSPECT", "")
assert_presealed(vx, "trade_date", "VX settlements combined")
seal_assert_count += 1
LINES.append(f"seal_guard.assert_presealed PASS [VX settlements combined] rows={len(vx)}")
vx.to_parquet(CERT / "vx_settlements_daily.parquet", index=False)
dup_vx = int(vx.duplicated(["trade_date", "contract_year", "contract_month", "era"]).sum())
stats["vx"] = {
    "n_contract_files_certified": n_contracts_cert, "n_contract_files_empty_or_all_postseal": n_contracts_empty,
    "identity_mismatches": identity_mismatch, "weekly_files_grabbed": weekly_grabbed,
    "n_rows": len(vx), "dup_rows": dup_vx,
    "first_trade_date": str(vx["trade_date"].min().date()), "last_trade_date": str(vx["trade_date"].max().date()),
    "n_rows_modern": int((vx["era"] == "modern_2013plus").sum()),
    "n_rows_archive": int((vx["era"] == "archive_2004_2012").sum()),
    "n_rows_legacy10x_flagged": int((vx["legacy_scale_flag"] != "").sum()),
    "contracts_per_trade_date_median": float(vx.groupby("trade_date").size().median()),
    "ragged_lines_truncated": ragged["lines"], "ragged_lines_nonempty_extra": ragged["nonempty_extra"],
    "ragged_files": ragged["files"],
}
log(f"  contracts certified={n_contracts_cert} empty/all-postseal={n_contracts_empty} "
    f"identity_mismatch={identity_mismatch} rows={len(vx)} span={stats['vx']['first_trade_date']}..{stats['vx']['last_trade_date']}")

# 10x rescale evidence: median settle/VIX-close ratio, nearest contract, two windows around 2007-03-26
vix_c = pd.read_parquet(CERT / "idx_VIX_daily.parquet")[["date", "close"]].rename(columns={"close": "vix"})
front = vx[(vx["era"] == "archive_2004_2012")].copy()
front["cm_date"] = pd.to_datetime(dict(year=front["contract_year"], month=front["contract_month"], day=1))
front = front.sort_values(["trade_date", "cm_date"]).groupby("trade_date").first().reset_index()
front = front.merge(vix_c, left_on="trade_date", right_on="date", how="inner")
w_pre = front[(front["trade_date"] >= "2007-01-15") & (front["trade_date"] <= "2007-03-25")]
w_post = front[(front["trade_date"] >= "2007-03-26") & (front["trade_date"] <= "2007-06-01")]
r_pre = float((w_pre["settle"] / w_pre["vix"]).median()) if len(w_pre) else float("nan")
r_post = float((w_post["settle"] / w_post["vix"]).median()) if len(w_post) else float("nan")
stats["vx"]["front_settle_over_vix_median_2007Q1_pre0326"] = r_pre
stats["vx"]["front_settle_over_vix_median_2007_post0326"] = r_post
log(f"  10x-rescale evidence: median(front settle / VIX close) pre-2007-03-26 = {r_pre:.2f}, post = {r_post:.2f}")

# ------------------------------------------------------------------ 4. cfevoloi
log("")
log("-- CFE volume + open interest (cfevoloi) --")
txt = (RAW / "cfe" / "cfevoloi.csv").read_text(encoding="utf-8", errors="replace")
tlines = txt.splitlines()
hdr_i = next(i for i, l in enumerate(tlines) if l.strip().strip('"').startswith("Date"))
voloi = pd.read_csv(io.StringIO("\n".join(tlines[hdr_i:])), skip_blank_lines=True)
voloi.columns = [c.strip() for c in voloi.columns]
voloi = voloi[voloi["Date"].astype(str).str.strip().str.len() > 0]
voloi = voloi[~voloi["Date"].astype(str).str.contains("[A-Za-z]", regex=True, na=True)]
voloi["date"] = parse_dates(voloi["Date"], "cfevoloi")
for c in voloi.columns:
    if c not in ("Date", "date"):
        voloi[c] = to_num(voloi[c])
voloi = voloi.drop(columns=["Date"])
voloi = certify_frame(voloi, "date", "cfevoloi")
voloi = voloi.sort_values("date").reset_index(drop=True)
voloi.to_parquet(CERT / "cfe_voloi_daily.parquet", index=False)
vx_vol_col = next(c for c in voloi.columns if c.upper().startswith("VOLATILITY INDEX VOLUME"))
vx_oi_col = next(c for c in voloi.columns if c.upper().startswith("VOLATILITY INDEX OI"))
stats["cfevoloi"] = {
    "n_rows": len(voloi), "n_cols": voloi.shape[1],
    "first": str(voloi["date"].min().date()), "last": str(voloi["date"].max().date()),
    "dup_dates": int(voloi.duplicated("date").sum()),
    "weekday_gaps_in_span": weekday_gap(voloi["date"]),
    "vx_volume_col": vx_vol_col, "vx_oi_col": vx_oi_col,
    "n_null_vx_volume": int(voloi[vx_vol_col].isna().sum()),
}
log(f"  rows={len(voloi)} cols={voloi.shape[1]} span={stats['cfevoloi']['first']}..{stats['cfevoloi']['last']} "
    f"dup={stats['cfevoloi']['dup_dates']} wkday_gaps={stats['cfevoloi']['weekday_gaps_in_span']}")

# ------------------------------------------------------------------ 5. COT TFF futures-only
log("")
log("-- CFTC COT TFF futures-only --")
EQ_PAT = r"VIX|S&P|NASDAQ|RUSSELL|DOW JONES|DJIA|MSCI|NIKKEI"
cot_frames = []
for y in range(2010, 2027):
    with zipfile.ZipFile(RAW / "cot" / f"fut_fin_txt_{y}.zip") as zf:
        with zf.open(zf.namelist()[0]) as fh:
            df = pd.read_csv(fh, dtype=str, low_memory=False)
    df["_src"] = f"annual_{y}"
    cot_frames.append(df)
with zipfile.ZipFile(RAW / "cot" / "fin_fut_txt_2006_2016.zip") as zf:
    with zf.open(zf.namelist()[0]) as fh:
        comb = pd.read_csv(fh, dtype=str, low_memory=False)
comb["_src"] = "combined_2006_2016"
cot = pd.concat(cot_frames + [comb], ignore_index=True)
cot.columns = [c.strip() for c in cot.columns]
cot["report_date"] = pd.to_datetime(cot["As_of_Date_In_Form_YYMMDD"].astype(str).str.strip().str.zfill(6), format="%y%m%d")
# combined file used ONLY for pre-2010 rows (annual files preferred where they exist)
cot = cot[(cot["_src"] != "combined_2006_2016") | (cot["report_date"] < pd.Timestamp("2010-01-01"))]
name = cot["Market_and_Exchange_Names"].astype(str).str.upper()
cot_sel = cot[name.str.contains(EQ_PAT, regex=True, na=False)].copy()
before_dedup = len(cot_sel)
cot_sel = cot_sel.drop_duplicates(subset=["CFTC_Contract_Market_Code", "report_date"], keep="first")
cot_sel = certify_frame(cot_sel, "report_date", "COT TFF futures-only (VIX + equity index rows)")
cot_sel = cot_sel.sort_values(["report_date", "CFTC_Contract_Market_Code"]).reset_index(drop=True)
cot_sel.to_parquet(CERT / "cot_tff_futures_only.parquet", index=False)
namesel = cot_sel["Market_and_Exchange_Names"].astype(str).str.upper()
vixrows = cot_sel[namesel.str.contains("VIX", na=False)]
tue_frac = float((cot_sel["report_date"].dt.weekday == 1).mean())
vix_tuesdays = pd.date_range(vixrows["report_date"].min(), vixrows["report_date"].max(), freq="W-TUE")
missing_vix_weeks = int(len(vix_tuesdays.difference(pd.DatetimeIndex(vixrows["report_date"].unique()))))
stats["cot"] = {
    "n_rows": len(cot_sel), "n_rows_before_dedup": before_dedup,
    "n_markets": int(cot_sel["Market_and_Exchange_Names"].nunique()),
    "first_report": str(cot_sel["report_date"].min().date()), "last_report": str(cot_sel["report_date"].max().date()),
    "pct_tuesday": 100 * tue_frac,
    "n_vix_reports": len(vixrows),
    "vix_first": str(vixrows["report_date"].min().date()), "vix_last": str(vixrows["report_date"].max().date()),
    "vix_missing_tuesdays_in_span": missing_vix_weeks,
    "vix_market_names": sorted(vixrows["Market_and_Exchange_Names"].unique().tolist()),
    "top_markets": cot_sel["Market_and_Exchange_Names"].value_counts().head(12).index.tolist(),
}
log(f"  rows={len(cot_sel)} markets={stats['cot']['n_markets']} span={stats['cot']['first_report']}..{stats['cot']['last_report']} "
    f"%Tue={stats['cot']['pct_tuesday']:.2f}")
log(f"  VIX rows={len(vixrows)} span={stats['cot']['vix_first']}..{stats['cot']['vix_last']} missing_tuesdays={missing_vix_weeks}")
log(f"  VIX market name(s): {stats['cot']['vix_market_names']}")

# ------------------------------------------------------------------ 6. sanity correlation
vxn_c = pd.read_parquet(CERT / "idx_VXN_daily.parquet")[["date", "close"]].rename(columns={"close": "vxn"})
j = vix_c.merge(vxn_c, on="date", how="inner").dropna()
corr = float(np.corrcoef(j["vix"], j["vxn"])[0, 1])
stats["sanity"] = {"n_overlap_days": len(j), "corr_VIX_VXN_levels": corr,
                   "overlap_first": str(j["date"].min().date()), "overlap_last": str(j["date"].max().date())}
log("")
log(f"-- sanity: corr(VIX, VXN) levels = {corr:.4f} on {len(j)} overlapping certified days "
    f"({stats['sanity']['overlap_first']}..{stats['sanity']['overlap_last']}) — sanity only, NOT alpha --")

stats["seal"] = {"n_frames_asserted": seal_assert_count, "n_seal_errors": seal_errors,
                 "total_postseal_rows_dropped": total_dropped_postseal, "selftest_pass": selftest_pass}

# ------------------------------------------------------------------ 7. GATE TABLE
def gate(name: str, spec: str, observed: str, ok: bool) -> bool:
    log(f"| {name:34s} | {spec:58s} | {observed:52s} | {'PASS' if ok else 'FAIL'} |")
    return ok


log("")
log("=" * 100)
log("GATE / SPEC / OBSERVED / PASS-FAIL   (printed by certify.py)")
log("=" * 100)
log(f"| {'GATE':34s} | {'SPEC':58s} | {'OBSERVED':52s} | VERDICT |")
res = []
res.append(gate("G0 core downloads",
                "8/8 indices; cfevoloi; >=150 VX files; 18/18 COT zips",
                f"{n_idx_dl}/8; voloi={has_voloi}; VX files={n_vx_dl}; COT={n_cot_dl}/18",
                n_idx_dl == 8 and has_voloi and n_vx_dl >= 150 and n_cot_dl == 18))
res.append(gate("G1 seal assertions",
                "assert_presealed passes on EVERY certified frame; selftest PASS",
                f"{seal_assert_count} frames asserted, {seal_errors} SealError, selftest={'PASS' if selftest_pass else 'FAIL'}, "
                f"{total_dropped_postseal} post-seal rows dropped",
                seal_errors == 0 and seal_assert_count >= 12 and selftest_pass))
res.append(gate("G2 VIX coverage",
                "first <= 1990-01-31 AND last == 2026-07-31",
                f"first={stats['indices']['VIX']['first']} last={stats['indices']['VIX']['last']}",
                stats["indices"]["VIX"]["first"] <= "1990-01-31" and stats["indices"]["VIX"]["last"] == "2026-07-31"))
res.append(gate("G3 VXN coverage",
                "first <= 2010-01-01 AND last == 2026-07-31",
                f"first={stats['indices']['VXN']['first']} last={stats['indices']['VXN']['last']}",
                stats["indices"]["VXN"]["first"] <= "2010-01-01" and stats["indices"]["VXN"]["last"] == "2026-07-31"))
res.append(gate("G4 VX settlements",
                ">=150 contracts; 0 identity mismatch; max trade=2026-07-31; min<=2005-06-30",
                f"contracts={n_contracts_cert}; mismatch={identity_mismatch}; "
                f"span={stats['vx']['first_trade_date']}..{stats['vx']['last_trade_date']}; dup={dup_vx}",
                n_contracts_cert >= 150 and identity_mismatch == 0
                and stats["vx"]["last_trade_date"] == "2026-07-31" and stats["vx"]["first_trade_date"] <= "2005-06-30"))
res.append(gate("G5 CFE vol+OI",
                "min <= 2004-12-31 AND max in [2026-07-29..2026-07-31]",
                f"span={stats['cfevoloi']['first']}..{stats['cfevoloi']['last']}",
                stats["cfevoloi"]["first"] <= "2004-12-31" and "2026-07-29" <= stats["cfevoloi"]["last"] <= "2026-07-31"))
res.append(gate("G6 COT TFF",
                ">=500 VIX reports; max report == 2026-07-28; >=99% Tuesdays",
                f"VIX reports={stats['cot']['n_vix_reports']}; max={stats['cot']['last_report']}; "
                f"%Tue={stats['cot']['pct_tuesday']:.2f}",
                stats["cot"]["n_vix_reports"] >= 500 and stats["cot"]["last_report"] == "2026-07-28"
                and stats["cot"]["pct_tuesday"] >= 99.0))
res.append(gate("G7 sanity corr(VIX,VXN)",
                ">= 0.80 (levels, overlapping certified days; sanity only)",
                f"corr={corr:.4f} on {len(j)} days", corr >= 0.80))
res.append(gate("G8 caps",
                "total <= 100MB; max file <= 30MB",
                f"total={man['total_bytes']/1e6:.1f}MB; max file={stats['caps']['max_file_bytes']/1e6:.2f}MB",
                man["total_bytes"] <= 100 * 1024 * 1024 and stats["caps"]["max_file_bytes"] <= 30 * 1024 * 1024))
overall = all(res)
log("=" * 100)
log(f"OVERALL: {'PASS' if overall else 'FAIL'} ({sum(res)}/9 gates)")
log("=" * 100)

(OUT / "gate_table.txt").write_text("\n".join(LINES) + "\n", encoding="utf-8")
(OUT / "contract_stats.json").write_text(json.dumps(stats, indent=1, default=str), encoding="utf-8")
print(f"WROTE {OUT / 'gate_table.txt'} and contract_stats.json; overall={'PASS' if overall else 'FAIL'}")
sys.exit(0 if overall else 1)
