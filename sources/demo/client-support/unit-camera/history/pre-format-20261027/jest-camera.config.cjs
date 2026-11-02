/** Focused real web Camera regression; no app writes or native fixture setup. */
const path = require('node:path');
const os = require('node:os');
const unit = process.env.ACADEMY_UNIT_ROOT;
if (!unit) throw new Error('Set ACADEMY_UNIT_ROOT to the actual Unit checkout.');
module.exports = {
  rootDir: unit,
  testEnvironment: require.resolve(path.join(unit, 'node_modules/jest-environment-jsdom')),
  testMatch: [path.join(unit, 'src/components/maps/__tests__/camera.web.test.tsx')],
  modulePaths: [path.join(unit, 'node_modules')],
  moduleDirectories: ['node_modules', path.join(unit, 'node_modules')],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': path.join(unit, '__mocks__/styleMock.js'),
    '^mapbox-gl$': path.join(unit, '__mocks__/mapbox-gl.js'),
    '^@/(.*)$': path.join(unit, 'src/$1'),
  },
  transform: {
    '^.+\\.[jt]sx?$': [require.resolve(path.join(unit, 'node_modules/babel-jest')), {
      babelrc: false,
      configFile: false,
      presets: [require.resolve(path.join(unit, 'node_modules/babel-preset-expo'))],
    }],
  },
  transformIgnorePatterns: ['/node_modules/'],
  collectCoverage: false,
  cacheDirectory: process.env.ACADEMY_CAMERA_TEST_CACHE || path.join(os.tmpdir(), `academy-unit-camera-jest-${process.pid}`),
  reporters: ['default'],
};
