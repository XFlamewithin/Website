"""Build the website into the _site/ folder.

    python3 scripts/build.py      then open _site/index.html in a browser
"""

import shutil
from html import escape

from common import (PAUSED, ROOT, SECTIONS, copy_path, load_resources, load_site,
                    load_status)

OUT = ROOT / "_site"

CSS = """
:root{--bg:#fff;--fg:#1d2327;--muted:#5f6b73;--link:#0b5cad;--line:#e3e7ea;--soft:#f4f6f8;--warn:#8a5a00}
@media (prefers-color-scheme:dark){:root{--bg:#15191c;--fg:#e8ecef;--muted:#9aa6ae;--link:#7ab7ff;--line:#2b3237;--soft:#1d2226;--warn:#e0b45c}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:18px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:46rem;margin:0 auto;padding:2.5rem 1rem 3rem}
header h1{margin:0;font-size:1.9rem;line-height:1.2}
.sub{margin:.2rem 0 0;color:var(--muted)}
.intro{margin:1.25rem 0}
nav{display:flex;gap:.5rem;flex-wrap:wrap;margin:1rem 0}
nav a{padding:.35rem .8rem;border:1px solid var(--line);border-radius:999px;text-decoration:none}
input[type=search]{width:100%;font:inherit;padding:.6rem .8rem;border:1px solid var(--line);border-radius:8px;background:var(--soft);color:var(--fg)}
h2{margin:2.5rem 0 .5rem;padding-bottom:.3rem;border-bottom:2px solid var(--line);font-size:1.4rem}
h3{margin:1.6rem 0 .3rem;font-size:1.1rem}
ul{list-style:none;margin:0;padding:0}
li{padding:.45rem 0;border-bottom:1px solid var(--line)}
a{color:var(--link)}
a.res{font-weight:600;text-underline-offset:3px}
.meta,.note{color:var(--muted);font-size:.88rem}
.note{display:block}
.tag{font-size:.72rem;font-weight:700;letter-spacing:.04em;color:var(--muted);border:1px solid var(--line);border-radius:4px;padding:0 .3rem;margin-left:.3rem;vertical-align:2px}
.paused{color:var(--warn);font-size:.88rem;display:block}
.alt{font-size:.85rem;margin-left:.4rem}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);color:var(--muted);font-size:.85rem}
.hidden{display:none}
@media print{nav,input,.alt{display:none}a{color:inherit}a.res::after{content:" – " attr(href);font-weight:400;font-size:.8rem;word-break:break-all}}
"""

JS = """
const q=document.getElementById('q');
q.addEventListener('input',()=>{const t=q.value.trim().toLowerCase();
document.querySelectorAll('[data-s]').forEach(li=>li.classList.toggle('hidden',t&&!li.dataset.s.includes(t)));
document.querySelectorAll('.topic,section').forEach(g=>g.classList.toggle('hidden',!g.querySelector('li:not(.hidden)')));});
"""


def item_html(r, entry, files_used):
    rid = r["id"]
    st = entry.get("status", "unchecked")
    has_copy = copy_path(rid).exists()
    is_pdf = has_copy or entry.get("kind") == "pdf" or r["url"].lower().endswith(".pdf")
    title = escape(r["title"])
    extras = []

    if has_copy:
        files_used.append(rid)
        local = f"files/{rid}.pdf"
        # PDFs are served from the approved saved copy, so they stay available
        # even if the original is changed or deleted.
        link = f'<a class="res" href="{local}">{title}</a>'
        if st not in PAUSED:
            extras.append(f'<a class="alt" href="{escape(r["url"])}" rel="noopener">original source</a>')
    elif st in PAUSED:
        link = f'<span class="res">{title}</span>'
        extras.append('<span class="paused">Temporarily unavailable while this resource is being reviewed.</span>')
    else:
        link = f'<a class="res" href="{escape(r["url"])}" rel="noopener">{title}</a>'

    tag = '<span class="tag">PDF</span>' if is_pdf else ""
    meta = f' <span class="meta">— {escape(r["source"])}</span>' if r.get("source") else ""
    note = f'<span class="note">{escape(r["note"])}</span>' if r.get("note") else ""
    search = escape(" ".join([r["topic"], r["title"], r.get("source", ""), r.get("note", "")]).lower())
    return f'<li data-s="{search}">{link}{tag}{meta}{"".join(extras)}{note}</li>'


def main():
    site = load_site()
    resources = load_resources()
    status = load_status()
    files_used = []

    body = []
    for key, heading in SECTIONS.items():
        items = [r for r in resources if r["section"] == key]
        if not items:
            continue
        body.append(f'<section id="{key}"><h2>{heading}</h2>')
        topics = list(dict.fromkeys(r["topic"] for r in items))
        for topic in topics:
            lis = "".join(item_html(r, status.get(r["id"], {}), files_used)
                          for r in items if r["topic"] == topic)
            body.append(f'<div class="topic"><h3>{escape(topic)}</h3><ul>{lis}</ul></div>')
        body.append("</section>")

    checked = [e["last_checked"] for e in status.values() if e.get("last_checked")]
    checked_line = f" Links last checked {max(checked)[:10]}." if checked else ""
    clinic = f'<p class="sub">{escape(site["clinic"])}</p>' if site.get("clinic") else ""
    nav = "".join(f'<a href="#{k}">{v}</a>' for k, v in SECTIONS.items()
                  if any(r["section"] == k for r in resources))

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
<main>
<header>
<h1>{escape(site["name"])}</h1>
<p class="sub">{escape(site["subtitle"])}</p>
{clinic}
</header>
<p class="intro">{escape(site["intro"])}</p>
<nav>{nav}</nav>
<input id="q" type="search" placeholder="Search resources…" aria-label="Search resources">
{"".join(body)}
<footer><p>{escape(site["disclaimer"])}</p><p>Links open websites run by other organizations.{checked_line}</p></footer>
</main>
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
