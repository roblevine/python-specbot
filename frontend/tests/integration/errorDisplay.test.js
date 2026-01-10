import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useMessages } from '../../src/state/useMessages.js'
import { useConversations } from '../../src/state/useConversations.js'
import { ApiError } from '../../src/services/apiClient.js'

// Mock the API client
vi.mock('../../src/services/apiClient.js', () => ({
  sendMessage: vi.fn(),
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

    // Mock API to throw 422 validation error
    vi.mocked(apiClient.sendMessage).mockRejectedValueOnce(
      new apiClient.ApiError(
        'Message validation failed',
        422,
        { field: 'message', reason: 'Message too short' }
      )
    )

    createConversation()
    await sendUserMessage('Test message')

    const errorMessage = currentMessages.value[0]

    expect(errorMessage.status).toBe('error')
    expect(errorMessage.errorMessage).toBe('Message validation failed')
    expect(errorMessage.errorType).toBe('Validation Error')
    expect(errorMessage.errorCode).toBe(422)
  })

  // T031: 500 server error displays in chat
  it('should display 500 server error in chat', async () => {
    const apiClient = await import('../../src/services/apiClient.js')
    const { createConversation } = useConversations()
    const { sendUserMessage, currentMessages } = useMessages()

    // Mock API to throw 500 server error
    vi.mocked(apiClient.sendMessage).mockRejectedValueOnce(
      new apiClient.ApiError(
        'Internal server error',
        500,
        { stack: 'Error stack trace...' }
      )
    )

    createConversation()
    await sendUserMessage('Test message')

    const errorMessage = currentMessages.value[0]

    expect(errorMessage.status).toBe('error')
    expect(errorMessage.errorMessage).toBe('Internal server error')
    expect(errorMessage.errorType).toBe('Server Error')
    expect(errorMessage.errorCode).toBe(500)
  })

  // T032: 400 bad request displays in chat
  it('should display 400 bad request error in chat', async () => {
    const apiClient = await import('../../src/services/apiClient.js')
    const { createConversation } = useConversations()
    const { sendUserMessage, currentMessages } = useMessages()

    // Mock API to throw 400 bad request error
    vi.mocked(apiClient.sendMessage).mockRejectedValueOnce(
      new apiClient.ApiError(
        'Invalid message format',
        400,
        { error: 'Missing required field' }
      )
    )

    createConversation()
    await sendUserMessage('Test message')

    const errorMessage = currentMessages.value[0]

    expect(errorMessage.status).toBe('error')
    expect(errorMessage.errorMessage).toBe('Invalid message format')
    expect(errorMessage.errorType).toBe('Validation Error')
    expect(errorMessage.errorCode).toBe(400)
  })

  // Additional test: Network errors should be categorized differently
  it('should categorize network errors without status codes', async () => {
    const apiClient = await import('../../src/services/apiClient.js')
    const { createConversation } = useConversations()
    const { sendUserMessage, currentMessages } = useMessages()

    // Mock API to throw network error (no status code)
    vi.mocked(apiClient.sendMessage).mockRejectedValueOnce(
      new apiClient.ApiError('Cannot connect to server', null, { network: true })
    )

    createConversation()
    await sendUserMessage('Test message')

    const errorMessage = currentMessages.value[0]

    expect(errorMessage.status).toBe('error')
    expect(errorMessage.errorMessage).toBe('Cannot connect to server')
    expect(errorMessage.errorType).toBe('Network Error')
    expect(errorMessage.errorCode).toBeUndefined()
  })
})
