import {bundle} from '@remotion/bundler';
const u=await bundle({entryPoint:new URL('./src/index.jsx',import.meta.url).pathname,outDir:new URL('./work/bundle',import.meta.url).pathname});console.log(u);
