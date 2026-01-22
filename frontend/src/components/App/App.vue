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
        @delete-conversation="handleDeleteConversation"
      />
      <div class="chat-container">
        <ChatArea
          :messages="currentMessages"
          :is-processing="isProcessing"
        />
        <!-- Feature 015: ModelSelector moved to InputArea component -->
        <!-- Feature 021: Pass model selector disabled state based on conversation messages -->
        <InputArea
          ref="inputAreaRef"
          :disabled="isProcessing"
          :model-selector-disabled="isModelSelectorDisabled"
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
import { onMounted, ref, computed, watch } from 'vue'
import StatusBar from '../StatusBar/StatusBar.vue'
import HistoryBar from '../HistoryBar/HistoryBar.vue'
import ChatArea from '../ChatArea/ChatArea.vue'
import InputArea from '../InputArea/InputArea.vue'
// Feature 015: ModelSelector moved to InputArea component
import RenameDialog from '../RenameDialog/RenameDialog.vue'
import DeleteConfirmationDialog from '../DeleteConfirmationDialog/DeleteConfirmationDialog.vue'
import { useConversations } from '../../state/useConversations.js'
import { useMessages } from '../../state/useMessages.js'
import { useAppState } from '../../state/useAppState.js'
import { useSidebarCollapse } from '../../composables/useSidebarCollapse.js'
// Feature 021: Import useModels for model restoration on conversation switch
import { useModels } from '../../state/useModels.js'
import * as logger from '../../utils/logger.js'

export default {
  name: 'App',
  components: {
    StatusBar,
    HistoryBar,
    ChatArea,
    InputArea,
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

    /**
     * Feature 021: Disable model selector when conversation has messages
     * This prevents model changes mid-conversation for consistency
     */
    const isModelSelectorDisabled = computed(() => {
      return activeConversation.value?.messages?.length > 0
    })

    /**
     * Feature 021: Get model selection composable for conversation model restoration
     */
    const { setSelectedModel, getDefaultModel, availableModels } = useModels()

    /**
     * Feature 021: Get the model ID from a conversation's first system message
     * @param {Object} conversation - Conversation object with messages array
     * @returns {string|null} - Model ID or null if not found
     */
    function getConversationModelId(conversation) {
      if (!conversation?.messages?.length) return null

      // Find the first system message that has a model field
      const firstSystemMessage = conversation.messages.find(
        msg => msg.sender === 'system' && msg.model
      )

      return firstSystemMessage?.model || null
    }

    /**
     * Feature 021: Check if a model ID is available in the current configuration
     * @param {string} modelId - Model ID to check
     * @returns {boolean} - True if model is available
     */
    function isModelAvailable(modelId) {
      if (!modelId) return false
      return availableModels.value.some(m => m.id === modelId)
    }

    /**
     * Feature 021: Watch activeConversation and restore model when switching conversations
     * This ensures the model selector shows the correct model for each conversation
     */
    watch(activeConversation, (newConversation) => {
      if (newConversation?.messages?.length > 0) {
        const modelId = getConversationModelId(newConversation)
        if (modelId && isModelAvailable(modelId)) {
          // Restore conversation's model without persisting to global storage
          setSelectedModel(modelId, false)
          logger.debug('Restored model from conversation', { modelId })
        } else if (modelId && !isModelAvailable(modelId)) {
          // Model was used but is no longer available - use default
          const defaultModel = getDefaultModel()
          if (defaultModel) {
            setSelectedModel(defaultModel.id, false)
            logger.warn('Conversation model no longer available, using default', {
              unavailableModel: modelId,
              usingModel: defaultModel.id
            })
          }
        } else {
          // Legacy conversation without model field - use default
          const defaultModel = getDefaultModel()
          if (defaultModel) {
            setSelectedModel(defaultModel.id, false)
            logger.debug('Using default model for legacy conversation', { modelId: defaultModel.id })
          }
        }
      }
    }, { immediate: true })

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
        // Feature 022: Restore focus to input after response completes
        inputAreaRef.value?.restoreFocus()
      } catch (error) {
        logger.error('Error sending message', error)
        setError('Failed to send message')
        // Feature 022: Also restore focus on error so user can retry
        inputAreaRef.value?.restoreFocus()
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
      // Feature 021: Model selector disabled state
      isModelSelectorDisabled,
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
