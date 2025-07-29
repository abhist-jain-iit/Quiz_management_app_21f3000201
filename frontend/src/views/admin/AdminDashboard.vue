<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">
            <i class="bi bi-gear-fill me-2"></i>
            Admin Dashboard
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

        <!-- Quick Actions -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-lightning-charge me-2"></i>
              Quick Actions
            </h5>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-2">
                <router-link
                  to="/admin/subjects"
                  class="btn btn-outline-primary w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3"
                >
                  <i class="bi bi-journal-text fs-1 mb-2"></i>
                  <span>Subjects</span>
                </router-link>
              </div>
              <div class="col-md-2">
                <router-link
                  to="/admin/chapters"
                  class="btn btn-outline-success w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3"
                >
                  <i class="bi bi-book fs-1 mb-2"></i>
                  <span>Chapters</span>
                </router-link>
              </div>
              <div class="col-md-2">
                <router-link
                  to="/admin/quizzes"
                  class="btn btn-outline-info w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3"
                >
                  <i class="bi bi-clipboard-check fs-1 mb-2"></i>
                  <span>Quizzes</span>
                </router-link>
              </div>
              <div class="col-md-2">
                <router-link
                  to="/admin/questions"
                  class="btn btn-outline-warning w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3"
                >
                  <i class="bi bi-question-circle fs-1 mb-2"></i>
                  <span>Questions</span>
                </router-link>
              </div>
              <div class="col-md-2">
                <router-link
                  to="/admin/users"
                  class="btn btn-outline-danger w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3"
                >
                  <i class="bi bi-people fs-1 mb-2"></i>
                  <span>Users</span>
                </router-link>
              </div>
              <div class="col-md-2">
                <button
                  class="btn btn-outline-secondary w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3"
                  @click="searchModal = true"
                >
                  <i class="bi bi-search fs-1 mb-2"></i>
                  <span>Search</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Background Jobs Testing -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-gear-wide-connected me-2"></i>
              Background Jobs Testing
            </h5>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-4">
                <button
                  class="btn btn-outline-warning w-100 d-flex flex-column align-items-center justify-content-center py-3"
                  @click="triggerDailyReminders"
                  :disabled="reminderJobRunning"
                >
                  <span
                    v-if="reminderJobRunning"
                    class="spinner-border spinner-border-sm mb-2"
                  ></span>
                  <i v-else class="bi bi-bell fs-3 mb-2"></i>
                  <span>Test Daily Reminders</span>
                  <small class="text-muted mt-1"
                    >Send reminders to inactive users</small
                  >
                </button>
              </div>
              <div class="col-md-4">
                <button
                  class="btn btn-outline-info w-100 d-flex flex-column align-items-center justify-content-center py-3"
                  @click="triggerMonthlyReports"
                  :disabled="reportJobRunning"
                >
                  <span
                    v-if="reportJobRunning"
                    class="spinner-border spinner-border-sm mb-2"
                  ></span>
                  <i v-else class="bi bi-file-earmark-text fs-3 mb-2"></i>
                  <span>Test Monthly Reports</span>
                  <small class="text-muted mt-1"
                    >Generate monthly activity reports</small
                  >
                </button>
              </div>
              <div class="col-md-4">
                <div class="card border-info">
                  <div class="card-body text-center p-3">
                    <i class="bi bi-info-circle fs-4 text-info mb-2"></i>
                    <h6 class="mb-1">Job Status</h6>
                    <div v-if="lastJobResult" class="small">
                      <div class="text-success" v-if="lastJobResult.success">
                        ✓ {{ lastJobResult.message }}
                      </div>
                      <div class="text-danger" v-else>
                        ✗ {{ lastJobResult.message }}
                      </div>
                    </div>
                    <div v-else class="text-muted small">No recent jobs</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Stats Cards -->
        <div class="row g-4 mb-4" v-if="dashboardData">
          <div class="col-md-3">
            <div class="card bg-primary text-white">
              <div class="card-body text-center">
                <i class="bi bi-people fs-1 mb-2"></i>
                <h4>{{ dashboardData.statistics?.total_users || 0 }}</h4>
                <p class="mb-0">Total Users</p>
              </div>
            </div>
          </div>

          <div class="col-md-3">
            <div class="card bg-success text-white">
              <div class="card-body text-center">
                <i class="bi bi-journal-text fs-1 mb-2"></i>
                <h4>{{ dashboardData.statistics?.total_subjects || 0 }}</h4>
                <p class="mb-0">Subjects</p>
              </div>
            </div>
          </div>

          <div class="col-md-3">
            <div class="card bg-info text-white">
              <div class="card-body text-center">
                <i class="bi bi-clipboard-check fs-1 mb-2"></i>
                <h4>{{ dashboardData.statistics?.total_quizzes || 0 }}</h4>
                <p class="mb-0">Quizzes</p>
              </div>
            </div>
          </div>

          <div class="col-md-3">
            <div class="card bg-warning text-white">
              <div class="card-body text-center">
                <i class="bi bi-graph-up fs-1 mb-2"></i>
                <h4>{{ dashboardData.statistics?.total_attempts || 0 }}</h4>
                <p class="mb-0">Quiz Attempts</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts Row -->
        <div class="row g-4 mb-4" v-if="dashboardData">
          <div class="col-md-6">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">User Registration Trend</h5>
              </div>
              <div class="card-body">
                <canvas id="userTrendChart" width="400" height="200"></canvas>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">Quiz Performance Overview</h5>
              </div>
              <div class="card-body">
                <canvas
                  id="performanceOverviewChart"
                  width="400"
                  height="200"
                ></canvas>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="row">
          <div class="col-md-6">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">Recent Users</h5>
              </div>
              <div class="card-body">
                <div v-if="loading" class="text-center py-4">
                  <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </div>

                <div
                  v-else-if="recentUsers.length === 0"
                  class="text-center py-4 text-muted"
                >
                  <i class="bi bi-person-x fs-1 mb-3"></i>
                  <p>No recent users</p>
                </div>

                <div v-else>
                  <div
                    v-for="user in recentUsers"
                    :key="user.id"
                    class="d-flex justify-content-between align-items-center mb-3 p-2 border rounded"
                  >
                    <div>
                      <h6 class="mb-1">{{ user.full_name }}</h6>
                      <small class="text-muted">{{ user.email }}</small>
                    </div>
                    <div class="text-end">
                      <span
                        class="badge"
                        :class="user.is_active ? 'bg-success' : 'bg-danger'"
                      >
                        {{ user.is_active ? "Active" : "Inactive" }}
                      </span>
                      <br />
                      <small class="text-muted">{{
                        formatDate(user.created_at)
                      }}</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">Recent Quiz Attempts</h5>
              </div>
              <div class="card-body">
                <div
                  v-if="recentAttempts.length === 0"
                  class="text-center py-4 text-muted"
                >
                  <i class="bi bi-clipboard-x fs-1 mb-3"></i>
                  <p>No recent attempts</p>
                </div>

                <div v-else>
                  <div
                    v-for="attempt in recentAttempts"
                    :key="attempt.id"
                    class="d-flex justify-content-between align-items-center mb-3 p-2 border rounded"
                  >
                    <div>
                      <h6 class="mb-1">{{ attempt.quiz_title }}</h6>
                      <small class="text-muted"
                        >by {{ attempt.user_name }}</small
                      >
                    </div>
                    <div class="text-end">
                      <span
                        class="badge"
                        :class="getScoreBadgeClass(attempt.percentage)"
                      >
                        {{ attempt.percentage }}%
                      </span>
                      <br />
                      <small class="text-muted">{{
                        formatDate(attempt.time_stamp_of_attempt)
                      }}</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Search Modal -->
    <div
      class="modal fade"
      :class="{ show: searchModal }"
      :style="{ display: searchModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Search</h5>
            <button
              type="button"
              class="btn-close"
              @click="searchModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <input
                type="text"
                class="form-control"
                placeholder="Search users, subjects, quizzes..."
                v-model="searchQuery"
                @input="performSearch"
              />
            </div>

            <div v-if="searchResults.length > 0">
              <h6>Search Results:</h6>
              <div class="list-group">
                <div
                  v-for="result in searchResults"
                  :key="result.id"
                  class="list-group-item"
                >
                  <div
                    class="d-flex justify-content-between align-items-center"
                  >
                    <div>
                      <h6 class="mb-1">
                        {{ result.name || result.title || result.full_name }}
                      </h6>
                      <small class="text-muted">{{ result.type }}</small>
                    </div>
                    <span class="badge bg-primary">{{ result.type }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div
              v-else-if="searchQuery && !searching"
              class="text-center py-4 text-muted"
            >
              <i class="bi bi-search fs-1 mb-3"></i>
              <p>No results found</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="searchModal"
      class="modal-backdrop fade show"
      @click="searchModal = false"
    ></div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from "vue";
import api from "../../services/api";
import Chart from "chart.js/auto";

export default {
  name: "AdminDashboard",
  setup() {
    const loading = ref(false);
    const exporting = ref(false);
    const searching = ref(false);
    const searchModal = ref(false);
    const searchQuery = ref("");
    const searchResults = ref([]);
    const dashboardData = ref(null);
    const recentUsers = ref([]);
    const recentAttempts = ref([]);

    // Background job testing states
    const reminderJobRunning = ref(false);
    const reportJobRunning = ref(false);
    const lastJobResult = ref(null);

    // Chart instances for proper cleanup
    let userTrendChart = null;
    let performanceOverviewChart = null;

    const loadDashboard = async () => {
      loading.value = true;
      try {
        console.log("Loading admin dashboard...");

        // Clear cache and force fresh data
        const timestamp = Date.now();

        const dashResponse = await api.getDashboard({ _t: timestamp });
        console.log("Dashboard data loaded:", dashResponse);
        dashboardData.value = dashResponse;

        const usersResponse = await api.getUsers({ _t: timestamp });
        console.log("Users loaded:", usersResponse);
        recentUsers.value = Array.isArray(usersResponse)
          ? usersResponse.slice(0, 5)
          : [];

        const scoresResponse = await api.getScores({ _t: timestamp });
        console.log("Scores loaded:", scoresResponse);
        recentAttempts.value = Array.isArray(scoresResponse)
          ? scoresResponse.slice(0, 5)
          : [];

        // Initialize charts after data is loaded
        setTimeout(() => {
          initCharts();
        }, 200);

        console.log("Admin dashboard loading completed successfully");
      } catch (error) {
        console.error("Error loading admin dashboard:", error);

        // Set default values to prevent UI errors
        dashboardData.value = {
          statistics: {
            total_users: 0,
            total_quizzes: 0,
            total_attempts: 0,
            avg_score: 0,
          },
        };
        recentUsers.value = [];
        recentAttempts.value = [];
      } finally {
        loading.value = false;
      }
    };

    const initCharts = () => {
      // Destroy existing charts before creating new ones
      if (userTrendChart) {
        userTrendChart.destroy();
        userTrendChart = null;
      }
      if (performanceOverviewChart) {
        performanceOverviewChart.destroy();
        performanceOverviewChart = null;
      }

      // User Registration Trend Chart
      const userTrendCtx = document.getElementById("userTrendChart");
      if (userTrendCtx && dashboardData.value?.user_registration_trend) {
        userTrendChart = new Chart(userTrendCtx, {
          type: "line",
          data: {
            labels: dashboardData.value.user_registration_trend.map(
              (item) => item.date
            ),
            datasets: [
              {
                label: "New Users",
                data: dashboardData.value.user_registration_trend.map(
                  (item) => item.count
                ),
                borderColor: "rgb(54, 162, 235)",
                backgroundColor: "rgba(54, 162, 235, 0.2)",
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

      // Performance Overview Chart
      const performanceCtx = document.getElementById(
        "performanceOverviewChart"
      );
      if (performanceCtx && dashboardData.value?.quiz_performance_overview) {
        performanceOverviewChart = new Chart(performanceCtx, {
          type: "bar",
          data: {
            labels: ["0-40%", "41-60%", "61-80%", "81-100%"],
            datasets: [
              {
                label: "Number of Attempts",
                data: [
                  dashboardData.value.quiz_performance_overview.poor || 0,
                  dashboardData.value.quiz_performance_overview.average || 0,
                  dashboardData.value.quiz_performance_overview.good || 0,
                  dashboardData.value.quiz_performance_overview.excellent || 0,
                ],
                backgroundColor: [
                  "rgba(255, 99, 132, 0.8)",
                  "rgba(255, 206, 86, 0.8)",
                  "rgba(75, 192, 192, 0.8)",
                  "rgba(54, 162, 235, 0.8)",
                ],
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
    };

    const performSearch = async () => {
      if (!searchQuery.value.trim()) {
        searchResults.value = [];
        return;
      }

      searching.value = true;
      try {
        const response = await api.search({ query: searchQuery.value });
        searchResults.value = response;
      } catch (error) {
        console.error("Search error:", error);
        searchResults.value = [];
      } finally {
        searching.value = false;
      }
    };

    const exportData = async () => {
      exporting.value = true;
      try {
        const result = await api.exportAdminCSV();
        alert("Admin CSV file downloaded successfully!");
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

    // Background job testing functions
    const triggerDailyReminders = async () => {
      reminderJobRunning.value = true;
      lastJobResult.value = null;

      try {
        console.log("Triggering daily reminders...");
        const result = await api.triggerDailyReminders();
        console.log("Daily reminders triggered:", result);

        // Poll for job completion
        if (result.task_id) {
          await pollJobStatus(result.task_id, "Daily reminders");
        } else {
          lastJobResult.value = {
            success: true,
            message: "Daily reminders job started successfully",
          };
        }
      } catch (error) {
        console.error("Error triggering daily reminders:", error);
        lastJobResult.value = {
          success: false,
          message: `Failed to trigger reminders: ${
            error.response?.data?.message || error.message
          }`,
        };
      } finally {
        reminderJobRunning.value = false;
      }
    };

    const triggerMonthlyReports = async () => {
      reportJobRunning.value = true;
      lastJobResult.value = null;

      try {
        console.log("Triggering monthly reports...");
        const result = await api.triggerMonthlyReports();
        console.log("Monthly reports triggered:", result);

        // Poll for job completion
        if (result.task_id) {
          await pollJobStatus(result.task_id, "Monthly reports");
        } else {
          lastJobResult.value = {
            success: true,
            message: "Monthly reports job started successfully",
          };
        }
      } catch (error) {
        console.error("Error triggering monthly reports:", error);
        lastJobResult.value = {
          success: false,
          message: `Failed to trigger reports: ${
            error.response?.data?.message || error.message
          }`,
        };
      } finally {
        reportJobRunning.value = false;
      }
    };

    const pollJobStatus = async (taskId, jobName) => {
      const maxAttempts = 30; // 30 seconds max
      let attempts = 0;

      const poll = async () => {
        try {
          const status = await api.getJobStatus(taskId);
          console.log(`${jobName} status:`, status);

          if (status.state === "SUCCESS") {
            lastJobResult.value = {
              success: true,
              message: `${jobName} completed successfully`,
            };
            return;
          } else if (status.state === "FAILURE") {
            lastJobResult.value = {
              success: false,
              message: `${jobName} failed: ${status.error || "Unknown error"}`,
            };
            return;
          } else if (attempts < maxAttempts) {
            attempts++;
            setTimeout(poll, 1000); // Poll every second
          } else {
            lastJobResult.value = {
              success: false,
              message: `${jobName} timed out`,
            };
          }
        } catch (error) {
          console.error(`Error polling ${jobName} status:`, error);
          lastJobResult.value = {
            success: false,
            message: `Error checking ${jobName} status`,
          };
        }
      };

      poll();
    };

    onMounted(() => {
      loadDashboard();
    });

    onUnmounted(() => {
      // Clean up charts when component is unmounted
      if (userTrendChart) {
        userTrendChart.destroy();
        userTrendChart = null;
      }
      if (performanceOverviewChart) {
        performanceOverviewChart.destroy();
        performanceOverviewChart = null;
      }
    });

    return {
      loading,
      exporting,
      searching,
      searchModal,
      searchQuery,
      searchResults,
      dashboardData,
      recentUsers,
      recentAttempts,
      reminderJobRunning,
      reportJobRunning,
      lastJobResult,
      loadDashboard,
      performSearch,
      exportData,
      formatDate,
      getScoreBadgeClass,
      triggerDailyReminders,
      triggerMonthlyReports,
    };
  },
};
</script>
