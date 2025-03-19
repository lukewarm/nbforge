/**
 * Get environment variables with fallbacks
 * This utility provides a consistent way to access environment variables
 * with graceful fallbacks between Vite build-time variables and runtime variables
 */

/**
 * Get an environment variable with fallbacks
 * @param {string} key - The environment variable key (without VITE_ prefix)
 * @param {any} defaultValue - Default value if not found
 * @returns {any} The value of the environment variable or default
 */
export function getEnv(key, defaultValue = null) {
  // Try Vite environment variables first (build time)
  const viteKey = `VITE_${key}`;
  
  if (import.meta.env[viteKey] !== undefined) {
    return import.meta.env[viteKey];
  }
  
  // Then try runtime-injected environment variables
  if (window.env && window.env[key] !== undefined) {
    return window.env[key];
  }
  
  // Fallback to default value
  return defaultValue;
}

/**
 * Get the API URL with appropriate fallbacks and ensure it includes the API version
 * @returns {string} The API URL including /api/v1
 */
export function getApiUrl() {
  const baseUrl = getEnv('API_URL', 'http://localhost:8000');
  
  // Check if the URL already ends with /api/v1
  if (baseUrl.endsWith('/api/v1')) {
    return baseUrl;
  }
  
  // Check if the URL already has a trailing slash
  if (baseUrl.endsWith('/')) {
    return `${baseUrl}api/v1`;
  }
  
  // Otherwise, add /api/v1
  return `${baseUrl}/api/v1`;
}

/**
 * Get the base URL for the application
 * @returns {string} The base URL
 */
export function getBaseUrl() {
  return getEnv('BASE_URL', '/');
}

/**
 * Get the environment (development, production, etc.)
 * @returns {string} The environment
 */
export function getNodeEnv() {
  return getEnv('NODE_ENV', 'production');
}

export default {
  getEnv,
  getApiUrl,
  getBaseUrl,
  getNodeEnv
}; 