import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderMedia,renderStill} from '@remotion/renderer';
const mode=process.argv[2]||'stills';
const serveUrl=await bundle({entryPoint:'/home/claude/ys/wk/mg/src/index.jsx'});
const b=await openBrowser('chrome',{browserExecutable:'/opt/pw-browsers/chromium-1243/chrome-linux64/chrome'});
const composition=await selectComposition({serveUrl,id:'Probe',puppeteerInstance:b});
if(mode==='stills'){for(const f of (process.argv[3]||'40,120,230,280,430,520,600,700,760').split(',').map(Number)){await renderStill({composition,serveUrl,output:`out/st_${f}.jpg`,frame:f,imageFormat:'jpeg',scale:0.5,puppeteerInstance:b,overwrite:true});}}
else{await renderMedia({composition,serveUrl,codec:'h264',outputLocation:'out/probe.mp4',puppeteerInstance:b,concurrency:2,crf:20,x264Preset:'veryfast'});}
await b.close({silent:true});console.log('ok');
