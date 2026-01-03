import { describe, it, expect, beforeEach } from 'vitest'
import {
  SCHEMA_VERSION,
  STORAGE_KEY,
  createEmptySchema,
  validateSchema,
  migrateSchema,
} from '../../src/storage/StorageSchema.js'

describe('StorageSchema', () => {
  describe('createEmptySchema', () => {
    it('should create schema with correct version', () => {
      const schema = createEmptySchema()
      expect(schema.version).toBe(SCHEMA_VERSION)
      expect(schema.version).toBe('2.0.0')
    })

    it('should create schema with empty conversations array', () => {
      const schema = createEmptySchema()
      expect(schema.conversations).toEqual([])
      expect(Array.isArray(schema.conversations)).toBe(true)
    })

    it('should create schema with null activeConversationId', () => {
      const schema = createEmptySchema()
      expect(schema.activeConversationId).toBeNull()
    })
  })

  describe('validateSchema', () => {
    const validSchema = {
      version: '2.0.0',
      conversations: [
        {
          id: 'conv-550e8400-e29b-41d4-a716-446655440000',
          createdAt: '2025-12-23T10:00:00.000Z',
          updatedAt: '2025-12-23T10:05:00.000Z',
          messages: [],
        },
      ],
      activeConversationId: 'conv-550e8400-e29b-41d4-a716-446655440000',
    }

    it('should accept valid schema', () => {
      const result = validateSchema(validSchema)
      expect(result.isValid).toBe(true)
      expect(result.error).toBeNull()
      expect(result.data).toEqual(validSchema)
    })

    it('should reject non-object values', () => {
      const results = [
        validateSchema(null),
        validateSchema(undefined),
        validateSchema('string'),
        validateSchema(123),
      ]

      results.forEach(result => {
        expect(result.isValid).toBe(false)
        expect(result.data).toEqual(createEmptySchema())
      })
    })

    it('should reject schema with wrong version', () => {
      const schema = { ...validSchema, version: '1.0.0' }
      const result = validateSchema(schema)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('version mismatch')
    })

    it('should reject schema without conversations array', () => {
      const schema = { ...validSchema, conversations: 'not-array' }
      const result = validateSchema(schema)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('array')
    })

    it('should filter out invalid conversations', () => {
      const schema = {
        version: '2.0.0',
        conversations: [
          {
            id: 'conv-valid',
            createdAt: '2025-12-23T10:00:00.000Z',
            updatedAt: '2025-12-23T10:05:00.000Z',
            messages: [],
          },
          {
            id: 'invalid-id',
            createdAt: '2025-12-23T10:00:00.000Z',
            updatedAt: '2025-12-23T10:05:00.000Z',
            messages: [],
          },
        ],
        activeConversationId: null,
      }

      const result = validateSchema(schema)
      expect(result.isValid).toBe(true)
      expect(result.data.conversations).toHaveLength(1)
      expect(result.data.conversations[0].id).toBe('conv-valid')
    })

    it('should reset activeConversationId if not found in conversations', () => {
      const schema = {
        ...validSchema,
        activeConversationId: 'conv-nonexistent',
      }

      const result = validateSchema(schema)
      expect(result.isValid).toBe(true)
      expect(result.data.activeConversationId).toBeNull()
    })

    it('should accept null activeConversationId', () => {
      const schema = { ...validSchema, activeConversationId: null }
      const result = validateSchema(schema)
      expect(result.isValid).toBe(true)
      expect(result.data.activeConversationId).toBeNull()
    })
  })

  describe('migrateSchema', () => {
    it('should return data unchanged if version matches', () => {
      const data = {
        version: '2.0.0',
        conversations: [],
        activeConversationId: null,
      }

      const migrated = migrateSchema(data)
      expect(migrated).toEqual(data)
    })

    it('should return empty schema for data without version', () => {
      const data = { conversations: [] }
      const migrated = migrateSchema(data)
      expect(migrated).toEqual(createEmptySchema())
    })

    it('should return empty schema for unknown version', () => {
      const data = {
        version: '99.0.0',
        conversations: [],
      }

      const migrated = migrateSchema(data)
      expect(migrated).toEqual(createEmptySchema())
    })
  })

  describe('STORAGE_KEY constant', () => {
    it('should have correct storage key format', () => {
      expect(STORAGE_KEY).toBe('chatInterface:v1:data')
    })
  })
})
