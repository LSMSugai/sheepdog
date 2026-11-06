"""Data of the four routes (rows), used by build_routes_article.py; run alone, writes the wide comparison table."""
import os, re
d = os.path.dirname(os.path.abspath(__file__)) + '/'
s1 = open(d + 'abstracts/1_stage1_validation.html').read()
head = s1[:s1.index('<body>')]
head = re.sub(r'<title>.*?</title>', '<title>sheepdog Detection Routes</title>', head)
css = '''<style>
.wrap{max-width:1900px}
table.routes{border-collapse:separate;border-spacing:0;width:100%;font-size:13px;line-height:1.45}
table.routes th{font:12px/1.3 var(--mono);letter-spacing:.04em;text-transform:uppercase;color:var(--muted);text-align:left;padding:10px 12px;border-bottom:2px solid var(--line);vertical-align:bottom}
table.routes td{padding:12px;border-bottom:1px solid var(--line);vertical-align:top;color:var(--ink)}
table.routes td.route{min-width:150px}
table.routes td.route b{display:block;font-size:14px;margin-bottom:4px}
table.routes code{font-family:var(--mono);font-size:11.5px;color:var(--c,#b86a12)}
table.routes ul{margin:0;padding-left:16px}
table.routes li{margin:0 0 3px}
.tag{display:inline-block;font:11px/1 var(--mono);padding:4px 7px;border-radius:99px;margin-top:4px}
.t1{background:var(--s1-soft);color:var(--s1)} .t2{background:var(--s2-soft);color:var(--s2)} .t4{background:var(--s4-soft);color:var(--s4)}
.unc{display:inline-block;font:11px/1 var(--mono);padding:4px 7px;border-radius:5px;margin-bottom:6px}
.u0{background:var(--line);color:var(--ink)} .u1{background:var(--s1-soft);color:var(--s1)} .u2{background:var(--s2-soft);color:var(--s2)} .u3{background:var(--s3-soft);color:var(--s3)}
tr.grp td{background:var(--bg);font:12px/1 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);padding:14px 12px 6px;border-bottom:1px solid var(--line)}
th.occ,td.occ{background:var(--s4-soft)} th.occ{color:var(--s4)}
.tnote{font-size:12.5px;color:var(--muted)} .tnote code{all:unset;font-family:var(--mono);font-size:11.5px;color:var(--s1)}
</style>'''
head = head.replace('</head>', css + '</head>')

rows = [
 dict(name='Stage 1 only', tag=('t1', 'empirical threshold'),
      how='score ≥ the empirical threshold of the cell',
      fn='<code>review_support()</code> or <code>suggest_thresholds()</code>; history built by hand, then <code>community_matrices()</code>',
      needs='a <code>random_detections</code> review; no model',
      guar='the <b>set</b> of kept detections reaches the target precision (e.g. 90% true)',
      unc=('u0', 'none'), uncx='a single threshold per cell; only <code>n_eff</code> hints at how solid it is',
      pros=['no model: counting reviewed clips', 'easy to explain', 'uses the design weights'],
      cons=['no built-in function for the history', 'only “reached” cells', 'set-level, not per detection', 'one cut per cell (unless <code>by</code>)', 'effort counted separately'],
      best='quick results; small projects; avoiding model assumptions',
      caution=['no built-in function: the history is built by hand', 'the guarantee is for the <b>set</b>: detections just above the cut can be mostly false', 'the cut is the first that passes; precision can dip again above it', 'only cells that “reached” the target get a cut; thin cells get none', 'assumes the <code>inclusion_prob</code> weights are right (cumulative across review rounds)', 'one cut per cell: assumes precision is stable across months and sites inside it (unless <code>by</code>)', 'effort (nights recorded) counted separately'],
      occ_rule='the empirical <b>score threshold</b>, as the detection threshold in crywolf', occ_fn='a fresh <code>random_detections</code> draw at that threshold (confirmation) and/or <code>random_recordings</code> → <code>export_occupancy_data()</code> without <code>fit</code>', occ_unc=('u2', 'within the model'), occ_uncx='false-positive rate estimated by the occupancy model; threshold treated as fixed'),
 dict(name='Stage 2 · way 1', tag=('t2', 'probability cut'),
      how='P(tp) ≥ <code>p_min</code> (0.95); with brms, the posterior mean',
      fn='<code>calibrate()</code> → <code>score_detections()</code> → <code>detection_history(rule = "mean")</code>',
      needs='a calibration model (lme4 or brms) that passed the checks',
      guar='<b>each</b> kept detection is ≥ 95% likely to be true, assuming the fitted curve is right',
      unc=('u0', 'ignored'), uncx='the curve is treated as exact',
      pros=['built in, effort included', 'per-detection guarantee', 'pooling covers cells with few clips', 'covariates possible', 'feeds Stage 3 directly'],
      cons=['depends on the model being right', 'pooling can lend a weak cell a curve', 'no uncertainty'],
      best='the standard route to Stage 3 matrices',
      caution=['depends on the model being right: use species with <code>calibration_quality()</code> “ok”', 'assumes the reviewed clips are a random draw of detections (<code>random_detections</code>, not <code>top</code>)', 'pooling can lend a weak cell a curve borrowed from other cells', 'outside the reviewed score range the curve is extrapolated', 'a site effect in the curve mixes local calling rate into P(tp)', 'assumes the same classifier version as the reviewed clips', 'the curve is treated as exact: no uncertainty'],
      occ_rule='the <b>score equivalent of p_min</b> (<code>thresholds.csv</code>, <code>calibrated_thresholds()</code>) as the detection threshold', occ_fn='same as Stage 1: confirmation draw at that threshold → <code>export_occupancy_data()</code> without <code>fit</code> (lme4 cannot export draws)', occ_unc=('u2', 'within the model'), occ_uncx='as Stage 1; a site-effect calibration mixes calling rate into the threshold'),
 dict(name='Stage 2 · way 2', tag=('t2', 'probability cut with certainty'),
      how='<code>pr_reliable</code> ≥ <code>prob_min</code>: the chance that P(tp) ≥ <code>p_min</code>',
      fn='<code>detection_history(rule = "probability", prob_min = 0.9)</code>',
      needs='a brms calibration (priors, convergence checks)',
      guar='each kept detection is ≥ 95% likely to be true <b>in at least 90% of the plausible curves</b> (<code>prob_min</code>), not only in the fitted one',
      unc=('u1', 'used in the cut'), uncx='stricter where the curve is uncertain, but not carried into the results',
      pros=['cautious where review was thin', 'still a single history'],
      cons=['needs brms: slower, more checks', 'drops some true detections', 'uncertainty not propagated'],
      best='cells that differ a lot in review effort',
      caution=['all the model assumptions of way 1', 'needs brms: slower; priors matter where review is thin (<code>calibration_sensitivity()</code>)', '<code>prob_min</code> is a second choice to justify', 'drops some true detections: more false negatives', 'uncertainty shapes the cut but is not carried into the results'],
      occ_rule='<code>threshold_lower</code> as a conservative score threshold; or, per draw, a probability cut', occ_fn='score route as above, or <code>export_occupancy_data(fit = …)</code> → <code>occasion_draws(rule = "threshold")</code>', occ_unc=('u1', 'partly'), occ_uncx='the cut is cautious; propagated only if the draws are used'),
 dict(name='Stage 2 · way 3', tag=('t2', 'one history per draw'),
      how='in each draw, P(tp) ≥ <code>p_min</code> under that draw’s curve; one history per draw',
      fn='<code>history_draws()</code> → <code>community_matrices_draws()</code>',
      needs='a brms calibration',
      guar='the same 95% cut as way 1, applied <b>separately in each posterior draw</b> of the curve; detections near the cut are kept in some draws and not others, which shows up as uncertainty in the results',
      unc=('u3', 'propagated'), uncx='mean and interval per matrix cell; analyses repeated over draws',
      pros=['carries calibration uncertainty into the results', 'most honest about what the calibration does not know'],
      cons=['needs brms', 'many histories to analyse and pool', 'harder to report'],
      best='publications where uncertainty in the community results matters',
      caution=['all the model assumptions of way 1: a wrong model gives confident wrong draws', 'needs brms and its convergence checks', 'intervals cover calibration uncertainty only, not the sampling of nights', 'many histories to analyse and pool; harder to report', 'in occupancy, risk of counting local prevalence twice'],
      occ_rule='per draw: P(tp) ≥ <code>p_min</code> (<code>rule = "threshold"</code>), or <b>no threshold</b> (<code>rule = "sample"</code>)', occ_fn='<code>export_occupancy_data(fit = …)</code> → <code>occasion_draws()</code> → crywolf, one fit per draw, pooled', occ_unc=('u3', 'propagated'), occ_uncx='calibration + occupancy uncertainty (sd_within, sd_between); risk of counting local prevalence twice'),
]

def li(xs): return '<ul>' + ''.join(f'<li>{x}</li>' for x in xs) + '</ul>'
trs = []
for r in rows:
    if isinstance(r, tuple):
        trs.append(f'<tr class="grp"><td colspan="12">{r[1]}</td></tr>'); continue
    trs.append(f'''<tr>
<td class="route"><b>{r["name"]}</b><span class="tag {r["tag"][0]}">{r["tag"][1]}</span></td>
<td>{r["how"]}</td><td>{r["fn"]}</td><td>{r["needs"]}</td><td>{r["guar"]}</td>
<td><span class="unc {r["unc"][0]}">{r["unc"][1]}</span><br>{r["uncx"]}</td>
<td>{li(r["pros"])}</td><td>{li(r["cons"])}</td><td>{r["best"]}</td><td class="occ">{r["occ_rule"]}</td><td class="occ">{r["occ_fn"]}</td><td class="occ"><span class="unc {r["occ_unc"][0]}">{r["occ_unc"][1]}</span><br>{r["occ_uncx"]}</td></tr>''')
body = f'''<body><div class="wrap">
<header><span class="eyebrow">sheepdog</span><h1>Routes to detection histories and occupancy</h1>
<p class="lede">How the detections that count are chosen, what each route guarantees and what it does with uncertainty.</p></header>
<section class="stage st1"><div style="overflow-x:auto">
<table class="routes"><thead><tr><th>Route</th><th>A detection counts when…</th><th>Functions</th><th>Needs</th><th>Reliability guarantee</th><th>Uncertainty</th><th>Pros</th><th>Cons</th><th>Best for</th><th class="occ">Occupancy: detection rule</th><th class="occ">Occupancy: how</th><th class="occ">Occupancy: uncertainty</th></tr></thead>
<tbody>{"".join(trs)}</tbody></table></div>
<p class="tnote">In all nightly routes a night counts as detected when at least k detections count (k = 1, 2, 3 kept for sensitivity). Way 1 is equivalent to a model-based score threshold (<code>calibrated_thresholds()</code>, <code>thresholds.csv</code>). A practical check: build the Stage 1 and Stage 2 histories (or compare their thresholds); if they agree, report Stage 2. Occupancy (purple columns) always needs a random validation design: a <code>random_detections</code> draw at the <b>same</b> threshold as the occupancy analysis (observation-confirmation) and/or <code>random_recordings</code> (multiple methods); crywolf estimates the false-positive rate itself, so the threshold need not be perfect.</p>
</section>
<p class="src">sheepdog (R package) · github.com/diogoprov/sheepdog · provetelab.org/sheepdog · draft table.</p>
</div></body></html>'''
open(d + 'abstracts/routes_detection_histories.html', 'w').write(head + body)
print('ok routes')
