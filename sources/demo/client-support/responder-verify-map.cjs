#!/usr/bin/env node
// Offline adapter-contract checks. Synthetic events are tests, never capture proof.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = process.argv[2] || path.resolve(__dirname, '../../../../capture-apps/Responder');
const dependency = (name) => require(require.resolve(name, { paths: [root] }));
const babel = dependency('@babel/core');
const React = dependency('react');
const compile = (name) => babel.transformSync(fs.readFileSync(path.join(root, name), 'utf8'), {
  filename: name, configFile: false, babelrc: false,
  plugins: [[dependency('@babel/plugin-transform-typescript'), { isTSX: true, allExtensions: true }],
    [dependency('@babel/plugin-transform-react-jsx'), { runtime: 'classic' }], dependency('@babel/plugin-transform-modules-commonjs')],
});
const helper = compile('src/stubs/mapbox-web-compat.ts');
compile('src/stubs/rnmapbox-maps.web.tsx');
const context = { exports: {}, require: (name) => name === 'react' ? React : dependency(name) };
vm.runInNewContext(helper.code, context, { filename: 'mapbox-web-compat-test.cjs' });
const { resolveWebCameraSettings, findWebCameraDeclaration, initialWebMapOptions, bindWebMapEvents } = context.exports;
const plain = (value) => JSON.parse(JSON.stringify(value));
function Camera() { return null; }
const defaults = { centerCoordinate: [-87.65, 41.87], zoomLevel: 13, heading: 10, pitch: 25 };
const tree = React.createElement(React.Fragment, null, React.createElement('div'), React.createElement(Camera, { defaultSettings: defaults }));
assert.deepEqual(plain(resolveWebCameraSettings(findWebCameraDeclaration(tree, Camera))), defaults);
assert.equal(findWebCameraDeclaration(React.createElement('div'), Camera), undefined);
const controlled = resolveWebCameraSettings({ defaultSettings: defaults, centerCoordinate: [-87.64,41.88], zoomLevel: 0, heading: 0, pitch: 0 });
assert.deepEqual(plain(controlled), { centerCoordinate: [-87.64,41.88], zoomLevel: 0, heading: 0, pitch: 0 });
assert.deepEqual(plain(resolveWebCameraSettings({ followUserLocation: true, followZoomLevel: 16 }, { latitude: null, longitude: null })), {});
assert.deepEqual(plain(resolveWebCameraSettings({ followUserLocation: true, followZoomLevel: 16 }, { latitude: NaN, longitude: 999 })), {});
assert.deepEqual(plain(resolveWebCameraSettings({ followUserLocation: true, followZoomLevel: 16 }, { latitude: 41.88, longitude: -87.64 })), { centerCoordinate: [-87.64,41.88], zoomLevel: 16 });
const department = { latitude: 41.87, longitude: -87.65, zoomLevel: 9 };
const style = 'mapbox://styles/mapbox/dark-v11';
assert.deepEqual(plain(initialWebMapOptions(style, {}, department)), { style, center: [-87.65,41.87], zoom: 9, bearing: 0, pitch: 0 });
assert.deepEqual(plain(initialWebMapOptions(style, controlled, department)), { style, center: [-87.64,41.88], zoom: 0, bearing: 0, pitch: 0 });
const events = new Map();
const map = { on: (name, fn) => events.set(name, fn), off: (name, fn) => { assert.equal(events.get(name),fn); events.delete(name); },
  getCenter: () => ({ lng: -87.65, lat: 41.87 }), getZoom: () => 13, getBearing: () => 0, getPitch: () => 0 };
const calls = []; let active = { onDidFinishLoadingMap: (event) => calls.push(['load',event]), onCameraChanged: (event) => calls.push(['camera',event]), onPress: (event) => calls.push(['press',event]) };
const detach = bindWebMapEvents(map, () => active);
assert.equal(calls.length,0,'Mounting/registration must never fabricate successful map load.');
assert.equal(events.has('error'),false,'Do not suppress SDK errors when source supplied no error handler.');
const realLoad = { type: 'load' }; events.get('load')(realLoad);
assert.equal(calls[0][1],realLoad);
events.get('move')({}); assert.equal(calls[1][1].properties.isUserInteraction,false);
events.get('move')({ originalEvent: { type: 'pointermove' } }); assert.equal(calls[2][1].properties.isUserInteraction,true);
events.get('click')({ lngLat: { lng: -87.64, lat: 41.88 } });
assert.deepEqual(plain(calls[3][1].geometry), { type: 'Point', coordinates: [-87.64,41.88] });
let newCallback = false; active = { onDidFinishLoadingMap: () => { newCallback = true; } }; events.get('load')({});
assert.equal(newCallback,true,'Events use current source callbacks rather than stale closures.');
detach(); assert.equal(events.size,0,'Unmount must release the exact bound callbacks.');
console.log('PASS: real-load-only callback wiring, current source callbacks, click/camera coordinates, default/controlled/zero-valued camera props, department fallback, and existing-fix-only follow behavior. No browser, provider, token or GPS use.');
