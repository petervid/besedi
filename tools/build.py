import os,re,sys,json,gzip,collections,math
sys.path.insert(0,os.path.dirname(__file__))
from themes import THEMES
D,OUT=sys.argv[1],sys.argv[2]
SH=20
os.makedirs(OUT+'/t',exist_ok=True); os.makedirs(OUT+'/ix',exist_ok=True)
def norm(t):
    t=t.lower().replace('ё','е').replace('ѣ','е').replace('ѫ','ъ').replace('ѭ','ю').replace('і','и')
    return re.sub(r'ъ\b','',t)
BOOKS=[('Матей',r'мате[йя]|мат\.'),('Марко',r'марк'),('Лука',r'лук[аи]'),('Йоан',r'[йи]оан'),('Деяния',r'деяни'),('Римляни',r'римл'),
('Коринтяни',r'коринт|кор\.'),('Галатяни',r'галат'),('Ефесяни',r'ефес'),('Филипяни',r'филип'),('Колосяни',r'колос'),('Солунци',r'солун'),
('Тимотей',r'тимот'),('Евреи',r'евреи'),('Яков',r'яков'),('Петър',r'петрово|петр'),('Откровение',r'откр'),('Битие',r'битие'),('Изход',r'изход'),
('Второзаконие',r'второзак'),('Царе',r'царе'),('Йов',r'[йи]ов\b'),('Псалми',r'псал'),('Притчи',r'притч'),('Еклисиаст',r'еклис'),('Исая',r'исаи|исая'),
('Еремия',r'ереми'),('Езекиил',r'езекиил'),('Даниил',r'даниил'),('Малахия',r'малахи'),('Захария',r'захари'),('Осия',r'осия'),('Михей',r'михе')]
VRX=re.compile(r'\b('+'|'.join('(?:%s)'%b for _,b in BOOKS)+r')[а-я.]*\s*(\d{1,3})\s*[:,.]\s*(\d{1,3})')
def book(s):
    for n,b in BOOKS:
        if re.match(b,s): return n
PLACES=['Изгрев','София','Търново','Варна','Бургас','Мусала','Рила','Седемте рилски езера','Мърчаево','Пловдив','Казанлък','Русе','Шумен','Ямбол','Стара Загора','Сливен','Хасково','Хоризонт']
R=[(t[0],re.compile(r'\b(?:'+t[3]+')')) for t in THEMES]
files=sorted(os.listdir(D))
meta=[]; post=collections.defaultdict(list); docthemes=[]; shard=[]; W=[]
for idx,f in enumerate(files):
    raw=open(os.path.join(D,f),encoding='utf-8').read()
    title,info,url,_,body=raw.split('\n',4)
    num,date=[x.strip() for x in info.split('|')]
    n=norm(body); words=re.findall(r'[а-я]{2,}',n)
    c=collections.Counter(words)
    for w,k in c.items(): post[w].append((idx,min(k,255)))
    tail=body[-900:]; place=next((p for p in PLACES if p in tail),'')
    if place=='Изгрев': place='София, Изгрев'
    vm=VRX.search(norm(body[:1500])) or VRX.search(norm(body[-600:]))
    verse=''
    if vm: verse=f"{book(vm.group(1))} {vm.group(2)}:{vm.group(3)}"
    meta.append([int(num),date,title,url.rsplit('/',1)[1],len(words),place,verse])
    W.append(len(words))
    paras=[p.strip() for p in body.split('\n\n') if p.strip()]
    th={}
    for tid,r in R:
        k=len(r.findall(n))
        if k:
            best=max(paras,key=lambda p:(len(r.findall(norm(p)))/ (len(p)+200)) if 120<len(p)<900 else -1) if paras else ''
            th[tid]=(k,best)
    docthemes.append(th)
    shard.append(body)
    if len(shard)==SH or idx==len(files)-1:
        with gzip.open(f'{OUT}/t/{idx//SH:03d}.json.gz','wt',encoding='utf-8',compresslevel=9) as g: json.dump(shard,g,ensure_ascii=False,separators=(',',':'))
        shard=[]
N=len(files); Wtot=sum(W)
# themes
themes=[]; mem=[[] for _ in range(N)]
for tid,name,desc,_ in THEMES:
    tot=sum(dt[tid][0] for dt in docthemes if tid in dt); avg=tot/Wtot
    sc=[]
    for i,dt in enumerate(docthemes):
        if tid in dt and W[i]>=300:
            k,best=dt[tid]; dens=k/W[i]
            if dens>=2*avg and k>=8: sc.append((dens*math.log(k),i,best))
    sc.sort(reverse=True)
    for _,i,_ in sc: mem[i].append(tid)
    years=collections.Counter(meta[i][1][:4] for _,i,_ in sc)
    themes.append({'id':tid,'name':name,'desc':desc,'count':len(sc),'per1000':round(avg*1000,2),'years':dict(sorted(years.items())),
      'docs':[i for _,i,_ in sc],'top':[[i,b[:700]] for _,i,b in sc[:40]]})
for i,m in enumerate(meta): m.append(mem[i])
json.dump(meta,open(OUT+'/meta.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
json.dump(themes,open(OUT+'/themes.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
# bible
bv=collections.defaultdict(list)
for i,m in enumerate(meta):
    if m[6]: bv[m[6]].append(i)
json.dump(sorted(bv.items(),key=lambda x:-len(x[1])),open(OUT+'/verses.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
# index buckets by 2-letter prefix, merged to ~target size
ws=sorted(post); buckets=[]; cur={}; size=0; start=None
def enc(pl):
    a=[];p=0
    for d,k in pl: a.append(d-p); a.append(k); p=d
    return a
groups=collections.OrderedDict()
for w in ws: groups.setdefault(w[:2],[]).append(w)
TARGET=260000
for pre,wl in groups.items():
    for w in wl: cur[w]=enc(post[w])
    size+=sum(len(post[w])*4+len(w)+6 for w in wl)
    if start is None: start=pre
    if size>=TARGET:
        buckets.append((start,pre,cur)); cur={}; size=0; start=None
if cur: buckets.append((start,pre,cur))
idxmap=[]
for bi,(a,b,d) in enumerate(buckets):
    with gzip.open(f'{OUT}/ix/{bi:03d}.json.gz','wt',encoding='utf-8',compresslevel=9) as g: json.dump(d,g,ensure_ascii=False,separators=(',',':'))
    idxmap.append([a,b])
json.dump({'N':N,'shard':SH,'buckets':idxmap,'df':None},open(OUT+'/ix/map.json','w',encoding='utf-8'),ensure_ascii=False)
print('docs',N,'buckets',len(buckets),'shards',math.ceil(N/SH))
for t in themes: print(t['name'],t['count'])
print('verses',sum(1 for m in meta if m[6]),'places',collections.Counter(m[5] for m in meta).most_common(8))
