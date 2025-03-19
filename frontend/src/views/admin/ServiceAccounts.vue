<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Service Accounts</h1>
    
    <div v-if="loading" class="text-center py-12">
      <svg class="animate-spin h-10 w-10 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="mt-2 text-gray-600">Loading service accounts...</p>
    </div>
    
    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
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
    
    <div v-else>
      <!-- Create new service account form -->
      <div class="bg-white shadow sm:rounded-lg mb-6">
        <div class="px-4 py-5 sm:p-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Create New Service Account</h3>
          <div class="mt-2 max-w-xl text-sm text-gray-500">
            <p>Service accounts can be used for programmatic API access without user interaction.</p>
          </div>
          <form @submit.prevent="createServiceAccount" class="mt-5 sm:flex sm:items-end">
            <div class="w-full sm:max-w-xs mr-3">
              <label for="name" class="block text-sm font-medium text-gray-700">Name</label>
              <div class="mt-1">
                <input 
                  type="text" 
                  name="name" 
                  id="name" 
                  v-model="newServiceAccount.name"
                  class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md" 
                  placeholder="Service Account Name"
                  required
                />
              </div>
            </div>
            <div class="w-full sm:max-w-xs mr-3">
              <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
              <div class="mt-1">
                <input 
                  type="text" 
                  name="description" 
                  id="description" 
                  v-model="newServiceAccount.description"
                  class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md" 
                  placeholder="Optional description"
                />
              </div>
            </div>
            <div class="mt-3 sm:mt-0">
              <button 
                type="submit" 
                :disabled="creatingAccount"
                class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <svg v-if="creatingAccount" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Create</span>
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <!-- API key modal -->
      <div v-if="showApiKeyModal" class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
        <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showApiKeyModal = false"></div>
          <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
          <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
            <div>
              <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                <svg class="h-6 w-6 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div class="mt-3 text-center sm:mt-5">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  Service Account Created Successfully
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500">
                    <strong class="text-red-600">IMPORTANT:</strong> Please save the API key below as it will not be shown again. If you lose this key, you'll need to generate a new one.
                  </p>
                </div>
                <div class="mt-4">
                  <label for="api-key" class="block text-sm font-medium text-gray-700 text-left mb-1">API Key:</label>
                  <div class="relative">
                    <input 
                      id="api-key"
                      type="text" 
                      readonly 
                      :value="apiKey" 
                      class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md pr-10 bg-gray-50 font-mono"
                    />
                    <button 
                      @click="copyApiKey" 
                      class="absolute inset-y-0 right-0 pr-3 flex items-center text-indigo-600 hover:text-indigo-900"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M8 2a1 1 0 000 2h2a1 1 0 100-2H8z" />
                        <path d="M3 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v6h-4.586l1.293-1.293a1 1 0 00-1.414-1.414l-3 3a1 1 0 000 1.414l3 3a1 1 0 001.414-1.414L10.414 13H15v3a2 2 0 01-2 2H5a2 2 0 01-2-2V5zM15 11h2a1 1 0 010 2h-2v-2z" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div class="mt-5 sm:mt-6">
              <button 
                type="button" 
                class="inline-flex justify-center w-full rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:text-sm"
                @click="showApiKeyModal = false"
              >
                I've Saved the Key - Close
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- List of existing service accounts -->
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h3 class="text-lg leading-6 font-medium text-gray-900">Service Accounts</h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500">A list of all service accounts in the system.</p>
          </div>
          <button
            @click="fetchServiceAccounts"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <svg class="h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
            </svg>
            Refresh
          </button>
        </div>
        <div v-if="serviceAccounts.length === 0" class="text-center py-8 bg-gray-50">
          <p class="text-gray-500">No service accounts found.</p>
          <p class="text-sm text-gray-400 mt-1">Create one using the form above.</p>
        </div>
        <ul v-else class="divide-y divide-gray-200">
          <li v-for="account in serviceAccounts" :key="account.id" class="px-4 py-4">
            <div class="flex items-center justify-between">
              <div>
                <div class="flex items-center">
                  <div class="h-10 w-10 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-500">
                    <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                    </svg>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ account.name }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ account.description || 'No description' }}
                    </div>
                    <div class="text-xs text-gray-400 mt-1">
                      ID: {{ account.id }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="flex items-center">
                <div class="text-sm text-gray-500 mr-4">
                  <div>Created: {{ formatDate(account.created_at) }}</div>
                  <div v-if="account.last_used_at">Last used: {{ formatDate(account.last_used_at) }}</div>
                  <div v-else class="text-gray-400">Never used</div>
                </div>
                <button
                  @click="confirmDeleteAccount(account)"
                  :disabled="deletingAccount === account.id"
                  class="inline-flex items-center p-2 border border-transparent rounded-full shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  <svg v-if="deletingAccount === account.id" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <svg v-else class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </li>
        </ul>
      </div>
      
      <!-- Delete confirmation modal -->
      <div v-if="showDeleteModal" class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
        <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showDeleteModal = false"></div>
          <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
          <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
            <div>
              <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div class="mt-3 text-center sm:mt-5">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  Delete Service Account
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500">
                    Are you sure you want to delete the service account "{{ accountToDelete?.name }}"? This action cannot be undone, and any applications using this service account will no longer be able to access the API.
                  </p>
                </div>
              </div>
            </div>
            <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
              <button 
                type="button" 
                class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:col-start-2 sm:text-sm"
                @click="deleteServiceAccount"
              >
                Delete
              </button>
              <button 
                type="button" 
                class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:col-start-1 sm:text-sm"
                @click="showDeleteModal = false"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { getApiUrl } from '@/utils/env'

const API_URL = getApiUrl()
const authStore = useAuthStore()
const toast = useToast()

// Service accounts state
const serviceAccounts = ref([])
const loading = ref(true)
const error = ref(null)

// Form state
const newServiceAccount = ref({
  name: '',
  description: ''
})
const creatingAccount = ref(false)

// Modal state
const showApiKeyModal = ref(false)
const apiKey = ref('')
const showDeleteModal = ref(false)
const accountToDelete = ref(null)
const deletingAccount = ref(null)

// Watch for modal visibility changes (for debugging)
watch(showApiKeyModal, (newVal) => {
  console.log('API Key modal visibility changed:', newVal)
  if (newVal && apiKey.value) {
    console.log('API Key is available:', apiKey.value.substring(0, 3) + '...')
  }
})

async function fetchServiceAccounts() {
  loading.value = true
  error.value = null
  
  try {
    const response = await fetch(`${API_URL}/service-accounts`, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch service accounts')
    }
    
    serviceAccounts.value = await response.json()
  } catch (err) {
    console.error('Error fetching service accounts:', err)
    error.value = 'Failed to load service accounts. Please try again.'
  } finally {
    loading.value = false
  }
}

async function createServiceAccount() {
  if (!newServiceAccount.value.name) {
    toast.error('Name is required')
    return
  }
  
  creatingAccount.value = true
  console.log('Creating service account:', newServiceAccount.value)
  
  try {
    const response = await fetch(`${API_URL}/service-accounts`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: newServiceAccount.value.name,
        description: newServiceAccount.value.description,
        scopes: newServiceAccount.value.scopes
      })
    })
    
    if (!response.ok) {
      console.error('Error response:', response.status, response.statusText)
      throw new Error('Failed to create service account')
    }
    
    const data = await response.json()
    console.log('Service account created successfully, response data:', data)
    
    // The response should have the service account data and API key in the same object
    // Add to the list (without the API key)
    const serviceAccountData = {
      id: data.id,
      name: data.name, 
      description: data.description,
      created_at: data.created_at,
      last_used_at: data.last_used_at,
      is_active: data.is_active,
      permissions: data.permissions
    }
    
    console.log('Adding service account to list:', serviceAccountData)
    serviceAccounts.value.unshift(serviceAccountData)
    
    // Show API key
    console.log('Setting API key:', data.api_key ? 'API key present' : 'API key missing')
    apiKey.value = data.api_key
    showApiKeyModal.value = true
    
    // Reset form
    newServiceAccount.value = {
      name: '',
      description: ''
    }
    
    toast.success('Service account created successfully')
    
    // Set a timeout to ensure the modal is shown
    setTimeout(() => {
      if (!showApiKeyModal.value && apiKey.value) {
        console.log('Forcing modal to show after timeout');
        showApiKeyModal.value = true;
      }
    }, 500);
  } catch (err) {
    console.error('Error creating service account:', err)
    toast.error('Failed to create service account. Please try again.')
  } finally {
    creatingAccount.value = false
  }
}

function copyApiKey() {
  if (!navigator.clipboard) {
    // Fallback method for browsers without clipboard API
    try {
      const textArea = document.createElement('textarea');
      textArea.value = apiKey.value;
      textArea.style.position = 'fixed';  // Avoid scrolling to bottom
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      const successful = document.execCommand('copy');
      document.body.removeChild(textArea);
      
      if (successful) {
        toast.success('API key copied to clipboard');
      } else {
        toast.error('Failed to copy API key');
      }
    } catch (err) {
      console.error('Fallback: Could not copy text: ', err);
      toast.error('Failed to copy API key');
    }
  } else {
    // Modern browsers with clipboard API
    navigator.clipboard.writeText(apiKey.value)
      .then(() => {
        toast.success('API key copied to clipboard');
      })
      .catch((err) => {
        console.error('Clipboard API error: ', err);
        toast.error('Failed to copy API key');
      });
  }
}

function confirmDeleteAccount(account) {
  accountToDelete.value = account
  showDeleteModal.value = true
}

async function deleteServiceAccount() {
  if (!accountToDelete.value) return
  
  deletingAccount.value = accountToDelete.value.id
  
  try {
    const response = await fetch(`${API_URL}/service-accounts/${accountToDelete.value.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (!response.ok) {
      throw new Error('Failed to delete service account')
    }
    
    // Remove from the list
    serviceAccounts.value = serviceAccounts.value.filter(account => account.id !== accountToDelete.value.id)
    
    toast.success('Service account deleted successfully')
  } catch (err) {
    console.error('Error deleting service account:', err)
    toast.error('Failed to delete service account. Please try again.')
  } finally {
    deletingAccount.value = null
    showDeleteModal.value = false
    accountToDelete.value = null
  }
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  
  const date = new Date(dateString)
  
  // Check if date is valid
  if (isNaN(date.getTime())) return 'Invalid date'
  
  // Format date to localized string
  return date.toLocaleString()
}

onMounted(() => {
  fetchServiceAccounts()
})
</script> 