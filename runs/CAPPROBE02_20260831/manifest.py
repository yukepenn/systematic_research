"""CAPPROBE02 frozen manifest builder. Filesystem metadata only; no .ncd content parsed,
no economic statistic computed, nothing >= 2026-08-01 is read."""
import os, json, statistics, datetime, collections
from gaps import trading_days, HOLIDAYS

DB = r"C:\Users\Yuke Zhang\Documents\NinjaTrader 8\db\minute"
PAYLOAD_MIN = 201
SYMS = ["^TICK", "^TRIN", "^VIX", "^ADD"]
VIRGIN = "20260801"
BURN_LO, BURN_HI = "20260531", "20260731"

def scan(sym):
    d = os.path.join(DB, sym)
    if not os.path.isdir(d):
        return None
    out = {}
    for f in os.listdir(d):
        if f.endswith(".ncd"):
            dt = f.split(".")[0]
            if len(dt) == 8 and dt.isdigit():
                out[dt] = os.path.getsize(os.path.join(d, f))
    return out

res = {}
for sym in SYMS:
    files = scan(sym)
    if files is None:
        res[sym] = {"store_exists": False}
        continue
    pay = {d: s for d, s in files.items() if s >= PAYLOAD_MIN}
    emp = {d: s for d, s in files.items() if s < PAYLOAD_MIN}
    years = {}
    for y in range(2012, 2027):
        td = trading_days(y) if y in HOLIDAYS else None
        got = sorted(d for d in pay if d.startswith(str(y)))
        if not got and not td:
            continue
        row = {"payload": len(got),
               "empty": len([d for d in emp if d.startswith(str(y))])}
        if td:
            miss = [d for d in td if d not in pay]
            row["expected_sessions"] = len(td)
            row["coverage_pct"] = round(100 * (len(td) - len(miss)) / len(td), 1)
            row["missing"] = miss
            row["non_calendar_extra"] = sorted(d for d in got if d not in set(td))
        years[str(y)] = row
    sizes = sorted(pay.values())
    res[sym] = {
        "store_exists": True,
        "store_path": os.path.join(DB, sym),
        "total_files": len(files),
        "payload_sessions": len(pay),
        "empty_files": len(emp),
        "date_min_payload": min(pay) if pay else None,
        "date_max_payload": max(pay) if pay else None,
        "median_payload_bytes": int(statistics.median(sizes)) if sizes else None,
        "half_session_band_1700_2000B": sorted(d for d, s in pay.items() if 1700 <= s <= 2000),
        "by_year": years,
        "sealed_virgin_files_counted_not_read": sorted(d for d in files if d >= VIRGIN),
        "burned_window_files": len([d for d in files if BURN_LO <= d <= BURN_HI]),
    }

# joinable pre-2022 sessions
tick = set(d for d, s in (scan("^TICK") or {}).items() if s >= PAYLOAD_MIN)
trin = set(d for d, s in (scan("^TRIN") or {}).items() if s >= PAYLOAD_MIN)
pre = lambda S: set(d for d in S if "20130101" <= d <= "20211231")
both_pre = pre(tick) & pre(trin)
both_mod = set(d for d in (tick & trin) if "20220103" <= d <= "20260731")
res["_join"] = {
    "tick_pre2022": len(pre(tick)),
    "trin_pre2022": len(pre(trin)),
    "tick_AND_trin_pre2022": len(both_pre),
    "tick_AND_trin_2022_202607": len(both_mod),
}
print(json.dumps(res, indent=1))
