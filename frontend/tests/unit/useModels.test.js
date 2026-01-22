/**
 * useModels Composable Tests
 * Feature: 021-disable-model-selector
 *
 * Tests for the setSelectedModel function with optional persist parameter
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock SettingsStorage before importing useModels
vi.mock('../../src/storage/SettingsStorage.js', () => ({
  getSetting: vi.fn(),
  saveSetting: vi.fn(),
}))

// Mock apiClient
vi.mock('../../src/services/apiClient.js', () => ({
  fetchModels: vi.fn().mockResolvedValue({
    models: [
      { id: 'gpt-4', name: 'GPT-4', description: 'Most capable', default: true },
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: 'Fast', default: false },
    ]
  }),
}))

import { useModels } from '../../src/state/useModels.js'
import { saveSetting } from '../../src/storage/SettingsStorage.js'

describe('useModels', () => {
  beforeEach(async () => {
    vi.clearAllMocks()

    // Initialize models
    const { initializeModels } = useModels()
    await initializeModels()
  })

  describe('setSelectedModel', () => {
    it('should persist model selection to storage by default', () => {
      const { setSelectedModel } = useModels()

      setSelectedModel('gpt-4')

      expect(saveSetting).toHaveBeenCalledWith('selectedModelId', 'gpt-4')
    })

    it('should persist model selection when persist=true', () => {
      const { setSelectedModel } = useModels()

      setSelectedModel('gpt-4', true)

      expect(saveSetting).toHaveBeenCalledWith('selectedModelId', 'gpt-4')
    })

    it('should NOT persist model selection when persist=false', () => {
      const { setSelectedModel, selectedModelId } = useModels()

      // Clear any previous calls
      vi.clearAllMocks()

      setSelectedModel('gpt-3.5-turbo', false)

      // Should update state
      expect(selectedModelId.value).toBe('gpt-3.5-turbo')

      // Should NOT call saveSetting
      expect(saveSetting).not.toHaveBeenCalled()
    })

    it('should update selectedModelId regardless of persist value', () => {
      const { setSelectedModel, selectedModelId } = useModels()

      // With persist=false
      setSelectedModel('gpt-3.5-turbo', false)
      expect(selectedModelId.value).toBe('gpt-3.5-turbo')

      // With persist=true
      setSelectedModel('gpt-4', true)
      expect(selectedModelId.value).toBe('gpt-4')
    })
  })
})
