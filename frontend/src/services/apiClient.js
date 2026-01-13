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
