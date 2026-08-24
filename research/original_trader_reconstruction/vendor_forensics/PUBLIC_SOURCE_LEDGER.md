# PUBLIC SOURCE LEDGER (vendor forensics; all lawful public sources; no auth bypass, no decompilation)

| Source | Type | What it yielded | Archived |
|---|---|---|---|
| ninZa VWAP Flux Trader Manual (forestcms...digitaloceanspaces .../ninZaVWAPFlux-TraderManual.pdf, uploaded 2026-02-02) | official PDF | full 14-param list + UI order + screenshots; mechanism sections 2.1-2.14; suggested settings ×5; chart images (NQ MAR26 1-min + 100-tick) that selected the anchored-layer architecture | `vendor_docs/vwapflux-manual.pdf` + page images in session scratchpad |
| ninza.co/product/vwap-flux (curl + Chrome UA; 403 to plain fetch) | product page CMS JSON | complete changelog (release 2026-01-09 → 2026-02-24), signal series semantics, pricing $300, download-file names | HTML in scratchpad |
| vwap.nt8.ninza.co | landing page | marketing architecture wording (AnchorPeriodMinutes, Amount) | scratchpad |
| renkokings.com/product/thunderzilla | product page | complete changelog (2024-02-14 release; 2025-08-11 Qty-Per-Trend), Signal_Trade alphabet, Renko-exclusive statement, 32 gallery screenshots | scratchpad (tz.txt + imgs) |
| family.ninza.co Flarum API d/345, d/308, d/110, d/591 | forum | 8 settings-dialog screenshots (param list + per-instrument NQ/ES/YM/GC values); trailing-stop trigger semantics; ApexFlow pairing | scratchpad fam/p1-8.png |
| ninza.co/product/cumulative-delta + volume-delta + manuals | pages+PDFs | verbatim Volume Base definitions (>=ask / <=bid; inside unaddressed); No-Tick-Replay tech changelog 2025-12-24; signal series | `vendor_docs/*.pdf` |
| Quantum Vol-Delta manual | PDF | param list; Tick Replay requirement statement | `vendor_docs/` |
| Wayback ninza.co/product/thunderzilla snapshot 2025-09-16 | archive | confirmed changelog JSON changeDate 2025-08-11 | noted |
| Local: Documents/NinjaTrader 8 templates/logs/csproj/workspaces | local files | ninZa 6-DLL package + RenkoKings templates (EV-021/022); NO TZ/Flux artifacts | repo-external, findings ledgered |
| (pending, workflow w2mqke1pn) ApexFlow / Infinity / Captain / NVI/PVI / Noble Cloud / bar-type docs | pages | property fingerprints for the match matrix | to be appended |

Rule maintained throughout: property names, public signals, templates, ordinary metadata,
and behavioral testing only. The licensed SolarWave DLL is never decompiled; no vendor
authentication is bypassed; no paid content accessed without license.
