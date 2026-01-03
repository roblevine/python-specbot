import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useMessages } from '../../src/state/useMessages.js'
import { useConversations } from '../../src/state/useConversations.js'
import { useAppState } from '../../src/state/useAppState.js'
import { StreamingClient } from '../../src/services/streamingClient.js'

// Mock StreamingClient
vi.mock('../../src/services/streamingClient.js', () => {
  return {
    StreamingClient: vi.fn().mockImplementation(() => {
      return {
        streamChat: vi.fn(async (text, conversationId, history, model, callbacks) => {
          // Simulate streaming behavior
          callbacks.onStart('msg-test-id')

          // Simulate chunks
          const words = text.split(' ')
          for (const word of words) {
            callbacks.onChunk(word + ' ')
          }

          // Complete stream
          callbacks.onDone('msg-test-id', model)
        }),
        stopStream: vi.fn()
      }
    })
  }
})

describe('useMessages', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllTimers()
    const { __resetState } = useConversations()
    __resetState()
    vi.clearAllMocks()
  })

  it('should return empty messages for no active conversation', () => {
    const { currentMessages } = useMessages()

    expect(currentMessages.value).toEqual([])
  })

  it('should send user message and stream assistant response', async () => {
    const { createConversation } = useConversations()
    const { sendStreamingMessage, currentMessages } = useMessages()

    createConversation()
    await sendStreamingMessage('Hello world')

    expect(currentMessages.value).toHaveLength(2)
    expect(currentMessages.value[0].sender).toBe('user')
    expect(currentMessages.value[0].text).toBe('Hello world')
    expect(currentMessages.value[1].sender).toBe('assistant')
    expect(currentMessages.value[1].text).toBe('Hello world ')
  })

  it('should mark user message as sent and assistant message as completed', async () => {
    const { createConversation } = useConversations()
    const { sendStreamingMessage, currentMessages } = useMessages()

    createConversation()
    await sendStreamingMessage('Test message')

    expect(currentMessages.value[0].status).toBe('sent')
    expect(currentMessages.value[1].status).toBe('completed')
  })

  it('should trim message text', async () => {
    const { createConversation } = useConversations()
    const { sendStreamingMessage, currentMessages } = useMessages()

    createConversation()
    await sendStreamingMessage('  Message with spaces  ')

    expect(currentMessages.value[0].text).toBe('Message with spaces')
    // Assistant echoes back (with trailing space from mock)
    expect(currentMessages.value[1].text).toBe('Message with spaces ')
  })

  it('should not send empty message', async () => {
    const { createConversation } = useConversations()
    const { sendStreamingMessage, currentMessages } = useMessages()

    createConversation()
    await sendStreamingMessage('')

    expect(currentMessages.value).toHaveLength(0)
  })

  it('should not send whitespace-only message', async () => {
    const { createConversation } = useConversations()
    const { sendStreamingMessage, currentMessages } = useMessages()

    createConversation()
    await sendStreamingMessage('   \n\t  ')

    expect(currentMessages.value).toHaveLength(0)
  })

  it('should set error status for invalid message', async () => {
    const { createConversation } = useConversations()
    const { sendStreamingMessage } = useMessages()
    const { statusType } = useAppState()

    createConversation()
    await sendStreamingMessage('')

    expect(statusType.value).toBe('error')
  })

  it('should save to storage after sending message', async () => {
    const { createConversation } = useConversations()
    const { sendStreamingMessage } = useMessages()

    createConversation()
    await sendStreamingMessage('Test message')

    const stored = localStorage.getItem('chatInterface:v1:data')
    expect(stored).toBeTruthy()

    const data = JSON.parse(stored)
    expect(data.conversations[0].messages).toHaveLength(2)
  })
})
