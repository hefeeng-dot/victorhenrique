#!/usr/bin/env python3
"""Gera o site (Biblioteca) a partir de content/*.json.

Uso:
  python3 build.py            # gera index.html e uma pasta por código (ex.: /4tqzc/index.html)
  python3 build.py --drafts   # inclui itens marcados com "draft": true

Para criar uma página nova: copie um arquivo de content/, troque o conteúdo e rode o build.
Internamente os arquivos continuam sendo "iscas"; para o público o nome é "Biblioteca".
"""
import json, glob, os, sys, html
from datetime import datetime
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
INCLUDE_DRAFTS = "--drafts" in sys.argv
E = html.escape
DEFAULT_ACCENT = "#6B8F71"

site = json.load(open(os.path.join(ROOT, "site.json"), encoding="utf-8"))
HANDLE = site["handle"]
LIB = site.get("library_name", "Biblioteca")

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800'
         '&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">')

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='8' fill='%230B0B0F'/%3E"
           "%3Ccircle cx='16' cy='16' r='6' fill='%23FF7A1A'/%3E%3C/svg%3E")


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lighten(h, amount):
    """Mistura a cor com branco: as cores dos posts são pensadas para fundo claro."""
    r, g, b = (round(c + (255 - c) * amount) for c in hex_to_rgb(h))
    return f"#{r:02x}{g:02x}{b:02x}"


def accent_vars(accent):
    r, g, b = hex_to_rgb(accent)
    return f"--accent:{accent};--accent-hi:{lighten(accent, .35)};--accent-rgb:{r},{g},{b}"


def head(title, description, accent, css_href):
    robots = '<meta name="robots" content="noindex,nofollow">' if site.get("noindex") else ""
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">{robots}'
            f'<meta name="theme-color" content="#0B0B0F">'
            f'<title>{E(title)}</title><meta name="description" content="{E(description)}">'
            f'<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}">'
            f'<link rel="icon" href="{FAVICON}">{FONTS}<link rel="stylesheet" href="{css_href}">'
            f'<style>:root{{{accent_vars(accent)}}}</style>'
            f'<script>document.documentElement.classList.add("js")</script></head><body>'
            f'<div class="glow" aria-hidden="true"></div>')


def nav(root, current=None):
    """root: caminho até a raiz do site ("./" ou "../"). current: "lib", "links" ou None."""
    def link(key, href, label):
        if current == key:
            return f'<span class="nav-link is-current">{E(label)}</span>'
        return f'<a class="nav-link" href="{href}">{E(label)}</a>'
    return (f'<header class="nav"><div class="nav-in">'
            f'<a class="brand" href="{root}"><span class="dot"></span>{E(HANDLE)}</a>'
            f'<nav class="nav-links">{link("lib", root, LIB)}{link("links", root + "links/", "Links")}</nav>'
            f'</div></header>')


ICONS = {
    "instagram": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6" fill="currentColor"/>',
    "tiktok": '<path d="M14 3v11.5a3.5 3.5 0 1 1-3.5-3.5M14 3c.4 2.6 2.2 4.4 5 4.6"/>',
    "youtube": '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="m10 9.5 5 2.5-5 2.5z" fill="currentColor"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="m4 7 8 6 8-6"/>',
    "library": '<path d="M5 4h4v16H5zM10 4h4v16h-4zM15.5 5l3.8-1 3 15.4-3.8 1z"/>',
    "link": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
}


def icon(name):
    return (f'<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS.get(name, ICONS["link"])}</svg>')


def fmt_date(iso):
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d/%m/%Y")


def domain(url):
    u = urlparse(url)
    host = u.netloc or url
    host = host[4:] if host.startswith("www.") else host
    if host == "github.com" and u.path.strip("/"):
        return u.path.strip("/")  # mostra dono/repo, que é o que identifica o projeto
    return host


WARN_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 2 21h20L12 3Z" fill="none" '
             'stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M12 10v5M12 18h.01" '
             'stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>')
ARROW = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M9 7h8v8" fill="none" '
         'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def render_section_body(s):
    """Uma seção pode ter texto, lista ("list") e blocos de código copiáveis ("code")."""
    out = []
    if s.get("text"):
        out.append(f'<p>{E(s["text"])}</p>')
    if s.get("list"):
        out.append('<ul class="bullets">' + "".join(f'<li>{E(x)}</li>' for x in s["list"]) + '</ul>')
    for c in s.get("code", []):
        if c.get("caption"):
            out.append(f'<p class="caption">{E(c["caption"])}</p>')
        out.append(f'<div class="codeblock"><pre>{E(c["code"])}</pre>'
                   f'<button class="copy" type="button">Copiar</button></div>')
    return "".join(out)


def render_item(it, n):
    cls = "item reveal draft" if it.get("draft") else "item reveal"
    out = [f'<article class="{cls}"><div class="item-head"><span class="num">{n:02d}</span>'
           f'<h2>{E(it["name"])}</h2>']
    if it.get("url"):
        out.append(f'<a class="visit" href="{E(it["url"])}" target="_blank" rel="noopener">'
                   f'<span>{E(domain(it["url"]))}</span>{ARROW}</a>')
    out.append('</div>')
    if it.get("chips"):
        out.append('<ul class="chips">' + "".join(f'<li>{E(c)}</li>' for c in it["chips"]) + '</ul>')
    out.append('<div class="item-body">')
    for s in it.get("sections", []):
        body = render_section_body(s)
        if s.get("warn"):
            out.append(f'<div class="sec warn">{WARN_ICON}<div><b>{E(s["label"])}</b>{body}</div></div>')
        else:
            out.append(f'<div class="sec"><b>{E(s["label"])}</b>{body}</div>')
    if it.get("prompt"):
        out.append(f'<div class="prompt"><div class="prompt-bar"><span>Prompt</span>'
                   f'<button class="copy" type="button">Copiar</button></div>'
                   f'<pre>{E(it["prompt"])}</pre></div>')
    out.append("</div></article>")
    return "".join(out)


JS = """<script>
(function(){
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var els = document.querySelectorAll(".reveal");
  if (reduce || !("IntersectionObserver" in window)) {
    els.forEach(function(e){ e.classList.add("in"); });
  } else {
    var vh = window.innerHeight || document.documentElement.clientHeight;
    els.forEach(function(e){ if (e.getBoundingClientRect().top < vh) e.classList.add("in"); });
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(en){ if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, {rootMargin: "0px 0px -8% 0px"});
    els.forEach(function(e){ if (!e.classList.contains("in")) io.observe(e); });
  }
  document.querySelectorAll(".item, .tile, .link-row").forEach(function(c){
    c.addEventListener("pointermove", function(ev){
      var r = c.getBoundingClientRect();
      c.style.setProperty("--mx", (ev.clientX - r.left) + "px");
      c.style.setProperty("--my", (ev.clientY - r.top) + "px");
    });
  });
  document.querySelectorAll(".copy").forEach(function(b){
    b.addEventListener("click", function(){
      var t = b.closest(".prompt, .codeblock").querySelector("pre").innerText;
      navigator.clipboard.writeText(t).then(function(){
        b.textContent = "Copiado ✓"; b.classList.add("ok");
        setTimeout(function(){ b.textContent = "Copiar"; b.classList.remove("ok"); }, 1600);
      });
    });
  });
  var bar = document.querySelector(".progress span");
  if (bar) {
    var upd = function(){
      var h = document.documentElement, max = h.scrollHeight - h.clientHeight;
      bar.style.transform = "scaleX(" + (max > 0 ? h.scrollTop / max : 0) + ")";
    };
    document.addEventListener("scroll", upd, {passive: true}); upd();
  }
  var q = document.querySelector("#q");
  if (q) {
    var tiles = document.querySelectorAll(".tile"), empty = document.querySelector(".empty");
    q.addEventListener("input", function(){
      var v = q.value.trim().toLowerCase(), shown = 0;
      tiles.forEach(function(t){
        var hit = !v || t.dataset.search.indexOf(v) > -1;
        t.hidden = !hit; if (hit) shown++;
      });
      empty.hidden = shown > 0;
    });
  }
})();
</script>"""

FOOT = (f'<footer class="foot"><span>{E(HANDLE)}</span>'
        f'<span>Salve este link para consultar depois.</span></footer>')

pages = []
for path in sorted(glob.glob(os.path.join(ROOT, "content", "*.json"))):
    data = json.load(open(path, encoding="utf-8"))
    items = [i for i in data["items"] if INCLUDE_DRAFTS or not i.get("draft")]
    skipped = [i["name"] for i in data["items"] if i.get("draft") and not INCLUDE_DRAFTS]
    if skipped:
        print(f'  aviso: {data["code"]}: itens em rascunho fora da página -> {", ".join(skipped)}')
    slug = data["code"].lower()
    accent = data.get("accent", DEFAULT_ACCENT)
    count = len(items)

    h = [head(f'{data["title"]} · {LIB} {HANDLE}', data["summary"], accent, "../assets/style.css")]
    h.append('<div class="progress" aria-hidden="true"><span></span></div>')
    h.append(nav("../"))
    h.append('<main class="wrap">')
    h.append(f'<section class="hero reveal"><span class="code">#{E(data["code"])}</span>'
             f'<h1>{E(data["title"])}</h1><p class="lead">{E(data["intro"])}</p>'
             f'<ul class="meta"><li>{count} {"item" if count == 1 else "itens"}</li>'
             f'<li>Publicado em {fmt_date(data["date"])}</li>')
    if data.get("verified"):
        h.append(f'<li class="ok">Links conferidos em {E(data["verified"])}</li>')
    h.append('</ul></section><div class="items">')
    h.extend(render_item(it, n) for n, it in enumerate(items, 1))
    h.append('</div>')
    if data.get("closing"):
        h.append(f'<aside class="closing reveal">{E(data["closing"])}</aside>')
    h.append(f'<a class="back reveal" href="../">Ver tudo na {E(LIB)} →</a>')
    h.append(f'{FOOT}</main>{JS}</body></html>')

    outdir = os.path.join(ROOT, slug)
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write("".join(h))
    pages.append({**data, "slug": slug, "count": count})
    print(f'  ok: /{slug}/')

pages.sort(key=lambda p: p["date"], reverse=True)
h = [head(site["site_title"], site["site_intro"], "#FF7A1A", "assets/style.css")]
h.append(nav("./", "lib"))
h.append('<main class="wrap">')
h.append(f'<section class="hero reveal"><span class="code">{E(HANDLE)}</span>'
         f'<h1>{E(LIB)}</h1><p class="lead">{E(site["site_intro"])}</p>'
         f'<label class="search"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" '
         f'fill="none" stroke="currentColor" stroke-width="2"/><path d="m20 20-3.5-3.5" stroke="currentColor" '
         f'stroke-width="2" stroke-linecap="round"/></svg><input id="q" type="search" autocomplete="off" '
         f'placeholder="Buscar pelo código ou assunto"></label></section>')
h.append('<div class="grid">')
for p in pages:
    search = " ".join([p["code"], p["title"], p["summary"]]).lower()
    h.append(f'<a class="tile reveal" href="{p["slug"]}/" data-search="{E(search)}" '
             f'style="{accent_vars(p.get("accent", DEFAULT_ACCENT))}">'
             f'<div class="tile-top"><span class="code">#{E(p["code"])}</span>'
             f'<span class="count">{p["count"]} {"item" if p["count"] == 1 else "itens"}</span></div>'
             f'<h2>{E(p["title"])}</h2><p>{E(p["summary"])}</p>'
             f'<div class="tile-foot"><span>{fmt_date(p["date"])}</span><span class="go">Abrir {ARROW}</span></div></a>')
h.append('</div><p class="empty" hidden>Nada encontrado. Confira o código que veio no post.</p>')
h.append(f'{FOOT}</main>{JS}</body></html>')
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write("".join(h))
print("  ok: /  (index)")

# Página de links (estilo "link na bio")
h = [head(f'Links · {HANDLE}', site.get("links_intro", ""), "#FF7A1A", "../assets/style.css")]
h.append(nav("../", "links"))
h.append('<main class="wrap links-page">')
h.append(f'<section class="hero reveal"><span class="avatar"><span class="dot"></span></span>'
         f'<h1>{E(HANDLE)}</h1><p class="lead">{E(site.get("links_intro", ""))}</p></section>')
h.append('<div class="links">')
all_links = [{"label": LIB, "sub": f'{len(pages)} materiais dos posts', "url": "../", "icon": "library", "internal": True}]
all_links += site.get("links", [])
for l in all_links:
    ext = '' if l.get("internal") else ' target="_blank" rel="noopener"'
    sub = f'<small>{E(l["sub"])}</small>' if l.get("sub") else ''
    h.append(f'<a class="link-row reveal" href="{E(l["url"])}"{ext}>'
             f'<span class="link-ico">{icon(l.get("icon", "link"))}</span>'
             f'<span class="link-txt"><b>{E(l["label"])}</b>{sub}</span>'
             f'<span class="link-go">{ARROW}</span></a>')
h.append(f'</div>{FOOT}</main>{JS}</body></html>')
os.makedirs(os.path.join(ROOT, "links"), exist_ok=True)
open(os.path.join(ROOT, "links", "index.html"), "w", encoding="utf-8").write("".join(h))
print("  ok: /links/")

open(os.path.join(ROOT, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n" if site.get("noindex") else "User-agent: *\nAllow: /\n")
