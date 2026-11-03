"""Build the website into the _site/ folder.

    python3 scripts/build.py      then open _site/index.html in a browser
"""

import shutil
from html import escape

from icons import topic_icon
from common import (PAUSED, ROOT, SECTIONS, copy_path, effective_status, load_resources,
                    load_site, load_status)

OUT = ROOT / "_site"

FONTS = ("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600"
         "&family=Figtree:wght@400;500;600&display=swap")

CSS = """
:root{
  --bg:#f3f2ed;--step:#e8e6de;--ink:#1b2523;--muted:#5b615d;--line:#cfccc2;
  --accent:#1c675c;--accent-ink:#fff;--warn:#8a5410;--warn-soft:#f1e3cc;
  --serif:"Fraunces",Georgia,serif;--sans:"Figtree",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
}
@media (prefers-color-scheme:dark){:root{
  --bg:#131716;--step:#1d2321;--ink:#e8e6e0;--muted:#a1a6a0;--line:#39403d;
  --accent:#7cc8b9;--accent-ink:#0f1f1c;--warn:#e2b56a;--warn-soft:#3a2f1e;
}}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;min-height:100vh;display:flex;flex-direction:column;background:var(--bg);color:var(--ink);font:16px/1.5 var(--sans);-webkit-font-smoothing:antialiased}
main{flex:1;width:100%}
header,.bar,footer{width:100%}
.wrap{max-width:1240px;margin-inline:auto;padding-inline:24px}

header.wrap{padding-top:44px;padding-bottom:20px}
h1{font:600 2rem/1.1 var(--serif);letter-spacing:-.02em;margin:0}
.sub{margin:.3rem 0 0;color:var(--muted);font-weight:500}
.sub .dot{margin:0 .45rem}
.intro{margin:.75rem 0 0;max-width:62ch}

.bar{position:sticky;top:0;z-index:5;background:var(--bg);transition:background .2s}
.bar.stuck{background:var(--step)}
.bar .wrap{display:flex;gap:12px;align-items:center;flex-wrap:wrap;padding-top:10px;padding-bottom:10px}
.tabs{display:inline-flex;background:var(--step);border-radius:999px;padding:4px}
.bar.stuck .tabs{background:var(--bg)}
.tab{font:600 1rem var(--sans);color:var(--muted);background:none;border:0;border-radius:999px;padding:.5rem 1.15rem;cursor:pointer;display:flex;align-items:center;gap:.5rem;transition:background .2s,color .2s,transform .12s}
.tab:hover{color:var(--ink)}
.tab:active{transform:scale(.97)}
.tab:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.tab[aria-selected=true]{background:var(--accent);color:var(--accent-ink)}
.search{flex:1;min-width:200px;max-width:380px;margin-left:auto;position:relative}
.search svg{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:var(--muted);pointer-events:none}
.search input{width:100%;font:inherit;padding:.6rem 1rem .6rem 2.5rem;border:1px solid var(--line);border-radius:999px;background:var(--bg);color:var(--ink);transition:border-color .2s}
.search input:focus{outline:2px solid var(--accent);outline-offset:1px;border-color:var(--accent)}

main.wrap{padding-top:20px;padding-bottom:56px}
.panel{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:36px 48px;align-items:start}
.panel[hidden]{display:none}
.group h2{font:600 1.2rem/1.25 var(--serif);letter-spacing:-.01em;margin:0 0 8px;display:flex;align-items:flex-start;gap:.6rem}
.ic{width:26px;height:26px;margin-top:-1px;flex:none;color:var(--accent);fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
ul{list-style:none;margin:0;padding:0}
li{padding:7px 0}
a{color:var(--accent)}
a.res{color:var(--ink);font-weight:600;text-decoration:underline;text-decoration-color:transparent;text-underline-offset:3px;text-decoration-thickness:1.5px;transition:color .2s,text-decoration-color .2s}
a.res:hover,a.res:focus-visible{color:var(--accent);text-decoration-color:currentColor}
.res.off{color:var(--muted);font-weight:600}
.meta{display:block;color:var(--muted);font-size:.875rem;margin-top:1px}
.meta a{color:var(--muted);white-space:nowrap;text-underline-offset:2px}
.meta a:hover{color:var(--accent)}
.meta .sep{margin:0 .4rem}
.note{display:block;font-size:.9rem;margin-top:2px}
.review{display:inline-block;font-size:.8rem;font-weight:600;color:var(--warn);background:var(--warn-soft);border-radius:999px;padding:.1rem .6rem;margin-left:6px}
.empty{color:var(--muted);text-align:center;padding:48px 0}
.empty button{font:inherit;color:var(--accent);background:none;border:0;text-decoration:underline;cursor:pointer;padding:0}
.hidden{display:none!important}

footer{background:var(--step);color:var(--muted);font-size:.875rem}
footer .wrap{display:grid;grid-template-columns:2fr 1fr;gap:32px;padding-top:24px;padding-bottom:36px}
footer p{margin:0}
@media (max-width:700px){
  header.wrap{padding-top:28px}
  h1{font-size:1.6rem}
  .search{max-width:none;margin-left:0;flex-basis:100%}
  .tabs{width:100%}.tab{flex:1;justify-content:center;padding:.5rem .6rem}
  .panel{gap:24px}
  footer .wrap{grid-template-columns:1fr;gap:12px}
}

@media (prefers-reduced-motion:no-preference){
  header>*{animation:rise .5s cubic-bezier(.2,.7,.2,1) both}
  header>*:nth-child(2){animation-delay:.07s}header>*:nth-child(3){animation-delay:.14s}
  .panel.enter .group h2{animation:rise .45s cubic-bezier(.2,.7,.2,1) both;animation-delay:calc(var(--i)*45ms)}
  .panel.enter .group li{animation:rise .45s cubic-bezier(.2,.7,.2,1) both;animation-delay:calc(var(--i)*45ms + 70ms)}
}
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@media print{.bar,.meta a{display:none}.panel{grid-template-columns:1fr 1fr}.panel[hidden]{display:grid!important}footer{background:none}}
"""

JS = """
(()=>{
const tabs=[...document.querySelectorAll('.tab')],panels=[...document.querySelectorAll('.panel')];
const q=document.getElementById('q'),empty=document.getElementById('empty'),bar=document.querySelector('.bar');
let cur=tabs[0].dataset.t;
function show(t,focus){
  cur=t;
  tabs.forEach(b=>{const on=b.dataset.t===t;b.setAttribute('aria-selected',on);b.tabIndex=on?0:-1;if(on&&focus)b.focus();});
  panels.forEach(p=>{const on=p.id===t;p.hidden=!on;if(on){p.classList.remove('enter');void p.offsetWidth;p.classList.add('enter');}});
  history.replaceState(null,'','#'+t);filter();
}
function filter(){
  const s=q.value.trim().toLowerCase(),counts={};
  panels.forEach(p=>{let n=0;
    p.querySelectorAll('li').forEach(li=>{const hit=!s||li.dataset.s.includes(s);li.classList.toggle('hidden',!hit);n+=hit;});
    p.querySelectorAll('.group').forEach(c=>c.classList.toggle('hidden',!c.querySelector('li:not(.hidden)')));
    counts[p.id]=n;});
  if(counts[cur]){empty.classList.add('hidden');return;}
  const other=Object.keys(counts).find(k=>k!==cur&&counts[k]);
  empty.innerHTML='No matches here.'+(other?` <button type="button">${counts[other]} found in ${document.querySelector('[data-t='+other+'] .l').textContent}</button>`:'');
  empty.classList.remove('hidden');
  const b=empty.querySelector('button');if(b)b.onclick=()=>show(other);
}
tabs.forEach((b,i)=>{b.onclick=()=>show(b.dataset.t);
  b.onkeydown=e=>{const d=e.key==='ArrowRight'?1:e.key==='ArrowLeft'?-1:0;if(d)show(tabs[(i+d+tabs.length)%tabs.length].dataset.t,true);};});
q.addEventListener('input',filter);
addEventListener('keydown',e=>{if(e.key==='/'&&document.activeElement!==q){e.preventDefault();q.focus();}});
new IntersectionObserver(([e])=>bar.classList.toggle('stuck',!e.isIntersecting)).observe(document.getElementById('top'));
const fromHash=()=>{const h=location.hash.slice(1);if(panels.some(p=>p.id===h)&&h!==cur)show(h);};
addEventListener('hashchange',fromHash);
const h=location.hash.slice(1);show(panels.some(p=>p.id===h)?h:cur);
})();
"""

SEARCH_ICON = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
               'stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/>'
               '<path d="m20 20-3.5-3.5"/></svg>')


def item_html(r, entry, files_used):
    rid = r["id"]
    st = effective_status(entry)
    has_copy = copy_path(rid).exists() and st != "withdrawn"
    title = escape(r["title"])
    meta = [escape(r["source"])] if r.get("source") else []
    if has_copy or entry.get("kind") == "pdf" or r["url"].lower().endswith(".pdf"):
        meta.append("PDF")
    review = ""

    if has_copy:
        files_used.append(rid)
        # PDFs are served from the approved saved copy, so they stay available
        # even if the original is changed or deleted.
        link = f'<a class="res" href="files/{rid}.pdf">{title}</a>'
        if st not in PAUSED:
            meta.append(f'<a href="{escape(r["url"])}" rel="noopener">Original ↗</a>')
    elif st in PAUSED or st == "withdrawn":
        link = f'<span class="res off">{title}</span>'
        review = '<span class="review" title="Temporarily unavailable while this resource is being reviewed">Under review</span>'
    else:
        link = f'<a class="res" href="{escape(r["url"])}" rel="noopener">{title}</a>'

    meta_html = f'<span class="meta">{"<span class=sep>·</span>".join(meta)}</span>' if meta else ""
    note = f'<span class="note">{escape(r["note"])}</span>' if r.get("note") else ""
    search = escape(" ".join([r["topic"], r["title"], r.get("source", ""), r.get("note", "")]).lower())
    return f'<li data-s="{search}">{link}{review}{meta_html}{note}</li>'


def main():
    site = load_site()
    resources = load_resources()
    status = load_status()
    files_used = []

    tabs, panels = [], []
    for key, heading in SECTIONS.items():
        items = [r for r in resources if r["section"] == key]
        if not items:
            continue
        tabs.append(f'<button class="tab" role="tab" id="tab-{key}" data-t="{key}" aria-controls="{key}">'
                    f'<span class="l">{heading}</span></button>')
        groups = []
        for i, topic in enumerate(dict.fromkeys(r["topic"] for r in items)):
            in_topic = [r for r in items if r["topic"] == topic]
            lis = "".join(item_html(r, status.get(r["id"], {}), files_used) for r in in_topic)
            groups.append(f'<section class="group" style="--i:{min(i, 12)}">'
                          f'<h2>{topic_icon(topic, in_topic)}{escape(topic)}</h2><ul>{lis}</ul></section>')
        panels.append(f'<div class="panel" id="{key}" role="tabpanel" aria-labelledby="tab-{key}">{"".join(groups)}</div>')

    checked = [e["last_checked"] for e in status.values() if e.get("last_checked")]
    checked_line = f" Links checked daily; last checked {max(checked)[:10]}." if checked else ""
    sub = escape(site["subtitle"])
    if site.get("clinic"):
        sub += f'<span class="dot">•</span>{escape(site["clinic"])}'

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(site["name"])} – Patient Resources</title>
<meta name="description" content="{escape(site["intro"])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<style>{CSS}</style>
</head>
<body>
<header class="wrap" id="top">
<h1>{escape(site["name"])}</h1>
<p class="sub">{sub}</p>
<p class="intro">{escape(site["intro"])}</p>
</header>
<div class="bar"><div class="wrap">
<div class="tabs" role="tablist" aria-label="Resource type">{"".join(tabs)}</div>
<label class="search">{SEARCH_ICON}<input id="q" type="search" placeholder="Search resources" aria-label="Search resources" autocomplete="off"></label>
</div></div>
<main class="wrap">
{"".join(panels)}
<p class="empty hidden" id="empty" aria-live="polite"></p>
</main>
<footer><div class="wrap">
<p>{escape(site["disclaimer"])}</p>
<p>Links open websites run by other organizations.{checked_line}</p>
</div></footer>
<script>{JS}</script>
</body>
</html>
"""
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "files").mkdir(parents=True)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    for rid in files_used:
        shutil.copy2(copy_path(rid), OUT / "files" / f"{rid}.pdf")
    print(f"Built {OUT / 'index.html'} ({len(resources)} resources, {len(files_used)} saved PDFs)")


if __name__ == "__main__":
    main()
