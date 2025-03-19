<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <div v-if="loading" class="text-center py-12">
      <loading-spinner message="Loading execution details..." />
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

    <div v-else-if="execution" class="space-y-6">
      <!-- Header with breadcrumbs and actions -->
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <div class="flex items-center text-sm text-gray-500 mb-2">
            <router-link to="/notebooks" class="hover:text-indigo-600">Notebooks</router-link>
            <svg class="mx-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <router-link to="/executions" class="hover:text-indigo-600">Executions</router-link>
            <svg class="mx-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <span class="font-medium text-gray-900 truncate">{{ getNotebookDisplayName(execution) }}</span>
          </div>
          <h1 class="text-2xl font-bold text-gray-900 sm:text-3xl">
            {{ getNotebookDisplayName(execution) }}
          </h1>
          <p class="mt-1 text-sm text-gray-500 max-w-3xl">
            {{ execution.notebook_path }}
          </p>
        </div>
        
        <div class="flex flex-wrap gap-2">
          <button
            @click="$router.push('/executions')"
            type="button"
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <svg class="-ml-1 mr-2 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M7.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l2.293 2.293a1 1 0 010 1.414z" clip-rule="evenodd" />
            </svg>
            Back to Executions
          </button>
          
          <button
            v-if="['pending', 'running', 'submitted'].includes(execution.status)"
            @click="cancelExecution"
            type="button"
            :disabled="cancelingExecution"
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            <svg v-if="cancelingExecution" class="animate-spin -ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            {{ cancelingExecution ? 'Cancelling...' : 'Cancel Execution' }}
          </button>
        </div>
      </div>

      <!-- Primary information card - always visible, high priority information -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Left column - Execution status and vital info -->
            <div class="space-y-6">
              <div>
                <h3 class="text-lg font-medium text-gray-900">Status</h3>
                <div class="mt-2 flex items-center">
                  <span 
                    class="px-3 py-2 inline-flex text-sm font-medium rounded-md mr-2"
                    :class="{
                      'bg-gray-100 text-gray-800': execution.status === 'pending',
                      'bg-blue-100 text-blue-800': execution.status === 'submitted',
                      'bg-yellow-100 text-yellow-800': execution.status === 'running',
                      'bg-green-100 text-green-800': execution.status === 'completed',
                      'bg-red-100 text-red-800': execution.status === 'failed',
                      'bg-gray-100 text-gray-800': execution.status === 'cancelled'
                    }"
                  >
                    <svg 
                      v-if="execution.status === 'running'" 
                      class="animate-spin -ml-1 mr-2 h-4 w-4 text-yellow-600" 
                      xmlns="http://www.w3.org/2000/svg" 
                      fill="none" 
                      viewBox="0 0 24 24"
                    >
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ execution.status.charAt(0).toUpperCase() + execution.status.slice(1) }}
                  </span>
                  
                  <!-- Elapsed time for active executions -->
                  <span v-if="['running', 'pending', 'submitted'].includes(execution.status)" class="text-sm text-gray-600 flex items-center">
                    <svg class="mr-1 h-4 w-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
                    </svg>
                    Running for {{ calculateDuration(execution.started_at || execution.created_at, null) }}
                  </span>
                </div>
              </div>
              
              <div>
                <h3 class="text-lg font-medium text-gray-900">Timeline</h3>
                <dl class="mt-2 space-y-1">
                  <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                    <dt class="text-sm font-medium text-gray-500">Submitted:</dt>
                    <dd class="text-sm text-gray-900 sm:mt-0 sm:col-span-2" :title="execution.created_at ? formatUTCDate(execution.created_at) : 'N/A'">
                      <span v-if="execution.created_at">
                        {{ formatRelativeTime(execution.created_at) }}
                        <span class="text-gray-500 text-xs ml-1">({{ formatDateTime(execution.created_at) }})</span>
                      </span>
                      <span v-else>N/A</span>
                    </dd>
                  </div>
                  <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                    <dt class="text-sm font-medium text-gray-500">Started:</dt>
                    <dd class="text-sm text-gray-900 sm:mt-0 sm:col-span-2" :title="execution.started_at ? formatUTCDate(execution.started_at) : 'N/A'">
                      <span v-if="execution.started_at">
                        {{ formatRelativeTime(execution.started_at) }}
                        <span class="text-gray-500 text-xs ml-1">({{ formatDateTime(execution.started_at) }})</span>
                      </span>
                      <span v-else>N/A</span>
                    </dd>
                  </div>
                  <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                    <dt class="text-sm font-medium text-gray-500">Completed:</dt>
                    <dd class="text-sm text-gray-900 sm:mt-0 sm:col-span-2" :title="execution.completed_at ? formatUTCDate(execution.completed_at) : 'N/A'">
                      <span v-if="execution.completed_at">
                        {{ formatRelativeTime(execution.completed_at) }}
                        <span class="text-gray-500 text-xs ml-1">({{ formatDateTime(execution.completed_at) }})</span>
                      </span>
                      <span v-else>N/A</span>
                    </dd>
                  </div>
                  <div class="sm:grid sm:grid-cols-3 sm:gap-4">
                    <dt class="text-sm font-medium text-gray-500">Duration:</dt>
                    <dd class="text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ calculateDuration(execution.started_at, execution.completed_at) }}</dd>
                  </div>
                </dl>
              </div>
            </div>
            
            <!-- Right column - Submitter and results -->
            <div class="space-y-6">
              <div>
                <h3 class="text-lg font-medium text-gray-900">Submitted By</h3>
                <div class="mt-2 flex items-center">
                  <div v-if="execution.user" class="flex items-center">
                    <div class="bg-gray-100 rounded-full h-10 w-10 flex items-center justify-center text-gray-700 mr-3">
                      <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-gray-900">{{ execution.user?.username || 'Unknown User' }}</p>
                      <p class="text-xs text-gray-500">{{ execution.user?.email || '' }}</p>
                    </div>
                  </div>
                  <div v-else-if="execution.service_account" class="flex items-center">
                    <div class="bg-gray-100 rounded-full h-10 w-10 flex items-center justify-center text-gray-700 mr-3">
                      <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 10V7a5 5 0 0110 0v3m-9 1a9 9 0 0118 0v4m-9 5a2 2 0 01-2-2v-5a2 2 0 114 0v5a2 2 0 01-2 2h-3zm-3 8h.01"/>
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-gray-900">API: {{ execution.service_account?.name || 'Unknown API' }}</p>
                      <p class="text-xs text-gray-500">{{ execution.service_account?.description || 'API Execution' }}</p>
                    </div>
                  </div>
                  <div v-else class="flex items-center">
                    <div class="bg-gray-100 rounded-full h-10 w-10 flex items-center justify-center text-gray-700 mr-3">
                      <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-gray-900">System</p>
                      <p class="text-xs text-gray-500">Automated process</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-if="execution.status === 'completed' || execution.status === 'failed'">
                <h3 class="text-lg font-medium text-gray-900">Results</h3>
                <div class="mt-2 space-y-3">
                  <div v-if="execution.output_html" class="flex flex-col space-y-2">
                    <router-link 
                      :to="{ 
                        name: 'results-viewer', 
                        query: { 
                          path: execution.output_html,
                          notebookPath: execution.output_notebook
                        }
                      }"
                      class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 w-full justify-center"
                    >
                      <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                        <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                      </svg>
                      View Results
                    </router-link>
                  </div>
                  
                  <a 
                    v-if="execution.output_notebook"
                    :href="getHtmlUrl(execution.output_notebook)"
                    download
                    class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 w-full justify-center"
                  >
                    <svg class="-ml-1 mr-2 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 102 0v7.586l1.293-1.293a1 1 0 101.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                    Download Notebook
                  </a>
                  
                  <div v-if="!execution.output_html && !execution.output_notebook" class="text-sm text-gray-500 italic">
                    No output files are available for this execution.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Execution parameters --> 
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 border-b border-gray-200 sm:px-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">
            Execution Parameters
          </h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">
            Input parameters that were used for this execution
          </p>
        </div>
        <div class="px-4 py-5 sm:p-6">
          <dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div v-for="(value, key, index) in execution.parameters" :key="key" class="sm:col-span-1">
              <dt class="text-sm font-medium text-gray-500">
                {{ key }}
                <span class="text-xs font-normal ml-1 text-gray-400">({{ typeof value === 'object' ? (Array.isArray(value) ? 'array' : 'object') : typeof value }})</span>
              </dt>
              <dd class="mt-1 text-sm text-gray-900">
                <pre v-if="typeof value === 'object'" class="whitespace-pre-wrap text-xs bg-gray-100 p-3 rounded">{{ JSON.stringify(value, null, 2) }}</pre>
                <span v-else>{{ value }}</span>
              </dd>
            </div>
            <div v-if="!execution.parameters || Object.keys(execution.parameters).length === 0" class="sm:col-span-2">
              <p class="text-sm text-gray-500 italic">No parameters were specified for this execution.</p>
            </div>
          </dl>
        </div>
      </div>
      
      <!-- Execution details -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 border-b border-gray-200 sm:px-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">
            Technical Details
          </h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">
            Additional details about the execution environment
          </p>
        </div>
        <div class="border-t border-gray-200">
          <dl>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Execution ID</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2 flex items-center">
                <code class="px-2 py-1 bg-gray-100 rounded text-xs mr-2">{{ execution.id }}</code>
                <button 
                  type="button" 
                  @click="copyToClipboard(execution.id)"
                  class="inline-flex items-center p-1 border border-transparent rounded-full shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  :title="copySuccess ? 'Copied!' : 'Copy ID to clipboard'"
                >
                  <svg 
                    v-if="!copySuccess" 
                    class="h-4 w-4" 
                    xmlns="http://www.w3.org/2000/svg" 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke="currentColor"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                  </svg>
                  <svg 
                    v-else 
                    class="h-4 w-4" 
                    xmlns="http://www.w3.org/2000/svg" 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke="currentColor"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </button>
              </dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Python Version</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ execution.python_version || 'Not specified' }}
              </dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Resources</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-blue-100 text-blue-800 mr-2">
                  CPU: {{ execution.cpu_milli || 'Default' }} millicores
                </span>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-purple-100 text-purple-800">
                  Memory: {{ execution.memory_mib || 'Default' }} MiB
                </span>
              </dd>
            </div>
          </dl>
        </div>
      </div>

      <!-- Error Message (if any) -->
      <div v-if="execution.error" class="bg-red-50 border border-red-200 rounded-lg shadow-sm overflow-hidden">
        <div class="px-4 py-5 sm:p-6">
          <h3 class="text-lg font-medium text-red-800 flex items-center">
            <svg class="h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            Execution Error
          </h3>
          <div class="mt-3 bg-white p-4 rounded border border-red-100 overflow-auto max-h-96">
            <pre class="whitespace-pre-wrap text-sm text-red-900">{{ execution.error }}</pre>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">Execution not found</h3>
      <p class="mt-1 text-sm text-gray-500">
        The execution you're looking for doesn't exist or has been removed.
      </p>
      <div class="mt-6">
        <router-link to="/executions" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          View All Executions
        </router-link>
      </div>
    </div>

    <!-- Confirmation Modal for cancel execution -->
    <ConfirmationModal
      v-if="showCancelConfirmation"
      title="Cancel Execution"
      message="Are you sure you want to cancel this execution? This action cannot be undone."
      confirmButtonText="Cancel Execution"
      cancelButtonText="Nevermind"
      @confirm="confirmCancelExecution"
      @cancel="showCancelConfirmation = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useExecutionsStore } from '@/stores/executions'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { handleApiError } from '@/utils/errorHandler'
import { getApiUrl } from '@/utils/env'
import ConfirmationModal from '@/components/ConfirmationModal.vue'

const route = useRoute()
const router = useRouter()
const executionsStore = useExecutionsStore()

const execution = ref(null)
const loading = ref(true)
const error = ref(null)
const pollingInterval = ref(null)
const cancelingExecution = ref(false)
const showCancelConfirmation = ref(false)
const copySuccess = ref(false)

// Get the API URL
const API_URL = getApiUrl()

onMounted(async () => {
  try {
    await fetchExecution()
    startPolling()
  } catch (err) {
    error.value = handleApiError(err)
    loading.value = false
  }
})

async function fetchExecution() {
  loading.value = true
  try {
    execution.value = await executionsStore.getExecution(route.params.id)
    console.log('Debug - Execution data:', execution.value)
  } catch (err) {
    error.value = handleApiError(err)
  } finally {
    loading.value = false
  }
}

function getHtmlUrl(path) {
  console.log('Debug - Processing output path:', path)
  if (!path) {
    console.error('Debug - Path is undefined or null')
    return '#'
  }
  
  // If it's already a full URL
  if (path.startsWith('http')) {
    console.log('Debug - Using direct URL:', path)
    return path
  } 
  // If it's an S3 path (s3://bucket/path)
  else if (path.startsWith('s3://')) {
    // Extract the path part after the bucket name
    console.log('Debug - Converting S3 URL:', path)
    const s3Path = path.replace(/^s3:\/\/[^\/]+\//, '')
    const url = `${API_URL}/static/reports/${encodeURIComponent(s3Path)}`
    console.log('Debug - Constructed URL from S3 path:', url)
    return url
  }
  // Regular path
  else {
    const url = `${API_URL}/static/reports/${encodeURIComponent(path)}`
    console.log('Debug - Constructed URL from regular path:', url)
    return url
  }
}

function startPolling() {
  if (execution.value && (execution.value.status === 'pending' || execution.value.status === 'running' || execution.value.status === 'submitted')) {
    pollingInterval.value = setInterval(async () => {
      try {
        const status = await executionsStore.getExecutionStatus(route.params.id)
        
        // Only update the execution if something changed
        if (JSON.stringify(execution.value) !== JSON.stringify({ ...execution.value, ...status })) {
          execution.value = { ...execution.value, ...status }
          
          // Stop polling if execution is complete, but don't trigger a full reload
          if (status.status !== 'pending' && status.status !== 'running' && status.status !== 'submitted') {
            stopPolling()
            
            // For completed or failed statuses, only get additional execution data if needed fields are missing
            if ((status.status === 'completed' || status.status === 'failed') && 
                (!execution.value.output_notebook || !execution.value.output_html || !execution.value.completed_at)) {
              // Get additional data without triggering a full page refresh
              try {
                const fullData = await executionsStore.getExecution(route.params.id)
                execution.value = fullData
              } catch (error) {
                console.error('Error fetching complete execution data:', error)
              }
            }
          }
        }
      } catch (err) {
        console.error('Polling error:', err)
        stopPolling()
      }
    }, 15000) // Poll every 15 seconds
  }
}

function stopPolling() {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
    pollingInterval.value = null
  }
}

async function cancelExecution() {
  if (cancelingExecution.value) return; // Prevent multiple cancel attempts
  
  // Show the confirmation modal instead of using native confirm
  showCancelConfirmation.value = true;
}

async function confirmCancelExecution() {
  try {
    cancelingExecution.value = true;
    error.value = null;
    
    // Hide the confirmation modal
    showCancelConfirmation.value = false;
    
    console.log('Cancelling execution:', route.params.id);
    
    // Call the store method to cancel the execution
    const result = await executionsStore.cancelExecution(route.params.id);
    
    // Display success message with any additional info from the backend
    console.log('Cancellation result:', result);
    
    if (result.message) {
      // Show a success toast/notification with the message
      console.log('Success message:', result.message);
    }
    
    // Refresh execution data after cancellation
    await fetchExecution();
  } catch (err) {
    console.error('Error cancelling execution:', err);
    
    // Handle specific error codes
    if (err.response) {
      if (err.response.status === 403) {
        error.value = 'You do not have permission to cancel this execution.';
      } else if (err.response.status === 404) {
        // Handle 404 - job not found in Kubernetes
        error.value = err.response.data.detail || 'The execution job could not be found. It may have already completed, failed, or been terminated.';
        // Refresh execution data to get the latest status
        await fetchExecution();
      } else if (err.response.status === 409) {
        // Handle 409 - conflict (execution in wrong state)
        error.value = err.response.data.detail || 'Cannot cancel this execution in its current state.';
        // Refresh execution data to get the latest status
        await fetchExecution();
      } else {
        error.value = handleApiError(err);
      }
    } else {
      error.value = handleApiError(err);
    }
  } finally {
    cancelingExecution.value = false;
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

function formatUTCDate(dateString) {
  if (!dateString) return 'N/A'
  
  try {
    // For UTC dates, we need to ensure the date is treated as UTC
    // If the string doesn't end with Z, add it to force UTC interpretation
    const utcDateString = dateString.endsWith('Z') ? dateString : dateString + 'Z'
    const date = new Date(utcDateString)
    
    // Validate the date
    if (isNaN(date.getTime())) {
      // Try without the Z suffix as a fallback
      const fallbackDate = new Date(dateString)
      if (isNaN(fallbackDate.getTime())) {
        return 'Invalid date'
      }
      // Format as UTC specifically
      return `${fallbackDate.toUTCString()} (UTC)`
    }
    
    // Return UTC string explicitly marked as UTC
    return `${date.toUTCString()} (UTC)`
  } catch (error) {
    return 'Error formatting date'
  }
}

function formatDateTime(dateString) {
  if (!dateString) return 'N/A'
  
  try {
    // Explicitly parse the date string as UTC
    // Backend API dates should be in UTC format
    const date = new Date(dateString + 'Z')
    
    // If the Z suffix causes an invalid date (because the string already had Z),
    // fall back to standard parsing
    if (isNaN(date.getTime())) {
      const fallbackDate = new Date(dateString)
      if (isNaN(fallbackDate.getTime())) {
        console.warn('Invalid date:', dateString)
        return 'N/A'
      }
      return formatDateObject(fallbackDate)
    }
    
    return formatDateObject(date)
  } catch (error) {
    console.error('Error formatting date:', error)
    return 'N/A'
  }
}

// Helper function to format a date object consistently
function formatDateObject(date) {
  // Get timezone abbreviation
  const timeZoneName = new Intl.DateTimeFormat('en', { timeZoneName: 'short' })
    .formatToParts(date)
    .find(part => part.type === 'timeZoneName')?.value || ''
  
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
  if (!execution.value.completed_at && 
      Math.abs(durationMs) > 3600000 && 
      ['pending', 'submitted', 'running'].includes(execution.value?.status) &&
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
    if (!execution.value.completed_at && ['pending', 'submitted', 'running'].includes(execution.value?.status)) {
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

function copyToClipboard(text) {
  const input = document.createElement('input')
  input.value = text
  document.body.appendChild(input)
  input.select()
  document.execCommand('copy')
  document.body.removeChild(input)
  copySuccess.value = true
  
  // Reset the copy success state after 2 seconds
  setTimeout(() => {
    copySuccess.value = false
  }, 2000)
}

onUnmounted(() => {
  stopPolling()
})

// Watch for status changes to start/stop polling
watch(() => execution.value?.status, (newStatus) => {
  if (newStatus === 'pending' || newStatus === 'running' || newStatus === 'submitted') {
    startPolling()
  } else {
    stopPolling()
  }
})
</script> 