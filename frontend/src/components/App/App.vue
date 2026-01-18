<template>
  <div class="app">
    <!-- Feature 015: StatusBar simplified - status/statusType props removed -->
    <StatusBar
      :title="activeConversationTitle"
      @rename="handleRenameRequest()"
    />
    <div class="app-main">
      <HistoryBar
        :conversations="conversations"
        :active-conversation-id="activeConversationId"
        :is-collapsed="sidebarCollapsed"
        @select-conversation="handleSelectConversation"
        @new-conversation="handleNewConversation"
        @toggle-sidebar="toggleSidebar"
        @rename-conversation="handleRenameRequest"
      />
      <div class="chat-container">
        <ChatArea
          :messages="currentMessages"
          :is-processing="isProcessing"
        />
        <!-- Feature 015: ModelSelector moved to InputArea component -->
        <InputArea
          ref="inputAreaRef"
          :disabled="isProcessing"
          @send-message="handleSendMessage"
        />
      </div>
    </div>
    <RenameDialog
      v-if="showRenameDialog"
      :current-title="renamingTitle"
      @save="handleRenameSave"
      @cancel="handleRenameCancel"
    />
  </div>
</template>

<script>
import { onMounted, ref, computed } from 'vue'
import StatusBar from '../StatusBar/StatusBar.vue'
import HistoryBar from '../HistoryBar/HistoryBar.vue'
import ChatArea from '../ChatArea/ChatArea.vue'
import InputArea from '../InputArea/InputArea.vue'
// Feature 015: ModelSelector moved to InputArea component
import RenameDialog from '../RenameDialog/RenameDialog.vue'
import { useConversations } from '../../state/useConversations.js'
import { useMessages } from '../../state/useMessages.js'
import { useAppState } from '../../state/useAppState.js'
import { useSidebarCollapse } from '../../composables/useSidebarCollapse.js'
import * as logger from '../../utils/logger.js'

export default {
  name: 'App',
  components: {
    StatusBar,
    HistoryBar,
    ChatArea,
    InputArea,
    RenameDialog,
  },
  setup() {
    // Template refs
    const inputAreaRef = ref(null)

    // Get composables
    const {
      conversations,
      activeConversationId,
      activeConversation,
      createConversation,
      setActiveConversation,
      loadFromStorage,
      saveToStorage,
      renameConversation,
    } = useConversations()

    // Computed property for active conversation title
    const activeConversationTitle = computed(() => {
      return activeConversation.value?.title || 'New Conversation'
    })

    // Rename dialog state
    const showRenameDialog = ref(false)
    const renamingConversationId = ref(null)

    // Computed property for the title being renamed
    const renamingTitle = computed(() => {
      if (!renamingConversationId.value) return ''
      const conversation = conversations.value.find(c => c.id === renamingConversationId.value)
      return conversation?.title || ''
    })

    const { currentMessages, sendUserMessage } = useMessages()

    const { isProcessing, status, statusType, setStatus, setError } = useAppState()

    // Sidebar collapse state
    const { isCollapsed: sidebarCollapsed, toggle: toggleSidebar, loadFromStorage: loadSidebarState } =
      useSidebarCollapse()

    // Initialize app on mount
    onMounted(() => {
      try {
        logger.info('Initializing app...')
        loadFromStorage()
        loadSidebarState()
        setStatus('Ready', 'ready')
        logger.info('App initialized successfully')
      } catch (error) {
        logger.error('Failed to initialize app', error)
        setError('Failed to load data')
      }
    })

    // Handle sending a message
    async function handleSendMessage(text) {
      try {
        await sendUserMessage(text)
      } catch (error) {
        logger.error('Error sending message', error)
        setError('Failed to send message')
      }
    }

    // Handle selecting a conversation
    function handleSelectConversation(conversationId) {
      try {
        logger.info('Selecting conversation', { conversationId })
        setActiveConversation(conversationId)
        saveToStorage()
        logger.info('Conversation selected successfully', { conversationId })
      } catch (error) {
        logger.error('Failed to select conversation', error)
        setError('Failed to select conversation')
      }
    }

    // Handle creating a new conversation
    function handleNewConversation() {
      try {
        logger.info('Creating new conversation from button click')
        createConversation()
        saveToStorage()

        // Clear the input field when starting a new conversation
        if (inputAreaRef.value?.clearInput) {
          inputAreaRef.value.clearInput()
        }

        logger.info('New conversation created successfully')
      } catch (error) {
        logger.error('Failed to create new conversation', error)
        setError('Failed to create new conversation')
      }
    }

    // Handle rename request (from StatusBar or HistoryBar)
    function handleRenameRequest(conversationId = null) {
      renamingConversationId.value = conversationId || activeConversationId.value
      showRenameDialog.value = true
      logger.info('Opening rename dialog', { conversationId: renamingConversationId.value })
    }

    // Handle rename save
    async function handleRenameSave(newTitle) {
      try {
        await renameConversation(renamingConversationId.value, newTitle)
        showRenameDialog.value = false
        renamingConversationId.value = null
        logger.info('Conversation renamed successfully', { newTitle })
      } catch (error) {
        logger.error('Failed to rename conversation', error)
        setError('Failed to rename conversation')
      }
    }

    // Handle rename cancel
    function handleRenameCancel() {
      showRenameDialog.value = false
      renamingConversationId.value = null
    }

    return {
      inputAreaRef,
      conversations,
      activeConversationId,
      activeConversationTitle,
      currentMessages,
      isProcessing,
      // Feature 015: status and statusType removed from return - no longer needed in template
      sidebarCollapsed,
      showRenameDialog,
      renamingTitle,
      handleSendMessage,
      handleSelectConversation,
      handleNewConversation,
      handleRenameRequest,
      handleRenameSave,
      handleRenameCancel,
      toggleSidebar,
    }
  },
}
</script>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.app-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.chat-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}
</style>
