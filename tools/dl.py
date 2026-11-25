import re, sys, time, html, os, random, urllib.request
OUT='/mnt/project-files/besedi/tekstove'
os.makedirs(OUT, exist_ok=True)
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
lines=[l.rstrip('\n').split('\t') for l in open('/mnt/project-files/besedi/spisak_url.txt',encoding='utf-8')][:int(sys.argv[1])]
def clean(s):
    s=re.sub(r'<br\s*/?>','\n',s); s=re.sub(r'</p>','\n\n',s); s=re.sub(r'<[^>]+>','',s)
    s=html.unescape(s).replace('\r','').replace('\xa0',' '); s=re.sub(r'[ \t]+\n','\n',s); s=re.sub(r'\n{3,}','\n\n',s); return s.strip()
def fetch(url):
    for a in range(6):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA,'Accept-Language':'bg,en;q=0.8'}),timeout=60)
            return r.read().decode('utf-8')
        except Exception as e:
            w=10*(2**a); print('ERR',url,e,'wait',w,flush=True); time.sleep(w)
    return None
for n,date,url in lines:
    slug=url.rstrip('/').rsplit('/',1)[1]
    fn=f'{OUT}/{n}_{slug}.txt'[:250]
    if os.path.exists(fn) and os.path.getsize(fn)>200: continue
    h=fetch(url)
    if h is None: print('FAIL',n,url,flush=True); continue
    t=re.search(r'<h1[^>]*>(.*?)(<div|</h1>)',h,re.S); title=clean(t.group(1)) if t else ''
    m=re.search(r'<div class="text-base leading-6 md:text-lg md:leading-6">(.*?)</div>\s*</div>\s*</div>\s*</div>\s*</main>',h,re.S)
    if not m: print('NOBODY',n,url,flush=True); continue
    body=clean(m.group(1))
    open(fn,'w',encoding='utf-8').write(f'{title}\n{n} | {date}\n{url}\n\n{body}\n')
    print('OK',n,len(body),flush=True)
    time.sleep(1.5+random.random())
