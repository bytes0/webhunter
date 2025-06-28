<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-4">Dashboard</h1>
      <p class="text-gray-600">Welcome to the Bug Bounty Platform. Monitor your security assessments and view reports.</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="bg-white shadow rounded-lg p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <span class="text-blue-600 text-lg">🔍</span>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Scans</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stats.totalScans }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white shadow rounded-lg p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
              <span class="text-green-600 text-lg">✅</span>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Completed</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stats.completedScans }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white shadow rounded-lg p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
              <span class="text-yellow-600 text-lg">🔧</span>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Technologies</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stats.vulnerabilities }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white shadow rounded-lg p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
              <span class="text-purple-600 text-lg">🌐</span>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Subdomains</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stats.reports }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="bg-white shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <router-link to="/recon" class="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <h3 class="font-medium text-gray-900">Start Recon Scan</h3>
          <p class="text-sm text-gray-500">Discover subdomains and open ports</p>
        </router-link>
        
        <router-link to="/osint" class="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <h3 class="font-medium text-gray-900">OSINT Gathering</h3>
          <p class="text-sm text-gray-500">Collect open source intelligence</p>
        </router-link>
        
        <router-link to="/vulnscan" class="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <h3 class="font-medium text-gray-900">Vulnerability Scan</h3>
          <p class="text-sm text-gray-500">Scan for security vulnerabilities</p>
        </router-link>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-medium text-gray-900">Recent Activity</h2>
        <button 
          @click="loadDashboardData" 
          :disabled="isLoading"
          class="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 font-medium disabled:opacity-50"
        >
          {{ isLoading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
      <div v-if="recentActivity.length === 0" class="text-gray-500 text-center py-8">
        <div class="text-4xl mb-2">📊</div>
        <p>No recent activity. Start your first scan!</p>
      </div>
      <div v-else class="space-y-4">
        <div v-for="activity in recentActivity" :key="activity.id" class="flex items-center space-x-4 p-3 border border-gray-100 rounded-lg hover:bg-gray-50 transition-colors">
          <div class="flex-shrink-0">
            <div class="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
              <span class="text-gray-600 text-lg">{{ activity.icon }}</span>
            </div>
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium text-gray-900">{{ activity.title }}</p>
            <p class="text-sm text-gray-500">{{ activity.description }}</p>
          </div>
          <div class="flex-shrink-0">
            <span class="text-xs text-gray-400">{{ formatDate(activity.timestamp) }}</span>
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
  name: 'Dashboard',
  setup() {
    const stats = ref({
      totalScans: 0,
      completedScans: 0,
      vulnerabilities: 0,
      reports: 0
    })
    
    const recentActivity = ref([])
    const isLoading = ref(false)

    const loadDashboardData = async () => {
      if (isLoading.value) return // Prevent multiple simultaneous requests
      
      isLoading.value = true
      try {
        const response = await axios.get('/api/v1/reporting/dashboard')
        const data = response.data
        
        // Map the nested backend response to frontend structure
        stats.value = {
          totalScans: data.overview?.total_scans || 0,
          completedScans: data.overview?.completed_scans || 0,
          vulnerabilities: data.overview?.total_technologies || 0, // Using technologies as proxy for vulnerabilities
          reports: data.overview?.total_subdomains || 0 // Using subdomains as proxy for reports
        }
        
        // Transform recent activity to match frontend expectations
        recentActivity.value = (data.recent_activity || []).map(activity => {
          let icon = '🔄'
          let title = ''
          
          if (activity.status === 'completed') {
            icon = '✅'
            title = `Scan Completed: ${activity.target}`
          } else {
            icon = '🔄'
            title = `Scan Started: ${activity.target}`
          }
          
          // Add scan type indicator with specific icons
          let scanTypeLabel = ''
          if (activity.scan_type) {
            const scanTypeIcons = {
              'osint': '🔍',
              'recon': '🌐',
              'vulnscan': '🛡️'
            }
            const scanIcon = scanTypeIcons[activity.scan_type] || '📊'
            scanTypeLabel = ` ${scanIcon} ${activity.scan_type.toUpperCase()}`
          }
          title += scanTypeLabel
          
          return {
            id: activity.scan_id,
            title: title,
            description: activity.description || 'Scan completed',
            timestamp: activity.timestamp,
            icon: icon,
            type: activity.type,
            scan_type: activity.scan_type
          }
        })
      } catch (error) {
        console.error('Error loading dashboard data:', error)
        // Set default values on error
        stats.value = {
          totalScans: 0,
          completedScans: 0,
          vulnerabilities: 0,
          reports: 0
        }
        recentActivity.value = []
      } finally {
        isLoading.value = false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      const now = new Date()
      const diffInHours = Math.floor((now - date) / (1000 * 60 * 60))
      
      if (diffInHours < 1) {
        return 'Just now'
      } else if (diffInHours < 24) {
        return `${diffInHours}h ago`
      } else if (diffInHours < 48) {
        return 'Yesterday'
      } else {
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
      }
    }

    onMounted(() => {
      loadDashboardData()
    })

    return {
      stats,
      recentActivity,
      isLoading,
      formatDate
    }
  }
}
</script> 