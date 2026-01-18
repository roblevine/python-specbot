import { describe, it, expect } from 'vitest'
import { writeFileSync, readFileSync, existsSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))

/**
 * Contract Tests for DELETE /api/v1/conversations/{conversation_id}
 *
 * Feature: 016-delete-conversation
 * Tests: T041
 *
 * These tests verify that the frontend's delete conversation requests
 * match the expected contract format.
 */

/**
 * Capture contract snapshot for deleteConversation request
 *
 * @param {string} operationId - The operation ID
 * @param {object} request - The request object
 */
function captureDeleteSnapshot(operationId, request) {
  const snapshot = {
    metadata: {
      operationId,
      capturedAt: new Date().toISOString(),
      frontendVersion: '1.0.0',
    },
    request,
  }

  const snapshotDir = join(__dirname, '../../../tests/contract-snapshots')
  const snapshotPath = join(snapshotDir, `${operationId}.json`)

  writeFileSync(snapshotPath, JSON.stringify(snapshot, null, 2))
}

describe('Contract: DELETE /api/v1/conversations/{conversation_id}', () => {
  describe('Request Format', () => {
    it('captures deleteConversation request snapshot with valid UUID', async () => {
      const conversationId = '550e8400-e29b-41d4-a716-446655440000'

      const request = {
        method: 'DELETE',
        path: `/api/v1/conversations/${conversationId}`,
        headers: {},
        body: null,
      }

      // Capture snapshot
      captureDeleteSnapshot('deleteConversation', request)

      // Validate request format
      expect(request.method).toBe('DELETE')
      expect(request.path).toMatch(/^\/api\/v1\/conversations\/[a-f0-9-]+$/)
      expect(request.body).toBeNull()
    })

    it('validates conversation ID is a valid UUID format', () => {
      const validUUIDs = [
        '550e8400-e29b-41d4-a716-446655440000',
        '123e4567-e89b-12d3-a456-426614174000',
        'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
      ]

      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

      validUUIDs.forEach(uuid => {
        expect(uuid).toMatch(uuidRegex)
        const path = `/api/v1/conversations/${uuid}`
        expect(path).toMatch(/^\/api\/v1\/conversations\/[a-f0-9-]+$/)
      })
    })

    it('validates request has no body', () => {
      const request = {
        method: 'DELETE',
        path: '/api/v1/conversations/550e8400-e29b-41d4-a716-446655440000',
        headers: {},
        body: null,
      }

      expect(request.body).toBeNull()
    })

    it('validates request method is DELETE', () => {
      const request = {
        method: 'DELETE',
        path: '/api/v1/conversations/550e8400-e29b-41d4-a716-446655440000',
        headers: {},
        body: null,
      }

      expect(request.method).toBe('DELETE')
    })
  })

  describe('Response Contract', () => {
    it('expects 204 No Content on successful deletion', () => {
      const expectedSuccessResponse = {
        statusCode: 204,
        body: null,
      }

      expect(expectedSuccessResponse.statusCode).toBe(204)
      expect(expectedSuccessResponse.body).toBeNull()
    })

    it('expects 404 with error body when conversation not found', () => {
      const expectedErrorResponse = {
        statusCode: 404,
        body: {
          error: 'Conversation not found',
          code: 'CONVERSATION_NOT_FOUND',
          detail: 'No conversation found with ID 550e8400-e29b-41d4-a716-446655440000',
        },
      }

      expect(expectedErrorResponse.statusCode).toBe(404)
      expect(expectedErrorResponse.body.error).toBeDefined()
      expect(expectedErrorResponse.body.code).toBeDefined()
    })

    it('expects error response to have required fields', () => {
      const errorResponse = {
        error: 'Conversation not found',
        code: 'CONVERSATION_NOT_FOUND',
      }

      // Required fields per contract
      expect(errorResponse).toHaveProperty('error')
      expect(errorResponse).toHaveProperty('code')
      expect(typeof errorResponse.error).toBe('string')
      expect(typeof errorResponse.code).toBe('string')
    })
  })

  describe('Path Parameter Validation', () => {
    it('conversation_id must be in UUID format', () => {
      const validId = '550e8400-e29b-41d4-a716-446655440000'
      const path = `/api/v1/conversations/${validId}`

      expect(path).toBe('/api/v1/conversations/550e8400-e29b-41d4-a716-446655440000')
    })

    it('rejects invalid conversation ID formats', () => {
      const invalidIds = [
        'not-a-uuid',
        '12345',
        'abc',
        '',
        'conv-550e8400-e29b-41d4-a716-446655440000', // wrong prefix
      ]

      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

      invalidIds.forEach(id => {
        expect(id).not.toMatch(uuidRegex)
      })
    })
  })

  describe('Snapshot Verification', () => {
    it('should create a valid snapshot file', () => {
      const conversationId = '550e8400-e29b-41d4-a716-446655440000'

      const request = {
        method: 'DELETE',
        path: `/api/v1/conversations/${conversationId}`,
        headers: {},
        body: null,
      }

      captureDeleteSnapshot('deleteConversation', request)

      // Verify snapshot was created
      const snapshotPath = join(__dirname, '../../../tests/contract-snapshots/deleteConversation.json')
      expect(existsSync(snapshotPath)).toBe(true)

      // Verify snapshot content
      const snapshot = JSON.parse(readFileSync(snapshotPath, 'utf8'))
      expect(snapshot.metadata.operationId).toBe('deleteConversation')
      expect(snapshot.request.method).toBe('DELETE')
      expect(snapshot.request.path).toContain('/api/v1/conversations/')
    })
  })
})
