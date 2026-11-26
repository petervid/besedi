const {chromium}=require('playwright');const fs=require('fs');
const META=JSON.parse(fs.readFileSync('/home/user/besedi/meta.json'));const SL=JSON.parse(fs.readFileSync('/home/user/besedi/b/slugs.json'));
const OUT='/home/user/besedi/og/b';fs.mkdirSync(OUT,{recursive:true});
const only=process.argv[2]?process.argv[2].split(',').map(Number):null;
const fmtD=d=>{const m=d.match(/^(\d{4})-(\d\d)-(\d\d)$/);return m?`${+m[3]}.${m[2]}.${m[1]}`:d};
const rt=w=>{const m=Math.max(1,Math.round(w/200));return m<60?`≈ ${m} мин четене`:`≈ ${Math.floor(m/60)} ч ${m%60?m%60+' мин ':''}четене`};
const N=n=>n.toLocaleString('bg-BG').replace(/ | /g,' ');
(async()=>{const b=await chromium.launch();const idx=only||META.map((_,i)=>i);let next=0,done=0;const t0=Date.now();
async function worker(){const p=await b.newPage({viewport:{width:1200,height:630},deviceScaleFactor:1});await p.goto('http://localhost:8765/ogtpl.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
 while(next<idx.length){const i=idx[next++];const m=META[i];const eb=['Беседа',fmtD(m[1]),m[5]].filter(Boolean).join(' · ');
  await p.evaluate(([a,t,r])=>fill(a,t,r),[eb,m[2].split(' / ')[0].trim(),`${rt(m[4])} · ${N(m[4])} думи`]);
  await p.screenshot({path:`${OUT}/${SL[i]}.jpg`,type:'jpeg',quality:70,clip:{x:0,y:0,width:1200,height:630}});
  if(++done%250===0)console.log(done,Math.round((Date.now()-t0)/1000)+'s')}}
await Promise.all([1,2,3,4].map(worker));await b.close();console.log('done',done)})();
