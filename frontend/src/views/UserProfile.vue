<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <div class="md:flex md:items-center md:justify-between mb-6">
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          My Profile
        </h2>
      </div>
      <div class="mt-4 flex md:mt-0 md:ml-4" v-if="user">
        <button
          v-if="isEditing"
          @click="cancelEdit"
          type="button"
          class="ml-3 inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Cancel
        </button>
        <button
          v-if="isEditing"
          @click="saveProfile"
          type="button"
          class="ml-3 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          :disabled="isSaving"
        >
          <svg v-if="isSaving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Save Changes
        </button>
        <button
          v-else
          @click="startEdit"
          type="button"
          class="ml-3 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Edit Profile
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <loading-spinner message="Loading profile..." />
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

    <div v-if="saveSuccess" class="bg-green-50 border-l-4 border-green-400 p-4 my-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-green-700">Profile updated successfully!</p>
        </div>
      </div>
    </div>

    <div v-else-if="user" class="bg-white shadow overflow-hidden sm:rounded-lg">
      <!-- Profile header with avatar -->
      <div class="px-4 py-5 sm:px-6 flex items-center">
        <UserAvatar 
          :user="user" 
          size="lg" 
          class="mr-4"
        />
        <div>
          <h3 class="text-lg leading-6 font-medium text-gray-900">
            {{ user.full_name || user.username }}
          </h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">
            {{ user.email }}
          </p>
        </div>
      </div>
      
      <!-- Profile details -->
      <div class="border-t border-gray-200">
        <dl>
          <!-- Username field -->
          <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt class="text-sm font-medium text-gray-500">
              Username
            </dt>
            <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              <div v-if="isEditing">
                <input 
                  type="text" 
                  v-model="formData.username" 
                  class="max-w-lg block w-full shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:max-w-xs sm:text-sm border-gray-300 rounded-md"
                />
                <p v-if="errors.username" class="mt-2 text-sm text-red-600">{{ errors.username }}</p>
              </div>
              <div v-else>
                {{ user.username }}
              </div>
            </dd>
          </div>
          
          <!-- Email field - read only -->
          <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt class="text-sm font-medium text-gray-500">
              Email address
            </dt>
            <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {{ user.email }}
              <p class="mt-1 text-xs text-gray-500" v-if="isEditing">
                To change your email address, please contact support.
              </p>
            </dd>
          </div>
          
          <!-- Password change section - only shown when editing -->
          <div v-if="isEditing && !isOAuthUser" class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt class="text-sm font-medium text-gray-500">
              Change Password
            </dt>
            <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              <div class="space-y-4">
                <div>
                  <label for="current-password" class="block text-sm font-medium text-gray-700">Current Password</label>
                  <div class="mt-1">
                    <input 
                      type="password" 
                      id="current-password"
                      v-model="formData.currentPassword" 
                      class="max-w-lg block w-full shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:max-w-xs sm:text-sm border-gray-300 rounded-md"
                    />
                    <p v-if="errors.currentPassword" class="mt-2 text-sm text-red-600">{{ errors.currentPassword }}</p>
                  </div>
                </div>
                
                <div>
                  <label for="new-password" class="block text-sm font-medium text-gray-700">New Password</label>
                  <div class="mt-1">
                    <input 
                      type="password" 
                      id="new-password"
                      v-model="formData.newPassword" 
                      class="max-w-lg block w-full shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:max-w-xs sm:text-sm border-gray-300 rounded-md"
                    />
                    <p v-if="errors.newPassword" class="mt-2 text-sm text-red-600">{{ errors.newPassword }}</p>
                  </div>
                </div>
                
                <div>
                  <label for="confirm-password" class="block text-sm font-medium text-gray-700">Confirm New Password</label>
                  <div class="mt-1">
                    <input 
                      type="password" 
                      id="confirm-password"
                      v-model="formData.confirmPassword" 
                      class="max-w-lg block w-full shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:max-w-xs sm:text-sm border-gray-300 rounded-md"
                    />
                    <p v-if="errors.confirmPassword" class="mt-2 text-sm text-red-600">{{ errors.confirmPassword }}</p>
                  </div>
                </div>
              </div>
            </dd>
          </div>
          
          <!-- Account created - always read only -->
          <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt class="text-sm font-medium text-gray-500">
              Account created
            </dt>
            <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {{ formatDate(user.created_at) }}
            </dd>
          </div>
        </dl>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import UserAvatar from '@/components/avatar/UserAvatar.vue'
import axios from 'axios'

const authStore = useAuthStore()
const loading = ref(false)
const error = ref(null)
const user = computed(() => authStore.user)
const isEditing = ref(false)
const isSaving = ref(false)
const saveSuccess = ref(false)
const errors = reactive({})

// Form data for the editable fields
const formData = reactive({
  username: '',
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// Determine if user is authenticated with OAuth
const isOAuthUser = computed(() => {
  // This is a placeholder - you'll need to determine how to identify OAuth users in your system
  // For example, maybe they have an oauth_provider field or no password field
  return false
})

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  
  try {
    const date = new Date(dateString)
    
    // Check if the date is valid
    if (isNaN(date.getTime())) {
      console.error('Invalid date string:', dateString)
      return 'N/A'
    }
    
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  } catch (error) {
    console.error('Error formatting date:', error)
    return 'N/A'
  }
}

function startEdit() {
  // Initialize form data with current values
  formData.username = user.value.username || ''
  formData.currentPassword = ''
  formData.newPassword = ''
  formData.confirmPassword = ''
  
  // Clear any previous errors
  Object.keys(errors).forEach(key => delete errors[key])
  
  isEditing.value = true
  saveSuccess.value = false
}

function cancelEdit() {
  isEditing.value = false
  
  // Clear form data
  formData.username = ''
  formData.currentPassword = ''
  formData.newPassword = ''
  formData.confirmPassword = ''
  
  // Clear any errors
  Object.keys(errors).forEach(key => delete errors[key])
}

function validateForm() {
  let isValid = true
  
  // Clear previous errors
  Object.keys(errors).forEach(key => delete errors[key])
  
  // Validate username
  if (!formData.username || formData.username.trim() === '') {
    errors.username = 'Username is required'
    isValid = false
  }
  
  // If changing password, validate password fields
  if (formData.newPassword || formData.confirmPassword || formData.currentPassword) {
    // Check current password
    if (!formData.currentPassword) {
      errors.currentPassword = 'Current password is required'
      isValid = false
    }
    
    // Check new password
    if (!formData.newPassword) {
      errors.newPassword = 'New password is required'
      isValid = false
    } else if (formData.newPassword.length < 8) {
      errors.newPassword = 'Password must be at least 8 characters'
      isValid = false
    }
    
    // Check password confirmation
    if (!formData.confirmPassword) {
      errors.confirmPassword = 'Please confirm your new password'
      isValid = false
    } else if (formData.newPassword !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match'
      isValid = false
    }
  }
  
  return isValid
}

async function saveProfile() {
  if (!validateForm()) {
    return;
  }
  
  isSaving.value = true;
  error.value = null;
  saveSuccess.value = false;
  
  try {
    // Prepare the update data
    const updateData = {
      username: formData.username
    };
    
    // Only include password fields if they were filled out
    if (formData.newPassword) {
      updateData.current_password = formData.currentPassword;
      updateData.new_password = formData.newPassword;
    }
    
    // Call your API to update the user
    await authStore.updateUser(updateData);
    
    // Show success message
    saveSuccess.value = true;
    isEditing.value = false;
    
    // Clear sensitive form data
    formData.currentPassword = '';
    formData.newPassword = '';
    formData.confirmPassword = '';
  } catch (err) {
    // Handle specific error cases
    if (err.response?.status === 400) {
      const errorDetail = err.response?.data?.detail || "Invalid input";
      error.value = errorDetail;
      
      // Handle specific uniqueness errors
      if (errorDetail.includes("Username already registered")) {
        errors.username = "This username is already taken. Please choose another.";
      } else if (errorDetail.includes("Email already registered")) {
        error.value = "This email address is already registered. Please use a different email.";
      }
      
      // Map other API error fields to form fields if needed
      if (err.response.data.errors) {
        for (const field in err.response.data.errors) {
          if (field === 'username') {
            errors.username = err.response.data.errors[field][0];
          } else if (field === 'new_password') {
            errors.newPassword = err.response.data.errors[field][0];
          } else if (field === 'current_password') {
            errors.currentPassword = err.response.data.errors[field][0];
          } else if (field === 'confirm_password') {
            errors.confirmPassword = err.response.data.errors[field][0];
          }
        }
      }
    } else if (err.response?.status === 401) {
      error.value = 'Current password is incorrect';
      errors.currentPassword = 'Current password is incorrect';
    } else if (err.response?.status === 404) {
      error.value = 'User not found';
    } else if (err.response?.status === 422) {
      // Handle validation errors
      error.value = 'Validation error. Please check your input.';
      
      if (err.response.data?.detail) {
        const validationErrors = err.response.data.detail;
        for (const validationError of validationErrors) {
          const field = validationError.loc[validationError.loc.length - 1];
          if (field === 'username') {
            errors.username = validationError.msg;
          } else if (field === 'new_password') {
            errors.newPassword = validationError.msg;
          } else if (field === 'current_password') {
            errors.currentPassword = validationError.msg;
          }
        }
      }
    } else {
      // Generic error
      error.value = 'Failed to update profile. Please try again.';
    }
  } finally {
    isSaving.value = false;
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await authStore.fetchCurrentUser()
  } catch (err) {
    error.value = 'Failed to load user profile'
  } finally {
    loading.value = false
  }
})
</script> 