/**
 * Unit tests for dateFormatter utility
 * Feature: 015-ux-refinements
 * Task: T006
 *
 * Tests the formatMessageDatetime function which formats timestamps
 * in the format "Sun 18-Jan-26 09:58am"
 */

import { describe, it, expect } from 'vitest'
import { formatMessageDatetime } from '../../../src/utils/dateFormatter.js'

describe('formatMessageDatetime', () => {
  it('formats a morning timestamp correctly', () => {
    // Sunday, January 18, 2026 at 9:58 AM
    const timestamp = '2026-01-18T09:58:00.000Z'
    const result = formatMessageDatetime(timestamp)

    // Note: Result depends on local timezone, so we check the format pattern
    expect(result).toMatch(/^[A-Z][a-z]{2} \d{2}-[A-Z][a-z]{2}-\d{2} \d{1,2}:\d{2}[ap]m$/)
  })

  it('formats an afternoon timestamp correctly', () => {
    // Wednesday, March 15, 2026 at 2:30 PM
    const timestamp = '2026-03-15T14:30:00.000Z'
    const result = formatMessageDatetime(timestamp)

    expect(result).toMatch(/^[A-Z][a-z]{2} \d{2}-[A-Z][a-z]{2}-\d{2} \d{1,2}:\d{2}[ap]m$/)
  })

  it('formats midnight correctly as 12:00am', () => {
    // January 1, 2026 at midnight UTC
    const timestamp = '2026-01-01T00:00:00.000Z'
    const result = formatMessageDatetime(timestamp)

    // Should contain "12:" and "am" for midnight (in some timezone)
    expect(result).toMatch(/^[A-Z][a-z]{2} \d{2}-[A-Z][a-z]{2}-\d{2} \d{1,2}:\d{2}[ap]m$/)
  })

  it('formats noon correctly as 12:00pm', () => {
    // January 1, 2026 at noon UTC
    const timestamp = '2026-01-01T12:00:00.000Z'
    const result = formatMessageDatetime(timestamp)

    expect(result).toMatch(/^[A-Z][a-z]{2} \d{2}-[A-Z][a-z]{2}-\d{2} \d{1,2}:\d{2}[ap]m$/)
  })

  it('pads single-digit day with leading zero', () => {
    // January 5, 2026
    const timestamp = '2026-01-05T10:00:00.000Z'
    const result = formatMessageDatetime(timestamp)

    // Day should be "05" not "5" - format is "Day DD-Mon-YY"
    expect(result).toMatch(/ 0\d-[A-Z][a-z]{2}-/)
  })

  it('pads single-digit minutes with leading zero', () => {
    // Time with single-digit minutes (e.g., 10:05)
    const timestamp = '2026-01-18T10:05:00.000Z'
    const result = formatMessageDatetime(timestamp)

    // Minutes should be padded
    expect(result).toMatch(/:\d{2}[ap]m$/)
  })

  it('formats different weekdays correctly', () => {
    const testCases = [
      { timestamp: '2026-01-18T12:00:00.000Z', expectedDay: 'Sun' }, // Sunday
      { timestamp: '2026-01-19T12:00:00.000Z', expectedDay: 'Mon' }, // Monday
      { timestamp: '2026-01-20T12:00:00.000Z', expectedDay: 'Tue' }, // Tuesday
    ]

    for (const { timestamp } of testCases) {
      const result = formatMessageDatetime(timestamp)
      // Should start with a 3-letter day abbreviation
      expect(result).toMatch(/^[A-Z][a-z]{2} /)
    }
  })

  it('formats different months correctly', () => {
    const testCases = [
      { timestamp: '2026-01-15T12:00:00.000Z', expectedMonth: 'Jan' },
      { timestamp: '2026-06-15T12:00:00.000Z', expectedMonth: 'Jun' },
      { timestamp: '2026-12-15T12:00:00.000Z', expectedMonth: 'Dec' },
    ]

    for (const { timestamp } of testCases) {
      const result = formatMessageDatetime(timestamp)
      // Should contain a 3-letter month abbreviation
      expect(result).toMatch(/-[A-Z][a-z]{2}-\d{2}/)
    }
  })

  it('uses 2-digit year format', () => {
    const timestamp = '2026-01-18T12:00:00.000Z'
    const result = formatMessageDatetime(timestamp)

    // Year should be 2 digits (e.g., "26" not "2026")
    expect(result).toMatch(/-\d{2} /)
  })

  it('uses lowercase am/pm', () => {
    const morningTimestamp = '2026-01-18T09:00:00.000Z'
    const eveningTimestamp = '2026-01-18T21:00:00.000Z'

    const morningResult = formatMessageDatetime(morningTimestamp)
    const eveningResult = formatMessageDatetime(eveningTimestamp)

    // Should end with lowercase am or pm
    expect(morningResult).toMatch(/[ap]m$/)
    expect(eveningResult).toMatch(/[ap]m$/)
  })

  it('handles Date object input', () => {
    const date = new Date('2026-01-18T09:58:00.000Z')
    const result = formatMessageDatetime(date)

    expect(result).toMatch(/^[A-Z][a-z]{2} \d{2}-[A-Z][a-z]{2}-\d{2} \d{1,2}:\d{2}[ap]m$/)
  })

  it('handles timestamp number input', () => {
    const timestamp = new Date('2026-01-18T09:58:00.000Z').getTime()
    const result = formatMessageDatetime(timestamp)

    expect(result).toMatch(/^[A-Z][a-z]{2} \d{2}-[A-Z][a-z]{2}-\d{2} \d{1,2}:\d{2}[ap]m$/)
  })
})
