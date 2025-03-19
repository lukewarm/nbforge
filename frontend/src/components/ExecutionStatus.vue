<template>
  <div class="inline-flex items-center">
    <!-- Display the status with appropriate colors -->
    <span 
      class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full"
      :class="{
        'bg-gray-100 text-gray-800': status === 'pending',
        'bg-blue-100 text-blue-800': status === 'submitted',
        'bg-yellow-100 text-yellow-800': status === 'running',
        'bg-green-100 text-green-800': status === 'completed',
        'bg-red-100 text-red-800': status === 'failed',
        'bg-gray-100 text-gray-800': status === 'cancelled'
      }"
    >
      <!-- Show loading spinner for active statuses if loading is true -->
      <svg 
        v-if="loading && (status === 'pending' || status === 'running' || status === 'submitted')"
        class="animate-spin -ml-1 mr-2 h-4 w-4" 
        :class="{
          'text-gray-600': status === 'pending' || status === 'cancelled',
          'text-blue-600': status === 'submitted',
          'text-yellow-600': status === 'running'
        }"
        xmlns="http://www.w3.org/2000/svg" 
        fill="none" 
        viewBox="0 0 24 24"
      >
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      
      <!-- Display the status icon based on the status -->
      <span v-else class="mr-1.5">
        <!-- Pending icon -->
        <svg v-if="status === 'pending'" class="h-3.5 w-3.5 text-gray-600" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
        </svg>
        
        <!-- Submitted icon -->
        <svg v-else-if="status === 'submitted'" class="h-3.5 w-3.5 text-blue-600" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clip-rule="evenodd" />
        </svg>
        
        <!-- Running icon -->
        <svg v-else-if="status === 'running'" class="h-3.5 w-3.5 text-yellow-600" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
        </svg>
        
        <!-- Completed icon -->
        <svg v-else-if="status === 'completed'" class="h-3.5 w-3.5 text-green-600" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        
        <!-- Failed icon -->
        <svg v-else-if="status === 'failed'" class="h-3.5 w-3.5 text-red-600" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        
        <!-- Cancelled icon -->
        <svg v-else-if="status === 'cancelled'" class="h-3.5 w-3.5 text-gray-600" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clip-rule="evenodd" />
        </svg>
      </span>
      
      <!-- Status text -->
      {{ status.charAt(0).toUpperCase() + status.slice(1) }}
    </span>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

defineProps({
  status: {
    type: String,
    required: true,
    validator: (value) => {
      return ['pending', 'submitted', 'running', 'completed', 'failed', 'cancelled'].includes(value.toLowerCase());
    }
  },
  loading: {
    type: Boolean,
    default: false
  }
});
</script> 