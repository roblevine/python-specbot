import { test, expect } from '@playwright/test'

/**
 * E2E tests for error display scenarios
 * Tests all three user stories with real browser interactions
 */
test.describe('Error Display Scenarios', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    // Clear localStorage before each test
    await page.evaluate(() => localStorage.clear())
    await page.reload()
  })

  // T062: Simulate network failure
  test('should display network failure error in chat', async ({ page }) => {
    // Intercept API call and simulate network failure
    await page.route('**/api/v1/messages', route => {
      route.abort('failed')
    })

    // Type and send message
    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Test message')
    const sendButton = page.locator('button:has-text("Send")')
    await sendButton.click()

    // Wait for error message to appear
    const errorMessage = page.locator('.message-error').first()
    await expect(errorMessage).toBeVisible()

    // Verify error section is displayed
    const errorSection = errorMessage.locator('.error-section')
    await expect(errorSection).toBeVisible()

    // Verify error icon is present
    const errorIcon = errorSection.locator('.error-icon')
    await expect(errorIcon).toBeVisible()
    await expect(errorIcon).toContainText('⚠')

    // Verify error message text
    const errorText = errorSection.locator('.error-message')
    await expect(errorText).toBeVisible()
    await expect(errorText).toContainText(/cannot connect|network|failed/i)
  })

  // T063: Stop backend scenario (simulated via timeout)
  test('should display "Cannot connect to server" error when backend is down', async ({ page }) => {
    // Simulate backend being down by timing out the request
    await page.route('**/api/v1/messages', route => {
      // Never resolve - simulate timeout
      setTimeout(() => route.abort('timedout'), 15000)
    })

    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Test message')
    await page.locator('button:has-text("Send")').click()

    // Wait for error message (should appear before timeout due to client timeout)
    const errorMessage = page.locator('.message-error').first()
    await expect(errorMessage).toBeVisible({ timeout: 15000 })

    const errorSection = errorMessage.locator('.error-section')
    const errorText = errorSection.locator('.error-message')
    await expect(errorText).toContainText(/timeout|connect/i)
  })

  // T064: 422 validation error
  test('should display 422 validation error in chat', async ({ page }) => {
    // Intercept API and return 422 validation error
    await page.route('**/api/v1/messages', route => {
      route.fulfill({
        status: 422,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Message validation failed',
          details: { field: 'message', reason: 'Message too short' }
        })
      })
    })

    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Hi')
    await page.locator('button:has-text("Send")').click()

    // Wait for error message
    const errorMessage = page.locator('.message-error').first()
    await expect(errorMessage).toBeVisible()

    const errorSection = errorMessage.locator('.error-section')
    const errorText = errorSection.locator('.error-message')
    await expect(errorText).toContainText(/validation failed/i)
  })

  // T065: Click Details button to expand error details
  test('should expand error details when Details button is clicked', async ({ page }) => {
    // Intercept API and return 500 server error with details
    await page.route('**/api/v1/messages', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Internal server error',
          details: {
            stack: 'Error at processMessage (server.js:42)',
            timestamp: new Date().toISOString()
          }
        })
      })
    })

    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Test message')
    await page.locator('button:has-text("Send")').click()

    // Wait for error message
    const errorMessage = page.locator('.message-error').first()
    await expect(errorMessage).toBeVisible()

    // Verify Details button is present
    const detailsButton = errorMessage.locator('.error-toggle')
    await expect(detailsButton).toBeVisible()
    await expect(detailsButton).toContainText('Details')

    // Initially, error details should not be visible
    const errorDetails = errorMessage.locator('.error-details')
    await expect(errorDetails).not.toBeVisible()

    // Click Details button
    await detailsButton.click()

    // Now error details should be visible
    await expect(errorDetails).toBeVisible()

    // Verify error details contain expected information
    await expect(errorDetails).toContainText('Server Error')
    await expect(errorDetails).toContainText('500')
    await expect(errorDetails).toContainText(/stack|error/i)

    // Button text should change to "Hide Details"
    await expect(detailsButton).toContainText('Hide Details')

    // Click again to collapse
    await detailsButton.click()

    // Error details should be hidden again
    await expect(errorDetails).not.toBeVisible()
    await expect(detailsButton).toContainText('Details')
  })

  // T066: Keyboard navigation (Enter/Space) works on Details button
  test('should expand error details with keyboard navigation', async ({ page }) => {
    // Intercept API and return error with details
    await page.route('**/api/v1/messages', route => {
      route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Bad request',
          details: { info: 'Invalid payload' }
        })
      })
    })

    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Test message')
    await page.locator('button:has-text("Send")').click()

    // Wait for error message
    const errorMessage = page.locator('.message-error').first()
    await expect(errorMessage).toBeVisible()

    const detailsButton = errorMessage.locator('.error-toggle')
    await expect(detailsButton).toBeVisible()

    // Focus the Details button
    await detailsButton.focus()

    // Press Enter key
    await page.keyboard.press('Enter')

    // Error details should now be visible
    const errorDetails = errorMessage.locator('.error-details')
    await expect(errorDetails).toBeVisible()

    // Press Enter again to collapse
    await page.keyboard.press('Enter')
    await expect(errorDetails).not.toBeVisible()

    // Focus again and try Space key
    await detailsButton.focus()
    await page.keyboard.press('Space')

    // Should expand again
    await expect(errorDetails).toBeVisible()
  })

  // T067: Verify sensitive data is redacted
  test('should redact sensitive data in error details', async ({ page }) => {
    // Intercept API and return error with sensitive data
    await page.route('**/api/v1/messages', route => {
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Authentication failed',
          details: {
            token: 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature',
            apiKey: 'AKIAIOSFODNN7EXAMPLE',
            message: 'Invalid credentials'
          }
        })
      })
    })

    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Test message')
    await page.locator('button:has-text("Send")').click()

    // Wait for error message
    const errorMessage = page.locator('.message-error').first()
    await expect(errorMessage).toBeVisible()

    // Click Details button to expand
    const detailsButton = errorMessage.locator('.error-toggle')
    await detailsButton.click()

    // Get error details content
    const errorDetails = errorMessage.locator('.error-details')
    await expect(errorDetails).toBeVisible()

    const detailsText = await errorDetails.textContent()

    // Verify sensitive data is NOT present in raw form
    expect(detailsText).not.toContain('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9')
    expect(detailsText).not.toContain('AKIAIOSFODNN7EXAMPLE')

    // Verify redacted placeholders ARE present
    expect(detailsText).toMatch(/REDACTED/i)
  })

  // Additional test: Multiple errors in succession
  test('should display multiple errors in chronological order', async ({ page }) => {
    // First error - network failure
    await page.route('**/api/v1/messages', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Server error 1' })
      })
    }, { times: 1 })

    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('First message')
    await page.locator('button:has-text("Send")').click()

    // Wait for first error
    await expect(page.locator('.message-error').first()).toBeVisible()

    // Second error - different error
    await page.route('**/api/v1/messages', route => {
      route.fulfill({
        status: 422,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Validation error' })
      })
    })

    await input.fill('Second message')
    await page.locator('button:has-text("Send")').click()

    // Should have 2 error messages
    const errorMessages = page.locator('.message-error')
    await expect(errorMessages).toHaveCount(2)

    // Verify first error still displays correctly
    await expect(errorMessages.nth(0)).toContainText('Server error 1')

    // Verify second error displays correctly
    await expect(errorMessages.nth(1)).toContainText('Validation error')
  })
})
