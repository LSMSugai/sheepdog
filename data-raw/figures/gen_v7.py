"""v7: new step 6 = post_validation(); review_support() becomes step 7 (A, alternative B); acting = step 8."""
import json
from gen_v6 import out
from gen_panels import T, R, C, L, P, svg, badge, arrow

NOTE = 'font-size="10.5" opacity=".85"'
def note(b, x, y, s): b.append(T(x, y, s, "ts", "start", NOTE))

def s1pv():
    b = []
    Wd, Hd = 900, 196
    b.append(badge(8, 14, 6)); b.append(T(22, 18, "post_validation()", "tc f1t", "start", 'font-size="12"'))
    note(b, 160, 18, "reads the verdicts (step 5) and summarises the review in one call;")
    note(b, 160, 31, "arguments: target_precision 0.90 · min_n 15 · weighted (design weights, default on for random_detections)")
    files = [("validation_by_clip.csv", "classify_review() or", "app_verdicts()", "manifest + one verdict per clip"),
             ("precision_by_bin.csv", "precision_by_bin()", "", "precision by species × score bin"),
             ("suggested_thresholds.csv", "suggest_thresholds()", "", "empirical threshold per cell"),
             ("nightly_presence.csv", "nightly_presence()", "", "confirmed presence by night"),
             ("retraining_clips.csv", "retraining_clips()", "", "positive clips for retraining"),
             ("precision_by_bin.png", "plot_precision()", "", "precision curves (needs ggplot2)")]
    cw, gap, x0, y0 = 138, 10, 0, 50
    for i, (fn, f1, f2, d) in enumerate(files):
        x = x0 + i * (cw + gap)
        hl = fn == "suggested_thresholds.csv"
        b.append(R(x, y0, cw, 54, "fs1 st1" if hl else "fsurf sline", 6))
        # file icon
        b.append(P(f"M{x+10} {y0+12} h12 l5 5 v19 h-17 Z", "fsurf st1 w15"))
        b.append(T(x + 34, y0 + 22, fn.split(".")[0], "tc tink", "start", 'style="font-size:8.6px"'))
        b.append(T(x + 34, y0 + 35, "." + fn.split(".")[1], "tc tm", "start", 'style="font-size:8.6px"'))
        b.append(T(x + 8, y0 + 74, f1, "tc f1t", "start", 'style="font-size:9.5px"'))
        if f2: b.append(T(x + 8, y0 + 87, f2, "tc f1t", "start", 'style="font-size:9.5px"'))
        b.append(T(x + 8, y0 + (102 if f2 else 89), d, "ts", "start", 'style="font-size:9.6px" opacity=".85"'))
    b.append(L(0, 160, Wd, 160, "sgrid"))
    note(b, 0, 178, "the empirical thresholds of suggested_thresholds.csv are the ones review_support() reports in step 7, now with the diagnosis")
    return svg(Wd, Hd, "".join(b), "post_validation(): the files it writes and the functions behind each")

out["s1pv"] = s1pv()
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok v7")

# ---------------- B as two sequential sub-steps: 7.1 calibrate() -> 7.2 calibrated_thresholds()
from gen_panels import logistic, logit, W
def pill(b, x, y, txt, color="2"):
    b.append(R(x, y - 9, 28, 18, f"f{color}", 9)); b.append(T(x + 14, y + 4, txt, "tny finv", "middle"))

def s1d_b():
    b = []
    # 7.1
    pill(b, 0, 12, "7.1"); b.append(T(36, 16, "calibrate()", "tc f2t", "start", 'font-size="12"'))
    note(b, 128, 16, "fits and checks the calibration model (stage 2)")
    for k, n in enumerate(["input: the step 6 validation_by_clip.csv (random_detections clips only),",
                           "the selection tables, p_min = 0.95, fold_group = \"night\"",
                           "check: model_comparison.csv, calibration_quality.csv (species ok),",
                           "calibration_curves.png  ·  writes thresholds.csv for p_min already"]):
        note(b, 36, 33 + k * 13, n)
    b.append(arrow(14, 30, 14, 98, "ar2"))
    # 7.2
    pill(b, 0, 110, "7.2"); b.append(T(36, 114, "calibrated_thresholds(res$fit, target = …)", "tc f2t", "start", 'font-size="12"'))
    note(b, 36, 130, "reads the threshold off the fitted curve, for any target and rule")
    x0, x1, y0, y1 = 40, 420, 286, 156
    X = lambda c: x0 + (c - .1) / .9 * (x1 - x0); Y = lambda p: y0 - p * (y0 - y1)
    for p in (0, .5, 1):
        b.append(L(x0, Y(p), x1, Y(p), "sgrid")); b.append(T(x0 - 5, Y(p) + 4, f"{p:g}", "tc", "end"))
    for c in (.1, .5, 1): b.append(T(X(c), y0 + 15, f"{c:g}", "tc", "middle"))
    b.append(T((x0 + x1) / 2, y0 + 30, "confidence score", "ts", "middle"))
    b.append(T(x0 - 30, y1 - 10, "P(tp) from the model", "ts"))
    a_, b_ = .6, 1.7
    ss = [0.1 + i * .89 / 60 for i in range(61)]
    b.append(P("M" + " L".join(f"{X(s):.1f} {Y(logistic(a_ + b_ * logit(s))):.1f}" for s in ss), "nofill st2 w25"))
    thr = logistic((logit(.95) - a_) / b_)
    b.append(L(x0, Y(.95), x1, Y(.95), "stink dash")); b.append(T(x0 + 4, Y(.95) - 5, "target P(tp) 0.95", "tc tink"))
    b.append(L(X(thr), Y(.95), X(thr), Y(0), "st2 w15")); b.append(C(X(thr), Y(.95), 3.5, "f2"))
    b.append(T(X(thr) - 4, Y(.2), f"{thr:.2f}", "tc f2t", "end"))
    for k, n in enumerate(["rule = \"probability\": score where P(tp) reaches the target and stays above it",
                           "rule = \"precision\" (scored = res$scored): same question as A, to compare",
                           "cells borrow strength (partial pooling); no diagnosis; brms adds threshold_lower"]):
        note(b, 0, 340 + k * 13, n)
    b.append(L(0, 384, 440, 384, "sgrid"))
    note(b, 0, 400, "output: one row per site × species with threshold and p_tp_at_threshold")
    return svg(W, 408, "".join(b), "Model-based threshold: calibrate(), then calibrated_thresholds()")

out["s1d"] = s1d_b()
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok v7b")
