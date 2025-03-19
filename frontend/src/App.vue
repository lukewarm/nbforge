<template>
  <div class="min-h-screen bg-gray-100">
    <NavBar />
    <main class="py-10">
      <div v-if="routeError" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center">
        <div class="bg-red-50 border-l-4 border-red-400 p-4 my-4 text-left">
          <p class="text-red-700">Error loading page. Please try refreshing.</p>
        </div>
      </div>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" @error="handleRouteError" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import { useAuthStore } from '@/stores/auth'

const routeError = ref(false)
const authStore = useAuthStore()

function handleRouteError(error) {
  console.error('Route error:', error)
  routeError.value = true
}

onMounted(async () => {
  try {
    await authStore.initAuth()
  } catch (error) {
    console.error('Failed to initialize auth:', error)
  }
})
</script> 