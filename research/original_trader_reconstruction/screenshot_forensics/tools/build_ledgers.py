"""Build §56 CSV ledgers from staging JSONL + curation constants."""
import csv, json, re
from pathlib import Path

SF = Path(__file__).resolve().parents[1]
recs = {}
for f in sorted((SF / "staging").glob("*.jsonl")):
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            r = json.loads(line)
            recs[r["image_id"]] = (f.stem, r)

def num(s):
    if s is None or s == "":
        return None
    m = re.search(r"-?[\d,]+(?:\.\d+)?", str(s).replace("(", "-").replace(")", ""))
    return float(m.group().replace(",", "")) if m else None

# ---- family assignment by report window (era-based, Class C labels) ----
def family(iid, j):
    t = j.get("image_type") or ""
    re_ = j.get("report_end_date") or j.get("social_post_date") or ""
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", str(re_))
    if not m:
        return "UNDATED"
    mm, yy = int(m.group(1)), int(m.group(3))
    if yy <= 2025 and (yy < 2025 or mm <= 9):
        return "S-ERA (SolarWind A-params 90/179/5/10/10)"
    if yy == 2025:
        return "S-EVOLVED (A-params + M/St/U groups)"
    if yy == 2026 and mm == 1:
        return "TRANSITION (multi-block, pre-VF-panel)"
    return "V-ERA (VF-wrapper strategy / variants)"

rows_risk, rows_cost, rows_name, rows_param, rows_retro = [], [], [], [], []
for iid in sorted(recs):
    batch, j = recs[iid]
    t = j.get("totals") or {}
    fam = family(iid, j)
    if t.get("largest_loss") or t.get("largest_win"):
        ll = num(t.get("largest_loss"))
        rows_risk.append({
            "image_id": iid, "window": f'{j.get("report_start_date","")}->{j.get("report_end_date","")}',
            "report_type": j.get("image_type"), "family_era": fam,
            "strategy_name": j.get("strategy_name_visible") or "",
            "largest_loss": t.get("largest_loss"), "largest_win": t.get("largest_win"),
            "max_dd": t.get("max_dd"), "net": t.get("net"),
            "exact_2600": "YES" if ll is not None and 2590 <= abs(ll) <= 2610 else "",
            "exact_1300": "YES" if ll is not None and 1295 <= abs(ll) <= 1305 else "",
            "loss_limit_visible": "", "stop_param_visible": "",
        })
    comm = t.get("commission")
    if comm is not None and str(comm) != "":
        tr = num(t.get("trades"))
        c = num(comm)
        rows_cost.append({
            "image_id": iid, "window": f'{j.get("report_start_date","")}->{j.get("report_end_date","")}',
            "report_type": j.get("image_type"), "commission_total": comm,
            "trades": t.get("trades"),
            "commission_per_trade": round(c / tr, 2) if (c and tr) else "",
            "include_commission_state": "", "slippage": t.get("slippage"),
            "notes": "",
        })
    sn = j.get("strategy_name_visible")
    if sn:
        rows_name.append({"image_id": iid, "strategy_name_verbatim": sn,
                          "window": f'{j.get("report_start_date","")}->{j.get("report_end_date","")}',
                          "capture_date": j.get("screen_capture_date") or "", "family_era": fam})
    sc = j.get("settings_column") or []
    for i, v in enumerate(sc, 1):
        rows_param.append({"panel_id": f"{iid}-P", "image_id": iid, "row_index": i,
                           "raw_box": v, "capture_date": j.get("screen_capture_date") or "",
                           "report_window": f'{j.get("report_start_date","")}->{j.get("report_end_date","")}',
                           "family_era": fam})
    # retrospective risk: lag-based
    from datetime import datetime
    def dp(s):
        m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", str(s or ""))
        return datetime(int(m.group(3)), int(m.group(1)), int(m.group(2))) if m else None
    cd, red = dp(j.get("screen_capture_date")) or dp(j.get("taskbar_date")), dp(j.get("report_end_date"))
    if red:
        lag = (cd - red).days if cd else None
        risk = ("LOW" if lag is not None and lag <= 3 else
                "MEDIUM" if lag is not None and lag <= 14 else
                "HIGH_LAG_OR_UNKNOWN" if lag is not None else "UNKNOWN")
        rows_retro.append({"window": f'{j.get("report_start_date","")}->{j.get("report_end_date","")}',
                           "image_id": iid, "strategy": j.get("strategy_name_visible") or "(panel unnamed)",
                           "capture_lag_days": lag if lag is not None else "",
                           "evidence": "dual OS clocks" if cd else "no capture clock",
                           "risk_level": risk})

out = SF
for name, data, fields in [
    ("RISK_EVENT_LEDGER.csv", rows_risk, list(rows_risk[0].keys())),
    ("EXECUTION_COST_EVIDENCE.csv", rows_cost, list(rows_cost[0].keys())),
    ("STRATEGY_NAME_LEDGER.csv", rows_name, list(rows_name[0].keys())),
    ("PARAMETER_PANEL_LEDGER.csv", rows_param, list(rows_param[0].keys())),
    ("RETROSPECTIVE_OPTIMIZATION_RISK.csv", rows_retro, list(rows_retro[0].keys())),
]:
    with open(out / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(data)
    print(name, len(data))

# ---- author comment ledger from ip batches + social fields ----
rows_ac = []
n = 0
for iid in sorted(recs):
    batch, j = recs[iid]
    soc = j.get("social") or {}
    for c in (soc.get("comments") or []):
        n += 1
        who = str(c.get("who") or "")
        rows_ac.append({
            "comment_id": f"AC-{n:04d}", "image_id": iid,
            "post_context": (soc.get("post_title") or "")[:80],
            "visible_date": c.get("date") or "",
            "speaker": who,
            "is_author": "YES" if "AUTHOR" in who.upper() or "mac studio" in who else "",
            "exact_original_text": c.get("text") or "",
            "subject_category": "", "implication": "", "contradicts_prior": "",
        })
with open(out / "AUTHOR_COMMENT_LEDGER.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows_ac[0].keys()))
    w.writeheader(); w.writerows(rows_ac)
print("AUTHOR_COMMENT_LEDGER.csv", len(rows_ac))
