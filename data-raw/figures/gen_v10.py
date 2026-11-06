"""v10: Stage 1 · Diagnostic figure as two workflows, 7A.1–7A.4 and 7B.1–7B.4, plus the comparison."""
import json, re, math
from gen_v9 import *          # runs the whole chain
from gen_panels import T, R, C, L, P, svg, W, badge, arrow, logistic, logit
from gen_v8 import a_threshold, note, NOTE, MONO

def tag(b, x, y, txt, color="1"):
    """step tag such as 7A.1, centred vertically on y"""
    b.append(R(x, y - 10, 38, 20, f"f{color}", 10)); b.append(T(x + 19, y + 4, txt, "tny finv", "middle"))

def head(b, txt, fn, color, title, sub=None):
    """the panel header already names the step: here only the function and a note"""
    if fn:
        b.append(T(0, 16, fn, f"tc f{color}t", "start", 'font-size="12"'))
        if sub: note(b, 0, 31, sub)
    elif sub: note(b, 0, 16, sub)

# ---------------- 7A.1 · threshold: the review_support() panel with a new tag
def a1():
    s = a_threshold()
    s = s.replace(badge(8, 12, 7), "")
    s = s.replace('<text x="22.0" y="16.0" class="tc f1t"', '<text x="0.0" y="16.0" class="tc f1t"')
    s = re.sub(r'(<text x=")140\.0(" y="(16|29)\.0")', r'\g<1>124.0\2', s)
    return s

# ---------------- 7A.2 · how the diagnosis is decided (the order used by review_support())
def a2():
    b = []
    head(b, "7A.2", None, "1", "Read the diagnosis", "review_support() asks, in this order:")
    qs = [("any reviewed clip in the cell?", "no", "not reviewed", "fsurf sline dash", "tm", "n_reviewed = 0"),
          ("did suggest_thresholds() find a cut?", "yes", "reached", "f3", "finv", "precision ≥ target, n_eff ≥ min_n"),
          ("fewer than min_n high-score detections left?", "yes", "exhausted", "fmuted", "finv", "unreviewed_high < 15"),
          ("precision at high scores below min_precision?", "yes", "unreliable", "fbad", "finv", "prec_high < 0.5"),
          ]
    y = 56
    for i, (q, ans, lab, cls, tcls, why) in enumerate(qs):
        b.append(R(0, y, 262, 34, "fsurf sline", 6))
        b.append(T(10, y + 15, q, "ts tink", "start", 'style="font-size:10.6px"'))
        b.append(T(10, y + 28, why, "tc tm", "start", MONO))
        b.append(arrow(264, y + 17, 300, y + 17))
        b.append(T(282, y + 12, ans, "tny tm", "middle"))
        b.append(R(304, y + 5, 116, 24, cls, 12)); b.append(T(362, y + 21, lab, "ts " + tcls, "middle"))
        if i < len(qs) - 1:
            b.append(arrow(130, y + 36, 130, y + 52)); b.append(T(138, y + 47, "no" if ans == "yes" else "yes", "tny tm"))
        y += 56
    b.append(arrow(130, y - 20, 130, y - 4)); b.append(T(138, y - 9, "no", "tny tm"))
    b.append(R(72, y, 116, 24, "f1", 12)); b.append(T(130, y + 16, "review more", "ts finv", "middle"))
    note(b, 196, y + 16, "high-score clips are left and precision is")
    note(b, 196, y + 29, "not yet bad: more review can settle it")
    b.append(L(0, y + 46, 440, y + 46, "sgrid"))
    note(b, 0, y + 62, "high score = confidence ≥ conf_high (0.7); one label per site × species")
    return svg(W, y + 70, "".join(b), "How review_support() decides the diagnosis")

# ---------------- 7A.3 · act on the diagnosis
def a3():
    b = []
    rows = [("f3", "finv", "reached", ["the threshold can be used:", "go to 7A.4"]),
            ("f1", "finv", "review more", ["a new random_detections round for the cell", "(same threshold, new seed)  ↺ Figure 1 · step 2", "then steps 3–7 again with all rounds stacked (6.1)"]),
            ("fmuted", "finv", "exhausted *", ["keep the clips: the pooled model (7B) can", "still give a threshold; or leave the cell out", "* if the target is far off, see Retraining"]),
            ("fbad", "finv", "unreliable *", ["the classifier is the limit: retrain it,", "then a new round  ↺ step 2", "* see Stage 1 · Retraining"]),
            ("fsurf sline dash", "tm", "not reviewed", ["draw clips for this cell  ↺ step 2"])]
    y = 4
    for cls, tcls, lab, nxt in rows:
        b.append(R(0, y, 116, 24, cls, 12)); b.append(T(58, y + 16, lab, "ts " + tcls, "middle"))
        b.append(arrow(120, y + 12, 140, y + 12))
        for k, n in enumerate(nxt): note(b, 148, y + 10 + k * 13, n)
        y += max(42, 13 * len(nxt) + 16)
    b.append(L(0, y + 2, 440, y + 2, "sgrid"))
    b.append(T(0, y + 20, "* retraining may help: see Stage 1 · Retraining", "ts fbadt", "start", 'style="font-size:10px"'))
    return svg(W, y + 28, "".join(b), "Next step for each diagnosis")

# ---------------- 7A.4 · enough data to continue, and the three ways out (wide)
def a4():
    b = []
    head(b, "7A.4", None, "1", "Enough data to continue?")
    checks = ["☐ every cell you need is “reached” (or left out on purpose)",
              "☐ the threshold rests on ≥ min_n clips (n_eff) above the cut",
              "☐ for Stage 2: random_detections clips across the score range",
              "☐ for occupancy: a validation design at the same threshold"]
    b.append(R(0, 30, 440, 88, "fs1 st1", 8))
    for k, c in enumerate(checks): note(b, 12, 50 + k * 19, c)
    b.append(arrow(220, 122, 220, 142, "ar1")); b.append(T(228, 136, "all met", "tny f1t"))
    exits = [("Stage 2 · Calibration", "f2t", "fs2 st2", ["model-based route (7B, routes", "way 1–3): P(tp) for every", "detection, then Stage 3"]),
             ("Stage 1 only", "f1t", "fs1 st1", ["the empirical threshold:", "history built by hand, then", "community_matrices()"]),
             ("Occupancy export", "f4t", "fs4 st4", ["export_occupancy_data():", "threshold as detection rule;", "crywolf estimates false +"])]
    for i, (t, tc, cls, ls) in enumerate(exits):
        x = i * 148
        b.append(R(x, 146, 144, 84, cls, 8))
        b.append(T(x + 8, 163, t, "ts " + tc))
        for k, l in enumerate(ls): b.append(T(x + 8, 181 + k * 13, l, "ts", "start", 'style="font-size:9.6px" opacity=".85"'))
    b.append(L(0, 244, 440, 244, "sgrid"))
    note(b, 0, 262, "not yet → back to 7A.3 · the three ways out are compared in")
    note(b, 0, 275, "“Routes to detection histories and occupancy”")
    return svg(W, 284, "".join(b), "Enough data to continue, and the three ways out").replace(f'viewBox="0 0 {W} 284"', f'viewBox="0 24 {W} 260"')

# ---------------- 7B.1 · fit: calibrate() and the model comparison
def b1():
    b = []
    head(b, "7B.1", "calibrate()", "2", None, "fits the Stage 2 calibration model to the reviews")
    for k, n in enumerate(["input: validation_by_clip.csv from step 6 (random_detections clips only),",
                           "the selection tables, p_min = 0.95, fold_group = \"night\""]):
        note(b, 0, 56 + k * 13, n)
    # model comparison: held-out log-loss per candidate, one-SE rule
    x0, y0, y1 = 60, 210, 100
    vals = [(".m0", .52, .02), (".m1", .41, .02), (".m2", .385, .02), (".m3", .38, .021), (".m4", .379, .022)]
    labs = ["one curve", "+ species", "+ site", "species × site", "+ covariate"]
    Y = lambda v: y0 - (v - .3) / .25 * (y0 - y1)
    best = min(v for _, v, _ in vals); se = [s for _, v, s in vals if v == best][0]
    b.append(L(x0 - 10, Y(best + se), 430, Y(best + se), "stink dash"))
    b.append(T(430, Y(best + se) - 4, "best + 1 SE", "tc tink", "end", MONO))
    for i, ((m, v, s), lab) in enumerate(zip(vals, labs)):
        x = x0 + i * 74
        chosen = i == 2
        b.append(L(x, Y(v - s), x, Y(v + s), "st2 w15"))
        b.append(C(x, Y(v), 4.5 if chosen else 3.5, "f2" if chosen else "fsurf st2 w15"))
        b.append(T(x, y0 + 14, f"m{i}", "tc tink", "middle"))
        b.append(T(x, y0 + 26, lab, "tny tm", "middle"))
    b.append(T(x0 - 22, y1 - 8, "held-out log-loss (lower is better)", "ts"))
    b.append(T(x0 + 2 * 74 + 8, Y(.385) + 20, "kept: simplest within 1 SE", "tny f2t"))
    b.append(L(0, 252, 440, 252, "sgrid"))
    for k, n in enumerate(["writes model_comparison.csv, calibration_quality.csv (7B.2), thresholds.csv",
                           "and calibration_curves.png; set engine = \"brms\" for the Bayesian fit"]):
        note(b, 0, 270 + k * 13, n)
    return svg(W, 292, "".join(b), "calibrate(): candidate models compared by cross-validation")

# ---------------- 7B.2 · check the calibration before using it
def b2():
    b = []
    head(b, "7B.2", "calibration_quality()", "2", None, "per species, on held-out clips: check before using the curve")
    inner = re.sub(r"^<svg[^>]*>|</svg>$", "", out["s2q"])
    b.append(f'<g transform="translate(0,44) scale(0.98)">{inner}</g>')
    note(b, 0, 290, "adds info: beats the species’ base rate · discriminates: ranks true above false")
    note(b, 0, 303, "calibrated: probabilities match the share of true clips (slope near 1)")
    return svg(W, 312, "".join(b), "calibration_quality(): ok, poor or insufficient per species")

# ---------------- 7B.3 · threshold from the curve
def b3():
    b = []
    head(b, "7B.3", "calibrated_thresholds(res$fit, target = 0.95)", "2", None, "reads the threshold off the fitted curve")
    x0, x1, y0, y1 = 40, 420, 196, 60
    X = lambda c: x0 + (c - .1) / .9 * (x1 - x0); Y = lambda p: y0 - p * (y0 - y1)
    for p in (0, .5, 1):
        b.append(L(x0, Y(p), x1, Y(p), "sgrid")); b.append(T(x0 - 5, Y(p) + 4, f"{p:g}", "tc", "end"))
    for c in (.1, .5, 1): b.append(T(X(c), y0 + 15, f"{c:g}", "tc", "middle"))
    b.append(T((x0 + x1) / 2, y0 + 30, "confidence score", "ts", "middle"))
    b.append(T(x0 - 30, y1 - 10, "P(tp) from the model", "ts"))
    sp = [(.6, 1.7, "boa-ran", "w25"), (.1, 1.5, "den-nan", "w15")]
    for a_, b_, nm, w in sp:
        ss = [0.1 + i * .89 / 60 for i in range(61)]
        b.append(P("M" + " L".join(f"{X(s):.1f} {Y(logistic(a_ + b_ * logit(s))):.1f}" for s in ss), f"nofill st2 {w}", '' if w == "w25" else 'opacity=".55"'))
    b.append(L(x0, Y(.95), x1, Y(.95), "stink dash")); b.append(T(x0 + 4, Y(.95) - 5, "target P(tp) 0.95", "tc tink"))
    for j, (a_, b_, nm, w) in enumerate(sp):
        thr = logistic((logit(.95) - a_) / b_)
        b.append(L(X(thr), Y(.95), X(thr), Y(0), "st2 w15")); b.append(C(X(thr), Y(.95), 3.5, "f2"))
        b.append(T(X(thr) + (-4 if j == 0 else 4), Y(.12), f"{thr:.2f}", "tc f2t", "end" if j == 0 else "start"))
    b.append(T(x0 + 6, Y(.62), "thick: boa-ran", "tc f2t", "start", MONO)); b.append(T(x0 + 6, Y(.62) + 12, "thin: den-nan", "tc f2t", "start", MONO + ' opacity=".7"'))
    for k, n in enumerate(["one threshold per species (or site × species): only for species “ok” in 7B.2",
                           "rule = \"precision\" (scored = res$scored) asks the 7A question instead",
                           "with brms, also threshold_lower; cells borrow strength (partial pooling)"]):
        note(b, 0, 250 + k * 13, n)
    return svg(W, 290, "".join(b), "calibrated_thresholds(): score where P(tp) reaches 0.95")

# ---------------- 7B.4 · act on the check
def b4():
    b = []
    rows = [("f3", "finv", "ok", ["use the threshold from 7B.3, or go on to", "Stage 2 · Calibration (routes way 1–3)"]),
            ("fbad", "finv", "poor *", ["add a covariate (month, site) to the candidates,", "or use the empirical threshold (7A) for it", "* if neither helps, see Retraining"]),
            ("fsurf sline dash", "tm", "insufficient", ["too few true or false clips: review more", "↺ Figure 1 · step 2; calibration_effort()", "shows how many clips per cell are needed"])]
    y = 4
    for cls, tcls, lab, nxt in rows:
        b.append(R(0, y, 116, 24, cls, 12)); b.append(T(58, y + 16, lab, "ts " + tcls, "middle"))
        b.append(arrow(120, y + 12, 140, y + 12))
        for k, n in enumerate(nxt): note(b, 148, y + 10 + k * 13, n)
        y += 13 * len(nxt) + 22
    b.append(L(0, y, 440, y, "sgrid"))
    note(b, 0, y + 18, "7B gives no review_support() diagnosis; later, cell_status() (Stage 3)")
    note(b, 0, y + 31, "labels each cell reliable, probably absent or unreliable")
    return svg(W, y + 40, "".join(b), "Next step for each calibration check")

# ---------------- compare 7A and 7B (wide)
def cmp_():
    b = []; Wd = 900
    b.append(T(0, 16, "Compare the two thresholds", "tb"))
    note(b, 196, 16, "same cells: 7A against 7B run with rule = \"precision\", target = 0.90 (like with like)")
    x0, x1, y0, y1 = 50, 250, 196, 36
    X = lambda v: x0 + (v - .3) / .7 * (x1 - x0); Y = lambda v: y0 - (v - .3) / .7 * (y0 - y1)
    b.append(R(x0, y1, x1 - x0, y0 - y1, "fsurf sline", 4))
    b.append(P(f"M{X(.3)} {Y(.36)} L{X(.94)} {Y(1)} L{X(1)} {Y(1)} L{X(1)} {Y(.94)} L{X(.36)} {Y(.3)} Z", "fs3", 'opacity=".7"'))
    b.append(L(X(.3), Y(.3), X(1), Y(1), "sline dash"))
    pts = [(.55, .58, 1), (.62, .6, 1), (.7, .73, 1), (.78, .76, 1), (.84, .86, 1), (.66, .82, 0), (.9, .7, 0)]
    for a, m, ok in pts: b.append(C(X(a), Y(m), 4, "f3" if ok else "fbad"))
    for v in (.3, 1):
        b.append(T(X(v), y0 + 14, f"{v:g}", "tc", "middle")); b.append(T(x0 - 6, Y(v) + 4, f"{v:g}", "tc", "end"))
    b.append(T((x0 + x1) / 2, y0 + 30, "7A threshold (empirical)", "ts", "middle"))
    b.append(T(14, (y0 + y1) / 2, "7B threshold (model)", "ts", "middle", f'transform="rotate(-90 14 {(y0+y1)/2})"'))
    cards = [("f3t", "fs3 st3", "they agree", ["the model reproduces what the reviewed", "clips show: report Stage 2 (way 1–3);", "7A stays as the check"]),
             ("fbadt", "fsbad stbad", "they differ in some cells", ["7B higher: pooling may lend the cell a", "curve; 7A higher: precision may dip above", "the first cut. Look at those cells (7A.3, 7B.4)"])]
    for i, (tc, cls, t, ls) in enumerate(cards):
        x = 300 + i * 300
        b.append(R(x, 40, 288, 112, cls, 8))
        b.append(C(x + 16, 58, 5, "f3" if i == 0 else "fbad")); b.append(T(x + 28, 62, t, "ts " + tc))
        for k, l in enumerate(ls): note(b, x + 14, 86 + k * 16, l)
    note(b, 300, 180, "7B with P(tp) 0.95 asks a stricter question (each detection, not the set), so its thresholds")
    note(b, 300, 193, "usually sit higher than 7A at 0.90: compare with rule = \"precision\" to see whether the model fits")
    return svg(Wd, 232, "".join(b), "Comparison of the empirical and model-based thresholds")

out.update(d7a1=a1(), d7a2=a2(), d7a3=a3(), d7a4=a4(), d7b1=b1(), d7b2=b2(), d7b3=b3(), d7b4=b4(), d7cmp=cmp_())
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok v10")
