import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useMessages } from '../../src/state/useMessages.js'
import { useConversations } from '../../src/state/useConversations.js'
import { useAppState } from '../../src/state/useAppState.js'

// Mock the API client
vi.mock('../../src/services/apiClient.js', () => ({
  sendMessage: vi.fn((messageText) => {
    return Promise.resolve({
      status: 'success',
      message: messageText,
      timestamp: new Date().toISOString()
    })
  }),
  ApiError: class ApiError extends Error {
    constructor(message, statusCode = null, details = null) {
      super(message)
      this.name = 'ApiError'
      this.statusCode = statusCode
      this.details = details
    }
  }
}))

describe('useMessages', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllTimers()
    const { __resetState } = useConversations()
    __resetState()
  })

  it('should return empty messages for no active conversation', () => {
    const { currentMessages } = useMessages()

    expect(currentMessages.value).toEqual([])
  })

  it('should send user message and create loopback', async () => {
    const { createConversation } = useConversations()
    const { sendUserMessage, currentMessages } = useMessages()

    createConversation()
    await sendUserMessage('Hello world')

    expect(currentMessages.value).toHaveLength(2)
    expect(currentMessages.value[0].sender).toBe('user')
    expect(currentMessages.value[0].text).toBe('Hello world')
    expect(currentMessages.value[1].sender).toBe('system')
    expect(currentMessages.value[1].text).toBe('Hello world')
  })

  it('should mark messages as sent', async () => {
    const { createConversation } = useConversations()
    const { sendUserMessage, currentMessages } = useMessages()

    createConversation()
    await sendUserMessage('Test message')

    expect(currentMessages.value[0].status).toBe('sent')
    expect(currentMessages.value[1].status).toBe('sent')
  })

  it('should trim message text', async () => {
    const { createConversation } = useConversations()
    const { sendUserMessage, currentMessages } = useMessages()

    createConversation()
    await sendUserMessage('  Message with spaces  ')

    expect(currentMessages.value[0].text).toBe('Message with spaces')
    expect(currentMessages.value[1].text).toBe('Message with spaces')
  })

  it('should not send empty message', async () => {
    const { createConversation } = useConversations()
    const { sendUserMessage, currentMessages } = useMessages()

    createConversation()
    await sendUserMessage('')

    expect(currentMessages.value).toHaveLength(0)
  })

  it('should not send whitespace-only message', async () => {
    const { createConversation } = useConversations()
    const { sendUserMessage, currentMessages } = useMessages()

    createConversation()
    await sendUserMessage('   \n\t  ')

    expect(currentMessages.value).toHaveLength(0)
  })

  it('should set error status for invalid message', async () => {
    const { createConversation } = useConversations()
    const { sendUserMessage } = useMessages()
    const { statusType } = useAppState()

    createConversation()
    await sendUserMessage('')

    expect(statusType.value).toBe('error')
  })

  it('should save to storage after sending message', async () => {
    const { createConversation } = useConversations()
    const { sendUserMessage } = useMessages()

    createConversation()
    await sendUserMessage('Test message')

    const stored = localStorage.getItem('chatInterface:v1:data')
    expect(stored).toBeTruthy()

    const data = JSON.parse(stored)
    expect(data.conversations[0].messages).toHaveLength(2)
  })

  // US1: Error handling tests
  it('should create error message when API call fails', async () => {
    const apiClient = await import('../../src/services/apiClient.js')
    const { createConversation } = useConversations()
    const { sendUserMessage, currentMessages } = useMessages()

    // Mock API to throw error
    vi.mocked(apiClient.sendMessage).mockRejectedValueOnce(
      new apiClient.ApiError('Cannot connect to server', null, {})
    )

    createConversation()
    await sendUserMessage('Test message')

    const messages = currentMessages.value
    const errorMessage = messages[messages.length - 1]

    expect(errorMessage.status).toBe('error')
    expect(errorMessage.errorMessage).toBe('Cannot connect to server')
    expect(errorMessage.errorType).toBe('Network Error')
  })

  it('should populate errorMessage, errorType, errorTimestamp fields', async () => {
    const apiClient = await import('../../src/services/apiClient.js')
    const { createConversation } = useConversations()
    const { sendUserMessage, currentMessages } = useMessages()

    vi.mocked(apiClient.sendMessage).mockRejectedValueOnce(
      new apiClient.ApiError('Network failure', null, {})
    )

    createConversation()
    const beforeTime = new Date().toISOString()
    await sendUserMessage('Test message')
    const afterTime = new Date().toISOString()

    const errorMessage = currentMessages.value[0]

    expect(errorMessage.errorMessage).toBe('Network failure')
    expect(errorMessage.errorType).toBe('Network Error')
    expect(errorMessage.errorTimestamp).toBeDefined()
    expect(errorMessage.errorTimestamp >= beforeTime).toBe(true)
    expect(errorMessage.errorTimestamp <= afterTime).toBe(true)
  })

  it('should categorize network errors correctly', async () => {
    const apiClient = await import('../../src/services/apiClient.js')
    const { createConversation } = useConversations()
    const { sendUserMessage, currentMessages } = useMessages()

    vi.mocked(apiClient.sendMessage).mockRejectedValueOnce(
      new apiClient.ApiError('Timeout', null, {})
    )

    createConversation()
    await sendUserMessage('Test')

    expect(currentMessages.value[0].errorType).toBe('Network Error')
  })

  /**
   * T017: Tests for streaming state management
   * Feature: 009-message-streaming User Story 1
   */
  describe('Streaming', () => {
    beforeEach(() => {
      // Reset streaming state before each test
      const { __resetStreamingState } = useMessages()
      __resetStreamingState()
    })

    it('should have streamingMessage state initially null', () => {
      const { streamingMessage } = useMessages()
      expect(streamingMessage.value).toBeNull()
    })

    it('should have isStreaming state initially false', () => {
      const { isStreaming } = useMessages()
      expect(isStreaming.value).toBe(false)
    })

    it('should start streaming and create streamingMessage', () => {
      const { createConversation } = useConversations()
      const { startStreaming, streamingMessage, isStreaming } = useMessages()

      createConversation()
      const messageId = 'msg-stream-123'
      const model = 'gpt-4'

      startStreaming(messageId, model)

      expect(streamingMessage.value).toBeDefined()
      expect(streamingMessage.value.id).toBe(messageId)
      expect(streamingMessage.value.text).toBe('')
      expect(streamingMessage.value.sender).toBe('system')
      expect(streamingMessage.value.status).toBe('streaming')
      expect(streamingMessage.value.model).toBe(model)
      expect(isStreaming.value).toBe(true)
    })

    it('should append tokens to streamingMessage', () => {
      const { createConversation } = useConversations()
      const { startStreaming, appendToken, streamingMessage } = useMessages()

      createConversation()
      startStreaming('msg-123')

      appendToken('Hello')
      expect(streamingMessage.value.text).toBe('Hello')

      appendToken(' ')
      expect(streamingMessage.value.text).toBe('Hello ')

      appendToken('world')
      expect(streamingMessage.value.text).toBe('Hello world')
    })

    it('should complete streaming and move to messages array', () => {
      const { createConversation } = useConversations()
      const { startStreaming, appendToken, completeStreaming, streamingMessage, isStreaming, currentMessages } = useMessages()

      createConversation()
      startStreaming('msg-123', 'gpt-3.5-turbo')
      appendToken('Complete message')

      completeStreaming()

      expect(streamingMessage.value).toBeNull()
      expect(isStreaming.value).toBe(false)
      expect(currentMessages.value).toHaveLength(1)
      expect(currentMessages.value[0].text).toBe('Complete message')
      expect(currentMessages.value[0].status).toBe('sent')
      expect(currentMessages.value[0].model).toBe('gpt-3.5-turbo')
    })

    it('should track isStreaming flag during streaming lifecycle', () => {
      const { createConversation } = useConversations()
      const { startStreaming, appendToken, completeStreaming, isStreaming } = useMessages()

      createConversation()

      expect(isStreaming.value).toBe(false)

      startStreaming('msg-123')
      expect(isStreaming.value).toBe(true)

      appendToken('token1')
      expect(isStreaming.value).toBe(true)

      appendToken('token2')
      expect(isStreaming.value).toBe(true)

      completeStreaming()
      expect(isStreaming.value).toBe(false)
    })

    it('should clean up stream when aborted', () => {
      const { createConversation } = useConversations()
      const { startStreaming, appendToken, abortStreaming, streamingMessage, isStreaming } = useMessages()

      createConversation()
      startStreaming('msg-123')
      appendToken('Partial')

      abortStreaming()

      expect(streamingMessage.value).toBeNull()
      expect(isStreaming.value).toBe(false)
    })

    it('should handle error during streaming', () => {
      const { createConversation } = useConversations()
      const { startStreaming, appendToken, errorStreaming, streamingMessage, isStreaming, currentMessages } = useMessages()

      createConversation()
      startStreaming('msg-123')
      appendToken('Partial text')

      const errorMessage = 'Rate limit exceeded'
      const errorCode = 'RATE_LIMIT'

      errorStreaming(errorMessage, errorCode)

      expect(streamingMessage.value).toBeNull()
      expect(isStreaming.value).toBe(false)
      expect(currentMessages.value).toHaveLength(1)
      expect(currentMessages.value[0].text).toBe('Partial text')
      expect(currentMessages.value[0].status).toBe('error')
      expect(currentMessages.value[0].errorMessage).toBe(errorMessage)
      expect(currentMessages.value[0].errorType).toBe(errorCode)
    })

    it('should preserve token order during rapid streaming', () => {
      const { createConversation } = useConversations()
      const { startStreaming, appendToken, streamingMessage } = useMessages()

      createConversation()
      startStreaming('msg-123')

      const tokens = ['The', ' ', 'quick', ' ', 'brown', ' ', 'fox']
      tokens.forEach(token => appendToken(token))

      expect(streamingMessage.value.text).toBe('The quick brown fox')
    })

    it('should handle unicode and special characters in tokens', () => {
      const { createConversation } = useConversations()
      const { startStreaming, appendToken, streamingMessage } = useMessages()

      createConversation()
      startStreaming('msg-123')

      appendToken('Hello 🚀')
      appendToken(' 世界')
      appendToken(' @#$%')

      expect(streamingMessage.value.text).toBe('Hello 🚀 世界 @#$%')
    })

    it('should not allow starting new stream while streaming', () => {
      const { createConversation } = useConversations()
      const { startStreaming, isStreaming, streamingMessage } = useMessages()

      createConversation()
      const firstId = 'msg-first'
      const secondId = 'msg-second'

      startStreaming(firstId)
      expect(isStreaming.value).toBe(true)
      expect(streamingMessage.value.id).toBe(firstId)

      // Try to start another stream (should be ignored or throw error)
      startStreaming(secondId)
      expect(streamingMessage.value.id).toBe(firstId) // Should still be first
    })
  })
})
