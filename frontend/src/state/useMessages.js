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

/**
 * T038: Categorize errors based on statusCode
 * @param {ApiError} error - The API error
 * @returns {string} Error category
 */
function categorizeError(error) {
  // If no statusCode, it's a network error
  if (!error.statusCode) {
    return 'Network Error'
  }

  // Categorize based on HTTP status code
  if (error.statusCode >= 400 && error.statusCode < 500) {
    return 'Validation Error'
  }

  if (error.statusCode >= 500) {
    return 'Server Error'
  }

  return 'Network Error'
}

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

    // Create user message reference for error handling
    let userMessage = null

    try {
      setProcessing(true)
      setStatus('Sending message...', 'processing')

      const now = new Date().toISOString()

      // Create user message
      userMessage = {
        id: generateId('msg'),
        text: text.trim(),
        sender: 'user',
        timestamp: now,
        status: 'pending',
      }

      // Add user message to conversation
      addMessage(activeConversation.value.id, userMessage)

      // T026: Gather conversation history (all messages before current one)
      const conversationHistory = activeConversation.value.messages
        .filter(msg => msg.status === 'sent') // Only include successfully sent messages
        .map(msg => ({
          sender: msg.sender, // 'user' or 'system'
          text: msg.text
        }))

      logger.debug('Sending message with conversation history', {
        messageLength: text.trim().length,
        historyLength: conversationHistory.length
      })

      // T043: Call backend API with conversation history
      const response = await apiSendMessage(
        text.trim(),
        activeConversation.value.id,
        conversationHistory // T026: Include history for context-aware responses
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
      // T022-T024, T038-T039, T060: Create error message with error fields
      const errorMessage = {
        id: generateId('msg'),
        text: text.trim(),
        sender: 'user',
        timestamp: new Date().toISOString(),
        status: 'error',
        errorMessage: error.message,
        errorType: categorizeError(error), // T038: Categorize based on statusCode
        errorTimestamp: new Date().toISOString(),
      }

      // T039: Add errorCode field if statusCode exists
      if (error.statusCode) {
        errorMessage.errorCode = error.statusCode
      }

      // T060: Add errorDetails field if details exist
      if (error.details && Object.keys(error.details).length > 0) {
        errorMessage.errorDetails = JSON.stringify(error.details)
      }

      // Replace pending user message with error message
      const conversationMessages = activeConversation.value.messages
      const lastMessageIndex = conversationMessages.length - 1
      if (lastMessageIndex >= 0 && conversationMessages[lastMessageIndex].id === userMessage.id) {
        conversationMessages[lastMessageIndex] = errorMessage
      }

      // Save to storage
      saveToStorage()

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
