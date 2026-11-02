/** Run the actual installed CallImagesModal regression without writing Unit. */
const path = require('node:path');
const os = require('node:os');
const unit = process.env.ACADEMY_UNIT_ROOT;
if (!unit) throw new Error('Set ACADEMY_UNIT_ROOT to the actual Unit checkout.');
const baseline = require(path.join(unit, 'jest.config.js'));
module.exports = {
  ...baseline,
  rootDir: unit,
  roots: [path.join(unit, 'src/components/calls/__tests__')],
  testMatch: [path.join(unit, 'src/components/calls/__tests__/call-images-modal.test.tsx')],
  collectCoverage: false,
  cacheDirectory: process.env.ACADEMY_IMAGES_TEST_CACHE || path.join(os.tmpdir(), `academy-unit-images-jest-${process.pid}`),
  reporters: ['default'],
  moduleNameMapper: {
    ...baseline.moduleNameMapper,
    '^@/(.*)$': path.join(unit, 'src/$1'),
    '^react-native-permissions$': path.join(__dirname, 'test-fixture-permissions.cjs'),
  },
};
