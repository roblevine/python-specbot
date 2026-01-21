/**
 * Settings Storage Adapter
 * Unified interface for all localStorage settings operations
 *
 * Feature: 018-audit-local-storage
 */

import {
  SETTINGS_KEY,
  DEFAULT_SETTINGS,
  createDefaultSettings,
  validateSettings,
} from './SettingsSchema.js'
import * as logger from '../utils/logger.js'

/**
 * Loads all settings from localStorage
 * @returns {Object} Settings object (always returns valid settings, defaults if invalid)
 */
export function loadSettings() {
  try {
    const stored = localStorage.getItem(SETTINGS_KEY)

    if (!stored) {
      logger.debug('No settings found, using defaults')
      return { ...DEFAULT_SETTINGS }
    }

    const data = JSON.parse(stored)
    const validation = validateSettings(data)

    if (!validation.isValid) {
      logger.warn('Invalid settings data, using defaults', { error: validation.error })
      return { ...DEFAULT_SETTINGS }
    }

    logger.debug('Loaded settings from storage', validation.data)
    return validation.data
  } catch (error) {
    logger.error('Failed to load settings', error)
    return { ...DEFAULT_SETTINGS }
  }
}

/**
 * Saves a single setting to localStorage
 * Preserves other settings when updating one
 * @param {string} key - Setting key (e.g., 'sidebarCollapsed', 'selectedModelId')
 * @param {*} value - Value to save
 */
export function saveSetting(key, value) {
  try {
    // Load current settings or create new
    let data
    const stored = localStorage.getItem(SETTINGS_KEY)

    if (stored) {
      try {
        data = JSON.parse(stored)
        // If invalid, start fresh
        if (!validateSettings(data).isValid) {
          data = createDefaultSettings()
        }
      } catch {
        data = createDefaultSettings()
      }
    } else {
      data = createDefaultSettings()
    }

    // Update the specific setting
    data.settings[key] = value

    // Save back to localStorage
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(data))
    logger.debug('Saved setting', { key, value })
  } catch (error) {
    logger.error('Failed to save setting', { key, error })
    // Don't throw - settings are non-critical
  }
}

/**
 * Gets a single setting value
 * @param {string} key - Setting key
 * @param {*} defaultValue - Default value if not found (defaults to null)
 * @returns {*} The setting value or default
 */
export function getSetting(key, defaultValue = null) {
  try {
    const settings = loadSettings()
    return key in settings ? settings[key] : defaultValue
  } catch (error) {
    logger.error('Failed to get setting', { key, error })
    return defaultValue
  }
}
