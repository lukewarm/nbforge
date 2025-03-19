<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <div v-if="loading" class="text-center py-12">
      <loading-spinner message="Loading notebook..." />
    </div>

    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 my-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>
      </div>
    </div>

    <div v-else-if="notebook" class="space-y-8">
      <!-- Header with metadata -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-start">
      <div>
            <h2 class="text-2xl font-bold text-gray-900">
              {{ notebook.name || notebook.path.split('/').pop() }}
            </h2>
            <p v-if="notebook.description" class="mt-1 max-w-2xl text-sm text-gray-500">
              {{ notebook.description }}
            </p>
          </div>
          <div class="flex space-x-3">
            <router-link 
              :to="{ name: 'executions', query: { notebook: notebook.path } }"
              class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <svg class="-ml-0.5 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
              </svg>
              View Executions
            </router-link>
          </div>
        </div>
        <div class="border-t border-gray-200 px-4 py-5 sm:px-6">
          <dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div class="sm:col-span-1">
              <dt class="text-sm font-medium text-gray-500">Path</dt>
              <dd class="mt-1 text-sm text-gray-900">
                <button 
                  @click="downloadNotebook"
                  :disabled="downloadStatus === 'downloading'"
                  class="text-indigo-600 hover:text-indigo-900 flex items-center"
                >
                  {{ notebook.path }}
                  <svg v-if="downloadStatus === 'downloading'" class="animate-spin ml-1 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <svg v-else class="inline-block ml-1 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </button>
                <span v-if="downloadStatus === 'success'" class="ml-2 text-green-500 text-sm">
                  Download successful
                </span>
                <span v-if="downloadStatus === 'error'" class="ml-2 text-red-500 text-sm">
                  Download failed
                </span>
              </dd>
            </div>
            <div v-if="notebook.tags && notebook.tags.length > 0" class="sm:col-span-2">
              <dt class="text-sm font-medium text-gray-500">Tags</dt>
              <dd class="mt-1 text-sm text-gray-900">
                <div class="flex flex-wrap gap-2">
          <span
                    v-for="tag in notebook.tags" 
            :key="tag"
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
          >
            {{ tag }}
          </span>
        </div>
              </dd>
      </div>

            <!-- Advanced Details (collapsible) -->
            <div class="sm:col-span-2 mt-4">
              <button 
                type="button"
                @click="showAdvancedDetails = !showAdvancedDetails"
                class="text-sm text-gray-600 flex items-center focus:outline-none"
              >
                <svg 
                  class="h-5 w-5 mr-1 text-gray-500 transform transition-transform duration-200"
                  :class="{ 'rotate-90': showAdvancedDetails }"
                  xmlns="http://www.w3.org/2000/svg" 
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
                Advanced Details
              </button>
              
              <div v-if="showAdvancedDetails" class="mt-4 grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                <div class="sm:col-span-1">
                  <dt class="text-sm font-medium text-gray-500">Last Modified</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ formatDate(notebook.last_modified) }}</dd>
                </div>
                <div class="sm:col-span-1">
                  <dt class="text-sm font-medium text-gray-500">Size</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ formatFileSize(notebook.size) }}</dd>
                </div>
                <div class="sm:col-span-1">
                  <dt class="text-sm font-medium text-gray-500">Python Version</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ notebook.python_version || '3.9' }}</dd>
                </div>
                <div class="sm:col-span-1">
                  <dt class="text-sm font-medium text-gray-500">CPU</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ config.defaultResources.cpuMilli }} millicores ({{ config.defaultResources.cpuMilli/1000 }} CPU)</dd>
                </div>
                <div class="sm:col-span-1">
                  <dt class="text-sm font-medium text-gray-500">Memory</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ config.defaultResources.memoryMib }} MiB ({{ (config.defaultResources.memoryMib/1024).toFixed(1) }} GB)</dd>
                </div>
                <div v-if="notebook.requirements && Object.keys(notebook.requirements).length > 0" class="sm:col-span-2">
                  <dt class="text-sm font-medium text-gray-500">Requirements</dt>
                  <dd class="mt-1 text-sm text-gray-900">
                    <div class="flex flex-wrap gap-2">
                      <span 
                        v-for="(version, pkg) in notebook.requirements" 
                        :key="pkg" 
                        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {{ pkg }} {{ version }}
                      </span>
          </div>
                  </dd>
          </div>
        </div>
      </div>
          </dl>
        </div>
      </div>

      <!-- Main section: Parameter form -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Execute Notebook</h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">
            Configure parameters for notebook execution
          </p>
        </div>
        <div class="border-t border-gray-200">
          <div class="px-4 py-5 sm:p-6">
            <form @submit.prevent="executeNotebook" class="space-y-6">
              <!-- Parameters -->
              <div v-if="notebook.parameters && notebook.parameters.length > 0">
                <h4 class="text-sm font-medium text-gray-700 mb-3">Parameters</h4>
                <div class="space-y-6">
                  <div v-for="param in notebook.parameters" :key="param.name" class="sm:grid sm:grid-cols-3 sm:gap-4 sm:items-start">
                    <label :for="param.name" class="block text-sm font-medium text-gray-700 sm:mt-px sm:pt-2">
                      <div class="flex items-center">
                        <!-- Type indicator icon -->
                        <span v-if="getTypeIcon(param)" class="mr-1.5">
                          <svg class="h-4 w-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path :d="getTypeIcon(param)" />
                          </svg>
                        </span>
                        {{ param.name }}
                        <!-- Required indicator -->
                        <span v-if="param.validation?.required" class="ml-1 text-red-500">*</span>
                      </div>
                      <p v-if="param.description" class="text-gray-500 font-normal text-xs mt-0.5">{{ param.description }}</p>
                      <p class="text-xs text-gray-500 mt-0.5">
                        {{ getTypeDescription(param) }}
                      </p>
                    </label>
                    <div class="mt-1 sm:mt-0 sm:col-span-2 relative">
                      <!-- Text input -->
                      <input
                        v-if="!param.input_type || param.input_type === 'text'"
                        :id="param.name"
                        v-model="formData.parameters[param.name]"
                        type="text"
                        class="max-w-lg block w-full shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:max-w-xs sm:text-sm border-gray-300 rounded-md"
                        :class="{ 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500': paramErrors[param.name] }"
                        :placeholder="param.default"
                        :aria-describedby="`${param.name}-description ${param.name}-error`"
                      />
                      
                      <!-- Number input -->
                      <input
                        v-else-if="param.input_type === 'number' || param.type === 'int' || param.type === 'float'"
                        :id="param.name"
                        v-model.number="formData.parameters[param.name]"
                        type="number"
                        class="max-w-lg block w-full shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:max-w-xs sm:text-sm border-gray-300 rounded-md"
                        :class="{ 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500': paramErrors[param.name] }"
                        :placeholder="param.default"
                        :min="param.validation?.min"
                        :max="param.validation?.max"
                        :step="param.type === 'int' ? 1 : 'any'"
                        :aria-describedby="`${param.name}-description ${param.name}-error`"
                      />
                      
                      <!-- Date input -->
                      <div v-else-if="param.input_type === 'date'" class="relative max-w-xs">
                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                          </svg>
                        </div>
                        <input
                          :id="param.name"
                          v-model="formData.parameters[param.name]"
                          type="date"
                          class="pl-10 max-w-lg block w-full shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:max-w-xs sm:text-sm border-gray-300 rounded-md"
                          :class="{ 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500': paramErrors[param.name] }"
                          :min="param.validation?.min"
                          :max="param.validation?.max"
                          :aria-describedby="`${param.name}-description ${param.name}-error`"
                        />
                      </div>
                      
                      <!-- Checkbox for boolean -->
                      <div v-else-if="param.input_type === 'checkbox' || param.type === 'bool'" class="flex items-center">
                        <input
                          :id="param.name"
                          v-model="formData.parameters[param.name]"
                          type="checkbox"
                          class="focus:ring-indigo-500 h-5 w-5 text-indigo-600 border-gray-300 rounded"
                          :aria-describedby="`${param.name}-description ${param.name}-error`"
                        />
                        <span class="ml-2 text-sm text-gray-500">{{ formData.parameters[param.name] ? 'Yes' : 'No' }}</span>
                      </div>
                      
                      <!-- Select dropdown -->
                      <div v-else-if="param.input_type === 'select' && param.options" class="relative max-w-xs">
                        <select
                          :id="param.name"
                          v-model="formData.parameters[param.name]"
                          class="appearance-none block w-full pl-3 pr-10 py-2 border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                          :class="{ 'border-red-300 text-red-900 focus:ring-red-500 focus:border-red-500': paramErrors[param.name] }"
                          :aria-describedby="`${param.name}-description ${param.name}-error`"
                        >
                          <option v-for="option in param.options" :key="option" :value="option">
                            {{ option }}
                          </option>
                        </select>
                        <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                          <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                          </svg>
                        </div>
                      </div>
                      
                      <!-- Multi-select -->
                      <div v-else-if="param.input_type === 'multiselect' && param.options" class="max-w-lg">
                        <fieldset>
                          <legend class="sr-only">{{ param.name }}</legend>
                          <div class="space-y-2">
                            <div 
                              v-for="option in param.options" 
                              :key="option" 
                              class="relative flex items-start"
                            >
                              <div class="flex items-center h-5">
                                <input
                                  :id="`${param.name}-${option}`"
                                  v-model="multiSelectValues[param.name]"
                                  :value="option"
                                  type="checkbox"
                                  class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                                  :aria-describedby="`${param.name}-description ${param.name}-error`"
                                />
                              </div>
                              <div class="ml-3 text-sm">
                                <label :for="`${param.name}-${option}`" class="font-medium text-gray-700">{{ option }}</label>
                              </div>
                            </div>
                          </div>
                        </fieldset>
                        <div v-if="multiSelectValues[param.name] && multiSelectValues[param.name].length > 0" class="mt-2 flex flex-wrap gap-1">
                          <span 
                            v-for="selected in multiSelectValues[param.name]" 
                            :key="selected"
                            class="inline-flex items-center py-0.5 pl-2 pr-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-700"
                          >
                            {{ selected }}
                            <button 
                              type="button" 
                              class="flex-shrink-0 ml-0.5 h-4 w-4 rounded-full inline-flex items-center justify-center text-indigo-400 hover:bg-indigo-200 hover:text-indigo-500 focus:outline-none focus:bg-indigo-500 focus:text-white"
                              @click="removeMultiSelectValue(param.name, selected)"
                            >
                              <span class="sr-only">Remove {{ selected }}</span>
                              <svg class="h-2 w-2" stroke="currentColor" fill="none" viewBox="0 0 8 8">
                                <path stroke-linecap="round" stroke-width="1.5" d="M1 1l6 6m0-6L1 7" />
                              </svg>
                            </button>
                          </span>
                        </div>
                      </div>
                      
                      <!-- Textarea for longer text -->
                      <textarea
                        v-else-if="param.input_type === 'textarea'"
                        :id="param.name"
                        v-model="formData.parameters[param.name]"
                        rows="3"
                        class="max-w-lg shadow-sm block w-full focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border-gray-300 rounded-md"
                        :class="{ 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500': paramErrors[param.name] }"
                        :placeholder="param.default"
                        :aria-describedby="`${param.name}-description ${param.name}-error`"
                      ></textarea>
                      
                      <!-- Default text input if no specific type -->
                      <input
                        v-else
                        :id="param.name"
                        v-model="formData.parameters[param.name]"
                        type="text"
                        class="max-w-lg block w-full shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:max-w-xs sm:text-sm border-gray-300 rounded-md"
                        :class="{ 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500': paramErrors[param.name] }"
                        :placeholder="param.default"
                        :aria-describedby="`${param.name}-description ${param.name}-error`"
                      />
                      
                      <!-- Default value indicator and reset button -->
                      <div v-if="hasDefaultValue(param)" class="mt-1 flex items-center">
                        <button 
                          type="button" 
                          class="inline-flex items-center px-2 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                          @click="resetToDefault(param.name, param.default)"
                        >
                          <svg class="-ml-0.5 mr-1 h-3 w-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
                          </svg>
                          Reset to default
                        </button>
                        <span class="ml-2 text-xs text-gray-500">Default: {{ getDisplayDefault(param) }}</span>
                      </div>

                      <!-- Error message -->
                      <p v-if="paramErrors[param.name]" :id="`${param.name}-error`" class="mt-2 text-sm text-red-600">
                        {{ paramErrors[param.name] }}
                      </p>
                      
                      <!-- Value constraints hint -->
                      <p v-if="getConstraintHint(param)" :id="`${param.name}-description`" class="mt-2 text-xs text-gray-500">
                        {{ getConstraintHint(param) }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-sm text-gray-500">
                This notebook has no parameters.
              </div>

              <!-- Submit button -->
              <div class="pt-5">
                <div class="flex justify-end">
                  <button
                    type="submit"
                    class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    :disabled="executing"
                  >
                    <svg v-if="executing" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ executing ? 'Executing...' : 'Execute Notebook' }}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-12">
      <p class="text-gray-500">Notebook not found</p>
    </div>

    <!-- Duplicate execution modal -->
    <DuplicateExecutionModal
      :is-open="showDuplicateModal"
      :execution="duplicateExecution"
      @run-anyway="executeWithForceRun"
      @use-existing="duplicateModalClosed"
      @use-existing-error="duplicateModalError"
      @cancel="duplicateModalClosed"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotebooksStore } from '@/stores/notebooks'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { handleApiError } from '@/utils/errorHandler'
import { formatDate, formatFileSize } from '@/utils/format'
import { config } from '@/config'
import { getApiUrl } from '@/utils/env'
import DuplicateExecutionModal from '@/components/DuplicateExecutionModal.vue'

const route = useRoute()
const router = useRouter()
const notebooksStore = useNotebooksStore()

const notebook = ref(null)
const loading = ref(true)
const error = ref(null)
const executing = ref(false)
const paramErrors = ref({})
const showAdvancedDetails = ref(false)
const isInitialLoad = ref(true)
const skipNextUrlUpdate = ref(false)

// Form data for execution
const formData = reactive({
  pythonVersion: '3.9',
  cpuMilli: config.defaultResources.cpuMilli,
  memoryMib: config.defaultResources.memoryMib,
  parameters: {}
})

// For handling multiselect values
const multiSelectValues = reactive({})

// Get the API URL
const API_URL = getApiUrl()

// Download link
const downloadUrl = computed(() => {
  if (notebook.value) {
    // Just use the original path exactly as it comes from the server
    const path = notebook.value.path;
    
    // Log the path we're using
    console.log(`Using notebook path for download: ${path}`);
    
    // Encode the path as a query parameter
    return `${API_URL}/notebooks/download?path=${encodeURIComponent(path)}`;
  }
  return '';
})

// Add this reactive variable for download status
const downloadStatus = ref('')

// Initialize form data when notebook is loaded
watch(() => notebook.value, (newNotebook) => {
  if (!newNotebook) return
  
  // Set Python version
  formData.pythonVersion = newNotebook.python_version || config.supportedPythonVersions[0]
  
  // Initialize parameters with default values
  if (newNotebook.parameters) {
    newNotebook.parameters.forEach(param => {
      // Parse default value based on type
      let defaultValue = param.default
      
      if (param.type === 'bool' || param.input_type === 'checkbox') {
        defaultValue = defaultValue === 'True' || defaultValue === true
      } else if (param.type === 'int') {
        defaultValue = parseInt(defaultValue, 10)
      } else if (param.type === 'float') {
        defaultValue = parseFloat(defaultValue)
      } else if (param.input_type === 'multiselect') {
        try {
          // Handle array default values
          if (typeof defaultValue === 'string' && defaultValue.startsWith('[')) {
            defaultValue = JSON.parse(defaultValue.replace(/'/g, '"'))
          }
          // Initialize multiselect values
          multiSelectValues[param.name] = Array.isArray(defaultValue) ? [...defaultValue] : []
        } catch (e) {
          multiSelectValues[param.name] = []
        }
      } else if (typeof defaultValue === 'string') {
        // Remove quotes from string defaults
        defaultValue = defaultValue.replace(/^["']|["']$/g, '')
      }
      
      formData.parameters[param.name] = defaultValue
    })
  }
  
  // Apply URL parameters after setting defaults
  if (isInitialLoad.value) {
    applyUrlParamsToForm()
    isInitialLoad.value = false
  }
}, { immediate: true })

// Update formData when multiSelectValues change
watch(multiSelectValues, (newValues) => {
  for (const [key, value] of Object.entries(newValues)) {
    formData.parameters[key] = value
  }
}, { deep: true })

// Watch for changes to form parameters and update URL
watch(() => formData.parameters, (newParams) => {
  if (!notebook.value || isInitialLoad.value || skipNextUrlUpdate.value) {
    skipNextUrlUpdate.value = false
    return
  }
  
  updateUrlWithFormParams()
}, { deep: true })

// Watch for changes to multiSelectValues and update URL
watch(multiSelectValues, () => {
  if (!notebook.value || isInitialLoad.value || skipNextUrlUpdate.value) {
    skipNextUrlUpdate.value = false
    return
  }
  
  updateUrlWithFormParams()
}, { deep: true })

onMounted(async () => {
  try {
    loading.value = true
    
    notebook.value = await notebooksStore.fetchNotebook(route.params.path);
  } catch (err) {
    error.value = handleApiError(err);
  } finally {
    loading.value = false;
  }
})

// Function to update URL with current form parameters
function updateUrlWithFormParams() {
  const query = { ...route.query }
  
  // Only include parameters that have values different from defaults
  if (notebook.value && notebook.value.parameters) {
    notebook.value.parameters.forEach(param => {
      const value = formData.parameters[param.name]
      const defaultValue = param.default
      
      // Skip if value is the same as default
      if (value === defaultValue) {
        delete query[param.name]
        return
      }
      
      // Handle different parameter types
      if (param.input_type === 'multiselect') {
        // For multiselect, store as JSON string
        const multiValue = multiSelectValues[param.name]
        if (multiValue && multiValue.length > 0) {
          query[param.name] = JSON.stringify(multiValue)
        } else {
          delete query[param.name]
        }
      } else if (param.type === 'bool' || param.input_type === 'checkbox') {
        // For boolean, store as string 'true' or 'false'
        query[param.name] = value ? 'true' : 'false'
      } else if (value !== undefined && value !== null && value !== '') {
        // For other types, store as string
        query[param.name] = String(value)
      } else {
        delete query[param.name]
      }
    })
  }
  
  // Update URL without triggering navigation
  router.replace({ 
    query 
  }, { 
    replace: true 
  })
}

// Function to apply URL parameters to form
function applyUrlParamsToForm() {
  if (!notebook.value || !notebook.value.parameters || !route.query) return
  
  skipNextUrlUpdate.value = true
  
  // Get parameter definitions for validation
  const paramDefs = {}
  notebook.value.parameters.forEach(param => {
    paramDefs[param.name] = param
  })
  
  // Apply each URL parameter if it's a valid parameter for this notebook
  Object.entries(route.query).forEach(([key, value]) => {
    if (paramDefs[key]) {
      const param = paramDefs[key]
      
      try {
        // Parse value based on parameter type
        if (param.type === 'int') {
          formData.parameters[key] = parseInt(value, 10)
        } else if (param.type === 'float') {
          formData.parameters[key] = parseFloat(value)
        } else if (param.type === 'bool' || param.input_type === 'checkbox') {
          formData.parameters[key] = value === 'true'
        } else if (param.input_type === 'multiselect') {
          try {
            const parsedValue = JSON.parse(value)
            if (Array.isArray(parsedValue)) {
              // Validate against available options
              if (param.options) {
                const validValues = parsedValue.filter(v => param.options.includes(v))
                multiSelectValues[key] = validValues
                formData.parameters[key] = validValues
              } else {
                multiSelectValues[key] = parsedValue
                formData.parameters[key] = parsedValue
              }
            }
          } catch (e) {
            console.error(`Failed to parse multiselect value for ${key}:`, e)
          }
        } else {
          // For text, select, etc.
          formData.parameters[key] = value
        }
        
        // Validate the parsed value
        if (param.validation) {
          const val = formData.parameters[key]
          if (param.validation.min !== undefined && val < param.validation.min) {
            formData.parameters[key] = param.validation.min
          }
          if (param.validation.max !== undefined && val > param.validation.max) {
            formData.parameters[key] = param.validation.max
          }
        }
      } catch (e) {
        console.error(`Failed to apply URL parameter ${key}:`, e)
      }
    }
  })
}

// Validate form before submission
function validateForm() {
  const errors = {}
  
  if (!notebook.value || !notebook.value.parameters) {
    return true
  }
  
  notebook.value.parameters.forEach(param => {
    const value = formData.parameters[param.name]
    
    // Required validation
    if (param.validation?.required && (value === undefined || value === null || value === '')) {
      errors[param.name] = 'This field is required'
    }
    
    // Type validation
    if (value !== undefined && value !== null && value !== '') {
      if (param.type === 'int' && !Number.isInteger(Number(value))) {
        errors[param.name] = 'Must be an integer'
      } else if (param.type === 'float' && isNaN(Number(value))) {
        errors[param.name] = 'Must be a number'
      }
    }
    
    // Min/max validation
    if (param.validation) {
      if (param.validation.min !== undefined && value < param.validation.min) {
        errors[param.name] = `Minimum value is ${param.validation.min}`
      }
      if (param.validation.max !== undefined && value > param.validation.max) {
        errors[param.name] = `Maximum value is ${param.validation.max}`
      }
    }
  })
  
  paramErrors.value = errors
  return Object.keys(errors).length === 0
}

// State for duplicate execution handling
const showDuplicateModal = ref(false)
const duplicateExecution = ref(null)

async function executeNotebook() {
  if (!validateForm()) {
    return
  }
  
  executing.value = true
  error.value = null
  
  try {
    const result = await notebooksStore.executeNotebook(notebook.value.path, {
      pythonVersion: formData.pythonVersion,
      cpuMilli: formData.cpuMilli,
      memoryMib: formData.memoryMib,
      parameters: formData.parameters
    })
    
    // Check if a duplicate was found
    if (result.isDuplicate) {
      // If we have a duplicateExecution with an ID, store it for the modal
      if (result.duplicateExecution && result.duplicateExecution.id) {
        console.log('Duplicate execution found with ID:', result.duplicateExecution.id);
        duplicateExecution.value = result.duplicateExecution;
        showDuplicateModal.value = true;
      } else {
        console.error('Duplicate execution response missing execution details:', result);
        error.value = 'Duplicate execution found but details are missing';
      }
      executing.value = false;
      return;
    }
    
    // Ensure we have a valid execution ID before navigating
    if (!result.execution || !result.execution.id) {
      console.error('Error: Missing execution ID in response', result);
      error.value = 'Failed to get execution ID from server response';
      executing.value = false;
      return;
    }
    
    console.log('Navigating to execution detail with ID:', result.execution.id);
    
    // Navigate to execution detail page for the new execution
    router.push({ name: 'execution-detail', params: { id: result.execution.id } })
  } catch (err) {
    console.error('Error executing notebook:', err);
    error.value = handleApiError(err);
    executing.value = false;
  }
}

// Handle force run when duplicate is found
async function executeWithForceRun() {
  showDuplicateModal.value = false
  
  executing.value = true
  error.value = null
  
  try {
    console.log('Executing notebook with force_rerun=true')
    
    // Create execution with force_rerun flag
    const result = await notebooksStore.executeNotebook(notebook.value.path, {
      pythonVersion: formData.pythonVersion,
      cpuMilli: formData.cpuMilli,
      memoryMib: formData.memoryMib,
      parameters: formData.parameters,
      force_rerun: true // Force the execution to run even if duplicate exists
    })
    
    console.log('Force rerun result:', result)
    
    // If we still get a duplicate response, there might be an issue with the backend
    if (result.isDuplicate) {
      console.warn('Still received duplicate response despite force_rerun=true', result)
      
      if (result.duplicateExecution && result.duplicateExecution.id) {
        // We have a duplicate execution ID, proceed with it
        console.log('Using duplicate execution ID despite force_rerun:', result.duplicateExecution.id)
        executing.value = false
        router.push({ name: 'execution-detail', params: { id: result.duplicateExecution.id } })
      } else {
        // Handle the error condition
        console.error('No execution ID in duplicate response')
        error.value = 'Could not force rerun - no execution ID received'
        executing.value = false
      }
      return
    }
    
    // Ensure we have a valid execution ID before navigating
    if (!result.execution || !result.execution.id) {
      console.error('Error: Missing execution ID in response', result)
      error.value = 'Failed to get execution ID from server response'
      executing.value = false
      return
    }
    
    console.log('Navigating to execution detail with ID:', result.execution.id)
    
    // Navigate to execution detail page
    executing.value = false
    router.push({ name: 'execution-detail', params: { id: result.execution.id } })
  } catch (err) {
    console.error('Error executing notebook:', err);
    error.value = handleApiError(err);
    executing.value = false;
  }
}

// Close the duplicate modal
function duplicateModalClosed() {
  console.log('Duplicate modal closed');
  showDuplicateModal.value = false;
  
  // Don't immediately clear the duplicateExecution as it may be needed for navigation
  // We'll clear it after we're sure navigation is complete or not needed
  setTimeout(() => {
    duplicateExecution.value = null;
  }, 500);
}

// Handle error when trying to use existing execution
function duplicateModalError() {
  showDuplicateModal.value = false;
  duplicateExecution.value = null;
  error.value = 'Could not navigate to the existing execution. Details are missing.';
}

// Add the new helper functions
// Get type icon path for parameter
function getTypeIcon(param) {
  const type = param.type || (param.input_type === 'number' ? 'number' : 'string');
  
  switch (type) {
    case 'int':
    case 'float':
    case 'number':
      return 'M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V4a2 2 0 00-2-2H6zm1 2a1 1 0 000 2h6a1 1 0 100-2H7zm0 3a1 1 0 000 2h6a1 1 0 100-2H7zm0 3a1 1 0 100 2h6a1 1 0 100-2H7z';
    case 'bool':
      return 'M10 2a8 8 0 100 16 8 8 0 000-16zm0 2a6 6 0 110 12zm-1 5v4a1 1 0 102 0V9a1 1 0 10-2 0zm1-3a1 1 0 100 2 1 1 0 000-2z';
    case 'date':
      return 'M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z';
    default:
      return 'M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z';
  }
}

function getTypeDescription(param) {
  const type = param.type || (param.input_type === 'number' ? 'number' : 'string');
  
  if (param.input_type === 'multiselect') {
    return 'Multiple choice - select one or more options';
  } else if (param.input_type === 'select') {
    return 'Single choice - select one option';
  }
  
  switch (type) {
    case 'int':
      return 'Integer number';
    case 'float':
      return 'Decimal number';
    case 'bool':
      return 'Boolean (true/false)';
    case 'date':
      return 'Date value';
    case 'List[str]':
      return 'List of text values';
    default:
      return 'Text value';
  }
}

function getConstraintHint(param) {
  const validation = param.validation;
  if (!validation) return '';
  
  const hints = [];
  
  if (validation.required) {
    hints.push('Required');
  }
  
  if (validation.min !== undefined) {
    if (param.input_type === 'date') {
      hints.push(`Minimum date: ${validation.min}`);
    } else {
      hints.push(`Minimum value: ${validation.min}`);
    }
  }
  
  if (validation.max !== undefined) {
    if (param.input_type === 'date') {
      hints.push(`Maximum date: ${validation.max}`);
    } else {
      hints.push(`Maximum value: ${validation.max}`);
    }
  }
  
  return hints.join(' • ');
}

function hasDefaultValue(param) {
  const currentValue = formData.parameters[param.name];
  let defaultValue = param.default;
  
  // Handle different types for comparison
  if (param.type === 'bool' || param.input_type === 'checkbox') {
    defaultValue = defaultValue === 'True' || defaultValue === true;
  } else if (param.type === 'int') {
    defaultValue = parseInt(defaultValue, 10);
  } else if (param.type === 'float') {
    defaultValue = parseFloat(defaultValue);
  } else if (typeof defaultValue === 'string') {
    defaultValue = defaultValue.replace(/^["']|["']$/g, '');
  }
  
  return currentValue !== defaultValue;
}

function getDisplayDefault(param) {
  let defaultValue = param.default;
  
  if (param.type === 'bool' || param.input_type === 'checkbox') {
    return defaultValue === 'True' || defaultValue === true ? 'Yes' : 'No';
  } else if (param.input_type === 'multiselect') {
    try {
      if (typeof defaultValue === 'string' && defaultValue.startsWith('[')) {
        defaultValue = JSON.parse(defaultValue.replace(/'/g, '"'));
      }
      return Array.isArray(defaultValue) ? defaultValue.join(', ') : defaultValue;
    } catch (e) {
      return defaultValue;
    }
  }
  
  return defaultValue;
}

function resetToDefault(paramName, defaultValue) {
  const param = notebook.value.parameters.find(p => p.name === paramName);
  if (!param) return;
  
  let parsedDefault = defaultValue;
  
  if (param.type === 'bool' || param.input_type === 'checkbox') {
    parsedDefault = parsedDefault === 'True' || parsedDefault === true;
  } else if (param.type === 'int') {
    parsedDefault = parseInt(parsedDefault, 10);
  } else if (param.type === 'float') {
    parsedDefault = parseFloat(parsedDefault);
  } else if (param.input_type === 'multiselect') {
    try {
      if (typeof parsedDefault === 'string' && parsedDefault.startsWith('[')) {
        parsedDefault = JSON.parse(parsedDefault.replace(/'/g, '"'));
      }
      multiSelectValues[paramName] = Array.isArray(parsedDefault) ? [...parsedDefault] : [];
    } catch (e) {
      multiSelectValues[paramName] = [];
    }
  } else if (typeof parsedDefault === 'string') {
    parsedDefault = parsedDefault.replace(/^["']|["']$/g, '');
  }
  
  formData.parameters[paramName] = parsedDefault;
}

function removeMultiSelectValue(paramName, value) {
  if (multiSelectValues[paramName]) {
    multiSelectValues[paramName] = multiSelectValues[paramName].filter(v => v !== value);
  }
}

// Real-time validation
function validateParam(paramName) {
  if (!notebook.value) return;
  
  const param = notebook.value.parameters.find(p => p.name === paramName);
  if (!param) return;
  
  const value = formData.parameters[paramName];
  
  // Required validation
  if (param.validation?.required && (value === undefined || value === null || value === '')) {
    paramErrors.value[paramName] = 'This field is required';
    return;
  }
  
  // Type validation
  if (value !== undefined && value !== null && value !== '') {
    if (param.type === 'int' && !Number.isInteger(Number(value))) {
      paramErrors.value[paramName] = 'Must be an integer';
      return;
    } else if (param.type === 'float' && isNaN(Number(value))) {
      paramErrors.value[paramName] = 'Must be a number';
      return;
    }
  }
  
  // Min/max validation
  if (param.validation) {
    if (param.validation.min !== undefined && value < param.validation.min) {
      paramErrors.value[paramName] = `Minimum value is ${param.validation.min}`;
      return;
    }
    if (param.validation.max !== undefined && value > param.validation.max) {
      paramErrors.value[paramName] = `Maximum value is ${param.validation.max}`;
      return;
    }
  }
  
  // If we get here, validation passed
  delete paramErrors.value[paramName];
}

// Add watchers for real-time validation
watch(() => formData.parameters, (newValues, oldValues) => {
  // Find which parameter changed
  const changedParam = Object.keys(newValues).find(key => 
    JSON.stringify(newValues[key]) !== JSON.stringify(oldValues?.[key])
  );
  
  if (changedParam) {
    validateParam(changedParam);
  }
}, { deep: true });

async function downloadNotebook() {
  if (!notebook.value) return;
  
  try {
    // Set downloading status
    downloadStatus.value = 'downloading'
    error.value = null
    
    // Log the full URL for debugging
    console.log(`Download notebook path: ${notebook.value.path}`)
    console.log(`Requesting download from URL: ${downloadUrl.value}`)
    
    // Make authenticated axios request to get the file
    const response = await fetch(downloadUrl.value, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    if (!response.ok) {
      console.error(`Download failed with status: ${response.status} ${response.statusText}`)
      
      // Try to get error message from response
      let errorDetail = '';
      try {
        const errorBody = await response.json();
        errorDetail = errorBody.detail || JSON.stringify(errorBody);
        console.error('Error details:', errorDetail);
      } catch (e) {
        // If can't parse JSON, use whatever text is available
        errorDetail = await response.text();
        console.error('Error response text:', errorDetail);
      }
      
      throw new Error(`Download failed: ${response.status} ${response.statusText}${errorDetail ? ` - ${errorDetail}` : ''}`);
    }
    
    // Get the file content as blob
    const blob = await response.blob();
    console.log(`Successfully retrieved blob, size: ${blob.size} bytes`);
    
    // Create a temporary URL for the blob
    const url = window.URL.createObjectURL(blob);
    
    // Create a temporary link element to trigger download
    const link = document.createElement('a');
    link.href = url;
    
    // Get filename from path or response headers
    const contentDisposition = response.headers.get('content-disposition');
    let filename;
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
      filename = filenameMatch ? filenameMatch[1] : null;
      console.log(`Extracted filename from headers: ${filename}`);
    }
    
    if (!filename) {
      // Fall back to path-based filename
      const pathParts = notebook.value.path.split('/');
      filename = pathParts[pathParts.length - 1];
      if (!filename.endsWith('.ipynb')) {
        filename += '.ipynb';
      }
      console.log(`Using filename from path: ${filename}`);
    }
    
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    
    // Clean up
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    // Set success status
    downloadStatus.value = 'success'
    setTimeout(() => {
      downloadStatus.value = ''
    }, 3000)
  } catch (err) {
    console.error('Error downloading notebook:', err);
    error.value = `Failed to download: ${err.message}`;
    downloadStatus.value = 'error'
  }
}
</script> 

<style scoped>
/* Enhance focus states for accessibility */
input:focus, select:focus, textarea:focus {
  outline: 2px solid rgba(79, 70, 229, 0.2);
  outline-offset: 2px;
}

/* Smooth transitions */
input, select, textarea, button {
  transition: all 0.2s ease;
}

/* Better mobile experience */
@media (max-width: 640px) {
  input[type="date"], input[type="number"], select {
    font-size: 16px; /* Prevents iOS zoom on focus */
  }
}
</style> 