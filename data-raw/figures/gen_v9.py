"""v9: several-reviewers row with visuals; summary step with tighter outputs and no post_validation bar."""
import json
from gen_v8 import *   # runs v8 and everything before it
from gen_panels import T, R, C, L, P, svg, arrow, wave

def person(b, x, y, filled, s=1.0):
    pc = "f1" if filled else "nofill st1 w15"
    b.append(C(x, y - 5 * s, 4.2 * s, pc))
    b.append(P(f"M{x-7.5*s} {y+7*s} Q{x-7.5*s} {y-.5*s} {x} {y-.5*s} Q{x+7.5*s} {y-.5*s} {x+7.5*s} {y+7*s} Z", pc))

def clip(b, x, y, who, w=22, h=13):
    """who: 'A', 'B' or 'AB' (overlap)."""
    b.append(R(x, y, w, h, "fsurf sline", 2))
    b.append(wave(x + 3, y + h / 2, w - 6, 3.5, 6, "wv1"))
    if "A" in who: b.append(R(x - 1, y - 4, 7, 7, "f1", 3.5))
    if "B" in who: b.append(R(x + (7 if who == "AB" else -1), y - 4, 7, 7, "fsurf st1 w15", 3.5))

def mini_folder(b, x, y, cls="fs1 st1", w=18):
    b.append(P(f"M{x} {y+4} L{x} {y+16} L{x+w} {y+16} L{x+w} {y+2} L{x+9} {y+2} L{x+6} {y-2} L{x} {y-2} Z", cls))

def vis(b, i, x, y):
    """small drawing for box i, in the band y..y+44"""
    if i == 0:   # assign: clips tagged by reviewer, one overlap clip
        tags = ["A", "B", "A", "B", "AB", "A"]
        for k, t in enumerate(tags):
            clip(b, x + 2 + (k % 3) * 30, y + 6 + (k // 3) * 22, t)
        person(b, x + 104, y + 12, True, .9); person(b, x + 104, y + 34, False, .9)
    elif i == 1:  # split: one folder per reviewer, overlap clip in both
        for r, (yy, f) in enumerate([(y + 4, True), (y + 26, False)]):
            person(b, x + 7, yy + 8, f, .85)
            mini_folder(b, x + 20, yy)
            b.append(T(x + 43, yy + 13, "A/" if f else "B/", "tc tink", "start", 'style="font-size:9px"'))
            for k in range(2 if f else 1):
                clip(b, x + 62 + k * 22, yy + 2, "", 18, 12)
            clip(b, x + 62 + (2 if f else 1) * 22, yy + 2, "AB", 18, 12)
    elif i == 2:  # verify: each reviewer sorts their own clips
        for r, (yy, f) in enumerate([(y + 4, True), (y + 26, False)]):
            person(b, x + 7, yy + 8, f, .85)
            b.append(arrow(x + 18, yy + 8, x + 30, yy + 8))
            marks = ["fs3 st3", "fs3 st3", "fsbad stbad"] if f else ["fs3 st3", "fsbad stbad"]
            for k, m in enumerate(marks):
                b.append(R(x + 36 + k * 20, yy + 1, 16, 13, m + " w15", 2))
            b.append(T(x + 36 + len(marks) * 20 + 4, yy + 12, "✓ ✗", "ts", "start", 'style="font-size:10px"'))
    elif i == 3:  # read: one table per reviewer
        for r, (xx, f) in enumerate([(x + 4, True), (x + 64, False)]):
            person(b, xx + 8, y + 10, f, .8)
            b.append(R(xx + 18, y + 2, 38, 40, "fsurf sline", 3))
            b.append(R(xx + 18, y + 2, 38, 8, "fs1" if f else "fline", 2))
            for k in range(4):
                b.append(L(xx + 22, y + 16 + k * 7, xx + 40, y + 16 + k * 7, "sline"))
                b.append(C(xx + 48, y + 16 + k * 7, 2.4, "f3" if (k + r) % 3 else "fbad"))
    elif i == 4:  # agreement: 2x2 matrix of the overlap clips
        cx, cy, s = x + 30, y + 6, 17
        b.append(T(cx + s, y + 2, "B", "tny tm", "middle")); b.append(T(cx - 8, cy + s + 3, "A", "tny tm", "middle"))
        for rr in range(2):
            for cc in range(2):
                cls = "fs3 st3" if rr == cc else "fsbad stbad"
                b.append(R(cx + cc * s, cy + rr * s, s - 2, s - 2, cls + " w15", 2))
                b.append(T(cx + cc * s + (s - 2) / 2, cy + rr * s + 11, ["11", "1", "2", "6"][rr * 2 + cc], "tny tink", "middle"))
        b.append(T(x + 76, y + 24, "κ = 0.79", "tc tink", "start", 'style="font-size:10px"'))
    elif i == 5:  # consensus: one verdict per clip, conflicts flagged
        rows = [("fs3 st3", "positive"), ("fsbad stbad", "negative"), ("fline sline", "disagreement")]
        for k, (cls, lab) in enumerate(rows):
            yy = y + 4 + k * 13
            clip(b, x + 4, yy, "", 18, 10)
            b.append(R(x + 28, yy + 1, 8, 8, cls + " w15", 2))
            b.append(T(x + 40, yy + 9, lab, "ts" + (" fbadt" if k == 2 else ""), "start", 'style="font-size:9.6px"'))

def s1rev_v9():
    b = []
    Wd = 900
    note(b, 0, 14, "optional, when more than one person verifies the clips: replaces steps 4–5 for the clips of the manifest (step 3)")
    # reviewer key
    person(b, 640, 10, True, .7); b.append(T(650, 14, "reviewer A", "ts", "start", 'style="font-size:9.6px"'))
    person(b, 720, 10, False, .7); b.append(T(730, 14, "reviewer B", "ts", "start", 'style="font-size:9.6px"'))
    clip(b, 800, 4, "AB", 18, 11); b.append(T(824, 14, "both (overlap)", "ts", "start", 'style="font-size:9.6px"'))
    steps = [("4.1", "Assign", ["assign_reviewers()"], "manifest + reviewer,", "second_reviewer",
              ["clips split among reviewers,", "balanced by species; a share", "(overlap = 0.1) gets a second"]),
             ("4.2", "Split folders", ["split_by_reviewer()"], "<reviewer>/<species>/", "",
              ["copies each reviewer’s clips", "to their own folder; overlap", "clips go to both"]),
             ("4.3", "Verify", ["BirdNET GUI or", "run_app()"], "Positive/ · Negative/", "",
              ["each reviewer verifies", "their own folder"]),
             ("5.1", "Read verdicts", ["classify_review()"], "one table per", "reviewer",
              ["on each reviewer’s folder", "(or app_verdicts())"]),
             ("5.2", "Agreement", ["reviewer_agreement()"], "agreement, kappa", "per species",
              ["clips seen twice: Cohen’s κ", "(2 reviewers) or Fleiss’ κ"]),
             ("5.3", "Consensus", ["consensus_verdicts()"], "one verdict per clip", "→ step 6",
              ["conflicts → “disagreement”:", "left out of precision and", "calibration; re-review them"])]
    bw, gap, y0, V = 138, 14.4, 28, 50
    for i, (n, title, fns, o1, o2, desc) in enumerate(steps):
        x = i * (bw + gap)
        b.append(R(x, y0, bw, V + 140, "fsurf sline dash", 8))
        pill1(b, x + 8, y0 + 16, n, True); b.append(T(x + 42, y0 + 20, title, "ts tink"))
        vis(b, i, x + 8, y0 + 30)
        for k, f in enumerate(fns):
            b.append(T(x + 10, y0 + V + 42 + k * 14, f, "tc f1t", "start", 'style="font-size:9.2px"'))
        yd = y0 + V + 42 + len(fns) * 14 + 4
        for k, dd in enumerate(desc):
            b.append(T(x + 10, yd + k * 13, dd, "ts", "start", 'style="font-size:9.6px" opacity=".85"'))
        yc = y0 + V + 108
        b.append(P(f"M{x+10} {yc} h9 l4 4 v14 h-13 Z", "fsurf st1 w15"))
        b.append(T(x + 28, yc + 10, o1, "tc tm", "start", 'style="font-size:8px"'))
        if o2: b.append(T(x + 28, yc + 21, o2, "tc tm", "start", 'style="font-size:8px"'))
        if i < len(steps) - 1:
            b.append(arrow(x + bw + 2, y0 + 52, x + bw + gap - 2, y0 + 52))
    return svg(Wd, y0 + V + 146, "".join(b), "Several reviewers: assign, split, verify, read, agreement, consensus")

def s1pv_v9():
    b = []
    Wd = 900
    note(b, 0, 14, "input: validation_by_clip.csv from step 5 (classify_review() or app_verdicts()), one verdict per clip")
    steps = [("6.1", True, "Stack tables", ["read_validation_tables()"], "one table",
              ["optional: several runs,", "sites or review rounds;", "keeps every verdict"]),
             ("6.2", False, "Precision by bin", ["precision_by_bin()", "plot_precision()"], "precision_by_bin.csv / .png",
              ["share of positives per", "species × score bin,", "weighted by design"]),
             ("6.3", False, "Empirical thresholds", ["suggest_thresholds()"], "suggested_thresholds.csv",
              ["lowest cut reaching", "target_precision with", "n_eff ≥ min_n"]),
             ("6.4", False, "Presence by night", ["nightly_presence()"], "nightly_presence.csv",
              ["night confirmed when a", "clip is positive; no", "threshold, no model"]),
             ("6.5", False, "Retraining clips", ["retraining_clips()"], "retraining_clips.csv",
              ["confirmed positives;", "* next: Stage 1 ·", "Retraining"])]
    bw, gap, y0 = 164, 20, 30
    for i, (n, opt, title, fns, out_, desc) in enumerate(steps):
        x = i * (bw + gap)
        b.append(R(x, y0, bw, 134, "fsurf " + ("sline dash" if opt else "sline"), 8))
        pill1(b, x + 8, y0 + 16, n, opt); b.append(T(x + 42, y0 + 20, title, "ts tink"))
        for k, f in enumerate(fns):
            b.append(T(x + 10, y0 + 42 + k * 14, f, "tc f1t", "start", 'style="font-size:9.4px"'))
        yd = y0 + 42 + len(fns) * 14 + 4
        for k, dd in enumerate(desc):
            b.append(T(x + 10, yd + k * 13, dd, "ts", "start", 'style="font-size:9.8px" opacity=".85"'))
        yc = y0 + 106
        b.append(P(f"M{x+10} {yc} h9 l4 4 v14 h-13 Z", "fsurf st1 w15"))
        b.append(T(x + 28, yc + 13, out_, "tc tm", "start", 'style="font-size:8.2px"'))
        if i < len(steps) - 1:
            b.append(arrow(x + bw + 3, y0 + 67, x + bw + gap - 3, y0 + 67))
    return svg(Wd, y0 + 140, "".join(b), "Summary step as a sequence of functions")

out["s1rev"] = s1rev_v9()
out["s1pv"] = s1pv_v9()
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok v9")

# ---------------- step 7 without "next", with a small drawing in each branch
import math
from gen_panels import badge
def s1diag_v9():
    b = []
    Wd = 900
    b.append(badge(8, 14, 7)); b.append(T(22, 18, "What did the verification give?", "tb"))
    note(b, 250, 18, "two questions, one per route; answer one, or both to compare them")
    b.append(P("M450 30 V46 M230 46 H670 M230 46 V60 M670 46 V60", "nofill sline"))
    b.append(arrow(230, 52, 230, 62, "ar1")); b.append(arrow(670, 52, 670, 62, "ar2"))
    BH = 252
    def branch(x, color, soft, tag, title, q, how, gives):
        b.append(R(x, 64, 420, BH, f"{soft} st{color}", 10))
        b.append(R(x + 12, 76, 34, 20, f"f{color}", 10)); b.append(T(x + 29, 90, tag, "tny finv", "middle"))
        b.append(T(x + 56, 91, title, f"tb f{color}t"))
        for k, ql in enumerate(q):
            b.append(T(x + 14, 118 + k * 17, ql, "tb tink", "start", 'style="font-size:14px"'))
        y = 118 + len(q) * 17 + 10
        for lab, lines in (("how", how), ("gives", gives)):
            b.append(T(x + 14, y, lab, f"tc f{color}t"))
            for k, ln in enumerate(lines):
                b.append(T(x + 62, y + k * 13, ln, "ts", "start", NOTE))
            y += 13 * len(lines) + 6
    branch(10, "1", "fs1", "7A", "Empirical threshold",
           ["“What is the threshold for 90% of", "precision in my dataset?”"],
           ["review_support() (it calls suggest_thresholds())"],
           ["a threshold per site × species, and a diagnosis:", "reached · review more · exhausted · unreliable · not reviewed"])
    branch(470, "2", "fs2", "7B", "Model-based threshold",
           ["“What is the threshold for a 95%", "probability of true positive?”"],
           ["calibrate() (Stage 2 model, checked) → calibrated_thresholds()"],
           ["a threshold per site × species from the fitted curve, and", "calibration_quality(): ok · poor · insufficient"])
    # shared plot frame
    YT, YB = 222, 290
    def frame(bx, ylab):
        x0, x1 = bx + 40, bx + 400
        b.append(R(bx + 10, 206, 400, 102, "fsurf", 6))
        b.append(L(x0, YT - 4, x0, YB, "sgrid")); b.append(L(x0, YB, x1, YB, "sgrid"))
        b.append(T(x0 - 4, YT + 3, "1", "tny tm", "end")); b.append(T(x0 - 4, YB + 3, "0", "tny tm", "end"))
        b.append(T(bx + 22, (YT + YB) / 2, ylab, "tny tm", "middle", f'transform="rotate(-90 {bx+22} {(YT+YB)/2})"'))
        b.append(T(x1, YB + 12, "score →", "tny tm", "end"))
        sx = lambda s: x0 + (s - 0.1) / 0.9 * (x1 - x0)
        py = lambda p: YB - p * (YB - YT)
        return sx, py
    SM = 'style="font-size:9.5px"'
    # 7A: precision of the reviewed clips at or above each candidate cut
    sx, py = frame(10, "precision")
    cuts = [0.1 + i * 0.85 / 80 for i in range(81)]
    prec = lambda c: min(0.99, 0.5 + 0.48 * (1 - math.exp(-3 * (c - 0.1) / 0.85)) + 0.02 * math.sin(c * 30))
    few = 0.87
    pts = [(c, prec(c)) for c in cuts]
    b.append(R(sx(few), YT - 4, sx(0.95) - sx(few), YB - YT + 4, "fline", 0, 'opacity=".6"'))
    b.append(T(sx(0.91), YB - 20, "n_eff", "tny tm", "middle", SM)); b.append(T(sx(0.91), YB - 8, "< min_n", "tny tm", "middle", SM))
    b.append(P("M" + " L".join(f"{sx(c):.1f} {py(p):.1f}" for c, p in pts if c <= few), "nofill st1 w2"))
    b.append(P("M" + " L".join(f"{sx(c):.1f} {py(p):.1f}" for c, p in pts if c >= few), "nofill st1 w15 dash"))
    b.append(L(sx(0.1), py(0.9), sx(0.95), py(0.9), "sline dash"))
    b.append(T(sx(0.1) + 4, py(0.9) - 3, "target_precision 0.90", "tny tm", "start", SM))
    tc = next(c for c, p in pts if p >= 0.9)
    b.append(L(sx(tc), YT - 4, sx(tc), YB, "st1 w15")); b.append(C(sx(tc), py(prec(tc)), 3, "f1"))
    b.append(T(sx(tc) + 4, YB - 8, "first cut that passes", "tny f1t", "start", SM))
    b.append(T(sx(0.1) + 4, YB - 8, "precision of reviewed clips ≥ each cut", "tny tm", "start", SM))
    # 7B: reviewed clips (0/1) and the fitted curve
    sx, py = frame(470, "P(tp)")
    s0, k = 0.55, 12
    f = lambda s: 1 / (1 + math.exp(-k * (s - s0)))
    clips = [(0.15, 0), (0.2, 0), (0.27, 0), (0.33, 0), (0.38, 1), (0.42, 0), (0.47, 0), (0.5, 1), (0.53, 0), (0.57, 1),
             (0.6, 1), (0.64, 0), (0.67, 1), (0.71, 1), (0.75, 1), (0.79, 1), (0.83, 1), (0.87, 1), (0.9, 1), (0.94, 1), (0.98, 1)]
    for i, (s, v) in enumerate(clips):
        b.append(C(sx(s), py(v) + (-4 if v else 4), 2.6, "f3" if v else "fbad", 'opacity=".8"'))
    ss = [0.1 + i * 0.9 / 100 for i in range(101)]
    b.append(P("M" + " L".join(f"{sx(s):.1f} {py(f(s)):.1f}" for s in ss), "nofill st2 w2"))
    b.append(L(sx(0.1), py(0.95), sx(1.0), py(0.95), "sline dash"))
    b.append(T(sx(0.1) + 4, py(0.95) + 11, "p_min 0.95", "tny tm", "start", SM))
    tb = s0 + math.log(19) / k
    b.append(L(sx(tb), py(0.95), sx(tb), YB, "st2 w15")); b.append(C(sx(tb), py(0.95), 3, "f2"))
    b.append(T(sx(tb) - 4, YB - 8, "where the curve crosses 0.95", "tny f2t", "end", SM))
    b.append(T(sx(0.1) + 4, YB - 26, "reviewed clips: true", "tny tm", "start", SM)); b.append(C(sx(0.1) + 94, YB - 29.5, 2.6, "f3"))
    b.append(T(sx(0.1) + 102, YB - 26, "/ false", "tny tm", "start", SM)); b.append(C(sx(0.1) + 133, YB - 29.5, 2.6, "fbad"))
    b.append(L(0, 64 + BH + 16, Wd, 64 + BH + 16, "sgrid"))
    note(b, 0, 64 + BH + 34, "compare 7A and 7B: agreement supports the model · the workflow of each is in the figure “Stage 1 · Diagnostic (7A / 7B)”")
    return svg(Wd, 64 + BH + 42, "".join(b), "Diagnostic step: 7A precision of reviewed clips per cut, 7B fitted probability curve")

out["s1diag"] = s1diag_v9()
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok diag v9")
