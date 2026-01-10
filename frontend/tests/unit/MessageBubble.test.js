import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MessageBubble from '@/components/ChatArea/MessageBubble.vue'

describe('MessageBubble - Error Display', () => {
  it('should display error section when message status is error', () => {
    const errorMessage = {
      id: 'msg-1',
      text: 'Failed message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'error',
      errorMessage: 'Message failed to send',
      errorType: 'Network Error'
    }

    const wrapper = mount(MessageBubble, {
      props: { message: errorMessage }
    })

    expect(wrapper.find('.error-section').exists()).toBe(true)
    expect(wrapper.find('.error-message').text()).toBe('Message failed to send')
  })

  it('should apply error styling to error messages', () => {
    const errorMessage = {
      id: 'msg-1',
      text: 'Failed message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'error',
      errorMessage: 'Network error'
    }

    const wrapper = mount(MessageBubble, {
      props: { message: errorMessage }
    })

    expect(wrapper.classes()).toContain('message-error')
  })

  it('should not display error section for non-error messages', () => {
    const normalMessage = {
      id: 'msg-1',
      text: 'Normal message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'sent'
    }

    const wrapper = mount(MessageBubble, {
      props: { message: normalMessage }
    })

    expect(wrapper.find('.error-section').exists()).toBe(false)
  })

  it('should render error icon when error is present', () => {
    const errorMessage = {
      id: 'msg-1',
      text: 'Failed message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'error',
      errorMessage: 'Message failed to send'
    }

    const wrapper = mount(MessageBubble, {
      props: { message: errorMessage }
    })

    expect(wrapper.find('.error-icon').exists()).toBe(true)
  })

  it('should display error type if provided', () => {
    const errorMessage = {
      id: 'msg-1',
      text: 'Failed message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'error',
      errorMessage: 'Connection failed',
      errorType: 'Network Error'
    }

    const wrapper = mount(MessageBubble, {
      props: { message: errorMessage }
    })

    const errorSection = wrapper.find('.error-section')
    expect(errorSection.exists()).toBe(true)
  })

  // T041: Renders Details button when errorDetails present
  it('should render Details button when errorDetails are present', () => {
    const errorMessage = {
      id: 'msg-1',
      text: 'Failed message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'error',
      errorMessage: 'API Error',
      errorType: 'Server Error',
      errorCode: 500,
      errorDetails: JSON.stringify({ stack: 'Error at line 42', endpoint: '/api/v1/messages' })
    }

    const wrapper = mount(MessageBubble, {
      props: { message: errorMessage }
    })

    expect(wrapper.find('.error-toggle').exists()).toBe(true)
    expect(wrapper.find('.error-toggle').text()).toContain('Details')
  })

  // T041: Should NOT render Details button when errorDetails absent
  it('should not render Details button when errorDetails are absent', () => {
    const errorMessage = {
      id: 'msg-1',
      text: 'Failed message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'error',
      errorMessage: 'Network error'
    }

    const wrapper = mount(MessageBubble, {
      props: { message: errorMessage }
    })

    expect(wrapper.find('.error-toggle').exists()).toBe(false)
  })

  // T042: Clicking Details button expands error details section
  it('should expand error details when Details button is clicked', async () => {
    const errorMessage = {
      id: 'msg-1',
      text: 'Failed message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'error',
      errorMessage: 'API Error',
      errorDetails: JSON.stringify({ stack: 'Error stack trace' })
    }

    const wrapper = mount(MessageBubble, {
      props: { message: errorMessage }
    })

    // Initially collapsed
    expect(wrapper.find('.error-details').exists()).toBe(false)

    // Click to expand
    await wrapper.find('.error-toggle').trigger('click')

    // Now expanded
    expect(wrapper.find('.error-details').exists()).toBe(true)
  })

  // T043: Clicking Details button again collapses error details
  it('should collapse error details when Details button is clicked again', async () => {
    const errorMessage = {
      id: 'msg-1',
      text: 'Failed message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'error',
      errorMessage: 'API Error',
      errorDetails: JSON.stringify({ stack: 'Error stack trace' })
    }

    const wrapper = mount(MessageBubble, {
      props: { message: errorMessage }
    })

    // Expand
    await wrapper.find('.error-toggle').trigger('click')
    expect(wrapper.find('.error-details').exists()).toBe(true)

    // Collapse
    await wrapper.find('.error-toggle').trigger('click')
    expect(wrapper.find('.error-details').exists()).toBe(false)
  })

  // T044: Expanded error details display errorType, errorCode, redacted errorDetails
  it('should display errorType, errorCode, and redacted errorDetails when expanded', async () => {
    const errorMessage = {
      id: 'msg-1',
      text: 'Failed message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'error',
      errorMessage: 'Validation failed',
      errorType: 'Validation Error',
      errorCode: 422,
      errorDetails: JSON.stringify({ field: 'message', reason: 'Too short' })
    }

    const wrapper = mount(MessageBubble, {
      props: { message: errorMessage }
    })

    await wrapper.find('.error-toggle').trigger('click')

    const detailsSection = wrapper.find('.error-details')
    expect(detailsSection.exists()).toBe(true)
    expect(detailsSection.text()).toContain('Validation Error')
    expect(detailsSection.text()).toContain('422')
    expect(detailsSection.text()).toContain('field')
  })

  // T045: Error details are redacted by default (sensitive data hidden)
  it('should redact sensitive data in error details by default', async () => {
    const errorMessage = {
      id: 'msg-1',
      text: 'Failed message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'error',
      errorMessage: 'Auth failed',
      errorDetails: JSON.stringify({
        token: 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature',
        apiKey: 'AKIAIOSFODNN7EXAMPLE'
      })
    }

    const wrapper = mount(MessageBubble, {
      props: { message: errorMessage }
    })

    await wrapper.find('.error-toggle').trigger('click')

    const detailsSection = wrapper.find('.error-details')

    // Should NOT contain original sensitive data
    expect(detailsSection.text()).not.toContain('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9')
    expect(detailsSection.text()).not.toContain('AKIAIOSFODNN7EXAMPLE')

    // Should contain redacted placeholders
    expect(detailsSection.text()).toContain('REDACTED')
  })

  // T046: Keyboard navigation (Enter/Space) works on Details button
  it('should expand error details with Enter key', async () => {
    const errorMessage = {
      id: 'msg-1',
      text: 'Failed message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'error',
      errorMessage: 'API Error',
      errorDetails: JSON.stringify({ stack: 'Error stack trace' })
    }

    const wrapper = mount(MessageBubble, {
      props: { message: errorMessage }
    })

    expect(wrapper.find('.error-details').exists()).toBe(false)

    // Press Enter key
    await wrapper.find('.error-toggle').trigger('keydown', { key: 'Enter' })
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.error-details').exists()).toBe(true)
  })

  it('should expand error details with Space key', async () => {
    const errorMessage = {
      id: 'msg-1',
      text: 'Failed message',
      sender: 'user',
      timestamp: new Date().toISOString(),
      status: 'error',
      errorMessage: 'API Error',
      errorDetails: JSON.stringify({ stack: 'Error stack trace' })
    }

    const wrapper = mount(MessageBubble, {
      props: { message: errorMessage }
    })

    expect(wrapper.find('.error-details').exists()).toBe(false)

    // Press Space key
    await wrapper.find('.error-toggle').trigger('keydown', { key: ' ' })
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.error-details').exists()).toBe(true)
  })
})
