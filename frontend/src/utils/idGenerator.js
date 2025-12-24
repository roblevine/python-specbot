/**
 * ID Generator Utility
 * Generates unique identifiers for conversations and messages
 */

/**
 * Generates a UUID v4 identifier with a prefix
 * @param {string} prefix - Prefix for the ID ('conv' or 'msg')
 * @returns {string} UUID with prefix (e.g., 'conv-550e8400-e29b-41d4-a716-446655440000')
 */
export function generateId(prefix) {
  // Use crypto.randomUUID if available (modern browsers)
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return `${prefix}-${crypto.randomUUID()}`
  }

  // Fallback for older browsers
  return `${prefix}-${generateUUIDFallback()}`
}

/**
 * Fallback UUID v4 generator for browsers without crypto.randomUUID
 * @returns {string} UUID v4 format string
 */
function generateUUIDFallback() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}
