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

export { LOG_LEVELS }
