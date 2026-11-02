#!/usr/bin/env node
// Pure camera configuration checks. No browser, map service, token or GPS use.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { createRequire } = require('node:module');
const target = path.resolve(process.argv[2] || path.join(__dirname, '../../../../capture-apps/IC'));
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
