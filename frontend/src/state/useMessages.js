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

// T021: Placeholder for deferred title generation after streaming
let pendingTitleGeneration = null

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

/**
 * Feature 023: Tool execution state
 * Tracks active tool calls during streaming
 */
const activeToolCall = ref(null)

export function useMessages() {
  const { activeConversation, addMessage, saveToStorage, generateAndSetTitle } = useConversations()
  const { setProcessing, setStatus, setError } = useAppState()
  const { selectedModelId, availableModels } = useModels() // Feature 008: Get selected model; T021: Get models for title generation

  /**
   * Gets messages for the current active conversation
   */
  const currentMessages = computed(() => {
    if (!activeConversation.value) return []
    return activeConversation.value.messages
  })

  /**
   * Feature 009: Sends a user message and receives streaming response
   * Feature 022: Returns Promise that resolves when streaming completes (for focus restoration)
   * @param {string} text - Message text to send
   * @returns {Promise<void>} Resolves when streaming is complete
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

    // Feature 022: Wrap streaming in a Promise so callers can await completion
    return new Promise((resolve, reject) => {
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

        // Gather conversation history
        const conversationHistory = activeConversation.value.messages
          .filter(msg => msg.status === 'sent')
          .map(msg => ({
            sender: msg.sender,
            text: msg.text
          }))

        logger.debug('Sending message with conversation history', {
          messageLength: text.trim().length,
          historyLength: conversationHistory.length,
          selectedModel: selectedModelId.value
        })

        // Feature 009: Use streaming API
        const streamMessageId = generateId('msg')
        startStreaming(streamMessageId, selectedModelId.value)

        // Mark user message as sent
        userMessage.status = 'sent'
        saveToStorage()

        // Set up streaming callbacks
        cleanupFunction = apiStreamMessage(
          text.trim(),
          // onToken callback
          (content) => {
            appendToken(content)
          },
          // onComplete callback
          (metadata) => {
            completeStreaming()

            // T021: Trigger title generation after streaming completes
            // Run asynchronously - don't block the completion
            const conversationId = activeConversation.value?.id
            if (conversationId && activeConversation.value?.title === 'New Conversation') {
              generateAndSetTitle(conversationId, availableModels.value, selectedModelId.value)
                .catch(err => logger.warn('Title generation failed', { error: err.message }))
            }

            setProcessing(false)
            setStatus('Message sent', 'ready')
            logger.info('Streaming completed', {
              messageId: streamMessageId,
              model: metadata.model
            })

            // Feature 022: Resolve Promise when streaming completes
            resolve()
          },
          // onError callback
          (errorEvent) => {
            errorStreaming(errorEvent.error, errorEvent.code, errorEvent.debug_info)
            setProcessing(false)
            setError(`Streaming error: ${errorEvent.error}`)
            logger.error('Streaming error', { error: errorEvent.error, code: errorEvent.code, debug_info: errorEvent.debug_info })

            // Feature 022: Resolve (not reject) on error so focus can still be restored
            resolve()
          },
          // history
          conversationHistory,
          // model
          selectedModelId.value,
          // Feature 023: onToolCall callback
          (toolInfo) => {
            handleToolCall(toolInfo)
          },
          // Feature 023: onToolResult callback
          (result) => {
            handleToolResult(result)
          }
        )
      } catch (error) {
        // Handle errors
        const errorMessage = {
          id: generateId('msg'),
          text: text.trim(),
          sender: 'user',
          timestamp: new Date().toISOString(),
          status: 'error',
          errorMessage: error.message,
          errorType: categorizeError(error),
          errorTimestamp: new Date().toISOString(),
        }

        if (error.statusCode) {
          errorMessage.errorCode = error.statusCode
        }

        if (error.details && Object.keys(error.details).length > 0) {
          errorMessage.errorDetails = JSON.stringify(error.details)
        }

        // Replace pending user message with error message
        const conversationMessages = activeConversation.value.messages
        const lastMessageIndex = conversationMessages.length - 1
        if (lastMessageIndex >= 0 && conversationMessages[lastMessageIndex].id === userMessage?.id) {
          conversationMessages[lastMessageIndex] = errorMessage
        }

        saveToStorage()

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

        setProcessing(false)

        // Feature 022: Resolve on error so focus can still be restored
        resolve()
      }
    })
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
   * @param {Object} debugInfo - Optional debug information (only in DEBUG mode)
   */
  function errorStreaming(errorMsg, errorCode, debugInfo = null) {
    if (!streamingMessage.value || !activeConversation.value) {
      logger.warn('Cannot handle streaming error: no active streaming message')
      return
    }

    // Create error message with partial text
    // Ensure text field has content (use partial response if available, otherwise placeholder)
    const errorMessage = {
      ...streamingMessage.value,
      text: streamingMessage.value.text || '[Response generation failed]',
      status: 'error',
      errorMessage: errorMsg,
      errorType: errorCode,
      errorTimestamp: new Date().toISOString(),
    }

    // Include debug info as errorDetails if available (only present when backend DEBUG=true)
    if (debugInfo) {
      errorMessage.errorDetails = JSON.stringify(debugInfo, null, 2)
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
   * Feature 023: Handle tool invocation event
   * @param {Object} toolInfo - Tool call info with tool name and args
   */
  function handleToolCall(toolInfo) {
    activeToolCall.value = {
      tool: toolInfo.tool,
      args: toolInfo.args,
      startTime: Date.now(),
    }

    // Update status to show tool is being used
    const toolDisplayName = getToolDisplayName(toolInfo.tool)
    setStatus(`Using ${toolDisplayName}...`, 'processing')
    logger.info('Tool invocation started', { tool: toolInfo.tool, args: toolInfo.args })
  }

  /**
   * Feature 023: Handle tool result event
   * @param {Object} result - Tool result with success and sources
   */
  function handleToolResult(result) {
    if (activeToolCall.value) {
      const duration = Date.now() - activeToolCall.value.startTime
      const toolDisplayName = getToolDisplayName(result.tool)

      if (result.success) {
        setStatus(`${toolDisplayName} completed`, 'processing')
        logger.info('Tool execution completed', {
          tool: result.tool,
          duration,
          sourcesCount: result.sources?.length || 0
        })
      } else {
        logger.warn('Tool execution failed', { tool: result.tool, duration })
      }
    }

    activeToolCall.value = null
  }

  /**
   * Feature 023: Get display name for a tool
   * @param {string} toolId - Tool identifier
   * @returns {string} Human-readable tool name
   */
  function getToolDisplayName(toolId) {
    const toolNames = {
      'web_search': 'Web Search',
      'bbc_news': 'BBC News Search',
    }
    return toolNames[toolId] || toolId
  }

  /**
   * T018: Reset streaming state for testing
   * @private
   */
  function __resetStreamingState() {
    streamingMessage.value = null
    isStreaming.value = false
    activeToolCall.value = null
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
    // Feature 023: Tool state
    activeToolCall,
  }
}
