// 1.30's graph fixture: a NodeNext source imports its neighbour by the `.js` name the compiler requires.
import { b } from './b.js';

export function a(n: number): number {
  return n <= 0 ? 0 : b(n - 1) + 1;
}
