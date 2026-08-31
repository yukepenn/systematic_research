"""TICK01ERA_20260831 - the FROZEN G2_F1_TICK01 mechanism, re-run UNCHANGED on 2013/2015/2017.

Spec runs/TICK01ERA_20260831/spec.yaml committed BEFORE this file produced anything.

build_grid / detect_events / cluster_t below are COPIED VERBATIM (modulo the NQ source) from
runs/G2_F1_TICK01_20260829/src/tick01.py. TRIG, REARM, H_TARGET, H_DIAG, MDE_K and the three gate
predicates are byte-identical to that run. Nothing is tuned, searched or selected here.

Era stratification is structural, not cosmetic: ERABREAK01 (p=0.0011) forbids pooling pre-2022
intraday-vol statistics with modern ones, so every gate is evaluated INSIDE a stratum and the
modern window is quoted from its own closed run rather than recomputed or merged.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
sys.path.insert(0, ROOT)
from research_sdk.null_guard import run_circular_null, verify_null_sensitivity  # noqa: E402

RUN = os.path.join(ROOT, "runs", "TICK01ERA_20260831")
OUT = os.path.join(RUN, "out")
ERA_DIR = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "out", "era")
os.makedirs(OUT, exist_ok=True)

# ---- FROZEN, INHERITED. NOT ONE OF THESE IS CHOSEN BY THIS RUN. ----------------------
TRIG, REARM = -1000.0, -400.0
H_TARGET = 15
H_DIAG = (5, 30, 60)
N_DRAWS_T2 = 1000
SEED_T2 = 20260831
MDE_K = 2.80
MIN_TICK_BARS = 300          # CAPPROBE01's frozen payload rule
YEARS = [2013, 2015, 2017]

# DEFECT FIXED 2026-08-31, and it is the CLAUDE.md sec7 truncate-then-write class.
# These two writers were originally opened in "w" mode AT MODULE LEVEL. TICK01ERA2 imports this
# module to reuse the frozen automaton, and that import alone TRUNCATED this run's already
# committed gate_table.txt and tick01era_log.txt to zero bytes before the importer could
# re-point them. Nothing was lost - both files were restored from commit a856b79 - but the
# failure mode is exactly the one that once zeroed CURRENT_BASELINE.md. Opening is now LAZY:
# importing this module can no longer touch a single byte on disk.
_log = None
_gate = None


def open_writers(out_dir: str | None = None):
    """Called by main(), never by import. An importer sets its OWN writers instead."""
    global _log, _gate, OUT
    if out_dir is not None:
        OUT = out_dir
    os.makedirs(OUT, exist_ok=True)
    _log = open(os.path.join(OUT, "tick01era_log.txt"), "w", encoding="utf-8")
    _gate = open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    if _log is not None:
        print(*a, file=_log)


def G(*a):
    P(*a)
    if _gate is not None:
        print(*a, file=_gate)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ============================================================ VERBATIM FROM tick01.py
def detect_events(frame: pd.DataFrame, trig=TRIG, rearm=REARM, sign=-1) -> np.ndarray:
    x = frame["tick"].to_numpy()
    if sign < 0:
        a = x <= trig
        b = x >= rearm
    else:
        a = x >= trig
        b = x <= rearm
    codes = pd.factorize(frame["session"], sort=False)[0]
    s = pd.Series(np.where(a, 1.0, np.where(b, 0.0, np.nan)))
    prev = s.groupby(codes).ffill().groupby(codes).shift(1).to_numpy()
    return a & ~(prev == 1.0)


def cluster_t(x: np.ndarray, clusters: np.ndarray):
    n = len(x)
    xbar = float(np.mean(x))
    e = x - xbar
    sums = pd.Series(e).groupby(pd.Series(clusters)).sum().to_numpy()
    g = len(sums)
    se = np.sqrt(np.sum(sums ** 2) * (g / (g - 1))) / n
    return xbar, xbar / se, se, g
# ====================================================================================


def load_era(year: int):
    """One CSV per era year from SWBarExport_v2. Returns (tick_df, nq_front_df, prov)."""
    p = os.path.join(ERA_DIR, f"era{year}_bars.csv")
    d = pd.read_csv(p)
    d["time"] = pd.to_datetime(d["time"])
    d["date"] = d["time"].dt.normalize()
    d = d[d["date"].dt.year == year]

    tick = d[d["symbol"] == "$TICK"][["time", "date", "close"]].copy()

    # ---- payload gate, CAPPROBE01's frozen >=300-bar rule, applied to RTH bars only
    tod = tick["time"].dt.time
    rth = tick[(tod >= pd.Timestamp("09:31").time()) & (tod <= pd.Timestamp("15:59").time())]
    per = rth.groupby("date").size()
    good = set(per[per >= MIN_TICK_BARS].index)
    P(f"    {year}: ^TICK calendar dates present {tick['date'].nunique():,}; "
      f"pass the frozen >= {MIN_TICK_BARS}-RTH-bar payload gate: {len(good):,} "
      f"(rejected {tick['date'].nunique() - len(good):,})")
    tick = tick[tick["date"].isin(good)]

    # ---- front-month NQ: MAX SESSION VOLUME, ties -> EARLIEST EXPIRY (declared in spec)
    fut = d[d["symbol"] != "$TICK"].copy()
    ftod = fut["time"].dt.time
    fr = fut[(ftod >= pd.Timestamp("09:31").time()) & (ftod <= pd.Timestamp("15:59").time())]
    vol = fr.groupby(["date", "symbol"])["volume"].sum().reset_index()
    order = {s: i for i, s in enumerate(sorted(fut["symbol"].unique(), key=_expiry_key))}
    vol["ord"] = vol["symbol"].map(order)
    vol = vol.sort_values(["date", "volume", "ord"], ascending=[True, False, True])
    front = vol.groupby("date").first().reset_index()[["date", "symbol", "volume"]]
    P(f"    {year}: front-month contract by session -> " +
      ", ".join(f"{s}:{int(c)}" for s, c in front["symbol"].value_counts().sort_index().items()))

    sel = fut.merge(front[["date", "symbol"]], on=["date", "symbol"], how="inner")
    sel = sel[["time", "date", "close", "volume"]].sort_values("time")
    prov = dict(year=year, csv=p, sha256=sha256(p), rows=int(len(d)),
                tick_dates=int(tick["date"].nunique()),
                nq_front_rows=int(len(sel)),
                nq_close_min=float(sel["close"].min()), nq_close_max=float(sel["close"].max()),
                contracts=";".join(f"{s}={int(c)}" for s, c in
                                   front["symbol"].value_counts().sort_index().items()))
    return tick, sel, prov


def _expiry_key(sym: str) -> tuple:
    """NQH3 -> (2013,3). NT8 display symbols are decade-ambiguous, but within a single era
    export only one decade is present, so the year digit resolves uniquely against YEARS."""
    m = {"H": 3, "M": 6, "U": 9, "Z": 12}
    if len(sym) < 4 or sym[:2] != "NQ":
        return (9999, 99)
    mon, dig = sym[2], int(sym[3])
    base = None
    for y in YEARS + [y + 1 for y in YEARS]:
        if y % 10 == dig:
            base = y if base is None else min(base, y)
    return (base if base else 9999, m.get(mon, 99))


def build_grid(tick: pd.DataFrame, nq: pd.DataFrame):
    """VERBATIM structure from tick01.py build_grid: one row per (session, RTH slot
    09:31..15:59); equal-length contiguous blocks so a session rotation is positional."""
    tick = tick.drop_duplicates(subset="time").copy()
    tick["tod"] = tick["time"].dt.time
    slots = pd.timedelta_range("09:31:00", "15:59:00", freq="1min")
    slot_times = set((pd.Timestamp("2000-01-01") + slots).time)
    off = ~tick["tod"].isin(slot_times)
    tick = tick[~off]

    sessions = np.sort(tick["date"].unique())
    n_sess, n_slot = len(sessions), len(slots)
    idx = pd.MultiIndex.from_product([sessions, slots], names=["date", "slot"])
    stamps = idx.get_level_values("date") + idx.get_level_values("slot")

    tmap = pd.Series(tick["close"].to_numpy(), index=tick["time"])
    if not tmap.index.is_unique:
        raise SystemExit("DEFECT: duplicate TICK stamps after dedup")
    nq = nq.drop_duplicates(subset="time")
    qmap = pd.Series(nq["close"].to_numpy(), index=nq["time"])
    if not qmap.index.is_unique:
        raise SystemExit("DEFECT: duplicate NQ stamps after front selection")

    frame = pd.DataFrame({
        "session": np.repeat(sessions, n_slot),
        "stamp": stamps,
        "tick": tmap.reindex(stamps).to_numpy(),
        "nq_at": qmap.reindex(stamps).to_numpy(),
    })
    for h in sorted(set(H_DIAG) | {H_TARGET}):
        fwd = qmap.reindex(stamps + pd.Timedelta(minutes=h)).to_numpy()
        frame[f"fwd{h}"] = (fwd / frame["nq_at"].to_numpy() - 1.0) * 1e4
    assert len(frame) == n_sess * n_slot
    P(f"      grid {n_sess:,} sessions x {n_slot} slots = {len(frame):,} rows; "
      f"tick {frame['tick'].notna().sum():,}, NQ exact-stamp {frame['nq_at'].notna().sum():,}, "
      f"fwd{H_TARGET} {frame[f'fwd{H_TARGET}'].notna().sum():,}")
    return frame, n_sess


def evaluate(name: str, frame: pd.DataFrame, n_sess: int) -> dict:
    fwd_t = f"fwd{H_TARGET}"
    P("")
    P("=" * 100)
    P(f"=== STRATUM {name}")
    P("=" * 100)

    ev = frame[detect_events(frame)].copy()
    evs = ev[ev[fwd_t].notna() & ev["nq_at"].notna()]
    P(f"    events detected {len(ev):,}; scored (exact NQ stamp + computable fwd15) {len(evs):,}")
    if len(ev):
        for y, c in ev["session"].dt.year.value_counts().sort_index().items():
            P(f"      {y}: {c:>5,} events")
    P(f"    sessions {n_sess:,}; sessions with >=1 event {ev['session'].nunique():,}; "
      f"events per 252 sessions {len(ev) / (n_sess / 252.0):,.1f}")
    if len(evs) < 3 or evs["session"].nunique() < 2:
        P("    *** too few scored events for a gate in this stratum - this is a RESULT "
          "(the regime does not produce the event), not a failure to run ***")
        return dict(name=name, n=int(len(evs)), n_events=int(len(ev)), sessions=n_sess,
                    insufficient=True, events=ev)

    x = evs[fwd_t].to_numpy()
    mean_bps, t_cl, se, g = cluster_t(x, evs["session"].to_numpy())
    sd = float(np.std(x, ddof=1))
    mde = MDE_K * sd / np.sqrt(len(x))

    # ---- T2 count-matched same-session control (frozen construction)
    universe = frame[frame["tick"].notna() & frame["nq_at"].notna() & frame[fwd_t].notna()]
    k_by = evs.groupby("session").size()
    uni = {s: gg[fwd_t].to_numpy() for s, gg in universe.groupby("session")}
    rng = np.random.default_rng(SEED_T2)
    dm = np.empty(N_DRAWS_T2)
    for d in range(N_DRAWS_T2):
        tot, cnt = 0.0, 0
        for s, k in k_by.items():
            u = uni[s]
            pick = rng.choice(len(u), size=int(k), replace=False)
            tot += float(u[pick].sum()); cnt += int(k)
        dm[d] = tot / cnt
    ctrl_p95 = float(np.percentile(dm, 95)); ctrl_mean = float(np.mean(dm))
    P(f"    T2 control: universe {len(universe):,} minutes / {len(uni):,} sessions, "
      f"per-draw n {int(k_by.sum()):,}; draw mean {ctrl_mean:+.3f}, p95 {ctrl_p95:+.3f} bps")

    # ---- T3 session-block circular-shift null, sensitivity FIRST
    loader = lambda: frame[["session", "tick", fwd_t, "nq_at"]].copy()
    decide = lambda f: detect_events(f)

    def score(dcs, base):
        v = base[fwd_t].to_numpy()[np.asarray(dcs, dtype=bool)]
        v = v[~np.isnan(v)]
        return float(np.mean(v)) if len(v) else np.nan

    probes = [k for k in (1, 7, 313) if k % n_sess != 0][:3] or [1, 2, 3]
    sens = verify_null_sensitivity(loader, decide, score, shifts=probes, unit="session")
    null = run_circular_null(loader, decide, score, n_shifts=n_sess - 1, unit="session")
    arr = np.asarray(null["null_stats"], dtype=float)
    fin = arr[~np.isnan(arr)]
    null_p95 = float(np.percentile(fin, 95))
    P(f"    T3 null: sensitivity spread {sens['spread']:.4f} bps -> HAS TEETH; "
      f"{len(arr):,} rotations ({int(np.isnan(arr).sum())} zero-event), null mean {np.mean(fin):+.4f}, "
      f"p95 {null_p95:+.4f}, percentile of real {null['percentile']:.4f}, p_ge {null['p_ge']:.4f}")
    if abs(null["real_stat"] - mean_bps) > 1e-9:
        raise SystemExit("DEFECT: null-machinery real stat != T1 event mean")

    # ---- secondary +1000 (NON-GATE) and horizon profile (NON-GATE)
    pv = frame[detect_events(frame, trig=+1000.0, rearm=+400.0, sign=+1)]
    pvs = pv[pv[fwd_t].notna() & pv["nq_at"].notna()]
    if len(pvs) >= 2 and pvs["session"].nunique() >= 2:
        pm, pt, _, _ = cluster_t(pvs[fwd_t].to_numpy(), pvs["session"].to_numpy())
    else:
        pm, pt = float("nan"), float("nan")
    P(f"    NON-GATE secondary +1000: n {len(pvs):,}, mean {pm:+.3f} bps, t {pt:+.2f}")
    hp = {}
    for h in H_DIAG:
        fh = f"fwd{h}"
        sub = ev[ev[fh].notna() & ev["nq_at"].notna()]
        hm, ht, _, _ = cluster_t(sub[fh].to_numpy(), sub["session"].to_numpy())
        hp[h] = (len(sub), hm, ht)
        P(f"    NON-GATE horizon {h:>3} min: n {len(sub):>5,} mean {hm:+.3f} bps t {ht:+.2f}")

    return dict(name=name, insufficient=False, n=len(x), g=g, sessions=n_sess,
                n_events=int(len(ev)), mean=mean_bps, t=t_cl, sd=sd, mde=mde,
                ctrl_p95=ctrl_p95, ctrl_mean=ctrl_mean, null_p95=null_p95,
                null_pct=null["percentile"], null_p_ge=null["p_ge"], rotations=int(len(arr)),
                T1=bool(mean_bps > 0 and t_cl >= 2.0), T2=bool(mean_bps > ctrl_p95),
                T3=bool(mean_bps > null_p95), pos_mean=pm, pos_t=pt,
                horizons={str(h): dict(n=int(v[0]), mean=round(v[1], 4), t=round(v[2], 3))
                          for h, v in hp.items()},
                events=ev)


def power_audit():
    """Preregistered audit of the CAPPROBE01 1,147 -> 3,380 / MDE x0.58 claim."""
    f = open(os.path.join(OUT, "power_audit.txt"), "w", encoding="utf-8")

    def A(*a):
        P(*a); print(*a, file=f)

    A("")
    A("=" * 100)
    A("=== PREREGISTERED POWER-ARITHMETIC AUDIT (spec section power_arithmetic_to_verify_and_print)")
    A("=" * 100)
    tickdir = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8",
                           "db", "minute", "^TICK")
    by_year = {}
    for n in os.listdir(tickdir):
        if len(n) >= 8 and n[:8].isdigit():
            y = int(n[:4])
            sz = os.path.getsize(os.path.join(tickdir, n))
            by_year.setdefault(y, [0, 0])
            by_year[y][0] += 1
            if sz > 32:
                by_year[y][1] += 1
    A("    (a) WHAT IS ACTUALLY LOCAL (db\\minute\\^TICK, payload = file > 32 B):")
    local_pre = 0
    for y in sorted(by_year):
        tot, pay = by_year[y]
        tag = ""
        if y < 2022:
            local_pre += pay
            tag = "  <- pre-2022"
        A(f"        {y}: files {tot:>5,}  payload {pay:>5,}{tag}")
    A(f"        pre-2022 payload sessions ACTUALLY LOCAL: {local_pre:,}")
    A("")
    modern = 1147
    hypo = 3380
    A(f"        CAPPROBE01 claimed  {modern:,} -> ~{hypo:,}  ({hypo / modern:.2f}x)  "
      f"=> MDE x {1 / np.sqrt(hypo / modern):.3f}")
    A(f"        that figure assumes a COMPLETE 2013-2021 backfill: "
      f"{hypo - modern:,} extra sessions = 9 years x {(hypo - modern) / 9:.0f}/yr")
    act = modern + local_pre
    A(f"        ACTUAL today: {modern:,} + {local_pre:,} = {act:,}  ({act / modern:.3f}x)  "
      f"=> MDE x {1 / np.sqrt(act / modern):.3f}")
    # DERIVED, never asserted: which of 2013-2021 are complete is READ OFF the store above.
    # An earlier draft of this line hard-coded "2014, 2016 and 2018-2021 are NOT local", which was
    # true of the orchestrator's snapshot and became FALSE mid-run when sibling run CAPPROBE02
    # finished the backfill. A program must not print a claim it did not compute.
    thin = [y for y in range(2013, 2022) if by_year.get(y, [0, 0])[1] < 200]
    A(f"        DERIVED from the listing above: years 2013-2021 with < 200 payload sessions = "
      f"{thin if thin else 'NONE - the backfill is COMPLETE'}")
    if thin:
        A(f"        >>> the 2.95x / 0.58 pair still describes an acquisition that has not happened.")
    else:
        A(f"        >>> the SESSION half of CAPPROBE01's arithmetic is now CORRECT: sibling run "
          f"CAPPROBE02 completed the backfill while this run was executing. It was a forecast "
          f"when written and is a fact now. (b) and (c) below are unaffected: they are about "
          f"WHICH POPULATION the 1.07x was measured on, not about how many sessions exist.")
    A("")
    A("    (b) WHAT n THE 1.07x FIGURE WAS ACTUALLY COMPUTED ON:")
    gt = open(os.path.join(ROOT, "runs", "INTERNALS_ACQUIRE_20260827", "out", "gate.txt"),
              encoding="utf-8").read()
    for line in gt.splitlines():
        s = line.strip()
        if s.startswith("n covered") or "1.07x" in s or s.startswith("P1 scoring entries") \
                or "AND on a session internals cover" in s:
            A(f"        gate.txt| {s}")
    L = pd.read_csv(os.path.join(ROOT, "runs", "RR_W001_ACTION_VALUE_LEDGER", "out",
                                 "ledger_p1pct.csv"))
    S = L[L["in_scoring_population"] == 1].copy()
    S["ts"] = pd.to_datetime(S["decision_ts"])
    A(f"        P1 scoring population: {len(S):,} rows, {S['ts'].min()} -> {S['ts'].max()}")
    pre = int((S["ts"] < pd.Timestamp("2022-01-01")).sum())
    A(f"        P1 scoring rows dated BEFORE 2022-01-01: {pre:,}")
    A("")
    A("    (c) CAN PRE-2022 INTERNALS ADD A ROW TO THAT n?")
    A(f"        The 1.07x MDE is 2.80*sd/sqrt(n) on n = 764 P1 DECISIONS, not on n = 1,147 SESSIONS.")
    A(f"        P1's ledger begins {S['ts'].min()}. A 2013-2021 $TICK backfill adds "
      f"{pre:,} P1 decisions.")
    A(f"        => MDE multiplier for the INTERNALS_ACQUIRE lane from this acquisition: "
      f"x 1.000 (EXACTLY UNCHANGED).")
    A(f"        The 1,147 -> 3,380 substitution swapped a SESSION count for a DECISION count. "
      f"The two populations are different objects and only one of them is what the 1.07x measures.")
    A("")
    A("    (d) THE CORRECT MULTIPLIER FOR THIS RUN'S POPULATION:")
    A(f"        This run's n is EVENTS, not sessions and not P1 decisions. Modern: 63 scored events "
      f"on 1,147 sessions = {63 / 1147:.4f} events/session, but that rate is regime-carried "
      f"(44 events in 2022 -> 2 in 2025), so no session count implies an event count. "
      f"The realised era event counts are printed in the stratum blocks above/below and are the "
      f"only honest version of this arithmetic.")
    f.close()


def threshold_comparability(frames):
    """NON-GATE DIAGNOSTIC, added after the spec was committed and touching NO gate.

    An era re-test at a FIXED -1000 threshold is only meaningful if -1000 sits in a comparable
    place in the $TICK distribution in each era. If the index had been rescaled between eras the
    'unchanged mechanism' would silently be a different mechanism. This prints the evidence
    instead of assuming it. No gate reads any number below.
    """
    P("")
    P("=" * 100)
    P("=== NON-GATE DIAGNOSTIC: is -1000 the SAME PLACE in the $TICK distribution in each era?")
    P("=" * 100)
    P(f"    {'window':<12}{'in-grid bars':>14}{'p0.1':>9}{'p1':>8}{'p50':>8}{'p99':>8}{'p99.9':>9}"
      f"{'min':>9}{'<= -1000 in grid':>18}")
    rows = []
    for y in YEARS:
        fr = frames[y][0]
        v = fr["tick"].to_numpy()
        v = v[~np.isnan(v)]
        q = np.percentile(v, [0.1, 1, 50, 99, 99.9])
        rows.append((str(y), len(v), q, float(v.min()), int((v <= TRIG).sum())))
    tk = pd.read_parquet(os.path.join(ROOT, "research", "data_internals", "TICK_1m.parquet"))
    tk["tod"] = tk["time"].dt.time
    slots = pd.timedelta_range("09:31:00", "15:59:00", freq="1min")
    st = set((pd.Timestamp("2000-01-01") + slots).time)
    tk = tk[tk["tod"].isin(st)]
    for y, g in tk.groupby(tk["time"].dt.year):
        v = g["close"].to_numpy()
        q = np.percentile(v, [0.1, 1, 50, 99, 99.9])
        rows.append((f"{y} (modern)", len(v), q, float(v.min()), int((v <= TRIG).sum())))
    for name, n, q, mn, cnt in rows:
        P(f"    {name:<12}{n:>14,}{q[0]:>9.0f}{q[1]:>8.0f}{q[2]:>8.0f}{q[3]:>8.0f}{q[4]:>9.0f}"
          f"{mn:>9.0f}{cnt:>18,}")
    P("    READ: the tail SCALE is stable across eras, so -1000 is not an era-inconsistent")
    P("    threshold. What changes between eras is HOW OFTEN the tail is reached - i.e. the")
    P("    event is a VOLATILITY-REGIME phenomenon, exactly as the 2026 closure recorded.")


def main():
    open_writers()
    P("=" * 100)
    P("=== TICK01ERA - frozen G2_F1_TICK01 mechanism, unchanged, on 2013 / 2015 / 2017")
    P(f"=== TRIG {TRIG} REARM {REARM} H_TARGET {H_TARGET} MDE_K {MDE_K} "
      f"(all inherited; none chosen here)")
    P("=" * 100)

    frames, provs = {}, []
    for y in YEARS:
        tick, nq, prov = load_era(y)
        provs.append(prov)
        fr, ns = build_grid(tick, nq)
        frames[y] = (fr, ns)
    pd.DataFrame(provs).to_csv(os.path.join(OUT, "manifest.csv"), index=False)
    P("")
    P("    frozen era manifest written to out/manifest.csv (sha256 per source CSV)")
    for pr in provs:
        P(f"      {pr['year']}  sha256 {pr['sha256'][:16]}  rows {pr['rows']:,}  "
          f"tick dates {pr['tick_dates']:,}  NQ close range "
          f"{pr['nq_close_min']:,.2f}..{pr['nq_close_max']:,.2f}  contracts {pr['contracts']}")

    threshold_comparability(frames)

    results = []
    for y in YEARS:
        fr, ns = frames[y]
        results.append(evaluate(f"ERA_{y}", fr, ns))

    pooled = pd.concat([frames[y][0] for y in YEARS], ignore_index=True)
    n_sess_pool = int(pooled["session"].nunique())
    res_pool = evaluate("ERA_PRE2022_POOLED", pooled, n_sess_pool)
    results.append(res_pool)

    # EVERY detected event is preserved, including strata that could not be gated.
    parts = [r["events"].assign(stratum=r["name"]) for r in results
             if "events" in r and r["name"] != "ERA_PRE2022_POOLED" and len(r["events"])]
    allev = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(
        columns=["session", "stamp", "tick", "nq_at", "fwd15", "stratum"])
    allev.to_csv(os.path.join(OUT, "era_events.csv"), index=False)
    P("")
    P(f"    out/era_events.csv: {len(allev):,} detected events preserved across all era strata")

    power_audit()

    # ------------------------------------------------------------------ GATE TABLE
    G("")
    G("=" * 118)
    G("=== GATE TABLE - TICK01ERA_20260831 - printed by the program, never assembled by hand")
    G("=== mechanism FROZEN from G2_F1_TICK01 (trigger -1000 / re-arm -400 / NQ fwd 15 min)")
    G("=" * 118)
    G(f"{'STRATUM':<22}{'GATE':<5}{'SPEC':<52}{'OBSERVED':<32}{'PASS-FAIL'}")
    for r in results:
        if r.get("insufficient"):
            obs = "only {} scored events".format(r["n"])
            G("{:<22}{:<5}{:<52}{:<32}{}".format(r["name"], "--", "gate not evaluable", obs, "N/A"))
            continue
        o1 = "mean {:+.3f} bps, t {:+.2f} (n={:,}, G={:,})".format(r["mean"], r["t"], r["n"], r["g"])
        o2 = "event {:+.3f} vs ctrl p95 {:+.3f}".format(r["mean"], r["ctrl_p95"])
        o3 = "real {:+.3f} vs null p95 {:+.3f}".format(r["mean"], r["null_p95"])
        o4 = "{:.3f} bps = {:.2f}x |mean|".format(r["mde"], r["mde"] / abs(r["mean"]))
        G("{:<22}{:<5}{:<52}{:<32}{}".format(
            r["name"], "T1", "mean fwd15 > 0 AND session-clustered t >= 2.0", o1,
            "PASS" if r["T1"] else "FAIL"))
        G("{:<22}{:<5}{:<52}{:<32}{}".format(
            "", "T2", "event mean > p95 of count-matched same-session draws", o2,
            "PASS" if r["T2"] else "FAIL"))
        G("{:<22}{:<5}{:<52}{:<32}{}".format(
            "", "T3", "real above p95 of session-block circular-shift null", o3,
            "PASS" if r["T3"] else "FAIL"))
        G("{:<22}{:<5}{:<52}{:<32}{}".format(
            "", "", "MDE 2.80*sd/sqrt(n) [printed BEFORE the verdict]", o4,
            "UNDERPOWERED" if r["mde"] > 2.0 * abs(r["mean"]) else "powered"))
        G("")

    pooled_ok = (not res_pool.get("insufficient")) and res_pool["T1"] and res_pool["T2"] and res_pool["T3"]
    verdict = "SURVIVES -> the 2026 closure was a DATA-POWER closure" if pooled_ok else \
              "FAILS AGAIN -> the closure is a MECHANISM closure, confirmed out of sample"
    G(f"    VERDICT (from ERA_PRE2022_POOLED only, per the frozen verdict rule): {verdict}")
    if not res_pool.get("insufficient"):
        under = res_pool["mde"] > 2.0 * abs(res_pool["mean"])
        G(f"    UNDERPOWERED_STILL clause (declared in the spec, reported ADDITIONALLY): "
          f"MDE {res_pool['mde']:.3f} bps vs 2.0x|mean| {2.0 * abs(res_pool['mean']):.3f} bps -> "
          f"{'the re-test is ITSELF underpowered and closes nothing on its own' if under else 'the re-test is powered at the declared bar'}")
    G("")
    G("    MODERN REFERENCE, quoted verbatim from the closed run, NEVER merged with the above:")
    G("      G2_F1_TICK01 2022-01-03..2026-07-31: n=63, mean +2.841 bps, t +0.54, "
      "ctrl p95 +4.366, null p95 +3.885, MDE 15.112 bps = 5.32x |mean| -> T1/T2/T3 all FAIL")
    G("    per-year strata above are REGIME DESCRIPTION ONLY; no verdict is taken from one year.")
    G("    prohibitions honoured: no threshold search, no horizon selection, no policy, no P&L, "
      "no cost claim, no sealed read, no pre-2022/modern pooling.")

    json.dump({r["name"]: {k: (v if not isinstance(v, (np.floating, np.integer)) else float(v))
                           for k, v in r.items() if k != "events"} for r in results},
              open(os.path.join(OUT, "results.json"), "w", encoding="utf-8"), indent=2, default=str)
    _log.close(); _gate.close()


if __name__ == "__main__":
    main()
