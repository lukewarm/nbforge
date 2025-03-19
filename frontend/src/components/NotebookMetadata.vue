<template>
  <div class="bg-white shadow overflow-hidden sm:rounded-lg">
    <div class="px-4 py-5 sm:px-6">
      <h3 class="text-lg leading-6 font-medium text-gray-900">
        Notebook Metadata
      </h3>
      <p class="mt-1 max-w-2xl text-sm text-gray-500">
        Details and configuration for this notebook.
      </p>
    </div>
    <div class="border-t border-gray-200">
      <dl>
        <!-- Identity -->
        <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt class="text-sm font-medium text-gray-500">Name</dt>
          <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
            {{ metadata.identity.name || 'Unnamed Notebook' }}
          </dd>
        </div>
        <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt class="text-sm font-medium text-gray-500">Description</dt>
          <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
            {{ metadata.identity.description || 'No description provided' }}
          </dd>
        </div>
        <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt class="text-sm font-medium text-gray-500">Author</dt>
          <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
            {{ metadata.identity.author || 'Unknown' }}
          </dd>
        </div>
        <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt class="text-sm font-medium text-gray-500">Tags</dt>
          <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tag in metadata.identity.tags"
                :key="tag"
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
              >
                {{ tag }}
              </span>
              <span v-if="!metadata.identity.tags || metadata.identity.tags.length === 0" class="text-gray-500">
                No tags
              </span>
            </div>
          </dd>
        </div>
        
        <!-- Resources -->
        <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt class="text-sm font-medium text-gray-500">CPU</dt>
          <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
            {{ metadata.resources.cpu_milli ? `${metadata.resources.cpu_milli}m` : 'Default' }}
          </dd>
        </div>
        <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt class="text-sm font-medium text-gray-500">Memory</dt>
          <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
            {{ metadata.resources.memory_mib ? `${metadata.resources.memory_mib}Mi` : 'Default' }}
          </dd>
        </div>
        <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt class="text-sm font-medium text-gray-500">GPU</dt>
          <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
            {{ metadata.resources.gpu || 'None' }}
          </dd>
        </div>
        
        <!-- Requirements -->
        <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt class="text-sm font-medium text-gray-500">Requirements</dt>
          <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
            <ul v-if="metadata.requirements && metadata.requirements.length > 0" class="border border-gray-200 rounded-md divide-y divide-gray-200">
              <li v-for="(req, index) in metadata.requirements" :key="index" class="pl-3 pr-4 py-3 flex items-center justify-between text-sm">
                <div class="w-0 flex-1 flex items-center">
                  <span class="ml-2 flex-1 w-0 truncate">{{ req }}</span>
                </div>
              </li>
            </ul>
            <span v-else class="text-gray-500">No requirements specified</span>
          </dd>
        </div>
        
        <!-- Parameters -->
        <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt class="text-sm font-medium text-gray-500">Parameters</dt>
          <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
            <ul v-if="metadata.parameters && metadata.parameters.length > 0" class="border border-gray-200 rounded-md divide-y divide-gray-200">
              <li v-for="param in metadata.parameters" :key="param.name" class="pl-3 pr-4 py-3 flex items-center justify-between text-sm">
                <div class="w-0 flex-1 flex items-center">
                  <span class="ml-2 flex-1 w-0 truncate">
                    <span class="font-medium">{{ param.name }}</span>
                    <span v-if="param.type" class="text-gray-500"> ({{ param.type }})</span>
                    <span v-if="param.description" class="block text-gray-500">{{ param.description }}</span>
                  </span>
                </div>
                <div v-if="param.default !== undefined" class="ml-4 flex-shrink-0">
                  <span class="font-medium text-indigo-600">Default: {{ formatDefaultValue(param.default) }}</span>
                </div>
              </li>
            </ul>
            <span v-else class="text-gray-500">No parameters defined</span>
          </dd>
        </div>
      </dl>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  metadata: {
    type: Object,
    required: true,
    default: () => ({
      identity: {},
      resources: {},
      requirements: [],
      parameters: []
    })
  }
})

// Format default value based on type
const formatDefaultValue = (value) => {
  if (value === null) return 'null'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}
</script> 