import { describe, it, expect } from 'vitest'
import {
  validateMessageText,
  validateConversation,
  validateMessage,
} from '../../src/utils/validators.js'

describe('validators', () => {
  describe('validateMessageText', () => {
    it('should accept valid text', () => {
      const result = validateMessageText('Hello world')
      expect(result.isValid).toBe(true)
      expect(result.error).toBeNull()
    })

    it('should reject empty string', () => {
      const result = validateMessageText('')
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('empty')
    })

    it('should reject whitespace-only string', () => {
      const result = validateMessageText('   \n\t  ')
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('empty')
    })

    it('should reject non-string values', () => {
      const results = [
        validateMessageText(123),
        validateMessageText(null),
        validateMessageText(undefined),
        validateMessageText({}),
      ]

      results.forEach(result => {
        expect(result.isValid).toBe(false)
        expect(result.error).toContain('string')
      })
    })

    it('should reject text over 10,000 characters', () => {
      const longText = 'a'.repeat(10001)
      const result = validateMessageText(longText)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('10,000')
    })

    it('should accept text at 10,000 character limit', () => {
      const maxText = 'a'.repeat(10000)
      const result = validateMessageText(maxText)
      expect(result.isValid).toBe(true)
    })
  })

  describe('validateConversation', () => {
    const validConversation = {
      id: 'conv-550e8400-e29b-41d4-a716-446655440000',
      createdAt: '2025-12-23T10:00:00.000Z',
      updatedAt: '2025-12-23T10:05:00.000Z',
      messages: [],
      title: 'Test Conversation',
    }

    it('should accept valid conversation', () => {
      const result = validateConversation(validConversation)
      expect(result.isValid).toBe(true)
      expect(result.error).toBeNull()
    })

    it('should reject non-object values', () => {
      const results = [
        validateConversation(null),
        validateConversation(undefined),
        validateConversation('string'),
        validateConversation(123),
      ]

      results.forEach(result => {
        expect(result.isValid).toBe(false)
      })
    })

    it('should reject conversation without ID', () => {
      const conv = { ...validConversation }
      delete conv.id
      const result = validateConversation(conv)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('ID')
    })

    it('should reject conversation with invalid ID prefix', () => {
      const conv = { ...validConversation, id: 'msg-123' }
      const result = validateConversation(conv)
      expect(result.isValid).toBe(false)
    })

    it('should reject conversation without createdAt', () => {
      const conv = { ...validConversation }
      delete conv.createdAt
      const result = validateConversation(conv)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('createdAt')
    })

    it('should reject conversation without updatedAt', () => {
      const conv = { ...validConversation }
      delete conv.updatedAt
      const result = validateConversation(conv)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('updatedAt')
    })

    it('should reject conversation without messages array', () => {
      const conv = { ...validConversation }
      delete conv.messages
      const result = validateConversation(conv)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('messages')
    })

    it('should reject conversation with invalid ISO dates', () => {
      const conv1 = { ...validConversation, createdAt: '2025-12-23' }
      const conv2 = { ...validConversation, updatedAt: 'invalid-date' }

      expect(validateConversation(conv1).isValid).toBe(false)
      expect(validateConversation(conv2).isValid).toBe(false)
    })
  })

  describe('validateMessage', () => {
    const validMessage = {
      id: 'msg-660e8400-e29b-41d4-a716-446655440001',
      text: 'Hello world',
      sender: 'user',
      timestamp: '2025-12-23T10:00:00.000Z',
      status: 'sent',
    }

    it('should accept valid message', () => {
      const result = validateMessage(validMessage)
      expect(result.isValid).toBe(true)
      expect(result.error).toBeNull()
    })

    it('should reject message without ID', () => {
      const msg = { ...validMessage }
      delete msg.id
      const result = validateMessage(msg)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('ID')
    })

    it('should reject message with invalid ID prefix', () => {
      const msg = { ...validMessage, id: 'conv-123' }
      const result = validateMessage(msg)
      expect(result.isValid).toBe(false)
    })

    it('should reject message with invalid text', () => {
      const msg = { ...validMessage, text: '' }
      const result = validateMessage(msg)
      expect(result.isValid).toBe(false)
    })

    it('should reject message with invalid sender', () => {
      const msg = { ...validMessage, sender: 'bot' }
      const result = validateMessage(msg)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('sender')
    })

    it('should accept both user and system senders', () => {
      const userMsg = { ...validMessage, sender: 'user' }
      const systemMsg = { ...validMessage, sender: 'system' }

      expect(validateMessage(userMsg).isValid).toBe(true)
      expect(validateMessage(systemMsg).isValid).toBe(true)
    })

    it('should reject message with invalid status', () => {
      const msg = { ...validMessage, status: 'delivered' }
      const result = validateMessage(msg)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('status')
    })

    it('should accept all valid statuses', () => {
      const statuses = ['pending', 'sent', 'error']

      statuses.forEach(status => {
        const msg = { ...validMessage, status }
        expect(validateMessage(msg).isValid).toBe(true)
      })
    })

    it('should reject message without timestamp', () => {
      const msg = { ...validMessage }
      delete msg.timestamp
      const result = validateMessage(msg)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('timestamp')
    })

    it('should reject message with invalid ISO timestamp', () => {
      const msg = { ...validMessage, timestamp: '2025-12-23' }
      const result = validateMessage(msg)
      expect(result.isValid).toBe(false)
    })
  })
})
