import { describe, it, expect } from 'vitest'
import { generateId } from '../../src/utils/idGenerator.js'

describe('idGenerator', () => {
  describe('generateId', () => {
    it('should generate ID with correct prefix', () => {
      const convId = generateId('conv')
      const msgId = generateId('msg')

      expect(convId).toMatch(/^conv-/)
      expect(msgId).toMatch(/^msg-/)
    })

    it('should generate UUID v4 format', () => {
      const id = generateId('test')
      // Remove prefix
      const uuid = id.replace('test-', '')

      // UUID v4 format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
      const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
      expect(uuid).toMatch(uuidPattern)
    })

    it('should generate unique IDs', () => {
      const ids = new Set()
      for (let i = 0; i < 100; i++) {
        ids.add(generateId('test'))
      }

      // All 100 IDs should be unique
      expect(ids.size).toBe(100)
    })

    it('should work with different prefixes', () => {
      const prefixes = ['conv', 'msg', 'test', 'user', 'session']

      prefixes.forEach(prefix => {
        const id = generateId(prefix)
        expect(id).toMatch(new RegExp(`^${prefix}-`))
      })
    })
  })
})
