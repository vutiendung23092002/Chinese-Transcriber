// Consolidate the approved-to-revise mockup source files, without app code.
const fs=require('fs');
let base=fs.readFileSync('assets/mockups/review.js','utf8');
let revision=fs.readFileSync('assets/mockups/reference-v2.js','utf8');
const originalRender=base.split('\n').find(line=>line.startsWith('function render()'));
if(!originalRender)throw new Error('Original mockup renderer not found');
let updatedRender=originalRender.replace("document.getElementById('main').scrollTop=0", "placeConfig();if(screen==='settings'){['codex-connect','codex-guide','codex-quota'].forEach((id,i)=>document.querySelectorAll('.settings-section')[i].id=id);document.querySelector('.settings-models').id='codex-models'}document.getElementById('main').scrollTop=0");
base=base.split('\n').filter(line=>!/^function (logo|shell|dashboard|mini|brand|render)\(/.test(line)&&!line.startsWith("render();if(params.get")).join('\n');
const wrapperStart=revision.indexOf('const renderOriginalV2=render;');
const wrapperEnd=revision.indexOf("window.addEventListener('resize',placeConfig);",wrapperStart);
if(wrapperStart<0||wrapperEnd<0)throw new Error('V2 renderer wrapper not found');
revision=revision.slice(0,wrapperStart)+updatedRender+'\n'+revision.slice(wrapperEnd);
revision=revision.replace(/render\(\);\s*$/, "render();if(params.get('dialog'))showDialog(params.get('dialog'));\n");
fs.writeFileSync('assets/mockups/review.js',base+'\n'+revision,'utf8');
let css=fs.readFileSync('assets/mockups/review.css','utf8');
css+='\n'+fs.readFileSync('assets/mockups/reference-v2.css','utf8');
fs.writeFileSync('assets/mockups/review.css',css,'utf8');
let html=fs.readFileSync('assets/mockups/review.html','utf8');
html=html.replace('<link rel="stylesheet" href="reference-v2.css">','').replace('<script src="reference-v2.js"></script>','');
fs.writeFileSync('assets/mockups/review.html',html,'utf8');
// Keep drafting sources in the revision archive, outside the active preview.
fs.mkdirSync('assets/mockups/archive/v2-draft',{recursive:true});
for(const name of ['reference-v2.js','reference-v2.css'])fs.renameSync('assets/mockups/'+name,'assets/mockups/archive/v2-draft/'+name);
console.log('Consolidated V2 into review.html, review.css and review.js.');
