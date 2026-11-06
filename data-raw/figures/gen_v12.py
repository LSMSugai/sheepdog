"""v12: compact panels (320 wide) for A step 1 and B steps 1–4, so the diagnostic figure fits ~1400 px with larger text."""
import json, math
from gen_v11 import *
from gen_panels import T, R, C, L, P, svg, arrow, logistic, logit
from gen_v8 import note, NOTE, MONO

NW = 320
SM = 'style="font-size:9.6px"'

def frame(b, x0, x1, y0, y1, ylab, xlab="confidence score →", yt=(0, .5, 1)):
    for p in yt:
        b.append(L(x0, y0 - p * (y0 - y1), x1, y0 - p * (y0 - y1), "sgrid"))
        b.append(T(x0 - 4, y0 - p * (y0 - y1) + 3, f"{p:g}", "tc", "end", MONO))
    b.append(T(x1, y0 + 12, xlab, "tc", "end", MONO)); b.append(T(x0 - 26, y1 - 8, ylab, "ts", "start", SM))
    X = lambda c: x0 + (c - .1) / .9 * (x1 - x0); Y = lambda p: y0 - p * (y0 - y1)
    return X, Y

# ---------------- A · step 1 (no R output)
def a1c():
    b = []
    b.append(T(0, 16, "review_support()", "tc f1t", "start", 'font-size="12"'))
    note(b, 0, 32, "target_precision 0.90 · min_n 15")
    note(b, 0, 45, "conf_high 0.7 · min_precision 0.5")
    b.append(R(0, 56, NW, 176, "fsurf sline", 6))
    b.append(T(10, 74, "inside: suggest_thresholds()", "tc f1t"))
    note(b, 10, 89, "precision of the reviewed clips at or")
    note(b, 10, 102, "above each cut, weighted by design")
    X, Y = frame(b, 40, 306, 204, 132, "precision")
    cum = [.58, .62, .67, .72, .78, .84, .91, .94, .97]
    pts = [(X(.1 + i * .1), Y(p)) for i, p in enumerate(cum)]
    b.append(P("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts), "nofill st1 w2"))
    for x, y in pts: b.append(C(x, y, 2.2, "f1"))
    b.append(L(40, Y(.9), 306, Y(.9), "stink dash")); b.append(T(44, Y(.9) - 4, "target 0.90", "tc tink", "start", MONO))
    b.append(L(X(.7), Y(.9), X(.7), Y(0), "st1 w15")); b.append(T(X(.7) - 4, Y(.2), "0.70", "tc f1t", "end", MONO))
    b.append(arrow(160, 236, 160, 254, "ar1"))
    b.append(R(0, 258, NW, 46, "fs1", 6))
    note(b, 10, 276, "per site × species: the lowest cut that")
    note(b, 10, 290, "passes (≥ min_n clips), and a diagnosis")
    note(b, 0, 324, "threshold only where diagnosis = reached")
    return svg(NW, 332, "".join(b), "review_support(): empirical threshold per cell")

# ---------------- B · step 1
def b1c():
    b = []
    b.append(T(0, 16, "calibrate()", "tc f2t", "start", 'font-size="12"'))
    note(b, 0, 32, "fits the Stage 2 model to the")
    note(b, 0, 45, "random_detections clips (step 6)")
    x0, y0, y1 = 44, 196, 92
    vals = [.52, .41, .385, .38, .379]; se = .02
    Y = lambda v: y0 - (v - .3) / .25 * (y0 - y1)
    b.append(L(x0 - 14, Y(.379 + se), 310, Y(.379 + se), "stink dash"))
    b.append(T(310, Y(.379 + se) - 4, "best + 1 SE", "tc tink", "end", MONO))
    for i, v in enumerate(vals):
        x = x0 + i * 60
        b.append(L(x, Y(v - se), x, Y(v + se), "st2 w15"))
        b.append(C(x, Y(v), 4.5 if i == 2 else 3.4, "f2" if i == 2 else "fsurf st2 w15"))
        b.append(T(x, y0 + 14, f"m{i}", "tc tink", "middle"))
    b.append(T(x0 + 120, Y(.385) + 18, "kept: simplest", "tny f2t", "middle"))
    b.append(T(0, y1 - 22, "held-out log-loss (lower is better)", "ts", "start", SM))
    note(b, 0, 232, "m0 one curve · m1 + species intercept")
    note(b, 0, 245, "m2 + species slope · m3 + site · m4 species × site")
    b.append(L(0, 258, NW, 258, "sgrid"))
    note(b, 0, 276, "writes model_comparison.csv, the")
    note(b, 0, 289, "check (step 2) and thresholds.csv;")
    note(b, 0, 302, "engine = \"brms\" for the Bayesian fit")
    return svg(NW, 310, "".join(b), "calibrate(): candidate models compared by cross-validation")

# ---------------- B · step 2
def b2c():
    b = []
    b.append(T(0, 16, "calibration_quality()", "tc f2t", "start", 'font-size="12"'))
    note(b, 0, 32, "per species, on held-out clips")
    cols = [("species", 0, "start"), ("gain", 100, "middle"), ("AUC", 152, "middle"), ("slope", 204, "middle"), ("status", 276, "middle")]
    for h, x, a in cols: b.append(T(x, 58, h, "ts tink", a, SM))
    rows = [("boa-ran", "+.21", True, ".91", True, "1.02", True, "ok"),
            ("den-nan", "+.12", True, ".84", True, "0.93", True, "ok"),
            ("sci-nas", "+.01", False, ".58", False, "0.41", False, "poor"),
            ("pse-pla", "n = 9", None, "–", None, "–", None, "insufficient")]
    for i, (sp, g, gok, auc, aok, sl, sok, st) in enumerate(rows):
        y = 84 + i * 32
        b.append(L(0, y + 12, NW, y + 12, "sgrid"))
        b.append(T(0, y + 3, sp, "tc tink", "start", MONO))
        for (val, ok), x in zip([(g, gok), (auc, aok), (sl, sok)], [100, 152, 204]):
            if ok is None: b.append(T(x, y + 3, val, "tc", "middle", MONO))
            else:
                b.append(R(x - 22, y - 9, 44, 17, "fs3" if ok else "fsbad", 4))
                b.append(T(x, y + 3, val, "tc " + ("f3t" if ok else "fbadt"), "middle", MONO))
        cls = {"ok": ("f3", "finv"), "poor": ("fbad", "finv"), "insufficient": ("fsurf sline dash", "tm")}[st]
        b.append(R(276 - 42, y - 9, 84, 18, cls[0], 9)); b.append(T(276, y + 3, st, "tny " + cls[1], "middle"))
    note(b, 0, 232, "gain: beats the species’ base rate")
    note(b, 0, 245, "AUC: ranks true clips above false")
    note(b, 0, 258, "slope ≈ 1: probabilities are right")
    b.append(L(0, 272, NW, 272, "sgrid"))
    note(b, 0, 290, "check before using the curve: only")
    note(b, 0, 303, "species marked ok go on to step 3")
    return svg(NW, 310, "".join(b), "calibration_quality(): ok, poor or insufficient per species")

# ---------------- B · step 3
def b3c():
    b = []
    b.append(T(0, 16, "calibrated_thresholds()", "tc f2t", "start", 'font-size="12"'))
    note(b, 0, 32, "fit, target = 0.95: the score where")
    note(b, 0, 45, "each species’ curve reaches 0.95")
    X, Y = frame(b, 40, 306, 196, 78, "P(tp)")
    sp = [(.6, 1.7, "w25", ""), (.1, 1.5, "w15", 'opacity=".55"')]
    ss = [0.1 + i * .89 / 60 for i in range(61)]
    for a_, b_, w, ex in sp:
        b.append(P("M" + " L".join(f"{X(s):.1f} {Y(logistic(a_ + b_ * logit(s))):.1f}" for s in ss), f"nofill st2 {w}", ex))
    b.append(L(40, Y(.95), 306, Y(.95), "stink dash")); b.append(T(44, Y(.95) - 4, "0.95", "tc tink", "start", MONO))
    for j, (a_, b_, w, ex) in enumerate(sp):
        thr = logistic((logit(.95) - a_) / b_)
        b.append(L(X(thr), Y(.95), X(thr), Y(0), "st2 w15")); b.append(C(X(thr), Y(.95), 3, "f2"))
        b.append(T(X(thr) + (-4 if j == 0 else 4), Y(.12), f"{thr:.2f}", "tc f2t", "end" if j == 0 else "start", MONO))
    b.append(T(46, Y(.6), "thick: boa-ran", "tc f2t", "start", MONO)); b.append(T(46, Y(.6) + 11, "thin: den-nan", "tc f2t", "start", MONO + ' opacity=".7"'))
    b.append(L(0, 232, NW, 232, "sgrid"))
    note(b, 0, 250, "one threshold per species (or site ×")
    note(b, 0, 263, "species), for species ok in step 2;")
    note(b, 0, 276, "rule = \"precision\" asks the A question;")
    note(b, 0, 289, "brms adds threshold_lower")
    return svg(NW, 297, "".join(b), "calibrated_thresholds(): score where P(tp) reaches 0.95")

# ---------------- B · step 4
def b4c():
    b = []
    rows = [("f3", "finv", "ok", ["use the threshold from step 3,", "or go on to Stage 2 · Calibration", "(routes way 1–3)"]),
            ("fbad", "finv", "poor *", ["add a covariate (month, site),", "or use the empirical threshold", "(A) for this species"]),
            ("fsurf sline dash", "tm", "insufficient", ["too few true or false clips: review", "more ↺ Figure 1 · step 2;", "calibration_effort() says how many"])]
    y = 4
    for cls, tcls, lab, nxt in rows:
        b.append(R(0, y, 86, 22, cls, 11)); b.append(T(43, y + 15, lab, "ts " + tcls, "middle", SM))
        b.append(arrow(90, y + 11, 104, y + 11))
        for k, n in enumerate(nxt): note(b, 110, y + 10 + k * 13, n)
        y += 13 * len(nxt) + 26
    b.append(T(0, y + 4, "* if neither helps, see Retraining", "ts fbadt", "start", 'style="font-size:10px"'))
    b.append(L(0, y + 18, NW, y + 18, "sgrid"))
    note(b, 0, y + 36, "B gives no review_support() diagnosis;")
    note(b, 0, y + 49, "later, cell_status() (Stage 3) labels")
    note(b, 0, y + 62, "each cell reliable, probably absent")
    note(b, 0, y + 75, "or unreliable")
    return svg(NW, y + 82, "".join(b), "Next step for each calibration check")

out.update(d7a1=a1c(), d7b1=b1c(), d7b2=b2c(), d7b3=b3c(), d7b4=b4c())
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok v12")
