<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="md:flex md:items-center md:justify-between mb-6">
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          Notebooks
        </h2>
      </div>
      <div class="mt-4 flex md:mt-0 md:ml-4">
        <button
          @click="showValidatorModal = true"
          type="button"
          class="ml-3 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
          Prepare a new notebook
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <loading-spinner message="Loading notebooks..." />
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

    <div v-else-if="notebooks.length === 0" class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No notebooks</h3>
      <p class="mt-1 text-sm text-gray-500">
        No notebooks found. Notebooks should be added through source control and CI.
      </p>
      <div class="mt-6">
        <button
          type="button"
          @click="showValidatorModal = true"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
          </svg>
          Prepare a new notebook
        </button>
      </div>
    </div>

    <div v-else>
      <!-- Search input -->
      <div class="mb-6">
        <div class="relative rounded-md shadow-sm">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
            </svg>
          </div>
          <input
            type="text"
            v-model="searchQuery"
            class="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md"
            placeholder="Search notebooks..."
          />
        </div>
      </div>

      <!-- Notebook list -->
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <ul class="divide-y divide-gray-200">
          <li v-for="notebook in paginatedNotebooks" :key="notebook.path">
            <div 
              class="px-4 py-4 sm:px-6 hover:bg-gray-50 cursor-pointer"
              @click="viewNotebook(notebook)"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0">
                  <router-link 
                    :to="{ name: 'notebook-detail', params: { path: notebook.path } }"
                    class="text-indigo-600 hover:text-indigo-900"
                    @click.stop
                  >
                    {{ notebook.name || notebook.path.split('/').pop() }}
                  </router-link>
                  <p class="mt-1 flex items-center text-sm text-gray-500">
                    <svg class="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
                    </svg>
                    <span class="truncate">{{ notebook.path }}</span>
                  </p>
                </div>
                <div class="ml-4 flex-shrink-0 flex">
                  <p class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                    {{ formatFileSize(notebook.size) }}
                  </p>
                </div>
              </div>
              <div class="mt-2 sm:flex sm:justify-between">
                <div class="sm:flex">
                  <p class="flex items-center text-sm text-gray-500">
                    <svg class="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
                    </svg>
                    {{ notebook.parameters ? notebook.parameters.length : 0 }} parameters
                  </p>
                </div>
                <div class="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                  <svg class="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                  </svg>
                  <p>
                    Last modified
                    <time>{{ formatDate(notebook.last_modified) }}</time>
                  </p>
                </div>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <!-- Pagination Controls -->
      <div v-if="filteredNotebooks.length > 0" class="px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-4">
        <div class="flex items-center">
          <span class="text-sm text-gray-700">
            Showing
            <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span>
            to
            <span class="font-medium">{{ Math.min(currentPage * pageSize, filteredNotebooks.length) }}</span>
            of
            <span class="font-medium">{{ filteredNotebooks.length }}</span>
            results
          </span>
          <div class="ml-4">
            <select
              v-model="pageSize"
              @change="changePageSize(pageSize)"
              class="ml-1 border-gray-300 rounded-md shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
            >
              <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }} per page</option>
            </select>
          </div>
        </div>
        <div class="flex-1 flex justify-center md:justify-end">
          <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
            <button
              @click="changePage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span class="sr-only">Previous</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
            
            <!-- First page number -->
            <button
              v-if="totalPages > 5 && currentPage > 3"
              @click="changePage(1)"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              1
            </button>
            
            <!-- Ellipsis if needed -->
            <span
              v-if="totalPages > 5 && currentPage > 3"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700"
            >
              ...
            </span>
            
            <!-- Page numbers around current page -->
            <button
              v-for="page in totalPages"
              :key="page"
              v-show="page === 1 || page === totalPages || 
                     (page >= currentPage - 1 && page <= currentPage + 1) ||
                     (totalPages <= 5)"
              @click="changePage(page)"
              :class="[
                'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                currentPage === page
                  ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              ]"
            >
              {{ page }}
            </button>
            
            <!-- Ellipsis if needed -->
            <span
              v-if="totalPages > 5 && currentPage < totalPages - 2"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700"
            >
              ...
            </span>
            
            <!-- Last page number -->
            <button
              v-if="totalPages > 5 && currentPage < totalPages - 2"
              @click="changePage(totalPages)"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              {{ totalPages }}
            </button>
            
            <button
              @click="changePage(currentPage + 1)"
              :disabled="currentPage === totalPages || totalPages === 0"
              class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span class="sr-only">Next</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
          </nav>
        </div>
      </div>
    </div>

    <!-- Validator Modal -->
    <modal-dialog v-if="showValidatorModal" @close="closeValidatorModal" :fullWidth="true">
      <template #title>Prepare a new notebook</template>
      <template #content>
        <notebook-validator />
      </template>
    </modal-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useNotebooksStore } from '@/stores/notebooks'
import { handleApiError } from '@/utils/errorHandler'
import { formatDate, formatFileSize } from '@/utils/format'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ModalDialog from '@/components/ModalDialog.vue'
import NotebookUpload from '@/components/NotebookUpload.vue'
import NotebookValidator from '@/components/NotebookValidator.vue'

const router = useRouter()
const notebooksStore = useNotebooksStore()

const loading = computed(() => notebooksStore.loading)
const error = ref(null)
const notebooks = computed(() => notebooksStore.notebooks)
const searchQuery = ref('')
const showUploadModal = ref(false)
const showValidatorModal = ref(false)

const currentPage = ref(1)
const pageSize = ref(10)
const pageSizeOptions = [10, 25, 50, 100]

const filteredNotebooks = computed(() => {
  if (!searchQuery.value) {
    return notebooks.value
  }
  
  const query = searchQuery.value.toLowerCase()
  return notebooks.value.filter(notebook => 
    notebook.name.toLowerCase().includes(query) || 
    notebook.path.toLowerCase().includes(query)
  )
})

const paginatedNotebooks = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return filteredNotebooks.value.slice(startIndex, endIndex)
})

const totalPages = computed(() => {
  return Math.ceil(filteredNotebooks.value.length / pageSize.value)
})

function viewNotebook(notebook) {
  router.push({ 
    name: 'notebook-detail', 
    params: { path: notebook.path }
  })
}

async function fetchNotebooks() {
  try {
    await notebooksStore.fetchNotebooks()
    error.value = null
  } catch (err) {
    error.value = handleApiError(err)
  }
}

function onNotebookUploaded() {
  showUploadModal.value = false
  fetchNotebooks()
}

function closeValidatorModal() {
  console.log('Closing validator modal, current validatedNotebook:', notebooksStore.validatedNotebook);
  showValidatorModal.value = false;
  notebooksStore.validatedNotebook = null;
  console.log('Reset validatedNotebook in store:', notebooksStore.validatedNotebook);
  fetchNotebooks();
}

function changePage(page) {
  currentPage.value = page
  // Scroll to top of list
  const listTop = document.querySelector('.divide-y')
  if (listTop) {
    listTop.scrollIntoView({ behavior: 'smooth' })
  }
}

function changePageSize(size) {
  pageSize.value = size
  // Reset to first page when changing page size
  currentPage.value = 1
}

watch(searchQuery, () => {
  currentPage.value = 1
})

onMounted(() => {
  console.log('NotebookList component mounted')
  fetchNotebooks()
})
</script> 