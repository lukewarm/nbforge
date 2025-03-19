import { useRouter } from 'vue-router'

/**
 * Handles API errors and returns a user-friendly error message
 * @param {Error} error - The error object from axios
 * @returns {string} A user-friendly error message
 */
export function handleApiError(error) {
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    const status = error.response.status
    const data = error.response.data
    
    if (status === 400) {
      return data.detail || 'Invalid request. Please check your input.'
    } else if (status === 401) {
      return 'Authentication required. Please log in.'
    } else if (status === 403) {
      return 'You do not have permission to perform this action.'
    } else if (status === 404) {
      return 'The requested resource was not found.'
    } else if (status === 422) {
      // Validation error
      if (data.detail && Array.isArray(data.detail)) {
        return data.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ')
      }
      return data.detail || 'Validation error. Please check your input.'
    } else if (status >= 500) {
      return 'A server error occurred. Please try again later.'
    }
    
    return data.detail || `Error: ${status}`
  } else if (error.request) {
    // The request was made but no response was received
    return 'No response from server. Please check your network connection.'
  } else {
    // Something happened in setting up the request that triggered an Error
    return error.message || 'An unexpected error occurred.'
  }
} 