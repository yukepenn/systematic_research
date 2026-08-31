"""Diff local .ncd payload coverage against the NYSE trading calendar. Metadata only."""
import os, sys, datetime, collections

DB = r"C:\Users\Yuke Zhang\Documents\NinjaTrader 8\db\minute"
PAYLOAD_MIN = 201  # frozen in spec.txt: EMPTY <= 200 B

HOLIDAYS = {
 2013:"0101 0121 0218 0329 0527 0704 0902 1128 1225",
 2014:"0101 0120 0217 0418 0526 0704 0901 1127 1225",
 2015:"0101 0119 0216 0403 0525 0703 0907 1126 1225",
 2016:"0101 0118 0215 0325 0530 0704 0905 1124 1226",
 2017:"0102 0116 0220 0414 0529 0704 0904 1123 1225",
 2018:"0101 0115 0219 0330 0528 0704 0903 1122 1205 1225",
 2019:"0101 0121 0218 0419 0527 0704 0902 1128 1225",
 2020:"0101 0120 0217 0410 0525 0703 0907 1126 1225",
 2021:"0101 0118 0215 0402 0531 0705 0906 1125 1224",
 2022:"0101 0117 0221 0415 0530 0620 0704 0905 1124 1226",
 2023:"0102 0116 0220 0407 0529 0619 0704 0904 1123 1225",
 2024:"0101 0115 0219 0329 0527 0619 0704 0902 1128 1225",
 2025:"0101 0109 0120 0217 0418 0526 0619 0704 0901 1127 1225",  # 0109 = Carter day of mourning
}

def trading_days(y):
    hol = set(HOLIDAYS.get(y, "").split())
    out = []
    d = datetime.date(y, 1, 1)
    while d.year == y:
        if d.weekday() < 5 and d.strftime("%m%d") not in hol:
            out.append(d.strftime("%Y%m%d"))
        d += datetime.timedelta(days=1)
    return out

def payload_dates(sym):
    d = os.path.join(DB, sym)
    if not os.path.isdir(d):
        return set()
    s = set()
    for f in os.listdir(d):
        if f.endswith(".ncd"):
            p = os.path.join(d, f)
            if os.path.getsize(p) >= PAYLOAD_MIN:
                s.add(f.split(".")[0])
    return s

if __name__ == "__main__":
    sym = sys.argv[1]
    y0, y1 = int(sys.argv[2]), int(sys.argv[3])
    have = payload_dates(sym)
    allmiss = []
    print(f"=== {sym} ===")
    for y in range(y0, y1 + 1):
        td = trading_days(y)
        miss = [d for d in td if d not in have]
        extra = sorted(x for x in have if x.startswith(str(y)) and x not in set(td))
        print(f"{y}: expect={len(td):3d} have={len(td)-len(miss):3d} miss={len(miss):3d} "
              f"cov={100*(len(td)-len(miss))/len(td):5.1f}%" + (f"  EXTRA={extra}" if extra else ""))
        if miss:
            print("     missing:", " ".join(miss))
        allmiss += miss
    print("TOTAL MISSING:", len(allmiss))
