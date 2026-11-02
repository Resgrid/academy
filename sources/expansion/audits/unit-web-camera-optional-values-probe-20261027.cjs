/** Offline SDK option-contract probe. No browser, network, DOM or app mutation.
 * Run: node this-file.cjs --unit-root /path/to/Unit --source /path/to/map-view.web.tsx
 * Optional: --expect-invalid 8 (original) or --expect-invalid 0 (proposed fix).
 * Extracts the four actual Camera option object expressions, evaluates them
 * with bounded inputs, and invokes installed MapboxGL Map.prototype.jumpTo on
 * a minimal camera host. This tests numeric option handling, not map rendering.
 * easeTo's original object is checked with jumpTo's shared option-key contract;
 * this does not claim a rendered or live easeTo/browser operation was tested.
 */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { createRequire } = require('node:module');
const arg = (name) => { const i = process.argv.indexOf(name); return i < 0 ? null : process.argv[i + 1]; };
const unitRoot = path.resolve(arg('--unit-root') || '');
const sourcePath = path.resolve(arg('--source') || path.join(unitRoot, 'src/components/maps/map-view.web.tsx'));
if (!arg('--unit-root')) throw new Error('Supply --unit-root for the installed Unit dependencies.');
const requireUnit = createRequire(path.join(unitRoot, 'package.json'));
const mapbox = requireUnit('mapbox-gl');
const packagePath = requireUnit.resolve('mapbox-gl/package.json');
const sdkPath = requireUnit.resolve('mapbox-gl');
const sha = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');
const source = fs.readFileSync(sourcePath, 'utf8');
function expression(after, call) {
  const start = source.indexOf(after);
  const callStart = source.indexOf(call, start);
  const open = source.indexOf('{', callStart + call.length);
  if (start < 0 || callStart < 0 || open < 0) throw new Error(`Missing reviewed source shape: ${after}`);
  let depth = 0;
  for (let i = open; i < source.length; i += 1) {
    if (source[i] === '{') depth += 1;
    if (source[i] === '}') {
      depth -= 1;
      if (depth === 0) return source.slice(open, i + 1).replace(/ as \[number, number\]/g, '');
    }
  }
  throw new Error('Unbalanced source Camera options.');
}
const shapes = {
  imperative_setCamera: expression('setCamera: (options:', 'map.easeTo('),
  initial_defaultSettings: expression('const center = defaultSettings.centerCoordinate;', 'map.jumpTo('),
  initial_centerCoordinate: expression('// Handle centerCoordinate / zoomLevel changes', 'map.jumpTo('),
  controlled_centerCoordinate: expression('const cameraOptions =', '='),
};
const cases = [
  {name:'missing_heading_pitch',zoom:15,heading:undefined,pitch:undefined},
  {name:'all_optional_values_missing',zoom:undefined,heading:undefined,pitch:undefined},
  {name:'valid_zero_values',zoom:0,heading:0,pitch:0},
  {name:'defined_values',zoom:12,heading:45,pitch:20},
];
const results = [];
for (const [shape, objectSource] of Object.entries(shapes)) {
  const build = new Function('options','defaultSettings','center','centerCoordinate','zoomLevel','heading','pitch','animationDuration', `return (${objectSource});`);
  for (const sample of cases) {
    const point = [-87.6523,41.8721];
    const input = {centerCoordinate:point,zoomLevel:sample.zoom,heading:sample.heading,pitch:sample.pitch};
    const options = build(input,input,point,point,sample.zoom,sample.heading,sample.pitch,0);
    const host = {transform:{zoom:4,bearing:3,pitch:4,center:{lng:-119.7583809782715,lat:39.14086268299356}},stop(){},fire(){return this;}};
    mapbox.Map.prototype.jumpTo.call(host, options, {_programmatic:true});
    const values = {zoom:host.transform.zoom,bearing:host.transform.bearing,pitch:host.transform.pitch};
    const finite = Object.values(values).every(Number.isFinite);
    const expected = {zoom:sample.zoom === undefined ? 4 : sample.zoom,bearing:sample.heading === undefined ? 3 : sample.heading,pitch:sample.pitch === undefined ? 4 : sample.pitch};
    const retainedValues = finite && Object.entries(expected).every(([key,value])=>values[key]===value);
    results.push({shape,case:sample.name,option_keys:Object.keys(options),all_numeric_options_finite:finite,defined_and_zero_values_preserved:retainedValues,nonfinite_fields:Object.entries(values).filter(([,value])=>!Number.isFinite(value)).map(([key])=>key)});
  }
}
const invalid = results.filter((item)=>!item.all_numeric_options_finite).length;
const report = {schema_version:1,source_sha256:sha(source),mapbox_gl_version:JSON.parse(fs.readFileSync(packagePath,'utf8')).version,mapbox_gl_entry_sha256:sha(fs.readFileSync(sdkPath)),mapbox_gl_package_sha256:sha(fs.readFileSync(packagePath)),probe_sha256:sha(fs.readFileSync(__filename)),cases:results.length,nonfinite_results:invalid,results,limits:['Actual installed SDK jumpTo numeric option handling was invoked offline on a minimal host. No browser/DOM/map rendering or physical device operation.','These results establish an undefined-option contract defect or its removal, not that the observed Nevada rendering is fixed. Real UI retest is required.','The source object expressions are extracted unchanged except removal of the TypeScript tuple assertion; SDK easeTo was source-inspected rather than executed.']};
process.stdout.write(JSON.stringify(report,null,2)+'\n');
const expectedArg=arg('--expect-invalid');
if (expectedArg !== null && invalid !== Number(expectedArg)) process.exitCode=1;
if (results.some((item)=>['valid_zero_values','defined_values'].includes(item.case)&&!item.defined_and_zero_values_preserved)) process.exitCode=1;
