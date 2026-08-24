"""Merge staging/*.jsonl first-pass records: update IMAGE_MASTER, build derived tables.

Outputs (all in screenshot_forensics/):
- IMAGE_MASTER.csv: image_type_initial, reviewed=YES, forensic_status filled
- derived/first_pass_index.csv: one row per image with key fields flattened
- derived/capture_lag.csv: images with both capture date and report end date
- derived/risk_candidates.csv: every largest-loss / largest-win with family-era hints
"""
import csv, json, re
from datetime import datetime
from pathlib import Path

SF = Path(__file__).resolve().parents[1]
recs = {}
problems = []
for f in sorted((SF / "staging").glob("*.jsonl")):
    if f.name in ("batches.json", "batch_assign.json"):
        continue
    for ln, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
            recs[r["image_id"]] = (f.stem, r)
        except Exception as e:
            problems.append(f"{f.name}:{ln}: {e}")

print(f"records={len(recs)} problems={len(problems)}")
for p in problems[:10]:
    print("PROBLEM", p)

# update IMAGE_MASTER
mp = SF / "IMAGE_MASTER.csv"
rows = list(csv.DictReader(open(mp, encoding="utf-8")))
for r in rows:
    got = recs.get(r["image_id"])
    if got:
        batch, j = got
        r["image_type_initial"] = j.get("image_type") or ""
        r["reviewed"] = "YES"
        r["forensic_status"] = "FIRST_PASS"
        note = (j.get("notes") or "")[:180].replace("\n", " ")
        r["notes"] = note
with open(mp, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
missing = [r["image_id"] for r in rows if r["reviewed"] != "YES"]
print("missing:", missing)

def dparse(s):
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return datetime(int(m.group(3)), int(m.group(1)), int(m.group(2)))
    return None

idx_fields = ["image_id","batch","image_type","screen_capture_date","taskbar_date",
              "social_post_date","report_start_date","report_end_date","machine_name",
              "display_mode","strategy_name_visible","instrument_contract","net","trades",
              "win_rate","pf","max_dd","commission","largest_win","largest_loss",
              "trades_per_day","avg_time_min","avg_bars","settings_column","confidence"]
out = []
lag = []
risk = []
for iid in sorted(recs):
    batch, j = recs[iid]
    t = j.get("totals") or {}
    row = {
        "image_id": iid, "batch": batch, "image_type": j.get("image_type") or "",
        "screen_capture_date": j.get("screen_capture_date") or "",
        "taskbar_date": j.get("taskbar_date") or "",
        "social_post_date": j.get("social_post_date") or "",
        "report_start_date": j.get("report_start_date") or "",
        "report_end_date": j.get("report_end_date") or "",
        "machine_name": j.get("machine_name") or "",
        "display_mode": j.get("display_mode") or "",
        "strategy_name_visible": j.get("strategy_name_visible") or "",
        "instrument_contract": j.get("instrument_contract") or "",
        "net": t.get("net"), "trades": t.get("trades"), "win_rate": t.get("win_rate"),
        "pf": t.get("pf"), "max_dd": t.get("max_dd"), "commission": t.get("commission"),
        "largest_win": t.get("largest_win"), "largest_loss": t.get("largest_loss"),
        "trades_per_day": t.get("trades_per_day"), "avg_time_min": t.get("avg_time_min"),
        "avg_bars": t.get("avg_bars"),
        "settings_column": " | ".join(j.get("settings_column") or []),
        "confidence": j.get("confidence") or "",
    }
    out.append(row)
    cd = dparse(j.get("screen_capture_date")) or dparse(j.get("taskbar_date"))
    re_ = dparse(j.get("report_end_date"))
    if cd and re_:
        lag.append({"image_id": iid, "capture": cd.date().isoformat(),
                    "report_end": re_.date().isoformat(),
                    "lag_days": (cd - re_).days})
    if t.get("largest_loss") or t.get("largest_win"):
        risk.append({"image_id": iid, "report_start": j.get("report_start_date") or "",
                     "report_end": j.get("report_end_date") or "",
                     "image_type": j.get("image_type") or "",
                     "strategy_name": j.get("strategy_name_visible") or "",
                     "largest_loss": t.get("largest_loss"), "largest_win": t.get("largest_win"),
                     "max_dd": t.get("max_dd"), "net": t.get("net")})

d = SF / "derived"; d.mkdir(exist_ok=True)
for name, data, fields in [
    ("first_pass_index.csv", out, idx_fields),
    ("capture_lag.csv", lag, ["image_id","capture","report_end","lag_days"]),
    ("risk_candidates.csv", risk, ["image_id","report_start","report_end","image_type","strategy_name","largest_loss","largest_win","max_dd","net"]),
]:
    with open(d / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(data)
    print(name, len(data))
