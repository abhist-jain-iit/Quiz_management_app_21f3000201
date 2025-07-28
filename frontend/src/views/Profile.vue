<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">
              <i class="bi bi-person-circle me-2"></i>
              User Profile
            </h4>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="user">
              <div class="row">
                <div class="col-md-4 text-center mb-4">
                  <div class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center" 
                       style="width: 120px; height: 120px; font-size: 3rem;">
                    <i class="bi bi-person-fill"></i>
                  </div>
                  <h5 class="mt-3">{{ user.full_name }}</h5>
                  <p class="text-muted">{{ user.email }}</p>
                  <span class="badge bg-primary">{{ user.is_admin ? 'Administrator' : 'Student' }}</span>
                </div>

                <div class="col-md-8">
                  <h5 class="mb-3">Profile Information</h5>
                  
                  <div class="row mb-3">
                    <div class="col-sm-4">
                      <strong>Username:</strong>
                    </div>
                    <div class="col-sm-8">
                      {{ user.username }}
                    </div>
                  </div>

                  <div class="row mb-3">
                    <div class="col-sm-4">
                      <strong>Full Name:</strong>
                    </div>
                    <div class="col-sm-8">
                      {{ user.full_name }}
                    </div>
                  </div>

                  <div class="row mb-3">
                    <div class="col-sm-4">
                      <strong>Email:</strong>
                    </div>
                    <div class="col-sm-8">
                      {{ user.email }}
                    </div>
                  </div>

                  <div class="row mb-3" v-if="user.qualification">
                    <div class="col-sm-4">
                      <strong>Qualification:</strong>
                    </div>
                    <div class="col-sm-8">
                      {{ user.qualification }}
                    </div>
                  </div>

                  <div class="row mb-3" v-if="user.date_of_birth">
                    <div class="col-sm-4">
                      <strong>Date of Birth:</strong>
                    </div>
                    <div class="col-sm-8">
                      {{ formatDate(user.date_of_birth) }}
                    </div>
                  </div>

                  <div class="row mb-3">
                    <div class="col-sm-4">
                      <strong>Member Since:</strong>
                    </div>
                    <div class="col-sm-8">
                      {{ formatDate(user.created_at) }}
                    </div>
                  </div>

                  <div class="row mb-3">
                    <div class="col-sm-4">
                      <strong>Account Status:</strong>
                    </div>
                    <div class="col-sm-8">
                      <span class="badge" :class="user.is_active ? 'bg-success' : 'bg-danger'">
                        {{ user.is_active ? 'Active' : 'Inactive' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Quiz Statistics (for non-admin users) -->
              <div v-if="!user.is_admin && stats" class="mt-4">
                <h5 class="mb-3">Quiz Statistics</h5>
                <div class="row g-3">
                  <div class="col-md-3">
                    <div class="card bg-primary text-white text-center">
                      <div class="card-body">
                        <h4>{{ stats.total_attempts || 0 }}</h4>
                        <p class="mb-0">Total Attempts</p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="col-md-3">
                    <div class="card bg-success text-white text-center">
                      <div class="card-body">
                        <h4>{{ stats.average_score || 0 }}%</h4>
                        <p class="mb-0">Average Score</p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="col-md-3">
                    <div class="card bg-info text-white text-center">
                      <div class="card-body">
                        <h4>{{ stats.best_score || 0 }}%</h4>
                        <p class="mb-0">Best Score</p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="col-md-3">
                    <div class="card bg-warning text-white text-center">
                      <div class="card-body">
                        <h4>{{ stats.subjects_attempted || 0 }}</h4>
                        <p class="mb-0">Subjects</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Recent Activity -->
              <div v-if="recentScores.length > 0" class="mt-4">
                <h5 class="mb-3">Recent Quiz Attempts</h5>
                <div class="table-responsive">
                  <table class="table table-striped">
                    <thead>
                      <tr>
                        <th>Quiz</th>
                        <th>Date</th>
                        <th>Score</th>
                        <th>Percentage</th>
                        <th>Time Taken</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="score in recentScores" :key="score.id">
                        <td>{{ score.quiz_title }}</td>
                        <td>{{ formatDate(score.time_stamp_of_attempt) }}</td>
                        <td>{{ score.total_scored }}/{{ score.total_questions }}</td>
                        <td>
                          <span class="badge" :class="getScoreBadgeClass(score.percentage)">
                            {{ score.percentage }}%
                          </span>
                        </td>
                        <td>{{ score.time_taken || 'N/A' }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../services/api'

export default {
  name: 'Profile',
  setup() {
    const loading = ref(false)
    const user = ref(null)
    const stats = ref(null)
    const recentScores = ref([])

    const loadProfile = async () => {
      loading.value = true
      try {
        const [profileResponse, dashboardResponse, scoresResponse] = await Promise.all([
          api.getProfile(),
          api.getDashboard(),
          api.getScores()
        ])
        
        user.value = profileResponse.user
        stats.value = dashboardResponse
        recentScores.value = scoresResponse.slice(0, 10) // Show recent 10
      } catch (error) {
        console.error('Error loading profile:', error)
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }

    const getScoreBadgeClass = (percentage) => {
      if (percentage >= 80) return 'bg-success'
      if (percentage >= 60) return 'bg-warning'
      return 'bg-danger'
    }

    onMounted(() => {
      loadProfile()
    })

    return {
      loading,
      user,
      stats,
      recentScores,
      formatDate,
      getScoreBadgeClass
    }
  }
}
</script>
