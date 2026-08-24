# Screenshot-forensics shared schema (all agents write to this; directive §64 one-coherent-schema rule)

## Per-image record: `per_image/OTRIMG-XXXX.md`
Sections (directive §6): A file identity | B date evidence (7 distinct date kinds, never
merged: screen_capture / social_post / report_start / report_end / contract_clue /
file_metadata / inferred_version) | C source type | D strategy identity (verbatim, never
invent suffixes) | E data series | F parameters (full vertical order, control types, crop
status) | G engine settings | H performance (All/Long/Short) | I graph morphology |
J social content (verbatim Chinese, speaker attribution) | K forensic interpretation.

## Staging JSONL: `staging/<batch>.jsonl` — one JSON object per image, keys:
image_id, image_type (NT_STRATEGY_ANALYZER_SUMMARY | NT_STRATEGY_ANALYZER_ANALYSIS |
NT_STRATEGY_ANALYZER_GRAPH | NT_STRATEGY_ANALYZER_SETTINGS | NT_TRADE_PERFORMANCE |
NT_CHART | NT_STRATEGY_DIALOG | SOCIAL_NOTE | SOCIAL_COMMENT | SOCIAL_THREAD |
AUTHOR_REPLY | VENDOR_REFERENCE | OTHER | UNKNOWN — multi-region images: primary type
plus regions list in notes), screen_capture_date, screen_capture_time, taskbar_date,
social_post_date, report_start_date, report_end_date, machine_name, display_mode,
strategy_name_visible, instrument_contract, account_name, totals{net, gross_profit,
gross_loss, commission, pf, max_dd, sharpe, trades, win_rate, avg_trade, avg_win,
avg_loss, ratio_wl, max_consec_win, max_consec_los, largest_win, largest_loss,
trades_per_day, avg_time_min, avg_bars, profit_per_month, slippage}, long_short_summary,
settings_column[], other_text, social{author, post_title, post_date, comments[{who,
text, date}]}, notes, confidence (HIGH|MED|LOW), unreadable_items.

Unknown/absent → "" or null. NEVER guess cropped digits: write "45?" for a value whose
trailing digits are cut. RAW_VISIBLE_TEXT separate from INFERRED_FULL_VALUE everywhere.

## Transcription rules
- Chinese verbatim; attribute every social statement to AUTHOR / COMMENTER / UNKNOWN.
- JD-class images: macOS menu-bar date AND remote-Windows taskbar date are SEPARATE
  fields; title-bar machine name (e.g. "creator", "hp") always recorded.
- Settings column (right edge, half-cropped): read TWICE; list every visible box in
  vertical order as "num:90" / "bool:checked" / "enum:▼(unreadable)" / "num:45?(cropped)";
  record group-separator arrows (▾) as "SEP".
- Confusable digits (0/6/8, 1/7, 5/6, 179/175/180): flag LOW confidence if uncertain.
