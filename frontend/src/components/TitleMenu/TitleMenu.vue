<template>
  <div class="title-menu">
    <button
      class="menu-trigger"
      aria-label="Conversation options"
      aria-haspopup="true"
      :aria-expanded="isOpen"
      @click.stop="toggleMenu"
    >
      <span class="ellipsis-icon">&#8943;</span>
    </button>
    <div
      v-if="isOpen"
      class="menu-dropdown"
      role="menu"
    >
      <button
        class="menu-item"
        role="menuitem"
        @click="handleRename"
      >
        Rename
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'TitleMenu',
  emits: ['rename'],
  setup(props, { emit }) {
    const isOpen = ref(false)

    function toggleMenu() {
      isOpen.value = !isOpen.value
    }

    function handleRename() {
      isOpen.value = false
      emit('rename')
    }

    function handleClickOutside(event) {
      if (!event.target.closest('.title-menu')) {
        isOpen.value = false
      }
    }

    function handleEscape(event) {
      if (event.key === 'Escape' && isOpen.value) {
        isOpen.value = false
      }
    }

    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
      document.addEventListener('keydown', handleEscape)
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
    })

    return {
      isOpen,
      toggleMenu,
      handleRename,
    }
  },
}
</script>

<style scoped>
.title-menu {
  position: relative;
  display: inline-flex;
}

.menu-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: background-color 0.2s, color 0.2s;
}

.menu-trigger:hover {
  background-color: rgba(0, 0, 0, 0.1);
  color: var(--color-text);
}

.menu-trigger:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.ellipsis-icon {
  font-size: 1.2rem;
  line-height: 1;
}

.menu-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 100;
  min-width: 120px;
  margin-top: var(--spacing-xs);
  padding: var(--spacing-xs);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.menu-item {
  display: block;
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  text-align: left;
  background: transparent;
  border: none;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-text);
  transition: background-color 0.2s;
}

.menu-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.menu-item:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
}
</style>
