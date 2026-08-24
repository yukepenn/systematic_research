"""Family E step 3: print feature table for skips + contrast takes; look for separator."""
import json
import numpy as np

X = np.load("hunt_E_X.npy")
y = np.load("hunt_E_y.npy")
m = json.load(open("hunt_E_meta.json"))
fn = m["feat_names"]; meta = m["meta"]

focus = [
    # all skips
    "2023-01-03T12:37:00", "2023-01-03T13:28:00",
    "2023-01-04T13:25:00", "2023-01-04T14:07:00", "2023-01-04T14:11:00",
    "2023-01-04T14:18:00", "2023-01-04T14:25:00",
    "2023-01-04T21:07:00", "2023-01-04T23:36:00",
    "2023-01-05T12:21:00", "2023-01-05T13:24:00", "2023-01-05T14:16:00",
    "2023-01-08T18:02:00",
    "2023-01-12T13:39:00", "2023-01-12T19:17:00",
    # contrast takes
    "2023-01-02T21:39:00", "2023-01-03T12:48:00", "2023-01-03T16:04:00",
    "2023-01-03T20:14:00", "2023-01-04T14:04:00", "2023-01-04T14:49:00",
    "2023-01-04T15:24:00", "2023-01-05T19:33:00", "2023-01-12T14:54:00",
    "2023-01-12T20:36:00", "2023-01-17T18:04:00", "2023-01-17T21:42:00",
    "2023-01-18T13:54:00", "2023-01-19T15:34:00", "2023-01-19T16:03:00",
    "2023-01-16T12:54:00",
]
cols = ["mod", "dir", "prevclose_dist", "vwap_dist", "sessopen_dist",
        "hh_flip", "hh_ext", "vs_last_exit_same", "vs_last_entry_same",
        "vs_last_exit_any", "leg_ret_signed", "leg_amp", "leg_bars",
        "mom60", "mom120", "range240", "atr60", "dist_sess_ext_fav",
        "sess_range_pos", "slow2_al", "slow3_al", "htf15_al", "htf30_al",
        "slow2_tvd", "wave_prev", "weak_prev", "n_t2_early", "gap_next"]
ci = [fn.index(c) for c in cols]
idx = {t: k for k, (t, d, l, c) in enumerate(meta)}
print(("time".ljust(17) + "lab cert " + " ".join(c[:9].rjust(9) for c in cols)))
for t in focus:
    k = idx[t]
    tt, d, lab, cert = meta[k]
    row = " ".join(f"{X[k, j]:9.2f}" for j in ci)
    print(f"{t[5:16]:<17}{('SKIP' if y[k] else 'take'):<4}{cert:<5}{d} {row}")
