const path = require('node:path');
const os = require('node:os');
const unit = process.env.ACADEMY_UNIT_ROOT;
if (!unit) throw new Error('Set ACADEMY_UNIT_ROOT to the actual Unit checkout.');
const baseline = require(path.join(unit, 'jest.config.js'));
module.exports = {
  ...baseline,
  rootDir: unit,
  modulePaths: [path.join(unit, "node_modules")],
  roots: [path.join(unit, 'src/components/check-in-timers/__tests__')],
  testMatch: [path.join(unit, 'src/components/check-in-timers/__tests__/check-in-timer-card.test.tsx'), path.join(unit, 'src/components/check-in-timers/__tests__/check-in-utc-dates.test.tsx')],
  collectCoverage: false,
  cacheDirectory: path.join(os.tmpdir(), `academy-unit-check-in-date-jest-${process.pid}`),
  reporters: ['default'],
  moduleNameMapper: {
    ...baseline.moduleNameMapper,
    '^@/(.*)$': path.join(unit, 'src/$1'),
    '^react-native-permissions$': path.join(__dirname, 'test-fixture-permissions.cjs'),
  },
};
