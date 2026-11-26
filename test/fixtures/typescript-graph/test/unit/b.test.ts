// 1.30's graph fixture: the one test reaches b.ts directly and a.ts through b.ts's import.
import { b } from '../../src/b.js';

if (b(3) !== 3) throw new Error('b(3) should be 3');
