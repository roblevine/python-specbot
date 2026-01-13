/**
 * LocalStorage Adapter
 * Handles persistence of conversation data to browser LocalStorage
 */

import {
  STORAGE_KEY,
  SCHEMA_VERSION,
  createEmptySchema,
  validateSchema,
  migrateSchema,
} from './StorageSchema.js'
import * as logger from '../utils/logger.js'

/**
 * Saves conversations to localStorage
 * @param {Array} conversations - Array of conversation objects
 * @param {string|null} activeConversationId - ID of the active conversation
 * @param {Object} preferences - User preferences (e.g., sidebar collapsed state)
 * @param {string|null} selectedModelId - Selected model ID (Feature 008)
 */
export function saveConversations(conversations, activeConversationId = null, preferences = null, selectedModelId = null) {
  try {
    const data = {
      version: SCHEMA_VERSION,
      conversations,
      activeConversationId,
      selectedModelId: selectedModelId,
      preferences: preferences || { sidebarCollapsed: false },
    }

    // Validate before saving
    const validation = validateSchema(data)
    if (!validation.isValid) {
      logger.error('Failed to save conversations: validation error', validation.error)
      return
    }

    const jsonData = JSON.stringify(validation.data)
    localStorage.setItem(STORAGE_KEY, jsonData)
    logger.debug('Conversations saved to localStorage', { count: conversations.length })
  } catch (error) {
    logger.error('Failed to save conversations to localStorage', error)
  }
}

/**
 * Loads conversations from localStorage
 * @returns {Object} Object with conversations array, activeConversationId, preferences, and version
 */
export function loadConversations() {
  try {
    const jsonData = localStorage.getItem(STORAGE_KEY)

    if (!jsonData) {
      logger.info('No data in localStorage, returning empty schema')
      return createEmptySchema()
    }

    let data = JSON.parse(jsonData)

    // Migrate if needed
    if (data.version !== SCHEMA_VERSION) {
      logger.info('Migrating schema', { from: data.version, to: SCHEMA_VERSION })
      data = migrateSchema(data)
    }

    const validation = validateSchema(data)

    if (!validation.isValid) {
      logger.warn('Loaded data failed validation, returning sanitized data', validation.error)
    }

    logger.debug('Conversations loaded from localStorage', {
      count: validation.data.conversations.length,
      version: validation.data.version,
    })

    return validation.data
  } catch (error) {
    logger.error('Failed to load conversations from localStorage', error)
    return createEmptySchema()
  }
}

/**
 * Saves selected model ID to localStorage
 * Feature 008: OpenAI Model Selector
 * @param {string|null} modelId - Selected model ID
 */
export function saveSelectedModel(modelId) {
  try {
    // Load existing data
    const existingData = loadConversations()

    // Update selectedModelId
    existingData.selectedModelId = modelId

    // Save back
    saveConversations(
      existingData.conversations,
      existingData.activeConversationId,
      existingData.preferences,
      modelId
    )

    logger.debug('Selected model saved to localStorage', { modelId })
  } catch (error) {
    logger.error('Failed to save selected model', error)
  }
}

/**
 * Clears all chat interface data from localStorage
 */
export function clearAllData() {
  try {
    localStorage.removeItem(STORAGE_KEY)
    logger.info('All chat data cleared from localStorage')
  } catch (error) {
    logger.error('Failed to clear localStorage data', error)
  }
}
