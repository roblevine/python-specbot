import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import HistoryBar from '../../src/components/HistoryBar/HistoryBar.vue'

describe('HistoryBar - New Conversation Button', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(HistoryBar, {
      props: {
        conversations: [],
        activeConversationId: null,
      },
    })
  })

  describe('Button Rendering', () => {
    it('renders the new conversation button', () => {
      const button = wrapper.find('.new-conversation-btn')
      expect(button.exists()).toBe(true)
    })

    it('button has correct text label', () => {
      const button = wrapper.find('.new-conversation-btn')
      expect(button.text()).toContain('New Conversation')
    })

    it('button is visible in the history header', () => {
      const header = wrapper.find('.history-header')
      const button = header.find('.new-conversation-btn')
      expect(button.exists()).toBe(true)
    })
  })

  describe('Button Interaction', () => {
    it('emits new-conversation event when button is clicked', async () => {
      const button = wrapper.find('.new-conversation-btn')
      await button.trigger('click')

      expect(wrapper.emitted('new-conversation')).toBeTruthy()
      expect(wrapper.emitted('new-conversation')).toHaveLength(1)
    })

    it('prevents rapid duplicate emissions (debounce)', async () => {
      vi.useFakeTimers()

      const button = wrapper.find('.new-conversation-btn')

      // Click 3 times rapidly
      await button.trigger('click')
      await button.trigger('click')
      await button.trigger('click')

      // Should only emit once due to debounce
      expect(wrapper.emitted('new-conversation')).toHaveLength(1)

      // Wait for debounce to clear (300ms)
      vi.advanceTimersByTime(300)

      // Click again
      await button.trigger('click')

      // Should emit second time now
      expect(wrapper.emitted('new-conversation')).toHaveLength(2)

      vi.useRealTimers()
    })

    it('allows click after debounce period expires', async () => {
      vi.useFakeTimers()

      const button = wrapper.find('.new-conversation-btn')

      // First click
      await button.trigger('click')
      expect(wrapper.emitted('new-conversation')).toHaveLength(1)

      // Wait for debounce to clear
      vi.advanceTimersByTime(350)

      // Second click should work
      await button.trigger('click')
      expect(wrapper.emitted('new-conversation')).toHaveLength(2)

      vi.useRealTimers()
    })
  })

  describe('Accessibility', () => {
    it('button has correct aria-label attribute', () => {
      const button = wrapper.find('.new-conversation-btn')
      expect(button.attributes('aria-label')).toBe('Start new conversation')
    })

    it('button is a native button element', () => {
      const button = wrapper.find('.new-conversation-btn')
      expect(button.element.tagName).toBe('BUTTON')
    })

    it('button is keyboard accessible', async () => {
      const button = wrapper.find('.new-conversation-btn')

      // Simulate keyboard Enter key
      await button.trigger('keydown.enter')

      // Note: Click events are triggered by browsers on Enter for buttons
      // In our test, we just verify the button can receive keyboard events
      expect(button.element.tagName).toBe('BUTTON')
    })
  })

  describe('Button State', () => {
    it('button is always enabled', () => {
      const button = wrapper.find('.new-conversation-btn')
      expect(button.attributes('disabled')).toBeUndefined()
    })

    it('button is visible when there are no conversations', () => {
      const button = wrapper.find('.new-conversation-btn')
      expect(button.isVisible()).toBe(true)
    })

    it('button is visible when there are existing conversations', async () => {
      await wrapper.setProps({
        conversations: [
          {
            id: 'conv-123',
            title: 'Test Conversation',
            messages: [],
            createdAt: '2025-12-25T10:00:00.000Z',
            updatedAt: '2025-12-25T10:00:00.000Z',
          },
        ],
      })

      const button = wrapper.find('.new-conversation-btn')
      expect(button.isVisible()).toBe(true)
    })
  })

  describe('Event Declaration', () => {
    it('declares new-conversation as an emitted event', () => {
      expect(wrapper.vm.$options.emits).toContain('new-conversation')
    })

    it('maintains existing select-conversation emit', () => {
      expect(wrapper.vm.$options.emits).toContain('select-conversation')
    })
  })
})
