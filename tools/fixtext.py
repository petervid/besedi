#!/usr/bin/env python3
"""Поправя текста на отделни беседи от суровия HTML (raw/NNNN.html) и обновява t/, meta.json (брой думи),
индекса за търсене ix/ и изходните файлове в tekstove/. Ползва се, когато се открие грешка при извличането.
python3 tools/fixtext.py <папка със суров HTML> <индекс> [<индекс> ...]"""
import re, json, glob, html, sys, collections
RAW = sys.argv[1]; IDX = [int(x) for x in sys.argv[2:]]
TXT = '/mnt/project-files/besedi/tekstove'
def clean(s):
    # only real tags (a Latin letter after "<"): "<198" or "<В" in the text are kept as text
    s = re.sub(r'<br\s*/?>', '\n', s); s = re.sub(r'</p>', '\n\n', s); s = re.sub(r'</?[A-Za-z][^>]*>', '', s)
    s = html.unescape(s).replace('\r', '').replace('\xa0', ' '); s = re.sub(r'[ \t]+\n', '\n', s); s = re.sub(r'\n{3,}', '\n\n', s); return s.strip()
def norm(t):
    t = t.lower().replace('ё', 'е').replace('ѣ', 'е').replace('ѫ', 'ъ').replace('ѭ', 'ю').replace('і', 'и')
    return re.sub(r'ъ\b', '', t)
meta = json.load(open('meta.json')); M = json.load(open('ix/map.json')); SH = M['shard']
new = {i: clean(open(f'{RAW}/{i:04d}.html').read()) for i in IDX}
for s in {i // SH for i in IDX}:
    p = f't/{s:03d}.json'; d = json.load(open(p))
    for i in IDX:
        if i // SH == s: d[i % SH] = new[i]
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
counts = {}
for i in IDX:
    w = re.findall(r'[а-я]{2,}', norm(new[i])); meta[i][4] = len(w); counts[i] = collections.Counter(w)
json.dump(meta, open('meta.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
def dec(a):
    out = []; d = 0
    for k in range(0, len(a), 2): d += a[k]; out.append((d, a[k + 1]))
    return out
def enc(pl):
    a = []; p = 0
    for d, k in pl: a += [d - p, k]; p = d
    return a
def bucket(w):
    p = w[:2]
    for bi, (a, b) in enumerate(M['buckets']):
        if a <= p <= b: return bi
    return None
touched = collections.defaultdict(set)
for i, c in counts.items():
    for w in c: touched[bucket(w)].add(w)
for bi in range(len(M['buckets'])):
    p = f'ix/{bi:03d}.json'; B = json.load(open(p)); ch = False
    for w in list(B):
        pl = dec(B[w])
        if any(d in counts for d, _ in pl):
            pl = [(d, k) for d, k in pl if d not in counts]; ch = True
            B[w] = enc(pl) if pl else None
    for w in touched.get(bi, ()):
        pl = dec(B[w]) if B.get(w) else []
        pl += [(i, min(c[w], 255)) for i, c in counts.items() if w in c]; pl.sort(); B[w] = enc(pl); ch = True
    B = {k: v for k, v in B.items() if v}
    if ch: json.dump(B, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
for i in IDX:
    fs = glob.glob(f'{TXT}/{meta[i][0]:04d}_*.txt')
    for f in fs:
        head = open(f, encoding='utf-8').read().split('\n', 4)
        open(f, 'w', encoding='utf-8').write('\n'.join(head[:4]) + '\n' + new[i] + '\n')
    print(i, meta[i][2], 'words', meta[i][4], 'source files', len(fs))
