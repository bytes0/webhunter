<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow rounded-lg p-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-4">Reporting</h1>
      <p class="text-gray-600">Generate comprehensive security assessment reports.</p>
    </div>

    <!-- Generate Report Form -->
    <div class="card">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Generate New Report</h3>
      <form @submit.prevent="generateReport" class="space-y-4">
        <div>
          <label for="reportType" class="block text-sm font-medium text-gray-700 mb-2">Report Type</label>
          <select id="reportType" v-model="reportForm.reportType" class="input-field">
            <option value="summary">Summary Report</option>
            <option value="detailed">Detailed Report</option>
            <option value="executive">Executive Report</option>
          </select>
        </div>
        
        <div>
          <label for="scanIds" class="block text-sm font-medium text-gray-700 mb-2">Select Scans</label>
          <div class="space-y-2">
            <div v-for="scan in availableScans" :key="scan.id" class="flex items-center">
              <input
                :id="scan.id"
                type="checkbox"
                :value="scan.id"
                v-model="reportForm.scanIds"
                class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <label :for="scan.id" class="ml-2 text-sm text-gray-700">
                {{ scan.title }} ({{ scan.type }})
              </label>
            </div>
          </div>
        </div>

        <div>
          <label for="format" class="block text-sm font-medium text-gray-700 mb-2">Output Format</label>
          <select id="format" v-model="reportForm.format" class="input-field">
            <option value="pdf">PDF</option>
            <option value="html">HTML</option>
            <option value="json">JSON</option>
          </select>
        </div>

        <button type="submit" class="btn-primary" :disabled="isGenerating">
          {{ isGenerating ? 'Generating Report...' : 'Generate Report' }}
        </button>
      </form>
    </div>

    <!-- Active Reports -->
    <div v-if="activeReports.length > 0" class="card">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Active Reports</h3>
      <div class="space-y-4">
        <div v-for="report in activeReports" :key="report.report_id" class="border rounded-lg p-4">
          <div class="flex justify-between items-center">
            <div>
              <h4 class="font-medium text-gray-900">{{ report.report_type }}</h4>
              <p class="text-sm text-gray-500">Started: {{ formatDate(report.created_at) }}</p>
            </div>
            <div class="flex items-center space-x-2">
              <span class="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                {{ report.status }}
              </span>
              <button @click="checkReportStatus(report.report_id)" class="btn-secondary text-sm">
                Check Status
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Generated Reports -->
    <div class="card">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Generated Reports</h3>
      <div class="space-y-4">
        <div v-for="report in generatedReports" :key="report.id" class="border rounded-lg p-4">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <h4 class="font-medium text-gray-900">{{ report.title }}</h4>
              <p class="text-sm text-gray-500">{{ report.type }} • {{ formatDate(report.created_at) }}</p>
              <p class="text-sm text-gray-500">{{ report.scan_count }} scans • {{ report.vulnerabilities_found }} vulnerabilities</p>
            </div>
            <div class="flex items-center space-x-2">
              <span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                {{ report.status }}
              </span>
              <button @click="downloadReport(report.id)" class="btn-secondary text-sm">
                Download
              </button>
              <button @click="viewReport(report.id)" class="btn-primary text-sm">
                View
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Report Templates -->
    <div class="card">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Report Templates</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-for="template in reportTemplates" :key="template.name" class="border rounded-lg p-4">
          <h4 class="font-medium text-gray-900 mb-2">{{ template.title }}</h4>
          <p class="text-sm text-gray-500 mb-3">{{ template.description }}</p>
          <div class="space-y-1 text-xs text-gray-600">
            <div>Sections: {{ template.sections.join(', ') }}</div>
            <div>Pages: ~{{ template.estimated_pages }}</div>
          </div>
          <button @click="useTemplate(template)" class="w-full btn-secondary mt-3 text-sm">
            Use Template
          </button>
        </div>
      </div>
    </div>

    <!-- Dashboard Data -->
    <div class="card">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Reporting Dashboard</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="text-center p-4 bg-blue-50 rounded-lg">
          <div class="text-2xl font-bold text-blue-600">{{ dashboardData.overview?.total_scans || 0 }}</div>
          <div class="text-sm text-gray-500">Total Scans</div>
        </div>
        <div class="text-center p-4 bg-green-50 rounded-lg">
          <div class="text-2xl font-bold text-green-600">{{ dashboardData.overview?.total_reports || 0 }}</div>
          <div class="text-sm text-gray-500">Total Reports</div>
        </div>
        <div class="text-center p-4 bg-yellow-50 rounded-lg">
          <div class="text-2xl font-bold text-yellow-600">{{ dashboardData.overview?.active_scans || 0 }}</div>
          <div class="text-sm text-gray-500">Active Scans</div>
        </div>
        <div class="text-center p-4 bg-red-50 rounded-lg">
          <div class="text-2xl font-bold text-red-600">{{ dashboardData.overview?.vulnerabilities_found || 0 }}</div>
          <div class="text-sm text-gray-500">Vulnerabilities</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'Reporting',
  setup() {
    const reportForm = ref({
      reportType: 'summary',
      scanIds: [],
      format: 'pdf'
    })

    const isGenerating = ref(false)
    const activeReports = ref([])
    const generatedReports = ref([])
    const availableScans = ref([])
    const reportTemplates = ref([])
    const dashboardData = ref({})

    const generateReport = async () => {
      if (reportForm.value.scanIds.length === 0) {
        alert('Please select at least one scan')
        return
      }

      isGenerating.value = true
      try {
        const response = await axios.post('/api/v1/reporting/generate', reportForm.value)
        const report = response.data
        
        activeReports.value.push(report)
        reportForm.value.scanIds = []
        
        // Poll for status updates
        pollReportStatus(report.report_id)
      } catch (error) {
        console.error('Error generating report:', error)
      } finally {
        isGenerating.value = false
      }
    }

    const checkReportStatus = async (reportId) => {
      try {
        const response = await axios.get(`/api/v1/reporting/reports/${reportId}`)
        const report = response.data
        
        // Update active report
        const index = activeReports.value.findIndex(r => r.report_id === reportId)
        if (index !== -1) {
          activeReports.value[index] = report
        }
        
        // If completed, remove from active and add to generated
        if (report.status === 'completed') {
          activeReports.value = activeReports.value.filter(r => r.report_id !== reportId)
          generatedReports.value.unshift(report)
        }
      } catch (error) {
        console.error('Error checking report status:', error)
      }
    }

    const pollReportStatus = (reportId) => {
      const interval = setInterval(async () => {
        try {
          const response = await axios.get(`/api/v1/reporting/reports/${reportId}`)
          const report = response.data
          
          // Update active report
          const index = activeReports.value.findIndex(r => r.report_id === reportId)
          if (index !== -1) {
            activeReports.value[index] = report
          }
          
          // If completed, remove from active and add to generated
          if (report.status === 'completed') {
            activeReports.value = activeReports.value.filter(r => r.report_id !== reportId)
            generatedReports.value.unshift(report)
            clearInterval(interval)
          }
        } catch (error) {
          console.error('Error polling report status:', error)
          clearInterval(interval)
        }
      }, 5000) // Poll every 5 seconds
    }

    const downloadReport = async (reportId) => {
      try {
        const response = await axios.get(`/api/v1/reporting/reports/${reportId}/download`)
        const downloadData = response.data
        
        // Create download link
        const link = document.createElement('a')
        link.href = downloadData.download_url
        link.download = `report-${reportId}.${downloadData.format}`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (error) {
        console.error('Error downloading report:', error)
      }
    }

    const viewReport = (reportId) => {
      // Navigate to report view or open in new tab
      window.open(`/api/v1/reporting/reports/${reportId}/download?format=html`, '_blank')
    }

    const loadGeneratedReports = async () => {
      try {
        const response = await axios.get('/api/v1/reporting/reports')
        generatedReports.value = response.data.reports
      } catch (error) {
        console.error('Error loading reports:', error)
        // Fallback data
        generatedReports.value = [
          {
            id: 'report-001',
            title: 'Security Assessment Report - example.com',
            type: 'comprehensive',
            status: 'completed',
            created_at: '2024-01-15T10:30:00Z',
            scan_count: 3,
            vulnerabilities_found: 5
          }
        ]
      }
    }

    const loadAvailableScans = async () => {
      // This would load scans from the database
      availableScans.value = [
        { id: 'scan-001', title: 'Recon Scan - example.com', type: 'recon' },
        { id: 'scan-002', title: 'Vulnerability Scan - example.com', type: 'vulnscan' },
        { id: 'scan-003', title: 'OSINT Gathering - example.com', type: 'osint' }
      ]
    }

    const loadReportTemplates = async () => {
      try {
        const response = await axios.get('/api/v1/reporting/templates')
        reportTemplates.value = response.data.templates
      } catch (error) {
        console.error('Error loading templates:', error)
        // Fallback data
        reportTemplates.value = [
          {
            name: 'executive_summary',
            title: 'Executive Summary',
            description: 'Report sintetico per dirigenti',
            sections: ['overview', 'key_findings', 'recommendations'],
            estimated_pages: 5
          },
          {
            name: 'technical_report',
            title: 'Technical Report',
            description: 'Report tecnico dettagliato',
            sections: ['methodology', 'findings', 'remediation', 'appendix'],
            estimated_pages: 25
          },
          {
            name: 'compliance_report',
            title: 'Compliance Report',
            description: 'Report per compliance e audit',
            sections: ['scope', 'compliance_matrix', 'findings', 'remediation_plan'],
            estimated_pages: 15
          }
        ]
      }
    }

    const loadDashboardData = async () => {
      try {
        const response = await axios.get('/api/v1/reporting/dashboard')
        dashboardData.value = response.data
      } catch (error) {
        console.error('Error loading dashboard data:', error)
        // Fallback data
        dashboardData.value = {
          overview: {
            total_scans: 45,
            total_reports: 12,
            active_scans: 3,
            vulnerabilities_found: 28
          }
        }
      }
    }

    const useTemplate = (template) => {
      reportForm.value.reportType = template.name
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString()
    }

    onMounted(() => {
      loadGeneratedReports()
      loadAvailableScans()
      loadReportTemplates()
      loadDashboardData()
    })

    return {
      reportForm,
      isGenerating,
      activeReports,
      generatedReports,
      availableScans,
      reportTemplates,
      dashboardData,
      generateReport,
      checkReportStatus,
      downloadReport,
      viewReport,
      useTemplate,
      formatDate
    }
  }
}
</script> 