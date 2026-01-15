/**
 * API Client for Backend Communication
 *
 * Handles HTTP requests to the backend API server.
 * Implements T040-T042: sendMessage with error handling and timeout.
 *
 * Feature: 003-backend-api-loopback User Story 1
 */

import * as logger from '../utils/logger.js'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_TIMEOUT = 120000 // 120 seconds (2 minutes) - increased to support large LLM responses

// T033: Retry configuration
const DEFAULT_RETRY_OPTIONS = {
  maxRetries: 3,
  baseDelayMs: 1000,
  maxDelayMs: 10000,
  retryableStatusCodes: [408, 429, 500, 502, 503, 504], // Request Timeout, Too Many Requests, Server Errors
}

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  constructor(message, statusCode = null, details = null) {
    super(message)
    this.name = 'ApiError'
    this.statusCode = statusCode
    this.details = details
  }
}

/**
 * T033: Retry helper with exponential backoff
 * Wraps an async function with retry logic for transient failures
 *
 * @param {Function} fn - Async function to retry
 * @param {object} options - Retry options
 * @returns {Promise<any>} - Result of the function call
 * @throws {ApiError} - After all retries exhausted
 */
async function withRetry(fn, options = {}) {
  const opts = { ...DEFAULT_RETRY_OPTIONS, ...options }
  let lastError = null

  for (let attempt = 0; attempt <= opts.maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error

      // Check if error is retryable
      const isNetworkError = error instanceof TypeError && error.message.includes('fetch')
      const isRetryableStatus = error.statusCode && opts.retryableStatusCodes.includes(error.statusCode)

      if (!isNetworkError && !isRetryableStatus) {
        // Non-retryable error, throw immediately
        throw error
      }

      if (attempt < opts.maxRetries) {
        // Calculate delay with exponential backoff + jitter
        const delay = Math.min(
          opts.baseDelayMs * Math.pow(2, attempt) + Math.random() * 1000,
          opts.maxDelayMs
        )

        logger.debug(`Retry attempt ${attempt + 1}/${opts.maxRetries} after ${delay}ms`, {
          error: error.message,
          statusCode: error.statusCode,
        })

        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  }

  // All retries exhausted
  logger.error('All retries exhausted', { error: lastError?.message })
  throw lastError
}

/**
 * T040: Send message to backend API
 * T041: Error handling for network errors, timeouts, HTTP errors
 * T042: 10-second timeout (per FR-009)
 * T025: Added conversation history support for context-aware responses
 * T030: Added model parameter for model selection (Feature 008)
 *
 * @param {string} messageText - The message to send
 * @param {string} conversationId - Optional conversation ID
 * @param {Array<{sender: string, text: string}>} history - Optional conversation history
 * @param {string} model - Optional model ID to use for this request (Feature 008: T030)
 * @returns {Promise<{status: string, message: string, timestamp: string, model: string}>}
 * @throws {ApiError} - On network, timeout, or HTTP errors
 */
export async function sendMessage(messageText, conversationId = null, history = null, model = null) {
  logger.debug('Sending message to backend API', { messageText, conversationId, historyLength: history?.length, model })

  // Create request payload
  const requestBody = {
    message: messageText,
  }

  if (conversationId) {
    requestBody.conversationId = conversationId
  }

  // T025: Include conversation history if provided
  if (history && history.length > 0) {
    requestBody.history = history
  }

  // T030: Include model selection if provided
  if (model) {
    requestBody.model = model
  }

  // Add client-side timestamp
  requestBody.timestamp = new Date().toISOString()

  // Create abort controller for timeout
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT)

  try {
    // Make POST request
    const response = await fetch(`${API_BASE_URL}/api/v1/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
      signal: controller.signal,
    })

    // Clear timeout
    clearTimeout(timeoutId)

    // Handle HTTP error responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))

      logger.warn('Backend returned error response', {
        status: response.status,
        error: errorData,
      })

      // Map HTTP status codes to user-friendly messages
      let errorMessage = 'Unknown error occurred'

      if (response.status === 400) {
        errorMessage = errorData.error || 'Invalid message format'
      } else if (response.status === 422) {
        errorMessage = errorData.error || 'Message validation failed'
      } else if (response.status === 500) {
        errorMessage = 'Server error occurred'
      } else if (response.status === 503) {
        errorMessage = 'Service temporarily unavailable'
      }

      throw new ApiError(errorMessage, response.status, errorData)
    }

    // Parse successful response
    const data = await response.json()

    logger.info('Message sent successfully', { response: data })

    return data

  } catch (error) {
    clearTimeout(timeoutId)

    // Handle timeout errors
    if (error.name === 'AbortError') {
      logger.error('Request timed out', { timeout: API_TIMEOUT })
      throw new ApiError('Request timed out. Please try again.', null, { timeout: true })
    }

    // Handle network errors (backend not running, DNS issues, etc.)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      logger.error('Cannot connect to backend', error)
      throw new ApiError('Cannot connect to server', null, { network: true })
    }

    // Re-throw ApiError instances
    if (error instanceof ApiError) {
      throw error
    }

    // Handle unexpected errors
    logger.error('Unexpected error sending message', error)
    throw new ApiError('Failed to send message', null, { originalError: error })
  }
}

/**
 * T031: Fetch available models from backend
 *
 * Feature: 008-openai-model-selector User Story 1
 *
 * @returns {Promise<{models: Array<{id: string, name: string, description: string, default: boolean}>}>}
 * @throws {ApiError} - On network or HTTP errors
 */
export async function fetchModels() {
  logger.debug('Fetching available models from backend API')

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/models`, {
      method: 'GET',
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))

      logger.warn('Backend returned error fetching models', {
        status: response.status,
        error: errorData,
      })

      let errorMessage = 'Failed to fetch models'

      if (response.status === 503) {
        errorMessage = 'Model service temporarily unavailable'
      }

      throw new ApiError(errorMessage, response.status, errorData)
    }

    const data = await response.json()

    logger.info('Models fetched successfully', { count: data.models?.length })

    return data

  } catch (error) {
    // Handle network errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      logger.error('Cannot connect to backend to fetch models', error)
      throw new ApiError('Cannot connect to server', null, { network: true })
    }

    // Re-throw ApiError instances
    if (error instanceof ApiError) {
      throw error
    }

    // Handle unexpected errors
    logger.error('Unexpected error fetching models', error)
    throw new ApiError('Failed to fetch models', null, { originalError: error })
  }
}

/**
 * T015: Stream message with real-time token-by-token responses
 *
 * Uses fetch + ReadableStream to parse SSE (Server-Sent Events) format.
 * EventSource doesn't support POST, so we use fetch with manual SSE parsing.
 *
 * Feature: 009-message-streaming User Story 1
 *
 * @param {string} messageText - The message to send
 * @param {Function} onToken - Callback for each token: (content: string) => void
 * @param {Function} onComplete - Callback when complete: (metadata: object) => void
 * @param {Function} onError - Optional callback for errors: (error: object) => void
 * @param {Array<{sender: string, text: string}>} history - Optional conversation history
 * @param {string} model - Optional model ID to use for this request
 * @returns {Function} cleanup - Call to abort the stream
 */
export function streamMessage(messageText, onToken, onComplete, onError = null, history = null, model = null) {
  logger.debug('Starting streaming message', { messageText, historyLength: history?.length, model })

  // Validate callbacks are functions to prevent silent failures
  if (typeof onToken !== 'function') {
    const error = new Error('onToken must be a function')
    logger.error('Invalid callback', { onToken })
    if (onError && typeof onError === 'function') {
      onError({ error: error.message, code: 'INVALID_CALLBACK' })
    }
    throw error
  }

  if (typeof onComplete !== 'function') {
    const error = new Error('onComplete must be a function')
    logger.error('Invalid callback', { onComplete })
    if (onError && typeof onError === 'function') {
      onError({ error: error.message, code: 'INVALID_CALLBACK' })
    }
    throw error
  }

  // Create request payload
  const requestBody = {
    message: messageText,
    timestamp: new Date().toISOString(),
  }

  if (history && history.length > 0) {
    requestBody.history = history
  }

  if (model) {
    requestBody.model = model
  }

  // Create abort controller for cleanup
  const controller = new AbortController()

  // Track if we've received any tokens (for timeout detection)
  let receivedFirstToken = false
  let streamTimeout = null

  // Set a timeout to detect if streaming hangs (no tokens received)
  const STREAM_START_TIMEOUT = 30000 // 30 seconds to receive first token
  streamTimeout = setTimeout(() => {
    if (!receivedFirstToken) {
      logger.error('Streaming timeout - no tokens received')
      if (onError && typeof onError === 'function') {
        onError({
          error: 'Streaming request timed out. No response received from server.',
          code: 'STREAM_TIMEOUT',
        })
      }
      controller.abort()
    }
  }, STREAM_START_TIMEOUT)

  // Start streaming in background (don't await)
  const streamPromise = (async () => {
    try {
      // Make POST request with streaming headers
      const response = await fetch(`${API_BASE_URL}/api/v1/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify(requestBody),
        signal: controller.signal,
      })

      // Handle HTTP errors
      if (!response.ok) {
        clearTimeout(streamTimeout)
        const errorData = await response.json().catch(() => ({ error: response.statusText }))
        logger.warn('Streaming request failed', { status: response.status, error: errorData })

        if (onError && typeof onError === 'function') {
          onError({
            error: errorData.error || 'Request failed',
            code: `HTTP_${response.status}`,
            statusCode: response.status,
          })
        }
        return
      }

      // Get readable stream reader
      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = '' // Buffer for partial SSE events

      // Read stream chunks
      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          logger.debug('Stream completed')
          clearTimeout(streamTimeout)
          break
        }

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true })

        // Process complete SSE events (format: "data: {...}\n\n")
        const events = buffer.split('\n\n')

        // Keep last incomplete event in buffer
        buffer = events.pop() || ''

        // Process each complete event
        for (const eventString of events) {
          if (!eventString.trim() || !eventString.startsWith('data: ')) {
            continue
          }

          try {
            // Parse JSON from SSE format
            const jsonString = eventString.substring(6) // Remove "data: " prefix
            const event = JSON.parse(jsonString)

            // Handle different event types
            if (event.type === 'token') {
              receivedFirstToken = true
              clearTimeout(streamTimeout) // Clear timeout once we start receiving tokens

              try {
                onToken(event.content)
              } catch (callbackError) {
                logger.error('Error in onToken callback', callbackError)
                // Report callback errors to user
                if (onError && typeof onError === 'function') {
                  onError({
                    error: 'Error processing streamed token',
                    code: 'CALLBACK_ERROR',
                    originalError: callbackError.message,
                  })
                }
              }
            } else if (event.type === 'complete') {
              try {
                onComplete(event)
              } catch (callbackError) {
                logger.error('Error in onComplete callback', callbackError)
                if (onError && typeof onError === 'function') {
                  onError({
                    error: 'Error completing stream',
                    code: 'CALLBACK_ERROR',
                    originalError: callbackError.message,
                  })
                }
              }
            } else if (event.type === 'error') {
              if (onError && typeof onError === 'function') {
                onError(event)
              }
            }
          } catch (parseError) {
            logger.error('Failed to parse SSE event', { eventString, error: parseError })
            // Report parse errors to user instead of silently failing
            if (onError && typeof onError === 'function') {
              onError({
                error: 'Error parsing server response',
                code: 'PARSE_ERROR',
                originalError: parseError.message,
              })
            }
          }
        }
      }
    } catch (error) {
      clearTimeout(streamTimeout)

      // Handle abort (cleanup called)
      if (error.name === 'AbortError') {
        logger.debug('Stream aborted by user')
        return
      }

      // Handle network errors
      logger.error('Streaming error', error)

      if (onError && typeof onError === 'function') {
        onError({
          error: error.message || 'Network error',
          code: 'NETWORK_ERROR',
          originalError: error,
        })
      }
    }
  })()

  // Return cleanup function
  return () => {
    logger.debug('Aborting stream')
    clearTimeout(streamTimeout)
    controller.abort()
  }
}

/**
 * Health check endpoint
 * @returns {Promise<{status: string}>}
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
    })

    if (!response.ok) {
      throw new Error('Health check failed')
    }

    return await response.json()
  } catch (error) {
    logger.error('Health check failed', error)
    throw new ApiError('Backend health check failed', null, { originalError: error })
  }
}

// ============================================================================
// Conversation API (Feature: 010-server-side-conversations)
// ============================================================================

/**
 * T014: Get all conversations from server
 *
 * Feature: 010-server-side-conversations User Story 1
 *
 * @returns {Promise<{status: string, conversations: Array}>}
 * @throws {ApiError} - On network or HTTP errors
 */
export async function getConversations() {
  logger.debug('Fetching conversations from server')

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/conversations`, {
      method: 'GET',
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))

      logger.warn('Failed to fetch conversations', {
        status: response.status,
        error: errorData,
      })

      throw new ApiError(
        errorData.error || 'Failed to fetch conversations',
        response.status,
        errorData
      )
    }

    const data = await response.json()
    logger.info('Conversations fetched successfully', { count: data.conversations?.length })

    return data
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      logger.error('Cannot connect to backend to fetch conversations', error)
      throw new ApiError('Cannot connect to server', null, { network: true })
    }

    if (error instanceof ApiError) {
      throw error
    }

    logger.error('Unexpected error fetching conversations', error)
    throw new ApiError('Failed to fetch conversations', null, { originalError: error })
  }
}

/**
 * T015: Get a single conversation by ID
 *
 * Feature: 010-server-side-conversations User Story 1
 *
 * @param {string} conversationId - The conversation ID to fetch
 * @returns {Promise<{status: string, conversation: object}>}
 * @throws {ApiError} - On network or HTTP errors
 */
export async function getConversation(conversationId) {
  logger.debug('Fetching conversation from server', { conversationId })

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/conversations/${conversationId}`, {
      method: 'GET',
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))

      logger.warn('Failed to fetch conversation', {
        conversationId,
        status: response.status,
        error: errorData,
      })

      if (response.status === 404) {
        throw new ApiError('Conversation not found', response.status, errorData)
      }

      throw new ApiError(
        errorData.error || 'Failed to fetch conversation',
        response.status,
        errorData
      )
    }

    const data = await response.json()
    logger.info('Conversation fetched successfully', { conversationId })

    return data
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      logger.error('Cannot connect to backend to fetch conversation', error)
      throw new ApiError('Cannot connect to server', null, { network: true })
    }

    if (error instanceof ApiError) {
      throw error
    }

    logger.error('Unexpected error fetching conversation', error)
    throw new ApiError('Failed to fetch conversation', null, { originalError: error })
  }
}

/**
 * T021: Create a new conversation on server
 *
 * Feature: 010-server-side-conversations User Story 2
 *
 * @param {object} conversationData - Optional conversation data (id, title, messages)
 * @returns {Promise<{status: string, conversation: object}>}
 * @throws {ApiError} - On network or HTTP errors
 */
export async function createConversation(conversationData = {}) {
  logger.debug('Creating conversation on server', { conversationData })

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(conversationData),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))

      logger.warn('Failed to create conversation', {
        status: response.status,
        error: errorData,
      })

      throw new ApiError(
        errorData.error || 'Failed to create conversation',
        response.status,
        errorData
      )
    }

    const data = await response.json()
    logger.info('Conversation created successfully', { conversationId: data.conversation?.id })

    return data
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      logger.error('Cannot connect to backend to create conversation', error)
      throw new ApiError('Cannot connect to server', null, { network: true })
    }

    if (error instanceof ApiError) {
      throw error
    }

    logger.error('Unexpected error creating conversation', error)
    throw new ApiError('Failed to create conversation', null, { originalError: error })
  }
}

/**
 * T022: Update a conversation on server
 *
 * Feature: 010-server-side-conversations User Story 2
 *
 * @param {string} conversationId - The conversation ID to update
 * @param {object} updateData - Data to update (title, messages)
 * @returns {Promise<{status: string, conversation: object}>}
 * @throws {ApiError} - On network or HTTP errors
 */
export async function updateConversation(conversationId, updateData) {
  logger.debug('Updating conversation on server', { conversationId, updateData })

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/conversations/${conversationId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updateData),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))

      logger.warn('Failed to update conversation', {
        conversationId,
        status: response.status,
        error: errorData,
      })

      if (response.status === 404) {
        throw new ApiError('Conversation not found', response.status, errorData)
      }

      throw new ApiError(
        errorData.error || 'Failed to update conversation',
        response.status,
        errorData
      )
    }

    const data = await response.json()
    logger.info('Conversation updated successfully', { conversationId })

    return data
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      logger.error('Cannot connect to backend to update conversation', error)
      throw new ApiError('Cannot connect to server', null, { network: true })
    }

    if (error instanceof ApiError) {
      throw error
    }

    logger.error('Unexpected error updating conversation', error)
    throw new ApiError('Failed to update conversation', null, { originalError: error })
  }
}

/**
 * T029: Delete a conversation from server
 *
 * Feature: 010-server-side-conversations User Story 3
 *
 * @param {string} conversationId - The conversation ID to delete
 * @returns {Promise<void>}
 * @throws {ApiError} - On network or HTTP errors
 */
export async function deleteConversation(conversationId) {
  logger.debug('Deleting conversation from server', { conversationId })

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/conversations/${conversationId}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))

      logger.warn('Failed to delete conversation', {
        conversationId,
        status: response.status,
        error: errorData,
      })

      if (response.status === 404) {
        throw new ApiError('Conversation not found', response.status, errorData)
      }

      throw new ApiError(
        errorData.error || 'Failed to delete conversation',
        response.status,
        errorData
      )
    }

    logger.info('Conversation deleted successfully', { conversationId })
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      logger.error('Cannot connect to backend to delete conversation', error)
      throw new ApiError('Cannot connect to server', null, { network: true })
    }

    if (error instanceof ApiError) {
      throw error
    }

    logger.error('Unexpected error deleting conversation', error)
    throw new ApiError('Failed to delete conversation', null, { originalError: error })
  }
}

/**
 * T033: Check server connectivity
 * Performs a quick health check to determine if server is reachable
 *
 * @returns {Promise<boolean>} - True if server is reachable
 */
export async function isServerReachable() {
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 second timeout

    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      signal: controller.signal,
    })

    clearTimeout(timeoutId)
    return response.ok
  } catch (error) {
    return false
  }
}

/**
 * T033: Export withRetry for use by consumers
 * Allows wrapping any async function with retry logic
 */
export { withRetry }
