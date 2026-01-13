import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  saveConversations,
  loadConversations,
  clearAllData,
} from '../../src/storage/LocalStorageAdapter.js'

describe('LocalStorageAdapter', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
    vi.clearAllMocks()
  })

  describe('saveConversations', () => {
    it('should save conversations to localStorage', () => {
      const conversations = [
        {
          id: 'conv-1',
          createdAt: '2025-12-23T10:00:00.000Z',
          updatedAt: '2025-12-23T10:05:00.000Z',
          messages: [],
        },
      ]
      const activeId = 'conv-1'

      saveConversations(conversations, activeId)

      const stored = localStorage.getItem('chatInterface:v1:data')
      expect(stored).toBeTruthy()

      const data = JSON.parse(stored)
      expect(data.version).toBe('1.1.0')
      expect(data.conversations).toEqual(conversations)
      expect(data.activeConversationId).toBe(activeId)
      expect(data.preferences).toEqual({ sidebarCollapsed: false })
    })

    it('should handle null activeConversationId', () => {
      const conversations = []
      saveConversations(conversations, null)

      const stored = localStorage.getItem('chatInterface:v1:data')
      const data = JSON.parse(stored)
      expect(data.activeConversationId).toBeNull()
    })
  })

  describe('loadConversations', () => {
    it('should load conversations from localStorage', () => {
      const testData = {
        version: '1.0.0',
        conversations: [
          {
            id: 'conv-1',
            createdAt: '2025-12-23T10:00:00.000Z',
            updatedAt: '2025-12-23T10:05:00.000Z',
            messages: [],
          },
        ],
        activeConversationId: 'conv-1',
      }

      localStorage.setItem('chatInterface:v1:data', JSON.stringify(testData))

      const result = loadConversations()
      expect(result.conversations).toEqual(testData.conversations)
      expect(result.activeConversationId).toBe('conv-1')
    })

    it('should return empty schema if no data exists', () => {
      const result = loadConversations()
      expect(result.conversations).toEqual([])
      expect(result.activeConversationId).toBeNull()
      expect(result.version).toBe('1.1.0')
      expect(result.preferences).toEqual({ sidebarCollapsed: false })
    })

    it('should handle corrupted data gracefully', () => {
      localStorage.setItem('chatInterface:v1:data', 'invalid-json')

      const result = loadConversations()
      expect(result.conversations).toEqual([])
      expect(result.activeConversationId).toBeNull()
    })
  })

  describe('clearAllData', () => {
    it('should clear all data from localStorage', () => {
      localStorage.setItem('chatInterface:v1:data', '{"test":"data"}')
      localStorage.setItem('other-key', 'other-value')

      clearAllData()

      expect(localStorage.getItem('chatInterface:v1:data')).toBeNull()
      // Other keys should remain
      expect(localStorage.getItem('other-key')).toBe('other-value')
    })
  })
})
