<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-4">OSINT Gathering</h1>
      <p class="text-gray-600">Collect open source intelligence about your target.</p>
    </div>

    <!-- Target Input & Tool Selector -->
    <div class="bg-white shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">New OSINT Scan</h2>
      <div class="space-y-4">
        <div>
          <label for="target" class="block text-sm font-medium text-gray-700">Target Domain</label>
          <input
            id="target"
            v-model="target"
            type="text"
            placeholder="example.com"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
        <ToolSelector
          title="Select OSINT Tools"
          :tools="osintTools"
          v-model="selectedTools"
        />
        <div class="flex justify-end">
          <button
            @click="startScan"
            :disabled="!target || isScanning || selectedTools.length === 0"
            class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isScanning ? 'Scanning...' : 'Start OSINT Scan' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Scan History -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-medium text-gray-900">Scan History</h2>
        <button @click="loadTasks" class="btn-secondary">Refresh</button>
      </div>
      
      <div v-if="allTasks.length === 0" class="text-center py-8">
        <p class="text-gray-500">No OSINT scans found. Start a new scan above.</p>
      </div>
      
      <div v-else class="space-y-4">
        <div
          v-for="task in allTasks"
          :key="task.task_id"
          class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center justify-between mb-3">
            <div class="flex-1">
              <h3 class="font-medium text-gray-900">{{ task.target }}</h3>
              <p class="text-sm text-gray-500">Task ID: {{ task.task_id }}</p>
              <p class="text-sm text-gray-500">
                Created: {{ new Date(task.created_at).toLocaleString() }}
              </p>
            </div>
            <div class="flex items-center space-x-2">
              <span
                :class="{
                  'bg-green-100 text-green-800': task.status === 'completed',
                  'bg-yellow-100 text-yellow-800': task.status === 'running',
                  'bg-red-100 text-red-800': task.status === 'failed'
                }"
                class="px-2 py-1 text-xs font-medium rounded-full"
              >
                {{ task.status }}
              </span>
            </div>
          </div>
          
          <!-- Progress Bar for Running Scans -->
          <div v-if="task.status === 'running'" class="mb-3">
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${task.progress || 0}%` }"
              ></div>
            </div>
            <p class="text-xs text-gray-500 mt-1">{{ task.progress || 0 }}% complete</p>
          </div>
          
          <!-- Results Summary -->
          <div v-if="task.status === 'completed' && task.counts" class="mb-3">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div v-if="task.counts.whois_records > 0">
                <span class="font-medium text-gray-700">WHOIS Records:</span>
                <span class="text-gray-900 ml-1">{{ task.counts.whois_records }}</span>
              </div>
              <div v-if="task.counts.dns_records > 0">
                <span class="font-medium text-gray-700">DNS Records:</span>
                <span class="text-gray-900 ml-1">{{ task.counts.dns_records }}</span>
              </div>
              <div v-if="task.counts.wayback_urls > 0">
                <span class="font-medium text-gray-700">Wayback URLs:</span>
                <span class="text-gray-900 ml-1">{{ task.counts.wayback_urls }}</span>
              </div>
            </div>
          </div>
          
          <!-- Action Buttons -->
          <div class="flex justify-end space-x-2">
            <button
              v-if="task.status === 'completed'"
              @click="viewResults(task.task_id)"
              class="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              View Results
            </button>
            <button
              v-if="task.status === 'running'"
              @click="stopTask(task.task_id)"
              class="px-3 py-1 text-sm text-red-600 hover:text-red-800 font-medium"
            >
              Stop Scan
            </button>
            <button
              @click="removeTask(task.task_id)"
              class="px-3 py-1 text-sm text-red-600 hover:text-red-800 font-medium"
            >
              Remove
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Results Modal -->
    <div v-if="showResults" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">OSINT Results</h3>
          <button @click="showResults = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div v-if="currentResults" class="space-y-4">
          <!-- WHOIS Information -->
          <div v-if="currentResults.whois">
            <h4 class="font-medium text-gray-900 mb-2">WHOIS Information</h4>
            <div class="bg-gray-50 rounded-lg p-3">
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span class="font-medium text-gray-700">Domain:</span>
                  <span class="text-gray-600 ml-2">{{ currentResults.whois.domain }}</span>
                </div>
                <div>
                  <span class="font-medium text-gray-700">Registrar:</span>
                  <span class="text-gray-600 ml-2">{{ currentResults.whois.registrar || 'N/A' }}</span>
                </div>
                <div v-if="currentResults.whois.name_servers && currentResults.whois.name_servers.length > 0">
                  <span class="font-medium text-gray-700">Name Servers:</span>
                  <div class="text-gray-600 ml-2">
                    <div v-for="ns in currentResults.whois.name_servers" :key="ns" class="text-xs">{{ ns }}</div>
                  </div>
                </div>
                <div v-if="currentResults.whois.emails && currentResults.whois.emails.length > 0">
                  <span class="font-medium text-gray-700">Emails:</span>
                  <div class="text-gray-600 ml-2">
                    <div v-for="email in currentResults.whois.emails" :key="email" class="text-xs">{{ email }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- DNS Records -->
          <div v-if="currentResults.dns">
            <h4 class="font-medium text-gray-900 mb-2">DNS Records</h4>
            <div class="bg-gray-50 rounded-lg p-3 space-y-3">
              <div v-if="currentResults.dns.a_records && currentResults.dns.a_records.length > 0">
                <h5 class="font-medium text-gray-700 text-sm">A Records</h5>
                <div class="text-xs text-gray-600 space-y-1">
                  <div v-for="record in currentResults.dns.a_records" :key="record">{{ record }}</div>
                </div>
              </div>
              
              <div v-if="currentResults.dns.aaaa_records && currentResults.dns.aaaa_records.length > 0">
                <h5 class="font-medium text-gray-700 text-sm">AAAA Records</h5>
                <div class="text-xs text-gray-600 space-y-1">
                  <div v-for="record in currentResults.dns.aaaa_records" :key="record">{{ record }}</div>
                </div>
              </div>
              
              <div v-if="currentResults.dns.mx_records && currentResults.dns.mx_records.length > 0">
                <h5 class="font-medium text-gray-700 text-sm">MX Records</h5>
                <div class="text-xs text-gray-600 space-y-1">
                  <div v-for="record in currentResults.dns.mx_records" :key="record">{{ record }}</div>
                </div>
              </div>
              
              <div v-if="currentResults.dns.ns_records && currentResults.dns.ns_records.length > 0">
                <h5 class="font-medium text-gray-700 text-sm">NS Records</h5>
                <div class="text-xs text-gray-600 space-y-1">
                  <div v-for="record in currentResults.dns.ns_records" :key="record">{{ record }}</div>
                </div>
              </div>
              
              <div v-if="currentResults.dns.txt_records && currentResults.dns.txt_records.length > 0">
                <h5 class="font-medium text-gray-700 text-sm">TXT Records</h5>
                <div class="text-xs text-gray-600 space-y-1">
                  <div v-for="record in currentResults.dns.txt_records" :key="record">{{ record }}</div>
                </div>
              </div>
              
              <div v-if="currentResults.dns.cname_records && currentResults.dns.cname_records.length > 0">
                <h5 class="font-medium text-gray-700 text-sm">CNAME Records</h5>
                <div class="text-xs text-gray-600 space-y-1">
                  <div v-for="record in currentResults.dns.cname_records" :key="record">{{ record }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Wayback URLs -->
          <div v-if="currentResults.wayback_urls && currentResults.wayback_urls.length > 0">
            <h4 class="font-medium text-gray-900 mb-2">Wayback URLs ({{ currentResults.wayback_urls.length }})</h4>
            <div class="bg-gray-50 rounded-lg p-3 max-h-40 overflow-y-auto">
              <div v-for="url in currentResults.wayback_urls.slice(0, 50)" :key="url" class="text-xs text-gray-700 mb-1">
                <a :href="url" target="_blank" class="text-blue-600 hover:text-blue-800 break-all">{{ url }}</a>
              </div>
              <div v-if="currentResults.wayback_urls.length > 50" class="text-xs text-gray-500 mt-2">
                Showing first 50 of {{ currentResults.wayback_urls.length }} URLs
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="text-center py-8">
          <p class="text-gray-500">No results available for this task.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import ToolSelector from '@/components/ToolSelector.vue'

export default {
  name: 'OSINT',
  components: { ToolSelector },
  setup() {
    const target = ref('')
    const allTasks = ref([])
    const isScanning = ref(false)
    const showResults = ref(false)
    const currentResults = ref(null)
    const selectedTools = ref(['whois', 'dns', 'waybackurls'])
    const osintTools = [
      { id: 'whois', name: 'WHOIS Lookup', description: 'Domain registration and contact info', available: true },
      { id: 'dns', name: 'DNS Records', description: 'A, MX, NS, TXT, CNAME, etc.', available: true },
      { id: 'waybackurls', name: 'Wayback URLs', description: 'Historical URLs from the Wayback Machine', available: true }
    ]

    const loadTasks = async () => {
      try {
        console.log('🔍 Loading OSINT tasks...')
        const response = await axios.get('/api/v1/osint/tasks')
        console.log('✅ OSINT tasks response:', response.data)
        allTasks.value = response.data.tasks || []
        console.log('📊 Tasks loaded:', allTasks.value.length)
      } catch (error) {
        console.error('❌ Error loading OSINT scan history:', error)
        console.error('Error details:', error.response?.data || error.message)
      }
    }

    const startScan = async () => {
      if (!target.value) return
      
      isScanning.value = true
      try {
        console.log('🚀 Starting OSINT scan for:', target.value)
        const response = await axios.post('/api/v1/osint/gather', {
          target: target.value,
          tools: selectedTools.value
        })
        console.log('✅ OSINT scan started:', response.data)
        
        // Clear target and reload tasks
        target.value = ''
        selectedTools.value = ['whois', 'dns', 'waybackurls'] // Reset to default
        await loadTasks()
      } catch (error) {
        console.error('❌ Error starting OSINT scan:', error)
      } finally {
        isScanning.value = false
      }
    }

    const viewResults = async (taskId) => {
      try {
        console.log('📋 Loading results for task:', taskId)
        const response = await axios.get(`/api/v1/osint/gather/${taskId}/results`)
        console.log('✅ OSINT results:', response.data)
        currentResults.value = response.data.results || {}
        showResults.value = true
      } catch (error) {
        console.error('❌ Error loading OSINT results:', error)
      }
    }

    const stopTask = async (taskId) => {
      try {
        console.log('⏹️ Stopping task:', taskId)
        await axios.post(`/api/v1/osint/gather/${taskId}/stop`)
        await loadTasks()
      } catch (error) {
        console.error('❌ Error stopping task:', error)
      }
    }

    const removeTask = async (taskId) => {
      try {
        console.log('🗑️ Removing task:', taskId)
        await axios.delete(`/api/v1/osint/gather/${taskId}`)
        await loadTasks()
      } catch (error) {
        console.error('❌ Error removing task:', error)
      }
    }

    onMounted(() => {
      console.log('🎯 OSINT component mounted - calling loadTasks()')
      loadTasks()
    })

    return {
      target,
      allTasks,
      isScanning,
      showResults,
      currentResults,
      selectedTools,
      osintTools,
      loadTasks,
      startScan,
      viewResults,
      stopTask,
      removeTask
    }
  }
}
</script> 