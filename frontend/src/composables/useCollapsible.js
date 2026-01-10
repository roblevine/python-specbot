/**
 * useCollapsible - Composable for collapsible/expandable UI
 * Handles state, transitions, and accessibility
 */
import { ref, computed } from 'vue'

export function useCollapsible(initialExpanded = false) {
  const isExpanded = ref(initialExpanded)

  const toggle = () => {
    isExpanded.value = !isExpanded.value
  }

  const expand = () => {
    isExpanded.value = true
  }

  const collapse = () => {
    isExpanded.value = false
  }

  // ARIA attributes
  const triggerAttrs = computed(() => ({
    'aria-expanded': isExpanded.value,
    'aria-controls': 'collapsible-content',
    'type': 'button'
  }))

  const contentAttrs = computed(() => ({
    'id': 'collapsible-content',
    'role': 'region',
    'aria-hidden': !isExpanded.value
  }))

  return {
    isExpanded,
    toggle,
    expand,
    collapse,
    triggerAttrs,
    contentAttrs
  }
}
