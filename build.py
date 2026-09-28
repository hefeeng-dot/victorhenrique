#!/usr/bin/env python3
"""Gera o site de iscas a partir de content/*.json.

Uso:
  python3 build.py            # gera index.html e uma pasta por código (ex.: /4tqzc/index.html)
  python3 build.py --drafts   # inclui itens marcados com "draft": true

Para criar uma isca nova: copie um arquivo de content/, troque o conteúdo e rode o build.
"""
import json, glob, os, sys, html, shutil
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
INCLUDE_DRAFTS = "--drafts" in sys.argv
E = html.escape

site = json.load(open(os.path.join(ROOT, "site.json"), encoding="utf-8"))

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&display=swap" rel="stylesheet">')

def head(title, accent, css_href):
    robots = '<meta name="robots" content="noindex,nofollow">' if site.get("noindex") else ""
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">{robots}'
            f'<title>{E(title)}</title>{FONTS}<link rel="stylesheet" href="{css_href}">'
            f'<style>:root{{--accent:{accent}}}</style></head><body><div class="wrap">')

def fmt_date(iso):
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d/%m/%Y")

def render_item(it):
    cls = "card draft" if it.get("draft") else "card"
    out = [f'<section class="{cls}"><h2>{E(it["name"])}</h2>']
    if it.get("url"):
        out.append(f'<a class="btn" href="{E(it["url"])}" target="_blank" rel="noopener">{E(it["url"].replace("https://",""))} ↗</a>')
    for s in it.get("sections", []):
        w = " warn" if s.get("warn") else ""
        out.append(f'<div class="sec{w}"><b>{E(s["label"])}</b>{E(s["text"])}</div>')
    if it.get("prompt"):
        out.append(f'<pre>{E(it["prompt"])}</pre><button class="copy" type="button">Copiar prompt</button>')
    out.append("</section>")
    return "".join(out)

JS = ('<script>document.querySelectorAll(".copy").forEach(function(b){b.addEventListener("click",function(){'
      'var t=b.previousElementSibling.innerText;navigator.clipboard.writeText(t).then(function(){'
      'var o=b.textContent;b.textContent="Copiado!";setTimeout(function(){b.textContent=o},1500)})})});</script>')

pages = []
for path in sorted(glob.glob(os.path.join(ROOT, "content", "*.json"))):
    data = json.load(open(path, encoding="utf-8"))
    items = [i for i in data["items"] if INCLUDE_DRAFTS or not i.get("draft")]
    skipped = [i["name"] for i in data["items"] if i.get("draft") and not INCLUDE_DRAFTS]
    if skipped:
        print(f'  aviso: {data["code"]}: itens em rascunho fora da página -> {", ".join(skipped)}')
    slug = data["code"].lower()
    accent = data.get("accent", "#6B8F71")
    h = [head(f'{data["title"]} — {site["handle"]}', accent, "../assets/style.css")]
    h.append(f'<div class="top"><a href="../">← todas as iscas</a><span>{E(site["handle"])}</span></div>')
    h.append(f'<span class="chip">{E(data["code"])}</span><h1>{E(data["title"])}</h1>')
    h.append(f'<p class="lead">{E(data["intro"])}</p>')
    meta = f'Post de {fmt_date(data["date"])}'
    if data.get("verified"):
        meta += f' · links verificados em {E(data["verified"])}'
    h.append(f'<div class="meta">{meta}</div>')
    h.extend(render_item(i) for i in items)
    if data.get("closing"):
        h.append(f'<p class="closing">{E(data["closing"])}</p>')
    h.append(f'<div class="foot">Salva esse link pra usar depois. · {E(site["handle"])}</div></div>{JS}</body></html>')
    outdir = os.path.join(ROOT, slug)
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write("".join(h))
    pages.append({**data, "slug": slug})
    print(f'  ok: /{slug}/')

pages.sort(key=lambda p: p["date"], reverse=True)
h = [head(site["site_title"], "#6B8F71", "assets/style.css")]
h.append(f'<div class="top"><span>{E(site["handle"])}</span><span></span></div>')
h.append(f'<h1>Iscas</h1><p class="lead">{E(site["site_intro"])}</p><div class="meta">{len(pages)} iscas</div><div class="grid">')
for p in pages:
    h.append(f'<a class="tile" href="{p["slug"]}/" style="--accent:{p.get("accent","#6B8F71")}">'
             f'<span class="chip" style="background:{p.get("accent","#6B8F71")}">{E(p["code"])}</span>'
             f'<h2>{E(p["title"])}</h2><p>{E(p["summary"])}</p><small>{fmt_date(p["date"])}</small></a>')
h.append(f'</div><div class="foot">{E(site["handle"])}</div></div></body></html>')
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write("".join(h))
print("  ok: /  (index)")

open(os.path.join(ROOT, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n" if site.get("noindex") else "User-agent: *\nAllow: /\n")
