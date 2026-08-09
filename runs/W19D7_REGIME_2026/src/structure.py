"""W19D7 step 2 — D1 effective ensemble diversity, the clamp binding rate, and the
incumbent-versus-challenger decomposition.

Per the frozen spec §4, D1 uses member POSITIONS (strategy state) and that is deliberate and
non-circular: it asks a structural question whose answer is not defined in terms of profit. No
P&L enters D1. The clamp binding rate is labelled SEMI-STRATEGY wherever it appears and is
excluded from panel.py's changepoint panel and analog search.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
import common as C1

RUN = os.path.join(ROOT, "runs", "W19D7_REGIME_2026")
OUT = os.path.join(RUN, "out")
DEV_END = pd.Timestamp("2026-05-29").date()
MARKET_BREAK = pd.Timestamp("2024-07-09")   # from panel.py PC1; read from boundary.json
STUB = pd.Timestamp("2026-01-02")           # calendar convention, NOT a finding

bnd = json.load(open(os.path.join(OUT, "boundary.json")))
MARKET_BREAK = pd.Timestamp(bnd["boundary"])
print(f"market break from panel.py: {MARKET_BREAK.date()} "
      f"(convention={bnd['boundary_is_convention']})", flush=True)

bars = C1.load_dev_bars()
sigma = sm.sigma_series(bars["close"].to_numpy())
sess = pd.to_datetime(bars["sess_date"])
year = sess.dt.year.to_numpy()

# ---------------------------------------------------------------- D1 + clamp binding
POS, FLIPS, SEFF = [], [], []
for vm in C1.INCUMBENT_VMS:
    is_up, flip, s_eff, anchor = sm.member_states(bars["close"].to_numpy(), sigma, float(vm))
    fills, pos, pend = sm.member_trades(bars, is_up, flip, s_eff, anchor)
    POS.append(pos); FLIPS.append(flip); SEFF.append(s_eff)
POS = np.column_stack(POS).astype(float)
FLIPS = np.column_stack(FLIPS)
SEFF = np.column_stack(SEFF)
CEIL = 1200 * 0.25
pinned = SEFF >= CEIL - 1e-9
tgt = sm.e10_target(np.column_stack([sm.member_trades(
    bars, *sm.member_states(bars["close"].to_numpy(), sigma, float(vm)))[2]
    for vm in C1.INCUMBENT_VMS]))


def participation_ratio(X):
    """(sum lambda)^2 / sum lambda^2 on the eigenvalues of the member-position correlation
    matrix. 13 = fully diverse, 1 = fully collapsed."""
    X = X[:, np.std(X, axis=0) > 0]
    if X.shape[1] < 2:
        return 1.0
    R = np.corrcoef(X, rowvar=False)
    R = np.nan_to_num(R, nan=0.0)
    ev = np.linalg.eigvalsh(R)
    ev = np.clip(ev, 0, None)
    return float(ev.sum() ** 2 / (ev ** 2).sum())


def d1_row(label, mask):
    P = POS[mask]
    sgn = np.sign(P)
    nz = (sgn != 0).all(axis=1)
    allagree = float((np.abs(sgn[nz].sum(axis=1)) == P.shape[1]).mean()) if nz.sum() else np.nan
    return {"period": label, "n_bars": int(mask.sum()),
            "effective_members_participation_ratio": participation_ratio(P),
            "frac_bars_all13_nonzero": float(nz.mean()),
            "frac_all13_agree_given_all_nonzero": allagree,
            "clamp_pinned_member_bars_pct_SEMI_STRATEGY": float(pinned[mask].mean() * 100),
            "mean_abs_target": float(np.abs(tgt[mask]).mean()),
            "frac_target_at_pm10_cap": float((np.abs(tgt[mask]) >= 10).mean()),
            "mean_member_flips_per_1000_bars": float((FLIPS[mask] != 0).sum() /
                                                     max(1, mask.sum()) / 13 * 1000)}


rows = [d1_row(str(y), year == y) for y in sorted(set(year))]
rows.append(d1_row(f"BEFORE {MARKET_BREAK.date()}", (sess < MARKET_BREAK).to_numpy()))
rows.append(d1_row(f"AFTER {MARKET_BREAK.date()}", (sess >= MARKET_BREAK).to_numpy()))
rows.append(d1_row(f"STUB {STUB.date()}+ (convention)", (sess >= STUB).to_numpy()))
D1 = pd.DataFrame(rows)
D1.to_csv(os.path.join(OUT, "d1_diversity.csv"), index=False)
print("\n=== D1 EFFECTIVE ENSEMBLE DIVERSITY ===")
print(D1.round(4).to_string(index=False), flush=True)

# ---------------------------------------------------------------- incumbent decomposition
def daily_from_fills(path, point_value, comm_col="commission"):
    """Strategy is flat at every session close, so realised daily P&L is exact from fills."""
    f = pd.read_csv(path, comment="#")
    f["time"] = pd.to_datetime(f["time"])
    SIGN = {"Buy": +1, "BuyToCover": +1, "Sell": -1, "SellShort": -1}
    s = f["order_action"].map(SIGN)
    if s.isna().any():
        raise ValueError(f"unmapped order_action in {path}: "
                         f"{sorted(set(f.loc[s.isna(),'order_action']))}")
    cash = -(s * f["price"] * f["qty"] * point_value) - f[comm_col].fillna(0.0)
    # session date = the trading date whose 18:00 open began the session
    sd = f["time"].dt.date
    roll = f["time"].dt.hour >= 18
    sd = np.where(roll, (f["time"] + pd.Timedelta(days=1)).dt.date, sd)
    out = pd.DataFrame({"sess": pd.to_datetime(sd), "net": cash}).groupby("sess")["net"].sum()
    return out


curves = {}
curves["E10_SOLAR_leg"] = pd.read_csv(
    os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "out", "daily_control.csv")
).assign(sess=lambda d: pd.to_datetime(d["sess"])).set_index("sess")["net"]
try:
    curves["ProductA_v3"] = daily_from_fills(
        os.path.join(ROOT, "runs", "W18E_PRODUCTA_C4", "out", "smm_v3_fills.csv"), 2.0)
except Exception as e:
    print("ProductA_v3 curve unavailable:", e, flush=True)
try:
    curves["BEST_ONE_NQ_v4"] = daily_from_fills(
        os.path.join(ROOT, "runs", "W17B_C4_WATCHDOG", "out", "nq_v4_fills.csv"), 20.0)
except Exception as e:
    print("BEST_ONE_NQ_v4 curve unavailable:", e, flush=True)

# curves_all.csv was written from a dict with mixed 2- and 3-tuple keys, so it has a 3-row
# header and a stray index-name row. Read it structurally rather than guessing a format.
xi = pd.read_csv(os.path.join(ROOT, "runs", "W18R2_M5_XINST", "out", "curves_all.csv"),
                 header=[0, 1, 2], index_col=0)
xi = xi[xi.index.notna()]
xi = xi[~xi.index.astype(str).str.startswith("sess")]
xi.index = pd.to_datetime(xi.index, format="%Y-%m-%d", errors="coerce")
xi = xi[xi.index.notna()].astype(float)
# keep only the commissioned legs (third header level == 'nan'), drop the nocomm duplicates
keep = {(a, b): (a, b, c) for (a, b, c) in xi.columns if str(c).lower() in ("nan", "")}
for inst in ("ES", "RTY", "YM"):
    if (inst, "CONTROL") in keep:
        curves[f"{inst}_CONTROL"] = xi[keep[(inst, "CONTROL")]].dropna()
print("cross-instrument curves loaded:", sorted(k for k in keep), flush=True)


def stats(x):
    x = np.asarray(x, dtype=float)
    if len(x) < 5:
        return {}
    eq = np.cumsum(x); dd = np.maximum.accumulate(eq) - eq
    k = max(1, int(0.05 * len(x)))
    sd = x.std(ddof=1)
    return {"n": len(x), "net": float(x.sum()),
            "sharpe": float(x.mean() / sd * np.sqrt(252)) if sd > 0 else np.nan,
            "CDaR_0.95": float(np.sort(dd)[::-1][:k].mean())}


dec = []
for name, s in curves.items():
    s = s[s.index <= pd.Timestamp(DEV_END)]
    for y in sorted(set(s.index.year)):
        dec.append({"object": name, "split": f"year {y}", **stats(s[s.index.year == y])})
    dec.append({"object": name, "split": f"BEFORE {MARKET_BREAK.date()}",
                **stats(s[s.index < MARKET_BREAK])})
    dec.append({"object": name, "split": f"AFTER {MARKET_BREAK.date()}",
                **stats(s[s.index >= MARKET_BREAK])})
    dec.append({"object": name, "split": f"STUB {STUB.date()}+ (convention)",
                **stats(s[s.index >= STUB])})
DEC = pd.DataFrame(dec)
DEC.to_csv(os.path.join(OUT, "incumbent_decomposition.csv"), index=False)
print("\n=== INCUMBENT DECOMPOSITION (is the incumbent itself degraded?) ===")
print(DEC.round(4).to_string(index=False), flush=True)

# --------------------------------- challenger-minus-incumbent, in and out of the stub
diffs = {}
m1c = pd.read_csv(os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "out",
                               "daily_arm_FULL.csv")).assign(
    sess=lambda d: pd.to_datetime(d["sess"])).set_index("sess")["net"]
diffs["M1_arm_FULL_minus_control"] = m1c - curves["E10_SOLAR_leg"]
for inst in ("NQ", "ES", "RTY", "YM"):
    kb, kc = keep.get((inst, "BLEND75")), keep.get((inst, "CONTROL"))
    if kb is None or kc is None:
        continue
    b = xi[kb].dropna(); c = xi[kc].dropna()
    cal = b.index.intersection(c.index)
    diffs[f"M5_{inst}_blend_minus_control"] = b.reindex(cal) - c.reindex(cal)
dd = []
for name, s in diffs.items():
    s = s[s.index <= pd.Timestamp(DEV_END)]
    tot = s.sum()
    stub = s[s.index >= STUB].sum()
    dd.append({"comparison": name, "total_diff": float(tot),
               "diff_in_stub": float(stub),
               "stub_share_of_total": float(stub / tot) if tot != 0 else np.nan,
               "diff_before_break": float(s[s.index < MARKET_BREAK].sum()),
               "diff_after_break_excl_stub": float(
                   s[(s.index >= MARKET_BREAK) & (s.index < STUB)].sum())})
DD = pd.DataFrame(dd)
DD.to_csv(os.path.join(OUT, "challenger_diff_decomposition.csv"), index=False)
print("\n=== CHALLENGER MINUS INCUMBENT, BY SPLIT ===")
print(DD.round(2).to_string(index=False), flush=True)
print("\nstructure done", flush=True)
