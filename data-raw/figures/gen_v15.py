"""v15: Stage 3 · occupancy routes panel (threshold or draws)."""
import json, re
from gen_v14 import *
from gen_panels import T, R, C, L, P, svg, arrow
from gen_v8 import note, NOTE, MONO

def occ_routes():
    b = []; W = 440
    SM = 'style="font-size:9.6px"'
    def box(y, h, title, eng, lines):
        b.append(R(0, y, W, h, "fs4 st4", 8))
        b.append(T(12, y + 20, title, "ts f4t"))
        b.append(R(W - 12 - len(eng) * 6.2 - 12, y + 8, len(eng) * 6.2 + 12, 15, "f2", 7)); b.append(T(W - 12 - len(eng) * 6.2 - 6, y + 19, eng, "tny finv"))
        for k, (t, c) in enumerate(lines): b.append(T(12, y + 42 + k * 15, t, c, "start", MONO if c.startswith("tc") else SM))
    box(0, 118, "threshold route", "lme4 or brms", [
        ("score threshold: Stage 1 (A) or calibrated_thresholds() (B)", "ts tink"),
        ("export_occupancy_data() without fit", "tc tink"),
        ("crywolf: fp_read_sheepdog() → fp_aggregate(threshold = )", "tc tink"),
        ("→ fp_data() → fp_occu(): one fit", "tc tink")])
    box(130, 118, "draws route", "brms", [
        ("the calibration itself: one detection matrix per draw", "ts tink"),
        ("export_occupancy_data(fit = brms fit)", "tc tink"),
        ("crywolf: fp_draws_data(rule = \"sample\" or \"threshold\")", "tc tink"),
        ("→ fp_occu_mc(): one fit per draw, pooled", "tc tink")])
    b.append(T(0, 274, "both need", "ts tink"))
    for k, c in enumerate(["☐ known truth: random_detections at the same threshold", "   (observation confirmation) and/or random_recordings", "   (multiple methods)",
                           "☐ a calibration without a site effect, or local prevalence", "   is counted twice"]):
        note(b, 0, 292 + k * 14, c)
    note(b, 0, 372, "crywolf estimates p10 itself from the known truth: see the")
    note(b, 0, 386, "crywolf explainer for how it works and how the designs differ")
    return svg(W, 394, "".join(b), "Two routes from sheepdog to an occupancy model with false positives")

out["occ_routes"] = occ_routes()
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok v15")
