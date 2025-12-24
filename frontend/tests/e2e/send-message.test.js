import { test, expect } from '@playwright/test'

/**
 * E2E test for complete message send and loopback workflow
 * Tests the entire user journey from typing to seeing loopback response
 */
test.describe('Send Message Loopback', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    // Clear localStorage before each test
    await page.evaluate(() => localStorage.clear())
    await page.reload()
  })

  test('should send message and see loopback response', async ({ page }) => {
    // Type message in input area
    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Hello world')

    // Click send button
    const sendButton = page.locator('button:has-text("Send")')
    await sendButton.click()

    // Verify user message appears
    const userMessage = page.locator('[data-sender="user"]').filter({ hasText: 'Hello world' })
    await expect(userMessage).toBeVisible()

    // Verify loopback response appears
    const systemMessage = page.locator('[data-sender="system"]').filter({ hasText: 'Hello world' })
    await expect(systemMessage).toBeVisible()

    // Verify input is cleared
    await expect(input).toHaveValue('')
  })

  test('should display messages in chronological order', async ({ page }) => {
    // Send first message
    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('First message')
    await page.locator('button:has-text("Send")').click()

    // Send second message
    await input.fill('Second message')
    await page.locator('button:has-text("Send")').click()

    // Verify order (should have 4 messages total: 2 user + 2 system)
    const messages = page.locator('[data-message-id]')
    await expect(messages).toHaveCount(4)

    // First should be "First message" from user
    const firstMsg = messages.nth(0)
    await expect(firstMsg).toContainText('First message')
    await expect(firstMsg).toHaveAttribute('data-sender', 'user')
  })

  test('should not send empty message', async ({ page }) => {
    const input = page.locator('textarea, input[type="text"]').first()
    const sendButton = page.locator('button:has-text("Send")')

    // Verify send button is disabled when input is empty
    await expect(sendButton).toBeDisabled()

    // Verify no messages appear
    const messages = page.locator('[data-message-id]')
    await expect(messages).toHaveCount(0)

    // Try whitespace-only
    await input.fill('   \n\t  ')

    // Send button should still be disabled for whitespace
    await expect(sendButton).toBeDisabled()

    // Still no messages
    await expect(messages).toHaveCount(0)
  })

  test('should persist messages across page reload', async ({ page }) => {
    // Send a message
    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Persistent message')
    await page.locator('button:has-text("Send")').click()

    // Wait for both messages to appear (user + system loopback)
    await page.waitForSelector('[data-sender="user"]')
    await page.waitForSelector('[data-sender="system"]')

    // Reload page
    await page.reload()

    // Wait for app to load and restore from storage
    await page.waitForLoadState('networkidle')

    // Verify messages still present
    const userMessage = page
      .locator('[data-sender="user"]')
      .filter({ hasText: 'Persistent message' })
    await expect(userMessage).toBeVisible()

    const systemMessage = page
      .locator('[data-sender="system"]')
      .filter({ hasText: 'Persistent message' })
    await expect(systemMessage).toBeVisible()
  })
})
