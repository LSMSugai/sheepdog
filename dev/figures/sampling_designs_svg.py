"""Draws vignettes/figures/sampling-designs.svg, the design chooser that
opens vignette("sampling-designs"). Run from the package root:
python3 dev/figures/sampling_designs_svg.py
The medians in panel 2 come from the vignette (score_quantiles)."""
from xml.sax.saxutils import escape

W, H = 1320, 1600
SANS = "Helvetica Neue, Helvetica, Arial, sans-serif"
MONO = "SFMono-Regular, Menlo, Consolas, monospace"
INK, MUTED, RULE, PANEL = "#1d232b", "#5b6573", "#d5dae1", "#f4f6f8"
GREY_BAR, WARN_BG, WARN_INK = "#c9ced6", "#fdf3e6", "#7a4a12"
out = []


def t(x, y, s, size=13, fill=INK, weight="normal", font=SANS, anchor="start",
      style=""):
    out.append(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
               f'fill="{fill}" font-weight="{weight}" text-anchor="{anchor}"'
               f'{" font-style=" + chr(34) + style + chr(34) if style else ""}>'
               f'{escape(s)}</text>')


def wrap(s, width, size, mono=False):
    cw = size * (0.6 if mono else 0.52)
    n = max(1, int(width / cw))
    lines, cur = [], ""
    for w in s.split():
        if len(cur) + len(w) + (1 if cur else 0) > n:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, width, size=13, lh=None, **kw):
    lh = lh or size * 1.38
    for i, line in enumerate(wrap(s, width, size, kw.get("font") == MONO)):
        t(x, y + i * lh, line, size, **kw)
    return y + len(wrap(s, width, size, kw.get("font") == MONO)) * lh


def rect(x, y, w, h, fill, rx=0, stroke="none", dash=None, sw=1):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
               f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def line(x1, y1, x2, y2, stroke=RULE, sw=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
               f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def code(x, y, s, fill, bg, size=13):
    w = len(s) * size * 0.6 + 12
    rect(x, y - size - 2, w, size + 9, bg, rx=4)
    t(x + 6, y, s, size, fill=fill, font=MONO)
    return w


# ---- header ---------------------------------------------------------------
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" role="img" aria-labelledby="ttl desc">')
out.append('<title id="ttl">Choosing a sampling design in select_clips()</title>')
out.append('<desc id="desc">Three cards match each sampling_mode of '
           'select_clips() to the question it answers: top for retraining and '
           'calibration, random_detections for false-positive rates, '
           'random_recordings for false-positive and false-negative rates. '
           'Below, three panels explain how to cap the effort, why top clips '
           'underestimate false positives and what follows the review.</desc>')
rect(0, 0, W, H, "#ffffff")
M = 54
t(M, 62, "sheepdog · select_clips(pred, sampling_mode = …)", 14, MUTED, font=MONO)
t(M, 108, "Pick the sampling design by the question", 38, weight="bold")
t(M, 152, "you need to answer", 38, weight="bold")
t(W - M, 104, "The three designs answer different questions.", 15, MUTED,
  anchor="end")
t(W - M, 126, "A validation sample drawn for one purpose is", 15, MUTED,
  anchor="end")
out.append(f'<text x="{W - M}" y="148" font-family="{SANS}" font-size="15" '
           f'fill="{MUTED}" text-anchor="end">generally <tspan font-weight='
           f'"bold" fill="{INK}">not valid</tspan> for another.</text>')
line(M, 176, W - M, 176, INK, 1.5)

# ---- cards ----------------------------------------------------------------
cards = [
    dict(col="#1f4e9c", tint="#e6edf8", tag="TRAIN & CALIBRATE",
         q="Which clips best teach or calibrate my classifier?",
         mode='sampling_mode = "top"',
         bars=[(.30, 0), (.75, 1), (.45, 0), (.55, 0), (.82, 1), (.25, 0),
               (.50, 0), (.62, 0), (.40, 0), (.78, 1)], dashed=[],
         legend="Each bar = one prediction (order arbitrary) · filled = selected",
         desc="Keeps the highest-confidence predictions in each site × "
              "species × night × hour stratum.",
         rows=[("Unit drawn", "Prediction"),
               ("Selection", "Highest confidence per stratum"),
               ("Use for", "Classifier retraining; calibrate() score → "
                           "probability")],
         args=[("n_top = 2", "predictions kept per stratum"),
               ("min_confidence", "discard predictions below this score first"),
               ("strata", "grouping for the per-stratum pick")],
         warn="Not a probability sample (inclusion_prob = NA). Never use it "
              "to estimate false-positive rates."),
    dict(col="#a8460f", tint="#f9ebe2", tag="FALSE POSITIVES",
         q="How many of my detections are false positives?",
         mode='sampling_mode = "random_detections"',
         bars=[(.30, 0), (.62, 0), (.42, 1), (.55, 0), (.80, 0), (.28, 0),
               (.48, 1), (.66, 1), (.42, 0), (.74, 0)], dashed=[],
         legend="Each bar = one prediction (order arbitrary) · filled = selected",
         desc="Draws occasions with a detection ≥ threshold at random, "
              "whatever their score; every detection in a drawn occasion is "
              "reviewed.",
         rows=[("Unit drawn", "Occasion with a detection"),
               ("Selection", "Random, within score-independent strata"),
               ("Use for", "Observation-confirmation design (Chambert et al. "
                           "2015)")],
         args=[("threshold", "required; must equal the occupancy-analysis "
                             "threshold"),
               ('occasion_unit = "file"', 'or "minute": whole recording or '
                                          'one-minute occasion'),
               ("n_top", "occasions drawn per stratum"),
               ('strata = "night_hour"', 'or "night", "site_species", "hour", '
                                         '"week", "month", or your own '
                                         'columns (never confidence/rank)')],
         warn="Check clips per occasion = n_detections_occasion: a missing "
              "clip breaks the “all detections confirmed” assumption."),
    dict(col="#116a52", tint="#e3f2ec", tag="FALSE POSITIVES + NEGATIVES",
         q="What does the classifier miss, and what does it get wrong?",
         mode='sampling_mode = "random_recordings"',
         bars=[(.28, 0), (.62, 0), (0, 0), (.50, 1), (.66, 0), (.10, 1),
               (.45, 0), (.55, 0), (0, 0), (.64, 0)], dashed=[2, 8],
         legend="Each bar = one recording (order arbitrary) · dashed = no "
                "predictions",
         desc="Draws recordings at random among all recorded, including ones "
              "with no predictions (dashed), and annotates them by ear.",
         rows=[("Unit drawn", "Recording or minute"),
               ("Selection", "Random, among all recorded"),
               ("Use for", "Multiple-method design (Miller et al. 2011)")],
         args=[("recordings", "required: list of ALL recordings, with or "
                              "without predictions"),
               ("recording_fraction = 0.01", "or n_recordings_per_site; "
                                             "raise it for small projects"),
               ('species = "boa-ran"', "limit annotation to target species "
                                       "to save listening effort"),
               ("recording_duration = 300", "sets clip_end for whole "
                                            "recordings")],
         warn="Not confirmations of detections: confidence and rank are NA, "
              "and they are handled differently downstream."),
]
CW, GAP, CY, CH = 392, 25, 204, 830
for i, c in enumerate(cards):
    x = M + i * (CW + GAP)
    col = c["col"]
    rect(x, CY, CW, CH, "#ffffff", rx=10, stroke=RULE)
    out.append(f'<path d="M{x} {CY + 10} a10 10 0 0 1 10 -10 h{CW - 20} '
               f'a10 10 0 0 1 10 10 v134 h-{CW} z" fill="{col}"/>')
    t(x + 20, CY + 30, c["tag"], 12, "#ffffff", "bold")
    para(x + 20, CY + 58, c["q"], CW - 40, 19, 25, fill="#ffffff",
         weight="bold")
    mw = len(c["mode"]) * 14 * 0.6 + 14
    rect(x + 20, CY + 98, mw, 28, "rgba(255,255,255,0.16)", rx=4,
         stroke="rgba(255,255,255,0.55)")
    t(x + 27, CY + 117, c["mode"], 14, "#ffffff", font=MONO)

    # mini chart
    gx, gy, gw, gh = x + 34, CY + 166, CW - 54, 86
    rect(gx, gy, gw, gh, PANEL, rx=4)
    out.append(f'<text transform="translate({x + 24},{gy + gh - 4}) '
               f'rotate(-90)" font-family="{SANS}" font-size="10" '
               f'fill="{MUTED}">confidence ↑</text>')
    thr_y = gy + gh - 0.45 * gh
    bw = (gw - 20) / len(c["bars"])
    for k, (h, sel) in enumerate(c["bars"]):
        bx = gx + 10 + k * bw + 3
        if k in c["dashed"]:
            rect(bx, gy + gh - 12, bw - 6, 10, "none", stroke=MUTED,
                 dash="3 2")
            continue
        rect(bx, gy + gh - h * gh, bw - 6, h * gh, col if sel else GREY_BAR)
    if i < 2:
        line(gx + 4, thr_y, gx + gw - 4, thr_y, MUTED, 1, "4 3")
    t(x + CW / 2, gy + gh + 18, c["legend"], 10.5, MUTED, anchor="middle")
    y = para(x + 20, gy + gh + 44, c["desc"], CW - 40, 13, 18, fill=INK)

    y += 12
    for lab, val in c["rows"]:
        t(x + 20, y, lab, 13, MUTED)
        y2 = para(x + 116, y, val, CW - 136, 13, 18, weight="bold")
        y = y2 + 6
    y += 8
    t(x + 20, y, "KEY ARGUMENTS", 11.5, MUTED, "bold")
    y += 26
    for a, d in c["args"]:
        code(x + 20, y, a, col, c["tint"], 13)
        y = para(x + 20, y + 20, d, CW - 40, 12, 16, fill=MUTED) + 12

    wy = CY + CH - 84
    rect(x + 18, wy, CW - 36, 64, WARN_BG, rx=6)
    out.append(f'<path d="M{x + 36} {wy + 18} l8 14 h-16 z" fill="none" '
               f'stroke="{WARN_INK}" stroke-width="1.4"/>')
    t(x + 36, wy + 30, "!", 9, WARN_INK, "bold", anchor="middle")
    para(x + 54, wy + 25, c["warn"], CW - 90, 12, 16, fill=WARN_INK)

# ---- after choosing --------------------------------------------------------
Y0 = CY + CH + 32
line(M, Y0, W - M, Y0, INK, 1.5)
t(M, Y0 + 40, "After choosing a design", 22, weight="bold")
t(M + 268, Y0 + 40, "three things to know", 14, MUTED)
PY, PH = Y0 + 64, H - (Y0 + 64) - 30


def panel(i, title, sub):
    x = M + i * (CW + GAP)
    rect(x, PY, CW, PH, PANEL, rx=10)
    out.append(f'<circle cx="{x + 32}" cy="{PY + 34}" r="13" fill="{INK}"/>')
    t(x + 32, PY + 39, str(i + 1), 13, "#ffffff", "bold", anchor="middle")
    t(x + 56, PY + 39, title, 16, weight="bold")
    para(x + 56, PY + 60, sub, CW - 76, 12.5, 17, fill=MUTED)
    return x


# 1: capping the effort
x = panel(0, "Too many clips to listen to?",
          "Cap the total with one of these arguments.")
tx, ty, tw = x + 18, PY + 86, CW - 36
rect(tx, ty, tw, PH - 104, "#ffffff", rx=6, stroke=RULE)
cols = [tx + tw - 150, tx + tw - 94, tx + tw - 36]
t(tx + 12, ty + 22, "Argument", 11, MUTED, "bold")
for cx, lab, cc in zip(cols, ["top", "rand. det.", "rand. rec."],
                       [cards[0]["col"], cards[1]["col"], cards[2]["col"]]):
    t(cx, ty + 22, lab, 10.5, cc, "bold", anchor="middle")
rows = [("target_total", "total per site, split evenly across species",
         [1, 1, 0]),
        ("max_per_species", "fixed cap per site × species (ignored if "
                            "target_total is set)", [1, 1, 0]),
        ("balance_by_hour = TRUE", "spread picks round-robin across hours",
         [1, 1, 0]),
        ("recording_fraction", "or n_recordings_per_site: recordings per "
                               "site to annotate", [0, 0, 1])]
ry = ty + 34
for a, d, marks in rows:
    line(tx, ry, tx + tw, ry)
    t(tx + 12, ry + 20, a, 12.5, font=MONO, weight="bold")
    yy = para(tx + 12, ry + 38, d, tw - 170, 11.5, 15, fill=MUTED)
    for cx, mk, cc in zip(cols, marks,
                          [cards[0]["col"], cards[1]["col"], cards[2]["col"]]):
        t(cx, ry + 30, "✓" if mk else "–", 15, cc if mk else MUTED,
          "bold" if mk else "normal", anchor="middle")
    ry = max(yy, ry + 52) + 4

# 2: why not top
x = panel(1, "Why not use “top” for false positives?",
          "Because it only picks the high scorers. Median confidence of the "
          "clips each design selects (vignette example):")
bx, by, bw = x + 18, PY + 122, CW - 36
rect(bx, by, bw, 166, "#ffffff", rx=6, stroke=RULE)
bars = [("All detections ≥ threshold (reference)", .72, "#6b7480"),
        ("random_detections (weighted by 1 / inclusion_prob)", .72,
         cards[1]["col"]),
        ("top", .81, cards[0]["col"])]
inner = bw - 28
for k, (lab, v, cc) in enumerate(bars):
    yy = by + 26 + k * 44
    t(bx + 14, yy, lab, 12)
    t(bx + bw - 14, yy, f"{v:.2f}", 12, weight="bold", font=MONO,
      anchor="end")
    rect(bx + 14, yy + 8, inner, 10, "#e6e9ee", rx=2)
    rect(bx + 14, yy + 8, inner * v, 10, cc, rx=2)
ref = bx + 14 + inner * .72
line(ref, by + 30, ref, by + 150, INK, 1.2, "3 2")
t(bx + 14, by + 158, "0", 10.5, MUTED, font=MONO)
t(bx + bw - 14, by + 158, "1", 10.5, MUTED, font=MONO, anchor="end")
t(bx + bw / 2, by + 158, "dashed = all detections (0.72)", 10.5, MUTED,
  anchor="middle")
yy = by + 192
out.append(f'<text x="{bx}" y="{yy}" font-family="{SANS}" font-size="12.5" '
           f'fill="{INK}"><tspan fill="{cards[1]["col"]}" font-weight="bold">'
           f'random_detections</tspan> matches the real mix of scores ✓</text>')
out.append(f'<text x="{bx}" y="{yy + 22}" font-family="{SANS}" '
           f'font-size="12.5" fill="{INK}"><tspan fill="{cards[0]["col"]}" '
           f'font-weight="bold">top</tspan> is shifted up → fewer false '
           f'positives in the</text>')
out.append(f'<text x="{bx}" y="{yy + 40}" font-family="{SANS}" '
           f'font-size="12.5" fill="{INK}">sample → false-positive rate '
           f'<tspan font-weight="bold">underestimated</tspan> ✗</text>')

# 3: what next
x = panel(2, "What happens next?", "From selected clips to an occupancy model.")
sx, sy, sw = x + 18, PY + 86, CW - 36
rect(sx, sy, sw, 280, "#ffffff", rx=6, stroke=RULE)
steps = [("Choose clips", "select_clips()"),
         ("Cut the audio clips", "cut_clips() or extract_validation_clips()"),
         ("Listen and record a verdict", "positive / negative / unsure"),
         ("Join verdicts back to the table", "post_validation()"),
         ("Fit the occupancy model", 'vignette("crywolf-integration")')]
for k, (a, b) in enumerate(steps):
    yy = sy + 30 + k * 52
    if k:
        line(sx, yy - 22, sx + sw, yy - 22)
    t(sx + 18, yy, str(k + 1), 13, MUTED, "bold")
    t(sx + 44, yy, a, 13.5, weight="bold")
    t(sx + 44, yy + 19, b, 12, MUTED, font=MONO)
para(sx, sy + 304, "random_detections clips carry inclusion_prob: weight "
     "them by 1 / inclusion_prob when estimating rates.",
     sw, 12, 16, fill=MUTED)

out.append("</svg>")
open("vignettes/figures/sampling-designs.svg", "w").write("\n".join(out))
