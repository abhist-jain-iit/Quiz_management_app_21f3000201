<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-4">
        <div class="card shadow">
          <div class="card-body p-4">
            <div class="text-center mb-4">
              <i class="bi bi-mortarboard-fill text-primary fs-1"></i>
              <h3 class="mt-2">Login to Quiz Master</h3>
              <p class="text-muted">Enter your credentials to continue</p>
            </div>

            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-person"></i>
                  </span>
                  <input
                    type="text"
                    class="form-control"
                    id="username"
                    v-model="form.username"
                    :class="{ 'is-invalid': errors.username }"
                    required
                  >
                </div>
                <div class="invalid-feedback" v-if="errors.username">
                  {{ errors.username }}
                </div>
              </div>

              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-lock"></i>
                  </span>
                  <input
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control"
                    id="password"
                    v-model="form.password"
                    :class="{ 'is-invalid': errors.password }"
                    required
                  >
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    @click="showPassword = !showPassword"
                  >
                    <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  </button>
                </div>
                <div class="invalid-feedback" v-if="errors.password">
                  {{ errors.password }}
                </div>
              </div>

              <div class="alert alert-danger" v-if="errorMessage">
                <i class="bi bi-exclamation-triangle me-2"></i>
                {{ errorMessage }}
              </div>

              <div class="d-grid mb-3">
                <button
                  type="submit"
                  class="btn btn-primary"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-box-arrow-in-right me-2"></i>
                  {{ loading ? 'Logging in...' : 'Login' }}
                </button>
              </div>
            </form>

            <div class="text-center">
              <p class="mb-0">
                Don't have an account?
                <router-link to="/register" class="text-decoration-none">
                  Register here
                </router-link>
              </p>
            </div>

            <!-- Demo Credentials -->
            <div class="mt-4 p-3 bg-light rounded">
              <h6 class="text-muted mb-2">Demo Credentials:</h6>
              <small class="text-muted">
                <strong>Admin:</strong> admin / Admin@123<br>
                <strong>User:</strong> Create a new account
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const showPassword = ref(false)
    const errorMessage = ref('')
    
    const form = reactive({
      username: '',
      password: ''
    })
    
    const errors = reactive({
      username: '',
      password: ''
    })

    const validateForm = () => {
      errors.username = ''
      errors.password = ''
      
      if (!form.username.trim()) {
        errors.username = 'Username is required'
        return false
      }
      
      if (!form.password.trim()) {
        errors.password = 'Password is required'
        return false
      }
      
      return true
    }

    const handleLogin = async () => {
      if (!validateForm()) return
      
      loading.value = true
      errorMessage.value = ''
      
      try {
        const response = await api.login({
          username: form.username.trim(),
          password: form.password
        })
        
        // Store tokens and user data
        localStorage.setItem('access_token', response.access_token)
        localStorage.setItem('refresh_token', response.refresh_token)
        localStorage.setItem('user', JSON.stringify(response.user))
        
        // Redirect based on user role
        if (response.user.is_admin) {
          router.push('/admin')
        } else {
          router.push('/dashboard')
        }
      } catch (error) {
        console.error('Login error:', error)
        errorMessage.value = error.response?.data?.message || 'Login failed. Please try again.'
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      errors,
      loading,
      showPassword,
      errorMessage,
      handleLogin
    }
  }
}
</script>
