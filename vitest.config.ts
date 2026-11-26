import { defineConfig } from 'vitest/config';

// Two projects over the same files: `unit`, the fast loop (npm test), leaves out anything that needs a real
// browser, the network, or a spawned process; `integration` runs every file with those switched on. A test that
// spawns node into folders of its own is a file named *.int.test.ts, which only `integration` runs.
export default defineConfig({
  test: {
    projects: [
      { test: { name: 'unit', include: ['test/unit/**/*.test.ts'], exclude: ['test/unit/**/*.int.test.ts'] } },
      { test: { name: 'integration', include: ['test/unit/**/*.test.ts'] } },
    ],
  },
});
