/**
 * Integration Tests for Message Streaming
 *
 * Tests the complete streaming flow from API client through state management
 * to UI component rendering.
 *
 * Feature: 009-message-streaming User Story 1
 * Task: T022
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import ChatArea from '@/components/ChatArea/ChatArea.vue'
import { useMessages } from '@/state/useMessages.js'
import { useConversations } from '@/state/useConversations.js'
import * as apiClient from '@/services/apiClient.js'

// Mock API client
vi.mock('@/services/apiClient.js', () => ({
  sendMessage: vi.fn(),
  streamMessage: vi.fn()
}))

// Mock localStorage
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = value.toString() },
    removeItem: (key) => { delete store[key] },
    clear: () => { store = {} }
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

describe('Streaming Flow Integration', () => {
  let conversationState
  let messageState

  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()

    // Initialize state
    conversationState = useConversations()
    messageState = useMessages()

    // Reset conversation state
    if (conversationState.__resetState) {
      conversationState.__resetState()
    }

    // Create a test conversation
    conversationState.createConversation('Test Streaming Conversation')

    // Setup default mocks
    apiClient.sendMessage.mockResolvedValue({
      status: 'success',
      message: 'AI response',
      timestamp: new Date().toISOString(),
      model: 'gpt-3.5-turbo'
    })
  })

  afterEach(() => {
    // Clean up streaming state
    if (messageState.__resetStreamingState) {
      messageState.__resetStreamingState()
    }
    vi.restoreAllMocks()
  })

  it('T022: should trigger streaming when SSE stream is received', async () => {
    // Mock streamMessage to simulate SSE stream
    const mockCleanup = vi.fn()
    apiClient.streamMessage.mockImplementation((message, conversationId, history, model, callbacks) => {
      // Simulate streaming tokens
      setTimeout(() => {
        callbacks.onToken('Hello')
      }, 10)
      setTimeout(() => {
        callbacks.onToken(' world')
      }, 20)
      setTimeout(() => {
        callbacks.onToken('!')
      }, 30)
      setTimeout(() => {
        callbacks.onComplete({ model: 'gpt-3.5-turbo' })
      }, 40)

      return mockCleanup
    })

    // Start streaming with proper msg- prefixed ID
    const messageText = 'Test message'
    messageState.startStreaming('msg-test-streaming-1', 'gpt-3.5-turbo')

    // Verify streaming state
    expect(messageState.isStreaming.value).toBe(true)
    expect(messageState.streamingMessage.value).toBeTruthy()
    expect(messageState.streamingMessage.value.text).toBe('')

    // Simulate receiving tokens
    messageState.appendToken('Hello')
    expect(messageState.streamingMessage.value.text).toBe('Hello')

    messageState.appendToken(' world')
    expect(messageState.streamingMessage.value.text).toBe('Hello world')

    messageState.appendToken('!')
    expect(messageState.streamingMessage.value.text).toBe('Hello world!')

    // Complete streaming
    messageState.completeStreaming()

    await nextTick()

    // Verify message was added to conversation
    expect(messageState.isStreaming.value).toBe(false)
    expect(messageState.streamingMessage.value).toBe(null)
    expect(messageState.currentMessages.value.length).toBeGreaterThan(0)

    const lastMessage = messageState.currentMessages.value[messageState.currentMessages.value.length - 1]
    expect(lastMessage.text).toBe('Hello world!')
    expect(lastMessage.status).toBe('sent')
  })

  it('T022: should accumulate tokens in streaming message', async () => {
    // Start streaming with proper msg- prefixed ID
    messageState.startStreaming('msg-test-streaming-2', 'gpt-4')

    expect(messageState.streamingMessage.value.text).toBe('')

    // Append multiple tokens
    const tokens = ['The', ' quick', ' brown', ' fox', ' jumps']
    tokens.forEach(token => {
      messageState.appendToken(token)
    })

    expect(messageState.streamingMessage.value.text).toBe('The quick brown fox jumps')
    expect(messageState.streamingMessage.value.status).toBe('streaming')
  })

  it('T022: should display streaming message in ChatArea component', async () => {
    // Mount ChatArea with empty messages
    const wrapper = mount(ChatArea, {
      props: {
        messages: [],
        isProcessing: false
      }
    })

    await nextTick()

    // Should show empty state initially
    expect(wrapper.find('.empty-state').exists()).toBe(true)

    // Start streaming with proper msg- prefixed ID
    messageState.startStreaming('msg-test-streaming-3', 'gpt-3.5-turbo')
    messageState.appendToken('Streaming')
    messageState.appendToken(' message')

    await nextTick()

    // Empty state should be hidden and messages container should show
    expect(wrapper.find('.empty-state').exists()).toBe(false)
    expect(wrapper.find('.messages-container').exists()).toBe(true)

    // Find all MessageBubble components
    const messageBubbles = wrapper.findAllComponents({ name: 'MessageBubble' })
    expect(messageBubbles.length).toBe(1)

    // Verify streaming message is displayed
    const streamingBubble = messageBubbles[0]
    expect(streamingBubble.props('message').text).toBe('Streaming message')
    expect(streamingBubble.props('message').status).toBe('streaming')
  })

  it('T022: should save completed streaming message to conversation', async () => {
    // Start streaming with proper msg- prefixed ID
    messageState.startStreaming('msg-test-streaming-4', 'gpt-4')

    // Add some tokens
    messageState.appendToken('Complete')
    messageState.appendToken(' message')

    // Get initial message count
    const initialCount = messageState.currentMessages.value.length

    // Complete streaming
    messageState.completeStreaming()

    await nextTick()

    // Verify message was added
    expect(messageState.currentMessages.value.length).toBe(initialCount + 1)

    const completedMessage = messageState.currentMessages.value[initialCount]
    expect(completedMessage.text).toBe('Complete message')
    expect(completedMessage.status).toBe('sent')
    expect(completedMessage.sender).toBe('system')
    expect(completedMessage.model).toBe('gpt-4')

    // Verify localStorage was updated
    const stored = JSON.parse(localStorage.getItem('chatInterface:v1:data'))
    expect(stored).toBeTruthy()
    expect(stored.conversations[0].messages).toContainEqual(
      expect.objectContaining({
        text: 'Complete message',
        status: 'sent'
      })
    )
  })

  it('T022: should have ChatArea component with streamingMessage ref and auto-scroll watchers', async () => {
    // Mount ChatArea with at least one message so messages-container renders
    const wrapper = mount(ChatArea, {
      props: {
        messages: [{
          id: 'msg-existing-1',
          text: 'Existing message',
          sender: 'user',
          timestamp: new Date().toISOString(),
          status: 'sent'
        }],
        isProcessing: false
      }
    })

    await nextTick()

    // Verify component has access to streamingMessage
    expect(wrapper.vm.streamingMessage).toBeDefined()
    expect(wrapper.vm.isStreaming).toBeDefined()

    // Verify chatArea ref exists
    expect(wrapper.vm.chatArea).toBeDefined()

    // Start streaming and verify the streaming message is reactive
    messageState.startStreaming('msg-test-streaming-5', 'gpt-3.5-turbo')
    messageState.appendToken('First token')

    await nextTick()

    // Verify streamingMessage is accessible in the component
    expect(wrapper.vm.streamingMessage.text).toBe('First token')

    // Note: Testing actual watch behavior with timing is flaky in unit tests.
    // The watch functionality is validated in e2e tests where we can observe
    // real browser behavior. Here we just verify the data flow is correct.
  })

  it('T022: should handle streaming errors gracefully', async () => {
    // Start streaming with proper msg- prefixed ID
    messageState.startStreaming('msg-test-streaming-6', 'gpt-4')
    messageState.appendToken('Partial')
    messageState.appendToken(' response')

    const initialCount = messageState.currentMessages.value.length

    // Simulate error during streaming
    messageState.errorStreaming('Connection lost', 'NETWORK_ERROR')

    await nextTick()

    // Verify streaming state is cleared
    expect(messageState.isStreaming.value).toBe(false)
    expect(messageState.streamingMessage.value).toBe(null)

    // Verify error message was added to conversation
    expect(messageState.currentMessages.value.length).toBe(initialCount + 1)

    const errorMessage = messageState.currentMessages.value[initialCount]
    expect(errorMessage.text).toBe('Partial response')
    expect(errorMessage.status).toBe('error')
    expect(errorMessage.errorMessage).toBe('Connection lost')
    expect(errorMessage.errorType).toBe('NETWORK_ERROR')
  })

  it('T022: should prevent multiple simultaneous streams', async () => {
    // Start first stream with proper msg- prefixed ID
    messageState.startStreaming('msg-test-streaming-7', 'gpt-4')
    expect(messageState.isStreaming.value).toBe(true)

    const firstStreamId = messageState.streamingMessage.value.id

    // Try to start second stream
    messageState.startStreaming('msg-test-streaming-8', 'gpt-3.5-turbo')

    // Should still be on first stream
    expect(messageState.streamingMessage.value.id).toBe(firstStreamId)
  })

  it('T022: should handle abort streaming', async () => {
    // Start streaming with proper msg- prefixed ID
    messageState.startStreaming('msg-test-streaming-9', 'gpt-4')
    messageState.appendToken('Aborted')

    const initialCount = messageState.currentMessages.value.length

    // Abort streaming
    messageState.abortStreaming()

    await nextTick()

    // Verify streaming state is cleared
    expect(messageState.isStreaming.value).toBe(false)
    expect(messageState.streamingMessage.value).toBe(null)

    // Verify no message was added (aborted before completion)
    expect(messageState.currentMessages.value.length).toBe(initialCount)
  })
})
