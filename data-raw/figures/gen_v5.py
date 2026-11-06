"""v5: stage 1 Selection step panel with in-figure descriptions."""
import json
from gen_v4 import out
from gen_panels import T, R, C, L, P, svg, W, badge, recs, arrow

def note(b, x, y, txt):
    b.append(T(x, y, txt, "ts", "start", 'font-size="10.5" opacity=".85"'))

def warn(b, x, y, color="1"):
    b.append(C(x, y, 7, f"fsurf st{color} w15")); b.append(T(x, y + 3.5, "!", f"tny f{color}t", "middle"))

def s1a():
    b = []
    # step 1
    b.append(badge(8, 12, 1)); b.append(T(22, 16, "Read classifier outputs", "tb"))
    b.append(T(200, 16, "read_selection_tables()", "tc f1t"))
    note(b, 22, 31, "stacks the BirdNET selection tables: every prediction with its score")
    # step 2
    b.append(badge(8, 54, 2)); b.append(T(22, 58, "Select clips", "tb"))
    b.append(T(200, 58, "select_clips(sampling_mode = …)", "tc f1t"))
    note(b, 22, 73, "one of three designs; the same night of 12 hourly recordings under each")
    rows = [('"top"', ["highest score", "per recording"]),
            ('"random_detections"', ["score ≥ threshold;", "all detections kept"]),
            ('"random_recordings"', ["any, incl. empty (∅);", "expert check"])]
    bx0, bw, gap, bh = 128, 22, 3.6, 42
    drawn_rd = {2, 6, 9}; drawn_rr = {1, 4, 8}
    for r, (name, sub) in enumerate(rows):
        y0 = 86 + r * 60
        b.append(T(0, y0 + 12, name, "tc f1t", "start", 'font-size="9.5"'))
        for k, s in enumerate(sub): note(b, 0, y0 + 25 + k * 12, s)
        for i, sc in enumerate(recs):
            x = bx0 + i * (bw + gap)
            cls = "fs1 st1" if (r == 1 and i in drawn_rd) or (r == 2 and i in drawn_rr) else "fsurf sline"
            b.append(R(x, y0, bw, bh, cls, 3))
            top_i = max(range(len(sc)), key=lambda k: sc[k]) if sc else None
            for k, s in enumerate(sc):
                cy = y0 + bh - 3 - s * (bh - 6)
                pick = ((r == 0 and k == top_i) or (r == 1 and i in drawn_rd and s >= .5) or (r == 2 and i in drawn_rr))
                b.append(C(x + bw / 2 + (k - (len(sc) - 1) / 2) * 4, cy, 2.6 if pick else 2,
                           "f1" if pick else "fmuted", "" if pick else 'opacity=".45"'))
            if r == 2 and i in drawn_rr and not sc:
                b.append(T(x + bw / 2, y0 + bh / 2 + 4, "∅", "tc f1t", "middle"))
        ty = y0 + bh - 3 - .5 * (bh - 6)
        b.append(L(bx0 - 3, ty, bx0 + 12 * (bw + gap), ty, "sline dash"))
    for i in range(0, 12, 2):
        x = bx0 + i * (bw + gap) + bw / 2
        b.append(T(x, 280, f"{(18 + i) % 24:02d}h", "tc", "middle"))
    # ! list_recordings, needed by random_recordings
    b.append(R(0, 292, 140, 22, "fs3 st3", 5))
    warn(b, 12, 303, "3"); b.append(T(24, 307, "list_recordings()", "tc f3t"))
    b.append(arrow(60, 291, 60, 272, "nofill st3 w15"))
    note(b, 150, 301, "needed by random_recordings: lists every")
    note(b, 150, 314, "recording, including those without predictions")
    # ! optional covariate_bins
    b.append(L(0, 326, 440, 326, "sgrid"))
    warn(b, 8, 341); b.append(T(20, 345, "optional", "ts tink")); b.append(T(76, 345, "covariate_bins()", "tc f1t"))
    note(b, 20, 359, "stratifies the random_detections draw along a gradient (e.g. temperature)")
    return svg(W, 368, "".join(b), "Selection step: read classifier outputs, then select clips with three designs")

out["s1a"] = s1a()

import re
def emphasise_optional(svgtxt):
    """bold-italic the function names inside grey notes that list optional functions"""
    def fix(m):
        body = m.group(2)
        if "optional" not in body and not re.search(r"reviewer_agreement|consensus_verdicts|plot_precision", body):
            return m.group(0)
        body = re.sub(r"(\w+\(\))", r'<tspan class="optfn">\1</tspan>', body)
        return m.group(1) + body + "</text>"
    return re.sub(r'(<text[^>]*opacity="\.85"[^>]*>)(.*?)</text>', fix, svgtxt)
out["s1b"] = emphasise_optional(out["s1b"])
out["s1c"] = emphasise_optional(out["s1c"])
json.dump(out, open("panels.json", "w"), ensure_ascii=False)
print("ok v5")
