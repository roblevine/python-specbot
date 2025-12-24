import { describe, it, expect, beforeEach } from 'vitest'
import { useConversations } from '../../src/state/useConversations.js'

describe('useConversations', () => {
  beforeEach(() => {
    localStorage.clear()
    const { __resetState } = useConversations()
    __resetState()
  })

  it('should create a new conversation', () => {
    const { createConversation, conversations } = useConversations()

    const conversation = createConversation()

    expect(conversation).toBeDefined()
    expect(conversation.id).toMatch(/^conv-/)
    expect(conversation.messages).toEqual([])
    expect(conversation.createdAt).toBeTruthy()
    expect(conversation.updatedAt).toBeTruthy()
    expect(conversations.value).toHaveLength(1)
  })

  it('should set created conversation as active', () => {
    const { createConversation, activeConversationId } = useConversations()

    const conversation = createConversation()

    expect(activeConversationId.value).toBe(conversation.id)
  })

  it('should add message to conversation', () => {
    const { createConversation, addMessage } = useConversations()

    const conversation = createConversation()
    const message = {
      id: 'msg-test-123',
      text: 'Hello',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'sent',
    }

    addMessage(conversation.id, message)

    expect(conversation.messages).toHaveLength(1)
    expect(conversation.messages[0]).toEqual(message)
  })

  it('should update conversation title from first message', () => {
    const { createConversation, addMessage } = useConversations()

    const conversation = createConversation()
    const message = {
      id: 'msg-test-123',
      text: 'This is my first message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'sent',
    }

    addMessage(conversation.id, message)

    expect(conversation.title).toBe('This is my first message')
  })

  it('should update conversation updatedAt when message added', async () => {
    const { createConversation, addMessage } = useConversations()

    const conversation = createConversation()
    const originalUpdatedAt = conversation.updatedAt

    // Small delay to ensure timestamp difference
    await new Promise(resolve => setTimeout(resolve, 10))

    const message = {
      id: 'msg-test-123',
      text: 'Test message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'sent',
    }

    addMessage(conversation.id, message)

    expect(conversation.updatedAt).not.toBe(originalUpdatedAt)
  })

  it('should throw error when adding message to non-existent conversation', () => {
    const { addMessage } = useConversations()

    const message = {
      id: 'msg-test-123',
      text: 'Test',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'sent',
    }

    expect(() => addMessage('conv-nonexistent', message)).toThrow()
  })

  it('should save conversations with messages to storage', () => {
    const { createConversation, addMessage, saveToStorage } = useConversations()

    const conversation = createConversation()
    const message = {
      id: 'msg-test-123',
      text: 'Test message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'sent',
    }

    addMessage(conversation.id, message)
    saveToStorage()

    const stored = localStorage.getItem('chatInterface:v1:data')
    expect(stored).toBeTruthy()

    const data = JSON.parse(stored)
    expect(data.conversations).toHaveLength(1)
    expect(data.conversations[0].messages).toHaveLength(1)
  })

  it('should not save conversations without messages', () => {
    const { createConversation, saveToStorage } = useConversations()

    createConversation() // Conversation with no messages
    saveToStorage()

    const stored = localStorage.getItem('chatInterface:v1:data')
    const data = JSON.parse(stored)

    expect(data.conversations).toHaveLength(0)
  })

  it('should load conversations from storage', () => {
    const { createConversation, addMessage, saveToStorage, loadFromStorage } = useConversations()

    // Create and save a conversation
    const conversation = createConversation()
    const message = {
      id: 'msg-test-123',
      text: 'Test message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'sent',
    }
    addMessage(conversation.id, message)
    saveToStorage()

    // Simulate reload by getting new instance
    const { conversations, loadFromStorage: load2 } = useConversations()
    load2()

    expect(conversations.value.length).toBeGreaterThan(0)
  })

  it('should create initial conversation if none exist on load', () => {
    const { loadFromStorage, conversations } = useConversations()

    loadFromStorage()

    expect(conversations.value).toHaveLength(1)
  })
})
