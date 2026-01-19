/**
 * Unit tests for CodeBlock component - Feature 017
 *
 * Tests cover:
 * - T019: Copy button visibility, clipboard API, success feedback
 * - Component rendering with code and language props
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import CodeBlock from '@/components/ChatArea/CodeBlock.vue'

describe('CodeBlock Component', () => {
  let originalClipboard

  beforeEach(() => {
    // Mock clipboard API
    originalClipboard = navigator.clipboard
    Object.defineProperty(navigator, 'clipboard', {
      value: {
        writeText: vi.fn().mockResolvedValue(undefined)
      },
      writable: true,
      configurable: true
    })
  })

  afterEach(() => {
    // Restore clipboard
    Object.defineProperty(navigator, 'clipboard', {
      value: originalClipboard,
      writable: true,
      configurable: true
    })
    vi.restoreAllMocks()
  })

  describe('Rendering', () => {
    it('should render code content', () => {
      const wrapper = mount(CodeBlock, {
        props: {
          code: 'const x = 1;',
          language: 'javascript'
        }
      })

      expect(wrapper.text()).toContain('const x = 1;')
    })

    it('should render without language prop', () => {
      const wrapper = mount(CodeBlock, {
        props: {
          code: 'some code'
        }
      })

      expect(wrapper.text()).toContain('some code')
    })

    it('should display language label when provided', () => {
      const wrapper = mount(CodeBlock, {
        props: {
          code: 'def hello(): pass',
          language: 'python'
        }
      })

      expect(wrapper.text()).toContain('python')
    })

    it('should have code-block class', () => {
      const wrapper = mount(CodeBlock, {
        props: {
          code: 'code'
        }
      })

      expect(wrapper.find('.code-block').exists()).toBe(true)
    })
  })

  describe('Copy Button', () => {
    it('should have a copy button', () => {
      const wrapper = mount(CodeBlock, {
        props: {
          code: 'const x = 1;'
        }
      })

      expect(wrapper.find('.copy-button').exists()).toBe(true)
    })

    it('should show "Copy" text initially', () => {
      const wrapper = mount(CodeBlock, {
        props: {
          code: 'const x = 1;'
        }
      })

      expect(wrapper.find('.copy-button').text()).toContain('Copy')
    })

    it('should call clipboard API when copy button is clicked', async () => {
      const wrapper = mount(CodeBlock, {
        props: {
          code: 'const x = 1;'
        }
      })

      await wrapper.find('.copy-button').trigger('click')

      expect(navigator.clipboard.writeText).toHaveBeenCalledWith('const x = 1;')
    })

    it('should show "Copied!" feedback after successful copy', async () => {
      const wrapper = mount(CodeBlock, {
        props: {
          code: 'const x = 1;'
        }
      })

      await wrapper.find('.copy-button').trigger('click')
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.copy-button').text()).toContain('Copied')
    })

    it('should revert to "Copy" after timeout', async () => {
      vi.useFakeTimers()

      const wrapper = mount(CodeBlock, {
        props: {
          code: 'const x = 1;'
        }
      })

      await wrapper.find('.copy-button').trigger('click')
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.copy-button').text()).toContain('Copied')

      // Fast-forward 2 seconds
      vi.advanceTimersByTime(2000)
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.copy-button').text()).toContain('Copy')

      vi.useRealTimers()
    })

    it('should handle clipboard API failure gracefully', async () => {
      navigator.clipboard.writeText = vi.fn().mockRejectedValue(new Error('Clipboard error'))

      const wrapper = mount(CodeBlock, {
        props: {
          code: 'const x = 1;'
        }
      })

      // Should not throw
      await wrapper.find('.copy-button').trigger('click')
      await wrapper.vm.$nextTick()

      // Button should still be functional
      expect(wrapper.find('.copy-button').exists()).toBe(true)
    })
  })

  describe('Hover State', () => {
    it('should have hover styles on code block container', () => {
      const wrapper = mount(CodeBlock, {
        props: {
          code: 'code'
        }
      })

      // Check that container has the class that will receive hover styles
      expect(wrapper.find('.code-block').exists()).toBe(true)
    })
  })

  describe('Accessibility', () => {
    it('should have accessible button', () => {
      const wrapper = mount(CodeBlock, {
        props: {
          code: 'const x = 1;'
        }
      })

      const button = wrapper.find('.copy-button')
      expect(button.attributes('type')).toBe('button')
    })
  })

  describe('Multi-line Code', () => {
    it('should preserve multi-line code formatting', () => {
      const multiLineCode = `function hello() {
  console.log('Hello');
  return true;
}`
      const wrapper = mount(CodeBlock, {
        props: {
          code: multiLineCode
        }
      })

      // The code should contain the line breaks
      expect(wrapper.text()).toContain('function hello')
      expect(wrapper.text()).toContain('console.log')
    })
  })

  describe('Special Characters', () => {
    it('should handle code with special characters', () => {
      const codeWithSpecial = '<script>alert("XSS")</script>'
      const wrapper = mount(CodeBlock, {
        props: {
          code: codeWithSpecial
        }
      })

      // Code should be displayed (escaped or as text)
      expect(wrapper.text()).toContain('script')
    })

    it('should copy exact code including special characters', async () => {
      const codeWithSpecial = '<div class="test">Content</div>'
      const wrapper = mount(CodeBlock, {
        props: {
          code: codeWithSpecial
        }
      })

      await wrapper.find('.copy-button').trigger('click')

      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(codeWithSpecial)
    })
  })
})
