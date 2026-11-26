// A mutation run (npm run mutate): Stryker changes the source one small way at a time and runs the unit tests that
// reach the change. A change no test notices (a survivor) is code whose behaviour no test holds (C-018).
//
// The command runner, not Stryker's vitest runner (C-018; stacks/typescript/README.md, the Mutation row). Each mutant is one
// `vitest run` of the test files that import the mutated file (MUTATE_TESTS, set by scripts/mutate.mjs from the
// import graph). Temporary files go in the sandbox, removed with it (C-046). vitest is started by
// node on its own file, not by npx (C-047).
export default {
  testRunner: 'command',
  commandRunner: { command: `mkdir -p .tmp && TMPDIR=$PWD/.tmp node node_modules/vitest/vitest.mjs run --project unit --bail=1 --maxWorkers=1 ${process.env.MUTATE_TESTS ?? ''}` },
  coverageAnalysis: 'off',
  // Names a file that does not exist, so Stryker reads no tsconfig (C-018; stacks/typescript/README.md, the Mutation row).
  tsconfigFile: 'no-tsconfig-for-stryker.json',
  mutate: ['src/**/*.ts', '!src/**/*.gen.ts'],
  ignorePatterns: ['/dist', '/reports', '/.stryker-tmp', '/.tmp'],
  reporters: ['clear-text', 'json'],
  jsonReporter: { fileName: 'reports/mutation/mutation.json' },
  tempDirName: '.stryker-tmp',
  timeoutMS: 60000,
  concurrency: 4,
  thresholds: { high: 80, low: 60, break: null },
};
