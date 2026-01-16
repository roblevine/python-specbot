<template>
  <div class="model-selector" role="group" aria-label="AI Model Selection">
    <label for="model-select" class="model-selector__label">
      Model:
    </label>
    <select
      id="model-select"
      v-model="selectedModelId"
      class="model-selector__select"
      @change="handleModelChange"
      :disabled="isLoading || availableModels.length === 0"
      :aria-label="isLoading ? 'Loading available models' : 'Select AI model for conversation'"
      :aria-busy="isLoading"
      :aria-invalid="error ? 'true' : 'false'"
      :aria-describedby="error ? 'model-error' : undefined"
    >
      <option v-if="isLoading" value="">Loading models...</option>
      <option v-else-if="error" value="">Error loading models</option>
      <option
        v-else
        v-for="model in availableModels"
        :key="model.id"
        :value="model.id"
        class="model-selector__option"
        :aria-label="`${model.name}: ${model.description}`"
      >
        {{ model.name }} — {{ model.description }}
      </option>
    </select>
    <div
      v-if="error"
      id="model-error"
      class="model-selector__error"
      role="alert"
      aria-live="polite"
    >
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
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.model-selector__label {
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.model-selector__select {
  padding: 0.375rem 0.75rem;
  font-size: var(--font-size-xs);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  background-color: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  transition: border-color 0.2s;
  min-width: 200px;
  max-width: 400px;
}

.model-selector__select:hover:not(:disabled) {
  border-color: var(--color-primary);
}

.model-selector__select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(153, 126, 103, 0.25);
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
  font-size: var(--font-size-xs);
  color: var(--color-error);
}
</style>
