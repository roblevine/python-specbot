/**
 * useMessages Composable
 * Manages message sending with backend API integration
 *
 * Updated for Feature 003-backend-api-loopback:
 * - T043: Call apiClient.sendMessage() instead of local loopback
 * - T044: Handle API response format (status, message, timestamp)
 */

import { computed, ref } from 'vue'
import { generateId } from '../utils/idGenerator.js'
import { validateMessageText } from '../utils/validators.js'
import * as logger from '../utils/logger.js'
import { useConversations } from './useConversations.js'
import { useAppState } from './useAppState.js'
import { sendMessage as apiSendMessage, ApiError, streamMessage as apiStreamMessage } from '../services/apiClient.js'
import { useModels } from './useModels.js'

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

/**
 * T018: Streaming state management
 * Feature: 009-message-streaming User Story 1
 */
const streamingMessage = ref(null)
const isStreaming = ref(false)
let cleanupFunction = null

export function useMessages() {
  const { activeConversation, addMessage, saveToStorage } = useConversations()
  const { setProcessing, setStatus, setError } = useAppState()
  const { selectedModelId } = useModels() // Feature 008: Get selected model

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
        historyLength: conversationHistory.length,
        selectedModel: selectedModelId.value
      })

      // T043: Call backend API with conversation history and selected model
      const response = await apiSendMessage(
        text.trim(),
        activeConversation.value.id,
        conversationHistory, // T026: Include history for context-aware responses
        selectedModelId.value // Feature 008 T030: Include selected model
      )

      // T044: Handle API response format (status, message, timestamp, model)
      if (response.status === 'success') {
        // Create system message from API response
        const systemMessage = {
          id: generateId('msg'),
          text: response.message, // Backend response with "api says: " prefix
          sender: 'system',
          timestamp: response.timestamp,
          status: 'sent',
          model: response.model, // Feature 008 T033: Store model that generated response
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

  /**
   * T018: Start streaming a response
   * @param {string} messageId - Message ID for the streaming message
   * @param {string} model - Model being used for generation
   */
  function startStreaming(messageId, model = null) {
    // Prevent starting new stream if already streaming
    if (isStreaming.value) {
      logger.warn('Cannot start new stream: already streaming')
      return
    }

    const now = new Date().toISOString()

    streamingMessage.value = {
      id: messageId,
      text: '',
      sender: 'system',
      timestamp: now,
      status: 'streaming',
      model: model,
    }

    isStreaming.value = true
    logger.logStreamStart('Streaming response', { messageId, model })
  }

  /**
   * T018: Append a token to the streaming message
   * @param {string} token - Token content to append
   */
  function appendToken(token) {
    if (!streamingMessage.value) {
      logger.warn('Cannot append token: no active streaming message')
      return
    }

    streamingMessage.value.text += token
  }

  /**
   * T018: Complete streaming and move message to conversation
   */
  function completeStreaming() {
    if (!streamingMessage.value || !activeConversation.value) {
      logger.warn('Cannot complete streaming: no active streaming message or conversation')
      return
    }

    // Update status to sent
    const completedMessage = {
      ...streamingMessage.value,
      status: 'sent',
    }

    // Add to conversation messages
    addMessage(activeConversation.value.id, completedMessage)

    // Save to storage
    saveToStorage()

    // Clean up streaming state
    streamingMessage.value = null
    isStreaming.value = false

    if (cleanupFunction) {
      cleanupFunction()
      cleanupFunction = null
    }

    logger.logStreamComplete(0, completedMessage.text.length, completedMessage.model)
  }

  /**
   * T018: Abort streaming (user cancelled)
   */
  function abortStreaming() {
    if (cleanupFunction) {
      cleanupFunction()
      cleanupFunction = null
    }

    streamingMessage.value = null
    isStreaming.value = false

    logger.logStreamAbort('user_cancelled')
  }

  /**
   * T018: Handle streaming error
   * @param {string} errorMsg - Error message
   * @param {string} errorCode - Error code
   */
  function errorStreaming(errorMsg, errorCode) {
    if (!streamingMessage.value || !activeConversation.value) {
      logger.warn('Cannot handle streaming error: no active streaming message')
      return
    }

    // Create error message with partial text
    const errorMessage = {
      ...streamingMessage.value,
      status: 'error',
      errorMessage: errorMsg,
      errorType: errorCode,
      errorTimestamp: new Date().toISOString(),
    }

    // Add error message to conversation
    addMessage(activeConversation.value.id, errorMessage)

    // Save to storage
    saveToStorage()

    // Clean up streaming state
    streamingMessage.value = null
    isStreaming.value = false

    if (cleanupFunction) {
      cleanupFunction()
      cleanupFunction = null
    }

    logger.logStreamError(errorMsg, { code: errorCode })
  }

  /**
   * T018: Reset streaming state for testing
   * @private
   */
  function __resetStreamingState() {
    streamingMessage.value = null
    isStreaming.value = false
    if (cleanupFunction) {
      cleanupFunction()
      cleanupFunction = null
    }
  }

  return {
    currentMessages,
    sendUserMessage,
    // T018: Streaming state and functions
    streamingMessage,
    isStreaming,
    startStreaming,
    appendToken,
    completeStreaming,
    abortStreaming,
    errorStreaming,
    __resetStreamingState, // For testing
  }
}
