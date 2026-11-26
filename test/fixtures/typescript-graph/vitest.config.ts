// 1.30's graph fixture: a setup file vitest loads by configuration, not by import, so the cache key must name it.
export default { test: { setupFiles: ['./test/setup.ts'] } };
