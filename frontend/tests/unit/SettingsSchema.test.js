import { describe, it, expect } from 'vitest'
import {
  SETTINGS_VERSION,
  SETTINGS_KEY,
  DEFAULT_SETTINGS,
  createDefaultSettings,
  validateSettings,
} from '../../src/storage/SettingsSchema.js'

describe('SettingsSchema', () => {
  describe('Constants', () => {
    it('should export correct version', () => {
      expect(SETTINGS_VERSION).toBe('2.0.0')
    })

    it('should export correct storage key', () => {
      expect(SETTINGS_KEY).toBe('specbot:settings:v2')
    })

    it('should export default settings', () => {
      expect(DEFAULT_SETTINGS).toEqual({
        sidebarCollapsed: false,
        selectedModelId: null,
      })
    })
  })

  describe('createDefaultSettings', () => {
    it('should create a new settings object with defaults', () => {
      const settings = createDefaultSettings()
      expect(settings.version).toBe('2.0.0')
      expect(settings.settings.sidebarCollapsed).toBe(false)
      expect(settings.settings.selectedModelId).toBeNull()
    })

    it('should return a new object each time', () => {
      const settings1 = createDefaultSettings()
      const settings2 = createDefaultSettings()
      expect(settings1).not.toBe(settings2)
      expect(settings1.settings).not.toBe(settings2.settings)
    })
  })

  describe('validateSettings', () => {
    it('should return valid for correct data', () => {
      const data = {
        version: '2.0.0',
        settings: {
          sidebarCollapsed: true,
          selectedModelId: 'gpt-4',
        },
      }
      const result = validateSettings(data)
      expect(result.isValid).toBe(true)
      expect(result.data).toEqual(data.settings)
      expect(result.error).toBeNull()
    })

    it('should return invalid for wrong version', () => {
      const data = {
        version: '1.0.0',
        settings: {
          sidebarCollapsed: false,
          selectedModelId: null,
        },
      }
      const result = validateSettings(data)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('version')
    })

    it('should return invalid for missing version', () => {
      const data = {
        settings: {
          sidebarCollapsed: false,
          selectedModelId: null,
        },
      }
      const result = validateSettings(data)
      expect(result.isValid).toBe(false)
    })

    it('should return invalid for non-boolean sidebarCollapsed', () => {
      const data = {
        version: '2.0.0',
        settings: {
          sidebarCollapsed: 'true',
          selectedModelId: null,
        },
      }
      const result = validateSettings(data)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('sidebarCollapsed')
    })

    it('should return invalid for empty string selectedModelId', () => {
      const data = {
        version: '2.0.0',
        settings: {
          sidebarCollapsed: false,
          selectedModelId: '',
        },
      }
      const result = validateSettings(data)
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('selectedModelId')
    })

    it('should accept null selectedModelId', () => {
      const data = {
        version: '2.0.0',
        settings: {
          sidebarCollapsed: false,
          selectedModelId: null,
        },
      }
      const result = validateSettings(data)
      expect(result.isValid).toBe(true)
    })

    it('should accept valid string selectedModelId', () => {
      const data = {
        version: '2.0.0',
        settings: {
          sidebarCollapsed: false,
          selectedModelId: 'claude-3-opus',
        },
      }
      const result = validateSettings(data)
      expect(result.isValid).toBe(true)
      expect(result.data.selectedModelId).toBe('claude-3-opus')
    })

    it('should return invalid for null data', () => {
      const result = validateSettings(null)
      expect(result.isValid).toBe(false)
    })

    it('should return invalid for undefined data', () => {
      const result = validateSettings(undefined)
      expect(result.isValid).toBe(false)
    })

    it('should return invalid for missing settings object', () => {
      const data = {
        version: '2.0.0',
      }
      const result = validateSettings(data)
      expect(result.isValid).toBe(false)
    })
  })
})
