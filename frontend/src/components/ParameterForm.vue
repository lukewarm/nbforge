<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <div v-for="param in parameters" :key="param.name" class="space-y-2">
      <parameter-field
        v-model="formData[param.name]"
        :parameter="param"
        :error="errors[param.name]"
        @update:modelValue="clearError(param.name)"
        @validation="updateValidation(param.name, $event)"
      />
    </div>

    <div class="flex justify-end space-x-3 pt-5">
      <button
        type="button"
        @click="$emit('cancel')"
        class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Cancel
      </button>
      <button
        type="submit"
        :disabled="!isValid"
        class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Execute
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import ParameterField from './ParameterField.vue'

const props = defineProps({
  parameters: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['submit', 'cancel'])

const formData = reactive({})
const errors = reactive({})
const validations = reactive({})

// Initialize form data with default values
onMounted(() => {
  resetForm()
})

const isValid = computed(() => {
  // Check if all parameters are valid
  for (const param of props.parameters) {
    if (validations[param.name] === false) {
      return false
    }
  }
  return true
})

const updateValidation = (paramName, isValid) => {
  validations[paramName] = isValid
}

const clearError = (paramName) => {
  delete errors[paramName]
}

const handleSubmit = () => {
  // Validate all fields
  let hasErrors = false
  
  for (const param of props.parameters) {
    if (param.required && (formData[param.name] === undefined || formData[param.name] === null || formData[param.name] === '')) {
      errors[param.name] = `${param.name} is required`
      hasErrors = true
    }
  }
  
  if (hasErrors) {
    return
  }
  
  emit('submit', formData)
}

const resetForm = () => {
  for (const param of props.parameters) {
    formData[param.name] = param.default
  }
  Object.keys(errors).forEach(key => delete errors[key])
}
</script> 