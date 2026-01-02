/**
 * useMessages Composable
 * Manages message sending with backend API integration
 *
 * Updated for Feature 003-backend-api-loopback:
 * - T043: Call apiClient.sendMessage() instead of local loopback
 * - T044: Handle API response format (status, message, timestamp)
 *
 * Updated for Feature 005-llm-integration (T027-T028):
 * - Add streaming state management (isStreaming, partialText, etc.)
 * - Implement sendStreamingMessage with LLM streaming
 */

import { ref, computed } from 'vue'
import { generateId } from '../utils/idGenerator.js'
import { validateMessageText } from '../utils/validators.js'
import * as logger from '../utils/logger.js'
import { useConversations } from './useConversations.js'
import { useAppState } from './useAppState.js'
import { sendMessage as apiSendMessage, ApiError } from '../services/apiClient.js'
import { StreamingClient } from '../services/streamingClient.js'
import { useModelSelection } from './useModelSelection.js'

// Initialize streaming client
const streamingClient = new StreamingClient()

// Streaming state (shared across all instances)
const isStreaming = ref(false)
const streamingMessageId = ref(null)
const partialText = ref('')
const streamController = ref(null)

export function useMessages() {
  const { activeConversation, addMessage, saveToStorage } = useConversations()
  const { setProcessing, setStatus, setError } = useAppState()
  const { selectedModel } = useModelSelection()

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

  /**
   * T027-T028: Send message with LLM streaming
   * @param {string} text - Message text to send
   * @returns {Promise<void>}
   */
  async function sendStreamingMessage(text) {
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

    if (isStreaming.value) {
      logger.warn('Already streaming - ignoring new request')
      return
    }

    try {
      isStreaming.value = true
      setStatus('Sending message...', 'processing')

      const now = new Date().toISOString()

      // Create user message
      const userMessage = {
        id: generateId('msg'),
        text: text.trim(),
        sender: 'user',
        timestamp: now,
        status: 'sent',
      }

      // Add user message to conversation
      addMessage(activeConversation.value.id, userMessage)

      // Build conversation history for context (for now empty, US3 will implement)
      const conversationHistory = []

      // Create placeholder assistant message for streaming
      const assistantMessageId = generateId('msg')
      const assistantMessage = {
        id: assistantMessageId,
        text: '',
        sender: 'assistant',
        timestamp: now,
        status: 'streaming',
        model: selectedModel.value,
      }

      addMessage(activeConversation.value.id, assistantMessage)
      streamingMessageId.value = assistantMessageId
      partialText.value = ''

      logger.info('Starting stream', {
        userMessageId: userMessage.id,
        assistantMessageId,
        model: selectedModel.value,
      })

      // Stream response
      await streamingClient.streamChat(
        text.trim(),
        activeConversation.value.id,
        conversationHistory,
        selectedModel.value,
        {
          onStart: (messageId) => {
            logger.debug('Stream started', { messageId })
            setStatus('AI is responding...', 'processing')
          },

          onChunk: (content) => {
            // Accumulate chunks
            partialText.value += content
            assistantMessage.text = partialText.value

            // Trigger reactivity update
            saveToStorage()
          },

          onDone: (messageId, model) => {
            logger.info('Stream completed', { messageId, model, length: partialText.value.length })

            assistantMessage.status = 'completed'
            assistantMessage.model = model
            saveToStorage()

            setStatus('Ready', 'ready')
            isStreaming.value = false
            streamingMessageId.value = null
            partialText.value = ''
            streamController.value = null
          },

          onError: (code, message, details) => {
            logger.error('Stream error', { code, message, details })

            // Update message with error
            assistantMessage.text = partialText.value || ''
            assistantMessage.status = 'error'
            assistantMessage.error = { code, message }
            saveToStorage()

            setError(message)
            setStatus('Error', 'error')
            isStreaming.value = false
            streamingMessageId.value = null
            partialText.value = ''
            streamController.value = null
          }
        }
      )

    } catch (error) {
      logger.error('Failed to stream message', error)
      setError('Failed to send message')
      isStreaming.value = false
      streamingMessageId.value = null
      partialText.value = ''
      streamController.value = null
    }
  }

  /**
   * Stop active stream (T026)
   */
  function stopStream() {
    if (isStreaming.value && streamController.value) {
      logger.info('Stopping stream by user request')
      streamingClient.stopStream()

      // Add interruption message
      if (activeConversation.value && streamingMessageId.value) {
        const interruptionMessage = {
          id: generateId('msg'),
          text: 'Conversation interrupted by user',
          sender: 'system',
          timestamp: new Date().toISOString(),
          status: 'sent',
        }

        addMessage(activeConversation.value.id, interruptionMessage)
        saveToStorage()
      }

      isStreaming.value = false
      streamingMessageId.value = null
      partialText.value = ''
      streamController.value = null
      setStatus('Ready', 'ready')
    }
  }

  return {
    currentMessages,
    sendUserMessage,
    // T027-T028: Streaming functionality
    sendStreamingMessage,
    stopStream,
    isStreaming,
    streamingMessageId,
    partialText,
  }
}
