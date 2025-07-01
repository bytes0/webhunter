<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Reconnaissance</h1>
      <p class="text-gray-600">Discover subdomains, open ports, and technologies on your target domain.</p>
    </div>

    <!-- Scan Form -->
    <div class="bg-white shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Start New Scan</h2>
      
      <form @submit.prevent="startScan" class="space-y-4">
        <div>
          <label for="target" class="block text-sm font-medium text-gray-700 mb-2">
            Target Domain
          </label>
          <input
            id="target"
            v-model="scanForm.target"
            type="text"
            placeholder="example.com"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <!-- Tool Selection -->
        <ToolSelector
          title="Select Recon Tools"
          :tools="reconTools"
          v-model="scanForm.selectedTools"
        />

        <div class="flex justify-end space-x-3">
          <button
            type="button"
            @click="resetForm"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Reset
          </button>
          <button
            type="submit"
            :disabled="isStarting || !scanForm.target || scanForm.selectedTools.length === 0"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isStarting ? 'Starting...' : 'Start Scan' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Active Scans -->
    <div v-if="activeScans.length > 0" class="bg-white shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Active Scans</h2>
      <div class="space-y-4">
        <div 
          v-for="scan in activeScans" 
          :key="scan.id"
          class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center justify-between mb-3">
            <div class="flex-1">
              <h3 class="font-medium text-gray-900">{{ scan.target }}</h3>
              <p class="text-sm text-gray-500">Scan ID: {{ scan.id }}</p>
              <p class="text-sm text-gray-500">Started: {{ formatDate(scan.created_at) }}</p>
            </div>
            <div class="flex items-center space-x-2">
              <span 
                :class="[
                  'px-2 py-1 text-xs font-medium rounded-full',
                  scan.status === 'running' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'
                ]"
              >
                {{ scan.status }}
              </span>
            </div>
          </div>
          
          <!-- Progress Bar for Running Scans -->
          <div v-if="scan.status === 'running'" class="mb-3">
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${scan.progress || 0}%` }"
              ></div>
            </div>
            <p class="text-xs text-gray-500 mt-1">{{ scan.progress || 0 }}% complete</p>
          </div>
          
          <!-- Action Buttons -->
          <div class="flex justify-end space-x-2">
            <button
              @click="viewResults(scan.id)"
              class="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              View Results
            </button>
            <button
              @click="stopScan(scan.id)"
              class="px-3 py-1 text-sm text-red-600 hover:text-red-800 font-medium"
            >
              Stop Scan
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Scan Results -->
    <div v-if="scanResults.length > 0" class="bg-white shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Recent Results</h2>
      <div class="space-y-4">
        <div 
          v-for="result in scanResults" 
          :key="result.id"
          class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center justify-between mb-3">
            <div class="flex-1">
              <h3 class="font-medium text-gray-900">{{ result.target }}</h3>
              <p class="text-sm text-gray-500">Scan ID: {{ result.id }}</p>
              <p class="text-sm text-gray-500">Completed: {{ formatDate(result.completed_at) }}</p>
            </div>
            <div class="flex items-center space-x-2">
              <span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                completed
              </span>
            </div>
          </div>
          
          <!-- Results Summary -->
          <div class="mb-3">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span class="font-medium text-gray-700">Subdomains:</span>
                <span class="text-gray-900 ml-1">{{ result.subdomains_count || 0 }}</span>
              </div>
              <div>
                <span class="font-medium text-gray-700">Open Ports:</span>
                <span class="text-gray-900 ml-1">{{ result.ports_count || 0 }}</span>
              </div>
              <div>
                <span class="font-medium text-gray-700">Technologies:</span>
                <span class="text-gray-900 ml-1">{{ result.technologies_count || 0 }}</span>
              </div>
            </div>
          </div>
          
          <!-- Action Buttons -->
          <div class="flex justify-end space-x-2">
            <button
              @click="toggleScanDetails(result.id)"
              class="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              {{ expandedScans.includes(result.id) ? 'Hide Details' : 'Show Details' }}
            </button>
            <button
              v-if="result.subdomains_count > 0"
              @click="exportToCSV(result)"
              class="px-3 py-1 text-sm text-green-600 hover:text-green-800 font-medium"
            >
              Export CSV
            </button>
            <button
              @click="removeScan(result.id)"
              class="px-3 py-1 text-sm text-red-600 hover:text-red-800 font-medium"
            >
              Remove
            </button>
          </div>

          <!-- Expandable Details -->
          <div v-if="expandedScans.includes(result.id)" class="mt-4 space-y-4">
            <!-- Subdomains -->
            <div v-if="result.results?.subdomains?.length > 0" class="border-t pt-4">
              <h4 class="text-sm font-medium text-gray-700 mb-2 flex items-center justify-between">
                <span>Subdomains Found ({{ result.results.subdomains.length }})</span>
                <button 
                  @click="copyToClipboard(result.results.subdomains.map(s => s.subdomain).join('\n'))"
                  class="text-xs text-blue-600 hover:text-blue-800"
                >
                  Copy All
                </button>
              </h4>
              <div class="bg-gray-50 rounded p-3 max-h-48 overflow-y-auto border">
                <div v-for="subdomain in result.results.subdomains" :key="subdomain.subdomain" 
                     class="text-sm text-gray-700 mb-1 font-mono flex items-center justify-between">
                  <span>{{ subdomain.subdomain }}</span>
                  <span class="text-xs text-gray-500">{{ subdomain.source }}</span>
                </div>
              </div>
            </div>

            <!-- Ports -->
            <div v-if="result.results?.ports?.length > 0" class="border-t pt-4">
              <h4 class="text-sm font-medium text-gray-700 mb-2">Open Ports ({{ result.results.ports.length }})</h4>
              <div class="bg-gray-50 rounded p-3 max-h-32 overflow-y-auto border">
                <div v-for="port in result.results.ports" :key="port.port" 
                     class="text-sm text-gray-700 mb-1">
                  Port {{ port.port }}/{{ port.protocol }} - {{ port.service }} {{ port.version }}
                </div>
              </div>
            </div>

            <!-- Technologies -->
            <div v-if="result.results?.technologies?.length > 0" class="border-t pt-4">
              <h4 class="text-sm font-medium text-gray-700 mb-2">Technologies ({{ result.results.technologies.length }})</h4>
              <div class="bg-gray-50 rounded p-3 max-h-32 overflow-y-auto border">
                <div v-for="tech in result.results.technologies" :key="tech.technology" 
                     class="text-sm text-gray-700 mb-1">
                  {{ tech.technology }} {{ tech.version }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import ToolSelector from '@/components/ToolSelector.vue'

export default {
  name: 'Recon',
  components: {
    ToolSelector
  },
  setup() {
    const scanForm = ref({
      target: '',
      selectedTools: []
    })
    
    const reconTools = ref([
      {
        id: 'hackertarget_api',
        name: 'HackerTarget API',
        description: 'Subdomain enumeration via HackerTarget API',
        available: true
      },
      {
        id: 'nmap',
        name: 'Nmap',
        description: 'Port scanning and service detection',
        available: true
      },
      {
        id: 'nuclei',
        name: 'Nuclei',
        description: 'Technology detection and vulnerability scanning',
        available: true
      }
    ])
    
    const activeScans = ref([])
    const scanResults = ref([])
    const expandedScans = ref([])
    const isStarting = ref(false)
    let pollingInterval = null

    const loadScans = async () => {
      try {
        const response = await axios.get('/api/v1/recon/scans')
        const data = response.data
        
        // Map the backend response format to frontend format
        const allScans = data.scans || []
        
        // Show all scans that are running or recently completed
        activeScans.value = allScans
          .filter(scan => scan.status === 'running' || scan.status === 'started')
          .map(scan => ({
            id: scan.scan_id,
            target: scan.target,
            status: scan.status,
            progress: scan.progress,
            created_at: scan.created_at
          }))
        
        // Show completed scans in results
        scanResults.value = allScans
          .filter(scan => scan.status === 'completed' || scan.status === 'stopped' || scan.status === 'failed')
          .slice(0, 10)
          .map(scan => ({
            id: scan.scan_id,
            target: scan.target,
            status: scan.status,
            progress: scan.progress,
            created_at: scan.created_at,
            completed_at: scan.completed_at,
            subdomains_count: scan.counts?.subdomains || 0,
            ports_count: scan.counts?.ports || 0,
            technologies_count: scan.counts?.technologies || 0,
            results: scan.results || {}
          }))
      } catch (error) {
        console.error('Error loading scans:', error)
      }
    }

    const startScan = async () => {
      if (!scanForm.value.target || scanForm.value.selectedTools.length === 0) {
        return
      }
      
      isStarting.value = true
      try {
        const response = await axios.post('/api/v1/recon/scan', {
          target: scanForm.value.target,
          tools: scanForm.value.selectedTools
        })
        
        if (response.data.scan_id) {
          scanForm.value.target = ''
          scanForm.value.selectedTools = []
          await loadScans()
        }
      } catch (error) {
        console.error('Error starting scan:', error)
        alert('Failed to start scan. Please try again.')
      } finally {
        isStarting.value = false
      }
    }

    const resetForm = () => {
      scanForm.value.target = ''
      scanForm.value.selectedTools = []
    }

    const viewResults = (scanId) => {
      // Navigate to results page or show modal
      console.log('View results for scan:', scanId)
    }

    const toggleScanDetails = (scanId) => {
      const index = expandedScans.value.indexOf(scanId)
      if (index > -1) {
        expandedScans.value.splice(index, 1)
      } else {
        expandedScans.value.push(scanId)
      }
    }

    const exportToCSV = (scan) => {
      if (!scan.results || !scan.results.subdomains) return

      const csvContent = [
        'Subdomain,Source',
        ...scan.results.subdomains.map(s => `${s.subdomain},${s.source}`)
      ].join('\n')

      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `recon_${scan.target}_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      window.URL.revokeObjectURL(url)
    }

    const copyToClipboard = (text) => {
      navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard!')
      }).catch(err => {
        console.error('Failed to copy: ', err)
      })
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString()
    }

    const startPolling = () => {
      pollingInterval = setInterval(loadScans, 5000) // Poll every 5 seconds
    }

    const stopPolling = () => {
      if (pollingInterval) {
        clearInterval(pollingInterval)
        pollingInterval = null
      }
    }

    const stopScan = async (scanId) => {
      if (!confirm('Are you sure you want to stop this scan?')) {
        return
      }
      
      try {
        await axios.post(`/api/v1/recon/scan/${scanId}/stop`)
        await loadScans() // Refresh the scans list
      } catch (error) {
        console.error('Error stopping scan:', error)
        alert('Failed to stop scan. Please try again.')
      }
    }

    const removeScan = async (scanId) => {
      if (!confirm('Are you sure you want to remove this scan? This action cannot be undone.')) {
        return
      }
      
      try {
        await axios.delete(`/api/v1/recon/scan/${scanId}`)
        await loadScans() // Refresh the scans list
      } catch (error) {
        console.error('Error removing scan:', error)
        alert('Failed to remove scan. Please try again.')
      }
    }

    onMounted(() => {
      loadScans()
      startPolling()
    })

    onUnmounted(() => {
      stopPolling()
    })

    return {
      scanForm,
      reconTools,
      activeScans,
      scanResults,
      expandedScans,
      isStarting,
      startScan,
      resetForm,
      viewResults,
      toggleScanDetails,
      exportToCSV,
      copyToClipboard,
      formatDate,
      stopScan,
      removeScan
    }
  }
}
</script> 