/**
 * Streaming Client for LLM Chat Responses
 *
 * Handles Server-Sent Events (SSE) streaming from the backend chat API.
 * Uses fetch with ReadableStream for POST requests (EventSource only supports GET).
 *
 * Feature: 005-llm-integration
 * Tasks: T009 (skeleton), T025-T026 (implementation)
 */

export class StreamingClient {
  /**
   * Create a new streaming client.
   *
   * @param {string} baseURL - Base URL for the API (default: from env or localhost:8000)
   */
  constructor(baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') {
    this.baseURL = baseURL
    this.activeStream = null
  }

  /**
   * Start streaming chat response.
   *
   * T025: Full implementation with fetch + ReadableStream and SSE parsing.
   *
   * @param {string} message - User message
   * @param {string} conversationId - Conversation ID (conv-<uuid>)
   * @param {Array} conversationHistory - Previous messages [{role, content}, ...]
   * @param {string} model - LLM model ("gpt-5" or "gpt-5-codex")
   * @param {Object} callbacks - Event handlers
   * @param {Function} callbacks.onStart - Called when stream starts with messageId
   * @param {Function} callbacks.onChunk - Called for each content chunk
   * @param {Function} callbacks.onDone - Called when stream completes
   * @param {Function} callbacks.onError - Called on errors
   * @returns {AbortController} Controller to cancel stream
   */
  async streamChat(message, conversationId, conversationHistory, model, callbacks) {
    const controller = new AbortController()
    this.activeStream = controller

    try {
      const response = await fetch(`${this.baseURL}/api/v1/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message,
          conversationId,
          conversationHistory: conversationHistory || [],
          model: model || 'gpt-5'
        }),
        signal: controller.signal
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      // Parse SSE stream
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          break
        }

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true })

        // Process complete events (separated by double newlines)
        const events = buffer.split('\n\n')

        // Keep the last incomplete event in buffer
        buffer = events.pop()

        for (const eventText of events) {
          if (!eventText.trim()) continue

          // Parse SSE format: "event: type\ndata: json"
          const lines = eventText.split('\n')
          let eventType = 'message'
          let eventData = null

          for (const line of lines) {
            if (line.startsWith('event:')) {
              eventType = line.substring(6).trim()
            } else if (line.startsWith('data:')) {
              const dataStr = line.substring(5).trim()
              try {
                eventData = JSON.parse(dataStr)
              } catch (e) {
                console.error('Failed to parse SSE data:', dataStr, e)
              }
            }
          }

          if (!eventData) continue

          // Handle different event types
          if (eventType === 'message') {
            if (eventData.type === 'start') {
              callbacks.onStart?.(eventData.messageId)
            } else if (eventData.type === 'chunk') {
              callbacks.onChunk?.(eventData.content)
            } else if (eventData.type === 'done') {
              callbacks.onDone?.(eventData.messageId, eventData.model)
            }
          } else if (eventType === 'error') {
            callbacks.onError?.(eventData.code, eventData.message, eventData.details)
          }
        }
      }

      this.activeStream = null
      return controller

    } catch (error) {
      this.activeStream = null

      if (error.name === 'AbortError') {
        // Stream was cancelled by user
        console.log('Stream cancelled by user')
      } else {
        // Network or other error
        console.error('Stream error:', error)
        callbacks.onError?.('network_error', error.message, { originalError: error })
      }

      throw error
    }
  }

  /**
   * Stop active stream.
   *
   * This is a skeleton implementation. Full implementation in T026.
   */
  stopStream() {
    // Skeleton - full implementation in T026
    console.log('StreamingClient.stopStream called')

    if (this.activeStream) {
      this.activeStream.abort()
      this.activeStream = null
    }
  }
}
