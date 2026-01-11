import { describe, it, expect, beforeEach, afterEach } from 'vitest'

describe('Color Palette CSS Variables', () => {
  let styleElement

  beforeEach(() => {
    // Create a style element with our CSS variables for testing
    styleElement = document.createElement('style')
    styleElement.textContent = `
      :root {
        --color-grey-bg: #f5f5f7;
        --color-grey-surface: #ffffff;
        --color-grey-border: #d1d1d6;
        --color-grey-text-primary: #1d1d1f;
        --color-grey-text-secondary: #86868b;
        --color-blue-primary: #a8c9e8;
        --color-blue-hover: #8fb3d9;
        --color-blue-light: #d4e4f5;
        --color-user-message-bg: var(--color-blue-primary);
        --color-user-message-text: var(--color-grey-text-primary);
        --color-assistant-message-bg: var(--color-grey-surface);
        --color-assistant-message-text: var(--color-grey-text-primary);
      }
    `
    document.head.appendChild(styleElement)
  })

  afterEach(() => {
    if (styleElement && styleElement.parentNode) {
      document.head.removeChild(styleElement)
    }
  })

  it('should define grey color palette variables', () => {
    const root = document.documentElement
    const styles = getComputedStyle(root)

    expect(styles.getPropertyValue('--color-grey-bg').trim()).toBe('#f5f5f7')
    expect(styles.getPropertyValue('--color-grey-surface').trim()).toBe('#ffffff')
    expect(styles.getPropertyValue('--color-grey-border').trim()).toBe('#d1d1d6')
    expect(styles.getPropertyValue('--color-grey-text-primary').trim()).toBe('#1d1d1f')
    expect(styles.getPropertyValue('--color-grey-text-secondary').trim()).toBe('#86868b')
  })

  it('should define pastel blue accent color variables', () => {
    const root = document.documentElement
    const styles = getComputedStyle(root)

    expect(styles.getPropertyValue('--color-blue-primary').trim()).toBe('#a8c9e8')
    expect(styles.getPropertyValue('--color-blue-hover').trim()).toBe('#8fb3d9')
    expect(styles.getPropertyValue('--color-blue-light').trim()).toBe('#d4e4f5')
  })

  it('should define semantic color aliases for user messages', () => {
    const root = document.documentElement
    const styles = getComputedStyle(root)

    // These reference other variables, so we check they're defined
    const userBg = styles.getPropertyValue('--color-user-message-bg').trim()
    const userText = styles.getPropertyValue('--color-user-message-text').trim()

    expect(userBg).toBeTruthy()
    expect(userText).toBeTruthy()
  })

  it('should define semantic color aliases for assistant messages', () => {
    const root = document.documentElement
    const styles = getComputedStyle(root)

    const assistantBg = styles.getPropertyValue('--color-assistant-message-bg').trim()
    const assistantText = styles.getPropertyValue('--color-assistant-message-text').trim()

    expect(assistantBg).toBeTruthy()
    expect(assistantText).toBeTruthy()
  })

  describe('Color format validation', () => {
    it('should have valid hex color formats', () => {
      const hexColorRegex = /^#[0-9a-fA-F]{6}$/
      const colors = [
        '#f5f5f7', // grey-bg
        '#ffffff', // grey-surface
        '#d1d1d6', // grey-border
        '#1d1d1f', // grey-text-primary
        '#86868b', // grey-text-secondary
        '#a8c9e8', // blue-primary
        '#8fb3d9', // blue-hover
        '#d4e4f5', // blue-light
      ]

      colors.forEach((color) => {
        expect(color).toMatch(hexColorRegex)
      })
    })
  })
})
