<template>
  <ModalDialog @close="cancel">
    <template #title>
      {{ title }}
    </template>
    
    <template #content>
      <div class="text-sm text-gray-500">
        {{ message }}
      </div>
    </template>
    
    <template #footer>
      <button 
        type="button" 
        class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
        @click="confirm"
      >
        {{ confirmButtonText }}
      </button>
      <button 
        type="button" 
        class="mt-3 w-full sm:mt-0 sm:w-auto inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:text-sm"
        @click="cancel"
      >
        {{ cancelButtonText }}
      </button>
    </template>
  </ModalDialog>
</template>

<script setup>
import ModalDialog from './ModalDialog.vue';

const props = defineProps({
  title: {
    type: String,
    default: 'Confirm Action'
  },
  message: {
    type: String,
    required: true
  },
  confirmButtonText: {
    type: String,
    default: 'Confirm'
  },
  cancelButtonText: {
    type: String,
    default: 'Cancel'
  }
});

const emit = defineEmits(['confirm', 'cancel']);

function confirm() {
  emit('confirm');
}

function cancel() {
  emit('cancel');
}
</script> 