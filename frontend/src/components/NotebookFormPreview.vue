<template>
  <div class="rounded-md bg-white p-6 shadow-md">
    <div class="mb-4">
      <h3 class="text-lg font-medium leading-6 text-gray-900">Form Preview</h3>
      <p class="mt-1 text-sm text-gray-500">This is how the form will appear to users. You can interact with it to test validation.</p>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-500"></div>
      <span class="ml-2 text-gray-600">Loading form preview...</span>
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

    <div v-else-if="!parameters || parameters.length === 0" class="text-center py-6">
      <p class="text-gray-600">This notebook has no parameters to display.</p>
    </div>
    
    <div v-else class="space-y-6">
      <!-- Parameter Form -->
      <form @submit.prevent="validateForm" class="space-y-6">
        <div v-for="(param, index) in parameters" :key="param.name" class="sm:grid sm:grid-cols-3 sm:gap-4 sm:items-start sm:border-t sm:border-gray-200 sm:pt-5" :class="{'sm:border-t-0 sm:pt-0': index === 0}">
          <!-- Label and description -->
          <div>
            <label :for="param.name" class="block text-sm font-medium text-gray-700 sm:mt-px sm:pt-2">
              {{ param.display_name || param.name }}
              <span v-if="param.validation && param.validation.required" class="text-red-500 ml-1">*</span>
            </label>
            <p v-if="param.description" class="mt-1 text-sm text-gray-500" :id="`${param.name}-description`">
              {{ param.description }}
            </p>
            <p class="mt-1 text-sm text-gray-500">
              <span class="inline-flex items-center">
                <svg class="h-4 w-4 text-gray-400 mr-1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path :d="getTypeIcon(param)" />
                </svg>
                {{ getTypeDescription(param) }}
              </span>
              <span v-if="getConstraintHint(param)" class="block mt-1 text-xs text-gray-500">
                {{ getConstraintHint(param) }}
              </span>
            </p>
          </div>

          <!-- Input field -->
          <div class="mt-1 sm:mt-0 sm:col-span-2">
            <!-- Text input -->
            <input
              v-if="param.input_type === 'text' || !param.input_type"
              :id="param.name"
              v-model="formData.parameters[param.name]"
              type="text"
              class="max-w-lg block w-full shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:max-w-xs sm:text-sm border-gray-300 rounded-md"
              :class="{ 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500': paramErrors[param.name] }"
              :placeholder="param.placeholder || ''"
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
              :step="param.type === 'float' ? 'any' : 1"
              :min="param.validation?.min"
              :max="param.validation?.max"
              :placeholder="param.placeholder || ''"
              :aria-describedby="`${param.name}-description ${param.name}-error`"
            />
            
            <!-- Date input -->
            <div v-else-if="param.input_type === 'date'" class="max-w-lg relative rounded-md shadow-sm sm:max-w-xs">
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
              class="max-w-lg shadow-sm block w-full focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border border-gray-300 rounded-md"
              :class="{ 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500': paramErrors[param.name] }"
              :placeholder="param.placeholder || ''"
              :aria-describedby="`${param.name}-description ${param.name}-error`"
            ></textarea>

            <!-- Default value display -->
            <div v-if="hasDefaultValue(param)" class="mt-1 text-xs text-gray-500">
              Default: {{ getDisplayDefault(param) }}
              <button 
                type="button" 
                class="ml-1 text-xs text-indigo-600 hover:text-indigo-800 focus:outline-none focus:underline"
                @click="resetToDefault(param.name, param.default)"
              >
                Reset
              </button>
            </div>

            <!-- Validation error message -->
            <p v-if="paramErrors[param.name]" class="mt-2 text-sm text-red-600" :id="`${param.name}-error`">
              {{ paramErrors[param.name] }}
            </p>
          </div>
        </div>

        <div class="pt-5 border-t border-gray-200 flex justify-end space-x-3">
          <button
            type="button"
            class="py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            @click="$emit('close')"
          >
            Close
          </button>
          <button
            type="submit"
            class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Test Form
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'

const props = defineProps({
  notebookMetadata: {
    type: Object,
    required: true
  },
})

const emit = defineEmits(['close'])

// State
const loading = ref(false)
const error = ref(null)
const parameters = ref([])
const paramErrors = ref({})

// Form data
const formData = reactive({
  parameters: {}
})

// For handling multiselect values
const multiSelectValues = reactive({})

// Watch for changes to the notebook metadata
watch(() => props.notebookMetadata, (newMetadata) => {
  if (!newMetadata) return
  
  // Extract parameters from metadata
  parameters.value = newMetadata.parameters || []
  
  // Initialize form data with default values
  initializeFormData()
}, { immediate: true })

// Initialize form data
function initializeFormData() {
  if (!parameters.value.length) return
  
  // Reset form data
  formData.parameters = {}
  
  // Initialize parameters with default values
  parameters.value.forEach(param => {
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

// Form validation
function validateForm() {
  paramErrors.value = {}
  let isValid = true
  
  parameters.value.forEach(param => {
    const value = formData.parameters[param.name]
    const validation = param.validation || {}
    
    // Check required fields
    if (validation.required && (value === undefined || value === null || value === '')) {
      paramErrors.value[param.name] = `${param.display_name || param.name} is required`
      isValid = false
      return
    }
    
    // Skip validation if empty and not required
    if (value === undefined || value === null || value === '') {
      return
    }
    
    // Validate by type
    if (param.type === 'int' || param.type === 'float') {
      if (typeof value !== 'number' || isNaN(value)) {
        paramErrors.value[param.name] = `${param.display_name || param.name} must be a valid number`
        isValid = false
        return
      }
      
      if (validation.min !== undefined && value < validation.min) {
        paramErrors.value[param.name] = `${param.display_name || param.name} must be at least ${validation.min}`
        isValid = false
        return
      }
      
      if (validation.max !== undefined && value > validation.max) {
        paramErrors.value[param.name] = `${param.display_name || param.name} must be at most ${validation.max}`
        isValid = false
        return
      }
    }
  })
  
  if (!isValid) {
    error.value = 'Please fix the validation errors in the form'
  } else {
    error.value = null
    // Show success message
    alert('Form validation passed! All parameters are valid.')
  }
  
  return isValid
}

// Helper functions
function removeMultiSelectValue(paramName, value) {
  const index = multiSelectValues[paramName].indexOf(value)
  if (index !== -1) {
    multiSelectValues[paramName].splice(index, 1)
  }
}

function getTypeIcon(param) {
  const type = param.type || (param.input_type === 'number' ? 'number' : 'string')
  
  switch (type) {
    case 'int':
    case 'float':
    case 'number':
      return 'M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V4a2 2 0 00-2-2H6zm1 2a1 1 0 000 2h6a1 1 0 100-2H7zm0 3a1 1 0 000 2h6a1 1 0 100-2H7zm0 3a1 1 0 100 2h6a1 1 0 100-2H7z'
    case 'bool':
      return 'M10 2a8 8 0 100 16 8 8 0 000-16zm0 2a6 6 0 110 12zm-1 5v4a1 1 0 102 0V9a1 1 0 10-2 0zm1-3a1 1 0 100 2 1 1 0 000-2z'
    case 'date':
      return 'M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z'
    default:
      return 'M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z'
  }
}

function getTypeDescription(param) {
  const type = param.type || (param.input_type === 'number' ? 'number' : 'string')
  
  switch (type) {
    case 'string':
      return 'Text value'
    case 'int':
      return 'Integer number'
    case 'float':
      return 'Decimal number'
    case 'bool':
      return 'Boolean (true/false)'
    case 'date':
      return 'Date value'
    case 'List[str]':
      return 'List of text values'
    default:
      return 'Text value'
  }
}

function getConstraintHint(param) {
  const validation = param.validation
  if (!validation) return ''
  
  const hints = []
  
  if (validation.required) {
    hints.push('Required')
  }
  
  if (validation.min !== undefined) {
    if (param.input_type === 'date') {
      hints.push(`Minimum date: ${validation.min}`)
    } else {
      hints.push(`Minimum value: ${validation.min}`)
    }
  }
  
  if (validation.max !== undefined) {
    if (param.input_type === 'date') {
      hints.push(`Maximum date: ${validation.max}`)
    } else {
      hints.push(`Maximum value: ${validation.max}`)
    }
  }
  
  return hints.join(' • ')
}

function hasDefaultValue(param) {
  const currentValue = formData.parameters[param.name]
  let defaultValue = param.default
  
  // Handle different types for comparison
  if (param.type === 'bool' || param.input_type === 'checkbox') {
    defaultValue = defaultValue === 'True' || defaultValue === true
  } else if (param.type === 'int') {
    defaultValue = parseInt(defaultValue, 10)
  } else if (param.type === 'float') {
    defaultValue = parseFloat(defaultValue)
  } else if (typeof defaultValue === 'string') {
    defaultValue = defaultValue.replace(/^["']|["']$/g, '')
  }
  
  return currentValue !== defaultValue
}

function getDisplayDefault(param) {
  let defaultValue = param.default
  
  if (param.type === 'bool' || param.input_type === 'checkbox') {
    return defaultValue === 'True' || defaultValue === true ? 'Yes' : 'No'
  } else if (param.input_type === 'multiselect') {
    try {
      if (typeof defaultValue === 'string' && defaultValue.startsWith('[')) {
        defaultValue = JSON.parse(defaultValue.replace(/'/g, '"'))
      }
      return Array.isArray(defaultValue) ? defaultValue.join(', ') : defaultValue
    } catch (e) {
      return defaultValue
    }
  }
  
  return defaultValue
}

function resetToDefault(paramName, defaultValue) {
  const param = parameters.value.find(p => p.name === paramName)
  if (!param) return
  
  let parsedDefault = defaultValue
  
  if (param.type === 'bool' || param.input_type === 'checkbox') {
    parsedDefault = parsedDefault === 'True' || parsedDefault === true
  } else if (param.type === 'int') {
    parsedDefault = parseInt(parsedDefault, 10)
  } else if (param.type === 'float') {
    parsedDefault = parseFloat(parsedDefault)
  } else if (param.input_type === 'multiselect') {
    try {
      if (typeof parsedDefault === 'string' && parsedDefault.startsWith('[')) {
        parsedDefault = JSON.parse(parsedDefault.replace(/'/g, '"'))
      }
      multiSelectValues[paramName] = Array.isArray(parsedDefault) ? [...parsedDefault] : []
    } catch (e) {
      multiSelectValues[paramName] = []
    }
  }
  
  formData.parameters[paramName] = parsedDefault
}
</script> 