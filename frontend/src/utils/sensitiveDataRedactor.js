/**
 * Sensitive Data Redaction Utility
 * Based on patterns from secrets-patterns-db and security best practices
 */

export const SENSITIVE_PATTERNS = [
  // API Keys and Tokens (ordered from specific to generic)
  {
    name: 'AWS API Key',
    pattern: /AKIA[0-9A-Z]{16}/g,
    replacement: '***REDACTED_AWS_KEY***'
  },
  {
    name: 'Google API Key',
    pattern: /AIza[0-9A-Za-z\-_]{35}/g,
    replacement: '***REDACTED_GOOGLE_KEY***'
  },
  {
    name: 'Stripe Key',
    pattern: /sk_live_[0-9a-zA-Z]{24}/g,
    replacement: '***REDACTED_STRIPE_KEY***'
  },
  {
    name: 'GitHub Token',
    pattern: /gh[pousr]_[A-Za-z0-9_]{36,255}/g,
    replacement: '***REDACTED_GITHUB_TOKEN***'
  },
  {
    name: 'Bearer Token',
    pattern: /Bearer\s+[a-zA-Z0-9\-._~+/]+=*/g,
    replacement: 'Bearer ***REDACTED_TOKEN***'
  },

  // Private Keys
  {
    name: 'Private Key',
    pattern: /-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----[\s\S]*?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----/g,
    replacement: '***REDACTED_PRIVATE_KEY***'
  },

  // JWT Tokens (must come before generic patterns)
  {
    name: 'JWT Token',
    pattern: /eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}/g,
    replacement: '***REDACTED_JWT***'
  },

  // Passwords (in assignments)
  {
    name: 'Password Assignment',
    pattern: /(?:password|pwd|pass)['"\s:=]+[^\s'"]{4,100}/gi,
    replacement: 'password=***REDACTED***'
  },

  // Session/Auth tokens in URLs
  {
    name: 'Session Token in URL',
    pattern: /[?&](session|token|auth)=[a-zA-Z0-9\-_]{10,}/gi,
    replacement: '&$1=***REDACTED***'
  },

  // Generic API Key patterns (must come after specific ones)
  {
    name: 'Generic API Key',
    pattern: /(?:api[_-]?key)['"\s:=]+[a-zA-Z0-9\-_.]{8,100}/gi,
    replacement: 'api_key=***REDACTED***'
  },
  {
    name: 'Generic Secret',
    pattern: /(?:secret|token)['"\s:=]+[a-zA-Z0-9\-_.]{8,100}/gi,
    replacement: 'secret=***REDACTED***'
  },

  // Credit Card Numbers
  {
    name: 'Credit Card',
    pattern: /\b(?:\d{4}[-\s]?){3}\d{4}\b/g,
    replacement: '****-****-****-****'
  },

  // Email addresses (optional - depends on use case)
  {
    name: 'Email',
    pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
    replacement: '***@***.***'
  }
]

/**
 * Redacts sensitive information from text
 * @param {string} text - Text to redact
 * @param {boolean} showPatternNames - Whether to include pattern names in redaction
 * @returns {string} Redacted text
 */
export function redactSensitiveData(text, showPatternNames = false) {
  if (!text || typeof text !== 'string') {
    return text
  }

  let redactedText = text

  // Apply patterns in order (specific to generic)
  for (const { name, pattern, replacement } of SENSITIVE_PATTERNS) {
    const finalReplacement = showPatternNames
      ? `[${name.toUpperCase()}_REDACTED]`
      : replacement
    redactedText = redactedText.replace(pattern, finalReplacement)
  }

  return redactedText
}

/**
 * Detects if text contains sensitive information
 * @param {string} text - Text to check
 * @returns {boolean} True if sensitive data detected
 */
export function containsSensitiveData(text) {
  if (!text || typeof text !== 'string') {
    return false
  }

  return SENSITIVE_PATTERNS.some(({ pattern }) => {
    // Reset regex lastIndex to ensure consistent results
    pattern.lastIndex = 0
    return pattern.test(text)
  })
}

/**
 * Gets list of detected sensitive pattern types
 * @param {string} text - Text to analyze
 * @returns {string[]} Array of detected pattern names
 */
export function detectSensitivePatterns(text) {
  if (!text || typeof text !== 'string') {
    return []
  }

  return SENSITIVE_PATTERNS
    .filter(({ pattern }) => {
      pattern.lastIndex = 0
      return pattern.test(text)
    })
    .map(({ name }) => name)
}
