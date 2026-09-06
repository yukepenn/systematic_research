# REPRESENTATION COVERAGE MATRIX

**Durable asset (GENESIS III §29, created 2026-09-06; updated after Wave 1).** Prevents "we
studied CL" from meaning "one CL z-score MR test was done." One row per market, one column per
representation class.

**Cell states:** `UNTESTED` · `DESCRIPTIVE` (measured facts, no strategy object tested) ·
`CLOSED@SCOPE` (a specific frozen object failed — the *scope* is closed, not the column) ·
`LEAD` (economically meaningful observation, not yet a cleared engine) · `SURVIVED` ·
`PROD-CAND`. Every `CLOSED@SCOPE` cell names its run; the closure is exactly that object.

| Market | Outright state | Event transition | RV / spread | Curve / carry | Session mechanics | Shock response | Cond. continuation | Cond. MR | Micro / execution | Regime-local |
|---|---|---|---|---|---|---|---|---|---|---|
| **NQ** | **PROD** (P1/PCT live) | **SURVIVED** (Solar flip = the event) | CLOSED@SCOPE (ES-NQ β-resid, W2_EQRESID) | UNTESTED | DESCRIPTIVE (session box, 15:50 break fact) | CLOSED@SCOPE (FOMC pre-event dir, G2_F10/F12) | SURVIVED (B-MOM channel) | CLOSED@SCOPE (many, see graveyards) | DESCRIPTIVE (census + XPASS01 NULL G00082: join-bid fills 0.9s median, adverse selection grows with T, no policy change; W5-pool governance premise corrected) | CLOSED@SCOPE (LIQREV01 DEAD as standalone: no-harm gates D6b/D6c failed — active-day ρ +0.614 to P1, G00071) |
| **ES** | DESCRIPTIVE (VR<1) | UNTESTED | CLOSED@SCOPE (β-resid G00061) | UNTESTED | DESCRIPTIVE (auction geometry CLAIMS01; month-end stock-bond rebalance conjunction DEAD G00077; turn-of-month ≈ 0 banked) | UNTESTED | UNTESTED | CLOSED@SCOPE (stat G00063 + portfolio-inert G00066: s*>1, never beats P1-alone) | UNTESTED | UNTESTED |
| **RTY** | DESCRIPTIVE (VR<1) | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | CLOSED@SCOPE (family G00063; dominated by ES member closed portfolio-inert G00066) | UNTESTED | UNTESTED |
| **YM** | DESCRIPTIVE (VR<1) | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | CLOSED@SCOPE (as RTY) | UNTESTED | UNTESTED |
| **GC** | DESCRIPTIVE (drift Sharpe~0.45 ρ0.04) | CLOSED@SCOPE (6-event daily catalog all DEAD vs drift-matched control, G00069) | CLOSED@SCOPE (GC−SI divergence ANTI-convergent, G00069 E5) | CLOSED@SCOPE (SI/GC switch G00070; basis-mom data-collapsed G00075) | UNTESTED (daily-only data) | CLOSED@SCOPE (liquidation/gap events, G00069) | UNTESTED | CLOSED@SCOPE (washout drift-explained, G00060) | no data | CLOSED@SCOPE (vol-sleeve neutral, G00064) |
| **SI** | UNTESTED | UNTESTED | CLOSED@SCOPE (G00070 adjudicated-closed, windows spent) | CLOSED@SCOPE (G00070: the dev relation was the silver rally in disguise; family table = selection-pricing only, NEVER a discovery surface) | no data | UNTESTED | UNTESTED | UNTESTED | no data | UNTESTED |
| **CL** | DESCRIPTIVE (pit≈RW; structure is VOL) | CLOSED@SCOPE (7-event catalog all DEAD, 1/52 cells vs 2.6 expected, G00068) | UNTESTED | CLOSED@SCOPE at 2009-15 depth (basis-mom G00075, DATA-GATED beyond) | CLOSED@SCOPE (settlement transition dead, G00068 E2) | CLOSED@SCOPE (shock/EIA response-path flat 12/12, G00068) | CLOSED@SCOPE (in-catalog, G00068) | CLOSED@SCOPE (multi-day z-MR, G00065) | UNTESTED | UNTESTED |
| **ZB** | DESCRIPTIVE (VR<1, ρ−0.05 to P1) | ⭐ **PROD-CAND** (ZBMACRO01 FROZEN-READY G00079: 08:46-entry executable, skeptic-survived — FT running); auction family FULLY CLOSED (rebound G00073 powered; concession G00080 below-MDE, era mirror banked) | CLOSED@SCOPE (DV01-neutral slope RV gross-negative, G00074) | CLOSED@SCOPE (slope RV G00074; basis-mom G00075; outright carry-timing NOT-CLEARED-AT-DEBT-BAR G00081 — bear-survival banked, revival = forward accrual) | CLOSED@SCOPE (overnight-displacement E2 + settlement E6 dead, G00067) | CLOSED@SCOPE (shock-no-followthrough E5 dead, G00067; pre-event macro dir closed earlier) | DESCRIPTIVE (compression E3, extremes-revert E4) | CLOSED@SCOPE (intraday MR cost-fragile, G00062) | UNTESTED | CLOSED@SCOPE (corr-gated FTQ POWERED-INVERTED, G00076) |
| **6E** | DESCRIPTIVE (daily, ρ 0.15 regime-varying) | UNTESTED | UNTESTED | UNTESTED | UNTESTED (daily-only) | UNTESTED | UNTESTED | UNTESTED | no data | UNTESTED |

**Standing closures that cut across cells (do not re-enter):** P1-transfer construction
(XINST01, 4 markets); scheduled-macro **pre-event direction** (3 instruments — realized
response-path conditioning was the open representation and is now LEAD on ZB, DEAD on CL);
generic TSMOM/XSMOM scopes (GENESIS II); %-return features on additively back-adjusted series
(DELEV01 — points only).

**Update rule:** coordinator-only writes; every cell change cites a run id or ledger trial.
