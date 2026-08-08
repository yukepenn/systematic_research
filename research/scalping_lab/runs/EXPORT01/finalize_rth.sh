#!/bin/bash
cd "D:/OneDrive - Washington University in St. Louis/TradingResearch/systematic_research"
B="research/scalping_lab/runs/EXPORT01/out"
SECONDS=0
until [ $(ls "$B" 2>/dev/null | grep -c "_rth_ticks.csv") -ge 13 ]; do sleep 20; if [ $SECONDS -gt 900 ]; then break; fi; done
sleep 30
python research/scalping_lab/src/python/csv_to_parquet.py >> research/scalping_lab/runs/EXPORT01/convert_log.txt 2>&1
echo "RTH files converted: $(grep -c _rth research/scalping_lab/substrate/MANIFEST.csv)"
