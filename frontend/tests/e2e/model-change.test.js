import { test, expect } from '@playwright/test'

/**
 * E2E test for mid-conversation model changes
 * Feature: 008-openai-model-selector User Story 3
 * Task: T041
 */
test.describe('Model Change Mid-Conversation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    // Clear localStorage before each test
    await page.evaluate(() => localStorage.clear())
    await page.reload()

    // Wait for models to load
    await page.waitForSelector('.model-selector__select option[value!=""]', { timeout: 5000 })
  })

  test('T041: should change model mid-conversation and show correct indicators', async ({ page }) => {
    // Wait for the default model to be selected
    const modelSelector = page.locator('.model-selector__select')
    await expect(modelSelector).not.toBeDisabled()

    // Get the default model
    const defaultModel = await modelSelector.inputValue()

    // Send first message with default model
    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('First message')
    await page.locator('button:has-text("Send")').click()

    // Wait for system response
    await page.waitForSelector('[data-sender="system"]', { timeout: 5000 })

    // Verify first system message has model indicator with default model
    const firstSystemMessage = page.locator('[data-sender="system"]').first()
    const firstModelIndicator = firstSystemMessage.locator('.model-indicator')
    await expect(firstModelIndicator).toBeVisible()
    await expect(firstModelIndicator).toContainText(defaultModel)

    // Get available models
    const options = await modelSelector.locator('option[value!=""]').all()
    if (options.length < 2) {
      console.log('Skipping test: Not enough models available')
      return
    }

    // Find a different model to switch to
    const modelOptions = await page.locator('.model-selector__select option[value!=""]').allTextContents()
    let differentModel = null
    let differentModelValue = null

    for (const option of await page.locator('.model-selector__select option[value!=""]').all()) {
      const value = await option.getAttribute('value')
      if (value !== defaultModel) {
        differentModel = await option.textContent()
        differentModelValue = value
        break
      }
    }

    if (!differentModelValue) {
      console.log('Skipping test: No different model available')
      return
    }

    // Change model
    await modelSelector.selectOption(differentModelValue)

    // Send second message with new model
    await input.fill('Second message')
    await page.locator('button:has-text("Send")').click()

    // Wait for second system response
    await page.waitForSelector('[data-sender="system"]:nth-of-type(2)', { timeout: 5000 })

    // Verify second system message has model indicator with new model
    const secondSystemMessage = page.locator('[data-sender="system"]').nth(1)
    const secondModelIndicator = secondSystemMessage.locator('.model-indicator')
    await expect(secondModelIndicator).toBeVisible()
    await expect(secondModelIndicator).toContainText(differentModelValue)

    // Verify first message still shows original model
    await expect(firstModelIndicator).toContainText(defaultModel)
  })

  test('T041: should persist model selection across page reload', async ({ page }) => {
    // Select a specific model
    const modelSelector = page.locator('.model-selector__select')
    await expect(modelSelector).not.toBeDisabled()

    const options = await modelSelector.locator('option[value!=""]').all()
    if (options.length === 0) {
      console.log('Skipping test: No models available')
      return
    }

    // Select the first available model
    const firstModelValue = await options[0].getAttribute('value')
    await modelSelector.selectOption(firstModelValue)

    // Send a message
    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Test message')
    await page.locator('button:has-text("Send")').click()

    // Wait for response
    await page.waitForSelector('[data-sender="system"]', { timeout: 5000 })

    // Reload page
    await page.reload()

    // Wait for models to load again
    await page.waitForSelector('.model-selector__select option[value!=""]', { timeout: 5000 })

    // Verify model selection is restored
    const selectedValue = await modelSelector.inputValue()
    expect(selectedValue).toBe(firstModelValue)

    // Verify message history is preserved with model indicators
    const systemMessage = page.locator('[data-sender="system"]').first()
    const modelIndicator = systemMessage.locator('.model-indicator')
    await expect(modelIndicator).toBeVisible()
    await expect(modelIndicator).toContainText(firstModelValue)
  })

  test('T041: should immediately use new model for next message', async ({ page }) => {
    const modelSelector = page.locator('.model-selector__select')
    await expect(modelSelector).not.toBeDisabled()

    // Get available models
    const options = await modelSelector.locator('option[value!=""]').all()
    if (options.length < 2) {
      console.log('Skipping test: Not enough models available')
      return
    }

    // Select first model
    const firstModelValue = await options[0].getAttribute('value')
    await modelSelector.selectOption(firstModelValue)

    // Change to second model
    const secondModelValue = await options[1].getAttribute('value')
    await modelSelector.selectOption(secondModelValue)

    // Send message immediately after model change
    const input = page.locator('textarea, input[type="text"]').first()
    await input.fill('Message with new model')
    await page.locator('button:has-text("Send")').click()

    // Wait for response
    await page.waitForSelector('[data-sender="system"]', { timeout: 5000 })

    // Verify message uses the new model
    const systemMessage = page.locator('[data-sender="system"]').first()
    const modelIndicator = systemMessage.locator('.model-indicator')
    await expect(modelIndicator).toBeVisible()
    await expect(modelIndicator).toContainText(secondModelValue)
  })

  test('T041: should show different models for consecutive messages', async ({ page }) => {
    const modelSelector = page.locator('.model-selector__select')
    await expect(modelSelector).not.toBeDisabled()

    const options = await modelSelector.locator('option[value!=""]').all()
    if (options.length < 2) {
      console.log('Skipping test: Not enough models available')
      return
    }

    const input = page.locator('textarea, input[type="text"]').first()
    const sendButton = page.locator('button:has-text("Send")')

    // Send messages with alternating models
    for (let i = 0; i < Math.min(3, options.length); i++) {
      const modelValue = await options[i % options.length].getAttribute('value')
      await modelSelector.selectOption(modelValue)

      await input.fill(`Message ${i + 1}`)
      await sendButton.click()

      // Wait for response
      await page.waitForSelector(`[data-sender="system"]:nth-of-type(${i + 1})`, { timeout: 5000 })

      // Verify model indicator
      const systemMessage = page.locator('[data-sender="system"]').nth(i)
      const modelIndicator = systemMessage.locator('.model-indicator')
      await expect(modelIndicator).toContainText(modelValue)
    }
  })
})
