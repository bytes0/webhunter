<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-4">Vulnerability Scanner</h1>
      <p class="text-gray-600">Scan for vulnerabilities in web applications and networks.</p>
    </div>

    <!-- Scan Form -->
    <div class="bg-white shadow rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Start Vulnerability Scan</h3>
      <form @submit.prevent="startScan" class="space-y-4">
        <div>
          <label for="target" class="block text-sm font-medium text-gray-700 mb-2">Target</label>
          <input
            id="target"
            v-model="scanForm.target"
            type="text"
            placeholder="https://example.com or 192.168.1.1"
            class="input-field"
            required
          />
        </div>
        
        <div>
          <label for="scanType" class="block text-sm font-medium text-gray-700 mb-2">Scan Type</label>
          <select id="scanType" v-model="scanForm.scanType" class="input-field">
            <option value="web">Web Application</option>
            <option value="network">Network</option>
            <option value="api">API</option>
          </select>
        </div>

        <div>
          <label for="scanLevel" class="block text-sm font-medium text-gray-700 mb-2">Scan Level</label>
          <select id="scanLevel" v-model="scanForm.scanLevel" class="input-field">
            <option value="low">Low (Quick)</option>
            <option value="medium">Medium (Balanced)</option>
            <option value="high">High (Comprehensive)</option>
          </select>
        </div>
      </form>
    </div>

    <!-- Tool Selector -->
    <ToolSelector 
      :tools="availableTools" 
      v-model="selectedTools"
    />

    <!-- Start Scan Button -->
    <div class="flex justify-end">
      <button 
        @click="startScan"
        class="btn-primary" 
        :disabled="isScanning || selectedTools.length === 0 || !scanForm.target"
      >
        {{ isScanning ? 'Starting Scan...' : `Start Scan (${selectedTools.length} tools)` }}
      </button>
    </div>

    <!-- Active Scans -->
    <div v-if="activeScans.length > 0" class="bg-white shadow rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Active Scans</h3>
      <div class="space-y-4">
        <div v-for="scan in activeScans" :key="scan.scan_id" class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
          <div class="flex items-center justify-between mb-3">
            <div class="flex-1">
              <h4 class="font-medium text-gray-900">{{ scan.target }}</h4>
              <p class="text-sm text-gray-500">Scan ID: {{ scan.scan_id }}</p>
              <p class="text-sm text-gray-500">{{ scan.scan_type }} • {{ scan.scan_level }}</p>
              <p class="text-sm text-gray-500">Started: {{ formatDate(scan.created_at) }}</p>
            </div>
            <div class="flex items-center space-x-2">
              <span class="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                {{ scan.status }}
              </span>
            </div>
          </div>
          
          <!-- Progress Bar for Running Scans -->
          <div v-if="scan.progress" class="mb-3">
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" :style="{ width: scan.progress + '%' }"></div>
            </div>
            <p class="text-xs text-gray-500 mt-1">{{ scan.progress }}% complete</p>
          </div>
          
          <!-- Action Buttons -->
          <div class="flex justify-end space-x-2">
            <button @click="checkStatus(scan.scan_id)" class="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 font-medium">
              Check Status
            </button>
            <button @click="stopScan(scan.scan_id)" class="px-3 py-1 text-sm text-red-600 hover:text-red-800 font-medium">
              Stop Scan
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Scan Results -->
    <div v-if="scanResults" class="bg-white shadow rounded-lg p-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-medium text-gray-900">Scan Results</h3>
        <button @click="clearResults" class="px-3 py-1 text-sm text-red-600 hover:text-red-800 font-medium">
          Clear Results
        </button>
      </div>
      
      <!-- Summary -->
      <div class="mb-6">
        <h4 class="font-medium text-gray-900 mb-3">Vulnerability Summary</h4>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="text-center p-4 bg-red-50 rounded-lg">
            <div class="text-2xl font-bold text-red-600">{{ scanResults.summary?.critical || 0 }}</div>
            <div class="text-sm text-gray-500">Critical</div>
          </div>
          <div class="text-center p-4 bg-orange-50 rounded-lg">
            <div class="text-2xl font-bold text-orange-600">{{ scanResults.summary?.high || 0 }}</div>
            <div class="text-sm text-gray-500">High</div>
          </div>
          <div class="text-center p-4 bg-yellow-50 rounded-lg">
            <div class="text-2xl font-bold text-yellow-600">{{ scanResults.summary?.medium || 0 }}</div>
            <div class="text-sm text-gray-500">Medium</div>
          </div>
          <div class="text-center p-4 bg-blue-50 rounded-lg">
            <div class="text-2xl font-bold text-blue-600">{{ scanResults.summary?.low || 0 }}</div>
            <div class="text-sm text-gray-500">Low</div>
          </div>
        </div>
      </div>

      <!-- Vulnerabilities -->
      <div v-if="scanResults.vulnerabilities?.length > 0">
        <h4 class="font-medium text-gray-900 mb-3">Vulnerabilities Found</h4>
        <div class="space-y-4">
          <div v-for="vuln in scanResults.vulnerabilities" :key="vuln.id" class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
            <div class="flex justify-between items-start mb-2">
              <div>
                <h5 class="font-medium text-gray-900">{{ vuln.title }}</h5>
                <p class="text-sm text-gray-500">{{ vuln.description }}</p>
              </div>
              <span :class="getSeverityClass(vuln.severity)" class="px-2 py-1 text-xs font-medium rounded-full">
                {{ vuln.severity }}
              </span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span class="font-medium text-gray-700">URL:</span>
                <span class="text-gray-900 ml-2">{{ vuln.url }}</span>
              </div>
              <div v-if="vuln.parameter">
                <span class="font-medium text-gray-700">Parameter:</span>
                <span class="text-gray-900 ml-2">{{ vuln.parameter }}</span>
              </div>
              <div v-if="vuln.cwe">
                <span class="font-medium text-gray-700">CWE:</span>
                <span class="text-gray-900 ml-2">{{ vuln.cwe }}</span>
              </div>
              <div v-if="vuln.cvss_score">
                <span class="font-medium text-gray-700">CVSS Score:</span>
                <span class="text-gray-900 ml-2">{{ vuln.cvss_score }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Scan Templates -->
    <div class="bg-white shadow rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Scan Templates</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-for="template in scanTemplates" :key="template.name" class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
          <h4 class="font-medium text-gray-900 mb-2">{{ template.name }}</h4>
          <p class="text-sm text-gray-500 mb-3">{{ template.description }}</p>
          <div class="space-y-1 text-xs text-gray-600">
            <div>Type: {{ template.scan_type }}</div>
            <div>Level: {{ template.scan_level }}</div>
            <div>Duration: {{ template.duration }}</div>
          </div>
          <button @click="useTemplate(template)" class="w-full btn-secondary mt-3 text-sm">
            Use Template
          </button>
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
  name: 'VulnScan',
  components: {
    ToolSelector
  },
  setup() {
    const scanForm = ref({
      target: '',
      scanType: 'web',
      scanLevel: 'medium'
    })

    const isScanning = ref(false)
    const activeScans = ref([])
    const scanResults = ref(null)
    const selectedTools = ref([])
    const availableTools = ref([
      {
        id: 'nuclei',
        name: 'Nuclei',
        description: 'Fast vulnerability scanner',
        available: true
      },
      {
        id: 'nikto',
        name: 'Nikto',
        description: 'Web server scanner',
        available: true
      }
    ])

    const scanTemplates = ref([
      {
        name: 'Quick Web Scan',
        description: 'Fast scan for common web vulnerabilities',
        scan_type: 'web',
        scan_level: 'low',
        duration: '5-10 minutes'
      },
      {
        name: 'Comprehensive Web Scan',
        description: 'Thorough scan for all web vulnerabilities',
        scan_type: 'web',
        scan_level: 'high',
        duration: '30-60 minutes'
      },
      {
        name: 'Network Scan',
        description: 'Network infrastructure vulnerability scan',
        scan_type: 'network',
        scan_level: 'medium',
        duration: '15-30 minutes'
      }
    ])

    const startScan = async () => {
      if (selectedTools.value.length === 0) {
        alert('Please select at least one tool to run.')
        return
      }

      isScanning.value = true
      try {
        const requestData = {
          ...scanForm.value,
          tools: selectedTools.value
        }
        
        const response = await axios.post('/api/v1/vulnscan/scan', requestData)
        const scan = response.data
        
        activeScans.value.push(scan)
        scanForm.value.target = ''
        
        // Poll for status updates
        pollScanStatus(scan.scan_id)
      } catch (error) {
        console.error('Error starting scan:', error)
      } finally {
        isScanning.value = false
      }
    }

    const checkStatus = async (scanId) => {
      try {
        const response = await axios.get(`/api/v1/vulnscan/scan/${scanId}`)
        const scan = response.data
        
        // Update active scan
        const index = activeScans.value.findIndex(s => s.scan_id === scanId)
        if (index !== -1) {
          activeScans.value[index] = scan
        }
        
        // If completed, get results
        if (scan.status === 'completed') {
          const resultsResponse = await axios.get(`/api/v1/vulnscan/scan/${scanId}/results`)
          scanResults.value = resultsResponse.data.results
          
          // Remove from active scans
          activeScans.value = activeScans.value.filter(s => s.scan_id !== scanId)
        }
      } catch (error) {
        console.error('Error checking scan status:', error)
      }
    }

    const pollScanStatus = (scanId) => {
      const interval = setInterval(async () => {
        try {
          const response = await axios.get(`/api/v1/vulnscan/scan/${scanId}`)
          const scan = response.data
          
          // Update active scan
          const index = activeScans.value.findIndex(s => s.scan_id === scanId)
          if (index !== -1) {
            activeScans.value[index] = scan
          }
          
          // If completed, get results and stop polling
          if (scan.status === 'completed') {
            const resultsResponse = await axios.get(`/api/v1/vulnscan/scan/${scanId}/results`)
            scanResults.value = resultsResponse.data.results
            
            // Remove from active scans
            activeScans.value = activeScans.value.filter(s => s.scan_id !== scanId)
            clearInterval(interval)
          } else if (scan.status === 'failed') {
            // Handle failed scans
            activeScans.value = activeScans.value.filter(s => s.scan_id !== scanId)
            clearInterval(interval)
          }
        } catch (error) {
          console.error('Error polling scan status:', error)
          clearInterval(interval)
          // Remove failed scan
          activeScans.value = activeScans.value.filter(s => s.scan_id !== scanId)
        }
      }, 5000) // Poll every 5 seconds
      
      // Store interval reference for cleanup
      return interval
    }

    const useTemplate = (template) => {
      scanForm.value.scanType = template.scan_type
      scanForm.value.scanLevel = template.scan_level
    }

    const getSeverityClass = (severity) => {
      switch (severity.toLowerCase()) {
        case 'critical':
          return 'bg-red-100 text-red-800'
        case 'high':
          return 'bg-orange-100 text-orange-800'
        case 'medium':
          return 'bg-yellow-100 text-yellow-800'
        case 'low':
          return 'bg-blue-100 text-blue-800'
        default:
          return 'bg-gray-100 text-gray-800'
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString()
    }

    const stopScan = async (scanId) => {
      try {
        await axios.post(`/api/v1/vulnscan/scan/${scanId}/stop`)
        activeScans.value = activeScans.value.filter(s => s.scan_id !== scanId)
      } catch (error) {
        console.error('Error stopping scan:', error)
      }
    }

    const clearResults = () => {
      scanResults.value = null
    }

    onMounted(() => {
      // Select all tools by default
      selectedTools.value = availableTools.value
        .filter(tool => tool.available)
        .map(tool => tool.id)
    })

    return {
      scanForm,
      isScanning,
      activeScans,
      scanResults,
      selectedTools,
      availableTools,
      scanTemplates,
      startScan,
      checkStatus,
      useTemplate,
      getSeverityClass,
      formatDate,
      stopScan,
      clearResults
    }
  }
}
</script> 