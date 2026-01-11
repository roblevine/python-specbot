import { ref, watch } from 'vue'
import * as logger from '../utils/logger.js'

/**
 * Composable for managing sidebar collapse state with LocalStorage persistence
 * @returns {Object} Sidebar collapse state and control methods
 */
export function useSidebarCollapse() {
  const isCollapsed = ref(false)

  /**
   * Load sidebar collapsed state from LocalStorage
   */
  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem('sidebar.collapsed')

      // Validate: only accept 'true' or 'false' strings
      if (stored !== 'true' && stored !== 'false') {
        if (stored !== null) {
          logger.warn('Invalid sidebar.collapsed value, defaulting to false', { stored })
        }
        isCollapsed.value = false
        return
      }

      isCollapsed.value = stored === 'true'
      logger.debug('Loaded sidebar state from storage', { isCollapsed: isCollapsed.value })
    } catch (error) {
      logger.error('Failed to load sidebar state', error)
      isCollapsed.value = false
    }
  }

  /**
   * Watch for changes and save to LocalStorage
   */
  watch(isCollapsed, (newValue) => {
    try {
      localStorage.setItem('sidebar.collapsed', String(newValue))
      logger.debug('Saved sidebar state to storage', { isCollapsed: newValue })
    } catch (error) {
      logger.error('Failed to persist sidebar preference', error)
      // Continue execution - user can still use sidebar, just won't persist
    }
  })

  /**
   * Toggle sidebar collapsed state
   */
  const toggle = () => {
    isCollapsed.value = !isCollapsed.value
    logger.info('Sidebar toggled', { isCollapsed: isCollapsed.value })
  }

  /**
   * Explicitly collapse sidebar
   */
  const collapse = () => {
    isCollapsed.value = true
  }

  /**
   * Explicitly expand sidebar
   */
  const expand = () => {
    isCollapsed.value = false
  }

  return {
    isCollapsed,
    toggle,
    collapse,
    expand,
    loadFromStorage,
  }
}
