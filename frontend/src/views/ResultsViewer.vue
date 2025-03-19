<template>
  <div class="h-screen flex flex-col bg-gray-50">
    <div v-if="loading" class="flex flex-col items-center justify-center h-full">
      <svg class="animate-spin h-10 w-10 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="mt-4 text-sm font-medium text-gray-700">Loading results...</p>
    </div>
    
    <div v-else-if="error" class="flex flex-col items-center justify-center h-full p-6">
      <div class="rounded-md bg-red-50 p-4 mb-6 w-full max-w-lg">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-red-800">{{ error }}</p>
          </div>
        </div>
      </div>
      <button 
        @click="$router.push('/executions')" 
        class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Return to Executions
      </button>
    </div>
    
    <div v-else class="flex flex-col h-full">
      <div class="flex justify-between items-center p-4 bg-white border-b border-gray-200 shadow-sm z-10">
        <div class="flex items-center">
          <button 
            @click="$router.go(-1)" 
            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <svg class="-ml-0.5 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
            </svg>
            Back
          </button>
          <h1 class="ml-4 text-lg font-medium text-gray-900">Notebook Results</h1>
        </div>
        
        <div>
          <div class="flex space-x-2">
            <button 
              v-if="notebookUrl"
              @click="downloadNotebook" 
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
              Download Notebook
            </button>
            <button 
              @click="download" 
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <svg class="-ml-1 mr-2 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
              Download HTML
            </button>
          </div>
        </div>
      </div>
      
      <div class="flex-1 relative overflow-hidden bg-white m-2 sm:m-4 rounded-lg shadow">
        <iframe 
          v-if="blobUrl" 
          :src="blobUrl" 
          class="absolute inset-0 w-full h-full"
          frameborder="0"
          title="Notebook Results"
          referrerpolicy="no-referrer"
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-downloads allow-modals"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        ></iframe>
        
        <div v-else class="flex flex-col items-center justify-center h-full p-6">
          <svg class="h-12 w-12 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span class="mt-2 text-sm text-gray-500">No content available to display</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { getApiUrl } from '@/utils/env'
const route = useRoute()
const loading = ref(true)
const error = ref(null)
const rawContent = ref(null)
const url = ref(null)
const notebookUrl = ref(null)
const htmlContent = ref(null)
const blobUrl = ref(null)

// Get the API URL
const API_URL = getApiUrl()

// Get the paths from the query parameters
const path = computed(() => route.query.path || '')
const notebookPath = computed(() => route.query.notebookPath || '')

onMounted(async () => {
  if (!path.value) {
    error.value = 'No content path specified'
    loading.value = false
    return
  }
  
  try {
    // Process HTML path
    if (path.value.startsWith('http')) {
      url.value = path.value
    } 
    else if (path.value.startsWith('s3://')) {
      const s3Path = path.value.replace(/^s3:\/\/[^\/]+\//, '')
      url.value = `${API_URL}/static/reports/${encodeURIComponent(s3Path)}`
    }
    else {
      url.value = `${API_URL}/static/reports/${encodeURIComponent(path.value)}`
    }

    // Process notebook path if available
    if (notebookPath.value) {
      if (notebookPath.value.startsWith('http')) {
        notebookUrl.value = notebookPath.value
      } 
      else if (notebookPath.value.startsWith('s3://')) {
        const s3Path = notebookPath.value.replace(/^s3:\/\/[^\/]+\//, '')
        notebookUrl.value = `${API_URL}/static/reports/${encodeURIComponent(s3Path)}`
      }
      else {
        notebookUrl.value = `${API_URL}/static/reports/${encodeURIComponent(notebookPath.value)}`
      }
    }
    
    // Fetch the HTML content with authentication
    if (url.value) {
      const response = await fetch(url.value, { 
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`Failed to load content: ${response.statusText}`);
      }
      
      // Get the HTML content as text
      htmlContent.value = await response.text();
      
      // Create a data URL for the iframe instead of a blob URL
      blobUrl.value = `data:text/html;charset=utf-8,${encodeURIComponent(htmlContent.value)}`;
    }
  } catch (err) {
    console.error('Error loading results:', err)
    error.value = `Unable to load results: ${err.message}`
  } finally {
    loading.value = false
  }
})

// Clean up blob URL when component is destroyed
onBeforeUnmount(() => {
  if (blobUrl.value) {
    URL.revokeObjectURL(blobUrl.value);
  }
})

function download() {
  if (url.value) {
    // Instead of direct link, use fetch with auth token and convert to blob
    fetch(url.value, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`Download failed: ${response.status} ${response.statusText}`);
      }
      return response.blob();
    })
    .then(blob => {
      // Create a data URL from the blob
      const url = URL.createObjectURL(blob);
      
      // Create a link and trigger download
      const link = document.createElement('a');
      link.href = url;
      link.download = `results-${Date.now()}.html`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up the URL object
      URL.revokeObjectURL(url);
    })
    .catch(err => {
      console.error('Error downloading HTML:', err);
      error.value = `Failed to download: ${err.message}`;
    });
  }
}

function downloadNotebook() {
  if (notebookUrl.value) {
    // Instead of direct link, use fetch with auth token and convert to blob
    fetch(notebookUrl.value, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`Download failed: ${response.status} ${response.statusText}`);
      }
      return response.blob();
    })
    .then(blob => {
      // Create a data URL from the blob
      const url = URL.createObjectURL(blob);
      
      // Create a link and trigger download
      const link = document.createElement('a');
      link.href = url;
      link.download = `notebook-${Date.now()}.ipynb`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up the URL object
      URL.revokeObjectURL(url);
    })
    .catch(err => {
      console.error('Error downloading notebook:', err);
      error.value = `Failed to download: ${err.message}`;
    });
  }
}
</script> 