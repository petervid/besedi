import os,gzip,base64,sys
SRC='site2'; OUT=sys.argv[1]
html=open(f'{SRC}/index.html',encoding='utf-8').read()
a="    const r=await fetch(path); if(!r.ok) throw new Error(path+' '+r.status);\n    const buf=new Uint8Array(await r.arrayBuffer());"
b="""    let buf;const el=document.querySelector(`script[data-p="${path}"]`);
    if(el){const bin=atob(el.textContent.trim());buf=new Uint8Array(bin.length);for(let k=0;k<bin.length;k++)buf[k]=bin.charCodeAt(k)}
    else{const r=await fetch(path); if(!r.ok) throw new Error(path+' '+r.status);buf=new Uint8Array(await r.arrayBuffer())}"""
assert a in html; html=html.replace(a,b,1)
a2="\n(async()=>{\n  try{[META,MAP,THEMES]"
assert a2 in html; html=html.replace(a2,"\nwindow.addEventListener('DOMContentLoaded',async()=>{\n  try{[META,MAP,THEMES]",1)
a3="  route().then(()=>{const c=crumbs();if(c)app.insertAdjacentHTML('afterbegin',c)});\n})();"
assert a3 in html; html=html.replace(a3,"  route().then(()=>{const c=crumbs();if(c)app.insertAdjacentHTML('afterbegin',c)});\n});",1)
html=html.replace('<meta name="claude:viewport-fit-sides" content="cover">\n','')
files=['meta.json','themes.json','verses.json','bulgaria.json','ix/map.json']+['ix/'+f for f in sorted(os.listdir(f'{SRC}/ix')) if f!='map.json']+['t/'+f for f in sorted(os.listdir(f'{SRC}/t'))]
with open(OUT,'w',encoding='utf-8') as o:
    o.write('<!doctype html>\n<html lang="bg">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n')
    head_end=html.index('<header class="top">')
    o.write(html[:head_end]); o.write('</head>\n<body>\n'); o.write(html[head_end:])
    for f in files:
        data=gzip.compress(open(f'{SRC}/{f}','rb').read(),9)
        o.write(f'\n<script type="application/octet-stream" data-p="{f}">'+base64.b64encode(data).decode()+'</script>')
    o.write('\n</body>\n</html>\n')
print(os.path.getsize(OUT)/1e6,'MB')
