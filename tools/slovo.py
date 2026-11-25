#!/usr/bin/env python3
"""Анализ на словото: числа, чести думи, ключови думи по периоди, изрази и промени във времето.
Пуска се от корена на сайта: python3 tools/slovo.py  →  slovo.json"""
import json, re, glob, math, collections

META = json.load(open('meta.json', encoding='utf-8'))
SHARD = json.load(open('ix/map.json', encoding='utf-8'))['shard']

def norm(t):
    t = t.lower().replace('ё', 'е').replace('ѣ', 'е').replace('ѫ', 'ъ').replace('ѭ', 'ю').replace('і', 'и')
    t = re.sub(r'ъ\b', '', t)
    return re.sub(r'ь\b', '', t)

ENDS = ['ението','ането','ието','ения','ение','ания','ание','ане','ата','ите','ият','ния','ост','ия','ът','ят','та','то','те','ни','на','но','а','е','и','о','у','я']
def stem(w):
    if len(w) < 5: return w
    for e in ENDS:
        if w.endswith(e) and len(w) - len(e) >= 4: return w[:-len(e)]
    return w

STOP = set("""и в на да се не е че са за от с ще по ако като то това той тя те ние вие аз ти му ми ги го ви ни им й ѝ си съм сме сте бъде бъдат бил била били било беше бяха бях бе е а но или ли пък даже дори още вече само все тъй така също тук там къде кога как какво какъв каква какви кой коя кое кои който която което които чий нещо нищо някой някоя някое някои никой всеки всяка всяко всички всичко всяко сега тогава после преди след при към до през между над под без чрез срещу около върху освен защото понеже затова обаче значи именно следователно щом докато когато ако щото че нека нито ни ето ей о у ах ох ей хм мене тебе него нея нас вас тях мен теб негов негова негово негови неин нейна нейно нейни наш наша наше наши ваш ваша ваше ваши техен тяхна тяхно техни мой моя мое мои твой твоя твое твои свой своя свое свои себе си да не ще няма има имат има имам имаш имаме имате бъда бъдеш бъдем бъдете би бих бихте биха бихме е са съм си сме сте беше бяха бил била било били много малко повече по-малко най по-добре добре едно един една едни два две три пет десет хиляди първо първия първата втори втората ден дни година години път пъти начин някъде никъде навсякъде вътре вън горе долу далеч близо колко толкова доколкото дотолкова защо затуй нали навярно може могат мога можем можете можеш трябва казва казвам казах каза казват кажа кажете кажеш казвате казано рече рекъл говори говоря говорите говорят говорим знае знам знаете знаят зная мисли мислите мисля мислят иска искам искате искат искаш иде иду идат дойде дойдат отиде отидат става стават стане станат прави правят правите правя направи направят направите види видите видят виждате вижда виждам дава дават даде дадат дай дайте взема вземе вземат хора човек човека човекът хората нещата неща неща работа сега ето туй онзи онази онова онези този тази това тези тия оня тоя туй тоз таз някак някакъв някаква някакво някакви никакъв никаква никакво никакви всякакъв всякаква всякакво всякакви сам сама само сами самият самата самото тъкмо точно просто наистина действително например тъй като г т н др т.е стр друг друга други друго във със както пак каже всичките всичкото тогаз толкоз доста където гдето нещо най-първо може бива ред сега защо тъй тям тук-там значи иначе вместо всякой нийде онуй горе-долу""".split())
# words that are dates, names or headings, not the teaching itself
NOISE = set("""дънов г-н г-жа софия изгрев държана държано държан лекция лекции беседа беседи клас класа сутринта вечерта ч януари февруари март април май юни юли август септември октомври ноември декември понеделник вторник сряда четвъртък петък събота неделя неделна неделни събрание събранието прочета прочетох прочетете глава стих стиха""".split())

def P(y):
    return '1895–1913' if y < 1914 else '1914–1921' if y < 1922 else '1922–1929' if y < 1930 else '1930–1937' if y < 1938 else '1938–1944'
PERIODS = ['1895–1913', '1914–1921', '1922–1929', '1930–1937', '1938–1944']
PDESC = {'1895–1913': 'Ранните години: съборите, нарядите и първите беседи.',
         '1914–1921': 'Неделните беседи в София („Сила и живот“) и годините на войните.',
         '1922–1929': 'Откриването на Школата: Общ и Младежки окултен клас.',
         '1930–1937': 'Изгрев, Рила, утринните слова и разцветът на Братството.',
         '1938–1944': 'Последните години: Паневритмията, войната и Мърчаево.'}

CONCEPTS = [('Любов', r'любов|любв|обич'), ('Мъдрост', r'мъдр'), ('Истина', r'истин'), ('Бог', r'бог(?!ат|ат)|божи|божествен'),
            ('Христос', r'христ'), ('Природа', r'природ'), ('Душа', r'душ(?!ев)'), ('Ученик', r'учени[кц]'),
            ('Музика и пеене', r'музик|пеен|пее|песен|песн'), ('Светлина', r'светлин'), ('Свобода', r'свобод'), ('Страдание', r'страда')]
CRX = [(n, re.compile(r'\b(?:' + r + ')')) for n, r in CONCEPTS]
PRON = [('Аз', r'\bаз\b'), ('Ние', r'\bние\b'), ('Вие', r'\bвие\b')]
PRX = [(n, re.compile(r)) for n, r in PRON]

def texts():
    for f in sorted(glob.glob('t/*.json')):
        k = int(re.search(r'(\d+)\.json$', f)[1])
        for j, t in enumerate(json.load(open(f, encoding='utf-8'))):
            yield k * SHARD + j, t

years = collections.defaultdict(lambda: {'d': 0, 'w': 0, 's': 0, 'q': 0, 'c': collections.Counter(), 'p': collections.Counter()})
tf = collections.Counter(); df = collections.Counter(); forms = collections.defaultdict(collections.Counter)
ptf = {p: collections.Counter() for p in PERIODS}; pdf = {p: collections.Counter() for p in PERIODS}; pwords = collections.Counter(); pdocs = collections.Counter()
ng_chunk = collections.Counter(); NG = collections.Counter(); NGdf = collections.Counter(); ng_form = {}
distinct = set()
pvocab = {p: set() for p in PERIODS}; psample = collections.Counter()

def flush():
    global ng_chunk
    for g, c in ng_chunk.items():
        if c >= 2: NGdf[g] += c
    ng_chunk = collections.Counter()

for n, (i, raw) in enumerate(texts()):
    m = META[i]; y = int(m[1][:4]); p = P(y)
    t = norm(raw); toks = re.findall(r'[а-я]+(?:-[а-я]+)?', t)
    Y = years[y]; Y['d'] += 1; Y['w'] += len(toks)
    sents = [s for s in re.split(r'[.!?…]+', t) if re.search(r'[а-я]', s)]
    Y['s'] += len(sents); Y['q'] += t.count('?')
    for name, rx in CRX: Y['c'][name] += len(rx.findall(t))
    for name, rx in PRX: Y['p'][name] += len(rx.findall(t))
    pwords[p] += len(toks); pdocs[p] += 1
    distinct.update(toks)
    seen = set()
    for w in toks:
        if w in STOP or w in NOISE or len(w) < 3: continue
        s = stem(w); tf[s] += 1; forms[s][w] += 1; ptf[p][s] += 1; seen.add(s)
    for s in seen: df[s] += 1; pdf[p][s] += 1
    # n-grams of 2..5 words that start and end with a content word, counted once per lecture
    L = len(toks); g_seen = set()
    for a in range(L):
        if toks[a] in STOP or toks[a] in NOISE or len(toks[a]) < 3: continue
        for k in range(2, 6):
            b = a + k
            if b > L: break
            last = toks[b - 1]
            if last in STOP or len(last) < 3: continue
            if sum(1 for w in toks[a:b] if w not in STOP) < 2 or any(w in NOISE for w in toks[a:b]): continue
            g_seen.add(tuple(stem(w) if w not in STOP else w for w in toks[a:b]))
            key = tuple(stem(w) if w not in STOP else w for w in toks[a:b])
            if key not in ng_form: ng_form[key] = ' '.join(toks[a:b])
    for g in g_seen: ng_chunk[g] += 1
    if n % 400 == 399: flush()
flush()

def disp(s): return forms[s].most_common(1)[0][0]
N = sum(pwords.values()); NDOC = len(META)

surf = collections.Counter()
for st_, fc in forms.items(): surf.update(fc)
SUF = ['ата', 'ите', 'ият', 'ия', 'ът', 'ят', 'та', 'то', 'те', 'а', 'я']
def base(w):
    for e in SUF:
        b = w[:-len(e)]
        if w.endswith(e) and len(b) >= 3 and surf.get(b, 0) >= 0.08 * surf[w]: return b
    return w
grp = collections.Counter()
for w, c in surf.items():
    if c >= 200: grp[base(w)] += c
top = [[w, c] for w, c in grp.most_common(140)][:120]

# distinctive words per period: log-odds with informative Dirichlet prior (Monroe et al.)
A0 = 2000.0; tot_all = sum(tf.values())
periods = []
for p in PERIODS:
    a = ptf[p]; na = sum(a.values()); nb = tot_all - na; out = []
    for s, ca in a.items():
        if pdf[p][s] < max(6, 0.04 * pdocs[p]): continue
        cb = tf[s] - ca; prior = A0 * tf[s] / tot_all
        d = math.log((ca + prior) / (na + A0 - ca - prior)) - math.log((cb + prior) / (nb + A0 - cb - prior))
        z = d / math.sqrt(1 / (ca + prior) + 1 / (cb + prior))
        ratio = (ca / na) / ((cb + 1) / nb)
        if ratio > 1.4: out.append((z, s, ratio))
    out.sort(reverse=True)
    periods.append({'name': p, 'desc': PDESC[p], 'docs': pdocs[p], 'words': pwords[p],
                    'top': [[disp(s), round(r, 1)] for z, s, r in out[:24]],
                    'freq': [disp(s) for s, c in a.most_common(30)][:15]})

# phrases: keep those in many lectures; drop shorter ones contained in a longer phrase with similar reach
cand = [(g, c) for g, c in NGdf.items() if c >= 25]
cand.sort(key=lambda x: (-x[1]))
keep = []
for g, c in cand:
    txt = ' ' + ' '.join(g) + ' '
    if any((txt in ' ' + ' '.join(h) + ' ') and hc >= 0.7 * c for h, hc in keep): continue
    keep.append((g, c))
# prefer longer phrases: drop a phrase if a longer kept one contains it with ≥70% of its reach
final = []
for g, c in keep:
    txt = ' ' + ' '.join(g) + ' '
    if any(len(h) > len(g) and txt in ' ' + ' '.join(h) + ' ' and hc >= 0.7 * c for h, hc in keep): continue
    final.append([ng_form[g], c, len(g)])
phr = {k: [x[:2] for x in final if x[2] == k][:25] for k in (2, 3, 4, 5)}

ys = sorted(years)
lens = sorted(((m[4], k) for k, m in enumerate(META)), reverse=True)
out = {
    'total': {'words': N, 'docs': NDOC, 'distinct': len(distinct), 'years': len(ys), 'avg': round(N / NDOC),
              'pages': round(N / 300)},
    'longest': [[k, w] for w, k in lens[:8]],
    'years': {y: [years[y]['d'], years[y]['w'], round(years[y]['w'] / max(1, years[y]['s']), 1), round(years[y]['q'] / max(1, years[y]['w']) * 1000, 2),
                  {c: round(years[y]['c'][c] / max(1, years[y]['w']) * 10000, 1) for c, _ in CONCEPTS},
                  {c: round(years[y]['p'][c] / max(1, years[y]['w']) * 10000, 1) for c, _ in PRON}] for y in ys},
    'concepts': [c for c, _ in CONCEPTS], 'pron': [c for c, _ in PRON],
    'top': top, 'periods': periods, 'phrases': phr,
}
json.dump(out, open('slovo.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('ok', N, len(distinct))
for p in periods: print(p['name'], [w for w, r in p['top'][:15]])
print('top', [w for w, c in top[:60]])
for k in phr: print(k, [x[0] for x in phr[k][:15]])

# ---- clean-up pass: drop proper names (mostly capitalised in the texts) and overlapping fragments of the same formula
def _clean():
    d = json.load(open('slovo.json', encoding='utf-8'))
    words = {w for p in d['periods'] for w, r in p['top']} | {w for w, c in d['top']}
    cap = collections.Counter(); low = collections.Counter()
    rx = re.compile(r'(?<![а-яА-Я])([А-Я]?[а-я-]+)')
    for i, raw in texts():
        for m in rx.finditer(raw.replace('ѣ', 'е').replace('ѫ', 'ъ')):
            w = m.group(1); lw = re.sub(r'ъ$', '', w.lower())
            if lw in words:
                if w[0].isupper(): cap[lw] += 1
                else: low[lw] += 1
    name = lambda w: cap[w] > 3 * low[w] and w not in ('бог', 'господ', 'христос', 'христа', 'учител', 'школа')
    for p in d['periods']: p['top'] = [x for x in p['top'] if not name(x[0])][:20]
    d['top'] = [x for x in d['top'] if not name(x[0])][:100]
    for k, arr in d['phrases'].items():
        out = []
        for ph, c in arr:
            ws = ph.split()
            if any(len(set(ws) & set(o.split())) >= len(ws) - 1 for o, oc in out): continue
            out.append([ph, c])
        d['phrases'][k] = out[:15]
    json.dump(d, open('slovo.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    for p in d['periods']: print(p['name'], [w for w, r in p['top']])
    for k in d['phrases']: print(k, [x[0] for x in d['phrases'][k]])
_clean()

# ---- recurring formulas, counted as the number of lectures that contain them
FORMULAS = [('Бог е Любов', r'бог е любов'), ('Любовта, Мъдростта и Истината', r'любовта,? мъдростта и истината'),
            ('Светлият път на Мъдростта', r'светлият път на мъдростта'), ('Царството Божие', r'царството божие|божието царство'),
            ('Верен, истинен, чист и благ всякога бъди', r'верен,? истинен,? чист'), ('Да позная Тебе, единаго истиннаго Бога', r'тебе,? единаго|тебе,? единнаго|тебе,? единия истинен'),
            ('Новата култура', r'новата култура'), ('Шестата раса', r'шестата раса'), ('Отче наш', r'отче наш'),
            ('Образ и подобие', r'образ и подобие'), ('Великата Божия Любов', r'великата божия любов'), ('Разумната природа', r'разумната природа'),
            ('Невидимият свят', r'невидимия(?:т)? свят'), ('Новото учение', r'новото учение'), ('Христос в нас', r'христос в (?:нас|вас|човека)')]
def _formulas():
    d = json.load(open('slovo.json', encoding='utf-8'))
    rx = [(n, re.compile(r)) for n, r in FORMULAS]; c = collections.Counter(); per = {n: collections.Counter() for n, _ in FORMULAS}
    for i, raw in texts():
        t = re.sub(r'\s+', ' ', norm(raw)); y = META[i][1][:4]
        for n, r in rx:
            if r.search(t): c[n] += 1; per[n][P(int(y))] += 1
    d['formulas'] = [[n, c[n], [per[n][p] for p in PERIODS]] for n, _ in sorted(FORMULAS, key=lambda x: -c[x[0]]) if c[n]]
    DROP = {'краска', 'лента', 'прочете', 'д-р', 'събрахме', 'тая', 'вашите', 'требва', 'нема'}
    for p in d['periods']: p['top'] = [x for x in p['top'] if x[0] not in DROP][:18]
    d['phrases'].pop('5', None)
    json.dump(d, open('slovo.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(d['formulas'])
_formulas()

# ---- final touches (also applied by hand once): drop filler phrases and meeting protocols from "longest"
def _final():
    d = json.load(open('slovo.json', encoding='utf-8'))
    BAD = ['учителя', 'дълго време', 'дадения случай', 'двама души', 'същия закон', 'края на краищата', 'приведа един пример', 'баща си и майка', 'бог ви е дал', 'бог ни е дал']
    for k in d['phrases']: d['phrases'][k] = [x for x in d['phrases'][k] if not any(b in x[0] for b in BAD)]
    L = sorted(((x[4], i) for i, x in enumerate(META) if not any(w in x[2].lower() for w in ('протокол', 'среща', 'събор'))), reverse=True)[:8]
    d['longest'] = [[i, w] for w, i in L]
    json.dump(d, open('slovo.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
_final()
