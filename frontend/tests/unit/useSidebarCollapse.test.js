import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { useSidebarCollapse } from '../../src/composables/useSidebarCollapse.js'

describe('useSidebarCollapse', () => {
  let localStorageMock

  beforeEach(() => {
    // Mock localStorage
    localStorageMock = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    }
    global.localStorage = localStorageMock
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

  it('should load collapsed state from localStorage', () => {
    localStorageMock.getItem.mockReturnValue('true')

    const { isCollapsed, loadFromStorage } = useSidebarCollapse()

    loadFromStorage()
    expect(localStorageMock.getItem).toHaveBeenCalledWith('sidebar.collapsed')
    expect(isCollapsed.value).toBe(true)
  })

  it('should load expanded state from localStorage', () => {
    localStorageMock.getItem.mockReturnValue('false')

    const { isCollapsed, loadFromStorage } = useSidebarCollapse()

    loadFromStorage()
    expect(localStorageMock.getItem).toHaveBeenCalledWith('sidebar.collapsed')
    expect(isCollapsed.value).toBe(false)
  })

  it('should default to false if localStorage value is invalid', () => {
    localStorageMock.getItem.mockReturnValue('invalid')

    const { isCollapsed, loadFromStorage } = useSidebarCollapse()

    loadFromStorage()
    expect(isCollapsed.value).toBe(false)
  })

  it('should default to false if localStorage value is null', () => {
    localStorageMock.getItem.mockReturnValue(null)

    const { isCollapsed, loadFromStorage } = useSidebarCollapse()

    loadFromStorage()
    expect(isCollapsed.value).toBe(false)
  })

  it('should handle localStorage.getItem errors gracefully', () => {
    localStorageMock.getItem.mockImplementation(() => {
      throw new Error('localStorage unavailable')
    })

    const { isCollapsed, loadFromStorage } = useSidebarCollapse()

    // Should not throw
    expect(() => loadFromStorage()).not.toThrow()

    // Should default to false
    expect(isCollapsed.value).toBe(false)
  })

  it('should save to localStorage when state changes', async () => {
    const { toggle } = useSidebarCollapse()

    toggle()

    // Wait for Vue's watch to trigger
    await new Promise((resolve) => setTimeout(resolve, 10))

    expect(localStorageMock.setItem).toHaveBeenCalledWith('sidebar.collapsed', 'true')
  })

  it('should handle localStorage.setItem errors gracefully', async () => {
    localStorageMock.setItem.mockImplementation(() => {
      throw new Error('localStorage quota exceeded')
    })

    const { toggle } = useSidebarCollapse()

    // Should not throw
    expect(() => toggle()).not.toThrow()

    // Wait for Vue's watch to trigger
    await new Promise((resolve) => setTimeout(resolve, 10))

    // State should still change even if save fails
    // (user can still use sidebar, just won't persist)
  })

  it('should save "false" string when expanded', async () => {
    const { isCollapsed, collapse, expand } = useSidebarCollapse()

    collapse()
    await new Promise((resolve) => setTimeout(resolve, 10))
    expect(localStorageMock.setItem).toHaveBeenCalledWith('sidebar.collapsed', 'true')

    expand()
    await new Promise((resolve) => setTimeout(resolve, 10))
    expect(localStorageMock.setItem).toHaveBeenCalledWith('sidebar.collapsed', 'false')
  })
})
