import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 second timeout
    });

    // Add auth token interceptor
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.logout();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth methods
  async login(email, password) {
    try {
      const response = await this.api.post('/api/v1/auth/login', {
        email: email,
        password: password,
      });
      const { access_token } = response.data;
      localStorage.setItem('authToken', access_token);
      return response.data;
    } catch (error) {
      throw this._handleError(error, 'Login failed');
    }
  }

  async register(email, password, fullName) {
    try {
      const response = await this.api.post('/api/v1/auth/register', {
        email: email,
        password: password,
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error, 'Registration failed');
    }
  }

  async getCurrentUser() {
    try {
      const response = await this.api.get('/api/v1/users/me');
      return response.data;
    } catch (error) {
      throw this._handleError(error, 'Failed to get user info');
    }
  }

  // Learning modules
  async generateModule(prompt, difficulty = 'medium', duration = 30, backgroundKnowledge = '') {
    try {
      console.log('🚀 API: Generating module with params:', { prompt, difficulty, duration, backgroundKnowledge });
      const response = await this.api.post('/api/v1/modules/generate', {
        prompt: prompt,
        background_knowledge: backgroundKnowledge,
        user_id: null // Will be set from token in backend
      });
      console.log('✅ API: Module generation response:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ API: Module generation failed:', error);
      console.error('Response:', error.response?.data);
      throw this._handleError(error, 'Failed to generate module');
    }
  }

  async getModule(moduleId) {
    try {
      const response = await this.api.get(`/api/v1/modules/${moduleId}`);
      return response.data;
    } catch (error) {
      throw this._handleError(error, 'Failed to fetch module');
    }
  }

  async getUserModules() {
    try {
      console.log('🌐 API: Fetching user modules...');
      console.log('🔑 Token:', localStorage.getItem('authToken') ? 'Present' : 'Missing');
      const response = await this.api.get('/api/v1/modules');
      console.log('✅ API: Modules response:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ API: Failed to fetch modules:', error);
      console.error('Response:', error.response?.data);
      throw this._handleError(error, 'Failed to fetch user modules');
    }
  }

  async deleteModule(moduleId) {
    try {
      console.log('🗑️ API: Deleting module:', moduleId);
      const response = await this.api.delete(`/api/v1/modules/${moduleId}`);
      console.log('✅ API: Module deleted:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ API: Failed to delete module:', error);
      throw this._handleError(error, 'Failed to delete module');
    }
  }

  // Quiz methods
  async submitQuiz(moduleId, answers) {
    try {
      const response = await this.api.post(`/api/v1/modules/${moduleId}/quiz/submit`, {
        answers: answers,
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error, 'Failed to submit quiz');
    }
  }

  // Assignment methods
  async getAssignmentLatex(moduleId) {
    try {
      const response = await this.api.get(`/api/v1/assignments/${moduleId}/latex`);
      return response.data;
    } catch (error) {
      throw this._handleError(error, 'Failed to fetch assignment LaTeX');
    }
  }

  async getAssignmentPdf(moduleId) {
    try {
      const response = await this.api.get(`/api/v1/assignments/${moduleId}/pdf`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error, 'Failed to fetch assignment PDF');
    }
  }

  // Learning paths
  async generateLearningPath(goals, currentLevel, timeCommitment) {
    try {
      const response = await this.api.post('/learning-paths/generate', {
        goals: goals,
        current_level: currentLevel,
        time_commitment: timeCommitment,
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error, 'Failed to generate learning path');
    }
  }

  // Utility methods
  isAuthenticated() {
    const token = localStorage.getItem('authToken');
    if (!token) return false;
    
    try {
      // Basic JWT expiration check
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  }

  logout() {
    localStorage.removeItem('authToken');
  }

    // Chat methods
  async sendChatMessage(message, moduleId = null) {
    try {
      const response = await this.api.post('/api/v1/chat', {
        message: message,
        current_module: moduleId ? moduleId.toString() : null
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error, 'Failed to send chat message');
    }
  }

  // PDF methods
  async downloadModulePDF(moduleId) {
    try {
      const response = await this.api.get(`/api/v1/modules/${moduleId}/pdf`, {
        responseType: 'blob',
      });
      
      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Get filename from response headers or use default
      const contentDisposition = response.headers['content-disposition'];
      let filename = `module_${moduleId}_notes.pdf`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return { success: true, filename };
    } catch (error) {
      throw this._handleError(error, 'Failed to download PDF');
    }
  }

  // Health check
  async checkHealth() {
    try {
      const response = await this.api.get('/health');
      return response.status === 200;
    } catch {
      return false;
    }
  }

  // Private error handler
  _handleError(error, defaultMessage) {
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.message || 
                        error.message || 
                        defaultMessage;
    
    const errorObject = new Error(errorMessage);
    errorObject.status = error.response?.status;
    errorObject.originalError = error;
    return errorObject;
  }
}

// Singleton instance
const apiServiceInstance = new ApiService();
export default apiServiceInstance;
