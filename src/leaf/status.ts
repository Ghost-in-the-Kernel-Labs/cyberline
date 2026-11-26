/** The states a catalogued requirement may be in (VISION.md, section 5). */
export const STATUSES = ['proposed', 'accepted', 'superseded', 'withdrawn'] as const;

export type Status = (typeof STATUSES)[number];

/** Whether a value is one of STATUSES: isStatus('accepted') is true; isStatus('done') and isStatus(1) are false. */
export function isStatus(value: unknown): value is Status {
  return (STATUSES as readonly unknown[]).includes(value);
}
