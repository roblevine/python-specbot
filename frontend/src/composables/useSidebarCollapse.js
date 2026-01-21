import { ref, watch } from 'vue'
import * as logger from '../utils/logger.js'
import { getSetting, saveSetting } from '../storage/SettingsStorage.js'

/**
 * Composable for managing sidebar collapse state with SettingsStorage persistence
 *
 * Feature: 018-audit-local-storage
 * @returns {Object} Sidebar collapse state and control methods
 */
export function useSidebarCollapse() {
  const isCollapsed = ref(false)

  /**
   * Load sidebar collapsed state from SettingsStorage
   * T010: Load initial state from SettingsStorage
   * T012: Handle default value when no settings exist
   */
  const loadFromStorage = () => {
    try {
      const stored = getSetting('sidebarCollapsed', false)
      isCollapsed.value = stored
      logger.debug('Loaded sidebar state from storage', { isCollapsed: isCollapsed.value })
    } catch (error) {
      logger.error('Failed to load sidebar state', error)
      isCollapsed.value = false
    }
  }

  /**
   * Watch for changes and save to SettingsStorage
   * T014: Save to SettingsStorage when isCollapsed changes
   */
  watch(isCollapsed, (newValue) => {
    try {
      saveSetting('sidebarCollapsed', newValue)
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
