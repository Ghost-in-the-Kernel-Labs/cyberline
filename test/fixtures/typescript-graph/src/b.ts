// 1.30's graph fixture: the cycle back to a.ts, again by its `.js` name.
import { a } from './a.js';

export function b(n: number): number {
  return n <= 0 ? 0 : a(n - 1) + 1;
}
