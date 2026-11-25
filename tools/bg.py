import os,re,json,sys,collections
D='data/tekstove'
meta=json.load(open('site2/meta.json'))
files=sorted(os.listdir(D))
BG=re.compile(r'българ|славян|бълг\.',re.I)
CAT={
'mission':r'мисия|призван|назначени|роля|предназначени|задача|избран|служ',
'new':r'нов[аио]т?[аи]? (?:епоха|време|култура|раса)|шестата раса|бъдеще|новото|иде|идва|настъп|царството',
'trials':r'мъчнотии|изпитани|страдани|войн|катастроф|криза|беди|тежк|скръб|минат|преминат',
'nature':r'недостат|добродетел|качеств|характер|завист|раздор|пороци|упорит|трудолюб|сърцат|сила|слабост',
'world':r'човечество|светът|целия свят|народите|всички народи|братство|световн|други народи|духа',
}
CR={k:re.compile(v,re.I) for k,v in CAT.items()}
docs=collections.Counter(); out=[]
for i,f in enumerate(files):
    body=open(os.path.join(D,f),encoding='utf-8').read().split('\n',4)[-1]
    paras=[p.strip() for p in re.split(r'\n\s*\n',body) if p.strip()]
    for k,p in enumerate(paras):
        n=len(BG.findall(p))
        if not n: continue
        docs[i]+=n
        sc={c:len(r.findall(p)) for c,r in CR.items()}
        out.append(dict(i=i,k=k,n=n,len=len(p),sc=sc,p=p))
print('paras',len(out),'docs',len(docs))
json.dump(out,open('bgparas.json','w'),ensure_ascii=False)
print([ (meta[i][0],meta[i][2][:40],c) for i,c in docs.most_common(25)])
