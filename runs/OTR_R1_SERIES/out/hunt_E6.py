"""Family E step 6: split events into REVERSAL vs FRESH (per true sequence) and
brute-force separators for each subgroup independently."""
import csv, json
import numpy as np

X = np.load("hunt_E_X.npy")
y = np.load("hunt_E_y.npy")
mj = json.load(open("hunt_E_meta.json"))
fn = mj["feat_names"]; meta = mj["meta"]

labels = []
with open("r12f_flip_features.csv", newline="") as f:
    for row in csv.DictReader(f):
        labels.append(row)

# assign fresh/rev per TRUE sequence: rev iff previous labeled flip in the SAME session
# was TAKEN. Special case: 01-17 session L@07:21 is REV (missing short in position).
is_rev = []
prev_day = None; prev_taken = False
for row in labels:
    day = row["session_end_day"]
    if day != prev_day:
        prev_day = day
        prev_taken = day == "2023-01-17"  # missing short in position before L@07:21
    is_rev.append(prev_taken)
    prev_taken = row["label"] == "TAKE"
is_rev = np.array(is_rev)

cert = np.array([r["certainty"] for r in labels])
hardm = cert == "HARD"

for gname, gmask in [("REVERSAL", is_rev), ("FRESH", ~is_rev)]:
    print(f"\n########## {gname} events: {gmask.sum()} (skips {y[gmask].sum()})")
    for k in np.where(gmask)[0]:
        if y[k]:
            print("   SKIP", meta[k][0], meta[k][1], meta[k][3],
                  "mod", X[k, fn.index('mod')], "leg", X[k, fn.index('leg_bars')])
    Xg, yg, cg = X[gmask], y[gmask], cert[gmask]
    hg = cg == "HARD"
    # single predicates
    print("--- single predicates, 0 errors:")
    found = 0
    for j, name in enumerate(fn):
        vals = np.unique(Xg[:, j])
        thrs = (vals[:-1] + vals[1:]) / 2
        for t in thrs:
            for m, op in [(Xg[:, j] <= t, "<="), (Xg[:, j] > t, ">")]:
                if np.array_equal(m, yg == 1):
                    print(f"   SKIP iff {name} {op} {t:.3f}")
                    found += 1
    if found == 0:
        print("   (none)")
    # pairs
    print("--- conjunction pairs, 0 errors (max 25 shown):")
    preds = []
    for j, name in enumerate(fn):
        vals = np.unique(Xg[:, j])
        thrs = (vals[:-1] + vals[1:]) / 2
        if len(thrs) > 40:
            thrs = np.unique(np.quantile(Xg[:, j], np.linspace(0.02, 0.98, 41)))
        for t in thrs:
            preds.append((j, "<=", t, Xg[:, j] <= t))
            preds.append((j, ">", t, Xg[:, j] > t))
    skips = yg == 1
    cands = [p for p in preds if p[3][skips].all()]
    shown = 0; seen = set()
    res = []
    for a in range(len(cands)):
        ja, opa, ta, ma = cands[a]
        for b in range(a + 1, len(cands)):
            jb, opb, tb, mb = cands[b]
            if ja == jb:
                continue
            m = ma & mb
            if np.array_equal(m, skips):
                res.append((fn[ja], opa, ta, fn[jb], opb, tb))
    for r in res:
        key = (r[0], r[3])
        if key in seen:
            continue
        seen.add(key)
        print(f"   SKIP iff {r[0]} {r[1]} {r[2]:.3f} AND {r[3]} {r[4]} {r[5]:.3f}")
        shown += 1
        if shown >= 25:
            break
    if not res:
        print("   (none) — best near-misses:")
        best = []
        for a in range(len(preds)):
            ja, opa, ta, ma = preds[a]
            for b in range(a + 1, len(preds)):
                jb, opb, tb, mb = preds[b]
                if ja == jb:
                    continue
                m = ma & mb
                errs = m != skips
                he = errs[hg].sum(); oe = errs[~hg].sum()
                best.append((he, oe, fn[ja], opa, ta, fn[jb], opb, tb))
        best.sort()
        seen2 = set()
        sh = 0
        for r in best:
            key = (r[2], r[5])
            if key in seen2:
                continue
            seen2.add(key)
            print("  ", r[:2], r[2], r[3], round(r[4], 2), "AND", r[5], r[6], round(r[7], 2))
            sh += 1
            if sh >= 15:
                break
