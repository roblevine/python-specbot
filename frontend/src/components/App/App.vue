<template>
  <div class="app">
    <StatusBar
      :title="activeConversationTitle"
      :status="status"
      :status-type="statusType"
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
        @delete-conversation="handleDeleteConversation"
      />
      <div class="chat-container">
        <ChatArea
          :messages="currentMessages"
          :is-processing="isProcessing"
        />
        <ModelSelector />
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
    <DeleteConfirmationDialog
      v-if="showDeleteDialog"
      :conversation-title="deletingConversationTitle"
      @confirm="handleDeleteConfirm"
      @cancel="handleDeleteCancel"
    />
  </div>
</template>

<script>
import { onMounted, ref, computed } from 'vue'
import StatusBar from '../StatusBar/StatusBar.vue'
import HistoryBar from '../HistoryBar/HistoryBar.vue'
import ChatArea from '../ChatArea/ChatArea.vue'
import InputArea from '../InputArea/InputArea.vue'
import ModelSelector from '../ModelSelector/ModelSelector.vue'
import RenameDialog from '../RenameDialog/RenameDialog.vue'
import DeleteConfirmationDialog from '../DeleteConfirmationDialog/DeleteConfirmationDialog.vue'
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
    ModelSelector,
    RenameDialog,
    DeleteConfirmationDialog,
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
      deleteConversation,
    } = useConversations()

    // Computed property for active conversation title
    const activeConversationTitle = computed(() => {
      return activeConversation.value?.title || 'New Conversation'
    })

    // Rename dialog state
    const showRenameDialog = ref(false)
    const renamingConversationId = ref(null)

    // Delete dialog state
    const showDeleteDialog = ref(false)
    const deletingConversationId = ref(null)

    // Computed property for the title being renamed
    const renamingTitle = computed(() => {
      if (!renamingConversationId.value) return ''
      const conversation = conversations.value.find(c => c.id === renamingConversationId.value)
      return conversation?.title || ''
    })

    // Computed property for the title being deleted
    const deletingConversationTitle = computed(() => {
      if (!deletingConversationId.value) return ''
      const conversation = conversations.value.find(c => c.id === deletingConversationId.value)
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

    // Handle delete conversation request (shows confirmation dialog)
    function handleDeleteConversation(conversationId) {
      deletingConversationId.value = conversationId
      showDeleteDialog.value = true
      logger.info('Opening delete confirmation dialog', { conversationId })
    }

    // Handle delete confirmation
    async function handleDeleteConfirm() {
      const conversationId = deletingConversationId.value
      showDeleteDialog.value = false
      deletingConversationId.value = null

      try {
        logger.info('Deleting conversation', { conversationId })
        await deleteConversation(conversationId)
        logger.info('Conversation deleted successfully', { conversationId })
      } catch (error) {
        logger.error('Failed to delete conversation', error)
        setError('Failed to delete conversation')
      }
    }

    // Handle delete cancel
    function handleDeleteCancel() {
      showDeleteDialog.value = false
      deletingConversationId.value = null
      logger.info('Delete cancelled')
    }

    return {
      inputAreaRef,
      conversations,
      activeConversationId,
      activeConversationTitle,
      currentMessages,
      isProcessing,
      status,
      statusType,
      sidebarCollapsed,
      showRenameDialog,
      renamingTitle,
      handleSendMessage,
      handleSelectConversation,
      handleNewConversation,
      handleRenameRequest,
      handleRenameSave,
      handleRenameCancel,
      handleDeleteConversation,
      handleDeleteConfirm,
      handleDeleteCancel,
      showDeleteDialog,
      deletingConversationTitle,
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
