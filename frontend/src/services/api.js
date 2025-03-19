import axios from 'axios'
import { handleApiError } from '@/utils/errorHandler'
import router from '@/router'
import { getApiUrl } from '@/utils/env'

const baseURL = getApiUrl()

const api = axios.create({
  baseURL: baseURL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    const errorMessage = handleApiError(error)
    console.error(errorMessage)
    return Promise.reject(error)
  }
)

// Authentication API endpoints
export const authApi = {
  login: (credentials) => {
    const formData = new FormData()
    formData.append('username', credentials.email)
    formData.append('password', credentials.password)
    
    return api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  register: (userData) => api.post('/auth/register', userData),
  me: () => api.get('/auth/me'),
  googleLogin: () => api.get('/auth/oauth/google'),
  githubLogin: () => api.get('/auth/oauth/github')
}

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token')
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login')
      }
    }
    return Promise.reject(error)
  }
)

export const notebooksApi = {
  list: (prefix = '') => api.get(`/notebooks?prefix=${prefix}`),
  get: (path) => {
    // Simple encoding for API requests
    return api.get(`/notebooks/${encodeURIComponent(path)}`);
  },
  upload: (formData) => api.post('/notebooks/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  execute: (path, executionData) => {
    console.log('Calling execute API with:', executionData);
    return api.post(`/executions`, executionData)
      .then(response => {
        console.log('Raw execute API response:', response);
        
        // Check for duplicate execution response structure
        if (response.data && response.data.is_duplicate === true) {
          console.log('Duplicate execution detected in response:', response.data);
          
          // Check if we have a properly formed execution object
          if (response.data.execution) {
            console.log('Execution data found in duplicate response:', response.data.execution);
          } else {
            console.warn('No execution data in duplicate response - this might cause issues');
          }
        }
        
        return response;
      })
      .catch(error => {
        console.error('Execute API error:', error);
        throw error;
      });
  },
  checkDuplicate: (executionData) => api.post('/executions/check-duplicate', executionData),
  validate: (formData) => api.post('/notebooks/validate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  updateMetadata: (formData) => api.post('/notebooks/update-metadata', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    responseType: 'blob'
  })
}

export const executionsApi = {
  list: () => api.get('/executions'),
  get: (id) => {
    if (!id) {
      console.error('Cannot fetch execution with undefined ID');
      return Promise.reject(new Error('Invalid execution ID: undefined'));
    }
    return api.get(`/executions/${id}`);
  },
  getReport: (id) => {
    if (!id) {
      console.error('Cannot fetch execution report with undefined ID');
      return Promise.reject(new Error('Invalid execution ID: undefined'));
    }
    return api.get(`/executions/${id}/report`);
  },
  cancel: (id) => {
    if (!id) {
      console.error('Cannot cancel execution with undefined ID');
      return Promise.reject(new Error('Invalid execution ID: undefined'));
    }
    return api.post(`/executions/${id}/cancel`);
  }
} 