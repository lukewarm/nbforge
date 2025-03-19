<template>
  <div>
    <div class="flex items-center justify-center w-full">
      <label
        class="flex flex-col w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer hover:bg-gray-50"
        @dragover.prevent="onDragOver"
        @dragleave.prevent="onDragLeave"
        @drop.prevent="onDrop"
        :class="{ 'border-indigo-500 bg-indigo-50': isDragging }"
      >
        <div class="flex flex-col items-center justify-center pt-5 pb-6">
          <svg
            class="w-8 h-8 mb-3 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            ></path>
          </svg>
          <p class="mb-1 text-sm text-gray-500">
            <span class="font-semibold">Click to upload</span> or drag and drop
          </p>
          <p class="text-xs text-gray-500">Jupyter Notebook (.ipynb)</p>
        </div>
        <input
          type="file"
          class="hidden"
          accept=".ipynb"
          @change="handleFileChange"
          ref="fileInput"
        />
      </label>
    </div>
    <div v-if="error" class="mt-2 text-sm text-red-600">
      {{ error }}
    </div>
    <div v-if="selectedFile" class="mt-4">
      <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
        <div class="flex items-center">
          <svg
            class="w-6 h-6 text-indigo-600 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            ></path>
          </svg>
          <span class="text-sm font-medium text-gray-900">{{ selectedFile.name }}</span>
        </div>
        <button
          type="button"
          @click="clearFile"
          class="text-gray-400 hover:text-gray-500"
        >
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>
      </div>
      <div class="mt-4">
        <button
          type="button"
          @click="uploadFile"
          :disabled="uploading"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          <svg
            v-if="uploading"
            class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          {{ uploading ? 'Uploading...' : 'Upload Notebook' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useNotebooksStore } from '@/stores/notebooks'
import { handleApiError } from '@/utils/errorHandler'

const notebooksStore = useNotebooksStore()
const fileInput = ref(null)
const selectedFile = ref(null)
const error = ref(null)
const uploading = ref(false)
const isDragging = ref(false)

const emit = defineEmits(['uploaded'])

function onDragOver(event) {
  isDragging.value = true
}

function onDragLeave(event) {
  isDragging.value = false
}

function onDrop(event) {
  isDragging.value = false
  const files = event.dataTransfer.files
  if (!files || files.length === 0) {
    return
  }

  const file = files[0]
  if (!file.name.endsWith('.ipynb')) {
    error.value = 'Please select a valid Jupyter Notebook (.ipynb) file'
    return
  }

  selectedFile.value = file
  error.value = null
}

function handleFileChange(event) {
  const files = event.target.files
  if (!files || files.length === 0) {
    return
  }

  const file = files[0]
  if (!file.name.endsWith('.ipynb')) {
    error.value = 'Please select a valid Jupyter Notebook (.ipynb) file'
    return
  }

  selectedFile.value = file
  error.value = null
}

function clearFile() {
  selectedFile.value = null
  error.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function uploadFile() {
  if (!selectedFile.value) {
    error.value = 'Please select a file to upload'
    return
  }

  uploading.value = true
  error.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    await notebooksStore.uploadNotebook(formData)
    emit('uploaded')
    clearFile()
  } catch (err) {
    error.value = handleApiError(err)
  } finally {
    uploading.value = false
  }
}
</script> 