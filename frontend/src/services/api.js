import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 10000 // 10 second timeout
    })

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('Request interceptor error:', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`API Response: ${response.status} ${response.config.url}`)
        return response
      },
      (error) => {
        console.error('API Error:', error.response?.status, error.response?.data || error.message)

        if (error.response?.status === 401) {
          // Clear auth data and redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')

          // Update auth state
          if (window.updateAuthState) {
            window.updateAuthState()
          }

          // Only redirect if not already on login page
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
        }

        return Promise.reject(error)
      }
    )
  }

  // Helper method to handle API errors
  handleError(error, defaultMessage = 'An error occurred') {
    if (error.response?.data?.message) {
      return error.response.data.message
    } else if (error.message) {
      return error.message
    } else {
      return defaultMessage
    }
  }

  // Authentication
  async login(credentials) {
    try {
      const response = await this.client.post('/auth/login', credentials)
      return response.data
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  async register(userData) {
    try {
      const response = await this.client.post('/auth/register', userData)
      return response.data
    } catch (error) {
      console.error('Registration error:', error)
      throw error
    }
  }

  async logout() {
    try {
      const response = await this.client.post('/auth/logout')
      return response.data
    } catch (error) {
      console.error('Logout error:', error)
      // Don't throw error for logout - just log it
      return null
    }
  }

  async getProfile() {
    try {
      const response = await this.client.get('/auth/profile')
      return response.data
    } catch (error) {
      console.error('Get profile error:', error)
      throw error
    }
  }

  // Dashboard
  async getDashboard() {
    try {
      const response = await this.client.get('/dashboard')
      return response.data
    } catch (error) {
      console.error('Dashboard error:', error)
      throw error
    }
  }

  // Subjects
  async getSubjects(params = {}) {
    const response = await this.client.get('/subjects', { params })
    return response.data
  }

  async getSubject(id) {
    const response = await this.client.get(`/subjects/${id}`)
    return response.data
  }

  async createSubject(data) {
    const response = await this.client.post('/subjects', data)
    return response.data
  }

  async updateSubject(id, data) {
    const response = await this.client.put(`/subjects/${id}`, data)
    return response.data
  }

  async deleteSubject(id) {
    const response = await this.client.delete(`/subjects/${id}`)
    return response.data
  }

  // Chapters
  async getChapters(params = {}) {
    const response = await this.client.get('/chapters', { params })
    return response.data
  }

  async getChapter(id) {
    const response = await this.client.get(`/chapters/${id}`)
    return response.data
  }

  async createChapter(data) {
    const response = await this.client.post('/chapters', data)
    return response.data
  }

  async updateChapter(id, data) {
    const response = await this.client.put(`/chapters/${id}`, data)
    return response.data
  }

  async deleteChapter(id) {
    const response = await this.client.delete(`/chapters/${id}`)
    return response.data
  }

  // Quizzes
  async getQuizzes(params = {}) {
    const response = await this.client.get('/quizzes', { params })
    return response.data
  }

  async getQuiz(id) {
    const response = await this.client.get(`/quizzes/${id}`)
    return response.data
  }

  async createQuiz(data) {
    const response = await this.client.post('/quizzes', data)
    return response.data
  }

  async updateQuiz(id, data) {
    const response = await this.client.put(`/quizzes/${id}`, data)
    return response.data
  }

  async deleteQuiz(id) {
    const response = await this.client.delete(`/quizzes/${id}`)
    return response.data
  }

  // Quiz Attempt
  async getQuizForAttempt(id) {
    const response = await this.client.get(`/quiz-attempt/${id}`)
    return response.data
  }

  // Questions
  async getQuestions(params = {}) {
    const response = await this.client.get('/questions', { params })
    return response.data
  }

  async getQuestion(id) {
    const response = await this.client.get(`/questions/${id}`)
    return response.data
  }

  async createQuestion(data) {
    const response = await this.client.post('/questions', data)
    return response.data
  }

  async updateQuestion(id, data) {
    const response = await this.client.put(`/questions/${id}`, data)
    return response.data
  }

  async deleteQuestion(id) {
    const response = await this.client.delete(`/questions/${id}`)
    return response.data
  }

  // Scores
  async getScores(params = {}) {
    const response = await this.client.get('/scores', { params })
    return response.data
  }

  async submitQuizScore(data) {
    const response = await this.client.post('/scores', data)
    return response.data
  }

  // Users (Admin only)
  async getUsers(params = {}) {
    const response = await this.client.get('/users', { params })
    return response.data
  }

  async getUser(id) {
    const response = await this.client.get(`/users/${id}`)
    return response.data
  }

  async updateUser(id, data) {
    const response = await this.client.put(`/users/${id}`, data)
    return response.data
  }

  async deleteUser(id) {
    const response = await this.client.delete(`/users/${id}`)
    return response.data
  }

  // Search
  async search(params = {}) {
    const response = await this.client.get('/search', { params })
    return response.data
  }

  // Export
  async exportUserCSV() {
    const response = await this.client.post('/export/user-csv', {}, {
      responseType: 'blob'
    })

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url

    // Get filename from response headers or use default
    const contentDisposition = response.headers['content-disposition']
    let filename = 'quiz_data.csv'
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }

    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    return { message: 'CSV downloaded successfully' }
  }

  async exportAdminCSV() {
    const response = await this.client.post('/export/admin-csv', {}, {
      responseType: 'blob'
    })

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url

    // Get filename from response headers or use default
    const contentDisposition = response.headers['content-disposition']
    let filename = 'admin_users_data.csv'
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }

    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    return { message: 'CSV downloaded successfully' }
  }
}

export default new ApiService()
