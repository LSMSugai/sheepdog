"""v11: diagnostic figure with A and B each in one row; steps named "A · step n" / "B · step n"."""
import json
from gen_v10 import *
from gen_panels import T, R, C, L, P, svg, W, arrow
from gen_v8 import note, NOTE, MONO

def ren(s, pairs):
    for a, b in pairs:
        assert a in s, a
        s = s.replace(a, b)
    return s

# ---------------- A · step 2: how the diagnosis is decided, and what to do with each label
def a_diag_act():
    b = []; Wd = 660
    note(b, 0, 14, "review_support() asks, in this order, one label per site × species; each label says what to do next")
    rows = [("any reviewed clip in the cell?", "n_reviewed = 0", "no", "not reviewed", "fsurf sline dash", "tm",
             ["draw clips for this cell", "↺ Figure 1 · step 2"]),
            ("did suggest_thresholds() find a cut?", "precision ≥ target, n_eff ≥ min_n", "yes", "reached", "f3", "finv",
             ["the threshold can be used:", "go to step 3"]),
            ("fewer than min_n high-score detections left?", "unreviewed_high < 15", "yes", "exhausted *", "fmuted", "finv",
             ["keep the clips: the model (B) may still", "give a threshold, or leave the cell out"]),
            ("precision at high scores below min_precision?", "prec_high < 0.5", "yes", "unreliable *", "fbad", "finv",
             ["the classifier is the limit: retrain it,", "then a new round ↺ Figure 1 · step 2"])]
    y = 30
    for i, (q, why, ans, lab, cls, tcls, act) in enumerate(rows):
        b.append(R(0, y, 262, 36, "fsurf sline", 6))
        b.append(T(10, y + 15, q, "ts tink", "start", 'style="font-size:10.6px"'))
        b.append(T(10, y + 29, why, "tc tm", "start", MONO))
        b.append(arrow(264, y + 18, 296, y + 18)); b.append(T(280, y + 13, ans, "tny tm", "middle"))
        b.append(R(300, y + 6, 112, 24, cls, 12)); b.append(T(356, y + 22, lab, "ts " + tcls, "middle"))
        b.append(arrow(416, y + 18, 432, y + 18))
        for k, a in enumerate(act): note(b, 438, y + 15 + k * 13, a)
        b.append(arrow(130, y + 38, 130, y + 56)); b.append(T(138, y + 50, "no" if ans == "yes" else "yes", "tny tm"))
        y += 60
    b.append(R(72, y, 116, 24, "f1", 12)); b.append(T(130, y + 16, "review more", "ts finv", "middle"))
    b.append(arrow(192, y + 12, 432, y + 12))
    for k, a in enumerate(["new random_detections round (same", "threshold, new seed) ↺ Figure 1 · step 2;", "stack all rounds (6.1), then A again"]):
        note(b, 438, y + 10 + k * 13, a)
    note(b, 72, y + 40, "high-score clips are left and precision is not yet bad")
    b.append(L(0, y + 56, Wd, y + 56, "sgrid"))
    note(b, 0, y + 72, "high score = confidence ≥ conf_high (0.7)")
    b.append(T(0, y + 88, "* retraining may help: see Stage 1 · Retraining", "ts fbadt", "start", 'style="font-size:10px"'))
    return svg(Wd, y + 96, "".join(b), "How review_support() decides the diagnosis, and the next step for each label")

# ---------------- A · step 3: enough data, and what can be done with the empirical threshold alone
def a_enough():
    b = []
    checks = ["☐ every cell you need is “reached” (or left out on purpose)",
              "☐ the threshold rests on ≥ min_n clips (n_eff) above the cut",
              "☐ for occupancy: a validation design at the same threshold"]
    b.append(R(0, 0, 440, 72, "fs1 st1", 8))
    for k, c in enumerate(checks): note(b, 12, 20 + k * 19, c)
    b.append(arrow(220, 76, 220, 96, "ar1")); b.append(T(228, 90, "all met", "tny f1t"))
    exits = [("Community matrices", "f3t", "fs3 st3", ["detection history built by hand", "from the threshold (score ≥ cut,", "k detections per night), then", "community_matrices() (Stage 3)"]),
             ("Occupancy with false positives", "f4t", "fs4 st4", ["export_occupancy_data(), then in", "crywolf: fp_read_sheepdog() →", "fp_aggregate(threshold = cut);", "crywolf estimates the false positives"])]
    for i, (t, tc, cls, ls) in enumerate(exits):
        x = i * 224
        b.append(R(x, 100, 216, 100, cls, 8))
        b.append(T(x + 10, 118, t, "ts " + tc))
        for k, l in enumerate(ls): b.append(T(x + 10, 136 + k * 13, l, "ts", "start", 'style="font-size:9.8px" opacity=".85"'))
    b.append(L(0, 214, 440, 214, "sgrid"))
    note(b, 0, 232, "not yet → back to step 2 · no model: the threshold holds for the set of")
    note(b, 0, 245, "kept detections, not for each one (see B for the model-based route)")
    return svg(W, 254, "".join(b), "Enough data to continue, and what the empirical threshold can feed")

out["d7a2m"] = a_diag_act()
out["d7a4"] = a_enough()
out["d7b1"] = ren(out["d7b1"], [("calibration_quality.csv (7B.2)", "calibration_quality.csv (step 2)")])
out["d7b3"] = ren(out["d7b3"], [("only for species “ok” in 7B.2", "only for species “ok” in step 2"),
                                 ("asks the 7A question instead", "asks the A question instead")])
out["d7b4"] = ren(out["d7b4"], [("use the threshold from 7B.3, or go on to", "use the threshold from step 3, or go on to"),
                                 ("or use the empirical threshold (7A) for it", "or use the empirical threshold (A) for it"),
                                 ("7B gives no review_support() diagnosis", "B gives no review_support() diagnosis")])
out["d7cmp"] = ren(out["d7cmp"], [("same cells: 7A against 7B run with", "same cells: A against B run with"),
                                   ("7A threshold (empirical)", "A threshold (empirical)"),
                                   ("7B threshold (model)", "B threshold (model)"),
                                   ("7A stays as the check", "A stays as the check"),
                                   ("7B higher: pooling", "B higher: pooling"), ("curve; 7A higher", "curve; A higher"),
                                   ("(7A.3, 7B.4)", "(A step 2, B step 4)"),
                                   ("7B with P(tp) 0.95 asks", "B with P(tp) 0.95 asks"),
                                   ("higher than 7A at 0.90", "higher than A at 0.90")])
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok v11")
