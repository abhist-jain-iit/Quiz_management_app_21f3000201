<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-lg-8">
        <!-- Hero Section -->
        <div class="text-center py-5">
          <h1 class="display-4 fw-bold text-primary mb-4">
            <i class="bi bi-mortarboard-fill me-3"></i>
            Welcome to Quiz Master V2
          </h1>
          <p class="lead text-muted mb-4">
            Your ultimate exam preparation platform for multiple courses
          </p>
          
          <div class="d-flex justify-content-center gap-3 mb-5" v-if="!isAuthenticated">
            <router-link to="/login" class="btn btn-primary btn-lg">
              <i class="bi bi-box-arrow-in-right me-2"></i>
              Login
            </router-link>
            <router-link to="/register" class="btn btn-outline-primary btn-lg">
              <i class="bi bi-person-plus me-2"></i>
              Register
            </router-link>
          </div>
          
          <div class="d-flex justify-content-center gap-3 mb-5" v-else>
            <router-link to="/dashboard" class="btn btn-primary btn-lg">
              <i class="bi bi-speedometer2 me-2"></i>
              Go to Dashboard
            </router-link>
            <router-link to="/admin" class="btn btn-success btn-lg" v-if="isAdmin">
              <i class="bi bi-gear-fill me-2"></i>
              Admin Panel
            </router-link>
          </div>
        </div>

        <!-- Features Section -->
        <div class="row g-4 mb-5">
          <div class="col-md-4">
            <div class="card h-100 text-center border-0 shadow-sm">
              <div class="card-body">
                <i class="bi bi-journal-text text-primary fs-1 mb-3"></i>
                <h5 class="card-title">Multiple Subjects</h5>
                <p class="card-text text-muted">
                  Access quizzes across various subjects and chapters
                </p>
              </div>
            </div>
          </div>
          
          <div class="col-md-4">
            <div class="card h-100 text-center border-0 shadow-sm">
              <div class="card-body">
                <i class="bi bi-stopwatch text-primary fs-1 mb-3"></i>
                <h5 class="card-title">Timed Quizzes</h5>
                <p class="card-text text-muted">
                  Practice with real exam conditions and time limits
                </p>
              </div>
            </div>
          </div>
          
          <div class="col-md-4">
            <div class="card h-100 text-center border-0 shadow-sm">
              <div class="card-body">
                <i class="bi bi-graph-up text-primary fs-1 mb-3"></i>
                <h5 class="card-title">Track Progress</h5>
                <p class="card-text text-muted">
                  Monitor your performance with detailed analytics
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Statistics Section -->
        <div class="row g-4" v-if="stats">
          <div class="col-md-3">
            <div class="card bg-primary text-white text-center">
              <div class="card-body">
                <h3 class="card-title">{{ stats.total_subjects || 0 }}</h3>
                <p class="card-text">Subjects</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-3">
            <div class="card bg-success text-white text-center">
              <div class="card-body">
                <h3 class="card-title">{{ stats.total_chapters || 0 }}</h3>
                <p class="card-text">Chapters</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-3">
            <div class="card bg-info text-white text-center">
              <div class="card-body">
                <h3 class="card-title">{{ stats.total_quizzes || 0 }}</h3>
                <p class="card-text">Quizzes</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-3">
            <div class="card bg-warning text-white text-center">
              <div class="card-body">
                <h3 class="card-title">{{ stats.total_users || 0 }}</h3>
                <p class="card-text">Users</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

export default {
  name: 'Home',
  setup() {
    const stats = ref(null)
    const user = ref(null)

    const isAuthenticated = computed(() => {
      return !!localStorage.getItem('access_token') && !!user.value
    })

    const isAdmin = computed(() => {
      return user.value?.is_admin || false
    })

    const loadUser = () => {
      const userData = localStorage.getItem('user')
      if (userData) {
        user.value = JSON.parse(userData)
      }
    }

    const loadStats = async () => {
      try {
        if (isAuthenticated.value) {
          const response = await api.getDashboard()
          stats.value = response
        }
      } catch (error) {
        console.error('Error loading stats:', error)
      }
    }

    onMounted(() => {
      loadUser()
      loadStats()
    })

    return {
      stats,
      user,
      isAuthenticated,
      isAdmin
    }
  }
}
</script>
