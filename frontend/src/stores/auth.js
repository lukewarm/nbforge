import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '@/router'
import { getApiUrl } from '@/utils/env'

const API_URL = getApiUrl()

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const loading = ref(false)
  const error = ref(null)
  const demoMode = ref(false)
  const demoChecked = ref(false)
  
  const isAuthenticated = computed(() => !!token.value)
  
  // Initialize user from token if available
  async function initAuth() {
    if (token.value) {
      try {
        await fetchCurrentUser()
        // If we successfully fetched the user, check if we're in demo mode
        try {
          const response = await fetch(`${API_URL}/auth/config`)
          const config = await response.json()
          demoMode.value = config.demo_mode || false
          console.log('Demo mode status:', demoMode.value)
        } catch (err) {
          console.error('Failed to check demo mode config:', err)
        }
      } catch (err) {
        console.error('Token validation failed:', err)
        // Token might be invalid, clear it
        logout()
        
        // After logout, check if demo mode is enabled
        await checkAndSetupDemoMode()
      }
    } else {
      await checkAndSetupDemoMode()
    }
    
    return user.value
  }
  
  // Helper function to check for demo mode and set up if needed
  async function checkAndSetupDemoMode() {
    try {
      console.log('Checking for demo mode...')
      const response = await fetch(`${API_URL}/auth/config`)
      if (!response.ok) {
        throw new Error(`Failed to fetch auth config: ${response.status}`)
      }
      
      const config = await response.json()
      demoChecked.value = true  // Mark that we've checked demo status
      console.log('Auth config:', config)
      
      if (config.demo_mode) {
        console.log('Demo mode is enabled, requesting demo token')
        demoMode.value = true
        
        // Get demo token
        const tokenResponse = await fetch(`${API_URL}/auth/demo-token`)
        if (!tokenResponse.ok) {
          throw new Error(`Failed to fetch demo token: ${tokenResponse.status}`)
        }
        
        const tokenData = await tokenResponse.json()
        console.log('Received demo token')
        token.value = tokenData.access_token
        localStorage.setItem('token', token.value)
        
        try {
          // Fetch user info with the new token
          const userResponse = await fetch(`${API_URL}/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token.value}`
            }
          })
          
          if (userResponse.ok) {
            user.value = await userResponse.json()
            console.log('Demo user authenticated successfully:', user.value.email)
            return true
          } else {
            // If the user fetch fails, clear the token
            console.error('Failed to authenticate with demo token')
            localStorage.removeItem('token')
            token.value = null
          }
        } catch (error) {
          console.error('Error fetching user with demo token:', error)
          localStorage.removeItem('token')
          token.value = null
        }
      } else {
        console.log('Demo mode is not enabled')
        demoMode.value = false
      }
    } catch (err) {
      console.error('Demo mode setup failed:', err)
      demoMode.value = false
    }
    
    return false
  }
  
  async function login(credentials) {
    if (demoMode.value) {
      // In demo mode, we don't need to log in
      return user.value
    }
    
    loading.value = true
    error.value = null
    
    try {
      // Create the request JSON body
      const requestBody = new URLSearchParams({
        username: credentials.email,
        password: credentials.password
      });
      
      // Create headers with the correct content type
      const headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
      };
      
      // Send the form data for OAuth2 compatibility
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: headers,
        body: requestBody
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Login failed');
      }
      
      const data = await response.json();
      
      // Store the token
      token.value = data.access_token;
      localStorage.setItem('token', token.value);
      
      // If rememberMe is true, send a second request to get a longer-lived token
      if (credentials.rememberMe) {
        try {
          // Send a JSON request with remember_me parameter
          const rememberMeResponse = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            },
            body: JSON.stringify({
              username: credentials.email,
              password: credentials.password,
              remember_me: true
            })
          });
          
          if (rememberMeResponse.ok) {
            const rememberMeData = await rememberMeResponse.json();
            // Replace the token with the longer-lived one
            token.value = rememberMeData.access_token;
            localStorage.setItem('token', token.value);
          }
        } catch (err) {
          console.error('Failed to get remember-me token:', err);
          // Continue with the normal token
        }
      }
      
      // Fetch user details
      await fetchCurrentUser();
      
      return user.value;
    } catch (err) {
      error.value = err.message || 'Login failed';
      throw error.value;
    } finally {
      loading.value = false;
    }
  }
  
  async function register(userData) {
    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Registration failed')
      }
      
      // After registration, log the user in
      return this.login({
        email: userData.email,
        password: userData.password
      })
    } catch (error) {
      throw error
    }
  }
  
  async function fetchCurrentUser() {
    try {
      // For demo mode, add additional debugging
      if (demoMode.value) {
        console.log('Fetching user in demo mode with token:', token.value ? `${token.value.substring(0, 10)}...` : 'No token')
      }
      
      if (!token.value) {
        throw new Error('No authentication token available')
      }
      
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      })
      
      if (!response.ok) {
        // Add more detailed error logging
        const errorText = await response.text()
        console.error(`Failed to fetch user: Status ${response.status}, Response:`, errorText)
        throw new Error(`Failed to fetch user: ${response.status}`)
      }
      
      const data = await response.json()
      user.value = data
      return user.value
    } catch (err) {
      console.error('Failed to fetch user:', err)
      
      // Special handling for demo mode failures - retry getting a new token
      if (demoMode.value) {
        console.log('Attempting to refresh demo token after failed user fetch')
        try {
          // Get a fresh demo token
          const tokenResponse = await fetch(`${API_URL}/auth/demo-token`)
          if (tokenResponse.ok) {
            const tokenData = await tokenResponse.json()
            token.value = tokenData.access_token
            localStorage.setItem('token', token.value)
            console.log('Obtained new demo token, retrying user fetch')
            
            // Try one more time with the new token
            const retryResponse = await fetch(`${API_URL}/auth/me`, {
              headers: {
                'Authorization': `Bearer ${token.value}`
              }
            })
            
            if (retryResponse.ok) {
              const userData = await retryResponse.json()
              user.value = userData
              return user.value
            } else {
              console.error('Retry failed with new demo token:', await retryResponse.text())
            }
          }
        } catch (retryErr) {
          console.error('Demo token refresh failed:', retryErr)
        }
      }
      
      throw err
    }
  }
  
  function logout() {
    if (demoMode.value) {
      // In demo mode, we don't actually log out
      return
    }
    
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }
  
  async function updateUser(userData) {
    try {
      const response = await fetch(`${API_URL}/users/me`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token.value}`,
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(userData)
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const error = new Error(errorData.detail || 'Failed to update user');
        error.response = {
          status: response.status,
          data: errorData
        };
        throw error;
      }
      
      const data = await response.json();
      user.value = data;
      return data;
    } catch (err) {
      console.error('Failed to update user:', err);
      throw err;
    }
  }
  
  return {
    user,
    token,
    loading,
    error,
    demoMode,
    demoChecked,
    isAuthenticated,
    login,
    register,
    logout,
    initAuth,
    fetchCurrentUser,
    updateUser,
    checkAndSetupDemoMode
  }
}) 