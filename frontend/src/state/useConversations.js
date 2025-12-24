/**
 * useConversations Composable
 * Manages conversation list and active conversation state
 */

import { ref, computed } from 'vue'
import { generateId } from '../utils/idGenerator.js'
import { validateConversation, validateMessage } from '../utils/validators.js'
import * as logger from '../utils/logger.js'
import { saveConversations, loadConversations } from '../storage/LocalStorageAdapter.js'

// Shared state (singleton pattern for composable)
const conversations = ref([])
const activeConversationId = ref(null)

export function useConversations() {
  /**
   * Gets the currently active conversation
   */
  const activeConversation = computed(() => {
    if (!activeConversationId.value) return null
    return conversations.value.find(c => c.id === activeConversationId.value) || null
  })

  /**
   * Creates a new conversation
   * @returns {Object} The created conversation
   */
  function createConversation() {
    const now = new Date().toISOString()
    const conversation = {
      id: generateId('conv'),
      createdAt: now,
      updatedAt: now,
      messages: [],
      title: 'New Conversation',
    }

    const validation = validateConversation(conversation)
    if (!validation.isValid) {
      logger.error('Failed to create conversation', validation.error)
      throw new Error(`Invalid conversation: ${validation.error}`)
    }

    conversations.value.push(conversation)
    activeConversationId.value = conversation.id

    logger.info('Created new conversation', { id: conversation.id })
    return conversation
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
   * Loads conversations from storage
   */
  function loadFromStorage() {
    try {
      const data = loadConversations()
      conversations.value = data.conversations
      activeConversationId.value = data.activeConversationId

      // If no conversations exist, create an initial one
      if (conversations.value.length === 0) {
        createConversation()
      }

      logger.info('Loaded conversations from storage', { count: conversations.value.length })
    } catch (error) {
      logger.error('Failed to load from storage', error)
    }
  }

  /**
   * Saves conversations to storage
   */
  function saveToStorage() {
    try {
      // Only save conversations that have messages
      const conversationsToSave = conversations.value.filter(c => c.messages.length > 0)

      saveConversations(conversationsToSave, activeConversationId.value)
      logger.debug('Saved conversations to storage', { count: conversationsToSave.length })
    } catch (error) {
      logger.error('Failed to save to storage', error)
    }
  }

  /**
   * Resets all state (for testing only)
   * @private
   */
  function __resetState() {
    conversations.value = []
    activeConversationId.value = null
  }

  return {
    conversations: computed(() => conversations.value),
    activeConversationId: computed(() => activeConversationId.value),
    activeConversation,
    createConversation,
    addMessage,
    loadFromStorage,
    saveToStorage,
    __resetState,
  }
}
