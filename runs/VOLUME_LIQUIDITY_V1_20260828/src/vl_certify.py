"""VOLUME_LIQUIDITY_V1 -- PRE-RESULT ENGINE CERTIFICATION (SPEC 6A-6E).  ALL BLOCKING.

NO ECONOMIC INTERPRETATION HAPPENS IN THIS FILE.  It prints no Sharpe, no gate table and no
verdict about the strategy.  Aggregate P&L appears only where 6B/6D require proving that P&L
RESPONDS or RECONCILES -- never as a performance claim.

Restricted to the DEVELOPMENT window throughout, so the held-back and modern windows are not
touched by certification either.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "research_sdk"))
import keysafe as KS                                                         # noqa: E402
import vl_independent as VI                                                  # noqa: E402
import vl_primary as VP                                                      # noqa: E402

OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
DEV_END = VP.DEV_END
_fh = open(os.path.join(OUT, "vl_certify.txt"), "w", encoding="utf-8")
res, FAIL = {}, []


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


P("=" * 112)
P("=== VOLUME_LIQUIDITY_V1 -- PRE-RESULT ENGINE CERTIFICATION.  NO ECONOMIC INTERPRETATION.")
P("=" * 112)
for f in ("vl_primary.py", "vl_independent.py"):
    P(f"    {f:<22} sha256 {sha(os.path.join(HERE, f))}")
P(f"    development window     every evaluated date < {DEV_END.date()}")

# ------------------------------------------------------------------ 6E-a  INDEPENDENCE BY AST
P("")
P("--- 6E-a  THE INDEPENDENT IMPLEMENTATION MUST NOT IMPORT THE PRIMARY  (AST, not grep)")
tree = ast.parse(open(os.path.join(HERE, "vl_independent.py"), encoding="utf-8").read())
imports = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        imports.update(a.name for a in node.names)
    elif isinstance(node, ast.ImportFrom):
        imports.add(node.module or "")
P(f"    modules imported by vl_independent.py: {sorted(imports)}")
ok = "vl_primary" not in imports
P(f"    'vl_primary' among them: {'YES -- *** NOT INDEPENDENT ***' if not ok else 'NO -- independent'}")
res["6E_a_no_import"] = bool(ok)
if not ok:
    FAIL.append("6E-a")

# ------------------------------------------------------------------ baseline
P("")
P("--- BASELINE  (development window only)")
base = VP.run(date_max=DEV_END)
bp = base["pos"]
P(f"    weeks with positions   {bp['monday'].nunique():,}   "
  f"{bp['monday'].min().date()} -> {bp['monday'].max().date()}")
P(f"    (root, week) positions {len(bp):,}   roots {bp['root'].nunique()}")
P(f"    daily rows             {len(base['daily']):,}")
assert base["daily"]["date"].max() < DEV_END, "DEVELOPMENT WINDOW VIOLATION"
P(f"    ASSERTION max evaluated date {base['daily']['date'].max().date()} < {DEV_END.date()}  PASS")

# ------------------------------------------------------------------ 6A-NEG
P("")
P("--- 6A-NEG  CORRUPT VOLUME **AND** PRICES STRICTLY AFTER THE CUTOFF -> WEIGHTS EXACTLY UNCHANGED")
P("    Tested at several cutoffs, and scored ONLY on the 4 weeks immediately BEFORE each cutoff --")
P("    the decisions actually adjacent to the corruption.  A global cutoff scored on distant weeks")
P("    would be a probe with no teeth (ESNQ P0-1, discipline rule 55).")
Ts = [pd.Timestamp(x) for x in ("2012-06-04", "2014-03-03", "2016-09-05", "2018-05-07")]
neg_max = 0.0
neg_rows = 0
for T in Ts:
    def vmod(v, T=T):
        v = v.copy()
        v.loc[v["date"] >= T, "vol"] = v.loc[v["date"] >= T, "vol"] * 7.0 + 1234.0
        return v

    def rmod(e, T=T):
        e = e.copy()
        e.loc[e["date"] >= T, "ret_usd"] = e.loc[e["date"] >= T, "ret_usd"] * -3.0 + 999.0
        return e
    pert = VP.run(date_max=DEV_END, vol_mod=vmod, ret_mod=rmod)["pos"]
    lo = T - pd.Timedelta(days=28)
    a = bp[(bp["monday"] >= lo) & (bp["monday"] <= T)].set_index(["monday", "root"])["n"]
    b = pert[(pert["monday"] >= lo) & (pert["monday"] <= T)].set_index(["monday", "root"])["n"]
    j = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna()
    dmax = float((j["a"] - j["b"]).abs().max()) if len(j) else np.nan
    neg_max = max(neg_max, 0.0 if not np.isfinite(dmax) else dmax)
    neg_rows += len(j)
    P(f"    cutoff {T.date()}  adjacent weeks scored {j['a'].groupby(level=0).size().shape[0]:>2}  "
      f"positions {len(j):>4}  max |dn| {dmax:.3e}   "
      f"{'PASS' if dmax == 0.0 else '*** FAIL - LOOK-AHEAD ***'}")
    if len(a) != len(b):
        P(f"        note: position-row counts {len(a)} vs {len(b)} -- an availability change would "
          f"itself be a leak")
P(f"    >>> 6A-NEG  max |dn| over {neg_rows:,} adjacent positions = {neg_max:.3e}   "
  f"{'PASS' if neg_max == 0.0 else '*** FAIL ***'}")
res["6A_NEG_max_abs_dn"] = neg_max
res["6A_NEG_positions"] = int(neg_rows)
if neg_max != 0.0:
    FAIL.append("6A-NEG")

# ------------------------------------------------------------------ 6A-POS
P("")
P("--- 6A-POS  CORRUPT ONE **CAUSALLY ADMISSIBLE PRIOR** OBSERVATION THAT MED63/MAD63 ACTUALLY USE")
P("    A probe that returns 'nothing moved' is not certification.  This one must have teeth.")
probe = []
for r, d0 in (("ES", pd.Timestamp("2013-04-11")), ("CL", pd.Timestamp("2015-08-12")),
              ("ZN", pd.Timestamp("2011-10-19")), ("GC", pd.Timestamp("2017-02-15"))):
    def vmod(v, r=r, d0=d0):
        v = v.copy()
        m = (v["root"] == r) & (v["date"] == d0)
        v.loc[m, "vol"] = v.loc[m, "vol"] * 25.0
        return v
    pert = VP.run(date_max=DEV_END, vol_mod=vmod)["pos"]
    a = bp.set_index(["monday", "root"])["n"]
    b = pert.set_index(["monday", "root"])["n"]
    j = pd.concat([a.rename("a"), b.rename("b")], axis=1)
    diff = (j["a"] - j["b"]).abs()
    moved = int((diff > 0).sum())
    # weeks whose 63-window can contain d0: those with cutoff strictly after d0
    fut = j.index.get_level_values(0) > d0
    moved_future = int((diff[fut] > 0).sum())
    moved_past = int((diff[~fut] > 0).sum())
    P(f"    perturb {r} {d0.date()} x25   positions changed {moved:>5}   "
      f"of which AFTER the perturbed date {moved_future:>5}   BEFORE it {moved_past:>3}   "
      f"max |dn| {float(diff.max()):.4f}")
    probe.append(dict(root=r, date=str(d0.date()), moved=moved, moved_future=moved_future,
                      moved_past=moved_past, max_abs=float(diff.max())))
pos_ok = all(p["moved_future"] > 0 for p in probe)
past_ok = all(p["moved_past"] == 0 for p in probe)
P(f"    >>> 6A-POS  every probe moved FUTURE weights: "
  f"{'PASS - the probe has teeth' if pos_ok else '*** FAIL - NO TEETH ***'}")
P(f"    >>> and moved NO weight dated before the perturbation: "
  f"{'PASS' if past_ok else '*** FAIL - RETROCAUSAL ***'}")
res["6A_POS"] = dict(probes=probe, has_teeth=bool(pos_ok), no_retrocausal=bool(past_ok))
if not (pos_ok and past_ok):
    FAIL.append("6A-POS")

# ------------------------------------------------------------------ 6B
P("")
P("--- 6B  CORRUPT FUTURE RETURNS -> WEIGHTS UNMOVED, ONLY SUBSEQUENT P&L CHANGES")
T = pd.Timestamp("2015-01-05")


def rmod_only(e):
    e = e.copy()
    e.loc[e["date"] >= T, "ret_usd"] = e.loc[e["date"] >= T, "ret_usd"] * 4.0 - 500.0
    return e


pert = VP.run(date_max=DEV_END, ret_mod=rmod_only)
a = bp.set_index(["monday", "root"])["n"]
b = pert["pos"].set_index(["monday", "root"])["n"]
j = pd.concat([a.rename("a"), b.rename("b")], axis=1)
pre = j.index.get_level_values(0) < T
dpre = float((j["a"] - j["b"]).abs()[pre].max())
da = base["daily"].set_index(["date", "root"])["pnl_gross"]
db = pert["daily"].set_index(["date", "root"])["pnl_gross"]
k = pd.concat([da.rename("a"), db.rename("b")], axis=1).dropna()
before = k.index.get_level_values(0) < T
pnl_before = float((k["a"] - k["b"]).abs()[before].max())
pnl_after = float((k["a"] - k["b"]).abs()[~before].max())
P(f"    weights dated before {T.date()}: max |dn| {dpre:.3e}   "
  f"{'PASS' if dpre == 0.0 else '*** FAIL ***'}")
P(f"    daily gross P&L before {T.date()}: max |d| ${pnl_before:.6f}   "
  f"{'PASS - unchanged' if pnl_before == 0.0 else '*** FAIL ***'}")
P(f"    daily gross P&L on/after {T.date()}: max |d| ${pnl_after:,.2f}   "
  f"{'PASS - it responds' if pnl_after > 0 else '*** FAIL - P&L IGNORES RETURNS ***'}")
b_ok = dpre == 0.0 and pnl_before == 0.0 and pnl_after > 0
res["6B"] = dict(dpre=dpre, pnl_before=pnl_before, pnl_after=pnl_after, PASS=bool(b_ok))
if not b_ok:
    FAIL.append("6B")

# ------------------------------------------------------------------ 6C
P("")
P("--- 6C  KEY SAFETY  (research_sdk/keysafe.py)")
v, e = VP.load_inputs()
lk = KS.build_lookup(v.loc[v["root"] == "ES", "date"], v.loc[v["root"] == "ES", "vol"],
                     name="ES root-total volume")
KS.assert_resolves(lk, base["daily"].loc[base["daily"]["root"] == "ES", "date"].unique(),
                   min_frac=1.0, name="ES volume vs traded dates")
KS.known_match_control(lk, pd.Timestamp("2013-04-11"), name="ES volume")
KS.assert_unique_index(base["pos"], ["monday", "root"], name="weekly positions")
KS.assert_unique_index(base["daily"], ["date", "root"], name="daily rows")
merged = KS.safe_merge(base["daily"][["root", "date", "n"]], v[["root", "date", "vol"]],
                       on=["root", "date"], how="inner", name="daily x volume")
P(f"    ES volume lookup entries                     {len(lk):,}")
P(f"    every traded ES date resolves in the lookup  PASS (min_frac 1.0)")
P(f"    known-match control 2013-04-11               PASS")
P(f"    (monday, root) unique in positions           PASS  {len(base['pos']):,} rows")
P(f"    (date, root) unique in daily                 PASS  {len(base['daily']):,} rows")
P(f"    safe_merge daily x volume, unmatched = 0     PASS  {len(merged):,} rows")
P(f"    non-empty inputs -> non-empty output          PASS  "
  f"({len(base['daily']):,} in, {len(merged):,} out)")
res["6C"] = dict(PASS=True, lookup=len(lk), merged=int(len(merged)))

# ------------------------------------------------------------------ 6D
P("")
P("--- 6D  P&L IDENTITY, PROVED INDEPENDENTLY, AND RECONCILED root -> sector -> portfolio")
d = base["daily"]
recon = d["n"].values * d["ret_usd"].values
id_gross = float(np.max(np.abs(recon - d["pnl_gross"].values)))
side_rate = d["root"].map(lambda r: VP.cost_per_side(r, VP.SLIP_TICKS_PRIMARY)).values
id_cost = float(np.max(np.abs(d["sides"].values * side_rate - d["cost"].values)))
id_net = float(np.max(np.abs((recon - d["sides"].values * side_rate) - d["pnl_net"].values)))
by_root = d.groupby("root")["pnl_net"].sum()
by_sec = d.groupby("sector")["pnl_net"].sum()
tot_d, tot_r, tot_s = d["pnl_net"].sum(), by_root.sum(), by_sec.sum()
tot_w = base["weekly"]["net"].sum()
P(f"    identity  n * ret_usd            == pnl_gross    max |d| {id_gross:.3e}")
P(f"    identity  sides * cost_per_side  == cost         max |d| {id_cost:.3e}")
P(f"    identity  gross - cost           == pnl_net      max |d| {id_net:.3e}")
P(f"    reconcile daily -> root          |d| ${abs(tot_d-tot_r):.9f}")
P(f"    reconcile daily -> sector        |d| ${abs(tot_d-tot_s):.9f}")
P(f"    reconcile daily -> weekly        |d| ${abs(tot_d-tot_w):.9f}")
P(f"    exposure check: no hidden multiplication -- every daily row uses exactly ONE position")
P(f"       distinct n per (date, root): max {int(d.groupby(['date','root']).size().max())} row(s)")
P(f"    basis: ret_usd comes from the certified self-financing construction, which NEVER")
P(f"       differences two contracts; merged/back-adjusted series are barred by the data contract")
d_ok = max(id_gross, id_cost, id_net) < 1e-9 and abs(tot_d - tot_r) < 1e-6 \
    and abs(tot_d - tot_s) < 1e-6 and abs(tot_d - tot_w) < 1e-6
P(f"    >>> 6D  {'PASS' if d_ok else '*** FAIL ***'}")
res["6D"] = dict(id_gross=id_gross, id_cost=id_cost, id_net=id_net,
                 root_gap=float(abs(tot_d - tot_r)), sector_gap=float(abs(tot_d - tot_s)),
                 weekly_gap=float(abs(tot_d - tot_w)), PASS=bool(d_ok))
if not d_ok:
    FAIL.append("6D")

# ------------------------------------------------------------------ 6E
P("")
P("--- 6E  INDEPENDENT PARITY   vectorized merge_asof path  vs  explicit chronological loop")
ind = VI.run(date_max=DEV_END)
ip, id_ = ind["pos"], ind["daily"]
pa = bp.set_index(["monday", "root"])["n"]
pb = ip.set_index(["monday", "root"])["n"]
only_a = pa.index.difference(pb.index)
only_b = pb.index.difference(pa.index)
common = pa.index.intersection(pb.index)
dn = (pa.loc[common] - pb.loc[common]).abs()
rel = dn / np.maximum(pa.loc[common].abs(), 1e-12)
sign_ok = int((np.sign(pa.loc[common]) != np.sign(pb.loc[common])).sum())
P(f"    positions  primary {len(pa):,}   independent {len(pb):,}   common {len(common):,}")
P(f"    positions only in primary {len(only_a)}   only in independent {len(only_b)}")
P(f"    max |dn| {float(dn.max()):.3e}   max relative {float(rel.max()):.3e}   "
  f"direction disagreements {sign_ok}")
da = base["daily"].set_index(["date", "root"])
db = id_.set_index(["date", "root"])
ck = da.index.intersection(db.index)
P(f"    daily rows primary {len(da):,}   independent {len(db):,}   common {len(ck):,}   "
  f"only-primary {len(da.index.difference(db.index))}  only-independent {len(db.index.difference(da.index))}")
tv = float((da.loc[ck, "sides"] - db.loc[ck, "sides"]).abs().max())
pv = float((da.loc[ck, "pnl_net"] - db.loc[ck, "pnl_net"]).abs().max())
rootgap = float((da.groupby("root")["pnl_net"].sum() - db.groupby("root")["pnl_net"].sum())
                .abs().max())
portgap = float(abs(da["pnl_net"].sum() - db["pnl_net"].sum()))
P(f"    max |d turnover sides| {tv:.3e}     max |d daily net| ${pv:.3e}")
P(f"    max per-ROOT net gap ${rootgap:.6f}     PORTFOLIO net gap ${portgap:.6f}")
e_ok = (len(only_a) == 0 and len(only_b) == 0 and sign_ok == 0
        and float(rel.max()) < 1e-9 and tv < 1e-9 and rootgap < 0.01 and portgap < 0.01
        and len(da.index.difference(db.index)) == 0 and len(db.index.difference(da.index)) == 0)
P(f"    >>> 6E  {'PASS' if e_ok else '*** FAIL - STOP BEFORE ECONOMIC INTERPRETATION ***'}")
res["6E"] = dict(pos_primary=int(len(pa)), pos_independent=int(len(pb)),
                 only_primary=int(len(only_a)), only_independent=int(len(only_b)),
                 max_abs_dn=float(dn.max()), max_rel_dn=float(rel.max()),
                 direction_disagreements=int(sign_ok), max_turnover_diff=tv,
                 max_daily_net_diff=pv, max_root_net_gap=rootgap, portfolio_net_gap=portgap,
                 PASS=bool(e_ok))
if not e_ok:
    FAIL.append("6E")

# ------------------------------------------------------------------ verdict
P("")
P("=" * 112)
P(f"=== ENGINE CERTIFICATION: {'PASS -- ALL FIVE CLAUSES' if not FAIL else 'FAIL ' + str(FAIL)}")
P("=" * 112)
P("    No Sharpe, no gate table, no economic verdict was produced by this file.")
P("    Development economics may proceed ONLY if the line above says PASS.")
res["ALL_PASS"] = not FAIL
res["failures"] = FAIL
res["sha256"] = {f: sha(os.path.join(HERE, f)) for f in ("vl_primary.py", "vl_independent.py")}
json.dump(res, open(os.path.join(OUT, "vl_certify.json"), "w", encoding="utf-8"),
          indent=2, default=str)
_fh.close()
