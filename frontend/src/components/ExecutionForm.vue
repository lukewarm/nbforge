<template>
  <div class="bg-white shadow sm:rounded-lg">
    <div class="px-4 py-5 sm:p-6">
      <h3 class="text-lg leading-6 font-medium text-gray-900">
        Execute Notebook
      </h3>
      
      <!-- Python Version Selector -->
      <div class="mt-4">
        <label for="pythonVersion" class="block text-sm font-medium text-gray-700">Python Version</label>
        <select
          id="pythonVersion"
          v-model="formData.pythonVersion"
          class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
        >
          <option v-for="version in config.supportedPythonVersions" :key="version" :value="version">
            Python {{ version }}
          </option>
        </select>
      </div>
      
      <!-- Resource Configuration -->
      <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label for="cpuMilli" class="block text-sm font-medium text-gray-700">CPU (millicores)</label>
          <input
            id="cpuMilli"
            v-model.number="formData.cpuMilli"
            type="number"
            min="100"
            max="8000"
            step="100"
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          />
        </div>
        <div>
          <label for="memoryMib" class="block text-sm font-medium text-gray-700">Memory (MiB)</label>
          <input
            id="memoryMib"
            v-model.number="formData.memoryMib"
            type="number"
            min="256"
            max="32768"
            step="256"
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          />
        </div>
      </div>
      
      <!-- Parameters Form -->
      <div v-if="parameters.length > 0" class="mt-6">
        <h4 class="text-sm font-medium text-gray-700 mb-4">Parameters</h4>
        <parameter-form 
          :parameters="parameters" 
          @submit="onParametersSubmit"
        />
      </div>
      <div v-else class="mt-6">
        <p class="text-sm text-gray-500">This notebook has no parameters.</p>
        
        <div class="mt-5">
          <button
            type="button"
            @click="executeWithoutParams"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Execute Notebook
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import ParameterForm from './ParameterForm.vue'
import { config } from '@/config'

const props = defineProps({
  notebook: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['submit'])

const formData = reactive({
  pythonVersion: props.notebook.metadata?.resources?.python_version || config.supportedPythonVersions[0],
  cpuMilli: 1000,
  memoryMib: 2048,
  parameters: {}
})

const parameters = computed(() => {
  return props.notebook.parameters || []
})

const onParametersSubmit = (paramValues) => {
  formData.parameters = paramValues
  emit('submit', {
    pythonVersion: formData.pythonVersion,
    cpuMilli: formData.cpuMilli,
    memoryMib: formData.memoryMib,
    parameters: paramValues
  })
}

const executeWithoutParams = () => {
  emit('submit', {
    pythonVersion: formData.pythonVersion,
    cpuMilli: formData.cpuMilli,
    memoryMib: formData.memoryMib,
    parameters: {}
  })
}
</script> 