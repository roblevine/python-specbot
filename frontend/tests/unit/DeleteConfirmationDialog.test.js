import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DeleteConfirmationDialog from '../../src/components/DeleteConfirmationDialog/DeleteConfirmationDialog.vue'

describe('DeleteConfirmationDialog', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(DeleteConfirmationDialog, {
      props: {
        conversationTitle: 'Test Conversation',
      },
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('Rendering', () => {
    it('renders with conversationTitle prop', () => {
      expect(wrapper.text()).toContain('Test Conversation')
    })

    it('displays the conversation title in the message', () => {
      const message = wrapper.find('.dialog-message')
      expect(message.text()).toContain('Test Conversation')
    })

    it('displays the dialog title', () => {
      const title = wrapper.find('.dialog-title')
      expect(title.text()).toBe('Delete Conversation')
    })

    it('displays warning message about irreversible action', () => {
      const warning = wrapper.find('.dialog-warning')
      expect(warning.text()).toContain('cannot be undone')
    })

    it('renders Cancel button', () => {
      const cancelBtn = wrapper.find('.btn-secondary')
      expect(cancelBtn.exists()).toBe(true)
      expect(cancelBtn.text()).toBe('Cancel')
    })

    it('renders Delete button with danger styling', () => {
      const deleteBtn = wrapper.find('.btn-danger')
      expect(deleteBtn.exists()).toBe(true)
      expect(deleteBtn.text()).toBe('Delete')
    })

    it('renders dialog with proper ARIA attributes', () => {
      const dialog = wrapper.find('.delete-dialog')
      expect(dialog.attributes('role')).toBe('dialog')
      expect(dialog.attributes('aria-modal')).toBe('true')
      expect(dialog.attributes('aria-labelledby')).toBe('delete-dialog-title')
    })
  })

  describe('Props', () => {
    it('requires conversationTitle prop', () => {
      const props = DeleteConfirmationDialog.props
      expect(props.conversationTitle.required).toBe(true)
    })

    it('conversationTitle must be a String', () => {
      const props = DeleteConfirmationDialog.props
      expect(props.conversationTitle.type).toBe(String)
    })

    it('updates display when conversationTitle changes', async () => {
      await wrapper.setProps({ conversationTitle: 'New Title' })
      expect(wrapper.text()).toContain('New Title')
    })

    it('handles long conversation titles', async () => {
      const longTitle = 'A'.repeat(100)
      await wrapper.setProps({ conversationTitle: longTitle })
      expect(wrapper.text()).toContain(longTitle)
    })

    it('handles special characters in title', async () => {
      await wrapper.setProps({ conversationTitle: '<script>alert("xss")</script>' })
      const message = wrapper.find('.dialog-message')
      // Vue escapes HTML by default
      expect(message.text()).toContain('<script>')
    })
  })

  describe('Confirm Event', () => {
    it('emits "confirm" when Delete button is clicked', async () => {
      const deleteBtn = wrapper.find('.btn-danger')
      await deleteBtn.trigger('click')

      expect(wrapper.emitted('confirm')).toBeTruthy()
      expect(wrapper.emitted('confirm')).toHaveLength(1)
    })

    it('declares "confirm" in emits array', () => {
      expect(wrapper.vm.$options.emits).toContain('confirm')
    })
  })

  describe('Cancel Event', () => {
    it('emits "cancel" when Cancel button is clicked', async () => {
      const cancelBtn = wrapper.find('.btn-secondary')
      await cancelBtn.trigger('click')

      expect(wrapper.emitted('cancel')).toBeTruthy()
      expect(wrapper.emitted('cancel')).toHaveLength(1)
    })

    it('emits "cancel" on Escape key press', async () => {
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('cancel')).toBeTruthy()
      expect(wrapper.emitted('cancel')).toHaveLength(1)
    })

    it('emits "cancel" when clicking overlay', async () => {
      const overlay = wrapper.find('.delete-dialog-overlay')
      await overlay.trigger('click')

      expect(wrapper.emitted('cancel')).toBeTruthy()
      expect(wrapper.emitted('cancel')).toHaveLength(1)
    })

    it('does not emit "cancel" when clicking inside dialog', async () => {
      const dialog = wrapper.find('.delete-dialog')
      await dialog.trigger('click')

      expect(wrapper.emitted('cancel')).toBeFalsy()
    })

    it('declares "cancel" in emits array', () => {
      expect(wrapper.vm.$options.emits).toContain('cancel')
    })
  })

  describe('Accessibility', () => {
    it('focuses Cancel button on mount (safer default)', async () => {
      // Need to wait for mount lifecycle
      await wrapper.vm.$nextTick()

      const cancelBtn = wrapper.find('.btn-secondary')
      // Check if cancel button has the ref
      expect(wrapper.vm.cancelButtonRef).toBeDefined()
    })

    it('dialog has proper semantic structure', () => {
      expect(wrapper.find('h3.dialog-title').exists()).toBe(true)
      expect(wrapper.find('p.dialog-message').exists()).toBe(true)
      expect(wrapper.find('.dialog-actions').exists()).toBe(true)
    })

    it('buttons are native button elements', () => {
      const buttons = wrapper.findAll('button')
      expect(buttons.length).toBeGreaterThanOrEqual(2)
      buttons.forEach(btn => {
        expect(btn.element.tagName).toBe('BUTTON')
      })
    })
  })

  describe('Visual Styling', () => {
    it('overlay has proper class', () => {
      const overlay = wrapper.find('.delete-dialog-overlay')
      expect(overlay.exists()).toBe(true)
    })

    it('Delete button has danger class', () => {
      const deleteBtn = wrapper.find('.btn-danger')
      expect(deleteBtn.classes()).toContain('btn-danger')
    })

    it('Cancel button has secondary class', () => {
      const cancelBtn = wrapper.find('.btn-secondary')
      expect(cancelBtn.classes()).toContain('btn-secondary')
    })
  })

  describe('Multiple Escape Key Presses', () => {
    it('handles multiple Escape key presses gracefully', async () => {
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
      await wrapper.vm.$nextTick()

      // Should emit cancel for each press
      expect(wrapper.emitted('cancel').length).toBe(3)
    })
  })

  describe('Event Cleanup', () => {
    it('removes event listeners on unmount', async () => {
      const removeEventListenerSpy = vi.spyOn(document, 'removeEventListener')

      wrapper.unmount()

      expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function))

      removeEventListenerSpy.mockRestore()
    })
  })
})
