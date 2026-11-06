"""v4: stage 1 panel c shows the two ways to pick a threshold (empirical vs model-based)."""
import json
from gen_v3 import out
from gen_panels import T, R, C, L, P, svg, logistic, logit, W, H, badge

def s1c():
    b = []
    def frame(x0, x1, y0, y1, ylab, xt):
        X = lambda c: x0 + (c - .1) / .9 * (x1 - x0)
        Y = lambda p: y0 - p * (y0 - y1)
        for p in (0, .5, 1):
            b.append(L(x0, Y(p), x1, Y(p), "sgrid"))
            b.append(T(x0 - 5, Y(p) + 4, f"{p:g}", "tc", "end"))
        for c in xt:
            b.append(T(X(c), y0 + 15, f"{c:g}", "tc", "middle"))
        b.append(T((x0 + x1) / 2, y0 + 30, "confidence score", "ts", "middle"))
        b.append(T(x0 - 24, y1 - 30, ylab, "ts"))
        return X, Y

    # --- A: empirical (suggest_thresholds)
    b.append(badge(10, 12, 6))
    b.append(T(22, 16, "A · empirical", "tb f1t"))
    b.append(T(4, 31, "suggest_thresholds()", "tc"))
    X, Y = frame(30, 205, 200, 80, "precision of clips ≥ score", (.1, .5, 1))
    cum = [.58, .62, .67, .72, .78, .84, .91, .94, .97]
    pts = [(X(.1 + i * .1), Y(p)) for i, p in enumerate(cum)]
    b.append(P("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts), "nofill st1 w2"))
    for x, y in pts: b.append(C(x, y, 2.8, "f1"))
    b.append(L(30, Y(.9), 205, Y(.9), "stink dash"))
    b.append(T(34, Y(.9) - 5, "target 0.90", "tc tink"))
    b.append(L(X(.7), Y(.9), X(.7), Y(0), "st1 w15"))
    b.append(T(X(.7) + 4, Y(.2), "0.70", "tc f1t"))
    b.append(T(34, Y(.42), "reviewed clips", "ts"))
    b.append(T(34, Y(.32), "weighted by design", "ts"))

    # --- B: model-based (calibrated_thresholds)
    b.append(badge(256, 12, 6, color="2"))
    b.append(T(268, 16, "B · model-based", "tb f2t"))
    b.append(T(250, 31, "calibrated_thresholds()", "tc"))
    X, Y = frame(270, 432, 200, 80, "P(tp) from the model", (.1, .5, 1))
    a_, b_ = .6, 1.7
    ss = [0.1 + i * .89 / 60 for i in range(61)]
    b.append(P("M" + " L".join(f"{X(s):.1f} {Y(logistic(a_ + b_ * logit(s))):.1f}" for s in ss), "nofill st2 w25"))
    thr = logistic((logit(.95) - a_) / b_)
    b.append(L(270, Y(.95), 432, Y(.95), "stink dash"))
    b.append(T(274, Y(.95) - 5, "target P(tp) 0.95", "tc tink"))
    b.append(L(X(thr), Y(.95), X(thr), Y(0), "st2 w15"))
    b.append(C(X(thr), Y(.95), 3.5, "f2"))
    b.append(T(X(thr) - 4, Y(.2), f"{thr:.2f}", "tc f2t", "end"))
    b.append(T(274, Y(.82), "checked", "ts"))
    b.append(T(274, Y(.72), "stage 2 model", "ts"))

    notesA = ["lowest score from which the",
              "reviewed random_detections clips",
              "at or above it reach the target",
              "precision (at least min_n clips),",
              "weighted by design",
              "optional: precision_by_bin(),",
              "plot_precision()"]
    notesB = ["score at which P(tp) from the",
              "checked stage 2 calibration",
              "model reaches the target and",
              "stays above it; cells borrow",
              "strength from each other",
              "(partial pooling); brms adds a",
              "conservative threshold_lower"]
    for k, (na, nb) in enumerate(zip(notesA, notesB)):
        b.append(T(4, 252 + k * 13, na, "ts", "start", 'font-size="10.5" opacity=".85"'))
        b.append(T(248, 252 + k * 13, nb, "ts", "start", 'font-size="10.5" opacity=".85"'))
    b.append(L(0, 346, 440, 346, "sgrid"))
    b.append(T(220, 364, "compare A and B: agreement supports the model", "ts tink", "middle"))
    return svg(W, 372, "".join(b), "Two ways to pick the threshold: empirical precision and model-based P(tp)")

out["s1c"] = s1c()
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok")

# ---------------- stage 1 panel e: routes after review_support() + data gate
def s1e():
    from gen_panels import arrow
    b = []
    Wd, Hd = 900, 284
    b.append(T(0, 16, "review_support() diagnosis", "tb"))
    b.append(badge(166, 12, 8))
    b.append(T(178, 16, "next step", "tb"))
    b.append(T(612, 16, "Enough data to continue?", "tb"))
    rows = [("reached", "f3", "finv", "✓",
             ["Enough reviewed clips above the cut: the threshold is set.",
              "Check the data needs on the right, then continue."]),
            ("review more", "f1", "finv", "+",
             ["Draw another random_detections round for this cell",
              "(same threshold, new seed), review, re-run.  ↺ step 2"]),
            ("exhausted", "fmuted", "finv", "–",
             ["No high-score detections left to review: keep the clips you",
              "have; rely on the pooled stage 2 model, or flag the cell."]),
            ("unreliable", "fbad", "finv", "!",
             ["Listen to the false positives → build_training_set() →",
              "retrain → re-run BirdNET → exclude_training_clips()  ↺ step 2"]),
            ("not reviewed", "fsurf sline dash", "tm", "?",
             ["No reviewed clip yet: draw clips for this cell.  ↺ step 2", ""])]
    for i, (lab, cls, tcls, sym, lines) in enumerate(rows):
        y = 34 + i * 48
        b.append(R(0, y, 130, 32, cls, 6))
        b.append(T(14, y + 21, sym, "tb " + tcls))
        b.append(T(30, y + 21, lab, "ts " + tcls))
        b.append(arrow(134, y + 16, 156, y + 16))
        b.append(R(160, y, 428, 40, "fsurf sline", 6))
        for k, ln in enumerate(lines):
            if ln: b.append(T(172, y + 16 + k * 15, ln, "ts tink"))
    # arrows to the gate
    b.append(arrow(588, 50, 608, 50, "ar"))
    b.append(P("M588 146 H598 V60", "nofill ar dash"))
    # gate
    b.append(R(612, 30, 288, 222, "fs1 st1", 8))
    checks = [("Threshold", "≥ min_n reviewed clips above the cut"),
              ("Curve (stage 2)", "quality ok; effort curve plateaus"),
              ("Retraining", "≥ 100 positive clips per class (min_files)"),
              ("False positives", "enough confirmed occasions per site")]
    for k, (h, d) in enumerate(checks):
        y = 52 + k * 48
        b.append(T(626, y + 4, "☐  " + h, "ts tink"))
        b.append(T(644, y + 20, d, "ts", "start", 'font-size="10.5"'))
    b.append(T(626, 274, "all met → stage 2 · occupancy", "ts f1t"))
    b.append(arrow(800, 270, 880, 270, "ar1"))
    return svg(Wd, Hd, "".join(b), "What to do after each review_support() diagnosis, and when there is enough data")

out["s1e"] = s1e()
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok e")

# ---------------- stage 1 panel a v2: read_selection_tables() -> select_clips(sampling_mode = ...)
def s1a():
    from gen_panels import recs, arrow
    b = []
    # step 1: input
    b.append(R(0, 2, 182, 24, "fs1", 5))
    b.append(badge(13, 14, 1))
    b.append(T(26, 18, "read_selection_tables()", "tc f1t"))
    b.append(arrow(186, 14, 206, 14, "ar1"))
    b.append(T(212, 18, "all predictions with their scores", "ts tink"))
    # step 2: select_clips with three options
    b.append(badge(8, 46, 3))
    b.append(T(20, 50, "select_clips(sampling_mode = …)", "tc tink"))
    rows = [('"top"', "highest per recording"),
            ('"random_detections"', "random, score ≥ 0.5"),
            ('"random_recordings"', "any · expert check")]
    bx0, bw, gap, bh = 128, 22, 3.6, 42
    for r, (name, sub) in enumerate(rows):
        y0 = 62 + r * 66
        b.append(T(0, y0 + 16, name, "tc f1t", "start", 'font-size="9.5"'))
        b.append(T(0, y0 + 30, sub, "ts"))
        drawn_rd = {2, 6, 9}; drawn_rr = {1, 4, 8}
        for i, sc in enumerate(recs):
            x = bx0 + i * (bw + gap)
            cls = "fsurf sline"
            if (r == 1 and i in drawn_rd) or (r == 2 and i in drawn_rr): cls = "fs1 st1"
            b.append(R(x, y0, bw, bh, cls, 3))
            top_i = max(range(len(sc)), key=lambda k: sc[k]) if sc else None
            for k, s in enumerate(sc):
                cy = y0 + bh - 3 - s * (bh - 6)
                pick = ((r == 0 and k == top_i) or (r == 1 and i in drawn_rd and s >= .5)
                        or (r == 2 and i in drawn_rr))
                b.append(C(x + bw / 2 + (k - (len(sc) - 1) / 2) * 4, cy, 2.6 if pick else 2,
                           "f1" if pick else "fmuted", "" if pick else 'opacity=".45"'))
            if r == 2 and i in drawn_rr and not sc:
                b.append(T(x + bw / 2, y0 + bh / 2 + 4, "∅", "tc f1t", "middle"))
        ty = y0 + bh - 3 - .5 * (bh - 6)
        b.append(L(bx0 - 3, ty, bx0 + 12 * (bw + gap), ty, "sline dash"))
    for i in range(0, 12, 2):
        x = bx0 + i * (bw + gap) + bw / 2
        b.append(T(x, 250, f"{(18 + i) % 24:02d}h", "tc", "middle"))
    # requirement and option
    b.append(R(0, 258, 132, 22, "fs3 st3", 5))
    b.append(badge(12, 269, 2, color="3"))
    b.append(T(24, 273, "list_recordings()", "tc f3t"))
    b.append(arrow(66, 257, 66, 232, "nofill st3 w15"))
    b.append(L(0, 288, 440, 288, "sgrid"))
    b.append(badge(8, 302, 3, optional=True))
    b.append(T(20, 306, "optional · covariate_bins(): stratify random_detections along a gradient", "ts"))
    return svg(W, 314, "".join(b), "read_selection_tables, then select_clips with three sampling designs")

out["s1a"] = s1a()
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok a")
