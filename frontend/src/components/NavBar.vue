<template>
  <nav class="bg-white shadow">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex">
          <!-- Logo -->
          <div class="flex-shrink-0 flex items-center">
            <router-link to="/" class="text-xl font-bold text-indigo-600">
              NBForge
            </router-link>
          </div>

          <!-- Navigation Links (Desktop) -->
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <router-link
              v-for="item in navigation"
              :key="item.name"
              :to="item.to"
              class="inline-flex items-center px-1 pt-1 border-b-2"
              :class="[
                $route.name === item.to.name
                  ? 'border-indigo-500 text-gray-900'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              ]"
            >
              {{ item.name }}
            </router-link>
          </div>
        </div>

        <!-- Mobile menu button -->
        <div class="flex items-center sm:hidden">
          <button 
            @click="mobileMenuOpen = !mobileMenuOpen" 
            class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
          >
            <span class="sr-only">Open main menu</span>
            <!-- Icon when menu is closed (menu/hamburger) -->
            <svg
              v-if="!mobileMenuOpen"
              class="h-6 w-6"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
            <!-- Icon when menu is open (x) -->
            <svg
              v-else
              class="h-6 w-6"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <!-- User Menu (Desktop) -->
        <div class="hidden sm:ml-6 sm:flex sm:items-center">
          <!-- Show login button if not authenticated -->
          <router-link
            v-if="!authStore.isAuthenticated"
            to="/login"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Sign in
          </router-link>
          
          <!-- User menu if authenticated -->
          <template v-else>
            <!-- Bell icon removed as requested -->

            <!-- Profile dropdown -->
            <Menu as="div" class="ml-3 relative">
              <MenuButton class="flex rounded-full bg-white text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 hover:ring-2 hover:ring-indigo-300 transition-all duration-150">
                <span class="sr-only">Open user menu</span>
                <UserAvatar :user="authStore.user" size="xs" />
              </MenuButton>

              <transition
                enter-active-class="transition ease-out duration-200"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <MenuItems class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
                  <MenuItem v-slot="{ active }">
                    <div
                      class="block px-4 py-2 text-sm text-gray-700 border-b border-gray-100"
                    >
                      <div class="flex items-center mb-1">
                        <svg class="mr-2 h-4 w-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                          <path fill-rule="evenodd" d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z" clip-rule="evenodd" />
                        </svg>
                        <div class="font-medium">{{ authStore.user?.full_name || authStore.user?.username }}</div>
                      </div>
                      <div class="text-gray-500 text-xs ml-6">{{ authStore.user?.email }}</div>
                    </div>
                  </MenuItem>
                  <MenuItem v-slot="{ active }">
                    <router-link
                      to="/profile"
                      :class="[active ? 'bg-gray-100' : '', 'block px-4 py-2 text-sm text-gray-700']"
                    >
                      <div class="flex items-center">
                        <svg class="mr-2 h-4 w-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                          <path fill-rule="evenodd" d="M18.685 19.097A9.723 9.723 0 0021.75 12c0-5.385-4.365-9.75-9.75-9.75S2.25 6.615 2.25 12a9.723 9.723 0 003.065 7.097A9.716 9.716 0 0012 21.75a9.716 9.716 0 006.685-2.653zm-12.54-1.285A7.486 7.486 0 0112 15a7.486 7.486 0 015.855 2.812A8.224 8.224 0 0112 20.25a8.224 8.224 0 01-5.855-2.438zM15.75 9a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" clip-rule="evenodd" />
                        </svg>
                        Your Profile
                      </div>
                    </router-link>
                  </MenuItem>
                  <!-- Admin link (only for superusers) -->
                  <MenuItem v-if="authStore.user?.is_superuser" v-slot="{ active }">
                    <router-link
                      to="/admin"
                      :class="[active ? 'bg-gray-100' : '', 'block px-4 py-2 text-sm text-gray-700']"
                    >
                      <div class="flex items-center">
                        <svg class="mr-2 h-4 w-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                          <path fill-rule="evenodd" d="M11.078 2.25c-.917 0-1.699.663-1.85 1.567L9.05 4.889c-.02.12-.115.26-.297.348a7.493 7.493 0 00-.986.57c-.166.115-.334.126-.45.083L6.3 5.508a1.875 1.875 0 00-2.282.819l-.922 1.597a1.875 1.875 0 00.432 2.385l.84.692c.095.078.17.229.154.43a7.598 7.598 0 000 1.139c.015.2-.059.352-.153.43l-.841.692a1.875 1.875 0 00-.432 2.385l.922 1.597a1.875 1.875 0 002.282.818l1.019-.382c.115-.043.283-.031.45.082.312.214.641.405.985.57.182.088.277.228.297.35l.178 1.071c.151.904.933 1.567 1.85 1.567h1.844c.916 0 1.699-.663 1.85-1.567l.178-1.072c.02-.12.114-.26.297-.349.344-.165.673-.356.985-.57.167-.114.335-.125.45-.082l1.02.382a1.875 1.875 0 002.28-.819l.923-1.597a1.875 1.875 0 00-.432-2.385l-.84-.692c-.095-.078-.17-.229-.154-.43a7.614 7.614 0 000-1.139c-.016-.2.059-.352.153-.43l.84-.692c.708-.582.891-1.59.433-2.385l-.922-1.597a1.875 1.875 0 00-2.282-.818l-1.02.382c-.114.043-.282.031-.449-.083a7.49 7.49 0 00-.985-.57c-.183-.087-.277-.227-.297-.348l-.179-1.072a1.875 1.875 0 00-1.85-1.567h-1.843zM12 15.75a3.75 3.75 0 100-7.5 3.75 3.75 0 000 7.5z" clip-rule="evenodd" />
                        </svg>
                        Admin Panel
                      </div>
                    </router-link>
                  </MenuItem>
                  <MenuItem v-slot="{ active }">
                    <a
                      href="#"
                      :class="[active ? 'bg-gray-100' : '', 'block px-4 py-2 text-sm text-gray-700']"
                      @click="logout"
                    >
                      <div class="flex items-center">
                        <svg class="mr-2 h-4 w-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                          <path fill-rule="evenodd" d="M7.5 3.75A1.5 1.5 0 006 5.25v13.5a1.5 1.5 0 001.5 1.5h6a1.5 1.5 0 001.5-1.5V15a.75.75 0 011.5 0v3.75a3 3 0 01-3 3h-6a3 3 0 01-3-3V5.25a3 3 0 013-3h6a3 3 0 013 3V9A.75.75 0 0115 9V5.25a1.5 1.5 0 00-1.5-1.5h-6zm5.03 4.72a.75.75 0 010 1.06l-1.72 1.72h10.94a.75.75 0 010 1.5H10.81l1.72 1.72a.75.75 0 11-1.06 1.06l-3-3a.75.75 0 010-1.06l3-3a.75.75 0 011.06 0z" clip-rule="evenodd" />
                        </svg>
                        Sign out
                      </div>
                    </a>
                  </MenuItem>
                </MenuItems>
              </transition>
            </Menu>
          </template>
        </div>
      </div>
    </div>
    
    <!-- Mobile menu -->
    <div 
      v-show="mobileMenuOpen" 
      class="sm:hidden bg-white border-t border-gray-200"
    >
      <div class="pt-2 pb-3 space-y-1">
        <!-- Navigation Links -->
        <router-link
          v-for="item in navigation"
          :key="item.name"
          :to="item.to"
          @click="mobileMenuOpen = false"
          class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
          :class="[
            $route.name === item.to.name
              ? 'border-indigo-500 text-indigo-700 bg-indigo-50'
              : 'border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700'
          ]"
        >
          {{ item.name }}
        </router-link>
      </div>
      
      <!-- Mobile user menu -->
      <div class="pt-4 pb-3 border-t border-gray-200">
        <div v-if="authStore.isAuthenticated" class="flex items-center px-4">
          <div class="flex-shrink-0">
            <UserAvatar :user="authStore.user" size="sm" />
          </div>
          <div class="ml-3">
            <div class="text-base font-medium text-gray-800">{{ authStore.user?.full_name || authStore.user?.username }}</div>
            <div class="text-sm font-medium text-gray-500">{{ authStore.user?.email }}</div>
          </div>
        </div>
        
        <div class="mt-3 space-y-1">
          <!-- Show login button if not authenticated -->
          <router-link
            v-if="!authStore.isAuthenticated"
            to="/login"
            @click="mobileMenuOpen = false"
            class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700"
          >
            Sign in
          </router-link>
          
          <!-- User menu if authenticated -->
          <template v-else>
            <router-link
              to="/profile"
              @click="mobileMenuOpen = false"
              class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700"
            >
              Your Profile
            </router-link>
            
            <!-- Admin link (only for superusers) -->
            <router-link
              v-if="authStore.user?.is_superuser"
              to="/admin"
              @click="mobileMenuOpen = false"
              class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700"
            >
              Admin Panel
            </router-link>
            
            <a
              href="#"
              @click="logout(); mobileMenuOpen = false"
              class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700"
            >
              Sign out
            </a>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { BellIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { getApiUrl } from '@/utils/env'
import UserAvatar from '@/components/avatar/UserAvatar.vue'

const navigation = [
  { name: 'Notebooks', to: { name: 'notebooks' } },
  { name: 'Executions', to: { name: 'executions' } },
]

const authStore = useAuthStore()
const isDemoMode = ref(false)
const mobileMenuOpen = ref(false)

// Get the API URL
const API_URL = getApiUrl()

const logout = () => {
  authStore.logout()
}

// Get OAuth config for login buttons
async function getOAuthConfig() {
  try {
    const response = await fetch(`${API_URL}/auth/config`)
    const data = await response.json()
    oauthConfig.value = {
      google: data.oauth_providers?.google || false,
      github: data.oauth_providers?.github || false
    }
  } catch (error) {
    console.error('Failed to fetch auth configuration:', error)
  }
}

onMounted(async () => {
  try {
    const response = await fetch(`${API_URL}/auth/config`)
    const config = await response.json()
    
    // Check if we're in demo mode and using a demo account
    if (config.demo_mode && authStore.isLoggedIn) {
      const demoUsers = config.demo_users || []
      isDemoMode.value = demoUsers.includes(authStore.user?.email)
    }
  } catch (error) {
    console.error('Failed to check demo mode:', error)
  }
})
</script> 