// Run the actual store against the current Core response envelope, without a live API.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const target=path.resolve(process.argv[2]||'');
assert(target.endsWith('/capture-apps/Unit-records'),'Use the isolated recording copy.');
const nativeRequire=createRequire(path.join(target,'package.json'));
const ts=nativeRequire('typescript');
const fixture={Data:{Instance:{RouteInstanceId:'753b31f0-9092-4631-95b9-44a7722f9eed',RoutePlanId:'0383ecbd-5334-47ed-bde3-55d1337f9408',Status:1,UnitId:51008,StopsCompleted:1,StopsTotal:2},TotalStops:2,CompletedStops:1,PendingStops:1,SkippedStops:0,Stops:[]}};
async function run(file){
 const output=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
 const exports={};const calls=[];
 const require=name=>name==='@/api/routes/routes'?{getRouteProgress:async id=>{calls.push(id);return structuredClone(fixture);}}:nativeRequire(name);
 vm.runInNewContext(output,{exports,require,console,setTimeout,clearTimeout,setInterval,clearInterval},{filename:file});
 const store=exports.useRoutesStore;
 store.setState({activeInstance:{...fixture.Data.Instance,StopsCompleted:0}});
 await store.getState().fetchRouteProgress(fixture.Data.Instance.RouteInstanceId);
 return {state:store.getState(),calls};
}
const file='src/stores/routes/store.ts';
const before=await run(path.join(here,'before',file));
assert.equal(before.state.activeInstance.RouteInstanceId,undefined);
console.log('PASS original progress poll loses the instance ID with the current Core envelope');
const after=await run(path.join(target,file));
assert.equal(after.state.activeInstance.RouteInstanceId,fixture.Data.Instance.RouteInstanceId);
assert.equal(after.state.activeInstance.UnitId,51008);
assert.equal(after.state.activeInstance.StopsCompleted,1);
assert.equal(after.state.activeInstance.Status,1);
assert.deepEqual(after.calls,[fixture.Data.Instance.RouteInstanceId]);
assert.equal(after.state.activeInstance.Instance,undefined);
console.log('PASS real store retains the exact instance ID, unit, status and fresh progress');
console.log('PASS the API is called with the same route ID; the wrapper is not stored as an instance');
