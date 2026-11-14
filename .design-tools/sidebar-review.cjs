const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1600,height:1000}});
 const base=pathToFileURL(path.resolve('assets/mockups/review.html')).href;
 const checks=[];
 for(const screen of ['dashboard','file','live','library','prompts','settings','trash']){
  await page.goto(base+'?screen='+screen);
  checks.push(await page.evaluate(()=>{
   const nav=document.querySelector('.nav').getBoundingClientRect(),active=document.querySelector('.nav [aria-current]').getBoundingClientRect();
   return {screen:new URLSearchParams(location.search).get('screen'),activeOffset:Math.round((active.x+active.width/2)-(nav.x+nav.width/2)),selectionInsideRail:active.x+active.width-4<=nav.right,menuCount:document.querySelectorAll('.rail-menu,[data-action="toggle-context"]').length,pathReady:!!document.querySelector('.rail-surface path').getAttribute('d')};
  }));
 }
 await page.goto(base+'?screen=live');
 await page.locator('#sidebar').screenshot({path:'assets/mockups/v2-sidebar-refined.png'});
 const railBox=await page.locator('.nav').boundingBox();
 const selected=await page.locator('.nav [aria-current]').boundingBox();
 await page.screenshot({path:'assets/mockups/v2-sidebar-notch.png',clip:{x:railBox.x-12,y:selected.y-22,width:railBox.width+26,height:80},scale:'css'});
 if(checks.some(x=>x.activeOffset!==8||!x.selectionInsideRail||!x.pathReady||x.menuCount))throw Error('Reference selection pocket or menu removal failed');
 console.log(JSON.stringify({sidebar:checks},null,2));
 await browser.close();
})();
