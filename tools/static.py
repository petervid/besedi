#!/usr/bin/env python3
"""Генерира статична страница за всяка беседа (b/<адрес>.html), списък b/index.html и sitemap.xml,
за да могат търсачките да индексират текстовете. Пуска се от корена на сайта: python3 tools/static.py"""
import json, re, os, html, datetime

BASE = 'https://petervid.github.io/besedi/'
META = json.load(open('meta.json', encoding='utf-8'))
THEMES = {t['id']: t['name'] for t in json.load(open('themes.json', encoding='utf-8'))}
SHARD = json.load(open('ix/map.json', encoding='utf-8'))['shard']
esc = lambda s: html.escape(str(s), quote=True)

def fmt(d):
    m = re.match(r'^(\d{4})-(\d\d)-(\d\d)$', d)
    return f'{int(m[3])}.{m[2]}.{m[1]}' if m else d

def slug(m, used):
    s = re.sub(r'%[0-9A-Fa-f]{2}', '', m[3]).lower()
    s = re.sub(r'[^a-z0-9-]+', '-', s).strip('-') or str(m[0])
    if s in used: s = f'{s}-{m[0]}'
    used.add(s); return s

used = set()
SLUG = [slug(m, used) for m in META]
url = lambda i: f'{SLUG[i]}.html'

CSS = """:root{--bg:#f2f6fb;--bg2:#fbf3ef;--surface:#fff;--ink:#1d2f4a;--muted:#596b82;--line:#d9e3ee;--accent:#b07f22;--deep:#2b6a9e;--gold:#d2a64a}
@media (prefers-color-scheme:dark){:root{--bg:#0d1828;--bg2:#1a1830;--surface:#14233a;--ink:#e8eef6;--muted:#9db0c6;--line:#24364f;--accent:#e3bf6b;--deep:#9fcdf0;--gold:#e3bf6b;color-scheme:dark}}
*{box-sizing:border-box}html{background:var(--bg)}
body{margin:0;background:linear-gradient(180deg,var(--bg) 0%,var(--bg) 60%,var(--bg2) 100%) fixed;color:var(--ink);font-family:Manrope,"Segoe UI",system-ui,sans-serif;font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
a{color:var(--deep)}
.top{border-bottom:1px solid color-mix(in srgb,var(--gold) 45%,var(--line));background:color-mix(in srgb,var(--bg) 90%,transparent)}
.wrap{max-width:760px;margin:0 auto;padding:0 16px}
.top .wrap{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center;justify-content:space-between;padding-block:12px}
.brand{font-family:"Cormorant Garamond",Georgia,serif;font-size:23px;font-weight:600;color:var(--ink);text-decoration:none;display:flex;gap:9px;align-items:center}
.cta{font-weight:700;font-size:14px;text-decoration:none;border:1px solid color-mix(in srgb,var(--gold) 50%,var(--line));background:var(--surface);padding:7px 15px;border-radius:999px}
.crumbs{font-size:13.5px;color:var(--muted);margin:20px 0 0}.crumbs a{text-decoration:none}
header.h{text-align:center;margin:26px 0 26px}
.eb{font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);font-weight:700;margin:0}
h1{font-family:"Cormorant Garamond",Georgia,serif;font-weight:500;font-size:clamp(32px,6vw,50px);line-height:1.05;margin:.25em 0 0;text-wrap:balance}
.info{color:var(--muted);font-size:14px;margin-top:12px;display:flex;flex-wrap:wrap;justify-content:center;gap:4px 16px}
.chips{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin-top:10px}
.chips a{font-size:12px;padding:3px 10px;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--muted);text-decoration:none}
.orn{color:var(--gold);margin-top:16px}
.text{font-family:Literata,Georgia,serif;font-size:19px;line-height:1.78;hyphens:auto;text-wrap:pretty}
.text p{margin:0 0 1.05em}
nav.rn{display:flex;justify-content:space-between;gap:12px;border-top:1px solid var(--line);margin-top:28px;padding-top:14px;flex-wrap:wrap}
nav.rn a{text-decoration:none;max-width:48%}
footer{color:var(--muted);font-size:13px;text-align:center;padding:30px 16px 40px}
footer .v{font-family:"Cormorant Garamond",Georgia,serif;font-size:18px;color:var(--accent);letter-spacing:.06em;margin-bottom:6px}
ul.l{list-style:none;padding:0;columns:2 300px;column-gap:28px}ul.l li{break-inside:avoid;padding:3px 0;font-size:14px}ul.l .d{color:var(--muted);font-size:12.5px;margin-right:6px}
h2{font-family:"Cormorant Garamond",Georgia,serif;font-weight:500;font-size:30px;margin:30px 0 4px}
@media (max-width:560px){.text{font-size:17.5px}}"""

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Literata:opsz,wght@7..72,400&family=Manrope:wght@400;600;700&display=swap">'
LOGO = '<svg width="28" height="28" viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="18" fill="none" stroke="#d2a64a" stroke-width="1.6"/><polygon points="20,4.5 29.1,32.5 5.3,15.2 34.7,15.2 10.9,32.5" fill="none" stroke="#2b6a9e" stroke-width="1.6" stroke-linejoin="round"/></svg>'
FOOT = '<footer><div class="v">Любов · Мъдрост · Истина · Правда · Добродетел</div>3877 беседи на Петър Дънов (Беинса Дуно), 1895–1944. Текстовете са взети от <a href="https://beinsa.org">beinsa.org</a>.<br><a href="../">Портал с търсене</a> · <a href="./">Всички беседи</a></footer>'

def head(title, desc, canon, extra='', img=None):
    img = img or f'{BASE}og.jpg?v=2'
    return f'''<!doctype html>
<html lang="bg"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:type" content="article"><meta property="og:site_name" content="Беседите на Учителя"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{canon}"><meta property="og:image" content="{img}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/jpeg"><meta property="og:locale" content="bg_BG"><meta property="og:image:alt" content="Беседите на Учителя"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="../favicon.ico" sizes="any"><link rel="icon" href="../favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="../apple-touch-icon.png"><meta name="theme-color" content="#f2f6fb">
{FONTS}<style>{CSS}</style>{extra}</head><body>'''

def readtime(w):
    m = max(1, round(w / 200))
    return f'≈ {m} мин четене' if m < 60 else f'≈ {m // 60} ч {str(m % 60) + " мин " if m % 60 else ""}четене'

def describe(text):
    for p in re.split(r'\n\s*\n', text):
        p = re.sub(r'\s+', ' ', p).strip()
        if len(p) > 120:
            return p[:157].rsplit(' ', 1)[0] + '…'
    return re.sub(r'\s+', ' ', text).strip()[:157]

os.makedirs('b', exist_ok=True)
for f in os.listdir('b'):
    if f.endswith('.html'): os.remove(os.path.join('b', f))
shard_cache = {}
def text(i):
    k = i // SHARD
    if k not in shard_cache:
        shard_cache.clear(); shard_cache[k] = json.load(open(f't/{k:03d}.json', encoding='utf-8'))
    return shard_cache[k][i % SHARD]

N = len(META)
for i, m in enumerate(META):
    num, date, title, src, words, place, verse, th = m
    t = text(i)
    paras = ''.join(f'<p>{esc(p.strip()).replace(chr(10), "<br>")}</p>' for p in re.split(r'\n\s*\n', t) if p.strip())
    desc = describe(t)
    full = f'{title} · беседа от Учителя Петър Дънов, {fmt(date)}'
    ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": title[:110], "datePublished": date,
                     "author": {"@type": "Person", "name": "Петър Дънов (Беинса Дуно)"}, "inLanguage": "bg",
                     "isPartOf": {"@type": "WebSite", "name": "Беседите на Учителя", "url": BASE}, "url": BASE + 'b/' + url(i)}, ensure_ascii=False)
    info = ''.join(f'<span>{esc(x)}</span>' for x in [fmt(date), place, verse, f'{words:,} думи'.replace(',', ' '), readtime(words)] if x)
    chips = ''.join(f'<a href="../#tema-{t_}">{esc(THEMES[t_])}</a>' for t_ in th if t_ in THEMES)
    prev = f'<a href="{url(i-1)}">← {esc(META[i-1][2])}</a>' if i > 0 else '<span></span>'
    nxt = f'<a href="{url(i+1)}" style="text-align:right">{esc(META[i+1][2])} →</a>' if i < N - 1 else ''
    page = head(full, desc, BASE + 'b/' + url(i), f'<script type="application/ld+json">{ld}</script>', f'{BASE}og/b/{SLUG[i]}.jpg?v=1') + f'''
<div class="top"><div class="wrap"><a class="brand" href="../">{LOGO}Беседите на Учителя</a><a class="cta" href="../#b-{num}">Отвори в портала с търсене →</a></div></div>
<main class="wrap"><p class="crumbs"><a href="../">Начало</a> › <a href="./#y{date[:4]}">{date[:4]}</a> › {esc(title)}</p>
<article><header class="h"><p class="eb">Беседа {num} от {N} · Беинса Дуно</p><h1>{esc(title)}</h1>
<div class="info">{info}<a href="https://beinsa.org/beseda/{esc(src)}" rel="noopener">Оригинал на beinsa.org ↗</a></div>{f'<div class="chips">{chips}</div>' if chips else ''}<div class="orn">✦</div></header>
<div class="text">{paras}</div></article>
<nav class="rn">{prev}{nxt}</nav></main>{FOOT}</body></html>'''
    open(f'b/{url(i)}', 'w', encoding='utf-8').write(page)

# index of all lectures by year
by = {}
for i, m in enumerate(META): by.setdefault(m[1][:4], []).append(i)
body = ''.join(f'<h2 id="y{y}">{y} <span style="font-size:16px;color:var(--muted)">· {len(ids)} беседи</span></h2><ul class="l">' +
               ''.join(f'<li><span class="d">{fmt(META[i][1])}</span><a href="{url(i)}">{esc(META[i][2])}</a></li>' for i in ids) + '</ul>'
               for y, ids in sorted(by.items()))
open('b/index.html', 'w', encoding='utf-8').write(
    head('Всички беседи на Учителя Петър Дънов (1895–1944)', f'Пълен списък на {N} беседи на Учителя Петър Дънов (Беинса Дуно) по години, с пълния текст на всяка беседа.', BASE + 'b/') +
    f'<div class="top"><div class="wrap"><a class="brand" href="../">{LOGO}Беседите на Учителя</a><a class="cta" href="../">Търсене в беседите →</a></div></div>'
    f'<main class="wrap"><header class="h"><p class="eb">1895–1944</p><h1>Всички {N} беседи</h1><div class="info">' +
    ' · '.join(f'<a href="#y{y}">{y}</a>' for y in sorted(by)) + f'</div></header>{body}</main>{FOOT}</body></html>')

today = datetime.date.today().isoformat()
with open('sitemap.xml', 'w', encoding='utf-8') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    f.write(f'  <url><loc>{BASE}</loc><lastmod>{today}</lastmod><priority>1.0</priority></url>\n')
    f.write(f'  <url><loc>{BASE}b/</loc><lastmod>{today}</lastmod><priority>0.9</priority></url>\n')
    for i in range(N): f.write(f'  <url><loc>{BASE}b/{url(i)}</loc><lastmod>{today}</lastmod></url>\n')
    f.write('</urlset>\n')
json.dump(SLUG, open('b/slugs.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('pages', N)
