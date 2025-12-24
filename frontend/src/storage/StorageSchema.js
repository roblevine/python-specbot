/**
 * Storage Schema Definition
 * Defines the v1.0.0 schema structure and validation for LocalStorage
 */

import { validateConversation } from '../utils/validators.js'

export const SCHEMA_VERSION = '1.0.0'
export const STORAGE_KEY = 'chatInterface:v1:data'

/**
 * Creates an empty schema structure
 * @returns {Object} Empty schema with version
 */
export function createEmptySchema() {
  return {
    version: SCHEMA_VERSION,
    conversations: [],
    activeConversationId: null,
  }
}

/**
 * Validates the entire storage schema
 * @param {Object} data - Data to validate
 * @returns {Object} Validation result with { isValid: boolean, error: string|null, data: Object }
 */
export function validateSchema(data) {
  if (!data || typeof data !== 'object') {
    return {
      isValid: false,
      error: 'Schema data must be an object',
      data: createEmptySchema(),
    }
  }

  // Check version
  if (data.version !== SCHEMA_VERSION) {
    return {
      isValid: false,
      error: `Schema version mismatch. Expected ${SCHEMA_VERSION}, got ${data.version}`,
      data: createEmptySchema(),
    }
  }

  // Validate conversations array
  if (!Array.isArray(data.conversations)) {
    return {
      isValid: false,
      error: 'Conversations must be an array',
      data: createEmptySchema(),
    }
  }

  // Validate each conversation
  const validConversations = []
  for (const conv of data.conversations) {
    const result = validateConversation(conv)
    if (result.isValid) {
      validConversations.push(conv)
    } else {
      console.warn(`Invalid conversation removed:`, result.error, conv)
    }
  }

  // Validate activeConversationId
  let activeId = data.activeConversationId
  if (activeId !== null && !validConversations.find(c => c.id === activeId)) {
    console.warn(`Active conversation ID ${activeId} not found, resetting to null`)
    activeId = null
  }

  return {
    isValid: true,
    error: null,
    data: {
      version: SCHEMA_VERSION,
      conversations: validConversations,
      activeConversationId: activeId,
    },
  }
}

/**
 * Migrates data from older schema versions (future enhancement)
 * @param {Object} data - Data to migrate
 * @returns {Object} Migrated data
 */
export function migrateSchema(data) {
  // Currently only v1.0.0 exists
  // Future migrations would go here
  if (!data.version) {
    // Assume very old format, create empty schema
    return createEmptySchema()
  }

  if (data.version === SCHEMA_VERSION) {
    return data
  }

  // Unknown version, return empty
  console.warn(`Unknown schema version ${data.version}, creating empty schema`)
  return createEmptySchema()
}
