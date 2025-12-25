<template>
  <div class="app">
    <StatusBar :status="status" :status-type="statusType" />
    <div class="app-main">
      <HistoryBar
        :conversations="conversations"
        :active-conversation-id="activeConversationId"
        @select-conversation="handleSelectConversation"
        @new-conversation="handleNewConversation"
      />
      <div class="chat-container">
        <ChatArea :messages="currentMessages" :is-processing="isProcessing" />
        <InputArea :disabled="isProcessing" @send-message="handleSendMessage" />
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted } from 'vue'
import StatusBar from '../StatusBar/StatusBar.vue'
import HistoryBar from '../HistoryBar/HistoryBar.vue'
import ChatArea from '../ChatArea/ChatArea.vue'
import InputArea from '../InputArea/InputArea.vue'
import { useConversations } from '../../state/useConversations.js'
import { useMessages } from '../../state/useMessages.js'
import { useAppState } from '../../state/useAppState.js'
import * as logger from '../../utils/logger.js'

export default {
  name: 'App',
  components: {
    StatusBar,
    HistoryBar,
    ChatArea,
    InputArea,
  },
  setup() {
    // Get composables
    const {
      conversations,
      activeConversationId,
      createConversation,
      loadFromStorage,
      saveToStorage,
    } = useConversations()

    const { currentMessages, sendUserMessage } = useMessages()

    const { isProcessing, status, statusType, setStatus, setError } = useAppState()

    // Initialize app on mount
    onMounted(() => {
      try {
        logger.info('Initializing app...')
        loadFromStorage()
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
      logger.info('Conversation selected', { conversationId })
      // For P1, we only have one conversation so this is a no-op
      // P2 will implement switching between conversations
    }

    // Handle creating a new conversation
    function handleNewConversation() {
      try {
        logger.info('Creating new conversation from button click')
        createConversation()
        saveToStorage()
        logger.info('New conversation created successfully')
      } catch (error) {
        logger.error('Failed to create new conversation', error)
        setError('Failed to create new conversation')
      }
    }

    return {
      conversations,
      activeConversationId,
      currentMessages,
      isProcessing,
      status,
      statusType,
      handleSendMessage,
      handleSelectConversation,
      handleNewConversation,
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
