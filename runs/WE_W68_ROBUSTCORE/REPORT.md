# WE_W68 — LEANING LESS ON THE FRAGILE HALF · REPORT

Preregistered, with the trap named in the spec before running and a new adoption clause added
for this wave. **Nothing adopted. The preregistered falsifier fired, and one of my own earlier
explanations is corrected.**

---

## 1. `CORRECTION` — W66's wider ladder does NOT strengthen the Solar side

W68's spec justified testing the 18-member ladder because it *"strengthens the SOLAR side"*.
Measured directly, with the B-MOM term switched off:

| | Solar only (w_bmom = 0) |
|---|---|
| 13-member ladder | **7.26 pts/session** |
| 18-member ladder | **7.25 pts/session** |

**Identical.** Extending the ladder to VolMult 40 adds nothing to the Solar engine. Whatever
C2r's 26 %-smaller drawdown distribution comes from, it comes from **how a wider consensus
interacts with B-MOM's OR-gate** — not from a better trend signal. My stated motivation was
wrong and is withdrawn.

## 2. Phase 1 — the cross, with the fragility column that decides it

`BMOM%` = share of net from entries the member consensus alone would not have made.

| arm | trades | pts | week + % | wk streak | median week | weekly $ | mean top-5 DD | worst week | **BMOM %** |
|---|---|---|---|---|---|---|---|---|---|
| **ladder13 w=2.83 — incumbent** | 1,942 | **14.86** | 58.3 | 8 | $455 | **$1,475** | $14,266 | −$7,418 | 27.6 |
| ladder13 w=2.00 | 1,986 | 13.41 | 58.8 | 8 | $311 | $1,117 | $10,720 | −$5,786 | **28.8** |
| ladder13 w=0 (Solar only) | 1,841 | 7.26 | 53.9 | 8 | $153 | $891 | $15,020 | −$10,746 | 0 |
| **ladder18 w=2.83 (C2r)** | 1,930 | 14.80 | 56.9 | **6** | **$634** | $1,350 | **$10,521** | −$7,038 | 27.9 |
| ladder18 w=2.00 | 1,964 | 11.55 | 54.4 | 6 | $201 | $806 | **$9,925** | **−$4,941** | **16.9** |
| ladder18 w=0 | 1,772 | 7.25 | 49.0 | **4** | $0 | $943 | $12,590 | −$7,966 | 0 |

Two things the fragility column caught that the other columns hid:

- **C2r does not reduce the dependence at all** (27.9 % vs the incumbent's 27.6 %). It is a
  different tuning of the same fragile structure, not a robustness improvement. **It fails the
  wave's B-MOM clause**, which existed precisely for this.
- **Lowering w_bmom on the 13-member ladder RAISES the B-MOM share** (27.6 % → 28.8 %). Only on
  the 18-member ladder does it fall (27.9 % → 16.9 %) — and that arm costs **45 % of weekly
  dollars at a fixed drawdown**.

## 3. Phase 2 — the consensus threshold k, aggregated

W67 proved the Solar side reduces to *"at least k of NMEM net-long"*. Questioned by aggregating
over neighbours, never by selecting:

| arm | pts | week + % | wk streak | median week | weekly $ | mean top-5 DD | Ulcer | BMOM % |
|---|---|---|---|---|---|---|---|---|
| incumbent | 14.86 | 58.3 | 8 | $455 | $1,475 | $14,266 | $6,183 | 27.6 |
| ladder13 k-aggregate {5,6,7} | 11.69 | 54.9 | 6 | $295 | $760 | $12,489 | $4,606 | 49.5 |
| **ladder18 k-aggregate {7,8,9}** | **15.55** | 55.4 | **5** | $557 | **$1,479** | $15,230 | **$4,969** | 27.7 |

The 18-member k-aggregate matches the incumbent's weekly dollars, cuts the Ulcer index 20 % and
the longest weekly losing streak from 8 to 5 — and its per-year profile is the flattest thing
this campaign has produced:

| | 2022 | **2023** | 2024 | 2025 | **2026** |
|---|---|---|---|---|---|
| incumbent | 11.59 | **3.04** | 19.59 | 23.17 | 15.79 |
| ladder18 k-aggregate | 15.60 | **12.46** | 10.94 | 14.93 | **35.80** |

**It fixes 2023 (4×) and 2026 (2.3×) and gives back 2024 and 2025.** It wins 3 of 5 years and
scores 18 % on the rolling all-three test — below C2r's 23 %. And 2026 is only 106 sessions, so
that 35.80 is the thinnest number on the page.

## 4. Phase 3 — the tilt is already at a local optimum (`FACT`)

The 50-session tilt multiplier, never examined in 67 waves:

| | pts | week + % | median week | weekly $ | mean top-5 DD |
|---|---|---|---|---|---|
| tilt OFF (×1.0) | 13.44 | 56.9 | $437 | $1,107 | $13,003 |
| **×1.25 — the vendor's** | **14.86** | **58.3** | $455 | **$1,475** | $14,266 |
| ×1.5 | 13.87 | 58.3 | $350 | $1,332 | $14,395 |

**The inherited 1.25 is the best of the three.** The tilt is worth about 1.4 pts/session (≈10 %)
and its constant needs no change. That is worth recording plainly: questioning an inherited
parameter and finding it already right is a result, not a null day.

## 5. The falsifier, fired

The spec said: *"if leaning less on B-MOM costs more production than it saves in drawdown at
every weight, the recorded conclusion is that the object's dependence on an in-sample component
is not reducible from inside, and the disclosure stands as the deliverable."*

That is what happened. **Every arm that improves the numbers does so through B-MOM's OR-gate,
and the only arm that genuinely reduces the B-MOM share (ladder18 w=2.00, 16.9 %) gives up 45 %
of weekly dollars at a fixed drawdown.**

> `RECORDED`: **the object's dependence on B-MOM is not reducible from inside the object.** Half
> its net comes from a component this repo has independently judged regime-local twice, and
> nothing in the ladder, the consensus threshold, the tilt or the B-MOM weight buys that
> dependence down at an acceptable price. The disclosure — not a fix — is the deliverable.

## 6. What is now known about every constant in the object

| constant | status after W66–W68 |
|---|---|
| VolMult ladder ends and density | extending up helps the drawdown *distribution* but does not strengthen Solar and does not reduce fragility; the gain is generically "more members" (W66 null) |
| σ window 460 | diversifying the **timescale** does not help — most combinations win 0 % of rolling windows |
| S clamp 40/1200 ticks | dimensionally inconsistent **and load-bearing**; removing it makes every consistency metric worse. The vendor's floor protects the fast members in low volatility |
| ×10, 0.9026, 0.7086 | **inert** — they cancel out of the decision |
| ±13 clamp on Tp | **dead code**, unreachable |
| tilt ×1.25 | **already optimal** of {1.0, 1.25, 1.5} |
| consensus k = 6 of 13 | live; aggregating neighbours on 18 members flattens the year profile and costs 2024–25 |
| **B-MOM weight 2.83** | **the largest lever in the object and its largest risk** |
| hysteresis 3.0 / 1.0 | equivalent to the consensus threshold — same lever, different units |

## 7. Files
`out/robust.txt` `out/cross.csv` `out/consensus.csv` `out/tilt.csv` ·
code `research/weekly_edge/src/run_we_w68.py`
