// Exercise the actual API adapter against current Core response contracts.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const target=path.resolve(process.argv[2]||'');
assert(target.endsWith('/capture-apps/Unit-records'));
const requireNative=createRequire(path.join(target,'package.json'));
const ts=requireNative('typescript');
const fc={type:'FeatureCollection',features:[{type:'Feature',properties:{name:'Fictional room'},geometry:{type:'Polygon',coordinates:[[[1,2],[2,2],[2,3],[1,2]]]}}]};
const map={IndoorMapId:'demo-map',Name:'Fictional map',CenterLatitude:39,CenterLongitude:-104,BoundsNELat:39.1,BoundsNELon:-103.9,BoundsSWLat:38.9,BoundsSWLon:-104.1};
const floors=[{IndoorMapFloorId:'demo-floor',Name:'Ground',FloorOrder:0}];
const fixtures={
 '/Mapping/GetAllActiveLayers':{Data:[{Id:'3',Name:'Fictional layer',LayerSource:'maplayer',Type:0,Color:'#0080ff',IsOnByDefault:true}]},
 '/Mapping/GetIndoorMap':{Data:{Map:map,Floors:floors}},
 '/Mapping/GetMapLayerGeoJSON':fc,
 '/Mapping/GetIndoorMapZonesGeoJSON':fc,
 '/Mapping/GetCustomMapRegionsGeoJSON':fc,
};
function load(file){
 const calls=[];
 const request=async (endpoint,params)=>{calls.push({endpoint,params});const key=Object.keys(fixtures).find(k=>endpoint===k||endpoint.startsWith(k+'/'));return {data:structuredClone(fixtures[key])};};
 const factory=endpoint=>({get:async params=>request(endpoint,params)});
 const exports={};
 const require=name=>name.includes('/common/')?{api:{get:request},createApiEndpoint:factory,createCachedApiEndpoint:factory}:{};
 const text=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
 vm.runInNewContext(text,{exports,require,console,encodeURIComponent},{filename:file});
 return {api:exports,calls};
}
const old=load(path.join(here,'before/src/api/mapping/mapping.ts')).api;
assert.equal((await old.getAllActiveLayers()).Data[0].LayerId,undefined);
assert.equal((await old.getIndoorMap('demo-map')).Data.IndoorMapId,undefined);
assert.equal((await old.getMapLayerGeoJSON('3')).Data,undefined);
console.log('PASS reproduced original missing layer ID, nested-map and raw-GeoJSON mismatches');
const {api,calls}=load(path.join(target,'src/api/mapping/mapping.ts'));
const layer=(await api.getAllActiveLayers()).Data[0];
assert.equal(layer.LayerId,'3');assert.equal(layer.Source,'maplayer');assert.equal(layer.IsOnByDefault,true);
const detail=(await api.getIndoorMap('demo-map')).Data;
assert.equal(detail.IndoorMapId,map.IndoorMapId);
assert.equal(detail.Floors[0].IndoorMapFloorId,'demo-floor');
assert.equal(detail.BoundsNELatitude,39.1);assert.equal(detail.BoundsSWLongitude,-104.1);
for(const method of ['getMapLayerGeoJSON','getIndoorMapZonesGeoJSON','getCustomMapRegionsGeoJSON']){
 const result=await api[method]('3');assert.equal(JSON.stringify(result.Data),JSON.stringify(fc));
}
assert(calls.some(c=>c.endpoint==='/Mapping/GetMapLayerGeoJSON/3'&&c.params===undefined));
fixtures['/Mapping/GetMapLayerGeoJSON']={type:'Unexpected',features:[]};
await assert.rejects(api.getMapLayerGeoJSON('3'),/Invalid GeoJSON/);
console.log('PASS actual adapter preserves Core identifiers, map/floor envelope and all exact GeoJSON coordinates/properties');
assert(calls.some(c=>c.endpoint==='/Mapping/GetIndoorMap/demo-map'));
console.log('PASS current Core path parameters are used; malformed GeoJSON is rejected');
