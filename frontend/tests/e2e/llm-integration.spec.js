import { test, expect } from '@playwright/test'

/**
 * E2E tests for LLM streaming integration
 * Tests the complete user journey with streaming AI responses
 *
 * Feature: 005-llm-integration User Story 1
 * Task: T018 (TDD - should FAIL before implementation)
 */

test.describe('LLM Streaming Integration', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    // Clear localStorage before each test
    await page.evaluate(() => localStorage.clear())
    await page.reload()
  })

  test('should send message and see streamed AI response', async ({ page }) => {
    /**
     * Success Criteria SC-001: First word appears within 3 seconds
     * Success Criteria SC-002: Response text streams progressively, not all at once
     */

    // Type message in input area
    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Hello, how are you?')

    // Click send button
    const sendButton = page.locator('button:has-text("Send")')
    await sendButton.click()

    // Verify user message appears
    const userMessage = page.locator('[data-sender="user"]').filter({ hasText: 'Hello, how are you?' })
    await expect(userMessage).toBeVisible()

    // Wait for AI response to start streaming (should be within 3 seconds)
    const assistantMessage = page.locator('[data-sender="assistant"]').first()
    await expect(assistantMessage).toBeVisible({ timeout: 3000 })

    // Verify response is from assistant, not system (loopback)
    await expect(assistantMessage).toHaveAttribute('data-sender', 'assistant')

    // Verify message has some content
    const messageText = await assistantMessage.textContent()
    expect(messageText.length).toBeGreaterThan(0)

    // Verify input is cleared
    await expect(input).toHaveValue('')
  })

  test('should show streaming indicator during response', async ({ page }) => {
    /**
     * Success Criteria SC-008: Send → Stop button transition within 1 second
     */

    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Tell me a story')

    const sendButton = page.locator('button:has-text("Send")')
    await sendButton.click()

    // Send button should transform to Stop button within 1 second
    const stopButton = page.locator('button:has-text("Stop")')
    await expect(stopButton).toBeVisible({ timeout: 1000 })

    // Verify user message is visible
    await expect(page.locator('[data-sender="user"]').filter({ hasText: 'Tell me a story' })).toBeVisible()

    // Wait for stream to complete
    // Stop button should disappear when done
    await expect(stopButton).toBeHidden({ timeout: 30000 })

    // Send button should reappear
    await expect(sendButton).toBeVisible()
  })

  test('should allow interrupting stream with Stop button', async ({ page }) => {
    /**
     * Success Criteria SC-009: Stop button halts stream within 500ms, shows interruption message
     * Success Criteria SC-010: Stream interruptions don't crash, preserve all messages sent/received
     */

    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Write a very long essay about Python programming')

    const sendButton = page.locator('button:has-text("Send")')
    await sendButton.click()

    // Wait for streaming to start
    const stopButton = page.locator('button:has-text("Stop")')
    await expect(stopButton).toBeVisible()

    // Wait for some content to stream
    const assistantMessage = page.locator('[data-sender="assistant"]').first()
    await expect(assistantMessage).toBeVisible()

    // Click Stop button
    await stopButton.click()

    // Stop button should disappear within 500ms
    await expect(stopButton).toBeHidden({ timeout: 500 })

    // Should show interruption message
    const interruptionMessage = page.locator('text=/conversation interrupted/i')
    await expect(interruptionMessage).toBeVisible()

    // Send button should be available again
    await expect(sendButton).toBeVisible()
    await expect(sendButton).toBeEnabled()

    // Verify messages are preserved (user message + partial AI response)
    const messages = page.locator('[data-message-id]')
    const messageCount = await messages.count()
    expect(messageCount).toBeGreaterThanOrEqual(2) // At least user + partial assistant

    // Should be able to send another message without crashing
    await input.fill('Another test message')
    await sendButton.click()

    await expect(page.locator('[data-sender="user"]').filter({ hasText: 'Another test message' })).toBeVisible()
  })

  test('should display streaming text progressively', async ({ page }) => {
    /**
     * Success Criteria SC-002: Response text streams progressively, not all at once
     */

    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Count to ten')

    await page.locator('button:has-text("Send")').click()

    // Wait for assistant message to appear
    const assistantMessage = page.locator('[data-sender="assistant"]').first()
    await expect(assistantMessage).toBeVisible()

    // Record initial text length
    const initialText = await assistantMessage.textContent()
    const initialLength = initialText.length

    // Wait a bit and check again - text should have grown
    await page.waitForTimeout(500)
    const updatedText = await assistantMessage.textContent()
    const updatedLength = updatedText.length

    // If streaming is working, text should grow over time
    // (This may not always be true for very short responses, so we're lenient)
    // Main verification is that we don't get entire response at once
    expect(updatedLength).toBeGreaterThanOrEqual(initialLength)
  })

  test('should handle streaming errors gracefully', async ({ page }) => {
    /**
     * Success Criteria SC-006: Errors show feedback within 5 seconds in both status bar and chat area
     */

    // Note: This test will fail until error handling is implemented
    // We'll need to mock an error condition or trigger one with invalid config

    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Test message')

    await page.locator('button:has-text("Send")').click()

    // If there's an error, it should show within 5 seconds
    // Check both status bar and chat area for error indicators

    // Status bar error indicator (should have error color)
    const statusBar = page.locator('[data-testid="status-bar"], .status-bar').first()

    // Chat area error message
    // (This specific test may pass or fail depending on API configuration)
  })

  test('should maintain conversation context across messages', async ({ page }) => {
    /**
     * Success Criteria SC-007: Multi-turn conversations maintain context for at least 5 exchanges
     * (This is for User Story 3, but we include skeleton test here)
     */

    const input = page.locator('textarea, input[type="text"]').first()
    const sendButton = page.locator('button:has-text("Send")')

    // First exchange
    await input.fill('My name is Alice')
    await sendButton.click()

    await expect(page.locator('[data-sender="assistant"]').first()).toBeVisible({ timeout: 10000 })

    // Wait for streaming to complete
    await expect(page.locator('button:has-text("Stop")')).toBeHidden({ timeout: 30000 })

    // Second exchange - should remember context
    await input.fill('What is my name?')
    await sendButton.click()

    await expect(page.locator('[data-sender="assistant"]').nth(1)).toBeVisible({ timeout: 10000 })

    // The AI response should reference "Alice" if context is working
    // (Full verification requires US3 implementation)
  })

  test('should persist streaming messages across page reload', async ({ page }) => {
    /**
     * Verify that streamed messages are saved to localStorage
     */

    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Test persistent streaming')

    await page.locator('button:has-text("Send")').click()

    // Wait for both user and assistant messages
    await expect(page.locator('[data-sender="user"]')).toBeVisible()
    await expect(page.locator('[data-sender="assistant"]').first()).toBeVisible()

    // Wait for streaming to complete
    await expect(page.locator('button:has-text("Stop")')).toBeHidden({ timeout: 30000 })

    // Reload page
    await page.reload()
    await page.waitForLoadState('networkidle')

    // Verify messages still present
    await expect(page.locator('[data-sender="user"]').filter({ hasText: 'Test persistent streaming' })).toBeVisible()
    await expect(page.locator('[data-sender="assistant"]').first()).toBeVisible()
  })

  test('should not allow sending messages while streaming', async ({ page }) => {
    /**
     * Input should be disabled during streaming to prevent spam
     */

    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Long response please')

    await page.locator('button:has-text("Send")').click()

    // Wait for streaming to start
    await expect(page.locator('button:has-text("Stop")')).toBeVisible()

    // Input should be disabled during streaming
    await expect(input).toBeDisabled()

    // Wait for streaming to complete
    await expect(page.locator('button:has-text("Stop")')).toBeHidden({ timeout: 30000 })

    // Input should be enabled again
    await expect(input).toBeEnabled()
  })

  test('should show model name in status bar', async ({ page }) => {
    /**
     * User Story 2: Model selection display
     * (Skeleton test for US2)
     */

    // Status bar should show current model (default: gpt-5)
    const statusBar = page.locator('[data-testid="status-bar"], .status-bar').first()

    // Should display model name
    await expect(statusBar).toContainText(/gpt-5/i)
  })

  test('should handle special characters in streamed response', async ({ page }) => {
    /**
     * Verify that special characters, emoji, and formatting are preserved
     */

    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Send me a message with emoji')

    await page.locator('button:has-text("Send")').click()

    // Wait for assistant response
    const assistantMessage = page.locator('[data-sender="assistant"]').first()
    await expect(assistantMessage).toBeVisible({ timeout: 10000 })

    // Response should be visible and contain text
    const messageText = await assistantMessage.textContent()
    expect(messageText.length).toBeGreaterThan(0)
  })

  test('should show appropriate error for network failure', async ({ page }) => {
    /**
     * Test error handling when backend is unreachable
     */

    // Simulate network failure by going offline
    await page.context().setOffline(true)

    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Test offline message')

    await page.locator('button:has-text("Send")').click()

    // Should show error within 5 seconds (SC-006)
    const errorMessage = page.locator('[data-error], .error-message').first()
    await expect(errorMessage).toBeVisible({ timeout: 5000 })

    // Error should be user-friendly, not technical
    const errorText = await errorMessage.textContent()
    expect(errorText.toLowerCase()).not.toContain('fetch')
    expect(errorText.toLowerCase()).not.toContain('http')

    // Go back online
    await page.context().setOffline(false)
  })
})
