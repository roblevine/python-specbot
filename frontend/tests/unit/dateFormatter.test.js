import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { formatMessageDatetime, formatConversationTimestamp } from '../../src/utils/dateFormatter.js'

describe('dateFormatter', () => {
  describe('formatMessageDatetime', () => {
    it('should format timestamp with day name, date, and time', () => {
      // January 22, 2026 at 3:45 PM
      const timestamp = new Date(2026, 0, 22, 15, 45, 0).toISOString()
      const result = formatMessageDatetime(timestamp)

      expect(result).toMatch(/Thu/)
      expect(result).toMatch(/22/)
      expect(result).toMatch(/Jan/)
      expect(result).toMatch(/26/)
      expect(result).toMatch(/3:45pm/)
    })

    it('should handle morning times with am', () => {
      const timestamp = new Date(2026, 0, 22, 9, 30, 0).toISOString()
      const result = formatMessageDatetime(timestamp)

      expect(result).toMatch(/9:30am/)
    })

    it('should handle midnight as 12am', () => {
      const timestamp = new Date(2026, 0, 22, 0, 5, 0).toISOString()
      const result = formatMessageDatetime(timestamp)

      expect(result).toMatch(/12:05am/)
    })

    it('should handle noon as 12pm', () => {
      const timestamp = new Date(2026, 0, 22, 12, 0, 0).toISOString()
      const result = formatMessageDatetime(timestamp)

      expect(result).toMatch(/12:00pm/)
    })
  })

  describe('formatConversationTimestamp', () => {
    let mockDate

    beforeEach(() => {
      // Mock current date to January 22, 2026 at 3:00 PM
      mockDate = new Date(2026, 0, 22, 15, 0, 0)
      vi.useFakeTimers()
      vi.setSystemTime(mockDate)
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('should show time only for today', () => {
      // Today at 9:45 AM
      const timestamp = new Date(2026, 0, 22, 9, 45, 0).toISOString()
      const result = formatConversationTimestamp(timestamp)

      // Should be time format like "9:45 AM"
      expect(result).toMatch(/9:45/)
      expect(result).toMatch(/AM/i)
    })

    it('should show "Yesterday" for yesterday', () => {
      // Yesterday (January 21, 2026)
      const timestamp = new Date(2026, 0, 21, 14, 30, 0).toISOString()
      const result = formatConversationTimestamp(timestamp)

      expect(result).toBe('Yesterday')
    })

    it('should show day name for this week (2-6 days ago)', () => {
      // 3 days ago (January 19, 2026 - Monday)
      const timestamp = new Date(2026, 0, 19, 10, 0, 0).toISOString()
      const result = formatConversationTimestamp(timestamp)

      expect(result).toBe('Monday')
    })

    it('should show date for older than a week', () => {
      // 10 days ago (January 12, 2026)
      const timestamp = new Date(2026, 0, 12, 10, 0, 0).toISOString()
      const result = formatConversationTimestamp(timestamp)

      // Should contain month, day, and year
      expect(result).toMatch(/Jan/)
      expect(result).toMatch(/12/)
      expect(result).toMatch(/2026/)
    })

    it('should handle very old dates', () => {
      // Last year
      const timestamp = new Date(2025, 5, 15, 10, 0, 0).toISOString()
      const result = formatConversationTimestamp(timestamp)

      expect(result).toMatch(/Jun/)
      expect(result).toMatch(/15/)
      expect(result).toMatch(/2025/)
    })

    it('should handle edge case: just before midnight yesterday', () => {
      // Yesterday at 11:59 PM
      const timestamp = new Date(2026, 0, 21, 23, 59, 0).toISOString()
      const result = formatConversationTimestamp(timestamp)

      expect(result).toBe('Yesterday')
    })

    it('should handle edge case: just after midnight today', () => {
      // Today at 12:01 AM
      const timestamp = new Date(2026, 0, 22, 0, 1, 0).toISOString()
      const result = formatConversationTimestamp(timestamp)

      // Should show time only
      expect(result).toMatch(/12:01/)
      expect(result).toMatch(/AM/i)
    })

    it('should handle exactly 7 days ago', () => {
      // January 15, 2026 (7 days ago)
      const timestamp = new Date(2026, 0, 15, 10, 0, 0).toISOString()
      const result = formatConversationTimestamp(timestamp)

      // 7 days = not this week, should show date
      expect(result).toMatch(/Jan/)
      expect(result).toMatch(/15/)
    })

    it('should handle 6 days ago (still this week)', () => {
      // January 16, 2026 (6 days ago - Friday)
      const timestamp = new Date(2026, 0, 16, 10, 0, 0).toISOString()
      const result = formatConversationTimestamp(timestamp)

      // 6 days = still this week, should show day name
      expect(result).toBe('Friday')
    })
  })
})
