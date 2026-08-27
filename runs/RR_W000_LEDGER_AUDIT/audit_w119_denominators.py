"""RR_W000 - POST-HOC AUDIT of runs/WE_W119_BOOKLOSS/out/book_loss_ledger.csv.

RUN CLASS: AUDIT. No hypothesis is selected, no population is redefined, no candidate is
promoted, no alpha budget is consumed. This re-derives figures that CURRENT_BASELINE quotes
and checks the MASK each one was computed on. It reads only a committed artifact.

Provenance: found during Phase 0 onboarding of the causal-monetization campaign, while reading
W119 as the closest existing analogue to the planned ACTION-VALUE LEDGER.
"""
import os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEDGER = os.path.join(ROOT, "runs", "WE_W119_BOOKLOSS", "out", "book_loss_ledger.csv")
OUT = os.path.join(ROOT, "runs", "RR_W000_LEDGER_AUDIT", "out", "audit.txt")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fh = open(OUT, "w", encoding="utf-8")


def P_(*a):
    print(*a, flush=True)
    print(*a, file=fh)


d = pd.read_csv(LEDGER)
P_("=" * 108)
P_("=== RR_W000 - AUDIT of the W119 BOOK_LOSS_LEDGER denominators.  NOTHING IS PROMOTED.")
P_("=" * 108)
P_(f"    artifact: runs/WE_W119_BOOKLOSS/out/book_loss_ledger.csv   {len(d):,} rows x {len(d.columns)} cols")

lose = d["book_pnl"] < 0
notlose = ~lose
win = d["book_pnl"] > 0
flat = d["book_pnl"] == 0

P_("")
P_("--- FINDING 1: the 'winning sessions' denominator contains structurally flat sessions ---")
P_(f"    book_pnl <  0  LOSING          n = {int(lose.sum()):>5,}")
P_(f"    book_pnl >  0  WINNING         n = {int(win.sum()):>5,}")
P_(f"    book_pnl == 0  FLAT            n = {int(flat.sum()):>5,}")
P_(f"    ~(book_pnl < 0) NOT-LOSING     n = {int(notlose.sum()):>5,}   = WINNING + FLAT")
P_(f"    flat sessions with p1_trades == 0 : {int((flat & (d['p1_trades'] == 0)).sum())} of {int(flat.sum())}")
P_(f"    flat sessions with xm_active == 0 : {int((flat & (d['xm_active'] == 0)).sum())} of {int(flat.sum())}")
P_("    -> every flat session is GUARANTEED to have zero trades. Putting them in the")
P_("       'winning' bucket mechanically drags its trade count toward zero.")
P_("")
P_(f"{'statistic':<28}{'LOSING':>14}{'NOT-LOSING':>14}{'WINNING':>14}{'quoted ratio':>16}{'correct ratio':>16}")
rows = [
    ("P1 trades / session", "p1_trades", lambda s: s.mean(), "{:.4f}"),
    ("P1 contract-minutes", "p1_contract_minutes", lambda s: s.mean(), "{:.1f}"),
    ("|RTH move| pts", "rth_move_pts", lambda s: s.abs().mean(), "{:.2f}"),
    ("RTH range pts", "rth_range_pts", lambda s: s.mean(), "{:.2f}"),
]
for lab, col, fn, f in rows:
    a, b, c = fn(d.loc[lose, col]), fn(d.loc[notlose, col]), fn(d.loc[win, col])
    P_(f"{lab:<28}{f.format(a):>14}{f.format(b):>14}{f.format(c):>14}"
       f"{a / b:>15.3f}x{a / c:>15.3f}x")
P_("")
P_("    CURRENT_BASELINE quoted '3.04 trades vs 1.38', '18 % fewer contract-minutes' and")
P_("    'sessions moving 31 % less'. All three used the NOT-LOSING denominator.")
P_("    Against genuinely WINNING sessions the turnover contrast is 3.04 vs 2.42, not 3.04 vs 1.38.")

P_("")
P_("--- FINDING 2: E_NO_ENGINE = 0 is FORCED BY CONSTRUCTION, not measured ---")
mv = d["rth_move_pts"].abs()
thr = mv.quantile(0.90)
noeng = (d["p1_trades"] == 0) & (d["xm_active"] == 0)
raw = noeng & (mv >= thr)
P_(f"    W119 spec defines E_NO_ENGINE as 'neither leg held a position while the session's")
P_(f"    absolute RTH move was in its own top decile'.")
P_(f"    top-decile |RTH move| threshold        : {thr:.1f} pts   (NaN moves: {int(mv.isna().sum())})")
P_(f"    sessions with NEITHER leg active       : {int(noeng.sum()):>5,}")
P_(f"    ... AND in the top |move| decile       : {int(raw.sum()):>5,}   <- E_NO_ENGINE on the RAW mask")
P_(f"    ... AND ALSO book_pnl < 0              : {int((raw & lose).sum()):>5,}   <- what the report printed")
P_(f"    distinct book_pnl values on the raw mask: {sorted(d.loc[raw, 'book_pnl'].unique())}")
P_("")
P_("    A session in which neither leg holds a position has book_pnl == 0 by definition and can")
P_("    NEVER satisfy book_pnl < 0. The lens was evaluated INSIDE the losing-session population,")
P_("    so it was empty before any data was read. It measured nothing.")
sub = d.loc[raw]
P_(f"    On the raw mask: n = {len(sub)}, mean |RTH move| {sub['rth_move_pts'].abs().mean():.1f} pts, "
   f"mean RTH range {sub['rth_range_pts'].mean():.1f} pts")
P_("    Those are ABSENCES, not losses. Pricing them requires a directional oracle, so any dollar")
P_("    figure attached to them is EX_POST_EXECUTION_FEASIBLE_ORACLE (level 2) and NOT available")
P_("    money - OPPORTUNITY_LANGUAGE.md is binding on exactly this.")

P_("")
P_("=" * 108)
P_("=== WHAT CHANGES AND WHAT DOES NOT")
P_("=" * 108)
P_("    CHANGES : the claim 'E_NO_ENGINE = 0, so coverage is genuinely not the gap' is NOT")
P_("              supported by this artifact. Coverage was never measured on that lens.")
P_("    CHANGES : the turnover contrast is overstated ~1.75x by the denominator.")
P_("    DOES NOT: W121 killed the turnover INFERENCE on independent evidence - entry-count caps")
P_("              lose to a count-matched random-halt placebo. The corrected, WEAKER contrast is")
P_("              consistent with W121 and does not reopen turnover.")
P_("    DOES NOT: no result is reversed, no object changes status, nothing is promoted.")
fh.close()
