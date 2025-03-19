import { getApiUrl } from './utils/env';

export const config = {
  apiBaseUrl: getApiUrl(),
  pollInterval: 5000, // milliseconds
  maxRetries: 3,
  defaultTimeout: 3600, // seconds
  supportedPythonVersions: ['3.8', '3.9', '3.10', '3.11'],
  allowPythonVersionChange: false,  // Set to true if backend supports changing Python version
  allowResourceConfiguration: false, // Set to true if backend supports resource configuration
  
  // Default resource settings
  defaultResources: {
    cpuMilli: 1000,
    memoryMib: 2048
  }
} 