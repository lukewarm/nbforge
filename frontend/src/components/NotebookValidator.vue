<template>
  <div>
    <!-- File Upload Section -->
    <div v-if="!validatedNotebook" class="mb-6">
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
            <span class="text-sm font-medium text-gray-900">
              {{ selectedFile.name }}
            </span>
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
            @click="prepareNotebook"
            :disabled="validating"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            <svg
              v-if="validating"
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
            {{ validating ? 'Processing...' : 'Process Notebook' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Metadata Editor Section -->
    <div v-if="validatedNotebook" class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6 flex justify-between">
        <div>
          <h3 class="text-lg leading-6 font-medium text-gray-900">
            Prepare Notebook for NBForge
          </h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">
            Configure your notebook's metadata to make it compatible with NBForge. Add parameters, resources and other settings.
          </p>
        </div>
        <button
          @click="resetValidation"
          class="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <svg class="-ml-0.5 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
          </svg>
          Upload Different Notebook
        </button>
      </div>
      <div class="border-t border-gray-200 px-4 py-5 sm:px-6">
        <form @submit.prevent="updateMetadata">
          <!-- Basic Information -->
          <div class="space-y-6">
            <div>
              <h4 class="text-sm font-medium text-gray-900">Basic Information</h4>
              <div class="mt-2 grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <div class="sm:col-span-4">
                  <label for="name" class="block text-sm font-medium text-gray-700">Name</label>
                  <div class="mt-1">
                    <input 
                      type="text" 
                      id="name" 
                      v-model="editedMetadata.name" 
                      class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    />
                  </div>
                </div>
                <div class="sm:col-span-6">
                  <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
                  <div class="mt-1">
                    <textarea 
                      id="description" 
                      v-model="editedMetadata.description" 
                      rows="3" 
                      class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    ></textarea>
                  </div>
                </div>
                <div class="sm:col-span-4">
                  <label for="python-version" class="block text-sm font-medium text-gray-700">Python Version</label>
                  <div class="mt-1">
                    <select 
                      id="python-version" 
                      v-model="editedMetadata.python_version" 
                      class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    >
                      <option value="3.8">Python 3.8</option>
                      <option value="3.9">Python 3.9</option>
                      <option value="3.10">Python 3.10</option>
                      <option value="3.11">Python 3.11</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <!-- Tags -->
            <div>
              <h4 class="text-sm font-medium text-gray-900">Tags</h4>
              <div class="mt-2">
                <div class="flex flex-wrap gap-2 mb-2">
                  <span 
                    v-for="(tag, index) in editedMetadata.tags" 
                    :key="index" 
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
                  >
                    {{ tag }}
                    <button 
                      type="button" 
                      @click="removeTag(index)" 
                      class="ml-1.5 inline-flex text-indigo-400 hover:text-indigo-600"
                    >
                      <svg class="h-3 w-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </span>
                </div>
                <div class="flex">
                  <input 
                    type="text" 
                    v-model="newTag" 
                    @keyup.enter="addTag" 
                    placeholder="Add a tag" 
                    class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  />
                  <button 
                    type="button" 
                    @click="addTag" 
                    class="ml-2 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>

            <!-- Parameters (Read-only) -->
            <div>
              <h4 class="text-sm font-medium text-gray-900">Parameters</h4>
              <div class="mt-2">
                <ul v-if="validatedNotebook.parameters && Array.isArray(validatedNotebook.parameters) && validatedNotebook.parameters.length > 0" class="border border-gray-200 rounded-md divide-y divide-gray-200">
                  <li v-for="param in validatedNotebook.parameters" :key="param.name" class="pl-3 pr-4 py-3 flex items-center justify-between text-sm">
                    <div class="w-0 flex-1 flex items-center">
                      <span class="ml-2 flex-1 w-0 truncate">
                        <span class="font-medium">{{ param.name }}</span>
                        <span v-if="param.type" class="text-gray-500"> ({{ param.type }})</span>
                        <span v-if="param.description" class="block text-gray-500">{{ param.description }}</span>
                      </span>
                    </div>
                    <div v-if="param.default !== undefined" class="ml-4 flex-shrink-0">
                      <span class="font-medium text-indigo-600">Default: {{ formatDefaultValue(param.default) }}</span>
                    </div>
                  </li>
                </ul>
                <p v-else class="text-sm text-gray-500">No parameters defined in this notebook.</p>
                
                <div class="mt-4 bg-blue-50 p-4 rounded-md">
                  <div class="flex">
                    <div class="flex-shrink-0">
                      <svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                      </svg>
                    </div>
                    <div class="ml-3 flex-1 md:flex md:justify-between">
                      <p class="text-sm text-blue-700">
                        Parameters must be updated directly in the notebook by modifying the parameters cell.
                      </p>
                    </div>
                  </div>
                  <div class="mt-3">
                    <p class="text-sm text-blue-700">
                      <strong>Parameter Examples:</strong>
                    </p>
                    <pre class="mt-2 text-xs bg-white p-2 rounded overflow-x-auto">
# Simple string parameter
name: str = "default_name"  # {"description": "Your name"}

# Numeric parameter with default
iterations: int = 100  # {"description": "Number of training iterations", "validation": {"min": 1, "max": 1000}}

# Choice parameter with dropdown options
model_type: str = "random_forest"  # {"description": "Type of model to use", "input_type": "select", "options": ["random_forest", "xgboost", "linear"]}

# Boolean parameter
use_cache: bool = True  # {"description": "Whether to use cached data"}

# Date parameter
analysis_date: str = "2024-01-01"  # {"description": "Date to analyze data for", "input_type": "date"}

# List parameter with multi-select
features: List[str] = ["col1", "col2"]  # {"description": "Features to use in model", "input_type": "multiselect", "options": ["col1", "col2", "col3", "col4"]}
                    </pre>
                  </div>
                </div>
              </div>
            </div>

            <!-- Requirements (Now Editable) -->
            <div>
              <h4 class="text-sm font-medium text-gray-900">Requirements</h4>
              <div class="mt-2">
                <div v-if="editedMetadata.requirements && Object.keys(editedMetadata.requirements).length > 0" class="mb-4">
                  <ul class="border border-gray-200 rounded-md divide-y divide-gray-200">
                    <li v-for="(version, pkgName) in editedMetadata.requirements" :key="pkgName" class="pl-3 pr-4 py-3 flex items-center justify-between text-sm">
                      <div class="w-0 flex-1 flex items-center">
                        <span class="ml-2 flex-1 w-0 truncate font-medium">{{ pkgName }}</span>
                      </div>
                      <div class="ml-4 flex flex-shrink-0 items-center">
                        <input 
                          type="text" 
                          v-model="editedMetadata.requirements[pkgName]" 
                          class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-24 sm:text-sm border-gray-300 rounded-md"
                        />
                        <button 
                          type="button" 
                          @click="removeRequirement(pkgName)" 
                          class="ml-2 text-red-400 hover:text-red-600"
                        >
                          <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                          </svg>
                        </button>
                      </div>
                    </li>
                  </ul>
                </div>
                <div v-else class="mb-2 text-sm text-gray-500">No requirements defined yet.</div>
                <div class="flex">
                  <input 
                    type="text" 
                    v-model="newRequirementName" 
                    placeholder="Package name" 
                    class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  />
                  <input 
                    type="text" 
                    v-model="newRequirementVersion" 
                    placeholder="Version" 
                    class="ml-2 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-32 sm:text-sm border-gray-300 rounded-md"
                  />
                  <button 
                    type="button" 
                    @click="addRequirement" 
                    class="ml-2 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>

            <!-- Submit/Update buttons -->
            <div class="pt-5 border-t border-gray-200">
              <div class="flex justify-end">
                <button
                  type="button"
                  @click="resetValidation"
                  class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  class="ml-3 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  @click="showFormPreview = true"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="-ml-1 mr-2 h-5 w-5 inline" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                    <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
                  </svg>
                  Preview Form
                </button>
                <button
                  type="submit"
                  :disabled="updating"
                  :class="{'opacity-50 cursor-not-allowed': updating}"
                  class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <svg v-if="updating" class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ updating ? 'Updating...' : 'Download Updated Notebook' }}
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Form Preview Modal -->
    <div v-if="showFormPreview" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showFormPreview = false"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-5xl sm:w-full">
          <NotebookFormPreview 
            :notebookMetadata="validatedNotebook" 
            @close="showFormPreview = false" 
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useNotebooksStore } from '@/stores/notebooks'
import { handleApiError } from '@/utils/errorHandler'
import NotebookFormPreview from '@/components/NotebookFormPreview.vue'

const notebooksStore = useNotebooksStore()
const fileInput = ref(null)
const selectedFile = ref(null)
const error = ref(null)
const validating = ref(false)
const updating = ref(false)
const newTag = ref('')
const newRequirementName = ref('')
const newRequirementVersion = ref('')
const isDragging = ref(false)
const showFormPreview = ref(false)

// Computed property to access the validated notebook from the store
const validatedNotebook = computed(() => notebooksStore.validatedNotebook)

// Reactive object for edited metadata
const editedMetadata = reactive({
  name: '',
  description: '',
  tags: [],
  python_version: '3.10',
  requirements: {}
})

// Watch for changes in validatedNotebook and update editedMetadata
watch(validatedNotebook, (newVal) => {
  console.log('validatedNotebook changed:', newVal);
  if (newVal) {
    updateEditedMetadata();
  }
}, { immediate: true });

// Update edited metadata from validated notebook
function updateEditedMetadata() {
  console.log('Updating edited metadata from:', validatedNotebook.value);
  if (validatedNotebook.value) {
    editedMetadata.name = validatedNotebook.value.name || '';
    editedMetadata.description = validatedNotebook.value.description || '';
    editedMetadata.tags = Array.isArray(validatedNotebook.value.tags) ? [...validatedNotebook.value.tags] : [];
    editedMetadata.python_version = validatedNotebook.value.python_version || '3.10';
    
    // Clone the requirements object
    editedMetadata.requirements = validatedNotebook.value.requirements ? 
      JSON.parse(JSON.stringify(validatedNotebook.value.requirements)) : {};
  }
}

// Ensure store state is properly initialized
onMounted(() => {
  // Reset validatedNotebook if it's in an inconsistent state
  if (notebooksStore.validatedNotebook === undefined) {
    notebooksStore.validatedNotebook = null;
  }
})

// Format default value based on type
const formatDefaultValue = (value) => {
  if (value === null) return 'null'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
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

async function prepareNotebook() {
  if (!selectedFile.value) {
    error.value = 'Please select a file first'
    return
  }

  error.value = null
  validating.value = true

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    // Call the validateNotebook API through the store (don't need to rename the API call)
    await notebooksStore.validateNotebook(formData)
    
    // Initialize edited metadata
    updateEditedMetadata()
  } catch (err) {
    error.value = handleApiError(err)
  } finally {
    validating.value = false
  }
}

function resetValidation() {
  notebooksStore.validatedNotebook = null
  clearFile()
}

function addTag() {
  if (newTag.value.trim() && !editedMetadata.tags.includes(newTag.value.trim())) {
    editedMetadata.tags.push(newTag.value.trim())
    newTag.value = ''
  }
}

function removeTag(index) {
  editedMetadata.tags.splice(index, 1)
}

function addRequirement() {
  if (!newRequirementName.value.trim()) {
    return;
  }
  
  if (!editedMetadata.requirements) {
    editedMetadata.requirements = {};
  }
  
  editedMetadata.requirements[newRequirementName.value.trim()] = newRequirementVersion.value.trim() || '*';
  
  // Reset inputs
  newRequirementName.value = '';
  newRequirementVersion.value = '';
}

function removeRequirement(packageName) {
  if (editedMetadata.requirements && packageName in editedMetadata.requirements) {
    delete editedMetadata.requirements[packageName];
  }
}

async function updateMetadata() {
  if (!selectedFile.value) {
    error.value = 'File not found'
    return
  }

  updating.value = true
  error.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('metadata', JSON.stringify(editedMetadata))
    
    const downloadUrl = await notebooksStore.updateNotebookMetadata(formData)
    
    // Create a download link and trigger it
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = selectedFile.value.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    // Clean up the URL object
    setTimeout(() => {
      window.URL.revokeObjectURL(downloadUrl)
    }, 100)
    
  } catch (err) {
    error.value = handleApiError(err)
  } finally {
    updating.value = false
  }
}

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
</script> 