"""Small drawings of what each route does (score axis, curve/clips, cut, kept detections)."""
import math

def esc(s): return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def T(x, y, s, cls="tm", a="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{a}" {extra}>{esc(s)}</text>'
def R(x, y, w, h, cls, rx=0, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" class="{cls}" {extra}/>'
def C(x, y, r, cls, extra=""):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="{cls}" {extra}/>'
def L(x1, y1, x2, y2, cls, extra=""):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{cls}" {extra}/>'
def P(d, cls, extra=""):
    return f'<path d="{d}" class="{cls}" {extra}/>'

W, H = 280, 196
X0, X1, YT, YB = 34, 270, 14, 100
def sx(s): return X0 + (s - 0.1) / 0.9 * (X1 - X0)
def py(p): return YB - p * (YB - YT)
def curve(s0, k): return lambda s: 1 / (1 + math.exp(-k * (s - s0)))
def cut(s0, k, p=0.95): return s0 + math.log(p / (1 - p)) / k
SS = [0.1 + i * 0.9 / 120 for i in range(121)]
def path(f): return "M" + " L".join(f"{sx(s):.1f} {py(f(s)):.1f}" for s in SS)

DETS = [0.14, 0.19, 0.23, 0.28, 0.31, 0.36, 0.4, 0.44, 0.47, 0.51, 0.55, 0.58, 0.61, 0.64, 0.67, 0.7,
        0.72, 0.75, 0.77, 0.79, 0.81, 0.83, 0.85, 0.87, 0.89, 0.91, 0.93, 0.95, 0.97, 0.99]
FS = 'style="font-size:9.5px"'
SM = 'style="font-size:9px"'

def axes(b, ylab):
    b.append(L(X0, YT - 4, X0, YB, "sgrid")); b.append(L(X0, YB, X1, YB, "sgrid"))
    b.append(T(X0 - 4, YT + 3, "1", "tny tm", "end")); b.append(T(X0 - 4, YB + 3, "0", "tny tm", "end"))
    b.append(T(10, (YT + YB) / 2, ylab, "tny tm", "middle", f'transform="rotate(-90 10 {(YT+YB)/2})"'))
    b.append(T(X1, YB + 12, "score →", "tny tm", "end"))

def strip(b, y, thr, color, label="detections", h=11):
    if label == "detections":
        b.append(T(X0 - 4, y + 8.5, "all", "tny tm", "end", SM))
    else:
        b.append(T(X0 - 4, y + 8.5, label, "tny tm", "end", SM))
    for s in DETS:
        b.append(R(sx(s) - 1.6, y, 3.2, h, f"f{color}" if s >= thr else "fline", 1))

def vcut(b, t, color, lab, y_lab=YT + 10, dash=False):
    b.append(L(sx(t), YT - 2, sx(t), YB, f"st{color} w15" + (" dash" if dash else "")))
    if lab: b.append(T(sx(t) - 4, y_lab, lab, f"tny f{color}t", "end", SM))

def target(b, p=0.95):
    b.append(L(X0, py(p), X1, py(p), "sline dash"))
    b.append(T(X0 + 3, py(p) - 3, "p_min 0.95", "tny tm", "start", SM))

def stage1():
    b = []; axes(b, "verdict")
    clips = [(0.15, 0), (0.2, 0), (0.26, 1), (0.3, 0), (0.35, 0), (0.42, 1), (0.46, 0), (0.5, 1), (0.53, 0), (0.57, 1),
             (0.6, 1), (0.63, 0), (0.66, 1), (0.69, 1), (0.71, 0), (0.74, 1), (0.77, 1), (0.8, 1), (0.83, 1), (0.85, 0),
             (0.88, 1), (0.9, 1), (0.92, 1), (0.95, 1), (0.97, 1), (0.99, 1)]
    t = 0.735
    b.append(R(sx(t), YT - 2, X1 - sx(t), YB - YT + 2, "fs1", 0, 'opacity=".6"'))
    for i, (s, v) in enumerate(clips):
        y = py(v) + (-5 if v else 5) + (i % 3 - 1) * 2.5
        b.append(C(sx(s), y, 3, "f3" if v else "fbad"))
    kept = [v for s, v in clips if s >= t]
    vcut(b, t, "1", "empirical cut", YT + 46)
    b.append(T(sx(t) + 4, YT + 46, f"{sum(kept)} of {len(kept)} true", "tny f1t", "start", SM))
    strip(b, 118, t, "1")
    b.append(T(X0, 156, "reviewed clips right of the cut (green true,", "ts", "start", FS))
    b.append(T(X0, 169, "red false) must be ≥ 90% true, design-weighted;", "ts", "start", FS))
    b.append(T(X0, 182, "no curve. Bars: detections kept in colour", "ts", "start", FS))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Stage 1: empirical cut">{"".join(b)}</svg>'

S0, K = 0.55, 12
def way1():
    b = []; axes(b, "P(tp)"); target(b)
    b.append(P(path(curve(S0, K)), "nofill st2 w2"))
    t = cut(S0, K)
    b.append(C(sx(t), py(.95), 3, "f2"))
    vcut(b, t, "2", "cut", YB - 8)
    strip(b, 118, t, "2")
    b.append(T(X0, 156, "one fitted curve; the cut is where it", "ts", "start", FS))
    b.append(T(X0, 169, "crosses 0.95: every detection to the right", "ts", "start", FS))
    b.append(T(X0, 182, "is ≥ 95% likely to be true (kept in colour)", "ts", "start", FS))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Way 1: one curve, one cut">{"".join(b)}</svg>'

DRAWS = [(0.50, 13), (0.53, 10), (0.55, 12), (0.57, 14), (0.60, 11), (0.52, 12), (0.58, 10), (0.56, 13), (0.54, 11)]
def band():
    lo = [min(curve(s0, k)(s) for s0, k in DRAWS) for s in SS]
    hi = [max(curve(s0, k)(s) for s0, k in DRAWS) for s in SS]
    d = "M" + " L".join(f"{sx(s):.1f} {py(p):.1f}" for s, p in zip(SS, hi))
    d += " L" + " L".join(f"{sx(s):.1f} {py(p):.1f}" for s, p in zip(reversed(SS), reversed(lo))) + " Z"
    return P(d, "fs2", 'opacity=".9"')

def way2():
    b = []; axes(b, "P(tp)"); b.append(band()); target(b)
    b.append(P(path(curve(S0, K)), "nofill st2 w15"))
    tm = cut(S0, K)
    ts_ = sorted(cut(s0, k) for s0, k in DRAWS)
    t = ts_[int(0.9 * (len(ts_) - 1)) + 1 if len(ts_) > 1 else 0]
    b.append(R(sx(tm), YB - 22, sx(t) - sx(tm), 22, "fline", 0, 'opacity=".8"'))
    vcut(b, tm, "2", "", dash=True)
    vcut(b, t, "2", "cut", YB - 30)
    b.append(T(sx(t) + 4, YB - 8, "uncertain", "tny tm", "start", SM))
    strip(b, 118, t, "2")
    b.append(T(X0, 156, "the band holds the plausible curves; a", "ts", "start", FS))
    b.append(T(X0, 169, "detection is kept only if ≥ 90% of them", "ts", "start", FS))
    b.append(T(X0, 182, "pass 0.95 (pr_reliable): the cut moves right", "ts", "start", FS))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Way 2: cut where the curve is reliably above p_min">{"".join(b)}</svg>'

def way3():
    b = []; axes(b, "P(tp)"); target(b)
    show = [DRAWS[0], DRAWS[2], DRAWS[4]]
    for s0, k in DRAWS:
        b.append(P(path(curve(s0, k)), "nofill st2", 'stroke-width="1" opacity=".35"'))
    for j, (s0, k) in enumerate(show):
        b.append(P(path(curve(s0, k)), "nofill st2 w15"))
        b.append(C(sx(cut(s0, k)), py(.95), 2.6, "f2"))
    for j, (s0, k) in enumerate(show):
        y = 116 + j * 13
        strip(b, y, cut(s0, k), "2", f"d{j+1}", 9)
    b.append(T(X0, 169, "each draw is a plausible curve with its own", "ts", "start", FS))
    b.append(T(X0, 182, "cut → one history per draw (d1, d2, …), pooled", "ts", "start", FS))
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Way 3: one history per posterior draw">{"".join(b)}</svg>'

GRAPHICS = [stage1(), way1(), way2(), way3()]
