# MANIFEST_NOTES — how to read `substrate/MANIFEST.csv` correctly (2026-08-18)

The CSV itself is append-only and is NOT rewritten. Two of its columns are misleading for
later rows; this note is the correction of record.

1. **`src` column**: hardcoded to `SWScalpTickExport_v1` by `src/python/csv_to_parquet.py`
   for every row. Rows appended **2026-08-10** (the 8 batch-1 confirmation-pool sessions:
   s20260210, s20260217, and companions per CONTAMINATION_LEDGER) were actually exported by
   **`SWScalpTickExport_v3`** (v1's overload pattern, 20M cap, repo EXPORT01/out path).
   v2 never produced any data (bugged single-arg AddDataSeries — see campaign memory/spec
   notes); no row in the manifest comes from v2.
2. **`capped` flag**: computed with the v1-era rule `n >= 12,000,000`. Under v3's 20M cap this
   misclassifies: s20260217 (15.83M rows) is **complete, not capped**, despite tripping the 12M
   rule. Conversely **s20251117 and s20251117_rth remain genuinely truncated at 12M** (v1-era
   exports; re-export at the 20M cap is the one outstanding completeness item, deferred to the
   next natural NT8 restart).
3. **Coverage summary as of 2026-08-18**: NQ 40 substrate sessions + 8 pool sessions (consumed
   2026-08-10, AMENDMENT_3 batch 1), ES 39 sessions (ARCHIVE_ONLY), minute NQ 2006-01-05→
   2026-05-29 (6,466,783 bars, sha256_16 dfd017ef, `minute/NQ/MANIFEST`).

If `csv_to_parquet.py` is ever used again, fix the `src` hardcode and the cap rule first;
until then, this note governs interpretation.

## Addendum 2026-08-19 (LIQREV01 red team) — minute-substrate defects of record
- `minute/NQ/nq1m_2005_202605.parquet` has genuine holes: the entire week 2014-01-27..31 is
  missing, plus scattered non-holiday weekdays (2009-03-27, 2009-06-19, 2013-07-12); 46 valid
  days carry only 261-379 RTH bars. Post-2014 CME 13:00-halt holiday Globex sessions (July 4,
  Juneteenth, Thanksgiving Day, Christmas Eve) pass a 200-bar RTH filter and look like thin
  trading days. Any daily-scale study on this file should disclose these; none changed the
  LIQREV01 verdict (quantified in its REPORT §2).
