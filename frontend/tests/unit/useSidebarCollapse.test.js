import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { useSidebarCollapse } from '../../src/composables/useSidebarCollapse.js'
import { SETTINGS_KEY } from '../../src/storage/SettingsSchema.js'

describe('useSidebarCollapse', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should initialize with collapsed state as false', () => {
    const { isCollapsed } = useSidebarCollapse()
    expect(isCollapsed.value).toBe(false)
  })

  it('should toggle collapsed state', () => {
    const { isCollapsed, toggle } = useSidebarCollapse()

    expect(isCollapsed.value).toBe(false)

    toggle()
    expect(isCollapsed.value).toBe(true)

    toggle()
    expect(isCollapsed.value).toBe(false)
  })

  it('should explicitly collapse sidebar', () => {
    const { isCollapsed, collapse } = useSidebarCollapse()

    expect(isCollapsed.value).toBe(false)

    collapse()
    expect(isCollapsed.value).toBe(true)

    // Calling collapse again should keep it collapsed
    collapse()
    expect(isCollapsed.value).toBe(true)
  })

  it('should explicitly expand sidebar', () => {
    const { isCollapsed, collapse, expand } = useSidebarCollapse()

    collapse()
    expect(isCollapsed.value).toBe(true)

    expand()
    expect(isCollapsed.value).toBe(false)

    // Calling expand again should keep it expanded
    expand()
    expect(isCollapsed.value).toBe(false)
  })

  // T018: Test loading from SettingsStorage
  describe('loadFromStorage (T018)', () => {
    it('should load collapsed state from SettingsStorage', () => {
      // Setup SettingsStorage data with collapsed = true
      const settingsData = {
        version: '2.0.0',
        settings: {
          sidebarCollapsed: true,
          selectedModelId: null,
        },
      }
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(settingsData))

      const { isCollapsed, loadFromStorage } = useSidebarCollapse()

      loadFromStorage()
      expect(isCollapsed.value).toBe(true)
    })

    it('should load expanded state from SettingsStorage', () => {
      const settingsData = {
        version: '2.0.0',
        settings: {
          sidebarCollapsed: false,
          selectedModelId: null,
        },
      }
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(settingsData))

      const { isCollapsed, loadFromStorage } = useSidebarCollapse()

      loadFromStorage()
      expect(isCollapsed.value).toBe(false)
    })

    it('should default to false if no settings exist', () => {
      const { isCollapsed, loadFromStorage } = useSidebarCollapse()

      loadFromStorage()
      expect(isCollapsed.value).toBe(false)
    })

    it('should default to false if settings data is corrupted', () => {
      localStorage.setItem(SETTINGS_KEY, 'invalid json')

      const { isCollapsed, loadFromStorage } = useSidebarCollapse()

      loadFromStorage()
      expect(isCollapsed.value).toBe(false)
    })

    it('should default to false if version mismatch', () => {
      const settingsData = {
        version: '1.0.0', // Wrong version
        settings: {
          sidebarCollapsed: true,
          selectedModelId: null,
        },
      }
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(settingsData))

      const { isCollapsed, loadFromStorage } = useSidebarCollapse()

      loadFromStorage()
      expect(isCollapsed.value).toBe(false)
    })
  })

  // T019: Test saving to SettingsStorage on change
  describe('save on change (T019)', () => {
    it('should save to SettingsStorage when state changes', async () => {
      const { toggle } = useSidebarCollapse()

      toggle()

      // Wait for Vue's watch to trigger
      await new Promise((resolve) => setTimeout(resolve, 10))

      const stored = localStorage.getItem(SETTINGS_KEY)
      const data = JSON.parse(stored)
      expect(data.settings.sidebarCollapsed).toBe(true)
    })

    it('should save false when expanded', async () => {
      const { collapse, expand } = useSidebarCollapse()

      collapse()
      await new Promise((resolve) => setTimeout(resolve, 10))

      let stored = localStorage.getItem(SETTINGS_KEY)
      let data = JSON.parse(stored)
      expect(data.settings.sidebarCollapsed).toBe(true)

      expand()
      await new Promise((resolve) => setTimeout(resolve, 10))

      stored = localStorage.getItem(SETTINGS_KEY)
      data = JSON.parse(stored)
      expect(data.settings.sidebarCollapsed).toBe(false)
    })

    it('should preserve other settings when saving', async () => {
      // Setup with an existing selectedModelId
      const settingsData = {
        version: '2.0.0',
        settings: {
          sidebarCollapsed: false,
          selectedModelId: 'gpt-4',
        },
      }
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(settingsData))

      const { collapse } = useSidebarCollapse()

      collapse()
      await new Promise((resolve) => setTimeout(resolve, 10))

      const stored = localStorage.getItem(SETTINGS_KEY)
      const data = JSON.parse(stored)
      expect(data.settings.sidebarCollapsed).toBe(true)
      expect(data.settings.selectedModelId).toBe('gpt-4') // Should be preserved
    })

    it('should handle localStorage errors gracefully when saving', async () => {
      const originalSetItem = localStorage.setItem
      localStorage.setItem = () => {
        throw new Error('localStorage quota exceeded')
      }

      const { toggle } = useSidebarCollapse()

      // Should not throw
      expect(() => toggle()).not.toThrow()

      // Wait for Vue's watch to trigger
      await new Promise((resolve) => setTimeout(resolve, 10))

      localStorage.setItem = originalSetItem
    })
  })
})
