import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useMessages } from '../../src/state/useMessages.js'
import { useConversations } from '../../src/state/useConversations.js'
import { ApiError } from '../../src/services/apiClient.js'

// Mock the API client
vi.mock('../../src/services/apiClient.js', () => ({
  sendMessage: vi.fn(),
  streamMessage: vi.fn(),
  // Conversation API mocks for server-side storage
  getConversations: vi.fn().mockResolvedValue({ conversations: [] }),
  getConversation: vi.fn().mockResolvedValue({ conversation: null }),
  createConversation: vi.fn().mockImplementation((data) =>
    Promise.resolve({
      conversation: {
        ...data,
        id: data?.id || 'conv-mock-123',
        title: data?.title || 'New Conversation',
        createdAt: data?.createdAt || new Date().toISOString(),
        updatedAt: data?.updatedAt || new Date().toISOString(),
        messages: data?.messages || []
      }
    })
  ),
  updateConversation: vi.fn().mockResolvedValue({ conversation: {} }),
  deleteConversation: vi.fn().mockResolvedValue(undefined),
  ApiError: class ApiError extends Error {
    constructor(message, statusCode = null, details = null) {
      super(message)
      this.name = 'ApiError'
      this.statusCode = statusCode
      this.details = details
    }
  }
}))

describe('Error Display Integration', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
    const { __resetState } = useConversations()
    __resetState()
  })

  // T030: 422 validation error displays in chat
  it('should display 422 validation error in chat', async () => {
    const apiClient = await import('../../src/services/apiClient.js')
    const { createConversation } = useConversations()
    const { sendUserMessage, currentMessages } = useMessages()

    // Mock streaming API to trigger error via onError callback
    vi.mocked(apiClient.streamMessage).mockImplementation((message, onToken, onComplete, onError) => {
      setTimeout(() => onError({ error: 'Message validation failed', code: 'HTTP_422', statusCode: 422 }), 10)
      return vi.fn()
    })

    await createConversation()
    await sendUserMessage('Test message')
    await new Promise(resolve => setTimeout(resolve, 50))

    // Check the error response message (index 1, after user message at index 0)
    const errorMessage = currentMessages.value[1]

    expect(errorMessage.status).toBe('error')
    expect(errorMessage.errorMessage).toBe('Message validation failed')
    expect(errorMessage.errorType).toBe('HTTP_422')
    expect(errorMessage.errorCode).toBeUndefined()
  })

  // T031: 500 server error displays in chat
  it('should display 500 server error in chat', async () => {
    const apiClient = await import('../../src/services/apiClient.js')
    const { createConversation } = useConversations()
    const { sendUserMessage, currentMessages } = useMessages()

    // Mock streaming API to trigger error via onError callback
    vi.mocked(apiClient.streamMessage).mockImplementation((message, onToken, onComplete, onError) => {
      setTimeout(() => onError({ error: 'Internal server error', code: 'HTTP_500', statusCode: 500 }), 10)
      return vi.fn()
    })

    await createConversation()
    await sendUserMessage('Test message')
    await new Promise(resolve => setTimeout(resolve, 50))

    // Check the error response message (index 1, after user message at index 0)
    const errorMessage = currentMessages.value[1]

    expect(errorMessage.status).toBe('error')
    expect(errorMessage.errorMessage).toBe('Internal server error')
    expect(errorMessage.errorType).toBe('HTTP_500')
    expect(errorMessage.errorCode).toBeUndefined()
  })

  // T032: 400 bad request displays in chat
  it('should display 400 bad request error in chat', async () => {
    const apiClient = await import('../../src/services/apiClient.js')
    const { createConversation } = useConversations()
    const { sendUserMessage, currentMessages } = useMessages()

    // Mock streaming API to trigger error via onError callback
    vi.mocked(apiClient.streamMessage).mockImplementation((message, onToken, onComplete, onError) => {
      setTimeout(() => onError({ error: 'Invalid message format', code: 'HTTP_400', statusCode: 400 }), 10)
      return vi.fn()
    })

    await createConversation()
    await sendUserMessage('Test message')
    await new Promise(resolve => setTimeout(resolve, 50))

    // Check the error response message (index 1, after user message at index 0)
    const errorMessage = currentMessages.value[1]

    expect(errorMessage.status).toBe('error')
    expect(errorMessage.errorMessage).toBe('Invalid message format')
    expect(errorMessage.errorType).toBe('HTTP_400')
    expect(errorMessage.errorCode).toBeUndefined()
  })

  // Additional test: Network errors should be categorized differently
  it('should categorize network errors without status codes', async () => {
    const apiClient = await import('../../src/services/apiClient.js')
    const { createConversation } = useConversations()
    const { sendUserMessage, currentMessages } = useMessages()

    // Mock streaming API to trigger network error via onError callback (no status code)
    vi.mocked(apiClient.streamMessage).mockImplementation((message, onToken, onComplete, onError) => {
      setTimeout(() => onError({ error: 'Cannot connect to server', code: 'NETWORK_ERROR' }), 10)
      return vi.fn()
    })

    await createConversation()
    await sendUserMessage('Test message')
    await new Promise(resolve => setTimeout(resolve, 50))

    // Check the error response message (index 1, after user message at index 0)
    const errorMessage = currentMessages.value[1]

    expect(errorMessage.status).toBe('error')
    expect(errorMessage.errorMessage).toBe('Cannot connect to server')
    expect(errorMessage.errorType).toBe('NETWORK_ERROR')
    expect(errorMessage.errorCode).toBeUndefined()
  })
})
