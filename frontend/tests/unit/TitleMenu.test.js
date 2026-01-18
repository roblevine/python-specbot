import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import TitleMenu from '../../src/components/TitleMenu/TitleMenu.vue'

describe('TitleMenu - Delete Functionality', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(TitleMenu)
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('Delete Option Rendering', () => {
    it('shows Delete option in the menu', async () => {
      // Open the menu
      await wrapper.find('.menu-trigger').trigger('click')

      const deleteButton = wrapper.find('.menu-item-danger')
      expect(deleteButton.exists()).toBe(true)
      expect(deleteButton.text()).toBe('Delete')
    })

    it('shows both Rename and Delete options', async () => {
      await wrapper.find('.menu-trigger').trigger('click')

      const menuItems = wrapper.findAll('.menu-item')
      expect(menuItems.length).toBe(2)

      const renameButton = menuItems.find(btn => btn.text() === 'Rename')
      const deleteButton = wrapper.find('.menu-item-danger')

      expect(renameButton.exists()).toBe(true)
      expect(deleteButton.exists()).toBe(true)
    })

    it('Delete option has danger styling class', async () => {
      await wrapper.find('.menu-trigger').trigger('click')

      const deleteButton = wrapper.find('.menu-item-danger')
      expect(deleteButton.classes()).toContain('menu-item-danger')
    })
  })

  describe('Delete Event Emission', () => {
    it('emits "delete" event when Delete is clicked', async () => {
      // Open the menu
      await wrapper.find('.menu-trigger').trigger('click')

      // Click Delete
      const deleteButton = wrapper.find('.menu-item-danger')
      await deleteButton.trigger('click')

      expect(wrapper.emitted('delete')).toBeTruthy()
      expect(wrapper.emitted('delete')).toHaveLength(1)
    })

    it('closes menu after Delete is clicked', async () => {
      // Open the menu
      await wrapper.find('.menu-trigger').trigger('click')
      expect(wrapper.find('.menu-dropdown').exists()).toBe(true)

      // Click Delete
      await wrapper.find('.menu-item-danger').trigger('click')

      // Menu should be closed
      expect(wrapper.find('.menu-dropdown').exists()).toBe(false)
    })

    it('declares "delete" in emits array', () => {
      expect(wrapper.vm.$options.emits).toContain('delete')
    })

    it('declares "rename" in emits array', () => {
      expect(wrapper.vm.$options.emits).toContain('rename')
    })
  })

  describe('Accessibility', () => {
    it('Delete button has menuitem role', async () => {
      await wrapper.find('.menu-trigger').trigger('click')

      const deleteButton = wrapper.find('.menu-item-danger')
      expect(deleteButton.attributes('role')).toBe('menuitem')
    })

    it('Delete button is focusable', async () => {
      await wrapper.find('.menu-trigger').trigger('click')

      const deleteButton = wrapper.find('.menu-item-danger')
      expect(deleteButton.element.tagName).toBe('BUTTON')
    })
  })

  describe('Menu Toggle Behavior', () => {
    it('opens menu on trigger click', async () => {
      expect(wrapper.find('.menu-dropdown').exists()).toBe(false)

      await wrapper.find('.menu-trigger').trigger('click')

      expect(wrapper.find('.menu-dropdown').exists()).toBe(true)
    })

    it('closes menu on second trigger click', async () => {
      await wrapper.find('.menu-trigger').trigger('click')
      expect(wrapper.find('.menu-dropdown').exists()).toBe(true)

      await wrapper.find('.menu-trigger').trigger('click')
      expect(wrapper.find('.menu-dropdown').exists()).toBe(false)
    })

    it('closes menu on Escape key', async () => {
      await wrapper.find('.menu-trigger').trigger('click')
      expect(wrapper.find('.menu-dropdown').exists()).toBe(true)

      // Simulate Escape key
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.menu-dropdown').exists()).toBe(false)
    })
  })

  describe('Rename Functionality (existing)', () => {
    it('emits "rename" event when Rename is clicked', async () => {
      await wrapper.find('.menu-trigger').trigger('click')

      const renameButton = wrapper.findAll('.menu-item').find(btn => btn.text() === 'Rename')
      await renameButton.trigger('click')

      expect(wrapper.emitted('rename')).toBeTruthy()
      expect(wrapper.emitted('rename')).toHaveLength(1)
    })

    it('closes menu after Rename is clicked', async () => {
      await wrapper.find('.menu-trigger').trigger('click')

      const renameButton = wrapper.findAll('.menu-item').find(btn => btn.text() === 'Rename')
      await renameButton.trigger('click')

      expect(wrapper.find('.menu-dropdown').exists()).toBe(false)
    })
  })
})
