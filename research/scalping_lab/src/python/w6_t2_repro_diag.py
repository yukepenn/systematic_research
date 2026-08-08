"""W6-T2 reproduction diagnostic (supplement to w6_t2_ceiling_es.py).

Purpose: attribute the T2 run-(a) reproduction-tolerance breach (2/8 cells,
both HGB). Hypothesis: the pipeline construction is IDENTICAL to C5 and the
breach is caused solely by the frozen same-sample rule (818 ES-feature-NaN
rows dropped) interacting with HGB's sample-sensitive internal early-stopping
split. Test: rebuild the dataset WITHOUT the ES-NaN drop (= the exact C5
sample, 27299 rows) and run all 8 label/model cells with identical folds,
models, seeds, and lift/CI machinery. If results match the original C5
metrics (near-)exactly, the re-implementation is proven faithful and the T2
breach is fully explained by the frozen sample rule, not a construction flaw.

No perm importance / calibration here (not needed for the attribution).
Output: t2_repro_diagnostic.csv + t2_diag_stdout.txt in artifacts/w6_fss10/.
"""
import os, sys, glob
import numpy as np, pandas as pd

sys.path.insert(0, os.path.join("research", "scalping_lab", "src", "python"))
from w6_t2_ceiling_es import (build_session, make_models, lift_with_ci, brier,
                              LABELS, NQ_FEATS, C1_GAP, MINHIST, NFOLDS, SH,
                              OUTD, C5M)


def main():
    print("W6-T2 repro diagnostic: run (a) pipeline on the FULL C5-equivalent "
          "sample (no ES-NaN drop)")
    sessions = sorted(os.path.basename(p)[:-8]
                      for p in glob.glob(os.path.join(SH, "s*.parquet")))
    frames = []
    for tag in sessions:
        R, _, _, _ = build_session(tag)
        if R is None:
            print(tag, "SKIPPED (quote-dead)", flush=True)
            continue
        frames.append(R)
    D = pd.concat(frames, ignore_index=True)
    D = D[D["t"] >= MINHIST]
    D = D.dropna(subset=NQ_FEATS).reset_index(drop=True)
    print(f"modeling rows (C5-equivalent, ES-NaN rows KEPT): {len(D)} "
          f"(original C5: 27299)")
    assert len(D) == 27299, "full-sample row count does not match C5"

    blocks = [list(b) for b in np.array_split(np.array(sessions), NFOLDS)]
    folds = []
    for v in range(1, NFOLDS):
        tr = [s for b in blocks[:v] for s in b]
        va = blocks[v]
        assert len(set(tr) & set(va)) == 0
        assert max(tr) < min(va)
        folds.append((v, tr, va))

    c5 = pd.read_csv(C5M).set_index(["label", "model"])
    rows = []
    for dname, dv, A, B in LABELS:
        lc = f"lab_{dname}_{A}_{B}"
        lab_id = f"{dname}_{A}_{B}"
        sub = D[D[lc] >= 0]
        for mname in make_models().keys():
            preds = []
            for v, tr, va in folds:
                trd = sub[sub["session"].isin(tr)]
                vad = sub[sub["session"].isin(va)]
                model = make_models()[mname]
                model.fit(trd[NQ_FEATS].values.astype(np.float64),
                          (trd[lc] == 1).values.astype(int))
                p = model.predict_proba(
                    vad[NQ_FEATS].values.astype(np.float64))[:, 1]
                preds.append(pd.DataFrame(dict(
                    session=vad["session"].values, fold=v,
                    y=(vad[lc] == 1).values.astype(int), p=p,
                    base_tr=(trd[lc] == 1).mean())))
            P = pd.concat(preds, ignore_index=True)
            top = np.zeros(len(P), bool)
            for v, _, _ in folds:
                m = P["fold"].values == v
                thr = np.quantile(P.loc[m, "p"].values, 0.9)
                top[m & (P["p"].values >= thr)] = True
            res = lift_with_ci(P[["session", "y"]], top)
            bri = brier(P["y"].values, P["p"].values)
            bri_base = brier(P["y"].values, P["base_tr"].values)
            skill = 1 - bri / bri_base
            k = (lab_id, mname)
            dl = res["lift"] - c5.loc[k, "lift"]
            dk = skill - c5.loc[k, "brier_skill"]
            rows.append(dict(label=lab_id, model=mname, n_val=res["n_all"],
                             lift_full=res["lift"], lift_c5=c5.loc[k, "lift"],
                             dlift=dl, skill_full=skill,
                             skill_c5=c5.loc[k, "brier_skill"], dskill=dk,
                             n_val_c5=int(c5.loc[k, "n_val"]),
                             exact=abs(dl) < 1e-9 and abs(dk) < 1e-9))
            print(f"  {lab_id:12s} {mname:5s} lift full-sample "
                  f"{100*res['lift']:+.4f}pp vs C5 "
                  f"{100*c5.loc[k,'lift']:+.4f}pp (d {100*dl:+.4f}pp) | "
                  f"skill {skill:+.6f} vs {c5.loc[k,'brier_skill']:+.6f} "
                  f"(d {dk:+.6f}) | n {res['n_all']} vs "
                  f"{int(c5.loc[k,'n_val'])}")
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(OUTD, "t2_repro_diagnostic.csv"), index=False)
    n_exact = int(R["exact"].sum())
    mx = R["dlift"].abs().max()
    print(f"\nexact-match cells: {n_exact}/8 | max |dlift| "
          f"{100*mx:.4f}pp | max |dskill| {R['dskill'].abs().max():.6f}")
    if mx < 1e-6:
        print("DIAGNOSTIC CONCLUSION: on the identical sample the pipeline "
              "reproduces C5 EXACTLY -> the T2 run-(a) tolerance breach is "
              "fully attributable to the frozen same-sample rule (818 "
              "ES-NaN rows) x HGB sample sensitivity, NOT a construction "
              "flaw.")
    elif mx < 0.005:
        print("DIAGNOSTIC CONCLUSION: on the identical sample the pipeline "
              "matches C5 to <0.5pp in every cell -> construction faithful; "
              "T2 breach attributable to the frozen same-sample rule x HGB "
              "sample sensitivity.")
    else:
        print("DIAGNOSTIC CONCLUSION: residual mismatch on the identical "
              "sample -> a construction difference DOES exist; the T2 stop "
              "stands and the difference must be found before any FSS-10 "
              "ruling.")
    print("W6T2-DIAG DONE")


if __name__ == "__main__":
    main()
