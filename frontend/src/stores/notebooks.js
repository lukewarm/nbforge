import { defineStore } from 'pinia'
import { notebooksApi } from '@/services/api'

export const useNotebooksStore = defineStore('notebooks', {
  state: () => ({
    notebooks: [],
    currentNotebook: null,
    validatedNotebook: null,
    loading: false,
    error: null
  }),

  actions: {
    async fetchNotebooks() {
      this.loading = true
      try {
        const response = await notebooksApi.list()
        this.notebooks = response.data
        return this.notebooks
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async fetchNotebook(path) {
      try {
        const response = await notebooksApi.get(path);
        const notebook = response.data;
        return notebook;
      } catch (error) {
        throw error;
      }
    },

    async executeNotebook(path, executionData) {
      try {
        // Format the request according to the backend API expectations
        const request = {
          notebook_path: path,
          parameters: executionData.parameters || {},
          python_version: executionData.pythonVersion,
          cpu_milli: executionData.cpuMilli,
          memory_mib: executionData.memoryMib,
          force_rerun: executionData.force_rerun || false
        }
        
        console.log('Force rerun flag set to:', request.force_rerun)
        
        // If force_rerun is true, skip the duplicate check
        if (!request.force_rerun) {
          // Check for duplicate executions first
          const duplicateResponse = await notebooksApi.checkDuplicate(request)
          
          // If duplicate found, return the duplicate info
          if (duplicateResponse.data.is_duplicate) {
            console.log('Duplicate found from checkDuplicate API:', duplicateResponse.data);
            return {
              isDuplicate: true,
              duplicateExecution: duplicateResponse.data.original_execution,
              message: duplicateResponse.data.message
            }
          }
        } else {
          console.log('Skipping duplicate check because force_rerun=true')
        }
        
        // No duplicate found or forced rerun, proceed with execution
        const response = await notebooksApi.execute(path, request)
        
        // Debug the actual structure of the response
        console.log('Execute API response:', response)
        console.log('Response data:', response.data)
        
        // If the response indicates a duplicate despite force_rerun
        if (response.data && response.data.is_duplicate === true) {
          console.log('Duplicate detected from execute API' + (request.force_rerun ? ' despite force_rerun' : '') + ':', response.data);
          // Return the duplicate info structure
          return {
            isDuplicate: true,
            duplicateExecution: response.data.original_execution || response.data.execution,
            message: response.data.message || 'Duplicate execution found'
          }
        }
        
        // Handle the API response correctly
        if (response.data && response.data.execution) {
          // Standard format as expected
          return {
            isDuplicate: false,
            execution: response.data.execution
          }
        } else {
          // Fallback in case the response structure is different
          console.error('Unexpected API response structure:', response.data)
          
          // If the response data itself is the execution object (with an id field)
          if (response.data && response.data.id) {
            return {
              isDuplicate: false,
              execution: response.data
            }
          }
          
          // Otherwise throw an error
          throw new Error('Invalid API response: execution data not found')
        }
      } catch (error) {
        this.error = error.message
        throw error
      }
    },
    
    async uploadNotebook(formData) {
      this.loading = true
      try {
        const response = await notebooksApi.upload(formData)
        // Refresh the notebook list after upload
        await this.fetchNotebooks()
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async validateNotebook(formData) {
      this.loading = true;
      console.log('Store: Starting notebook validation');
      try {
        const response = await notebooksApi.validate(formData);
        console.log('Store: Validation API response received:', response.data);
        this.validatedNotebook = response.data;
        console.log('Store: validatedNotebook set to:', this.validatedNotebook);
        return this.validatedNotebook;
      } catch (error) {
        console.error('Store: Validation error:', error);
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateNotebookMetadata(formData) {
      this.loading = true
      try {
        const response = await notebooksApi.updateMetadata(formData)
        
        // Create a download link for the updated notebook
        const blob = new Blob([response.data], { type: 'application/json' })
        const url = window.URL.createObjectURL(blob)
        
        // Return the URL for downloading
        return url
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    }
  }
}) 