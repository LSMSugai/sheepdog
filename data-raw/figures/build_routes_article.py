"""Narrow version of the routes figure for a pkgdown article: four route cards in a 2 x 2 grid."""
import os, re
d = os.path.dirname(os.path.abspath(__file__)) + '/'
src = open(d + 'routes_data.py').read()
ns = {'__file__': d + 'routes_data.py'}
exec(src[:src.index('def li(xs)')], ns)
rows = [r for r in ns['rows'] if isinstance(r, dict)]
from routes_graphics import GRAPHICS

s1 = open(d + 'abstracts/1_stage1_validation.html').read()
head = re.sub(r'<title>.*?</title>', '<title>sheepdog Routes</title>', s1[:s1.index('<body>')])

names = [("A", "empirical threshold", "Figure 2 · route A", "st1"),
         ("B · way 1", "probability cut", "Figure 4 · step 6", "st2"),
         ("B · way 2", "probability cut with certainty", "Figure 4 · step 6 (brms)", "st2"),
         ("B · way 3", "one history per draw", "Figure 4 · step 6 (brms)", "st2")]
how = {0: "score ≥ the empirical threshold of the cell (<code>review_support()</code>); history built by hand",
       1: rows[1]["how"] + "; <code>detection_history(rule = \"mean\")</code>",
       2: rows[2]["how"] + "; <code>detection_history(rule = \"probability\")</code>",
       3: rows[3]["how"] + "; <code>history_draws()</code>"}

css = '''<style>
.wrap{max-width:820px}
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 14px 12px;display:flex;flex-direction:column;gap:8px;--c:var(--s1);--soft:var(--s1-soft)}
.card.st2{--c:var(--s2);--soft:var(--s2-soft)}
.card .top{background:var(--soft);border:1.5px solid var(--c);border-radius:9px;padding:8px 10px}
.card .top b{font-weight:400;font-size:17px;color:var(--c)} .card .top span{font:11.5px/1 var(--mono);color:var(--c);margin-left:8px}
.card .top small{display:block;font-size:12px;color:var(--muted);margin-top:4px}
.card svg{display:block;width:100%;height:auto}
.card h4{margin:2px 0 0;font:11px/1.2 var(--mono);text-transform:uppercase;letter-spacing:.05em;color:var(--muted);font-weight:400}
.card p{margin:0;font-size:13px;line-height:1.45;color:var(--ink)}
.card code{font-family:var(--mono);font-size:11.5px;color:var(--c)}
.unc{display:inline-block;font:11px/1 var(--mono);padding:3px 6px;border-radius:5px;margin-right:4px}
.u0{background:var(--line);color:var(--ink)} .u1{background:var(--s1-soft);color:var(--s1)} .u2{background:var(--s2-soft);color:var(--s2)} .u3{background:var(--s3-soft);color:var(--s3)}
@media (max-width:640px){.cards{grid-template-columns:minmax(0,1fr)}}
</style>'''
head = head.replace('</head>', css + '</head>')

cards = []
for i, (r, (nm, tag, ref, st)) in enumerate(zip(rows, names)):
    cards.append(f'''<div class="card {st}">
<div class="top"><b>{nm}</b><span>{tag}</span><small>needs: {r["needs"]} · {ref}</small></div>
{GRAPHICS[i]}
<h4>Reliability guarantee</h4><p>{r["guar"]}</p>
<h4>A detection counts when…</h4><p>{how[i]}</p>
<h4>Uncertainty</h4><p><span class="unc {r["unc"][0]}">{r["unc"][1]}</span>{r["uncx"]}</p>
<h4>Best for</h4><p>{r["best"]}</p>
</div>''')

body = f'''<body><div class="wrap">
<header><span class="eyebrow">sheepdog</span><h1 style="font-size:32px">Four routes to a detection history</h1>
<p class="lede">From the same reviewed clips: an empirical threshold (A) or the calibration (B, three ways). In all, a night counts when at least k detections count.</p></header>
<section class="stage st1"><div class="cards">{"".join(cards)}</div></section>
<p class="src">sheepdog (R package) · values in the drawings are illustrative.</p>
</div></body></html>'''
open(d + 'abstracts/routes_article.html', 'w').write(head + body)
print('ok routes article')
