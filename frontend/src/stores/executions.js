import { defineStore } from 'pinia'
import { executionsApi } from '@/services/api'

export const useExecutionsStore = defineStore('executions', {
  state: () => ({
    executions: [],
    currentExecution: null,
    loading: false,
    error: null
  }),

  actions: {
    async fetchExecutions() {
      this.loading = true
      try {
        const response = await executionsApi.list()
        this.executions = response.data
        return this.executions
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async getExecution(id) {
      this.loading = true
      try {
        const response = await executionsApi.get(id)
        this.currentExecution = response.data
        return this.currentExecution
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async getExecutionStatus(id) {
      try {
        const response = await executionsApi.get(id)
        
        // Update the current execution if it's loaded
        if (this.currentExecution && this.currentExecution.id === id) {
          this.currentExecution = {
            ...this.currentExecution,
            ...response.data
          }
        }
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async getExecutionReport(id) {
      try {
        const response = await executionsApi.getReport(id)
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async cancelExecution(id) {
      try {
        if (!id) {
          throw new Error('Cannot cancel execution: Invalid execution ID');
        }
        
        console.log(`Cancelling execution ${id}...`);
        const response = await executionsApi.cancel(id);
        console.log(`Cancel response:`, response);
        
        // Check if the cancellation was actually successful
        if (response.data && response.data.status === 'cancellation_failed') {
          console.warn(`Cancellation failed for execution ${id}:`, response.data);
          
          // Don't update the execution status since cancellation failed
          // But return the response to let components handle it
          return response.data;
        }
        
        // Update the execution status in the store - use lowercase to match API
        if (this.currentExecution && this.currentExecution.id === id) {
          this.currentExecution.status = 'cancelled';
        }
        
        // Update the execution in the list if it exists
        const index = this.executions.findIndex(e => e.id === id);
        if (index !== -1) {
          this.executions[index].status = 'cancelled';
        }
        
        return response.data;
      } catch (error) {
        console.error(`Failed to cancel execution ${id}:`, error);
        this.error = error.message || 'Failed to cancel execution';
        throw error; // Re-throw to allow components to handle the error
      }
    }
  }
}) 