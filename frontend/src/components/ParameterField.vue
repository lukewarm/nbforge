<template>
  <div>
    <label :for="parameter.name" class="block text-sm font-medium text-gray-700">
      {{ parameter.name }}
      <span v-if="parameter.description" class="ml-1 text-gray-500">
        - {{ parameter.description }}
      </span>
    </label>

    <!-- Text input -->
    <input
      v-if="inputType === 'text'"
      :id="parameter.name"
      v-model="localValue"
      type="text"
      class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
      :class="{ 'border-red-300': error }"
    />

    <!-- Number input -->
    <input
      v-else-if="inputType === 'number'"
      :id="parameter.name"
      v-model.number="localValue"
      type="number"
      class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
      :class="{ 'border-red-300': error }"
      :min="parameter.validation?.min"
      :max="parameter.validation?.max"
      :step="parameter.validation?.step || 1"
    />

    <!-- Boolean input -->
    <div v-else-if="inputType === 'boolean'" class="mt-1">
      <div class="flex items-center">
        <input
          :id="parameter.name"
          v-model="localValue"
          type="checkbox"
          class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
        />
        <label :for="parameter.name" class="ml-2 block text-sm text-gray-900">
          {{ localValue ? 'Yes' : 'No' }}
        </label>
      </div>
    </div>

    <!-- Select input -->
    <select
      v-else-if="inputType === 'select'"
      :id="parameter.name"
      v-model="localValue"
      class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
      :class="{ 'border-red-300': error }"
    >
      <option v-for="option in parameter.options" :key="option.value" :value="option.value">
        {{ option.label || option.value }}
      </option>
    </select>

    <!-- JSON input -->
    <textarea
      v-else-if="inputType === 'json'"
      :id="parameter.name"
      v-model="jsonText"
      rows="4"
      class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
      :class="{ 'border-red-300': error }"
      @input="validateJson"
    ></textarea>

    <!-- Default fallback -->
    <input
      v-else
      :id="parameter.name"
      v-model="localValue"
      type="text"
      class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
      :class="{ 'border-red-300': error }"
    />

    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  parameter: {
    type: Object,
    required: true
  },
  modelValue: {
    type: [String, Number, Boolean, Object, Array],
    default: null
  },
  error: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'validation'])

// Determine input type based on parameter type and metadata
const inputType = computed(() => {
  if (props.parameter.input_type) {
    return props.parameter.input_type
  }
  
  // Infer from parameter type
  const type = props.parameter.type.toLowerCase()
  if (type.includes('int') || type.includes('float') || type.includes('number')) {
    return 'number'
  } else if (type.includes('bool')) {
    return 'boolean'
  } else if (type.includes('dict') || type.includes('list') || type.includes('object') || type.includes('array')) {
    return 'json'
  } else if (props.parameter.options && props.parameter.options.length > 0) {
    return 'select'
  }
  
  return 'text'
})

// For JSON input
const jsonText = ref('')

// Local value for v-model
const localValue = computed({
  get() {
    return props.modelValue !== undefined ? props.modelValue : props.parameter.default
  },
  set(value) {
    emit('update:modelValue', value)
  }
})

// Initialize JSON text if needed
watch(() => props.modelValue, (val) => {
  if (inputType.value === 'json' && val !== undefined) {
    try {
      jsonText.value = typeof val === 'string' ? val : JSON.stringify(val, null, 2)
    } catch (e) {
      jsonText.value = ''
    }
  }
}, { immediate: true })

// Validate JSON input
const validateJson = () => {
  let error = ''
  try {
    const parsed = JSON.parse(jsonText.value)
    emit('update:modelValue', parsed)
    error = ''
  } catch (e) {
    error = 'Invalid JSON format'
  }
  emit('validation', !error)
}

watch(() => props.parameter, validate, { deep: true })
watch(() => props.modelValue, validate)

function validate() {
  // Add validation logic here if needed
  emit('validation', true)
}
</script> 