# REPRESENTATION COVERAGE MATRIX

**Durable asset (GENESIS III §29, created 2026-09-06).** Prevents "we studied CL" from meaning
"one CL z-score MR test was done." One row per market, one column per representation class.

**Cell states:** `UNTESTED` · `DESCRIPTIVE` (measured facts, no strategy object tested) ·
`CLOSED@SCOPE` (a specific frozen object failed — the *scope* is closed, not the column) ·
`LEAD` (economically meaningful observation, not yet a cleared engine) · `SURVIVED` ·
`PROD-CAND`. Every `CLOSED@SCOPE` cell names its run; the closure is exactly that object.

| Market | Outright state | Event transition | RV / spread | Curve / carry | Session mechanics | Shock response | Cond. continuation | Cond. MR | Micro / execution | Regime-local |
|---|---|---|---|---|---|---|---|---|---|---|
| **NQ** | **PROD** (P1/PCT live) | **SURVIVED** (Solar flip = the event) | CLOSED@SCOPE (ES-NQ β-resid, W2_EQRESID) | UNTESTED | DESCRIPTIVE (session box, 15:50 break fact) | CLOSED@SCOPE (FOMC pre-event dir, G2_F10/F12) | SURVIVED (B-MOM channel) | CLOSED@SCOPE (many, see graveyards) | CLOSED@SCOPE (MS-BBO +2.065s VOID; causal reps untested) | LEAD (LIQREV01 post-2020, 8/8 gates — Wave F re-adjudication) |
| **ES** | DESCRIPTIVE (VR<1) | UNTESTED | CLOSED@SCOPE (β-resid vs NQ, G00061) | UNTESTED | DESCRIPTIVE (auction geometry, CLAIMS01) | UNTESTED | UNTESTED | **LEAD** (raw daily MR Sharpe 0.78, G00063 — Wave B portfolio adjudication) | UNTESTED | UNTESTED |
| **RTY** | DESCRIPTIVE (VR<1) | UNTESTED | UNTESTED (RTY/ES rel-strength untested) | UNTESTED | UNTESTED | UNTESTED | UNTESTED | LEAD (family member of G00063) | UNTESTED | UNTESTED |
| **YM** | DESCRIPTIVE (VR<1) | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | LEAD (family member of G00063) | UNTESTED | UNTESTED |
| **GC** | DESCRIPTIVE (VR<1, drift real Sharpe~0.45 ρ0.04) | 🟡 Wave E (G00069) | UNTESTED (GC/SI divergence in Wave E) | **LEAD** (CARRY_V1 dev: metals=98.5% of sector contribution — Wave A) | UNTESTED (daily-only data) | 🟡 Wave E (liquidation events) | UNTESTED | CLOSED@SCOPE (washout drift-explained, G00060) | no data | CLOSED@SCOPE (vol-sleeve neutral, G00064) |
| **SI** | UNTESTED | UNTESTED | **LEAD** (SI/GC — Wave A confirmation) | **LEAD** (CARRY_V1 dev: SI=84.1% of positive root contribution, 2019+ never computed — Wave A) | no data | UNTESTED | UNTESTED | UNTESTED | no data | UNTESTED |
| **CL** | DESCRIPTIVE (pit returns≈RW; structure is in VOL) | 🟡 Wave D (G00068) | UNTESTED | UNTESTED (curve data census needed) | 🟡 Wave D (settlement transition) | 🟡 Wave D (shock/EIA response-path) | UNTESTED | CLOSED@SCOPE (multi-day z-MR, G00065) | UNTESTED | UNTESTED |
| **ZB** | DESCRIPTIVE (VR<1, ρ−0.05 to P1) | 🟡 Wave C (G00067) | UNTESTED (ZN/ZB daily lane) | UNTESTED | 🟡 Wave C (overnight/settlement) | CLOSED@SCOPE (08:30 pre-event dir, G00062-adj; response-PATH is Wave C) | UNTESTED | CLOSED@SCOPE (intraday MR cost-fragile, G00062) | UNTESTED | UNTESTED |
| **6E** | DESCRIPTIVE (daily, ρ 0.15 regime-varying) | UNTESTED | UNTESTED | UNTESTED | UNTESTED (daily-only) | UNTESTED | UNTESTED | UNTESTED | no data | UNTESTED |

**Standing closures that cut across cells (do not re-enter):** P1-transfer construction
(XINST01, 4 markets); scheduled-macro **pre-event direction** (3 instruments — response-path
conditioning is a different, open representation); generic TSMOM/XSMOM scopes (GENESIS II);
%-return features on additively back-adjusted series (DELEV01 — points only).

**Update rule:** coordinator-only writes; every cell change cites a run id or ledger trial.
