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
   * This is a skeleton implementation. Full implementation in T025.
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
    // Skeleton - full implementation in T025
    console.log('StreamingClient.streamChat called:', {
      message,
      conversationId,
      historyLength: conversationHistory?.length || 0,
      model
    })

    throw new Error('StreamingClient.streamChat not yet implemented (T025)')
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
