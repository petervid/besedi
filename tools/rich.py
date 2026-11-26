#!/usr/bin/env python3
"""Форматиране от оригинала, което не е в обикновения текст: курсив, горен индекс (a²),
удебелени заглавия и рисунките. Чете суровия HTML на всяка беседа (raw/NNNN.html, свален от beinsa.org)
и записва r/NNN.json само за беседите с такова форматиране: {индекс: текст с маркери}.
Маркерите са символи от частната зона на Unicode, за да не пречат на търсенето:
   курсив     горен индекс     удебелено    адрес на рисунка
Броят на абзаците е същият като в обикновения текст, затова връзките към абзаци остават верни.
Пуска се от корена на сайта: python3 tools/rich.py <папка със суровия HTML>"""
import re, json, glob, html, sys, os, collections
RAW = sys.argv[1]
meta = json.load(open('meta.json')); texts = []
for f in sorted(glob.glob('t/*.json')): texts += json.load(open(f))
SH = json.load(open('ix/map.json'))['shard']
MK = re.compile(r'[^]*|[-]')
def clean(s):
    s = re.sub(r'<br\s*/?>', '\n', s); s = re.sub(r'</p>', '\n\n', s); s = re.sub(r'</?[A-Za-z][^>]*>', '', s)
    s = html.unescape(s).replace('\r', '').replace('\xa0', ' '); s = re.sub(r'[ \t]+\n', '\n', s); s = re.sub(r'\n{3,}', '\n\n', s); return s.strip()
def mark(b):
    b = re.sub(r'<img[^>]*src="/?([^"]+)"[^>]*>', lambda m: '' + m[1] + '', b)
    b = re.sub(r'<(em|i)>', '', b); b = re.sub(r'</(em|i)>', '', b)
    b = re.sub(r'<sup>', '', b); b = re.sub(r'</sup>', '', b)
    b = re.sub(r'<span class="font-semibold">(.*?)</span>', '\\1', b, flags=re.S)
    return b
out = collections.defaultdict(dict); imgs = set(); bad = []
for i in range(len(meta)):
    b = open(f'{RAW}/{i:04d}.html').read()
    if not re.search(r'<(img|em|i|sup)\b|font-semibold', b): continue
    r = clean(mark(b))
    # whitespace around markers can differ from the plain text: rebuild paragraph by paragraph
    plain = texts[i].strip(); pp = re.split(r'\n\s*\n', plain)
    rp = re.split(r'\n\s*\n', r)
    merged = []; carry = ''
    for p in rp:
        if not MK.sub('', p).strip(): carry += MK.sub(lambda m: m[0] if m[0].startswith('') else '', p).strip(); continue
        merged.append(carry + p); carry = ''
    if carry:
        if merged: merged[-1] += carry
        else: bad.append((i, 'only images')); continue
    if len(merged) != len(pp) or any(clean(MK.sub('', a)) != clean(c) for a, c in zip(merged, pp)):
        bad.append((i, len(merged), len(pp))); continue
    out[i // SH][i] = '\n\n'.join(merged)
    imgs.update(re.findall(r'([^]*)', r))
os.makedirs('r', exist_ok=True)
for f in glob.glob('r/*.json'): os.remove(f)
for s, d in out.items(): json.dump(d, open(f'r/{s:03d}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(sorted(i for d in out.values() for i in d), open('r/index.json', 'w'), separators=(',', ':'))
json.dump(sorted(imgs), open('r/images.json', 'w'), ensure_ascii=False, indent=0)
print('rich lectures', sum(map(len, out.values())), 'images', len(imgs), 'mismatches', len(bad), bad[:10])
