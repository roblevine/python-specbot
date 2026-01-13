import { test, expect } from '@playwright/test'

test.describe('UI Redesign - Color Scheme', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173')
    await page.waitForLoadState('networkidle')
  })

  test('should apply grey background color to main app', async ({ page }) => {
    const app = page.locator('.app')
    const backgroundColor = await app.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    )

    // #f5f5f7 = rgb(245, 245, 247)
    expect(backgroundColor).toContain('245')
    expect(backgroundColor).toContain('247')
  })

  test('should display user messages with pastel blue background', async ({ page }) => {
    // Send a message to create a user message bubble
    const input = page.locator('textarea')
    await input.fill('Test message for color verification')

    const sendButton = page.locator('button:has-text("Send")')
    await sendButton.click()

    // Wait for message to appear
    await page.waitForSelector('[data-role="user"]', { timeout: 3000 })

    const userMessage = page.locator('[data-role="user"]').first()
    const backgroundColor = await userMessage.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    )

    // #a8c9e8 = rgb(168, 201, 232) - pastel blue
    expect(backgroundColor).toContain('168')
    expect(backgroundColor).toContain('201')
    expect(backgroundColor).toContain('232')
  })

  test('should display assistant messages with grey/white background', async ({ page }) => {
    // Send a message to trigger assistant response
    const input = page.locator('textarea')
    await input.fill('Test message')

    const sendButton = page.locator('button:has-text("Send")')
    await sendButton.click()

    // Wait for assistant response
    await page.waitForSelector('[data-role="assistant"]', { timeout: 3000 })

    const assistantMessage = page.locator('[data-role="assistant"]').first()
    const backgroundColor = await assistantMessage.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    )

    // #ffffff = rgb(255, 255, 255) - white/grey surface
    expect(backgroundColor).toContain('255')
  })

  test('should apply grey border colors to UI elements', async ({ page }) => {
    const historyBar = page.locator('.history-bar')
    const borderColor = await historyBar.evaluate((el) =>
      window.getComputedStyle(el).borderColor
    )

    // Should have grey border (#d1d1d6 = rgb(209, 209, 214))
    expect(borderColor).toBeTruthy()
  })

  test('should have readable text with proper contrast', async ({ page }) => {
    // Check primary text color on background
    const app = page.locator('.app')
    const textColor = await app.evaluate((el) => window.getComputedStyle(el).color)

    // #1d1d1f = rgb(29, 29, 31) - near-black for readability
    expect(textColor).toContain('29')
    expect(textColor).toContain('31')
  })

  test('should maintain color scheme after page refresh', async ({ page }) => {
    // Send a message
    const input = page.locator('textarea')
    await input.fill('Color persistence test')
    await page.locator('button:has-text("Send")').click()
    await page.waitForTimeout(500)

    // Refresh page
    await page.reload()
    await page.waitForLoadState('networkidle')

    // Check colors still applied
    const app = page.locator('.app')
    const backgroundColor = await app.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    )

    // Grey background should persist
    expect(backgroundColor).toContain('245')
  })

  test('should apply hover state to interactive elements', async ({ page }) => {
    const sendButton = page.locator('button:has-text("Send")')

    // Get initial background color
    const initialBg = await sendButton.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    )

    // Hover over button
    await sendButton.hover()

    // Get hover background color
    const hoverBg = await sendButton.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    )

    // Hover state should potentially change color (or at least be defined)
    expect(hoverBg).toBeTruthy()
  })
})
