/**
 * useAppState Composable
 * Manages application UI state (processing, status, errors)
 */

import { ref, computed } from 'vue'
import * as logger from '../utils/logger.js'

// Shared state
const isProcessing = ref(false)
const status = ref('Ready')
const statusType = ref('ready') // 'ready', 'processing', 'error'

// T037: Connection status state
const isConnected = ref(true) // Optimistically assume connected
const connectionStatus = ref('connected') // 'connected', 'disconnected', 'reconnecting'
const lastConnectionCheck = ref(null)

export function useAppState() {
  /**
   * Sets the processing state
   * @param {boolean} value - Whether the app is processing
   */
  function setProcessing(value) {
    isProcessing.value = value
    if (value) {
      statusType.value = 'processing'
    } else if (statusType.value === 'processing') {
      statusType.value = 'ready'
    }
  }

  /**
   * Sets the status message and type
   * @param {string} message - Status message to display
   * @param {string} type - Status type ('ready', 'processing', 'error')
   */
  function setStatus(message, type = 'ready') {
    status.value = message
    statusType.value = type
    logger.debug('Status updated', { message, type })
  }

  /**
   * Sets an error status
   * @param {string} message - Error message to display
   */
  function setError(message) {
    setStatus(message, 'error')
    logger.warn('Error status set', message)

    // Auto-clear error after 5 seconds
    setTimeout(() => {
      if (statusType.value === 'error') {
        setStatus('Ready', 'ready')
      }
    }, 5000)
  }

  /**
   * Clears the status message
   */
  function clearStatus() {
    setStatus('Ready', 'ready')
  }

  /**
   * T037: Set connection status
   * @param {boolean} connected - Whether connected to server
   */
  function setConnected(connected) {
    isConnected.value = connected
    connectionStatus.value = connected ? 'connected' : 'disconnected'
    lastConnectionCheck.value = new Date().toISOString()

    if (!connected) {
      logger.warn('Connection to server lost')
    } else {
      logger.info('Connection to server restored')
    }
  }

  /**
   * T037: Set reconnecting status
   */
  function setReconnecting() {
    connectionStatus.value = 'reconnecting'
    logger.info('Attempting to reconnect to server')
  }

  /**
   * T037: Mark connection as failed after network error
   * @param {Error} error - The error that caused the connection failure
   */
  function handleConnectionError(error) {
    const isNetworkError = error?.details?.network === true ||
      (error instanceof TypeError && error.message.includes('fetch'))

    if (isNetworkError) {
      setConnected(false)
    }
  }

  return {
    isProcessing: computed(() => isProcessing.value),
    status: computed(() => status.value),
    statusType: computed(() => statusType.value),
    // T037: Connection status
    isConnected: computed(() => isConnected.value),
    connectionStatus: computed(() => connectionStatus.value),
    lastConnectionCheck: computed(() => lastConnectionCheck.value),
    setProcessing,
    setStatus,
    setError,
    clearStatus,
    // T037: Connection functions
    setConnected,
    setReconnecting,
    handleConnectionError,
  }
}
