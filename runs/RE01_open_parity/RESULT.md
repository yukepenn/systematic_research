# RE01 — open reconstruction vs vendor baseline: PASS

| Metric | Vendor (frozen canonical) | SolarWaveOpenV1 (no vendor code) | Delta |
|---|---|---|---|
| Net profit | $146,440.60 | $146,440.60 | $0.00 |
| Trades | 2,915 | 2,915 | 0 |
| Max drawdown | −$22,066.60 | −$22,066.60 | $0.00 |
| Profit factor | 1.132213 | 1.1322134 | 0 |
| Commission | $12,709.40 | $12,709.40 | $0.00 |
| Serialized trades | 2,914 | 2,914 | 0 (known boundary quirk) |

Side split (new detail, identical engine): long 1,386 trades / $103,162.04 / PF 1.1994 / Sharpe 0.673;
short 1,529 trades / $43,278.56 / PF 1.0733 / Sharpe 0.1245. The long side carries this window.

**Conclusion.** The Solar Wave RK Type-1 core is fully reconstructed from first principles.
The licensed vendor assembly is no longer required for any research in this campaign.
