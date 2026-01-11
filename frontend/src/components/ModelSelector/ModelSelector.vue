<template>
  <div class="model-selector">
    <label for="model-select" class="model-selector__label">
      Model:
    </label>
    <select
      id="model-select"
      v-model="selectedModelId"
      class="model-selector__select"
      @change="handleModelChange"
      :disabled="isLoading || availableModels.length === 0"
    >
      <option v-if="isLoading" value="">Loading models...</option>
      <option v-else-if="error" value="">Error loading models</option>
      <option
        v-else
        v-for="model in availableModels"
        :key="model.id"
        :value="model.id"
        class="model-selector__option"
      >
        {{ model.name }} — {{ model.description }}
      </option>
    </select>
    <div v-if="error" class="model-selector__error">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
/**
 * ModelSelector Component
 *
 * Dropdown selector for choosing the OpenAI model to use for chat.
 * Fetches available models from backend and persists selection.
 *
 * Feature: 008-openai-model-selector User Story 1
 * Task: T028
 */

import { onMounted } from 'vue'
import { useModels } from '../../state/useModels.js'

// Get model state and methods from composable
const {
  availableModels,
  selectedModelId,
  isLoading,
  error,
  setSelectedModel,
  initializeModels,
} = useModels()

/**
 * Handle model selection change
 */
function handleModelChange(event) {
  const modelId = event.target.value
  console.log('Model selection changed:', modelId)
  setSelectedModel(modelId)
}

/**
 * Initialize models on component mount
 */
onMounted(async () => {
  console.log('ModelSelector mounted, initializing models...')
  await initializeModels()
})
</script>

<style scoped>
.model-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.model-selector__label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.model-selector__select {
  padding: 0.375rem 0.75rem;
  font-size: 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  cursor: pointer;
  transition: border-color 0.2s;
  min-width: 300px;
  max-width: 500px;
}

.model-selector__select:hover:not(:disabled) {
  border-color: var(--primary-color);
}

.model-selector__select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px var(--primary-shadow);
}

.model-selector__select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.model-selector__option {
  padding: 0.5rem;
  line-height: 1.5;
}

.model-selector__error {
  font-size: 0.85rem;
  color: var(--error-color);
}

/* Support for light/dark mode variables */
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --text-primary: #333333;
  --text-secondary: #666666;
  --border-color: #ddd;
  --primary-color: #007bff;
  --primary-shadow: rgba(0, 123, 255, 0.25);
  --error-color: #dc3545;
}
</style>
