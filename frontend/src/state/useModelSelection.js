/**
 * Model Selection State Management
 *
 * Manages the user's LLM model selection with localStorage persistence.
 * Supports GPT-5 and GPT-5 Codex models.
 *
 * Feature: 005-llm-integration
 * Tasks: T010 (skeleton), T043 (validation)
 */

import { ref, watch } from 'vue'

const STORAGE_KEY = 'llm:modelSelection'
const DEFAULT_MODEL = 'gpt-5'
const AVAILABLE_MODELS = ['gpt-5', 'gpt-5-codex']

/**
 * Model selection composable.
 *
 * Provides reactive model selection with localStorage persistence.
 * Selection persists across browser sessions (FR-005).
 *
 * @returns {Object} Model selection state and methods
 */
export function useModelSelection() {
  const selectedModel = ref(loadModelSelection())

  /**
   * Load model selection from localStorage.
   *
   * @returns {string} Selected model or default
   */
  function loadModelSelection() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const data = JSON.parse(stored)
        // Validate model is in available list
        if (AVAILABLE_MODELS.includes(data.selectedModel)) {
          return data.selectedModel
        }
      }
    } catch (error) {
      console.error('Failed to load model selection:', error)
    }
    return DEFAULT_MODEL
  }

  /**
   * Save model selection to localStorage.
   *
   * @param {string} model - Model to save
   */
  function saveModelSelection(model) {
    if (!AVAILABLE_MODELS.includes(model)) {
      console.error(`Invalid model: ${model}. Must be one of: ${AVAILABLE_MODELS.join(', ')}`)
      return
    }

    selectedModel.value = model

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        selectedModel: model,
        lastUpdated: new Date().toISOString()
      }))
    } catch (error) {
      console.error('Failed to save model selection:', error)
    }
  }

  // Automatically persist changes
  watch(selectedModel, (newModel) => {
    if (AVAILABLE_MODELS.includes(newModel)) {
      saveModelSelection(newModel)
    }
  })

  return {
    selectedModel,
    setModel: saveModelSelection,
    availableModels: AVAILABLE_MODELS,
    defaultModel: DEFAULT_MODEL
  }
}
