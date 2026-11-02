#!/usr/bin/env node
// Pure module/server-render checks: does not launch the application, Expo, a browser or a UI.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { createRequire } = require('node:module');
const target = path.resolve(process.argv[2] || path.join(__dirname, '../../../../capture-apps/IC'));
const fromApp = createRequire(path.join(target, 'package.json'));
const ts = fromApp('typescript');
const React = fromApp('react');
const { StyleSheet } = fromApp('react-native-web');
const { renderToStaticMarkup } = fromApp('react-dom/server');
function load(relative, aliases = {}) {
  const filename = path.join(target, relative);
  const output = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.React, esModuleInterop: true, target: ts.ScriptTarget.ES2020 },
    reportDiagnostics: true, fileName: filename,
  });
  assert.equal((output.diagnostics || []).filter(d => d.category === ts.DiagnosticCategory.Error).length, 0, 'Transpile diagnostics');
  const module = { exports: {} };
  const localRequire = name => aliases[name] || (name === 'react-native' ? { StyleSheet } : fromApp(name));
  vm.runInThisContext('(function(require, module, exports) {' + output.outputText + '\n})', { filename })(localRequire, module, module.exports);
  return module.exports;
}
const { toDomProps } = load('src/components/ui/utils/dom-props.ts');
const { Text } = load('src/components/ui/text/index.web.tsx', {
  '@/components/ui/utils/dom-props': { toDomProps }, './styles': { textStyle: () => '' },
});
let presses = 0;
const span = Text.render({
  children: 'Recording compatibility check', testID: 'text-check', numberOfLines: 2,
  style: [{ color: 'red', fontSize: 14 }, false, [{ color: 'blue' }]],
  onPress: () => presses++, accessibilityRole: 'link', accessibilityLabel: 'Open recording help',
  accessibilityState: { expanded: false, busy: true },
}, null);
assert.equal(span.props.style.color, 'blue');
assert.equal(span.props.style.fontSize, 14);
assert.equal(span.props.style.WebkitLineClamp, 2);
assert.equal(span.props.style.display, '-webkit-box');
assert.equal(Object.keys(span.props.style).some(k => /^\d+$/.test(k)), false);
assert.equal(span.props['data-testid'], 'text-check');
assert.equal(span.props['aria-label'], 'Open recording help');
assert.equal(span.props['aria-expanded'], false);
assert.equal(span.props['aria-busy'], true);
assert.equal(span.props.role, 'link');
assert.equal(span.props.tabIndex, 0);
assert.equal(span.props.onPress, undefined);
span.props.onClick();
assert.equal(presses, 1);
let keyClick = 0;
span.props.onKeyDown({ key: 'Enter', preventDefault() {}, currentTarget: { click() { keyClick++; } } });
assert.equal(keyClick, 1);
const explicitClick = () => {};
const accessible = toDomProps({ onPress: () => {}, onClick: explicitClick, 'aria-label': 'Explicit', accessibilityLabel: 'Native', accessibilityRole: 'header', nativeID: 'heading', accessibilityLiveRegion: 'none' });
assert.equal(accessible.onClick, explicitClick);
assert.equal(accessible['aria-label'], 'Explicit');
assert.equal(accessible.role, 'heading');
assert.equal(accessible.id, 'heading');
assert.equal(accessible['aria-live'], 'off');
const markup = renderToStaticMarkup(React.createElement(Text, { style: [[{ color: 'red' }], { color: 'blue' }], numberOfLines: 3, children: 'Clamp check' }));
assert.ok(markup.includes('-webkit-line-clamp:3'));
assert.ok(markup.includes('color:blue'));
assert.equal(markup.includes('0:'), false);
console.log('PASS: nested style flattening, multiline clamp, press/click and keyboard actions, DOM accessibility, server rendering. No app UI launched.');
