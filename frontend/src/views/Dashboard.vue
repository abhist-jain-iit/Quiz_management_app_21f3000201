<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">
            <i class="bi bi-speedometer2 me-2"></i>
            Dashboard
          </h2>
          <div class="d-flex gap-2">
            <button
              class="btn btn-outline-primary"
              @click="exportData"
              :disabled="exporting"
            >
              <span
                v-if="exporting"
                class="spinner-border spinner-border-sm me-2"
              ></span>
              <i v-else class="bi bi-download me-2"></i>
              Export CSV
            </button>
            <button class="btn btn-primary" @click="loadDashboard">
              <i class="bi bi-arrow-clockwise me-2"></i>
              Refresh
            </button>
          </div>
        </div>

        <!-- Stats Cards -->
        <div class="row g-4 mb-4" v-if="dashboardData">
          <div class="col-md-3">
            <div class="card bg-primary text-white">
              <div class="card-body text-center">
                <i class="bi bi-journal-text fs-1 mb-2"></i>
                <h4>{{ dashboardData.statistics?.total_attempts || 0 }}</h4>
                <p class="mb-0">Quizzes Attempted</p>
              </div>
            </div>
          </div>

          <div class="col-md-3">
            <div class="card bg-success text-white">
              <div class="card-body text-center">
                <i class="bi bi-trophy fs-1 mb-2"></i>
                <h4>{{ dashboardData.statistics?.avg_percentage || 0 }}%</h4>
                <p class="mb-0">Average Score</p>
              </div>
            </div>
          </div>

          <div class="col-md-3">
            <div class="card bg-info text-white">
              <div class="card-body text-center">
                <i class="bi bi-clock fs-1 mb-2"></i>
                <h4>{{ dashboardData.statistics?.total_subjects || 0 }}</h4>
                <p class="mb-0">Subjects Available</p>
              </div>
            </div>
          </div>

          <div class="col-md-3">
            <div class="card bg-warning text-white">
              <div class="card-body text-center">
                <i class="bi bi-graph-up fs-1 mb-2"></i>
                <h4>{{ dashboardData.statistics?.total_quizzes || 0 }}</h4>
                <p class="mb-0">Total Quizzes</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts Row -->
        <div class="row g-4 mb-4" v-if="dashboardData">
          <div class="col-md-6">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">Monthly Activity</h5>
              </div>
              <div class="card-body">
                <canvas id="performanceChart" width="400" height="200"></canvas>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">Top Quizzes Performance</h5>
              </div>
              <div class="card-body">
                <canvas id="subjectChart" width="400" height="200"></canvas>
              </div>
            </div>
          </div>
        </div>

        <!-- Available Quizzes -->
        <div class="row">
          <div class="col-md-8">
            <div class="card">
              <div
                class="card-header d-flex justify-content-between align-items-center"
              >
                <h5 class="mb-0">Available Quizzes</h5>
                <div class="d-flex gap-2">
                  <select
                    class="form-select form-select-sm"
                    v-model="selectedSubject"
                    @change="filterQuizzes"
                  >
                    <option value="">All Subjects</option>
                    <option
                      v-for="subject in subjects"
                      :key="subject.id"
                      :value="subject.id"
                    >
                      {{ subject.name }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="card-body">
                <div v-if="loading" class="text-center py-4">
                  <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </div>

                <div
                  v-else-if="filteredQuizzes.length === 0"
                  class="text-center py-4 text-muted"
                >
                  <i class="bi bi-inbox fs-1 mb-3"></i>
                  <p>No quizzes available</p>
                </div>

                <div v-else class="row g-3">
                  <div
                    v-for="quiz in filteredQuizzes"
                    :key="quiz.id"
                    class="col-md-6"
                  >
                    <div class="card border">
                      <div class="card-body">
                        <h6 class="card-title">{{ quiz.title }}</h6>
                        <p class="card-text text-muted small">
                          <i class="bi bi-book me-1"></i
                          >{{ quiz.subject_name }} - {{ quiz.chapter_name }}
                        </p>
                        <p class="card-text text-muted small">
                          <i class="bi bi-clock me-1"></i>Duration:
                          {{ quiz.time_duration }}
                          <br />
                          <i class="bi bi-calendar me-1"></i
                          >{{ formatDate(quiz.date_of_quiz) }}
                        </p>
                        <div
                          class="d-flex justify-content-between align-items-center"
                        >
                          <small class="text-muted"
                            >{{ quiz.question_count }} questions</small
                          >
                          <router-link
                            :to="`/quiz/${quiz.id}/attempt`"
                            class="btn btn-primary btn-sm"
                            v-if="quiz.is_active"
                          >
                            <i class="bi bi-play-fill me-1"></i>
                            Start Quiz
                          </router-link>
                          <span v-else class="badge bg-secondary"
                            >Inactive</span
                          >
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Scores -->
          <div class="col-md-4">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">Recent Scores</h5>
              </div>
              <div class="card-body">
                <div
                  v-if="recentScores.length === 0"
                  class="text-center py-4 text-muted"
                >
                  <i class="bi bi-graph-down fs-1 mb-3"></i>
                  <p>No quiz attempts yet</p>
                </div>

                <div v-else>
                  <div
                    v-for="score in recentScores"
                    :key="score.id"
                    class="d-flex justify-content-between align-items-center mb-3 p-2 border rounded"
                  >
                    <div>
                      <h6 class="mb-1">{{ score.quiz_title }}</h6>
                      <small class="text-muted">{{
                        formatDate(score.time_stamp_of_attempt)
                      }}</small>
                    </div>
                    <div class="text-end">
                      <span
                        class="badge"
                        :class="getScoreBadgeClass(score.percentage)"
                      >
                        {{ score.percentage }}%
                      </span>
                      <br />
                      <small class="text-muted"
                        >{{ score.total_scored }}/{{
                          score.total_questions
                        }}</small
                      >
                    </div>
                  </div>
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
import { ref, reactive, onMounted, computed } from "vue";
import api from "../services/api";
import Chart from "chart.js/auto";

export default {
  name: "Dashboard",
  setup() {
    const loading = ref(false);
    const exporting = ref(false);
    const dashboardData = ref(null);
    const quizzes = ref([]);
    const subjects = ref([]);
    const recentScores = ref([]);
    const selectedSubject = ref("");

    const filteredQuizzes = computed(() => {
      if (!selectedSubject.value) return quizzes.value;
      return quizzes.value.filter(
        (quiz) => quiz.chapter?.subject_id === parseInt(selectedSubject.value)
      );
    });

    const loadDashboard = async () => {
      loading.value = true;
      try {
        const [
          dashResponse,
          quizzesResponse,
          subjectsResponse,
          scoresResponse,
        ] = await Promise.all([
          api.getDashboard(),
          api.getQuizzes({ is_active: true }),
          api.getSubjects(),
          api.getScores(),
        ]);

        dashboardData.value = dashResponse;
        quizzes.value = quizzesResponse;
        subjects.value = subjectsResponse;
        recentScores.value = scoresResponse.slice(0, 5); // Show only recent 5

        // Initialize charts after data is loaded
        setTimeout(() => {
          initCharts();
        }, 100);
      } catch (error) {
        console.error("Error loading dashboard:", error);
      } finally {
        loading.value = false;
      }
    };

    const initCharts = () => {
      // Monthly Activity Chart
      const performanceCtx = document.getElementById("performanceChart");
      if (performanceCtx && dashboardData.value?.charts?.monthly_activity) {
        new Chart(performanceCtx, {
          type: "line",
          data: {
            labels: dashboardData.value.charts.monthly_activity.map(
              (item) => item.month
            ),
            datasets: [
              {
                label: "Quiz Attempts",
                data: dashboardData.value.charts.monthly_activity.map(
                  (item) => item.attempts
                ),
                borderColor: "rgb(75, 192, 192)",
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                tension: 0.1,
              },
            ],
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
              },
            },
          },
        });
      }

      // Top Quizzes Chart
      const subjectCtx = document.getElementById("subjectChart");
      if (subjectCtx && dashboardData.value?.charts?.top_quizzes) {
        new Chart(subjectCtx, {
          type: "doughnut",
          data: {
            labels: dashboardData.value.charts.top_quizzes.map(
              (item) => item.title
            ),
            datasets: [
              {
                data: dashboardData.value.charts.top_quizzes.map(
                  (item) => item.avg_percentage
                ),
                backgroundColor: [
                  "#FF6384",
                  "#36A2EB",
                  "#FFCE56",
                  "#4BC0C0",
                  "#9966FF",
                  "#FF9F40",
                ],
              },
            ],
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: "bottom",
              },
            },
          },
        });
      }
    };

    const filterQuizzes = () => {
      // Filtering is handled by computed property
    };

    const exportData = async () => {
      exporting.value = true;
      try {
        await api.exportUserCSV();
        alert("Export started! You will be notified when ready.");
      } catch (error) {
        console.error("Export error:", error);
        alert("Export failed. Please try again.");
      } finally {
        exporting.value = false;
      }
    };

    const formatDate = (dateString) => {
      if (!dateString) return "";
      return new Date(dateString).toLocaleDateString();
    };

    const getScoreBadgeClass = (percentage) => {
      if (percentage >= 80) return "bg-success";
      if (percentage >= 60) return "bg-warning";
      return "bg-danger";
    };

    onMounted(() => {
      loadDashboard();
    });

    return {
      loading,
      exporting,
      dashboardData,
      quizzes,
      subjects,
      recentScores,
      selectedSubject,
      filteredQuizzes,
      loadDashboard,
      filterQuizzes,
      exportData,
      formatDate,
      getScoreBadgeClass,
    };
  },
};
</script>

<style scoped>
/* Ensure text visibility in all themes */
.card {
  background-color: var(--bs-body-bg);
  color: var(--bs-body-color);
}

.card-header {
  background-color: var(--bs-secondary-bg);
  color: var(--bs-body-color);
  border-bottom: 1px solid var(--bs-border-color);
}

.text-muted {
  color: var(--bs-secondary-color) !important;
}

.form-select {
  background-color: var(--bs-body-bg);
  color: var(--bs-body-color);
  border-color: var(--bs-border-color);
}

.form-select:focus {
  background-color: var(--bs-body-bg);
  color: var(--bs-body-color);
  border-color: var(--bs-primary);
  box-shadow: 0 0 0 0.25rem rgba(var(--bs-primary-rgb), 0.25);
}

.btn {
  color: var(--bs-btn-color);
  background-color: var(--bs-btn-bg);
  border-color: var(--bs-btn-border-color);
}

.btn:hover {
  color: var(--bs-btn-hover-color);
  background-color: var(--bs-btn-hover-bg);
  border-color: var(--bs-btn-hover-border-color);
}

/* Dark theme specific adjustments */
@media (prefers-color-scheme: dark) {
  .card {
    background-color: #212529;
    color: #ffffff;
  }

  .card-header {
    background-color: #343a40;
    color: #ffffff;
  }

  .text-muted {
    color: #adb5bd !important;
  }

  .form-select {
    background-color: #212529;
    color: #ffffff;
    border-color: #495057;
  }
}

/* Light theme specific adjustments */
@media (prefers-color-scheme: light) {
  .card {
    background-color: #ffffff;
    color: #212529;
  }

  .card-header {
    background-color: #f8f9fa;
    color: #212529;
  }

  .text-muted {
    color: #6c757d !important;
  }

  .form-select {
    background-color: #ffffff;
    color: #212529;
    border-color: #ced4da;
  }
}
</style>
