"""Stage 1 · Retraining figure (1x_stage1_retraining.html), in the numbered-step style of the other figures."""
import os, re
from gen_v14 import out            # runs the panel chain, keeps panels.json current
from gen_panels import T, R, C, L, P, svg, arrow
from gen_v8 import note, NOTE, MONO

d = os.path.dirname(os.path.abspath(__file__)) + '/'
stage1 = open(d + 'abstracts/1_stage1_validation.html').read()
head = re.sub(r'<title>.*?</title>', '<title>sheepdog Stage 1 Retraining</title>', stage1[:stage1.index('<body>')])
SM = 'style="font-size:10px"'

def pill(b, x, y, txt):
    b.append(R(x, y - 10, 24, 20, "f1", 10)); b.append(T(x + 12, y + 4, txt, "tny finv", "middle"))

# ---------------- when to retrain
def when():
    b = []
    for x, h in ((0, "route"), (70, "label"), (196, "retrain?"), (316, "why, and what to try first")):
        b.append(T(x, 16, h, "ts tink"))
    rows = [("A", "unreliable", "fbad", "finv", "yes", "fbadt", ["precision stays below min_precision even at high scores:", "more review only confirms it (Figure 2, A · step 2)"]),
            ("A", "exhausted", "fmuted", "finv", "consider", "f1t", ["nothing left to review and the target is far off:", "the classifier caps the precision"]),
            ("A", "review more", "f1", "finv", "not yet", "tm", ["review another round first (Figure 1 · step 2)"]),
            ("B", "poor", "fbad", "finv", "after the options", "f1t", ["first try more clips across the scores, a covariate or", "another model (Figure 4 · step 3); retrain if still poor"]),
            ("B", "insufficient", "fsurf sline dash", "tm", "not yet", "tm", ["too few true or false clips: review more"]),
            ("A or B", "one cause of FPs", "fsurf st1 w15", "tink", "yes", "fbadt", ["you listened to the false-positive clips (loop step 1) and", "most come from one confusing species or a recurring noise"])]
    for i, (rt, lab, cls, tcls, ans, acls, why) in enumerate(rows):
        y = 34 + i * 42
        b.append(L(0, y + 32, 900, y + 32, "sgrid"))
        b.append(T(0, y + 16, rt, "tc tink", "start", 'style="font-size:9.6px"'))
        b.append(R(70, y + 2, 112, 22, cls, 11)); b.append(T(126, y + 17, lab, "ts " + tcls, "middle"))
        b.append(T(196, y + 17, ans, "ts " + acls))
        for k, w in enumerate(why): note(b, 316, y + 11 + k * 14, w)
    note(b, 0, 300, "A = empirical route (review_support() label), B = model-based route (calibration_quality() status), as in Figures 2 and 4; FPs = false positives")
    return svg(900, 308, "".join(b), "When to retrain, by route and label")


from gen_panels import wave

def clip(b, x, y, cls="fsurf sline", w=20, h=13):
    b.append(R(x, y, w, h, cls, 2)); b.append(wave(x + 3, y + h / 2, w - 6, 3.2, 6, "wv1"))

def folder(b, x, y, cls="fs1 st1", w=18):
    b.append(P(f"M{x} {y+4} L{x} {y+15} L{x+w} {y+15} L{x+w} {y+2} L{x+9} {y+2} L{x+6} {y-2} L{x} {y-2} Z", cls))

def vis(b, i, x, y):
    """small drawing in the band y..y+46 of box i (box width 134)"""
    if i == 0:   # headphones over false-positive clips
        b.append(P(f"M{x+10} {y+22} Q{x+10} {y+2} {x+26} {y+2} Q{x+42} {y+2} {x+42} {y+22}", "nofill st1 w2"))
        b.append(R(x + 6, y + 18, 8, 14, "f1", 3)); b.append(R(x + 38, y + 18, 8, 14, "f1", 3))
        for k in range(3):
            clip(b, x + 56 + (k % 2) * 30, y + 2 + k * 14 - (k // 2) * 14 if k < 2 else y + 22, "fsbad stbad")
        b.append(T(x + 58, y + 46, "same confusion?", "tny fbadt"))
    elif i == 1:  # positive clips into a folder
        for k in range(3): clip(b, x + 4 + k * 24, y + 6, "fs3 st3")
        b.append(arrow(x + 78, y + 12, x + 92, y + 12, "ar1"))
        folder(b, x + 96, y + 4, "fs3 st3", 22)
        b.append(T(x + 4, y + 38, "confirmed positives", "tny f3t"))
    elif i == 2:  # train / val / test by night, Noise folder
        for k, (lab, cls) in enumerate([("train", "fs1 st1"), ("val", "fs2 st2"), ("test", "fsurf sline"), ("Noise", "fsbad stbad")]):
            xx = x + 2 + k * 30
            folder(b, xx, y + 6, cls, 20)
            b.append(T(xx + 10, y + 34, lab, "tny tm", "middle"))
        b.append(T(x + 2, y + 46, "nights never shared", "tny f1t"))
    elif i == 3:  # a training curve
        b.append(L(x + 4, y + 40, x + 120, y + 40, "sgrid")); b.append(L(x + 4, y + 4, x + 4, y + 40, "sgrid"))
        b.append(P(f"M{x+6} {y+8} Q{x+30} {y+32} {x+118} {y+36}", "nofill st1 w2"))
        b.append(P(f"M{x+6} {y+12} Q{x+34} {y+30} {x+118} {y+30}", "nofill st2 w15 dash"))
        b.append(T(x + 118, y + 26, "loss on val/", "tny f2t", "end"))
    elif i == 4:  # audio -> new selection table
        b.append(wave(x + 4, y + 18, 40, 8, 10, "wv1"))
        b.append(arrow(x + 50, y + 18, x + 66, y + 18, "ar1"))
        b.append(R(x + 70, y + 2, 52, 34, "fsurf sline", 3)); b.append(R(x + 70, y + 2, 52, 8, "fs1", 2))
        for k in range(3): b.append(L(x + 74, y + 16 + k * 7, x + 118, y + 16 + k * 7, "sline"))
        b.append(T(x + 4, y + 46, "new scores", "tny tm"))
    else:  # exclude training clips from the next draw
        for k in range(5):
            xx = x + 4 + k * 24
            clip(b, xx, y + 8, "fsurf sline")
            if k in (1, 3):
                b.append(L(xx - 2, y + 6, xx + 22, y + 23, "stbad w2")); b.append(L(xx - 2, y + 23, xx + 22, y + 6, "stbad w2"))
        b.append(T(x + 4, y + 40, "training clips never", "tny fbadt")); b.append(T(x + 4, y + 50, "drawn again", "tny fbadt"))

# ---------------- the loop
def loop():
    b = []
    steps = [("1", "Listen to the", "false positives", None, ["validation_by_clip.csv,", "verdict = negative: what", "the classifier confuses"]),
             ("2", "Collect", "the positives", "retraining_clips()", ["confirmed positive clips;", "post_validation() writes", "retraining_clips.csv"]),
             ("3", "Build the", "training set", "build_training_set()", ["test and val sets by night", "(split = \"night\"); negatives", "in one folder (\"Noise\")"]),
             ("4", "Train", "", "BirdNET-Analyzer", ["outside R; pass val/", "as --test_data"]),
             ("5", "Re-run", "", "the new classifier", ["on the audio → new", "selection tables"]),
             ("6", "Exclude the", "training clips", "exclude_training_clips()", ["or training_nights(),", "then a new round of", "validation"])]
    bw, gap, y0, V = 134, 19.2, 46, 58
    for i, (n, t1, t2, f, desc) in enumerate(steps):
        x = i * (bw + gap)
        b.append(R(x, y0, bw, 150 + V, "fsurf sline", 8))
        pill(b, x + 8, y0 + 18, n)
        b.append(T(x + 38, y0 + 16, t1, "ts tink")); b.append(T(x + 38, y0 + 30, t2, "ts tink"))
        vis(b, i, x + 4, y0 + 42)
        if f: b.append(T(x + 8, y0 + V + 56, f, "tc f1t", "start", 'style="font-size:%spx"' % ("8.2" if len(f) > 22 else "9.2")))
        for k, dd in enumerate(desc): b.append(T(x + 8, y0 + V + 78 + k * 14, dd, "ts", "start", 'style="font-size:9.8px" opacity=".85"'))
        if i < len(steps) - 1: b.append(arrow(x + bw + 3, y0 + 75, x + bw + gap - 3, y0 + 75))
    # bracket: what post_validation() already writes
    xb1, xb2 = 4, bw + gap + bw - 4
    b.append(P(f"M{xb1} {y0 - 8} V{y0 - 18} H{xb2} V{y0 - 8}", "nofill st1 w15"))
    b.append(T(xb1, y0 - 24, "post_validation() already writes both files (Figure 1 · step 6)", "tc f1t", "start", 'style="font-size:10px"'))
    # loop back
    xe = 5 * (bw + gap) + bw / 2
    y0 += 58
    b.append(P(f"M{xe} {y0 + 150} V{y0 + 182} H66 V{y0 + 156}", "nofill st1 w15 dash"))
    b.append(arrow(66, y0 + 162, 66, y0 + 154, "ar1"))
    b.append(T(450, y0 + 176, "back to Figure 1 · step 2: a new random_detections draw, review and the diagnosis again", "ts f1t", "middle"))
    return svg(900, y0 + 192, "".join(b), "The retraining loop in six steps")

# ---------------- checks
def reqs():
    b = []
    items = [("≥ 100 positive clips per class", "min_files in build_training_set() warns below it (BirdNET-Analyzer recommendation)"),
             ("negatives from your reviews", "the false positives teach the classifier what to reject; put them in one non-event folder"),
             ("split by night (or by site), not by clip", "clips of the same night are correlated; the checks of build_training_set() should all be 0"),
             ("keep training_set.csv", "with the new classifier: exclude_training_clips() needs it, so test clips are never training clips"),
             ("compare old and new", "the same random_detections design on nights neither classifier was trained on (training_nights())")]
    for k, (h, dsc) in enumerate(items):
        y = 18 + k * 34
        b.append(T(0, y, "☐  " + h, "ts tink")); note(b, 22, y + 15, dsc)
    return svg(900, 180, "".join(b), "Checks before and after retraining")

def fig(svgtxt, title, tag):
    return (f'<figure class="panel wide"><div class="phead"><span class="ttl">{title}</span><span class="ltr">{tag}</span></div>'
            f'<div>{svgtxt}</div></figure>')

body = f'''<body><div class="wrap">
<header><span class="eyebrow">sheepdog</span><h1>Stage 1 · Retraining</h1>
<p class="lede">When the classifier, not the amount of review, limits precision: retrain it with your verified clips, then validate the new classifier from Figure 1 · step 2.</p></header>
<section class="stage st1"><div class="panels">
{fig(when(), "When to retrain", "from the A and B labels")}
{fig(loop(), "The retraining loop", "steps 1–6")}
{fig(reqs(), "Before and after retraining", "checks")}
</div></section>
<p class="src">sheepdog (R package) · github.com/diogoprov/sheepdog · provetelab.org/sheepdog · BirdNET-Analyzer training runs outside R.</p>
</div></body></html>'''
os.makedirs(d + 'abstracts', exist_ok=True)
open(d + 'abstracts/1x_stage1_retraining.html', 'w').write(head + body)
print('ok retrain')
