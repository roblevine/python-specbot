/**
 * Logger Utility
 * Provides console logging with different severity levels
 */

const LOG_LEVELS = {
  DEBUG: 'DEBUG',
  INFO: 'INFO',
  WARN: 'WARN',
  ERROR: 'ERROR',
}

// Current log level (can be changed via setLogLevel)
let currentLogLevel = LOG_LEVELS.INFO

/**
 * Sets the minimum log level to output
 * @param {string} level - One of DEBUG, INFO, WARN, ERROR
 */
export function setLogLevel(level) {
  if (Object.values(LOG_LEVELS).includes(level)) {
    currentLogLevel = level
  }
}

/**
 * Gets the current log level
 * @returns {string} Current log level
 */
export function getLogLevel() {
  return currentLogLevel
}

/**
 * Logs a debug message
 * @param {string} message - Message to log
 * @param  {...any} args - Additional arguments
 */
export function debug(message, ...args) {
  if (shouldLog(LOG_LEVELS.DEBUG)) {
    console.log(`[DEBUG] ${message}`, ...args)
  }
}

/**
 * Logs an info message
 * @param {string} message - Message to log
 * @param  {...any} args - Additional arguments
 */
export function info(message, ...args) {
  if (shouldLog(LOG_LEVELS.INFO)) {
    console.info(`[INFO] ${message}`, ...args)
  }
}

/**
 * Logs a warning message
 * @param {string} message - Message to log
 * @param  {...any} args - Additional arguments
 */
export function warn(message, ...args) {
  if (shouldLog(LOG_LEVELS.WARN)) {
    console.warn(`[WARN] ${message}`, ...args)
  }
}

/**
 * Logs an error message
 * @param {string} message - Message to log
 * @param  {...any} args - Additional arguments
 */
export function error(message, ...args) {
  if (shouldLog(LOG_LEVELS.ERROR)) {
    console.error(`[ERROR] ${message}`, ...args)
  }
}

/**
 * Determines if a log level should be output
 * @param {string} level - Level to check
 * @returns {boolean} True if should log
 */
function shouldLog(level) {
  const levels = [LOG_LEVELS.DEBUG, LOG_LEVELS.INFO, LOG_LEVELS.WARN, LOG_LEVELS.ERROR]
  return levels.indexOf(level) >= levels.indexOf(currentLogLevel)
}

/**
 * T016: Streaming-specific logging functions
 * Feature: 009-message-streaming User Story 1
 */

/**
 * Logs the start of a streaming request
 * @param {string} messageText - The message being sent
 * @param {object} options - Optional streaming options (model, historyLength)
 */
export function logStreamStart(messageText, options = {}) {
  info('Stream started', {
    messagePreview: messageText.substring(0, 50) + (messageText.length > 50 ? '...' : ''),
    messageLength: messageText.length,
    ...options,
  })
}

/**
 * Logs when a token is received during streaming
 * @param {number} tokenCount - Current count of tokens received
 * @param {string} latestToken - The most recently received token (optional for debugging)
 */
export function logTokenReceived(tokenCount, latestToken = null) {
  if (tokenCount % 10 === 0) {
    // Log every 10 tokens to avoid console spam
    debug(`Streaming: ${tokenCount} tokens received`, latestToken ? { latestToken } : {})
  }
}

/**
 * Logs when a stream completes successfully
 * @param {number} duration - Duration in milliseconds
 * @param {number} totalTokens - Total number of tokens received
 * @param {string} model - Model used for generation
 */
export function logStreamComplete(duration, totalTokens, model = null) {
  info('Stream completed', {
    duration: `${duration}ms`,
    totalTokens,
    tokensPerSecond: totalTokens / (duration / 1000),
    ...(model && { model }),
  })
}

/**
 * Logs when a stream is aborted/cancelled
 * @param {string} reason - Reason for abortion (user, error, etc.)
 */
export function logStreamAbort(reason = 'user_cancelled') {
  info('Stream aborted', { reason })
}

/**
 * Logs when a stream encounters an error
 * @param {string} errorMessage - Error message
 * @param {object} errorDetails - Additional error details
 */
export function logStreamError(errorMessage, errorDetails = {}) {
  error('Stream error', { error: errorMessage, ...errorDetails })
}

export { LOG_LEVELS }
