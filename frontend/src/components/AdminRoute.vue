<template>
  <div>
    <!-- Loading state -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <svg class="animate-spin h-10 w-10 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="mt-2 text-gray-600">Checking admin access...</p>
    </div>
    
    <!-- Error state - access denied -->
    <div v-else-if="error" class="max-w-3xl mx-auto mt-8 p-6 bg-red-50 border-l-4 border-red-400 rounded-md">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Access Denied</h3>
          <div class="mt-2 text-sm text-red-700">
            <p>{{ error }}</p>
          </div>
          <div class="mt-4">
            <button @click="goToHome" class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
              Go to Home
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Success state - show child content -->
    <div v-else>
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  // Optional custom error message
  errorMessage: {
    type: String,
    default: 'You do not have permission to access this page. Only administrators can access this area.'
  }
})

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref(null)

function goToHome() {
  router.push('/')
}

onMounted(async () => {
  try {
    // Check if user is authenticated
    if (!authStore.isAuthenticated) {
      // Store the requested URL to redirect back after login
      const currentPath = router.currentRoute.value.fullPath
      router.push(`/login?redirect=${encodeURIComponent(currentPath)}`)
      return
    }
    
    // Check if user is admin (superuser)
    if (!authStore.user || !authStore.user.is_superuser) {
      error.value = props.errorMessage
    }
  } catch (err) {
    console.error('Error checking admin access:', err)
    error.value = 'An error occurred while checking your access. Please try again.'
  } finally {
    loading.value = false
  }
})
</script> 