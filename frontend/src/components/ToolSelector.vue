<template>
  <div class="space-y-4">
    <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
      <div 
        v-for="tool in tools" 
        :key="tool.id"
        v-memo="[tool.id, selectedTools.includes(tool.id)]"
        class="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <input
          :id="`tool-${tool.id}`"
          type="checkbox"
          :checked="selectedTools.includes(tool.id)"
          @change="toggleTool(tool.id)"
          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label :for="`tool-${tool.id}`" class="flex-1 cursor-pointer">
          <div class="font-medium text-gray-900">{{ tool.name }}</div>
          <div class="text-sm text-gray-500">{{ tool.description }}</div>
        </label>
        <div class="flex-shrink-0">
          <span 
            :class="[
              'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
              tool.available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            ]"
          >
            {{ tool.available ? 'Available' : 'Unavailable' }}
          </span>
        </div>
      </div>
    </div>
    
    <div class="flex justify-between items-center pt-4 border-t border-gray-200">
      <div class="text-sm text-gray-600">
        {{ selectedCount }} of {{ tools.length }} tools selected
      </div>
      <div class="space-x-2">
        <button
          @click="selectAll"
          class="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Select All
        </button>
        <button
          @click="clearAll"
          class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 font-medium"
        >
          Clear All
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'ToolSelector',
  props: {
    title: {
      type: String,
      required: true
    },
    tools: {
      type: Array,
      required: true
    },
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const selectedTools = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })

    const selectedCount = computed(() => selectedTools.value.length)

    const toggleTool = (toolId) => {
      const newSelection = selectedTools.value.includes(toolId)
        ? selectedTools.value.filter(id => id !== toolId)
        : [...selectedTools.value, toolId]
      selectedTools.value = newSelection
    }

    const selectAll = () => {
      const availableToolIds = props.tools
        .filter(tool => tool.available)
        .map(tool => tool.id)
      selectedTools.value = availableToolIds
    }

    const clearAll = () => {
      selectedTools.value = []
    }

    return {
      selectedTools,
      selectedCount,
      toggleTool,
      selectAll,
      clearAll
    }
  }
}
</script> 