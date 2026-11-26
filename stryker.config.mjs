// A mutation run (npm run mutate): Stryker changes the source one small way at a time and runs the unit tests that
// reach the change. A change no test notices (a survivor) is code whose behaviour no test holds (C-018).
//
// The command runner, not Stryker's vitest runner: that runner's second start ran no test file, so every mutant
// after the first pass "survived" untested and the first scores were fake (Suite Builder G-290). Each mutant is one
// `vitest run` of the test files that import the mutated file (MUTATE_TESTS, set by scripts/mutate.mjs from the
// import graph). Temporary files go in the sandbox, removed with it: 8,000 of them once filled /tmp. vitest is started by
// node on its own file, not by npx: npm's start-up cost a third of each mutant's second, and the gate's time is a metric.
export default {
  testRunner: 'command',
  commandRunner: { command: `mkdir -p .tmp && TMPDIR=$PWD/.tmp node node_modules/vitest/vitest.mjs run --project unit --bail=1 --maxWorkers=1 ${process.env.MUTATE_TESTS ?? ''}` },
  coverageAnalysis: 'off',
  mutate: ['src/**/*.ts', '!src/**/*.gen.ts'],
  ignorePatterns: ['/dist', '/reports', '/.stryker-tmp', '/.tmp'],
  reporters: ['clear-text', 'json'],
  jsonReporter: { fileName: 'reports/mutation/mutation.json' },
  tempDirName: '.stryker-tmp',
  timeoutMS: 60000,
  concurrency: 4,
  thresholds: { high: 80, low: 60, break: null },
};
