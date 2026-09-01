"""M_11 exposure profile from the DEPLOYED strategies' own per-bar ledgers.

Question: can a $10,206.86 account carry the book at the 3-MNQ mapping, and when is it
exposed across the 16:00 ET / 17:00 ET margin boundaries?

Substrate: the live NT8 exports. These are the executable objects' OWN position ledgers over
a DaysToLoad=365 warm-up replay, i.e. this is measurement, not simulation.
"""
import pandas as pd
import numpy as np

P1 = r"C:\NT8_ForwardLogs\export\we_p1pct_p1pct.csv"
XM = r"C:\NT8_ForwardLogs\export\we_xm_xm2.csv"

p1 = pd.read_csv(P1, usecols=["pyts", "qty", "size", "voteOK", "sessPnl", "stopped"],
                 parse_dates=["pyts"])
xm = pd.read_csv(XM, usecols=["timestamp", "position", "desired_direction", "realized_pnl"],
                 parse_dates=["timestamp"])
p1 = p1.rename(columns={"pyts": "ts"}).set_index("ts").sort_index()
xm = xm.rename(columns={"timestamp": "ts"}).set_index("ts").sort_index()

print("=" * 78)
print("SPAN  P1 %s -> %s  (%d bars)" % (p1.index.min(), p1.index.max(), len(p1)))
print("SPAN  XM %s -> %s  (%d bars)" % (xm.index.min(), xm.index.max(), len(xm)))
print("=" * 78)

# ---- session id: NT8 session runs 18:00 ET -> 17:00 ET.  Bars are END-stamped, so a bar
# stamped 18:01 is the first of a session.  Session date = the date of the 18:00 open.
def sess_id(idx):
    return (idx - pd.Timedelta(hours=18)).normalize()

p1["sess"] = sess_id(p1.index)
xm["sess"] = sess_id(xm.index)

# ---------------------------------------------------------------- 1. P1 position profile
print("\n--- 1. P1 POSITION PROFILE (qty is in NQ contracts) ---")
vc = p1["qty"].value_counts().sort_index()
for q, n in vc.items():
    print("  qty=%d  %8d bars  %6.2f%%" % (q, n, 100.0 * n / len(p1)))
print("  in a position: %.2f%% of bars" % (100.0 * (p1["qty"] > 0).mean()))
ent = ((p1["qty"] > 0) & (p1["qty"].shift(1).fillna(0) == 0)).sum()
print("  distinct entries (0 -> >0 transitions): %d" % ent)
sess_with_entry = p1.groupby("sess")["qty"].max()
print("  sessions total: %d   sessions with an entry: %d (%.1f%%)"
      % (len(sess_with_entry), (sess_with_entry > 0).sum(),
         100.0 * (sess_with_entry > 0).mean()))
print("  sessions whose max qty was 2: %d" % (sess_with_entry == 2).sum())

# ---------------------------------------------------------------- 2. XM position profile
print("\n--- 2. XM POSITION PROFILE (position is signed, in NQ contracts) ---")
vc = xm["position"].value_counts().sort_index()
for q, n in vc.items():
    print("  pos=%+d  %8d bars  %6.2f%%" % (q, n, 100.0 * n / len(xm)))
print("  in a position: %.2f%% of bars" % (100.0 * (xm["position"] != 0).mean()))
inpos = xm[xm["position"] != 0]
if len(inpos):
    tod = inpos.index.time
    print("  earliest time-of-day in a position: %s" % min(tod))
    print("  latest   time-of-day in a position: %s" % max(tod))

# ---------------------------------------------------------------- 3. the margin boundaries
print("\n--- 3. EXPOSURE ACROSS THE MARGIN BOUNDARIES ---")
print("    A futures broker grants reduced INTRADAY margin only inside a window and requires")
print("    full INITIAL margin on anything held past it (Tradovate: ~15:55-16:00 ET).")

def held_at(df, col, hh, mm, signed=False):
    """Sessions holding a position on the bar stamped hh:mm."""
    m = (df.index.hour == hh) & (df.index.minute == mm)
    sub = df[m]
    v = sub[col].abs() if signed else sub[col]
    return sub, v

for label, (hh, mm) in [("15:45 ET", (15, 45)), ("15:55 ET", (15, 55)),
                        ("16:00 ET", (16, 0)), ("16:59 ET", (16, 59))]:
    s1, v1 = held_at(p1, "qty", hh, mm)
    s2, v2 = held_at(xm, "position", hh, mm, signed=True)
    print("  %s : P1 holds on %4d/%4d bars (%5.1f%%, max qty %d) | "
          "XM holds on %4d/%4d bars (%5.1f%%, max |pos| %d)"
          % (label, (v1 > 0).sum(), len(s1), 100.0 * (v1 > 0).mean() if len(s1) else 0,
             int(v1.max()) if len(v1) else 0,
             (v2 > 0).sum(), len(s2), 100.0 * (v2 > 0).mean() if len(s2) else 0,
             int(v2.max()) if len(v2) else 0))

# ---------------------------------------------------------------- 4. combined, in MNQ
print("\n--- 4. COMBINED EXPOSURE AT THE 3-MNQ MAPPING ---")
comb = pd.DataFrame(index=p1.index.union(xm.index))
comb["p1"] = p1["qty"].reindex(comb.index).ffill().fillna(0)
comb["xm"] = xm["position"].abs().reindex(comb.index).ffill().fillna(0)
comb["nq_equiv"] = comb["p1"] + comb["xm"]
comb["mnq"] = comb["nq_equiv"] * 3
vc = comb["mnq"].value_counts().sort_index()
for q, n in vc.items():
    print("  %2d MNQ  %8d bars  %6.2f%%" % (q, n, 100.0 * n / len(comb)))
print("  MAX SIMULTANEOUS: %d MNQ (= %.1f NQ-equivalent)"
      % (comb["mnq"].max(), comb["nq_equiv"].max()))

# at the boundary specifically
for label, (hh, mm) in [("16:00 ET", (16, 0)), ("16:59 ET", (16, 59))]:
    m = (comb.index.hour == hh) & (comb.index.minute == mm)
    sub = comb[m]
    if len(sub):
        print("  at %s: max %d MNQ, held>0 on %d/%d sessions (%.1f%%), mean %.2f MNQ"
              % (label, sub["mnq"].max(), (sub["mnq"] > 0).sum(), len(sub),
                 100.0 * (sub["mnq"] > 0).mean(), sub["mnq"].mean()))
        d = sub["mnq"].value_counts().sort_index()
        print("       distribution at %s: %s" % (label, dict(d)))

# ---------------------------------------------------------------- 5. capital
print("\n--- 5. CAPITAL ARITHMETIC ---")
CASH = 10206.86
maxmnq = int(comb["mnq"].max())
print("  live account cash: $%,.2f".replace(",", ",") % CASH if False else "  live account cash: $%.2f" % CASH)
for name, im in [("CME MNQ maintenance (external ref)", 2_640.0),
                 ("typical broker overnight initial", 2_900.0),
                 ("typical broker INTRADAY (day) margin", 500.0),
                 ("aggressive intraday margin", 100.0)]:
    need = maxmnq * im
    print("    %-38s $%8.0f/ctr -> %2d MNQ needs $%9.0f  %s"
          % (name, im, maxmnq, need, "OK" if need <= CASH else "*** EXCEEDS CASH ***"))
    print("       %-35s account can carry %d contracts" % ("", int(CASH // im)))

print("\n  DRAWDOWN SURVIVABILITY")
for name, dd in [("trade-level maxDD (1NQ+1NQ)", 51891.0), ("weekly maxDD (1NQ+1NQ)", 45138.0)]:
    s = dd * 0.30
    print("    %-30s $%9.0f  ->  at 3/10: $%8.0f   = %5.1f%% of the $%.0f account"
          % (name, dd, s, 100.0 * s / CASH, CASH))
