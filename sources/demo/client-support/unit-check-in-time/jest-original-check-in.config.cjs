const path = require('node:path');
const fixed = require('./jest-check-in.config.cjs');
const original = path.join(__dirname, 'before/src/components/check-in-timers');
module.exports = {
  ...fixed,
  testMatch: [path.join(process.env.ACADEMY_UNIT_ROOT, 'src/components/check-in-timers/__tests__/check-in-utc-dates.test.tsx')],
  moduleNameMapper: {
    ...fixed.moduleNameMapper,
    '^\\.\\./check-in-timer-card$': path.join(original, 'check-in-timer-card.tsx'),
    '^\\.\\./check-in-history-list$': path.join(original, 'check-in-history-list.tsx'),
  },
};
