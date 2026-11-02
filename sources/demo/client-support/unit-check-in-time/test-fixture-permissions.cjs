// Test resolution placeholder only. The unchanged repository jest-setup.ts
// supplies its existing jest.mock factory for this absent dependency. This file
// is never imported by the application and implements no device permission API.
module.exports = {};
