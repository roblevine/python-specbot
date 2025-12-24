/**
 * LocalStorage Adapter
 * Handles persistence of conversation data to browser LocalStorage
 */

import { STORAGE_KEY, createEmptySchema, validateSchema } from './StorageSchema.js'
import * as logger from '../utils/logger.js'

/**
 * Saves conversations to localStorage
 * @param {Array} conversations - Array of conversation objects
 * @param {string|null} activeConversationId - ID of the active conversation
 */
export function saveConversations(conversations, activeConversationId = null) {
  try {
    const data = {
      version: '1.0.0',
      conversations,
      activeConversationId,
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
 * @returns {Object} Object with conversations array, activeConversationId, and version
 */
export function loadConversations() {
  try {
    const jsonData = localStorage.getItem(STORAGE_KEY)

    if (!jsonData) {
      logger.info('No data in localStorage, returning empty schema')
      return createEmptySchema()
    }

    const data = JSON.parse(jsonData)
    const validation = validateSchema(data)

    if (!validation.isValid) {
      logger.warn('Loaded data failed validation, returning sanitized data', validation.error)
    }

    logger.debug('Conversations loaded from localStorage', {
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
