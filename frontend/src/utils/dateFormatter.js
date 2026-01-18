/**
 * Date formatting utilities
 * Feature: 015-ux-refinements
 * Task: T007
 */

/**
 * Formats a timestamp for message display in the format "Sun 18-Jan-26 09:58am"
 *
 * @param {string|number|Date} timestamp - ISO timestamp string, Unix timestamp, or Date object
 * @returns {string} Formatted datetime string (e.g., "Sun 18-Jan-26 09:58am")
 */
export function formatMessageDatetime(timestamp) {
  const date = new Date(timestamp)

  // Get day name (Sun, Mon, Tue, etc.)
  const dayName = date.toLocaleDateString('en-US', { weekday: 'short' })

  // Get day of month with leading zero (01-31)
  const day = date.getDate().toString().padStart(2, '0')

  // Get month abbreviation (Jan, Feb, etc.)
  const month = date.toLocaleDateString('en-US', { month: 'short' })

  // Get 2-digit year (26 for 2026)
  const year = date.getFullYear().toString().slice(-2)

  // Get hours in 12-hour format
  const hours = date.getHours()
  const hour12 = hours % 12 || 12

  // Get minutes with leading zero
  const minutes = date.getMinutes().toString().padStart(2, '0')

  // Get am/pm (lowercase)
  const ampm = hours >= 12 ? 'pm' : 'am'

  return `${dayName} ${day}-${month}-${year} ${hour12}:${minutes}${ampm}`
}
