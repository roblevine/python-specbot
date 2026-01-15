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

  it('should default to first conversation when no activeConversationId is set', () => {
    // Manually save conversation data without an activeConversationId
    const testData = {
      version: '1.0.0',
      conversations: [
        {
          id: 'conv-test-123',
          title: 'Test Conversation',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messages: [
            {
              id: 'msg-test-1',
              text: 'Test message',
              sender: 'user',
              timestamp: new Date().toISOString(),
              status: 'sent',
            },
          ],
        },
      ],
      activeConversationId: null, // No active conversation set
    }
    localStorage.setItem('chatInterface:v1:data', JSON.stringify(testData))

    // Load and verify it sets the first conversation as active
    const { loadFromStorage, activeConversationId, conversations } = useConversations()
    loadFromStorage()

    expect(conversations.value).toHaveLength(1)
    expect(activeConversationId.value).toBe('conv-test-123')
  })

  describe('setActiveConversation', () => {
    it('should set the active conversation by ID', () => {
      const { createConversation, setActiveConversation, activeConversationId } = useConversations()

      const conv1 = createConversation()
      const conv2 = createConversation()

      // conv2 should be active after creation
      expect(activeConversationId.value).toBe(conv2.id)

      // Switch to conv1
      setActiveConversation(conv1.id)

      expect(activeConversationId.value).toBe(conv1.id)
    })

    it('should throw error when setting non-existent conversation as active', () => {
      const { setActiveConversation } = useConversations()

      expect(() => setActiveConversation('conv-nonexistent')).toThrow(
        'Conversation not found: conv-nonexistent'
      )
    })

    it('should allow switching between multiple conversations', () => {
      const { createConversation, setActiveConversation, activeConversationId } = useConversations()

      const conv1 = createConversation()
      const conv2 = createConversation()
      const conv3 = createConversation()

      // Switch through all conversations
      setActiveConversation(conv1.id)
      expect(activeConversationId.value).toBe(conv1.id)

      setActiveConversation(conv3.id)
      expect(activeConversationId.value).toBe(conv3.id)

      setActiveConversation(conv2.id)
      expect(activeConversationId.value).toBe(conv2.id)
    })
  })
})
