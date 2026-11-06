"""v8: row A = empirical threshold (step 7) | its diagnosis (step 8); row B = model-based threshold (7.1–7.2) | its check (step 8)."""
import json, re
from gen_v7 import out, pill
from gen_v5 import emphasise_optional
from gen_panels import T, R, C, L, P, svg, W, badge, arrow

NOTE = 'font-size="10.5" opacity=".85"'
def note(b, x, y, s): b.append(T(x, y, s, "ts", "start", NOTE))
MONO = 'style="font-size:8.4px"'

# ---------------- A · step 7: review_support() with suggest_thresholds() inside, and its output
def a_threshold():
    b = []
    b.append(badge(8, 12, 7)); b.append(T(22, 16, "review_support()", "tc f1t", "start", 'font-size="12"'))
    note(b, 140, 16, "target_precision · min_n · conf_high · min_precision")
    note(b, 140, 29, "defaults 0.90 · 15 · 0.7 · 0.5")
    b.append(R(0, 44, 440, 152, "fsurf sline", 6))
    b.append(T(10, 62, "inside: suggest_thresholds()", "tc f1t"))
    note(b, 10, 76, "precision of the reviewed clips at or above each cut, weighted by design;")
    note(b, 10, 89, "the threshold is the lowest cut that reaches the target with ≥ min_n clips")
    x0, x1, y0, y1 = 44, 420, 180, 104
    X = lambda c: x0 + (c - .1) / .9 * (x1 - x0); Y = lambda p: y0 - p * (y0 - y1)
    for p in (0, .5, 1):
        b.append(L(x0, Y(p), x1, Y(p), "sgrid")); b.append(T(x0 - 4, Y(p) + 3, f"{p:g}", "tc", "end", MONO))
    cum = [.58, .62, .67, .72, .78, .84, .91, .94, .97]
    pts = [(X(.1 + i * .1), Y(p)) for i, p in enumerate(cum)]
    b.append(P("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts), "nofill st1 w2"))
    for x, y in pts: b.append(C(x, y, 2.4, "f1"))
    b.append(L(x0, Y(.9), x1, Y(.9), "stink dash")); b.append(T(x0 + 3, Y(.9) - 4, "target 0.90", "tc tink", "start", MONO))
    b.append(L(X(.7), Y(.9), X(.7), Y(0), "st1 w15")); b.append(T(X(.7) + 4, Y(.25), "threshold 0.70", "tc f1t", "start", MONO))
    b.append(T(x1, y0 + 12, "confidence score →", "tc", "end", MONO))
    b.append(arrow(220, 198, 220, 220, "ar1"))
    b.append(T(0, 236, "output (printed in R):", "ts tink"))
    b.append(R(0, 244, 440, 120, "fs1", 6))
    b.append(T(8, 260, "# A tibble: 16 × 11", "tc tm", "start", MONO))
    cols = [("site", 8), ("species_folder", 34), ("n_high", 116), ("prec_high", 154),
            ("unreviewed_high", 206), ("threshold", 292), ("diagnosis", 346)]
    for name, x in cols: b.append(T(x, 276, name, "tc tink", "start", MONO))
    rows = [("ARA", "boa_ran", "24", "0.95", "3", "0.70", "reached", "f3t"),
            ("ARA", "den_nan", "18", "0.83", "21", "NA", "review more", "f1t"),
            ("BAI", "sci_nas", "15", "0.80", "2", "NA", "exhausted", "tm"),
            ("ARA", "pse_pla", "20", "0.30", "35", "NA", "unreliable", "fbadt"),
            ("NHE", "sci_nas", "0", "NA", "8", "NA", "not reviewed", "tm")]
    for r, row in enumerate(rows):
        y = 292 + r * 13
        for k, (name, x) in enumerate(cols):
            v = row[k]
            cls = row[7] if name == "diagnosis" else ("f1t" if name == "threshold" and v != "NA" else "tc")
            b.append(T(x, y, v, "tc " + cls, "start", MONO))
    b.append(T(8, 358, "# … 11 more rows; also n_reviewed, n_fp, n_high_all", "tc tm", "start", MONO))
    note(b, 0, 384, "threshold is filled only where diagnosis = reached; values are illustrative")
    return svg(W, 392, "".join(b), "review_support(): empirical threshold and diagnosis")

# ---------------- A · step 8: act on the diagnosis (rules + next steps + enough data)
def a_diagnosis():
    b = []
    b.append(badge(8, 12, 8)); b.append(T(22, 16, "Act on the diagnosis", "tb"))
    note(b, 168, 16, "the diagnosis column of review_support()")
    rows = [("f3", "finv", "✓", "reached", "threshold found",
             ["threshold set: check the data needs below,", "then continue"]),
            ("f1", "finv", "+", "review more", "high-score clips left, mid precision",
             ["new random_detections round for the cell", "(same threshold, new seed)  ↺ step 2"]),
            ("fmuted", "finv", "–", "exhausted *", "< min_n high-score left",
             ["keep the clips; rely on the pooled model (B) or flag", "the cell; * if the target is far off, see Retraining"]),
            ("fbad", "finv", "!", "unreliable *", "low precision at high scores",
             ["retrain the classifier, then a new round  ↺ step 2", "* see Stage 1 · Retraining"]),
            ("fsurf sline dash", "tm", "?", "not reviewed", "no reviewed clip yet",
             ["draw clips for this cell  ↺ step 2", ""])]
    for i, (cls, tcls, sym, lab, rule, nxt) in enumerate(rows):
        y = 32 + i * 50
        b.append(R(0, y, 116, 24, cls, 5))
        b.append(T(10, y + 16, sym, "tb " + tcls)); b.append(T(26, y + 16, lab, "ts " + tcls))
        b.append(T(0, y + 37, rule, "ts", "start", 'style="font-size:9.4px" opacity=".85"'))
        b.append(arrow(120, y + 12, 136, y + 12))
        for k, n in enumerate(nxt):
            if n: note(b, 142, y + 10 + k * 13, n)
    b.append(T(0, 290, "* retraining may help: see Stage 1 · Retraining", "ts fbadt", "start", 'style="font-size:10px"'))
    # enough data gate
    b.append(R(0, 302, 440, 114, "fs1 st1", 8))
    b.append(T(10, 320, "Enough data to continue?", "ts tink"))
    checks = ["☐ threshold: ≥ min_n clips above the cut", "☐ curve (Stage 2): quality ok, effort plateaus",
              "☐ retraining: ≥ 100 positives per class", "☐ false positives: enough confirmed occasions"]
    for k, c in enumerate(checks):
        note(b, 10, 338 + k * 15, c)
    b.append(T(10, 406, "all met → Stage 2 · Calibration, or the occupancy export", "ts f1t"))
    return svg(W, 424, "".join(b), "Next step for each diagnosis, and when there is enough data")

# ---------------- B · step 8: check the calibration (calibration_quality), reusing the stage 2 table
def b_check():
    b = []
    b.append(badge(8, 12, 8, color="2")); b.append(T(22, 16, "Check the calibration", "tb"))
    note(b, 172, 16, "calibration_quality.csv, written by calibrate() (7.1)")
    inner = re.sub(r"^<svg[^>]*>|</svg>$", "", out["s2q"])
    b.append(f'<g transform="translate(0,34) scale(0.98)">{inner}</g>')
    nxt = [("f3t", "ok", "use the model-based threshold (7.2) for the species"),
           ("fbadt", "poor *", "add a covariate or use A; * retrain (see Stage 1 · Retraining)"),
           ("tm", "insufficient", "too few clips: review more (step 2); see calibration_effort()")]
    for k, (cls, lab, txt) in enumerate(nxt):
        y = 300 + k * 16
        b.append(T(0, y, lab, "ts " + cls)); b.append(T(72, y, "→ " + txt, "ts", "start", NOTE))
    note(b, 0, 360, "B gives no review_support() diagnosis; later, cell_status() (stage 3) labels")
    note(b, 0, 373, "each site × species cell reliable, probably absent or unreliable")
    return svg(W, 392, "".join(b), "Check of the model-based route: calibration quality per species")

out["s1c"] = a_threshold()
out["s1e2"] = a_diagnosis()
out["s1bq"] = b_check()
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok v8")

# ---------------- step 6 as a sequence (6.1–6.5), post_validation() as the one-call shortcut
def pill1(b, x, y, txt, optional=False):
    if optional:
        b.append(R(x, y - 9, 28, 18, "fsurf st1 w15", 9)); b.append(T(x + 14, y + 4, txt, "tny f1t", "middle"))
    else:
        b.append(R(x, y - 9, 28, 18, "f1", 9)); b.append(T(x + 14, y + 4, txt, "tny finv", "middle"))

def s1pv_seq():
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
        b.append(R(x, y0, bw, 168, "fsurf " + ("sline dash" if opt else "sline"), 8))
        pill1(b, x + 8, y0 + 16, n, opt); b.append(T(x + 42, y0 + 20, title, "ts tink"))
        for k, f in enumerate(fns):
            b.append(T(x + 10, y0 + 42 + k * 14, f, "tc f1t", "start", 'style="font-size:9.4px"'))
        yd = y0 + 42 + len(fns) * 14 + 4
        for k, dd in enumerate(desc):
            b.append(T(x + 10, yd + k * 13, dd, "ts", "start", 'style="font-size:9.8px" opacity=".85"'))
        # output file chip
        b.append(P(f"M{x+10} {y0+136} h9 l4 4 v14 h-13 Z", "fsurf st1 w15"))
        b.append(T(x + 28, y0 + 150, out_, "tc tm", "start", 'style="font-size:8.2px"'))
        if i < len(steps) - 1:
            b.append(arrow(x + bw + 3, y0 + 84, x + bw + gap - 3, y0 + 84))
    b.append(L(0, 214, Wd, 214, "sgrid"))
    b.append(R(0, 222, Wd, 26, "fs1", 6))
    b.append(T(10, 239, "post_validation()", "tc f1t", "start", 'style="font-size:10.5px"'))
    note(b, 128, 239, "runs step 5 and 6.2–6.5 in one call and writes all these files; 6.3 is what review_support() reports in step 7")
    return svg(Wd, 254, "".join(b), "Summary step as a sequence of functions")

out["s1pv"] = s1pv_seq()
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok v8 seq")

# ---------------- step 7 in stage 1: the two diagnostic questions (7A / 7B)
def s1diag():
    b = []
    Wd = 900
    b.append(badge(8, 14, 7)); b.append(T(22, 18, "What did the verification give?", "tb"))
    note(b, 250, 18, "two questions, one per route; answer one, or both to compare them")
    # fork
    b.append(P("M450 30 V46 M230 46 H670 M230 46 V60 M670 46 V60", "nofill sline"))
    b.append(arrow(230, 52, 230, 62, "ar1")); b.append(arrow(670, 52, 670, 62, "ar2"))
    def branch(x, color, soft, tag, title, q, how, gives, nxt):
        b.append(R(x, 64, 420, 196, f"{soft} st{color}", 10))
        b.append(R(x + 12, 76, 34, 20, f"f{color}", 10)); b.append(T(x + 29, 90, tag, "tny finv", "middle"))
        b.append(T(x + 56, 91, title, f"tb f{color}t"))
        for k, ql in enumerate(q):
            b.append(T(x + 14, 118 + k * 17, ql, "tb tink", "start", 'style="font-size:14px"'))
        y = 118 + len(q) * 17 + 10
        for lab, lines in (("how", how), ("gives", gives), ("next", nxt)):
            b.append(T(x + 14, y, lab, f"tc f{color}t"))
            for k, ln in enumerate(lines):
                b.append(T(x + 62, y + k * 13, ln, "ts", "start", NOTE))
            y += 13 * len(lines) + 6
    branch(10, "1", "fs1", "7A", "Empirical threshold",
           ["“What is the threshold for 90% of", "precision in my dataset?”"],
           ["review_support() (it calls suggest_thresholds())"],
           ["a threshold per site × species, and a diagnosis:", "reached · review more · exhausted · unreliable · not reviewed"],
           ["act on the diagnosis until there is enough data"])
    branch(470, "2", "fs2", "7B", "Model-based threshold",
           ["“What is the threshold for a 95%", "probability of true positive?”"],
           ["calibrate() (Stage 2 model, checked) → calibrated_thresholds()"],
           ["a threshold per site × species from the fitted curve, and", "calibration_quality(): ok · poor · insufficient"],
           ["use the threshold for species marked ok"])
    b.append(L(0, 276, Wd, 276, "sgrid"))
    note(b, 0, 294, "compare 7A and 7B: agreement supports the model · the workflow of each is in the figure “Stage 1 · Diagnostic (7A / 7B)”")
    return svg(Wd, 302, "".join(b), "Diagnostic step: two questions, 7A empirical and 7B model-based")

out["s1diag"] = s1diag()
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok diag")

# ---------------- several reviewers: optional sequence inside the review step
def s1rev():
    b = []
    Wd = 900
    note(b, 0, 14, "optional, when more than one person verifies the clips: replaces steps 4–5 for the clips of the manifest (step 3)")
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
    bw, gap, y0 = 138, 14.4, 28
    for i, (n, title, fns, o1, o2, desc) in enumerate(steps):
        x = i * (bw + gap)
        b.append(R(x, y0, bw, 172, "fsurf sline dash", 8))
        pill1(b, x + 8, y0 + 16, n, True); b.append(T(x + 42, y0 + 20, title, "ts tink"))
        for k, f in enumerate(fns):
            b.append(T(x + 10, y0 + 42 + k * 14, f, "tc f1t", "start", 'style="font-size:9.2px"'))
        yd = y0 + 42 + len(fns) * 14 + 4
        for k, dd in enumerate(desc):
            b.append(T(x + 10, yd + k * 13, dd, "ts", "start", 'style="font-size:9.6px" opacity=".85"'))
        b.append(P(f"M{x+10} {y0+136} h9 l4 4 v14 h-13 Z", "fsurf st1 w15"))
        b.append(T(x + 28, y0 + 146, o1, "tc tm", "start", 'style="font-size:8px"'))
        if o2: b.append(T(x + 28, y0 + 157, o2, "tc tm", "start", 'style="font-size:8px"'))
        if i < len(steps) - 1:
            b.append(arrow(x + bw + 2, y0 + 84, x + bw + gap - 2, y0 + 84))
    return svg(Wd, 206, "".join(b), "Several reviewers: assign, split, verify, read, agreement, consensus")

out["s1rev"] = s1rev()
# point the review-step note to the new row
out["s1b"] = out["s1b"].replace("optional, several reviewers:", "several reviewers (see below):")
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok rev")
