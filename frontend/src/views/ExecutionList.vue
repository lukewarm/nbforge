<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <div class="md:flex md:items-center md:justify-between mb-6">
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          Executions
        </h2>
      </div>
      <div class="mt-4 flex md:mt-0 md:ml-4">
        <button
          @click="refreshExecutions"
          type="button"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- Improved Filters Panel -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Filter Executions</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label for="status-filter" class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select 
              id="status-filter" 
              v-model="statusFilter" 
              class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="">All statuses</option>
              <option value="pending">Pending</option>
              <option value="submitted">Submitted</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          
          <div>
            <label for="notebook-filter" class="block text-sm font-medium text-gray-700 mb-1">Notebook</label>
            <select 
              id="notebook-filter" 
              v-model="notebookFilter" 
              class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="">All notebooks</option>
              <option v-for="notebook in uniqueNotebooks" :key="notebook" :value="notebook">
                {{ getNotebookDisplayName({notebook_path: notebook}) }}
              </option>
            </select>
          </div>
          
          <div>
            <label for="search-filter" class="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input 
              type="text" 
              id="search-filter" 
              v-model="searchFilter" 
              placeholder="Search parameters or ID..." 
              class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
          </div>
          
          <div class="flex items-center md:col-span-3">
            <input 
              type="checkbox" 
              id="show-my-executions" 
              v-model="showMyExecutionsOnly" 
              class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            >
            <label for="show-my-executions" class="ml-2 block text-sm text-gray-900">
              Show only my executions
            </label>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="rounded-md bg-red-50 p-4 mb-6">
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

    <div v-if="loading" class="text-center py-12">
      <loading-spinner />
    </div>

    <div v-else-if="filteredExecutions.length === 0" class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No executions found</h3>
      <p class="mt-1 text-sm text-gray-500">
        Apply different filters or create a new execution.
      </p>
    </div>

    <div v-else class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Notebook
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Started
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Completed
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Duration
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Submitter
              </th>
              <th scope="col" class="relative px-6 py-3">
                <span class="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="execution in paginatedExecutions" :key="execution.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex flex-col">
                  <router-link :to="{ name: 'execution-detail', params: { id: execution.id } }" class="text-indigo-600 hover:text-indigo-900 font-medium">
                    {{ getNotebookDisplayName(execution) }}
                  </router-link>
                  <span v-if="execution.notebook_path" class="text-sm text-gray-500 mt-1 truncate">
                    {{ truncatePath(execution.notebook_path) }}
                  </span>
                  <!-- Show parameters as tags -->
                  <div v-if="execution.parameters && Object.keys(execution.parameters).length > 0" class="flex flex-wrap gap-1 mt-1">
                    <span 
                      v-for="(value, key) in formatCompactParameters(execution.parameters)" 
                      :key="key" 
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800 truncate max-w-xs"
                      :title="`${key}: ${value}`"
                    >
                      {{ key }}: {{ value }}
                    </span>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <!-- Status column with colorful badges -->
                <span 
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="{
                    'bg-gray-100 text-gray-800': execution.status === 'pending',
                    'bg-blue-100 text-blue-800': execution.status === 'submitted',
                    'bg-yellow-100 text-yellow-800': execution.status === 'running',
                    'bg-green-100 text-green-800': execution.status === 'completed',
                    'bg-red-100 text-red-800': execution.status === 'failed',
                    'bg-gray-100 text-gray-800': execution.status === 'cancelled'
                  }"
                >
                  {{ execution.status.charAt(0).toUpperCase() + execution.status.slice(1) }}
                  <svg 
                    v-if="execution.status === 'running'" 
                    class="animate-spin -mr-0.5 ml-1 h-3 w-3" 
                    xmlns="http://www.w3.org/2000/svg" 
                    fill="none" 
                    viewBox="0 0 24 24"
                  >
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span :title="formatDateTime(execution.created_at)">
                  {{ formatRelativeTime(execution.created_at) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span :title="formatDateTime(execution.started_at)">
                  {{ formatRelativeTime(execution.started_at) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span :title="formatDateTime(execution.completed_at)">
                  {{ formatRelativeTime(execution.completed_at) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ calculateDuration(execution.started_at, execution.completed_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div class="flex items-center">
                  <span v-if="execution.user" class="font-medium">
                    {{ execution.user.username }}
                  </span>
                  <span v-else-if="execution.service_account" class="font-medium text-purple-700">
                    API: {{ execution.service_account.name }}
                  </span>
                  <span v-else class="text-gray-400 italic">
                    System
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end space-x-2">
                  <!-- View in Results Viewer button -->
                  <router-link 
                    v-if="execution.status === 'completed' && execution.output_html"
                    :to="{ 
                      name: 'results-viewer', 
                      query: { 
                        path: execution.output_html,
                        notebookPath: execution.output_notebook
                      }
                    }"
                    class="text-indigo-600 hover:text-indigo-900 inline-flex items-center"
                  >
                    <svg class="mr-1 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
                    </svg>
                    View Results
                  </router-link>
                  
                  <!-- Download notebook button -->
                  <a 
                    v-if="execution.status === 'completed' && execution.output_notebook"
                    :href="getHtmlUrl(execution.output_notebook)" 
                    download
                    class="text-blue-600 hover:text-blue-900 inline-flex items-center"
                  >
                    <svg class="mr-1 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                    Notebook
                  </a>
                  
                  <!-- Cancel Button for running/pending/submitted executions -->
                  <button 
                    v-if="['pending', 'running', 'submitted'].includes(execution.status)"
                    @click="cancelExecution(execution.id)" 
                    :disabled="cancellingExecutions[execution.id]"
                    class="text-red-600 hover:text-red-900 inline-flex items-center"
                  >
                    <svg v-if="cancellingExecutions[execution.id]" class="animate-spin mr-1 h-5 w-5 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <svg v-else class="mr-1 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                    </svg>
                    {{ cancellingExecutions[execution.id] ? 'Cancelling...' : 'Cancel' }}
                  </button>
                  
                  <!-- Always show Details Button -->
                  <router-link 
                    :to="{ name: 'execution-detail', params: { id: execution.id } }"
                    class="text-indigo-600 hover:text-indigo-900 inline-flex items-center"
                  >
                    <svg class="mr-1 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                    </svg>
                    Details
                  </router-link>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Confirmation Modal for cancel execution -->
    <ConfirmationModal
      v-if="showCancelModal"
      title="Cancel Execution"
      message="Are you sure you want to cancel this execution? This action cannot be undone."
      confirmButtonText="Cancel Execution"
      cancelButtonText="Nevermind"
      @confirm="confirmCancelExecution"
      @cancel="closeConfirmModal"
    />

    <!-- Pagination Controls -->
    <div v-if="filteredExecutions.length > 0" class="px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
      <div class="flex items-center">
        <span class="text-sm text-gray-700">
          Showing
          <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span>
          to
          <span class="font-medium">{{ Math.min(currentPage * pageSize, filteredExecutions.length) }}</span>
          of
          <span class="font-medium">{{ filteredExecutions.length }}</span>
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
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useExecutionsStore } from '@/stores/executions'
import { useAuthStore } from '@/stores/auth'
import ExecutionStatus from '@/components/ExecutionStatus.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { handleApiError } from '@/utils/errorHandler'
import { getApiUrl } from '@/utils/env'
import ConfirmationModal from '@/components/ConfirmationModal.vue'

const router = useRouter()
const route = useRoute()
const executionsStore = useExecutionsStore()
const authStore = useAuthStore()

// Get the API URL
const API_URL = getApiUrl()

const statusFilter = ref('')
const showMyExecutionsOnly = ref(false)
const notebookFilter = ref('')
const searchFilter = ref('')
const error = ref(null)
const cancellingExecutions = ref({})
const showCancelModal = ref(false)
const executionToCancel = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)
const pageSizeOptions = [10, 25, 50, 100]

// Watch for route query changes
watch(() => route.query, (query) => {
  if (query.notebook) {
    notebookFilter.value = query.notebook
  }
  if (query.status) {
    statusFilter.value = query.status
  }
}, { immediate: true })

const loading = computed(() => executionsStore.loading)
const executions = computed(() => executionsStore.executions)
const currentUser = computed(() => authStore.user)

// Compute unique notebook paths for filter dropdown
const uniqueNotebooks = computed(() => {
  const notebookSet = new Set()
  executions.value.forEach(execution => {
    if (execution.notebook_path) {
      notebookSet.add(execution.notebook_path)
    }
  })
  return Array.from(notebookSet).sort()
})

const filteredExecutions = computed(() => {
  let filtered = executions.value;
  
  // Filter by status if selected
  if (statusFilter.value) {
    filtered = filtered.filter(execution => 
      execution.status.toLowerCase() === statusFilter.value
    );
  }
  
  // Filter by notebook if selected
  if (notebookFilter.value) {
    filtered = filtered.filter(execution => 
      execution.notebook_path === notebookFilter.value
    );
  }
  
  // Filter by search term if provided
  if (searchFilter.value.trim()) {
    const searchTerm = searchFilter.value.toLowerCase().trim();
    filtered = filtered.filter(execution => {
      // Search by execution ID
      if (execution.id.toLowerCase().includes(searchTerm)) {
        return true;
      }
      
      // Search by notebook name
      if (getNotebookDisplayName(execution).toLowerCase().includes(searchTerm)) {
        return true;
      }
      
      // Search in parameters
      if (execution.parameters) {
        // Convert parameters to string for simple text search
        const paramsString = JSON.stringify(execution.parameters).toLowerCase();
        if (paramsString.includes(searchTerm)) {
          return true;
        }
      }
      
      return false;
    });
  }
  
  // Filter by user if checkbox is checked
  if (showMyExecutionsOnly.value && currentUser.value) {
    filtered = filtered.filter(execution => 
      execution.user && execution.user.id === currentUser.value.id
    );
  }
  
  return filtered;
})

const paginatedExecutions = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return filteredExecutions.value.slice(startIndex, endIndex)
})

const totalPages = computed(() => {
  return Math.ceil(filteredExecutions.value.length / pageSize.value)
})

function getHtmlUrl(path) {
  if (!path) {
    return '#'
  }
  
  // If it's already a full URL
  if (path.startsWith('http')) {
    return path
  } 
  // If it's an S3 path (s3://bucket/path)
  else if (path.startsWith('s3://')) {
    // Extract the path part after the bucket name
    const s3Path = path.replace(/^s3:\/\/[^\/]+\//, '')
    return `${API_URL}/static/reports/${encodeURIComponent(s3Path)}`
  }
  // Regular path
  else {
    const baseUrl = window.location.origin
    return `${API_URL}/static/reports/${encodeURIComponent(path)}`
  }
}

async function refreshExecutions() {
  try {
    await executionsStore.fetchExecutions()
    error.value = null
  } catch (err) {
    error.value = handleApiError(err)
  }
}

function viewExecution(id) {
  router.push({ name: 'execution-detail', params: { id } })
}

async function cancelExecution(id) {
  if (cancellingExecutions.value[id]) return; // Prevent multiple cancel attempts
  
  // Clear previous errors
  error.value = null;
  
  // Set up confirmation modal
  executionToCancel.value = id;
  showCancelModal.value = true;
}

function closeConfirmModal() {
  showCancelModal.value = false;
  executionToCancel.value = null;
}

async function confirmCancelExecution() {
  // Get the ID from the stored execution
  const id = executionToCancel.value;
  
  if (!id || cancellingExecutions.value[id]) {
    closeConfirmModal();
    return;
  }
  
  try {
    // Set cancelling state
    cancellingExecutions.value[id] = true;
    
    // Close the modal
    showCancelModal.value = false;
    
    console.log(`Cancelling execution ${id}...`);
    const result = await executionsStore.cancelExecution(id);
    console.log(`Execution ${id} cancellation result:`, result);
    
    // Display any success message from the server
    if (result.message) {
      // Could show a success toast/notification here
      console.log('Success message:', result.message);
    }
    
    // Refresh the list after cancellation
    await refreshExecutions();
  } catch (err) {
    console.error(`Error cancelling execution ${id}:`, err);
    
    // Handle specific error codes
    if (err.response) {
      if (err.response.status === 403) {
        error.value = 'You do not have permission to cancel this execution.';
      } else if (err.response.status === 404) {
        // Handle 404 - job not found in Kubernetes
        error.value = err.response.data.detail || 'The execution job could not be found. It may have already completed, failed, or been terminated.';
        // Refresh executions list to get latest data
        await refreshExecutions();
      } else if (err.response.status === 409) {
        error.value = err.response.data.detail || 'Cannot cancel execution in its current state.';
        // Refresh executions list to get latest data
        await refreshExecutions();
      } else {
        error.value = handleApiError(err);
      }
    } else {
      error.value = handleApiError(err);
    }
  } finally {
    // Clear states
    cancellingExecutions.value[id] = false;
    executionToCancel.value = null;
  }
}

function viewResults(execution) {
  // Check if there's an HTML output
  if (execution.output_html) {
    // Navigate to the results viewer page
    router.push({
      name: 'results-viewer',
      query: { path: execution.output_html }
    });
  } 
  // If there's only a notebook output
  else if (execution.output_notebook) {
    // Either download it directly or open in a new tab
    window.open(execution.output_notebook, '_blank');
  }
  // If no outputs, navigate to execution details
  else {
    router.push({
      name: 'execution-detail',
      params: { id: execution.id }
    });
  }
}

function formatRelativeTime(dateString) {
  if (!dateString) return ''
  
  try {
    // Parse date as UTC by adding Z suffix if missing
    const dateUtc = dateString.endsWith('Z') ? dateString : dateString + 'Z'
    const date = new Date(dateUtc)
    
    // If Z suffix makes it invalid, try without it
    if (isNaN(date.getTime())) {
      const fallbackDate = new Date(dateString)
      if (isNaN(fallbackDate.getTime())) {
        // If both attempts fail, the date is invalid
        console.warn('Invalid date in formatRelativeTime', { dateString })
        return ''
      }
      
      return calculateRelativeTime(fallbackDate)
    }
    
    return calculateRelativeTime(date)
  } catch (error) {
    console.error('Error formatting relative time:', error)
    return ''
  }
}

// Helper function to calculate the relative time
function calculateRelativeTime(date) {
  const now = new Date()
  const diffMs = now - date
  
  // Return appropriate time format based on the difference
  if (diffMs < 0) {
    console.warn('Future date detected in formatRelativeTime', {
      date: date.toISOString(),
      now: now.toISOString(),
      diffMs
    })
    return 'just now'
  } else if (diffMs < 60000) {
    return 'just now'
  } else if (diffMs < 3600000) {
    const minutes = Math.floor(diffMs / 60000)
    return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`
  } else if (diffMs < 86400000) {
    const hours = Math.floor(diffMs / 3600000)
    return `${hours} hour${hours !== 1 ? 's' : ''} ago`
  } else {
    const days = Math.floor(diffMs / 86400000)
    return `${days} day${days !== 1 ? 's' : ''} ago`
  }
}

function formatDateTime(dateString) {
  if (!dateString) return 'N/A'
  
  try {
    // Explicitly parse the date string as UTC
    // Add Z suffix if missing to ensure UTC interpretation
    const utcDateString = dateString.endsWith('Z') ? dateString : dateString + 'Z'
    const date = new Date(utcDateString)
    
    // If adding Z causes an invalid date (it was already there or in another format),
    // fall back to regular parsing
    if (isNaN(date.getTime())) {
      const fallbackDate = new Date(dateString)
      if (isNaN(fallbackDate.getTime())) {
        console.warn('Invalid date:', dateString)
        return 'N/A'
      }
      return formatDateTimeForDisplay(fallbackDate)
    }
    
    return formatDateTimeForDisplay(date)
  } catch (error) {
    console.error('Error formatting date:', error)
    return 'N/A'
  }
}

// Helper function to format a date time with full details
function formatDateTimeForDisplay(date) {
  // Get the timezone offset name (e.g., "EST", "PDT")
  const timeZoneName = new Intl.DateTimeFormat('en', { timeZoneName: 'short' })
    .formatToParts(date)
    .find(part => part.type === 'timeZoneName')?.value || ''
  
  // Full date and time with seconds for tooltip
  return `${date.toLocaleDateString(undefined, {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })} ${date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })} (${timeZoneName})`
}

function formatParameters(parameters) {
  return Object.entries(parameters)
    .map(([key, value]) => {
      if (typeof value === 'object') {
        return `${key}: {...}`;
      }
      return `${key}: ${value}`;
    })
    .join(', ')
}

function formatCompactParameters(parameters) {
  const result = {};
  
  Object.entries(parameters).forEach(([key, value]) => {
    // Truncate long string values
    if (typeof value === 'string' && value.length > 15) {
      result[key] = value.substring(0, 12) + '...';
    } 
    // Format objects as {...}
    else if (typeof value === 'object' && value !== null) {
      result[key] = '{...}';
    }
    // Format arrays with length
    else if (Array.isArray(value)) {
      result[key] = `[${value.length} items]`;
    }
    // Format booleans with checkmark/x
    else if (typeof value === 'boolean') {
      result[key] = value ? '✓' : '✗';
    }
    // Use value as-is for simple types
    else {
      result[key] = value;
    }
  });
  
  return result;
}

function calculateDuration(startTime, endTime) {
  if (!startTime) return 'N/A'
  
  try {
    // Parse dates as UTC by adding Z suffix if missing
    const startUtc = startTime.endsWith('Z') ? startTime : startTime + 'Z'
    const start = new Date(startUtc)
    
    // If Z suffix makes it invalid, try without it
    if (isNaN(start.getTime())) {
      const fallbackStart = new Date(startTime)
      if (isNaN(fallbackStart.getTime())) {
        console.warn('Invalid start date in duration calculation', { startTime })
        return 'N/A'
      }
      
      // For end time, try the same approach
      let end
      if (endTime) {
        const endUtc = endTime.endsWith('Z') ? endTime : endTime + 'Z'
        end = new Date(endUtc)
        if (isNaN(end.getTime())) {
          end = new Date(endTime)
          if (isNaN(end.getTime())) {
            console.warn('Invalid end date in duration calculation', { endTime })
            return 'N/A'
          }
        }
      } else {
        end = new Date()
      }
      
      return calculateDurationBetweenDates(fallbackStart, end)
    }
    
    // For end time, apply the same logic
    let end
    if (endTime) {
      const endUtc = endTime.endsWith('Z') ? endTime : endTime + 'Z'
      end = new Date(endUtc)
      if (isNaN(end.getTime())) {
        end = new Date(endTime)
        if (isNaN(end.getTime())) {
          console.warn('Invalid end date in duration calculation', { endTime })
          return 'N/A'
        }
      }
    } else {
      end = new Date()
    }
    
    return calculateDurationBetweenDates(start, end)
  } catch (error) {
    console.error('Error calculating duration:', error)
    return 'N/A'
  }
}

// Helper function for duration calculations
function calculateDurationBetweenDates(start, end) {
  // Calculate the duration in milliseconds
  const durationMs = end.getTime() - start.getTime()
  
  // For newly started jobs, if the duration is suspiciously large (over 1h),
  // it's likely a timezone issue - show a more reasonable duration
  if (Math.abs(durationMs) > 3600000 && 
      !endTime && 
      ['pending', 'submitted', 'running'].includes(execution?.status) &&
      (new Date() - start) < 300000) { // Only for executions started less than 5 minutes ago
    return 'just started'
  }
  
  // Use the actual difference, not absolute value, to detect negative durations 
  // which indicate possible timezone issues
  if (durationMs < 0) {
    console.warn('Negative duration detected - possible timezone issue', {
      start: start.toISOString(), 
      end: end.toISOString(),
      diffMs: durationMs
    })
    // For active executions, show "just started" instead of a negative duration
    if (!endTime && ['pending', 'submitted', 'running'].includes(execution?.status)) {
      return 'just started'
    }
    return 'N/A'
  }
  
  // Format the duration
  const seconds = Math.floor(Math.abs(durationMs) / 1000)
  
  if (seconds < 60) {
    return `${seconds} seconds`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds}s`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }
}

function getNotebookDisplayName(execution) {
  // First check if notebook_name is available
  if (execution.notebook_name) {
    return execution.notebook_name;
  }
  
  // If no notebook_name, try to extract a name from notebook_path
  if (execution.notebook_path) {
    // Get the filename from the path
    const pathParts = execution.notebook_path.split('/');
    const filename = pathParts[pathParts.length - 1];
    
    // Remove the .ipynb extension if present
    return filename.replace(/\.ipynb$/, '');
  }
  
  // Fall back to a generic name with the execution ID
  return `Execution #${execution.id.substring(0, 8)}`;
}

function truncatePath(path) {
  if (!path) return '';
  // If path is longer than 40 characters, truncate the middle
  if (path.length > 40) {
    const start = path.substring(0, 20);
    const end = path.substring(path.length - 20);
    return `${start}...${end}`;
  }
  return path;
}

function changePage(page) {
  currentPage.value = page
  // Scroll to top of table
  const tableTop = document.querySelector('.min-w-full')
  if (tableTop) {
    tableTop.scrollIntoView({ behavior: 'smooth' })
  }
}

function changePageSize(size) {
  pageSize.value = size
  // Reset to first page when changing page size
  currentPage.value = 1
}

watch([statusFilter, notebookFilter, searchFilter, showMyExecutionsOnly], () => {
  currentPage.value = 1
})

onMounted(() => {
  // Initialize filters from URL query parameters
  if (route.query.notebook) {
    notebookFilter.value = route.query.notebook
  }
  if (route.query.status) {
    statusFilter.value = route.query.status
  }
  refreshExecutions()
})
</script>

<style scoped>
.execution-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.notebook-link {
  font-weight: 500;
  color: #0d6efd;
  text-decoration: none;
  transition: color 0.2s;
}

.notebook-link:hover {
  color: #0a58ca;
  text-decoration: underline;
}

.filter-controls {
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.form-check-label {
  user-select: none;
}

.card {
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  overflow: hidden;
}

.table-responsive {
  overflow-x: auto;
  min-height: 300px; /* Minimum height to avoid layout shifts */
}

.table th {
  font-weight: 600;
  color: #495057;
  white-space: nowrap;
}

.table td {
  vertical-align: middle;
  padding: 0.75rem;
}

.user-info {
  display: flex;
  align-items: center;
  white-space: nowrap;
}

@media (max-width: 992px) {
  .table {
    font-size: 0.9rem;
  }
  
  .notebook-link small {
    display: none;
  }
}
</style> 