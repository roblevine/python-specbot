import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ApiError, streamMessage } from '../../src/services/apiClient.js'

describe('ApiError', () => {
  // T033: ApiError includes statusCode and details properties
  it('should include statusCode and details properties', () => {
    const error = new ApiError(
      'Test error message',
      422,
      { field: 'message', reason: 'Invalid input' }
    )

    expect(error).toBeInstanceOf(Error)
    expect(error).toBeInstanceOf(ApiError)
    expect(error.message).toBe('Test error message')
    expect(error.name).toBe('ApiError')
    expect(error.statusCode).toBe(422)
    expect(error.details).toEqual({ field: 'message', reason: 'Invalid input' })
  })

  it('should handle null statusCode and details', () => {
    const error = new ApiError('Network error', null, null)

    expect(error.message).toBe('Network error')
    expect(error.statusCode).toBeNull()
    expect(error.details).toBeNull()
  })

  it('should handle statusCode without details', () => {
    const error = new ApiError('Server error', 500)

    expect(error.message).toBe('Server error')
    expect(error.statusCode).toBe(500)
    expect(error.details).toBeNull()
  })

  it('should handle details without statusCode', () => {
    const error = new ApiError('Validation error', null, { field: 'email' })

    expect(error.message).toBe('Validation error')
    expect(error.statusCode).toBeNull()
    expect(error.details).toEqual({ field: 'email' })
  })

  it('should preserve error stack trace', () => {
    const error = new ApiError('Test error', 400, {})

    expect(error.stack).toBeDefined()
    expect(error.stack).toContain('ApiError')
  })
})

/**
 * T014: Tests for streamMessage() function
 * Feature: 009-message-streaming User Story 1
 *
 * Tests streaming message functionality using fetch + ReadableStream
 * (EventSource doesn't support POST, so we use fetch with SSE parsing)
 */
describe('streamMessage', () => {
  let mockAbortController
  let mockReader
  let mockResponse

  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks()

    // Mock AbortController
    mockAbortController = {
      signal: {},
      abort: vi.fn(),
    }
    global.AbortController = vi.fn(() => mockAbortController)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  /**
   * Helper function to create a mock ReadableStream that yields SSE events
   */
  function createMockStream(events) {
    let eventIndex = 0

    mockReader = {
      read: vi.fn(async () => {
        if (eventIndex >= events.length) {
          return { done: true, value: undefined }
        }

        const event = events[eventIndex++]
        const encoder = new TextEncoder()
        return { done: false, value: encoder.encode(event) }
      }),
    }

    mockResponse = {
      ok: true,
      status: 200,
      body: {
        getReader: vi.fn(() => mockReader),
      },
    }

    global.fetch = vi.fn(async () => mockResponse)
  }

  // T014: Test fetch called with correct URL, method, headers, and body
  it('should call fetch with correct URL and streaming headers', async () => {
    createMockStream(['data: {"type":"token","content":"Hello"}\n\n'])

    const onToken = vi.fn()
    const onComplete = vi.fn()

    const cleanup = streamMessage('Test message', onToken, onComplete)

    // Wait for async operations
    await new Promise(resolve => setTimeout(resolve, 10))

    // URL may have base URL prefix depending on VITE_API_BASE_URL env var
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/v1\/messages$/),
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        }),
        body: expect.stringContaining('"message":"Test message"'),
        signal: mockAbortController.signal,
      })
    )

    cleanup()
  })

  // T014: Test token event handling - onToken callback should be called
  it('should call onToken callback for each token event', async () => {
    createMockStream([
      'data: {"type":"token","content":"Hello"}\n\n',
      'data: {"type":"token","content":" "}\n\n',
      'data: {"type":"token","content":"world"}\n\n',
    ])

    const onToken = vi.fn()
    const onComplete = vi.fn()

    const cleanup = streamMessage('Test', onToken, onComplete)

    // Wait for stream to process
    await new Promise(resolve => setTimeout(resolve, 50))

    expect(onToken).toHaveBeenCalledTimes(3)
    expect(onToken).toHaveBeenNthCalledWith(1, 'Hello')
    expect(onToken).toHaveBeenNthCalledWith(2, ' ')
    expect(onToken).toHaveBeenNthCalledWith(3, 'world')

    cleanup()
  })

  // T014: Test complete event handling - onComplete callback should be called
  it('should call onComplete callback for complete event', async () => {
    createMockStream([
      'data: {"type":"token","content":"Done"}\n\n',
      'data: {"type":"complete","model":"gpt-3.5-turbo","totalTokens":5}\n\n',
    ])

    const onToken = vi.fn()
    const onComplete = vi.fn()

    const cleanup = streamMessage('Test', onToken, onComplete)

    await new Promise(resolve => setTimeout(resolve, 50))

    expect(onComplete).toHaveBeenCalledTimes(1)
    expect(onComplete).toHaveBeenCalledWith({
      type: 'complete',
      model: 'gpt-3.5-turbo',
      totalTokens: 5,
    })

    cleanup()
  })

  // T014: Test connection close via cleanup function
  it('should abort connection when cleanup function is called', async () => {
    createMockStream([
      'data: {"type":"token","content":"Start"}\n\n',
      // Stream will be aborted before this
      'data: {"type":"token","content":"Never seen"}\n\n',
    ])

    const onToken = vi.fn()
    const onComplete = vi.fn()

    const cleanup = streamMessage('Test', onToken, onComplete)

    // Wait briefly for first event
    await new Promise(resolve => setTimeout(resolve, 10))

    // Call cleanup to abort
    cleanup()

    expect(mockAbortController.abort).toHaveBeenCalled()
  })

  // T014: Test with conversation history
  it('should include conversation history in request body', async () => {
    createMockStream(['data: {"type":"token","content":"Reply"}\n\n'])

    const onToken = vi.fn()
    const onComplete = vi.fn()
    const history = [
      { sender: 'user', text: 'Hello' },
      { sender: 'assistant', text: 'Hi there' },
    ]

    const cleanup = streamMessage('Follow up', onToken, onComplete, null, history)

    await new Promise(resolve => setTimeout(resolve, 10))

    expect(global.fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        body: expect.stringMatching(/"history":\[.*\]/),
      })
    )

    cleanup()
  })

  // T014: Test with custom model selection
  it('should include model parameter in request body', async () => {
    createMockStream(['data: {"type":"token","content":"Reply"}\n\n'])

    const onToken = vi.fn()
    const onComplete = vi.fn()

    const cleanup = streamMessage('Test', onToken, onComplete, null, null, 'gpt-4')

    await new Promise(resolve => setTimeout(resolve, 10))

    expect(global.fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        body: expect.stringContaining('"model":"gpt-4"'),
      })
    )

    cleanup()
  })

  // T014: Test error event handling
  it('should call onError callback for error events', async () => {
    createMockStream([
      'data: {"type":"token","content":"Start"}\n\n',
      'data: {"type":"error","error":"Rate limit exceeded","code":"RATE_LIMIT"}\n\n',
    ])

    const onToken = vi.fn()
    const onComplete = vi.fn()
    const onError = vi.fn()

    const cleanup = streamMessage('Test', onToken, onComplete, onError)

    await new Promise(resolve => setTimeout(resolve, 50))

    expect(onError).toHaveBeenCalledWith({
      type: 'error',
      error: 'Rate limit exceeded',
      code: 'RATE_LIMIT',
    })

    cleanup()
  })

  // T014: Test network error handling
  it('should handle fetch errors gracefully', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'))

    const onToken = vi.fn()
    const onComplete = vi.fn()
    const onError = vi.fn()

    const cleanup = streamMessage('Test', onToken, onComplete, onError)

    await new Promise(resolve => setTimeout(resolve, 50))

    expect(onError).toHaveBeenCalledWith(
      expect.objectContaining({
        error: expect.stringContaining('Network error'),
      })
    )

    cleanup()
  })

  // T014: Test HTTP error response handling
  it('should handle HTTP error responses', async () => {
    mockResponse = {
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: vi.fn().mockResolvedValue({ error: 'Server error' }),
    }

    global.fetch = vi.fn(async () => mockResponse)

    const onToken = vi.fn()
    const onComplete = vi.fn()
    const onError = vi.fn()

    const cleanup = streamMessage('Test', onToken, onComplete, onError)

    await new Promise(resolve => setTimeout(resolve, 50))

    expect(onError).toHaveBeenCalled()
    expect(onToken).not.toHaveBeenCalled()
    expect(onComplete).not.toHaveBeenCalled()

    cleanup()
  })

  // T014: Test SSE format parsing with multiple events in one chunk
  it('should handle multiple SSE events in a single chunk', async () => {
    createMockStream([
      'data: {"type":"token","content":"Hello"}\n\ndata: {"type":"token","content":" "}\n\ndata: {"type":"token","content":"world"}\n\n',
    ])

    const onToken = vi.fn()
    const onComplete = vi.fn()

    const cleanup = streamMessage('Test', onToken, onComplete)

    await new Promise(resolve => setTimeout(resolve, 50))

    expect(onToken).toHaveBeenCalledTimes(3)
    expect(onToken).toHaveBeenNthCalledWith(1, 'Hello')
    expect(onToken).toHaveBeenNthCalledWith(2, ' ')
    expect(onToken).toHaveBeenNthCalledWith(3, 'world')

    cleanup()
  })

  // T014: Test partial SSE events across chunks
  it('should handle SSE events split across multiple chunks', async () => {
    createMockStream([
      'data: {"type":"to',
      'ken","content":"Hel',
      'lo"}\n\n',
      'data: {"type":"complete","model":"gpt-3.5-turbo"}\n\n',
    ])

    const onToken = vi.fn()
    const onComplete = vi.fn()

    const cleanup = streamMessage('Test', onToken, onComplete)

    await new Promise(resolve => setTimeout(resolve, 50))

    expect(onToken).toHaveBeenCalledWith('Hello')
    expect(onComplete).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'complete',
        model: 'gpt-3.5-turbo',
      })
    )

    cleanup()
  })

  // T014: Test special characters and unicode preservation
  it('should preserve special characters and unicode in tokens', async () => {
    createMockStream([
      'data: {"type":"token","content":"Hello 🚀"}\n\n',
      'data: {"type":"token","content":"世界"}\n\n',
      'data: {"type":"token","content":"@#$%"}\n\n',
    ])

    const onToken = vi.fn()
    const onComplete = vi.fn()

    const cleanup = streamMessage('Test', onToken, onComplete)

    await new Promise(resolve => setTimeout(resolve, 50))

    expect(onToken).toHaveBeenNthCalledWith(1, 'Hello 🚀')
    expect(onToken).toHaveBeenNthCalledWith(2, '世界')
    expect(onToken).toHaveBeenNthCalledWith(3, '@#$%')

    cleanup()
  })
})
