<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-4">📱 Telegram Bot Integration</h1>
      <p class="text-gray-600">Connect to Telegram bot to receive real-time notifications about your scans.</p>
    </div>

    <!-- Bot Configuration -->
    <div class="bg-white shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Bot Configuration</h2>
      <div class="space-y-4">
        <div>
          <label for="botToken" class="block text-sm font-medium text-gray-700">Bot Token</label>
          <input
            id="botToken"
            v-model="botToken"
            type="password"
            placeholder="Enter your Telegram bot token"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          <p class="mt-1 text-sm text-gray-500">
            Get your bot token from <a href="https://t.me/botfather" target="_blank" class="text-blue-600 hover:text-blue-800">@BotFather</a>
          </p>
        </div>
        
        <div>
          <label for="chatId" class="block text-sm font-medium text-gray-700">Chat ID</label>
          <input
            id="chatId"
            v-model="chatId"
            type="text"
            placeholder="Enter your chat ID (optional - will be auto-detected)"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          <p class="mt-1 text-sm text-gray-500">
            Leave empty to auto-detect from bot messages
          </p>
        </div>

        <div class="flex justify-end">
          <button
            @click="saveBotConfig"
            :disabled="!botToken || isSaving"
            class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isSaving ? 'Saving...' : 'Save Configuration' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Connection Status -->
    <div class="bg-white shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Connection Status</h2>
      <div class="flex items-center space-x-3">
        <div 
          :class="{
            'bg-green-100 text-green-800': isConnected,
            'bg-red-100 text-red-800': !isConnected
          }"
          class="px-3 py-1 text-sm font-medium rounded-full"
        >
          {{ isConnected ? '🟢 Connected' : '🔴 Disconnected' }}
        </div>
        <button
          @click="testConnection"
          :disabled="!botToken || isTesting"
          class="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isTesting ? 'Testing...' : 'Test Connection' }}
        </button>
      </div>
      
      <div v-if="lastTestMessage" class="mt-4 p-3 bg-gray-50 rounded-lg">
        <p class="text-sm text-gray-700">{{ lastTestMessage }}</p>
      </div>
    </div>

    <!-- Notification Settings -->
    <div class="bg-white shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Notification Settings</h2>
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-medium text-gray-900">Scan Started</h3>
            <p class="text-sm text-gray-500">Notify when a new scan begins</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input 
              v-model="notifications.scanStarted" 
              type="checkbox" 
              class="sr-only peer"
            >
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>

        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-medium text-gray-900">Scan Completed</h3>
            <p class="text-sm text-gray-500">Notify when a scan finishes successfully</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input 
              v-model="notifications.scanCompleted" 
              type="checkbox" 
              class="sr-only peer"
            >
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>

        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-medium text-gray-900">Scan Failed</h3>
            <p class="text-sm text-gray-500">Notify when a scan encounters an error</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input 
              v-model="notifications.scanFailed" 
              type="checkbox" 
              class="sr-only peer"
            >
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>

        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-medium text-gray-900">Vulnerabilities Found</h3>
            <p class="text-sm text-gray-500">Notify when vulnerabilities are discovered</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input 
              v-model="notifications.vulnerabilitiesFound" 
              type="checkbox" 
              class="sr-only peer"
            >
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>

        <div class="flex justify-end">
          <button
            @click="saveNotificationSettings"
            :disabled="isSavingSettings"
            class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isSavingSettings ? 'Saving...' : 'Save Settings' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Recent Notifications -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-medium text-gray-900">Recent Notifications</h2>
        <button @click="loadNotifications" class="btn-secondary">Refresh</button>
      </div>
      
      <div v-if="recentNotifications.length === 0" class="text-center py-8">
        <p class="text-gray-500">No recent notifications. Start a scan to see notifications here.</p>
      </div>
      
      <div v-else class="space-y-3">
        <div
          v-for="notification in recentNotifications"
          :key="notification.id"
          class="border border-gray-200 rounded-lg p-4"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-2 mb-2">
                <span
                  :class="{
                    'bg-blue-100 text-blue-800': notification.type === 'scan_started',
                    'bg-green-100 text-green-800': notification.type === 'scan_completed',
                    'bg-red-100 text-red-800': notification.type === 'scan_failed',
                    'bg-yellow-100 text-yellow-800': notification.type === 'vulnerability_found'
                  }"
                  class="px-2 py-1 text-xs font-medium rounded-full"
                >
                  {{ getNotificationTypeLabel(notification.type) }}
                </span>
                <span class="text-sm text-gray-500">
                  {{ new Date(notification.timestamp).toLocaleString() }}
                </span>
              </div>
              <p class="text-gray-900">{{ notification.message }}</p>
              <p v-if="notification.target" class="text-sm text-gray-600 mt-1">
                Target: {{ notification.target }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'Telegram',
  setup() {
    const botToken = ref('')
    const chatId = ref('')
    const isConnected = ref(false)
    const isSaving = ref(false)
    const isTesting = ref(false)
    const isSavingSettings = ref(false)
    const lastTestMessage = ref('')
    const recentNotifications = ref([])
    
    const notifications = ref({
      scanStarted: true,
      scanCompleted: true,
      scanFailed: true,
      vulnerabilitiesFound: true
    })

    const loadConfig = async () => {
      try {
        const response = await axios.get('/api/v1/telegram/config')
        const config = response.data
        botToken.value = config.bot_token || ''
        chatId.value = config.chat_id || ''
        isConnected.value = config.is_connected || false
        notifications.value = {
          scanStarted: config.notifications?.scan_started ?? true,
          scanCompleted: config.notifications?.scan_completed ?? true,
          scanFailed: config.notifications?.scan_failed ?? true,
          vulnerabilitiesFound: config.notifications?.vulnerabilities_found ?? true
        }
      } catch (error) {
        console.error('Error loading Telegram config:', error)
      }
    }

    const saveBotConfig = async () => {
      isSaving.value = true
      try {
        await axios.post('/api/v1/telegram/config', {
          bot_token: botToken.value,
          chat_id: chatId.value
        })
        lastTestMessage.value = 'Configuration saved successfully!'
        await loadConfig()
      } catch (error) {
        console.error('Error saving bot config:', error)
        lastTestMessage.value = 'Error saving configuration: ' + (error.response?.data?.detail || error.message)
      } finally {
        isSaving.value = false
      }
    }

    const testConnection = async () => {
      isTesting.value = true
      try {
        const response = await axios.post('/api/v1/telegram/test')
        lastTestMessage.value = response.data.message || 'Test message sent successfully!'
        await loadConfig()
      } catch (error) {
        console.error('Error testing connection:', error)
        lastTestMessage.value = 'Error testing connection: ' + (error.response?.data?.detail || error.message)
      } finally {
        isTesting.value = false
      }
    }

    const saveNotificationSettings = async () => {
      isSavingSettings.value = true
      try {
        await axios.post('/api/v1/telegram/notifications', {
          scan_started: notifications.value.scanStarted,
          scan_completed: notifications.value.scanCompleted,
          scan_failed: notifications.value.scanFailed,
          vulnerabilities_found: notifications.value.vulnerabilitiesFound
        })
        lastTestMessage.value = 'Notification settings saved successfully!'
      } catch (error) {
        console.error('Error saving notification settings:', error)
        lastTestMessage.value = 'Error saving notification settings: ' + (error.response?.data?.detail || error.message)
      } finally {
        isSavingSettings.value = false
      }
    }

    const loadNotifications = async () => {
      try {
        const response = await axios.get('/api/v1/telegram/notifications')
        recentNotifications.value = response.data.notifications || []
      } catch (error) {
        console.error('Error loading notifications:', error)
      }
    }

    const getNotificationTypeLabel = (type) => {
      const labels = {
        scan_started: 'Scan Started',
        scan_completed: 'Scan Completed',
        scan_failed: 'Scan Failed',
        vulnerability_found: 'Vulnerability Found'
      }
      return labels[type] || type
    }

    onMounted(() => {
      loadConfig()
      loadNotifications()
    })

    return {
      botToken,
      chatId,
      isConnected,
      isSaving,
      isTesting,
      isSavingSettings,
      lastTestMessage,
      recentNotifications,
      notifications,
      saveBotConfig,
      testConnection,
      saveNotificationSettings,
      loadNotifications,
      getNotificationTypeLabel
    }
  }
}
</script> 