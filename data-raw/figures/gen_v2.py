"""v2 panels: new overview, reframed stage 2. Reuses helpers and other panels from gen_panels."""
import json, math, random
from gen_panels import (T, R, C, L, P, arrow, svg, logistic, logit, wave, axes, out, W, H)

# ------------------------------------------------------------------ OVERVIEW v2
def overview():
    b = []
    cw, n = 180, 7
    bands = [(0, 2, "INPUT", "bs0", "tb0"), (2, 4, "STAGE 1 · VALIDATION", "bs1", "tb1"),
             (4, 6, "STAGE 2 · CALIBRATION", "bs2", "tb2"), (6, 7, "STAGE 3 · COMMUNITY", "bs3", "tb3")]
    for i0, i1, lab, c, tc in bands:
        b.append(R(i0 * cw + 6, 8, (i1 - i0) * cw - 12, 26, c, 6))
        b.append(T((i0 + i1) / 2 * cw, 25.5, lab, "eb " + tc, "middle"))
    titles = [("Audio dataset", ["recordings of the", "acoustic survey"]),
              ("Classifier output", ["tables with classifier", "predictions and associated", "confidence score"]),
              ("Clip audios for review", ["three modes: top-score,", "random (detections) or", "random (full dataset)"]),
              ("Verdicts", ["presence is judged", "positive or negative"]),
              ("Threshold picker", ["P(true | score) from a", "checked logistic calibration"]),
              ("Nightly histories", ["site × species × night", "detected or not"]),
              ("Community matrices", ["effort-standardised", "site × month"])]
    for i, (t, subs) in enumerate(titles):
        cx = i * cw + cw / 2
        b.append(T(cx, 178, t, "tb", "middle"))
        for k, s in enumerate(subs):
            b.append(T(cx, 196 + k * 15, s, "tm", "middle"))
        if i < n - 1:
            b.append(arrow(cx + 70, 105, cx + cw - 70, 105))
    # 0 audio dataset: list of audio files
    x0 = 22
    b.append(R(x0, 50, 136, 104, "fsurf sline", 6))
    names = ["ARA01_…_1900.wav", "ARA01_…_2000.wav", "ARA01_…_2100.wav", "BAI01_…_1900.wav", "BAI01_…_2000.wav"]
    for j, nm in enumerate(names):
        y = 62 + j * 18
        b.append(R(x0 + 8, y, 18, 12, "fs1", 2))
        b.append(wave(x0 + 10, y + 6, 14, 4, 8, "wv1"))
        b.append(T(x0 + 32, y + 10, nm, "tc tink", "start", 'font-size="9.5"'))
    # 1 classifier output table
    x0 = cw + 40
    b.append(R(x0, 52, 100, 100, "fsurf sline", 6))
    for j, s in enumerate([.94, .41, .77, .18, .63, .52]):
        y = 66 + j * 14.5
        b.append(R(x0 + 10, y - 5, 46, 5, "fline", 2))
        b.append(T(x0 + 90, y + 1, f"{s:.2f}", "tc f1t", "end"))
    # 2 clips
    x0 = 2 * cw + 22
    b.append(wave(x0, 102, 136, 34, 34, "wv1"))
    for xs in (x0 + 18, x0 + 82):
        b.append(R(xs, 60, 34, 84, "nofill st1 dash", 4))
    # 3 verdicts
    x0 = 3 * cw + 38
    for j, ok in enumerate([1, 0, 1, 1]):
        xx = x0 + (j % 2) * 56; yy = 58 + (j // 2) * 48
        b.append(R(xx, yy, 48, 38, "fs3" if ok else "fsbad", 6))
        b.append(T(xx + 24, yy + 26, "✓" if ok else "✗", "big " + ("f3t" if ok else "fbadt"), "middle"))
    # 4 threshold picker: curve + p_min line + threshold marker
    x0 = 4 * cw + 24; X = lambda s: x0 + s * 134; Y = lambda p: 150 - p * 94
    b.append(L(x0, 150, x0 + 134, 150, "sline")); b.append(L(x0, 52, x0, 150, "sline"))
    a_, b_ = 0.6, 1.7
    b.append(P("M" + " L".join(f"{X(s):.1f} {Y(logistic(a_ + b_ * logit(s))):.1f}"
                               for s in [0.01 + i * 0.98 / 60 for i in range(61)]), "nofill st2 w25"))
    thr = logistic((logit(.95) - a_) / b_)
    b.append(L(x0, Y(.95), x0 + 134, Y(.95), "stink dash"))
    b.append(L(X(thr), Y(.95), X(thr), 150, "st2 w15"))
    b.append(C(X(thr), Y(.95), 4, "f2"))
    b.append(T(X(thr), 164, f"{thr:.2f}", "tc f2t", "middle"))
    b.append(T(x0 + 4, Y(.95) - 5, "p_min", "tc tink"))
    # 5 history grid
    x0 = 5 * cw + 30
    for r, row in enumerate(["1101001", "0100110", "1111011", "0010000", "1000101"]):
        for c, v in enumerate(row):
            b.append(R(x0 + c * 17, 56 + r * 19, 13, 15, "f2" if v == "1" else "fline", 2))
    # 6 matrix
    x0 = 6 * cw + 40
    vals = [[.9, .2, 0, .6], [.4, .8, .1, 0], [0, .5, .9, .3], [.7, 0, .2, .8]]
    for r, row in enumerate(vals):
        for c, v in enumerate(row):
            b.append(R(x0 + c * 25, 54 + r * 25, 22, 22, "f3" if v else "fline", 3,
                       f'fill-opacity="{(.2 + .8 * v) if v else 1:.2f}"'))
    # occupancy branch
    bx = 5 * cw + cw / 2
    b.append(P(f"M{bx} 236 L{bx} 250 L{n * cw - 20} 250", "nofill st4 dash"))
    b.append(T(n * cw - 8, 268, "or → occupancy model with false positives", "tm f4t", "end"))
    return svg(n * cw, 276, "".join(b), "Overview of the sheepdog pipeline")
out["overview"] = overview()

# ------------------------------------------------------------------ STAGE 2 v2
def s2q():  # calibration_quality table
    b = []
    cols = [("species", 0, "start"), ("adds info", 128, "middle"), ("discriminates", 214, "middle"),
            ("calibrated", 300, "middle"), ("status", 390, "middle")]
    sub = ["", "log-loss gain", "AUC", "slope ≈ 1", ""]
    for (h, x, a), s in zip(cols, sub):
        b.append(T(x, 18, h, "tb", a))
        if s: b.append(T(x, 33, s, "tc", a))
    rows = [("boa-ran", "+0.21", True, "0.91", True, "1.02", True, "ok"),
            ("den-nan", "+0.12", True, "0.84", True, "0.93", True, "ok"),
            ("sci-nas", "+0.01", False, "0.58", False, "0.41", False, "poor"),
            ("pse-pla", "n = 9", None, "–", None, "–", None, "insufficient")]
    for i, (sp, g, gok, auc, aok, sl, sok, st) in enumerate(rows):
        y = 64 + i * 38
        b.append(L(0, y + 14, 440, y + 14, "sgrid"))
        b.append(T(0, y + 4, sp, "tc tink", "start", 'font-size="11.5"'))
        for (val, ok), x in zip([(g, gok), (auc, aok), (sl, sok)], [128, 214, 300]):
            if ok is None:
                b.append(T(x, y + 4, val, "tc", "middle"))
            else:
                b.append(R(x - 30, y - 10, 60, 20, "fs3" if ok else "fsbad", 4))
                b.append(T(x, y + 4, ("✓ " if ok else "✗ ") + val, "tc " + ("f3t" if ok else "fbadt"), "middle"))
        cls = {"ok": ("f3", "finv"), "poor": ("fbad", "finv"), "insufficient": ("fsurf sline dash", "tm")}[st]
        b.append(R(390 - 42, y - 10, 84, 20, cls[0], 10))
        b.append(T(390, y + 4, st, "ts " + cls[1], "middle"))
    b.append(T(0, 236, "held-out clips, per species · calibration_quality()", "ts"))
    return svg(W, H, "".join(b), "Per-species checks of the calibration on held-out clips")
out["s2q"] = s2q()

def s2c():  # curves per species -> threshold; histogram of all detections under the axis
    b = []
    x0, x1, y0, y1 = 44, 420, 176, 26
    X = lambda s: x0 + s * (x1 - x0); Y = lambda p: y0 - p * (y0 - y1)
    for p in (0, .5, 1):
        b.append(L(x0, Y(p), x1, Y(p), "sgrid")); b.append(T(x0 - 6, Y(p) + 4, f"{p:g}", "tc", "end"))
    b.append(T(x0 - 32, y1 - 10, "P(true positive)", "ts"))
    pm = .95
    b.append(L(x0, Y(pm), x1, Y(pm), "stink dash"))
    b.append(T(x0 + 4, Y(pm) - 6, "p_min 0.95", "tc tink"))
    sp = [("boa-ran", 2.0, 2.0, .98, "st2 w25", ""), ("den-nan", .5, 1.5, .97, "st2 w2", 'stroke-dasharray="6 3"')]
    thrs = []
    for name, a, bb, smax, cls, ex in sp:
        ss = [0.02 + i * (smax - .02) / 60 for i in range(61)]
        b.append(P("M" + " L".join(f"{X(s):.1f} {Y(logistic(a + bb * logit(s))):.1f}" for s in ss), "nofill " + cls, ex))
        thr = logistic((logit(pm) - a) / bb); thrs.append(thr)
        b.append(C(X(thr), Y(pm), 4, "f2"))
        b.append(L(X(thr), Y(pm), X(thr), y0, "st2 dot"))
        b.append(T(X(thr), Y(pm) - 8, f"{thr:.2f}", "tc f2t", "middle"))
    b.append(T(X(.3) - 8, Y(.58), "boa-ran", "tc f2t", "end"))
    b.append(T(X(.65), Y(.5), "den-nan", "tc f2t"))
    # histogram of every detection of boa-ran (unreviewed included), coloured by reliability
    rnd = random.Random(4)
    scores = [min(.995, max(.02, rnd.betavariate(1.3, 1.1))) for _ in range(600)]
    bins = [0] * 25
    for s in scores: bins[min(24, int(s * 25))] += 1
    mx = max(bins); hb = 34
    for i, n_ in enumerate(bins):
        s0 = i / 25
        h = n_ / mx * hb
        rel = s0 + .02 >= thrs[0]
        b.append(R(X(s0) + 1, y0 + 6, (x1 - x0) / 25 - 2, h, "f2" if rel else "fline", 1))
    for c in (0, .5, 1):
        b.append(T(X(c), y0 + hb + 20, f"{c:g}", "tc", "middle"))
    b.append(T(x0, y0 + hb + 38, "bars: every boa-ran detection, reviewed or not, by score", "ts"))
    b.append(T(x0, y0 + hb + 52, "→ p_tp for each detection · one score threshold per species", "ts f2t"))
    return svg(W, 266, "".join(b), "Calibration curves per species applied to every detection, and the score threshold")
out["s2c"] = s2c()

def s2bayes():
    b = []
    # left: posterior of P(tp) for one detection
    x0, x1, yb = 14, 210, 150
    X = lambda p: x0 + (p - .8) / .2 * (x1 - x0)
    b.append(T(x0, 16, "one detection · score 0.81", "tc tink"))
    mu, sd = .962, .018
    pts = []
    for i in range(81):
        p = .8 + i * .2 / 80
        d = math.exp(-((p - mu) / sd) ** 2 / 2)
        pts.append((X(p), yb - d * 96, p))
    area = [f"{x:.1f} {y:.1f}" for x, y, p in pts if p >= .95]
    b.append(P(f"M{X(.95):.1f} {yb} L" + " L".join(area) + f" L{X(1):.1f} {yb} Z", "fs2"))
    b.append(P("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y, p in pts), "nofill st2 w2"))
    b.append(L(x0, yb, x1, yb, "sline"))
    for p in (.8, .9, 1): b.append(T(X(p), yb + 16, f"{p:g}", "tc", "middle"))
    b.append(T((x0 + x1) / 2, yb + 32, "P(true positive)", "ts", "middle"))
    b.append(L(X(.95), yb, X(.95), 34, "stink dash")); b.append(T(X(.95) - 4, 44, "p_min", "tc tink", "end"))
    lo = mu - 1.645 * sd
    b.append(L(X(lo), yb, X(lo), yb - 26, "stbad w15")); b.append(T(X(lo) - 4, yb - 30, "p_tp_lower", "tc fbadt", "end"))
    b.append(L(X(mu), yb, X(mu), yb - 96, "st2 w15")); b.append(T(X(mu) + 4, 40, "p_tp (mean)", "tc f2t"))
    b.append(T(x0, 31, "shaded: pr_reliable = 0.75", "ts f2t"))
    # right: many histories (draws)
    b.append(arrow(222, 92, 246, 92, "ar2"))
    gx = 262
    b.append(T(gx, 16, "history_draws()", "tc tink"))
    for k in range(4):
        x = gx + k * 12; y = 30 + k * 12
        b.append(R(x, y, 118, 86, "fsurf st2", 6))
        if k == 3:
            rnd = random.Random(7)
            for r in range(4):
                for c in range(6):
                    b.append(R(x + 10 + c * 17, y + 10 + r * 18, 13, 14, "f2" if rnd.random() < .5 else "fline", 2))
    b.append(T(gx, 168, "one history per posterior draw", "ts"))
    b.append(T(gx, 182, "→ community_matrices_draws()", "ts f2t"))
    b.append(T(gx, 196, "→ occasion_draws()", "ts f2t"))
    # diagnostics chips
    chips = ["prior check", "R-hat · ESS", "sensitivity", "pp check"]
    x = 0
    for c in chips:
        w = 7 * len(c) + 18
        b.append(R(x, 220, w, 22, "fs2", 11)); b.append(T(x + w / 2, 235, c, "ts f2t", "middle"))
        x += w + 8
    return svg(W, H, "".join(b), "Bayesian calibration: a posterior for each detection, histories over draws, and model checks")
out["s2bayes"] = s2bayes()

json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok", list(out))
