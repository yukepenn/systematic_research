"""Verifier engine for G2_F7 AUCTREV certification (S1/S2 support).

Re-implements BOTH recorded operationalizations of the frozen F6 contract as one
parameterized pipeline so every S1 disagreement can be classified at the decision
level (W52: decisions before dollars):
  seed_rule="morning" : qualification (c)/seed/exit uses bars stamped 00:00..09:30
                        ON the session's own calendar date (primary reading).
  seed_rule="chrono"  : qualification (c)/seed/exit uses the last SESSION bar
                        chronologically at/before the session date's 09:30
                        (clean-room reading, outI I2c/I3).
Everything else is identical in both recorded sources and coded once: session id
(time-of-day > 17:00 -> next calendar date), quals (a) >=300 bars 09:31..16:00 and
(b) >=1 bar 15:56..16:00 stamped on the session date, D = close16:00 - close15:50
grid closes, trailing-252 causal Q10/Q90 (np.quantile linear), strict <, next
qualifying session gap <= 7 calendar days, entry = first (16:00,17:00] session-date
bar OPEN (overnight fallback; unused on real tape), exit = seed-bar CLOSE, POINTS.
"""
import hashlib
import os
import sys

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from research_sdk import seal_guard  # noqa: E402

SUBSTRATE = os.path.join(REPO, r"research\scalping_lab\substrate\minute\NQ\nq1m_2005_202605.parquet")
EXPECTED_SHA = "dfd017eff0b031c2be89639fc4ad347d45053867edcdc2600002252b10b627cf"
RUN = os.path.join(REPO, r"runs\G2_F7_AUCTREV_CERT_20260829")
OUT = os.path.join(RUN, "out")

COST35 = 1.75
COST40 = 2.00
COST45 = 2.25
MULT = 20.0
TRAIL = 252
SESS_LO = pd.Timestamp("2006-01-01")
SESS_HI = pd.Timestamp("2026-05-31")
ERA1_END = pd.Timestamp("2015-12-31")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_bars():
    got = sha256_file(SUBSTRATE)
    assert got == EXPECTED_SHA, f"substrate sha256 mismatch: {got}"
    df = pd.read_parquet(SUBSTRATE, columns=["time", "open", "close"])
    df["ts"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S")
    seal_guard.assert_presealed(df, "ts", "G2_F7 verifier substrate load")
    df = df.sort_values("ts", kind="stable").reset_index(drop=True)
    day = df["ts"].dt.normalize()
    sec = (df["ts"] - day).dt.total_seconds().to_numpy()
    df["session"] = day.where(sec <= 17 * 3600, day + pd.Timedelta(days=1))
    df = df.loc[(df["session"] >= SESS_LO) & (df["session"] <= SESS_HI)].reset_index(drop=True)
    df["minute"] = df["ts"].dt.hour * 60 + df["ts"].dt.minute
    return df


def session_table(df: pd.DataFrame, seed_rule: str) -> pd.DataFrame:
    """One row per QUALIFYING session under seed_rule; grid closes, D, entry, seed/exit."""
    assert seed_rule in ("morning", "chrono")
    recs = []
    for sd, g in df.groupby("session", sort=True):
        gts = g["ts"].to_numpy()
        gmin = g["minute"].to_numpy()
        gdate = g["ts"].dt.normalize().to_numpy()
        own = gdate == np.datetime64(sd)          # stamped on the session's own date
        gclose = g["close"].to_numpy()
        gopen = g["open"].to_numpy()

        rth = own & (gmin >= 571) & (gmin <= 960)
        if int(rth.sum()) < 300:
            continue
        if not (own & (gmin >= 956) & (gmin <= 960)).any():
            continue
        morning = own & (gmin <= 570)
        if seed_rule == "morning":
            if not morning.any():
                continue
            seed_i = np.flatnonzero(morning)[-1]
        else:
            chrono = gts <= np.datetime64(sd + pd.Timedelta(hours=9, minutes=30))
            if not chrono.any():
                continue
            seed_i = np.flatnonzero(chrono)[-1]

        # grid closes 15:50 / 16:00: last own-date bar with minute <= stamp, ffill from seed
        def grid_close(mm):
            sel = np.flatnonzero(own & (gmin <= mm) & (gmin >= 571))
            return float(gclose[sel[-1]]) if len(sel) else float(gclose[seed_i])

        c1550, c1600 = grid_close(950), grid_close(960)

        ew = np.flatnonzero(own & (gmin > 960) & (gmin <= 1020))
        e_ts, e_px = (gts[ew[0]], float(gopen[ew[0]])) if len(ew) else (None, np.nan)

        recs.append(dict(session=sd, D=c1600 - c1550,
                         seed_ts=gts[seed_i], seed_close=float(gclose[seed_i]),
                         entry_ts=e_ts, entry_px=e_px,
                         has_morning=bool(morning.any())))
    q = pd.DataFrame(recs).sort_values("session").reset_index(drop=True)
    n = len(q)
    D = q["D"].to_numpy()
    q10 = np.full(n, np.nan)
    q90 = np.full(n, np.nan)
    q20 = np.full(n, np.nan)
    for i in range(TRAIL, n):
        w = D[i - TRAIL:i]
        q10[i] = np.quantile(w, 0.10)
        q20[i] = np.quantile(w, 0.20)
        q90[i] = np.quantile(w, 0.90)
    q["Q10"], q["Q20"], q["Q90"] = q10, q20, q90
    idx = np.arange(n)
    q["bottom"] = (idx >= TRAIL) & (D < q10)
    q["dec2"] = (idx >= TRAIL) & (D >= q10) & (D < q20)
    q["top"] = (idx >= TRAIL) & (D > q90)
    return q


def build_events(q: pd.DataFrame, df: pd.DataFrame, flag: str, side: str = "LONG",
                 entry_offset: int = 0):
    """Events for sessions where q[flag]; entry_offset=1 -> enter/exit one qualifying
    session later (S2 R_c late-entry control). Returns (events_df, counters)."""
    n = len(q)
    all_ts = df["ts"].to_numpy()
    all_open = df["open"].to_numpy()
    rows, n_sig, n_drop_next, n_drop_entry = [], 0, 0, 0
    for i in np.flatnonzero(q[flag].to_numpy()):
        n_sig += 1
        ei = i + entry_offset          # entry session index
        xi = ei + 1                    # exit session index
        if xi >= n:
            n_drop_next += 1
            continue
        esd, xsd = q.at[ei, "session"], q.at[xi, "session"]
        if (xsd - esd).days > 7:
            n_drop_next += 1
            continue
        e_ts, e_px = q.at[ei, "entry_ts"], q.at[ei, "entry_px"]
        if e_ts is None or (isinstance(e_px, float) and np.isnan(e_px)):
            lo = np.searchsorted(all_ts, np.datetime64(esd + pd.Timedelta(hours=18)), side="right")
            hi = np.searchsorted(all_ts, np.datetime64(xsd + pd.Timedelta(hours=9, minutes=30)), side="right")
            if hi <= lo:
                n_drop_entry += 1
                continue
            e_ts, e_px = all_ts[lo], float(all_open[lo])
        x_px = q.at[xi, "seed_close"]
        gross = (x_px - e_px) if side == "LONG" else (e_px - x_px)
        rows.append(dict(session_id=q.at[i, "session"].date().isoformat(),
                         era=1 if q.at[i, "session"] <= ERA1_END else 2,
                         D=q.at[i, "D"], Q10=q.at[i, "Q10"],
                         entry_ts=pd.Timestamp(e_ts), entry_px=e_px,
                         exit_ts=pd.Timestamp(q.at[xi, "seed_ts"]), exit_px=x_px,
                         gross_pts=gross, net35=gross - COST35))
    return pd.DataFrame(rows), dict(signals=n_sig, drop_next=n_drop_next, drop_entry=n_drop_entry)
