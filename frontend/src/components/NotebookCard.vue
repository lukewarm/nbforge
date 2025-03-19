<template>
  <div 
    class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow duration-200 cursor-pointer"
    @click="$emit('click')"
  >
    <div class="px-4 py-5 sm:p-6">
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <h3 class="text-lg font-medium text-gray-900 truncate">
            {{ notebook.metadata?.identity?.name || notebook.filename || notebook.path }}
          </h3>
          <p v-if="notebook.metadata?.identity?.description" class="mt-1 text-sm text-gray-500 line-clamp-2">
            {{ notebook.metadata.identity.description }}
          </p>
        </div>
        <div class="ml-4">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            Python {{ notebook.metadata?.resources?.python_version || '3.x' }}
          </span>
        </div>
      </div>
      
      <div class="mt-4">
        <div class="flex items-center text-sm text-gray-500">
          <span class="truncate">{{ notebook.path }}</span>
        </div>
        
        <div class="mt-2 flex flex-wrap gap-2">
          <span 
            v-for="tag in notebook.metadata?.identity?.tags || []" 
            :key="tag"
            class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
          >
            {{ tag }}
          </span>
        </div>
        
        <div class="mt-4 flex items-center justify-between">
          <div class="flex items-center text-sm text-gray-500">
            <span>{{ notebook.metadata?.parameters?.length || 0 }} parameters</span>
            <span class="mx-2">•</span>
            <span>{{ notebook.metadata?.requirements?.length || 0 }} requirements</span>
          </div>
          <div>
            <button 
              class="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              @click.stop="$emit('execute')"
            >
              Execute
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  notebook: {
    type: Object,
    required: true
  }
})

defineEmits(['click', 'execute'])
</script> 