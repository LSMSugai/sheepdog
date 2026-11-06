"""v6: step 6 = review_support() (empirical threshold + diagnosis, with suggest_thresholds() inside);
step 7 = model-based threshold with calibrated_thresholds()."""
import json, re
from gen_v5 import out, emphasise_optional
from gen_panels import T, R, C, L, P, svg, W, badge, arrow, logistic, logit

NOTE = 'font-size="10.5" opacity=".85"'
def note(b, x, y, s): b.append(T(x, y, s, "ts", "start", NOTE))

def s1c():
    b = []
    b.append(badge(8, 12, 7)); b.append(T(22, 16, "review_support()", "tc f1t", "start", 'font-size="12"'))
    note(b, 140, 16, "target_precision · min_n · conf_high · min_precision")
    note(b, 140, 29, "defaults 0.90 · 15 · 0.7 · 0.5")
    b.append(T(0, 42, "inside, for each site × species:", "ts tink"))
    # left box: suggest_thresholds
    b.append(R(0, 48, 212, 150, "fsurf sline", 6))
    b.append(T(10, 66, "suggest_thresholds()", "tc f1t"))
    note(b, 10, 80, "precision of the clips ≥ each cut")
    x0, x1, y0, y1 = 30, 200, 182, 92
    X = lambda c: x0 + (c - .1) / .9 * (x1 - x0); Y = lambda p: y0 - p * (y0 - y1)
    for p in (0, .5, 1):
        b.append(L(x0, Y(p), x1, Y(p), "sgrid")); b.append(T(x0 - 4, Y(p) + 3, f"{p:g}", "tc", "end", 'font-size="9"'))
    cum = [.58, .62, .67, .72, .78, .84, .91, .94, .97]
    pts = [(X(.1 + i * .1), Y(p)) for i, p in enumerate(cum)]
    b.append(P("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts), "nofill st1 w2"))
    for x, y in pts: b.append(C(x, y, 2.2, "f1"))
    b.append(L(x0, Y(.9), x1, Y(.9), "stink dash")); b.append(T(x0 + 2, Y(.9) - 4, "0.90", "tc tink", "start", 'font-size="9"'))
    b.append(L(X(.7), Y(.9), X(.7), Y(0), "st1 w15")); b.append(T(X(.7) + 3, Y(.25), "0.70", "tc f1t", "start", 'font-size="9"'))
    b.append(T(X(.55), y0 + 12, "score", "tc", "middle", 'font-size="9"'))
    # right box: high-score check -> diagnosis
    b.append(R(226, 48, 214, 150, "fsurf sline", 6))
    b.append(T(236, 66, "high-score check", "ts tink"))
    note(b, 236, 80, "clips ≥ conf_high: n_high, prec_high")
    note(b, 236, 93, "not yet reviewed: unreviewed_high")
    rules = [("f3", "threshold found → reached"), ("fbad", "low prec_high → unreliable"),
             ("fmuted", "< min_n left → exhausted"), ("f1", "otherwise → review more"),
             ("fsurf sline dash", "no reviewed clip → not reviewed")]
    for k, (cls, txt) in enumerate(rules):
        y = 110 + k * 17
        b.append(R(236, y - 9, 10, 10, cls, 2)); note(b, 252, y, txt)
    # arrows down to output
    b.append(arrow(106, 200, 106, 222, "ar1")); b.append(arrow(332, 200, 332, 222, "ar1"))
    # output: printed tibble, as in the R console
    b.append(T(0, 238, "output (printed in R):", "ts tink"))
    b.append(R(0, 246, 440, 120, "fs1", 6))
    mono = 'style="font-size:8.4px"'
    b.append(T(8, 262, "# A tibble: 16 × 11", "tc tm", "start", mono))
    cols = [("site", 8), ("species_folder", 34), ("n_high", 116), ("prec_high", 154),
            ("unreviewed_high", 206), ("threshold", 292), ("diagnosis", 346)]
    for name, x in cols: b.append(T(x, 278, name, "tc tink", "start", mono))
    rows = [("ARA", "boa_ran", "24", "0.95", "3", "0.70", "reached", "f3t"),
            ("ARA", "den_nan", "18", "0.83", "21", "NA", "review more", "f1t"),
            ("BAI", "sci_nas", "15", "0.80", "2", "NA", "exhausted", "tm"),
            ("ARA", "pse_pla", "20", "0.30", "35", "NA", "unreliable", "fbadt"),
            ("NHE", "sci_nas", "0", "NA", "8", "NA", "not reviewed", "tm")]
    for r, row in enumerate(rows):
        y = 294 + r * 13
        for k, (name, x) in enumerate(cols):
            v = row[k]
            cls = row[7] if name == "diagnosis" else ("f1t" if name == "threshold" and v != "NA" else "tc")
            b.append(T(x, y, v, "tc " + cls, "start", mono))
    b.append(T(8, 360, "# … 11 more rows; also n_reviewed, n_fp, n_high_all", "tc tm", "start", mono))
    b.append(L(0, 372, 440, 372, "sgrid"))
    note(b, 0, 388, "threshold is filled only where diagnosis = reached; values are illustrative")
    return svg(W, 396, "".join(b), "review_support(): empirical threshold and diagnosis per site and species")

def s1d():
    b = []
    b.append(badge(8, 12, 7, color="2")); b.append(T(22, 16, "calibrated_thresholds()", "tc f2t", "start", 'font-size="12"'))
    note(b, 196, 16, "via calibrate(): fits and checks the")
    note(b, 196, 29, "stage 2 model, then reads its curve")
    x0, x1, y0, y1 = 40, 420, 200, 56
    X = lambda c: x0 + (c - .1) / .9 * (x1 - x0); Y = lambda p: y0 - p * (y0 - y1)
    for p in (0, .5, 1):
        b.append(L(x0, Y(p), x1, Y(p), "sgrid")); b.append(T(x0 - 5, Y(p) + 4, f"{p:g}", "tc", "end"))
    for c in (.1, .5, 1): b.append(T(X(c), y0 + 15, f"{c:g}", "tc", "middle"))
    b.append(T((x0 + x1) / 2, y0 + 30, "confidence score", "ts", "middle"))
    b.append(T(x0 - 30, y1 - 12, "P(tp) from the model", "ts"))
    a_, b_ = .6, 1.7
    ss = [0.1 + i * .89 / 60 for i in range(61)]
    b.append(P("M" + " L".join(f"{X(s):.1f} {Y(logistic(a_ + b_ * logit(s))):.1f}" for s in ss), "nofill st2 w25"))
    thr = logistic((logit(.95) - a_) / b_)
    b.append(L(x0, Y(.95), x1, Y(.95), "stink dash")); b.append(T(x0 + 4, Y(.95) - 5, "target P(tp) 0.95", "tc tink"))
    b.append(L(X(thr), Y(.95), X(thr), Y(0), "st2 w15")); b.append(C(X(thr), Y(.95), 3.5, "f2"))
    b.append(T(X(thr) - 4, Y(.2), f"{thr:.2f}", "tc f2t", "end"))
    notes = ["how: calibrate() on the step 6 validation_by_clip.csv (random_detections clips",
             "   only), with the selection tables, p_min = 0.95 and fold_group = \"night\"",
             "check: model_comparison.csv, calibration_quality.csv (species ok), curves.png",
             "get: thresholds.csv is written already: the score where P(tp) reaches p_min;",
             "   other targets: calibrated_thresholds(res$fit, target = …)",
             "compare with A: calibrated_thresholds(rule = \"precision\", scored = res$scored)",
             "cells borrow strength (partial pooling); no diagnosis; brms adds threshold_lower"]
    for k, n in enumerate(notes): note(b, 0, 252 + k * 13, n)
    b.append(L(0, 346, 440, 346, "sgrid"))
    note(b, 0, 362, "output: one row per site × species with threshold and p_tp_at_threshold")
    return svg(W, 370, "".join(b), "Model-based threshold from the calibration model")

out["s1c"] = emphasise_optional(s1c())
out["s1d"] = s1d()
# panel e: diagnosis now comes from step 6
out["s1e"] = out["s1e"].replace("review_support() diagnosis", "step 7 diagnosis")
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok v6")
