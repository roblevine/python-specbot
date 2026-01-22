import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ApiError, streamMessage, generateTitle, getTitleModel } from '../../src/services/apiClient.js'

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

/**
 * T014: Tests for generateTitle() function
 * Feature: 019-llm-conversation-titles User Story 1
 */
describe('generateTitle', () => {
  let mockAbortController

  beforeEach(() => {
    vi.clearAllMocks()

    mockAbortController = {
      signal: {},
      abort: vi.fn(),
    }
    global.AbortController = vi.fn(() => mockAbortController)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should call API with correct URL and request body', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: 'success', title: 'Generated Title' }),
    })

    const messages = [
      { sender: 'user', text: 'Hello' },
      { sender: 'system', text: 'Hi there!' },
    ]

    await generateTitle(messages, 'gpt-3.5-turbo')

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/v1\/titles\/generate$/),
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
        body: expect.stringContaining('"model":"gpt-3.5-turbo"'),
      })
    )
  })

  it('should return the generated title', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: 'success', title: 'Python Binary Search Guide' }),
    })

    const messages = [
      { sender: 'user', text: 'How do I implement binary search?' },
      { sender: 'system', text: 'Binary search works by...' },
    ]

    const title = await generateTitle(messages, 'gpt-4')

    expect(title).toBe('Python Binary Search Guide')
  })

  it('should throw ApiError for less than 2 messages', async () => {
    const messages = [{ sender: 'user', text: 'Hello' }]

    await expect(generateTitle(messages, 'gpt-4')).rejects.toThrow('At least 2 messages required')
  })

  it('should throw ApiError when model is not provided', async () => {
    const messages = [
      { sender: 'user', text: 'Hello' },
      { sender: 'system', text: 'Hi!' },
    ]

    await expect(generateTitle(messages, null)).rejects.toThrow('Model ID is required')
  })

  it('should throw ApiError on HTTP error response', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      json: () => Promise.resolve({ error: 'Invalid request' }),
    })

    const messages = [
      { sender: 'user', text: 'Hello' },
      { sender: 'system', text: 'Hi!' },
    ]

    await expect(generateTitle(messages, 'gpt-4')).rejects.toThrow()
  })

  it('should throw ApiError on network error', async () => {
    global.fetch = vi.fn().mockRejectedValue(new TypeError('fetch failed'))

    const messages = [
      { sender: 'user', text: 'Hello' },
      { sender: 'system', text: 'Hi!' },
    ]

    await expect(generateTitle(messages, 'gpt-4')).rejects.toThrow('Cannot connect to server')
  })
})

/**
 * T015: Tests for getTitleModel() function
 * Feature: 019-llm-conversation-titles User Story 2
 */
describe('getTitleModel', () => {
  it('should return current model when models list is empty', () => {
    const result = getTitleModel('gpt-4', [])
    expect(result).toBe('gpt-4')
  })

  it('should return current model when it is not found in models list', () => {
    const models = [
      { id: 'gpt-3.5-turbo', provider: 'openai', titleModel: false },
    ]

    const result = getTitleModel('unknown-model', models)
    expect(result).toBe('unknown-model')
  })

  it('should return configured title model for the same provider', () => {
    const models = [
      { id: 'gpt-4', provider: 'openai', titleModel: false },
      { id: 'gpt-3.5-turbo', provider: 'openai', titleModel: true },
    ]

    const result = getTitleModel('gpt-4', models)
    expect(result).toBe('gpt-3.5-turbo')
  })

  it('should return current model when no title model configured for provider', () => {
    const models = [
      { id: 'gpt-4', provider: 'openai', titleModel: false },
      { id: 'gpt-3.5-turbo', provider: 'openai', titleModel: false },
    ]

    const result = getTitleModel('gpt-4', models)
    expect(result).toBe('gpt-4')
  })

  it('should use title model from correct provider', () => {
    const models = [
      { id: 'gpt-4', provider: 'openai', titleModel: false },
      { id: 'gpt-3.5-turbo', provider: 'openai', titleModel: true },
      { id: 'claude-3', provider: 'anthropic', titleModel: false },
      { id: 'claude-haiku', provider: 'anthropic', titleModel: true },
    ]

    // When using OpenAI model, should get OpenAI title model
    expect(getTitleModel('gpt-4', models)).toBe('gpt-3.5-turbo')

    // When using Anthropic model, should get Anthropic title model
    expect(getTitleModel('claude-3', models)).toBe('claude-haiku')
  })
})
