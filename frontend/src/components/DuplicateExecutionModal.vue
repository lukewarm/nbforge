<template>
  <Transition
    enter-active-class="transition ease-out duration-200"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition ease-in duration-150"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div v-if="isOpen" class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="cancel"></div>

        <!-- Modal panel -->
        <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          <div>
            <!-- Warning icon -->
            <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100">
              <svg class="h-6 w-6 text-yellow-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            
            <!-- Title and message -->
            <div class="mt-3 text-center sm:mt-5">
              <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                Duplicate Execution Detected
              </h3>
              <div class="mt-2">
                <p class="text-sm text-gray-500">
                  A similar execution with the same parameters for this notebook already exists.
                </p>
              </div>
            </div>

            <!-- Execution details -->
            <div class="mt-4 border rounded-md p-4 bg-gray-50">
              <div class="space-y-2">
                <div>
                  <span class="text-xs font-medium text-gray-500">Notebook:</span>
                  <p class="text-sm text-gray-900 truncate">{{ execution.notebook_path }}</p>
                </div>
                <div>
                  <span class="text-xs font-medium text-gray-500">Created:</span>
                  <p class="text-sm text-gray-900">{{ formatDate(execution.created_at) }}</p>
                </div>
                <div>
                  <span class="text-xs font-medium text-gray-500">Status:</span>
                  <span :class="statusClass">{{ execution.status }}</span>
                </div>
                <div v-if="showParameters">
                  <span class="text-xs font-medium text-gray-500">Parameters:</span>
                  <pre class="text-xs text-gray-900 mt-1 bg-white p-2 rounded border overflow-auto max-h-32">{{ JSON.stringify(execution.parameters, null, 2) }}</pre>
                </div>
              </div>
            </div>
          </div>

          <!-- Action buttons -->
          <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-3 sm:gap-3 sm:grid-flow-row-dense">
            <button 
              type="button" 
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:col-start-3 sm:text-sm"
              @click="runAnyway"
            >
              Run Anyway
            </button>
            <button 
              type="button" 
              class="mt-3 w-full inline-flex justify-center rounded-md border border-indigo-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-indigo-700 hover:bg-indigo-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:col-start-2 sm:text-sm"
              @click="useExisting"
            >
              Use Existing
            </button>
            <button 
              type="button" 
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:col-start-1 sm:text-sm"
              @click="cancel"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';

// Define props
const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  execution: {
    type: Object,
    required: true
  },
  showParameters: {
    type: Boolean,
    default: true
  }
});

// Define emits
const emit = defineEmits(['run-anyway', 'use-existing', 'cancel']);

// Router for navigation
const router = useRouter();

// Computed status class based on status
const statusClass = computed(() => {
  const baseClass = 'text-sm font-medium inline-flex items-center px-2 py-0.5 rounded';
  
  switch (props.execution.status) {
    case 'pending':
      return `${baseClass} bg-yellow-100 text-yellow-800`;
    case 'running':
      return `${baseClass} bg-blue-100 text-blue-800`;
    case 'completed':
      return `${baseClass} bg-green-100 text-green-800`;
    case 'failed':
      return `${baseClass} bg-red-100 text-red-800`;
    case 'cancelled':
      return `${baseClass} bg-gray-100 text-gray-800`;
    default:
      return `${baseClass} bg-gray-100 text-gray-800`;
  }
});

// Format date
function formatDate(dateString) {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleString();
}

// Action functions
function runAnyway() {
  emit('run-anyway');
}

function useExisting() {
  // Check if we have a valid execution ID before navigating
  if (props.execution && props.execution.id) {
    console.log('Using existing execution with ID:', props.execution.id);
    emit('use-existing');
    router.push({ name: 'execution-detail', params: { id: props.execution.id } });
  } else {
    console.error('Cannot navigate to execution detail: Missing execution ID');
    emit('use-existing-error');
  }
}

function cancel() {
  emit('cancel');
}
</script> 