/**
 * useMessages Composable
 * Manages message sending with backend API integration
 *
 * Updated for Feature 003-backend-api-loopback:
 * - T043: Call apiClient.sendMessage() instead of local loopback
 * - T044: Handle API response format (status, message, timestamp)
 */

import { computed } from 'vue'
import { generateId } from '../utils/idGenerator.js'
import { validateMessageText } from '../utils/validators.js'
import * as logger from '../utils/logger.js'
import { useConversations } from './useConversations.js'
import { useAppState } from './useAppState.js'
import { sendMessage as apiSendMessage, ApiError } from '../services/apiClient.js'

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
   * T043, T044: Sends a user message to backend API and receives loopback response
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
      setStatus('Sending message...', 'processing')

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

      // T043: Call backend API instead of local loopback
      const response = await apiSendMessage(
        text.trim(),
        activeConversation.value.id
      )

      // T044: Handle API response format (status, message, timestamp)
      if (response.status === 'success') {
        // Create system message from API response
        const systemMessage = {
          id: generateId('msg'),
          text: response.message, // Backend response with "api says: " prefix
          sender: 'system',
          timestamp: response.timestamp,
          status: 'sent',
        }

        // Add system message from API
        addMessage(activeConversation.value.id, systemMessage)

        // Mark user message as sent
        userMessage.status = 'sent'

        // Save to storage
        saveToStorage()

        setStatus('Message sent', 'ready')
        logger.info('Message sent successfully', {
          messageId: userMessage.id,
          responseTimestamp: response.timestamp,
        })
      } else {
        // Unexpected response format
        throw new Error('Unexpected response format from API')
      }
    } catch (error) {
      // Handle API errors with specific messages
      if (error instanceof ApiError) {
        setError(`Error: ${error.message}`)
        logger.error('API error sending message', {
          message: error.message,
          statusCode: error.statusCode,
          details: error.details,
        })
      } else {
        setError('Failed to send message')
        logger.error('Failed to send message', error)
      }
    } finally {
      setProcessing(false)
    }
  }

  return {
    currentMessages,
    sendUserMessage,
  }
}
