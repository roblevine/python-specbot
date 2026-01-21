/**
 * Settings Schema v2.0.0
 * Simple user preferences storage - no conversation data
 *
 * Feature: 018-audit-local-storage
 */

export const SETTINGS_VERSION = '2.0.0'
export const SETTINGS_KEY = 'specbot:settings:v2'

/**
 * Default settings structure
 */
export const DEFAULT_SETTINGS = {
  sidebarCollapsed: false,
  selectedModelId: null,
}

/**
 * Creates a new settings object with default values
 * @returns {Object} Fresh settings object
 */
export function createDefaultSettings() {
  return {
    version: SETTINGS_VERSION,
    settings: { ...DEFAULT_SETTINGS },
  }
}

/**
 * Validates stored settings data
 * @param {*} data - Data to validate
 * @returns {Object} Validation result with isValid, data, and error
 */
export function validateSettings(data) {
  // Check for null/undefined
  if (data == null) {
    return {
      isValid: false,
      data: null,
      error: 'Data is null or undefined',
    }
  }

  // Check version
  if (data.version !== SETTINGS_VERSION) {
    return {
      isValid: false,
      data: null,
      error: `Invalid version: expected ${SETTINGS_VERSION}, got ${data.version}`,
    }
  }

  // Check settings object exists
  if (!data.settings || typeof data.settings !== 'object') {
    return {
      isValid: false,
      data: null,
      error: 'Missing or invalid settings object',
    }
  }

  const settings = data.settings

  // Validate sidebarCollapsed
  if (typeof settings.sidebarCollapsed !== 'boolean') {
    return {
      isValid: false,
      data: null,
      error: 'sidebarCollapsed must be a boolean',
    }
  }

  // Validate selectedModelId
  if (settings.selectedModelId !== null) {
    if (typeof settings.selectedModelId !== 'string' || settings.selectedModelId === '') {
      return {
        isValid: false,
        data: null,
        error: 'selectedModelId must be null or a non-empty string',
      }
    }
  }

  // All validations passed
  return {
    isValid: true,
    data: settings,
    error: null,
  }
}
