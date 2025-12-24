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

  return {
    isProcessing: computed(() => isProcessing.value),
    status: computed(() => status.value),
    statusType: computed(() => statusType.value),
    setProcessing,
    setStatus,
    setError,
    clearStatus,
  }
}
