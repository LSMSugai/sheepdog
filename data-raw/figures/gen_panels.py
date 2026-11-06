"""Generate the SVG panels of the sheepdog pipeline page. Output: panels.json {id: svg}."""
import json, math, random

def esc(s): return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def T(x, y, s, cls="tm", a="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{a}" {extra}>{esc(s)}</text>'
def R(x, y, w, h, cls, rx=3, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" class="{cls}" {extra}/>'
def C(x, y, r, cls, extra=""):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="{cls}" {extra}/>'
def L(x1, y1, x2, y2, cls, extra=""):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{cls}" {extra}/>'
def P(d, cls, extra=""):
    return f'<path d="{d}" class="{cls}" {extra}/>'
def arrow(x1, y1, x2, y2, cls="ar"):
    ang = math.atan2(y2 - y1, x2 - x1); h = 6
    a1 = (x2 - h * math.cos(ang - .45), y2 - h * math.sin(ang - .45))
    a2 = (x2 - h * math.cos(ang + .45), y2 - h * math.sin(ang + .45))
    return (L(x1, y1, x2, y2, cls) +
            P(f"M{a1[0]:.1f} {a1[1]:.1f} L{x2:.1f} {y2:.1f} L{a2[0]:.1f} {a2[1]:.1f}", cls))
def badge(x, y, n, optional=False, color="1"):
    """numbered step badge centred at (x, y)"""
    if optional:
        return C(x, y, 8, f"fsurf st{color} w15") + T(x, y + 3.5, str(n), f"tny f{color}t", "middle")
    return C(x, y, 8, f"f{color}") + T(x, y + 3.5, str(n), "tny finv", "middle")

def svg(w, h, body, label):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">{body}</svg>'
def logistic(z): return 1 / (1 + math.exp(-z))
def logit(p): return math.log(p / (1 - p))
def wave(x, y, w, amp, n=14, cls="wv"):
    pts = []
    rnd = random.Random(int(x * 7 + y))
    for i in range(n + 1):
        xx = x + w * i / n
        a = amp * (0.25 + 0.75 * math.sin(math.pi * i / n)) * (1 if i % 2 else -1) * (0.6 + 0.4 * rnd.random())
        pts.append(f"{xx:.1f} {y + a:.1f}")
    return P("M" + " L".join(pts), cls)

W, H = 440, 250
out = {}

# ------------------------------------------------------------------ OVERVIEW
def overview():
    b = []
    cw = 180
    bands = [(0, 1, "INPUT", "bs0", "tb0"), (1, 3, "STAGE 1 · VALIDATION", "bs1", "tb1"),
             (3, 5, "STAGE 2 · CALIBRATION", "bs2", "tb2"), (5, 6, "STAGE 3 · COMMUNITY", "bs3", "tb3")]
    for i0, i1, lab, c, tc in bands:
        b.append(R(i0 * cw + 6, 8, (i1 - i0) * cw - 12, 26, c, 6))
        b.append(T((i0 + i1) / 2 * cw, 25.5, lab, "eb " + tc, "middle"))
    titles = [("Selection tables", "every prediction, with", "a confidence score"),
              ("Clip sample", "top-score or random", "design, cut to clips"),
              ("Verdicts", "each clip judged", "Positive or Negative"),
              ("P(true | score)", "hierarchical logistic", "calibration"),
              ("Nightly histories", "site × species × night", "detected or not"),
              ("Community matrices", "effort-standardised", "site × month")]
    for i, (t, s1, s2) in enumerate(titles):
        cx = i * cw + cw / 2
        b.append(T(cx, 178, t, "tb", "middle"))
        b.append(T(cx, 196, s1, "tm", "middle"))
        b.append(T(cx, 211, s2, "tm", "middle"))
        if i < 5:
            b.append(arrow(cx + 70, 105, cx + cw - 70, 105))
    # 1 table
    x0 = 40
    b.append(R(x0, 52, 100, 100, "fsurf sline", 6))
    sc = [.94, .41, .77, .18, .63, .52]
    for j, s in enumerate(sc):
        y = 66 + j * 14.5
        b.append(R(x0 + 10, y - 5, 46, 5, "fline", 2))
        b.append(T(x0 + 90, y + 1, f"{s:.2f}", "tc f1t", "end"))
    # 2 clip sample: waveform with dashed selection boxes
    x0 = cw + 22
    b.append(wave(x0, 102, 136, 34, 34, "wv1"))
    for xs in (x0 + 18, x0 + 82):
        b.append(R(xs, 60, 34, 84, "nofill st1 dash", 4))
    # 3 verdicts
    x0 = 2 * cw + 38
    for j, (ok) in enumerate([1, 0, 1, 1]):
        xx = x0 + (j % 2) * 56; yy = 58 + (j // 2) * 48
        b.append(R(xx, yy, 48, 38, "fs3" if ok else "fsbad", 6))
        b.append(T(xx + 24, yy + 26, "✓" if ok else "✗", "big " + ("f3t" if ok else "fbadt"), "middle"))
    # 4 logistic curve
    x0 = 3 * cw + 24
    b.append(L(x0, 150, x0 + 134, 150, "sline"))
    b.append(L(x0, 52, x0, 150, "sline"))
    rnd = random.Random(3)
    for k in range(22):
        s = 0.04 + 0.92 * k / 21
        p = logistic(0.6 + 1.7 * logit(s))
        tp = rnd.random() < p
        b.append(C(x0 + s * 134, 56 if tp else 146, 2.4, "fmuted", 'opacity=".55"'))
    pts = " L".join(f"{x0 + s * 134:.1f} {150 - logistic(0.6 + 1.7 * logit(s)) * 94:.1f}"
                    for s in [0.01 + i * 0.98 / 60 for i in range(61)])
    b.append(P("M" + pts, "nofill st2 w25"))
    b.append(T(x0 + 134, 164, "score →", "tc", "end"))
    # 5 history grid
    x0 = 4 * cw + 30
    pat = ["1101001", "0100110", "1111011", "0010000", "1000101"]
    for r, row in enumerate(pat):
        for c, v in enumerate(row):
            b.append(R(x0 + c * 17, 56 + r * 19, 13, 15, "f2" if v == "1" else "fline", 2))
    # 6 matrix heatmap
    x0 = 5 * cw + 40
    vals = [[.9, .2, 0, .6], [.4, .8, .1, 0], [0, .5, .9, .3], [.7, 0, .2, .8]]
    for r, row in enumerate(vals):
        for c, v in enumerate(row):
            b.append(R(x0 + c * 25, 54 + r * 25, 22, 22, "f3" if v else "fline", 3,
                       f'fill-opacity="{(.2 + .8 * v) if v else 1:.2f}"'))
    # occupancy branch
    b.append(P(f"M{4 * cw + cw / 2} 220 L{4 * cw + cw / 2} 236 L{6 * cw - 20} 236", "nofill st4 dash"))
    b.append(T(1072, 252, "or → occupancy model with false positives", "tm f4t", "end"))
    return svg(1080, 258, "".join(b), "Overview of the sheepdog pipeline")
out["overview"] = overview()

# ------------------------------------------------------------------ STAGE 1
recs = [[.32, .81, .55], [], [.62, .94], [.21], [.58, .47, .88, .71], [], [.36, .52],
        [.91, .66], [], [.28, .74], [.44], [.69, .57]]
def s1a():
    b = []
    rows = [("top", "highest per recording"),
            ("random_detections", "random, score ≥ 0.5"),
            ("random_recordings", "random, any")]
    bx0, bw, gap, bh = 128, 22, 3.6, 46
    for r, (name, sub) in enumerate(rows):
        y0 = 14 + r * 72
        b.append(T(0, y0 + 20, name, "tc tink", "start", 'font-size="9.5"'))
        b.append(T(0, y0 + 35, sub, "ts"))
        if r == 2: b.append(T(0, y0 + 49, "expert check", "ts"))
        drawn_rd = {2, 6, 9}; drawn_rr = {1, 4, 8}
        for i, sc in enumerate(recs):
            x = bx0 + i * (bw + gap)
            cls = "fsurf sline"
            if r == 1 and i in drawn_rd: cls = "fs1 st1"
            if r == 2 and i in drawn_rr: cls = "fs1 st1"
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
    # hour axis
    for i in range(0, 12, 2):
        x = bx0 + i * (bw + gap) + bw / 2
        b.append(T(x, 240, f"{(18 + i) % 24:02d}h", "tc", "middle"))
    return svg(W, H, "".join(b), "Three sampling designs applied to one night of twelve hourly recordings")
out["s1a"] = s1a()

def s1b():
    b = []
    clips = [.94, .88, .81, .74, .71, .66, .62]
    verdict = [1, 1, 1, 0, 1, 1, 0]
    for i, s in enumerate(clips):
        x = 4 + (i % 2) * 70; y = 18 + (i // 2) * 52
        if i == 6: x = 39
        b.append(R(x, y, 62, 40, "fsurf sline", 5))
        b.append(wave(x + 6, y + 17, 50, 9, 12, "wv1"))
        b.append(T(x + 56, y + 35, f"{s:.2f}", "tc", "end"))
    b.append(arrow(150, 120, 182, 120))
    b.append(badge(8, 10, 3))
    # reviewers
    for j, (lab, yy) in enumerate([("R1", 84), ("R2", 156)]):
        pc = "f1" if j == 0 else "nofill st1 w15"
        b.append(C(212, yy, 17, ("fs1 st1" if j == 0 else "fsurf st1")))
        b.append(C(212, yy - 5, 5, pc))
        b.append(P(f"M{212 - 9} {yy + 11} Q{212 - 9} {yy + 1} 212 {yy + 1} Q{212 + 9} {yy + 1} {212 + 9} {yy + 11} Z", pc))
    b.append(L(212, 102, 212, 138, "st1 dash"))
    b.append(T(212, 124, "κ", "tb tink", "middle"))
    b.append(T(212, 196, "agreement →", "ts", "middle"))
    b.append(T(212, 210, "consensus", "ts", "middle"))
    # generic icons (not official logos): desktop window with a spectrogram, browser window with controls
    gx_, gy_ = 168, 14
    b.append(badge(156, 27, 4))
    b.append(R(gx_, gy_, 36, 26, "fsurf st1 w15", 3))
    b.append(L(gx_, gy_ + 7, gx_ + 36, gy_ + 7, "st1"))
    for k in range(7):
        h_ = [6, 12, 9, 15, 8, 13, 5][k]
        b.append(R(gx_ + 4 + k * 4.2, gy_ + 23 - h_, 3, h_, "f1", 0.5))
    b.append(T(gx_ + 18, gy_ + 38, "BirdNET", "tny tm", "middle"))
    b.append(T(212, gy_ + 18, "or", "tny tm", "middle"))
    ax_ = 220
    b.append(R(ax_, gy_, 36, 26, "fsurf st1 w15", 3))
    b.append(L(ax_, gy_ + 7, ax_ + 36, gy_ + 7, "st1"))
    for k in range(3): b.append(C(ax_ + 4 + k * 3.5, gy_ + 3.5, 1, "f1"))
    b.append(L(ax_ + 5, gy_ + 13, ax_ + 31, gy_ + 13, "sline")); b.append(C(ax_ + 14, gy_ + 13, 2.5, "f1"))
    b.append(L(ax_ + 5, gy_ + 20, ax_ + 31, gy_ + 20, "sline")); b.append(C(ax_ + 24, gy_ + 20, 2.5, "f1"))
    b.append(T(ax_ + 18, gy_ + 38, "run_app()", "tny tm", "middle"))
    b.append(arrow(240, 120, 268, 120))
    b.append(badge(284, 10, 5))
    # folder tree
    def folder(x, y, w, lab, cls="fs1 st1"):
        return (P(f"M{x} {y + 4} L{x} {y + 18} L{x + w} {y + 18} L{x + w} {y + 2} L{x + 10} {y + 2} L{x + 7} {y - 2} L{x} {y - 2} Z", cls)
                + T(x + w + 6, y + 13, lab, "tc tink"))
    b.append(folder(276, 28, 18, "Boana_raniceps/"))
    b.append(L(285, 48, 285, 178, "sline"))
    b.append(L(285, 82, 300, 82, "sline")); b.append(L(285, 160, 300, 160, "sline"))
    b.append(folder(302, 72, 16, "Positive/", "fs3 st3"))
    b.append(folder(302, 150, 16, "Negative/", "fsbad stbad"))
    for k in range(5):
        b.append(R(306 + k * 22, 100, 18, 14, "f3", 2))
    for k in range(2):
        b.append(R(306 + k * 22, 178, 18, 14, "fbad", 2))
    b.append(T(306, 132, "5 true positives", "ts"))
    b.append(T(306, 210, "2 false positives", "ts"))
    # step list with light-grey descriptions
    steps = [(3, "Organize clips", "cut_clips() · pack_clips()",
              ["cuts each clip from its recording; one zip per species"], False),
             (4, "Verification", "BirdNET GUI or run_app()",
              ["optional, several reviewers: assign_reviewers(), split_by_reviewer(),",
               "reviewer_agreement() (κ), consensus_verdicts()"], True),
             (5, "Read verdicts", "classify_review() or app_verdicts()",
              ["Positive/Negative folders (GUI) or the app → one verdict per clip;",
               "optional: nightly_presence() gives confirmed presence by night"], True)]
    y = 238
    for n, name, fn, desc, opt in steps:
        b.append(badge(8, y - 4, n))
        b.append(T(22, y, name, "tb"))
        b.append(T(136, y, fn, "tc f1t"))
        for k, d in enumerate(desc):
            b.append(T(22, y + 15 + k * 13, d, "ts", "start", 'font-size="10.5" opacity=".85"'))
        y += 22 + 13 * len(desc) + 6
    return svg(W, 372, "".join(b), "Clips are cut, reviewed by one or more people and sorted into Positive and Negative folders")
out["s1b"] = s1b()

def s1c():
    b = []
    x0, x1, y0, y1 = 44, 420, 210, 22
    X = lambda c: x0 + (c - .1) / .9 * (x1 - x0)
    Y = lambda p: y0 - p * (y0 - y1)
    for p in (0, .5, 1):
        b.append(L(x0, Y(p), x1, Y(p), "sgrid"))
        b.append(T(x0 - 6, Y(p) + 4, f"{p:.1f}", "tc", "end"))
    binp = [.30, .40, .50, .60, .70, .80, .88, .93, .97]
    for i, p in enumerate(binp):
        c = .1 + i * .1
        b.append(R(X(c) + 2, Y(p), X(c + .1) - X(c) - 4, Y(0) - Y(p), "fs1", 2))
    cum = [.58, .62, .67, .72, .78, .84, .91, .94, .97]
    pts = [(X(.1 + i * .1), Y(p)) for i, p in enumerate(cum)]
    b.append(P("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts), "nofill st1 w2"))
    for x, y in pts: b.append(C(x, y, 3, "f1"))
    b.append(L(x0, Y(.9), x1, Y(.9), "stink dash"))
    b.append(T(x1 - 4, Y(.9) + 14, "target 0.90", "tc tink", "end"))
    b.append(L(X(.7), Y(0), X(.7), Y(1), "st1 w15"))
    b.append(R(X(.7) - 6, 2, 104, 18, "f1", 4))
    b.append(T(X(.7) + 46, 15, "threshold 0.70", "tb finv", "middle"))
    for c in (.1, .3, .5, .7, .9):
        b.append(T(X(c), 226, f"{c:.1f}", "tc", "middle"))
    b.append(T((x0 + x1) / 2, 244, "confidence score", "ts", "middle"))
    b.append(T(x0 + 4, 14, "line: precision of clips ≥ score", "ts f1t"))
    b.append(T(x0 + 4, 28, "bars: precision per bin", "ts"))
    return svg(W, H, "".join(b), "Precision by confidence bin and the suggested threshold")
out["s1c"] = s1c()

def s1d():
    b = []
    sites = ["ARA", "BAI", "NHE", "XAR"]
    spp = ["boa-ran", "den-nan", "sci-nas", "pse-pla"]
    grid = [["R", "M", "R", "U"], ["R", "R", "E", "U"], ["M", "R", "N", "M"], ["R", "M", "R", "E"]]
    sty = {"R": ("f3", "finv", "reached"), "M": ("f1", "finv", "review more"),
           "E": ("fmuted", "finv", "exhausted"), "U": ("fbad", "finv", "unreliable"),
           "N": ("fsurf sline dash", "tm", "not reviewed")}
    gx, gy, cw, ch = 64, 30, 62, 36
    for j, s in enumerate(spp):
        b.append(T(gx + j * cw + cw / 2 - 2, 20, s, "tc tink", "middle"))
    for i, site in enumerate(sites):
        b.append(T(gx - 10, gy + i * ch + ch / 2 + 4, site, "tc tink", "end"))
        for j in range(4):
            k = grid[i][j]
            b.append(R(gx + j * cw, gy + i * ch, cw - 4, ch - 4, sty[k][0], 4))
            b.append(T(gx + j * cw + (cw - 4) / 2, gy + i * ch + ch / 2 + 2, {"R": "✓", "M": "+", "E": "–", "U": "!", "N": "?"}[k],
                       "tb " + sty[k][1], "middle"))
    lx = 330
    for n, k in enumerate(["R", "M", "E", "U", "N"]):
        y = 38 + n * 26
        b.append(R(lx, y - 11, 16, 16, sty[k][0], 3))
        b.append(T(lx + 24, y + 2, sty[k][2], "ts tink"))
    b.append(badge(306, 182, 7))
    b.append(T(318, 186, "review_support()", "tc"))
    b.append(P(f"M{gx + cw * 1.5} {gy + 4 * ch + 2} q0 24 -40 24 L{gx - 30} {gy + 4 * ch + 26}", "nofill st1 dash"))
    b.append(arrow(gx - 26, gy + 4 * ch + 26, gx - 44, gy + 4 * ch + 26, "ar1"))
    b.append(T(gx - 40, gy + 4 * ch + 46, "“review more” → draw another round of clips (step 2)", "ts f1t"))
    notes = ["compares the reviewed clips with all the predictions of the selection tables",
             "and labels each site × species cell: “reached” (threshold found),",
             "“review more” (another round, step 2), “exhausted” (nothing left to review),",
             "“unreliable” (precision low even at high scores → retrain), “not reviewed”"]
    for k, n in enumerate(notes):
        b.append(T(0, 252 + k * 13, n, "ts", "start", 'font-size="10.5" opacity=".85"'))
    return svg(W, 310, "".join(b), "Review support of each site by species cell")
out["s1d"] = s1d()

# ------------------------------------------------------------------ STAGE 2
def axes(b, x0, x1, y0, y1, xl, yl, yt=(0, .5, 1), xt=(0, .5, 1)):
    for p in yt:
        y = y0 - p * (y0 - y1)
        b.append(L(x0, y, x1, y, "sgrid"))
        b.append(T(x0 - 6, y + 4, f"{p:g}", "tc", "end"))
    for c in xt:
        b.append(T(x0 + c * (x1 - x0), y0 + 16, f"{c:g}", "tc", "middle"))
    b.append(T((x0 + x1) / 2, y0 + 32, xl, "ts", "middle"))
    b.append(T(x0 - 32, y1 - 8, yl, "ts"))

def s2a():
    b = []
    x0, x1, y0, y1 = 44, 420, 204, 30
    axes(b, x0, x1, y0, y1, "confidence score", "P(true positive)")
    rnd = random.Random(11)
    a, bb = 0.9, 1.7
    for k in range(70):
        s = 0.06 + 0.9 * rnd.random()
        p = logistic(a + bb * logit(s))
        tp = rnd.random() < p
        y = (y1 + 6 + rnd.random() * 8) if tp else (y0 - 6 - rnd.random() * 8)
        b.append(C(x0 + s * (x1 - x0), y, 2.6, "f3" if tp else "fbad", 'opacity=".65"'))
    pts = " L".join(f"{x0 + s * (x1 - x0):.1f} {y0 - logistic(a + bb * logit(s)) * (y0 - y1):.1f}"
                    for s in [0.01 + i * 0.98 / 80 for i in range(81)])
    b.append(P("M" + pts, "nofill st2 w25"))
    b.append(R(x0 + 8, 86, 160, 24, "fsurf st2", 5))
    b.append(T(x0 + 16, 102, "tp ~ logit(confidence)", "tc f2t"))
    b.append(T(x1 - 2, y1 + 26, "Positive = 1", "ts f3t", "end"))
    b.append(T(x1 - 2, y0 - 20, "Negative = 0", "ts fbadt", "end"))
    return svg(W, H, "".join(b), "Reviewed clips as ones and zeros against their score, with a logistic fit")
out["s2a"] = s2a()

def s2b():
    b = []
    models = [("m0", "global", .52, .02), ("m1", "+ species", .44, .02), ("m2", "+ species", .41, .02),
              ("m3", "+ site", .405, .02), ("m4", "species ×", .40, .025)]
    sub2 = ["", "intercept", "slope", "", "site"]
    x0, y0, y1 = 50, 196, 26
    lo, hi = .30, .56
    Y = lambda v: y0 - (v - lo) / (hi - lo) * (y0 - y1)
    for v in (.3, .4, .5):
        b.append(L(x0, Y(v), 428, Y(v), "sgrid")); b.append(T(x0 - 6, Y(v) + 4, f"{v:.1f}", "tc", "end"))
    b.append(T(x0 - 36, 14, "CV log-loss (lower is better)", "ts"))
    best = min(m[2] for m in models); se = .02
    for i, (m, l1, v, e) in enumerate(models):
        x = x0 + 18 + i * 66
        sel = m == "m2"
        b.append(R(x, Y(v), 40, y0 - Y(v), "f2" if sel else "fs2", 3))
        b.append(L(x + 20, Y(v - e), x + 20, Y(v + e), "stink"))
        b.append(L(x + 14, Y(v - e), x + 26, Y(v - e), "stink")); b.append(L(x + 14, Y(v + e), x + 26, Y(v + e), "stink"))
        b.append(T(x + 20, y0 + 16, m, "tc tink", "middle"))
        b.append(T(x + 20, y0 + 30, l1, "ts", "middle"))
        if sub2[i]: b.append(T(x + 20, y0 + 43, sub2[i], "ts", "middle"))
    b.append(L(x0, Y(best + se), 394, Y(best + se), "st2 dash"))
    b.append(T(432, Y(best + se) + 4, "+1 SE", "tc f2t", "end"))
    xs = x0 + 18 + 2 * 66 + 20
    b.append(T(xs, Y(.41) - 62, "simplest model", "tb f2t", "middle"))
    b.append(T(xs, Y(.41) - 48, "within 1 SE", "ts f2t", "middle"))
    b.append(arrow(xs, Y(.41) - 42, xs, Y(.41) - 26, "ar2"))
    return svg(W, H, "".join(b), "Candidate models compared by cross-validated log-loss, with the one-standard-error rule")
out["s2b"] = s2b()

def s2c():
    b = []
    x0, x1, y0, y1 = 44, 420, 204, 30
    axes(b, x0, x1, y0, y1, "confidence score", "P(true positive)")
    pm = .95
    X = lambda s: x0 + s * (x1 - x0); Y = lambda p: y0 - p * (y0 - y1)
    b.append(L(x0, Y(pm), x1, Y(pm), "stink dash"))
    b.append(T(x0 + 4, Y(pm) - 6, "p_min 0.95", "tc tink"))
    rnd = random.Random(5)
    for _ in range(18):  # posterior draws for species B
        a = .5 + rnd.gauss(0, .35); bb = 1.5 + rnd.gauss(0, .2)
        pts = " L".join(f"{X(s):.1f} {Y(logistic(a + bb * logit(s))):.1f}" for s in [0.02 + i * .96 / 40 for i in range(41)])
        b.append(P("M" + pts, "nofill st2", 'opacity=".13"'))
    sp = [("boa-ran", 2.0, 2.0, .98, "st2 w25", ""), ("den-nan", .5, 1.5, .97, "st2 w2", 'stroke-dasharray="6 3"'),
          ("sci-nas", -1, .9, .85, "stbad w2", 'stroke-dasharray="2 3"')]
    for name, a, bb, smax, cls, ex in sp:
        ss = [0.02 + i * (smax - .02) / 60 for i in range(61)]
        b.append(P("M" + " L".join(f"{X(s):.1f} {Y(logistic(a + bb * logit(s))):.1f}" for s in ss), "nofill " + cls, ex))
        thr = logistic((logit(pm) - a) / bb)
        if thr <= smax:
            b.append(C(X(thr), Y(pm), 4, "f2"))
            b.append(T(X(thr), Y(pm) - 8, f"{thr:.2f}", "tc f2t", "middle"))
    b.append(T(X(.3) - 8, Y(.58), "boa-ran", "tc f2t", "end"))
    b.append(T(X(.57), Y(.5), "den-nan", "tc f2t"))
    endp = logistic(-1 + .9 * logit(.85))
    b.append(T(X(.85) + 4, Y(endp) + 4, "sci-nas", "tc fbadt"))
    b.append(T(X(1), Y(.15), "never reaches p_min", "ts fbadt", "end"))
    b.append(T(X(1), Y(.15) + 14, "within its reviewed scores", "ts fbadt", "end"))
    b.append(T(X(.02), Y(.82), "faint lines: brms draws", "ts"))
    return svg(W, H, "".join(b), "Calibration curves per species and the score at which each reaches p_min")
out["s2c"] = s2c()

def s2d():
    b = []
    # one night timeline
    b.append(T(0, 16, "one night · ARA · boa-ran", "tc tink"))
    x0, x1, yb, yt = 8, 196, 150, 40
    b.append(L(x0, yb, x1, yb, "sline"))
    b.append(L(x0, yt + 110 - .95 * 110, x1, yt + 110 - .95 * 110, "stink dash"))
    rnd = random.Random(2)
    ps = [.12, .97, .4, .99, .63, .96, .2, .88, .31]
    for i, p in enumerate(ps):
        x = x0 + 10 + i * 21
        y = yb - p * 110
        b.append(L(x, yb, x, y, "sline"))
        b.append(C(x, y, 4, "f2" if p >= .95 else "nofill st2"))
    b.append(T(x0, yb + 18, "18h", "tc")); b.append(T(x1, yb + 18, "05h", "tc", "end"))
    b.append(T(x0, yb + 40, "3 detections ≥ p_min", "ts f2t"))
    b.append(T(x0, yb + 54, "k = 1 → night detected", "ts f2t"))
    b.append(arrow(204, 100, 232, 100, "ar2"))
    # history grid
    gx, gy = 244, 34
    b.append(T(gx, 16, "detection history (nights →)", "tc tink"))
    pat = {"boa-ran": "1101101001", "den-nan": "0110010110", "sci-nas": "1111011111", "pse-pla": "0010000100"}
    for r, (sp, row) in enumerate(pat.items()):
        b.append(T(gx, gy + r * 30 + 14, sp, "tc"))
        for c, v in enumerate(row):
            cls = "f2" if v == "1" else "fline"
            hl = (r == 0 and c == 3)
            b.append(R(gx + 56 + c * 13, gy + r * 30, 10, 18, cls, 2, 'stroke-width="2"' + (' class-x' if False else '')))
            if hl: b.append(R(gx + 54 + c * 13, gy + r * 30 - 2, 14, 22, "nofill stink w15", 3))
    b.append(T(gx, gy + 4 * 30 + 16, "k = 1, 2, 3 kept as columns", "ts"))
    b.append(T(gx, gy + 4 * 30 + 30, "for sensitivity analysis", "ts"))
    return svg(W, H, "".join(b), "Every detection is scored and nights are marked detected when enough detections are reliable")
out["s2d"] = s2d()

# ------------------------------------------------------------------ STAGE 3
def s3a():
    b = []
    sites = ["ARA", "BAI", "NHE", "XAR"]
    spp = ["boa-ran", "den-nan", "sci-nas", "pse-pla", "phy-cuv", "lep-fus"]
    g = ["RRURRA", "RRRARR", "RARRRU", "RRRRAR"]
    gx, gy, cw, ch = 50, 40, 54, 30
    for j, s in enumerate(spp):
        b.append(T(gx + j * cw + 24, 30, s, "tc tink", "middle"))
    for i, site in enumerate(sites):
        b.append(T(gx - 8, gy + i * ch + 19, site, "tc tink", "end"))
        for j in range(6):
            k = g[i][j]
            cls = {"R": "f3", "A": "fs3 st3", "U": "fbad"}[k]
            b.append(R(gx + j * cw, gy + i * ch, cw - 6, ch - 6, cls, 4))
            if k == "A": b.append(T(gx + j * cw + 24, gy + i * ch + 17, "0", "tc f3t", "middle"))
            if k == "U": b.append(T(gx + j * cw + 24, gy + i * ch + 18, "!", "tb finv", "middle"))
    core = [0, 1, 3, 4]
    yb = gy + 4 * ch + 4
    for j in core:
        b.append(P(f"M{gx + j * cw} {yb} l0 6 l{cw - 6} 0 l0 -6", "nofill st3 w15"))
        b.append(T(gx + j * cw + 24, yb + 20, "core", "tb f3t", "middle"))
    for j in (2, 5):
        b.append(T(gx + j * cw + 24, yb + 20, "dropped", "ts fbadt", "middle"))
    ly = 222
    for n, (cls, lab) in enumerate([("f3", "reliable"), ("fs3 st3", "probably absent"), ("fbad", "unreliable")]):
        x = 50 + n * 120
        b.append(R(x, ly - 10, 14, 14, cls, 3)); b.append(T(x + 20, ly + 1, lab, "ts tink"))
    return svg(W, H, "".join(b), "Cell status by site and species, and the core species that enter the matrices")
out["s3a"] = s3a()

def s3b():
    b = []
    b.append(T(0, 16, "ARA · November · boa-ran", "tc tink"))
    gx, gy, cs = 6, 30, 27
    norec = {4, 5, 6, 17, 18, 19}
    det = {0, 2, 3, 8, 9, 11, 14, 21, 23, 26, 29}
    for d in range(30):
        x = gx + (d % 7) * cs; y = gy + (d // 7) * cs
        if d in norec: cls = "nofill sline dash"
        elif d in det: cls = "f3"
        else: cls = "fsurf st3"
        b.append(R(x, y, cs - 5, cs - 5, cls, 3))
        b.append(T(x + (cs - 5) / 2, y + 15, str(d + 1), "tny " + ("finv" if d in det else "tm"), "middle"))
    ly = gy + 5 * cs + 8
    for n, (cls, lab) in enumerate([("f3", "detected"), ("fsurf st3", "recorded, not detected"), ("nofill sline dash", "no recording")]):
        b.append(R(gx, ly + n * 18, 12, 12, cls, 2)); b.append(T(gx + 18, ly + n * 18 + 10, lab, "ts"))
    fx = 236
    b.append(T(fx, 76, "nights detected", "ts", "start"))
    b.append(T(fx + 170, 76, "11", "tb tink", "end"))
    b.append(L(fx, 88, fx + 172, 88, "stink w15"))
    b.append(T(fx, 108, "nights recorded", "ts", "start"))
    b.append(T(fx + 170, 108, "24", "tb tink", "end"))
    b.append(R(fx, 130, 172, 40, "fs3", 6))
    b.append(T(fx + 86, 156, "frequency = 0.46", "tb f3t", "middle"))
    b.append(T(fx, 196, "a cell of the site × month", "ts"))
    b.append(T(fx, 210, "frequency matrix", "ts"))
    return svg(W, H, "".join(b), "Effort standardisation: nights with detection divided by nights recorded")
out["s3b"] = s3b()

def s3c():
    b = []
    rows = ["ARA·Oct", "ARA·Nov", "ARA·Dec", "BAI·Oct", "BAI·Nov", "BAI·Dec"]
    cols = ["boa-ran", "den-nan", "pse-pla", "phy-cuv"]
    v = [[.38, .71, .10, .52], [.46, .63, .00, .58], [.29, .80, .13, .40],
         [.00, .55, .62, .21], [.08, .49, .74, .33], [.17, .60, .68, .25]]
    gx, gy, cw, ch = 82, 32, 76, 30
    for j, c in enumerate(cols): b.append(T(gx + j * cw + 35, 22, c, "tc tink", "middle"))
    for i, r in enumerate(rows):
        b.append(T(gx - 8, gy + i * ch + 19, r, "tc tink", "end"))
        for j in range(4):
            val = v[i][j]
            b.append(R(gx + j * cw, gy + i * ch, cw - 6, ch - 5, "f3" if val else "fline", 3,
                       f'fill-opacity="{(.15 + .85 * val) if val else 1:.2f}"'))
            b.append(T(gx + j * cw + 35, gy + i * ch + 17, f"{val:.2f}", "tc " + ("finv" if val > .5 else "tink"), "middle"))
    b.append(R(gx - 2, gy + ch - 2, cw - 2, ch - 1, "nofill stink w15", 4))
    b.append(T(gx, 236, "+ count matrix · effort table · trials matrix (gllvm)", "ts"))
    return svg(W, H, "".join(b), "Site by month community matrix of nightly detection frequencies")
out["s3c"] = s3c()

def s3d():
    b = []
    x0, x1, y0, y1 = 30, 420, 210, 24
    b.append(L(x0, (y0 + y1) / 2, x1, (y0 + y1) / 2, "sgrid")); b.append(L((x0 + x1) / 2, y0, (x0 + x1) / 2, y1, "sgrid"))
    b.append(T(x1, y0 + 18, "NMDS1", "tc", "end")); b.append(T(x0, y1 - 8, "NMDS2", "tc"))
    pts = {"ARA": [(110, 70, "Oct"), (128, 92, "Nov"), (96, 98, "Dec")],
           "BAI": [(300, 150, "Oct"), (282, 168, "Nov"), (318, 176, "Dec")],
           "NHE": [(250, 64, "Oct"), (272, 84, "Nov"), (232, 88, "Dec")],
           "XAR": [(140, 172, "Oct"), (160, 160, "Nov"), (122, 186, "Dec")]}
    shapes = ["f3", "f2", "f1", "f4"]
    for k, (site, ps) in enumerate(pts.items()):
        cx = sum(p[0] for p in ps) / 3; cy = sum(p[1] for p in ps) / 3
        b.append(C(cx, cy, 34, "nofill sline dash"))
        for x, y, m in ps:
            b.append(C(x, y, 5, shapes[k]))
        b.append(T(cx, cy - 40, site, "tb tink", "middle"))
    b.append(T(x0, 244, "vegan (PCoA, NMDS, RDA) · gllvm with the trials matrix", "ts"))
    return svg(W, H, "".join(b), "Ordination of site by month samples")
out["s3d"] = s3d()

# ------------------------------------------------------------------ OCCUPANCY
def s4a():
    b = []
    hdr = ["occasion", "top score", "review"]
    rows = [("ARA · n1 · 19h", .97, "confirmed"), ("ARA · n1 · 21h", .62, "rejected"), ("ARA · n2 · 20h", .88, "—"),
            ("BAI · n1 · 23h", .55, "confirmed"), ("BAI · n2 · 19h", .00, "—"), ("NHE · n1 · 22h", .74, "—")]
    xs = [0, 100, 164]
    for j, h in enumerate(hdr): b.append(T(xs[j], 18, h, "tc tink"))
    for i, (o, s, r) in enumerate(rows):
        y = 40 + i * 26
        b.append(L(0, y + 8, 236, y + 8, "sgrid"))
        b.append(T(xs[0], y, o, "tc"))
        b.append(R(xs[1], y - 9, 44 * s, 10, "f4", 2) if s else T(xs[1], y, "0", "tc"))
        cls = {"confirmed": "f3t", "rejected": "fbadt"}.get(r, "tm")
        b.append(T(xs[2], y, r, "ts " + cls))
    b.append(arrow(232, 110, 254, 110, "ar4"))
    fx, fy = 262, 26
    b.append(R(fx, fy, 174, 182, "fs4 st4", 8))
    b.append(T(fx + 10, fy + 20, "sheepdog-occupancy/", "tc f4t"))
    for k, f in enumerate(["occasions.csv", "detections.csv", "scores.csv", "validation.csv", "sites.csv",
                           "calibration_draws.parquet", "schema.json"]):
        b.append(T(fx + 12, fy + 44 + k * 19, f, "tc tink"))
    b.append(T(fx, 234, "→ crywolf, or any software", "ts f4t"))
    return svg(W, H, "".join(b), "Occasions, scores and reviews exported for an occupancy model with false positives")
out["s4a"] = s4a()

def s4b():
    b = []
    for k in range(4):
        x = 10 + k * 14; y = 30 + k * 14
        b.append(R(x, y, 120, 92, "fsurf st4", 6))
        rnd = random.Random(k + 1)
        if k == 3:
            for r in range(5):
                for c in range(7):
                    b.append(R(x + 10 + c * 14.5, y + 10 + r * 15.5, 10, 11, "f4" if rnd.random() < .45 else "fline", 2))
    b.append(T(10, 18, "one detection matrix per draw", "tc tink"))
    b.append(T(52, 200, "draw 1 … S", "ts"))
    b.append(arrow(190, 110, 220, 110, "ar4"))
    # posterior densities
    x0, x1, yb = 236, 432, 176
    def dens(mu, sd, cls, ex=""):
        pts = []
        for i in range(61):
            x = mu - 3.2 * sd + i * 6.4 * sd / 60
            y = math.exp(-((x - mu) / sd) ** 2 / 2)
            pts.append(f"{x0 + x * (x1 - x0):.1f} {yb - y * 100:.1f}")
        return P("M" + " L".join(pts), cls, ex)
    rnd = random.Random(9)
    for _ in range(7):
        b.append(dens(.55 + rnd.gauss(0, .05), .07, "nofill st4", 'opacity=".35"'))
    b.append(dens(.55, .095, "nofill st4 w25"))
    b.append(L(x0, yb, x1, yb, "sline"))
    for c in (0, .5, 1): b.append(T(x0 + c * (x1 - x0), yb + 16, f"{c:g}", "tc", "middle"))
    b.append(T((x0 + x1) / 2, yb + 34, "occupancy ψ", "ts", "middle"))
    b.append(T(x0, 40, "fit each, pool posteriors", "tc tink"))
    b.append(T(x0, 56, "thick line: pooled", "ts f4t"))
    return svg(W, H, "".join(b), "Calibration uncertainty carried into occupancy estimates by fitting one model per draw")
out["s4b"] = s4b()

json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print({k: len(v) for k, v in out.items()})
