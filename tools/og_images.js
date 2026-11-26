const {chromium}=require('playwright');const fs=require('fs');
const TH=JSON.parse(fs.readFileSync('site2/themes.json'));
const routes=[...['temi','balgaria','paneuritmia','slovo','hronologia','stihove'].map(r=>[r,r]),...TH.map(t=>['tema-'+t.id,t.id])];
const only=process.argv[2];
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:1200,height:630},deviceScaleFactor:1,colorScheme:'light',reducedMotion:'reduce'});const pg=await ctx.newPage();
fs.mkdirSync('site2/og',{recursive:true});
for(const [r,name] of routes){if(only&&!r.includes(only))continue;
 await pg.goto('http://localhost:8765/test.html#'+r);await pg.waitForSelector('.hero h1');await pg.waitForTimeout(r.startsWith('tema')?600:1200);
 await pg.evaluate(()=>{document.querySelector('header').style.display='none';document.querySelectorAll('.crumbs,#totop,.skip').forEach(e=>e.remove());
  const h=document.querySelector('.hero');[...h.parentNode.children].forEach(e=>{if(e!==h)e.style.display='none'});
  Object.assign(h.style,{borderRadius:'0',margin:'0',width:'1200px',height:'630px',boxSizing:'border-box',display:'flex',alignItems:'center',padding:'0 70px',border:'0'});
  const inn=h.querySelector('.hero-in');if(inn)Object.assign(inn.style,{width:'100%',display:'grid',gridTemplateColumns:'minmax(0,1fr) 310px',gap:'50px',alignItems:'center'});
  const h1=h.querySelector('h1');h1.style.fontSize=h1.textContent.length>26?'68px':'84px';h1.style.lineHeight='1.04';
  const l=h.querySelector('.lede');if(l){let t=l.textContent.trim();if(t.length>170){const ss=t.match(/[^.!?]+[.!?]+/g)||[t];t='';for(const x of ss){if((t+x).length>170&&t)break;t+=x}}l.textContent=t.trim();l.style.fontSize='27px';l.style.maxWidth='640px';l.style.lineHeight='1.4'}
  h.querySelectorAll('.toc,.acts,.stats,.tiles,form,.btn,.examples').forEach(e=>e.remove());
  const ey=h.querySelector('.eyebrow');if(ey)ey.style.fontSize='19px';
  const emb=h.querySelector('.hero-emb');if(emb)Object.assign(emb.style,{width:'310px',height:'auto',margin:'0',order:'2',position:'static',transform:'none'});
  const u=document.createElement('p');u.textContent='petervid.github.io/besedi · Беседите на Учителя';Object.assign(u.style,{position:'absolute',left:'70px',bottom:'34px',margin:0,font:'600 19px var(--ui)',color:'var(--muted)',letterSpacing:'.02em'});h.style.position='relative';h.appendChild(u);
  const m=document.querySelector('main');m.style.padding='0';m.style.maxWidth='none';document.body.style.paddingTop='0';window.scrollTo(0,0)});
 await pg.waitForTimeout(500);await (await pg.$('.hero')).screenshot({path:`site2/og/${name}.jpg`,type:'jpeg',quality:86});console.log(r)}
await b.close()})();
