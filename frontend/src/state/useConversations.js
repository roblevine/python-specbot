/**
 * useConversations Composable
 * Manages conversation list and active conversation state
 *
 * Feature: 010-server-side-conversations
 * Updated: 018-audit-local-storage - Removed all localStorage code (server-only)
 */

import { ref, computed } from 'vue'
import { generateId } from '../utils/idGenerator.js'
import { validateConversation, validateMessage } from '../utils/validators.js'
import * as logger from '../utils/logger.js'
import {
  getConversations as apiGetConversations,
  getConversation as apiGetConversation,
  createConversation as apiCreateConversation,
  updateConversation as apiUpdateConversation,
  deleteConversation as apiDeleteConversation,
} from '../services/apiClient.js'

// Shared state (singleton pattern for composable)
const conversations = ref([])
const activeConversationId = ref(null)

// T017: Loading and error state for conversation operations
const isLoading = ref(false)
const loadError = ref(null)
const saveError = ref(null)

/**
 * Sorts conversations by updatedAt descending (most recent first)
 * Uses id as secondary sort key for deterministic ordering when timestamps are equal
 * Feature: 015-ux-refinements
 * @param {Array} convs - Array of conversation objects
 * @returns {Array} Sorted array (mutates original)
 */
function sortConversationsByRecent(convs) {
  return convs.sort((a, b) => {
    // Primary: updatedAt descending (most recent first)
    const timeCompare = new Date(b.updatedAt) - new Date(a.updatedAt)
    if (timeCompare !== 0) return timeCompare
    // Secondary: id for stability when timestamps are equal
    return b.id.localeCompare(a.id)
  })
}

export function useConversations() {
  /**
   * Gets the currently active conversation
   */
  const activeConversation = computed(() => {
    if (!activeConversationId.value) return null
    return conversations.value.find(c => c.id === activeConversationId.value) || null
  })

  /**
   * Creates a new conversation (persists to server)
   * @returns {Promise<Object>} The created conversation
   */
  async function createConversation() {
    const now = new Date().toISOString()
    const conversationData = {
      id: generateId('conv'),
      createdAt: now,
      updatedAt: now,
      messages: [],
      title: 'New Conversation',
    }

    const validation = validateConversation(conversationData)
    if (!validation.isValid) {
      logger.error('Failed to create conversation', validation.error)
      throw new Error(`Invalid conversation: ${validation.error}`)
    }

    try {
      // Persist to server
      const response = await apiCreateConversation(conversationData)
      const savedConversation = response.conversation

      conversations.value.push(savedConversation)
      activeConversationId.value = savedConversation.id

      logger.info('Created new conversation on server', { id: savedConversation.id })
      return savedConversation
    } catch (error) {
      // Error handling - add locally but flag error
      logger.error('Failed to create conversation on server, adding locally', error)
      saveError.value = error.message || 'Failed to create conversation'

      // Add locally anyway so user doesn't lose the conversation
      conversations.value.push(conversationData)
      activeConversationId.value = conversationData.id

      return conversationData
    }
  }

  /**
   * Adds a message to a conversation
   * @param {string} conversationId - ID of the conversation
   * @param {Object} message - Message object to add
   */
  function addMessage(conversationId, message) {
    const validation = validateMessage(message)
    if (!validation.isValid) {
      logger.error('Failed to add message', validation.error)
      throw new Error(`Invalid message: ${validation.error}`)
    }

    const conversation = conversations.value.find(c => c.id === conversationId)
    if (!conversation) {
      logger.error('Conversation not found', { conversationId })
      throw new Error(`Conversation not found: ${conversationId}`)
    }

    conversation.messages.push(message)
    conversation.updatedAt = new Date().toISOString()

    // Update title from first message if it's still default (store full text, truncate only for display)
    if (conversation.title === 'New Conversation' && conversation.messages.length === 1) {
      conversation.title = message.text
    }

    logger.debug('Added message to conversation', { conversationId, messageId: message.id })
  }

  /**
   * Sets the active conversation by ID
   * @param {string} conversationId - ID of the conversation to activate
   */
  function setActiveConversation(conversationId) {
    const conversation = conversations.value.find(c => c.id === conversationId)
    if (!conversation) {
      logger.error('Cannot set active conversation - not found', { conversationId })
      throw new Error(`Conversation not found: ${conversationId}`)
    }

    activeConversationId.value = conversationId
    logger.info('Set active conversation', { conversationId })
  }

  /**
   * Loads conversations from server
   * T028: Server-only - no localStorage fallback
   * Feature: 018-audit-local-storage
   */
  async function loadFromStorage() {
    isLoading.value = true
    loadError.value = null

    try {
      // Fetch from server API
      const response = await apiGetConversations()
      const serverConversations = response.conversations || []

      logger.info('Fetched conversations from server', { count: serverConversations.length })

      // Fetch full conversation data for each
      if (serverConversations.length > 0) {
        const fullConversations = []
        for (const summary of serverConversations) {
          try {
            const fullResponse = await apiGetConversation(summary.id)
            fullConversations.push(fullResponse.conversation)
          } catch (error) {
            logger.warn('Failed to fetch full conversation', { id: summary.id, error })
          }
        }
        // Feature 015: Sort conversations by most recent first for deterministic ordering
        sortConversationsByRecent(fullConversations)
        conversations.value = fullConversations
      } else {
        conversations.value = []
      }

      // Set active conversation
      if (conversations.value.length > 0) {
        activeConversationId.value = conversations.value[0].id
        logger.info('Set active conversation', { id: activeConversationId.value })
      } else {
        // No conversations exist, create an initial one
        await createConversation()
      }

      logger.info('Loaded conversations from server', { count: conversations.value.length })
    } catch (error) {
      // T028: Error handling - no localStorage fallback, just show error
      logger.error('Failed to load conversations from server', error)
      loadError.value = error.message || 'Failed to load conversations'

      // Create empty state so app is usable
      conversations.value = []
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Saves conversations to server
   * T027: Server-only - no localStorage fallback
   * @param {string} conversationId - Optional specific conversation to save
   */
  async function saveToStorage(conversationId = null) {
    saveError.value = null

    try {
      if (conversationId) {
        // Save specific conversation
        const conversation = conversations.value.find(c => c.id === conversationId)
        if (conversation && conversation.messages.length > 0) {
          await apiUpdateConversation(conversationId, {
            title: conversation.title,
            messages: conversation.messages,
          })
          logger.debug('Saved conversation to server', { conversationId })
        }
      } else {
        // Save all conversations with messages
        const conversationsToSave = conversations.value.filter(c => c.messages.length > 0)

        for (const conversation of conversationsToSave) {
          try {
            await apiUpdateConversation(conversation.id, {
              title: conversation.title,
              messages: conversation.messages,
            })
          } catch (error) {
            // If 404, create it instead
            if (error.statusCode === 404) {
              await apiCreateConversation(conversation)
            } else {
              throw error
            }
          }
        }

        logger.debug('Saved all conversations to server', { count: conversationsToSave.length })
      }
    } catch (error) {
      // T027: Error handling - no localStorage fallback
      logger.error('Failed to save to server', error)
      saveError.value = error.message || 'Failed to save conversation'
    }
  }

  /**
   * Deletes a conversation
   * @param {string} conversationId - ID of conversation to delete
   */
  async function deleteConversation(conversationId) {
    try {
      await apiDeleteConversation(conversationId)

      // Remove from local state
      const index = conversations.value.findIndex(c => c.id === conversationId)
      if (index !== -1) {
        conversations.value.splice(index, 1)
      }

      // Update active conversation if needed
      if (activeConversationId.value === conversationId) {
        if (conversations.value.length > 0) {
          activeConversationId.value = conversations.value[0].id
        } else {
          // Create new conversation if all deleted
          await createConversation()
        }
      }

      logger.info('Deleted conversation', { conversationId })
    } catch (error) {
      logger.error('Failed to delete conversation', error)
      saveError.value = error.message || 'Failed to delete conversation'
      throw error
    }
  }

  /**
   * Renames a conversation
   * @param {string} conversationId - ID of conversation to rename
   * @param {string} newTitle - New title for the conversation
   */
  async function renameConversation(conversationId, newTitle) {
    const conversation = conversations.value.find(c => c.id === conversationId)
    if (!conversation) {
      logger.error('Cannot rename conversation - not found', { conversationId })
      throw new Error(`Conversation not found: ${conversationId}`)
    }

    const trimmedTitle = newTitle.trim()
    if (trimmedTitle.length === 0) {
      throw new Error('Title cannot be empty')
    }
    if (trimmedTitle.length > 500) {
      throw new Error('Title cannot exceed 500 characters')
    }

    conversation.title = trimmedTitle
    conversation.updatedAt = new Date().toISOString()

    logger.info('Renamed conversation', { conversationId, newTitle: trimmedTitle })

    // Persist to server
    await saveToStorage(conversationId)
  }

  /**
   * Clears the current error state
   */
  function clearError() {
    loadError.value = null
    saveError.value = null
  }

  /**
   * Retries loading conversations after an error
   */
  async function retryLoad() {
    clearError()
    await loadFromStorage()
  }

  /**
   * Resets all state (for testing only)
   * @private
   */
  function __resetState() {
    conversations.value = []
    activeConversationId.value = null
    isLoading.value = false
    loadError.value = null
    saveError.value = null
  }

  return {
    conversations: computed(() => conversations.value),
    activeConversationId: computed(() => activeConversationId.value),
    activeConversation,
    // T017: Loading and error state
    isLoading: computed(() => isLoading.value),
    loadError: computed(() => loadError.value),
    saveError: computed(() => saveError.value),
    // Actions
    createConversation,
    addMessage,
    setActiveConversation,
    loadFromStorage,
    saveToStorage,
    deleteConversation,
    renameConversation,
    clearError,
    retryLoad,
    __resetState,
  }
}
