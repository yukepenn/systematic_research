## VERDICT: **CONFIRMED-WITH-CORRECTIONS**

Every file exists and contains what was claimed. I re-implemented the entire analysis from scratch along an independent path (session calendar from the NQ ledger's own `sess_end` instead of MNQ `fbos`; forward `searchsorted` instead of `merge_asof` on `sopen−3min`; my own state-machine replays) and **every headline number reproduced exactly**. The verdict is sound. The defects are in labeling, provenance and one mislabeled early-close split — none of them move the conclusion.

---

## DEFECTS

**1. `n_early_close` counts the 2026-05-29 data-end truncation as a genuine early close.**
`src/v1d_late_entries.py:183` — `is_early = r.close_tod.values != "17:00"`. PART 0 (`v1d_late_entries.py:375-382`, `out/v1d_report.txt:24`) explicitly excludes the 16:57 session from the early-close set; `census()` does not. **2026-05-29 is a normal 17:00 session** — `smm_v2_bars.csv` has `2026-05-29 17:00:00,1` (sess_end); `mnq_3m_raw.csv` is just truncated 3 min early (459 bars vs 460). Verified consequence:

| Product A, "of which early-close" | N≤15 | 20 | 30 | 45 | 60 |
|---|---|---|---|---|---|
| published (`V1D_CLOSURE.md` §3, `out/v1d_census.csv`) | 3 | 4 | 6 | **8** | **9** |
| correct (my NQ-ledger derivation) | 3 | 4 | 6 | **7** | **8** |

The extra event is `2026-05-29 16:24 open 0→+1`, **36 min before a normal 17:00 close**. `n_normal_close` at N=45/60 should be 94/613, not 93/612. Also shifts every `min_before_close` on that session by 3 min. No sub-30-min event is involved, so the verdict is untouched.

**2. "540,231 bars" fidelity claim overstated by 20,518 bars.**
`V1D_CLOSURE.md` §4.0 ("reproduces … `tgt_raw` at 1.000000 (540,231 bars)"), §2, §3, and `v1d_late_entries.py:37`. But `load_bars()` (`:198-200`) filters `time <= DEV_END`, and `smm_v2_bars.csv` runs to **2026-07-31**. Verified: 540,231 total, **519,713 in the dev window**. The fidelity is genuine — I reproduced 1.000000/1.000000 on 519,713 bars — but as written the claim asserts a check over 2026-05-30 → 2026-07-31, data the item elsewhere says it never read. Not a leak (the code correctly excluded it); a prose claim of a check that was not performed.

**3. The MD's most-cited table (§4.2) is absent from the "full numeric output" and is not reproducible by running the script.**
MD windows `16:30–16:57` (10,950 bars, 43.6%) and `16:39–16:57` (7,665 bars, 1.71% M-change, 1.79% T-change, 0.091%/bar) appear **nowhere** in `out/v1d_report.txt`. The script (`:584-592`) emits only `16:39-17:00` → 8,760 bars, 12.67%, 0.080%/bar. grep counts in report.txt: `7665`=0, `10950`=0, `1.71`=0, `0.091`=0, `16:39-16:57`=0. I re-derived them by hand from the per-tod table and they are **arithmetically correct** (8760−1095=7665; (0.1267·8760−0.8941·1095)/7665=1.709%; 7/7665=0.0913%) — but hand-computed and undocumented. Same for MD §3's seven-row event table (also not in report.txt; I verified all 7 rows exactly). Corroborating: `V1D_CLOSURE.md` mtime **23:33:48** predates `out/v1d_report.txt` **23:34:04** and `out/v1d_signal_by_tod.csv` **23:34:02** — the MD was written before the shipped output existed.

**4. `P_flat_and_ge3` published with no explanation; it reads as a direct refutation of the headline.**
`out/v1d_report.txt:262-267` shows `P_flat_and_ge3` ≈ **0.4374, 0.4347, 0.4347, 0.4356, 0.4365, 0.4365** at 16:42–16:57 — i.e. "flat *and* above the ±3.0 entry threshold on ~44% of bars in the last 18 minutes." Neither file mentions the column. It is an artifact of the 16:39 forced-flat being ON in the baseline `pos` used to compute it. The decisive, correctly-windowed version — which the agent computed but did not report — is **P(flat & |M|≥3) = 0.0024 over 16:30–16:36** (my number), which *supports* the verdict. Publishing the misleading version and omitting the supporting one is a reporting defect.

**5. §4.2(ii) compares a per-bar move against a cumulative-retracement distance.**
MD juxtaposes "mean |3-min close change| 3.06–3.45 pts at 16:45–16:57" against "member stop distances 39–195 points." From source: `SolarWaveOneContractNQ_Final.cs:163-186`, a member flips when price retraces `mSEff` from a **running anchor extreme** — a multi-bar excursion. ~3.2 pts × ~20 remaining bars supports a 15–70 pt excursion, which reaches into the 39-pt bottom of the range. The settling diagnostic (max excursion from anchor over the remaining session) was never computed. Their inputs are all correct (I verified σ=6.4971 pts; `ResolveS` `:152-162` confirms the clamp is 10–300 *points*, so 39–195 is right and unclamped; RTH |Δ|=11.04, 16:45–16:57=3.26), and they do label the causal link INFERENCE. But the rhetoric exceeds the evidence; the DIRECT P(T changed) 14.28%→1.37% is what actually carries it.

**6. VERDICT-block wording overstates the Product A contrary finding.**
`V1D_CLOSURE.md` VERDICT §3: "produces **68 additional** risk-increasing events, of which **31** fall within 15 minutes and **38** within 20 minutes." Read literally: 31 of the 68 *additional* are inside 15 min. Correct: 31 is the *total* under no-clamp (28 additional); 38 total within 20 (34 additional); and 38 already contains the 31, so the two cannot be summed. §4.1's table is correct and unambiguous — but the VERDICT block is the part downstream artifacts quote.

**7. `sessions_affected_pct` is events ÷ sessions, labeled as a fraction of sessions.**
`v1d_late_entries.py:190`; rendered in MD §3 as "% of 1,139 sessions … 13.3". Verified: NQ N≤60 is **152 events on 150 distinct sessions** (13.17%, not 13.35%). N≤30 and N≤45 are 1:1 (3/3, 17/17), so "3 of 1,139 sessions (0.26%)" survives. Product A's same column reports 54.5% "sessions affected" for 621 events. Separately, `pct_of_all_entries` uses a *different denominator per row-group* (621/12,977 for "all" but 228/1,335 for "reversal") — not comparable within its own column.

**8. The 2024-04-21 rows are real events with a wrong calendar mapping, not "spurious rows."**
MD §2 / `out/v1d_report.txt:158-165` call them "6 spurious … rows … excluded as an artifact." They are genuine: 8 consecutive `tgt_ops=+1` submissions where `phys` never advanced, at the *start* of the 2024-04-22 session. The artifact is created entirely by the calendar choice — MNQ has no bars before 18:27 that day, so `attach_close` maps them to the previous Friday's close. **Using the NQ ledger's own `sess_end`, I get exactly 2 `mb<=0` events (the two genuine at-the-close ones) and zero artifact rows.** So "the MNQ-derived calendar is used as truth" (§2) *manufactured* the artifact it then excludes; the NQ ledger was the right calendar for an NQ-signal object. Also "6 spurious rows … the same 8 bars": 6 ≠ 8; the 6 are a subset.

**9. 2023-04-05 close is wrong in both calendars, unremarked for Product B.**
The NQ signal series gaps 14:03 → 20:03 with `sess_end=1` at 14:03 — meaning **in the actual NT8 backtest that session ended at 14:03**. The agent overrides this with MNQ's 17:00 for all objects, including the two whose signal series *is* NQ. Immaterial (I checked: no entry lands in 13:03–14:03 that day; census unchanged), but the stated rule is wrong for a gapped signal series.

**10. "Independently cross-checked against `smm_v2_fills.csv`" is not independent.**
MD §3. Both censuses route through the same `attach_close()` and the same MNQ calendar, from the same NT8 run. It is a consistency check. (The L/S filter is legitimate — I verified the vocabulary: L=Buy 6,800, S=SellShort 6,169; XL/XS/`Close position`/`Exit on session close` are all exit-side.) My genuinely independent re-derivation does agree, so the conclusion stands; the word "independently" is not earned by the cited check.

**11. MD §3 header undercounts its own table** — "The three events inside 15 minutes, and the two stamped exactly at a close:" heads a **seven**-row table (it also lists 2025-07-04 at mb=18 and 2023-04-07 at mb=24).

**12. No V1d pre-registration exists.** `runs/W17_C4_COMPLIANCE/spec.yaml:153-158` lists outputs = two `.cs` files, `c4_audit.py`, `REPORT.md` — no V1d artifact, no V1d section, no V1d success criterion. Defensible for a descriptive census, but §5 *is* a hypothesis test, and its four clock windows (12:03–13:00, 12:18–13:15, 08:18–09:15, 08:33–09:30) were chosen after the observed count was known to be 0. The conclusion drawn is the conservative direction, so nothing is inflated. Also `date_frozen: 2026-08-09` and the MD's date are one day ahead of the environment date (2026-08-08); mtimes are 2026-08-08 23:13–23:34 −0400.

**13. Downstream propagation drops the contrary half.** `research/system_master/CURRENT_TRUTH.md:82-83` propagates only "V1d = NOT-A-PROBLEM: removing the 16:30 block adds 3 entries" and omits the Product A "+68 / 31 within 15 min" finding that the MD itself insisted "must not be buried."

---

## WHAT I TRIED TO BREAK AND COULD NOT

**a. Every headline count, re-derived along a fully independent path** (NQ-ledger calendar, `searchsorted` not `merge_asof`, my own replays):
- BEST_ONE_NQ `[0,0,0,0,3,17,152]` ✓ · BEST_ONE_MNQ `[0,0,0,0,1,6,98]` ✓
- Product A `[0,0,3,4,14,101,621]`; open/increase/reversal = 3,478/8,164/1,335 = 12,977 ✓
- Counterfactuals: **1,976 / 1,979 / 1,982**, censuses `[…3,17,152]` / `[…6,20,155]` / `[1,2,3,3,9,23,158]` ✓ — the "+3" and "+6" are real
- Product A ops-off `[7,16,31,38,78,165,685]`, total 13,037 (**+68**) ✓ — the contrary finding is real
- C2 replay: Product A `[0,0,0,0,9,96,616]` **and `n(mb≤0)=0`** — the §6 claim that C2 removes both at-the-close events is true
- 16:00 spike: 1,095 sessions, Bprev≠0 = 1,027, |M|≥3 472 actual / 642 counterfactual, **111 unmasked (10.1%)**, 105 real 16:00 entries, **102 (97%)** unmasked ✓
- Poisson λ=2.90 → P(0)=**0.055** ✓; σ=6.4971 → 39.0/194.9 pts ✓; RTH |Δ|=11.04, 16:45–16:57=3.26 ✓
- **43 early closes (31/9/2/1) confirmed from *both* calendars independently** ✓

**b. The signal reconstruction is genuinely bit-exact.** My own code: Tpp 1.000000, tgt_raw 1.000000 on all 519,713 dev bars. My replay hits **1,975/1,975 real `nt_trades_nq.csv` entries timestamp-exact, 0 missed, 1 extra** — the counterfactuals really are run on a verified twin, not a model.

**c. The Python matches the C# line-for-line.** `SolarWaveOneContractNQ_Final.cs:311` `hm >= 163000 && hm <= 180000` ↔ `<=`; `:312` `hm >= 163900 && hm < 180000` ↔ `<`; `SolarWaveSMMaster_v2.cs:310,314-318` ops clamp ↔ `replay_a` exactly — including the fact that Product A uses `<180000` where Product B uses `<=180000`; the apparent inconsistency in the Python **mirrors a real inconsistency between the two `.cs` files**. `:304` gates `mm` on `sumNext` where Python gates on `T`; T=round(sumNext/13·10, AwayFromZero) preserves nonzero-ness and sign, so the substitution is exact and the 1.000000 Tpp match confirms it. `BmomBar` (`:197-231`): the `hm > 160000` early return does make `bmomPos=0` persist from 15:57 to the next 09:33 — I measured P(B≠0) = 0.9379 at 15:54, **0.0000 at 15:57 and 0.0000 at 16:57**.

**d. No look-ahead.** `tm[i+1]` is a forward *labeling* of the fill for a decision made on bar i; nothing from i+1 enters the decision. Session-end bars are excluded from event detection in `replay_a`, and cannot produce an entry in `replay_b` (M=0 at 17:00 and `ff` is true there). Position resets to 0 at each session start, matching `IsExitOnSessionCloseStrategy`.

**e. No locked-forward leakage, no 2006-2021.** LOCKED_FORWARD starts 2026-08-01; `smm_v2_bars.csv` and `smm_v2_fills.csv` both run to 2026-07-31 and were correctly cut at 2026-05-29. The two trade lists are *not* filtered in code — a latent bug — but max entry_time is **2026-05-28 09:48** (NQ) and **2026-05-27 23:15** (MNQ), so 0 rows past DEV_END. Every input begins 2022-01-02 18:03/18:06 (the open of the 2022-01-03 session).

**f. No silently dropped rows in the Product B census.** NaN mappings = 0; `mb<=0` = 0 for both objects; 1,975 and 1,561 fully accounted.

**g. No bootstrap, no RNG, no seed needed** — the only inferential statistic is a closed-form Poisson.

**h. No commission double-count, no near-zero/negative denominator.** No P&L or P&L ratio is computed anywhere in this item. Notably W16's own N≤60 friction-share cell carries "−0.200 (net negative denominator)" (`runs/W16_V0_HYGIENE/REPORT.md:105`), and `V1D_CLOSURE.md` §8 explicitly declines to re-use or re-test W16's P&L hint. Correct call.

**i. The W16 baseline is a real citation, not a straw man.** `runs/W16_V0_HYGIENE/REPORT.md:103-118` gives 3/17/152 and 1/6/98 — the "delta 0" claim is against the actual artifact. (Caveat: W16 at `:98-100` *already* stated the "empty by construction for N<30" mechanism, so the MD's "wrong in framing" charge is harsher than W16 deserves — W16's real error was assuming that construction held on all 1,139 sessions, which is precisely what this item found.)

**j. Nulls are reported at equal prominence.** §5 (the zero is NOT protection, P=0.055/0.201) is a standalone top-level section; the Product A contrary finding sits inside the VERDICT block; §8 disclaims profitability; the MNQ KNOWN_ERRORS #7 caveat is carried in the docstring, §3 and §5. This part is done well.

**k. The load-bearing claim survives.** Strip *both* late-session rules off Product B and it opens inside the final 20 minutes on 3 events across 3 distinct sessions out of 1,139 — verified independently. `no_new_entry_after` genuinely has nothing to do.

---

## FILES I READ (none edited)
- `D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\W17_C4_COMPLIANCE\V1D_CLOSURE.md`
- `...\runs\W17_C4_COMPLIANCE\src\v1d_late_entries.py`
- `...\runs\W17_C4_COMPLIANCE\out\v1d_report.txt`, `out\v1d_census.csv`, `out\v1d_signal_by_tod.csv`, `out\v1d_session_calendar.csv`
- `...\runs\W17_C4_COMPLIANCE\spec.yaml`
- `...\src\ninjascript\SolarWaveOneContractNQ_Final.cs`, `SolarWaveSMMaster_v2.cs`
- `...\runs\W16_V0_HYGIENE\REPORT.md`, `...\research\system_master\CURRENT_TRUTH.md`

## VERIFICATION SCRIPTS I WROTE (scratchpad, outside the repo)
`C:\Users\YUKEZH~1\AppData\Local\Temp\claude\D--OneDrive---Washington-University-in-St--Louis-TradingResearch-systematic-research\bfb80633-2ca8-4554-803e-2bd6cbeeb4c1\scratchpad\rt1.py` … `rt7.py`

**No NT8/CrossTrade tool used. No repo file created, edited or deleted. No commit.**