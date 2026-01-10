import { describe, it, expect } from 'vitest'
import { ApiError } from '../../src/services/apiClient.js'

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
