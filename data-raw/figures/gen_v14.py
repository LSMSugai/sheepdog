"""v14: Stage 2 · Calibration as numbered steps: the three ways to a history, and what comes next."""
import json, math, re
from gen_v13 import *
from gen_panels import T, R, C, L, P, svg, arrow
from gen_v8 import note, NOTE, MONO

SM = 'style="font-size:9.6px"'

def tagl(b, x, y, txt, cls="f2"):
    b.append(R(x, y - 10, len(txt) * 6.2 + 12, 15, cls, 7)); b.append(T(x + 6, y + 1, txt, "tny finv"))

# ---------------- step 6 · three ways from P(tp) to a nightly history
def ways():
    b = []; W = 440
    rows = [("way 1", "rule = \"mean\"", "lme4 or brms", "kept if P(tp) ≥ p_min (0.95)", ["one history; the curve", "is treated as exact"]),
            ("way 2", "rule = \"probability\"", "brms", "kept if pr_reliable ≥ prob_min (0.9)", ["one cautious history: drops", "detections near the cut"]),
            ("way 3", "history_draws()", "brms", "kept if P(tp) ≥ p_min in each draw", ["one history per posterior draw", "→ matrices with intervals"])]
    H = 104
    for i, (w, fn, eng, rule, desc) in enumerate(rows):
        y = 18 + i * H
        b.append(T(0, y, w, "tc f2t")); b.append(T(44, y, fn, "tc tink", "start", MONO))
        tagl(b, 0, y + 22, eng)
        b.append(T(0, y + 44, rule, "ts tink", "start", SM))
        for k, d in enumerate(desc): note(b, 0, y + 60 + k * 13, d)
        x0, x1 = 250, 432
        X = lambda p: x0 + (p - .85) / .15 * (x1 - x0)
        yb = y + 62
        if i < 2:
            b.append(L(x0, yb, x1, yb, "sgrid"))
            b.append(L(X(.95), y + 4, X(.95), yb, "stink dash")); b.append(T(X(.95), yb + 12, "0.95", "tny tm", "middle"))
        if i == 0:
            b.append(L(X(.968), y + 22, X(.968), yb, "st2 w2")); b.append(C(X(.968), y + 22, 3.5, "f2"))
            b.append(T(X(.94) , y + 26, "mean P(tp)", "tny f2t", "end")); b.append(T(X(.94), y + 37, "0.968 → kept", "tny f2t", "end"))
        elif i == 1:
            pts = []
            for k in range(61):
                p = .85 + k * .15 / 60
                pts.append((X(p), yb - 44 * math.exp(-((p - .962) / .014) ** 2 / 2)))
            above = [(x, yy) for (x, yy) in pts if x >= X(.95)]
            b.append(P(f"M{above[0][0]:.1f} {yb} " + " ".join(f"L{x:.1f} {yy:.1f}" for x, yy in above) + f" L{above[-1][0]:.1f} {yb} Z", "fs2"))
            b.append(P("M" + " L".join(f"{x:.1f} {yy:.1f}" for x, yy in pts), "nofill st2 w15"))
            b.append(T(X(.94), y + 26, "pr_reliable =", "tny f2t", "end")); b.append(T(X(.94), y + 37, "shaded share (0.8)", "tny f2t", "end"))
        else:
            for k in range(3):
                for j in range(6):
                    on = [[1, 1, 0, 1, 1, 0], [1, 0, 0, 1, 1, 0], [1, 1, 0, 1, 0, 0]][k][j]
                    b.append(R(x0 + 6 + k * 62 + j * 8.5, y + 6, 6.5, 26, "f2" if on else "fline", 1))
                b.append(T(x0 + 6 + k * 62 + 24, y + 46, f"draw {k+1}", "tny tm", "middle"))
            b.append(T(x0 + 6, y + 62, "nights →", "tny tm"))
        if i < 2: b.append(L(0, y + H - 14, W, y + H - 14, "sgrid"))
    note(b, 0, 18 + 3 * H - 6, "in all three, a night counts when ≥ k detections count (k = 1, 2, 3)")
    return svg(W, 18 + 3 * H + 2, "".join(b), "Three ways from P(tp) to a nightly detection history")

# ---------------- step 8 · what comes next (wide)
def nxt():
    b = []; Wd = 900
    note(b, 0, 14, "species with calibration_quality() ok · the routes are compared in “Routes to detection histories and occupancy”")
    b.append(R(0, 28, 444, 236, "fs3 st3", 10))
    b.append(T(14, 50, "Community matrices (Stage 3)", "ts f3t"))
    steps = [("cell_status()", "each site × species cell: reliable, probably absent or unreliable"),
             ("suggest_core_species()", "keeps species with no unreliable cell"),
             ("community_matrices()", "from the way 1 or 2 history: frequency, counts, effort, trials"),
             ("community_matrices_draws()", "from the way 3 histories: mean and interval per cell"),
             ("→ vegan or gllvm", "ordination (PCoA, NMDS, RDA) or gllvm with trials")]
    for k, (f, d) in enumerate(steps):
        y = 76 + k * 36
        b.append(T(14, y, f, "tc tink", "start", MONO)); b.append(T(14, y + 13, d, "ts", "start", SM))
    x0 = 456
    b.append(R(x0, 28, 444, 236, "fs4 st4", 10))
    b.append(T(x0 + 14, 50, "Occupancy with false positives (crywolf)", "ts f4t"))
    b.append(T(x0 + 14, 74, "threshold", "tc f2t"))
    b.append(T(x0 + 90, 74, "calibrated_thresholds() (or threshold_lower)", "tc tink", "start", MONO))
    b.append(T(x0 + 90, 87, "→ export_occupancy_data() without fit", "tc tink", "start", MONO))
    b.append(T(x0 + 90, 100, "→ fp_aggregate(threshold = score)", "tc tink", "start", MONO))
    tagl(b, x0 + 344, 74, "lme4 or brms")
    b.append(T(x0 + 14, 128, "draws", "tc f2t"))
    b.append(T(x0 + 90, 128, "export_occupancy_data(fit = brms fit)", "tc tink", "start", MONO))
    b.append(T(x0 + 90, 141, "→ fp_draws_data(rule = \"sample\")", "tc tink", "start", MONO))
    b.append(T(x0 + 90, 154, "→ fp_occu_mc(): one fit per draw, pooled", "tc tink", "start", MONO))
    tagl(b, x0 + 344, 128, "brms")
    b.append(L(x0 + 14, 170, x0 + 430, 170, "sgrid"))
    for k, c in enumerate(["a random validation design at the same threshold", "(random_detections) and/or random_recordings",
                           "a calibration without a site effect, or local", "prevalence is counted twice"]):
        note(b, x0 + 14, 190 + k * 14, ("☐ " if k in (0, 2) else "   ") + c)
    return svg(Wd, 272, "".join(b), "After Stage 2: community matrices or occupancy")

out["s2ways"] = ways()
out["s2next"] = nxt()
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok v14")

# ---------------- step 3 with options for each status
def check_opts():
    b = []; W = 440
    inner = re.sub(r"^<svg[^>]*>|</svg>$", "", out["s2q"])
    b.append(f'<g transform="translate(0,0)">{inner}</g>')
    b.append(L(0, 252, W, 252, "sgrid"))
    b.append(T(0, 272, "what to do with each status", "ts tink"))
    note(b, 160, 272, "(limits are provisional: read the reason column)")
    rows = [("f3", "finv", "ok", ["go on to step 4"]),
            ("fbad", "finv", "poor *", ["• score says little (low AUC, no gain): more", "   random_detections clips across the scores", "   (top clips lower the AUC), or a covariate", "   (month, site) among the candidates",
                                       "• probabilities off (slope, intercept): another", "   model (species slope, single-species family)",
                                       "• still poor: leave it out of P(tp) analyses, or", "   use the empirical threshold (Figure 2, route A)"]),
            ("fsurf sline dash", "tm", "insufficient", ["fewer than min_class (10) true or false clips:", "review more ↺ Figure 1 · step 2;", "calibration_effort() says how many. Meanwhile its", "curve is borrowed from other species and unchecked"])]
    y = 288
    for cls, tcls, lab, nxt in rows:
        b.append(R(0, y, 86, 22, cls, 11)); b.append(T(43, y + 15, lab, "ts " + tcls, "middle", SM))
        b.append(arrow(90, y + 11, 104, y + 11))
        for k, n in enumerate(nxt): note(b, 119 if n.startswith("   ") else 110, y + 10 + k * 13, n.strip())
        y += max(13 * len(nxt) + 16, 34)
    b.append(T(0, y + 4, "* if nothing helps, see Stage 1 · Retraining", "ts fbadt", "start", 'style="font-size:10px"'))
    return svg(W, y + 12, "".join(b), "calibration_quality() and what to do with each status")

out["s2q_opts"] = check_opts()
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok v14 opts")
