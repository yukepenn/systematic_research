"""Build ALL_VISIBLE_PARAMETER_ORIGIN_MATRIX.csv - directive v5.0 section 4.

One row per DISTINCT PARAMETER SLOT observed anywhere in the 2026 corpus (not per row-instance;
the same slot appears in up to 9 frames).  Slots are transcribed from the committed FACT tables in
vwap_flux_family/2026_PANEL_TOPOLOGY.md sections 2-3 and 2026_panel_rows.csv.

Section 5 is binding: a slot may only be given a component identity on LABEL / ORDER /
CONTROL-TYPE / GROUP-HEADER evidence.  Numeric coincidence yields OPEN_VENDOR_CANDIDATES at most.
Every slot whose label was never photographed therefore starts as UNEXPLAINED, and the
control-type SEQUENCE is recorded as the primary matchable fingerprint for the vendor pass.
"""
from __future__ import annotations

import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# (block, slot, img_evidence, date, scroll, ctrl, value, label, status, note)
N, K, E, S, G = "numeric", "checkbox", "enum", "separator", "group_header"
V = "VISIBLE_VALUE_ONLY"          # value photographed, label never photographed
L = "LABEL_PHOTOGRAPHED"

SLOTS = [
    # ---- HEAD-A : top of the list, the only two frames ever scrolled to position 0 -----------
    ("HEAD-A", 1, "OTRIMG-0119,0138", "2026-02-20/04-29", "TOP", G, "UNREADABLE", "", V,
     "group header, label truncated to ellipsis in the narrowed pane"),
    ("HEAD-A", 2, "OTRIMG-0119,0138", "2026-02-20/04-29", "TOP", E, "UNREADABLE", "", V,
     "dropdown; selected text not legible at this pane width"),
    ("HEAD-A", 3, "OTRIMG-0119,0138", "2026-02-20/04-29", "TOP", E, "UNREADABLE", "", V,
     "dropdown; selected text not legible"),
    ("HEAD-A", 4, "OTRIMG-0119,0138", "2026-02-20/04-29", "TOP", G, "UNREADABLE", "", V,
     "group header"),
    ("HEAD-A", 5, "OTRIMG-0119,0138", "2026-02-20/04-29", "TOP", K, "checked", "", V, ""),
    ("HEAD-A", 6, "OTRIMG-0119,0138", "2026-02-20/04-29", "TOP", N, "10", "", V, ""),
    ("HEAD-A", 7, "OTRIMG-0119,0138", "2026-02-20/04-29", "TOP", N, "26 -> 20", "", V,
     "CHANGED between 2026-02-20 (26) and 2026-04-29 (20) - a genuine retune"),
    ("HEAD-A", 8, "OTRIMG-0119,0138", "2026-02-20/04-29", "TOP", N, "14", "", V,
     "the recurring 14; also appears in the 0150 middle slice next to 6"),
    ("HEAD-A", 9, "OTRIMG-0119,0138", "2026-02-20/04-29", "TOP", N, "198?", "", V,
     "right-clipped by the box edge; trailing digits UNREADABLE"),
    ("HEAD-A", 10, "OTRIMG-0119,0138", "2026-02-20/04-29", "TOP", N, "180?", "", V,
     "right-clipped; trailing digits UNREADABLE"),
    ("HEAD-A", 11, "OTRIMG-0119,0138", "2026-02-20/04-29", "TOP", N, "140?", "", V,
     "right-clipped; trailing digits UNREADABLE"),
    ("HEAD-A", 12, "OTRIMG-0138", "2026-04-29", "TOP", K, "checked", "", V,
     "present 2026-04-29, absent 2026-02-20: group EXTENDED between those dates"),
    ("HEAD-A", 13, "OTRIMG-0138", "2026-04-29", "TOP", N, "16", "", V, "added by 2026-04-29"),
    ("HEAD-A", 14, "OTRIMG-0138", "2026-04-29", "TOP", N, "6", "", V, "added by 2026-04-29"),
    ("HEAD-A", 15, "OTRIMG-0138", "2026-04-29", "TOP", N, "9", "", V, "added by 2026-04-29"),

    # ---- BANK-1 / BANK-2 : two consecutive checkbox banks with identical masks -------------
    ("BANK-1", 1, "OTRIMG-0119", "2026-02-20", "TOP", G, "UNREADABLE", "", V, "group header"),
    ("BANK-1", 2, "OTRIMG-0119", "2026-02-20", "TOP", K,
     "U,C,C,U,U,C,C,C", "", V, "8-checkbox bank"),
    ("BANK-2", 1, "OTRIMG-0119", "2026-02-20", "TOP", G, "UNREADABLE", "", V, "group header"),
    ("BANK-2", 2, "OTRIMG-0119", "2026-02-20", "TOP", K, "U,C,C,U,U,C,C", "", V,
     "7 checkboxes, clipped at pane bottom; first SEVEN states IDENTICAL to BANK-1 -> the list "
     "contains repeated blocks"),

    # ---- MIDDLE : the single middle-scrolled frame in the whole corpus ----------------------
    ("MIDDLE", 1, "OTRIMG-0150", "2026-06-05", "58%", N, "30", "", V, ""),
    ("MIDDLE", 2, "OTRIMG-0150", "2026-06-05", "58%", N, "70", "", V, ""),
    ("MIDDLE", 3, "OTRIMG-0150", "2026-06-05", "58%", N, "2", "", V, ""),
    ("MIDDLE", 4, "OTRIMG-0150", "2026-06-05", "58%", N, "20", "", V, ""),
    ("MIDDLE", 5, "OTRIMG-0150", "2026-06-05", "58%", G, "UNREADABLE", "", V, ""),
    ("MIDDLE", 6, "OTRIMG-0150", "2026-06-05", "58%", K, "U,C,C,C", "", V, "4-checkbox bank"),
    ("MIDDLE", 7, "OTRIMG-0150", "2026-06-05", "58%", N, "14", "", V,
     "the 14/6 pair; 'KingRenko primary bars' reading is FALSIFIED (primary series is 1-Minute)"),
    ("MIDDLE", 8, "OTRIMG-0150", "2026-06-05", "58%", N, "6", "", V, "the 14/6 pair"),
    ("MIDDLE", 9, "OTRIMG-0150", "2026-06-05", "58%", K, "checked", "", V, ""),
    ("MIDDLE", 10, "OTRIMG-0150", "2026-06-05", "58%", N, "30", "", V, "MOTIF-30-16-0"),
    ("MIDDLE", 11, "OTRIMG-0150", "2026-06-05", "58%", N, "16", "", V, "MOTIF-30-16-0"),
    ("MIDDLE", 12, "OTRIMG-0150", "2026-06-05", "58%", N, "0", "", V, "MOTIF-30-16-0"),
    ("MIDDLE", 13, "OTRIMG-0150", "2026-06-05", "58%", G, "UNREADABLE", "", V, ""),
    ("MIDDLE", 14, "OTRIMG-0150", "2026-06-05", "58%", N, "3", "", V,
     "quartet 3|0|12|0 - shape matches the two quartets 13|0|13|30 and 15|0|15|30 in 0138, "
     "i.e. an hour/minute pair repeated twice (INFERENCE, labels not visible)"),
    ("MIDDLE", 15, "OTRIMG-0150", "2026-06-05", "58%", N, "0", "", V, "quartet"),
    ("MIDDLE", 16, "OTRIMG-0150", "2026-06-05", "58%", N, "12", "", V, "quartet"),
    ("MIDDLE", 17, "OTRIMG-0150", "2026-06-05", "58%", N, "0", "", V, "quartet"),
    ("MIDDLE", 18, "OTRIMG-0150", "2026-06-05", "58%", G, "UNREADABLE", "", V, ""),
    ("MIDDLE", 19, "OTRIMG-0150", "2026-06-05", "58%", K, "C,U,C,C,U", "", V, "5-checkbox bank"),
    ("MIDDLE", 20, "OTRIMG-0150", "2026-06-05", "58%", N, "5", "", V, ""),
    ("MIDDLE", 21, "OTRIMG-0150", "2026-06-05", "58%", K, "checked", "", V, ""),

    # ---- VF-HEAD : the mutable rows directly above the VF13 block ---------------------------
    ("VF-HEAD", 1, "OTRIMG-0117", "2026-02-13", "89%", N, "clipped", "", V, "top-clipped"),
    ("VF-HEAD", 2, "OTRIMG-0117", "2026-02-13", "89%", K, "unchecked", "", V, ""),
    ("VF-HEAD", 3, "OTRIMG-0117", "2026-02-13", "89%", K, "checked", "", V, ""),
    ("VF-HEAD", 4, "OTRIMG-0117,0132,0136", "2026-02-13..04-17", "89%", N, "15", "", V,
     "the ONE value that persists directly above VF13 across Feb/Apr; gone by 2026-08-14"),
    ("VF-HEAD", 5, "OTRIMG-0132", "2026-04-02", "92%", N, "30?", "", V, "MOTIF-30-16-0"),
    ("VF-HEAD", 6, "OTRIMG-0132,0136", "2026-04-02/04-17", "92%", N, "16", "", V, "MOTIF-30-16-0"),
    ("VF-HEAD", 7, "OTRIMG-0132,0136", "2026-04-02/04-17", "92%", N, "0", "", V, "MOTIF-30-16-0"),
    ("VF-HEAD", 8, "OTRIMG-0132", "2026-04-02", "92%", N, "10", "", V, ""),
    ("VF-HEAD", 9, "OTRIMG-0136", "2026-04-17", "94%", N, "9", "", V,
     "0132 has 10 here, 0136 has 9 - a retune inside two weeks"),
    ("VF-HEAD", 10, "OTRIMG-0164", "2026-08-14", "95%", N, "15?", "", V,
     "AUGUST: only ONE numeric plus one checkbox sit above VF13"),
    ("VF-HEAD", 11, "OTRIMG-0164", "2026-08-14", "95%", K, "checked", "", V,
     "AUGUST: a checkbox now sits directly above Volume Base - the head SHAPE changed"),

    # ---- VF13 : the only custom block whose LABELS were ever photographed -------------------
    ("VF13", 1, "OTRIMG-0146 (labels); 9 frames (values)", "2026-02-13..08-14", "89-99%", E,
     "BidAskPrice_RealVolume", "Volume Base", L, ""),
    ("VF13", 2, "OTRIMG-0146 + 8", "2026-02-13..08-14", "89-99%", N, "60",
     "Anchor Period (Minutes)", L, ""),
    ("VF13", 3, "OTRIMG-0146 + 8", "2026-02-13..08-14", "89-99%", N, "5", "VWAP Amount", L, ""),
    ("VF13", 4, "OTRIMG-0146 + 8", "2026-02-13..08-14", "89-99%", N, "20", "Trend Period", L, ""),
    ("VF13", 5, "OTRIMG-0146 + 8", "2026-02-13..08-14", "89-99%", E, "EMA", "Trend MA Type", L, ""),
    ("VF13", 6, "OTRIMG-0146 + 8", "2026-02-13..08-14", "89-99%", N, "95", "Max Percent", L, ""),
    ("VF13", 7, "OTRIMG-0146 + 8", "2026-02-13..08-14", "89-99%", N, "75", "Upper Percent", L, ""),
    ("VF13", 8, "OTRIMG-0146 + 8", "2026-02-13..08-14", "89-99%", N, "50", "Median Percent", L, ""),
    ("VF13", 9, "OTRIMG-0146 + 8", "2026-02-13..08-14", "89-99%", N, "25", "Lower Percent", L, ""),
    ("VF13", 10, "OTRIMG-0146 + 8", "2026-02-13..08-14", "89-99%", N, "5", "Min Percent", L, ""),
    ("VF13", 11, "OTRIMG-0146 + 8", "2026-02-13..08-14", "89-99%", N, "3",
     "Signal Quantity Per Trend", L, ""),
    ("VF13", 12, "OTRIMG-0146 + 8", "2026-02-13..08-14", "89-99%", N, "10",
     "Signal Close Threshold (%)", L, "vendor universal preset is 70; his is 10"),
    ("VF13", 13, "OTRIMG-0146 + 8", "2026-02-13..08-14", "89-99%", N, "5",
     "Signal Split (Bars)", L, ""),

    # ---- PREVF-TAIL : the pre-VF build's terminal custom rows (Jan/Feb 2026) ----------------
    ("PREVF-TAIL", 1, "OTRIMG-0113,0115", "2026-01-30/02-06", "65-90%", N, "75", "", V, ""),
    ("PREVF-TAIL", 2, "OTRIMG-0113,0115", "2026-01-30/02-06", "65-90%", N, "20", "", V, ""),
    ("PREVF-TAIL", 3, "OTRIMG-0113,0115", "2026-01-30/02-06", "65-90%", N, "46", "", V, ""),
    ("PREVF-TAIL", 4, "OTRIMG-0113,0115", "2026-01-30/02-06", "65-90%", N, "30", "", V, ""),
    ("PREVF-TAIL", 5, "OTRIMG-0113,0115", "2026-01-30/02-06", "65-90%", K, "checked", "", V, ""),
    ("PREVF-TAIL", 6, "OTRIMG-0113,0115", "2026-01-30/02-06", "65-90%", K, "checked", "", V, ""),
    ("PREVF-TAIL", 7, "OTRIMG-0113,0115", "2026-01-30/02-06", "65-90%", G, "UNREADABLE", "", V, ""),
    ("PREVF-TAIL", 8, "OTRIMG-0113,0115", "2026-01-30/02-06", "65-90%", N, "1", "", V, ""),
    ("PREVF-TAIL", 9, "OTRIMG-0113,0115", "2026-01-30/02-06", "65-90%", G, "UNREADABLE", "", V, ""),
    ("PREVF-TAIL", 10, "OTRIMG-0113,0115", "2026-01-30/02-06", "65-90%", K, "checked", "", V, ""),
    ("PREVF-TAIL", 11, "OTRIMG-0113,0115", "2026-01-30/02-06", "65-90%", N, "80", "", V, ""),
    ("PREVF-TAIL", 12, "OTRIMG-0113,0115", "2026-01-30/02-06", "65-90%", G, "UNREADABLE", "", V, ""),
    ("PREVF-TAIL", 13, "OTRIMG-0113,0115", "2026-01-30/02-06", "65-90%", K, "checked", "", V, ""),
    ("PREVF-TAIL", 14, "OTRIMG-0113,0115", "2026-01-30/02-06", "65-90%", N, "0", "", V, ""),
    ("PREVF-TAIL", 15, "OTRIMG-0113,0115", "2026-01-30/02-06", "65-90%", N, "2", "", V, ""),
]

# NinjaTrader-8 standard tail: 26 rows, platform settings, NOT the trader's parameters.
NT8_TAIL = [
    ("Data Series", ["Instrument", "Price based on", "Type", "Value"], ["", "", "", "1"]),
    ("Time frame", ["Start date", "End date", "Trading hours", "Break at EOD"],
     ["", "", "", "checked"]),
    ("Setup", ["Include commission", "Commission template", "Maximum bars look back",
               "Bars required to trade"], ["UNCHECKED", "disabled/greyed", "", "20"]),
    ("Historical fill processing", ["Order fill resolution", "Fill limit orders on touch",
                                    "Slippage"], ["", "unchecked", "0"]),
    ("Order handling", ["Entries per direction", "Entry handling", "Exit on session close"],
     ["2", "", "checked"]),
    ("Order properties", ["Set order quantity", "Time in force"], ["", ""]),
]

FIELDS = ["block", "slot_index", "image_evidence", "capture_dates", "scroll_position",
          "control_type", "visible_value", "exact_visible_label", "label_evidence",
          "candidate_origin_1", "exact_label_match", "label_order_match",
          "control_type_match", "status", "note"]


def main():
    rows = []
    for blk, idx, img, dts, scr, ctrl, val, lab, ev, note in SLOTS:
        if ev == L:
            cand = "ninZa VWAP Flux (13/13 published labels, exact order)"
            st = "HIGH_CONFIDENCE_FAMILY_MATCH"
            elm, lom, ctm = "YES", "YES", "YES"
        else:
            cand, st, elm, lom, ctm = "", "UNEXPLAINED", "NO (label never photographed)", \
                "sequence recorded", "YES (recorded)"
        rows.append(dict(block=blk, slot_index=idx, image_evidence=img, capture_dates=dts,
                         scroll_position=scr, control_type=ctrl, visible_value=val,
                         exact_visible_label=lab, label_evidence=ev, candidate_origin_1=cand,
                         exact_label_match=elm, label_order_match=lom, control_type_match=ctm,
                         status=st, note=note))
    for grp, labels, vals in NT8_TAIL:
        rows.append(dict(block="NT8-TAIL", slot_index=0, image_evidence="0127,0134,0142,0146,0148,0159,0162",
                         capture_dates="2026-02..08", scroll_position="95-99%",
                         control_type=G, visible_value="", exact_visible_label=grp,
                         label_evidence=L, candidate_origin_1="NinjaTrader 8 platform",
                         exact_label_match="YES", label_order_match="YES", control_type_match="YES",
                         status="IDENTIFIED_PLATFORM_SETTING", note="standard group header"))
        for i, (lab, val) in enumerate(zip(labels, vals), 1):
            rows.append(dict(block="NT8-TAIL", slot_index=i,
                             image_evidence="0127,0134,0142,0146,0148,0159,0162",
                             capture_dates="2026-02..08", scroll_position="95-99%",
                             control_type=N if val.isdigit() else (K if "check" in val else E),
                             visible_value=val, exact_visible_label=lab, label_evidence=L,
                             candidate_origin_1="NinjaTrader 8 platform",
                             exact_label_match="YES", label_order_match="YES",
                             control_type_match="YES", status="IDENTIFIED_PLATFORM_SETTING",
                             note="identical values in every 2026 bottom-scrolled frame"))

    out = os.path.join(HERE, "ALL_VISIBLE_PARAMETER_ORIGIN_MATRIX.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)

    # ---------------- coverage arithmetic ----------------
    custom = [r for r in rows if r["block"] != "NT8-TAIL"]
    nt8 = [r for r in rows if r["block"] == "NT8-TAIL"]
    lab_ok = [r for r in custom if r["label_evidence"] == L]
    unexp = [r for r in custom if r["status"] == "UNEXPLAINED"]
    AUG_EXTENT, FEB_EXTENT, NT8_ROWS = 523, 218, 26

    print("=" * 76)
    print("PARAMETER COVERAGE - directive v5.0 section 53")
    print("=" * 76)
    print(f"distinct parameter SLOTS observed anywhere in the 2026 corpus : {len(rows)}")
    print(f"   of which NinjaTrader-8 platform settings                   : {len(nt8)}")
    print(f"   of which the trader's own CUSTOM slots                     : {len(custom)}")
    print(f"      with the LABEL photographed                             : {len(lab_ok)}")
    print(f"      value-only, label NEVER photographed                    : {len(unexp)}")
    print()
    print(f"August-2026 panel extent (measured)                           : ~{AUG_EXTENT} rows")
    print(f"   NinjaTrader standard tail                                  : {NT8_ROWS} rows")
    print(f"   therefore his CUSTOM rows in August                        : ~{AUG_EXTENT-NT8_ROWS}")
    print()
    print(f">>> custom rows with a photographed LABEL : {len(lab_ok)} / ~{AUG_EXTENT-NT8_ROWS}"
          f"  = {100*len(lab_ok)/(AUG_EXTENT-NT8_ROWS):.1f} %")
    print(f">>> custom rows photographed AT ALL       : {len(custom)} / ~{AUG_EXTENT-NT8_ROWS}"
          f"  = {100*len(custom)/(AUG_EXTENT-NT8_ROWS):.1f} %")
    print(f">>> custom rows NEVER photographed        : "
          f"~{AUG_EXTENT-NT8_ROWS-len(custom)} = "
          f"{100*(AUG_EXTENT-NT8_ROWS-len(custom))/(AUG_EXTENT-NT8_ROWS):.1f} %")
    print()
    print("Section 5 forbids identifying a component from numeric coincidence.  Every one of the")
    print(f"{len(unexp)} value-only slots therefore CANNOT reach LEVEL A on labels - the labels do")
    print("not exist in the corpus.  The only admissible route for them is a match on")
    print("CONTROL-TYPE SEQUENCE + GROUP-SEPARATOR POSITION + values, which is what the vendor")
    print("forensic pass must supply.  Control-type sequences per block:")
    seqs = {}
    for r in custom:
        seqs.setdefault(r["block"], []).append(r["control_type"][:4])
    for b, s in seqs.items():
        print(f"   {b:<12} n={len(s):>2}  {'|'.join(s)}")
    print(f"\nwritten: {out}")


if __name__ == "__main__":
    main()
