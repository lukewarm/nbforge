import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import { useAuthStore } from './stores/auth'
import { getApiUrl, getNodeEnv } from './utils/env'

// Import Toast
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";

const app = createApp(App)
const pinia = createPinia()

// Set up environment variables with fallback to window.env
const env = {
  API_URL: getApiUrl(),
  // Add other environment variables as needed
  NODE_ENV: getNodeEnv()
}

// Make env available globally in the app
app.config.globalProperties.$env = env

// Toast options
const toastOptions = {
  position: "top-right",
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: "button",
  icon: true,
  rtl: false
};

app.use(pinia)
app.use(router)
app.use(Toast, toastOptions)

// Initialize auth state before mounting the app
const authStore = useAuthStore(pinia)
authStore.initAuth().finally(() => {
  app.mount('#app')
}) 