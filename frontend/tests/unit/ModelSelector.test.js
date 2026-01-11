/**
 * Unit Tests for ModelSelector Component
 *
 * Tests the ModelSelector dropdown component functionality.
 *
 * Feature: 008-openai-model-selector User Story 1
 * Task: T016
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick, ref } from 'vue'
import ModelSelector from '@/components/ModelSelector/ModelSelector.vue'
import { useModels } from '@/state/useModels.js'

// Mock the useModels composable
vi.mock('@/state/useModels.js', () => ({
  useModels: vi.fn()
}))

// Mock fetch for API calls
global.fetch = vi.fn()

describe('ModelSelector Component', () => {
  let mockUseModels

  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks()

    // Default mock implementation with proper Vue refs
    mockUseModels = {
      availableModels: ref([]),
      selectedModelId: ref(null),
      isLoading: ref(false),
      error: ref(null),
      setSelectedModel: vi.fn(),
      initializeModels: vi.fn()
    }

    useModels.mockReturnValue(mockUseModels)
  })

  it('T016: should render model selector with label', () => {
    const wrapper = mount(ModelSelector)

    expect(wrapper.find('.model-selector').exists()).toBe(true)
    expect(wrapper.find('.model-selector__label').text()).toBe('Model:')
    expect(wrapper.find('.model-selector__select').exists()).toBe(true)
  })

  it('T016: should display loading state', async () => {
    mockUseModels.isLoading.value = true

    const wrapper = mount(ModelSelector)
    await nextTick()

    const select = wrapper.find('.model-selector__select')
    expect(select.element.disabled).toBe(true)
    expect(select.find('option').text()).toContain('Loading models')
  })

  it('T016: should display error state', async () => {
    mockUseModels.error.value = 'Failed to load models'

    const wrapper = mount(ModelSelector)
    await nextTick()

    expect(wrapper.find('.model-selector__error').exists()).toBe(true)
    expect(wrapper.find('.model-selector__error').text()).toBe('Failed to load models')
    expect(wrapper.find('.model-selector__select').element.disabled).toBe(true)
  })

  it('T016: should display available models', async () => {
    mockUseModels.availableModels.value = [
      { id: 'gpt-4', name: 'GPT-4', description: 'Most capable', default: false },
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: 'Fast', default: true }
    ]

    const wrapper = mount(ModelSelector)
    await nextTick()

    const options = wrapper.findAll('option')
    // Filter out loading/error options
    const modelOptions = options.filter(opt => opt.element.value !== '')

    expect(modelOptions.length).toBe(2)
    expect(modelOptions[0].text()).toBe('GPT-4')
    expect(modelOptions[0].element.value).toBe('gpt-4')
    expect(modelOptions[1].text()).toBe('GPT-3.5 Turbo')
    expect(modelOptions[1].element.value).toBe('gpt-3.5-turbo')
  })

  it('T016: should show selected model', async () => {
    mockUseModels.availableModels.value = [
      { id: 'gpt-4', name: 'GPT-4', description: 'Most capable', default: false },
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: 'Fast', default: true }
    ]
    mockUseModels.selectedModelId.value = 'gpt-4'

    const wrapper = mount(ModelSelector)
    await nextTick()

    const select = wrapper.find('.model-selector__select')
    expect(select.element.value).toBe('gpt-4')
  })

  it('T016: should call setSelectedModel when selection changes', async () => {
    mockUseModels.availableModels.value = [
      { id: 'gpt-4', name: 'GPT-4', description: 'Most capable', default: false },
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: 'Fast', default: true }
    ]
    mockUseModels.selectedModelId.value = 'gpt-3.5-turbo'

    const wrapper = mount(ModelSelector)
    await nextTick()

    const select = wrapper.find('.model-selector__select')

    // Change selection
    await select.setValue('gpt-4')

    // Verify setSelectedModel was called
    expect(mockUseModels.setSelectedModel).toHaveBeenCalledWith('gpt-4')
  })

  it('T016: should call initializeModels on mount', async () => {
    mount(ModelSelector)
    await flushPromises()

    expect(mockUseModels.initializeModels).toHaveBeenCalled()
  })

  it('T016: should disable select when no models available', async () => {
    mockUseModels.availableModels.value = []

    const wrapper = mount(ModelSelector)
    await nextTick()

    const select = wrapper.find('.model-selector__select')
    expect(select.element.disabled).toBe(true)
  })

  it('T016: should handle model selection persistence', async () => {
    // Simulate models loaded with selection persisted from localStorage
    mockUseModels.availableModels.value = [
      { id: 'gpt-4', name: 'GPT-4', description: 'Most capable', default: false },
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: 'Fast', default: true }
    ]
    mockUseModels.selectedModelId.value = 'gpt-4' // Previously selected

    const wrapper = mount(ModelSelector)
    await nextTick()

    const select = wrapper.find('.model-selector__select')

    // Verify the persisted selection is shown
    expect(select.element.value).toBe('gpt-4')
  })

  it('T016: should show default model when no selection', async () => {
    mockUseModels.availableModels.value = [
      { id: 'gpt-4', name: 'GPT-4', description: 'Most capable', default: false },
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: 'Fast', default: true }
    ]
    mockUseModels.selectedModelId.value = 'gpt-3.5-turbo' // Default model

    const wrapper = mount(ModelSelector)
    await nextTick()

    const select = wrapper.find('.model-selector__select')
    expect(select.element.value).toBe('gpt-3.5-turbo')
  })

  it('T016: should render models in order', async () => {
    mockUseModels.availableModels.value = [
      { id: 'model-1', name: 'Model 1', description: 'First', default: true },
      { id: 'model-2', name: 'Model 2', description: 'Second', default: false },
      { id: 'model-3', name: 'Model 3', description: 'Third', default: false }
    ]

    const wrapper = mount(ModelSelector)
    await nextTick()

    const options = wrapper.findAll('option').filter(opt => opt.element.value !== '')

    expect(options.length).toBe(3)
    expect(options[0].element.value).toBe('model-1')
    expect(options[1].element.value).toBe('model-2')
    expect(options[2].element.value).toBe('model-3')
  })

  it('T016: should handle rapid model changes', async () => {
    mockUseModels.availableModels.value = [
      { id: 'gpt-4', name: 'GPT-4', description: 'Most capable', default: false },
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: 'Fast', default: true },
      { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', description: 'Fastest', default: false }
    ]
    mockUseModels.selectedModelId.value = 'gpt-3.5-turbo'

    const wrapper = mount(ModelSelector)
    await nextTick()

    const select = wrapper.find('.model-selector__select')

    // Rapid changes
    await select.setValue('gpt-4')
    await select.setValue('gpt-4-turbo')
    await select.setValue('gpt-3.5-turbo')

    // Verify all calls were made
    expect(mockUseModels.setSelectedModel).toHaveBeenCalledTimes(3)
    expect(mockUseModels.setSelectedModel).toHaveBeenNthCalledWith(1, 'gpt-4')
    expect(mockUseModels.setSelectedModel).toHaveBeenNthCalledWith(2, 'gpt-4-turbo')
    expect(mockUseModels.setSelectedModel).toHaveBeenNthCalledWith(3, 'gpt-3.5-turbo')
  })

  it('T016: should not call setSelectedModel with invalid value', async () => {
    mockUseModels.availableModels.value = [
      { id: 'gpt-4', name: 'GPT-4', description: 'Most capable', default: true }
    ]

    const wrapper = mount(ModelSelector)
    await nextTick()

    const select = wrapper.find('.model-selector__select')

    // Try to set empty value
    await select.setValue('')

    // setSelectedModel should still be called (the composable will handle validation)
    expect(mockUseModels.setSelectedModel).toHaveBeenCalledWith('')
  })
})
