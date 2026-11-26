#!/usr/bin/env python3
"""Страници за споделяне: tema/<id>.html за всяка тема и <раздел>/index.html за разделите.
Всяка има собствени og:title, og:description и og:image (og/<име>.jpg), за да се вижда правилна
картинка, когато връзката се сподели. Човек, който отвори връзката, се прехвърля към самия раздел.
Пуска се от корена на сайта след static.py: python3 tools/share.py"""
import json, os, html, re, datetime
BASE = 'https://petervid.github.io/besedi/'
esc = lambda s: html.escape(str(s), quote=True)
META = json.load(open('meta.json', encoding='utf-8'))
TH = json.load(open('themes.json', encoding='utf-8'))
SLUG = json.load(open('b/slugs.json', encoding='utf-8'))
def fmt(d):
    m = re.match(r'^(\d{4})-(\d\d)-(\d\d)$', d)
    return f'{int(m[3])}.{m[2]}.{m[1]}' if m else d
SECTIONS = [
 ('temi', 'Темите в беседите', f'{len(TH)} главни теми в учението на Петър Дънов, с най-характерните откъси и разпределение по години.'),
 ('balgaria', 'България и българите в новото време', 'Какво казва Учителя за България, българите и тяхната мисия: подбрани откъси по раздели.'),
 ('paneuritmia', 'Паневритмия', 'Видео курс по Паневритмия с д‑р Светла Балтова и думите на Учителя за смисъла на упражненията.'),
 ('slovo', 'Словото в числа', 'Колко е казано, кои думи се повтарят най-често и как се променя езикът на беседите през годините.'),
 ('hronologia', 'Хронология на беседите', 'Всички 3877 беседи на Петър Дънов, подредени по години и серии.'),
 ('stihove', 'Библейски стихове в беседите', 'Стиховете от Библията, които Учителя тълкува в беседите си.'),
]
CSS = """:root{--bg:#f2f6fb;--ink:#1d2f4a;--muted:#596b82;--line:#d9e3ee;--accent:#b07f22;--deep:#2b6a9e;--gold:#d2a64a;--surface:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#0d1828;--ink:#e8eef6;--muted:#9db0c6;--line:#24364f;--accent:#e3bf6b;--deep:#9fcdf0;--gold:#e3bf6b;--surface:#14233a;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 Manrope,"Segoe UI",system-ui,sans-serif}
.wrap{max-width:760px;margin:0 auto;padding:28px 16px 60px}a{color:var(--deep)}
.eb{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:700;margin:0}
h1{font-family:"Cormorant Garamond",Georgia,serif;font-weight:500;font-size:clamp(32px,6vw,48px);line-height:1.08;margin:.2em 0 .3em}
.lede{color:var(--muted);font-size:17px}.go{display:inline-block;margin:14px 0 24px;font-weight:700;text-decoration:none;border:1px solid var(--gold);background:var(--surface);padding:9px 18px;border-radius:999px}
blockquote{margin:0;padding:16px 0;border-top:1px solid var(--line);font-family:Georgia,serif;font-size:16.5px}blockquote p{margin:0 0 6px}.src{font:13px Manrope,system-ui,sans-serif;color:var(--muted)}"""
def page(path, name, title, desc, target, body=''):
    depth = path.count('/')
    up = '../' * depth
    url = BASE + re.sub(r'index\.html$', '', path)
    img = f'{BASE}og/{name}.jpg?v=1'
    t = f'{title} · Беседите на Учителя'
    h = f'''<!doctype html>
<html lang="bg"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(t)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Беседите на Учителя"><meta property="og:locale" content="bg_BG">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}">
<meta property="og:image" content="{img}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:alt" content="{esc(title)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{img}">
<link rel="icon" href="{up}favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="{up}apple-touch-icon.png">
<style>{CSS}</style>
<script>location.replace("{up}#{target}")</script>
</head><body><main class="wrap"><p class="eb">Беседите на Учителя</p><h1>{esc(title)}</h1><p class="lede">{esc(desc)}</p>
<a class="go" href="{up}#{target}">Отвори в сайта →</a>{body}</main></body></html>
'''
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    open(path, 'w', encoding='utf-8').write(h)
    return url
urls = []
for sid, title, desc in SECTIONS:
    urls.append(page(f'{sid}/index.html', sid, title, desc, sid))
for t in TH:
    desc = f"{t['desc']} {t['count']} беседи и най-характерните откъси."
    qs = ''.join(f'<blockquote>{"".join(f"<p>{esc(p)}</p>" for p in q.split(chr(10)) if p.strip())}<div class="src"><a href="../b/{SLUG[i]}.html">{esc(META[i][2])}</a> · {esc(fmt(META[i][1]))}</div></blockquote>' for i, q in t['top'][:8])
    urls.append(page(f"tema/{t['id']}.html", t['id'], t['name'], desc, 'tema-' + t['id'], qs))
sm = open('sitemap.xml', encoding='utf-8').read()
sm = re.sub(r'  <url><loc>[^<]*/(?:tema/[^<]*|(?:' + '|'.join(s[0] for s in SECTIONS) + r')/)</loc>[^\n]*\n', '', sm)
today = datetime.date.today().isoformat()
sm = sm.replace('</urlset>', ''.join(f'  <url><loc>{u}</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>\n' for u in urls) + '</urlset>')
open('sitemap.xml', 'w', encoding='utf-8').write(sm)
print(len(urls), 'share pages')
