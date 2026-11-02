/** Offline installed-SDK Camera + real Transform probe; never constructs a Map/WebGL/browser.
 * node this-file.cjs --unit-root /path/to/Unit --source /path/to/map-view.web.tsx --expect-invalid 0
 * For testing only, exposes two internal classes from the installed unminified SDK
 * in memory. Original SDK/app files are never changed. Animation is forced to0 so
 * real Camera jump/ease/fly paths execute synchronously without a render loop.
 */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),Module=require('node:module');
const arg=(name)=>{const i=process.argv.indexOf(name);return i<0?null:process.argv[i+1];};
if(!arg('--unit-root'))throw new Error('Supply --unit-root.');
const unit=path.resolve(arg('--unit-root')),sourcePath=path.resolve(arg('--source')||path.join(unit,'src/components/maps/map-view.web.tsx'));
const req=Module.createRequire(path.join(unit,'package.json'));const sdkPath=req.resolve('mapbox-gl/dist/mapbox-gl-unminified.js');
const originalSDK=fs.readFileSync(sdkPath,'utf8');
if((originalSDK.match(/return exported;/g)||[]).length!==1)throw new Error('Installed SDK internal export location changed; inspect before rerunning.');
const testSDK=originalSDK.replace('return exported;','exported.__academyTransform=Transform; exported.__academyCamera=Camera; return exported;');
const loaded=new Module(sdkPath,module);loaded.filename=sdkPath;loaded.paths=Module._nodeModulePaths(unit);loaded._compile(testSDK,sdkPath);const sdk=loaded.exports;
const source=fs.readFileSync(sourcePath,'utf8');const sha=(v)=>crypto.createHash('sha256').update(v).digest('hex');
function expression(after,call){const start=source.indexOf(after),invoke=source.indexOf(call,start),open=source.indexOf('{',invoke+call.length);if(start<0||invoke<0||open<0)throw new Error('Reviewed Camera source shape changed.');let depth=0;for(let i=open;i<source.length;i++){if(source[i]==='{')depth++;if(source[i]==='}'&&--depth===0)return source.slice(open,i+1).replace(/ as \[number, number\]/g,'');}throw new Error('Unbalanced options.');}
const shapes={imperative_setCamera:{method:'easeTo',body:expression('setCamera: (options:','map.easeTo(')},initial_defaultSettings:{method:'jumpTo',body:expression('const center = defaultSettings.centerCoordinate;','map.jumpTo(')},initial_centerCoordinate:{method:'jumpTo',body:expression('// Handle centerCoordinate / zoomLevel changes','map.jumpTo(')},controlled_easeTo:{method:'easeTo',body:expression('const cameraOptions =','=')},controlled_flyTo:{method:'flyTo',body:expression('const cameraOptions =','=')}};
const cases=[{name:'missing_orientation',zoom:15},{name:'missing_all_optional'},{name:'valid_zero',zoom:0,heading:0,pitch:0},{name:'defined',zoom:12,heading:45,pitch:20}];
const results=[];
for(const[shape,entry]of Object.entries(shapes)){
 const build=new Function('options','defaultSettings','center','centerCoordinate','zoomLevel','heading','pitch','animationDuration',`return (${entry.body});`);
 for(const sample of cases){const point=[-87.6523,41.8721],input={centerCoordinate:point,zoomLevel:sample.zoom,heading:sample.heading,pitch:sample.pitch};const options=build(input,input,point,point,sample.zoom,sample.heading,sample.pitch,0);
  const transform=new sdk.__academyTransform(0,22,0,85,true,{name:'mercator'});transform.resize(1434,829);const camera=new sdk.__academyCamera(transform,{bearingSnap:7,respectPrefersReducedMotion:false});camera.jumpTo({center:[-119.7583809782715,39.14086268299356],zoom:4,bearing:3,pitch:4});
  let error=null;try{camera[entry.method]({...options,duration:0,animate:false},{_programmatic:true});}catch(e){error={name:e.name,message:e.message};}
  const numeric=[transform.zoom,transform.bearing,transform.pitch,transform.center.lng,transform.center.lat];const matrixFinite=Array.from(transform.pixelMatrix).every(Number.isFinite);const finite=error===null&&numeric.every(Number.isFinite)&&matrixFinite;
  results.push({shape,method:entry.method,case:sample.name,requested_numeric_values:{zoom:sample.zoom??null,bearing:sample.heading??null,pitch:sample.pitch??null},option_keys:Object.keys(options),finite_transform_and_pixel_matrix:finite,pixel_matrix_finite:matrixFinite,actual_center:[transform.center.lng,transform.center.lat],actual_zoom:transform.zoom,actual_bearing:transform.bearing,actual_pitch:transform.pitch,error,zero_zoom_note:sample.zoom===0?'Real Transform may constrain zoom0 to the viewport/world bounds; the option must remain defined0 and all resulting state/matrices finite.':null});
 }
}
const invalid=results.filter(x=>!x.finite_transform_and_pixel_matrix).length;
const report={schema_version:1,source_sha256:sha(source),installed_sdk_version:JSON.parse(fs.readFileSync(req.resolve('mapbox-gl/package.json'),'utf8')).version,installed_unminified_sdk_sha256:sha(originalSDK),probe_sha256:sha(fs.readFileSync(__filename)),cases:results.length,invalid_results:invalid,results,limits:['Uses the installed SDK real Camera and real Mercator Transform/matrix calculations, exposed only in memory. No application/SDK source file is edited.','Animation duration is0 for deterministic offline execution; no renderer, WebGL, tile/style load, GPS, browser session or runtime bundle inspection.','A passing SDK contract does not prove the actual loaded browser bundle or cartography has refreshed. CI-mode Metro source changes require a normal explicit restart; source-only fixes are not qualified screenshots.']};
process.stdout.write(JSON.stringify(report,null,2)+'\n');if(arg('--expect-invalid')!==null&&invalid!==Number(arg('--expect-invalid')))process.exitCode=1;
