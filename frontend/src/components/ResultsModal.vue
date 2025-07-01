<template>
  <div 
    v-if="show" 
    class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50 p-4"
    @click.self="close"
  >
    <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
      <!-- Modal Header -->
      <div class="flex justify-between items-center p-4 border-b">
        <h2 class="text-xl font-bold text-gray-800">Scan Results</h2>
        <button @click="close" class="text-gray-500 hover:text-gray-800">&times;</button>
      </div>
      
      <!-- Modal Body -->
      <div class="p-6 overflow-y-auto">
        <div v-if="results" class="space-y-4">
          <div>
            <h3 class="font-semibold text-gray-700">Target:</h3>
            <p class="text-gray-900">{{ results.target }}</p>
          </div>
          <div>
            <h3 class="font-semibold text-gray-700">Tool:</h3>
            <p class="text-gray-900">{{ results.tool }}</p>
          </div>
          <div>
            <h3 class="font-semibold text-gray-700">Vulnerabilities Found:</h3>
            <p class="text-gray-900">{{ results.vulnerabilities_found }}</p>
          </div>
          <div v-if="results.vulnerabilities && results.vulnerabilities.length">
            <h3 class="font-semibold text-gray-700">Vulnerability Details:</h3>
            <ul class="list-disc list-inside space-y-2 pl-4">
              <li v-for="(vuln, index) in results.vulnerabilities" :key="index" class="text-sm">
                <strong>{{ vuln.type }}</strong> (Severity: {{ vuln.severity }})
                <pre class="bg-gray-100 p-2 rounded mt-1 text-xs overflow-x-auto">{{ vuln.description }}</pre>
              </li>
            </ul>
          </div>
          <div>
            <h3 class="font-semibold text-gray-700">Raw Tool Output:</h3>
            <pre class="bg-gray-900 text-white text-xs p-4 rounded-md overflow-x-auto w-full">{{ results.raw_output || 'No raw output available.' }}</pre>
          </div>
        </div>
        <div v-else>
          <p>No results to display.</p>
        </div>
      </div>
      
      <!-- Modal Footer -->
      <div class="flex justify-end p-4 border-t">
        <button 
          @click="close"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResultsModal',
  props: {
    show: {
      type: Boolean,
      required: true,
    },
    results: {
      type: Object,
      default: () => null,
    },
  },
  emits: ['close'],
  setup(props, { emit }) {
    const close = () => {
      emit('close')
    }
    return { close }
  },
}
</script> 