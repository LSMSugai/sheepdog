import os, re, json, base64
d = os.path.dirname(os.path.abspath(__file__)) + '/'
style = open(d + 'base.css').read()
panels = json.load(open(d + 'panels.json'))

fp = d + 'fontpkg/node_modules/@fontsource/'
ff = ''
for fam, pkg, ws in [('Figtree', 'figtree', [400, 700]), ('IBM Plex Mono', 'ibm-plex-mono', [400])]:
    for w in ws:
        b = base64.b64encode(open(f'{fp}{pkg}/files/{pkg}-latin-{w}-normal.woff2', 'rb').read()).decode()
        ff += f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:normal;font-display:block;src:url(data:font/woff2;base64,{b}) format('woff2')}}\n"

extra = '''
:root{--bg:#ffffff}
svg{stroke:none}
*,svg text{font-weight:400!important}
body{padding-block:40px 40px}
.wrap{gap:24px}
figure.panel{border-color:#e3e8e5}
.wrapper code{font-family:var(--mono);font-size:12.5px;color:var(--c)}
.src{font-size:12.5px;color:var(--muted);border-top:1px solid var(--line);padding-top:12px}
.stage{gap:16px}
figure.panel.wide{grid-column:1 / -1}
svg text .optfn,svg .optfn{font-weight:700!important;font-style:italic}
.phead{display:flex;align-items:baseline;gap:10px;border-bottom:1px solid var(--line);padding-bottom:8px}
.phead .ttl{font-size:16px;color:var(--ink)}
.phead .ltr{font:12px/1 var(--mono);color:var(--c)}

.st{display:inline-grid;place-items:center;width:17px;height:17px;border-radius:50%;background:var(--c);color:var(--surface);font:11px/1 var(--mono);margin:0 5px 0 2px;vertical-align:1px}
.st.g{background:var(--s3)}
.st.o{background:var(--surface);color:var(--c);border:1.5px solid var(--c);width:14px;height:14px}
figcaption .ltr{white-space:nowrap}

.row3{display:grid;grid-template-columns:minmax(0,1fr) 180px minmax(0,1fr);gap:14px;align-items:stretch}
.strip{border:1.5px dashed var(--c);border-radius:12px;padding:12px 16px;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:6px 10px;text-align:center;background:var(--soft)}
.strip code{font-family:var(--mono);font-size:12.5px;color:var(--c);overflow-wrap:normal;word-break:normal}
.strip code.big{font-size:13px;color:var(--ink)}
.strip .runs,.strip .note{font-size:13px;color:var(--muted)}
.strip .ar{color:var(--c);line-height:1}
@media (max-width:760px){.row3{grid-template-columns:minmax(0,1fr)}}

.grp.idx{margin-bottom:-6px}
.grp{font:12px/1.2 var(--mono);letter-spacing:.04em;color:var(--c);text-transform:uppercase}
h1{font-size:40px}
.s1grid{display:grid;grid-template-columns:minmax(0,1fr) repeat(4,30px);column-gap:8px;row-gap:16px}
.s1grid>.panels{grid-column:1}
.s1grid>.r1{grid-row:1}.s1grid>.r2{grid-row:2}.s1grid>.r3{grid-row:3}.s1grid>.r4{grid-row:4}
.brk{border:1.5px solid var(--c);border-left:none;border-radius:0 10px 10px 0;margin:6px 0;position:relative;width:12px}
.brk .bl{position:absolute;left:16px;top:50%;transform:translateY(-50%);writing-mode:vertical-rl;white-space:nowrap;font-size:11.5px;line-height:1.1;color:var(--muted)}
.brk code{font-family:var(--mono);font-size:11px;color:var(--c)}
@media (max-width:760px){.s1grid{grid-template-columns:minmax(0,1fr)}.brk{display:none}}
'''

def doc(title, body):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<style>{ff}{style}{extra}</style></head>
<body><div class="wrap">{body}
<p class="src">sheepdog (R package) · github.com/diogoprov/sheepdog · provetelab.org/sheepdog · values in the drawings are illustrative.</p>
</div></body></html>'''

def fig(pid, ltr, title, text, grp=None, wide=False):
    g = f'<span class="grp">{grp}</span>' if grp else ''
    return (f'<figure class="panel{" wide" if wide else ""}"><div>{panels[pid]}</div><figcaption>{g}<span class="ttl"><span class="ltr">{ltr}</span>{title}</span>'
            f'<p>{text}</p></figcaption></figure>')

def figh(pid, title, steps, grp=None):
    g = f'<span class="grp idx">{grp}</span>' if grp else ''
    return (f'<figure class="panel">{g}<div class="phead"><span class="ttl">{title}</span><span class="ltr">{steps}</span></div>'
            f'<div>{panels[pid]}</div></figure>')

def header(h, lede=None, eyebrow='sheepdog'):
    e = f'<span class="eyebrow">{eyebrow}</span>' if eyebrow else ''
    l = f'<p class="lede">{lede}</p>' if lede else ''
    return f'<header>{e}<h1>{h}</h1>{l}</header>'

def stage(cls, figs, wrapper='', head=''):
    return f'<section class="stage {cls}">{head}<div class="panels">{"".join(figs)}</div>{wrapper}</section>'

S1 = [figh('s1a', 'Selection step', 'steps 1–2', 'Stage 1 - Validation data'),
      figh('s1b', 'Review step', 'steps 3–5', 'Stage 1 - Review app'),
      figh('s1c', 'A · Empirical threshold', 'step 7'),
      figh('s1e2', 'A · Act on the diagnosis', 'step 8'),
      figh('s1d', 'B · Model-based threshold', 'steps 7.1–7.2, alternative to A'),
      figh('s1bq', 'B · Check the calibration', 'step 8')]

G1, G2, G3, GB = 'i · Is the calibration reliable?', 'ii · Apply it to every prediction', 'iii · Turn probabilities into detections', 'Bayesian option (brms) · across i–iii'
S2 = [fig('s2a', 'a', 'Fit the score-to-probability curve', 'Each reviewed clip is a 1 (true) or 0 (false) at its confidence score. The calibration is a logistic regression of the verdict on the logit of the score, extended in sheepdog with species and site random effects.', G1),
      fig('s2b', 'b', 'Choose the model by cross-validation', 'Five candidates go from one global curve up to species × site effects. sheepdog keeps the simplest model whose held-out log-loss is within one standard error of the best.', G1),
      fig('s2q', 'c', 'Check each species on held-out clips', 'Pooling can hide a weak species. <code>calibration_quality()</code> asks of each one: does the model beat its base rate, does it rank true clips above false ones, and are its probabilities right? <code>calibration_effort()</code> shows how many clips per cell are needed.', G1),
      fig('s2c', 'd', 'Apply the curve to every detection', '<code>score_detections()</code> gives every detection a probability <code>p_tp</code>, reviewed or not. The score where each species’ curve crosses <code>p_min</code> is its threshold (<code>calibrated_thresholds()</code>), the per-species probabilistic threshold of Wood &amp; Kahl (2024).', G2),
      fig('s2d', 'e', 'Collapse detections into nights', 'A site × species × night counts as detected when at least k detections reach <code>p_min</code>. The history keeps k = 1, 2 and 3 for sensitivity analysis and feeds stage 3 or the occupancy export.', G3),
      fig('s2bayes', 'f', 'Carry the uncertainty forward', 'The selected model is refitted in brms. Each detection gets a posterior: the mean <code>p_tp</code>, a lower bound <code>p_tp_lower</code>, and <code>pr_reliable</code>, the probability that P(tp) ≥ <code>p_min</code>. Histories and matrices can be rebuilt for each draw. The fit is checked with prior, convergence, sensitivity and posterior predictive checks.', GB)]
S3 = [fig('s3a', 'a', 'Keep only cells you can trust', 'Each site × species cell is reliable, probably absent (a true zero) or unreliable (a zero that could be a false negative). Only species with no unreliable cell are core species and enter the matrices.'),
      fig('s3b', 'b', 'Standardise by effort', 'Sites differ in how many nights were recorded. Each cell of the matrix is nights detected ÷ nights recorded in that site × month.'),
      fig('s3c', 'c', 'Assemble the site × month matrix', 'One row per site × month and one column per core species. The highlighted cell is the 0.46 from panel b.'),
      fig('s3d', 'd', 'Analyse the community', 'The matrices go into ordination (PCoA, NMDS, RDA) in vegan or into gllvm, which takes the nights recorded as binomial trials.')]
S4 = [fig('s4a', 'a', 'Export occasions, scores and reviews', 'Every occasion of the survey goes into the export, including those with no detection, together with its score and, if it was reviewed, its verdict and sampling design. Everything is written to one folder with a documented schema.'),
      fig('s4b', 'b', 'Carry calibration uncertainty into ψ', '<code>occasion_draws()</code> builds one detection matrix per posterior draw. You fit the occupancy model to each one and pool the posteriors.')]

def wrap(text): return f'<div class="wrapper"><strong>Shortcut:</strong> {text}</div>'
occ_head = '<div class="stage-head"><h2>Alternative ending · Occupancy with false positives</h2><p>Instead of fixing a threshold, pass the scores and verdicts to an occupancy model that estimates false positives itself.</p></div>'


def stage1_html():
    wide = lambda pid, t, st, g=None: figh(pid, t, st, g).replace('<figure class="panel">', '<figure class="panel wide">', 1)
    row1 = f'<div class="panels r1">{S1[0]}{S1[1]}</div>'
    rev = f'<div class="panels r2">{wide("s1rev", "Review step · several reviewers", "optional, steps 4.1–5.3", "Stage 1 - Several reviewers")}</div>'
    pv = f'<div class="panels r3">{wide("s1pv", "Summary step", "steps 6.1–6.5")}</div>'
    dg = f'<div class="panels r4">{wide("s1diag", "Diagnostic step", "step 7: 7A or 7B")}</div>'
    def br(col, rows, fn, txt):
        return (f'<div class="brk" style="grid-column:{col};grid-row:{rows}"><span class="bl"><code>{fn}</code> {txt}</span></div>')
    brs = (br(2, '1', 'extract_validation_clips()', 'runs steps 1 → 2 → 3 in one call')
           + br(3, '1', 'run_app()', 'covers steps 2–5 in a browser app')
           + br(4, '1 / span 3', 'post_validation()', 'runs steps 5 and 6.2–6.5; reads the verdicts itself, so it can replace step 5')
           + br(5, '3 / span 2', 'review_support()', '7A: calls suggest_thresholds() (6.3) again and adds the diagnosis'))
    return f'<section class="stage st1"><div class="s1grid">{row1}{rev}{pv}{dg}{brs}</div></section>'


def stage2_html():
    def st(pid, title, step, sub, grp=None, wide=False):
        g = f'<span class="grp idx">{grp}</span>' if grp else ''
        return (f'<figure class="panel{" wide2" if wide else ""}">{g}<div class="phead"><span class="ttl">{title}</span><span class="ltr">{step}</span></div>'
                f'<p class="psub">{sub}</p><div>{panels[pid]}</div></figure>')
    G1, G2, G3 = 'i · Is the calibration reliable?', 'ii · Apply it and turn probabilities into detections', 'iii · Carry the uncertainty and go on'
    r1 = ('<div class="panels three3 r1">'
          + st('s2a', 'Fit the score-to-probability curve', 'step 1', 'Input: the <code>random_detections</code> clips verified in Stage 1 (<code>validation_by_clip.csv</code>, Figure 1 · step 6), read with <code>read_validations()</code>. Each clip is 1 (true) or 0 (false) at its score; the curve is a logistic regression on logit(score), with species and site effects.', G1)
          + st('s2b', 'Choose the model', 'step 2', '<code>compare_calibration_models()</code> fits five candidates with cross-validation by night; <code>select_calibration_model()</code> keeps the simplest within one standard error of the best.')
          + st('s2q_opts', 'Check each species', 'step 3', '<code>calibration_quality()</code> on held-out clips asks: does the model beat the base rate, does it rank true clips above false ones, are its probabilities right? Only species marked ok go on.')
          + '</div>')
    r2 = ('<div class="panels three3 r2">'
          + st('s2c', 'Apply the curve to every detection', 'step 4', '<code>score_detections()</code> gives every detection its P(tp), reviewed or not. <code>calibrated_thresholds()</code> gives the score where each curve reaches <code>p_min</code> (Wood &amp; Kahl 2024).', G2)
          + st('s2d', 'Collapse detections into nights', 'step 5', '<code>detection_history()</code>: a site × species × night counts as detected when at least k detections count. k = 1, 2 and 3 are kept for sensitivity.')
          + st('s2ways', 'Three ways to decide which detections count', 'step 6', 'The rule of step 5. Way 1 needs any calibration; ways 2 and 3 need the posterior of a brms fit (step 7).')
          + '</div>')
    r3 = ('<div class="panels row3s r3">'
          + st('s2bayes', 'Fit with brms', 'step 7', '<code>engine = "brms"</code>: each detection gets a posterior, with the mean <code>p_tp</code>, a lower bound <code>p_tp_lower</code> and <code>pr_reliable</code>. Checks: <code>calibration_prior()</code>, <code>calibration_diagnostics()</code>, <code>calibration_sensitivity()</code>, <code>calibration_ppc()</code>.', G3)
          + st('s2next', 'What comes next', 'step 8', 'From the history (way 1 or 2) or the histories (way 3) to community matrices, or to occupancy with false positives.', wide=True)
          + '</div>')
    def br(col, rows, fn, txt):
        return f'<div class="brk" style="grid-column:{col};grid-row:{rows}"><span class="bl"><code>{fn}</code> {txt}</span></div>'
    brs = (br(2, '1 / span 2', 'calibrate()', 'runs steps 1–5 (way 1) in one call and writes their files')
           + br(3, '1 / span 3', 'engine = "brms"', 'the same, fitted with brms: adds step 7 and ways 2–3'))
    css = ('<style>.wrap{max-width:1460px}.s2grid{display:grid;grid-template-columns:minmax(0,1fr) repeat(2,30px);column-gap:8px;row-gap:16px}'
           '.s2grid>.panels{grid-column:1}.s2grid>.r1{grid-row:1}.s2grid>.r2{grid-row:2}.s2grid>.r3{grid-row:3}'
           '.panels.three3{grid-template-columns:repeat(3,minmax(0,1fr));align-items:start}.panels.row3s{grid-template-columns:minmax(0,1fr) minmax(0,2fr);align-items:start}'
           '.psub{font-size:13px;line-height:1.45;color:var(--muted);margin:0}.psub code{font-family:var(--mono);font-size:12px;color:var(--c)}'
           '@media (max-width:900px){.panels.three3,.panels.row3s,.s2grid{grid-template-columns:minmax(0,1fr)}.brk{display:none}}</style>')
    return css + f'<section class="stage st2"><div class="s2grid">{r1}{r2}{r3}{brs}</div></section>'


def stage3_html():
    def st(pid, title, step, sub, grp=None):
        g = f'<span class="grp idx">{grp}</span>' if grp else ''
        return (f'<figure class="panel">{g}<div class="phead"><span class="ttl">{title}</span><span class="ltr">{step}</span></div>'
                f'<p class="psub">{sub}</p><div>{panels[pid]}</div></figure>')
    r1 = ('<div class="panels r1">'
          + st('s3a', 'Keep the cells you can trust', 'steps 1–2', '<code>cell_status(fit, validations, p_min, min_n)</code> labels each site × species cell reliable (the curve reaches <code>p_min</code> within the reviewed scores, with ≥ <code>min_n</code> clips), probably absent (reviewed, no true positive: a real zero) or unreliable (a zero that could be a false negative). <code>suggest_core_species()</code> keeps the species with no unreliable cell; the final choice is yours. Needs the Stage 2 fit.')
          + st('s3b', 'Count nights, standardise by effort', 'step 3', 'A night counts as detected when it has at least <code>k_min</code> (2) reliable detections (P(tp) ≥ <code>p_min</code>). Nights recorded are the distinct nights of the site in the history. Site × month cells with fewer than <code>min_nights_month</code> (5) nights are dropped.')
          + '</div>')
    r2 = ('<div class="panels r2">'
          + st('s3c', 'Assemble the site × month matrices', 'step 4', '<code>community_matrices()</code> gives frequency (nights detected ÷ nights recorded), counts, effort and trials, one column per core species. For way 3, <code>community_matrices_draws()</code> gives a mean and an interval per cell.')
          + st('s3d', 'Analyse the community', 'step 5', 'Ordination (PCoA, NMDS, RDA) in vegan, or gllvm with the trials matrix as binomial denominators. With way 3, repeat the analysis over draws and pool.')
          + '</div>')
    def br(rows, fn, txt):
        return f'<div class="brk" style="grid-column:2;grid-row:{rows}"><span class="bl"><code>{fn}</code> {txt}</span></div>'
    brs = br('1 / span 2', 'build_community_matrices()', 'reads the history file and runs steps 3–4 for the core species you give')
    occ = ('<section class="stage st4"><div class="stage-head"><h2>Occupancy with false positives</h2><p>A separate ending, not a step of Stage 3: export the occasions, scores and reviews, and let an occupancy model estimate the false positives (index section “Occupancy models”).</p></div><div class="panels">'
           + st('s4a', 'Export occasions, scores and reviews', 'step 1', '<code>export_occupancy_data()</code> writes every occasion of the survey, including those with no detection, with its score and, if reviewed, its verdict and sampling design, to one folder with a documented schema.')
           + st('occ_routes', 'Two routes into crywolf', 'step 2', 'A score threshold (any route) gives one data set; the brms calibration draws give one per draw.')
           + '</div></section>')
    css = ('<style>.s3grid{display:grid;grid-template-columns:minmax(0,1fr) 30px;column-gap:8px;row-gap:16px}.s3grid>.panels{grid-column:1}'
           '.s3grid>.r1{grid-row:1}.s3grid>.r2{grid-row:2}.panels.r1,.panels.r2{align-items:start}'
           '.psub{font-size:13px;line-height:1.45;color:var(--muted);margin:0}.psub code{font-family:var(--mono);font-size:12px;color:var(--c)}'
           '@media (max-width:760px){.s3grid{grid-template-columns:minmax(0,1fr)}.brk{display:none}}</style>')
    return css + f'<section class="stage st3"><div class="s3grid">{r1}{r2}{brs}</div></section>' + occ


def diag_html():
    w = lambda pid, t, st, g=None: figh(pid, t, st, g).replace('<figure class="panel">', '<figure class="panel wide">', 1)
    A = (f'<section class="stage st1"><div class="stage-head"><h2>A · Empirical threshold</h2><p>7A in Figure 1 · “What is the threshold for 90% of precision in my dataset?”</p></div>'
         f'<div class="panels rowA">{figh("d7a1", "Get the threshold", "A · step 1")}{figh("d7a2m", "Read the diagnosis and act on it", "A · step 2")}{figh("d7a4", "Enough data to continue?", "A · step 3")}</div></section>')
    B = (f'<section class="stage st2"><div class="stage-head"><h2>B · Model-based threshold</h2><p>7B in Figure 1 · “What is the threshold for a 95% probability of true positive?”</p></div>'
         f'<div class="panels rowB">{figh("d7b1", "Fit the calibration", "B · step 1")}{figh("d7b2", "Check it", "B · step 2")}{figh("d7b3", "Get the threshold", "B · step 3")}{figh("d7b4", "Act on the check", "B · step 4")}</div>'
         f'<div class="panels">{w("d7b5", "What comes next", "B · step 5")}</div></section>')
    Cm = f'<section class="stage st3"><div class="panels">{w("d7cmp", "Compare A and B", "after both")}</div></section>'
    css = ('<style>.wrap{max-width:1460px}.panels.rowA{grid-template-columns:minmax(0,32fr) minmax(0,66fr) minmax(0,44fr)}'
           '.panels.rowB{grid-template-columns:repeat(4,minmax(0,1fr))}.stage.st3 figure svg,.stage.st2 figure.wide svg{max-width:1100px}'
           '.panels.rowA,.panels.rowB{align-items:start}'
           '@media (max-width:900px){.panels.rowA,.panels.rowB{grid-template-columns:minmax(0,1fr)}}</style>')
    return css + A + B + Cm


files = {
    '0_sheepdog_pipeline': ('sheepdog Pipeline',
        header('sheepdog: from confidence scores to species-based matrices', eyebrow=None) +
        f'<section class="overview" aria-label="Pipeline overview">{panels["overview"]}</section>'),
    '1_stage1_validation': ('sheepdog Stage 1',
        header('Stage 1 · Validation', 'Draw clips from the detections, verify them, and measure how often the classifier is right.') +
        stage1_html()),
    '1y_stage1_diagnostic': ('sheepdog Stage 1 Diagnostic',
        header('Stage 1 · Diagnostic (7A / 7B)', 'Step 7 of Figure 1 in detail: A, the empirical threshold and its diagnosis (7A); B, the model-based threshold and its check (7B); and how to compare them.') +
        diag_html()),
    '2_stage2_calibration': ('sheepdog Stage 2',
        header('Stage 2 · Calibration', 'Check that the score-to-probability calibration is reliable, apply it to every prediction, and turn the probabilities into detections for further analyses.') +
        stage2_html()),
    '3_stage3_community': ('sheepdog Stage 3',
        header('Stage 3 · Community matrices', 'Keep the reliable cells, count nights with a strict entry rule, standardise by effort and build site × month matrices for ordination; or export to an occupancy model with false positives.') +
        stage3_html()),
}
for k, (t, body) in files.items():
    os.makedirs(d + 'abstracts', exist_ok=True)
    html = doc(t, body)
    if k.startswith('0_'):
        html = html.replace('</style>', '.wrap{max-width:1400px}.overview svg{min-width:0}</style>', 1)
    open(d + f'abstracts/{k}.html', 'w').write(html)
print('built')
