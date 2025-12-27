import { test, expect } from '@playwright/test'

/**
 * E2E test for New Conversation Button feature
 * Tests the complete user flow of starting a fresh conversation
 */
test.describe('New Conversation Button', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    // Clear localStorage before each test
    await page.evaluate(() => localStorage.clear())
    await page.reload()
  })

  test('user can start a new conversation', async ({ page }) => {
    // Send a message in first conversation
    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('First conversation message')
    await page.locator('button:has-text("Send")').click()

    // Wait for messages to appear (user + loopback)
    await page.waitForSelector('[data-sender="user"]')
    await page.waitForSelector('[data-sender="system"]')

    // Verify we have 2 messages (user + system)
    const messagesBeforeNewConv = page.locator('[data-message-id]')
    await expect(messagesBeforeNewConv).toHaveCount(2)

    // Click new conversation button
    const newConvButton = page.locator('button:has-text("New Conversation")')
    await newConvButton.click()

    // Wait for chat area to clear
    await page.waitForTimeout(200) // Small delay for state update

    // Verify chat area is now empty (new conversation has no messages)
    const messagesAfterNewConv = page.locator('[data-message-id]')
    await expect(messagesAfterNewConv).toHaveCount(0)

    // Verify previous conversation is in history (should have 2 conversations now)
    const conversationItems = page.locator('.conversation-item')
    await expect(conversationItems).toHaveCount(2)

    // Verify we can still send messages in new conversation
    await input.fill('New conversation message')
    await page.locator('button:has-text("Send")').click()

    // Verify new message appears
    const newMessage = page
      .locator('[data-sender="user"]')
      .filter({ hasText: 'New conversation message' })
    await expect(newMessage).toBeVisible()
  })

  test('unsaved message is discarded when starting new conversation', async ({ page }) => {
    // Type message but don't send
    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Unsaved message that will be lost')

    // Verify input has the unsaved text
    await expect(input).toHaveValue('Unsaved message that will be lost')

    // Click new conversation button
    const newConvButton = page.locator('button:has-text("New Conversation")')
    await newConvButton.click()

    // Wait for input to be cleared
    await expect(input).toHaveValue('', { timeout: 1000 })

    // Verify no messages in chat area (nothing was sent)
    const messages = page.locator('[data-message-id]')
    await expect(messages).toHaveCount(0)
  })

  test('rapid clicks are prevented by debounce', async ({ page }) => {
    // Send a message to create first conversation
    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Test message')
    await page.locator('button:has-text("Send")').click()

    // Wait for message to appear
    await page.waitForSelector('[data-sender="user"]')

    // Get initial conversation count (should be 1)
    const initialConvItems = page.locator('.conversation-item')
    const initialCount = await initialConvItems.count()
    expect(initialCount).toBe(1)

    // Click new conversation button 5 times rapidly
    const newConvButton = page.locator('button:has-text("New Conversation")')
    for (let i = 0; i < 5; i++) {
      await newConvButton.click({ delay: 50 })
    }

    // Wait for any async operations to complete
    await page.waitForTimeout(500)

    // Should have created fewer than 5 new conversations due to debounce
    // Exact count depends on timing, but should be < 5 and >= 1
    const finalConvItems = page.locator('.conversation-item')
    const finalCount = await finalConvItems.count()
    expect(finalCount).toBeGreaterThanOrEqual(1)
    expect(finalCount).toBeLessThan(6) // 1 initial + max 5 if no debounce
  })

  test('button is keyboard accessible', async ({ page }) => {
    // Send a message first to have a conversation
    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Test message')
    await page.locator('button:has-text("Send")').click()

    // Wait for message
    await page.waitForSelector('[data-sender="user"]')

    // Get initial conversation count
    const initialConvItems = page.locator('.conversation-item')
    const initialCount = await initialConvItems.count()

    // Focus on the new conversation button using Tab navigation
    const newConvButton = page.locator('button:has-text("New Conversation")')
    await newConvButton.focus()

    // Verify button is focused
    await expect(newConvButton).toBeFocused()

    // Press Enter to activate button
    await page.keyboard.press('Enter')

    // Wait for state update
    await page.waitForTimeout(200)

    // Verify new conversation was created
    const finalConvItems = page.locator('.conversation-item')
    const finalCount = await finalConvItems.count()
    expect(finalCount).toBe(initialCount + 1)

    // Verify chat area cleared
    const messages = page.locator('[data-message-id]')
    await expect(messages).toHaveCount(0)
  })

  test('button appears in correct location (top of history bar)', async ({ page }) => {
    // Verify button exists
    const newConvButton = page.locator('button:has-text("New Conversation")')
    await expect(newConvButton).toBeVisible()

    // Verify button is inside button container (below history header)
    const buttonContainer = page.locator('.button-container')
    await expect(buttonContainer).toBeVisible()
    const buttonInContainer = buttonContainer.locator('button:has-text("New Conversation")')
    await expect(buttonInContainer).toBeVisible()
  })

  // P2 Feature - Skipping for P1 MVP
  test.skip('previous conversations remain accessible after creating new one', async ({ page }) => {
    // This test requires conversation switching functionality (P2)
    // P1 only supports creating new conversations, not switching between them
  })

  test('button is always visible and enabled', async ({ page }) => {
    const newConvButton = page.locator('button:has-text("New Conversation")')

    // Verify button is visible initially
    await expect(newConvButton).toBeVisible()
    await expect(newConvButton).toBeEnabled()

    // Send a message
    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Test message')
    await page.locator('button:has-text("Send")').click()
    await page.waitForSelector('[data-sender="user"]')

    // Button should still be visible and enabled
    await expect(newConvButton).toBeVisible()
    await expect(newConvButton).toBeEnabled()

    // Create a new conversation
    await newConvButton.click()
    await page.waitForTimeout(200)

    // Button should still be visible and enabled
    await expect(newConvButton).toBeVisible()
    await expect(newConvButton).toBeEnabled()
  })
})
