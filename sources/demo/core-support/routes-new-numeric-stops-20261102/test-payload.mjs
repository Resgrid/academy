import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';

const root=path.dirname(fileURLToPath(import.meta.url));
const relative='Web/Resgrid.Web/wwwroot/js/app/internal/routes/resgrid.routes.new.js';
function exercise(stage,dwell,radius,location=true,name='Example') {
  const source=fs.readFileSync(path.join(root,stage,relative),'utf8');
  const addStart=source.indexOf("$('#saveStopBtn').on('click'");
  const submitStart=source.indexOf("$('form').on('submit'");
  const submitEnd=source.indexOf("$('#PendingStopsJson').val(JSON.stringify(stopsToSubmit));",submitStart);
  assert.ok(addStart>0 && submitStart>addStart && submitEnd>submitStart);
  const values={'#stopName':name,'#stopLat':location?'41.85':'','#stopLng':location?'-87.69':'','#stopType':'0','#stopPriority':'0','#stopDwellMinutes':dwell,'#stopGeofenceRadius':radius,'#stopContactName':'Training contact','#stopContactNumber':'312-555-0110','#stopNotes':'Fictional exercise','#stopContactId':'','#stopAddress':'Chicago, IL','#stopPlannedArrival':'','#stopPlannedDeparture':''};
  const handlers={},alerts=[];
  const jq=selector=>({on(event,handler){handlers[selector+':'+event]=handler;},val(...args){if(args.length){values[selector]=args[0];return this;}return values[selector];},modal(){}});
  jq.trim=value=>String(value??'').trim();
  const context=vm.createContext({$:jq,pendingStops:[],stopIdCounter:0,stopEditor:{refresh(){}},alert:message=>alerts.push(message)});
  vm.runInContext(source.slice(addStart,source.indexOf('// ── Serialize stops',addStart)),context);
  vm.runInContext(source.slice(submitStart,source.indexOf('});',submitEnd)+3),context);
  handlers['#saveStopBtn:click']();
  handlers['form:submit']();
  return {payload:JSON.parse(values['#PendingStopsJson']),alerts};
}
const original=exercise('before','10','75').payload[0];
assert.equal(typeof original.dwellMinutes,'string');
assert.equal(typeof original.geofenceRadius,'string');
const cases=[['10','75',10,75],['','',null,null],['0','0',0,0],['15','',15,null]];
for(const [dwell,radius,expectedDwell,expectedRadius] of cases){
  const {payload,alerts}=exercise('after',dwell,radius);
  assert.equal(alerts.length,0);assert.equal(payload.length,1);
  assert.equal(payload[0].dwellMinutes,expectedDwell);
  assert.equal(payload[0].geofenceRadius,expectedRadius);
  assert.equal(payload[0].latitude,41.85);assert.equal(payload[0].longitude,-87.69);
  assert.equal(payload[0].contactNumber,'312-555-0110');
}
for(const [location,name] of [[false,'Example'],[true,'']]){
  const result=exercise('after','10','75',location,name);
  assert.equal(result.payload.length,0);assert.equal(result.alerts.length,1);
}
console.log(JSON.stringify({status:'passed',original_numeric_type_failure_reproduced:true,corrected_payload_cases:cases.length,existing_required_field_guards:2,method:'Execute unchanged extracted Add Stop and submit handlers; inspect their serialized JSON.'},null,2));
