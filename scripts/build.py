"""Build the website into the _site/ folder.

    python3 scripts/build.py      then open _site/index.html in a browser
"""

import shutil
from html import escape

from icons import topic_icon
from common import (PAUSED, ROOT, SECTIONS, copy_path, effective_status, load_resources,
                    load_site, load_status)

OUT = ROOT / "_site"

CSS = """
:root{
  --bg:#fff;--panel:#f3f4f6;--ink:#111;--muted:#5f6368;--line:#d9dbdf;--sel:#e7e9ec;
  --accent:#0b6e8a;--warn:#8a5a00;--warn-soft:#fff4d6;--radius:10px;
}
@media (prefers-color-scheme:dark){:root{
  --bg:#111;--panel:#1c1c1c;--ink:#f2f2f2;--muted:#b4b4b4;--line:#333;--sel:#2a2a2a;
  --accent:#4cb4d2;--warn:#f5c15a;--warn-soft:#3a2f12;
}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;min-height:100dvh;display:flex;flex-direction:column;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
a{color:var(--ink);text-underline-offset:2px}
.hidden{display:none!important}
.in{width:100%;max-width:1180px;margin:0 auto;padding-inline:16px}

.hero .in{padding-top:48px;padding-bottom:28px}
h1{font-size:clamp(2.5rem,5vw,4.5rem);font-weight:700;line-height:1.05;letter-spacing:-.03em;margin:0}
.sub{margin:.5rem 0 0;font-size:1.125rem;font-weight:600}
.sub .dot{margin:0 .4rem}
.intro{margin:.25rem 0 0;font-size:1.125rem;color:var(--muted);max-width:60ch}

.top{position:sticky;top:0;z-index:20;background:var(--panel)}
.top .in{display:flex;align-items:center;gap:18px;min-height:52px;flex-wrap:wrap}
.tabs{display:flex;gap:2px;flex:1}
.tab{font:inherit;font-weight:500;color:var(--muted);background:none;border:0;border-bottom:2px solid transparent;padding:14px 12px 12px;cursor:pointer;white-space:nowrap;transition:color .15s}
.tab:hover{color:var(--ink)}
.tab:active{transform:translateY(1px)}
.tab[aria-selected=true]{color:var(--ink);border-color:var(--ink)}
.tab:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.search{position:relative;width:280px}
.search svg{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:var(--muted);pointer-events:none}
.search input{width:100%;font:inherit;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:8px 10px 8px 32px;min-height:40px}
.search input:focus{outline:2px solid var(--accent);outline-offset:-1px}

main{flex:1;width:100%;max-width:1180px;margin:0 auto;padding:24px 16px 64px}
.panel{columns:3 320px;column-gap:16px}
.panel[hidden]{display:none}
.group{break-inside:avoid;background:var(--panel);border-radius:var(--radius);padding:16px 0 10px;overflow:hidden;margin-bottom:16px}
.group h2{font-size:1.125rem;line-height:1.3;margin:0 16px 6px;display:flex;align-items:center;gap:8px}
.ic{width:20px;height:20px;flex:none;color:var(--muted);fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
ul{list-style:none;margin:0;padding:0}
li{position:relative;padding:8px 16px;transition:background .15s}
li:has(a.res):hover{background:var(--sel)}
a.res{font-weight:600;text-decoration:none}
/* the whole row opens the resource */
a.res::after{content:"";position:absolute;inset:0}
a.res:hover{text-decoration:underline}
a.res:focus-visible{outline:none}
a.res:focus-visible::after{outline:2px solid var(--accent);outline-offset:-2px}
.res.off{color:var(--muted);font-weight:600}
.meta{display:block;color:var(--muted);font-size:.9375rem}
.meta a{position:relative;z-index:1;color:var(--muted);white-space:nowrap;text-decoration:none;padding:8px 0}
.meta a:hover{color:var(--ink);text-decoration:underline}
.meta .sep{margin:0 .35rem}
.note{display:block;font-size:.9375rem;margin-top:2px}
.review{display:inline-block;font-size:.8125rem;font-weight:600;padding:2px 9px;border-radius:99px;background:var(--warn-soft);color:var(--warn);margin-left:6px}
.empty{color:var(--muted);text-align:center;padding:40px 0}
.empty button{position:relative;font:inherit;color:var(--accent);background:none;border:0;text-decoration:underline;cursor:pointer;padding:0}

footer{background:var(--panel);color:var(--muted)}
footer .in{display:grid;grid-template-columns:2fr 1fr;gap:24px;padding-top:18px;padding-bottom:28px}
footer p{margin:0;max-width:62ch}
@media (max-width:760px){
  .hero .in{padding-top:32px;padding-bottom:20px}
  .top .in{gap:0;padding-bottom:10px}
  .tabs{flex:1 0 100%;overflow-x:auto;margin-inline:-10px}
  .tab{padding:13px 10px 11px}
  .search{width:100%}
  .search input{min-height:44px}
  footer .in{grid-template-columns:1fr;gap:10px}
}
@media (prefers-reduced-motion:no-preference){
  /* replays on every tab switch, because a panel's cards restart when it is shown */
  .hero .in>*,.panel .group,.panel li{animation:rise .45s cubic-bezier(.2,.7,.2,1) both}
  .panel li{animation-delay:120ms}
  .hero .in>:nth-child(2){animation-delay:70ms}
  .hero .in>:nth-child(3){animation-delay:140ms}
  .panel .group:nth-child(2){animation-delay:60ms}
  .panel .group:nth-child(3){animation-delay:120ms}
  .panel .group:nth-child(4){animation-delay:180ms}
  .panel .group:nth-child(n+5){animation-delay:240ms}
}
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@media print{.top,.meta a{display:none}.panel[hidden]{display:block!important}.panel{columns:2}}
"""

JS = """
(()=>{
const tabs=[...document.querySelectorAll('.tab')],panels=[...document.querySelectorAll('.panel')];
const q=document.getElementById('q'),empty=document.getElementById('empty');
let cur=tabs[0].dataset.t;
function show(t,focus){
  cur=t;
  tabs.forEach(b=>{const on=b.dataset.t===t;b.setAttribute('aria-selected',on);b.tabIndex=on?0:-1;if(on&&focus)b.focus();});
  panels.forEach(p=>{p.hidden=p.dataset.p!==t;});
  history.replaceState(null,'','#'+t);filter();
}
function filter(){
  const s=q.value.trim().toLowerCase(),counts={};
  panels.forEach(p=>{let n=0;
    p.querySelectorAll('li').forEach(li=>{const hit=!s||li.dataset.s.includes(s);li.classList.toggle('hidden',!hit);n+=hit;});
    p.querySelectorAll('.group').forEach(c=>c.classList.toggle('hidden',!c.querySelector('li:not(.hidden)')));
    counts[p.dataset.p]=n;});
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
// Old links to #patients open the adults tab.
const hashTab=()=>{const h=location.hash.slice(1);return h==='patients'?'adults':h;};
const fromHash=()=>{const h=hashTab();if(panels.some(p=>p.dataset.p===h)&&h!==cur)show(h);};
addEventListener('hashchange',fromHash);
const h=hashTab();show(panels.some(p=>p.dataset.p===h)?h:cur);
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
        items = [r for r in resources if key in r["sections"]]
        if not items:
            continue
        tabs.append(f'<button class="tab" role="tab" id="tab-{key}" data-t="{key}" aria-controls="panel-{key}">'
                    f'<span class="l">{heading}</span></button>')
        groups = []
        for topic in dict.fromkeys(r["topic"] for r in items):
            in_topic = [r for r in items if r["topic"] == topic]
            lis = "".join(item_html(r, status.get(r["id"], {}), files_used) for r in in_topic)
            groups.append(f'<section class="group">'
                          f'<h2>{topic_icon(topic, in_topic)}{escape(topic)}</h2><ul>{lis}</ul></section>')
        panels.append(f'<div class="panel" id="panel-{key}" data-p="{key}" role="tabpanel" aria-labelledby="tab-{key}">{"".join(groups)}</div>')

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
<style>{CSS}</style>
</head>
<body>
<header class="hero"><div class="in">
<h1>{escape(site["name"])}</h1>
<p class="sub">{sub}</p>
<p class="intro">{escape(site["intro"])}</p>
</div></header>
<div class="top"><div class="in">
<div class="tabs" role="tablist" aria-label="Resource type">{"".join(tabs)}</div>
<label class="search">{SEARCH_ICON}<input id="q" type="search" placeholder="Search resources" aria-label="Search resources" autocomplete="off"></label>
</div></div>
<main>
{"".join(panels)}
<p class="empty hidden" id="empty" aria-live="polite"></p>
</main>
<footer><div class="in">
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
