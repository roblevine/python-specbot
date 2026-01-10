import { describe, it, expect } from 'vitest'
import { useCollapsible } from '@/composables/useCollapsible'

describe('useCollapsible', () => {
  it('should initialize with collapsed state by default', () => {
    const { isExpanded } = useCollapsible()
    expect(isExpanded.value).toBe(false)
  })

  it('should initialize with expanded state when specified', () => {
    const { isExpanded } = useCollapsible(true)
    expect(isExpanded.value).toBe(true)
  })

  it('should toggle state', () => {
    const { isExpanded, toggle } = useCollapsible()

    expect(isExpanded.value).toBe(false)
    toggle()
    expect(isExpanded.value).toBe(true)
    toggle()
    expect(isExpanded.value).toBe(false)
  })

  it('should provide expand method', () => {
    const { isExpanded, expand } = useCollapsible()

    expect(isExpanded.value).toBe(false)
    expand()
    expect(isExpanded.value).toBe(true)
  })

  it('should provide collapse method', () => {
    const { isExpanded, collapse } = useCollapsible(true)

    expect(isExpanded.value).toBe(true)
    collapse()
    expect(isExpanded.value).toBe(false)
  })

  it('should provide correct ARIA attributes for trigger', () => {
    const { isExpanded, triggerAttrs, toggle } = useCollapsible()

    expect(triggerAttrs.value['aria-expanded']).toBe(false)
    expect(triggerAttrs.value['type']).toBe('button')
    expect(triggerAttrs.value['aria-controls']).toBeDefined()

    toggle()
    expect(triggerAttrs.value['aria-expanded']).toBe(true)
  })

  it('should provide correct ARIA attributes for content', () => {
    const { isExpanded, contentAttrs, toggle } = useCollapsible()

    expect(contentAttrs.value['role']).toBe('region')
    expect(contentAttrs.value['aria-hidden']).toBe(true)
    expect(contentAttrs.value['id']).toBeDefined()

    toggle()
    expect(contentAttrs.value['aria-hidden']).toBe(false)
  })
})
