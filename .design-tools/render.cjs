// Design export tooling only. No desktop application code.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const root = path.resolve(__dirname, '..');
const output = path.join(root, 'assets', 'mockups');
const preview = pathToFileURL(path.join(output, 'review.html')).href;
const screens = ['dashboard','file','live','library','prompts','settings','trash'];
const report = { screenshots: [], errors: [], geometry: [], contrasts: [], shellChecks: [] };
function luminance(hex) {const c=hex.match(/[0-9a-f]{2}/gi).map(x=>parseInt(x,16)/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return .2126*c[0]+.7152*c[1]+.0722*c[2]}
function ratio(a,b){const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
(async()=>{
  const browser = await chromium.launch({executablePath:'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',headless:true});
  const page = await browser.newPage({viewport:{width:1600,height:1000},deviceScaleFactor:1});
  page.on('pageerror', e=>report.errors.push(e.message));
  async function capture(name, query, fullPage=false) {
    await page.goto(preview+'?'+new URLSearchParams(query));
    await page.evaluate(()=>document.fonts.ready);
    await page.screenshot({path:path.join(output,name+'.png'),fullPage});
    report.screenshots.push(name+'.png');
    const geometry=await page.evaluate(()=>({width:innerWidth,body:document.documentElement.scrollWidth,main:document.getElementById('main')?{height:document.getElementById('main').clientHeight,scroll:document.getElementById('main').scrollHeight}:null}));
    report.geometry.push({name,...geometry});
  }
  for(const [palette,mode,prefix] of [['pastel','light','v2-light'],['pastel','dark','v2-dark']]){
    for(let i=0;i<screens.length;i++)await capture(`${prefix}-${String(i+1).padStart(2,'0')}-${screens[i]}`,{palette,mode,screen:screens[i]});
  }
  await page.goto(preview+'?screen=dashboard');
  const bodyBounds=await page.locator('.app-body').boundingBox();
  await page.screenshot({path:path.join(output,'v2-sidebar-detail.png'),clip:{x:bodyBounds.x,y:bodyBounds.y,width:304,height:bodyBounds.height}});
  report.screenshots.push('v2-sidebar-detail.png');
  await capture('v2-00-brand-board',{screen:'brand',palette:'pastel',mode:'light'},true);
  for(const kind of ['purge-version','purge-audio','last-version'])await capture('v2-dialog-'+kind,{screen:'trash',palette:'pastel',mode:'light',dialog:kind});
  for(const width of [1366,1024,768,390]) {
    await page.setViewportSize({width,height:900});
    for(const screen of screens){
      await page.goto(preview+'?'+new URLSearchParams({screen,palette:'pastel',mode:'light'}));
      const issue=await page.evaluate(()=>({bodyOverflow:document.documentElement.scrollWidth-innerWidth,mainOverflow:(()=>{const m=document.getElementById('main');return m?m.scrollWidth-m.clientWidth:0})()}));
      report.geometry.push({name:'layout-'+width+'-'+screen,...issue});
    }
  }
  // Verify the reported browser viewport and real navigation between tabs.
  for(const viewport of [{width:1920,height:912},{width:1600,height:900},{width:1366,height:768},{width:1280,height:720}]){
    await page.setViewportSize(viewport);
    await page.goto(preview+'?screen=dashboard');
    let reference;
    for(const screen of screens){
      await page.locator('.nav button[data-screen="'+screen+'"]:not(.rail-avatar):not(.rail-login)').click();
      const geometry=await page.evaluate(()=>{
        const context=document.getElementById('context-panel'),sidebar=document.getElementById('sidebar'),main=document.getElementById('main');
        const panel=context.getBoundingClientRect(),rail=sidebar.getBoundingClientRect();
        const controls=[...context.querySelectorAll('input,select,textarea,button')].map(node=>node.getBoundingClientRect());
        return {screen:new URLSearchParams(location.search).get('screen'),viewport:[innerWidth,innerHeight],leftWidth:panel.right-rail.left,contextWidth:panel.width,mainLeft:main.getBoundingClientRect().left,contextHeight:context.clientHeight,contextContent:context.scrollHeight,contextOverflow:getComputedStyle(context).overflowY,controlsFit:controls.every(rect=>rect.top>=panel.top&&rect.bottom<=panel.bottom)};
      });
      if(!reference)reference=geometry;
      if(geometry.leftWidth!==reference.leftWidth||geometry.contextWidth!==reference.contextWidth||geometry.mainLeft!==reference.mainLeft)report.errors.push('Shell changed size on '+screen+' at '+viewport.width);
      if(geometry.contextContent>geometry.contextHeight+1||['auto','scroll'].includes(geometry.contextOverflow)||!geometry.controlsFit)report.errors.push('Context needs scrolling or clips controls on '+screen+' at '+viewport.width);
      report.shellChecks.push(geometry);
      if(viewport.width===1920&&['dashboard','file'].includes(screen)){
        await page.mouse.move(viewport.width-24,24);
        await page.screenshot({path:path.join(output,'v2-layout-'+screen+'-1920.png'),animations:'disabled'});
      }
    }
  }
  await page.setViewportSize({width:1600,height:1000});
  // Check that review-only interactions and the destructive scope previews work.
  await page.goto(preview+'?screen=dashboard');
  await page.locator('.nav [data-screen="file"]').click();
  if(!page.url().includes('screen=file'))report.errors.push('Sidebar navigation failed');
  await page.goto(preview+'?screen=settings');
  if(await page.locator('[data-model]').count()!==8)report.errors.push('Curated model list incomplete');
  await page.locator('[data-model="GPT-6 Luna"]').click();
  if(await page.locator('[data-model="GPT-6 Luna"]').getAttribute('aria-pressed')!=='true')report.errors.push('Model preview selection failed');
  await page.goto(preview+'?screen=library');
  await page.locator('#library-search').fill('research');
  if(await page.locator('[data-audio]').count()!==1)report.errors.push('Library preview search failed');
  await page.goto(preview+'?screen=trash&dialog=last-version');
  if(await page.locator('#delete-audio-too').isChecked())report.errors.push('Last version dialog must retain audio by default');
  await page.keyboard.press('Escape');
  if(await page.locator('#modal').evaluate(x=>x.open))report.errors.push('Escape must dismiss dialog');
  for(const palette of ['pastel'])for(const mode of ['light','dark']){
    await page.goto(preview+'?'+new URLSearchParams({screen:'live',palette,mode}));
    const colors=await page.evaluate(()=>{const s=getComputedStyle(document.documentElement),out={};for(const k of ['text','muted','primary','on-primary','bg','panel','tint','line','danger','danger-bg','warn','warn-bg','success','success-bg','info','info-bg','interim','pink','pink-ink','lavender','lavender-ink','yellow','yellow-ink','cyan','cyan-ink','rail','rail-muted'])out[k]=s.getPropertyValue('--'+k).trim();return out});
    for(const [fg,bg] of [['text','panel'],['muted','panel'],['muted','bg'],['muted','tint'],['primary','tint'],['primary','panel'],['on-primary','primary'],['danger','danger-bg'],['warn','warn-bg'],['success','success-bg'],['info','info-bg'],['interim','panel'],['pink-ink','pink'],['lavender-ink','lavender'],['yellow-ink','yellow'],['cyan-ink','cyan'],['rail-muted','rail']]){const value=ratio(colors[fg],colors[bg]);report.contrasts.push({palette,mode,pair:fg+'/'+bg,ratio:+value.toFixed(2),pass:value>=4.5})}
  }
  // Build a durable contact sheet from the exported screen images.
  const thumbs=report.screenshots.filter(x=>/^v2-(light|dark)-\d/.test(x));
  const rows=screens.map((screen,i)=>[thumbs.find(x=>x.startsWith('v2-light-'+String(i+1).padStart(2,'0'))),thumbs.find(x=>x.startsWith('v2-dark-'+String(i+1).padStart(2,'0')))]);
  const labels=['Trang chủ','Dịch file ghi âm','Ghi âm trực tiếp','Thư viện & phiên bản','Prompt & Thuật ngữ','Cài đặt & Codex CLI','Thùng rác'];
  const sheet=`<!doctype html><html lang="vi"><meta charset="utf-8"><style>*{box-sizing:border-box}body{margin:0;padding:42px;background:#f6f5f7;color:#292633;font:16px 'Segoe UI',sans-serif}h1{font-size:34px;margin:8px 0 10px}p{color:#696471;margin:0 0 28px}.head,.grid{display:grid;grid-template-columns:1fr 1fr;gap:28px}.head{font-size:20px;margin:25px 0 8px}.item{margin-top:19px}.item strong{display:block;margin-bottom:10px;font-size:17px}img{width:100%;display:block;border-radius:6px;border:1px solid #e9e6ed}.kicker{font-size:12px;letter-spacing:2px;color:#85536c}</style><span class="kicker">CHINESE TRANSCRIBER · GIAI ĐOẠN 1</span><h1>Thiết kế V2 · Theo mẫu sidebar mới.</h1><p>Thiết kế để duyệt · Dữ liệu minh họa · Chưa triển khai ứng dụng</p><div class="head"><strong>Pastel & Graphite / Sáng</strong><strong>Pastel & Graphite / Tối</strong></div><div class="grid">${rows.flatMap((pair,i)=>pair.map(x=>`<div class="item"><strong>0${i+1} · ${labels[i]}</strong><img src="data:image/png;base64,${fs.readFileSync(path.join(output,x)).toString('base64')}"></div>`)).join('')}</div></html>`;
  await page.setViewportSize({width:2400,height:1000});await page.setContent(sheet);await page.screenshot({path:path.join(output,'v2-00-screen-overview.png'),fullPage:true});
  fs.writeFileSync(path.join(output,'qa-report.json'),JSON.stringify(report,null,2));
  await browser.close();
  console.log(JSON.stringify({exported:report.screenshots.length+3,shellChecks:report.shellChecks.length,errors:report.errors,overflows:report.geometry.filter(x=>x.bodyOverflow>1||x.mainOverflow>1),contrastFailures:report.contrasts.filter(x=>!x.pass),scrolling:report.geometry.filter(x=>x.main&&x.main.scroll>x.main.height+3)},null,2));
})();
