"""AUCTREV clean-room independent implementation (G2_F7 S1, trial G00034).

Built ONLY from: F7 spec.yaml (S1), F6 spec.yaml, F6 out/spec_resolutions.txt,
GENESIS_REPRO_INCUMBENT_20260828 out/run_provenance.txt. No primary src/output read.
Operational choices frozen in outI/spec_resolutions_indep.txt BEFORE this ran.
"""
import hashlib
import os
import sys

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO)
from research_sdk import seal_guard  # noqa: E402

SUBSTRATE = os.path.join(REPO, r"research\scalping_lab\substrate\minute\NQ\nq1m_2005_202605.parquet")
EXPECTED_SHA = "dfd017eff0b031c2be89639fc4ad347d45053867edcdc2600002252b10b627cf"
OUT_DIR = os.path.join(REPO, r"runs\G2_F7_AUCTREV_CERT_20260829\outI")

COST35_PTS = 35.0 / 20.0   # $35/ctrRT at $20/pt = 1.75 pts
COST40_PTS = 40.0 / 20.0   # stress, reported non-gate
MULT = 20.0                # NQ $/pt

SESS_LO = pd.Timestamp("2006-01-01")
SESS_HI = pd.Timestamp("2026-05-31")
ERA1_END = pd.Timestamp("2015-12-31")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    # --- provenance + seal ---------------------------------------------------------
    got = sha256_file(SUBSTRATE)
    assert got == EXPECTED_SHA, f"substrate sha256 mismatch: {got}"
    print(f"substrate sha256 OK: {got}")

    df = pd.read_parquet(SUBSTRATE, columns=["time", "open", "close"])
    df["ts"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S")
    seal_guard.assert_presealed(df, "ts", "AUCTREV clean-room substrate load (G00034)")
    df = df.sort_values("ts", kind="stable").reset_index(drop=True)

    ts = df["ts"]
    day = ts.dt.normalize()
    sec = (ts - day).dt.total_seconds().to_numpy()
    session = day.where(sec <= 17 * 3600, day + pd.Timedelta(days=1))
    df["session"] = session

    keep = (df["session"] >= SESS_LO) & (df["session"] <= SESS_HI)
    df = df.loc[keep].reset_index(drop=True)
    all_ts = df["ts"].to_numpy()
    all_open = df["open"].to_numpy()

    # --- per-session qualification + grid closes (I2/I3) ---------------------------
    recs = []
    for sd, g in df.groupby("session", sort=True):
        gts = g["ts"].to_numpy()
        gclose = g["close"].to_numpy()
        gopen = g["open"].to_numpy()
        t0930 = sd + pd.Timedelta(hours=9, minutes=30)
        t0931 = sd + pd.Timedelta(hours=9, minutes=31)
        t1550 = sd + pd.Timedelta(hours=15, minutes=50)
        t1556 = sd + pd.Timedelta(hours=15, minutes=56)
        t1600 = sd + pd.Timedelta(hours=16)
        t1700 = sd + pd.Timedelta(hours=17)

        n_intraday = int(np.searchsorted(gts, np.datetime64(t1600), side="right")
                         - np.searchsorted(gts, np.datetime64(t0931), side="left"))
        n_late = int(np.searchsorted(gts, np.datetime64(t1600), side="right")
                     - np.searchsorted(gts, np.datetime64(t1556), side="left"))
        i0930 = np.searchsorted(gts, np.datetime64(t0930), side="right") - 1
        if n_intraday < 300 or n_late < 1 or i0930 < 0:
            continue

        i1550 = np.searchsorted(gts, np.datetime64(t1550), side="right") - 1
        i1600 = np.searchsorted(gts, np.datetime64(t1600), side="right") - 1
        if i1550 < 0 or i1600 < 0:
            continue  # cannot form D (not expected given (a); counted implicitly as non-qualifying)

        # entry-window bar: first bar stamped in (16:00, 17:00]
        j_lo = np.searchsorted(gts, np.datetime64(t1600), side="right")
        j_hi = np.searchsorted(gts, np.datetime64(t1700), side="right")
        if j_hi > j_lo:
            e_ts, e_px = gts[j_lo], float(gopen[j_lo])
        else:
            e_ts, e_px = None, np.nan

        recs.append(dict(
            session=sd,
            c1550=float(gclose[i1550]), c1600=float(gclose[i1600]),
            c0930=float(gclose[i0930]), c0930_ts=gts[i0930],
            entry_ts=e_ts, entry_px=e_px,
        ))

    q = pd.DataFrame(recs).sort_values("session").reset_index(drop=True)
    q["D"] = q["c1600"] - q["c1550"]
    n_qual = len(q)
    print(f"qualifying sessions: {n_qual}  ({q['session'].iloc[0].date()} .. {q['session'].iloc[-1].date()})")

    # --- trailing 252-session deciles (I4) ------------------------------------------
    D = q["D"].to_numpy()
    BURN = 252
    q10 = np.full(n_qual, np.nan)
    q90 = np.full(n_qual, np.nan)
    for i in range(BURN, n_qual):
        w = D[i - BURN:i]
        q10[i] = np.quantile(w, 0.10)
        q90[i] = np.quantile(w, 0.90)
    q["Q10"], q["Q90"] = q10, q90
    q["bottom"] = (np.arange(n_qual) >= BURN) & (q["D"] < q["Q10"])
    q["top"] = (np.arange(n_qual) >= BURN) & (q["D"] > q["Q90"])

    # --- build events (I5/I6/I7/I8) --------------------------------------------------
    def build(side: str):
        flag_col = "bottom" if side == "LONG" else "top"
        rows, n_sig, n_drop_next, n_drop_entry = [], 0, 0, 0
        for i in np.flatnonzero(q[flag_col].to_numpy()):
            n_sig += 1
            if i + 1 >= n_qual:
                n_drop_next += 1
                continue
            sd = q.at[i, "session"]
            nsd = q.at[i + 1, "session"]
            if (nsd - sd).days > 7:
                n_drop_next += 1
                continue
            e_ts, e_px = q.at[i, "entry_ts"], q.at[i, "entry_px"]
            if e_ts is None or (isinstance(e_px, float) and np.isnan(e_px)):
                # fallback: first bar stamped > signal 18:00 and <= next-qual 09:30
                lo = np.searchsorted(all_ts, np.datetime64(sd + pd.Timedelta(hours=18)), side="right")
                hi = np.searchsorted(all_ts, np.datetime64(nsd + pd.Timedelta(hours=9, minutes=30)), side="right")
                if hi <= lo:
                    n_drop_entry += 1
                    continue
                e_ts, e_px = all_ts[lo], float(all_open[lo])
            x_ts, x_px = q.at[i + 1, "c0930_ts"], q.at[i + 1, "c0930"]
            gross = (x_px - e_px) if side == "LONG" else (e_px - x_px)
            rows.append(dict(
                session_id=sd.date().isoformat(),
                era=1 if sd <= ERA1_END else 2,
                D=q.at[i, "D"], decile_flag="BOTTOM" if side == "LONG" else "TOP",
                entry_ts=pd.Timestamp(e_ts), entry_px=e_px,
                exit_ts=pd.Timestamp(x_ts), exit_px=x_px,
                gross_pts=gross,
                net35_pts=gross - COST35_PTS,
                net40_pts=gross - COST40_PTS,
                net_usd=(gross - COST35_PTS) * MULT,
            ))
        return pd.DataFrame(rows), n_sig, n_drop_next, n_drop_entry

    ev, n_sig, n_dnext, n_dentry = build("LONG")
    evs, s_sig, s_dnext, s_dentry = build("SHORT")

    # --- outputs ---------------------------------------------------------------------
    os.makedirs(OUT_DIR, exist_ok=True)
    out_ev = ev[["session_id", "D", "decile_flag", "entry_ts", "entry_px",
                 "exit_ts", "exit_px", "gross_pts", "net_usd"]].copy()
    for c in ("D", "entry_px", "exit_px", "gross_pts", "net_usd"):
        out_ev[c] = out_ev[c].map(lambda v: f"{v:.2f}")
    out_ev.to_csv(os.path.join(OUT_DIR, "events_indep.csv"), index=False)

    def stats(frame, col="net35_pts"):
        n = len(frame)
        if n == 0:
            return n, np.nan, np.nan, np.nan
        m = frame[col].mean()
        t = m / (frame[col].std(ddof=1) / np.sqrt(n)) if n > 1 else np.nan
        return n, m, m * MULT, t

    lines = []
    lines.append("G2_F7 S1 clean-room independent implementation — AUCTREV (trial G00034)")
    lines.append(f"substrate sha256 {EXPECTED_SHA} VERIFIED; seal_guard.assert_presealed PASSED")
    lines.append(f"qualifying sessions {n_qual}; burn-in {BURN} (no signal); "
                 f"signal-capable sessions {n_qual - BURN}")
    lines.append("")
    lines.append("BOTTOM-decile LONG (the strategy event set), $35/RT, POINTS-based:")
    lines.append(f"  signals {n_sig}; dropped no-next/gap>7d {n_dnext}; dropped no-entry {n_dentry}")
    n, mpts, musd, t = stats(ev)
    lines.append(f"  N events        : {n}")
    lines.append(f"  mean net/event  : {mpts:+.4f} pts  = {musd:+.2f} USD   (event-clustered t = {t:.3f})")
    for era, tag in ((1, "2006-2015"), (2, "2016-2026/05")):
        nE, mE, uE, tE = stats(ev[ev["era"] == era])
        lines.append(f"  era {tag:12s}: N={nE:4d}  mean net/event {mE:+.4f} pts = {uE:+.2f} USD  (t={tE:.3f})")
    n40, m40, u40, t40 = stats(ev, "net40_pts")
    lines.append(f"  $40/RT stress   : mean net/event {m40:+.4f} pts = {u40:+.2f} USD (reported, non-gate)")
    drift = ev["entry_px"] - (q.set_index(q["session"].dt.date.astype(str))["c1600"]
                              .reindex(ev["session_id"]).to_numpy())
    lines.append(f"  entry-vs-16:00-grid drift: mean {drift.mean():+.4f} pts, sd {drift.std(ddof=1):.4f} (record only)")
    lines.append("")
    lines.append("TOP-decile SHORT readout (F6 R10 — reported, NEVER gated), $35/RT:")
    lines.append(f"  signals {s_sig}; dropped no-next/gap>7d {s_dnext}; dropped no-entry {s_dentry}")
    n, mpts, musd, t = stats(evs)
    lines.append(f"  N events {n}; mean net/event {mpts:+.4f} pts = {musd:+.2f} USD (t={t:.3f})")
    for era, tag in ((1, "2006-2015"), (2, "2016-2026/05")):
        nE, mE, uE, tE = stats(evs[evs["era"] == era])
        lines.append(f"  era {tag:12s}: N={nE:4d}  mean {mE:+.4f} pts = {uE:+.2f} USD (t={tE:.3f})")
    lines.append("")
    lines.append("Multiplicity: AUCTREV is 1 of 13 formal GENESIS II objects (~750 prior experiments).")
    lines.append("Evidence status: DISCOVERY_CONSUMED. live_enabled NO. spend $0.")

    text = "\n".join(lines) + "\n"
    enc = text.encode("utf-8")
    with open(os.path.join(OUT_DIR, "summary_indep.txt"), "wb") as f:
        f.write(enc)
    assert os.path.getsize(os.path.join(OUT_DIR, "summary_indep.txt")) > 0
    print(text)


if __name__ == "__main__":
    main()
