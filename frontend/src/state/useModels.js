/**
 * useModels Composable
 *
 * Manages model selection state for the application.
 * Handles fetching available models, persisting selection, and validation.
 *
 * Feature: 008-openai-model-selector User Story 1
 * Tasks: T027, T034, T035
 */

import { ref, watch, onMounted } from 'vue'
import { loadConversations, saveSelectedModel } from '../storage/LocalStorageAdapter.js'
import { fetchModels as apiFetchModels } from '../services/apiClient.js'

// Shared state across all component instances
const availableModels = ref([])
const selectedModelId = ref(null)
const isLoading = ref(false)
const error = ref(null)

/**
 * Composable for managing model selection state
 *
 * @returns {Object} Model state and methods
 */
export function useModels() {
  /**
   * Fetch available models from the backend
   * T027: Load models from GET /api/v1/models
   */
  async function fetchModels() {
    isLoading.value = true
    error.value = null

    try {
      const data = await apiFetchModels()

      if (!data.models || !Array.isArray(data.models)) {
        throw new Error('Invalid models response format')
      }

      if (data.models.length === 0) {
        throw new Error('No models configured on the server')
      }

      availableModels.value = data.models
      console.log(`Loaded ${data.models.length} models:`, data.models.map(m => m.id))

      return data.models
    } catch (err) {
      console.error('Failed to fetch models:', err)

      // T050: Provide user-friendly error messages
      let userMessage = 'Unable to load available models'

      if (err.message.includes('fetch') || err.message.includes('network')) {
        userMessage = 'Network error: Unable to connect to server'
      } else if (err.message.includes('503') || err.message.includes('Service unavailable')) {
        userMessage = 'Server configuration error: Models not available'
      } else if (err.message.includes('configured')) {
        userMessage = 'No models configured on the server'
      }

      error.value = userMessage
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Get the default model from available models
   * T027: Find model with default: true
   */
  function getDefaultModel() {
    const defaultModel = availableModels.value.find(m => m.default)
    return defaultModel || availableModels.value[0] || null
  }

  /**
   * Set the selected model
   * T027, T034: Update state and persist to localStorage
   */
  function setSelectedModel(modelId) {
    if (!modelId) {
      selectedModelId.value = null
      return
    }

    // Validate model exists
    const model = availableModels.value.find(m => m.id === modelId)
    if (!model) {
      console.warn(`Model ${modelId} not found in available models`)
      return
    }

    console.log(`Selected model: ${modelId}`)
    selectedModelId.value = modelId

    // T034: Persist to localStorage
    try {
      saveSelectedModel(modelId)
      console.log(`Persisted model selection: ${modelId}`)
    } catch (err) {
      console.error('Failed to persist model selection:', err)
    }
  }

  /**
   * Load selected model from localStorage
   * T034: Restore persisted selection on app load
   */
  function loadSelectedModelFromStorage() {
    try {
      const data = loadConversations()

      if (data.selectedModelId) {
        console.log(`Loaded selected model from storage: ${data.selectedModelId}`)
        return data.selectedModelId
      }

      return null
    } catch (err) {
      console.error('Failed to load selected model from storage:', err)
      return null
    }
  }

  /**
   * Initialize model selection
   * T027, T034, T035: Fetch models, restore selection, validate
   */
  async function initializeModels() {
    console.log('Initializing model selection...')

    try {
      // Fetch available models from backend
      const models = await fetchModels()

      if (models.length === 0) {
        throw new Error('No models available')
      }

      // T034: Load persisted selection from localStorage
      const storedModelId = loadSelectedModelFromStorage()

      // T035: Validate stored model exists in current configuration
      if (storedModelId) {
        const storedModel = models.find(m => m.id === storedModelId)

        if (storedModel) {
          console.log(`Using stored model: ${storedModelId}`)
          selectedModelId.value = storedModelId
        } else {
          console.warn(`Stored model ${storedModelId} not available, using default`)
          // Clear invalid selection
          saveSelectedModel(null)
          // Fall back to default
          const defaultModel = getDefaultModel()
          selectedModelId.value = defaultModel?.id || null
        }
      } else {
        // No stored selection, use default
        const defaultModel = getDefaultModel()
        selectedModelId.value = defaultModel?.id || null
        console.log(`Using default model: ${selectedModelId.value}`)
      }
    } catch (err) {
      console.error('Failed to initialize models:', err)
      // Error message already set by fetchModels
      // T050: Ensure error state is visible to user
      if (!error.value) {
        error.value = 'Unable to initialize model selection'
      }
    }
  }

  /**
   * Get the currently selected model object
   * T027: Return full model details
   */
  function getSelectedModel() {
    if (!selectedModelId.value) return null
    return availableModels.value.find(m => m.id === selectedModelId.value) || null
  }

  return {
    // State
    availableModels,
    selectedModelId,
    isLoading,
    error,

    // Methods
    fetchModels,
    getDefaultModel,
    setSelectedModel,
    getSelectedModel,
    initializeModels,
  }
}
