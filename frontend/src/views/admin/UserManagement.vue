<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">User Management</h1>
    
    <div v-if="loading" class="text-center py-12">
      <svg class="animate-spin h-10 w-10 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="mt-2 text-gray-600">Loading users...</p>
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
      <div class="mb-4 flex justify-between items-center">
        <div class="relative">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search users..."
            class="w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>
        <button
          @click="fetchUsers"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <svg class="h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
          </svg>
          Refresh
        </button>
      </div>
      
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <ul class="divide-y divide-gray-200">
          <li v-for="user in filteredUsers" :key="user.id" class="px-6 py-4">
            <div class="flex items-center justify-between">
              <div>
                <div class="flex items-center">
                  <div class="h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center text-gray-500">
                    {{ user.username ? user.username.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase() }}
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                      {{ user.full_name || user.username || 'Unnamed User' }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ user.email }}
                    </div>
                    <div class="text-xs text-gray-400">
                      ID: {{ user.id }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="flex items-center space-x-4">
                <div class="flex items-center">
                  <span class="text-sm text-gray-500 mr-2">Active</span>
                  <button 
                    @click="toggleUserStatus(user, 'active')"
                    :disabled="updatingUser === user.id"
                    class="relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    :class="user.is_active ? 'bg-indigo-600' : 'bg-gray-200'"
                  >
                    <span 
                      class="pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200" 
                      :class="user.is_active ? 'translate-x-5' : 'translate-x-0'"
                    ></span>
                  </button>
                </div>
                <div class="flex items-center">
                  <span class="text-sm text-gray-500 mr-2">Admin</span>
                  <button 
                    @click="toggleUserStatus(user, 'admin')"
                    :disabled="updatingUser === user.id || user.id === currentUserId"
                    class="relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    :class="[
                      user.is_superuser ? 'bg-indigo-600' : 'bg-gray-200',
                      user.id === currentUserId ? 'opacity-50 cursor-not-allowed' : ''
                    ]"
                  >
                    <span 
                      class="pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200" 
                      :class="user.is_superuser ? 'translate-x-5' : 'translate-x-0'"
                    ></span>
                  </button>
                </div>
              </div>
            </div>
          </li>
        </ul>
      </div>
      
      <div v-if="filteredUsers.length === 0" class="text-center py-8 bg-gray-50 rounded-md mt-4">
        <p class="text-gray-500">No users found matching your search.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { getApiUrl } from '@/utils/env'

const API_URL = getApiUrl()
const authStore = useAuthStore()
const toast = useToast()

const users = ref([])
const loading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const updatingUser = ref(null)
const currentUserId = computed(() => authStore.user?.id)

// Filtered users based on search query
const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  
  const query = searchQuery.value.toLowerCase()
  return users.value.filter(user => 
    (user.username && user.username.toLowerCase().includes(query)) ||
    (user.email && user.email.toLowerCase().includes(query)) ||
    (user.full_name && user.full_name.toLowerCase().includes(query))
  )
})

async function fetchUsers() {
  loading.value = true
  error.value = null
  
  try {
    const response = await fetch(`${API_URL}/users`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch users')
    }
    
    users.value = await response.json()
  } catch (err) {
    console.error('Error fetching users:', err)
    error.value = 'Failed to load users. Please try again.'
  } finally {
    loading.value = false
  }
}

async function toggleUserStatus(user, type) {
  // Prevent toggling your own admin status
  if (type === 'admin' && user.id === currentUserId.value) {
    toast.warning("You cannot change your own admin status")
    return
  }
  
  updatingUser.value = user.id
  
  try {
    // Prepare update data
    const updateData = {
      is_superuser: type === 'admin' ? !user.is_superuser : user.is_superuser,
      is_active: type === 'active' ? !user.is_active : user.is_active
    }
    
    const response = await fetch(`${API_URL}/users/${user.id}/privileges`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updateData)
    })
    
    if (!response.ok) {
      throw new Error('Failed to update user status')
    }
    
    const updatedUser = await response.json()
    
    // Update the user in our list
    const userIndex = users.value.findIndex(u => u.id === user.id)
    if (userIndex !== -1) {
      users.value[userIndex] = updatedUser
    }
    
    // Show success message
    toast.success(`User ${type === 'admin' ? 'admin status' : 'active status'} updated`)
  } catch (err) {
    console.error('Error updating user:', err)
    toast.error('Failed to update user. Please try again.')
    
    // Revert the toggle in the UI
    if (type === 'admin') {
      user.is_superuser = !user.is_superuser
    } else {
      user.is_active = !user.is_active
    }
  } finally {
    updatingUser.value = null
  }
}

onMounted(() => {
  fetchUsers()
})
</script> 