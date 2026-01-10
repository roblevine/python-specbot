import { describe, it, expect } from 'vitest'
import {
  redactSensitiveData,
  containsSensitiveData,
  detectSensitivePatterns
} from '@/utils/sensitiveDataRedactor'

describe('sensitiveDataRedactor', () => {
  describe('redactSensitiveData', () => {
    it('should redact AWS API keys', () => {
      const text = 'Error: API key AKIAIOSFODNN7EXAMPLE failed'
      const redacted = redactSensitiveData(text)

      expect(redacted).not.toContain('AKIAIOSFODNN7EXAMPLE')
      expect(redacted).toContain('***REDACTED_AWS_KEY***')
    })

    it('should redact JWT tokens', () => {
      const text = 'Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U'
      const redacted = redactSensitiveData(text)

      expect(redacted).toContain('***REDACTED_JWT***')
      expect(redacted).not.toContain('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9')
    })

    it('should redact Bearer tokens', () => {
      const text = 'Authorization: Bearer abc123def456'
      const redacted = redactSensitiveData(text)

      expect(redacted).toContain('Bearer ***REDACTED_TOKEN***')
      expect(redacted).not.toContain('abc123def456')
    })

    it('should not modify text without sensitive data', () => {
      const text = 'Normal error message'
      const redacted = redactSensitiveData(text)

      expect(redacted).toBe(text)
    })

    it('should handle null or undefined input', () => {
      expect(redactSensitiveData(null)).toBe(null)
      expect(redactSensitiveData(undefined)).toBe(undefined)
    })
  })

  describe('containsSensitiveData', () => {
    it('should detect AWS API keys', () => {
      const textWithSecret = 'API key: AKIAIOSFODNN7EXAMPLE'
      const textWithoutSecret = 'Normal error message'

      expect(containsSensitiveData(textWithSecret)).toBe(true)
      expect(containsSensitiveData(textWithoutSecret)).toBe(false)
    })

    it('should detect JWT tokens', () => {
      const text = 'JWT: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0In0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
      expect(containsSensitiveData(text)).toBe(true)
    })

    it('should return false for null or undefined', () => {
      expect(containsSensitiveData(null)).toBe(false)
      expect(containsSensitiveData(undefined)).toBe(false)
    })
  })

  describe('detectSensitivePatterns', () => {
    it('should identify which patterns were detected', () => {
      const text = 'AWS key: AKIAIOSFODNN7EXAMPLE, JWT: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0In0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
      const patterns = detectSensitivePatterns(text)

      expect(patterns).toContain('AWS API Key')
      expect(patterns).toContain('JWT Token')
    })

    it('should return empty array for text without sensitive data', () => {
      const text = 'Normal error message'
      const patterns = detectSensitivePatterns(text)

      expect(patterns).toEqual([])
    })

    it('should return empty array for null or undefined', () => {
      expect(detectSensitivePatterns(null)).toEqual([])
      expect(detectSensitivePatterns(undefined)).toEqual([])
    })
  })
})
