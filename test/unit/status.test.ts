import { describe, expect, it } from 'vitest';

import { STATUSES, isStatus } from '#p/leaf/status.js';

describe('a requirement status', () => {
  it('is one of four, in this order', () => {
    expect(STATUSES).toEqual(['proposed', 'accepted', 'superseded', 'withdrawn']);
  });

  it('is recognised by name', () => {
    for (const status of ['proposed', 'accepted', 'superseded', 'withdrawn']) expect(isStatus(status)).toBe(true);
  });

  it('is nothing else', () => {
    for (const other of ['done', '', 'Accepted', 1, null, undefined, ['accepted']]) expect(isStatus(other)).toBe(false);
  });
});
