/**
 * Validation Utilities
 * Functions for validating messages, conversations, and data structures
 */

/**
 * Validates message text
 * @param {string} text - Message text to validate
 * @returns {Object} Validation result with { isValid: boolean, error: string|null }
 */
export function validateMessageText(text) {
  if (typeof text !== 'string') {
    return { isValid: false, error: 'Message text must be a string' }
  }

  const trimmed = text.trim()

  if (trimmed.length === 0) {
    return { isValid: false, error: 'Message cannot be empty or only whitespace' }
  }

  if (trimmed.length > 10000) {
    return { isValid: false, error: 'Message cannot exceed 10,000 characters' }
  }

  return { isValid: true, error: null }
}

/**
 * Validates conversation data structure
 * @param {Object} conversation - Conversation object to validate
 * @returns {Object} Validation result with { isValid: boolean, error: string|null }
 */
export function validateConversation(conversation) {
  if (!conversation || typeof conversation !== 'object') {
    return { isValid: false, error: 'Conversation must be an object' }
  }

  if (!conversation.id || !conversation.id.startsWith('conv-')) {
    return { isValid: false, error: 'Conversation must have valid ID with conv- prefix' }
  }

  if (!conversation.createdAt || !isValidISODate(conversation.createdAt)) {
    return { isValid: false, error: 'Conversation must have valid createdAt ISO timestamp' }
  }

  if (!conversation.updatedAt || !isValidISODate(conversation.updatedAt)) {
    return { isValid: false, error: 'Conversation must have valid updatedAt ISO timestamp' }
  }

  if (!Array.isArray(conversation.messages)) {
    return { isValid: false, error: 'Conversation must have messages array' }
  }

  return { isValid: true, error: null }
}

/**
 * Validates message data structure
 * @param {Object} message - Message object to validate
 * @returns {Object} Validation result with { isValid: boolean, error: string|null }
 */
export function validateMessage(message) {
  if (!message || typeof message !== 'object') {
    return { isValid: false, error: 'Message must be an object' }
  }

  if (!message.id || !message.id.startsWith('msg-')) {
    return { isValid: false, error: 'Message must have valid ID with msg- prefix' }
  }

  // Allow empty text for streaming messages (they accumulate content progressively)
  // Only validate text if it's not a streaming assistant message
  const isStreamingAssistant = message.sender === 'assistant' && message.status === 'streaming'
  if (!isStreamingAssistant) {
    const textValidation = validateMessageText(message.text)
    if (!textValidation.isValid) {
      return textValidation
    }
  } else {
    // For streaming messages, just check text is a string
    if (typeof message.text !== 'string') {
      return { isValid: false, error: 'Message text must be a string' }
    }
  }

  // Updated for Feature 005: support 'assistant' sender for LLM responses
  if (!['user', 'system', 'assistant'].includes(message.sender)) {
    return { isValid: false, error: 'Message sender must be "user", "system", or "assistant"' }
  }

  // Updated for Feature 005: support 'streaming' and 'completed' statuses for LLM streaming
  if (!['pending', 'sent', 'error', 'streaming', 'completed'].includes(message.status)) {
    return { isValid: false, error: 'Message status must be "pending", "sent", "error", "streaming", or "completed"' }
  }

  if (!message.timestamp || !isValidISODate(message.timestamp)) {
    return { isValid: false, error: 'Message must have valid timestamp ISO format' }
  }

  return { isValid: true, error: null }
}

/**
 * Checks if a string is a valid ISO 8601 date
 * @param {string} dateString - Date string to validate
 * @returns {boolean} True if valid ISO date
 */
function isValidISODate(dateString) {
  if (typeof dateString !== 'string') return false
  const date = new Date(dateString)
  // Check if date is valid and can be converted to ISO string
  if (isNaN(date.getTime())) return false
  return date.toISOString() === dateString
}
