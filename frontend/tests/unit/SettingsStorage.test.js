import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  loadSettings,
  saveSetting,
  getSetting,
} from '../../src/storage/SettingsStorage.js'
import { SETTINGS_KEY, DEFAULT_SETTINGS } from '../../src/storage/SettingsSchema.js'

describe('SettingsStorage', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  describe('loadSettings', () => {
    it('should return default settings when no data exists', () => {
      const settings = loadSettings()
      expect(settings.sidebarCollapsed).toBe(false)
      expect(settings.selectedModelId).toBeNull()
    })

    it('should load persisted settings', () => {
      const storedData = {
        version: '2.0.0',
        settings: {
          sidebarCollapsed: true,
          selectedModelId: 'gpt-4',
        },
      }
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(storedData))

      const settings = loadSettings()
      expect(settings.sidebarCollapsed).toBe(true)
      expect(settings.selectedModelId).toBe('gpt-4')
    })

    it('should return defaults for corrupted JSON', () => {
      localStorage.setItem(SETTINGS_KEY, 'invalid json {{{')

      const settings = loadSettings()
      expect(settings.sidebarCollapsed).toBe(false)
      expect(settings.selectedModelId).toBeNull()
    })

    it('should return defaults for wrong version', () => {
      const storedData = {
        version: '1.0.0',
        settings: {
          sidebarCollapsed: true,
          selectedModelId: 'gpt-4',
        },
      }
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(storedData))

      const settings = loadSettings()
      expect(settings.sidebarCollapsed).toBe(false)
      expect(settings.selectedModelId).toBeNull()
    })

    it('should return defaults for invalid settings structure', () => {
      const storedData = {
        version: '2.0.0',
        settings: {
          sidebarCollapsed: 'not-a-boolean',
          selectedModelId: null,
        },
      }
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(storedData))

      const settings = loadSettings()
      expect(settings.sidebarCollapsed).toBe(false)
    })
  })

  describe('saveSetting', () => {
    it('should persist setting immediately', () => {
      saveSetting('sidebarCollapsed', true)

      const stored = localStorage.getItem(SETTINGS_KEY)
      const data = JSON.parse(stored)
      expect(data.settings.sidebarCollapsed).toBe(true)
    })

    it('should preserve other settings when saving one', () => {
      // First save one setting
      saveSetting('selectedModelId', 'gpt-4')

      // Then save another
      saveSetting('sidebarCollapsed', true)

      const stored = localStorage.getItem(SETTINGS_KEY)
      const data = JSON.parse(stored)
      expect(data.settings.selectedModelId).toBe('gpt-4')
      expect(data.settings.sidebarCollapsed).toBe(true)
    })

    it('should create new storage if none exists', () => {
      expect(localStorage.getItem(SETTINGS_KEY)).toBeNull()

      saveSetting('sidebarCollapsed', true)

      const stored = localStorage.getItem(SETTINGS_KEY)
      expect(stored).not.toBeNull()
      const data = JSON.parse(stored)
      expect(data.version).toBe('2.0.0')
    })

    it('should overwrite existing setting value', () => {
      saveSetting('selectedModelId', 'gpt-3.5')
      saveSetting('selectedModelId', 'gpt-4')

      const stored = localStorage.getItem(SETTINGS_KEY)
      const data = JSON.parse(stored)
      expect(data.settings.selectedModelId).toBe('gpt-4')
    })
  })

  describe('getSetting', () => {
    it('should return default value when no data exists', () => {
      const value = getSetting('sidebarCollapsed', false)
      expect(value).toBe(false)
    })

    it('should return stored value when data exists', () => {
      const storedData = {
        version: '2.0.0',
        settings: {
          sidebarCollapsed: true,
          selectedModelId: 'gpt-4',
        },
      }
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(storedData))

      const value = getSetting('sidebarCollapsed', false)
      expect(value).toBe(true)
    })

    it('should return default for unknown setting key', () => {
      const storedData = {
        version: '2.0.0',
        settings: {
          sidebarCollapsed: true,
          selectedModelId: 'gpt-4',
        },
      }
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(storedData))

      const value = getSetting('unknownKey', 'default')
      expect(value).toBe('default')
    })

    it('should return null default for unknown key if not specified', () => {
      const value = getSetting('nonExistentKey')
      expect(value).toBeNull()
    })

    it('should return DEFAULT_SETTINGS value for known key when no storage exists', () => {
      const value = getSetting('sidebarCollapsed')
      expect(value).toBe(false) // DEFAULT_SETTINGS.sidebarCollapsed is false
    })

    it('should return default for corrupted storage', () => {
      localStorage.setItem(SETTINGS_KEY, 'not valid json')

      const value = getSetting('sidebarCollapsed', false)
      expect(value).toBe(false)
    })
  })

  describe('localStorage unavailable', () => {
    it('should handle localStorage errors gracefully in saveSetting', () => {
      const originalSetItem = localStorage.setItem
      localStorage.setItem = () => {
        throw new Error('Storage quota exceeded')
      }

      // Should not throw
      expect(() => saveSetting('sidebarCollapsed', true)).not.toThrow()

      localStorage.setItem = originalSetItem
    })

    it('should return defaults when localStorage throws in loadSettings', () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = () => {
        throw new Error('Storage unavailable')
      }

      const settings = loadSettings()
      expect(settings.sidebarCollapsed).toBe(false)
      expect(settings.selectedModelId).toBeNull()

      localStorage.getItem = originalGetItem
    })
  })
})
