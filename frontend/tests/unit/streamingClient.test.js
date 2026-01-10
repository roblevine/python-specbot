/**
 * Unit Tests for StreamingClient
 *
 * Tests the StreamingClient class for LLM chat streaming.
 * Basic tests for constructor and stopStream functionality.
 *
 * Feature: 005-llm-integration User Story 1
 *
 * Note: Full integration testing (SSE parsing, callbacks, error handling)
 * is covered by E2E tests in tests/e2e/llm-integration.spec.js
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { StreamingClient } from '../../src/services/streamingClient.js'

describe('StreamingClient', () => {
  let client

  beforeEach(() => {
    client = new StreamingClient('http://localhost:8000')
    vi.clearAllMocks()
  })

  describe('constructor', () => {
    it('should accept required parameters', () => {
      expect(client.streamChat).toBeDefined()
      expect(typeof client.streamChat).toBe('function')
    })

    it('should use baseURL from constructor', () => {
      const customClient = new StreamingClient('http://custom-api:3000')
      expect(customClient.baseURL).toBe('http://custom-api:3000')
    })

    it('should use default baseURL if not provided', () => {
      const defaultClient = new StreamingClient()
      expect(defaultClient.baseURL).toBeTruthy()
    })
  })

  describe('stopStream', () => {
    it('should call abort on active controller', () => {
      const mockController = {
        abort: vi.fn()
      }
      client.activeStream = mockController

      client.stopStream()

      expect(mockController.abort).toHaveBeenCalled()
      expect(client.activeStream).toBeNull()
    })

    it('should handle no active stream gracefully', () => {
      client.activeStream = null
      expect(() => client.stopStream()).not.toThrow()
    })

    it('should set activeStream to null after stopping', () => {
      const mockController = {
        abort: vi.fn()
      }
      client.activeStream = mockController

      client.stopStream()

      expect(client.activeStream).toBeNull()
    })
  })
})
