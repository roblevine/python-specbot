/**
 * useConversations Composable
 * Manages conversation list and active conversation state
 *
 * Feature: 010-server-side-conversations
 * Tasks: T016, T017, T023, T024, T026, T030, T031, T034, T036, T038, T039, T040
 */

import { ref, computed } from 'vue'
import { generateId } from '../utils/idGenerator.js'
import { validateConversation, validateMessage } from '../utils/validators.js'
import * as logger from '../utils/logger.js'
import { saveConversations as saveToLocalStorage, loadConversations as loadFromLocalStorage, clearAllData } from '../storage/LocalStorageAdapter.js'
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

// T038: Migration state
const hasMigrated = ref(false)

export function useConversations() {
  /**
   * Gets the currently active conversation
   */
  const activeConversation = computed(() => {
    if (!activeConversationId.value) return null
    return conversations.value.find(c => c.id === activeConversationId.value) || null
  })

  /**
   * T024: Creates a new conversation (persists to server)
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
      // T024: Persist to server
      const response = await apiCreateConversation(conversationData)
      const savedConversation = response.conversation

      conversations.value.push(savedConversation)
      activeConversationId.value = savedConversation.id

      logger.info('Created new conversation on server', { id: savedConversation.id })
      return savedConversation
    } catch (error) {
      // T026: Error handling - add locally but flag error
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

    // Update title from first message if it's still default
    if (conversation.title === 'New Conversation' && conversation.messages.length === 1) {
      conversation.title = message.text.slice(0, 50)
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
   * Loads conversations from storage
   * T016, T017: Loads conversations from server API
   * Falls back to localStorage migration if server is empty and localStorage has data
   */
  async function loadFromStorage() {
    isLoading.value = true
    loadError.value = null

    try {
      // T016: Fetch from server API
      const response = await apiGetConversations()
      const serverConversations = response.conversations || []

      logger.info('Fetched conversations from server', { count: serverConversations.length })

      // T039: Check for migration scenario (server empty, localStorage has data)
      if (serverConversations.length === 0 && !hasMigrated.value) {
        const localData = loadFromLocalStorage()
        if (localData.conversations && localData.conversations.length > 0) {
          logger.info('Migrating conversations from localStorage', { count: localData.conversations.length })
          await migrateFromLocalStorage(localData)
          return
        }
      }

      // If we got full conversation summaries, we need to fetch full conversations
      // For now, store the summaries and fetch full data as needed
      if (serverConversations.length > 0) {
        // Fetch full conversation data for each
        const fullConversations = []
        for (const summary of serverConversations) {
          try {
            const fullResponse = await apiGetConversation(summary.id)
            fullConversations.push(fullResponse.conversation)
          } catch (error) {
            logger.warn('Failed to fetch full conversation', { id: summary.id, error })
          }
        }
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
      // T017: Error handling
      logger.error('Failed to load conversations from server', error)
      loadError.value = error.message || 'Failed to load conversations'

      // T034: Fallback to localStorage if server unavailable
      try {
        const localData = loadFromLocalStorage()
        conversations.value = localData.conversations || []
        activeConversationId.value = localData.activeConversationId

        if (conversations.value.length === 0) {
          // Create local-only conversation
          const now = new Date().toISOString()
          const localConversation = {
            id: generateId('conv'),
            createdAt: now,
            updatedAt: now,
            messages: [],
            title: 'New Conversation',
          }
          conversations.value.push(localConversation)
          activeConversationId.value = localConversation.id
        } else if (!activeConversationId.value && conversations.value.length > 0) {
          activeConversationId.value = conversations.value[0].id
        }

        logger.warn('Using localStorage fallback', { count: conversations.value.length })
      } catch (localError) {
        logger.error('Failed to load from localStorage fallback', localError)
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * T038, T039, T040: Migrate conversations from localStorage to server
   * @param {Object} localData - Data from localStorage
   */
  async function migrateFromLocalStorage(localData) {
    logger.info('Starting localStorage migration')
    hasMigrated.value = true

    try {
      const migratedConversations = []

      for (const conversation of localData.conversations) {
        try {
          // Create each conversation on server
          const response = await apiCreateConversation(conversation)
          migratedConversations.push(response.conversation)
          logger.debug('Migrated conversation', { id: conversation.id })
        } catch (error) {
          logger.error('Failed to migrate conversation', { id: conversation.id, error })
          // Continue with other conversations
          migratedConversations.push(conversation)
        }
      }

      conversations.value = migratedConversations

      // Set active conversation
      if (localData.activeConversationId) {
        activeConversationId.value = localData.activeConversationId
      } else if (migratedConversations.length > 0) {
        activeConversationId.value = migratedConversations[0].id
      }

      // T040: Clear localStorage after successful migration
      try {
        clearAllData()
        logger.info('Cleared localStorage after migration')
      } catch (clearError) {
        logger.warn('Failed to clear localStorage after migration', clearError)
      }

      logger.info('Migration complete', { count: migratedConversations.length })
    } catch (error) {
      logger.error('Migration failed', error)
      // Use local data as fallback
      conversations.value = localData.conversations
      activeConversationId.value = localData.activeConversationId
    } finally {
      isLoading.value = false
    }
  }

  /**
   * T023: Saves conversations to server
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
      // T026: Error handling
      logger.error('Failed to save to server', error)
      saveError.value = error.message || 'Failed to save conversation'

      // Fallback to localStorage
      try {
        const conversationsToSave = conversations.value.filter(c => c.messages.length > 0)
        const existingData = loadFromLocalStorage()
        saveToLocalStorage(
          conversationsToSave,
          activeConversationId.value,
          existingData.preferences,
          existingData.selectedModelId
        )
        logger.warn('Saved to localStorage as fallback')
      } catch (localError) {
        logger.error('Failed to save to localStorage fallback', localError)
      }
    }
  }

  /**
   * T030, T031: Deletes a conversation
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
   * Sets the active conversation
   * @param {string} conversationId - ID of conversation to set active
   */
  function setActiveConversation(conversationId) {
    const conversation = conversations.value.find(c => c.id === conversationId)
    if (conversation) {
      activeConversationId.value = conversationId
      logger.debug('Set active conversation', { conversationId })
    } else {
      logger.warn('Cannot set active conversation, not found', { conversationId })
    }
  }

  /**
   * T036: Clears the current error state
   */
  function clearError() {
    loadError.value = null
    saveError.value = null
  }

  /**
   * T036: Retries loading conversations after an error
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
    hasMigrated.value = false
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
    setActiveConversation,
    clearError,
    retryLoad,
    __resetState,
  }
}
