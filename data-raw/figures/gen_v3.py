"""v3 overview: merged inputs, sampling-design sketch + verdict stack, informed threshold picker with checks and a frequentist/Bayesian fork."""
import json, math, random
from gen_v2 import out
from gen_panels import T, R, C, L, P, arrow, svg, logistic, logit, wave

def overview():
    b = []
    W_, H_ = 1400, 424
    bands = [(10, 200, "INPUT", "bs0", "tb0"), (240, 690, "STAGE 1 · VALIDATION", "bs1", "tb1"),
             (700, 1172, "STAGE 2 · CALIBRATION", "bs2", "tb2"), (1182, 1392, "STAGE 3 · COMMUNITY", "bs3", "tb3")]
    for x0, x1, lab, c, tc in bands:
        b.append(R(x0, 8, x1 - x0, 26, c, 6))
        b.append(T((x0 + x1) / 2, 25.5, lab, "eb " + tc, "middle"))

    # ---------------- INPUT
    ax, ay = 22, 56
    b.append(R(ax, ay, 164, 100, "fsurf sline", 6))
    names = ["ARA01_…_1900.wav", "ARA01_…_2000.wav", "ARA01_…_2100.wav", "BAI01_…_1900.wav", "BAI01_…_2000.wav"]
    for j, nm in enumerate(names):
        y = ay + 10 + j * 18
        b.append(R(ax + 8, y, 18, 12, "fs1", 2))
        b.append(wave(ax + 10, y + 6, 14, 4, 8, "wv1"))
        b.append(T(ax + 32, y + 10, nm, "tc tink", "start", 'font-size="9.5"'))
    b.append(T(ax + 82, ay + 120, "Audio dataset", "tb", "middle"))
    b.append(T(ax + 82, ay + 136, "recordings of the survey", "tm", "middle"))
    cx_, cy_ = 44, 222
    b.append(R(cx_, cy_, 120, 96, "fsurf sline", 6))
    for j, s in enumerate([.94, .41, .77, .18, .63, .52]):
        y = cy_ + 14 + j * 14
        b.append(R(cx_ + 10, y - 5, 56, 5, "fline", 2))
        b.append(T(cx_ + 108, y + 1, f"{s:.2f}", "tc f1t", "end"))
    b.append(T(104, 338, "Classifier output", "tb", "middle"))
    b.append(T(104, 354, "tables with classifier predictions", "tm", "middle"))
    b.append(T(104, 369, "and associated confidence score", "tm", "middle"))
    # merging arrows
    b.append(P("M186 106 H214 V190", "nofill ar"))
    b.append(P("M164 270 H214 V190", "nofill ar"))
    b.append(arrow(214, 190, 240, 190))

    # ---------------- STAGE 1: sampling designs on a recordings grid (rows = files, squares = minutes)
    b.append(T(252, 56, "Select audio clips for review", "tb"))
    b.append('<defs><pattern id="hatch" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             '<line x1="0" y1="0" x2="0" y2="4" class="st2" stroke-width="1.6"/></pattern></defs>')
    rnd = random.Random(21)
    NR, NC = 6, 18
    act = [.35, .9, .95, .8, .55, .1]          # calling activity per file (hour)
    grid = []
    for r in range(NR):
        row = []
        for c in range(NC):
            u = rnd.random()
            if u > act[r] + .1: row.append(None)            # no prediction
            elif u > act[r] * .75: row.append(rnd.uniform(.1, .45))   # below threshold
            else: row.append(rnd.uniform(.5, 1))            # detection
        grid.append(row)
    cw_, ch_, g_ = 9.5, 7, 1.2
    designs = [("top", "for retraining · can’t estimate false positives", "fbadt"),
               ("random (detections)", "threshold and diagnostics · false-positive rate", "f1t"),
               ("random (full dataset)", "minutes or files, expert-verified · presence/absence", "f1t")]
    top2 = []
    for r in range(NR):
        idx = sorted([c for c in range(NC) if grid[r][c] and grid[r][c] >= .5], key=lambda c: -grid[r][c])[:2]
        top2.append(set(idx))
    det_cells = [(c_r, c_c) for c_r in range(NR) for c_c in range(NC) if grid[c_r][c_c] and grid[c_r][c_c] >= .5]
    rd = random.Random(8); drawn_min = set(rd.sample(det_cells, 7))
    rr = random.Random(13); drawn_full = set(rr.sample([(r_, c_) for r_ in range(NR) for c_ in range(NC)], 8))
    for d, (name, note, ncls) in enumerate(designs):
        top = 66 + d * 90
        b.append(T(252, top + 14, name, "tc tink"))
        b.append(T(252, top + 28, note, "ts " + ncls, "start", 'font-size="10.5"'))
        gx0, gy0 = 252, top + 36
        for r in range(NR):
            for c in range(NC):
                v = grid[r][c]
                x = gx0 + c * (cw_ + g_); y = gy0 + r * (ch_ + g_)
                if v is None: b.append(R(x, y, cw_, ch_, "fline", 1, 'fill-opacity=".45"'))
                elif v < .5: b.append(R(x, y, cw_, ch_, "fmuted", 1, 'fill-opacity=".45"'))
                else: b.append(R(x, y, cw_, ch_, "f1", 1, f'fill-opacity="{.35 + .65 * (v - .5) / .5:.2f}"'))
                mark = ((d == 0 and c in top2[r]) or (d == 1 and (r, c) in drawn_min))
                if d == 1 and (r, c) in drawn_min:
                    b.append(R(x - 1.2, y - 1.2, cw_ + 2.4, ch_ + 2.4, "nofill st2 w15", 1.5))
                if mark: b.append(C(x + cw_ / 2, y + ch_ / 2, 1.6, "f2" if d else "tink"))
        if d == 2:
            for (r, c) in drawn_full:
                x = gx0 + c * (cw_ + g_); y = gy0 + r * (ch_ + g_)
                b.append(R(x - 1.2, y - 1.2, cw_ + 2.4, ch_ + 2.4, "st2 w15", 1.5, 'fill="url(#hatch)"'))
    b.append(T(252, 352, "row = 1 recording · square = 1 minute", "ts"))
    b.append(T(252, 366, "colour = highest score (orange ≥ threshold)", "ts"))
    b.append(arrow(502, 214, 530, 214, "ar1"))

    # ---------------- STAGE 1: stack of reviewed clips = verdicts
    b.append(T(540, 56, "Clips → verdicts", "tb"))
    cols = [("top", [(.92, 1), (.88, 1), (.81, 1), (.71, 1), (.62, 0), (.35, 0)]),
            ("full", [(None, 1), (None, 0), (None, 0)]),
            ("det.", [(.81, 1), (.58, 0), (.66, 1), (.52, 0)])]
    for c, (lab, items) in enumerate(cols):
        x = 540 + c * 48
        b.append(T(x + 20, 80, lab, "tc", "middle"))
        for r, (s, ok) in enumerate(items):
            y = 88 + r * 36
            b.append(R(x, y, 40, 30, ("fs3 st3" if ok else "fsbad stbad"), 4))
            if s is not None:
                b.append(T(x + 20, y + 14, f"{s:.2f}", "tc tink", "middle"))
            b.append(T(x + 20, y + (26 if s is not None else 20), "✓" if ok else "✗", ("tny " if s is not None else "tb ") + ("f3t" if ok else "fbadt"), "middle"))
    b.append(T(540, 322, "Verdicts", "tb"))
    b.append(T(540, 338, "presence judged", "tm"))
    b.append(T(540, 353, "positive ✓ or negative ✗", "tm"))
    b.append(T(540, 368, "empty = whole minute", "tm"))
    b.append(T(540, 383, "or file", "tm"))
    b.append(arrow(680, 140, 714, 140, "ar2"))

    # ---------------- STAGE 2: informed threshold picker
    b.append(T(718, 56, "Informed threshold picker", "tb"))
    b.append(T(718, 72, "fit to det. verdicts only", "ts f2t"))
    x0, x1, y0, y1 = 722, 866, 176, 84
    X = lambda s: x0 + s * (x1 - x0); Y = lambda p: y0 - p * (y0 - y1)
    b.append(L(x0, y0, x1, y0, "sline")); b.append(L(x0, y1, x0, y0, "sline"))
    rnd = random.Random(3)
    a_, b_ = .6, 1.7
    for k in range(18):
        s = .05 + .9 * k / 17
        tp = rnd.random() < logistic(a_ + b_ * logit(s))
        b.append(C(X(s), y1 + 4 if tp else y0 - 4, 2.2, "f3" if tp else "fbad", 'opacity=".6"'))
    b.append(P("M" + " L".join(f"{X(s):.1f} {Y(logistic(a_ + b_ * logit(s))):.1f}" for s in [0.01 + i * .98 / 60 for i in range(61)]), "nofill st2 w25"))
    thr = logistic((logit(.95) - a_) / b_)
    b.append(L(x0, Y(.95), x1, Y(.95), "stink dash"))
    b.append(L(X(thr), Y(.95), X(thr), y0, "st2 w15")); b.append(C(X(thr), Y(.95), 3.5, "f2"))
    b.append(T(X(thr), y0 + 14, f"threshold {thr:.2f}", "tc f2t", "middle"))
    b.append(T(x0 + 3, Y(.95) - 4, "p_min", "tc tink"))
    # reliability checks
    b.append(T(884, 80, "Is the curve reliable?", "ts tink"))
    checks = ["model choice · CV log-loss, 1 SE", "per species · info, AUC, calibration", "effort · clips needed per cell"]
    for k, c in enumerate(checks):
        y = 90 + k * 30
        b.append(R(884, y, 262, 24, "fs2", 12))
        b.append(T(898, y + 16, "✓  " + c, "ts f2t"))
    b.append(arrow(866, 124, 880, 124, "ar2"))
    # fork
    b.append(P("M790 200 V330", "nofill ar2"))
    b.append(arrow(790, 252, 904, 252, "ar2")); b.append(arrow(790, 330, 904, 330, "ar2"))
    b.append(T(800, 244, "frequentist (lme4)", "ts tink"))
    b.append(T(800, 322, "Bayesian (brms)", "ts tink"))
    # frequentist: one history
    gx, gy = 912, 228
    for r, row in enumerate(["1101001", "0100110", "1111011", "0010000"]):
        for c, v in enumerate(row):
            b.append(R(gx + c * 15, gy + r * 13, 12, 10, "f2" if v == "1" else "fline", 2))
    b.append(T(1044, 248, "one nightly history", "ts"))
    b.append(T(1044, 262, "p_tp ≥ p_min", "tc"))
    # bayesian: stacked histories
    for k in range(3):
        x = 912 + k * 9; y = 300 + k * 8
        b.append(R(x, y, 100, 52, "fsurf st2", 5))
        if k == 2:
            rnd2 = random.Random(5)
            for r in range(3):
                for c in range(6):
                    b.append(R(x + 8 + c * 14.5, y + 7 + r * 13.5, 11, 10, "f2" if rnd2.random() < .5 else "fline", 2))
    b.append(T(1044, 326, "one history per draw", "ts"))
    b.append(T(1044, 340, "uncertainty kept", "tc"))
    # merge to stage 3
    b.append(P("M1160 252 H1176 V292", "nofill ar")); b.append(P("M1160 330 H1176 V292", "nofill ar"))
    b.append(arrow(1176, 292, 1208, 292))
    # occupancy branch from Bayesian
    b.append(P("M790 330 V392 H1386", "nofill st4 dash"))
    b.append(P("M966 370 V392", "nofill st4 dash"))
    b.append(T(798, 386, "lme4: verdicts + scores", "ts f4t"))
    # by-ear verdicts skip stage 2 and go straight to multiple-method occupancy
    b.append(P("M608 190 V304 H696 V392 H790", "nofill st4 dash"))
    b.append(T(702, 386, "expert checks", "ts f4t"))
    b.append(T(976, 386, "brms: + calibration draws", "ts f4t"))
    b.append(T(1386, 410, "or → occupancy with false positives (crywolf)", "tm f4t", "end"))

    # ---------------- STAGE 3: community matrix
    mx, my = 1222, 242
    vals = [[.9, .2, 0, .6], [.4, .8, .1, 0], [0, .5, .9, .3], [.7, 0, .2, .8]]
    for r, row in enumerate(vals):
        for c, v in enumerate(row):
            b.append(R(mx + c * 25, my + r * 25, 22, 22, "f3" if v else "fline", 3,
                       f'fill-opacity="{(.2 + .8 * v) if v else 1:.2f}"'))
    b.append(T(1270, 56, "Community matrix", "tb", "middle"))
    b.append(T(1270, 72, "effort-standardised", "tm", "middle"))
    b.append(T(1270, 87, "site × month, core species", "tm", "middle"))
    return svg(W_, H_, "".join(b), "Overview of the sheepdog pipeline")

out["overview"] = overview()
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok")
