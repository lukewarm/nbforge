import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Import components
import NotebookList from '@/views/NotebookList.vue'
import ExecutionList from '@/views/ExecutionList.vue'
import ExecutionDetail from '@/views/ExecutionDetail.vue'
import ResultsViewer from '@/views/ResultsViewer.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import ForgotPassword from '@/views/ForgotPassword.vue'
import ResetPassword from '@/views/ResetPassword.vue'
// Import admin components
import AdminLayout from '@/layouts/AdminLayout.vue'
import UserManagement from '@/views/admin/UserManagement.vue'
import ServiceAccounts from '@/views/admin/ServiceAccounts.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: NotebookList,
    meta: { requiresAuth: true }
  },
  {
    path: '/notebooks',
    name: 'notebooks',
    component: NotebookList,
    meta: { requiresAuth: true }
  },
  {
    path: '/list',
    redirect: '/notebooks',
    meta: { requiresAuth: true }
  },
  {
    path: '/notebook/:path(.*)',
    name: 'notebook-detail',
    component: () => import('../views/NotebookDetail.vue'),
    props: (route) => ({
      path: decodeURIComponent(route.params.path)
    }),
    meta: { requiresAuth: true }
  },
  {
    path: '/executions',
    name: 'executions',
    component: ExecutionList,
    meta: { requiresAuth: true }
  },
  {
    path: '/executions/:id',
    name: 'execution-detail',
    component: ExecutionDetail,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/results',
    name: 'results-viewer',
    component: ResultsViewer,
    props: (route) => ({ path: route.query.path }),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: { guest: true }
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: ForgotPassword,
    meta: { guest: true }
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: ResetPassword,
    meta: { guest: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/UserProfile.vue'),
    meta: { requiresAuth: true }
  },
  // Admin routes
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: { name: 'admin-users' }
      },
      {
        path: 'users',
        name: 'admin-users',
        component: UserManagement,
        meta: { requiresAuth: true }
      },
      {
        path: 'service-accounts',
        name: 'admin-service-accounts',
        component: ServiceAccounts,
        meta: { requiresAuth: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  sensitive: true
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  try {
    // Check if we need to initialize auth
    if (!authStore.user && (authStore.token || !authStore.demoChecked)) {
      // First check if in demo mode and set up if needed
      const isDemoAuthenticated = await authStore.checkAndSetupDemoMode()
      
      // If not in demo mode but has token, initialize auth
      if (!isDemoAuthenticated && authStore.token) {
        await authStore.initAuth()
      }
    }
    
    // In demo mode, redirect login/register to home
    if (authStore.demoMode && (to.name === 'login' || to.name === 'register')) {
      return next({ name: 'home' })
    }
    
    // Check if the route requires authentication
    if (to.matched.some(record => record.meta.requiresAuth)) {
      // If not authenticated, redirect to login
      if (!authStore.isAuthenticated) {
        return next({ name: 'login', query: { redirect: to.fullPath } })
      }
    }
    
    // If route is for guests only and user is authenticated, redirect to home
    if (to.matched.some(record => record.meta.guest) && authStore.isAuthenticated) {
      return next({ name: 'home' })
    }
    
    next()
  } catch (error) {
    console.error('Error in router guard:', error)
    next()
  }
})

export default router 