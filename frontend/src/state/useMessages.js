/**
 * useMessages Composable
 * Manages message sending and loopback functionality
 */

import { computed } from 'vue'
import { generateId } from '../utils/idGenerator.js'
import { validateMessageText } from '../utils/validators.js'
import * as logger from '../utils/logger.js'
import { useConversations } from './useConversations.js'
import { useAppState } from './useAppState.js'

export function useMessages() {
  const { activeConversation, addMessage, saveToStorage } = useConversations()
  const { setProcessing, setStatus, setError } = useAppState()

  /**
   * Gets messages for the current active conversation
   */
  const currentMessages = computed(() => {
    if (!activeConversation.value) return []
    return activeConversation.value.messages
  })

  /**
   * Sends a user message and generates a loopback response
   * @param {string} text - Message text to send
   * @returns {Promise<void>}
   */
  async function sendUserMessage(text) {
    // Validate message text
    const validation = validateMessageText(text)
    if (!validation.isValid) {
      setError(validation.error)
      logger.warn('Message validation failed', validation.error)
      return
    }

    if (!activeConversation.value) {
      setError('No active conversation')
      logger.error('Cannot send message: no active conversation')
      return
    }

    try {
      setProcessing(true)
      setStatus('Processing message...', 'processing')

      const now = new Date().toISOString()

      // Create user message
      const userMessage = {
        id: generateId('msg'),
        text: text.trim(),
        sender: 'user',
        timestamp: now,
        status: 'pending',
      }

      // Add user message to conversation
      addMessage(activeConversation.value.id, userMessage)

      // Simulate brief processing delay for loopback (makes it feel more natural)
      await new Promise(resolve => setTimeout(resolve, 50))

      // Create system loopback message
      const systemMessage = {
        id: generateId('msg'),
        text: text.trim(), // Echo back the same text
        sender: 'system',
        timestamp: new Date().toISOString(),
        status: 'pending',
      }

      // Add system loopback message
      addMessage(activeConversation.value.id, systemMessage)

      // Mark both messages as sent
      userMessage.status = 'sent'
      systemMessage.status = 'sent'

      // Save to storage
      saveToStorage()

      setStatus('Message sent', 'ready')
      logger.info('Message sent with loopback', { messageId: userMessage.id })
    } catch (error) {
      setError('Failed to send message')
      logger.error('Failed to send message', error)
    } finally {
      setProcessing(false)
    }
  }

  return {
    currentMessages,
    sendUserMessage,
  }
}
