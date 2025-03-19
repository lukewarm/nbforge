import axios from 'axios';
import { ref } from 'vue';
import { getApiUrl } from '../utils/env';

// Get the API URL once and reuse it
const API_URL = getApiUrl();

export const useNotebookExecution = () => {
  const status = ref('');
  const error = ref('');
  const loading = ref(false);

  const executeNotebook = async (file: File, parameters = {}) => {
    loading.value = true;
    error.value = '';
    
    try {
      const formData = new FormData();
      formData.append('notebook', file);
      formData.append('parameters', JSON.stringify(parameters));

      const response = await axios.post(
        `${API_URL}/notebooks/execute`,
        formData
      );
      return response.data;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  };

  const getStatus = async (jobId: string) => {
    try {
      const response = await axios.get(
        `${API_URL}/notebooks/status/${jobId}`
      );
      status.value = response.data.status;
      return response.data;
    } catch (e) {
      error.value = e.message;
      throw e;
    }
  };

  const getResult = async (jobId: string) => {
    try {
      const response = await axios.get(
        `${API_URL}/notebooks/result/${jobId}`
      );
      return response.data;
    } catch (e) {
      error.value = e.message;
      throw e;
    }
  };

  return {
    status,
    error,
    loading,
    executeNotebook,
    getStatus,
    getResult
  };
}; 