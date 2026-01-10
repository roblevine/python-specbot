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
})
