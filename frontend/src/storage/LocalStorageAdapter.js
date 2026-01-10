/**
 * LocalStorage Adapter
 * Handles persistence of conversation data to browser LocalStorage
 * Includes schema migration v1.0.0 → v2.0.0 (Feature 005 - T013)
 */

import { STORAGE_KEY, createEmptySchema, validateSchema } from './StorageSchema.js'
import * as logger from '../utils/logger.js'

const CURRENT_VERSION = '2.0.0'
const LEGACY_V1_KEY = 'chatInterface:v1:data'

/**
 * Migrate schema from v1.0.0 to v2.0.0 (Feature 005 - T013)
 * @param {Object} v1Data - Data in v1.0.0 format
 * @returns {Object} Data in v2.0.0 format
 */
function migrateV1toV2(v1Data) {
  logger.info('Migrating localStorage schema from v1.0.0 to v2.0.0')

  const v2Data = {
    version: '2.0.0',
    conversations: v1Data.conversations.map(conv => ({
      ...conv,
      messages: conv.messages.map(msg => ({
        ...msg,
        // Map v1 'system' sender to v2 'assistant' for AI responses
        sender: msg.sender === 'system' ? 'assistant' : msg.sender,
        // Map v1 'sent' status to v2 'completed'
        status: msg.status === 'sent' ? 'completed' : msg.status,
        // Add new v2 fields with defaults
        model: null,
        error: null
      })),
      // Add per-conversation model selection (defaults to null)
      selectedModel: null
    })),
    activeConversationId: v1Data.activeConversationId,
    // Add global model selection
    modelSelection: {
      selectedModel: 'gpt-5',
      lastUpdated: new Date().toISOString()
    }
  }

  logger.info('Migration complete', {
    conversations: v2Data.conversations.length,
    messages: v2Data.conversations.reduce((sum, c) => sum + c.messages.length, 0)
  })

  return v2Data
}

/**
 * Saves conversations to localStorage
 * @param {Array} conversations - Array of conversation objects
 * @param {string|null} activeConversationId - ID of the active conversation
 * @param {Object} modelSelection - Model selection state (optional)
 */
export function saveConversations(conversations, activeConversationId = null, modelSelection = null) {
  try {
    const data = {
      version: CURRENT_VERSION,
      conversations,
      activeConversationId,
      modelSelection: modelSelection || {
        selectedModel: 'gpt-5',
        lastUpdated: new Date().toISOString()
      }
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
 * Loads conversations from localStorage with automatic migration
 * @returns {Object} Object with conversations array, activeConversationId, modelSelection, and version
 */
export function loadConversations() {
  try {
    let jsonData = localStorage.getItem(STORAGE_KEY)
    let data = null

    // Check for legacy v1 data if current key is empty
    if (!jsonData) {
      const legacyData = localStorage.getItem(LEGACY_V1_KEY)
      if (legacyData) {
        logger.info('Found legacy v1.0.0 data, migrating...')
        const v1Data = JSON.parse(legacyData)
        data = migrateV1toV2(v1Data)

        // Save migrated data to new key
        const jsonData = JSON.stringify(data)
        localStorage.setItem(STORAGE_KEY, jsonData)

        logger.info('Migration saved to new storage key')
        // Keep v1 data for rollback safety (can be removed after 1 week)
      } else {
        logger.info('No data in localStorage, returning empty schema')
        return createEmptySchema()
      }
    } else {
      data = JSON.parse(jsonData)

      // Check if data needs migration (v1.0.0 in current key)
      if (data.version === '1.0.0') {
        logger.info('Detected v1.0.0 data in current key, migrating...')
        data = migrateV1toV2(data)

        // Save migrated data
        const jsonData = JSON.stringify(data)
        localStorage.setItem(STORAGE_KEY, jsonData)

        logger.info('Migration complete and saved')
      }
    }

    const validation = validateSchema(data)

    if (!validation.isValid) {
      logger.warn('Loaded data failed validation, returning sanitized data', validation.error)
    }

    logger.debug('Conversations loaded from localStorage', {
      version: validation.data.version,
      count: validation.data.conversations.length,
    })

    return validation.data
  } catch (error) {
    logger.error('Failed to load conversations from localStorage', error)
    return createEmptySchema()
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
