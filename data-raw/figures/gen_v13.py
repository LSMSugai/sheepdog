"""v13: B · step 5, what comes after the model-based route (community matrices or occupancy)."""
import json
from gen_v12 import *
from gen_panels import T, R, C, L, P, svg, arrow
from gen_v8 import note, NOTE, MONO

def b5():
    b = []; Wd = 900
    note(b, 0, 14, "species marked ok in step 2 · the routes are compared in “Routes to detection histories and occupancy”")
    def tagl(x, y, txt, cls):
        b.append(R(x, y - 10, len(txt) * 6.2 + 12, 15, cls, 7)); b.append(T(x + 6, y + 1, txt, "tny finv"))
    # community matrices
    b.append(R(0, 28, 444, 236, "fs3 st3", 10))
    b.append(T(14, 50, "Community matrices (Stage 3)", "ts f3t"))
    ways = [("way 1", "detection_history(rule = \"mean\")", "lme4 or brms", "P(tp) ≥ 0.95 under the fitted curve"),
            ("way 2", "detection_history(rule = \"probability\",", "brms", "prob_min = 0.9): cautious where review was thin"),
            ("way 3", "history_draws() → community_matrices_draws()", "brms", "one history per draw: mean and interval per cell")]
    y = 74
    for w, f, eng, d in ways:
        b.append(T(14, y, w, "tc f2t")); b.append(T(64, y, f, "tc tink", "start", MONO))
        b.append(T(64, y + 13, d, "ts", "start", 'style="font-size:9.6px"'))
        tagl(344, y, eng, "f2")
        y += 36
    b.append(L(14, y - 8, 430, y - 8, "sgrid"))
    b.append(T(14, y + 10, "then", "ts tink"))
    note(b, 48, y + 10, "cell_status() → suggest_core_species() → community_matrices()")
    note(b, 48, y + 24, "(frequency, counts, effort, trials) → vegan or gllvm")
    # occupancy
    x0 = 456
    b.append(R(x0, 28, 444, 236, "fs4 st4", 10))
    b.append(T(x0 + 14, 50, "Occupancy with false positives (crywolf)", "ts f4t"))
    b.append(T(x0 + 14, 74, "threshold", "tc f2t"))
    b.append(T(x0 + 90, 74, "calibrated_thresholds() (or threshold_lower)", "tc tink", "start", MONO))
    b.append(T(x0 + 90, 87, "→ export_occupancy_data() without fit", "tc tink", "start", MONO))
    b.append(T(x0 + 90, 100, "→ fp_aggregate(threshold = score)", "tc tink", "start", MONO))
    tagl(x0 + 344, 74, "lme4 or brms", "f2")
    b.append(T(x0 + 14, 128, "draws", "tc f2t"))
    b.append(T(x0 + 90, 128, "export_occupancy_data(fit = brms fit)", "tc tink", "start", MONO))
    b.append(T(x0 + 90, 141, "→ fp_draws_data(rule = \"sample\")", "tc tink", "start", MONO))
    b.append(T(x0 + 90, 154, "→ fp_occu_mc(): one fit per draw, pooled", "tc tink", "start", MONO))
    tagl(x0 + 344, 128, "brms", "f2")
    b.append(L(x0 + 14, 170, x0 + 430, 170, "sgrid"))
    for k, c in enumerate(["a random validation design at the same threshold", "(random_detections) and/or random_recordings",
                           "a calibration without a site effect, or local", "prevalence is counted twice"]):
        note(b, x0 + 14, 190 + k * 14, ("☐ " if k in (0, 2) else "   ") + c)
    return svg(Wd, 272, "".join(b), "After the model-based route: community matrices or occupancy")

out["d7b5"] = b5()
out["d7b4"] = out["d7b4"].replace("or go on to Stage 2 · Calibration", "then step 5 (what comes next)").replace("(routes way 1–3)", "")
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok v13")
