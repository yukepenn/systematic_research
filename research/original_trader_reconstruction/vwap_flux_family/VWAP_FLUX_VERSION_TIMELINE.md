# VWAP Flux — Public Version Timeline (lawful public-source research)

**Compiled:** 2026-08-24 (directive §20/§22/§30 task; campaign #6 OTR).
**Scope:** ninZa.co "VWAP Flux" (NinjaTrader 8 indicator). Version history from public sources only:
vendor product page, vendor CMS artifacts, vendor YouTube channel, vendor forum, Wayback Machine.
No purchases, no logins, no executable downloads (only the vendor's public Trader Manual PDF and HTML pages were retrieved).
**Rule applied throughout:** marketing language is labeled MARKETING and is *not* algorithmic proof.
Only the changelog, the Trader Manual, and the "Dedicated NinjaScript Signals" spec are treated as vendor-documented behavior.

**Method notes (reproducibility).** `ninza.co` returns HTTP 403 to generic fetchers; pages were retrieved
with a browser User-Agent. The product page is Next.js; the per-product changelog is embedded in the served
HTML as a `softwareChangeLog` JSON array (`ComponentProductChangeLog` entries) — extracted verbatim, not
paraphrased from rendered text. The Wayback Machine has **zero** captures of `ninza.co/product/vwap-flux`;
the only relevant capture is the marketing microsite `vwap.nt8.ninza.co` (one snapshot, 2026-01-14).
Local copies of every fetched artifact were kept in the session scratchpad; the Trader Manual PDF retrieved
today is **byte-identical (SHA-256 `d34b50da…`)** to the copy already archived in this folder.

---

## 1. Official per-product software changelog (VERBATIM, complete)

Source: https://ninza.co/product/vwap-flux — `softwareChangeLog` array in served HTML, fetched **2026-08-24**. Confidence: **HIGH** (vendor's own version record). The array contains exactly 5 entries; unlike older ninZa products (e.g. Easy Trend, whose array begins "01 Feb 2019 – The indicator was released (built new)"), VWAP Flux's array has **no release entry** — its first entry is already a fix.

| changeDate | Verbatim `detail` | Module |
|---|---|---|
| 2026-01-14 | "The issue caused by missing data was fixed; the parameters were rearranged." | whole indicator / settings UI |
| 2026-01-17 | "The \"Anchor Period\" limit (1440 minutes) was removed." | cloud (VWAP layers) |
| 2026-02-04 | "An issue when running on a small time frame was fixed." | whole indicator |
| 2026-02-09 | "Signal_Cum_Delta was added." | signal (NinjaScript output series) |
| 2026-02-24 | "Signal_Trend was upgraded." | trend (NinjaScript output series) |

**No changelog entries exist after 2026-02-24** (page read 2026-08-24). Confidence HIGH that the vendor logged
no product-level change Mar–Aug 2026. Caveat (MEDIUM): the shared GUI library `ninZaResources` has its own
changelog (https://ninza.co/changelog) with entries on 24 Mar / 30 Apr / 06 May / 15 Jun / 25 Jun / 29 Jun /
08 Jul / 22 Jul 2026 ("GUI controls & functions were added" etc.) — library-level changes could alter panel
appearance without a VWAP Flux changelog entry. Notably there is **no ninZaResources entry between
06 Jan 2026 and 24 Mar 2026**.

## 2. Release-window evidence (initial release ≈ 2026-01-09/10)

| Date | Evidence | Source (URL) | Confidence | Notes |
|---|---|---|---|---|
| 2026-01-09 | Product record `publishedAt: 2026-01-09T09:37:41.853Z` | ninza.co/product/vwap-flux (CMS JSON in page, fetched 2026-08-24) | HIGH | CMS publication timestamp of the product entry |
| 2026-01-10 | YouTube upload "[New release] The VWAP indicator you've been waiting for!" (`uploadDate 2026-01-10T07:47:22-08:00`) | youtube.com/watch?v=blAJZKmM01w (ninZa.co Pro Trading) | HIGH | Release announcement video |
| 2026-01-14 | First (and only) Wayback capture of marketing microsite | web.archive.org/web/20260114093406/https://vwap.nt8.ninza.co/ | HIGH | Microsite live and fully built by this date |
| 2026-01-14 | First changelog entry (fix + "parameters were rearranged") | product page changelog | HIGH | Settings panel *layout changed* 5 days after release |

**Conclusion: initial public release 2026-01-09/10** (product published Jan 9, announcement video Jan 10). The
directive's "~Jan-2026" is CONFIRMED. The Jan-14 "parameters were rearranged" entry means panel screenshots
from the first days may show a different parameter order than later builds.

Marketing cadence after release (YouTube `uploadDate`, all HIGH confidence for the date, content = MARKETING):
- 2026-01-13 `JqhN3PILPos` "How VWAP Flux pulled 800+ ticks from 20+ trades in the U.S. open chaos"
- 2026-01-16 `-t28q1-c-Cs` "[New release] VWAP Flux explanation | 3X better than regular VWAP"
- 2026-01-20 `Yg9kYKwW_S8` "[NinjaTrader 8] Over 28 trades | Can VWAP Flux recover from a losing streak?"
- 2026-01-21 `ZRB7f93nP94` "VWAP Flux – The ideal VWAP indicator for clear support & resistance!" (static S/R marketing already present)
- 2026-02-02 `3UDdoBx94_M` "[100% Automated] Maximize the power of Push signals with VWAP Flux" (description credits ApexFlow Zignal + VWAP Flux + **Infinity Algo Engine$** — the vendor's own no-code strategy engine)
- 2026-02-05 `lk7r-7ntWxM` "[Auto Trading] VWAP & Order Flow: 19 winning trades in 150 minutes"
- 2026-02-06 `-JccN2xLqp0` "[Live Webinar] How VWAP Flux is 3x more effective than typical VWAP"
- 2026-04-23 `OrYdExEMdEo` "[Real-time trading] 4 trades in 3 minutes – Capturing over 200 ticks with VWAP Flux"
- 2026-07-20 `jLM2FUdYUaI` "Recovering an account from a $1,100 drawdown in 25+ trades | Live trading using VWAP"
- 2026-07-29 vendor forum post (staff) "Trading with Captain Optimus Strong v2 + VWAP Flux + Quantum Vol-Delta" — family.ninza.co/d/614

## 3. Documentation artifacts and what version they describe

| Date | Artifact | Key version-relevant content | Confidence |
|---|---|---|---|
| 2026-01-14 | Wayback microsite capture (vwap.nt8.ninza.co) | Already advertises: 5-layer cloud, Fair Value Plot intensity = cum-delta trend strength, **static S/R zones with POC + intra-zone VWAP + absorption/push classification**, pullback signals. So the static-zone module and cum-delta *display* existed at launch — only the `Signal_Cum_Delta` *NinjaScript output series* was added later (Feb 9). | HIGH (capture), content = MARKETING |
| 2026-02-02 | Trader Manual PDF uploaded to vendor CMS (`createdAt 2026-02-02T07:33:53Z`; file: forestcms…/ninZaVWAPFlux-TraderManual.pdf) | Documents **Zone Period** (§2.14) and static S/R zones; documents `Signal Trend: 1 = bullish, -1 = bearish` and `Signal Trade: 1 = bullish, -1 = bearish` (§4) — i.e. **two-state Signal_Trend**, and **no Signal_Cum_Delta** (consistent: manual predates the Feb-9 addition). | HIGH |
| 2026-08-24 (current) | Product page "Dedicated NinjaScript Signals" block | `Signal_Trend: 2 = uptrend strong, 1 = uptrend weak, -2 = downtrend strong, -1 = downtrend weak`; `Signal_Trade: 1 = bullish, -1 = bearish, 0 = no signal`; `Signal_Cum_Delta: 1 = positive, -1 = negative, 0 = no signal` | HIGH (vendor-documented API) |

**Version inference (labeled):** the 2026-02-24 "Signal_Trend was upgraded" entry, bracketed by the Feb-2 manual
(±1 two-state) and the current page (four-state ±2/±1 strong/weak), most plausibly = **the 2-state → 4-state
(strong/weak) upgrade of Signal_Trend**. Confidence MEDIUM-HIGH — inference from two documented endpoints;
the changelog itself does not say what "upgraded" means.

## 4. Reconstructed version timeline (synthesis)

| Version epoch | Window | Publicly documented state |
|---|---|---|
| v-launch | 2026-01-09 → 01-13 | Initial build. Cloud + trend + pullback signals + static S/R zones (display). Anchor Period capped at 1440 min. Original parameter order (unknown). |
| v-Jan14 | 2026-01-14 → 01-16 | Missing-data fix; **parameters rearranged** (panel order changed). |
| v-Jan17 | 2026-01-17 → 02-03 | Anchor-Period 1440-min cap removed. |
| v-Feb04 | 2026-02-04 → 02-08 | Small-timeframe fix. Manual published Feb 2 describes this era: signals = Signal_Trend ±1, Signal_Trade ±1. |
| v-Feb09 | 2026-02-09 → 02-23 | **`Signal_Cum_Delta` output series added** (1/-1/0). |
| v-Feb24 | 2026-02-24 → present (2026-08-24) | **`Signal_Trend` upgraded** (inference: 2-state → 4-state strong/weak). No later product changelog entries through Aug 2026. |

Pricing/marketing footnote (MARKETING, LOW relevance): list $600, sale $300 on product page (2026-08-24); microsite banner "only $406 + $500 gift".

---

## 5. Alignment with the trader's observed panels — **HYPOTHESES ONLY**

Trader-side observations (internal evidence, `../screenshot_forensics/PARAMETER_VERSION_TIMELINE.md`):
first VF parameter stack visible 2026-02-13 (OTRIMG-0117); two checkbox banks (8+7) appear 2026-02-20
(OTRIMG-0119); behavior shifts late-Feb 2026.

| Trader observation | Nearest vendor event | Alignment reading | Status |
|---|---|---|---|
| First VF panel 2026-02-13 (values 60/5/20/EMA?/95-75-50-25-5/3/10/5) | `Signal_Cum_Delta` added 2026-02-09 | Trader's first visible VF stack appears 4 days after the Feb-9 build. Consistent with the trader installing/updating VWAP Flux in the 09–13 Feb window — but equally consistent with earlier ownership and no earlier panel screenshot. Note the panel shows the *post*-Jan-14 "rearranged" parameter order (13/13 label-order match to the Feb-2 manual). | **HYPOTHESIS — cannot distinguish install date from screenshot-coverage gap** |
| Two checkbox banks added 2026-02-20 | **None.** Product changelog gap 02-09→02-24; ninZaResources gap 01-06→03-24 | No vendor-side event on/near Feb 20 in either changelog. The banks most plausibly belong to the trader's own wrapper strategy UI (vendor VF panels in the manual contain no checkbox banks). An unlogged vendor GUI change cannot be excluded but has no supporting evidence. | **HYPOTHESIS — favors trader-side custom wrapper change** |
| Behavior shifts late-Feb 2026 | `Signal_Trend` upgraded 2026-02-24 | If the trader's wrapper gates entries on `Signal_Trend` values, the 2-state→4-state change is exactly the kind of vendor change that silently alters wrapper behavior: code testing `Signal_Trend == 1` would, post-upgrade, fire only in *weak* uptrend states (strong = 2), thinning/altering entries until the wrapper was updated to `>= 1` or `== 2`. | **HYPOTHESIS — mechanism plausible and date-aligned; no proof the trader's wrapper reads Signal_Trend this way** |

**Correction flag for internal docs:** `TRACK_VF_REPORT.md` states the manual shows "…/4/80/30" for the
signal group. The archived manual (same SHA-256 as today's download) shows suggested presets with
**Quantity Per Trend 5 / Close Threshold 70 / Split 15** (Split 30 only on the ninZaRenko-12/4 preset);
"4" appears only in the §2.11 *example sentence* ("if Signal Quantity Per Trend = 4 …"), and **no Close
Threshold of 80 appears anywhere in public material** (80 is the *Level: Max* value in the 1-min and
ninZaRenko presets). See `VENDOR_SIGNAL_USAGE_MODEL.md` §A.4.

---

## 6. Source register

| # | URL | Accessed / dated | What it provided | Confidence |
|---|---|---|---|---|
| S1 | https://ninza.co/product/vwap-flux | 2026-08-24 | changelog array; Dedicated NinjaScript Signals; description; `publishedAt`; download-file names (`NinZaVWAPFlux_NT8.zip` — NOT downloaded; `ninZaVWAPFlux-TraderManual.pdf`) | HIGH (vendor record); description = MARKETING |
| S2 | https://forestcms.nyc3.digitaloceanspaces.com/media/ninZaVWAPFlux-TraderManual.pdf | 2026-08-24 (CMS createdAt 2026-02-02) | 15-page official manual: parameter semantics, suggested presets, signal spec (pre-Feb-24) | HIGH |
| S3 | https://ninza.co/changelog | 2026-08-24 | ninZaResources (shared GUI lib) changelog; note "Changelogs were moved into each product's own page" | HIGH |
| S4 | https://web.archive.org/web/20260114093406/https://vwap.nt8.ninza.co/ | capture 2026-01-14 | launch-era marketing content incl. static S/R, POC, absorption/push, cum-delta strength | HIGH (date), MARKETING (content) |
| S5 | https://vwap.nt8.ninza.co/ | 2026-08-24 | current microsite (diff vs S4: content essentially unchanged; adds webinar/video sections) | HIGH (date), MARKETING |
| S6 | YouTube channel @ninzaco ("ninZa.co Pro Trading") — video IDs in §2 | uploadDate metadata read 2026-08-24 | dated marketing/automation videos | HIGH (dates), MARKETING (claims) |
| S7 | https://family.ninza.co/d/614 | posted 2026-07-29 | vendor-staff usage guidance (VF = direction/zones/context; delta = confirmation, "not … an entry signal by itself") | MEDIUM (educational, vendor-authored) |
| S8 | https://ninza.co/product/easy-trend | 2026-08-24 | cross-product Signal_Trend/Signal_Trade convention + example of a full changelog with release entry | HIGH |
| S9 | Wayback CDX API (`ninza.co/product/vwap-flux*`, `best.ninza.co/products/vwap-flux*`) | 2026-08-24 | zero captures of the product page → no independent archive of pre-Feb page states | HIGH (absence) |

Negative results: no futures.io / NexusFi / Reddit thread specifically reviewing VWAP Flux was found via web
search (searched 2026-08-24); no third-party changelog mirror exists; Wayback has no capture of the product
page at any date, so the Feb-era page state is reconstructed from the manual + changelog only.
