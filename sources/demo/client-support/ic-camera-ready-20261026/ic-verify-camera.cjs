#!/usr/bin/env node
// Pure camera configuration checks. No browser, map service, token or GPS use.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { createRequire } = require('node:module');
const target = path.resolve(process.argv[2] || path.join(__dirname, '../../../../../capture-apps/IC'));
const fromApp = createRequire(path.join(target, 'package.json'));
const ts = fromApp('typescript');
const React = fromApp('react');
const filename = path.join(target, 'src/components/maps/web-camera-settings.ts');
const output = ts.transpileModule(fs.readFileSync(filename, 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS, esModuleInterop: true, target: ts.ScriptTarget.ES2020 }, reportDiagnostics: true, fileName: filename });
assert.equal((output.diagnostics || []).filter(x => x.category === ts.DiagnosticCategory.Error).length, 0);
const moduleResult = { exports: {} };
vm.runInThisContext('(function(require, module, exports) {' + output.outputText + '\n})', { filename })(fromApp, moduleResult, moduleResult.exports);
const { findWebCameraDeclaration, resolveWebCameraSettings } = moduleResult.exports;
function Camera() { return null; }
const defaults = { centerCoordinate: [-87.6523, 41.8721], zoomLevel: 15, heading: 0, pitch: 0 };
const nested = React.createElement(React.Fragment, null, React.createElement('div'), React.createElement(Camera, { defaultSettings: defaults }));
assert.deepEqual(resolveWebCameraSettings(findWebCameraDeclaration(nested, Camera)), defaults);
const controlled = resolveWebCameraSettings({ defaultSettings: defaults, centerCoordinate: [-87.64, 41.88], zoomLevel: 0, heading: 90 });
assert.deepEqual(controlled.centerCoordinate, [-87.64, 41.88]);
assert.equal(controlled.zoomLevel, 0);
assert.equal(controlled.heading, 90);
assert.equal(controlled.pitch, 0);
assert.equal(findWebCameraDeclaration(React.createElement('div'), Camera), undefined);
console.log('PASS: native default camera coordinates, explicit overrides including zero values, and nested camera declarations. No provider or location access.');

// Test the readiness boundary with actual React refs/effects and a mock map only.
// These tests cannot establish visual/provider/GPS operation.
function loadTS(relative, overrides = {}) {
  const file = path.join(target, relative);
  const built = ts.transpileModule(fs.readFileSync(file, 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true, target: ts.ScriptTarget.ES2020 }, reportDiagnostics: true, fileName: file });
  assert.equal((built.diagnostics || []).filter(x => x.category === ts.DiagnosticCategory.Error).length, 0, relative);
  const result = { exports: {} };
  const localRequire = name => Object.hasOwn(overrides, name) ? overrides[name] : fromApp(name);
  vm.runInThisContext('(function(require, module, exports) {' + built.outputText + '\n})', { filename: file })(localRequire, result, result.exports);
  return result.exports;
}
const settingsModule = loadTS('src/components/maps/web-camera-settings.ts');
const bridgeModule = loadTS('src/components/maps/web-camera-bridge.ts');
const { createWebCameraBridge, readWebCameraChange } = bridgeModule;
const calls = [];
const mockMap = {
  easeTo: (...args) => calls.push(['easeTo', ...args]),
  flyTo: (...args) => calls.push(['flyTo', ...args]),
  fitBounds: (...args) => calls.push(['fitBounds', ...args]),
  jumpTo: (...args) => calls.push(['jumpTo', ...args]),
  getCenter: () => ({ lng: -87.6523, lat: 41.8721 }), getZoom: () => 13,
};
const bridge = createWebCameraBridge();
bridge.setCamera({ centerCoordinate: [-87.65, 41.87], zoomLevel: 4 });
bridge.setCamera({ centerCoordinate: [-87.64, 41.88], zoomLevel: 13, animationDuration: 0 });
assert.deepEqual(calls, []);
bridge.setMap(mockMap);
assert.deepEqual(calls, [['easeTo', { center: [-87.64, 41.88], zoom: 13, duration: 0 }, { _programmatic: true }]]);
bridge.setMap(mockMap);
assert.equal(calls.length, 1, 'ready notifications must not replay a consumed request');
bridge.setCamera({ zoomLevel: 0, heading: 0, pitch: 0, animationDuration: 0 });
assert.deepEqual(calls.at(-1)[1], { zoom: 0, bearing: 0, pitch: 0, duration: 0 });
const beforeInvalid = calls.length;
bridge.setCamera({ centerCoordinate: [NaN, 41.8] }); bridge.setCamera({ zoomLevel: Infinity });
bridge.flyTo({ center: [-87.6, NaN] }); bridge.fitBounds([-87.6, 41.9], [-87.7, NaN]);
assert.equal(calls.length, beforeInvalid, 'invalid coordinates must not manufacture a fallback');
bridge.setMap(null); bridge.flyTo([-87.63, 41.89], 0); assert.equal(calls.length, beforeInvalid);
bridge.setMap(mockMap); assert.deepEqual(calls.at(-1), ['flyTo', { center: [-87.63, 41.89], duration: 0 }, { _programmatic: true }]);
bridge.fitBounds([-87.6, 41.9], [-87.7, 41.8], [1, 2, 3, 4], 0);
assert.deepEqual(calls.at(-1), ['fitBounds', [[-87.7, 41.8], [-87.6, 41.9]], { padding: { top: 1, right: 2, bottom: 3, left: 4 }, duration: 0 }, { _programmatic: true }]);
assert.deepEqual(readWebCameraChange(mockMap, true), { properties: { isUserInteraction: true, center: [-87.6523, 41.8721], zoom: 13 } });
assert.equal(readWebCameraChange({ getCenter: () => ({ lng: NaN, lat: 0 }), getZoom: () => 1 }, false), undefined);

const TestRenderer = fromApp('react-test-renderer');
globalThis.IS_REACT_ACT_ENVIRONMENT = true;
let cameraMounts = 0; let layerMounts = 0;
function RefCamera() { React.useEffect(() => { cameraMounts++; }, []); return null; }
function Layer() { React.useEffect(() => { layerMounts++; }, []); return null; }
const nestedChildren = React.createElement(React.Fragment, null, React.createElement(RefCamera, { key: 'camera' }), React.createElement(Layer, { key: 'layer' }));
let tree;
TestRenderer.act(() => { tree = TestRenderer.create(React.createElement(React.Fragment, null, settingsModule.renderReadyWebMapChildren(nestedChildren, RefCamera, false))); });
assert.equal(cameraMounts, 1); assert.equal(layerMounts, 0);
TestRenderer.act(() => { tree.update(React.createElement(React.Fragment, null, settingsModule.renderReadyWebMapChildren(nestedChildren, RefCamera, true))); });
assert.equal(cameraMounts, 1, 'Camera ref must not remount/lose queued requests on load'); assert.equal(layerMounts, 1);
TestRenderer.act(() => tree.unmount());

function FakeMap() {}
FakeMap.prototype.unproject = function () { return null; };
const mapboxStub = { Map: FakeMap, LngLat: function(lng, lat) { this.lng = lng; this.lat = lat; } };
const view = loadTS('src/components/maps/map-view.web.tsx', {
  'mapbox-gl/dist/mapbox-gl.css': {}, 'mapbox-gl': mapboxStub,
  '@/lib/map-center': { useDepartmentMapCenter: () => ({ longitude: -87.6523, latitude: 41.8721 }) },
  '@/lib/mapbox-token': { onMapboxAccessTokenChange: () => undefined },
  './web-camera-settings': settingsModule, './web-camera-bridge': bridgeModule,
});
const actualRef = React.createRef(); const imperativeTarget = [-87.64, 41.88]; calls.length = 0;
function Parent({ readyMap }) {
  React.useEffect(() => actualRef.current.setCamera({ centerCoordinate: imperativeTarget, zoomLevel: 13, animationDuration: 0 }), []);
  return React.createElement(view.MapContext.Provider, { value: readyMap }, React.createElement(view.Camera, { ref: actualRef, defaultSettings: defaults }));
}
TestRenderer.act(() => { tree = TestRenderer.create(React.createElement(Parent, { readyMap: null })); });
assert.ok(actualRef.current); assert.equal(calls.length, 0);
TestRenderer.act(() => tree.update(React.createElement(Parent, { readyMap: mockMap })));
assert.deepEqual(calls.map(x => x[0]), ['jumpTo', 'easeTo'], 'source default initializes before queued incident recenter');
assert.deepEqual(calls[1][1], { center: imperativeTarget, zoom: 13, duration: 0 });
TestRenderer.act(() => tree.unmount());
console.log('PASS: real React camera refs mount before style readiness, layers wait, queued latest recenter survives load, finite real center/zoom callbacks, zero-valued camera settings and no synthetic geography. No browser/provider/location access.');
