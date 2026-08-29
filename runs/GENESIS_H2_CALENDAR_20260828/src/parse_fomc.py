"""Parse scheduled FOMC meeting dates 2006-2026 from fetched federalreserve.gov pages.

Sources (raw bytes saved + sha256 in out/calendar_artifacts/fetch_sha256.txt):
  fomccalendars.htm            -> years 2021-2027 (2027 discarded; spec window 2006-2026)
  fomchistorical{2006..2020}.htm

Scheduled meetings ONLY (spec R06): entries containing '(unscheduled)', '(cancelled)',
'(notation vote)' or 'Conference Call' are EXCLUDED and logged.
start_date = first listed calendar day; decision_date = last listed calendar day.
Output: fomc_meetings_2006_2026.csv (dates only) + fomc_parse_log.txt.
Cross-check: c01_announcement_calendar.csv FOMC rows (2022+) must equal fetched
decision days over their common window; discrepancies are printed loudly.
"""
import csv
import hashlib
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ART = os.path.join(RUN, "out", "calendar_artifacts")
ROOT = os.path.abspath(os.path.join(RUN, "..", ".."))

MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"])}
MON_ABBR = {m[:3]: v for m, v in MONTHS.items()}


def month_num(tok: str) -> int:
    tok = tok.strip()
    if tok in MONTHS:
        return MONTHS[tok]
    if tok[:3] in MON_ABBR:
        return MON_ABBR[tok[:3]]
    raise ValueError(f"unknown month token {tok!r}")


def parse_meeting(month_txt: str, day_txt: str, year: int):
    """month_txt e.g. 'January' | 'April/May' | 'Jan/Feb'; day_txt e.g. '31' | '29-30' | '30-1'."""
    day_txt = day_txt.replace("*", "").strip()
    months = [month_num(t) for t in month_txt.split("/")]
    days = [int(d) for d in re.split(r"[-–]", day_txt)]
    if len(days) == 1:
        m0 = m1 = months[0]
        d0 = d1 = days[0]
    else:
        d0, d1 = days
        if len(months) == 2:
            m0, m1 = months
        else:
            m0 = m1 = months[0]
            if d1 < d0:
                raise ValueError(f"cross-month days {day_txt!r} with single month {month_txt!r}")
    y0, y1 = year, year
    if len(months) == 2 and m1 < m0:  # Dec/Jan would wrap; has not occurred, fail loudly
        raise ValueError(f"month wrap not supported: {month_txt} {day_txt} {year}")
    return date(y0, m0, d0), date(y1, m1, d1)


def main():
    meetings = []   # (start, decision, source)
    excluded = []

    # --- historical pages 2006-2020 -------------------------------------------------
    for y in range(2006, 2021):
        fn = f"fomchistorical{y}.htm"
        html = open(os.path.join(ART, fn), encoding="utf-8", errors="replace").read()
        entries = re.findall(r"<h5[^>]*>([^<]+)</h5>", html)
        for e in entries:
            e = e.strip()
            if "(" in e or "Conference Call" in e:
                excluded.append((fn, e))
                continue
            m = re.match(r"^([A-Za-z/]+)\s+([\d\-–]+)\s+Meeting\s*-\s*(\d{4})$", e)
            m2 = re.match(r"^([A-Za-z]+)\s+(\d+)\s*[-–]\s*([A-Za-z]+)\s+(\d+)\s+Meeting\s*-\s*(\d{4})$", e)
            if m:
                yr = int(m.group(3))
                assert yr == y, f"year mismatch in {fn}: {e}"
                s, d = parse_meeting(m.group(1), m.group(2), yr)
            elif m2:  # e.g. 'July 31-August 1  Meeting - 2012'
                yr = int(m2.group(5))
                assert yr == y, f"year mismatch in {fn}: {e}"
                s = date(yr, month_num(m2.group(1)), int(m2.group(2)))
                d = date(yr, month_num(m2.group(3)), int(m2.group(4)))
            else:
                excluded.append((fn, "UNMATCHED: " + e))
                continue
            meetings.append((s, d, fn))

    # --- calendar page 2021-2026 ----------------------------------------------------
    fn = "fomccalendars.htm"
    html = open(os.path.join(ART, fn), encoding="utf-8", errors="replace").read()
    year_iter = list(re.finditer(r"<h4><a id=\"\d+\">(\d{4}) FOMC Meetings", html))
    for i, ym in enumerate(year_iter):
        y = int(ym.group(1))
        seg = html[ym.end(): year_iter[i + 1].start() if i + 1 < len(year_iter) else len(html)]
        if y < 2021 or y > 2026:
            continue
        rows = re.findall(
            r"fomc-meeting__month[^>]*>\s*<strong>([^<]+)</strong>.*?fomc-meeting__date[^>]*>([^<]+)<",
            seg, flags=re.S)
        for month_txt, day_txt in rows:
            raw = f"{month_txt.strip()} {day_txt.strip()}"
            if any(k in day_txt.lower() for k in ("unscheduled", "cancelled", "notation")):
                excluded.append((fn, f"{y}: {raw}"))
                continue
            s, d = parse_meeting(month_txt, day_txt, y)
            meetings.append((s, d, fn))

    meetings = sorted(set(meetings))
    # window 2006-2026 (spec); nothing else should be present
    assert all(2006 <= m[0].year <= 2026 for m in meetings), "meeting outside 2006-2026"

    # sanity: 8 scheduled meetings per year (2006 had 8; every year 2006-2025 has 8;
    # 2026 partial-year count depends on schedule — assert 2006..2025 == 8, print 2026)
    per_year = {}
    for s, d, _src in meetings:
        per_year[s.year] = per_year.get(s.year, 0) + 1
    expected = {y: 8 for y in range(2006, 2026)}
    expected[2020] = 7  # March 17-18 2020 meeting CANCELLED (page-labeled); 7 held
    problems = [f"{y}: {n} scheduled meetings (expected {expected[y]})"
                for y, n in sorted(per_year.items()) if y <= 2025 and n != expected[y]]

    out_csv = os.path.join(ART, "fomc_meetings_2006_2026.csv")
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["start_date", "decision_date", "source_file"])
        for s, d, src in meetings:
            w.writerow([s.isoformat(), d.isoformat(), src])

    # cross-check against c01 FOMC rows (2022+)
    c01 = os.path.join(ROOT, "research", "04_complementary_family", "c01_announcement_calendar.csv")
    c01_fomc = set()
    with open(c01) as f:
        for row in csv.DictReader(f):
            if row["event"] == "FOMC":
                c01_fomc.add(date.fromisoformat(row["date"]))
    fetched_dec = {d for _s, d, _src in meetings}
    lo, hi = min(c01_fomc), max(c01_fomc)
    fetched_in_window = {d for d in fetched_dec if lo <= d <= hi}
    only_c01 = sorted(c01_fomc - fetched_in_window)
    only_fetch = sorted(fetched_in_window - c01_fomc)

    log = os.path.join(ART, "fomc_parse_log.txt")
    with open(log, "w") as f:
        def p(*a):
            line = " ".join(str(x) for x in a)
            print(line)
            f.write(line + "\n")
        p(f"parsed {len(meetings)} scheduled meetings 2006-2026")
        p("per-year counts:", dict(sorted(per_year.items())))
        for pr in problems:
            p("COUNT PROBLEM:", pr)
        p(f"excluded {len(excluded)} non-scheduled/unparsed entries:")
        for src, e in excluded:
            p("  EXCLUDED", src, "|", e)
        p(f"cross-check vs c01 FOMC rows ({lo}..{hi}): c01 has {len(c01_fomc)},"
          f" fetched-in-window {len(fetched_in_window)}")
        p("  in c01 only:", only_c01 if only_c01 else "NONE")
        p("  in fetch only:", only_fetch if only_fetch else "NONE")
        h = hashlib.sha256(open(out_csv, "rb").read()).hexdigest()
        p("fomc_meetings_2006_2026.csv sha256", h)
        ok = (not problems) and (not only_c01) and (not only_fetch)
        p("PARSE STATUS:", "OK" if ok else "DISCREPANCY — investigate before use")
    return 0


if __name__ == "__main__":
    sys.exit(main())
