/* Source-level checks for the isolated WebView adapter; no browser/network. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = process.argv[2] || path.resolve(__dirname, '../../../../capture-apps/Responder');
const dependency = (name) => require(require.resolve(name, { paths: [root] }));
const babel = dependency('@babel/core');
const React = dependency('react');
const source = fs.readFileSync(path.join(root, 'src/stubs/react-native-webview.web.tsx'), 'utf8');
const result = babel.transformSync(source, {
  filename: 'webview.tsx', configFile: false, babelrc: false,
  plugins: [[dependency('@babel/plugin-transform-typescript'), { isTSX: true, allExtensions: true }], [dependency('@babel/plugin-transform-react-jsx'), { runtime: 'classic' }], dependency('@babel/plugin-transform-modules-commonjs')],
});
const flatten = (value) => Array.isArray(value) ? Object.assign({}, ...value.filter(Boolean).map(flatten)) : value;
const context = { exports: {}, require: (name) => name === 'react' ? React : name === 'react-native' ? { StyleSheet: { flatten } } : name === 'nativewind' ? { useColorScheme: () => ({ colorScheme: 'dark' }) } : dependency(name) };
vm.runInNewContext(result.code, context, { filename: 'webview-compat-test.cjs' });
const WebView = context.exports.default;
const html = '<p>Fictional call nature &amp; training context</p>';
const element = WebView({ source: { html, uri: 'https://example.invalid/unused' }, style: [{ height: 120 }, { width: '100%' }], testID: 'real-call-text', scrollEnabled: false });
assert.equal(element.type, 'iframe');
assert.equal(element.props.srcDoc, '<meta name="color-scheme" content="dark">' + html, 'Only browser color-scheme metadata may precede the unchanged source HTML.');
assert.equal(element.props.src, undefined, 'HTML content must not trigger an unrelated URI.');
assert.equal(element.props.sandbox, 'allow-same-origin');
assert.ok(!element.props.sandbox.includes('allow-scripts'));
assert.equal(element.props.scrolling, 'no');
assert.equal(element.props.style.height, 120);
assert.equal(element.props['data-testid'], 'real-call-text');
assert.equal(element.props.onMessage, undefined, 'No fabricated native-bridge result is emitted.');
assert.equal(WebView({ source: { uri: 'http://localhost:19102/local' } }).props.src, 'http://localhost:19102/local');
console.log('PASS: isolated WebView adapter preserves actual HTML/style and blocks script/native-bridge simulation.');
